#!/usr/bin/env bash
# Seeds a small plugin with one skill, for a packaging and publishing near miss.
set -euo pipefail
mkdir -p .claude-plugin "skills/csv-summary"
printf '{\n  "name": "data-helpers",\n  "version": "0.1.0",\n  "description": "Small helpers for CSV files."\n}\n' > .claude-plugin/plugin.json
cat > "skills/csv-summary/SKILL.md" << 'SKILL'
---
name: csv-summary
description: Summarizes a CSV file in five lines. Use when the user asks what a CSV contains.
---

1. Read the input file the user names. No file: ask for it.
2. Count rows and columns and describe the five most important columns.
3. Reply with the result and nothing else.
SKILL
