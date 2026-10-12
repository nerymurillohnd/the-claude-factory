#!/usr/bin/env bash
# Seeds a Claude Code skill that is valid under the current skills reference
# (https://code.claude.com/docs/en/skills, Frontmatter reference), using fields
# and syntax that older or generic Agent Skills knowledge calls errors.
set -euo pipefail
d=skills/doc-digest
mkdir -p "$d"
cat >"$d/SKILL.md" <<'SKILL'
---
description: Writes a dated five-bullet digest of one Markdown document. Use when the user asks for a digest, recap or TL;DR of a .md file.
when_to_use: Requests like "digest docs/plan.md" or "TL;DR of README.md".
argument-hint: "[file.md]"
arguments: file
allowed-tools: Bash(date +%F) Bash(wc -w *)
effort: low
---

# Document digest

Today: !`date +%F`

1. No file in the request: ask which Markdown file to digest, and stop.
2. Read `$file` in full.
3. Run `wc -w "$file"` for the word count.
4. Reply with the heading `Digest of $file (<today>, <n> words)`, then five bullets: the purpose, the three most important points, and any open question. Keep each bullet under 25 words.
SKILL
