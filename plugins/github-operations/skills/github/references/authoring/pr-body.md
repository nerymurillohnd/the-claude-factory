# PR title, body and labels

Write the title, body and labels of a pull request from the repository's own template, then check them with the script before anyone sees them. Creating the PR is `pr/start.md`; installing templates is `setup/templates.md`.

## 1. Choose the template

1. Look for the repository's templates: `.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE/`, `docs/pull_request_template.md`, `pull_request_template.md` at the root. The repository's template wins.
2. With none, use the plugin's: `<skill-dir>/assets/PULL_REQUEST_TEMPLATE/` (`standard.md`, `bug-fix.md`, `hotfix.md`, `maintenance.md`).
3. Apply the first row that matches. Read the diff, not the branch name.

| Order | Signal | Template |
| :-: | :-- | :-- |
| 1 | Production is broken or degraded now | `hotfix.md` |
| 2 | It corrects behavior that is wrong today | `bug-fix.md` |
| 3 | Only docs, tests, dependencies, CI or content, with no runtime effect | `maintenance.md` |
| 4 | Anything else, or any doubt | `standard.md` |

4. Move a `maintenance` change that touches runtime, data, security or production config up to `standard`.
5. If the linked issue has a form, use the mapping in `authoring/issue.md`.
6. If two templates fit, pick the heavier one.

## 2. Write the body

The API applies no template: GitHub fills it only in the web interface. Always write the body yourself.

1. Read the chosen template.
2. Collect evidence from the session: commands you ran, their output, files changed, decisions made.
3. Fill every section in order. Replace each HTML comment with the answer and delete the comment.
4. Write `N/A: <reason>` for a section that does not apply. Never delete a section.
5. Tick a box only when you did the thing in this session. Leave it unticked otherwise, and say why.
6. Paste real command output in the verification block. Never invent output.
7. Write `Closes #N` only when the PR fully resolves the issue; use `Related #N` otherwise.
8. Set the risk level from the real blast radius and reversibility.
9. Remove secrets, personal data and anything that identifies a customer or another private party.
10. Save the body to a file outside the repository.

For a hotfix, write the rollback first, fill `Follow-up` with a real issue number and a date, and add the repository's hotfix label.

## 3. Write the title

1. Use `type(scope): summary`: imperative, lower case after the colon, no final period, at most 72 characters. Add `!` before the colon for a breaking change.
2. Use the repository's own convention when its history shows a different one.
3. Do not type `(#N)`: GitHub adds it to a squash title.

## 4. Choose the labels

1. List the repository's labels and read the labels on recent merged PRs and `CONTRIBUTING.md` to learn the convention.
2. Apply the repository's labels that fit the change; when it has type labels, apply at least one.
3. When the repository has no labels for this kind of change, propose creating them as `setup/templates.md` says; never create a label without the user's approval.

## 5. Check, fix, check again

1. Run `<skill-dir>/scripts/check-pr-body.py --template <template file> --body <body file> --title "<title>"`.
2. Fix every finding it prints: a missing `## ` heading, an unanswered comment, a title that breaks the format or the length.
3. Run it again until it exits 0.
4. Check by reading what the script cannot: every ticked box has evidence, and the labels fit.
5. Show the user the title, labels and body only after the script passes.
