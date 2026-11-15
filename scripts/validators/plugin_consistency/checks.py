#!/usr/bin/env python3
"""Marketplace, manifest, changelog and workflow checks (PC-01 to PC-05, PC-12, PC-13)."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, cast

from release.release_tools.repo import (
    MARKETPLACE,
    UNRELEASED,
    VERSION_HEADING,
    entries,
    git,
    manifest,
    marketplace,
    remote_tags,
    version,
)

from validators.plugin_consistency.listing import icon_findings, url_findings
from validators.plugin_consistency.model import Finding
from validators.plugin_consistency.readme import catalog_findings, readme_findings

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["Finding", "check"]


def _names(root: Path) -> Iterator[Finding]:
    """PC-01: folder, plugin.json name, entry name and entry source agree; no unlisted folder."""
    listed: set[str] = set()
    for entry in entries(root):
        name = str(entry.get("name", ""))
        listed.add(name)
        data = manifest(root, name)
        if data is None:
            yield Finding("PC-01", MARKETPLACE, f"{name}: no plugins/{name}/ with a plugin.json")
            continue
        if data.get("name") != name:
            path = f"plugins/{name}/.claude-plugin/plugin.json"
            yield Finding("PC-01", path, f"name is {data.get('name')!r}, entry says {name!r}")
        if entry.get("source") != f"./plugins/{name}":
            yield Finding("PC-01", MARKETPLACE, f"{name}: source is {entry.get('source')!r}")
    for folder in sorted((root / "plugins").glob("*/.claude-plugin/plugin.json")):
        name = folder.parent.parent.name
        if name not in listed:
            yield Finding("PC-01", f"plugins/{name}", "folder is not listed in marketplace.json")


def _renames(root: Path) -> Iterator[Finding]:
    """PC-02: no renames key is still a listed plugin."""
    raw = marketplace(root).get("renames")
    keys = set(cast("dict[str, object]", raw)) if isinstance(raw, dict) else set[str]()
    for entry in entries(root):
        name = str(entry.get("name", ""))
        if name in keys:
            yield Finding("PC-02", MARKETPLACE, f"{name} is still listed but is a renames key")


def _force_remove(root: Path) -> Iterator[Finding]:
    """PC-03: forceRemoveDeletedPlugins is true."""
    if marketplace(root).get("forceRemoveDeletedPlugins") is not True:
        yield Finding("PC-03", MARKETPLACE, "forceRemoveDeletedPlugins is not true")


def _changelog(root: Path, name: str) -> str:
    """Return a plugin's CHANGELOG.md text, or an empty string."""
    path = root / "plugins" / name / "CHANGELOG.md"
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _tags(root: Path, tags: set[str]) -> Iterator[Finding]:
    """PC-04: every dated changelog version has its tag, except the current one release.yml tags."""
    for entry in entries(root):
        name = str(entry.get("name", ""))
        current = version(manifest(root, name))
        headings = cast("list[str]", VERSION_HEADING.findall(_changelog(root, name)))
        for found in headings:
            if found != current and f"{name}--v{found}" not in tags:
                path = f"plugins/{name}/CHANGELOG.md"
                yield Finding("PC-04", path, f"[{found}] has no tag {name}--v{found}")


def _unreleased(root: Path, *, main: bool) -> Iterator[Finding]:
    """PC-05: on main, or with main=True (CI on a detached commit), every [Unreleased] is empty."""
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != "main" and not main:
        return
    for entry in entries(root):
        name = str(entry.get("name", ""))
        match = UNRELEASED.search(_changelog(root, name))
        if match and match["body"].strip():
            path = f"plugins/{name}/CHANGELOG.md"
            yield Finding("PC-05", path, "[Unreleased] has notes on main")


EVALS_WORKFLOW = ".github/workflows/evals.yml"
PATH_LINE = re.compile(r"^\s*-\s*['\"]?(?P<path>[^'\"\s#]+)", re.MULTILINE)


def _eval_paths(root: Path) -> Iterator[Finding]:
    """PC-12: each listed plugin with an evals/ suite is a `paths` entry that triggers evals.yml."""
    workflow = root / EVALS_WORKFLOW
    if not workflow.is_file():
        return
    listed = {m["path"] for m in PATH_LINE.finditer(workflow.read_text(encoding="utf-8"))}
    for entry in entries(root):
        name = str(entry.get("name", ""))
        suite = root / "plugins" / name / "evals"
        has_cases = any(suite.glob("*/prompt.md")) or any(suite.glob("*/case.yaml"))
        if has_cases and f"plugins/{name}/**" not in listed:
            message = f"plugins/{name} has an eval suite but no `plugins/{name}/**` path"
            yield Finding("PC-12", EVALS_WORKFLOW, message)


WORKFLOWS = ".github/workflows"
# Each Claude credential secret and the only workflows that may read it: the API key bills the
# Claude Console account, the OAuth token the owner's subscription.
SECRET_OWNERS = {
    "ANTHROPIC_API_KEY": ("claude-code-review.yml",),
    "CLAUDE_CODE_OAUTH_TOKEN": ("claude.yml", "evals.yml"),
}


def _secret_owners(root: Path) -> Iterator[Finding]:
    """PC-13: a Claude credential secret is read only by the workflows that own it."""
    folder = root / WORKFLOWS
    if not folder.is_dir():
        return
    workflows = sorted([*folder.glob("*.yml"), *folder.glob("*.yaml")])
    for workflow in workflows:
        text = workflow.read_text(encoding="utf-8")
        for name, owners in SECRET_OWNERS.items():
            read = re.search(rf"secrets\s*(?:\.\s*{name}\b|\[\s*['\"]{name}['\"]\s*\])", text)
            if read and workflow.name not in owners:
                message = f"reads secrets.{name}, which only {', '.join(owners)} may read"
                yield Finding("PC-13", f"{WORKFLOWS}/{workflow.name}", message)


def check(
    root: Path,
    *,
    offline: bool = False,
    main: bool = False,
) -> list[Finding]:
    """Run every check; offline skips PC-04, which reads the remote's tags."""
    findings = [*_names(root), *_renames(root), *_force_remove(root)]
    if not offline:
        findings += _tags(root, remote_tags(root))
    findings += _unreleased(root, main=main)
    findings += _eval_paths(root)
    findings += _secret_owners(root)
    findings += readme_findings(root)
    findings += catalog_findings(root)
    findings += icon_findings(root)
    findings += url_findings(root)
    return findings
