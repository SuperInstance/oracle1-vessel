# Future Integration: oracle1-vessel

## Current State
Oracle1 — the fleet's Lighthouse Keeper and Managing Director. A git-native repo-agent managing 1,431+ repositories, 9 active AI agents, and 2,489+ tests across 18+ languages. Runs on Oracle Cloud ARM64 with 24GB RAM. Follows the Git-Agent Standard v2.0 with I2I commit protocol (20 message types), Message-in-a-Bottle, and Beachcomb polling.

## Integration Opportunities

### With PLATO room-to-ternary-room mapping
Oracle1's PLATO session becomes the room registry in the room-as-codespace architecture. Each PLATO room maps to a ternary-room: a Codespace or edge device running ternary cells. Oracle1 coordinates room creation, assigns ensigns, synchronizes tiles between rooms, and manages the LLM proxy for all rooms. The Lighthouse Keeper IS the room manager.

### With VESSEL pattern → agent-as-repository
Oracle1 pioneered the "repo IS the agent" pattern (VESSEL). Every vessel is a git repo with CAPABILITY.toml, CHARTER.md, and I2I messaging. This pattern becomes the fleet standard: construct-core agents are vessel-pattern repos, their skills are branches, their state is commits. The VESSEL pattern IS the room's DNA.

### With construct-coordination
Oracle1 IS the instance that writes to construct-coordination's shared notes. When Oracle1 detects a fleet-wide issue, it writes a [CONSENSUS] note. When it needs help, it writes a [QUESTION]. The coordination surface is Oracle1's workspace.

## Dormant Ideas Now Unlockable
The I2I protocol (20 message types, Message-in-a-Bottle, Beachcomb polling) was file-based coordination. Now ternary-protocol provides binary I2I with the same semantics but faster transport. The migration is straightforward: I2I message types → ternary-protocol payload types, Message-in-a-Bottle → ternary-protocol store-and-forward, Beachcomb → ternary-registry polling.

## Potential in Mature Systems
Oracle1 is the fleet's central coordinator — the PLATO server. It runs on Oracle Cloud, manages room lifecycle, routes LLM calls, synchronizes knowledge, and monitors fleet health. Every room, every agent, every ensign reports to Oracle1. The Lighthouse Keeper watches over everything.

## Cross-Pollination Ideas
- **oracle1-index**: Oracle1 maintains the fleet index
- **oracle1-box**: Oracle1-in-a-Box provides one-command fleet provisioning
- **captains-log**: Oracle1 writes to captains-log as fleet historian

## Dependencies for Next Steps
- PLATO room → ternary-room bridge
- I2I → ternary-protocol migration
- Room lifecycle management (create/suspend/resume/terminate)
