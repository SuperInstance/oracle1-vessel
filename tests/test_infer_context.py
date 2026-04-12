#!/usr/bin/env python3
"""
Tests for infer_context.py — Context Inference Protocol.

All GitHub API calls are mocked to avoid needing real credentials.
"""
import base64
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from collections import Counter

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import infer_context


class TestApiGet(unittest.TestCase):
    """Tests for the api_get function."""

    @patch("infer_context.urllib.request.urlopen")
    def test_api_get_success(self, mock_urlopen):
        """api_get returns parsed JSON on success."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"name": "test"}'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = infer_context.api_get("/test")
        self.assertEqual(result, {"name": "test"})

    @patch("infer_context.urllib.request.urlopen")
    def test_api_get_http_error_returns_none(self, mock_urlopen):
        """api_get returns None on HTTP errors."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "url", 403, "Forbidden", {}, None
        )
        result = infer_context.api_get("/forbidden")
        self.assertIsNone(result)

    @patch("infer_context.urllib.request.urlopen")
    def test_api_get_url_error_returns_none(self, mock_urlopen):
        """api_get returns None on URLError."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("connection refused")
        result = infer_context.api_get("/unreachable")
        self.assertIsNone(result)

    @patch("infer_context.urllib.request.urlopen")
    def test_api_get_timeout_returns_none(self, mock_urlopen):
        """api_get returns None on timeout."""
        mock_urlopen.side_effect = TimeoutError("timed out")
        result = infer_context.api_get("/slow")
        self.assertIsNone(result)

    @patch("infer_context.urllib.request.urlopen")
    def test_api_get_os_error_returns_none(self, mock_urlopen):
        """api_get returns None on OSError."""
        mock_urlopen.side_effect = OSError("network down")
        result = infer_context.api_get("/error")
        self.assertIsNone(result)


class TestGetRecentCommits(unittest.TestCase):
    """Tests for get_recent_commits."""

    @patch("infer_context.api_get")
    def test_returns_commits_list(self, mock_get):
        """get_recent_commits returns list of commits."""
        mock_get.return_value = [
            {"sha": "abc123", "commit": {"message": "fix: bug"}},
            {"sha": "def456", "commit": {"message": "feat: new thing"}},
        ]
        result = infer_context.get_recent_commits("owner", "repo", hours=24)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["sha"], "abc123")

    @patch("infer_context.api_get")
    def test_non_list_response_returns_empty(self, mock_get):
        """get_recent_commits returns empty list for non-list API responses."""
        mock_get.return_value = {"message": "Not found"}
        result = infer_context.get_recent_commits("owner", "repo")
        self.assertEqual(result, [])

    @patch("infer_context.api_get")
    def test_none_response_returns_empty(self, mock_get):
        """get_recent_commits returns empty list when API returns None."""
        mock_get.return_value = None
        result = infer_context.get_recent_commits("owner", "repo")
        self.assertEqual(result, [])


class TestInferExpertiseFromCommits(unittest.TestCase):
    """Tests for infer_expertise_from_commits."""

    @patch("infer_context.api_get")
    def test_extracts_topics_from_messages(self, mock_get):
        """Topics are extracted from commit messages."""
        mock_get.side_effect = [
            [
                {"sha": "abc", "commit": {"message": "feat: add cuda kernel for flux runtime"}},
                {"sha": "def", "commit": {"message": "fix: isa opcode handling in rust"}},
            ],
            {"files": [{"filename": "src/cuda_kernel.rs"}]},
            {"files": [{"filename": "src/isa.rs"}]},
        ]

        result = infer_context.infer_expertise_from_commits("owner", ["repo1"])
        self.assertIn("cuda", result["topics"])
        self.assertIn("flux", result["topics"])
        self.assertIn("isa", result["topics"])
        self.assertIn("rust", result["topics"])
        self.assertEqual(result["total_commits"], 2)

    @patch("infer_context.api_get")
    def test_infers_languages_from_extensions(self, mock_get):
        """Language inference works from file extensions."""
        mock_get.side_effect = [
            [{"sha": "abc", "commit": {"message": "build stuff"}}],
            {"files": [
                {"filename": "main.rs"},
                {"filename": "lib.rs"},
                {"filename": "README.md"},
                {"filename": "Cargo.toml"},
                {"filename": "setup.py"},
            ]},
        ]

        result = infer_context.infer_expertise_from_commits("owner", ["repo1"])
        self.assertEqual(result["languages"].get("Rust"), 2)
        self.assertEqual(result["languages"].get("Documentation"), 1)
        self.assertEqual(result["languages"].get("Configuration"), 1)
        self.assertEqual(result["languages"].get("Python"), 1)

    @patch("infer_context.api_get")
    def test_tracks_files_touched(self, mock_get):
        """Files touched are tracked with counts."""
        mock_get.side_effect = [
            [
                {"sha": "abc", "commit": {"message": "touch file"}},
                {"sha": "def", "commit": {"message": "touch file again"}},
            ],
            {"files": [{"filename": "src/main.rs"}]},
            {"files": [{"filename": "src/main.rs"}, {"filename": "src/lib.rs"}]},
        ]

        result = infer_context.infer_expertise_from_commits("owner", ["repo1"])
        self.assertEqual(result["files_touched"]["src/main.rs"], 2)
        self.assertEqual(result["files_touched"]["src/lib.rs"], 1)

    @patch("infer_context.api_get")
    def test_message_truncation(self, mock_get):
        """Recent messages are truncated to 100 chars."""
        long_msg = "a" * 200
        mock_get.side_effect = [
            [{"sha": "abc", "commit": {"message": long_msg}}],
            {"files": []},
        ]

        result = infer_context.infer_expertise_from_commits("owner", ["repo1"])
        self.assertEqual(len(result["recent_messages"]), 1)
        self.assertEqual(len(result["recent_messages"][0]), 100)

    @patch("infer_context.api_get")
    def test_empty_repos(self, mock_get):
        """Empty repo list returns zeroed expertise."""
        result = infer_context.infer_expertise_from_commits("owner", [])
        self.assertEqual(result["total_commits"], 0)
        self.assertEqual(result["files_touched"], {})
        self.assertEqual(result["topics"], {})

    @patch("infer_context.api_get")
    def test_returns_counter_dicts(self, mock_get):
        """Return values are plain dicts, not Counters."""
        mock_get.return_value = []
        result = infer_context.infer_expertise_from_commits("owner", ["repo1"])
        self.assertIsInstance(result["files_touched"], dict)
        self.assertIsInstance(result["topics"], dict)
        self.assertIsInstance(result["languages"], dict)
        self.assertIsInstance(result["recent_messages"], list)
        self.assertIsInstance(result["total_commits"], int)

    @patch("infer_context.api_get")
    def test_multiple_repos(self, mock_get):
        """Expertise aggregates across multiple repos."""
        mock_get.side_effect = [
            [{"sha": "a1", "commit": {"message": "cuda stuff"}}],
            {"files": [{"filename": "kernel.rs"}]},
            [{"sha": "b1", "commit": {"message": "more cuda stuff"}}],
            {"files": [{"filename": "memory.rs"}]},
        ]

        result = infer_context.infer_expertise_from_commits("owner", ["repo1", "repo2"])
        self.assertEqual(result["total_commits"], 2)
        self.assertEqual(result["topics"].get("cuda"), 2)


class TestReadAgentState(unittest.TestCase):
    """Tests for read_agent_state."""

    def _b64(self, text):
        return base64.b64encode(text.encode()).decode()

    @patch("infer_context.api_get")
    def test_reads_taskboard(self, mock_get):
        """read_agent_state reads TASKBOARD.md from vessel."""
        mock_get.side_effect = [
            {
                "content": self._b64("# Task Board\n## Active\n- task1"),
                "encoding": "base64",
            },
            # DIARY call
            None,
            # CHARTER call
            None,
        ]
        state = infer_context.read_agent_state("owner", "vessel")
        self.assertIn("taskboard", state)
        self.assertIn("Task Board", state["taskboard"])

    @patch("infer_context.api_get")
    def test_reads_diary(self, mock_get):
        """read_agent_state reads the latest diary entry."""
        # 1st: TASKBOARD.md, 2nd: DIARY dir, 3rd: latest diary, 4th: CHARTER.md
        mock_get.side_effect = [
            None,  # TASKBOARD.md not found
            [
                {"name": "2026-04-10.md", "type": "file"},
                {"name": "2026-04-11.md", "type": "file"},
            ],
            {
                "content": self._b64("# Diary\n## What Happened\nBuilt stuff today."),
                "encoding": "base64",
            },
            None,  # CHARTER.md not found
        ]
        state = infer_context.read_agent_state("owner", "vessel")
        self.assertIn("latest_diary", state)
        self.assertEqual(state["latest_diary"]["file"], "2026-04-11.md")
        self.assertIn("Built stuff", state["latest_diary"]["content"])

    @patch("infer_context.api_get")
    def test_reads_charter(self, mock_get):
        """read_agent_state reads CHARTER.md."""
        mock_get.side_effect = [
            None,  # TASKBOARD
            None,  # DIARY
            {
                "content": self._b64("# Charter\nServe the fleet."),
                "encoding": "base64",
            },
        ]
        state = infer_context.read_agent_state("owner", "vessel")
        self.assertIn("charter_summary", state)
        self.assertIn("Serve the fleet", state["charter_summary"])

    @patch("infer_context.api_get")
    def test_handles_all_missing(self, mock_get):
        """read_agent_state returns empty dict when nothing is found."""
        mock_get.return_value = None
        state = infer_context.read_agent_state("owner", "vessel")
        self.assertEqual(state, {})


class TestGenerateSynergyReport(unittest.TestCase):
    """Tests for generate_synergy_report."""

    def test_basic_report_structure(self):
        """Report has expected sections."""
        expertise = {
            "files_touched": {},
            "topics": {"cuda": 5, "rust": 3},
            "languages": {"Rust": 3},
            "recent_messages": ["feat: cuda kernel"],
            "total_commits": 10,
        }
        state = {}
        report = infer_context.generate_synergy_report("TestAgent", expertise, state)

        self.assertIn("Context Inference: TestAgent", report)
        self.assertIn("Current Active Context", report)
        self.assertIn("Active Topics", report)
        self.assertIn("cuda", report)
        self.assertIn("Languages in Use", report)
        self.assertIn("Commit velocity", report)
        self.assertIn("10 commits", report)

    def test_synergy_cuda_gpu(self):
        """cuda+gpu topic triggers GPU computing synergy."""
        expertise = {
            "files_touched": {},
            "topics": {"cuda": 1},
            "languages": {},
            "recent_messages": [],
            "total_commits": 1,
        }
        report = infer_context.generate_synergy_report("Agent", expertise, {})
        self.assertIn("GPU computing", report)

    def test_synergy_rust_trust(self):
        """rust+trust topic triggers trust engine synergy."""
        expertise = {
            "files_touched": {},
            "topics": {"rust": 1},
            "languages": {},
            "recent_messages": [],
            "total_commits": 1,
        }
        report = infer_context.generate_synergy_report("Agent", expertise, {})
        self.assertIn("Trust engine", report)

    def test_synergy_flux_isa(self):
        """flux+isa topic triggers ISA convergence synergy."""
        expertise = {
            "files_touched": {},
            "topics": {"flux": 1, "isa": 2},
            "languages": {},
            "recent_messages": [],
            "total_commits": 3,
        }
        report = infer_context.generate_synergy_report("Agent", expertise, {})
        self.assertIn("ISA convergence", report)

    def test_no_synergy_message(self):
        """Report shows 'need more data' when no synergies found."""
        expertise = {
            "files_touched": {},
            "topics": {"documentation": 1},
            "languages": {},
            "recent_messages": [],
            "total_commits": 1,
        }
        report = infer_context.generate_synergy_report("Agent", expertise, {})
        self.assertIn("Need more data", report)

    def test_diary_section_shown(self):
        """Diary insights are included when available."""
        expertise = {
            "files_touched": {},
            "topics": {},
            "languages": {},
            "recent_messages": [],
            "total_commits": 0,
        }
        state = {
            "latest_diary": {
                "file": "2026-04-12.md",
                "content": "## What Happened\nFixed cuda bugs.\n## What I Learned\nRust is fast.",
            }
        }
        report = infer_context.generate_synergy_report("Agent", expertise, state)
        self.assertIn("2026-04-12.md", report)
        self.assertIn("What Happened", report)

    def test_topic_bar_chart(self):
        """Topics are displayed with bar chart characters."""
        expertise = {
            "files_touched": {},
            "topics": {"cuda": 5, "rust": 2},
            "languages": {},
            "recent_messages": [],
            "total_commits": 7,
        }
        report = infer_context.generate_synergy_report("Agent", expertise, {})
        # 5 mentions -> 5 bars
        self.assertIn("\u2588" * 5, report)
        # 2 mentions -> 2 bars
        self.assertIn("\u2588" * 2, report)

    def test_report_footer(self):
        """Report includes the privacy footer."""
        expertise = {
            "files_touched": {},
            "topics": {},
            "languages": {},
            "recent_messages": [],
            "total_commits": 0,
        }
        report = infer_context.generate_synergy_report("Agent", expertise, {})
        self.assertIn("No private data accessed", report)


class TestModuleImportSafety(unittest.TestCase):
    """Verify the module can be imported safely."""

    def test_import_without_token(self):
        """infer_context imports fine without GITHUB_TOKEN or token file."""
        original = os.environ.pop("GITHUB_TOKEN", None)
        try:
            token_path = "/tmp/.mechanic_token"
            token_existed = os.path.exists(token_path)
            if token_existed:
                os.rename(token_path, token_path + ".bak")

            import importlib
            import infer_context as ic
            importlib.reload(ic)
            self.assertIsInstance(ic.GITHUB_TOKEN, str)
        finally:
            if original is not None:
                os.environ["GITHUB_TOKEN"] = original
            if token_existed:
                os.rename(token_path + ".bak", token_path)


if __name__ == "__main__":
    unittest.main()
