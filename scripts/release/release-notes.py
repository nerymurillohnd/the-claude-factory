#!/usr/bin/env python3
"""Run release-notes: a thin entry script around release.release_tools.notes.

Maintainer tooling: run it through `npm run release:notes`, which uses the project's .venv
Python. It puts scripts/ on the import path so the package has one name, release.release_tools.
"""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_ = runpy.run_module("release.release_tools.notes", run_name="__main__", alter_sys=True)
