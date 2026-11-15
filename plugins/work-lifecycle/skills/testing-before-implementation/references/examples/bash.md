# Example: a change to legacy shell code without tests

Judgment to copy: with no tests, a characterization test pins today's behavior first and runs green against the current code; only then is the change made test-first, and code written before its test is set aside on a branch, not deleted. Don't copy the tools, names or numbers.

<example>
<request>
`scripts/rotate-logs.sh` should keep the newest 7 logs instead of 5. There are no tests for it. I already changed the 5 to a 7 on my machine but didn't test anything.
</request>

<result>
Phase 1. The repository runs `shellcheck scripts/*.sh` in CI and has no shell tests. `bats` is listed in `.tool-versions` but unused. Baseline: `shellcheck scripts/*.sh` → no output, exit 0; no test suite to run.

Phase 2. Legacy code without tests: a characterization test first, then the change test-first, with `bats` since the project already pins it. Asked the user before adding the first test file; they agreed.

Phase 4, set aside. The working tree already held the change to 7, written before any test:

`git switch -c wip/rotate-keep-7-before-test && git add scripts/rotate-logs.sh && git commit -m "WIP: keep 7 logs, set aside before its test" && git switch -` → `Switched to branch 'main'`, and `scripts/rotate-logs.sh` is back to 5.

Characterization. `test/rotate-logs.bats` creates 9 dated logs in a temporary directory and asserts that `scripts/rotate-logs.sh "$dir"` leaves the newest 5. `bats test/rotate-logs.bats` → `1 test, 0 failures`. Green against the current code, as a characterization test must be.

Phase 3. Break: fails if the script keeps any count other than 7. A decision the request fixes. Expected by hand: of 9 logs dated the 1st to the 9th, the 3rd to the 9th remain.

Phase 4, red. Updated the characterization assertion from 5 to the 7 named files, as the change requires. `bats test/rotate-logs.bats` → `not ok 1 keeps the newest 7 logs`, `expected 7 files, found 5`.

Phase 5, green. Changed `KEEP=5` to `KEEP=7`. `bats test/rotate-logs.bats` → `1 test, 0 failures`.

Phase 7. `shellcheck scripts/*.sh` → exit 0, as the baseline. Committed as `fix(scripts): keep the newest 7 logs`. The branch `wip/rotate-keep-7-before-test` is left for the user to delete.

## Test-first report

**Baseline:** `shellcheck scripts/*.sh` → clean; no test suite existed

**Tests**
- `keeps the newest 7 logs`: breaks if the script keeps any other count
  - Red: `bats test/rotate-logs.bats` → `expected 7 files, found 5`
  - Green: `bats test/rotate-logs.bats` → `1 test, 0 failures`

**Final check against baseline**
- New failures: none
- Pre-existing failures: none

**Mutation check:** not run; not high-stakes

**Risks left without a test:** behavior when the directory holds non-log files; today's script deletes them too, which the characterization test now makes visible for the user to decide
</result>
</example>

## Why each step did what it did

- The user's early edit was set aside on a local branch, so nothing was lost and the test was written against the old behavior first.
- The characterization test was green before the change; its one assertion changed as part of the change, and the report says so.
- Adding the first test file was a new setup, so the user was asked before it.
