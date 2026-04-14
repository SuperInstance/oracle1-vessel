"""
scanner.py — Refactored beachcomb scanner using the unified GitHub client.

Scans fleet repos for new forks, pull requests, and message-in-a-bottle
folders from external contributors. Produces structured reports in both
Markdown and JSON formats.
"""

import json
import os
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.github import GitHubClient


class BeachcombScanner:
    """
    Fleet-wide scanner for forks, PRs, and bottles.

    Replaces the standalone tools/beachcomb.py with a proper class that
    integrates with the Lighthouse state management system.
    """

    def __init__(self, client: GitHubClient, state_path: Optional[str] = None):
        self.client = client
        self.state_path = Path(state_path) if state_path else Path(
            os.path.expanduser("~/.lighthouse/beachcomb-state.json")
        )
        self._state = self._load_state()
        self._new_forks: List[Dict] = []
        self._new_prs: List[Dict] = []
        self._new_bottles: List[Dict] = []

    def _load_state(self) -> Dict:
        """Load or create beachcomb state."""
        if self.state_path.exists():
            with open(self.state_path) as f:
                return json.load(f)
        return {
            "known_forks": {},
            "known_prs": {},
            "external_bottles": {},
            "last_scan": None,
            "scan_count": 0,
        }

    def _save_state(self) -> None:
        """Persist state to disk."""
        self._state["last_scan"] = datetime.now(UTC).isoformat()
        self._state["scan_count"] = self._state.get("scan_count", 0) + 1
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w") as f:
            json.dump(self._state, f, indent=2)

    def scan_forks(self, repo_limit: int = 30) -> List[Dict]:
        """Scan fleet repos for new forks from external users."""
        repos = self.client.list_org_repos(per_page=100)
        if not repos:
            return []

        new_forks = []
        for repo in repos[:repo_limit]:
            repo_name = repo["name"]
            forks = self.client.list_forks(repo_name)
            for fork in forks:
                fork_owner = fork["owner"]["login"]
                if fork_owner == self.client.org:
                    continue

                key = f"{repo_name}/{fork_owner}"
                if key in self._state["known_forks"]:
                    continue

                # Check for message-in-a-bottle in the fork
                has_bottle = False
                messages_from = []
                bottle_contents = self.client.get_file(repo_name, "message-in-a-bottle")
                if bottle_contents and isinstance(bottle_contents, list):
                    has_bottle = True
                    for_fleet = self.client.get_file(
                        repo_name, "message-in-a-bottle/for-fleet"
                    )
                    if for_fleet and isinstance(for_fleet, list):
                        messages_from = [
                            item["name"]
                            for item in for_fleet
                            if item.get("type") == "dir"
                        ]

                entry = {
                    "fork_owner": fork_owner,
                    "repo": repo_name,
                    "fork_url": fork["html_url"],
                    "has_bottle": has_bottle,
                    "messages_from": messages_from,
                    "detected": datetime.now(UTC).isoformat(),
                }
                self._state["known_forks"][key] = entry
                new_forks.append(entry)

        self._new_forks = new_forks
        return new_forks

    def scan_prs(self, repo_limit: int = 20) -> List[Dict]:
        """Scan for new pull requests from external contributors."""
        repos = self.client.list_org_repos(per_page=100)
        if not repos:
            return []

        new_prs = []
        for repo in repos[:repo_limit]:
            repo_name = repo["name"]
            prs = self.client.list_prs(repo_name)
            for pr in prs:
                pr_user = pr["user"]["login"]
                if pr_user == self.client.org:
                    continue

                pr_id = f"{repo_name}/#{pr['number']}"
                if pr_id in self._state["known_prs"]:
                    continue

                entry = {
                    "repo": repo_name,
                    "number": pr["number"],
                    "user": pr_user,
                    "title": pr["title"],
                    "url": pr["html_url"],
                    "detected": datetime.now(UTC).isoformat(),
                }
                self._state["known_prs"][pr_id] = entry
                new_prs.append(entry)

        self._new_prs = new_prs
        return new_prs

    def scan_external_bottles(self) -> List[Dict]:
        """Check known fork owners for personal repos with bottles."""
        owners_seen = {
            fork["fork_owner"]
            for fork in self._state["known_forks"].values()
        }

        new_bottles = []
        for owner in owners_seen:
            user_repos = self.client.get(f"/users/{owner}/repos", {
                "per_page": "10",
                "sort": "updated",
            })
            if not user_repos:
                continue

            for repo in user_repos:
                bottle = self.client.get(
                    f"/repos/{owner}/{repo['name']}/contents/message-in-a-bottle"
                )
                if bottle and isinstance(bottle, list):
                    key = f"external/{owner}/{repo['name']}"
                    if key not in self._state.get("external_bottles", {}):
                        entry = {
                            "owner": owner,
                            "repo": repo["name"],
                            "detected": datetime.now(UTC).isoformat(),
                        }
                        self._state.setdefault("external_bottles", {})[key] = entry
                        new_bottles.append(entry)

        self._new_bottles = new_bottles
        return new_bottles

    def run_full_scan(self, repo_limit: int = 30) -> Dict[str, Any]:
        """Run all scans and return a combined result."""
        forks = self.scan_forks(repo_limit)
        prs = self.scan_prs(repo_limit)
        bottles = self.scan_external_bottles()
        self._save_state()

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "new_forks": forks,
            "new_prs": prs,
            "new_bottles": bottles,
            "totals": {
                "known_forks": len(self._state["known_forks"]),
                "known_prs": len(self._state["known_prs"]),
                "external_bottles": len(self._state.get("external_bottles", {})),
                "scan_count": self._state.get("scan_count", 0),
            },
            "has_new_activity": bool(forks or prs or bottles),
        }

    def generate_report(self, results: Optional[Dict] = None) -> str:
        """Generate a Markdown beachcomb report."""
        if results is None:
            results = {
                "new_forks": self._new_forks,
                "new_prs": self._new_prs,
                "new_bottles": self._new_bottles,
                "totals": {
                    "known_forks": len(self._state.get("known_forks", {})),
                    "known_prs": len(self._state.get("known_prs", {})),
                    "external_bottles": len(self._state.get("external_bottles", {})),
                },
            }

        lines = [
            f"# Beachcomb Report -- {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC\n",
            "## Summary",
            f"- New forks: {len(results['new_forks'])}",
            f"- New PRs: {len(results['new_prs'])}",
            f"- New external bottles: {len(results['new_bottles'])}",
            f"- Total known forks: {results['totals']['known_forks']}",
            f"- Total known PRs: {results['totals']['known_prs']}",
            "",
        ]

        if results["new_forks"]:
            lines.append("## New Forks")
            for f in results["new_forks"]:
                icon = "[bottle]" if f["has_bottle"] else ""
                lines.append(f"- **{f['fork_owner']}** forked `{f['repo']}` {icon}")
                if f["messages_from"]:
                    lines.append(f"  - Messages from: {', '.join(f['messages_from'])}")
            lines.append("")

        if results["new_prs"]:
            lines.append("## New Pull Requests")
            for pr in results["new_prs"]:
                lines.append(f"- **{pr['repo']}#{pr['number']}** from {pr['user']}: {pr['title']}")
                lines.append(f"  -> {pr['url']}")
            lines.append("")

        if results["new_bottles"]:
            lines.append("## External Bottles Found")
            for b in results["new_bottles"]:
                lines.append(f"- **{b['owner']}** has bottle in `{b['repo']}`")
            lines.append("")

        if not results["new_forks"] and not results["new_prs"] and not results["new_bottles"]:
            lines.append("*No new activity this scan.*\n")

        return "\n".join(lines)
