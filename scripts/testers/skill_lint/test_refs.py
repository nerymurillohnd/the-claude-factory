"""Tests for path resolution and the skill reference graph."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validators.skill_lint.discover import load_skill
from validators.skill_lint.refs import (
    depths,
    escapes,
    imported_or_sourced,
    reference_graph,
    resolve,
)

from testers.skill_lint.helpers import VALID_SKILL_MD, build_skill


class ResolveTest(unittest.TestCase):
    """The three path forms and escapes."""

    def test_resolve_three_forms(self) -> None:
        """Relative, ${CLAUDE_SKILL_DIR} and ${CLAUDE_PLUGIN_ROOT} paths resolve."""
        files = {"SKILL.md": VALID_SKILL_MD, "scripts/run.py": "print(1)\n"}
        with tempfile.TemporaryDirectory() as tmp:
            skill = load_skill(build_skill(Path(tmp), files) / "SKILL.md")
            tokens = (
                "scripts/run.py",
                "${CLAUDE_SKILL_DIR}/scripts/run.py",
                "${CLAUDE_PLUGIN_ROOT}/skills/demo-skill/scripts/run.py",
            )
            found = [resolve(skill, token, "SKILL.md") for token in tokens]
        self.assertEqual(found, ["scripts/run.py"] * 3)

    def test_resolve_from_file_then_root(self) -> None:
        """A path is read from the referring file's folder first, then from the root."""
        files = {"SKILL.md": VALID_SKILL_MD, "references/a.md": "x", "references/b.md": "y"}
        with tempfile.TemporaryDirectory() as tmp:
            skill = load_skill(build_skill(Path(tmp), files) / "SKILL.md")
            self.assertEqual(resolve(skill, "b.md#part", "references/a.md"), "references/b.md")
            self.assertEqual(
                resolve(skill, "references/b.md", "references/a.md"), "references/b.md"
            )
            self.assertIsNone(resolve(skill, "#part", "references/a.md"))
            self.assertIsNone(resolve(skill, "missing.md", "SKILL.md"))

    def test_plugin_root_only_in_plugin(self) -> None:
        """${CLAUDE_PLUGIN_ROOT} resolves nothing outside a plugin."""
        files = {"SKILL.md": VALID_SKILL_MD, "scripts/run.py": "print(1)\n"}
        with tempfile.TemporaryDirectory() as tmp:
            folder = build_skill(Path(tmp), files, layout="project")
            skill = load_skill(folder / "SKILL.md")
            path = "${CLAUDE_PLUGIN_ROOT}/scripts/run.py"
            self.assertIsNone(resolve(skill, path, "SKILL.md"))

    def test_escape_dotdot(self) -> None:
        """Leaving the folder escapes; a nested ../ that stays inside does not."""
        files = {"SKILL.md": VALID_SKILL_MD, "references/a.md": "x", "b.md": "y"}
        with tempfile.TemporaryDirectory() as tmp:
            skill = load_skill(build_skill(Path(tmp), files) / "SKILL.md")
            self.assertTrue(escapes(skill, "../other/x.md", "SKILL.md"))
            self.assertTrue(escapes(skill, "/etc/passwd", "SKILL.md"))
            self.assertTrue(escapes(skill, "${CLAUDE_PLUGIN_ROOT}/x.sh", "SKILL.md"))
            self.assertFalse(escapes(skill, "../b.md", "references/a.md"))
            self.assertFalse(escapes(skill, "b.md", "SKILL.md"))

    def test_escape_symlink(self) -> None:
        """A symlink inside the folder that points outside escapes."""
        with tempfile.TemporaryDirectory() as tmp:
            folder = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD})
            outside = Path(tmp) / "outside.md"
            _ = outside.write_text("x", encoding="utf-8")
            (folder / "link.md").symlink_to(outside)
            skill = load_skill(folder / "SKILL.md")
            self.assertTrue(escapes(skill, "link.md", "SKILL.md"))
            self.assertIsNone(resolve(skill, "link.md", "SKILL.md"))


class GraphTest(unittest.TestCase):
    """References between skill files and their depth."""

    def test_depths_two_levels(self) -> None:
        """SKILL.md is depth 0, a linked file 1, a file linked from it 2."""
        files = {
            "SKILL.md": VALID_SKILL_MD + "\nSee [a](references/a.md).\n",
            "references/a.md": "Then read `references/b.md`.\n",
            "references/b.md": "end\n",
            "assets/orphan.bin": b"\x00\xff",
        }
        with tempfile.TemporaryDirectory() as tmp:
            skill = load_skill(build_skill(Path(tmp), files) / "SKILL.md")
            graph = reference_graph(skill)
        self.assertEqual(graph["SKILL.md"], {"references/a.md"})
        self.assertEqual(graph["assets/orphan.bin"], set())
        self.assertEqual(depths(graph), {"SKILL.md": 0, "references/a.md": 1, "references/b.md": 2})

    def test_python_sibling_import_is_reference(self) -> None:
        """Import x and from x import of a sibling x.py are references."""
        files = {
            "SKILL.md": VALID_SKILL_MD + "\nRun `python3 scripts/main.py`.\n",
            "scripts/main.py": "import helper\nfrom util import f\nimport os\n",
            "scripts/helper.py": "X = 1\n",
            "scripts/util.py": "def f() -> None: ...\n",
            "scripts/broken.py": "def (:\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            skill = load_skill(build_skill(Path(tmp), files) / "SKILL.md")
            graph = reference_graph(skill)
            used = imported_or_sourced(skill)
        self.assertEqual(graph["scripts/main.py"], {"scripts/helper.py", "scripts/util.py"})
        self.assertEqual(used, {"scripts/helper.py", "scripts/util.py"})
        self.assertEqual(graph["scripts/broken.py"], set())

    def test_shell_source_is_reference(self) -> None:
        """Source p and . p are references."""
        files = {
            "SKILL.md": VALID_SKILL_MD,
            "scripts/run.sh": (
                '#!/usr/bin/env bash\nsource ./lib.sh\n. "$(dirname "$0")/lib/more.sh"\n'
            ),
            "scripts/lib.sh": "x=1\n",
            "scripts/lib/more.sh": "y=2\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            skill = load_skill(build_skill(Path(tmp), files) / "SKILL.md")
            graph = reference_graph(skill)
            used = imported_or_sourced(skill)
        self.assertEqual(graph["scripts/run.sh"], {"scripts/lib.sh", "scripts/lib/more.sh"})
        self.assertEqual(used, {"scripts/lib.sh", "scripts/lib/more.sh"})
