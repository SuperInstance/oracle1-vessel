"""
infer.py — Context Inference Protocol implementation.

Reads an agent's recent commits to infer current expertise and context.
Enables synergy detection when two agents have complementary knowledge.
"""

import re
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from ..utils.github import GitHubClient


# Domain keywords extracted from fleet commit history
DOMAIN_KEYWORDS = [
    "cuda", "rust", "gpu", "trust", "confidence", "genome", "gene",
    "enzyme", "protein", "rna", "flux", "bytecode", "isa", "opcode",
    "runtime", "vm", "vocabulary", "protocol", "i2i", "fleet",
    "vessel", "lighthouse", "diary", "taskboard", "test", "fix",
    "build", "compile", "benchmark", "profile", "coverage", "crypto",
    "wasm", "a2a", "signal", "mud", "holodeck", "bridge", "crdt",
]

LANG_MAP = {
    ".rs": "Rust", ".py": "Python", ".go": "Go",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".c": "C", ".h": "C", ".cpp": "C++", ".hpp": "C++",
    ".md": "Documentation", ".json": "Configuration",
    ".toml": "Configuration", ".yaml": "Configuration", ".yml": "Configuration",
    ".zig": "Zig", ".java": "Java", ".swift": "Swift",
}

# Synergy pairs: when two topics co-occur, suggest collaboration
SYNERGY_PAIRS = {
    ("cuda", "gpu"): "GPU computing -- could collaborate on batch FLUX execution",
    ("rust", "trust"): "Trust engine -- could wire into I2I protocol",
    ("flux", "isa"): "ISA convergence -- could unify opcode numbering",
    ("flux", "bytecode"): "Bytecode optimization -- could profile and optimize",
    ("vocabulary", "protocol"): "Protocol vocabulary -- could define fleet communication terms",
    ("diary", "test"): "Testing expertise -- could fix broken test suites",
    ("coverage", "benchmark"): "Performance -- could optimize fleet runtimes",
    ("crdt", "protocol"): "CRDT coordination -- could build distributed fleet state",
    ("crdt", "git"): "Git-native CRDTs -- could merge-aware fleet coordination",
    ("holodeck", "bridge"): "MUD bridge -- could connect holodeck to fleet API",
}


class ContextInferrer:
    """
    Infers agent expertise and context from commit history.

    By watching what repos an agent commits to, what files they change,
    and what their diary/taskboard says, other agents can infer what
    that agent is currently knowledgeable about.
    """

    def __init__(self, client: GitHubClient):
        self.client = client

    def infer_expertise(
        self, owner: str, repos: List[str], hours: int = 24
    ) -> Dict[str, Any]:
        """
        Infer what an agent currently knows from their recent commits.

        Returns files_touched, topics, languages, commit_messages, and
        total_commits as a structured dict.
        """
        files_touched = Counter()
        topics = Counter()
        languages = Counter()
        commit_messages: List[str] = []

        since = (
            datetime.now(UTC) - timedelta(hours=hours)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        for repo in repos:
            commits = self.client.get_commits(repo, since=since)
            for c in commits:
                msg = c.get("commit", {}).get("message", "")
                commit_messages.append(msg)

                sha = c.get("sha", "")
                if sha:
                    detail = self.client.get_commit_detail(repo, sha)
                    if detail and isinstance(detail, dict):
                        for f in detail.get("files", []):
                            fname = f.get("filename", "")
                            files_touched[fname] += 1

                            ext = _get_extension(fname)
                            if ext in LANG_MAP:
                                languages[LANG_MAP[ext]] += 1

                keywords = re.findall(
                    r"\b(" + "|".join(DOMAIN_KEYWORDS) + r")\b",
                    msg.lower(),
                )
                for kw in keywords:
                    topics[kw] += 1

        return {
            "files_touched": dict(files_touched.most_common(20)),
            "topics": dict(topics.most_common(15)),
            "languages": dict(languages.most_common(10)),
            "recent_messages": [m[:100] for m in commit_messages[:10]],
            "total_commits": len(commit_messages),
        }

    def read_agent_state(self, owner: str, vessel_repo: str) -> Dict[str, Any]:
        """Read an agent's vessel for current state (TASKBOARD, DIARY, CHARTER)."""
        state: Dict[str, Any] = {}

        # Read TASKBOARD
        content = self.client.get_file_content(vessel_repo, "TASKBOARD.md")
        if content:
            state["taskboard"] = content[:500]

        # Read latest diary entry
        diary_dir = self.client.get(f"/repos/{owner}/{vessel_repo}/contents/DIARY")
        if isinstance(diary_dir, list) and diary_dir:
            latest = sorted(diary_dir, key=lambda x: x["name"], reverse=True)[0]
            diary_content = self.client.get_file_content(
                vessel_repo, f"DIARY/{latest['name']}"
            )
            if diary_content:
                state["latest_diary"] = {
                    "file": latest["name"],
                    "content": diary_content[:1000],
                }

        # Read CHARTER for capabilities
        charter = self.client.get_file_content(vessel_repo, "CHARTER.md")
        if charter:
            state["charter_summary"] = charter[:300]

        return state

    def find_synergies(self, topics: Dict[str, int]) -> List[str]:
        """Find collaboration opportunities based on active topics."""
        topic_set = set(topics.keys())
        synergies = []
        for (a, b), desc in SYNERGY_PAIRS.items():
            if a in topic_set or b in topic_set:
                synergies.append(desc)
        return synergies

    def generate_synergy_report(
        self, agent_name: str, expertise: Dict, state: Dict
    ) -> str:
        """Generate a full context inference and synergy report."""
        lines = [
            f"# Context Inference: {agent_name}\n",
            f"*Generated {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC by Lighthouse*\n",
            "## Current Active Context\n",
        ]

        if expertise["topics"]:
            lines.append("**Active Topics:**")
            for topic, count in sorted(
                expertise["topics"].items(), key=lambda x: -x[1]
            )[:10]:
                bar = "#" * min(count, 10)
                lines.append(f"  {bar} **{topic}** ({count} mentions)")
            lines.append("")

        if expertise["languages"]:
            lines.append("**Languages in Use:**")
            for lang, count in sorted(
                expertise["languages"].items(), key=lambda x: -x[1]
            )[:5]:
                lines.append(f"  - {lang}: {count} files")
            lines.append("")

        if expertise["total_commits"] > 0:
            lines.append(
                f"**Commit velocity:** {expertise['total_commits']} commits in last 24h\n"
            )

        if expertise["recent_messages"]:
            lines.append("## Recent Activity\n")
            for msg in expertise["recent_messages"][:5]:
                lines.append(f"- {msg}")
            lines.append("")

        synergies = self.find_synergies(expertise["topics"])
        lines.append("## Synergy Opportunities\n")
        if synergies:
            for s in synergies[:5]:
                lines.append(f"- [+] {s}")
        else:
            lines.append("- Need more data to identify synergies")
        lines.append("")

        return "\n".join(lines)


def _get_extension(filename: str) -> str:
    """Extract file extension from filename."""
    dot = filename.rfind(".")
    if dot >= 0:
        return filename[dot:].lower()
    return ""
