# Validation and results report, steps 7 and 8

Validation is a fresh, read-only proof that the approved actions did what the plan said. It does not trust the execution log: it re-reads the repository, the remote and GitHub.

## Step 7: validate

1. **Re-run the checks.** For every action marked `done` in `plan.md`, run its validation criterion again, now, and paste the raw output into `validation.md` in the backup folder. An action whose criterion does not hold is reported as `failed`, whatever the log says. An action marked `failed` or `skipped` stays that way, with its reason.
2. **Re-run the relevant audit sections** read-only and compare with the audit's output in the scratch folder: branches and states (`intake-local.md` 1.3–1.4), worktrees, stashes, working tree, residue, `git ls-remote` against tracking refs, and, for GitHub actions, the pull request, issue, workflow and artifact listings. Write the before/after counts side by side.
3. **Confirm nothing outside the plan changed.** Every ref that is not in the approved actions has the same SHA as in the audit (`git for-each-ref --format='%(refname) %(objectname)'` diffed against the audit's `refs.tsv`; differences must be explained by an action). `git status --porcelain` in the repository and in each worktree is what it was. The rescue refs are gone: `git for-each-ref refs/repo-cleanup-backup` prints nothing.
4. **Confirm the backup still opens**: `git bundle verify "<dir>/all.bundle"` and the checksum file matches (`sha256sum -c`, or `shasum -a 256 -c`).
5. **Integrity.** `git fsck --connectivity-only --no-progress`; after a `maintenance` action also `git count-objects -vH`. Anything reported is a finding, not a footnote.
6. **Anything new the cleanup revealed** (a failing check after a merge, a branch that could not be deleted, a protection that blocked a push) goes in the report as an open item with a recommendation, not as a silent extra action.

## Step 8: results report

Write `results.md` in the backup folder and present it to the user. Use plain language first, evidence second.

```markdown
## Cleanup results: <repo> (<date>)

**Outcome.** [Two to four sentences: what changed, what did not, and whether the repository is now in the state the plan promised.]

### Actions
| ID | Action | Status | Proof |
| :-- | :-- | :-- | :-- |
| A-01 | Backup | done | `bundle verify` ok, checksum `<sha256>`, restore test identical |
| A-02 | Delete local branch `x` | done | `git rev-parse --verify -q refs/heads/x` printed nothing |
| A-05 | Delete remote branch `y` | skipped | live SHA differed from the audited one; left untouched |

### Before and after
| Measure | Before | After |
| :-- | --: | --: |
| Local branches | 31 | 9 |
| Remote branches | 24 | 8 |
| Worktrees | 4 | 1 |
| Stashes | 6 | 0 |
| Open pull requests | 7 | 7 |

### Not done, and why
- <action or finding> — <reason> — <what the user can do>

### Open items
- <new finding from validation> — <recommendation>

### Recovery
Backup: `<dir>` (bundle, patches, archives, `manifest.txt`, `plan.md`). Restore commands are in `manifest.txt`.
Rescue branches kept: <list>.
```

Every number in the report comes from a command run in this step, quoted in `validation.md`. Do not report "cleaned" for anything the criteria did not prove.

## Closing

- **The backup folder.** Ask with `AskUserQuestion` whether to keep it. Recommend keeping it for at least the period the repository's reflog and `gc.pruneExpire` would have kept the data (weeks), and for as long as a `history-rewrite` or `maintenance` action ran. Delete it only on an explicit yes, and say what is lost. `restore-test.git` inside it can go once the user confirms the backup; it is rebuilt from the bundle.
- **The scratch folder** holds only audit output and temporary objects. Remove it at the end (`rm -rf` on the exact path you created, after checking it is that path and not the repository, the backup folder or the home folder). If it is the session scratchpad, leave it.
- **Nothing was installed and no configuration changed.** If any command left something behind (a worktree, a lock file, a stash), list it in the report rather than hiding it.
- **Commits and pull requests.** If any action produced commits or a branch, say whether they are pushed, signed, and which pull request they belong to. Do not push or open a pull request here that the approved plan did not include.

End with the short summary the user asked for: decisions taken, current state, and the next step.
