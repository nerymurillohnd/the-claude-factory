#!/usr/bin/env bash
# Seeds a small, plausible skill for a trigger case.
set -euo pipefail
mkdir -p "skills/csv-summary"
cat >"skills/csv-summary/SKILL.md" <<'SKILL'
---
name: csv-summary
description: Summarizes a CSV file in five lines. Use when the user asks what a CSV contains.
---

1. Read the input file the user names. No file: ask for it.
2. Count rows and columns and describe the five most important columns.
3. Reply with the result and nothing else.
SKILL
mkdir -p .claude-plugin
printf '{\n  "name": "data-helpers",\n  "version": "0.1.0",\n  "description": "Small helpers for CSV files."\n}\n' >.claude-plugin/plugin.json
