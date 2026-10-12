#!/usr/bin/env bash
# Seeds a folder with two small skills for the several-skills mode.
set -euo pipefail
mkdir -p skills/alpha skills/beta
cat >skills/alpha/SKILL.md <<'SKILL'
---
name: alpha
description: Prints today's date in ISO format. Use when the user asks for today's date.
---

Reply with today's date as YYYY-MM-DD.
SKILL
cat >skills/beta/SKILL.md <<'SKILL'
---
name: beta
description: Renames files. Use when the user asks to rename files.
---

Rename the files to the new pattern.
SKILL
