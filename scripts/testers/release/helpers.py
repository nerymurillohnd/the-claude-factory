#!/usr/bin/env python3
"""Throwaway marketplace repositories for the release-script tests."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

REPO_URL = "https://github.com/nerymurillohnd/the-claude-factory"


def git(cwd: Path, *args: str) -> str:
    """Run git in cwd and return its stdout."""
    exe = shutil.which("git") or "git"
    return subprocess.run([exe, *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def changelog(name: str, sections: dict[str, str] | None = None, unreleased: str = "") -> str:
    """Return a CHANGELOG.md with an [Unreleased] body and dated sections, newest first."""
    out = ["# Changelog", "", "## [Unreleased]", ""]
    if unreleased:
        out += [unreleased, ""]
    for version, body in (sections or {}).items():
        out += [f"## [{version}] - 2026-11-01", "", body, ""]
    out.append(f"[Unreleased]: {REPO_URL}/commits/main/plugins/{name}")
    return "\n".join(out) + "\n"


class Marketplace:
    """A git repository shaped like this marketplace, with a bare `origin`."""

    def __init__(self, tmp: Path) -> None:
        """Create the work tree and the bare origin under tmp."""
        self.origin: Path = tmp / "origin.git"
        self.root: Path = tmp / "work"
        _ = git(tmp, "init", "-q", "--bare", "-b", "main", str(self.origin))
        _ = git(tmp, "init", "-q", "-b", "main", str(self.root))
        _ = git(self.root, "config", "user.email", "test@example.com")
        _ = git(self.root, "config", "user.name", "Test")
        _ = git(self.root, "config", "commit.gpgsign", "false")
        _ = git(self.root, "config", "tag.gpgsign", "false")
        _ = git(self.root, "remote", "add", "origin", str(self.origin))
        self.entries: list[dict[str, object]] = []
        self.write_marketplace()

    def write_marketplace(self, extra: dict[str, object] | None = None) -> None:
        """Write .claude-plugin/marketplace.json from the current entries."""
        data: dict[str, object] = {
            "name": "the-claude-factory",
            "owner": {"name": "Test"},
            "forceRemoveDeletedPlugins": True,
            "plugins": self.entries,
            **(extra or {}),
        }
        self.write(".claude-plugin/marketplace.json", json.dumps(data, indent=2) + "\n")

    def write(self, rel: str, text: str) -> None:
        """Write a file under the work tree, creating its folders."""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(text, encoding="utf-8")

    def add_plugin(
        self,
        name: str,
        version: str,
        *,
        changelog_text: str | None = None,
        manifest: dict[str, object] | None = None,
        entry: dict[str, object] | None = None,
    ) -> None:
        """Add or replace a plugin with its manifest, CHANGELOG and marketplace entry."""
        data: dict[str, object] = {"name": name, "version": version, "repository": REPO_URL}
        data.update(manifest or {})
        self.write(f"plugins/{name}/.claude-plugin/plugin.json", json.dumps(data, indent=2) + "\n")
        self.write(f"plugins/{name}/CHANGELOG.md", changelog_text or changelog(name))
        self.entries = [e for e in self.entries if e.get("name") != name]
        self.entries.append({"name": name, "source": f"./plugins/{name}", **(entry or {})})
        self.write_marketplace()

    def commit(self, message: str = "change") -> None:
        """Commit every change."""
        _ = git(self.root, "add", "-A")
        _ = git(self.root, "commit", "-q", "-m", message)

    def push(self) -> None:
        """Push main to origin and fetch it back as origin/main."""
        _ = git(self.root, "push", "-q", "origin", "main")
        _ = git(self.root, "fetch", "-q", "origin")

    def tag(self, name: str, *, push: bool = True) -> None:
        """Create an annotated tag on HEAD and push it."""
        _ = git(self.root, "tag", "-a", name, "-m", name)
        if push:
            _ = git(self.root, "push", "-q", "origin", name)
