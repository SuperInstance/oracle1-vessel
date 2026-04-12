"""Tests for beachcomb.py — fleet fork/PR/bottle scanner."""

import json
import os
import sys
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Ensure tools/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Set up a fake GITHUB_TOKEN for all beachcomb tests."""
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token-for-testing")


class TestGetStateFile:
    @patch("beachcomb.os.path.dirname")
    @patch("beachcomb.os.path.exists", return_value=False)
    def test_creates_new_state_when_missing(self, mock_exists, mock_dirname):
        import beachcomb
        state = beachcomb.get_state_file()
        assert state["known_forks"] == {}
        assert state["known_prs"] == {}
        assert state["new_collaborators"] == []

    @patch("beachcomb.os.path.dirname", return_value="/tmp")
    @patch("beachcomb.os.path.exists", return_value=True)
    def test_loads_existing_state(self, mock_exists, mock_dirname, tmp_path):
        import beachcomb
        existing = {"known_forks": {"repo/owner": {}}, "known_prs": {}, "new_collaborators": []}
        with patch("builtins.open", mock_open(read_data=json.dumps(existing))):
            state = beachcomb.get_state_file()
        assert "repo/owner" in state["known_forks"]


class TestApiGet:
    @patch("beachcomb.urllib.request.urlopen")
    def test_api_get_success(self, mock_urlopen):
        import beachcomb
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"name": "test"}]'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = beachcomb.api_get("/test/path")
        assert result == [{"name": "test"}]

    @patch("beachcomb.urllib.request.urlopen")
    def test_api_get_404_returns_none(self, mock_urlopen):
        import beachcomb
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.github.com/test",
            code=404, msg="Not Found", hdrs=None, fp=None
        )
        result = beachcomb.api_get("/test/path")
        assert result is None


class TestGenerateReport:
    def test_empty_report(self):
        import beachcomb
        report = beachcomb.generate_report(
            {"known_forks": {}, "known_prs": {}},
            [], [], []
        )
        assert "No new activity" in report

    def test_report_with_new_forks(self):
        import beachcomb
        state = {"known_forks": {}, "known_prs": {}}
        forks = [{
            "fork_owner": "ExternalUser",
            "repo": "test-repo",
            "has_bottle": True,
            "messages_from": ["fleet"],
            "fork_url": "https://github.com/ExternalUser/test-repo",
        }]
        report = beachcomb.generate_report(state, forks, [], [])
        assert "ExternalUser" in report
        assert "test-repo" in report

    def test_report_with_new_prs(self):
        import beachcomb
        state = {"known_forks": {}, "known_prs": {}}
        prs = [{
            "repo": "some-repo",
            "number": 42,
            "user": "contributor",
            "title": "Fix something",
            "url": "https://github.com/SuperInstance/some-repo/pull/42",
        }]
        report = beachcomb.generate_report(state, [], prs, [])
        assert "#42" in report
        assert "contributor" in report

    def test_report_with_external_bottles(self):
        import beachcomb
        state = {"known_forks": {}, "known_prs": {}}
        bottles = [{"owner": "Someone", "repo": "their-repo"}]
        report = beachcomb.generate_report(state, [], [], bottles)
        assert "Someone" in report
        assert "External Bottles" in report
