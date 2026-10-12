---
name: review-staged
description: Reviews the staged changes for bugs and missing tests before a commit. Use when the user asks to review what is staged or to check changes before committing.
allowed-tools: Bash(git diff *)
---

## Staged changes

!`git diff --cached --stat`

!`git diff --cached`

## Instructions

Nothing staged above: say so and stop.

Otherwise review every staged hunk for bugs, missing tests and leftover debug code, and list each problem with its file and line.
