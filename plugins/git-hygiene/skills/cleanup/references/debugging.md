# Debugging (only on request or to resolve a finding)

Read this only when the user named a specific problem or an audit finding needs it. Diagnosis never authorizes source changes or history rewrites.

- Find text: `git grep -n -e '<pattern>' -- <pathspec>` searches the current checkout; add a revision (`git grep -n -e '<pattern>' <rev> -- <pathspec>`) for history. A match shows presence, not cause. Scope the search so it cannot print secrets; the guard refuses secret-bearing paths.
- Find who last changed known lines: `git blame -L <start>,<end> -- <path>`, then inspect that commit's diff and context (`git show <sha>`) before attributing a defect.
- Find the commit that introduced a regression with `git bisect` only when you have a known-good and a known-bad revision, a deterministic classifier, and an isolated checkout (a temporary worktree outside the repository). Review the test command for side effects first, keep a log (`git bisect log`), classify each revision good, bad or skip, and always finish with `git bisect reset`. Skipped revisions can leave several candidates, and a candidate is not a proven root cause until it matches the real symptom. `bisect start` and its steps change state: they need the user's approval and will raise a confirmation prompt.
