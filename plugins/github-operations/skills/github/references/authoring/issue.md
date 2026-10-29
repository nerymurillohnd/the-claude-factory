# Issues: write, triage, mark duplicates

Contents: 1. Choose the form · 2. Write and open an issue · 3. Triage · 4. Mark a duplicate · 5. Limits

Write issues in the layout of the repository's forms, triage them, and mark duplicates. Installing forms and labels is `setup/templates.md`.

## 1. Choose the form

Use the repository's forms in `.github/ISSUE_TEMPLATE/`; with none, the plugin's in `<skill-dir>/assets/ISSUE_TEMPLATE/`.

| Signal | Form | Matching PR template |
| :-- | :-- | :-- |
| Something breaks or differs from the docs | `bug_report` | `bug-fix` |
| Production is broken now | `incident` | `hotfix` |
| Improve something that exists | `feature_request` | `standard` |
| Propose something brand new | `idea` | `standard` |
| Planned upkeep, debt, no user-facing defect | `maintenance` | `maintenance` |
| A doc is wrong, unclear or missing | `docs_issue` | `maintenance` |
| "How do I…?" | `question` | none |

## 2. Write and open an issue

The API applies no form: an issue opened through the MCP or `gh` skips it. Set the title prefix, the labels and the body yourself.

1. Pick the form from the table.
2. Copy the form's `title` prefix and fill its placeholder.
3. Build the body from the form fields, in order: one `### <field label>` heading per field, a blank line, then the answer. This is the layout GitHub writes for a submitted form.
4. Answer every required field, even in a private repository where GitHub does not enforce `required`. Write `N/A` where a field offers it. Never invent a version, a log or a reproduction.
5. Add the labels in the form's `labels:`, and a component or priority label when the report gives the evidence.
6. Remove secrets, personal data and anything that identifies a customer or another private party.
7. Show the user the title, labels and body. Create the issue only after approval.
8. Create it with MCP `issue_write` (`method: create`; `type` only when `list_issue_types` shows the repository has issue types), or `gh issue create --body-file <file>`.
9. Read the issue back. GitHub drops labels silently when the token lacks push access: add missing ones with a second call and tell the user.
10. Report the issue number and URL.

## 3. Triage

1. Read the issue and its labels.
2. Replace the triage status label with the repository's label for needs-info, confirmed, duplicate, wontfix or upstream.
3. Map the impact answer to a priority label: cosmetic is low, a workaround is medium, blocked, data loss or outage is high.
4. Ask for missing facts in one short comment. Never close an issue silently.

## 4. Mark a duplicate

A comment containing `Duplicate of #N` makes GitHub mark the duplicate, for issues and pull requests, and the timeline event appears only when the commenter has write access.

1. Suggest first: write "possible duplicate of #N" and give the reporter a way to object. Never write `Duplicate of #N` for a guess: it creates a real event.
2. After the user or a maintainer confirms, read both issues, prefer an open target, and post a comment with `Duplicate of #N`.
3. Add the repository's duplicate label.
4. Close it with MCP `issue_write` (`method: update`, `state: closed`, `state_reason: duplicate`, `duplicate_of: <N>`), or `gh issue close <number> --reason duplicate --duplicate-of <N>` after checking `gh issue close --help` lists those options.
5. To undo a mark, tell the user to use **Undo** in the issue timeline: no API removes it.

## 5. Limits

- Forms are read from the default branch only.
- `required: true` is enforced only in public repositories.
- The GraphQL field `issueTemplates` does not list YAML forms: never use it to verify forms.
- `isBlankIssuesEnabled` describes the viewer: an admin sees `true` even when `config.yml` disables blank issues.
- A form's `type:` key needs issue types defined at organization level.
