#!/usr/bin/env python3
"""Run agent-headings: a thin entry script around validators.agent_headings.cli.

Maintainer tooling: run it through `npm run lint:agents`, which runs it with `uv run`.
It puts scripts/ on the import path so the package has one name, validators.agent_headings.
"""

from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_ = runpy.run_module("validators.agent_headings.cli", run_name="__main__", alter_sys=True)
