#!/usr/bin/env bash
# Seeds a skill whose description is too vague to trigger, for an authoring trigger case.
set -euo pipefail
mkdir -p "skills/pr-summary"
cat > "skills/pr-summary/SKILL.md" << 'SKILL'
---
name: pr-summary
description: Helps with pull requests.
---

1. Read the diff the user names. No diff: ask for it.
2. Write a three-line summary: what changed, why, and what to test.
3. Reply with the summary and nothing else.
SKILL
