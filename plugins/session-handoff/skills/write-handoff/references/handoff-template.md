# Handoff template

Copy the block below. Keep every heading and label **literally, in this order**. Verdict words (`done`,
`partial`, `open`, `dropped`), the word `unverified`, and the fixed lines below stay as written.

Fixed lines: `No previous handoff.` · `Not a git repository.` · `None known.` · `none` · `no upstream` ·
`none (no commits)` · `none (no new commits)` · `not checked (gh failed)` ·
`unverified (git failed: <one-line reason>)` · `No done, partial or dropped items.`

An empty section is one line: `None known.`

For a project verified to be outside git (step 1.2), Branch and HEAD are `Not a git repository.` and the whole
Repository state section is exactly:

```markdown
## Repository state
Not a git repository.
```

When git failed for another reason (step 1.2), Branch, HEAD and every Repository state line are
`unverified (git failed: <one-line reason>)`.

With no previous handoff, Reconciliation of previous handoff is the single line `No previous handoff.`
When no item is `done`, `partial` or `dropped`, the table is replaced by the line
`No done, partial or dropped items.` and the count and Conflicts lines stay. The verdicts and what
each row says are in step 3 of the skill.

Text in `<…>` is replaced; everything outside it is copied as written.

## The handoff

```markdown
# Session handoff

Project: <absolute path of the project directory>
Written: <YYYY-MM-DD HH:MM, the same time as the file name> UTC
Previous handoff: <file name only, e.g. 2026-10-01-1430.md> | No previous handoff.
Branch: <branch> | detached at <short hash> | Not a git repository. | unverified (git failed: <reason>)
HEAD: <full hash> | none | Not a git repository. | unverified (git failed: <reason>)

## Repository state
- Uncommitted: <files and why they are uncommitted, or None known.>
- Stashes: <entries, or None known.>
- Unpushed commits (against the upstream): <count and hashes | unverified (fetch failed) | no upstream>
- Behind upstream: <count | unverified (fetch failed) | no upstream>
- Branch vs default (<default branch name, e.g. main | unknown>): <on default | on another branch | detached | unknown>
- Commits since previous HEAD: <hash and subject per line | none (no new commits) | none (no commits) | the last 20, and why: no previous handoff, its HEAD is none or Not a git repository., its HEAD is invalid or missing, or not an ancestor>
- PRs: <every row of gh pr list --state all --limit 20, with state | none | not checked (gh failed)>

## Reconciliation of previous handoff
| Item | Opened | Verdict | Evidence or note |
|---|---|---|---|
| <item text> | <YYYY-MM-DD> | <done / partial / dropped> | <what step 3 asks for this verdict> |
| <item text> | <YYYY-MM-DD> | done | per the user, <YYYY-MM-DD>: <what they reported> |
Still open, unchanged: <n> (see Open items)
Conflicts (repository wins): <each contradiction between the previous handoff and the repository, or None known.>

## Done this session
- <what changed and why it mattered>: <how, in one clause> (<commit hash / PR #n / test or command result>)

## Decisions
- <decision>: <reason>; <alternative rejected, if any>

## Corrections
- <what the user corrected>: <the behaviour to follow from now on>

## Learnings
- <non-obvious fact about the project, tools or environment> (<source: command output, doc URL, observation>)

## Open items
- [<YYYY-MM-DD opened, the original date for a carried item>] <item>: <where it stands> ; <what finishing needs>
- [<YYYY-MM-DD opened more than 30 days ago>] Stale: confirm or drop. <item>: <where it stands> ; <what finishing needs>

## Next steps
1. <Open item> — <first concrete action>

## Unverified and gaps
- <claim or area>: <why it could not be verified; conversation parts that were compacted>
```

## What a line looks like

| Section | Weak (the next session can't act on it) | Strong |
|---|---|---|
| Done | `a1b2c3d, e4f5a6b` | `Login now rejects expired tokens, which it used to accept: added the expiry check and a test that failed before the fix (e4f5a6b, 48 tests pass)` |
| Decisions | `Redis rejected` | `Sessions stay in the database, not in Redis: one store is enough at the current traffic and avoids running a second service` |
| Corrections | `Keep it simple` | `Reuse the existing HTTP client instead of adding one: the user removed the second client so retries and timeouts live in one place` |
| Open items | `Tests (T-3)` | `[2026-03-02] Test the password-reset email: no test exists yet; needs a fake mail server and two cases, a valid link and an expired one` |

The rows above are invented; copy their shape, not their content.
