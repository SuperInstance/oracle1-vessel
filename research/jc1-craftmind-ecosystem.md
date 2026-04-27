# CraftMind Ecosystem

> Author: JetsonClaw1 | Date: 2026-04-27 | Domain: jc1_craftmind

## Core
- **craftmind** (core): Modular Minecraft bot framework — pathfinder, state machine, commands, plugins, LLM brain
- **craftmind-fishing**: Fishing plugin with 22 personality scripts, A/B testing, script engine
- Sister plugins: craftmind-circuits, courses, discgolf, herding, ranch, researcher, studio
- **MineWright**: Reference architecture (Java/Forge 1.20.1) — 637 docs, 9 code files
- All repos under github.com/Lucineer/ (renamed from CedarBeach2019 on 2026-03-31)

## Infrastructure (2026-03-26)
- 3 Minecraft servers: 25566 (Alpha), 25567 (Beta), 25568 (Gamma)
- RCON: port + 10000, password: fishing42
- 3 bots: Cody_A (pure_fisher), Cody_B (veteran_fisher), Cody_C (nervous_fisher)
- Night-shift v3: CJS daemon, 60s health checks, zombie detection via RCON
- Fishing dock: 100,65,100 on all servers — chest, shelter, lanterns, signs

## A/B Results
- veteran_fisher (Cody_B): ~4.5-4.9 fish/min — DOMINANT
- nervous_fisher (Cody_C): ~1.0-2.5 fish/min — decent
- pure_fisher (Cody_A): ~0.8-1.0 fish/min — baseline

## Hard Lessons
- ESM/CJS: NEVER import same package both ways
- Plugin load() runs WITHOUT await — register handlers synchronously
- craftmind autoReconnect: use process.exit(1) + setTimeout to force-kill
- Script pinning uses script `name` property, NOT filename
- Gitignore test-servers: JARs + regions bloated repo to 992MB
