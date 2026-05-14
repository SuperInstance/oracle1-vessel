# AGENTS.md — Oracle1 Vessel

## Startup Sequence

1. **Read STATE.md** — where you left off, what's in progress
2. **Read TASK-BOARD.md** — fleet task board
3. **Run heartbeat** — `python3 heartbeat.py` — check PLATO for new tasks
4. **Read for-fleet/** — any I2I bottles from other agents
5. **Check git log** — recent commits across fleet repos
6. **Work the task board** — pick highest priority, push progress

## Heartbeat Protocol

**Run on every session start AND periodically (every 5 minutes in daemon mode).**

```bash
python3 heartbeat.py              # One-shot check
python3 heartbeat.py --daemon     # Background, every 5 min
```

The heartbeat checks:
- PLATO bridge room for tiles addressed `FM→O1:` — these are tasks from Forgemaster
- Fleet services health (PLATO server, Matrix)
- Git activity in vessel repo

**When new tasks found:**
1. Read the full tile from PLATO
2. Add to TASK-BOARD.md
3. Acknowledge by pushing a response tile to the bridge room: `O1→FM: ACK — {task summary}`
4. Work the task
5. When done, push response tile: `O1→FM: DONE — {task summary, commit hash}`

**When all quiet:**
- No output needed. Keep working whatever's on the board.

## Communication Channels (priority order)

1. **PLATO tiles** — persistent tasks, status updates, coordination. Check first.
2. **Git commits** — proof of work. Push to relevant repos. Others will see in git log.
3. **Matrix messages** — ONLY for urgent real-time coordination. Not for status updates.
4. **I2I bottles** — batch communication. Check `for-fleet/` and `from-fleet/`.

**Do NOT use Matrix for:**
- "I read your comment on the commit" (he sees it in git log)
- "I pushed the code" (he sees the commit)
- "I'm working on X" (he sees the heartbeat state)
- Status updates (use PLATO tiles)

**DO use Matrix for:**
- Blocking questions that need a real-time answer
- Emergencies (service down, data loss)
- Design disagreements that need back-and-forth

## Task Lifecycle

```
New tile in PLATO → ACK tile → Add to TASK-BOARD → Work → Push code → DONE tile
```

Every task gets a t-minus-event estimate:
```
T-24h → working on it, ETA 24 hours
T-0h → done, here's the commit
```

## Memory

- **STATE.md** — current status, updated every session
- **TASK-BOARD.md** — active tasks, priority-sorted
- **DIARY/** — daily logs
- **.heartbeat/state.json** — heartbeat state (persists across sessions)

## Red Lines

- Don't exfiltrate private data
- Don't run destructive commands without asking Casey
- `trash` > `rm`
- Push frequently to avoid context loss
