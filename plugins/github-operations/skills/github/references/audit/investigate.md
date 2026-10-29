# Investigation and fixes the audit calls for

Read this when the audit found something that needs diagnosis or repair: a regression, a failing check, a refactor, dead code, a flaky or skipped test, a broken workflow. The audit only lists them. This reference says how they enter the report, the plan and the execution, and how to work without disturbing the repository.

## In the report and the plan

- A finding that needs diagnosis becomes a recommendation of kind **investigate**; one that needs a change becomes **fix**. Each states the symptom, the evidence and the expected outcome (a diagnosis written in `findings`, or a pull request).
- In the plan they are the `investigate` and `fix` classes. An `investigate` action changes no source and leaves the repository exactly as it found it. A `fix` action never commits to the base branch: it lands through a branch and a pull request, with the repository's own gates passing, and only if the user authorized the pull request.
- Ask for the information that decides the work (which check defines "good", which command reproduces the failure) at Gate 1, not during execution.

## Working area

Never investigate in the user's checkout. Use a throwaway worktree outside the repository, in the scratch folder or the backup folder:

```sh
git -C "<repo>" worktree add --detach "<scratch>/wt-investigate" <commit>      # detached: no branch is created
# ... work in <scratch>/wt-investigate ...
git -C "<repo>" worktree remove --force "<scratch>/wt-investigate"              # the one place --force is allowed: the worktree is a disposable copy
git -C "<repo>" worktree prune
```

Afterwards confirm that `git -C "<repo>" worktree list` and `git -C "<repo>" status --porcelain` are as before.

## Finding things

- **Where did this text or behavior come from?** `git log -S'<text>' --exclude=refs/stash --all --oneline` (changes in the number of occurrences) and `git log -G'<regex>' ...` (changes whose diff matches). `git log --follow -- <path>` follows renames.
- **Who changed this line, and when?** `git blame -w -M -C --date=short -L <start>,<end> -- <path>`: `-w` ignores whitespace, `-M` and `-C` follow lines moved inside a file and copied from other files.
- **What did this file look like then?** `git show <sha>:<path>`.
- **Where else is this symbol used?** `git grep -n '<symbol>'`; across history, `git grep -n '<symbol>' <sha>`.

## Bisect: finding the commit that broke something

Use a bisect only when there is a reliable test that tells good from bad.

1. **Agree on the test.** It is a command that exits 0 for good and 1–127 (except 125) for bad, and 125 for "cannot test this commit" (for example it does not build). Read the test before running it: it must not write outside the throwaway worktree, call the network with credentials, deploy, or delete anything. If the repository's test suite is the test, run only the single failing case.
2. **Prove the endpoints.** Run the test on the known-bad commit and on the known-good one, in the throwaway worktree. If the results are not bad and good, stop: the test is unreliable and a bisect would mislead.
3. **Run it** in the throwaway worktree:

   ```sh
   cd "<scratch>/wt-investigate"
   git bisect start <bad> <good>
   git bisect run <test command>
   git bisect log > "<scratch>/bisect.log"
   git bisect reset
   ```

   `git bisect run` writes the first bad commit to its output. Read it, then show the commit (`git show --stat <sha>`) and confirm the reasoning: a bisect finds the first commit where the test flips, which is not always the cause (a flaky test, a skipped commit with 125, a merge commit).
4. **Clean up.** `git bisect reset`, then remove the worktree as above. Bisect state lives in the worktree's own directory, so the user's checkout is untouched; confirm that `git -C "<repo>" bisect log` answers "We are not bisecting".

## Fixes

1. Start from the published base in a new branch in a separate worktree: `git -C "<repo>" worktree add -b fix/<topic> "<scratch>/wt-fix" <remote>/<base>`.
2. Make the smallest change that fixes the finding; keep each topic in its own commit with a message that says what changed and why. Commit with the user's signing configuration (`integrate.md`, "Signing").
3. Run the repository's own checks (tests, lint, type check, build) and record the raw output. A fix without a passing check is reported as unverified.
4. Push the branch (plain `git push -u <remote> fix/<topic>`) and open a pull request only if the user authorized it, with the repository's labels. Continue with the PR lifecycle in `pr/lifecycle.md`, so reviews and checks are resolved before anything merges.
5. Remove the worktree when the pull request exists. The branch stays until the pull request is merged or closed.

## What to write back

Each investigation ends with a short entry in `findings.md`: the question, the commands run, the raw output that answers it, the conclusion, and what remains unknown. A bisect also keeps `bisect.log` in the scratch folder.
