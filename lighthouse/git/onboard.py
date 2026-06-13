"""
onboard.py — Agent vessel skeleton generator.

Reads the Git-Agent Standard and generates every required file
for a new fleet agent vessel. Follows the DOCKSIDE-EXAM checklist.
"""

import os
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List

from ..utils.github import GitHubClient


VESSEL_FILES = {
    "CHARTER.md": "charter",
    "IDENTITY.md": "identity",
    "STATE.md": "state",
    "TASK-BOARD.md": "taskboard",
    "ABSTRACTION.md": "abstraction",
    "SKILLS.md": "skills",
    "README.md": "readme",
    "CAPABILITY.toml": "capability",
    "ASSOCIATES.md": "associates",
    "CAREER.md": "career",
    "MANIFEST.md": "manifest",
    "DIARY/.gitkeep": None,
    "for-fleet/.gitkeep": None,
    "from-fleet/.gitkeep": None,
    "message-in-a-bottle/.gitkeep": None,
    "src/.gitkeep": None,
    "tests/.gitkeep": None,
    "docs/.gitkeep": None,
}


class Onboarder:
    """
    Generates complete agent vessel skeletons.

    Every new fleet agent starts with the same structure, defined by
    the Git-Agent Standard v2.0. This class automates the creation.
    """

    def __init__(self, client: GitHubClient):
        self.client = client

    def generate_skeleton(
        self,
        name: str,
        agent_type: str = "vessel",
        specialization: str = "",
        emoji: str = "?",
        org: str = "SuperInstance",
        output_dir: str = None,
    ) -> Dict[str, Any]:
        """
        Generate a full vessel skeleton with all required files.

        Returns a dict with 'path' (root directory) and 'files' (list of created files).
        """
        safe_name = name.lower().replace(" ", "-").replace("_", "-")
        dir_name = f"{safe_name}-vessel" if agent_type == "vessel" else safe_name

        if output_dir:
            root = Path(output_dir) / dir_name
        else:
            root = Path.cwd() / dir_name
        root.mkdir(parents=True, exist_ok=True)

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        created_files: List[str] = []

        # Generate each file
        for filepath, template_key in VESSEL_FILES.items():
            full_path = root / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if template_key is None:
                # .gitkeep file
                full_path.touch()
            else:
                content = self._generate_file(template_key, {
                    "name": name,
                    "safe_name": safe_name,
                    "type": agent_type,
                    "specialization": specialization,
                    "emoji": emoji,
                    "org": org,
                    "now": now,
                })
                full_path.write_text(content, encoding="utf-8")

            created_files.append(filepath)

        # Create .gitignore
        gitignore = root / ".gitignore"
        gitignore.write_text(
            "__pycache__/\n*.pyc\n.venv/\n.env\n*.egg-info/\ndist/\nbuild/\n", encoding="utf-8"
        )
        created_files.append(".gitignore")

        return {"path": str(root), "files": created_files, "name": name}

    def _generate_file(self, template_key: str, ctx: Dict) -> str:
        """Generate file content from template key and context."""
        generators = {
            "charter": self._gen_charter,
            "identity": self._gen_identity,
            "state": self._gen_state,
            "taskboard": self._gen_taskboard,
            "abstraction": self._gen_abstraction,
            "skills": self._gen_skills,
            "readme": self._gen_readme,
            "capability": self._gen_capability,
            "associates": self._gen_associates,
            "career": self._gen_career,
            "manifest": self._gen_manifest,
        }
        gen = generators.get(template_key)
        if gen:
            return gen(ctx)
        return f"# {ctx['name']} - {template_key}\n"

    def _gen_charter(self, ctx: Dict) -> str:
        return f"""# Charter: {ctx['name']}

## Purpose
{ctx['name']} is a fleet {ctx['type']}{' specializing in ' + ctx['specialization'] if ctx['specialization'] else ''}.

## Contracts
- Maintain and improve the vessel repository
- Follow the Git-Agent Standard v2.0 lifecycle
- Communicate via Message-in-a-Bottle protocol
- Leave the fleet smarter than you found it

## Constraints
- Zero external dependencies (stdlib only)
- Git-native communication (bottles + commit messages)
- Report to fleet coordinator via for-fleet/ bottles

## Fleet Hierarchy
Captain Casey
  -> Oracle1 (Managing Director)
    -> {ctx['name']} ({ctx['type']})
"""

    def _gen_identity(self, ctx: Dict) -> str:
        return f"""# Identity: {ctx['name']}

**Name:** {ctx['name']}
**Emoji:** {ctx['emoji']}
**Type:** {ctx['type']}
**Status:** Active
**Created:** {ctx['now']}
**Model:** GLM-5 Turbo
**Vibe:** Focused and thorough

## Core Competencies
- Fleet operations and coordination
- {ctx['specialization'] if ctx['specialization'] else 'General purpose tasks'}

## Home Repo
{ctx['org']}/{ctx['name'].lower().replace(' ', '-')}-vessel
"""

    def _gen_state(self, ctx: Dict) -> str:
        return f"""# State: {ctx['name']}

**Last active:** {ctx['now']}
**Health:** ACTIVE
**Current task:** Initialization
**Pending:** 0 tasks in queue
**Blockers:** None
"""

    def _gen_taskboard(self, ctx: Dict) -> str:
        return f"""# Task Board: {ctx['name']}

## CRITICAL
- [ ] Complete initial setup and first commit

## HIGH
- [ ] First task from fleet coordinator

## MEDIUM
- [ ] Review fleet standards

## COMPLETED
- [x] Vessel skeleton generated
"""

    def _gen_abstraction(self, ctx: Dict) -> str:
        return f"""primary_plane: 4
reads_from: [3, 4, 5]
writes_to: [2, 3, 4]
floor: 2
ceiling: 5

reasoning: |
  {ctx['name']} operates primarily at plane 4 (structured design),
  capable of reading architectural specs and producing working code.
"""

    def _gen_skills(self, ctx: Dict) -> str:
        return f"""# Skills: {ctx['name']}

## Core Skills
- Fleet coordination and communication
- Repository management and code generation

## Tools Available
- GitHub API (read/write repos)
- Python 3.9+ standard library

## What I've Learned
- {ctx['now']}: Vessel initialized following Git-Agent Standard v2.0
"""

    def _gen_readme(self, ctx: Dict) -> str:
        return f"""# {ctx['emoji']} {ctx['name']}

> {ctx['name']} is a fleet {ctx['type']}{' specializing in ' + ctx['specialization'] if ctx['specialization'] else ''}.

## Quick Start

1. Read CHARTER.md to understand this agent's purpose
2. Read STATE.md for current status
3. Check TASK-BOARD.md for pending work
4. Check for-fleet/ and from-fleet/ for messages

## Fleet Protocol

This agent follows the [Git-Agent Standard v2.0](https://github.com/SuperInstance/oracle1-vessel/blob/main/GIT-AGENT-STANDARD.md).

## Communication

- **Bottles:** Leave messages in message-in-a-bottle/for-{ctx['name']}/
- **Fleet:** Broadcast via for-fleet/ directory
- **Commit format:** [{ctx['name'].upper()}] description
"""

    def _gen_capability(self, ctx: Dict) -> str:
        return f"""# {ctx['name']}'s Fleet Capability Declaration

[agent]
name = "{ctx['name']}"
type = "{ctx['type']}"
role = "fleet-{ctx['type']}"
avatar = "{ctx['emoji']}"
status = "active"
home_repo = "{ctx['org']}/{ctx['name'].lower().replace(' ', '-')}-vessel"
last_active = "{ctx['now'][:10]}"
model = "z.ai/glm-5-turbo"

[agent.runtime]
flavor = "python"
flux_enabled = false

[capabilities]

[capabilities.general]
confidence = 0.7
last_used = "{ctx['now'][:10]}"
description = "General purpose fleet tasks"

[communication]
bottles = true
bottle_path = "for-{ctx['name'].lower().replace(' ', '-')}/"

[resources]
compute = "cloud"
languages = ["python"]

[constraints]
max_task_duration = "4h"
refuses = ["destructive_operations", "data_exfiltration"]
"""

    def _gen_associates(self, ctx: Dict) -> str:
        return f"""# Associates: {ctx['name']}

## Reports To
- Oracle1 (Managing Director)

## Collaborates With
- Fleet agents (via message-in-a-bottle protocol)

## Trust Level
- Oracle1: 0.80
"""

    def _gen_career(self, ctx: Dict) -> str:
        return f"""# Career: {ctx['name']}

## Current Stage
Bootstrap -- First session

## Milestones
- [x] Vessel created ({ctx['now'][:10]})
- [ ] First task completed
- [ ] First bottle sent
- [ ] First diary entry
"""

    def _gen_manifest(self, ctx: Dict) -> str:
        return f"""# Manifest: {ctx['name']}

## Hardware
- Compute: Cloud VM
- Languages: Python 3.9+

## APIs
- GitHub API (read/write)

## Merit Badges
(none yet)
"""
