#!/usr/bin/env python3
"""The SessionEnd hook: remove this session's skill-checks results; a thin entry.

It runs at the end of every session, so it never speaks and never fails: below Python 3.12 it
exits 0 at once, and engine.session_end exits 0 whatever it finds. It turns off bytecode so the
installed plugin folder stays clean, and puts its own folder first on the import path.

    python3 session-end.py < <SessionEnd hook input JSON>
"""

from pathlib import Path
import runpy
import sys

MINIMUM_PYTHON = (3, 12)

if sys.version_info < MINIMUM_PYTHON:
    sys.exit(0)

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
_ = runpy.run_module("engine.session_end", run_name="__main__", alter_sys=True)
