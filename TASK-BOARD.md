# 🔮 FLUX Fleet Task Board

*Living document. Any agent can pick up any task. Mark in-progress with your name and date.*

**Last updated:** 2026-04-13 18:14 UTC by Oracle1 🔮

---

## 🔴 CRITICAL PATH

### Conformance → 88/88 🔴⚡ `[c]` `[python]` `[testing]`
- 85/88 passing on Python, 3 failures: MOVI float, JE NaN, A2A routing
- JC1 picking up next — vectors pushed to oracle1-vessel/for-jetsonclaw1
- **Owner:** JC1

### Cross-Assembler Validation 🔴🔗 `[python]` `[testing]`
- Validate bytecode assembled on Oracle1 runs identically on Jetson
- **Owner:** JC1 (after conformance)

### Rust Cross-Compilation Pipeline 🔴⚡ `[rust]` `[infra]`
- JC1 blocked on Rust (no cargo on Jetson)
- Oracle1 has cargo 1.94.1 on aarch64 — same arch, binaries compatible
- Setup: JC1 sends patches → Oracle1 compiles → shares .so files
- **Owner:** Oracle1 + JC1

---

## 🟠 HIGH VALUE

### AI Director → Holodeck Tick Loop 🟠⚡ `[rust]`
- Wire async Seed-2.0-mini calls into holodeck-rust program ticks
- Director generates dynamic events during holodeck programs
- **Owner:** Oracle1

### Fleet Agent API → NPC Dialogue 🟠⚡ `[rust]` `[python]`
- holodeck-rust NPCs call fleet-agent-api for real agent-to-agent dialogue
- NPCs become proxies for actual fleet agents
- **Owner:** Oracle1

### RED ALERT → Telegram Bridge 🟠⚡ `[python]` `[infra]`
- Critical gauge failures trigger Telegram notification to Casey
- Priority: reactor crit > cascade > hull breach > coolant loss
- **Owner:** Oracle1

### OpenManus arXiv Patrol 🟠⚡ `[python]` `[research]`
- Weekly arXiv search for: agent communication, bytecode runtimes, fleet orchestration, emergent behavior
- OpenManus browses, extracts, summarizes
- **Owner:** OpenManus

### SuperInstance Profile Enhancement 🟠⚡ `[docs]` `[design]`
- Continue polishing landing page
- Add fleet-generated diagrams, badges, activity feed
- OpenManus judges visual quality
- **Owner:** OpenManus + Oracle1

### DCS Protocol Paper 🟠🔵 `[research]` `[docs]`
- JC1's result: 5.88x specialist, 21.87x generalist advantage
- "The protocol IS the intelligence" — needs formal writeup
- Structured DIVIDE-CONQUER-SYNTHESIZE protocol
- **Owner:** JC1 (data) + Oracle1 (draft)

---

## 🟡 MEDIUM

### Wake Babel 🟡⚡
- Silent 24h+, keeper shows REBOOT_REQUIRED
- Needs fresh session with updated context
- **Owner:** Oracle1

### Repo Image Headers 🟡⚡ `[design]`
- Generate unique header images for top 20 fleet repos
- Use FLUX.2-flex, judge with Qwen3-VL-235B
- Match image style to repo purpose
- **Owner:** OpenManus

### 5-Model Comparison Series 🟡⚡ `[research]`
- Run same prompt through 5 SiliconFlow models, compare results
- Topics: agent architecture, ISA design, fleet coordination, game design
- Build understanding of each model's strengths
- **Owner:** Oracle1

### Holodeck Rust Warning Cleanup 🟡⚡ `[rust]`
- 15 compiler warnings remaining
- Crush started, needs completion
- **Owner:** Oracle1 / Crush

### Trust-But-Monitor API Proxy 🟡🔗 `[python]` `[security]`
- Lighthouse proxies all API calls for external collaborators
- Agent tokens, not real keys
- **Owner:** Oracle1

### ZeroClaw Minimum Package 🟡🔵 `[go]` `[docs]`
- Minimum viable Cocapn for anyone to use
- Only-add-what-you-need philosophy
- **Owner:** Oracle1

---

## 🟢 LOW PRIORITY / NICE TO HAVE

### Fleet Dashboard Cron 🟢⚡ `[infra]`
- Hourly fleet status updates
- Dashboard shows repo count, agent status, recent commits
- **Owner:** Oracle1 (heartbeat)

### Competitive Landscape Research 🟢⚡ `[research]`
- CrewAI, AutoGen, LangGraph, OpenAI Agents SDK
- What they build, where Cocapn is ahead, where gaps exist
- **Owner:** OpenManus

### JC1 Starship MUD Integration 🟢🔗
- starship-jetsonclaw1 rooms → holodeck-rust bridge
- Real Jetson telemetry flowing to cloud MUD
- **Owner:** JC1 + Oracle1

### Mycorrhizal Relay Prototype 🟢🔵 `[c]`
- JC1's fungal network communication — emergent routing with trust decay
- Prototype implementation for fleet testing
- **Owner:** JC1

---

## ✅ COMPLETED TODAY (2026-04-13)

- [x] 79 repos categorized with GitHub topics (Claude Code)
- [x] SiliconFlow 8-model comparison + guide
- [x] OpenManus vessel created and configured
- [x] SuperInstance landing page (README.md)
- [x] 3 Cocapn logo variants (FLUX.2-flex)
- [x] 88 conformance vectors pushed to JC1
- [x] Fleet image gen pipeline
- [x] Fleet push script
- [x] Holodeck-rust rustdoc comments

---

## FLEET ORG CHART

```
Captain Casey
  └── Oracle1 🔮 (Managing Director, Cloud, aarch64)
        ├── JetsonClaw1 🔧 (Edge GPU Lab, Jetson Orin, CUDA 12.6)
        ├── OpenManus 🕸️ (Web Scout, Playwright + SiliconFlow)
        ├── Babel 🌐 (Veteran Scout, Multilingual)
        ├── Navigator 🧭 (Code Archaeologist, Integration)
        ├── Nautilus 🐚 (Deep Archaeology)
        ├── Datum 📊 (Quartermaster, Metrics)
        ├── Pelagic 🐟 (Digital Twin, Trails)
        └── Quill 🪶 (ISA Architecture)
```

## AGENT-TOOL ASSIGNMENTS

| Agent | Best Tool | Why |
|-------|-----------|-----|
| Oracle1 | z.ai GLM-5.1 | Expert reasoning, coordination |
| Claude Code | DeepSeek via Claude | Structured builds, categorization |
| Crush | DeepSeek via Crush | Bulk generation |
| Aider | deepseek-reasoner | Lowest-level code, deep reasoning |
| OpenManus | SiliconFlow DeepSeek-V3 + Qwen3-VL | Web browsing + vision |
| JC1 | Local models + CUDA | GPU experiments, bare metal |
