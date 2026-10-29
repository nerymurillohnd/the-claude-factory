# Merge and squash messages

Write the message a merge leaves in `git log`. Running the merge is `pr/merge.md`; the repository setting is `setup/templates.md`. GitHub has no repository file for merge messages: this is a convention, in `<skill-dir>/assets/MERGE_TEMPLATE/merge-message.md`.

## 1. Choose the method

| Situation | Method |
| :-- | :-- |
| One logical change, normal PR | Squash |
| Each commit is meaningful, signed and kept on purpose | Merge commit |
| Hotfix | Squash, with the incident link in the body |

Respect the methods the repository allows; `pr/merge.md` has the full rule.

## 2. Write the message

1. Read the convention file.
2. Take the PR title; it already reads `type(scope): summary`. Check it: imperative, lower case, no period, at most 72 characters.
3. Do not type `(#N)`: GitHub adds it to a squash title.
4. Build the body from the PR: keep "What and why" and "Changes".
5. Drop checklists, HTML comments, empty sections, screenshots and reviewer notes.
6. Add one `Closes #N` per resolved issue.
7. Add `BREAKING CHANGE:` only when the PR declares one.
8. Remove emoji, secrets, personal data and customer names.
9. Check the result: a reader of `git log` a year from now understands the decision.
10. Show the user the title and body with the merge summary in `pr/merge.md`.

## 3. Pass it to the merge

- `gh pr merge --subject <title> --body <body>`: `--body` replaces the default message.
- MCP `merge_pull_request`: `commit_message` is appended to the default message. When the repository's default message is the PR body, leave `commit_message` out, or the body appears twice.
- After the merge, read the landed message with `git log -1 --format=%B <merge commit>`.
