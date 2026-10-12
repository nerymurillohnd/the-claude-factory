#!/usr/bin/env bash
# Seeds a small, plausible skill for a trigger case.
set -euo pipefail
mkdir -p "skills/report-builder"
cat >"skills/report-builder/SKILL.md" <<'SKILL'
---
name: report-builder
description: Builds a weekly status report from a task list. Use when the user asks for a status report.
---

1. Read the input file the user names. No file: ask for it.
2. Group the tasks by status and write one sentence per group.
3. Reply with the result and nothing else.
SKILL
