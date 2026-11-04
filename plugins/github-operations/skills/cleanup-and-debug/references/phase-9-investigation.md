# Phase 9: Investigation

Diagnose the approved recommendations that need debugging. This phase changes no source, but it registers a throwaway worktree in `.git/worktrees/` and leaves bisect state in it, so it runs only for approved recommendations and ends by removing both.

## Isolation

- Create a throwaway worktree outside the repository with `git worktree add --detach <path> <commit>` ([git-worktree][git-worktree]).
- Never bisect or reproduce in the main checkout. Bisect refs (`refs/bisect`) belong to the worktree that created them ([git-worktree][git-worktree]).

## Reproduce

- Reproduce the problem in the throwaway worktree before diagnosing it.
- Read every test or script before it runs: it executes code from each checked-out revision. It must not write outside the worktree, use credentials, deploy or delete.

## Bisect

- The test exits 0 for good, 1 to 127 except 125 for bad, and 125 to skip a revision that cannot be tested; any other code aborts ([git-bisect][git-bisect]).
- Use `git bisect start --first-parent` when the history is merge-based and branches had broken intermediate commits ([git-bisect][git-bisect]).
- A skipped commit next to the culprit leaves a range, not a single commit. Report it as a range.
- The first bad commit is where the test flips, not always the cause. Confirm it with `git show --stat`.

## Blame

- Plain `git blame` gives a line's last change.
- `git blame -w -M -C` follows whitespace-only changes and lines moved or copied across files, to find where a line really came from ([git-blame][git-blame]).
- A `^` before a commit marks a boundary commit ([git-blame][git-blame]).

## Clean up

- End every bisect with `git bisect reset` ([git-bisect][git-bisect]).
- Remove the throwaway worktree with `git worktree remove <path>`.

## Done when

- [ ] Every investigated recommendation has a finding with its cause, or a range and why it could not be narrowed.
- [ ] Every test was read before it ran.
- [ ] No `refs/bisect/*` or `BISECT_*` file remains.
- [ ] `git worktree list` no longer shows the throwaway worktree.

## Sources

Checked on 2026-11-04.

- [git-bisect][git-bisect]: exit "code between 1 and 127 (inclusive), except 125" is bad; "125 … the current revision will be skipped"; "Any other exit code will abort the bisect process"; `--first-parent` "Follow only the first parent commit upon seeing a merge commit"; `reset` cleans up "the bisection state and return to the original HEAD".
- [git-worktree][git-worktree]: `--detach` detaches HEAD in the new worktree; "refs inside refs/bisect, refs/worktree and refs/rewritten are not shared".
- [git-blame][git-blame]: `-w` "Ignore whitespace"; `-M` "Detect moved or copied lines within a file"; `-C` also detects "lines moved or copied from other files"; "commits marked with caret (boundary)".

[git-bisect]: https://git-scm.com/docs/git-bisect
[git-worktree]: https://git-scm.com/docs/git-worktree
[git-blame]: https://git-scm.com/docs/git-blame
