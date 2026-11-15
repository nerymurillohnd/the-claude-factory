#!/usr/bin/env python3
"""Plugin eval suite checks: PC-12 (evals.yml triggers the suite) and PC-14 (effort tags)."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from release.release_tools.repo import entries
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.error import YAMLError

from validators.plugin_consistency.model import Finding

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["eval_findings"]

EVALS_WORKFLOW = ".github/workflows/evals.yml"
# evals.yml runs one CI group per effort level, each with `--tag effort-<level>`.
EFFORT_TAGS = ("effort-low", "effort-medium", "effort-high")
FRONTMATTER = re.compile(r"\A---\n(?P<yaml>.*?)\n---(?:\n|\Z)", re.DOTALL)


def _load(text: str) -> CommentedMap | None:
    """Return the YAML mapping in text, or None when it isn't one."""
    try:
        loaded = YAML(typ="rt").load(text)
    except YAMLError:
        return None
    return loaded if isinstance(loaded, CommentedMap) else None


def _pull_request_paths(text: str) -> set[str]:
    """Return the `paths` filter of evals.yml's pull_request trigger; never paths-ignore."""
    workflow = _load(text)
    if workflow is None:
        return set()
    # YAML 1.1 parsers read the bare key `on` as true.
    triggers = workflow.get("on", workflow.get(True))
    pull_request = triggers.get("pull_request") if isinstance(triggers, CommentedMap) else None
    paths = pull_request.get("paths") if isinstance(pull_request, CommentedMap) else None
    if not isinstance(paths, CommentedSeq):
        return set()
    return {path for path in paths if isinstance(path, str)}


def _cases_in(suite: Path) -> list[Path]:
    """Return the case folders of one eval directory: each holds prompt.md or case.yaml."""
    folders = {p.parent for p in [*suite.glob("*/prompt.md"), *suite.glob("*/case.yaml")]}
    return sorted(folders)


def _suite_cases(root: Path, name: str) -> list[Path]:
    """Return the case folders of a plugin's eval suite, the one evals.yml runs."""
    return _cases_in(root / "plugins" / name / "evals")


def _extra_cases(root: Path, name: str) -> list[Path]:
    """Return the case folders of a plugin's other eval directories (evals-<name>/)."""
    plugin = root / "plugins" / name
    return [case for suite in sorted(plugin.glob("evals-*/")) for case in _cases_in(suite)]


def _tags(case: Path) -> list[str]:
    """Return a case's tags: prompt.md frontmatter overrides the top-level tags of case.yaml."""
    found: object = None
    prompt = case / "prompt.md"
    if prompt.is_file():
        match = FRONTMATTER.match(prompt.read_text(encoding="utf-8"))
        frontmatter = _load(match["yaml"]) if match else None
        found = frontmatter.get("tags") if frontmatter is not None else None
    spec = case / "case.yaml"
    if found is None and spec.is_file():
        data = _load(spec.read_text(encoding="utf-8"))
        found = data.get("tags") if data is not None else None
    if not isinstance(found, CommentedSeq):
        return []
    return [tag for tag in found if isinstance(tag, str)]


def _eval_paths(root: Path, suites: dict[str, list[Path]]) -> Iterator[Finding]:
    """PC-12: each plugin with a suite is a `paths` entry of evals.yml, which must exist."""
    workflow = root / EVALS_WORKFLOW
    text = workflow.read_text(encoding="utf-8") if workflow.is_file() else ""
    listed = _pull_request_paths(text)
    for name in suites:
        if f"plugins/{name}/**" not in listed:
            message = f"plugins/{name} has an eval suite but no `plugins/{name}/**` path"
            yield Finding("PC-12", EVALS_WORKFLOW, message)


def _effort_tags(root: Path, suites: dict[str, list[Path]]) -> Iterator[Finding]:
    """PC-14: each case has exactly one known effort tag, or no CI group or local run selects it."""
    for cases in suites.values():
        for case in cases:
            efforts = [tag for tag in _tags(case) if tag.startswith("effort-")]
            if len(efforts) != 1 or efforts[0] not in EFFORT_TAGS:
                path = case.relative_to(root).as_posix()
                has = ", ".join(efforts) or "none"
                message = f"needs one effort tag (low, medium, high); has {has}"
                yield Finding("PC-14", path, message)


def eval_findings(root: Path) -> Iterator[Finding]:
    """Run PC-12 on each listed plugin with an evals/ suite, and PC-14 on all its eval cases."""
    suites = {
        name: cases
        for entry in entries(root)
        if (cases := _suite_cases(root, name := str(entry.get("name", ""))))
    }
    yield from _eval_paths(root, suites)
    names = [str(entry.get("name", "")) for entry in entries(root)]
    tagged = {name: suites.get(name, []) + _extra_cases(root, name) for name in names}
    yield from _effort_tags(root, tagged)
