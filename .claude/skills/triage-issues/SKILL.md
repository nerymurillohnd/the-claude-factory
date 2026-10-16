---
name: triage-issues
description: Triages open GitHub issues of The Claude Factory — reproduces, labels, prioritizes and drafts replies from the saved templates; posts only after Nery approves. Use only when Nery explicitly asks to review, triage or answer issues.
argument-hint: "[issue-number|all]"
allowed-tools:
  - "Bash(gh issue list*)"
  - "Bash(gh issue view*)"
  - "Bash(gh label list*)"
---

# Triage issues

Scope: `$ARGUMENTS` (default: all issues labeled `status: triage` or `status: needs-info`).
Replies: `.claude/templates/issue-replies.md`.

## 1. Collect

```bash
gh issue list --repo nerymurillohnd/the-claude-factory --state open --label "status: triage" --json number,title,labels,createdAt,author
gh issue list --repo nerymurillohnd/the-claude-factory --state open --label "status: needs-info" --json number,title,labels,createdAt,author
gh issue view <n> --repo nerymurillohnd/the-claude-factory --comments
```

## 2. Classify each issue

1. **Plugin** — which one? Add `plugin: <name>`.
2. **Valid?** Check against the plugin README, current code and official docs. Try to reproduce in an isolated install (`/test-installed-plugin`).
3. **Outcome** — one of:
   - `status: confirmed` + `priority:` (high = core broken for many; medium = workaround exists; low = nice to have)
   - `status: needs-info` — list exactly what's missing
   - `status: duplicate` — link the original
   - `status: upstream` — Claude Code or third-party cause; link where to report
   - `status: wontfix` — out of scope or working as intended; explain why
4. **Security** disclosed publicly → follow the security reply, hide details, move to a private advisory.

## 3. Reply

- Draft each reply from the templates, personalized and specific. Show Nery the plan (table: issue · labels · outcome · reply) and wait for approval before posting.
- Post only after approval:

  ```bash
  gh issue edit <n> --add-label "<labels>" --remove-label "<the status label the issue had>"
  gh issue comment <n> --body-file <reply.md>
  ```

## 4. Plan the work

For confirmed issues, propose the fix and release level. Fixes ship in a plugin PR with a version bump; an issue closes once its release tag exists.
