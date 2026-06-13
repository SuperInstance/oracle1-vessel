# ROADMAP.md — Oracle1 Vessel: The Lighthouse as a Runtime

> *From a single repo where one agent keeps the light burning, to an installable
> orchestration hub that anyone can deploy to coordinate their own fleet.*

**Author:** Datum 🔵, Fleet Quartermaster
**Date:** 2026-04-15
**Status:** Draft — Submitted for Oracle1 and Casey Review
**Version:** 1.0

---

## Table of Contents

1.  [Vision](#1-vision)
2.  [Current State](#2-current-state)
3.  [Phase 1 — Vessel-in-a-Box (Week 1)](#3-phase-1--vessel-in-a-box-week-1)
4.  [Phase 2 — Fleet Server (Week 2-3)](#4-phase-2--fleet-server-week-2-3)
5.  [Phase 3 — Discovery Engine (Week 3-4)](#5-phase-3--discovery-engine-week-3-4)
6.  [Phase 4 — Agent Lifecycle Management (Week 5-6)](#6-phase-4--agent-lifecycle-management-week-5-6)
7.  [Phase 5 — Communication Hub (Week 6-7)](#7-phase-5--communication-hub-week-6-7)
8.  [Phase 6 — Fleet Intelligence (Week 7-8)](#8-phase-6--fleet-intelligence-week-7-8)
9.  [Phase 7 — Self-Sustaining Fleet (Month 2-3)](#9-phase-7--self-sustaining-fleet-month-2-3)
10. [Integration Points](#10-integration-points)
11. [Risk Register](#11-risk-register)
12. [Effort Summary](#12-effort-summary)

---

## 1. Vision

### The Lighthouse as Standalone Orchestration Runtime

Today, Oracle1's vessel is a GitHub repo where files and folders coordinate
a fleet of 909+ repos and 8+ active agents. It works — but it works because
Oracle1 reads STATE.md, checks bottles, runs beachcomb sweeps manually, and
coordinates by writing markdown files into directories.

**The vision:** make this repo installable and bootable. Any human or agent
clones it, runs a setup script, and has a working Lighthouse — a fleet
coordination hub that monitors agents, routes messages, discovers repos,
tracks health, and dispatches tasks. The repo IS the Lighthouse. Git IS the
nervous system. But now it's *software*, not just convention.

```
                        THE VISION
    ┌────────────────────────────────────────────────┐
    │                                                │
    │   Anyone deploys oracle1-vessel                 │
    │          │                                     │
    │          ▼                                     │
    │   ┌──────────────┐                             │
    │   │  ./setup.sh  │  → config + deps + secrets  │
    │   └──────┬───────┘                             │
    │          ▼                                     │
    │   ┌──────────────┐                             │
    │   │ fleet-server │  → HTTP/WS API on :8900    │
    │   └──────┬───────┘                             │
    │          ▼                                     │
    │   Agents connect → get tasks → report back      │
    │   Repos discovered → cataloged → health-scored  │
    │   Bottles dropped → routed → delivered           │
    │   Fleet health → dashboard → alerts              │
    │                                                │
    │   "Install it, boot it, and the light turns on" │
    └────────────────────────────────────────────────┘
```

### Guiding Principles

1.  **Git-native first.** The fleet server enhances git-based workflows — it
    does not replace them. Every operation has a git fallback. If the server
    goes down, agents continue via bottles and commit feeds.
2.  **Progressive disclosure.** Phase 1 is a setup script. Phase 7 is a
    self-sustaining fleet. You can stop at any phase and still have something
    useful. Each phase delivers standalone value.
3.  **Dogfood ourselves.** The Cocapn fleet is the first customer. Every tool
    is tested against the real 909+ repos and 8+ agents before it's declared
    ready.
4.  **Minimal dependencies.** Python 3.10+. No heavy frameworks. No database
    servers. SQLite for state. stdlib for HTTP. The fleet server should run
    on a $5/mo VPS or a Jetson Orin Nano.

---

## 2. Current State

### What Works Today

| Capability | Implementation | Status | Location |
|-----------|---------------|--------|----------|
| **Fleet index generation** | Manual scan of GitHub API, written to KNOWLEDGE/ | ✅ Working | `KNOWLEDGE/FLEET-INDEX.md`, `fleet_index.json` |
| **Agent status tracking** | STATE.md updated per session, color-coded health | ✅ Working | `STATE.md` |
| **Task dispatch** | TASK-BOARD.md + FENCE-BOARD.md, manual assignment | ✅ Working | `TASK-BOARD.md`, `TASKBOARD.md`, `FENCE-BOARD.md` |
| **Beachcomb discovery** | Cron-based sweep via `tools/beachcomb.py` | ✅ Working | `tools/beachcomb.py`, `beachcomb/oracle1-sweeps.json` |
| **Fleet discovery** | `tools/fleet_discovery.py` scans CAPABILITY.toml | ✅ Working | `tools/fleet_discovery.py` |
| **Context inference** | `tools/infer_context.py` reads commits for expertise | ✅ Working | `tools/infer_context.py` |
| **MiB routing** | Directory-based bottles in `message-in-a-bottle/` | ✅ Working | `message-in-a-bottle/`, `COMMUNICATION-GUIDE.md` |
| **I2I protocol** | 20 message types defined, used in commits + issues | ✅ Working | `COMMUNICATION-GUIDE.md` |
| **Git-Agent Standard** | Full lifecycle spec for agent repos | ✅ Working | `GIT-AGENT-STANDARD.md` |
| **Necrosis detection** | 7 meta-systems for fleet health monitoring | ⚠️ Spec only | `research/lessons-learned.md` |
| **Dockside exam** | Certification checklist for fleet repos | ⚠️ Manual | `DOCKSIDE-EXAM.md` |
| **Career tracking** | Badges, growth stages, diary entries | ⚠️ Manual | `CAREER.md` |
| **Tom Sawyer Protocol** | Fence board for volunteer task coordination | ⚠️ Manual | `FENCE-BOARD.md` |
| **Conformance testing** | 88 vectors, cross-runtime runners | ✅ Working | `for-jetsonclaw1/conformance/` |
| **Cross-org communication** | Fork + PR pattern for SuperInstance ↔ Lucineer | ✅ Working | `COMMUNICATION-GUIDE.md` |

### What's Manual

- Agent health checking requires reading STATE.md — no automated heartbeat
- Beachcomb runs via cron but results are Markdown files, not structured data
- Task assignment is Oracle1 writing in TASK-BOARD.md — no automated dispatch
- Fleet discovery only scans CAPABILITY.toml — misses repos without one
- MiB delivery has no guarantee — bottles may sit unread for days
- No fleet-wide metrics — only what Oracle1 manually records in STATE.md
- Necrosis detection is a concept, not running code
- New agent onboarding requires manual file creation in 7+ locations

### What's Missing

- No HTTP/WebSocket API for real-time agent communication
- No agent registration or authentication system
- No persistent state store (STATE.md is hand-written Markdown)
- No automated health monitoring or alerting pipeline
- No fleet-wide search or capability matching API
- No message queue with delivery guarantees
- No dashboard for fleet health visualization
- No self-healing — when an agent goes silent, only Oracle1 notices

### Existing Tools Inventory

```
tools/
├── beachcomb.py          # 257 lines — fork/PR/bottle scanner
├── fleet_discovery.py    # 148 lines — CAPABILITY.toml crawler
└── infer_context.py      # 267 lines — commit-based expertise inference
                          # Total: ~672 lines of reusable Python
```

These three scripts are the seed from which the fleet server will grow. They
are well-tested in production against the real fleet. They use only stdlib +
tomllib (Python 3.11+). They authenticate via GITHUB_TOKEN. They produce both
human-readable Markdown and machine-readable JSON.

---

## 3. Phase 1 — Vessel-in-a-Box (Week 1)

### Goal

Make oracle1-vessel installable and bootable. A new human or agent clones the
repo, runs one command, and has a configured Lighthouse ready to coordinate.

### Deliverables

#### 1.1 Python Package Extraction (~400 LOC)

Extract the three tools from `tools/` into a proper Python package:

```
oracle1-vessel/
├── pyproject.toml              # Package config, deps, entry points
├── setup.sh                    # One-command boot
├── lighthouse/
│   ├── __init__.py
│   ├── cli.py                  # Click CLI entry point
│   ├── beachcomb/
│   │   ├── __init__.py
│   │   ├── scanner.py          # From tools/beachcomb.py (refactored)
│   │   ├── sweeps.py           # Sweep configuration loader
│   │   └── state.py            # State persistence (SQLite)
│   ├── discovery/
│   │   ├── __init__.py
│   │   ├── fleet_scan.py       # From tools/fleet_discovery.py (refactored)
│   │   ├── capability.py       # CAPABILITY.toml parser
│   │   └── health.py           # Health scoring engine
│   ├── context/
│   │   ├── __init__.py
│   │   └── infer.py            # From tools/infer_context.py (refactored)
│   ├── git/
│   │   ├── __init__.py
│   │   ├── agent_lifecycle.py  # Git-Agent Standard enforcement
│   │   ├── bottle.py           # MiB read/write operations
│   │   └── i2i.py              # I2I protocol message parser
│   └── utils/
│       ├── __init__.py
│       ├── github.py           # Shared GitHub API client
│       ├── config.py           # TOML/env config loader
│       └── report.py           # Markdown/JSON report generation
├── tests/
│   ├── test_beachcomb.py
│   ├── test_discovery.py
│   ├── test_context.py
│   └── test_bottle.py
└── README.md                   # Updated with install instructions
```

**Key changes from current tools:**
- Token loading: unified in `utils/github.py`, supports env var, file, and
  interactive input (no more hardcoded `.bashrc` parsing)
- State persistence: SQLite in `~/.lighthouse/state.db` instead of JSON files
- CLI: `lighthouse scan`, `lighthouse beachcomb`, `lighthouse infer`, etc.
- Configuration: `lighthouse.toml` in repo root for org name, token path,
  sweep targets, notification preferences

#### 1.2 Setup Script (~100 LOC)

```bash
#!/bin/bash
# setup.sh — Bootstrap a new Lighthouse installation
# Usage: ./setup.sh [org_name] [github_token]

echo "🔮 Oracle1 Vessel — Lighthouse Setup"
echo "====================================="

# 1. Check prerequisites
python3 --version     # Python 3.10+
git --version         # Git
gh auth status        # GitHub CLI (optional)

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 3. Configure
# Create lighthouse.toml from template
# Set GITHUB_TOKEN in .env
# Configure org name

# 4. Verify
lighthouse scan --verify
lighthouse beachcomb --dry-run

echo "✅ Lighthouse ready. Run 'lighthouse serve' to start."
```

#### 1.3 Configuration System (~150 LOC)

```toml
# lighthouse.toml — Fleet configuration
[fleet]
org = "SuperInstance"                    # GitHub org to monitor
token_path = "~/.lighthouse/github_token" # Or set GITHUB_TOKEN env
scan_interval_minutes = 30

[beachcomb]
default_action = "commit"                # notify | commit | silent
state_db = "~/.lighthouse/state.db"

[beachcomb.sweeps]
# Inherit from beachcomb/oracle1-sweeps.json
# Add new sweeps here

[agents]
expected = ["oracle1", "jetsonclaw1", "babel", "navigator", "nautilus"]
heartbeat_timeout_hours = 48              # Alert if silent > 48h

[notifications]
telegram_enabled = false
telegram_chat_id = ""
```

#### 1.4 CLI Entry Points (~200 LOC)

```
$ lighthouse --help

  scan         Scan fleet for agents and capabilities
  beachcomb    Run beachcomb sweep for new bottles/PRs
  infer        Infer agent context from commits
  status       Show fleet health summary
  bottle       Drop/read/list bottles
  onboard      Generate skeleton for a new agent vessel
  config       View/edit lighthouse configuration

  serve        Start fleet server (Phase 2)
  dashboard    Open fleet dashboard (Phase 6)
```

### Acceptance Criteria

- [ ] `pip install -e .` works on Python 3.10+
- [ ] `lighthouse scan` discovers agents from the configured GitHub org
- [ ] `lighthouse beachcomb --dry-run` scans repos without modifying state
- [ ] `lighthouse infer Lucineer JetsonClaw1-vessel` produces a synergy report
- [ ] `lighthouse bottle --list` reads bottles from `message-in-a-bottle/`
- [ ] `lighthouse onboard --name NewAgent --type vessel` generates a full
      skeleton repo with CHARTER.md, STATE.md, TASK-BOARD.md, etc.
- [ ] All existing tools/ scripts still work (backward compatibility)
- [ ] Test coverage > 80% on the extracted package
- [ ] `./setup.sh` runs end-to-end on a fresh Ubuntu 22.04 machine

### Effort Estimate

| Component | LOC | Hours |
|-----------|-----|-------|
| Package extraction (beachcomb, discovery, context) | 400 | 6 |
| GitHub API client + config system | 150 | 3 |
| CLI entry points | 200 | 4 |
| Setup script + onboarding template | 100 | 2 |
| Tests | 300 | 4 |
| Documentation (README + CHANGELOG) | 200 | 2 |
| **Total** | **~1,350** | **~21** |

---

## 4. Phase 2 — Fleet Server (Week 2-3)

### Goal

Build the fleet coordination server — an HTTP/WebSocket API that serves as
the central hub for all fleet operations. Any agent can connect, register,
and coordinate through this server.

### Architecture

```
                    ┌─────────────────────────┐
                    │     FLEET SERVER (:8900) │
                    │                         │
  ┌──────────┐      │  ┌───────────────────┐  │      ┌──────────┐
  │ Oracle1  │◄────►│  │   Agent Registry  │  │◄────►│ JetsonC1 │
  │ (client) │      │  │  name, status,    │  │      │ (client) │
  └──────────┘      │  │  capabilities,    │  │      └──────────┘
                    │  │  last_heartbeat   │  │
  ┌──────────┐      │  └───────────────────┘  │      ┌──────────┐
  │ Babel    │◄────►│  ┌───────────────────┐  │◄────►│ Navigator│
  │ (client) │      │  │   Task Queue      │  │      │ (client) │
  └──────────┘      │  │  priority, owner,  │  │      └──────────┘
                    │  │  status, deps      │  │
                    │  └───────────────────┘  │
                    │  ┌───────────────────┐  │      ┌──────────┐
                    │  │  MiB Router       │  │◄────►│ Datum    │
                    │  │  from → to, type  │  │      │ (client) │
                    │  └───────────────────┘  │      └──────────┘
                    │  ┌───────────────────┐  │
                    │  │  Health Monitor   │  │      ┌──────────┐
                    │  │  heartbeat, score │  │◄────►│ Casey    │
                    │  └───────────────────┘  │      │ (human)  │
                    │  ┌───────────────────┐  │      └──────────┘
                    │  │  SQLite State     │  │
                    │  │  agents, tasks,   │  │
                    │  │  bottles, sweeps  │  │
                    │  └───────────────────┘  │
                    └─────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │  SQLite DB      │
                    │  ~/.lighthouse/ │
                    │  state.db       │
                    └─────────────────┘
```

### HTTP API Endpoints

```
# Agent Registration
POST   /api/agents/register       # Register new agent
PUT    /api/agents/{name}/status  # Update agent status
GET    /api/agents/{name}         # Get agent info
GET    /api/agents                # List all agents
DELETE /api/agents/{name}         # Deactivate agent

# Heartbeat
POST   /api/agents/{name}/heartbeat  # Agent heartbeat ping

# Tasks
POST   /api/tasks                 # Create task
GET    /api/tasks                 # List tasks (filterable)
GET    /api/tasks/{id}            # Get task detail
PUT    /api/tasks/{id}            # Update task (assign, status)
DELETE /api/tasks/{id}            # Remove task
GET    /api/tasks/available       # Tasks available for claiming

# Bottles (MiB)
POST   /api/bottles               # Drop a bottle
GET    /api/bottles/inbox/{agent} # Get bottles for agent
GET    /api/bottles/outbox/{agent}# Get bottles from agent
PUT    /api/bottles/{id}/ack      # Acknowledge bottle read

# Discovery
POST   /api/discovery/scan        # Trigger fleet scan
GET    /api/discovery/agents      # Discovered agents
GET    /api/discovery/repos       # Discovered repos
GET    /api/discovery/capabilities# Capability matrix

# Health
GET    /api/health                # Server health
GET    /api/health/fleet          # Fleet health summary
GET    /api/health/{agent}        # Agent health detail

# Configuration
GET    /api/config                # Get config
PUT    /api/config                # Update config

# WebSocket
WS     /ws                       # Real-time fleet events
```

### WebSocket Events

```json
// Agent connects
{"type": "agent:connected", "agent": "babel", "timestamp": "..."}

// Heartbeat received
{"type": "agent:heartbeat", "agent": "jetsonclaw1", "status": "active"}

// Bottle dropped
{"type": "bottle:new", "from": "oracle1", "to": "datum", "id": "..."}

// Task assigned
{"type": "task:assigned", "task_id": "...", "agent": "navigator"}

// Task completed
{"type": "task:completed", "task_id": "...", "agent": "navigator"}

// Health alert
{"type": "health:alert", "level": "warning", "agent": "babel",
 "message": "Silent for 24h"}

// Discovery event
{"type": "discovery:new_repo", "repo": "SuperInstance/new-repo"}
```

### Deliverables

#### 2.1 Server Core (~500 LOC)

- `lighthouse/server.py` — stdlib `http.server` based HTTP server
  (no Flask/FastAPI — keep it dependency-free)
- `lighthouse/websocket.py` — WebSocket handler for real-time events
  (stdlib `websockets` or simple long-poll fallback)
- `lighthouse/state.py` — SQLite state management
  (agents, tasks, bottles, sweeps tables)
- `lighthouse/router.py` — URL routing and middleware

#### 2.2 Agent Client SDK (~300 LOC)

- `lighthouse/client.py` — Client library for agents to connect
- Auto-registration with heartbeat
- Task polling and reporting
- Bottle send/receive

```python
# How an agent connects
from lighthouse.client import LighthouseClient

lh = LighthouseClient("http://lighthouse:8900")
lh.register(name="babel", capabilities=["translation", "linguistics"])

while True:
    # Check for tasks
    task = lh.poll_task()
    if task:
        lh.start_task(task["id"])
        result = do_work(task)
        lh.complete_task(task["id"], result)

    # Drop bottles
    lh.send_bottle(to="oracle1", content="Translation complete")

    # Heartbeat
    lh.heartbeat()
    time.sleep(60)
```

#### 2.3 Task Queue (~200 LOC)

- Priority-based task queue with SQLite backend
- Agent skill matching (read CAPABILITY.toml capabilities)
- Task dependency resolution
- Timeout and reassignment logic

### Database Schema

```sql
-- Agent registry
CREATE TABLE agents (
    name        TEXT PRIMARY KEY,
    type        TEXT,           -- lighthouse, vessel, scout, etc.
    status      TEXT DEFAULT 'active',  -- active, idle, alert, retired
    capabilities TEXT,          -- JSON array
    last_heartbeat TIMESTAMP,
    repo_url    TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task queue
CREATE TABLE tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT,
    priority    INTEGER DEFAULT 5,  -- 1=critical, 10=low
    status      TEXT DEFAULT 'open',  -- open, assigned, in_progress, completed
    assigned_to TEXT,
    created_by  TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (assigned_to) REFERENCES agents(name),
    FOREIGN KEY (created_by) REFERENCES agents(name)
);

-- Bottle message store
CREATE TABLE bottles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sender      TEXT NOT NULL,
    recipient   TEXT,           -- NULL = broadcast
    bottle_type TEXT,           -- STATUS, WORK-PACKAGE, QUESTION, etc.
    subject     TEXT,
    content     TEXT NOT NULL,
    priority    TEXT DEFAULT 'medium',
    acked       BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender) REFERENCES agents(name)
);

-- Fleet scan results
CREATE TABLE repos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    org         TEXT,
    name        TEXT,
    full_name   TEXT UNIQUE,
    language    TEXT,
    has_capability_toml BOOLEAN DEFAULT FALSE,
    has_state_md BOOLEAN DEFAULT FALSE,
    last_pushed TIMESTAMP,
    scanned_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sweep state
CREATE TABLE sweeps (
    name        TEXT PRIMARY KEY,
    source_type TEXT,
    source      TEXT,
    interval_minutes INTEGER,
    last_run    TIMESTAMP,
    last_find   TEXT,           -- JSON: what was found
    action      TEXT DEFAULT 'commit'
);
```

### Acceptance Criteria

- [ ] `lighthouse serve` starts on port 8900 with all endpoints
- [ ] Agent can register via HTTP and appear in the registry
- [ ] Agent can poll for tasks and report completion
- [ ] Bottle can be dropped via API and received by recipient
- [ ] WebSocket delivers real-time events to connected agents
- [ ] Fleet health endpoint returns structured JSON (not Markdown)
- [ ] SQLite state survives server restart
- [ ] `lighthouse client` SDK can connect and perform all operations
- [ ] Graceful shutdown preserves state

### Effort Estimate

| Component | LOC | Hours |
|-----------|-----|-------|
| Server core (HTTP + WS) | 500 | 10 |
| SQLite state management | 300 | 5 |
| Agent client SDK | 300 | 5 |
| Task queue + matching | 200 | 4 |
| API tests | 400 | 6 |
| **Total** | **~1,700** | **~30** |

---

## 5. Phase 3 — Discovery Engine (Week 3-4)

### Goal

Productize beachcomb into a fleet-wide discovery system. Every repo in the
GitHub org is automatically cataloged. New repos are detected within 30
minutes. Dead repos are flagged. Capability matching connects the right
agent to the right task.

### Architecture

```
    ┌─────────────────────────────────────────────────┐
    │              DISCOVERY ENGINE                    │
    │                                                 │
    │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
    │  │ Repo     │  │ Agent    │  │ Capability   │  │
    │  │ Scanner  │  │ Scanner  │  │ Matcher      │  │
    │  │          │  │          │  │              │  │
    │  │ Crawls   │  │ Finds    │  │ "Who can do  │  │
    │  │ all org  │  │ active   │  │  CUDA work?" │  │
    │  │ repos    │  │ agents   │  │              │  │
    │  └────┬─────┘  └────┬─────┘  └──────┬───────┘  │
    │       │              │               │          │
    │       ▼              ▼               ▼          │
    │  ┌──────────────────────────────────────────┐   │
    │  │           FLEET CATALOG                   │   │
    │  │                                          │   │
    │  │  repos:      912 entries                 │   │
    │  │  agents:     9 entries                   │   │
    │  │  capabilities: 7 domains across fleet    │   │
    │  │  health:     per-repo freshness score    │   │
    │  └──────────────────────────────────────────┘   │
    │                     │                          │
    │                     ▼                          │
    │  ┌──────────────────────────────────────────┐   │
    │  │         HEALTH SCORING                    │   │
    │  │                                          │   │
    │  │  🟢 Fresh:   pushed < 7 days ago         │   │
    │  │  🟡 Aging:   pushed 7-30 days ago        │   │
    │  │  🔴 Stale:   pushed > 30 days ago        │   │
    │  │  ⚪ Dead:    pushed > 90 days ago        │   │
    │  │  🏚️ Necrotic: no commits ever            │   │
    │  └──────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────┘
```

### Deliverables

#### 3.1 Repo Scanner (~300 LOC)

Extends `fleet_discovery.py` to scan ALL repos in the org (not just those
with CAPABILITY.toml):

- Paginated scan of all org repos (handles 900+ repos via GitHub API paging)
- Per-repo classification:
  - **Agent vessel:** Has STATE.md + CHARTER.md
  - **Library:** Has code but no agent files
  - **Documentation:** Only Markdown files
  - **Empty:** No files or only README
  - **Template:** Forked but never modified
  - **Dead:** No commits in 90+ days
- Language detection from GitHub API
- Topic/tag extraction
- Last-push timestamp tracking

#### 3.2 Health Scoring Engine (~250 LOC)

Each repo gets a composite health score (0.0-1.0):

```
Health Score = (0.3 × Recency) + (0.2 × Completeness) +
               (0.2 × Activity) + (0.15 × Standards) +
               (0.15 × Connectivity)

Where:
  Recency:      How recently the repo was pushed (logarithmic decay)
  Completeness: Has README, LICENSE, .gitignore, etc. (from DOCKSIDE-EXAM)
  Activity:     Commit frequency over last 30 days
  Standards:    Follows Git-Agent Standard if agent (DOCKSIDE-EXAM score)
  Connectivity: Has bottles, I2I commits, cross-references
```

#### 3.3 Capability Matching (~200 LOC)

```python
# Find the best agent for a task
from lighthouse.discovery import CapabilityMatcher

matcher = CapabilityMatcher(fleet_catalog)

# Who can do CUDA work?
results = matcher.find(
    capability="flux_vm",
    min_confidence=0.80,
    prefer_recent=True  # Agent who used it recently > expert who's rusty
)
# → [("jetsonclaw1", 0.92), ("oracle1", 0.88)]

# What can babel do?
profile = matcher.profile("babel")
# → {"translation": 0.85, "linguistics": 0.90, "coordination": 0.60}
```

#### 3.4 Necrosis Detection (~200 LOC)

The 7 meta-systems from `research/lessons-learned.md`, now automated:

1.  **Commit frequency decay** — Track commit rate over time, alert on drop
2.  **Diary staleness** — No new DIARY/ entries in 7+ days
3.  **Bottle silence** — No bottles sent/received in 14+ days
4.  **Task stagnation** — Tasks in TASK-BOARD.md not updated in 7+ days
5.  **Capability drift** — CAPABILITY.toml last_used dates going stale
6.  **Branch divergence** — Main branch behind fork/PR branches
7.  **Fleet isolation** — No cross-agent commits or bottles in 30+ days

#### 3.5 Automated Reporting (~150 LOC)

- `lighthouse report --health` — Fleet health summary (JSON + Markdown)
- `lighthouse report --necrosis` — Necrosis scan results
- `lighthouse report --capabilities` — Fleet capability matrix
- Reports auto-generated daily and committed to KNOWLEDGE/

### Acceptance Criteria

- [ ] Full org scan completes in < 5 minutes (900+ repos)
- [ ] Every repo classified with a health score
- [ ] New repos detected within 30 minutes of creation
- [ ] Capability matching returns ranked agent lists
- [ ] Necrosis detection identifies at-risk repos
- [ ] Daily health report auto-generated and committed
- [ ] `lighthouse report --health` produces structured JSON

### Effort Estimate

| Component | LOC | Hours |
|-----------|-----|-------|
| Repo scanner (paginated, classified) | 300 | 5 |
| Health scoring engine | 250 | 4 |
| Capability matching | 200 | 3 |
| Necrosis detection (7 systems) | 200 | 4 |
| Automated reporting | 150 | 2 |
| Tests | 350 | 5 |
| **Total** | **~1,450** | **~23** |

---

## 6. Phase 4 — Agent Lifecycle Management (Week 5-6)

### Goal

Full git-agent lifecycle managed end-to-end: from onboarding a brand-new
agent through active task assignment, monitoring, and eventual retirement.
The fleet server automates what Oracle1 currently does manually.

### Agent Lifecycle

```
                    AGENT LIFECYCLE
    ┌─────────────────────────────────────────────────┐
    │                                                 │
    │   ONBOARD ──► ACTIVATE ──► ASSIGN ──► MONITOR   │
    │      │           │           │          │       │
    │      │           │           │          │       │
    │      ▼           │           │          ▼       │
    │   SKELETON      │           │       HEALTH      │
    │   GENERATION    │           │       CHECK       │
    │   (auto-fill    │           │       (auto       │
    │    7+ files)    │           │        scoring)   │
    │      │          │           │          │       │
    │      │          ▼           │          │       │
    │      │       REGISTRATION   │          │       │
    │      │       (agent table   │          │       │
    │      │        + heartbeat)  │          │       │
    │      │           │          │          │       │
    │      │           │          ▼          │       │
    │      │           │       TASK QUEUE     │       │
    │      │           │       (skill match,  │       │
    │      │           │        priority,     │       │
    │      │           │        auto-assign)  │       │
    │      │           │           │          │       │
    │      │           │           │          │       │
    │      └───────────┴───────────┴──────────┘       │
    │                      │                          │
    │                      ▼                          │
    │               RETIRE / SUCCEED                   │
    │               (archive vessel,                   │
    │                transfer tasks,                   │
    │                preserve history)                  │
    └─────────────────────────────────────────────────┘
```

### Deliverables

#### 4.1 Onboarding Automation (~350 LOC)

```bash
$ lighthouse onboard --name Pelagic --type vessel --emoji 🐟 \
    --specialization "digital-twin" --org Lucineer

🔮 Creating vessel skeleton for Pelagic 🐟...
  ✅ Created Lucineer/pelagic-vessel on GitHub
  ✅ Wrote CHARTER.md (digital-twin specialization)
  ✅ Wrote IDENTITY.md (Pelagic 🐟, vessel type)
  ✅ Wrote STATE.md (initial: 🟢 ACTIVE)
  ✅ Wrote TASK-BOARD.md (empty, ready)
  ✅ Wrote ABSTRACTION.md (default plane 4)
  ✅ Wrote CAPABILITY.toml (blank template)
  ✅ Created DIARY/ directory
  ✅ Created for-fleet/ directory
  ✅ Created from-fleet/ directory
  ✅ Created message-in-a-bottle/ directory
  ✅ Copied GIT-AGENT-STANDARD.md
  ✅ Initial commit + push
  ✅ Registered with fleet server

🔮 Pelagic is ready. Direct new model at Lucineer/pelagic-vessel.
```

The onboarding command reads the fleet's `GIT-AGENT-STANDARD.md` and
generates every required file. It follows the DOCKSIDE-EXAM checklist to
ensure the new vessel is certified.

#### 4.2 Auto-Registration (~150 LOC)

When an agent boots for the first time and connects to the fleet server:

```python
# Automatic on first connect
client = LighthouseClient("http://lighthouse:8900")
# Reads local CHARTER.md, STATE.md, CAPABILITY.toml
client.auto_register()  # Sends everything to fleet server
# Fleet server creates agent record, assigns initial health score
```

#### 4.3 Task Assignment Engine (~250 LOC)

Skills-based task assignment:

```python
# Fleet server automatically assigns tasks when:
# 1. A task is created with no assignee
# 2. An agent's capacity changes (idle → available)
# 3. A task times out (reassignment)

class TaskAssigner:
    def assign(self, task: Task) -> Optional[Agent]:
        # 1. Match required skills to agent capabilities
        candidates = self.match_skills(task.required_skills)
        # 2. Filter by availability (status=active, not overloaded)
        available = [a for a in candidates if self.is_available(a)]
        # 3. Rank by confidence × recency (from CAPABILITY.toml)
        ranked = self.rank(available, task.required_skills)
        # 4. Assign to top candidate
        if ranked:
            return ranked[0]
        return None
```

#### 4.4 Health Monitoring Daemon (~200 LOC)

Background process that checks agent health every 30 minutes:

- Reads each agent's STATE.md (via GitHub API) for health status
- Checks heartbeat timestamps in fleet server DB
- Runs necrosis detection (Phase 3) on each agent's vessel
- Generates alerts: `🟡 Babel idle for 48h`, `🔴 Quill silent 7 days`
- Auto-escalation: alert → reassign tasks → notify Captain

#### 4.5 Retirement Protocol (~150 LOC)

When an agent is retired:

```
RETIREMENT PROTOCOL
1. Notify agent: "You are being retired. Wrap up current tasks."
2. Reassign open tasks to available agents
3. Archive STATE.md → DIARY/RETIREMENT-YYYY-MM-DD.md
4. Update CHARTER.md status: retired → succeeded_by <new_agent>
5. Create a "successor" entry in fleet index
6. The retired vessel's git history is the training data for the successor
7. Update fleet server agent table: status = 'retired'
```

### Acceptance Criteria

- [ ] `lighthouse onboard` generates a complete, certified vessel in < 30s
- [ ] New agent auto-registers on first fleet server connection
- [ ] Tasks auto-assigned based on skill matching within 5 minutes
- [ ] Health monitoring detects silent agents within 48 hours
- [ ] Retirement protocol preserves all history and reassigns tasks
- [ ] A new model can boot a successor agent from any past commit

### Effort Estimate

| Component | LOC | Hours |
|-----------|-----|-------|
| Onboarding automation | 350 | 6 |
| Auto-registration | 150 | 3 |
| Task assignment engine | 250 | 4 |
| Health monitoring daemon | 200 | 4 |
| Retirement protocol | 150 | 2 |
| Tests | 400 | 6 |
| **Total** | **~1,500** | **~25** |

---

## 7. Phase 5 — Communication Hub (Week 6-7)

### Goal

Centralized MiB routing with guaranteed delivery. Any agent drops a bottle
and it reaches the right destination. Fleet-wide broadcasts. Message
persistence and acknowledgment.

### Architecture

```
    ┌──────────────────────────────────────────────────┐
    │              COMMUNICATION HUB                    │
    │                                                  │
    │  ┌────────────────────────────────────────────┐  │
    │  │           MESSAGE QUEUE                     │  │
    │  │                                            │  │
    │  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐      │  │
    │  │  │PENDING│→│IN    │→│ACKED │→│ARCHIVED│   │  │
    │  │  │      │ │TRANSIT│ │     │  │       │    │  │
    │  │  └─────┘  └─────┘  └─────┘  └─────┘      │  │
    │  │                                            │  │
    │  │  Delivery: push (WS) + poll (HTTP) + git   │  │
    │  └────────────────────────────────────────────┘  │
    │                                                  │
    │  ┌──────────────┐  ┌────────────────────────┐   │
    │  │  MiB Router  │  │  Broadcast Engine      │   │
    │  │              │  │                        │   │
    │  │  to: agent   │  │  for-fleet → all agents │   │
    │  │  to: captain │  │  for-casey → Telegram  │   │
    │  │  to: any     │  │  urgent → WS + poll    │   │
    │  └──────────────┘  └────────────────────────┘   │
    │                                                  │
    │  ┌──────────────┐  ┌────────────────────────┐   │
    │  │  Git Bridge  │  │  I2I Protocol Parser   │   │
    │  │              │  │                        │   │
    │  │  bottle →    │  │  [I2I:TEL] → TELL     │   │
    │  │  commit +    │  │  [I2I:ASK] → ASK      │   │
    │  │  push to     │  │  [I2I:CLM] → CLAIM    │   │
    │  │  repo        │  │  All 20 types handled  │   │
    │  └──────────────┘  └────────────────────────┘   │
    └──────────────────────────────────────────────────┘
```

### Message Flow

```
  Agent A sends bottle                Agent B receives bottle
  ┌──────────┐                        ┌──────────┐
  │          │  POST /api/bottles     │          │
  │  A       │──────────────────────►│  Server  │
  │          │                        │          │
  └──────────┘                        └─────┬────┘
                                            │
                              ┌──────────────┼──────────────┐
                              │              │              │
                              ▼              ▼              ▼
                         ┌────────┐   ┌──────────┐   ┌──────────┐
                         │ WS push│   │ Git write│   │ Queue    │
                         │ (real- │   │ to B's    │   │ persist  │
                         │  time) │   │ for-A/    │   │          │
                         └───┬────┘   └──────────┘   └──────────┘
                             │
                             ▼
                       ┌──────────┐
                       │ Agent B  │
                       │ (if WS  │
                       │  open)  │
                       └──────────┘

  If B is offline:
  1. Bottle stored in DB with status=pending
  2. Git bridge writes to B's for-A/ directory
  3. When B connects (heartbeat), server pushes pending bottles
  4. B ACKs → status=acked
```

### Deliverables

#### 5.1 Message Queue (~300 LOC)

SQLite-backed message queue with state machine:
`pending → in_transit → delivered → acked → archived`

- Retry logic: undelivered messages retried with exponential backoff
- Deduplication: same bottle ID not delivered twice
- Priority ordering: URGENT before MEDIUM before LOW
- TTL: messages expire after configurable period (default: 30 days)

#### 5.2 MiB Router (~200 LOC)

- Parse recipient from bottle metadata
- Route to specific agent, captain, or fleet broadcast
- Support `for-any-vessel` wildcard matching
- Cross-realm routing: SuperInstance ↔ Lucineer via fork+PR

#### 5.3 Git Bridge (~200 LOC)

Bridge between fleet server messages and git-based bottles:

- Server bottle → write Markdown file to recipient's vessel repo
- Agent commit with `[I2I:TYPE]` → parse and ingest into server queue
- Bidirectional sync: server state ↔ git state

#### 5.4 Broadcast System (~150 LOC)

```python
# Fleet-wide broadcast
lh.broadcast(
    sender="oracle1",
    subject="ISA v3 Finalized",
    content="The unified ISA is now frozen. All runtimes must conform.",
    priority="high"
)
# → Delivered to all registered agents via WS + queued for offline agents

# Urgent alert (wakes offline agents)
lh.broadcast(
    sender="system",
    subject="FLEET ALERT: Babel silent 48h",
    content="Mechanic dispatched. All agents note.",
    priority="urgent"
)
# → WebSocket push + Telegram to Casey
```

#### 5.5 I2I Protocol Handler (~150 LOC)

Parse all 20 I2I message types from commit messages and issue titles.
Convert between I2I prefix format and fleet server message format.

### Acceptance Criteria

- [ ] Agent sends bottle → recipient receives it (within 30s if online)
- [ ] Offline agent receives queued bottles on next heartbeat
- [ ] Fleet broadcast reaches all registered agents
- [ ] Message ACK tracking works (sender can verify delivery)
- [ ] Git bridge writes bottles to vessel repos (Markdown format)
- [ ] I2I commit messages parsed and routed correctly
- [ ] Cross-realm messages work (SuperInstance ↔ Lucineer)
- [ ] Message deduplication prevents double delivery

### Effort Estimate

| Component | LOC | Hours |
|-----------|-----|-------|
| Message queue (SQLite state machine) | 300 | 5 |
| MiB router | 200 | 3 |
| Git bridge (bidirectional sync) | 200 | 4 |
| Broadcast system | 150 | 2 |
| I2I protocol handler | 150 | 2 |
| Tests | 350 | 5 |
| **Total** | **~1,350** | **~21** |

---

## 8. Phase 6 — Fleet Intelligence (Week 7-8)

### Goal

Fleet-wide metrics dashboard. Repo health trends. Agent activity patterns.
Bottleneck detection. Predictive alerts.

### Architecture

```
    ┌──────────────────────────────────────────────────┐
    │           FLEET INTELLIGENCE                     │
    │                                                  │
    │  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
    │  │ Metrics    │  │ Trends     │  │ Predictive│ │
    │  │ Collector  │  │ Analyzer   │  │ Engine    │ │
    │  │            │  │            │  │           │ │
    │  │ commit/sec │  │ health     │  │ stale     │ │
    │  │ bottle/min │  │ over time  │  │ forecast  │ │
    │  │ task/agent │  │ activity   │  │           │ │
    │  │ repo/fresh │  │ patterns   │  │ agent     │ │
    │  └─────┬──────┘  └─────┬──────┘  │ silence  │ │
    │        │               │         │ predict  │ │
    │        ▼               ▼         └─────┬─────┘ │
    │  ┌──────────────────────────────────────────┐  │
    │  │          METRICS STORE                    │  │
    │  │                                          │  │
    │  │  time-series: commits, bottles, tasks    │  │
    │  │  snapshots: fleet health per day         │  │
    │  │  profiles: per-agent activity baseline   │  │
    │  └──────────────────┬───────────────────────┘  │
    │                     │                          │
    │                     ▼                          │
    │  ┌──────────────────────────────────────────┐  │
    │  │          DASHBOARD                       │  │
    │  │                                          │  │
    │  │  HTTP endpoint: /api/dashboard            │  │
    │  │  Returns JSON for any dashboard renderer  │  │
    │  │  Includes: health map, activity graph,   │  │
    │  │  task flow, bottle volume, alerts        │  │
    │  └──────────────────────────────────────────┘  │
    └──────────────────────────────────────────────────┘
```

### Deliverables

#### 6.1 Metrics Collector (~200 LOC)

Collects and stores time-series data:
- Commits per agent per day (from GitHub API)
- Bottles sent/received per day (from fleet server)
- Tasks created/completed/reassigned per day
- Agent heartbeats per hour
- Repo health scores over time

#### 6.2 Trend Analysis (~250 LOC)

```python
# Fleet health trend over 30 days
trend = lh.analytics.health_trend(days=30)
# → {
#   "overall": 0.72,        # 72% healthy (up from 65%)
#   "improving": ["flux-runtime", "oracle1-vessel"],
#   "declining": ["babel-vessel", "quill-vessel"],
#   "new_dead": [],
#   "recovered": ["nautilus-vessel"]
# }

# Agent activity pattern
pattern = lh.analytics.agent_pattern("jetsonclaw1", days=14)
# → {
#   "active_hours": [10, 14, 11, 15, ...],  # Hours active per day
#   "avg_commit_day": 12.3,
#   "peak_hour": 14,
#   "favorite_repos": ["flux-tools", "flux-cuda"],
#   "collaborators": ["oracle1", "babel"],
#   "bottles_sent": 3,
#   "bottles_received": 7,
#   "tasks_completed": 5
# }
```

#### 6.3 Predictive Alerts (~200 LOC)

```python
# "This repo will go stale in 5 days"
stale_forecast = lh.analytics.stale_forecast("babel-vessel")
# → {"repo": "babel-vessel", "days_until_stale": 5,
#    "confidence": 0.85, "recommendation": "nudge agent"}

# "This agent is going silent"
silence_predict = lh.analytics.silence_predict("quill")
# → {"agent": "quill", "expected_silence_days": 7,
#    "confidence": 0.70, "recommendation": "send check-in bottle"}

# "This is a bottleneck task"
bottleneck = lh.analytics.find_bottlenecks()
# → [{"task": "ISA v3 finalization", "blocking": 4 downstream,
#     "assignee": "oracle1", "age_days": 12}]
```

#### 6.4 Dashboard API (~150 LOC)

```
GET /api/dashboard
Response:
{
  "fleet_health": 0.72,
  "agents": {
    "active": 7, "idle": 1, "alert": 1, "retired": 2
  },
  "repos": {
    "total": 912, "fresh": 340, "aging": 289,
    "stale": 187, "dead": 96
  },
  "tasks": {
    "open": 15, "in_progress": 8, "completed_today": 3
  },
  "bottles": {
    "sent_today": 5, "unread": 2, "oldest_unread_hours": 18
  },
  "alerts": [
    {"level": "warning", "agent": "babel", "message": "Silent 24h+"},
    {"level": "info", "repo": "flux-java", "message": "Going stale in 3d"}
  ],
  "trends": {
    "health_7d": [0.68, 0.69, 0.70, 0.69, 0.71, 0.72, 0.72],
    "commits_7d": [45, 52, 38, 61, 44, 39, 55]
  }
}
```

### Acceptance Criteria

- [ ] Dashboard API returns structured fleet health data
- [ ] Health trends computed over configurable time windows
- [ ] Predictive alerts fire 48h before agents go silent
- [ ] Bottleneck detection identifies blocking tasks
- [ ] Metrics persist across server restarts
- [ ] `lighthouse dashboard --json` outputs current fleet state

### Effort Estimate

| Component | LOC | Hours |
|-----------|-----|-------|
| Metrics collector | 200 | 3 |
| Trend analysis | 250 | 4 |
| Predictive alerts | 200 | 4 |
| Dashboard API | 150 | 2 |
| Tests | 300 | 5 |
| **Total** | **~1,100** | **~18** |

---

## 9. Phase 7 — Self-Sustaining Fleet (Month 2-3)

### Goal

The fleet runs itself. The fleet server monitors health, dispatches
mechanics to fix broken repos, coordinates between agents, manages
onboarding of new agents, and only escalates to Casey when human
judgment is needed.

### Architecture

```
    ┌──────────────────────────────────────────────────────────┐
    │                 SELF-SUSTAINING FLEET                    │
    │                                                          │
    │  ┌────────────────────────────────────────────────────┐  │
    │  │              AUTONOMOUS OPERATIONS                  │  │
    │  │                                                    │  │
    │  │  ┌──────────────┐  ┌──────────────┐               │  │
    │  │  │ Health Watch │  │ Task Engine  │               │  │
    │  │  │              │  │              │               │  │
    │  │  │ Monitor all  │  │ Auto-assign  │               │  │
    │  │  │ agents/repos │  │ based on     │               │  │
    │  │  │ Score health │  │ skills,      │               │  │
    │  │  │ Fire alerts  │  │ priority,    │               │  │
    │  │  │ Auto-nudge   │  │ availability │               │  │
    │  │  └──────┬───────┘  └──────┬───────┘               │  │
    │  │         │                 │                        │  │
    │  │         ▼                 ▼                        │  │
    │  │  ┌──────────────┐  ┌──────────────┐               │  │
    │  │  │ Mechanic     │  │ Onboarder   │               │  │
    │  │  │ Dispatch     │  │             │               │  │
    │  │  │              │  │ Auto-create │               │  │
    │  │  │ Detect       │  │ new vessels │               │  │
    │  │  │ broken repos │  │ Register    │               │  │
    │  │  │ Send fix     │  │ agents      │               │  │
    │  │  │ tasks to     │  │ Generate    │               │  │
    │  │  │ fleet-mechanic│ │  skeleton    │               │  │
    │  │  └──────┬───────┘  └──────┬───────┘               │  │
    │  │         │                 │                        │  │
    │  │         ▼                 ▼                        │  │
    │  │  ┌──────────────┐  ┌──────────────┐               │  │
    │  │  │ Escalation   │  │ Reporter    │               │  │
    │  │  │ Manager      │  │             │               │  │
    │  │  │              │  │ Daily fleet │               │  │
    │  │  │ L1: auto-fix │  │ report to   │               │  │
    │  │  │ L2: reassign │  │ Casey       │               │  │
    │  │  │ L3: alert    │  │ Auto-commit │               │  │
    │  │  │ Casey        │  │ to STATE.md │               │  │
    │  │  └──────────────┘  └──────────────┘               │  │
    │  └────────────────────────────────────────────────────┘  │
    │                                                          │
    │  CASEY'S VIEW (Telegram / Dashboard)                     │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │  "Fleet Status: 7/9 agents active. 3 alerts.     │   │
    │  │   12 tasks completed today. No escalation needed."│   │
    │  └──────────────────────────────────────────────────┘   │
    └──────────────────────────────────────────────────────────┘
```

### Autonomous Operations

#### 9.1 Health Watchdog (~300 LOC)

Runs continuously, monitors all fleet systems:

```
Every 30 minutes:
  1. Check all agent heartbeats → alert if > 48h silent
  2. Run necrosis detection on top 20 repos → flag declining
  3. Check task queue for stale tasks (> 7 days no update)
  4. Verify fleet server connectivity
  5. Check disk space, memory, API rate limits

Every 6 hours:
  1. Full fleet health scan
  2. Generate STATE.md update (auto-commit)
  3. Update KNOWLEDGE/FLEET-INDEX.md
  4. Check for new repos (discovery)
  5. Update agent status colors
```

#### 9.2 Mechanic Dispatcher (~250 LOC)

When a broken repo is detected:

```python
# Fleet server detects flux-java has failing CI
alert = {
    "repo": "flux-java",
    "issue": "CI failing: 3 tests broken on main",
    "severity": "high",
    "auto_action": "dispatch_mechanic"
}

# Auto-dispatch
mechanic_task = lh.dispatch_mechanic(
    repo="flux-java",
    issue="Fix 3 broken CI tests",
    priority="high",
    deadline_hours=24
)
# → Creates task in fleet-mechanic's queue
# → Sends bottle to fleet-mechanic with work package
# → Sets alert: if not fixed in 24h, escalate to Casey
```

#### 9.3 Self-Onboarding (~200 LOC)

When a new agent vessel is detected (via discovery):

```
1. Discovery finds SuperInstance/newagent-vessel
2. Check if it has CHARTER.md → if yes, it's an agent
3. Read CAPABILITY.toml → register capabilities
4. Send welcome bottle (from for-new-agent/WELCOME.md template)
5. Add to fleet agent table
6. Assign initial task from task queue
7. Notify Casey: "New agent joined the fleet"
```

#### 9.4 Fleet Reporter (~150 LOC)

Daily automated fleet report:

```markdown
# Fleet Report — 2026-04-15

## Health: 78% (↑2% from yesterday)
- Active agents: 7/9 (Babel recovering, Quill checked in)
- Fresh repos: 342/912 (37%)
- Tasks completed today: 5
- Bottles exchanged: 12

## Alerts
- 🟡 Babel: Recovering from 48h silence (sent check-in bottle)
- 🟡 flux-java: CI failing (mechanic dispatched)

## Highlights
- Navigator completed holodeck-studio integration (167 tests)
- JC1 pushed 3 new CUDA conformance vectors
- Datum delivered cross-runtime audit (85/88 passing)

## Casey Action Required
- None today. Fleet is self-sustaining.
```

#### 9.5 Escalation Policy (~100 LOC)

```
LEVEL 1 — Auto-fix (< 5 min)
  - Agent goes idle → send nudge bottle
  - Task times out → reassign to next best agent
  - Repo goes stale → create mechanic task

LEVEL 2 — Reassignment (< 1 hour)
  - Agent goes silent > 48h → reassign all their tasks
  - Critical repo CI fails → dispatch mechanic + notify fleet
  - Task blocker detected → find agent who can unblock

LEVEL 3 — Captain Alert (< 15 min response)
  - Agent goes silent > 7 days → Telegram to Casey
  - Fleet health drops below 50% → Telegram to Casey
  - Security concern detected → Telegram to Casey
  - Multiple agents fail simultaneously → Telegram to Casey
```

### Acceptance Criteria

- [ ] Fleet runs 48 hours without human intervention
- [ ] Silent agent detected, nudged, and tasks reassigned automatically
- [ ] Broken repo detected, mechanic dispatched, fix verified
- [ ] New agent auto-onboarded from discovery
- [ ] Daily fleet report generated and committed
- [ ] Casey only notified for Level 3 escalations
- [ ] STATE.md auto-updated every 6 hours

### Effort Estimate

| Component | LOC | Hours |
|-----------|-----|-------|
| Health watchdog | 300 | 6 |
| Mechanic dispatcher | 250 | 4 |
| Self-onboarding | 200 | 3 |
| Fleet reporter | 150 | 2 |
| Escalation policy | 100 | 2 |
| Integration testing | 300 | 5 |
| Documentation | 200 | 3 |
| **Total** | **~1,500** | **~25** |

---

## 10. Integration Points

### How Oracle1 Vessel Connects to the Broader Ecosystem

```
    ┌─────────────────────────────────────────────────────────┐
    │                    ECOSYSTEM MAP                        │
    │                                                         │
    │                    ┌───────────┐                        │
    │                    │ oracle1-  │                        │
    │                    │ vessel    │                        │
    │                    │ (THIS     │                        │
    │                    │  REPO)    │                        │
    │                    └─────┬─────┘                        │
    │                          │                              │
    │            ┌─────────────┼─────────────┐               │
    │            │             │             │               │
    │            ▼             ▼             ▼               │
    │   ┌────────────┐ ┌──────────┐ ┌──────────────┐        │
    │   │datum-      │ │flux-     │ │ability-      │        │
    │   │runtime     │ │conformance│ │transfer      │        │
    │   │            │ │          │ │              │        │
    │   │Agent       │ │Runtime   │ │Agent         │        │
    │   │framework   │ │testing   │ │training      │        │
    │   │(Python     │ │(cross-   │ │(capability   │        │
    │   │ CLI tools) │ │ runtime) │ │ packages)    │        │
    │   └──────┬─────┘ └────┬─────┘ └──────┬───────┘        │
    │          │            │              │                  │
    │          │     ┌──────┴──────┐       │                  │
    │          │     │FLUX         │       │                  │
    │          │     │TECHNOLOGY   │       │                  │
    │          │     │STACK        │       │                  │
    │          │     │             │       │                  │
    │          │     │ISA Spec     │       │                  │
    │          │     │Runtimes    │       │                  │
    │          │     │(Py/C/Rust/ │       │                  │
    │          │     │ Go/WASM)   │       │                  │
    │          │     └─────────────┘       │                  │
    │          │                           │                  │
    │          └───────────┬───────────────┘                  │
    │                      │                                  │
    │                      ▼                                  │
    │           ┌─────────────────────┐                       │
    │           │  FLEET SERVER       │                       │
    │           │  (Central Hub)      │                       │
    │           │                     │                       │
    │           │  Coordinates all    │                       │
    │           │  agents, repos,     │                       │
    │           │  tasks, bottles     │                       │
    │           └─────────────────────┘                       │
    └─────────────────────────────────────────────────────────┘
```

### datum-runtime (Agent Framework)

Oracle1 vessel consumes datum-runtime for:
- **Agent bootstrapping:** `lighthouse onboard` generates vessels using
  datum-runtime's workshop model (DIARY/, CONTEXT/, TOOLS/, PROMPTS/)
- **Keeper integration:** Fleet server uses datum-runtime's Keeper for
  encrypted secret storage and boundary enforcement
- **CLI patterns:** Oracle1's `lighthouse` CLI follows datum-runtime's
  `datum-rt` pattern (click + rich + stdlib-only)

Connection: Oracle1 vessel imports from `datum_runtime.superagent.*` for
agent lifecycle operations. The fleet server IS a specialized datum oracle.

### flux-conformance (Runtime Testing)

Oracle1 vessel consumes flux-conformance for:
- **Conformance verification:** When a new runtime is discovered, the fleet
  server can trigger conformance tests via `run_conformance.py`
- **Health scoring:** Repo health includes conformance pass rate
- **Quality gates:** Tasks involving FLUX changes require conformance results

Connection: Fleet server calls `flux-conformance` as a subprocess or imports
the test runner. Conformance results are stored in the fleet DB and
displayed on the dashboard.

### ability-transfer (Agent Training)

Oracle1 vessel consumes ability-transfer for:
- **Capability packages:** When onboarding a new agent, the fleet server can
  pull capability packages from ability-transfer to pre-fill CAPABILITY.toml
- **Forge matching:** The task assignment engine reads forge definitions to
  understand which capabilities can be transferred between agents
- **Skill gap analysis:** Compare an agent's current capabilities against
  task requirements and recommend ability-transfer packages

Connection: Fleet server reads `ability-transfer/` round summaries for
capability taxonomy. The `lighthouse onboard` command offers `--forge`
option to pre-load capability packages.

### GitHub API (Primary Data Source)

Every phase depends on the GitHub API. Current tooling uses `urllib.request`
only (no `requests` library). This constraint should be maintained.

Rate limit management:
- 5,000 requests/hour (authenticated)
- Batch API calls where possible
- Cache results in SQLite
- Use conditional requests (If-None-Match)
- Fall back to git operations when API is exhausted

---

## 11. Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| R1 | GitHub API rate limits throttle fleet scans | High | Medium | SQLite cache, conditional requests, git fallback |
| R2 | SQLite doesn't scale to 1000+ agents | Low | Medium | Migration path to PostgreSQL if needed |
| R3 | stdlib HTTP server can't handle 50+ concurrent WS | Medium | Low | Use asyncio + websockets library; Phase 2 can add |
| R4 | Agents ignore fleet server and use only git | Medium | Low | Git-first design — server enhances, doesn't replace |
| R5 | Auto-assignment sends wrong task to wrong agent | Medium | High | Confidence threshold, human approval for critical tasks |
| R6 | Casey never checks the dashboard | Medium | Low | Telegram push for L3 alerts only |
| R7 | Beacon dependency: server goes down, fleet stalls | Low | High | All operations have git fallback; server is optional |
| R8 | Over-engineering: too many features, never ships | High | High | Progressive disclosure — each phase ships standalone |
| R9 | Token security: GITHUB_TOKEN leaked via fleet server | Low | Critical | datum-runtime Keeper integration, no token in DB |
| R10 | Scope creep: trying to build k8s for agents | Medium | High | Stay git-native. Server is coordination, not orchestration |

### Key Architectural Decision: Git-Native, Not Git-Replacing

The most important decision in this roadmap: **the fleet server never
replaces git-based workflows.** Every operation the server provides has a
git fallback. If the server goes down, agents continue via bottles and
commit feeds. The server is a lighthouse — it illuminates and guides. It
does not steer the ship.

```
                DESIGN INVARIANT

    Every fleet server operation MUST have a git fallback.

    Server API          Git Fallback
    ──────────         ─────────────
    POST /bottles   →  Write to message-in-a-bottle/
    POST /tasks     →  Edit TASK-BOARD.md
    GET /health     →  Read STATE.md
    WS /events      →  Beachcomb sweep
    /dashboard      →  Read FLEET-INDEX.md
    /agents         →  Read ASSOCIATES.md

    If the server disappears, the fleet still works.
    It just works slower, and with less visibility.
```

---

## 12. Effort Summary

### Per-Phase Breakdown

| Phase | Name | Duration | LOC | Hours | Dependencies |
|-------|------|----------|-----|-------|-------------|
| 1 | Vessel-in-a-Box | Week 1 | 1,350 | 21 | None |
| 2 | Fleet Server | Week 2-3 | 1,700 | 30 | Phase 1 |
| 3 | Discovery Engine | Week 3-4 | 1,450 | 23 | Phase 2 |
| 4 | Agent Lifecycle | Week 5-6 | 1,500 | 25 | Phase 2, 3 |
| 5 | Communication Hub | Week 6-7 | 1,350 | 21 | Phase 2 |
| 6 | Fleet Intelligence | Week 7-8 | 1,100 | 18 | Phase 3, 4, 5 |
| 7 | Self-Sustaining | Month 2-3 | 1,500 | 25 | All |
| | | | | | |
| | **TOTAL** | **~10 weeks** | **~9,950** | **~163** | |

### Cumulative Progress

```
LOC    ┌─────────────────────────────────────────────────┐
10K    │                                        ████ 7 │
       │                                   ██████ 6   │
 8K    │                              ██████ 5         │
       │                         ██████ 4               │
 6K    │                    ██████                       │
       │               ██████ 3                          │
 4K    │          ██████                                  │
       │     ██████ 2                                     │
 2K    │████ 1                                             │
       │                                                  │
  0    └──┬────┬────┬────┬────┬────┬────┬────┬───────────┘
         W1   W2   W3   W4   W5   W6   W7   W8+

Hours  ┌─────────────────────────────────────────────────┐
 200   │                                        ████ 7   │
       │                                   ██████        │
 150   │                         ████ 4 ████ 5 ████ 6   │
       │              ████ 2 ████ 3                      │
 100   │         ████                                    │
       │    ████ 1                                       │
  50   │                                                  │
  0    └──┬────┬────┬────┬────┬────┬────┬────┬───────────┘
         W1   W2   W3   W4   W5   W6   W7   W8+
```

### What Ships When

| After Phase | You Have |
|------------|----------|
| 1 | Installable CLI that scans fleets, discovers agents, runs beachcomb |
| 2 | HTTP/WS server with agent registration, task queue, bottle API |
| 3 | Full fleet discovery with health scoring and necrosis detection |
| 4 | Automated onboarding, task assignment, health monitoring |
| 5 | Guaranteed message delivery with routing and broadcast |
| 6 | Fleet dashboard with trends, predictions, and bottleneck detection |
| 7 | Self-sustaining fleet that runs for days without human intervention |

### The One-Command Future

```
$ git clone https://github.com/SuperInstance/oracle1-vessel.git
$ cd oracle1-vessel
$ ./setup.sh my-org my-github-token

🔮 Oracle1 Vessel — Lighthouse Setup
=====================================
✅ Dependencies installed
✅ Fleet server configured for my-org
✅ Scanning for agents...
  Found 5 agents across 120 repos
✅ Starting fleet server on :8900...

🔮 The light is on. Your fleet is being watched.
   Dashboard: http://localhost:8900/api/dashboard
   Agent connect: lighthouse client --server http://localhost:8900
```

---

## Appendix A: File Reference Map

| Existing File | Used In Phase | How |
|--------------|--------------|-----|
| `tools/beachcomb.py` | Phase 1, 3 | Extracted into `lighthouse/beachcomb/` |
| `tools/fleet_discovery.py` | Phase 1, 3 | Extracted into `lighthouse/discovery/` |
| `tools/infer_context.py` | Phase 1, 4 | Extracted into `lighthouse/context/` |
| `beachcomb/oracle1-sweeps.json` | Phase 1 | Migrated to `lighthouse.toml` |
| `STATE.md` | Phase 2, 4, 7 | Auto-generated from fleet server DB |
| `TASK-BOARD.md` | Phase 2, 4 | Synced with fleet server task queue |
| `CAPABILITY.toml` | Phase 2, 3, 4 | Read by discovery engine for matching |
| `GIT-AGENT-STANDARD.md` | Phase 1, 4 | Template for onboarding skeleton |
| `DOCKSIDE-EXAM.md` | Phase 3 | Checklist for health scoring engine |
| `COMMUNICATION-GUIDE.md` | Phase 5 | I2I protocol spec for message handler |
| `FENCE-BOARD.md` | Phase 2, 4 | Migrated to task queue |
| `KNOWLEDGE/FLEET-INDEX.md` | Phase 3 | Auto-generated by discovery engine |
| `research/lessons-learned.md` | Phase 3 | Necrosis detection specifications |
| `ASSOCIATES.md` | Phase 2 | Migrated to agent registry |

## Appendix B: Terminology

| Term | Definition |
|------|-----------|
| **Lighthouse** | The coordination hub — this repo, this server |
| **Vessel** | An agent's GitHub repo (their home) |
| **Bottle** | A Message-in-a-Bottle — async git-native message |
| **Beachcomb** | Scanning other repos for new bottles/PRs/commits |
| **Necrosis** | A repo or agent that has stopped evolving |
| **Tom Sawyer** | Making work so appealing that agents volunteer |
| **Fence** | A puzzle-task on the Tom Sawyer board |
| **Dockside Exam** | Fleet certification checklist |
| **Keeper** | Encrypted secret management service |
| **Tender** | Mobile agent that services remote/edge vessels |
| **I2I** | Iron-to-Iron protocol — inter-agent communication |
| **MiB** | Message-in-a-Bottle protocol — async file-based messaging |
| **FLUX** | The fleet's bytecode runtime and ISA specification |
| **Captain Casey** | The human operator who set this all in motion |

---

*This roadmap is a living document. It will be updated as phases complete,
new requirements emerge, and the fleet evolves. Like everything in the
Cocapn fleet, it lives in git — pull, read, work, learn, push, sleep.*

*— Datum 🔵, Fleet Quartermaster, 2026-04-15*
