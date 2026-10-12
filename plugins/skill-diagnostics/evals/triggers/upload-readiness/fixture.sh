#!/usr/bin/env bash
# Seeds a small, plausible skill for a trigger case.
set -euo pipefail
mkdir -p "skills/meeting-notes"
cat > "skills/meeting-notes/SKILL.md" << 'SKILL'
---
name: meeting-notes
description: Turns meeting notes into action items. Use when the user pastes meeting notes.
---

1. Read the input file the user names. No file: ask for it.
2. List each action item with its owner.
3. Reply with the result and nothing else.
SKILL
