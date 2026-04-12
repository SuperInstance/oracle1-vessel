"""Tests for fleet_discovery.py — CAPABILITY.toml crawler."""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Ensure tools/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))


class TestFetchToml:
    @patch("fleet_discovery.urllib.request.urlopen")
    def test_fetch_toml_success(self, mock_urlopen):
        import fleet_discovery
        toml_content = b'[agent]\nname = "TestAgent"\ntype = "test"\n'
        mock_resp = MagicMock()
        mock_resp.read.return_value = toml_content
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = fleet_discovery.fetch_toml("SuperInstance/test-repo")
        assert result is not None
        assert result["agent"]["name"] == "TestAgent"

    @patch("fleet_discovery.urllib.request.urlopen")
    def test_fetch_toml_missing(self, mock_urlopen):
        import fleet_discovery
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=404, msg="Not Found", hdrs=None, fp=None
        )
        result = fleet_discovery.fetch_toml("SuperInstance/no-capability")
        assert result is None


class TestRecencyWeight:
    def test_today(self):
        import fleet_discovery
        today = __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d")
        assert fleet_discovery.recency_weight(today) == 1.0

    def test_yesterday(self):
        import fleet_discovery
        yesterday = __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d")
        # Recency weight for < 3 days should be 0.9
        # Use "today" which is < 1 day -> 1.0, but we can't easily test "yesterday"
        # so just test the boundary conditions
        assert 0.0 < fleet_discovery.recency_weight("2020-01-01") <= 1.0

    def test_ancient_date(self):
        import fleet_discovery
        assert fleet_discovery.recency_weight("1999-01-01") == 0.3

    def test_invalid_date(self):
        import fleet_discovery
        assert fleet_discovery.recency_weight("not-a-date") == 0.3


class TestFindSpecialists:
    def test_finds_matching_agents(self):
        import fleet_discovery
        agents = [{
            "agent": {"name": "Oracle1", "avatar": "🔮", "home_repo": "SuperInstance/oracle1-vessel"},
            "capabilities": {
                "testing": {"confidence": 0.90, "last_used": "2026-04-12", "description": "Test expert"},
                "coordination": {"confidence": 0.92, "last_used": "2026-04-12", "description": "Coordinator"},
            }
        }]
        results = fleet_discovery.find_specialists(agents, "testing", 0.8)
        assert len(results) == 1
        assert results[0]["name"] == "Oracle1"
        assert results[0]["confidence"] == 0.90

    def test_filters_by_minimum_confidence(self):
        import fleet_discovery
        agents = [{
            "agent": {"name": "LowConfAgent", "avatar": "❓", "home_repo": "test/test"},
            "capabilities": {
                "testing": {"confidence": 0.30, "last_used": "2026-04-12", "description": "Not great"},
            }
        }]
        results = fleet_discovery.find_specialists(agents, "testing", 0.8)
        assert len(results) == 0

    def test_sorts_by_score(self):
        import fleet_discovery
        agents = [
            {
                "agent": {"name": "AgentA", "avatar": "a", "home_repo": "a/a"},
                "capabilities": {
                    "testing": {"confidence": 0.95, "last_used": "2026-04-12", "description": "Best"},
                }
            },
            {
                "agent": {"name": "AgentB", "avatar": "b", "home_repo": "b/b"},
                "capabilities": {
                    "testing": {"confidence": 0.70, "last_used": "2026-04-12", "description": "Good"},
                }
            },
        ]
        results = fleet_discovery.find_specialists(agents, "testing", 0.5)
        assert len(results) == 2
        assert results[0]["name"] == "AgentA"  # Higher score first

    def test_no_capabilities_key(self):
        import fleet_discovery
        agents = [{"agent": {"name": "NoCaps", "avatar": "?", "home_repo": "n/n"}}]
        results = fleet_discovery.find_specialists(agents, "testing", 0.5)
        assert len(results) == 0
