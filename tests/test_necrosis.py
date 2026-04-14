#!/usr/bin/env python3
"""
test_necrosis.py — Tests for the fleet necrosis detection system.
"""

import json
import os
import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lighthouse.health.necrosis import (
    NecrosisDetector,
    NecrosisLevel,
    NecrosisReport,
    SystemResult,
    THRESHOLDS,
)


class TestNecrosisLevel(unittest.TestCase):
    """Test the NecrosisLevel enum."""

    def test_all_levels_exist(self):
        """Should have 5 severity levels."""
        levels = list(NecrosisLevel)
        self.assertEqual(len(levels), 5)
        self.assertIn(NecrosisLevel.HEALTHY, levels)
        self.assertIn(NecrosisLevel.AGING, levels)
        self.assertIn(NecrosisLevel.STALE, levels)
        self.assertIn(NecrosisLevel.AT_RISK, levels)
        self.assertIn(NecrosisLevel.NECROTIC, levels)

    def test_level_values(self):
        """Each level should have a string value."""
        for level in NecrosisLevel:
            self.assertIsInstance(level.value, str)


class TestThresholds(unittest.TestCase):
    """Test the threshold configuration."""

    def test_all_systems_have_thresholds(self):
        """All 7 systems should have thresholds."""
        expected_systems = [
            "commit_frequency", "diary_staleness", "bottle_silence",
            "task_stagnation", "capability_drift", "branch_divergence",
            "fleet_isolation",
        ]
        for system in expected_systems:
            self.assertIn(system, THRESHOLDS)
            self.assertIn("aging", THRESHOLDS[system])
            self.assertIn("stale", THRESHOLDS[system])
            self.assertIn("at_risk", THRESHOLDS[system])
            self.assertIn("necrotic", THRESHOLDS[system])

    def test_threshold_ordering(self):
        """Thresholds should be ordered: aging < stale < at_risk < necrotic."""
        for system, thresh in THRESHOLDS.items():
            self.assertLess(thresh["aging"], thresh["stale"])
            self.assertLess(thresh["stale"], thresh["at_risk"])
            self.assertLess(thresh["at_risk"], thresh["necrotic"])


class TestSystemResult(unittest.TestCase):
    """Test SystemResult dataclass."""

    def test_creation(self):
        """Should create with all fields."""
        result = SystemResult(
            system_name="test",
            level=NecrosisLevel.HEALTHY,
            days_since_activity=5.0,
            threshold={"aging": 7, "stale": 30, "at_risk": 60, "necrotic": 90},
            details="Test details",
            is_violation=False,
        )
        self.assertEqual(result.system_name, "test")
        self.assertFalse(result.is_violation)

    def test_to_dict(self):
        """Should serialize to dict."""
        result = SystemResult(
            system_name="test",
            level=NecrosisLevel.STALE,
            days_since_activity=25.0,
            threshold={"aging": 7, "stale": 30, "at_risk": 60, "necrotic": 90},
        )
        d = result.to_dict()
        self.assertEqual(d["system"], "test")
        self.assertEqual(d["level"], "stale")
        self.assertEqual(d["days"], 25.0)


class TestNecrosisDetector(unittest.TestCase):
    """Test the necrosis detection engine."""

    def setUp(self):
        self.detector = NecrosisDetector()

    def test_commit_frequency_healthy(self):
        """Recent push should be healthy."""
        recent = (datetime.now(UTC) - timedelta(hours=12)).isoformat()
        result = self.detector.check_commit_frequency(recent)
        self.assertEqual(result.level, NecrosisLevel.HEALTHY)
        self.assertFalse(result.is_violation)

    def test_commit_frequency_aging(self):
        """Push 10 days ago should be aging."""
        old = (datetime.now(UTC) - timedelta(days=10)).isoformat()
        result = self.detector.check_commit_frequency(old)
        self.assertEqual(result.level, NecrosisLevel.AGING)
        self.assertFalse(result.is_violation)

    def test_commit_frequency_stale(self):
        """Push 35 days ago should be stale (violation)."""
        old = (datetime.now(UTC) - timedelta(days=35)).isoformat()
        result = self.detector.check_commit_frequency(old)
        self.assertEqual(result.level, NecrosisLevel.STALE)
        self.assertTrue(result.is_violation)

    def test_commit_frequency_at_risk(self):
        """Push 65 days ago should be at risk."""
        old = (datetime.now(UTC) - timedelta(days=65)).isoformat()
        result = self.detector.check_commit_frequency(old)
        self.assertEqual(result.level, NecrosisLevel.AT_RISK)
        self.assertTrue(result.is_violation)

    def test_commit_frequency_necrotic(self):
        """Push 100 days ago should be necrotic."""
        old = (datetime.now(UTC) - timedelta(days=100)).isoformat()
        result = self.detector.check_commit_frequency(old)
        self.assertEqual(result.level, NecrosisLevel.NECROTIC)
        self.assertTrue(result.is_violation)

    def test_commit_frequency_none(self):
        """No push date should be necrotic."""
        result = self.detector.check_commit_frequency(None)
        self.assertEqual(result.level, NecrosisLevel.NECROTIC)

    def test_diary_staleness_healthy(self):
        """Recent diary should be healthy."""
        recent = (datetime.now(UTC) - timedelta(days=5)).isoformat()
        result = self.detector.check_diary_staleness(recent)
        self.assertEqual(result.level, NecrosisLevel.HEALTHY)

    def test_diary_staleness_no_diary(self):
        """No diary should show details."""
        result = self.detector.check_diary_staleness(None)
        self.assertIn("No diary", result.details)

    def test_bottle_silence_healthy(self):
        """Recent bottle should be healthy."""
        recent = (datetime.now(UTC) - timedelta(days=3)).isoformat()
        result = self.detector.check_bottle_silence(recent)
        self.assertEqual(result.level, NecrosisLevel.HEALTHY)

    def test_bottle_silence_no_bottle(self):
        """No bottle should show details."""
        result = self.detector.check_bottle_silence(None)
        self.assertIn("No bottles", result.details)

    def test_task_stagnation_healthy(self):
        """Recent task update should be healthy."""
        recent = (datetime.now(UTC) - timedelta(days=2)).isoformat()
        result = self.detector.check_task_stagnation(recent)
        self.assertEqual(result.level, NecrosisLevel.HEALTHY)

    def test_capability_drift_healthy(self):
        """Recent capability update should be healthy."""
        recent = (datetime.now(UTC) - timedelta(days=5)).isoformat()
        result = self.detector.check_capability_drift(recent)
        self.assertEqual(result.level, NecrosisLevel.HEALTHY)

    def test_branch_divergence_no_divergence(self):
        """No divergence should be healthy."""
        result = self.detector.check_branch_divergence(main_ahead=10, branch_ahead=0)
        self.assertEqual(result.level, NecrosisLevel.HEALTHY)
        self.assertFalse(result.is_violation)

    def test_branch_divergence_with_divergence(self):
        """Branch ahead should be violation."""
        result = self.detector.check_branch_divergence(main_ahead=0, branch_ahead=60)
        self.assertTrue(result.is_violation)

    def test_fleet_isolation_healthy(self):
        """Recent cross-activity should be healthy."""
        recent = (datetime.now(UTC) - timedelta(days=5)).isoformat()
        result = self.detector.check_fleet_isolation(recent)
        self.assertEqual(result.level, NecrosisLevel.HEALTHY)

    def test_fleet_isolation_no_activity(self):
        """No cross-activity should show details."""
        result = self.detector.check_fleet_isolation(None)
        self.assertIn("No cross-agent", result.details)


class TestNecrosisAudit(unittest.TestCase):
    """Test the full audit method."""

    def setUp(self):
        self.detector = NecrosisDetector()

    def test_healthy_audit(self):
        """All-recent audit should be fully healthy."""
        now = datetime.now(UTC).isoformat()
        report = self.detector.audit(
            target="healthy-repo",
            pushed_at=now,
            last_diary=now,
            last_bottle=now,
            last_task_update=now,
            last_capability_update=now,
            last_cross_activity=now,
        )
        self.assertEqual(report.overall_level, NecrosisLevel.HEALTHY)
        self.assertEqual(report.total_violations, 0)
        self.assertEqual(len(report.systems), 7)
        self.assertEqual(len(report.recommendations), 0)

    def test_necrotic_audit(self):
        """All-old audit should be fully necrotic."""
        old = (datetime.now(UTC) - timedelta(days=100)).isoformat()
        report = self.detector.audit(
            target="dead-repo",
            pushed_at=old,
            last_diary=old,
            last_bottle=old,
            last_task_update=old,
            last_capability_update=old,
            last_cross_activity=old,
        )
        self.assertEqual(report.overall_level, NecrosisLevel.NECROTIC)
        self.assertEqual(report.total_violations, 6)  # branch_divergence with 0,0 is healthy

    def test_mixed_audit(self):
        """Mixed timestamps should produce at_risk."""
        now = datetime.now(UTC).isoformat()
        old = (datetime.now(UTC) - timedelta(days=100)).isoformat()
        report = self.detector.audit(
            target="mixed-repo",
            pushed_at=now,
            last_diary=old,
            last_bottle=now,
            last_task_update=old,
            last_capability_update=now,
            last_cross_activity=now,
        )
        self.assertEqual(report.overall_level, NecrosisLevel.NECROTIC)
        self.assertGreater(report.total_violations, 0)

    def test_audit_from_repo_data(self):
        """Should audit from GitHub API dict."""
        repo = {
            "name": "test-repo",
            "full_name": "SuperInstance/test-repo",
            "pushed_at": (datetime.now(UTC) - timedelta(days=50)).isoformat(),
        }
        report = self.detector.audit_from_repo_data(repo)
        self.assertEqual(report.target, "SuperInstance/test-repo")
        self.assertEqual(report.target_type, "repo")
        self.assertEqual(len(report.systems), 7)

    def test_audit_recommendations(self):
        """Violations should produce recommendations."""
        old = (datetime.now(UTC) - timedelta(days=100)).isoformat()
        report = self.detector.audit(
            target="stale-repo",
            pushed_at=old,
        )
        self.assertGreater(len(report.recommendations), 0)

    def test_audit_stored(self):
        """Audit should be stored in detector's reports dict."""
        report = self.detector.audit(target="test")
        self.assertIn("test", self.detector._reports)
        self.assertEqual(self.detector._reports["test"], report)


class TestNecrosisReport(unittest.TestCase):
    """Test the NecrosisReport output formats."""

    def test_to_dict(self):
        """Should serialize to dict."""
        report = NecrosisReport(
            target="test",
            target_type="repo",
            generated_at=datetime.now(UTC).isoformat(),
        )
        d = report.to_dict()
        self.assertEqual(d["target"], "test")
        self.assertEqual(d["target_type"], "repo")
        self.assertIn("systems", d)
        self.assertIn("recommendations", d)

    def test_to_markdown(self):
        """Should generate readable Markdown."""
        report = NecrosisReport(
            target="test-repo",
            target_type="repo",
            generated_at=datetime.now(UTC).isoformat(),
            overall_level=NecrosisLevel.STALE,
            total_violations=3,
            recommendations=["Fix this repo"],
        )
        report.systems = [
            SystemResult(
                system_name="commit_frequency",
                level=NecrosisLevel.STALE,
                days_since_activity=35.0,
                threshold=THRESHOLDS["commit_frequency"],
                details="Last push: 2026-03-10",
                is_violation=True,
            ),
        ]
        md = report.to_markdown()
        self.assertIn("test-repo", md)
        self.assertIn("stale", md.lower())
        self.assertIn("commit", md.lower())
        self.assertIn("Recommendations", md)


class TestFleetAudit(unittest.TestCase):
    """Test fleet-wide necrosis auditing."""

    def setUp(self):
        self.detector = NecrosisDetector()

    def _make_repo(self, name, days_ago=5):
        pushed = (datetime.now(UTC) - timedelta(days=days_ago)).isoformat()
        return {"name": name, "full_name": f"SuperInstance/{name}", "pushed_at": pushed}

    def test_fleet_audit_healthy(self):
        """All-healthy fleet should have 0 violations."""
        repos = [self._make_repo(f"repo-{i}", days_ago=2) for i in range(10)]
        now = datetime.now(UTC).isoformat()
        extra = {f"repo-{i}": {"last_diary": now, "last_bottle": now, "last_task_update": now, "last_capability_update": now, "last_cross_activity": now} for i in range(10)}
        summary = self.detector.audit_fleet(repos, extra_data=extra)
        self.assertEqual(summary["total_repos"], 10)
        self.assertEqual(summary["level_distribution"]["healthy"], 10)
        self.assertEqual(len(summary["repos_needing_attention"]), 0)

    def test_fleet_audit_mixed(self):
        """Mixed fleet should categorize correctly."""
        now = datetime.now(UTC).isoformat()
        repos = [
            self._make_repo("fresh", days_ago=2),
            self._make_repo("old", days_ago=100),
            self._make_repo("medium", days_ago=15),
        ]
        extra = {
            "fresh": {"last_diary": now, "last_bottle": now, "last_task_update": now, "last_capability_update": now, "last_cross_activity": now},
            "old": {"last_diary": (datetime.now(UTC) - timedelta(days=100)).isoformat(), "last_bottle": (datetime.now(UTC) - timedelta(days=100)).isoformat(), "last_task_update": (datetime.now(UTC) - timedelta(days=100)).isoformat(), "last_capability_update": (datetime.now(UTC) - timedelta(days=100)).isoformat(), "last_cross_activity": (datetime.now(UTC) - timedelta(days=100)).isoformat()},
            "medium": {"last_diary": now, "last_bottle": now, "last_task_update": now, "last_capability_update": now, "last_cross_activity": now},
        }
        summary = self.detector.audit_fleet(repos, extra_data=extra)
        self.assertEqual(summary["total_repos"], 3)
        self.assertGreater(summary["level_distribution"]["necrotic"], 0)
        self.assertIn("SuperInstance/old", summary["repos_needing_attention"])

    def test_fleet_audit_recommendations(self):
        """Fleet with necrotic repos should have recommendations."""
        repos = [self._make_repo("dead", days_ago=100)]
        summary = self.detector.audit_fleet(repos)
        self.assertGreater(len(summary["recommendations"]), 0)

    def test_fleet_audit_sorted(self):
        """Reports should be sorted by severity."""
        now = datetime.now(UTC).isoformat()
        repos = [
            self._make_repo("fresh", days_ago=2),
            self._make_repo("dead", days_ago=100),
        ]
        extra = {
            "fresh": {"last_diary": now, "last_bottle": now, "last_task_update": now, "last_capability_update": now, "last_cross_activity": now},
            "dead": {"last_diary": (datetime.now(UTC) - timedelta(days=100)).isoformat(), "last_bottle": (datetime.now(UTC) - timedelta(days=100)).isoformat(), "last_task_update": (datetime.now(UTC) - timedelta(days=100)).isoformat(), "last_capability_update": (datetime.now(UTC) - timedelta(days=100)).isoformat(), "last_cross_activity": (datetime.now(UTC) - timedelta(days=100)).isoformat()},
        }
        summary = self.detector.audit_fleet(repos, extra_data=extra)
        reports = summary["reports"]
        self.assertEqual(reports[0]["target"], "SuperInstance/dead")

    def test_fleet_report_markdown(self):
        """Should generate readable fleet report."""
        repos = [
            self._make_repo("fresh", days_ago=2),
            self._make_repo("dead", days_ago=100),
        ]
        summary = self.detector.audit_fleet(repos)
        md = self.detector.generate_fleet_report_markdown(summary)
        self.assertIn("Fleet Necrosis Audit Report", md)
        self.assertIn("Level Distribution", md)
        self.assertIn("dead", md)

    def test_fleet_audit_with_extra_data(self):
        """Should incorporate extra data per repo."""
        repos = [self._make_repo("test")]
        extra = {
            "test": {
                "last_diary": (datetime.now(UTC) - timedelta(days=50)).isoformat(),
            }
        }
        summary = self.detector.audit_fleet(repos, extra_data=extra)
        self.assertEqual(summary["total_repos"], 1)

    def test_days_since_invalid(self):
        """Invalid ISO string should return infinity."""
        result = self.detector._days_since("not-a-date")
        self.assertEqual(result, float("inf"))

    def test_days_since_none(self):
        """None should return infinity."""
        result = self.detector._days_since(None)
        self.assertEqual(result, float("inf"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
