#!/usr/bin/env python3
"""Run frontmatter-lint: a thin entry script around validators.frontmatter_lint.cli.

Maintainer tooling: run it through `npm run lint:frontmatter`, which runs it with `uv run`.
It puts scripts/ on the import path so the package has one name, validators.frontmatter_lint.
"""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_ = runpy.run_module("validators.frontmatter_lint.cli", run_name="__main__", alter_sys=True)
