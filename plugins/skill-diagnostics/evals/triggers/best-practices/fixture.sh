#!/usr/bin/env bash
# Seeds a small, plausible skill for a trigger case.
set -euo pipefail
mkdir -p "skills/changelog-writer"
cat >"skills/changelog-writer/SKILL.md" <<'SKILL'
---
name: changelog-writer
description: Writes a changelog entry from a list of changes. Use when the user asks for release notes or a changelog.
---

1. Read the input file the user names. No file: ask for it.
2. Sort the changes into Added, Changed and Fixed.
3. Reply with the result and nothing else.
SKILL
