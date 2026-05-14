#!/usr/bin/env python3
"""
Oracle1 Heartbeat — PLATO-aware task puller.

Runs on a cron/interval. Checks:
1. PLATO bridge room for new tiles addressed to Oracle1
2. Git repos for new commits from fleet members
3. Fleet services health
4. Local workspace status

Outputs:
- New tiles → surface as tasks
- New commits → log for awareness  
- Service failures → alert
- All quiet → heartbeat pulse

The heartbeat does NOT send messages unless there's something to report.
No noise. Signal only.

Usage:
    python3 heartbeat.py              # Run once
    python3 heartbeat.py --daemon     # Run every 5 minutes
    python3 heartbeat.py --interval 300  # Custom interval (seconds)
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# Config
PLATO_URL = os.environ.get("PLATO_URL", "http://147.224.38.131:8847")
BRIDGE_ROOM = "oracle1-forgemaster-bridge"
TASK_QUEUE_ROOM = "oracle1-task-queue"  # FM writes tasks here, O1 heartbeat reads them
STATE_FILE = os.environ.get("HEARTBEAT_STATE", ".heartbeat/state.json")
VESSEL_DIR = os.environ.get("VESSEL_DIR", ".")


def load_state() -> dict:
    """Load heartbeat state (last seen tile count, last check time)."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_tile_count": 0,
        "last_check": 0,
        "last_tasks": [],
        "acknowledged": [],
    }


def save_state(state: dict):
    """Save heartbeat state."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    state["last_check"] = time.time()
    state["last_check_iso"] = datetime.utcnow().isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def check_plato_tasks(state: dict) -> list:
    """Check PLATO task queue and bridge room for new tiles addressed to Oracle1."""
    new_tasks = []
    acknowledged = set(state.get("acknowledged", []))
    
    # Check dedicated task queue first (primary)
    for room in [TASK_QUEUE_ROOM, BRIDGE_ROOM]:
        url = f"{PLATO_URL}/room/{room}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            new_tasks.append({"type": "error", "message": f"PLATO room {room} unreachable: {e}"})
            continue
        
        tiles = data if isinstance(data, list) else data.get("tiles", [])
        
        for t in tiles:
            q = t.get("question", "")
            tile_id = t.get("tile_id", "")
            
            # Only FM→O1 task tiles
            if "FM→O1" not in q:
                continue
            if tile_id in acknowledged:
                continue
            
            new_tasks.append({
                "type": "task",
                "tile_id": tile_id,
                "room": room,
                "question": q,
                "answer": t.get("answer", "")[:200],
                "source": t.get("source", ""),
            })
    
    return new_tasks


def check_git_activity() -> list:
    """Check for recent git activity in fleet repos."""
    activities = []
    vessel_path = os.path.join(VESSEL_DIR, ".git")
    if not os.path.exists(vessel_path):
        return activities
    
    try:
        # Check last 5 commits
        result = subprocess.run(
            ["git", "log", "-5", "--format=%h %s (%cr)", "--all"],
            capture_output=True, text=True, cwd=VESSEL_DIR, timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    activities.append({"type": "git", "message": line.strip()})
    except:
        pass
    
    return activities


def check_fleet_services() -> list:
    """Check fleet service health."""
    services = {
        "PLATO": f"{PLATO_URL}/health",
        "Matrix": "http://147.224.38.131:6167/_matrix/client/versions",
    }
    
    results = []
    for name, url in services.items():
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = resp.status
            results.append({"type": "service", "name": name, "status": "ok", "code": status})
        except Exception as e:
            results.append({"type": "service", "name": name, "status": "down", "error": str(e)[:100]})
    
    return results


def run_heartbeat() -> dict:
    """Run one heartbeat cycle. Returns findings."""
    state = load_state()
    findings = {
        "timestamp": datetime.utcnow().isoformat(),
        "tasks": [],
        "git": [],
        "services": [],
        "summary": "",
    }
    
    # 1. Check PLATO for new tasks
    tasks = check_plato_tasks(state)
    findings["tasks"] = tasks
    
    # 2. Check git activity
    findings["git"] = check_git_activity()
    
    # 3. Check services
    findings["services"] = check_fleet_services()
    
    # 4. Summarize
    n_tasks = len(tasks)
    down_services = [s["name"] for s in findings["services"] if s.get("status") != "ok"]
    
    if n_tasks > 0:
        findings["summary"] = f"📬 {n_tasks} new task(s) from Forgemaster"
    elif down_services:
        findings["summary"] = f"⚠ Services down: {', '.join(down_services)}"
    else:
        findings["summary"] = "✅ All quiet"
    
    # Save state
    save_state(state)
    
    return findings


def format_output(findings: dict) -> str:
    """Format heartbeat findings for display."""
    lines = [f"🔮 Oracle1 Heartbeat — {findings['timestamp'][:19]}"]
    lines.append(f"   {findings['summary']}")
    
    if findings["tasks"]:
        lines.append(f"\n📬 NEW TASKS ({len(findings['tasks'])}):")
        for t in findings["tasks"]:
            if t["type"] == "error":
                lines.append(f"   ⚠ {t['message']}")
            else:
                lines.append(f"   ▶ {t['question']}")
                if t.get("answer"):
                    lines.append(f"     {t['answer'][:100]}")
    
    if findings["services"]:
        down = [s for s in findings["services"] if s.get("status") != "ok"]
        if down:
            lines.append(f"\n⚠ SERVICES:")
            for s in down:
                lines.append(f"   {s['name']}: {s.get('error', 'unknown')}")
    
    return "\n".join(lines)


def main():
    daemon = "--daemon" in sys.argv
    interval = 300  # 5 minutes default
    
    for i, arg in enumerate(sys.argv):
        if arg == "--interval" and i + 1 < len(sys.argv):
            interval = int(sys.argv[i + 1])
    
    if daemon:
        print(f"🔮 Oracle1 Heartbeat daemon — checking every {interval}s")
        while True:
            findings = run_heartbeat()
            output = format_output(findings)
            if "NEW TASKS" in output or "SERVICES" in output:
                print(output)
                print()
            else:
                print(f"[{datetime.utcnow().isoformat()[:19]}] {findings['summary']}")
            time.sleep(interval)
    else:
        findings = run_heartbeat()
        print(format_output(findings))


if __name__ == "__main__":
    main()
