---
name: claude-surfaces-merge
description: Evidence behind the Claude Code and Claude surface names — Anthropic merged Cowork and chat into one Claude on 2026-09-16; Claude Code stayed separate; rollout still gradual.
metadata:
  type: reference
---

Anthropic merged Cowork and chat into one Claude on 2026-09-16; Claude Code was not part of the merge. This backs the Target surfaces convention in `.claude/rules/project-conventions.md`.

- Announcement (2026-09-16): "Starting today, Claude Cowork and chat are merging into one Claude." https://claude.com/blog/cowork-is-now-claude
- Help article (read 2026-11-10): the merge "removes the distinction between the two products"; Claude Code stays separate: "The model picker and the "Code" tab are where they were." https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude
- Rollout (as of 2026-11-10): gradual, starting with Pro, Max and Ultra; Team in beta; Enterprise generally available since 2026-10-23. Accounts without the update still show separate "Chat" and "Cowork" options, and incognito chats open the previous experience.
- Docs lag (as of 2026-11-10): https://code.claude.com/docs/en/plugins/components still has the section "Reach users on claude.ai and Cowork", with pre-merge names.

**How to apply:** use **Claude** for the unified chat and Cowork surface and **Claude Code** for the separate product. Recheck the rollout state and the docs before writing compatibility notes, and drop the per-account caveat once the rollout completes.
