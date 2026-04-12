#!/usr/bin/env python3
"""
Tests for beachcomb.py — Fork/PR/bottle scanner.

All GitHub API calls are mocked to avoid needing real credentials.
"""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import beachcomb


class TestApiGet(unittest.TestCase):
    """Tests for the api_get function."""

    @patch("beachcomb.urllib.request.urlopen")
    def test_api_get_success(self, mock_urlopen):
        """api_get returns parsed JSON on success."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"items": [1, 2, 3]}'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = beachcomb.api_get("/test/path")
        self.assertEqual(result, {"items": [1, 2, 3]})

    @patch("beachcomb.urllib.request.urlopen")
    def test_api_get_params_appended(self, mock_urlopen):
        """api_get appends query params to URL."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[]'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        beachcomb.api_get("/repos/test", {"per_page": "10", "sort": "updated"})
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        url = getattr(req, "full_url", "") or str(req)
        self.assertIn("per_page=10", url)
        self.assertIn("sort=updated", url)

    @patch("beachcomb.urllib.request.urlopen")
    def test_api_get_404_returns_none(self, mock_urlopen):
        """api_get returns None on 404."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "url", 404, "Not Found", {}, None
        )
        result = beachcomb.api_get("/nonexistent")
        self.assertIsNone(result)

    @patch("beachcomb.urllib.request.urlopen")
    def test_api_get_other_http_error_returns_none(self, mock_urlopen):
        """api_get returns None on non-404 HTTP errors."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "url", 500, "Server Error", {}, None
        )
        with patch("sys.stdout", new_callable=StringIO):
            result = beachcomb.api_get("/error")
        self.assertIsNone(result)

    @patch("beachcomb.urllib.request.urlopen")
    def test_api_get_url_error_returns_none(self, mock_urlopen):
        """api_get returns None on URLError (DNS failure, etc.)."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("DNS failure")
        result = beachcomb.api_get("/unreachable")
        self.assertIsNone(result)

    @patch("beachcomb.urllib.request.urlopen")
    def test_api_get_timeout_returns_none(self, mock_urlopen):
        """api_get returns None on timeout."""
        mock_urlopen.side_effect = TimeoutError("timed out")
        result = beachcomb.api_get("/slow")
        self.assertIsNone(result)


class TestGetStateFile(unittest.TestCase):
    """Tests for get_state_file / save_state."""

    def test_creates_default_state_when_missing(self):
        """get_state_file returns default structure when no file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("beachcomb.os.path.dirname", return_value=tmpdir):
                state = beachcomb.get_state_file()
        self.assertEqual(state["known_forks"], {})
        self.assertEqual(state["known_prs"], {})
        self.assertIsNone(state["last_scan"])

    def test_loads_existing_state(self):
        """get_state_file loads from existing JSON file."""
        existing = {
            "known_forks": {"repo/user1": {"fork_owner": "user1"}},
            "known_prs": {"repo#1": {"repo": "repo"}},
            "last_scan": "2026-04-12T00:00:00",
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "beachcomb-state.json")
            with open(path, "w") as f:
                json.dump(existing, f)
            with patch("beachcomb.os.path.dirname", return_value=tmpdir):
                state = beachcomb.get_state_file()
        self.assertEqual(state["known_forks"], existing["known_forks"])
        self.assertIn("repo#1", state["known_prs"])

    def test_save_state_adds_timestamp(self):
        """save_state adds last_scan timestamp."""
        state = {"known_forks": {}, "known_prs": {}}
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("beachcomb.os.path.dirname", return_value=tmpdir):
                beachcomb.save_state(state)
            self.assertIsNotNone(state["last_scan"])
            # Verify it's ISO format
            self.assertIn("T", state["last_scan"])


class TestScanForks(unittest.TestCase):
    """Tests for scan_forks with mocked API."""

    def _mock_api_get(self, side_effect_map):
        """Helper: returns different data per API path."""
        def fake_api_get(path, params=None):
            key = path.split("?")[0]
            return side_effect_map.get(key)
        return fake_api_get

    @patch("beachcomb.api_get")
    def test_detects_new_fork(self, mock_get):
        """scan_forks detects and records a new fork."""
        mock_get.side_effect = self._mock_api_get({
            "/users/SuperInstance/repos": [{"name": "flux-runtime"}],
            "/repos/SuperInstance/flux-runtime/forks": [
                {"owner": {"login": "ExternalUser"}, "html_url": "https://github.com/ExternalUser/flux-runtime"},
            ],
            "/repos/ExternalUser/flux-runtime/contents/message-in-a-bottle": None,
        })

        state = {"known_forks": {}, "known_prs": {}}
        with patch("sys.stdout", new_callable=StringIO):
            result = beachcomb.scan_forks(state)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["fork_owner"], "ExternalUser")
        self.assertEqual(result[0]["repo"], "flux-runtime")
        self.assertFalse(result[0]["has_bottle"])
        self.assertIn("flux-runtime/ExternalUser", state["known_forks"])

    @patch("beachcomb.api_get")
    def test_skips_known_forks(self, mock_get):
        """scan_forks skips forks already in state."""
        mock_get.side_effect = self._mock_api_get({
            "/users/SuperInstance/repos": [{"name": "flux-runtime"}],
            "/repos/SuperInstance/flux-runtime/forks": [
                {"owner": {"login": "KnownUser"}, "html_url": "https://github.com/KnownUser/flux-runtime"},
            ],
        })

        state = {
            "known_forks": {"flux-runtime/KnownUser": {"fork_owner": "KnownUser"}},
            "known_prs": {},
        }
        with patch("sys.stdout", new_callable=StringIO):
            result = beachcomb.scan_forks(state)

        self.assertEqual(len(result), 0)

    @patch("beachcomb.api_get")
    def test_detects_bottle(self, mock_get):
        """scan_forks detects message-in-a-bottle on a fork."""
        mock_get.side_effect = self._mock_api_get({
            "/users/SuperInstance/repos": [{"name": "flux-tools"}],
            "/repos/SuperInstance/flux-tools/forks": [
                {"owner": {"login": "BottleUser"}, "html_url": "https://github.com/BottleUser/flux-tools"},
            ],
            "/repos/BottleUser/flux-tools/contents/message-in-a-bottle": [
                {"type": "dir", "name": "README.md"},
            ],
            "/repos/BottleUser/flux-tools/contents/message-in-a-bottle/for-fleet": [
                {"type": "dir", "name": "oracle1"},
                {"type": "file", "name": "TASKS.md"},
            ],
        })

        state = {"known_forks": {}, "known_prs": {}}
        with patch("sys.stdout", new_callable=StringIO):
            result = beachcomb.scan_forks(state)

        self.assertTrue(result[0]["has_bottle"])
        self.assertEqual(result[0]["messages_from"], ["oracle1"])

    @patch("beachcomb.api_get")
    def test_skips_self_forks(self, mock_get):
        """scan_forks ignores forks by the owner itself."""
        mock_get.side_effect = self._mock_api_get({
            "/users/SuperInstance/repos": [{"name": "repo1"}],
            "/repos/SuperInstance/repo1/forks": [
                {"owner": {"login": "SuperInstance"}, "html_url": "https://github.com/SuperInstance/repo1"},
            ],
        })

        state = {"known_forks": {}, "known_prs": {}}
        with patch("sys.stdout", new_callable=StringIO):
            result = beachcomb.scan_forks(state)

        self.assertEqual(len(result), 0)

    @patch("beachcomb.api_get")
    def test_no_repos_returns_empty(self, mock_get):
        """scan_forks returns empty when no repos found."""
        mock_get.return_value = None
        state = {"known_forks": {}, "known_prs": {}}
        with patch("sys.stdout", new_callable=StringIO):
            result = beachcomb.scan_forks(state)
        self.assertEqual(result, [])


class TestScanPRs(unittest.TestCase):
    """Tests for scan_prs with mocked API."""

    def _mock_api_get(self, side_effect_map):
        def fake_api_get(path, params=None):
            key = path.split("?")[0]
            return side_effect_map.get(key)
        return fake_api_get

    @patch("beachcomb.api_get")
    def test_detects_external_pr(self, mock_get):
        """scan_prs detects a PR from an external user."""
        mock_get.side_effect = self._mock_api_get({
            "/users/SuperInstance/repos": [{"name": "flux-runtime"}],
            "/repos/SuperInstance/flux-runtime/pulls": [
                {
                    "number": 42,
                    "user": {"login": "ExternalContributor"},
                    "title": "Add CUDA kernel support",
                    "html_url": "https://github.com/SuperInstance/flux-runtime/pull/42",
                },
            ],
        })

        state = {"known_forks": {}, "known_prs": {}}
        with patch("sys.stdout", new_callable=StringIO):
            result = beachcomb.scan_prs(state)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["user"], "ExternalContributor")
        self.assertEqual(result[0]["number"], 42)
        # PR ID format is "repo/#num"
        self.assertIn("flux-runtime/#42", state["known_prs"])

    @patch("beachcomb.api_get")
    def test_skips_own_prs(self, mock_get):
        """scan_prs skips PRs from the repo owner."""
        mock_get.side_effect = self._mock_api_get({
            "/users/SuperInstance/repos": [{"name": "repo1"}],
            "/repos/SuperInstance/repo1/pulls": [
                {
                    "number": 1,
                    "user": {"login": "SuperInstance"},
                    "title": "Internal fix",
                    "html_url": "https://github.com/SuperInstance/repo1/pull/1",
                },
            ],
        })

        state = {"known_forks": {}, "known_prs": {}}
        with patch("sys.stdout", new_callable=StringIO):
            result = beachcomb.scan_prs(state)

        self.assertEqual(len(result), 0)

    @patch("beachcomb.api_get")
    def test_skips_known_prs(self, mock_get):
        """scan_prs skips PRs already in state."""
        mock_get.side_effect = self._mock_api_get({
            "/users/SuperInstance/repos": [{"name": "repo1"}],
            "/repos/SuperInstance/repo1/pulls": [
                {
                    "number": 5,
                    "user": {"login": "Someone"},
                    "title": "A PR",
                    "html_url": "https://example.com/pr/5",
                },
            ],
        })

        # PR ID format in state is "repo/#num"
        state = {"known_forks": {}, "known_prs": {"repo1/#5": {}}}
        with patch("sys.stdout", new_callable=StringIO):
            result = beachcomb.scan_prs(state)

        self.assertEqual(len(result), 0)


class TestGenerateReport(unittest.TestCase):
    """Tests for report generation."""

    def test_empty_report(self):
        """Report shows 'no activity' when nothing new found."""
        state = {"known_forks": {}, "known_prs": {}}
        report = beachcomb.generate_report(state, [], [], [])
        self.assertIn("No new activity this scan", report)

    def test_report_with_new_forks(self):
        """Report includes new fork details."""
        state = {"known_forks": {}, "known_prs": {}}
        forks = [
            {"fork_owner": "User1", "repo": "repo1", "has_bottle": True, "messages_from": ["oracle1"]},
            {"fork_owner": "User2", "repo": "repo2", "has_bottle": False, "messages_from": []},
        ]
        report = beachcomb.generate_report(state, forks, [], [])
        self.assertIn("New Forks", report)
        self.assertIn("User1", report)
        self.assertIn("repo1", report)
        self.assertIn("User2", report)

    def test_report_with_new_prs(self):
        """Report includes new PR details."""
        state = {"known_forks": {}, "known_prs": {}}
        prs = [
            {"repo": "repo1", "number": 1, "user": "Alice", "title": "Fix bug", "url": "https://example.com/1"},
        ]
        report = beachcomb.generate_report(state, [], prs, [])
        self.assertIn("New Pull Requests", report)
        self.assertIn("Alice", report)
        self.assertIn("Fix bug", report)

    def test_report_with_external_bottles(self):
        """Report includes external bottle discoveries."""
        state = {"known_forks": {}, "known_prs": {}}
        bottles = [{"owner": "Bob", "repo": "bobs-vessel"}]
        report = beachcomb.generate_report(state, [], [], bottles)
        self.assertIn("External Bottles Found", report)
        self.assertIn("Bob", report)

    def test_report_includes_totals(self):
        """Report includes total known counts."""
        state = {
            "known_forks": {"a/b": {}, "c/d": {}, "e/f": {}},
            "known_prs": {"x#1": {}, "y#2": {}},
        }
        report = beachcomb.generate_report(state, [], [], [])
        self.assertIn("Total known forks: 3", report)
        self.assertIn("Total known PRs: 2", report)


class TestModuleLoadSafety(unittest.TestCase):
    """Verify the module can be imported without a token file or env var."""

    def test_import_without_token(self):
        """beachcomb can be imported when no GITHUB_TOKEN is set and no token file exists."""
        original = os.environ.pop("GITHUB_TOKEN", None)
        try:
            token_path = "/tmp/.mechanic_token"
            token_existed = os.path.exists(token_path)
            if token_existed:
                os.rename(token_path, token_path + ".bak")

            import importlib
            import beachcomb as bc
            importlib.reload(bc)
            self.assertIsInstance(bc.GITHUB_TOKEN, str)
        finally:
            if original is not None:
                os.environ["GITHUB_TOKEN"] = original
            if token_existed:
                os.rename(token_path + ".bak", token_path)


if __name__ == "__main__":
    unittest.main()
