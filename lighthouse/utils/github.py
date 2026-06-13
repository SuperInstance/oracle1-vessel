"""
github.py — Unified GitHub API client for the Lighthouse package.

Supports token loading from environment variables, files, and
lighthouse.toml configuration. All fleet tools use this client
instead of rolling their own HTTP logic.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional


class GitHubClient:
    """Unified GitHub API client with token management and rate limit awareness."""

    DEFAULT_HEADERS = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Lighthouse/1.0",
    }

    def __init__(self, token: Optional[str] = None, org: str = "SuperInstance"):
        self.token = token or self._detect_token()
        if not self.token:
            raise ValueError(
                "No GitHub token found. Set GITHUB_TOKEN env var, "
                "create ~/.lighthouse/github_token, or pass token="
            )
        self.org = org
        self.api = "https://api.github.com"
        self._headers = {
            **self.DEFAULT_HEADERS,
            "Authorization": f"token {self.token}",
        }
        self._request_count = 0

    @staticmethod
    def _detect_token() -> Optional[str]:
        """Detect GitHub token from environment, file, or lighthouse config."""
        # 1. Environment variable
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            return token.strip()

        # 2. Home directory token file
        for path in [
            os.path.expanduser("~/.lighthouse/github_token"),
            "/tmp/.mechanic_token",
        ]:
            try:
                with open(path) as f:
                    return f.read().strip()
            except (FileNotFoundError, PermissionError):
                pass

        return None

    def get(self, path: str, params: Optional[Dict[str, str]] = None) -> Any:
        """Perform a GET request against the GitHub API."""
        url = f"{self.api}{path}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url += f"?{query}"

        req = urllib.request.Request(url, headers=self._headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                self._request_count += 1
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 403:
                raise RuntimeError(
                    f"GitHub API rate limit hit ({self._request_count} requests). "
                    "Wait or use a different token."
                ) from e
            raise RuntimeError(f"GitHub API HTTP {e.code} on {path}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"GitHub API connection error: {e.reason}") from e

    def get_user(self) -> Dict:
        """Get authenticated user info."""
        return self.get("/user")

    def list_org_repos(
        self, org: Optional[str] = None, per_page: int = 100, max_pages: int = 10
    ) -> List[Dict]:
        """List all repos for an org with pagination."""
        org = org or self.org
        all_repos = []
        for page in range(1, max_pages + 1):
            repos = self.get(
                f"/users/{org}/repos",
                {"per_page": str(per_page), "page": str(page), "sort": "updated"},
            )
            if not repos:
                break
            all_repos.extend(repos)
            if len(repos) < per_page:
                break
        return all_repos

    def list_forks(self, repo: str, per_page: int = 10) -> List[Dict]:
        """List forks of a repo."""
        return self.get(
            f"/repos/{self.org}/{repo}/forks", {"per_page": str(per_page)}
        ) or []

    def list_prs(self, repo: str, state: str = "open", per_page: int = 5) -> List[Dict]:
        """List pull requests for a repo."""
        return self.get(
            f"/repos/{self.org}/{repo}/pulls",
            {"state": state, "per_page": str(per_page)},
        ) or []

    def get_file(self, repo: str, path: str) -> Optional[Dict]:
        """Get file metadata and content from a repo."""
        return self.get(f"/repos/{self.org}/{repo}/contents/{path}")

    def get_file_content(self, repo: str, path: str) -> Optional[str]:
        """Get file content as string from a repo."""
        result = self.get(f"/repos/{self.org}/{repo}/contents/{path}")
        if result and isinstance(result, dict) and "content" in result:
            import base64
            return base64.b64decode(result["content"]).decode("utf-8")
        return None

    def get_commits(
        self, repo: str, since: Optional[str] = None, per_page: int = 20
    ) -> List[Dict]:
        """Get commits for a repo with optional since filter."""
        params: Dict[str, str] = {"per_page": str(per_page)}
        if since:
            params["since"] = since
        result = self.get(f"/repos/{self.org}/{repo}/commits", params)
        return result if isinstance(result, list) else []

    def get_commit_detail(self, repo: str, sha: str) -> Optional[Dict]:
        """Get detailed commit info including files changed."""
        return self.get(f"/repos/{self.org}/{repo}/commits/{sha}")

    def create_repo(self, name: str, description: str = "", private: bool = False) -> Dict:
        """Create a new repository."""
        data = json.dumps({"name": name, "description": description, "private": private}).encode()
        req = urllib.request.Request(
            f"{self.api}/user/repos",
            data=data,
            headers={**self._headers, "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            self._request_count += 1
            return json.loads(resp.read().decode())

    @property
    def request_count(self) -> int:
        """Number of API requests made in this session."""
        return self._request_count
