#!/usr/bin/env python3
"""Tests for skill-diagnostics' plugin.json: the on_skill_write option takes fixed values.

Run: scripts/testers/run_unittest.py scripts/testers/skill-diagnostics
Standard library only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[3]
MANIFEST = REPO / "plugins" / "skill-diagnostics" / ".claude-plugin" / "plugin.json"


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def option() -> JsonObject:
    """Return the on_skill_write entry of userConfig, or an empty object when it is missing."""
    value: object = _decode(MANIFEST.read_text(encoding="utf-8"))
    for key in ("userConfig", "on_skill_write"):
        value = value.get(key) if isinstance(value, JsonObject) else None
    return value if isinstance(value, JsonObject) else JsonObject()


class OnSkillWriteOption(unittest.TestCase):
    """Claude Code accepts only the three modes, so the hooks need no fallback."""

    def test_on_skill_write_has_fixed_options(self) -> None:
        """The option lists gate, suggest and off, in that order."""
        self.assertEqual(option().get("options"), ["gate", "suggest", "off"])

    def test_default_is_gate(self) -> None:
        """The default is one of the options: gate."""
        self.assertEqual(option().get("default"), "gate")

    def test_is_a_single_plain_string(self) -> None:
        """Options apply only to a string that is neither multiple nor sensitive."""
        entry = option()
        self.assertEqual(entry.get("type"), "string")
        self.assertNotIn("multiple", entry)
        self.assertNotIn("sensitive", entry)


if __name__ == "__main__":
    _ = unittest.main()
