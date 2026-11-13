#!/usr/bin/env python3
"""Run release-status: a thin entry script around release.release_tools.status.

Maintainer tooling: run it through `npm run release:notes`, which uses the project's .venv
Python. It puts scripts/ on the import path so the package has one name, release.release_tools.
"""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_ = runpy.run_module("release.release_tools.status", run_name="__main__", alter_sys=True)
