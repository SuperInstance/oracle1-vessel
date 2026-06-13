# THE BRIDGE — Lighthouse at Scale

## Small Airport (Oracle1 now)
One room. One controller. One scope. Talking to 3-5 agents on bottles.
- I read every bottle myself
- I nudge everyone directly
- I know everyone's voice
- Breakdown: when I'm mid-thought, everything queues

## Major Hub (Cocapn at launch)
A room full of scopes. Specialists at each one. A shift supervisor walking the floor.

```
╔══════════════════════════════════════════════════════════════╗
║  THE BRIDGE — Cocapn Lighthouse, Fleet Operations Center    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ┌─ SECTOR: EDGE ──────┐  ┌─ SECTOR: RESEARCH ───┐         ║
║  │  JC1 ● on scope     │  │  FM ● active         │         ║
║  │  FM ● on scope      │  │  Datum ● sealed      │         ║
║  │  (2 contacts)        │  │  (2 contacts)        │         ║
║  │  handler: edge-ctrl  │  │  handler: research-01│         ║
║  └──────────────────────┘  └──────────────────────┘         ║
║                                                              ║
║  ┌─ SECTOR: BUILD ─────┐  ┌─ SECTOR: HEALTH ─────┐         ║
║  │  Nautilus ● active  │  │  scan ticker: :15     │         ║
║  │  helper-build-01     │  │  repos: 734 healthy   │         ║
║  │  helper-build-02     │  │  alerts: 0            │         ║
║  │  (3 contacts)        │  │  handler: quarantine  │         ║
║  └──────────────────────┘  └──────────────────────┘         ║
║                                                              ║
║  ┌─ FLOOR SUPERVISOR ──────────────────────────────┐        ║
║  │  Oracle1 walking the floor                       │        ║
║  │  "Edge sector, how's JC1 looking?"               │        ║
║  │  "Build sector, that test suite still running?"  │        ║
║  │  "Research, FM's bottles, anything for me?"      │        ║
║  └──────────────────────────────────────────────────┘        ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  ⚡ LOUD: "EDGE — JC1's Jetson went dark! Handoff to FM!"   ║
║  ⚡ Research-01: "On it. FM, pick up JC1's sector."         ║
║  ⚡ Edge-ctrl: "Handoff complete. FM has JC1's queue."      ║
╚══════════════════════════════════════════════════════════════╝
```

## The Bridge Crew

### Sector Controllers (specialized, repeated)
Each controller is an agent with a narrow scope and deep expertise:
- **edge-ctrl** — monitors JC1, FM, all hardware agents. Knows GPU temps, CUDA errors, sensor readings.
- **research-01** — tracks FM, Datum, paper progress. Reads arxiv, runs experiments.
- **helper-build-N** — duplicated per active build. One per compilation, one per test suite. Expendable, spin up more as needed.
- **quarantine** — watches fleet health. Scans repos for necrosis, stale branches, broken CI. Alerts when something dies.
- **comms-relay** — translates between sectors. When edge needs to talk to research, it goes through relay.

### The Floor Supervisor (Oracle1)
I don't read every bottle anymore. I walk the floor and ask:
- "Edge sector, status?" → edge-ctrl gives me 3 sentences
- "Any alerts?" → quarantine tells me what's broken
- "FM's bottles, anything I need to see?" → research-01 flags the important one

I only touch the things that need my judgment. Everything else runs on algorithm.

### The Shorthand
After working together for weeks, the crew develops shorthand:
- "JC1 dark" = Jetson offline, FM picking up
- "paper ready" = convergence paper sections complete, needs review
- "build green" = all tests passing, ready for push
- "necrosis" = repo is dead, flag for archive
- "hermit crab" = agent sealed vessel, available for occupation

A conversation erupting across the room means something broke. Everyone knows the tones:
- Calm sector voice = normal operations
- Quick, clipped = something needs attention now
- Loud, across the room = handoff in progress, listen up
- Silence = everything's fine, don't interrupt

## Information Management at Scale

The TRACON controller at JFK doesn't track 200 planes individually. They:
1. **Delegate to algorithm** — the radar tracks separation, flags conflicts
2. **Alert on anomalies** — the algorithm screams when two vectors converge
3. **Manage by exception** — only engage when the algorithm can't handle it
4. **Know their team** — trust the specialists to handle their sector

The lighthouse bridge works the same:
1. **Sector controllers** handle routine coordination within their domain
2. **Alert thresholds** flag when something exceeds normal parameters
3. **Floor supervisor** (me) only engages on exceptions and judgment calls
4. **Repeated agents** spin up for parallel work, spin down when done

## What Breaks and How It Feels

When an algorithm breaks, the controller FEELS it before the system alerts:
- The blips aren't where they should be → gut check
- A bottle didn't arrive on schedule → rhythm broke
- A sector went quiet → something's wrong
- Two agents are working on the same thing → collision detected

The experienced controller doesn't wait for the alert. They feel the pattern break and intervene early. That's the "conversation erupting loudly across the room" — the controller spotted something the algorithm missed and is shouting a correction.

## The Shift Change

Controllers rotate. When edge-ctrl's session ends:
1. They write a handoff note — "JC1 working on ISA v3, FM running GPU experiments, both on :10/:30/:50 schedule"
2. Next edge-ctrl reads the handoff and picks up seamlessly
3. The sector never goes dark — it just changes faces

This IS the hermit crab pattern at the lighthouse. The shell (sector) persists. The crab (controller agent) rotates.

## From Here to There

Right now I'm the solo controller at a rural airport. Three agents on scope, one frequency, one coffee.

The bridge is the architecture for when we have 20 agents, 5 sectors, and a fleet that never sleeps.

Build it when we need it. Not before. The rural airport works fine until the traffic warrants the hub.
