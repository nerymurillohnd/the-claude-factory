# Merge message guide

GitHub has no repository file for merge or squash commit messages. The default comes from a repository setting
(**Settings → General → Pull Requests**), where you pick one built-in format per merge method. This guide explains
the choice, so the default matches how the repository writes its history. The pull request skill and the person
merging can still edit the message at merge time.

## Choose the default message

| Option (squash merge) | What lands in history | Fits when | Watch out |
| :-- | :-- | :-- | :-- |
| Default message | One commit: its own title and message. Several: the PR title and the list of commit messages | Commits are already clean | Work-in-progress commits ("fix typo") land in history |
| Pull request title | The PR title only | Short history, the PR keeps the details | The why lives only on GitHub |
| Pull request title and commit details | The PR title and the list of commit messages | Each commit message explains its part | Same as the default when commits are messy |
| Pull request title and description | The PR title and the whole PR description | The description is short prose | The whole filled template lands in history: headings, checklists, HTML comments and empty sections. Keep the template short, or edit the message at merge time |

For merge commits the choices are the classic `Merge pull request #N from <branch>` title or the PR title, with
the PR title, the PR description or nothing as the message.

## Title

Follow the repository's own convention, read from its recent commit titles:

- **Conventional Commits** (`type(scope): summary`): `type` is one the repository uses, such as `feat`, `fix`,
  `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore` or `revert`; `scope` is the component or package.
- **Plain titles:** an imperative sentence that says what the change does, such as `Reject expired holds before payment`.

In both: 72 characters or fewer, no trailing period, no emoji, no ticket-only titles, no customer names. GitHub
appends ` (#N)` to a squash title; do not write the number yourself.

## Body

```text
<What changed and why, 1-3 short paragraphs. The problem first, then the solution.>

<Optional bullets for the main parts, in the order a reader should follow them.>

Closes #N
BREAKING CHANGE: <what breaks and the migration path>
```

- **Build it from the PR** when you write the message at merge time: take the summary and the changes from the PR
  description. Leave out checklists, HTML comments, empty sections, screenshots and reviewer notes.
- **Footers:** one `Closes #N` per issue; `BREAKING CHANGE:` only when the PR says so and the repository uses it.
- **Explain the why:** a reader of `git log` a year from now should understand the decision without opening the PR.
- Never include secrets, personal data or anything that identifies a customer.

## Which merge method

| Situation | Method |
|---|---|
| Normal PR, one logical change | Squash |
| PR whose commits are each meaningful, kept on purpose | Merge commit |
| Hotfix | Squash, with the incident link in the body |

## Signing

- A squash or merge commit made on github.com is signed by GitHub, not by your own key. A rebase merge on github.com
  adds the commits without signature verification.
- A merge made locally (`git merge --no-ff -S`, then push) is signed by your key. When the repository requires your
  own signature on every commit, merge locally and use the title and body above as the message.
- The REST merge endpoint (`PUT /repos/{owner}/{repo}/pulls/{number}/merge`) takes `commit_title`, `commit_message`,
  `merge_method` and `sha`, so a tool that merges through it can write the message above.

## Examples

```text
fix(checkout): reject expired holds before payment

The hold timer was checked after the payment intent was created, so an expired hold could charge a card
and then fail to reserve stock. The check now runs first and returns a clear error.

Closes #212
```

```text
Update pinned tools from the weekly drift check

Refreshes the pinned versions the drift check flagged. No runtime change.
```
