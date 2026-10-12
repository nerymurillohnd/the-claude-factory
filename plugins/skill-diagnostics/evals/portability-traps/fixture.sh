#!/usr/bin/env bash
# Seeds a skill that works in Claude Code but breaks a claude.ai upload in
# ways that need current platform facts to spot.
set -euo pipefail
d=skills/claude-notes
mkdir -p "$d/scripts"
cat >"$d/SKILL.md" <<'SKILL'
---
name: claude-notes
description: Turns raw meeting notes into action items, tagging each with #owner and #due. Use when the user pastes meeting notes.
when_to_use: When notes mention tasks, owners or deadlines.
allowed-tools: Read
---

1. Run `${CLAUDE_SKILL_DIR}/scripts/extract.py` on the notes the user gives.
2. List every action item the script prints, grouped by owner.
SKILL
cat >"$d/scripts/extract.py" <<'PY'
#!/usr/bin/env python3
"""Print one action item per line from notes on stdin."""
import sys
for line in sys.stdin:
    if line.strip().lower().startswith(("todo", "action")):
        print(line.strip())
PY
chmod 755 "$d/scripts/extract.py"
