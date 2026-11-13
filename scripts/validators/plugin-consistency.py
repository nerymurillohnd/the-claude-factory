#!/usr/bin/env python3
"""Run plugin-consistency: a thin entry script around validators.plugin_consistency.cli.

Maintainer tooling: run it through `npm run check:consistency`, which uses the project's .venv
Python. It puts scripts/ on the import path so the package has one name,
validators.plugin_consistency.
"""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_ = runpy.run_module("validators.plugin_consistency.cli", run_name="__main__", alter_sys=True)
