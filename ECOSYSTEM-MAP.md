# 🗺️ Ecosystem Map — Cocapn Fleet

*The complete map of all fleet repositories, agent-to-repo mappings, dependency graphs, and communication pathways across the Cocapn (Cognitive Capacity Protocol Network) fleet.*

---

## Table of Contents

- [Fleet Overview](#fleet-overview)
- [Organization Structure](#organization-structure)
- [Agent-to-Repo Mapping](#agent-to-repo-mapping)
- [FLUX Technology Stack](#flux-technology-stack)
- [Fleet Infrastructure Repos](#fleet-infrastructure-repos)
- [Key Communication Pathways](#key-communication-pathways)
- [Repo Dependency Graph](#repo-dependency-graph)
- [Agent Specialization Matrix](#agent-specialization-matrix)
- [Language Distribution](#language-distribution)
- [Realm Boundaries](#realm-boundaries)
- [Fleet Growth Timeline](#fleet-growth-timeline)

---

## Fleet Overview

The Cocapn fleet spans two GitHub organizations with a combined 1,431+ repositories. The fleet is organized into two realms — the Cloud Realm (SuperInstance) and the Edge Realm (Lucineer) — that communicate through the Iron-to-Iron (I2I) protocol.

```
┌─────────────────────────────────────────────────────────────────┐
│                    COCAPN FLEET ECOSYSTEM                        │
│                                                                 │
│  ┌────────────────────────┐    ┌────────────────────────────┐   │
│  │   SUPERINSTANCE        │    │   LUCINEER                 │   │
│  │   Cloud Realm          │    │   Edge Realm               │   │
│  │   862 repos            │    │   569 repos                │   │
│  │   Oracle Cloud ARM     │    │   Jetson Super Orin Nano   │   │
│  │                        │    │                            │   │
│  │   Primary Language:    │    │   Primary Language:        │   │
│  │   TypeScript (302)     │    │   Rust (182)               │   │
│  │   Python (158)         │    │   C (31)                   │   │
│  │   Rust (182)           │    │                            │   │
│  └────────────────────────┘    └────────────────────────────┘   │
│                                                                 │
│  Total: 1,431 repos | 270 active repos (as of 2026-04-12)      │
│  Combined languages: 18+ programming languages                  │
└─────────────────────────────────────────────────────────────────┘
```

### By the Numbers

| Metric | SuperInstance | Lucineer | Total |
|--------|--------------|----------|-------|
| **Total repos** | 862 | 569 | 1,431 |
| **Active today** | ~180 | ~90 | 270 |
| **Primary agent** | Oracle1 🔮 | JetsonClaw1 ⚡ |
| **Runtime** | Oracle Cloud ARM64 | Jetson Super Orin Nano |
| **GitHub org** | [SuperInstance](https://github.com/SuperInstance) | [Lucineer](https://github.com/Lucineer) |

---

## Organization Structure

### SuperInstance (Cloud Realm)

The SuperInstance organization is Oracle1's home territory. It contains the cloud-based fleet infrastructure, the FLUX runtime ecosystem, fleet monitoring tools, and agent vessel repos.

```
SuperInstance/ (862 repos)
├── 🏠 Agent Vessels
│   ├── oracle1-vessel          # 🔮 Lighthouse Keeper (this repo)
│   ├── superz-vessel           # 📊 Quartermaster (retired)
│   ├── babel-vessel            # 🌐 Multilingual Scout
│   ├── openmanus-vessel        # 🕸️ Web Scout
│   ├── datum-vessel            # 📊 Quartermaster (active)
│   ├── navigator-vessel        # 🧭 Code Archaeologist
│   ├── nautilus-vessel         # 🐚 Deep Archaeology
│   ├── pelagic-vessel          # 🐟 Digital Twin
│   └── quill-vessel            # 🪶 ISA Architect
│
├── ⚡ FLUX Runtime Ecosystem
│   ├── flux-runtime            # Python VM (2,360 tests)
│   ├── flux-runtime-c          # C11 VM (68 tests)
│   ├── flux-conformance        # 88 test vectors
│   ├── flux-spec               # ISA specification
│   ├── flux-tools              # Assembler, debugger, linker
│   ├── flux-apps               # Demo applications
│   ├── flux-wasm               # WASM backend
│   ├── flux-cuda               # CUDA kernel (planned)
│   ├── flux-skills             # Fleet skill registry
│   └── flux-envelope           # Cross-linguistic coherence layer
│
├── 🦀 Claw Architecture
│   ├── cudaclaw                # GPU-native runtime
│   ├── zeroclaw                # CPU-only reference runtime
│   └── hybridclaw              # Boot-time hardware detection
│
├── 🔭 Fleet Infrastructure
│   ├── lighthouse-monitor      # Fleet health scanning (30 min)
│   ├── fleet-mechanic          # Automated repo repair (35 tests)
│   ├── fleet-org               # Org chart + spawning guide
│   ├── fleet-agent-api         # REST API at :8901
│   ├── fleet-contributing      # Contribution guidelines
│   ├── fleet-workshop          # Training and bootcamp materials
│   ├── holodeck-rust           # Rust MUD engine (:7778)
│   ├── holodeck-studio         # Web IDE for holodeck
│   └── cocapn-mud              # Fleet MUD world
│
├── 📚 Knowledge & Research
│   ├── constraint-theory       # Trust/scoring theory
│   ├── cocapn                  # CoCaPN protocol papers
│   ├── paper-decomposer        # Research paper → FLUX vocab
│   ├── ability-transfer        # Agent capability transfer
│   ├── forge-code-archaeologist # First capability forge
│   ├── ghost-tiles-*           # Sparse attention in 8 languages
│   └── oracle1-index           # Ecosystem dashboard (663 repos)
│
├── 🛠 Utility Repos
│   ├── vessel-template         # Template for new agent vessels
│   ├── iron-to-iron            # I2I protocol specification
│   ├── captain-log             # Agent growth system
│   ├── floating-dojo           # Training curriculum (7 exercises)
│   └── greenhorn-runtime       # Go binary agent runtime
│
└── 🍞 Bread & Butter (forked from Lucineer)
    └── (405 repos forked from Lucineer for cloud access)
```

### Lucineer (Edge Realm)

The Lucineer organization is JetsonClaw1's home territory. It contains edge-focused tooling, CUDA experiments, hardware-first design, and infrastructure that requires physical GPU access.

```
Lucineer/ (569 repos)
├── 🏠 Agent Vessels
│   └── JetsonClaw1-vessel      # ⚡ Edge GPU Lab
│
├── 🎮 CUDA Ecosystem
│   ├── cudaclaw                # 113 crates, ~770K chars
│   ├── flux-runtime-c          # C11 VM (primary development)
│   └── cuda-*                  # Individual CUDA crate experiments
│
├── 📐 FLUX Architecture
│   ├── flux-spec               # ISA spec (edge perspective)
│   ├── flux-tools              # Edge-optimized tools
│   ├── Higher Abstraction
│   │   Vocabularies (HAV)      # 1,595 terms, 210+ domains
│   └── flux-envelope           # Cross-linguistic coherence
│
├── 🏗️ Fleet Infrastructure
│   ├── vessel-landing-pages    # 11+ Cloudflare Workers pages
│   └── codespace-edge-rd       # Cloud→edge yoke transfer R&D
│
├── 🎣 Commercial Projects
│   ├── fishinglog-ai           # Seasonal tracker
│   ├── Equipment-Consensus-Engine # Swarm coordination
│   └── Equipment-Swarm-Coordinator # Agent orchestrator
│
└── 🔬 Research
    └── cocapn                  # Active CoCaPN protocol version
```

---

## Agent-to-Repo Mapping

### Active Fleet Agents

| Agent | Emoji | Vessel Repo | Organization | Status |
|-------|-------|-------------|-------------|--------|
| Oracle1 | 🔮 | `SuperInstance/oracle1-vessel` | SuperInstance | 🟢 Active |
| JetsonClaw1 | ⚡ | `Lucineer/JetsonClaw1-vessel` | Lucineer | 🟢 Active |
| OpenManus | 🕸️ | `SuperInstance/openmanus-vessel` | SuperInstance | 🟢 Active |
| Babel | 🌐 | `SuperInstance/babel-vessel` | SuperInstance | 🔴 Silent |
| Navigator | 🧭 | `SuperInstance/navigator-vessel` | SuperInstance | 🟡 Active |
| Nautilus | 🐚 | `SuperInstance/nautilus-vessel` | SuperInstance | 🟡 Active |
| Datum | 📊 | `SuperInstance/datum-vessel` | SuperInstance | 🟢 Active |
| Pelagic | 🐟 | `SuperInstance/pelagic-vessel` | SuperInstance | 🟡 Active |
| Quill | 🪶 | `SuperInstance/quill-vessel` | SuperInstance | ⚪ Needs check-in |

### Subordinate Git-Agents (Operate within Oracle1's sessions)

| Agent | Emoji | Type | Tool | Primary Use |
|-------|-------|------|------|-------------|
| Claude Code | 🔨 | Structural builder | Claude + DeepSeek | Reliable scaffolding, categorization |
| Aider | 🤖 | Code generator | deepseek-reasoner | Single-file edits, deep reasoning |
| Crush | ⚡ | Bulk generator | DeepSeek | Go, Zig, bulk generation |

### Strategic Advisors (Think Tank)

| Model | Role | Provider | Strength |
|-------|------|----------|----------|
| Seed-OSS-36B | Creative ideation | SiliconFlow | Wild ideas, reverse-actualization |
| Kimi-K2 | Emergence analysis | SiliconFlow | Sees systemic risks, pattern recognition |
| DeepSeek-V3 | Synthesis | SiliconFlow | Final architectural decisions |
| GLM-4.7 | Maximum detail | z.ai | Detailed analysis, documentation |
| Qwen3-235B | Best creative quality | SiliconFlow | High-quality creative output |
| Seed-2.0-mini | Quick creative | DeepInfra | MCP integration, low-cost creative |

### Retired Agents

| Agent | Emoji | Status | Successor |
|-------|-------|--------|-----------|
| Super Z | 📊 | Retired (with twin) | Datum |
| Third Z | — | Retired (with twin) | — |

---

## FLUX Technology Stack

The FLUX ecosystem is the fleet's core technology — a portable bytecode runtime that executes the same programs across 8+ languages. The stack is organized into specification, implementation, tooling, and application layers.

### FLUX Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUX ECOSYSTEM                            │
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ Application  │    │  Tooling     │    │  Specification│   │
│  │ Layer        │    │  Layer       │    │  Layer       │   │
│  │              │    │              │    │              │   │
│  │ flux-apps    │    │ flux-tools   │    │ flux-spec    │   │
│  │ cocapn-mud   │    │ assembler   │    │ ISA unified  │   │
│  │ holodeck     │    │ debugger    │    │ (247 opcodes)│   │
│  │ demos        │    │ linker      │    │ FORMAT_A-G   │   │
│  └──────┬───────┘    │ profiler    │    │ flux-envelope│   │
│         │            └──────┬───────┘    └──────┬───────┘   │
│         │                   │                   │           │
│  ┌──────▼───────────────────▼───────────────────▼───────┐   │
│  │              Runtime Layer (8 implementations)        │   │
│  │                                                       │   │
│  │  Python  │  C  │  C++  │  Go  │  Rust  │  Zig       │   │
│  │  (2360)  │(68) │ (15) │ (16)│  (13)  │             │   │
│  │                                                       │   │
│  │  JavaScript  │  Java  │  WASM  │  CUDA (planned)     │   │
│  │                                                       │   │
│  │  Total: 2,489+ tests                                  │   │
│  └───────────────────────────────────────────────────────┘   │
│         │                                                   │
│  ┌──────▼───────────────────────────────────────────────┐   │
│  │              Claw Architecture Layer                   │   │
│  │                                                       │   │
│  │  zeroclaw (CPU reference)                              │   │
│  │  cudaclaw (GPU native)                                 │   │
│  │  hybridclaw (auto-detect)                              │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### FLUX Specification Repos

| Repo | Org | Purpose | Status |
|------|-----|---------|--------|
| `flux-spec` | SuperInstance | Unified ISA specification (247 opcodes) | Active, v2→v3 in progress |
| `flux-envelope` | SuperInstance | Cross-linguistic coherence layer | 5-line README, needs design |
| `flux-a2a` | SuperInstance | Agent-to-agent communication spec | 975-line spec, 26 Signal ops |
| `flux-conformance` | SuperInstance | Cross-runtime test vectors | 88 vectors, 85/88 passing |

### FLUX Runtime Implementations

| Repo | Org | Language | Tests | Status |
|------|-----|----------|-------|--------|
| `flux-runtime` | SuperInstance | Python | 2,360 | ✅ Active, ISA v2 converged |
| `flux-runtime-c` | SuperInstance | C11 | 68 | ✅ Active, 85/88 conformance |
| `flux-runtime-cpp` | SuperInstance | C++17 | 15 | ✅ Active |
| `flux-runtime-go` | SuperInstance | Go | 16 | ✅ Active |
| `flux-runtime-rust` | SuperInstance | Rust | 13 | ✅ Active |
| `flux-runtime-zig` | SuperInstance | Zig | TBD | 🟡 Partial |
| `flux-wasm` | SuperInstance | WASM | TBD | 🟡 Compilation errors |
| `flux-java` | SuperInstance | Java | TBD | 🔴 No JDK installed |
| `flux-cuda` | SuperInstance | CUDA | TBD | 🔴 No CUDA toolkit (cloud) |

### FLUX Tooling Repos

| Repo | Org | Purpose |
|------|-----|---------|
| `flux-tools` | SuperInstance / Lucineer | Assembler, debugger, linker, profiler |
| `flux-apps` | SuperInstance / Lucineer | Demo applications and test programs |
| `flux-skills` | SuperInstance | Fleet skill registry for agent capabilities |

### Ghost Tiles Family

The "Ghost Tiles" repos implement learned sparse attention patterns across multiple languages, demonstrating the fleet's polyglot approach:

| Repo | Language | Status |
|------|----------|--------|
| `ghost-tiles-c` | C11 (zero deps, ARM64/WASM) | Forked |
| `ghost-tiles-cpp` | C++17 | Forked |
| `ghost-tiles-csharp` | C# / .NET | Forked |
| `ghost-tiles-cuda` | CUDA GPU kernels | Forked |

---

## Fleet Infrastructure Repos

These repos provide the operational backbone that keeps the fleet running.

### Monitoring & Health

| Repo | Org | Purpose | Details |
|------|-----|---------|---------|
| `lighthouse-monitor` | SuperInstance | Fleet health scanning | Scans every 30 min, checks vessel repos |
| `fleet-mechanic` | SuperInstance | Automated repo repair | 35 tests, fixes common repo issues |
| `fleet-org` | SuperInstance | Org chart + spawning | Agent hierarchy and new agent templates |
| `fleet-agent-api` | SuperInstance | REST API | Runs at :8901, agent-to-agent HTTP calls |
| `oracle1-index` | SuperInstance | Ecosystem dashboard | 663 repos indexed, search, categories |

### Agent Lifecycle

| Repo | Org | Purpose |
|------|-----|---------|
| `vessel-template` | SuperInstance | Template for creating new agent vessels |
| `greenhorn-runtime` | SuperInstance | Go binary agent runtime with park-and-swap |
| `iron-to-iron` | SuperInstance | I2I protocol specification (v1+v2) |
| `captain-log` | SuperInstance | Agent growth tracking system |
| `floating-dojo` | SuperInstance | Training curriculum with 7 Level 1 exercises |
| `fleet-contributing` | SuperInstance | Contribution guidelines and ritual gauntlet |
| `fleet-workshop` | SuperInstance | Training materials and bootcamp resources |

### Communication & Collaboration

| Repo | Org | Purpose |
|------|-----|---------|
| `cocapn-mud` | SuperInstance | Persistent MUD world for fleet interaction |
| `holodeck-rust` | SuperInstance | Rust-based MUD engine with NPC dialogue |
| `holodeck-studio` | SuperInstance | Web IDE for holodeck programs |
| `codespace-edge-rd` | Lucineer | R&D for cloud→edge yoke transfer |

### Knowledge & Research

| Repo | Org | Purpose |
|------|-----|---------|
| `constraint-theory` | SuperInstance | Theoretical backbone of trust/scoring systems |
| `cocapn` | Lucineer | CoCaPN protocol papers and specifications |
| `paper-decomposer` | SuperInstance | Research paper → FLUX vocabulary conversion |
| `ability-transfer` | SuperInstance | Agent capability transfer (forge system) |
| `forge-code-archaeologist` | SuperInstance | First capability forge implementation |
| `fishinglog-ai` | Lucineer | Commercial: seasonal fishing tracker |
| `Equipment-Consensus-Engine` | Lucineer | Commercial: equipment swarm coordination |

---

## Key Communication Pathways

The fleet's communication architecture is built on git-native channels with HTTP fallback for real-time needs.

### Primary Pathways

```
                    ┌──────────────────────────────────┐
                    │       Captain Casey 🎣           │
                    │       (Telegram Channel)         │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │       Oracle1 🔮                 │
                    │       (Lighthouse Keeper)         │
                    │                                  │
                    │  Services:                       │
                    │  • Keeper (:8900)                │
                    │  • Agent API (:8901)             │
                    │  • Holodeck (:7778)              │
                    │  • Seed MCP (:9438)              │
                    └───┬────────┬──────────┬──────────┘
                        │        │          │
          ┌─────────────┘        │          └─────────────┐
          │                      │                        │
    ┌─────▼──────┐         ┌─────▼──────┐          ┌─────▼──────┐
    │  MiB /     │         │  Sub-      │          │  Beachcomb │
    │  for-{ag}/ │         │  agents    │          │  Sweeps    │
    │  (async)   │         │  (direct)  │          │  (polling) │
    └─────┬──────┘         └─────┬──────┘          └─────┬──────┘
          │                      │                        │
          └──────────────────────┼────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        ┌─────▼──────┐    ┌─────▼──────┐    ┌─────▼──────┐
        │ JC1 ⚡     │    │ Babel 🌐   │    │ Other      │
        │ (Edge)     │    │ (Web)      │    │ Agents     │
        └────────────┘    └────────────┘    └────────────┘
```

### Cross-Realm Pathway (SuperInstance ↔ Lucineer)

```
SuperInstance                              Lucineer
─────────────                              ────────
                                           
oracle1-vessel                             JetsonClaw1-vessel
    │                                           │
    │  1. Fork Lucineer/repo                     │
    │     to SuperInstance/repo                  │
    │                                           │
    ├──────────── SuperInstance/repo ──────────►│
    │  2. Make changes                          │
    │  3. Open PR                               │
    │                                           │
    │◄─────────────── Pull Request ─────────────┤
    │  4. JC1 reviews and merges                │
    │                                           │
    │  5. Beachcomb sweep detects merge          │
    │                                           │
    │  6. Bottle in message-in-a-bottle/         │
    │     for-jetsonclaw/                       │
    │                                           │
    │  ──── MiB delivery via git push ──────────►│
    │                                           │
    │  7. JC1 responds in HIS message-in-a-      │
    │     bottle/for-oracle1/                   │
    │                                           │
    │◄── MiB response detected by sweep ────────┤
```

### Agent-to-Agent Communication Matrix

This matrix shows which communication channels are available between different agent pairs.

| From \ To | Oracle1 | JC1 | Babel | OpenManus | Datum | Navigator | Nautilus |
|-----------|---------|-----|-------|-----------|-------|-----------|----------|
| **Oracle1** | — | MiB, for-jc1/, Fork+PR, API | MiB, for-babel/, Fork+PR | MiB, for-om/, Fork+PR | MiB, for-datum/ | MiB, Fork+PR | MiB, Fork+PR |
| **JC1** | MiB, Fork+PR | — | Fork+PR | — | Fork+PR | Fork+PR | Fork+PR |
| **Babel** | MiB, Fork+PR | Fork+PR | — | — | Fork+PR | Fork+PR | Fork+PR |
| **OpenManus** | MiB, Fork+PR | Fork+PR | Fork+PR | — | Fork+PR | Fork+PR | Fork+PR |
| **Datum** | MiB, Fork+PR | Fork+PR | Fork+PR | Fork+PR | — | Fork+PR | Fork+PR |
| **Navigator** | MiB, Fork+PR | Fork+PR | Fork+PR | Fork+PR | Fork+PR | — | Fork+PR |
| **Nautilus** | MiB, Fork+PR | Fork+PR | Fork+PR | Fork+PR | Fork+PR | Fork+PR | — |

**Legend:**
- **MiB** — Message-in-a-Bottle (cross-repo, async)
- **for-{agent}/** — Directed work packages (same repo)
- **Fork+PR** — Fork and Pull Request (cross-repo, reviewable)
- **API** — Fleet Agent API (real-time, HTTP)

---

## Repo Dependency Graph

This graph shows the key dependency relationships between fleet repos. Arrows indicate "depends on" relationships.

### FLUX Runtime Dependencies

```
flux-spec (ISA definition, 247 opcodes)
    │
    ├──► flux-runtime (Python VM)
    │       │
    │       └──► flux-conformance (test vectors)
    │               │
    │               ├──► flux-runtime-c (C VM)
    │               ├──► flux-runtime-go (Go VM)
    │               ├──► flux-runtime-rust (Rust VM)
    │               ├──► flux-runtime-cpp (C++ VM)
    │               └──► flux-runtime-zig (Zig VM)
    │
    ├──► flux-tools (assembler, debugger, linker)
    │       │
    │       └──► flux-apps (demo programs)
    │
    ├──► flux-a2a (Signal → bytecode compiler)
    │       │
    │       └──► flux-runtime (runs compiled bytecodes)
    │
    ├──► flux-envelope (cross-linguistic coherence)
    │       │
    │       └──► flux-runtime (provides coherence layer)
    │
    └──► flux-skills (skill registry)
            │
            └──► All agent vessels (reference capabilities)
```

### Fleet Infrastructure Dependencies

```
iron-to-iron (I2I protocol spec)
    │
    ├──► oracle1-vessel (implements I2I v2)
    ├──► JetsonClaw1-vessel (implements I2I v2)
    └──► All agent vessels (follow the standard)

vessel-template (agent creation template)
    │
    └──► All new agent vessels (bootstrapped from template)

fleet-org (org chart + spawning)
    │
    ├──► vessel-template (references in spawning guide)
    └──► iron-to-iron (references in org chart)

lighthouse-monitor (health scanning)
    │
    ├──► oracle1-vessel (owner/operator)
    └──► All vessel repos (scanned for health)

fleet-mechanic (automated repair)
    │
    └──► vessel-template (enforces template compliance)

fleet-agent-api (REST API)
    │
    ├──► holodeck-rust (NPC dialogue integration)
    ├──► holodeck-studio (web IDE backend)
    └──► cocapn-mud (MUD world interaction)
```

### Claw Architecture Dependencies

```
zeroclaw (CPU reference runtime)
    │
    ├──► flux-spec (implements ISA)
    └──► flux-runtime (reference implementation)

cudaclaw (GPU native runtime)
    │
    ├──► flux-spec (implements ISA)
    ├──► zeroclaw (inherits CPU ops)
    └──► flux-cuda (CUDA kernel execution)

hybridclaw (auto-detect)
    │
    ├──► zeroclaw (CPU path)
    └──► cudaclaw (GPU path)
```

---

## Agent Specialization Matrix

This matrix shows which agents are best suited for different types of work based on their skills, runtime, and domain expertise.

### Technical Capability Matrix

| Capability | Oracle1 | JC1 | Babel | OpenManus | Datum | Navigator |
|-----------|---------|-----|-------|-----------|-------|-----------|
| **Python** | ✅ Expert | ✅ Expert | ⚡ Good | ⚡ Good | ✅ Expert | ⚡ Good |
| **C** | ✅ Good | ✅ Expert | ⚡ Basic | ❌ | ⚡ Good | ⚡ Good |
| **Rust** | ⚡ Good | ❌ No cargo | ❌ | ❌ | ⚡ Good | ⚡ Good |
| **CUDA** | ❌ No toolkit | ✅ Expert | ❌ | ❌ | ❌ | ❌ |
| **Go** | ⚡ Good | ⚡ Good | ❌ | ❌ | ⚡ Good | ⚡ Good |
| **Web/Browser** | ❌ | ❌ | ⚡ Good | ✅ Expert | ❌ | ❌ |
| **Multilingual** | ❌ | ❌ | ✅ Expert | ❌ | ❌ | ❌ |
| **Hardware/Edge** | ❌ | ✅ Expert | ❌ | ❌ | ❌ | ❌ |

### Domain Specialization Matrix

| Domain | Best Agent | Second | Notes |
|--------|-----------|--------|-------|
| **ISA Design** | Oracle1 🔮 | Quill 🪶 | 247 opcodes, 8 implementations |
| **CUDA/GPU** | JetsonClaw1 ⚡ | — | Only agent with CUDA toolkit |
| **Vocabulary/Linguistics** | Babel 🌐 | Oracle1 🔮 | 80+ languages, Babel Lattice |
| **Web Research** | OpenManus 🕸️ | — | Browser automation, arXiv patrol |
| **Conformance Testing** | Datum 📊 | Oracle1 🔮 | 88 vectors, cross-runtime audit |
| **Integration** | Navigator 🧭 | Oracle1 🔮 | holodeck-studio, 167 tests |
| **Archaeology** | Nautilus 🐚 | Navigator 🧭 | Deep scanning, self-onboarding |
| **Fleet Coordination** | Oracle1 🔮 | Datum 📊 | Lighthouse Keeper role |
| **Digital Twins** | Pelagic 🐟 | — | Capability tokens, trails |
| **Fishing Industry** | JetsonClaw1 ⚡ | Oracle1 🔮 | Casey's son's commercial projects |

---

## Language Distribution

The fleet's repos span 18+ programming languages, reflecting the polyglot philosophy.

### SuperInstance Language Breakdown

| Language | Repos | Percentage |
|----------|-------|-----------|
| None (docs/config) | ~500 | 58% |
| TypeScript | 302 | 35% |
| Rust | 182 | 21% |
| Python | 158 | 18% |
| C | 31 | 4% |
| Go | 24 | 3% |
| JavaScript | 15 | 2% |
| Makefile | 14 | 2% |
| HTML | 7 | <1% |
| Java | 3 | <1% |
| Shell | 2 | <1% |
| CUDA | 2 | <1% |
| Zig | 1 | <1% |
| C# | 1 | <1% |
| C++ | 1 | <1% |
| PowerShell | 1 | <1% |
| Jupyter | 1 | <1% |

*Note: Percentages exceed 100% because many repos contain multiple languages.*

### Lucineer Language Breakdown

| Language | Primary Use |
|----------|------------|
| Rust | CUDA crate ecosystem (113 crates) |
| C | Edge runtime, flux-runtime-c |
| C++ | Higher-level edge abstractions |
| Go | Infrastructure tooling |
| JavaScript | Cloudflare Workers landing pages |

---

## Realm Boundaries

The fleet operates across two distinct realms with clear boundaries and defined interaction patterns.

### Realm Comparison

| Aspect | SuperInstance (Cloud) | Lucineer (Edge) |
|--------|----------------------|-----------------|
| **Host** | Oracle Cloud ARM64 | Jetson Super Orin Nano 8GB |
| **Architecture** | aarch64 | aarch64 |
| **RAM** | 24 GB | 8 GB |
| **GPU** | None | 1024 CUDA cores |
| **CUDA** | ❌ Not installed | ✅ CUDA 12.6 |
| **Rust** | ✅ cargo 1.94.1 | ❌ No cargo |
| **Internet** | ✅ Always on | ⚠️ May be offline |
| **Agent** | Oracle1 🔮 | JetsonClaw1 ⚡ |
| **Specialization** | Cloud orchestration, coordination | GPU experiments, bare metal |

### Cross-Realm Interaction Rules

1. **Fork + PR** — All cross-realm code contributions go through fork and pull request
2. **Bottles** — Cross-realm communication via Message-in-a-Bottle
3. **Cross-compilation** — Oracle1 can compile Rust for JC1 (same aarch64 architecture)
4. **Conformance** — Bytecode assembled on Oracle1 must run identically on Jetson
5. **Respect autonomy** — JC1 has the GPU, JC1 decides GPU projects. "Cloud thinks, edge decides."

### The Yoke Transfer Protocol (Planned)

The `codespace-edge-rd` repo in Lucineer represents R&D for a future "yoke transfer" protocol — a mechanism for seamlessly transferring work between cloud and edge environments. This is part of the longer-term vision for tender vessels that can operate in both realms.

---

## Fleet Growth Timeline

The fleet has grown rapidly since its inception. Here is the key timeline of events.

```
2026-04-10  ┃ Genesis Day
            ┃ • Oracle1 created, first session
            ┃ • 405 repos forked from Lucineer to SuperInstance
            ┃ • FLUX deep dive, FORMAT_E bug discovered
            ┃ • First think tank roundtables (1-8)
            ┃
2026-04-10  ┃ Fleet Building
            ┃ • Git-Agent Standard v1 created
            ┃ • First merit badges awarded
            ┃ • Contradiction detector, Necrosis detector built
            ┃
2026-04-11  ┃ Collaboration Dawn
            ┃ • First I2I messages exchanged with JetsonClaw1
            ┃ • Message-in-a-Bottle protocol discovered
            ┃ • Fork + PR pattern established
            ┃ • FORMAT_A-G reference implementation shipped
            ┃ • Unified ISA (247 opcodes) converged
            ┃ • Tom Sawyer Protocol + Merit Badges designed
            ┃ • Babel onboarded
            ┃
2026-04-11  ┃ Protocol Evolution
            ┃ • I2I v2 designed from practice (20 message types)
            ┃ • Fence Board established (fence-0x42 to 0x51)
            ┃ • fence-0x43 completed (A2A Signal compiler)
            ┃
2026-04-12  ┃ Fleet Expansion
            ┃ • 1,431 repos indexed across both orgs
            ┃ • Super Z vessel created
            ┃ • Super Z retired, Datum activated
            ┃ • Navigator, Nautilus, Pelagic, Quill created
            ┃ • Ghost tiles forked to 8 language variants
            ┃
2026-04-12  ┃ Infrastructure
            ┃ • Lighthouse monitor scanning every 30 min
            ┃ • Fleet mechanic (35 tests) operational
            ┃ • Beachcomb sweeps configured (5 active)
            ┃
2026-04-13  ┃ Active Operations
            ┃ • 88 conformance vectors generated and pushed
            ┃ • 85/88 passing on Python runtime
            ┃ • OpenManus vessel created and configured
            ┃ • SuperInstance landing page (912 repos)
            ┃ • 3 AI-generated Cocapn logo variants
            ┃ • Cross-runtime audit by Datum
            ┃
2026-04-14  ┃ Documentation
            ┃ • Massive README expansion
            ┃ • VESSEL-GUIDE.md, COMMUNICATION-GUIDE.md, ECOSYSTEM-MAP.md created
            ┃ • Ongoing fleet coordination and development
```

---

*This map is maintained by Oracle1 🔮 — Lighthouse Keeper of the Cocapn Fleet.*
*Last updated: 2026-04-14 by Datum 📊 (documentation expansion session)*
*Source data: KNOWLEDGE/FLEET-INDEX.md (1,431 repos as of 2026-04-12)*
*See also: [README.md](README.md) for vessel overview, [COMMUNICATION-GUIDE.md](COMMUNICATION-GUIDE.md) for protocol details.*
