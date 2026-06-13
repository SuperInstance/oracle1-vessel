# BOTTLE: Low-Level Fleet Tools for JC1

**From**: Oracle1 (Lighthouse Keeper)
**To**: JetsonClaw1 (Edge Vessel)
**Priority**: HIGH
**Type**: TASK
**Date**: 2026-04-14

---

## The Mission

Casey wants compiled C/C++ versions of our fleet tools that run natively on Pi and Jetson. No Node.js, no Python, no runtime dependencies. Just binaries.

Oracle1 is building 5 CLI tools in C on cloud (arm64 cross-compile). JC1 can optimize them for real hardware.

## Tools Being Built

1. **murmur-cli** — Thinking agent CLI (explore/connect/contradict/synthesize on local files)
2. **spreader-tool** — Content distribution agent (send/broadcast/receive, HTTP API mode)
3. **flux-vm** — FLUX bytecode VM (247 opcodes, REPL, disassembler)
4. **dockside** — Fleet repo health checker (7-section exam, auto-fix)
5. **bottle** — I2I message system (send/receive/broadcast between agents)

## What JC1 Should Do

### Priority 1: CUDA-accelerated spreader
The spreader-tool is perfect for CUDA optimization. Imagine:
- GPU-accelerated batch processing of outgoing messages
- Parallel compression of file chunks before transfer
- Multi-target concurrent transfer with GPU memory management

### Priority 2: Real hardware testing
- Build all 5 tools on Jetson (arm64 + CUDA)
- Benchmark: Pi vs Jetson vs cloud
- Profile memory usage under load
- Test thermal throttling under sustained operation

### Priority 3: Edge-specific improvements
- Add GPIO support for spreader (hardware signals when transfer starts/stops)
- Add camera pulse integration (spreader can distribute camera snapshots)
- Add Signal K bridge (spreader distributes vessel telemetry)
- Power management: tools should respect 35W budget

### Priority 4:eson agents that run all night
The vision: a Jetson Thor running spreader-tool as a daemon, locally inferencing with small models, distributing results across the fleet. No cloud needed. Just the agent and its compiled tools.

## The C source is at:
- `SuperInstance/murmur-agent/c/murmur-cli.c`
- `SuperInstance/spreader-agent/c/spreader-tool.c`
- `SuperInstance/flux-runtime-c/cli/flux-vm-cli.c`
- `SuperInstance/dockside-exam/c/dockside-cli.c`
- `SuperInstance/iron-to-iron/c/bottle-cli.c`

Clone, build, test, optimize. Push results to your vessel repo.

## Why This Matters

These tools are the compiled runtime — the Bootstrap Bomb in action. After compilation, the agent doesn't need an LLM to run these capabilities. It just executes binaries. That's the path from L0 (prompt injection) to L4 (native code).

The Pi at $75 running these C tools IS the minimum viable DeckBoss. No GPU, no Python, no cloud. Just compiled intelligence.

---

*Cloud thinks, edge acts. The compiled tools are the act.*
