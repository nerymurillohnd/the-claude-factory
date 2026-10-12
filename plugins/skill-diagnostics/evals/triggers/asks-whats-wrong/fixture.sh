#!/usr/bin/env bash
# Seeds a small, plausible skill for a trigger case.
set -euo pipefail
mkdir -p "skills/notes-cleanup"
cat >"skills/notes-cleanup/SKILL.md" <<'SKILL'
---
name: notes-cleanup
description: Cleans up raw meeting notes into tidy bullet points. Use when the user pastes meeting notes.
---

1. Read the input file the user names. No file: ask for it.
2. Rewrite the notes as short bullet points grouped by topic.
3. Reply with the result and nothing else.
SKILL
