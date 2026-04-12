"""Tests for infer_context.py — context inference protocol."""

import json
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

# Ensure tools/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token-for-testing")


class TestApiGet:
    @patch("infer_context.urllib.request.urlopen")
    def test_api_get_success(self, mock_urlopen, mock_env):
        import infer_context
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"key": "value"}'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = infer_context.api_get("/test")
        assert result == {"key": "value"}

    @patch("infer_context.urllib.request.urlopen")
    def test_api_get_failure_returns_none(self, mock_urlopen, mock_env):
        import infer_context
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=500, msg="Error", hdrs=None, fp=None
        )
        result = infer_context.api_get("/test")
        assert result is None


class TestInferExpertiseFromCommits:
    @patch("infer_context.api_get")
    def test_infers_languages(self, mock_api, mock_env):
        import infer_context
        # Mock: repos endpoint returns list, commits endpoint returns empty list
        mock_api.return_value = []
        result = infer_context.infer_expertise_from_commits("TestOwner", ["repo1"])
        assert result["languages"] == {}
        assert result["total_commits"] == 0

    @patch("infer_context.api_get")
    def test_infers_topics_from_messages(self, mock_api, mock_env):
        import infer_context
        # Return a commit with a relevant message
        mock_api.return_value = [{
            "sha": "abc123",
            "commit": {"message": "Added rust flux runtime tests"},
        }]
        result = infer_context.infer_expertise_from_commits("TestOwner", ["repo1"])
        assert result["total_commits"] == 1
        # Should detect keywords
        assert "rust" in result["topics"] or "flux" in result["topics"] or "test" in result["topics"]

    @patch("infer_context.api_get")
    def test_infers_languages_from_files(self, mock_api, mock_env):
        import infer_context
        # Return commit with file details
        mock_api.side_effect = [
            # First call: commits list
            [{
                "sha": "abc123",
                "commit": {"message": "update code"},
            }],
            # Second call: commit detail
            {
                "files": [
                    {"filename": "src/main.rs"},
                    {"filename": "src/lib.rs"},
                    {"filename": "tests/test_main.py"},
                ]
            },
        ]
        result = infer_context.infer_expertise_from_commits("TestOwner", ["repo1"])
        assert result["total_commits"] == 1
        assert "Rust" in result["languages"]
        assert result["languages"]["Rust"] == 2


class TestReadAgentState:
    @patch("infer_context.api_get")
    def test_no_data_available(self, mock_api, mock_env):
        import infer_context
        mock_api.return_value = None
        state = infer_context.read_agent_state("Owner", "repo-vessel")
        assert state == {}

    @patch("infer_context.api_get")
    def test_reads_taskboard(self, mock_api, mock_env):
        import infer_context
        import base64
        encoded = base64.b64encode(b"# Task Board\n- Task 1\n- Task 2").decode()
        mock_api.return_value = {
            "content": encoded,
            "encoding": "base64",
        }
        state = infer_context.read_agent_state("Owner", "repo-vessel")
        assert "taskboard" in state


class TestGenerateSynergyReport:
    def test_empty_expertise(self):
        import infer_context
        expertise = {"files_touched": {}, "topics": {}, "languages": {}, "recent_messages": [], "total_commits": 0}
        report = infer_context.generate_synergy_report("TestAgent", expertise, {})
        assert "TestAgent" in report
        assert "Context Inference" in report

    def test_with_topics(self):
        import infer_context
        expertise = {
            "files_touched": {"main.rs": 3},
            "topics": {"rust": 5, "flux": 3},
            "languages": {"Rust": 3},
            "recent_messages": ["Working on flux runtime"],
            "total_commits": 2,
        }
        report = infer_context.generate_synergy_report("TestAgent", expertise, {})
        assert "rust" in report.lower()
        assert "Rust" in report

    def test_synergy_detection(self):
        import infer_context
        expertise = {
            "files_touched": {},
            "topics": {"flux": 2, "isa": 1},
            "languages": {},
            "recent_messages": [],
            "total_commits": 1,
        }
        report = infer_context.generate_synergy_report("TestAgent", expertise, {})
        # Should detect ISA convergence synergy
        assert "Synergy" in report
