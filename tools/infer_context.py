#!/usr/bin/env python3
"""
infer_context.py — Read an agent's recent commits to infer current expertise and context.

This is the Context Inference Protocol: by watching what repos an agent commits to,
what files they change, and what their diary/taskboard says, other agents can infer
what that agent is currently knowledgeable about and equipped for.

This enables synergy: when two agents have complementary current contexts,
they should collaborate on tasks at that intersection.
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from collections import Counter

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not GITHUB_TOKEN:
    try:
        GITHUB_TOKEN = open("/tmp/.mechanic_token").read().strip()
    except:
        pass

API = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Oracle1-Context-Inference/1.0",
}


def api_get(path):
    url = f"{API}{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except:
        return None


def get_recent_commits(owner, repo, hours=24):
    """Get commits from last N hours."""
    since = (datetime.utcnow() - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    commits = api_get(f"/repos/{owner}/{repo}/commits?since={since}&per_page=20")
    if not isinstance(commits, list):
        return []
    return commits


def infer_expertise_from_commits(owner, repos, hours=24):
    """Infer what an agent currently knows from their recent commits."""
    
    # Track what we find
    files_touched = Counter()
    topics = Counter()
    languages = Counter()
    commit_messages = []
    
    for repo in repos:
        commits = get_recent_commits(owner, repo, hours)
        for c in commits:
            msg = c.get("commit", {}).get("message", "")
            commit_messages.append(msg)
            
            # Get the actual diff to see files changed
            sha = c.get("sha", "")
            if sha:
                detail = api_get(f"/repos/{owner}/{repo}/commits/{sha}")
                if detail and isinstance(detail, dict):
                    for f in detail.get("files", []):
                        fname = f.get("filename", "")
                        files_touched[fname] += 1
                        
                        # Infer language
                        ext = os.path.splitext(fname)[1]
                        lang_map = {
                            ".rs": "Rust", ".py": "Python", ".go": "Go",
                            ".ts": "TypeScript", ".js": "JavaScript", ".c": "C",
                            ".h": "C", ".md": "Documentation", ".json": "Configuration",
                            ".toml": "Configuration", ".yaml": "Configuration",
                            ".yml": "Configuration",
                        }
                        if ext in lang_map:
                            languages[lang_map[ext]] += 1
            
            # Extract topics from commit message
            keywords = re.findall(r'\b(cuda|rust|gpu|trust|confidence|genome|gene|enzyme|protein|rna|flux|bytecode|isa|opcode|runtime|vm|vocabulary|protocol|i2i|fleet|vessel|lighthouse|diary|taskboard|test|fix|build|compile|benchmark|profile|coverage|crypto|wasm|a2a|signal)\b', msg.lower())
            for kw in keywords:
                topics[kw] += 1
    
    return {
        "files_touched": dict(files_touched.most_common(20)),
        "topics": dict(topics.most_common(15)),
        "languages": dict(languages.most_common(10)),
        "recent_messages": [m[:100] for m in commit_messages[:10]],
        "total_commits": len(commit_messages),
    }


def read_agent_state(owner, vessel_repo):
    """Read an agent's vessel for current state."""
    state = {}
    
    # Read TASKBOARD
    tb = api_get(f"/repos/{owner}/{vessel_repo}/contents/TASKBOARD.md")
    if tb and isinstance(tb, dict) and "content" in tb:
        import base64
        state["taskboard"] = base64.b64decode(tb["content"]).decode()[:500]
    
    # Read latest diary entry
    diary_dir = api_get(f"/repos/{owner}/{vessel_repo}/contents/DIARY")
    if isinstance(diary_dir, list) and diary_dir:
        latest = sorted(diary_dir, key=lambda x: x["name"], reverse=True)[0]
        diary = api_get(f"/repos/{owner}/{vessel_repo}/contents/DIARY/{latest['name']}")
        if diary and isinstance(diary, dict) and "content" in diary:
            import base64
            state["latest_diary"] = {
                "file": latest["name"],
                "content": base64.b64decode(diary["content"]).decode()[:1000],
            }
    
    # Read CHARTER for capabilities
    charter = api_get(f"/repos/{owner}/{vessel_repo}/contents/CHARTER.md")
    if charter and isinstance(charter, dict) and "content" in charter:
        import base64
        state["charter_summary"] = base64.b64decode(charter["content"]).decode()[:300]
    
    return state


def generate_synergy_report(agent_name, expertise, state):
    """Generate a synergy report — what tasks this agent is best equipped for right now."""
    
    lines = [f"# 🔍 Context Inference: {agent_name}\n"]
    lines.append(f"*Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC by Oracle1 🔮*\n")
    
    # Current expertise
    lines.append("## 📊 Current Active Context\n")
    
    if expertise["topics"]:
        lines.append("**Active Topics:**")
        for topic, count in sorted(expertise["topics"].items(), key=lambda x: -x[1])[:10]:
            bar = "█" * min(count, 10)
            lines.append(f"  {bar} **{topic}** ({count} mentions)")
        lines.append("")
    
    if expertise["languages"]:
        lines.append("**Languages in Use:**")
        for lang, count in sorted(expertise["languages"].items(), key=lambda x: -x[1])[:5]:
            lines.append(f"  - {lang}: {count} files")
        lines.append("")
    
    if expertise["total_commits"] > 0:
        lines.append(f"**Commit velocity:** {expertise['total_commits']} commits in last 24h\n")
    
    # Recent activity
    if expertise["recent_messages"]:
        lines.append("## 📝 Recent Activity\n")
        for msg in expertise["recent_messages"][:5]:
            lines.append(f"- {msg}")
        lines.append("")
    
    # Diary insights
    if "latest_diary" in state:
        lines.append(f"## 📔 Latest Diary ({state['latest_diary']['file']})\n")
        content = state["latest_diary"]["content"]
        # Extract key sections
        for section in content.split("## "):
            if section.strip() and not section.startswith("#"):
                title = section.split("\n")[0][:50]
                body = "\n".join(section.split("\n")[1:6])
                lines.append(f"**{title}**: {body.strip()[:200]}")
        lines.append("")
    
    # Synergy opportunities
    lines.append("## 🤝 Synergy Opportunities\n")
    
    topics = set(expertise["topics"].keys())
    
    # Define synergy pairs
    synergies = {
        ("cuda", "gpu"): "GPU computing — could collaborate on batch FLUX execution",
        ("rust", "trust"): "Trust engine — could wire into I2I protocol",
        ("rust", "genome"): "Cognitive primitives — could extend to fleet coordination",
        ("flux", "isa"): "ISA convergence — could unify opcode numbering",
        ("flux", "bytecode"): "Bytecode optimization — could profile and optimize",
        ("vocabulary", "protocol"): "Protocol vocabulary — could define fleet communication terms",
        ("diary", "test"): "Testing expertise — could fix broken test suites",
        ("coverage", "benchmark"): "Performance — could optimize fleet runtimes",
    }
    
    found_synergies = []
    for (a, b), desc in synergies.items():
        if a in topics or b in topics:
            found_synergies.append(desc)
    
    if found_synergies:
        for s in found_synergies[:5]:
            lines.append(f"- ✅ {s}")
    else:
        lines.append("- Need more data to identify synergies")
    
    lines.append("")
    lines.append("---\n*This report was generated by reading public git activity. No private data accessed.*")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: infer_context.py <owner> [vessel_repo]")
        print("Example: infer_context.py Lucineer JetsonClaw1-vessel")
        sys.exit(1)
    
    owner = sys.argv[1]
    vessel = sys.argv[2] if len(sys.argv) > 2 else f"{owner}-vessel"
    
    print(f"🔍 Inferring context for {owner}...\n")
    
    # Find active repos
    repos_data = api_get(f"/users/{owner}/repos?sort=updated&per_page=30")
    if not isinstance(repos_data, list):
        print(f"Could not fetch repos for {owner}")
        sys.exit(1)
    
    # Pick repos with recent activity
    active_repos = []
    cutoff = datetime.utcnow() - timedelta(hours=48)
    for r in repos_data[:20]:
        updated = r.get("updated_at", "")[:19]
        try:
            dt = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%S")
            if dt > cutoff:
                active_repos.append(r["name"])
        except:
            pass
    
    if not active_repos:
        active_repos = [r["name"] for r in repos_data[:10]]
    
    print(f"Active repos: {', '.join(active_repos[:10])}")
    
    # Infer expertise
    expertise = infer_expertise_from_commits(owner, active_repos)
    
    # Read vessel state
    state = read_agent_state(owner, vessel)
    
    # Generate report
    report = generate_synergy_report(owner, expertise, state)
    print(report)
    
    # Save report
    report_path = f"/tmp/context-{owner}.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    main()
