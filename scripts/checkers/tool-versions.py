#!/usr/bin/env python3
"""Run tool-versions: a thin entry script around checkers.tool_versions.cli.

Maintainer tooling: run it through `npm run check:tool-versions`, which uses the project's .venv
Python. It puts scripts/ on the import path so the package has one name, checkers.tool_versions.
"""

from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_ = runpy.run_module("checkers.tool_versions.cli", run_name="__main__", alter_sys=True)
