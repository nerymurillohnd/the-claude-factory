#!/usr/bin/env python3
"""Shared helpers for the skill-lint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from validators.skill_lint.discover import load_skill

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from validators.skill_lint.discover import Skill
    from validators.skill_lint.model import SkillKind

VALID_SKILL_MD = """\
---
name: demo-skill
description: Demonstrates a skill that passes every rule. Use when testing skill-lint.
---

# Demo skill

Say hello.
"""


def build_skill(
    root: Path,
    files: Mapping[str, str | bytes],
    *,
    layout: SkillKind = "plugin",
    plugin: str = "demo",
    name: str = "demo-skill",
) -> Path:
    """Write files under the layout's skill folder and return that folder.

    The layouts are plugins/<plugin>/skills/<name>/, .claude/skills/<name>/ and <name>/.
    """
    match layout:
        case "plugin":
            skill = root / "plugins" / plugin / "skills" / name
        case "project":
            skill = root / ".claude" / "skills" / name
        case "standalone":
            skill = root / name
    skill.mkdir(parents=True, exist_ok=True)
    for rel, content in files.items():
        target = skill / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            _ = target.write_bytes(content)
        else:
            _ = target.write_text(content, encoding="utf-8")
    return skill


def load(skill_dir: Path, modes: Mapping[str, str] | None = None) -> Skill:
    """Load a built skill with fixed git modes (none by default: every file untracked)."""
    fixed = dict(modes or {})
    return load_skill(skill_dir / "SKILL.md", mode_reader=lambda _: fixed)
