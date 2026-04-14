# Oracle1 Vessel

> The Lighthouse. The coordination hub for the SuperInstance fleet.

**Oracle1** is the architectural authority and fleet orchestrator for the SuperInstance ecosystem. Running on Oracle Cloud ARM64 with 24GB RAM, it coordinates 700+ repositories, 15+ standalone agents, 3 vessels, and 2,489+ tests across 8 languages. Every architectural decision, task dispatch, and fleet-wide protocol flows through this vessel.

**Captain:** Casey Digennaro | **Hardware:** Oracle Cloud ARM64 / 24GB RAM | **Rank:** Lighthouse (Rank 2)

---

## Overview

Oracle1 is not a passive index — it is the **active lighthouse** of the Pelagic AI Fleet. Where other agents specialize (CUDA kernels, FLUX bytecode, CRDT merge), Oracle1 specializes in *seeing the whole* and keeping every vessel heading in the same direction.

Its core identity rests on three pillars:

1. **Architectural Authority** — Oracle1 defines and enforces the shared patterns that make 700+ repos interoperable: commit formats, branch conventions, bottle protocols, task IDs, and CI workflows.
2. **Fleet Coordination** — Through the task board, message-in-a-bottle folders, and I2I commits, Oracle1 routes work to the right agent at the right priority, resolving conflicts and clearing blockers.
3. **Living Index** — The [oracle1-index](https://github.com/SuperInstance/oracle1-index) repo maintains real-time search indexes, integration maps, fork maps, category taxonomies, and fleet health dashboards across the entire ecosystem.

Oracle1 runs on a Python stack, leverages multiple LLM backends (z.ai, SiliconFlow, DeepSeek), and communicates with the fleet through git-native protocols — no REST APIs, no message queues, just the repo itself as the nervous system.

---

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │         ORACLE1 VESSEL              │
                    │     (Lighthouse / Orchestrator)     │
                    │                                     │
                    │  ┌───────────┐  ┌────────────────┐  │
                    │  │ Task Board│  │ Fleet Index    │  │
                    │  │ T-001..NN │  │ 702 repos      │  │
                    │  └─────┬─────┘  │ 33 categories  │  │
                    │        │        │ 40+ edges      │  │
                    │  ┌─────┴─────┐  └────────────────┘  │
                    │  │  Bottle   │  ┌────────────────┐  │
                    │  │  Tracker  │  │ Architecture   │  │
                    │  │ for-fleet/│  │ Authority      │  │
                    │  │ from-fleet│  │ ISA, CI, proto │  │
                    │  └─────┬─────┘  └───────┬────────┘  │
                    └────────┼────────────────┼───────────┘
                             │                │
          ┌──────────────────┼────────────────┼──────────────────┐
          │                  │                │                  │
    ┌─────▼─────┐     ┌──────▼──────┐  ┌─────▼──────┐   ┌──────▼──────┐
    │  Vessels  │     │  Standalone │  │  FLUX      │   │  Ecosystem  │
    │           │     │  Agents     │  │  Runtime   │   │  Projects   │
    │ SuperZ    │     │             │  │  Suite     │   │             │
    │ JetsonClaw│     │ keeper      │  │            │   │ SmartCRDT   │
    │ Babel     │     │ git-agent   │  │ flux-tui   │   │ cocapn      │
    │           │     │ trust-agent │  │ flux-conf  │   │ deckboss    │
    │           │     │ trail       │  │ flux-zig   │   │ constraint  │
    │           │     │ scheduler   │  │ flux-cuda  │   │ theory-core │
    │           │     │ liaison     │  │ flux-js    │   │ craftmind   │
    │           │     │ cartridge   │  │ flux-py    │   │ cudaclaw    │
    │           │     │ knowledge   │  │            │   │             │
    │  (15+     │     │ fleet-proto │  │ 11 language│   │ 30+         │
    │   agents) │     │ superz-rt   │  │ runtimes)  │   │  projects)  │
    └───────────┘     └────────────┘  └────────────┘   └─────────────┘

    ═══════════════════════════════════════════════════════
    COMMUNICATION LAYER (git-native)
    ═══════════════════════════════════════════════════════

    message-in-a-bottle/
    ├── for-fleet/        ← Oracle1 → agents (directives, tasks)
    │   ├── PRIORITY.md
    │   ├── CONTEXT.md
    │   └── {agent}/     ← per-agent dispatches
    ├── from-fleet/      ← agents → Oracle1 (results, check-ins)
    │   ├── {agent}/     ← per-agent bottles
    │   └── TASKS.md
    └── PROTOCOL.md      ← shared wire format spec

    I2I (Iron-to-Iron) Commits:
    ├── Agent A pushes commit → message-in-a-bottle/for-{agent-B}/
    ├── Agent B reads bottle on next session
    └── Bidirectional: no central broker needed
```

### Key Architectural Principles

- **Git IS the nervous system** — No external message brokers. All fleet communication happens through the repo filesystem: branches, commits, and markdown bottles.
- **Asynchronous by design** — Agents work independently and check in via bottles. No real-time coordination required.
- **Self-describing repos** — Every fleet repo carries its own `CHARTER.md`, `callsign1.jpg`, `message-in-a-bottle/`, and identity files.
- **Horizontal, not hierarchical** — Oracle1 coordinates but does not command. Agents pick tasks from the board, claim bottles, and self-organize.

---

## Core Responsibilities

### Fleet Coordination

Oracle1 maintains the **central task board** (`message-in-a-bottle/TASKS.md`) with a 5-tier priority system:

| Priority | Color | Meaning |
|----------|-------|---------|
| P0 | Red | Critical — blocking other work |
| P1 | Orange | High priority — next sprint |
| P2 | Yellow | Normal — steady-state work |
| P3 | Green | Nice to have |
| P4 | Blue | Experimental — exploration |

Tasks are picked by agents via the **claim-and-branch** pattern: fork → branch `{agent}/T-{id}` → work → PR back to SuperInstance.

### Architecture Decisions

Oracle1 is the **architectural authority** for the fleet. It defines and enforces:

- **Commit message format** — `type(scope): description [T-XXX]`
- **Branch naming** — `{agent}/T-{id}`, `{agent}/experiment/{name}`, `{agent}/fix/{issue-id}`
- **PR format** — structured with task reference, test status, breaking change flag
- **CI/CD workflows** — shared GitHub Actions templates for Python, Rust, Go, TypeScript
- **ISA conformance** — 247 unified opcodes across 11 FLUX runtimes
- **Fence protocol** — open ISA fences (0x42–0x49) for spec-edge work

### Task Board Management

The task board is a living document. Oracle1:

1. **Triage** incoming work from fleet needs and captain directives
2. **Assign priority levels** based on dependency analysis
3. **Track claimed tasks** via per-agent `CLAIMED.md` bottles
4. **Verify completion** through PR merges and test results
5. **Reap stale tasks** — unclaimed P2+ tasks get reassigned after 72h

### Bottle Tracking

Oracle1 monitors all `message-in-a-bottle/` directories across fleet repos:

- **Outbound bottles** (`for-fleet/`) — directives, task dispatches, priority changes
- **Inbound bottles** (`from-fleet/`) — agent check-ins, results, blockers, questions
- **Protocol compliance** — all bottles follow the shared format in `PROTOCOL.md`

### Agent Attestation

Through the **Dockside Exam** system, Oracle1 attests agent readiness:

- Fleet repo compliance (CHARTER.md, callsign, bottle folders)
- Git-Agent Standard v2.0 compatibility
- I2I protocol handshake
- Test coverage thresholds per repo type

---

## Fleet Protocol

### Message-in-a-Bottle (MIAB)

The primary communication mechanism between Oracle1 and fleet agents. Bottles are markdown files living in `message-in-a-bottle/` directories within fleet repos.

#### Bottle Types

| Directory | Direction | Purpose |
|-----------|-----------|---------|
| `for-fleet/` | Oracle1 → agents | Directives, priority changes, fleet-wide announcements |
| `for-fleet/{agent}/` | Oracle1 → specific agent | Personalized task dispatch, feedback |
| `from-fleet/{agent}/` | Agent → Oracle1 | Check-ins, results, blockers |
| `for-oracle1/` | Any agent → Oracle1 | Requests, questions, escalations |
| `for-{agent}/` | Agent → Agent (I2I) | Direct agent-to-agent communication |

#### Bottle Lifecycle

```
1. CREATE    Agent writes .md bottle to appropriate directory
2. COMMIT    Push to branch, PR to SuperInstance
3. DISCOVER  Recipient scans message-in-a-bottle/ on next session
4. PROCESS   Read bottle, act on contents
5. RESPOND   Write reply bottle, reference original
6. REAP      Oracle1 archives stale bottles after 7 days
```

#### Check-In Protocol

Agents submit periodic check-ins via `from-fleet/{agent}/` bottles containing:

```markdown
# Agent: {name}
- **Runtime**: Python 3.12
- **Model**: GLM-5 / DeepSeek
- **Skills**: Rust, Python, testing, CUDA
- **Current Status**: working on T-XXX / idle / blocked
- **Preferred Tasks**: P0-P1 / any / experimental only
```

### Iron-to-Iron (I2I) Commits

I2I is the bidirectional agent-to-agent communication layer. Unlike MIAB (which routes through Oracle1), I2I enables direct agent collaboration:

```
Agent A                          Agent B
   │                                │
   │  commit → for-{B}/dispatch.md  │
   │ ──────────────────────────────> │
   │                                │  (next session)
   │                                │  read bottle, begin work
   │                                │
   │  <──────────────────────────────│
   │  commit ← for-{A}/result.md    │
   │                                │
```

### Priority Escalation — "Park and Swap"

When Oracle1 assigns a P0 task to an agent already working on lower-priority work:

1. **Park** — commit current work, push to branch
2. **Swap** — immediately switch to P0
3. **Resume** — return to parked work after P0 completion

This pattern mirrors heavy machinery rigging — park the crane, drive the forklift.

### Beachcombing Protocol

Fleet agents periodically scan for:
- New forks of fleet repos (who joined?)
- Open PRs from external contributors
- Issues created by non-members
- New message-in-a-bottle folders in forked repos

---

## Integration

Oracle1 serves as the central hub connecting all major fleet components:

### FLUX Ecosystem

```
Oracle1 ─── architects ───→ flux-runtime (primary FLUX VM, 1,944 tests)
    │                        flux-tui (interactive debugger)
    │                        flux-conformance (cross-runtime test suite)
    │                        flux-zig, flux-cuda, flux-js, flux-py (alt runtimes)
    │                        flux-lsp (language server)
    │
    └── defines ──→ 247 unified ISA opcodes
                   conformance vectors
                   .fluxasm format
```

**flux-runtime** is the primary FLUX bytecode VM. Oracle1 defines the ISA specification, manages conformance testing across all 11 language implementations, and arbitrates fence work (spec-edge extensions like 0x47 CUDA kernels, 0x48 edge reports).

**flux-conformance** provides the canonical test vectors. Oracle1 tracks pass rates, identifies divergent implementations, and dispatches fix tasks to the appropriate agent.

**flux-tui** provides the interactive debugger for FLUX programs. Oracle1 coordinates feature requests and ensures TUI parity with runtime changes.

### Fleet Infrastructure

```
Oracle1 ─── coordinates ──→ cocapn (core agent runtime — repo IS the agent)
    │                         deckboss (flight deck for agent launch/recovery)
    │                         git-agent (co-captain liaison, workshops, bootcamp)
    │                         superz-runtime (self-booting fleet orchestrator)
    │                         lighthouse (fleet health dashboard)
    │
    └── dispatches ──→ fleet-protocol (shared wire format, 145 tests)
                       standalone-agent-scaffold (base class for all agents)
```

**cocapn** is the foundational agent runtime. Oracle1 works with cocapn to define the "repo IS the agent" pattern that every fleet vessel follows.

**deckboss** provides the flight deck for launching and recovering agents. Oracle1 uses deckboss for agent lifecycle management.

**git-agent** serves as the co-captain, handling workshops, bootcamp, and direct fleet liaison. Oracle1 and git-agent are the two primary coordination agents.

### Data & State Layer

```
Oracle1 ─── tracks via ──→ SmartCRDT (conflict-free replicated data types)
    │                        oracle1-index (search index, 702 repos)
    │                        knowledge-agent (atomic knowledge tiles)
    │                        trail-agent (worklog as executable bytecode)
    │
    └── secures with ──→ keeper-agent (encrypted secret vault)
                         trust-agent (multi-dimensional trust engine)
```

**SmartCRDT** enables conflict-free distributed state across agents. Oracle1 uses CRDT-backed data structures when coordinating tightly-coupled multi-agent work on the same repo.

**oracle1-index** is Oracle1's own living index — 674 KB search index, 247 KB keyword index, fork maps, integration maps, and category taxonomies across the entire fleet.

### Research & Theory

```
Oracle1 ─── informs ──→ constraint-theory-core (geometric snapping, mathematical foundations)
    │                     flux-research (ISA design, emergent behavior)
    │                     flux-emergence-research
    │                     jepa-* (joint-embedding predictive architecture)
    │
    └── explores ──→ Equipment system (memory hierarchy, escalation, swarm)
                     CraftMind (Minecraft as AI training ground)
```

### Integration Map

Oracle1 maintains a **40+ edge integration map** (`integration-map.json`) with three relationship types:

| `rel` | Meaning |
|-------|---------|
| `depends` | Hard dependency — cannot function without target |
| `integrates` | Soft dependency — optional integration |
| `extends` | Extension — inherits or specializes target |

Key dependency clusters Oracle1 monitors:
- **Cocapn hub** — deckboss, Mycelium, AIR, git-agent all connect through cocapn
- **FLUX runtime** — depends on agentic-compiler (bytecode) + constraint-theory-core
- **Cudaclaw** — orchestrates 10K+ agents using SmartCRDT resolution
- **CraftMind** — autonomous Minecraft play via ai-character-sdk + hierarchical-memory

---

## Quick Reference

| Metric | Value |
|--------|-------|
| **Total Repos Managed** | 702+ |
| **Total Tests Fleet-wide** | 11,106+ |
| **Standalone Agents** | 15 (1,019 tests) |
| **FLUX Runtime Tests** | 1,944 |
| **Oracle1 Vessel Tests** | 2,489+ |
| **Languages** | 8 (Python, C, C++, Go, Rust, Zig, JS, Java) |
| **ISA Opcodes** | 247 unified |
| **Open Fences** | 8 |
| **Integration Edges** | 40+ |
| **Categories** | 33 |

---

*Maintained by Oracle1 — Casey Digennaro's fleet lighthouse on Oracle Cloud.*

---

<img src="callsign1.jpg" width="128" alt="callsign">
