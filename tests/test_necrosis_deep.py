"""
Comprehensive tests for the Necrosis Detection System.

Tests cover:
- NecrosisLevel classification thresholds
- _days_since() time computation
- Individual system checks (7 systems)
- Full audit with all systems
- Fleet audit with multiple repos
- Report generation (markdown/dict)
- Edge cases (None timestamps, bad data)
"""

import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import MagicMock

from lighthouse.health.necrosis import (
    NecrosisLevel,
    NecrosisDetector,
    NecrosisReport,
    SystemResult,
    THRESHOLDS,
)


def iso_days_ago(days: float) -> str:
    """Generate an ISO timestamp N days ago."""
    return (datetime.now(UTC) - timedelta(days=days)).isoformat()


class TestNecrosisLevel:
    def test_levels_exist(self):
        assert NecrosisLevel.HEALTHY
        assert NecrosisLevel.AGING
        assert NecrosisLevel.STALE
        assert NecrosisLevel.AT_RISK
        assert NecrosisLevel.NECROTIC

    def test_level_ordering(self):
        """Levels should be ordered by severity."""
        levels = list(NecrosisLevel)
        assert levels.index(NecrosisLevel.HEALTHY) < levels.index(NecrosisLevel.NECROTIC)


class TestThresholds:
    def test_all_systems_have_thresholds(self):
        systems = [
            "commit_frequency", "diary_staleness", "bottle_silence",
            "task_stagnation", "capability_drift", "branch_divergence",
            "fleet_isolation",
        ]
        for sys_name in systems:
            assert sys_name in THRESHOLDS

    def test_thresholds_have_all_levels(self):
        for sys_name, thresholds in THRESHOLDS.items():
            assert "aging" in thresholds
            assert "stale" in thresholds
            assert "at_risk" in thresholds
            assert "necrotic" in thresholds

    def test_thresholds_ordered(self):
        for sys_name, t in THRESHOLDS.items():
            assert t["aging"] < t["stale"]
            assert t["stale"] < t["at_risk"]
            assert t["at_risk"] < t["necrotic"]


class TestClassifyLevel:
    def setup_method(self):
        self.detector = NecrosisDetector()

    def test_healthy(self):
        thresholds = THRESHOLDS["commit_frequency"]
        level = self.detector._classify_level(1.0, thresholds)
        assert level == NecrosisLevel.HEALTHY

    def test_aging(self):
        thresholds = THRESHOLDS["commit_frequency"]
        level = self.detector._classify_level(10.0, thresholds)
        assert level == NecrosisLevel.AGING

    def test_stale(self):
        thresholds = THRESHOLDS["commit_frequency"]
        level = self.detector._classify_level(35.0, thresholds)
        assert level == NecrosisLevel.STALE

    def test_at_risk(self):
        thresholds = THRESHOLDS["commit_frequency"]
        level = self.detector._classify_level(65.0, thresholds)
        assert level == NecrosisLevel.AT_RISK

    def test_necrotic(self):
        thresholds = THRESHOLDS["commit_frequency"]
        level = self.detector._classify_level(100.0, thresholds)
        assert level == NecrosisLevel.NECROTIC

    def test_boundary_aging(self):
        thresholds = THRESHOLDS["commit_frequency"]
        level = self.detector._classify_level(7.0, thresholds)
        assert level == NecrosisLevel.AGING

    def test_boundary_stale(self):
        thresholds = THRESHOLDS["commit_frequency"]
        level = self.detector._classify_level(30.0, thresholds)
        assert level == NecrosisLevel.STALE


class TestDaysSince:
    def setup_method(self):
        self.detector = NecrosisDetector()

    def test_none_returns_inf(self):
        assert self.detector._days_since(None) == float("inf")

    def test_empty_string_returns_inf(self):
        assert self.detector._days_since("") == float("inf")

    def test_recent_timestamp(self):
        ts = datetime.now(UTC).isoformat()
        days = self.detector._days_since(ts)
        assert days < 0.01  # basically now

    def test_old_timestamp(self):
        ts = iso_days_ago(10)
        days = self.detector._days_since(ts)
        assert 9.9 < days < 10.1

    def test_invalid_format_returns_inf(self):
        assert self.detector._days_since("not-a-timestamp") == float("inf")

    def test_z_suffix_handled(self):
        ts = (datetime.now(UTC) - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        days = self.detector._days_since(ts)
        assert 4.9 < days < 5.1

    def test_never_negative(self):
        """Future timestamps should return 0, not negative."""
        future = (datetime.now(UTC) + timedelta(days=10)).isoformat()
        days = self.detector._days_since(future)
        assert days >= 0


class TestSystemChecks:
    def setup_method(self):
        self.detector = NecrosisDetector()

    # Commit frequency
    def test_commit_frequency_healthy(self):
        result = self.detector.check_commit_frequency(iso_days_ago(1))
        assert result.level == NecrosisLevel.HEALTHY
        assert not result.is_violation

    def test_commit_frequency_necrotic(self):
        result = self.detector.check_commit_frequency(iso_days_ago(100))
        assert result.level == NecrosisLevel.NECROTIC
        assert result.is_violation

    def test_commit_frequency_none(self):
        result = self.detector.check_commit_frequency(None)
        assert result.level == NecrosisLevel.NECROTIC
        assert result.is_violation

    # Diary staleness
    def test_diary_staleness_healthy(self):
        result = self.detector.check_diary_staleness(iso_days_ago(5))
        assert result.level == NecrosisLevel.HEALTHY

    def test_diary_staleness_none(self):
        result = self.detector.check_diary_staleness(None)
        assert result.level == NecrosisLevel.NECROTIC
        assert "No diary" in result.details

    # Bottle silence
    def test_bottle_silence_healthy(self):
        result = self.detector.check_bottle_silence(iso_days_ago(3))
        assert result.level == NecrosisLevel.HEALTHY

    def test_bottle_silence_none(self):
        result = self.detector.check_bottle_silence(None)
        assert result.level == NecrosisLevel.NECROTIC

    # Task stagnation
    def test_task_stagnation_stale(self):
        result = self.detector.check_task_stagnation(iso_days_ago(20))
        assert result.level == NecrosisLevel.STALE
        assert result.is_violation

    # Capability drift
    def test_capability_drift_aging(self):
        result = self.detector.check_capability_drift(iso_days_ago(20))
        assert result.level == NecrosisLevel.AGING

    # Branch divergence
    def test_branch_divergence_aligned(self):
        result = self.detector.check_branch_divergence(0, 0)
        assert result.level == NecrosisLevel.HEALTHY
        assert not result.is_violation

    def test_branch_divergence_behind(self):
        result = self.detector.check_branch_divergence(0, 60)
        assert result.is_violation

    # Fleet isolation
    def test_fleet_isolation_healthy(self):
        result = self.detector.check_fleet_isolation(iso_days_ago(5))
        assert result.level == NecrosisLevel.HEALTHY


class TestFullAudit:
    def setup_method(self):
        self.detector = NecrosisDetector()

    def test_healthy_repo(self):
        report = self.detector.audit(
            target="healthy-repo",
            pushed_at=iso_days_ago(1),
            last_diary=iso_days_ago(2),
            last_bottle=iso_days_ago(3),
            last_task_update=iso_days_ago(1),
            last_capability_update=iso_days_ago(5),
            main_ahead=0,
            branch_ahead=0,
            last_cross_activity=iso_days_ago(2),
        )
        assert report.overall_level == NecrosisLevel.HEALTHY
        assert report.total_violations == 0
        assert len(report.systems) == 7

    def test_necrotic_repo(self):
        report = self.detector.audit(
            target="dead-repo",
            pushed_at=iso_days_ago(100),
            last_diary=iso_days_ago(100),
            last_bottle=iso_days_ago(100),
            last_task_update=iso_days_ago(100),
            last_capability_update=iso_days_ago(100),
            # branch_divergence defaults to (0,0) which is healthy
            last_cross_activity=iso_days_ago(100),
        )
        assert report.overall_level == NecrosisLevel.NECROTIC
        # 6 of 7 systems are violations (branch_divergence is healthy at 0,0)
        assert report.total_violations == 6

    def test_mixed_repo(self):
        """Some systems healthy, some stale."""
        report = self.detector.audit(
            target="mixed-repo",
            pushed_at=iso_days_ago(2),  # healthy
            last_diary=iso_days_ago(20),  # aging
            last_bottle=iso_days_ago(35),  # at_risk (bottle thresholds: 7/14/30/60)
            last_task_update=iso_days_ago(1),  # healthy
            last_capability_update=iso_days_ago(5),  # healthy
            last_cross_activity=iso_days_ago(3),  # healthy
        )
        # bottle_silence at 35 days = at_risk (threshold 30)
        assert report.overall_level == NecrosisLevel.AT_RISK
        assert report.total_violations >= 1

    def test_recommendations_generated(self):
        report = self.detector.audit(
            target="stale-repo",
            pushed_at=iso_days_ago(50),
            last_diary=None,
            last_bottle=None,
        )
        assert len(report.recommendations) > 0

    def test_audit_stores_report(self):
        report = self.detector.audit(target="stored-repo")
        assert "stored-repo" in self.detector._reports


class TestReportFormats:
    def setup_method(self):
        self.detector = NecrosisDetector()
        self.report = self.detector.audit(
            target="test-repo",
            pushed_at=iso_days_ago(1),
            last_diary=iso_days_ago(1),
            last_bottle=iso_days_ago(1),
            last_task_update=iso_days_ago(1),
            last_capability_update=iso_days_ago(1),
            last_cross_activity=iso_days_ago(1),
        )

    def test_to_markdown_contains_title(self):
        md = self.report.to_markdown()
        assert "Necrosis Audit: test-repo" in md

    def test_to_markdown_contains_level(self):
        md = self.report.to_markdown()
        assert "HEALTHY" in md

    def test_to_dict_has_required_fields(self):
        d = self.report.to_dict()
        assert "target" in d
        assert "overall_level" in d
        assert "systems" in d
        assert "recommendations" in d
        assert "total_violations" in d

    def test_system_result_to_dict(self):
        d = self.report.systems[0].to_dict()
        assert "system" in d
        assert "level" in d
        assert "days" in d


class TestFleetAudit:
    def setup_method(self):
        self.detector = NecrosisDetector()

    def test_fleet_audit_multiple_repos(self):
        repos = [
            {"name": "repo-a", "full_name": "org/repo-a", "pushed_at": iso_days_ago(1)},
            {"name": "repo-b", "full_name": "org/repo-b", "pushed_at": iso_days_ago(100)},
        ]
        summary = self.detector.audit_fleet(repos)
        assert summary["total_repos"] == 2
        assert "repo-a" not in summary["repos_needing_attention"]
        assert "org/repo-b" in summary["repos_needing_attention"]

    def test_fleet_audit_level_distribution(self):
        repos = [
            # Use full data to control health levels
            {"name": "healthy", "full_name": "org/healthy", "pushed_at": iso_days_ago(1)},
            {"name": "dead", "full_name": "org/dead", "pushed_at": iso_days_ago(100)},
        ]
        # Provide all timestamps for the healthy repo
        extra = {
            "healthy": {
                "last_diary": iso_days_ago(1),
                "last_bottle": iso_days_ago(1),
                "last_task_update": iso_days_ago(1),
                "last_capability_update": iso_days_ago(1),
                "last_cross_activity": iso_days_ago(1),
            }
        }
        summary = self.detector.audit_fleet(repos, extra)
        dist = summary["level_distribution"]
        # healthy repo should be healthy when all data provided
        assert dist["healthy"] >= 1 or dist["aging"] >= 1
        assert dist["necrotic"] >= 1

    def test_fleet_audit_sorted_by_severity(self):
        repos = [
            {"name": "healthy", "pushed_at": iso_days_ago(1)},
            {"name": "necrotic", "pushed_at": iso_days_ago(100)},
        ]
        summary = self.detector.audit_fleet(repos)
        reports = summary["reports"]
        # Worst should be first
        assert reports[0]["overall_level"] == "necrotic"

    def test_fleet_markdown_report(self):
        repos = [
            {"name": "test", "pushed_at": iso_days_ago(1)},
        ]
        summary = self.detector.audit_fleet(repos)
        md = self.detector.generate_fleet_report_markdown(summary)
        assert "Fleet Necrosis" in md
        assert "test" in md

    def test_fleet_recommendations_for_necrotic(self):
        repos = [
            {"name": "dead", "pushed_at": iso_days_ago(100)},
        ]
        summary = self.detector.audit_fleet(repos)
        assert len(summary["recommendations"]) > 0
        assert any("CRITICAL" in r for r in summary["recommendations"])


class TestSystemResult:
    def test_creation(self):
        result = SystemResult(
            system_name="test_system",
            level=NecrosisLevel.HEALTHY,
            days_since_activity=1.0,
            threshold=THRESHOLDS["commit_frequency"],
        )
        assert result.system_name == "test_system"
        assert result.level == NecrosisLevel.HEALTHY
        assert not result.is_violation

    def test_to_dict(self):
        result = SystemResult(
            system_name="test",
            level=NecrosisLevel.STALE,
            days_since_activity=30.0,
            threshold={"aging": 7, "stale": 30, "at_risk": 60, "necrotic": 90},
            details="test details",
            is_violation=True,
        )
        d = result.to_dict()
        assert d["level"] == "stale"
        assert d["is_violation"] is True


class TestAuditFromRepoData:
    def test_audit_from_github_data(self):
        detector = NecrosisDetector()
        repo = {
            "name": "test-repo",
            "full_name": "org/test-repo",
            "pushed_at": iso_days_ago(1),
        }
        # Provide all timestamps so it's actually healthy
        extra = {
            "last_diary": iso_days_ago(1),
            "last_bottle": iso_days_ago(1),
            "last_task_update": iso_days_ago(1),
            "last_capability_update": iso_days_ago(1),
            "last_cross_activity": iso_days_ago(1),
        }
        report = detector.audit_from_repo_data(repo, extra)
        assert report.target == "org/test-repo"
        assert report.overall_level == NecrosisLevel.HEALTHY

    def test_audit_with_extra_data(self):
        detector = NecrosisDetector()
        repo = {"name": "test", "pushed_at": iso_days_ago(1)}
        extra = {"last_diary": iso_days_ago(50)}
        report = detector.audit_from_repo_data(repo, extra)
        # Should detect stale diary
        diary_system = next(s for s in report.systems if s.system_name == "diary_staleness")
        assert diary_system.is_violation
