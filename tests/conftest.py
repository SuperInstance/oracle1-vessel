"""Shared test fixtures for oracle1-vessel tools tests."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# fleet_discovery.py reads ~/.bashrc at module level — create it if missing
@pytest.fixture(scope="session", autouse=True)
def ensure_bashrc_exists():
    """Ensure ~/.bashrc exists so fleet_discovery.py can import."""
    bashrc = Path.home() / ".bashrc"
    existed = bashrc.exists()
    original = None
    if existed:
        try:
            original = bashrc.read_text()
        except Exception:
            original = None
    bashrc.write_text('export GITHUB_TOKEN="fake-test-token"\n')
    # Remove from sys.modules so it re-imports cleanly
    for mod in list(sys.modules):
        if "fleet_discovery" in mod:
            del sys.modules[mod]
    yield
    for mod in list(sys.modules):
        if "fleet_discovery" in mod:
            del sys.modules[mod]
    if existed:
        bashrc.write_text(original)
    else:
        try:
            bashrc.unlink()
        except Exception:
            pass
