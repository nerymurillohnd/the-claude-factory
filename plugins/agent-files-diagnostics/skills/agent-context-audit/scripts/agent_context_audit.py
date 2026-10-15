#!/usr/bin/env python3
"""agent-context-audit: the deterministic stages of a read-only audit of agent instruction files.

Usage:
    agent_context_audit.py prepare [--repo PATH] [--out DIR] [--offline] [--challenge-rounds N]
    agent_context_audit.py accept --run DIR --stage domains|review --workflow-run ID
    agent_context_audit.py finalize --run DIR [--checked FILE]
    agent_context_audit.py latest [--repo PATH] [--out DIR]

Each stage prints one JSON object and exits 0; a usage error exits 4.
Requires Python 3.9+ (standard library only) and the claude CLI 2.1.300+ signed in.
"""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
from typing import cast

MIN_PYTHON = (3, 9)
EXIT_USAGE = 4


def main() -> int:
    """Load the runner package next to this file and hand over the command line."""
    if sys.version_info < MIN_PYTHON:
        _ = sys.stdout.write(
            '{"status": "cannot-run", "reason": "Python 3.9 or later is required"}\n'
        )
        return 0
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    cli = importlib.import_module("aca.cli")
    entry = cast("object", cli.main)
    if not callable(entry):
        return EXIT_USAGE
    code = entry()
    return code if isinstance(code, int) else EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
