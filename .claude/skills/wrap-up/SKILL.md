---
name: wrap-up
description: Closes a working session on The Claude Factory — updates the local project memory in .claude/memory/ and reports the state. Use only when Nery explicitly asks to wrap up, close the session or save what we did.
---

# Wrap up the session

Memory lives in `.claude/memory/`: `MEMORY.md` indexes one topic file per fact. Rules for it are in `.claude/CLAUDE.md` → *Project Memory*.

## 1. Collect what changed

- `git log --oneline origin/main..HEAD` and `git log --oneline -15` for this session's commits.
- `git status` for uncommitted work — commit it, or finish it first.
- Review the conversation for decisions, new constraints, access changes and lessons.

## 2. Update memory (edit, don't append blindly)

1. Add one topic file per new decision, gotcha or open item, and index it in `MEMORY.md`.
2. Update the topic files whose facts changed. Skip anything already in rules, skills or code.
3. Remove lines that are no longer true. Keep each file short.

## 3. Verify

1. Memory is gitignored: do not commit or push it.
2. Run the gates in `.claude/rules/QUALITY_GATE.md` → Before Every Push if code changed.

## 4. Report to Nery (Spanish)

Summary of the session, decisions, current state and the proposed next step.
