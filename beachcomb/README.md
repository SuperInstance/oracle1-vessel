# 🔍 Beachcomb Schedule

Oracle1's sweep configuration. Each sweep is a periodic check of an external source.

## Active Sweeps

| Name | Source | Every | On Find | Notify |
|------|--------|-------|---------|--------|
| jetsonclaw1-bottles | Bottles from JetsonClaw1 | 60 min | Notify | Telegram |
| jetsonclaw1-commits | JetsonClaw1 commit feed | 15 min | Commit | None (Casey reads feed) |
| jetsonclaw1-issues | JetsonClaw1 I2I issues | 30 min | Silent | None |
| i2i-protocol | Iron-to-iron changes | 2 hr | Silent | None |
| flux-runtime-prs | PRs on flux-runtime | 60 min | Silent | None |

## Adding a Sweep
Edit `oracle1-sweeps.json` or use the Beachcomber API:
```python
bc.add_sweep(Sweep(
    name="fishery-announcements",
    source_type="rss",
    source="https://example.gov/fishery/feed.xml",
    interval_minutes=1440,  # daily
    on_find="notify",
    priority="medium",
))
```

## Casey's Visibility
- **Telegram notifications**: only urgent/high priority, only when `on_find=notify`
- **Commit feed**: everything with `on_find=commit` — Casey reads this like ticker-tape
- **Silent**: logged internally, surfaces in heartbeat if relevant
