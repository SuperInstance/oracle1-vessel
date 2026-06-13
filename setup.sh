#!/bin/bash
# setup.sh — Bootstrap a new Lighthouse installation
# Usage: ./setup.sh [org_name] [github_token]
set -euo pipefail

echo "Oracle1 Vessel — Lighthouse Setup"
echo "===================================="

# 1. Check prerequisites
echo ""
echo "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found (need 3.10+)"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "  Python: $PYTHON_VERSION"

if ! command -v git &>/dev/null; then
    echo "ERROR: git not found"
    exit 1
fi
echo "  Git: $(git --version)"

# 2. Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
echo "  Virtual env: .venv/"

# 3. Install as editable package
echo ""
echo "Installing lighthouse package..."
pip install --quiet -e .
echo "  Installed: lighthouse v$(python3 -c 'from lighthouse import __version__; print(__version__)')"

# 4. Configure
echo ""
echo "Configuration:"
if [ -n "${2:-}" ]; then
    export GITHUB_TOKEN="$2"
    echo "  GITHUB_TOKEN: set from argument"
elif [ -n "${GITHUB_TOKEN:-}" ]; then
    echo "  GITHUB_TOKEN: set from environment"
else
    echo "  WARNING: GITHUB_TOKEN not set. Set it before running commands."
fi

if [ -n "${1:-}" ]; then
    echo "  Org: $1"
fi

# 5. Verify installation
echo ""
echo "Verifying installation..."
python3 -c "from lighthouse.utils.github import GitHubClient; print('  GitHub client: OK')"
python3 -c "from lighthouse.utils.config import LighthouseConfig; print('  Config system: OK')"
python3 -c "from lighthouse.beachcomb.scanner import BeachcombScanner; print('  Beachcomb: OK')"
python3 -c "from lighthouse.discovery.fleet_scan import FleetScanner; print('  Fleet scanner: OK')"
python3 -c "from lighthouse.discovery.capability import CapabilityMatcher; print('  Capability matcher: OK')"
python3 -c "from lighthouse.context.infer import ContextInferrer; print('  Context inferrer: OK')"
python3 -c "from lighthouse.git.bottle import BottleManager; print('  Bottle manager: OK')"
python3 -c "from lighthouse.git.onboard import Onboarder; print('  Onboarder: OK')"

echo ""
echo "===================================="
echo "Lighthouse ready!"
echo ""
echo "Commands:"
echo "  source .venv/bin/activate"
echo "  lighthouse status      # Fleet health summary"
echo "  lighthouse scan        # Scan all fleet repos"
echo "  lighthouse beachcomb   # Sweep for new activity"
echo "  lighthouse bottle list # List bottles"
echo "  lighthouse onboard --name NewAgent  # Create new vessel"
echo "  lighthouse config show # View config"
echo ""
