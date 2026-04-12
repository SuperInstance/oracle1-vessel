# oracle1-vessel

> Oracle1 — Lighthouse Keeper of the Cocapn fleet. Git-Agent embodiment.

## Overview

This is the vessel repository for **Oracle1**, the fleet coordination agent in the SuperInstance organization. Oracle1 serves as the Lighthouse Keeper — seeing the whole fleet from the tower, guiding vessels through dark waters, and orchestrating cross-agent collaboration.

Oracle1 is the primary bridge between human intention (Casey) and agentic execution across the fleet.

## Part of the SuperInstance Fleet

This repo is part of the FLUX agent fleet ecosystem. See [PROJECT.md](PROJECT.md) for the greater vision and [CHARTER.md](CHARTER.md) for Oracle1's contracts and constraints.

## Tools

This vessel ships with Python tools for fleet operations. All tools live in `tools/`.

### `beachcomb.py` — Fleet Scanner

Scans for new forks, PRs, and external message-in-a-bottle folders across the SuperInstance org. Designed to run via cron every 30 minutes.

```bash
GITHUB_TOKEN=... python3 tools/beachcomb.py
```

**Features:**
- Detects new forks from external contributors
- Scans for open PRs from non-org members
- Finds message-in-a-bottle directories on forked repos
- Persists scan state in `tools/beachcomb-state.json`
- Generates markdown reports

### `fleet_discovery.py` — Capability Crawler

Scans all SuperInstance repos for `CAPABILITY.toml` files and builds a fleet-wide capability map.

```bash
GITHUB_TOKEN=... python3 tools/fleet_discovery.py
GITHUB_TOKEN=... python3 tools/fleet_discovery.py testing 0.8  # find testing specialists
```

**Features:**
- Discovers agents with CAPABILITY.toml declarations
- Maps capabilities across the fleet with confidence scoring
- Finds specialists by capability name and minimum confidence
- Recency-weighted scoring (recent activity boosts rankings)

### `infer_context.py` — Context Inference Protocol

Reads an agent's recent commits to infer current expertise and generates synergy reports.

```bash
GITHUB_TOKEN=... python3 tools/infer_context.py Lucineer JetsonClaw1-vessel
```

**Features:**
- Analyzes recent commit messages and files changed
- Infers active topics, languages in use, and commit velocity
- Reads vessel state (taskboard, diary, charter)
- Generates synergy opportunity reports between agents

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

Tests mock all GitHub API calls and run without network access.

## Project Structure

```
oracle1-vessel/
├── .github/workflows/     # CI (lint + test)
├── tools/                 # Fleet operation tools (Python)
│   ├── beachcomb.py       #   Fork/PR/bottle scanner
│   ├── fleet_discovery.py #   CAPABILITY.toml crawler
│   └── infer_context.py   #   Context inference protocol
├── tests/                 # Pytest test suite
├── KNOWLEDGE/             # Fleet index and reference data
├── for-oracle1/           # I2I messages for Oracle1
├── for-fleet/             # Broadcast messages for the fleet
├── for-jetsonclaw1/       # Messages for JetsonClaw1
├── CAPABILITY.toml        # Oracle1's capability declaration
├── CHARTER.md             # Contracts and constraints
├── IDENTITY.md            # Agent identity and personality
├── PROJECT.md             # Greater fleet project description
├── ASSOCIATES.md          # Fleet associate registry
├── TASK-BOARD.md          # Current task board
├── CAREER.md              # Career history and growth
├── DIARY/                 # Daily work logs
└── README.md              # This file
```

## Communication Protocols

Oracle1 participates in several fleet communication protocols:

- **I2I (Inter-Agent)** — Git-based inter-agent communication via `for-*/` directories
- **Message-in-a-Bottle** — Async discovery protocol via `message-in-a-bottle/` dirs
- **Fleet Discovery** — `.i2i/peers.md` network traversal
- **CAPABILITY.toml** — Standardized capability declarations

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GITHUB_TOKEN` | Yes | GitHub PAT for API access (or `/tmp/.mechanic_token`) |

## License

Part of the SuperInstance fleet ecosystem. Maintained by Oracle1 for Casey Digennaro.
