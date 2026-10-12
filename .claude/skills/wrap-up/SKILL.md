---
name: wrap-up
description: Closes a working session on The Claude Factory — updates the committed project memory in .claude/memory/ (state, environment, learnings, session log), verifies, and commits it. Use when Nery says to wrap up, close or end the session, save context, or remember what we did.
disable-model-invocation: true
---

# Wrap up the session

Memory files: `.claude/memory/project-state.md`, `environment.md`, `learnings.md`, `session-log.md`. Rules for them are in `.claude/CLAUDE.md` → *Project memory*.

## 1. Collect what changed

- `git log --oneline origin/main..HEAD` and `git log --oneline -15` for this session's commits.
- `git status` for uncommitted work — finish it or list it as an open item.
- Review the conversation for decisions, new constraints, access changes and lessons.

## 2. Update memory (edit, don't append blindly)

1. **project-state** — add dated decisions; refresh *Status*; add/close *Open items*; update the plugin backlog.
2. **environment** — only if tools, access, pins or surfaces changed.
3. **learnings** — one imperative line per lesson that cost time; skip anything already in rules, skills or code.
4. **session-log** — new entry at the top: date + title, 3–6 bullets (what changed, commits, verification), and **Next**.
5. Remove lines that are no longer true. Keep each file short.

## 3. Verify and commit

1. Run `npx --yes markdownlint-cli2@0.23.3` (and the full `verify` skill if code changed).
2. Commit: `docs(memory): wrap up <YYYY-MM-DD> session`.
3. Push if the session has push access; otherwise tell Nery the commit is local.

## 4. Report to Nery (Spanish)

Summary of the session, decisions, current state and the proposed next step.
