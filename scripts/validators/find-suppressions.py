#!/usr/bin/env python3
"""Run find-suppressions: a thin entry script around validators.find_suppressions.cli.

Maintainer tooling: run it through `npm run lint:suppressions`, which uses the project's .venv
Python. It puts scripts/ on the import path so the package has one name,
validators.find_suppressions.
"""

from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_ = runpy.run_module("validators.find_suppressions.cli", run_name="__main__", alter_sys=True)
