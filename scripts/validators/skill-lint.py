#!/usr/bin/env python3
"""Run skill-lint: a thin entry script around skill_lint.cli."""

from __future__ import annotations

import sys

from skill_lint.cli import main

sys.exit(main())
