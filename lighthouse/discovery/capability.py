"""
capability.py — Capability matching engine for fleet agents.

Reads CAPABILITY.toml files from agent vessels and matches agents
to tasks based on confidence scores and recency weights.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from ..utils.github import GitHubClient

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


def recency_weight(last_used: str) -> float:
    """Calculate recency weight from ISO date string."""
    try:
        dt = datetime.fromisoformat(last_used.replace("Z", "+00:00")).replace(tzinfo=None)
        from datetime import timezone
        days = (datetime.now(timezone.utc).replace(tzinfo=None) - dt).days
        if days < 1:
            return 1.0
        if days < 3:
            return 0.9
        if days < 7:
            return 0.7
        if days < 30:
            return 0.5
        return 0.3
    except (ValueError, TypeError, AttributeError):
        return 0.3


class CapabilityMatcher:
    """
    Matches fleet agents to tasks based on declared capabilities.

    Scans CAPABILITY.toml files across the fleet and provides
    capability lookup, specialist finding, and profile generation.
    """

    def __init__(self, client: GitHubClient):
        self.client = client
        self._agents: List[Dict] = []

    def scan_capabilities(self, repos: Optional[List[Dict]] = None) -> List[Dict]:
        """Scan all repos for CAPABILITY.toml files and build agent list."""
        if repos is None:
            repos = self.client.list_org_repos()

        agents = []
        for repo in repos:
            full_name = repo["full_name"]
            content = self._fetch_capability_toml(full_name)
            if content and "agent" in content:
                agents.append(content)

        self._agents = agents
        return agents

    def _fetch_capability_toml(self, repo_full_name: str) -> Optional[Dict]:
        """Fetch and parse CAPABILITY.toml from a repo."""
        content = self.client.get_file_content(repo_full_name, "CAPABILITY.toml")
        if content:
            try:
                return tomllib.loads(content)
            except Exception:
                return None
        return None

    def find_specialists(
        self,
        capability: str,
        min_confidence: float = 0.5,
        prefer_recent: bool = True,
    ) -> List[Dict]:
        """Find agents with a specific capability, ranked by score."""
        results = []
        for agent in self._agents:
            caps = agent.get("capabilities", {})
            cap = caps.get(capability)
            if cap and cap.get("confidence", 0) >= min_confidence:
                conf = cap["confidence"]
                rec = recency_weight(cap.get("last_used", "2000-01-01"))
                score = (conf * rec) if prefer_recent else conf
                results.append({
                    "name": agent["agent"].get("name", "unknown"),
                    "avatar": agent["agent"].get("avatar", "?"),
                    "confidence": conf,
                    "recency": rec,
                    "score": score,
                    "description": cap.get("description", ""),
                    "home_repo": agent["agent"].get("home_repo", ""),
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def get_capability_map(self) -> Dict[str, List[Dict]]:
        """Build a complete capability-to-agent map across the fleet."""
        cap_map: Dict[str, List[Dict]] = {}
        for agent in self._agents:
            for cap_name, cap_data in agent.get("capabilities", {}).items():
                if cap_name not in cap_map:
                    cap_map[cap_name] = []
                cap_map[cap_name].append({
                    "agent": agent["agent"].get("name", "?"),
                    "confidence": cap_data.get("confidence", 0),
                })
        return cap_map

    def get_agent_profile(self, agent_name: str) -> Dict[str, float]:
        """Get capability confidence profile for a specific agent."""
        for agent in self._agents:
            if agent["agent"].get("name") == agent_name:
                profile = {}
                for cap_name, cap_data in agent.get("capabilities", {}).items():
                    profile[cap_name] = cap_data.get("confidence", 0)
                return profile
        return {}

    def find_best_for_task(
        self,
        required_skills: List[str],
        min_confidence: float = 0.5,
    ) -> List[Dict]:
        """Find the best agent for a task requiring multiple skills."""
        agent_scores: Dict[str, float] = {}
        agent_details: Dict[str, Dict] = {}

        for agent in self._agents:
            name = agent["agent"].get("name", "unknown")
            caps = agent.get("capabilities", {})

            matched = 0
            total_score = 0.0
            for skill in required_skills:
                cap = caps.get(skill)
                if cap and cap.get("confidence", 0) >= min_confidence:
                    matched += 1
                    conf = cap["confidence"]
                    rec = recency_weight(cap.get("last_used", "2000-01-01"))
                    total_score += conf * rec

            if matched > 0:
                coverage = matched / len(required_skills)
                avg_score = total_score / matched
                agent_scores[name] = avg_score * coverage
                agent_details[name] = {
                    "name": name,
                    "avatar": agent["agent"].get("avatar", "?"),
                    "skills_matched": matched,
                    "skills_total": len(required_skills),
                    "coverage": coverage,
                    "avg_score": avg_score,
                    "composite": avg_score * coverage,
                    "home_repo": agent["agent"].get("home_repo", ""),
                }

        ranked = sorted(agent_details.values(), key=lambda x: x["composite"], reverse=True)
        return ranked
