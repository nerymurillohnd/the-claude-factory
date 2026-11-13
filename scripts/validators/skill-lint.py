#!/usr/bin/env python3
"""Run skill-lint: a thin entry script around validators.skill_lint.cli.

Maintainer tooling: run it through `npm run lint:skills`, which uses the project's .venv
Python. It puts scripts/ on the import path so the package has one name, validators.skill_lint.
"""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_ = runpy.run_module("validators.skill_lint.cli", run_name="__main__", alter_sys=True)
