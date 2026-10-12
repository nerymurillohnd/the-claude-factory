#!/usr/bin/env bash
# Seeds a small, complete skill with every value defined.
set -euo pipefail
mkdir -p skills/word-count
cat >skills/word-count/SKILL.md <<'SKILL'
---
name: word-count
description: Counts the words in one text file and reports the total. Use when the user asks how many words a file has.
---

# Word count

Input: the path of one text file, from the request. No path: ask for it.

1. Read the whole file.
2. Count the words: runs of characters separated by spaces or line breaks.
3. Reply with one line: `<path>: <n> words`.
SKILL
