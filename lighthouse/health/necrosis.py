"""
necrosis.py — Fleet necrosis detection system.

Implements 7 meta-systems for detecting at-risk repos and agents:
1. Commit frequency decay — Track commit rate over time
2. Diary staleness — No new DIARY/ entries
3. Bottle silence — No bottles sent/received
4. Task stagnation — Tasks not updated in days
5. Capability drift — CAPABILITY.toml dates going stale
6. Branch divergence — Main behind fork/PR branches
7. Fleet isolation — No cross-agent activity

Based on the theory from research/lessons-learned.md in oracle1-vessel.
"""

import json
from datetime import datetime, UTC, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class NecrosisLevel(Enum):
    """Necrosis severity levels."""
    HEALTHY = "healthy"
    AGING = "aging"
    STALE = "stale"
    AT_RISK = "at_risk"
    NECROTIC = "necrotic"


# Thresholds for each necrosis system (in days)
THRESHOLDS = {
    "commit_frequency": {
        "aging": 7,
        "stale": 30,
        "at_risk": 60,
        "necrotic": 90,
    },
    "diary_staleness": {
        "aging": 14,
        "stale": 30,
        "at_risk": 60,
        "necrotic": 90,
    },
    "bottle_silence": {
        "aging": 7,
        "stale": 14,
        "at_risk": 30,
        "necrotic": 60,
    },
    "task_stagnation": {
        "aging": 7,
        "stale": 14,
        "at_risk": 30,
        "necrotic": 60,
    },
    "capability_drift": {
        "aging": 14,
        "stale": 30,
        "at_risk": 60,
        "necrotic": 90,
    },
    "branch_divergence": {
        "aging": 7,
        "stale": 14,
        "at_risk": 30,
        "necrotic": 60,
    },
    "fleet_isolation": {
        "aging": 14,
        "stale": 30,
        "at_risk": 60,
        "necrotic": 90,
    },
}


@dataclass
class SystemResult:
    """Result of a single necrosis system check."""
    system_name: str
    level: NecrosisLevel
    days_since_activity: float
    threshold: Dict[str, int]
    details: str = ""
    is_violation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system": self.system_name,
            "level": self.level.value,
            "days": self.days_since_activity,
            "threshold": self.threshold,
            "details": self.details,
            "is_violation": self.is_violation,
        }


@dataclass
class NecrosisReport:
    """Complete necrosis audit report for a repo or agent."""
    target: str
    target_type: str  # "repo" or "agent"
    generated_at: str
    overall_level: NecrosisLevel = NecrosisLevel.HEALTHY
    systems: List[SystemResult] = field(default_factory=list)
    total_violations: int = 0
    recommendations: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Generate a Markdown necrosis report."""
        level_emoji = {
            NecrosisLevel.HEALTHY: "ok",
            NecrosisLevel.AGING: "yellow_circle",
            NecrosisLevel.STALE: "orange_circle",
            NecrosisLevel.AT_RISK: "red_circle",
            NecrosisLevel.NECROTIC: "skull",
        }

        lines = [
            f"# Necrosis Audit: {self.target}",
            f"*Generated {self.generated_at[:19]} UTC*",
            "",
            f"**Overall Level:** {self.overall_level.value.upper()}",
            f"**Violations:** {self.total_violations}/7 systems",
            "",
            "## System Results",
            "",
        ]

        for result in self.systems:
            status = "VIOLATION" if result.is_violation else "OK"
            lines.append(f"### {result.system_name.replace('_', ' ').title()} [{status}]")
            lines.append(f"- Level: {result.level.value}")
            lines.append(f"- Days since activity: {result.days_since_activity:.1f}")
            if result.details:
                lines.append(f"- Details: {result.details}")
            lines.append("")

        if self.recommendations:
            lines.append("## Recommendations")
            for rec in self.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "target_type": self.target_type,
            "generated_at": self.generated_at,
            "overall_level": self.overall_level.value,
            "total_violations": self.total_violations,
            "systems": [s.to_dict() for s in self.systems],
            "recommendations": self.recommendations,
        }


class NecrosisDetector:
    """
    Fleet necrosis detection engine.

    Runs 7 meta-systems to detect repos and agents at risk of becoming
    "Functioning Mausoleums" — structures that appear healthy but have
    stopped evolving.
    """

    def __init__(self, github_client=None):
        """
        Initialize the necrosis detector.

        Args:
            github_client: Optional GitHubClient for live API checks.
                          If None, runs in analysis-only mode.
        """
        self.client = github_client
        self._reports: Dict[str, NecrosisReport] = {}

    def _classify_level(self, days: float, thresholds: Dict[str, int]) -> NecrosisLevel:
        """Classify a time delta into a necrosis level."""
        if days >= thresholds["necrotic"]:
            return NecrosisLevel.NECROTIC
        if days >= thresholds["at_risk"]:
            return NecrosisLevel.AT_RISK
        if days >= thresholds["stale"]:
            return NecrosisLevel.STALE
        if days >= thresholds["aging"]:
            return NecrosisLevel.AGING
        return NecrosisLevel.HEALTHY

    def _days_since(self, iso_string: Optional[str]) -> float:
        """Calculate days since an ISO timestamp."""
        if not iso_string:
            return float("inf")
        try:
            dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
            delta = datetime.now(UTC) - dt
            return max(0, delta.total_seconds() / 86400)
        except (ValueError, TypeError):
            return float("inf")

    def check_commit_frequency(self, pushed_at: Optional[str]) -> SystemResult:
        """System 1: Check commit frequency decay."""
        days = self._days_since(pushed_at)
        level = self._classify_level(days, THRESHOLDS["commit_frequency"])
        details = ""
        if pushed_at:
            details = f"Last push: {pushed_at[:10]}"
        return SystemResult(
            system_name="commit_frequency",
            level=level,
            days_since_activity=days,
            threshold=THRESHOLDS["commit_frequency"],
            details=details,
            is_violation=level.value in ("stale", "at_risk", "necrotic"),
        )

    def check_diary_staleness(self, last_diary: Optional[str]) -> SystemResult:
        """System 2: Check diary staleness."""
        days = self._days_since(last_diary)
        level = self._classify_level(days, THRESHOLDS["diary_staleness"])
        details = ""
        if last_diary:
            details = f"Last diary: {last_diary[:10]}"
        else:
            details = "No diary entries found"
        return SystemResult(
            system_name="diary_staleness",
            level=level,
            days_since_activity=days,
            threshold=THRESHOLDS["diary_staleness"],
            details=details,
            is_violation=level.value in ("stale", "at_risk", "necrotic"),
        )

    def check_bottle_silence(self, last_bottle: Optional[str]) -> SystemResult:
        """System 3: Check bottle communication silence."""
        days = self._days_since(last_bottle)
        level = self._classify_level(days, THRESHOLDS["bottle_silence"])
        details = ""
        if last_bottle:
            details = f"Last bottle: {last_bottle[:10]}"
        else:
            details = "No bottles found"
        return SystemResult(
            system_name="bottle_silence",
            level=level,
            days_since_activity=days,
            threshold=THRESHOLDS["bottle_silence"],
            details=details,
            is_violation=level.value in ("stale", "at_risk", "necrotic"),
        )

    def check_task_stagnation(self, last_task_update: Optional[str]) -> SystemResult:
        """System 4: Check task board stagnation."""
        days = self._days_since(last_task_update)
        level = self._classify_level(days, THRESHOLDS["task_stagnation"])
        details = ""
        if last_task_update:
            details = f"Last task update: {last_task_update[:10]}"
        else:
            details = "No task board found"
        return SystemResult(
            system_name="task_stagnation",
            level=level,
            days_since_activity=days,
            threshold=THRESHOLDS["task_stagnation"],
            details=details,
            is_violation=level.value in ("stale", "at_risk", "necrotic"),
        )

    def check_capability_drift(self, last_capability_update: Optional[str]) -> SystemResult:
        """System 5: Check capability.toml staleness."""
        days = self._days_since(last_capability_update)
        level = self._classify_level(days, THRESHOLDS["capability_drift"])
        details = ""
        if last_capability_update:
            details = f"Last capability update: {last_capability_update[:10]}"
        else:
            details = "No CAPABILITY.toml found"
        return SystemResult(
            system_name="capability_drift",
            level=level,
            days_since_activity=days,
            threshold=THRESHOLDS["capability_drift"],
            details=details,
            is_violation=level.value in ("stale", "at_risk", "necrotic"),
        )

    def check_branch_divergence(
        self, main_ahead: int = 0, branch_ahead: int = 0
    ) -> SystemResult:
        """System 6: Check branch divergence (commits ahead/behind)."""
        divergence = branch_ahead - main_ahead
        days = max(0, divergence * 0.5)  # Rough estimate: 0.5 days per commit behind
        level = self._classify_level(days, THRESHOLDS["branch_divergence"])
        details = f"Main: {main_ahead} ahead, Branch: {branch_ahead} ahead"
        return SystemResult(
            system_name="branch_divergence",
            level=level,
            days_since_activity=days,
            threshold=THRESHOLDS["branch_divergence"],
            details=details,
            is_violation=divergence > 0 and level.value in ("stale", "at_risk", "necrotic"),
        )

    def check_fleet_isolation(self, last_cross_activity: Optional[str]) -> SystemResult:
        """System 7: Check fleet isolation (no cross-agent activity)."""
        days = self._days_since(last_cross_activity)
        level = self._classify_level(days, THRESHOLDS["fleet_isolation"])
        details = ""
        if last_cross_activity:
            details = f"Last cross-agent activity: {last_cross_activity[:10]}"
        else:
            details = "No cross-agent activity found"
        return SystemResult(
            system_name="fleet_isolation",
            level=level,
            days_since_activity=days,
            threshold=THRESHOLDS["fleet_isolation"],
            details=details,
            is_violation=level.value in ("stale", "at_risk", "necrotic"),
        )

    def audit(
        self,
        target: str,
        target_type: str = "repo",
        pushed_at: Optional[str] = None,
        last_diary: Optional[str] = None,
        last_bottle: Optional[str] = None,
        last_task_update: Optional[str] = None,
        last_capability_update: Optional[str] = None,
        main_ahead: int = 0,
        branch_ahead: int = 0,
        last_cross_activity: Optional[str] = None,
    ) -> NecrosisReport:
        """
        Run a full 7-system necrosis audit on a target.

        Args:
            target: Name of the repo or agent to audit
            target_type: "repo" or "agent"
            pushed_at: ISO timestamp of last push
            last_diary: ISO timestamp of last diary entry
            last_bottle: ISO timestamp of last bottle sent
            last_task_update: ISO timestamp of last task board update
            last_capability_update: ISO timestamp of last CAPABILITY.toml update
            main_ahead: Commits main branch is ahead
            branch_ahead: Commits branch is ahead of main
            last_cross_activity: ISO timestamp of last cross-agent activity

        Returns:
            NecrosisReport with all 7 system results
        """
        systems = [
            self.check_commit_frequency(pushed_at),
            self.check_diary_staleness(last_diary),
            self.check_bottle_silence(last_bottle),
            self.check_task_stagnation(last_task_update),
            self.check_capability_drift(last_capability_update),
            self.check_branch_divergence(main_ahead, branch_ahead),
            self.check_fleet_isolation(last_cross_activity),
        ]

        violations = sum(1 for s in systems if s.is_violation)

        # Determine overall level
        level_order = [
            NecrosisLevel.HEALTHY,
            NecrosisLevel.AGING,
            NecrosisLevel.STALE,
            NecrosisLevel.AT_RISK,
            NecrosisLevel.NECROTIC,
        ]
        worst_idx = 0
        for s in systems:
            idx = level_order.index(s.level)
            if idx > worst_idx:
                worst_idx = idx
        overall = level_order[worst_idx]

        # Generate recommendations
        recommendations = []
        for s in systems:
            if s.is_violation:
                if s.system_name == "commit_frequency":
                    recommendations.append(
                        f"{target} has not been pushed in {s.days_since_activity:.0f} days. "
                        "Consider archiving or injecting new activity."
                    )
                elif s.system_name == "diary_staleness":
                    recommendations.append(
                        f"{target} has no diary entries in {s.days_since_activity:.0f} days. "
                        "An agent without a diary is not learning."
                    )
                elif s.system_name == "bottle_silence":
                    recommendations.append(
                        f"{target} has been silent for {s.days_since_activity:.0f} days. "
                        "Leave a bottle or open an I2I issue."
                    )
                elif s.system_name == "task_stagnation":
                    recommendations.append(
                        f"{target}'s task board is {s.days_since_activity:.0f} days stale. "
                        "Update or close tasks."
                    )
                elif s.system_name == "capability_drift":
                    recommendations.append(
                        f"{target}'s capabilities are {s.days_since_activity:.0f} days old. "
                        "Update CAPABILITY.toml with current skills."
                    )
                elif s.system_name == "branch_divergence":
                    recommendations.append(
                        f"{target} has branch divergence. Consider merging or rebasing."
                    )
                elif s.system_name == "fleet_isolation":
                    recommendations.append(
                        f"{target} is isolated from the fleet for {s.days_since_activity:.0f} days. "
                        "Initiate cross-agent collaboration."
                    )

        report = NecrosisReport(
            target=target,
            target_type=target_type,
            generated_at=datetime.now(UTC).isoformat(),
            overall_level=overall,
            systems=systems,
            total_violations=violations,
            recommendations=recommendations,
        )

        self._reports[target] = report
        return report

    def audit_from_repo_data(self, repo: Dict, extra: Optional[Dict] = None) -> NecrosisReport:
        """
        Convenience method: audit a repo from GitHub API data.

        Args:
            repo: GitHub API repo dict (name, pushed_at, etc.)
            extra: Optional dict with additional timestamps:
                  last_diary, last_bottle, last_task_update,
                  last_capability_update, main_ahead, branch_ahead,
                  last_cross_activity
        """
        extra = extra or {}
        return self.audit(
            target=repo.get("full_name", repo.get("name", "unknown")),
            target_type="repo",
            pushed_at=repo.get("pushed_at"),
            last_diary=extra.get("last_diary"),
            last_bottle=extra.get("last_bottle"),
            last_task_update=extra.get("last_task_update"),
            last_capability_update=extra.get("last_capability_update"),
            main_ahead=extra.get("main_ahead", 0),
            branch_ahead=extra.get("branch_ahead", 0),
            last_cross_activity=extra.get("last_cross_activity"),
        )

    def audit_fleet(
        self, repos: List[Dict], extra_data: Optional[Dict[str, Dict]] = None
    ) -> Dict[str, Any]:
        """
        Audit the entire fleet and generate a summary report.

        Args:
            repos: List of GitHub API repo dicts
            extra_data: Optional dict mapping repo name to extra timestamps

        Returns:
            Summary dict with per-repo reports and fleet-wide statistics
        """
        extra_data = extra_data or {}
        reports = []
        level_counts = {level.value: 0 for level in NecrosisLevel}

        for repo in repos:
            name = repo.get("name", "")
            extra = extra_data.get(name, {})
            report = self.audit_from_repo_data(repo, extra)
            reports.append(report)
            level_counts[report.overall_level.value] += 1

        # Sort by severity (worst first)
        reports.sort(key=lambda r: [
            NecrosisLevel.NECROTIC,
            NecrosisLevel.AT_RISK,
            NecrosisLevel.STALE,
            NecrosisLevel.AGING,
            NecrosisLevel.HEALTHY,
        ].index(r.overall_level))

        summary = {
            "generated_at": datetime.now(UTC).isoformat(),
            "total_repos": len(repos),
            "level_distribution": level_counts,
            "reports": [r.to_dict() for r in reports],
            "repos_needing_attention": [
                r.target for r in reports
                if r.overall_level.value in ("at_risk", "necrotic")
            ],
            "recommendations": [],
        }

        # Top-level recommendations
        necrotic_count = level_counts["necrotic"]
        at_risk_count = level_counts["at_risk"]
        stale_count = level_counts["stale"]

        if necrotic_count > 0:
            summary["recommendations"].append(
                f"CRITICAL: {necrotic_count} repo(s) are necrotic. "
                "Immediate action required — archive or inject new life."
            )
        if at_risk_count > 0:
            summary["recommendations"].append(
                f"WARNING: {at_risk_count} repo(s) are at risk. "
                "Schedule intervention within 7 days."
            )
        if stale_count > 5:
            summary["recommendations"].append(
                f"NOTE: {stale_count} repo(s) are stale. "
                "Consider a fleet-wide freshness sprint."
            )

        return summary

    def generate_fleet_report_markdown(self, summary: Dict[str, Any]) -> str:
        """Generate a Markdown fleet necrosis report."""
        lines = [
            "# Fleet Necrosis Audit Report",
            f"*Generated {summary['generated_at'][:19]} UTC*",
            "",
            f"**Total repos audited:** {summary['total_repos']}",
            "",
            "## Level Distribution",
        ]

        emoji_map = {
            "healthy": "ok",
            "aging": "yellow_circle",
            "stale": "orange_circle",
            "at_risk": "red_circle",
            "necrotic": "skull",
        }

        for level, count in summary["level_distribution"].items():
            lines.append(f"- {emoji_map.get(level, '?')} {level}: {count}")

        lines.append("")

        if summary["repos_needing_attention"]:
            lines.append("## Repos Needing Attention")
            for name in summary["repos_needing_attention"]:
                lines.append(f"- {name}")
            lines.append("")

        if summary["recommendations"]:
            lines.append("## Fleet-Wide Recommendations")
            for rec in summary["recommendations"]:
                lines.append(f"- {rec}")
            lines.append("")

        # Per-repo details
        lines.append("## Per-Repo Details")
        for report_dict in summary["reports"][:20]:
            name = report_dict["target"]
            level = report_dict["overall_level"]
            violations = report_dict["total_violations"]
            lines.append(f"- **{name}**: {level} ({violations} violations)")

        return "\n".join(lines)
