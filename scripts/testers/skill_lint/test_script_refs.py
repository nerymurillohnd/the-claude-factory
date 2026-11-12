"""Tests for what a skill's scripts load: shell source lines and the shell check."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validators.skill_lint.discover import load_skill
from validators.skill_lint.refs import imported_or_sourced, reference_graph
from validators.skill_lint.script_refs import is_shell, sourced_paths

from testers.skill_lint.helpers import VALID_SKILL_MD, build_skill


class SourcedPathsTest(unittest.TestCase):
    """Only source and . in command position load a file."""

    def test_dot_argument_is_not_source(self) -> None:
        """A . that is an argument of another command sources nothing."""
        text = "find . -name x\ngit add . lib.sh\ncp a . && echo .\n"
        self.assertEqual(sourced_paths(text), [])

    def test_command_positions(self) -> None:
        """Line start, separators and then/do/else introduce a source command."""
        text = (
            ". ./a.sh\n"
            "x && source b.sh\n"
            "y || . c.sh\n"
            "z; source d.sh\n"
            "if true; then . e.sh; fi\n"
            "for i in 1; do source f.sh; done\n"
            "{ . g.sh; }\n"
            "  source h.sh\n"
        )
        expected = ["./a.sh", "b.sh", "c.sh", "d.sh", "e.sh", "f.sh", "g.sh", "h.sh"]
        self.assertEqual(sourced_paths(text), expected)


class SourceBaseTest(unittest.TestCase):
    """A sourced path resolves from the script's folder, then from the skill root."""

    def test_root_relative_source(self) -> None:
        """Source scripts/lib.sh from scripts/run.sh reaches scripts/lib.sh."""
        files = {
            "SKILL.md": VALID_SKILL_MD + "\nRun `bash scripts/run.sh`.\n",
            "scripts/run.sh": "#!/usr/bin/env bash\nsource scripts/lib.sh\n",
            "scripts/lib.sh": "x=1\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            skill = load_skill(build_skill(Path(tmp), files) / "SKILL.md")
            graph = reference_graph(skill)
            used = imported_or_sourced(skill)
        self.assertEqual(graph["scripts/run.sh"], {"scripts/lib.sh"})
        self.assertEqual(used, {"scripts/lib.sh"})


class IsShellTest(unittest.TestCase):
    """A shell script is known by its extension or its shebang interpreter."""

    def test_shell_shebangs(self) -> None:
        """Sh, bash, zsh, dash and ksh shebangs, direct or through env, are shell."""
        for first in (
            "#!/bin/sh",
            "#!/bin/bash",
            "#!/usr/bin/env bash",
            "#!/usr/bin/env -S bash -e",
            "#!/usr/bin/env zsh",
            "#!/bin/dash",
            "#!/bin/ksh",
        ):
            with self.subTest(first=first):
                self.assertTrue(is_shell("run", f"{first}\necho\n"))

    def test_other_shebangs(self) -> None:
        """Fish, python and node shebangs are not shell, though some names hold sh."""
        for first in ("#!/usr/bin/env fish", "#!/usr/bin/fish", "#!/usr/bin/env python3"):
            with self.subTest(first=first):
                self.assertFalse(is_shell("run", f"{first}\necho\n"))

    def test_extension(self) -> None:
        """A .sh, .bash or .zsh file is shell without a shebang."""
        self.assertTrue(is_shell("scripts/a.sh", "echo\n"))
        self.assertFalse(is_shell("scripts/a.fish", "echo\n"))


if __name__ == "__main__":
    _ = unittest.main()
