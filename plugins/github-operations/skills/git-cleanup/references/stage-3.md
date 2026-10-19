# Stage 3: Approved Execution, Re-Validation & Post-Verification (Cleanup Starts Here)

* **Trigger Condition:** Executed **only** after the user explicitly authorizes specific recommendation IDs (R1, R2, …). Any omitted or rejected ID remains completely untouched.
* **Command Suites:** Read `phase-5.md` before you delete a branch and `phase-6.md` before any integration.
* **Pre-Flight Inventory Check:**
  * Immediately before executing each approved recommendation, re-run the specific read-only verification command for that item (e.g., re-check `git merge-base` or re-verify worktree lock state).
  * **State Drift Abort:** If the target ref, working tree state, or scope has changed since the Stage 2 audit, **halt immediately**, do not execute that command, and report the drift to the user.
* **Execution Sequence:**
  1. **Rollback Points:** Create lightweight backup references (`refs/backup/<date>-<target>` or `git branch backup/<date>-<name> <oid>`) prior to any ref removal.
  2. **Execute Ordered Approved Mutations:** Execute only authorized commands in dependency order (e.g., worktree metadata prune → local branch removal with `-d` → explicit path cleaning).
  3. **Re-Enumeration & Integrity Check:** Re-run verification commands to confirm repository state, check reflogs, and verify working directory cleanliness.
  4. **Post-Execution Audit Report:** Emit a concluding report detailing:
     * Specific executed IDs and corresponding commands.
     * User-visible effects achieved.
     * Rollback refs created and recovery instructions.
     * Omitted, rejected, or unchanged items.
     * Remaining repository uncertainties.
