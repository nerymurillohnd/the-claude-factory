# Merge message convention

GitHub has no repository file for merge or squash commit messages. The default comes from
**Settings → Pull requests → Allow squash merging** (and the equivalent for merge commits), where you pick one
built-in format. This file is the convention the PR skill follows to write the message, and the setting to
make GitHub's own default match it.

## Setting to configure once per repository

- **Squash merging → default commit message: "Pull request title and description."** The squash commit then carries
  what the skill already wrote in the PR, instead of a list of work-in-progress commits.

## Title

`type(scope): summary`

- **type:** `feat` · `fix` · `refactor` · `perf` · `docs` · `test` · `build` · `ci` · `chore` · `revert`
- **scope:** the component, plugin, package or area; omit it only when the change is repository-wide.
- **summary:** imperative mood, lower case, no trailing period; the whole title is 72 characters or fewer.
- GitHub appends ` (#N)` to a squash title; do not write the number yourself.
- No emoji, no ticket-only titles, no customer names.

## Body

```text
<What changed and why, 1-3 short paragraphs. The problem first, then the solution.>

<Optional bullets for the main parts, in the order a reader should follow them.>

Closes #N
BREAKING CHANGE: <what breaks and the migration path>
```

- **Build it from the PR:** take "What and why" and "Changes" from the PR body. Leave out checklists, HTML comments,
  empty sections, screenshots and reviewer notes.
- **Footers:** one `Closes #N` per issue; `BREAKING CHANGE:` only when the PR says so; nothing else.
- **Explain the why:** a reader of `git log` a year from now should understand the decision without opening the PR.
- Never include secrets, personal data or anything that identifies a customer.

## Which merge method

| Situation | Method |
|---|---|
| Normal PR, one logical change | Squash |
| PR whose commits are each meaningful and signed, kept on purpose | Merge commit |
| Hotfix | Squash, with the incident link in the body |

## Signing

- A merge or squash made on github.com is signed by GitHub, not by your own key.
- A merge made locally (`git merge --no-ff -S`, then push) is signed by your key. When the repository requires your own
  signature on every commit, merge locally and use the title and body above as the message.
- Whether the REST merge endpoint used by the GitHub MCP server accepts a custom commit title and message is unverified;
  check its documentation before relying on it.

## Examples

```text
fix(checkout): reject expired holds before payment

The hold timer was checked after the payment intent was created, so an expired hold could charge a card
and then fail to reserve stock. The check now runs first and returns a clear error.

Closes #212
```

```text
chore(deps): update pinned tools from the 2026-10-14 drift check

Refreshes the pinned versions flagged by the weekly drift check. No runtime change.
```
