# Phase 7: Diagnostic & Defect Isolation (Debugging)

Choose the narrowest evidence route for the diagnostic question without altering state or leaking private content.

## Diagnostic Commands

```sh
git grep -n -e '<pattern>' -- <pathspec>
git blame -L <start>,<end> -- <path>
git bisect start <bad> <good>
git bisect log
git bisect reset
```

## Investigation Baseline & Context Capture

Before running diagnostic or isolation commands, establish and record the following baseline:

* Observed symptom vs. expected behavior.
* Exact reproduction command or test case.
* Target paths and current repository status.
* Known-good and known-bad revision endpoints.

## Attribution & Evidence Integrity

* **Tracked Text Search (`git grep`):**
  * Locates tracked text in the current checkout (or a historical revision if specified).
  * *Presence is not causality.* Scope search patterns tightly to prevent secret disclosure in output streams.
* **Line Attribution (`git blame`):**
  * Identifies the last edit that touched a line, not fault, root cause, or author intent.
  * Inspect the cited commit diff, commit message, and full contextual patch before drawing defect conclusions.
* **Regression Isolation (`git bisect`):**
  * Requires reliable, consistently classifiable endpoints and an isolated checkout strategy.
  * Skipped or untestable revisions (`git bisect skip`) may leave a range of candidate commits rather than an exact culprit.
  * Reconcile candidate commits with their full diffs, tests, and observed runtime symptoms before attributing causality.

## Automated Bisect Execution Safety

* **Authorized Execution:** If the user has authorized bisection with explicit endpoints and a safe test command, run the bisection in an isolated clean worktree and always restore the starting state upon completion (`git bisect reset`).
* **Missing Prerequisites:** If endpoints, reproducible commands, or authorizations are absent, report the precise missing choice before altering the checkout.
* **Test Command Audit:** Inspect automated test commands (`git bisect run <cmd>`) prior to execution for mutating side effects (e.g., writing untracked artifacts, modifying files, external network calls). Do not execute arbitrary untrusted historical scripts.

## Diagnostic Reporting & Action Boundary

Conclude diagnostic investigations with a structured finding report covering:

1. **Strongest Evidence:** Specific diff segments, logs, or reproduction outputs.
2. **Exact Revision Range:** Tested endpoints and candidate commit SHAs.
3. **Method & Uncertainty:** Steps taken and any ambiguity (e.g., skipped commits).
4. **State Confirmation:** Verification that the starting checkout/worktree state was fully restored.
5. **Proposed Fix Boundary:** Scope and location for remediation.

*Action Boundary:* Diagnosis and identifying a first-bad commit do not authorize writing fixes, mutating source files, or rewriting history. Implementing a fix requires a separate, dedicated implementation task.
