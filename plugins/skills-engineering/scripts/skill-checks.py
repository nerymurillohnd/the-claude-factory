#!/usr/bin/env python3
"""Run the skills-engineering skill checks: a thin entry around engine.cli.

It checks the Python version before importing anything written for 3.12, turns off bytecode so
the installed plugin folder stays clean, and puts its own folder first on the import path, so it
finds its packages from any working directory and under `python3 -I`.

    python3 skill-checks.py run [--family F] [--out DIR] <SKILL.md>
    python3 skill-checks.py check <id> <SKILL.md> [options]
"""

from pathlib import Path
import runpy
import sys

MINIMUM_PYTHON = (3, 12)

if sys.version_info < MINIMUM_PYTHON:
    found = ".".join(str(part) for part in sys.version_info[:3])
    _ = sys.stderr.write(f"skill-checks.py: needs Python 3.12 or later; this is {found}.\n")
    sys.exit(2)

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
_ = runpy.run_module("engine.cli", run_name="__main__", alter_sys=True)
