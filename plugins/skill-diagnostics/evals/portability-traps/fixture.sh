#!/usr/bin/env bash
# Seeds a skill that works in Claude Code but breaks once uploaded to claude.ai
# and used in Cowork, in ways that need current platform facts to spot
# (https://code.claude.com/docs/en/skills: Using skill frontmatter outside
# Claude Code; How Claude Code handles the body of a synced skill).
set -euo pipefail
d=skills/claude-notes
mkdir -p "$d"
cat >"$d/SKILL.md" <<'SKILL'
---
name: claude-notes
description: Turns raw meeting notes into action items, tagging each with #owner and #due. Use when the user pastes meeting notes.
when_to_use: When notes mention tasks, owners or deadlines.
allowed-tools: Read
---

Today: !`date +%F`

1. Find every task in the notes the user gives.
2. Give each task an owner from the notes, and a due date counted from today's date above (default: one week).
3. List the tasks grouped by owner, each as `- [ ] <task> #owner <name> #due <YYYY-MM-DD>`.
SKILL
