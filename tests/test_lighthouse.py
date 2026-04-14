#!/usr/bin/env python3
"""
test_lighthouse.py — Comprehensive test suite for the Lighthouse package.

Tests all modules: utils (github, config), beachcomb (scanner),
discovery (fleet_scan, capability), context (infer), git (bottle, onboard).
Zero external dependencies -- uses only stdlib + unittest.mock.
"""

import json
import os
import sys
import unittest
from datetime import datetime, UTC
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lighthouse.utils.github import GitHubClient
from lighthouse.utils.config import LighthouseConfig
from lighthouse.beachcomb.scanner import BeachcombScanner
from lighthouse.discovery.fleet_scan import FleetScanner, RepoType
from lighthouse.discovery.capability import CapabilityMatcher, recency_weight
from lighthouse.context.infer import ContextInferrer, _get_extension
from lighthouse.git.bottle import BottleManager
from lighthouse.git.onboard import Onboarder


# ============================================================================
# Utility Tests
# ============================================================================


class TestGitHubClient(unittest.TestCase):
    """Test the unified GitHub API client."""

    def test_detect_token_from_env(self):
        """Token should be detected from environment variable."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token-123"}):
            client = GitHubClient()
            self.assertEqual(client.token, "test-token-123")

    def test_no_token_raises_error(self):
        """Missing token should raise ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("builtins.open", side_effect=FileNotFoundError):
                with self.assertRaises(ValueError):
                    GitHubClient()

    def test_org_default(self):
        """Default org should be SuperInstance."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            self.assertEqual(client.org, "SuperInstance")

    def test_custom_org(self):
        """Custom org should override default."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient(org="Lucineer")
            self.assertEqual(client.org, "Lucineer")

    def test_headers_contain_auth(self):
        """Headers should contain Authorization with token."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            self.assertIn("Authorization", client._headers)
            self.assertEqual(client._headers["Authorization"], "token tok")

    def test_request_count_tracks(self):
        """Request count should track API calls."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            self.assertEqual(client.request_count, 0)

    def test_get_user_success(self):
        """get_user should return user dict."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            client._GitHubClient__request_count = 0
            mock_response = {"login": "SuperInstance", "id": 123}
            with patch.object(client, "get", return_value=mock_response):
                result = client.get_user()
                self.assertEqual(result["login"], "SuperInstance")


class TestLighthouseConfig(unittest.TestCase):
    """Test the configuration system."""

    def test_default_config_values(self):
        """Config should have sensible defaults."""
        config = LighthouseConfig(config_path="/nonexistent/path.toml")
        self.assertEqual(config.org, "SuperInstance")
        self.assertEqual(config.scan_interval, 30)
        self.assertEqual(config.heartbeat_timeout_hours, 48)

    def test_get_dotted_path(self):
        """Should retrieve nested values via dotted paths."""
        config = LighthouseConfig(config_path="/nonexistent/path.toml")
        self.assertEqual(config.get("fleet.org"), "SuperInstance")
        self.assertEqual(config.get("agents.heartbeat_timeout_hours"), 48)
        self.assertIsNone(config.get("nonexistent.key"))

    def test_get_with_default(self):
        """Should return default for missing keys."""
        config = LighthouseConfig(config_path="/nonexistent/path.toml")
        self.assertEqual(config.get("missing.key", "fallback"), "fallback")

    def test_set_dotted_path(self):
        """Should set nested values via dotted paths."""
        config = LighthouseConfig(config_path="/nonexistent/path.toml")
        config.set("fleet.org", "NewOrg")
        self.assertEqual(config.get("fleet.org"), "NewOrg")

    def test_expected_agents(self):
        """Should return list of expected agents."""
        config = LighthouseConfig(config_path="/nonexistent/path.toml")
        agents = config.expected_agents
        self.assertIsInstance(agents, list)
        self.assertIn("oracle1", agents)

    def test_beachcomb_action(self):
        """Should return default beachcomb action."""
        config = LighthouseConfig(config_path="/nonexistent/path.toml")
        self.assertEqual(config.beachcomb_action, "commit")

    def test_to_dict(self):
        """Should return plain dict copy."""
        config = LighthouseConfig(config_path="/nonexistent/path.toml")
        d = config.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("fleet", d)

    def test_repr(self):
        """Should have readable repr."""
        config = LighthouseConfig(config_path="/nonexistent/path.toml")
        r = repr(config)
        self.assertIn("LighthouseConfig", r)
        self.assertIn("SuperInstance", r)


# ============================================================================
# Beachcomb Tests
# ============================================================================


class TestBeachcombScanner(unittest.TestCase):
    """Test the beachcomb scanner."""

    def _make_client(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            return client

    def test_init_creates_default_state(self):
        """Should initialize with empty state."""
        client = self._make_client()
        scanner = BeachcombScanner(client, state_path="/tmp/test-bc-state.json")
        self.assertEqual(scanner._state["known_forks"], {})
        self.assertEqual(scanner._state["known_prs"], {})

    def test_scan_forks_no_repos(self):
        """Should handle no repos gracefully."""
        client = self._make_client()
        with patch.object(client, "list_org_repos", return_value=[]):
            scanner = BeachcombScanner(client, state_path="/tmp/test-bc-1.json")
            forks = scanner.scan_forks()
            self.assertEqual(forks, [])

    def test_scan_forks_detects_new(self):
        """Should detect new forks from external users."""
        client = self._make_client()
        repos = [{"name": "test-repo", "full_name": "SuperInstance/test-repo"}]
        forks = [{"owner": {"login": "ExternalUser"}, "html_url": "https://github.com/ExternalUser/test-repo"}]

        with patch.object(client, "list_org_repos", return_value=repos):
            with patch.object(client, "list_forks", return_value=forks):
                with patch.object(client, "get", return_value=None):
                    scanner = BeachcombScanner(client, state_path="/tmp/test-bc-2.json")
                    results = scanner.scan_forks()
                    self.assertEqual(len(results), 1)
                    self.assertEqual(results[0]["fork_owner"], "ExternalUser")

    def test_scan_forks_skips_own(self):
        """Should skip forks from the same org."""
        client = self._make_client()
        repos = [{"name": "test-repo", "full_name": "SuperInstance/test-repo"}]
        forks = [{"owner": {"login": "SuperInstance"}, "html_url": "https://..."}]

        with patch.object(client, "list_org_repos", return_value=repos):
            with patch.object(client, "list_forks", return_value=forks):
                scanner = BeachcombScanner(client, state_path="/tmp/test-bc-3.json")
                results = scanner.scan_forks()
                self.assertEqual(len(results), 0)

    def test_scan_forks_ignores_known(self):
        """Should not re-report known forks."""
        client = self._make_client()
        scanner = BeachcombScanner(client, state_path="/tmp/test-bc-4.json")
        scanner._state["known_forks"]["test-repo/ExternalUser"] = {"detected": "2026-01-01"}

        repos = [{"name": "test-repo", "full_name": "SuperInstance/test-repo"}]
        forks = [{"owner": {"login": "ExternalUser"}, "html_url": "https://..."}]

        with patch.object(client, "list_org_repos", return_value=repos):
            with patch.object(client, "list_forks", return_value=forks):
                results = scanner.scan_forks()
                self.assertEqual(len(results), 0)

    def test_scan_prs_no_repos(self):
        """Should handle no repos for PR scanning."""
        client = self._make_client()
        with patch.object(client, "list_org_repos", return_value=[]):
            scanner = BeachcombScanner(client, state_path="/tmp/test-bc-5.json")
            prs = scanner.scan_prs()
            self.assertEqual(prs, [])

    def test_scan_prs_detects_new(self):
        """Should detect new PRs from external users."""
        client = self._make_client()
        repos = [{"name": "test-repo"}]
        prs = [{"user": {"login": "ExternalUser"}, "number": 42, "title": "Fix bug", "html_url": "https://..."}]

        with patch.object(client, "list_org_repos", return_value=repos):
            with patch.object(client, "list_prs", return_value=prs):
                scanner = BeachcombScanner(client, state_path="/tmp/test-bc-6.json")
                results = scanner.scan_prs()
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]["title"], "Fix bug")

    def test_run_full_scan(self):
        """Should run all scans and combine results."""
        client = self._make_client()
        scanner = BeachcombScanner(client, state_path="/tmp/test-bc-7.json")

        with patch.object(scanner, "scan_forks", return_value=[{"fork_owner": "X"}]):
            with patch.object(scanner, "scan_prs", return_value=[{"repo": "Y"}]):
                with patch.object(scanner, "scan_external_bottles", return_value=[{"owner": "Z"}]):
                    results = scanner.run_full_scan()
                    self.assertTrue(results["has_new_activity"])
                    self.assertEqual(len(results["new_forks"]), 1)
                    self.assertEqual(len(results["new_prs"]), 1)
                    self.assertEqual(len(results["new_bottles"]), 1)

    def test_generate_report_empty(self):
        """Should handle empty results in report."""
        client = self._make_client()
        scanner = BeachcombScanner(client, state_path="/tmp/test-bc-8.json")
        report = scanner.generate_report()
        self.assertIn("No new activity", report)

    def test_generate_report_with_forks(self):
        """Should include forks in report."""
        client = self._make_client()
        scanner = BeachcombScanner(client, state_path="/tmp/test-bc-9.json")
        results = {
            "new_forks": [{"fork_owner": "X", "repo": "test", "has_bottle": False, "messages_from": []}],
            "new_prs": [],
            "new_bottles": [],
            "totals": {"known_forks": 1, "known_prs": 0, "external_bottles": 0},
        }
        report = scanner.generate_report(results)
        self.assertIn("X", report)
        self.assertIn("test", report)


# ============================================================================
# Discovery Tests
# ============================================================================


class TestFleetScanner(unittest.TestCase):
    """Test the fleet scanner and health scoring."""

    def _make_client(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            return GitHubClient()

    def test_classify_agent_vessel(self):
        """Should classify -vessel repos as agent vessels."""
        client = self._make_client()
        scanner = FleetScanner(client)
        self.assertEqual(
            scanner.classify_repo({"name": "oracle1-vessel", "size": 100, "pushed_at": "2026-04-14T00:00:00Z", "created_at": "2026-04-10T00:00:00Z", "forks_count": 0}),
            RepoType.AGENT_VESSEL,
        )

    def test_classify_empty(self):
        """Should classify size-0 repos as empty."""
        client = self._make_client()
        scanner = FleetScanner(client)
        self.assertEqual(
            scanner.classify_repo({"name": "empty-repo", "size": 0, "pushed_at": "", "created_at": "", "forks_count": 0}),
            RepoType.EMPTY,
        )

    def test_classify_dead(self):
        """Should classify repos not pushed in 90+ days as dead."""
        client = self._make_client()
        scanner = FleetScanner(client)
        self.assertEqual(
            scanner.classify_repo({"name": "old-repo", "size": 100, "pushed_at": "2025-01-01T00:00:00Z", "created_at": "2025-01-01T00:00:00Z", "forks_count": 0}),
            RepoType.DEAD,
        )

    def test_classify_library(self):
        """Should classify repos with language as library."""
        client = self._make_client()
        scanner = FleetScanner(client)
        self.assertEqual(
            scanner.classify_repo({"name": "flux-runtime", "size": 500, "pushed_at": "2026-04-14T00:00:00Z", "created_at": "2026-04-10T00:00:00Z", "forks_count": 0, "language": "Python"}),
            RepoType.LIBRARY,
        )

    def test_health_score_fresh(self):
        """Fresh repos should have high health scores."""
        client = self._make_client()
        scanner = FleetScanner(client)
        score = scanner.compute_health_score({
            "pushed_at": "2026-04-14T00:00:00Z",
            "description": "A test repo",
            "language": "Python",
            "size": 2000,
            "topics": ["flux", "runtime"],
            "license": {"name": "MIT"},
            "forks_count": 5,
            "stargazers_count": 10,
        })
        self.assertGreater(score, 0.6)

    def test_health_score_dead(self):
        """Dead repos should have low health scores."""
        client = self._make_client()
        scanner = FleetScanner(client)
        score = scanner.compute_health_score({
            "pushed_at": "2020-01-01T00:00:00Z",
            "description": "",
            "language": None,
            "size": 0,
            "topics": [],
            "forks_count": 0,
            "stargazers_count": 0,
        })
        self.assertLess(score, 0.3)

    def test_build_catalog(self):
        """Should build a complete fleet catalog."""
        client = self._make_client()
        scanner = FleetScanner(client)
        repos = [
            {"name": "oracle1-vessel", "full_name": "SuperInstance/oracle1-vessel", "size": 100, "pushed_at": "2026-04-14T00:00:00Z", "created_at": "2026-04-10T00:00:00Z", "forks_count": 0, "language": None, "description": "", "topics": []},
            {"name": "flux-runtime", "full_name": "SuperInstance/flux-runtime", "size": 5000, "pushed_at": "2026-04-14T00:00:00Z", "created_at": "2026-04-10T00:00:00Z", "forks_count": 0, "language": "Python", "description": "FLUX VM", "topics": ["flux"]},
            {"name": "empty-repo", "full_name": "SuperInstance/empty-repo", "size": 0, "pushed_at": "", "created_at": "", "forks_count": 0, "language": None, "description": "", "topics": []},
        ]
        catalog = scanner.build_catalog(repos)
        self.assertEqual(catalog["total_repos"], 3)
        self.assertIn("agent_vessel", catalog["by_type"])
        self.assertIn("empty", catalog["by_type"])
        self.assertEqual(len(catalog["repos"]), 3)

    def test_health_report(self):
        """Should generate a readable health report."""
        client = self._make_client()
        scanner = FleetScanner(client)
        catalog = scanner.build_catalog([
            {"name": "test", "full_name": "SuperInstance/test", "size": 100, "pushed_at": "2026-04-14T00:00:00Z", "created_at": "2026-04-10T00:00:00Z", "forks_count": 0, "language": None, "description": "", "topics": []},
        ])
        report = scanner.generate_health_report(catalog)
        self.assertIn("Fleet Health Report", report)
        self.assertIn("Health Distribution", report)


class TestCapabilityMatcher(unittest.TestCase):
    """Test the capability matching engine."""

    def test_recency_weight_recent(self):
        """Recent dates should have high weight."""
        weight = recency_weight("2026-04-14")
        self.assertGreater(weight, 0.8)

    def test_recency_weight_old(self):
        """Old dates should have low weight."""
        weight = recency_weight("2020-01-01")
        self.assertLessEqual(weight, 0.3)

    def test_recency_weight_invalid(self):
        """Invalid dates should return default weight."""
        weight = recency_weight("not-a-date")
        self.assertEqual(weight, 0.3)

    def test_find_specialists(self):
        """Should find and rank agents by capability score."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            matcher = CapabilityMatcher(client)
            matcher._agents = [
                {
                    "agent": {"name": "Agent-A", "avatar": "A", "home_repo": "test"},
                    "capabilities": {
                        "testing": {"confidence": 0.9, "last_used": "2026-04-14", "description": "Testing expert"},
                    },
                },
                {
                    "agent": {"name": "Agent-B", "avatar": "B", "home_repo": "test"},
                    "capabilities": {
                        "testing": {"confidence": 0.7, "last_used": "2026-04-01", "description": "Good tester"},
                    },
                },
            ]
            results = matcher.find_specialists("testing", min_confidence=0.5)
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]["name"], "Agent-A")

    def test_find_specialists_no_match(self):
        """Should return empty list if no agents match."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            matcher = CapabilityMatcher(client)
            matcher._agents = []
            results = matcher.find_specialists("nonexistent")
            self.assertEqual(len(results), 0)

    def test_find_specialists_below_threshold(self):
        """Should exclude agents below confidence threshold."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            matcher = CapabilityMatcher(client)
            matcher._agents = [
                {
                    "agent": {"name": "Agent-A", "avatar": "A", "home_repo": "test"},
                    "capabilities": {
                        "testing": {"confidence": 0.3, "last_used": "2026-04-14", "description": ""},
                    },
                },
            ]
            results = matcher.find_specialists("testing", min_confidence=0.5)
            self.assertEqual(len(results), 0)

    def test_capability_map(self):
        """Should build complete capability-to-agent map."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            matcher = CapabilityMatcher(client)
            matcher._agents = [
                {
                    "agent": {"name": "Agent-A", "avatar": "A", "home_repo": "test"},
                    "capabilities": {
                        "testing": {"confidence": 0.9, "last_used": "2026-04-14"},
                        "rust": {"confidence": 0.8, "last_used": "2026-04-12"},
                    },
                },
            ]
            cap_map = matcher.get_capability_map()
            self.assertIn("testing", cap_map)
            self.assertIn("rust", cap_map)

    def test_agent_profile(self):
        """Should return capability profile for named agent."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            matcher = CapabilityMatcher(client)
            matcher._agents = [
                {
                    "agent": {"name": "Agent-A", "avatar": "A", "home_repo": "test"},
                    "capabilities": {
                        "testing": {"confidence": 0.9, "last_used": "2026-04-14"},
                    },
                },
            ]
            profile = matcher.get_agent_profile("Agent-A")
            self.assertEqual(profile["testing"], 0.9)
            self.assertEqual(matcher.get_agent_profile("Unknown"), {})

    def test_find_best_for_task(self):
        """Should rank agents by multi-skill coverage."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            matcher = CapabilityMatcher(client)
            matcher._agents = [
                {
                    "agent": {"name": "Agent-A", "avatar": "A", "home_repo": "test"},
                    "capabilities": {
                        "testing": {"confidence": 0.9, "last_used": "2026-04-14"},
                        "rust": {"confidence": 0.8, "last_used": "2026-04-14"},
                        "python": {"confidence": 0.7, "last_used": "2026-04-14"},
                    },
                },
                {
                    "agent": {"name": "Agent-B", "avatar": "B", "home_repo": "test"},
                    "capabilities": {
                        "testing": {"confidence": 0.9, "last_used": "2026-04-14"},
                    },
                },
            ]
            results = matcher.find_best_for_task(["testing", "rust", "python"])
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]["name"], "Agent-A")
            self.assertEqual(results[0]["skills_matched"], 3)


# ============================================================================
# Context Inference Tests
# ============================================================================


class TestContextInferrer(unittest.TestCase):
    """Test the context inference engine."""

    def _make_client(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            return GitHubClient()

    def test_get_extension(self):
        """Should extract file extensions correctly."""
        self.assertEqual(_get_extension("test.py"), ".py")
        self.assertEqual(_get_extension("Makefile"), "")
        self.assertEqual(_get_extension("test.test.ts"), ".ts")

    def test_infer_expertise_empty(self):
        """Should handle no commits gracefully."""
        client = self._make_client()
        inferrer = ContextInferrer(client)

        with patch.object(client, "get_commits", return_value=[]):
            result = inferrer.infer_expertise("testorg", ["repo1"])
            self.assertEqual(result["total_commits"], 0)
            self.assertEqual(result["topics"], {})

    def test_infer_expertise_with_commits(self):
        """Should extract topics and languages from commits."""
        client = self._make_client()
        inferrer = ContextInferrer(client)

        mock_commit = {
            "sha": "abc123",
            "commit": {"message": "[ORACLE1] flux bytecode runtime test fix"},
        }
        mock_detail = {
            "files": [
                {"filename": "src/vm.py", "status": "modified"},
                {"filename": "tests/test_vm.rs", "status": "added"},
                {"filename": "README.md", "status": "modified"},
            ]
        }

        with patch.object(client, "get_commits", return_value=[mock_commit]):
            with patch.object(client, "get_commit_detail", return_value=mock_detail):
                result = inferrer.infer_expertise("testorg", ["repo1"])
                self.assertEqual(result["total_commits"], 1)
                self.assertIn("flux", result["topics"])
                self.assertIn("bytecode", result["topics"])
                self.assertIn("Python", result["languages"])
                self.assertIn("Rust", result["languages"])

    def test_find_synergies(self):
        """Should find synergy pairs from topics."""
        client = self._make_client()
        inferrer = ContextInferrer(client)
        synergies = inferrer.find_synergies({"flux": 3, "isa": 2})
        self.assertTrue(len(synergies) > 0)

    def test_find_synergies_no_match(self):
        """Should return empty list for unknown topics."""
        client = self._make_client()
        inferrer = ContextInferrer(client)
        synergies = inferrer.find_synergies({"unknown_topic": 5})
        self.assertEqual(len(synergies), 0)

    def test_generate_synergy_report(self):
        """Should generate readable synergy report."""
        client = self._make_client()
        inferrer = ContextInferrer(client)
        expertise = {
            "topics": {"flux": 5, "bytecode": 3, "isa": 2},
            "languages": {"Python": 10},
            "recent_messages": ["test commit"],
            "total_commits": 5,
        }
        report = inferrer.generate_synergy_report("TestAgent", expertise, {})
        self.assertIn("TestAgent", report)
        self.assertIn("flux", report)
        self.assertIn("Synergy", report)


# ============================================================================
# Bottle Tests
# ============================================================================


class TestBottleManager(unittest.TestCase):
    """Test the Message-in-a-Bottle manager."""

    def setUp(self):
        self.test_dir = "/tmp/test-bottles"
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.mgr = BottleManager(bottle_dir=self.test_dir)

    def tearDown(self):
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_drop_creates_file(self):
        """Should create a bottle file in the correct directory."""
        path = self.mgr.drop("oracle1", "Test Subject", "Test content", sender="TestAgent")
        self.assertTrue(os.path.exists(path))
        content = Path(path).read_text(encoding="utf-8")
        self.assertIn("Test Subject", content)
        self.assertIn("Test content", content)
        self.assertIn("TestAgent", content)
        self.assertIn("oracle1", content)

    def test_drop_broadcast(self):
        """Should create a broadcast bottle."""
        path = self.mgr.drop_broadcast("Fleet Update", "All hands on deck")
        self.assertTrue(os.path.exists(path))
        self.assertIn("any-vessel", path)

    def test_list_bottles_empty(self):
        """Should return empty list when no bottles."""
        bottles = self.mgr.list_bottles()
        self.assertEqual(len(bottles), 0)

    def test_list_bottles_after_drop(self):
        """Should list dropped bottles."""
        self.mgr.drop("oracle1", "Subject 1", "Content 1")
        self.mgr.drop("oracle1", "Subject 2", "Content 2")
        bottles = self.mgr.list_bottles(target="oracle1")
        self.assertEqual(len(bottles), 2)

    def test_list_bottles_filter_by_target(self):
        """Should only list bottles for specified target."""
        self.mgr.drop("oracle1", "For Oracle", "Content")
        self.mgr.drop("jetsonclaw1", "For JC1", "Content")
        bottles = self.mgr.list_bottles(target="oracle1")
        self.assertEqual(len(bottles), 1)

    def test_search_bottles(self):
        """Should search bottles by subject."""
        self.mgr.drop("oracle1", "Test Subject Here", "Content")
        self.mgr.drop("oracle1", "Other Subject", "Content")
        results = self.mgr.search_bottles("Test")
        self.assertEqual(len(results), 1)

    def test_read_bottle(self):
        """Should read bottle content by filename."""
        self.mgr.drop("oracle1", "Readable", "This is the content")
        bottles = self.mgr.list_bottles(target="oracle1")
        filename = bottles[0]["filename"]
        content = self.mgr.read_bottle("oracle1", filename)
        self.assertIn("This is the content", content)

    def test_read_nonexistent_bottle(self):
        """Should return None for nonexistent bottle."""
        result = self.mgr.read_bottle("oracle1", "nonexistent.md")
        self.assertIsNone(result)

    def test_directories(self):
        """Should list for-{agent} directories."""
        self.mgr.drop("oracle1", "Test", "Content")
        self.mgr.drop("babel", "Test", "Content")
        dirs = self.mgr.directories
        self.assertIn("for-oracle1", dirs)
        self.assertIn("for-babel", dirs)

    def test_front_matter_parsed(self):
        """Should parse YAML front matter from bottles."""
        self.mgr.drop("oracle1", "Test", "Content", sender="Sender", bottle_type="URGENT")
        bottles = self.mgr.list_bottles(target="oracle1")
        self.assertEqual(bottles[0].get("from"), "Sender")
        self.assertEqual(bottles[0].get("to"), "oracle1")
        self.assertEqual(bottles[0].get("type"), "URGENT")

    def test_get_unread(self):
        """Should filter bottles by date."""
        self.mgr.drop("oracle1", "Recent", "Content")
        unread = self.mgr.get_unread("oracle1", last_read="2020-01-01")
        self.assertEqual(len(unread), 1)
        unread_none = self.mgr.get_unread("oracle1", last_read="2099-01-01")
        self.assertEqual(len(unread_none), 0)


# ============================================================================
# Onboarder Tests
# ============================================================================


class TestOnboarder(unittest.TestCase):
    """Test the vessel skeleton generator."""

    def _make_onboarder(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            client = GitHubClient()
            return Onboarder(client)

    def setUp(self):
        self.test_dir = "/tmp/test-onboard"
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_generate_basic_vessel(self):
        """Should generate a complete vessel skeleton."""
        onboarder = self._make_onboarder()
        result = onboarder.generate_skeleton(
            name="TestAgent",
            output_dir=self.test_dir,
        )
        self.assertTrue(os.path.exists(result["path"]))
        self.assertGreater(len(result["files"]), 10)

    def test_generate_creates_charter(self):
        """Should create CHARTER.md."""
        onboarder = self._make_onboarder()
        result = onboarder.generate_skeleton(
            name="TestAgent",
            output_dir=self.test_dir,
        )
        charter = Path(result["path"]) / "CHARTER.md"
        self.assertTrue(charter.exists())
        content = charter.read_text(encoding="utf-8")
        self.assertIn("TestAgent", content)
        self.assertIn("Purpose", content)

    def test_generate_creates_all_required_files(self):
        """Should create all Git-Agent Standard required files."""
        onboarder = self._make_onboarder()
        result = onboarder.generate_skeleton(
            name="TestAgent",
            output_dir=self.test_dir,
        )
        required = ["CHARTER.md", "STATE.md", "TASK-BOARD.md", "IDENTITY.md", "README.md"]
        for f in required:
            self.assertIn(f, result["files"], f"Missing required file: {f}")

    def test_generate_with_specialization(self):
        """Should include specialization in charter."""
        onboarder = self._make_onboarder()
        result = onboarder.generate_skeleton(
            name="TestAgent",
            specialization="CUDA computing",
            output_dir=self.test_dir,
        )
        charter = (Path(result["path"]) / "CHARTER.md").read_text(encoding="utf-8")
        self.assertIn("CUDA computing", charter)

    def test_generate_capability_toml(self):
        """Should generate valid CAPABILITY.toml."""
        onboarder = self._make_onboarder()
        result = onboarder.generate_skeleton(
            name="TestAgent",
            output_dir=self.test_dir,
        )
        cap = Path(result["path"]) / "CAPABILITY.toml"
        self.assertTrue(cap.exists())
        content = cap.read_text(encoding="utf-8")
        self.assertIn("[agent]", content)
        self.assertIn("TestAgent", content)

    def test_generate_creates_directories(self):
        """Should create all required directories."""
        onboarder = self._make_onboarder()
        result = onboarder.generate_skeleton(
            name="TestAgent",
            output_dir=self.test_dir,
        )
        dirs = ["DIARY", "for-fleet", "from-fleet", "src", "tests", "docs"]
        for d in dirs:
            self.assertTrue((Path(result["path"]) / d).exists(), f"Missing dir: {d}")

    def test_generate_creates_gitignore(self):
        """Should create .gitignore."""
        onboarder = self._make_onboarder()
        result = onboarder.generate_skeleton(
            name="TestAgent",
            output_dir=self.test_dir,
        )
        gitignore = Path(result["path"]) / ".gitignore"
        self.assertTrue(gitignore.exists())
        content = gitignore.read_text(encoding="utf-8")
        self.assertIn("__pycache__", content)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Lighthouse Test Suite")
    print("=" * 60)
    unittest.main(verbosity=2)
