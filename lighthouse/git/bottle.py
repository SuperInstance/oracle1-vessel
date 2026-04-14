"""
bottle.py — Message-in-a-Bottle read/write operations.

Provides structured read, write, list, and search operations for
the fleet's git-native async communication protocol.
"""

import os
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional


class BottleManager:
    """
    Manages Message-in-a-Bottle (MiB) operations.

    Bottles are the fleet's primary async communication mechanism.
    Each bottle is a markdown file in a directory hierarchy:
        message-in-a-bottle/for-{agent}/bottle-name.md
    """

    def __init__(self, bottle_dir: Optional[str] = None):
        if bottle_dir:
            self.bottle_dir = Path(bottle_dir)
        else:
            self.bottle_dir = Path.cwd() / "message-in-a-bottle"
        self.bottle_dir.mkdir(parents=True, exist_ok=True)

    def drop(
        self,
        recipient: str,
        subject: str,
        content: str,
        sender: str = "Lighthouse",
        bottle_type: str = "STATUS",
    ) -> str:
        """
        Drop a bottle for a specific agent.

        Creates a markdown file in the for-{recipient}/ directory
        with front matter and content.
        """
        target_dir = self.bottle_dir / f"for-{recipient}"
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        filename = f"{subject.replace(' ', '-').lower()[:50]}-{timestamp}.md"
        filepath = target_dir / filename

        front_matter = (
            f"---\n"
            f"from: {sender}\n"
            f"to: {recipient}\n"
            f"date: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"type: {bottle_type}\n"
            f"subject: {subject}\n"
            f"---\n\n"
        )

        full_content = f"{front_matter}# {subject}\n\n**From:** {sender}\n\n{content}\n"
        filepath.write_text(full_content, encoding="utf-8")

        return str(filepath)

    def drop_broadcast(self, subject: str, content: str, sender: str = "Lighthouse") -> str:
        """Drop a bottle for any vessel to find (broadcast)."""
        return self.drop(
            recipient="any-vessel",
            subject=subject,
            content=content,
            sender=sender,
            bottle_type="BROADCAST",
        )

    def list_bottles(self, target: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List bottles, optionally filtered by target agent.

        Returns a list of dicts with: filename, sender, date, type, subject.
        """
        bottles = []

        if target:
            search_dir = self.bottle_dir / f"for-{target}"
            if not search_dir.exists():
                return []
            dirs = [search_dir]
        else:
            if not self.bottle_dir.exists():
                return []
            dirs = [d for d in self.bottle_dir.iterdir() if d.is_dir()]

        for dir_path in dirs:
            for md_file in dir_path.glob("*.md"):
                bottle_info = self._parse_bottle_file(md_file)
                if bottle_info:
                    bottles.append(bottle_info)

        bottles.sort(key=lambda b: b.get("date", ""), reverse=True)
        return bottles

    def read_bottle(self, recipient: str, filename: str) -> Optional[str]:
        """Read a specific bottle's content."""
        filepath = self.bottle_dir / f"for-{recipient}" / filename
        if filepath.exists():
            return filepath.read_text(encoding="utf-8")
        return None

    def search_bottles(self, query: str) -> List[Dict[str, Any]]:
        """Search all bottles for content matching query string."""
        results = []
        query_lower = query.lower()
        for bottle in self.list_bottles():
            if query_lower in bottle.get("subject", "").lower():
                results.append(bottle)
            elif query_lower in bottle.get("filename", "").lower():
                results.append(bottle)
        return results

    def _parse_bottle_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Parse front matter from a bottle markdown file."""
        try:
            content = filepath.read_text(encoding="utf-8")
            info: Dict[str, Any] = {
                "filename": filepath.name,
                "filepath": str(filepath),
                "dir": filepath.parent.name,
            }

            # Parse YAML front matter
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    front = content[3:end].strip()
                    for line in front.split("\n"):
                        if ":" in line:
                            key, _, value = line.partition(":")
                            info[key.strip()] = value.strip()

            return info
        except Exception:
            return None

    def get_unread(
        self, agent_name: str, last_read: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get bottles that haven't been read yet."""
        all_bottles = self.list_bottles(target=agent_name)
        if last_read is None:
            return all_bottles
        return [
            b for b in all_bottles
            if b.get("date", "") > last_read
        ]

    @property
    def directories(self) -> List[str]:
        """List all for-{agent} directories."""
        if not self.bottle_dir.exists():
            return []
        return sorted(d.name for d in self.bottle_dir.iterdir() if d.is_dir())
