"""
fleet_scan.py — Fleet-wide repository scanner.

Scans all repos in the GitHub org, classifies them by type (agent vessel,
library, documentation, empty, template, dead), and computes health scores.
"""

import json
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from ..utils.github import GitHubClient


# Repo classification constants
class RepoType:
    AGENT_VESSEL = "agent_vessel"
    LIBRARY = "library"
    DOCUMENTATION = "documentation"
    EMPTY = "empty"
    TEMPLATE = "template"
    DEAD = "dead"
    UNKNOWN = "unknown"


REPO_TYPE_ICONS = {
    RepoType.AGENT_VESSEL: "house",
    RepoType.LIBRARY: "books",
    RepoType.DOCUMENTATION: "scroll",
    RepoType.EMPTY: "barren",
    RepoType.TEMPLATE: "copy",
    RepoType.DEAD: "skull",
    RepoType.UNKNOWN: "question",
}


class FleetScanner:
    """
    Scans all repos in the fleet org and produces a catalog.

    Classifies repos by type, detects language, tracks freshness,
    and generates health scores for the fleet.
    """

    def __init__(self, client: GitHubClient):
        self.client = client

    def scan_all_repos(self, max_pages: int = 10) -> List[Dict]:
        """Scan all repos in the org with pagination."""
        return self.client.list_org_repos(per_page=100, max_pages=max_pages)

    def classify_repo(self, repo: Dict) -> str:
        """Classify a repo into one of the RepoType categories."""
        name = repo.get("name", "")
        size = repo.get("size", 0)
        pushed = repo.get("pushed_at", "")
        forks = repo.get("forks_count", 0)

        # Check for agent vessel markers
        if "-vessel" in name or name in ("oracle1-vessel", "JetsonClaw1-vessel"):
            return RepoType.AGENT_VESSEL

        # Check repo size
        if size == 0:
            return RepoType.EMPTY

        # Check if it's a template (forked but never modified)
        if forks > 0 and pushed == repo.get("created_at", ""):
            return RepoType.TEMPLATE

        # Check if dead (no push in 90+ days)
        if pushed:
            try:
                pushed_dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
                days_since = (datetime.now(UTC) - pushed_dt).days
                if days_since > 90:
                    return RepoType.DEAD
            except (ValueError, TypeError):
                pass

        # Check language
        language = repo.get("language")
        if not language:
            # Likely docs/config-only
            return RepoType.DOCUMENTATION

        return RepoType.LIBRARY

    def compute_health_score(self, repo: Dict) -> float:
        """
        Compute a composite health score (0.0-1.0) for a repo.

        Health = 0.3*Recency + 0.2*Completeness + 0.2*Activity +
                 0.15*Standards + 0.15*Connectivity
        """
        score = 0.0

        # Recency (0.3 weight)
        pushed = repo.get("pushed_at", "")
        if pushed:
            try:
                pushed_dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
                days = (datetime.now(UTC) - pushed_dt).days
                if days < 1:
                    score += 0.3
                elif days < 7:
                    score += 0.25
                elif days < 30:
                    score += 0.15
                elif days < 90:
                    score += 0.05
            except (ValueError, TypeError):
                pass

        # Completeness (0.2 weight) — has description
        if repo.get("description"):
            score += 0.1
        if repo.get("language"):
            score += 0.05
        if repo.get("license"):
            score += 0.05

        # Activity (0.2 weight) — size as proxy
        size = repo.get("size", 0)
        if size > 1000:
            score += 0.2
        elif size > 100:
            score += 0.15
        elif size > 0:
            score += 0.08

        # Standards (0.15 weight) — has topics
        topics = repo.get("topics", [])
        if topics:
            score += 0.08
        if len(topics) >= 3:
            score += 0.07

        # Connectivity (0.15 weight) — has forks/stars/watchers
        forks = repo.get("forks_count", 0)
        stars = repo.get("stargazers_count", 0)
        if forks > 0 or stars > 0:
            score += 0.15
        elif repo.get("watchers_count", 0) > 0:
            score += 0.1

        return round(min(score, 1.0), 2)

    def build_catalog(self, repos: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Build a complete fleet catalog with classifications and health scores."""
        if repos is None:
            repos = self.scan_all_repos()

        catalog = {
            "generated_at": datetime.now(UTC).isoformat(),
            "org": self.client.org,
            "total_repos": len(repos),
            "by_type": {},
            "by_language": {},
            "by_health": {"fresh": 0, "aging": 0, "stale": 0, "dead": 0},
            "repos": [],
        }

        for repo in repos:
            repo_type = self.classify_repo(repo)
            health = self.compute_health_score(repo)
            language = repo.get("language", "None")

            entry = {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "type": repo_type,
                "health": health,
                "language": language,
                "size": repo.get("size", 0),
                "pushed_at": repo.get("pushed_at", ""),
                "description": repo.get("description", "")[:100],
            }
            catalog["repos"].append(entry)

            # Count by type
            catalog["by_type"][repo_type] = catalog["by_type"].get(repo_type, 0) + 1

            # Count by language
            catalog["by_language"][language] = catalog["by_language"].get(language, 0) + 1

            # Count by health band
            if health >= 0.6:
                catalog["by_health"]["fresh"] += 1
            elif health >= 0.3:
                catalog["by_health"]["aging"] += 1
            elif health >= 0.1:
                catalog["by_health"]["stale"] += 1
            else:
                catalog["by_health"]["dead"] += 1

        # Sort repos by health descending
        catalog["repos"].sort(key=lambda r: r["health"], reverse=True)

        return catalog

    def generate_health_report(self, catalog: Optional[Dict] = None) -> str:
        """Generate a Markdown fleet health report."""
        if catalog is None:
            catalog = self.build_catalog()

        lines = [
            f"# Fleet Health Report -- {catalog['generated_at'][:10]}",
            f"**Org:** {catalog['org']} | **Repos:** {catalog['total_repos']}",
            "",
            "## Health Distribution",
            f"- Fresh (>=0.6): {catalog['by_health']['fresh']}",
            f"- Aging (0.3-0.6): {catalog['by_health']['aging']}",
            f"- Stale (0.1-0.3): {catalog['by_health']['stale']}",
            f"- Dead (<0.1): {catalog['by_health']['dead']}",
            "",
            "## By Type",
        ]
        for rtype, count in sorted(catalog["by_type"].items(), key=lambda x: -x[1]):
            lines.append(f"- {rtype}: {count}")

        lines.append("")
        lines.append("## Top 20 Healthiest Repos")
        for repo in catalog["repos"][:20]:
            health_bar = "#" * int(repo["health"] * 20)
            lines.append(
                f"- {repo['name']:40} [{health_bar:20s}] {repo['health']:.2f} ({repo['type']})"
            )

        lines.append("")
        lines.append("## Bottom 10 (Needs Attention)")
        for repo in catalog["repos"][-10:]:
            health_bar = "#" * int(repo["health"] * 20)
            lines.append(
                f"- {repo['name']:40} [{health_bar:20s}] {repo['health']:.2f} ({repo['type']})"
            )

        return "\n".join(lines)
