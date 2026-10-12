---
paths:
  - ".github/**"
---

# GitHub operations

## Issues

- Every new issue arrives with `status: triage` and a `type:` label from its form.
- Triage within the same working session it's seen: add `plugin: <name>`, a `priority:` label, and move status.
- Status flow: `triage` → `needs-info` | `confirmed` | `duplicate` | `wontfix` | `upstream` → `in-progress` → `released`.
- Close an issue only after the fix is **released**, linking the GitHub Release; or with a clear explanation for duplicate/wontfix/upstream.
- Replies: English, friendly, specific; use `.claude/templates/issue-replies.md`. Never promise dates.
- Security reports in public issues: thank, ask to use private reporting, hide/lock the issue if it discloses an exploit.

## Pull requests

- External PRs are disabled (Collaborators only). Our own PRs use `.github/pull_request_template.md`.
- Commits: Conventional Commits (`feat(plugin-name): …`, `fix(plugin-name): …`, `docs: …`, `ci: …`, `chore(release): …`).

## Workflows

- Pin every action to a full commit SHA with the version in a comment.
- Least-privilege `permissions` per workflow.
- Validate workflow edits with actionlint (CI runs it; locally via `rhysd/actionlint`).
- Tool versions pinned in `validate.yml` `env` are reviewed by `/docs-drift-check`.

## Labels

- Defined in `.github/labels.json`; `plugin: <name>` labels are derived from the catalog.
- Sync after adding a plugin or editing labels: `node .github/scripts/sync-labels.mjs` (needs authenticated `gh`).
