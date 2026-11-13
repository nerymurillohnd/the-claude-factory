#!/usr/bin/env python3
"""Read the marketplace, plugin manifests, tags and changelogs from a repository checkout."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pathlib import Path

MARKETPLACE = ".claude-plugin/marketplace.json"
MARKETPLACE_NAME = "the-claude-factory"
_HEADING = re.compile(r"^## \[(?P<version>[^\]]+)\]")
_LINK_REF = re.compile(r"^\[[^\]]+\]: ")


class GitError(RuntimeError):
    """A git command failed for a reason other than a missing object."""


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git in root without raising, and return the completed process."""
    exe = shutil.which("git")
    if exe is None:
        msg = "git is not installed"
        raise GitError(msg)
    return subprocess.run([exe, *args], cwd=root, check=False, capture_output=True, text=True)


def read_json(text: str) -> dict[str, object]:
    """Parse a JSON object, or raise ValueError when the text holds anything else."""
    data = cast("object", json.loads(text))
    if not isinstance(data, dict):
        msg = "expected a JSON object"
        raise TypeError(msg)
    return cast("dict[str, object]", data)


def marketplace(root: Path) -> dict[str, object]:
    """Return the parsed marketplace.json of the work tree."""
    return read_json((root / MARKETPLACE).read_text(encoding="utf-8"))


def entries(root: Path) -> list[dict[str, object]]:
    """Return the marketplace's plugin entries, in order."""
    raw = marketplace(root).get("plugins", [])
    items = cast("list[object]", raw) if isinstance(raw, list) else []
    return [cast("dict[str, object]", e) for e in items if isinstance(e, dict)]


def plugin_names(root: Path) -> list[str]:
    """Return the names of the marketplace's plugins, in order."""
    return [str(e.get("name", "")) for e in entries(root)]


def manifest_path(plugin: str) -> str:
    """Return the repository path of a plugin's plugin.json."""
    return f"plugins/{plugin}/.claude-plugin/plugin.json"


def manifest(root: Path, plugin: str, ref: str | None = None) -> dict[str, object] | None:
    """Return a plugin's plugin.json from the work tree, or at ref; None when it is absent."""
    if ref is None:
        path = root / manifest_path(plugin)
        return read_json(path.read_text(encoding="utf-8")) if path.is_file() else None
    shown = git(root, "show", f"{ref}:{manifest_path(plugin)}")
    return read_json(shown.stdout) if shown.returncode == 0 else None


def version(data: dict[str, object] | None) -> str | None:
    """Return the manifest's version as a string, or None."""
    value = data.get("version") if data else None
    return value if isinstance(value, str) else None


def remote_tags(root: Path, remote: str = "origin") -> set[str]:
    """Return the tag names on the remote, without the peeled `^{}` entries."""
    listed = git(root, "ls-remote", "--tags", remote)
    if listed.returncode != 0:
        raise GitError(listed.stderr.strip() or f"git ls-remote {remote} failed")
    tags: set[str] = set()
    for line in listed.stdout.splitlines():
        ref = line.partition("\t")[2]
        if ref.startswith("refs/tags/") and not ref.endswith("^{}"):
            tags.add(ref.removeprefix("refs/tags/"))
    return tags


def changelog_section(text: str, wanted: str) -> str | None:
    """Return the body of the `## [wanted]` section, stripped, or None when it is absent."""
    body: list[str] | None = None
    for line in text.splitlines():
        heading = _HEADING.match(line)
        if body is None:
            if heading and heading["version"] == wanted:
                body = []
            continue
        if heading or _LINK_REF.match(line):
            break
        body.append(line)
    return None if body is None else "\n".join(body).strip()
