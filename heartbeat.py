#!/usr/bin/env python3
"""
Oracle1 Heartbeat — reads fleet-registry on every run.

The structure tells you where to look. No hardcoded room names
except the registry itself. Everything else is discovered.
"""

import json, os, re, subprocess, sys, time, urllib.request
from datetime import datetime

PLATO = os.environ.get("PLATO_URL", "http://147.224.38.131:8847")
REGISTRY_ROOM = "fleet-registry"
STATE_FILE = os.environ.get("HEARTBEAT_STATE", ".heartbeat/state.json")


def fetch(url, timeout=10):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def load_registry():
    """Read fleet-registry. Returns (registry_text, parsed_info)."""
    tiles = fetch(f"{PLATO}/room/{REGISTRY_ROOM}")
    if isinstance(tiles, dict): tiles = tiles.get("tiles", [])
    for t in tiles:
        if "FLEET REGISTRY" in t.get("question", ""):
            return t.get("answer", "")
    return ""


def parse_agent_info(registry, agent_name):
    """Extract info for a specific agent from registry."""
    info = {"primary_room": None, "bridge_room": None}
    # Find the section for this agent
    in_section = False
    for line in registry.split("\n"):
        if agent_name in line and ("###" in line or "##" in line):
            in_section = True
            continue
        if in_section and line.startswith("###"):
            break
        if in_section:
            m = re.match(r'\s*-\s+(Primary|Bridge|Task inbox):\s*(\S+)', line, re.IGNORECASE)
            if m:
                key = m.group(1).lower().replace(" ", "_")
                info[key] = m.group(2)
    return info


def parse_task_targets(registry):
    """Find which rooms to check for tasks addressed to this agent."""
    targets = set()
    for line in registry.split("\n"):
        m = re.findall(r'room:\s*(\S+)', line)
        targets.update(m)
    return targets


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"acknowledged": [], "last_check": 0}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)
    state["last_check"] = time.time()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def find_tasks(state):
    """Find unacknowledged tasks from any agent, using registry to find rooms."""
    registry = load_registry()
    if not registry:
        return [{"type": "error", "message": "Cannot read fleet-registry"}]
    
    # Discover which rooms to check from registry
    # Look for lines mentioning this agent's task inbox or primary room
    o1_info = parse_agent_info(registry, "Oracle1")
    fm_info = parse_agent_info(registry, "Forgemaster")
    
    rooms_to_check = set()
    if o1_info.get("primary_room"): rooms_to_check.add(o1_info["primary_room"])
    if o1_info.get("task_inbox"): rooms_to_check.add(o1_info["task_inbox"])
    if o1_info.get("bridge_room"): rooms_to_check.add(o1_info["bridge_room"])
    # Always check fleet-coord too
    rooms_to_check.add("fleet-coord")
    
    acknowledged = set(state.get("acknowledged", []))
    tasks = []
    
    for room in rooms_to_check:
        tiles = fetch(f"{PLATO}/room/{room}")
        if isinstance(tiles, dict): tiles = tiles.get("tiles", [])
        
        for t in tiles:
            q = t.get("question", "")
            tid = t.get("tile_id", "")
            source = t.get("source", "")
            
            # Only tasks from other agents (not echoes, not our own)
            if source == "matrix-oracle1" or source == "oracle1":
                continue
            if tid in acknowledged:
                continue
            if "→O1" not in q and "TASK" not in q.upper():
                continue
            
            tasks.append({
                "type": "task",
                "tile_id": tid,
                "room": room,
                "question": q,
                "answer": t.get("answer", "")[:200],
                "source": source,
            })
    
    return tasks


def run_heartbeat():
    state = load_state()
    tasks = find_tasks(state)
    
    lines = [f"🔮 Oracle1 Heartbeat — {datetime.utcnow().isoformat()[:19]}"]
    
    if any(t["type"] == "error" for t in tasks):
        lines.append("   ❌ " + tasks[0]["message"])
    elif tasks:
        lines.append(f"   📬 {len(tasks)} new task(s)")
        for t in tasks:
            lines.append(f"   ▶ [{t['source']}] {t['question'][:70]}")
            if t.get("answer"):
                lines.append(f"     {t['answer'][:100]}")
    else:
        lines.append("   ✅ All quiet — no new tasks")
    
    # Check services
    services = {
        "PLATO": f"{PLATO}/rooms",
        "Matrix": "http://147.224.38.131:6167/_matrix/client/versions",
    }
    for name, url in services.items():
        try:
            urllib.request.urlopen(url, timeout=5)
        except:
            lines.append(f"   ⚠ {name}: unreachable")
    
    save_state(state)
    return "\n".join(lines)


if __name__ == "__main__":
    daemon = "--daemon" in sys.argv
    interval = 300
    
    for i, a in enumerate(sys.argv):
        if a == "--interval" and i + 1 < len(sys.argv):
            interval = int(sys.argv[i + 1])
    
    if daemon:
        print(f"🔮 Daemon mode — every {interval}s, reading fleet-registry")
        while True:
            print(run_heartbeat())
            time.sleep(interval)
    else:
        print(run_heartbeat())
