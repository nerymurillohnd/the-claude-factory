#!/usr/bin/env python3
"""agent-context-audit: a read-only audit of what Claude Code and Codex load as context.

Usage:
    agent_context_audit.py [run] [--repo PATH]... [--out DIR] [--mode MODE] [--json]
                           [--exit-zero] [--challenge-rounds N] [--auditor-model M]
                           [--reconciler-model M] [--max-budget-usd X] [--concurrency N]
                           [--offline] [--verify-online] [--online-domain DOMAIN]...
    agent_context_audit.py latest [--repo PATH]... [--json]

Exit codes: 0 complete, 1 complete with findings, 2 partial, 3 failure, 4 preflight or usage.
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
        _ = sys.stdout.write("agent-context-audit: cannot run: Python 3.9 or later is required\n")
        return EXIT_USAGE
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    cli = importlib.import_module("aca.cli")
    entry = cast("object", cli.main)
    if not callable(entry):
        return EXIT_USAGE
    code = entry()
    return code if isinstance(code, int) else EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
