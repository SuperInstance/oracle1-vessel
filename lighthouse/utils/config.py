"""
config.py — Configuration loader for the Lighthouse package.

Supports lighthouse.toml in the repo root, with env var overrides
for sensitive values like GITHUB_TOKEN.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


DEFAULT_CONFIG = {
    "fleet": {
        "org": "SuperInstance",
        "token_path": "~/.lighthouse/github_token",
        "scan_interval_minutes": 30,
    },
    "beachcomb": {
        "default_action": "commit",
        "state_db": "~/.lighthouse/state.db",
    },
    "agents": {
        "expected": ["oracle1", "jetsonclaw1", "babel", "navigator", "nautilus"],
        "heartbeat_timeout_hours": 48,
    },
    "notifications": {
        "telegram_enabled": False,
        "telegram_chat_id": "",
    },
}


class LighthouseConfig:
    """Fleet configuration loaded from lighthouse.toml with env var overrides."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else self._find_config()
        self._data = self._load()

    def _find_config(self) -> Path:
        """Find lighthouse.toml by searching upward from cwd."""
        cwd = Path.cwd()
        for parent in [cwd] + list(cwd.parents):
            candidate = parent / "lighthouse.toml"
            if candidate.exists():
                return candidate
        return cwd / "lighthouse.toml"

    def _load(self) -> Dict[str, Any]:
        """Load config from TOML file, falling back to defaults."""
        config = dict(DEFAULT_CONFIG)
        if self.config_path and self.config_path.exists():
            with open(self.config_path, "rb") as f:
                user_config = tomllib.load(f)
            self._deep_merge(config, user_config)
        return config

    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> None:
        """Deep-merge override into base dict."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                LighthouseConfig._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, dotted_path: str, default: Any = None) -> Any:
        """Get config value by dotted path, e.g. 'fleet.org'."""
        keys = dotted_path.split(".")
        node = self._data
        for key in keys:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return default
        return node

    def set(self, dotted_path: str, value: Any) -> None:
        """Set config value by dotted path."""
        keys = dotted_path.split(".")
        node = self._data
        for key in keys[:-1]:
            if key not in node:
                node[key] = {}
            node = node[key]
        node[keys[-1]] = value

    @property
    def org(self) -> str:
        return self.get("fleet.org", "SuperInstance")

    @property
    def token_path(self) -> str:
        return self.get("fleet.token_path", "~/.lighthouse/github_token")

    @property
    def scan_interval(self) -> int:
        return int(self.get("fleet.scan_interval_minutes", 30))

    @property
    def expected_agents(self) -> list:
        return self.get("agents.expected", [])

    @property
    def heartbeat_timeout_hours(self) -> int:
        return int(self.get("agents.heartbeat_timeout_hours", 48))

    @property
    def beachcomb_action(self) -> str:
        return self.get("beachcomb.default_action", "commit")

    @property
    def state_db_path(self) -> str:
        path = self.get("beachcomb.state_db", "~/.lighthouse/state.db")
        return os.path.expanduser(path)

    def save(self, path: Optional[str] = None) -> None:
        """Save current config to a TOML file."""
        target = Path(path) if path else self.config_path
        try:
            import tomli_w  # type: ignore
            with open(target, "wb") as f:
                tomli_w.dump(self._data, f)
        except ImportError:
            # Fallback: save as JSON
            with open(str(target).replace(".toml", ".json"), "w") as f:
                json.dump(self._data, f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Return config as a plain dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"LighthouseConfig(path={self.config_path}, org={self.org})"
