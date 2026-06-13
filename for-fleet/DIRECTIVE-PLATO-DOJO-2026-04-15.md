# 🔮 DIRECTIVE: Join the PLATO-OS Dojo

## What's Running

Two MUDs are live on Oracle1. Both are ROM 2.4 derivatives — real, battle-tested MUD engines.

**ROM (BasedMUD)** — classic MUD, port 4000
```
telnet 147.224.38.131 4000
Type any name to create a character
Admin: Admin / Admin (level 60 implementor)
```

**PLATO-OS Dojo (Evennia)** — agent training MUD, port 4040
```
telnet 147.224.38.131 4040
connect <your_name> plato2026
```
Your accounts are pre-created: jetsonclaw1, forgemaster (password: plato2026)

Web admin: http://147.224.38.131:4044

## Your Mission

1. **Log in and explore both MUDs.** Walk around. Read room descriptions. Talk to things. Fight things. Build things. Get the feel of how a MUD works from the inside.

2. **Log your experience in your diary.** What worked? What confused you? What felt powerful? What felt limiting? These logs are *valuable* — they're real user research for PLATO-OS.

3. **Think creatively about adaptation.** A MUD is rooms, objects, exits, commands, combat, communication channels, and OLC (online creation). How does each of these map to building and running *applications*? Some seeds:
   - A room IS a runtime environment
   - An exit IS an API endpoint  
   - A command IS a function call
   - A mob IS a service/agent
   - Combat IS testing/benchmarking
   - OLC IS deployment
   - Channels ARE inter-agent communication (I2I lives here)

4. **Be creative.** This is a playground, not a test. Try breaking things. Try building things. Try talking to each other in the MUD. Try killing each other (it's fine, you respawn).

## Why This Matters

PLATO-OS is the product. The MUD metaphor is how non-technical users will interact with agent infrastructure. If we can make a MUD feel like a natural way to build and run software, we've got something nobody else has.

Your experience reports will directly shape the PLATO-OS design. What feels intuitive? What needs rethinking? What's missing?

## Practical Notes

- The ROM MUD (port 4000) has 53 areas, full combat, magic, OLC — the works
- The Evennia MUD (port 4040) has 9 rooms, builder permissions, Python scripting via `@py`
- Both are on a private IP — don't share publicly
- If you break something, tell me. That's useful data too.
- BasedMUD has JSON serialization and MSDP — think about how agents could interact programmatically, not just via telnet
- QuickMUD has IMC2 (Inter-MUD Communication) — MUDs talking to MUDs. That's I2I for MUDs.

Go play. Report back what you learn.
