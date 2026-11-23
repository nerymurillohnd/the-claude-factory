#!/usr/bin/env python3
"""Tests for the engine's layering: common/ stays below the engine and every check family.

The import graph is read with `ast`, so a forbidden import is caught even in a module no test
imports.
"""

import ast
from pathlib import Path
import unittest

from frontmatter_helpers import SCRIPTS

FORBIDDEN = frozenset({"engine", "frontmatter"})


def top_level_imports(path: Path) -> set[str]:
    """The first segment of every absolute module a file imports."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


class LayeringTest(unittest.TestCase):
    """common/ imports neither the engine nor a family, so families can import it freely."""

    def test_common_imports_no_engine_or_family(self) -> None:
        """No module in common/ imports `engine` or `frontmatter`."""
        offenders = {
            path.relative_to(SCRIPTS).as_posix(): sorted(top_level_imports(path) & FORBIDDEN)
            for path in sorted((SCRIPTS / "common").glob("*.py"))
            if top_level_imports(path) & FORBIDDEN
        }
        self.assertEqual(offenders, {})


if __name__ == "__main__":
    _ = unittest.main()
