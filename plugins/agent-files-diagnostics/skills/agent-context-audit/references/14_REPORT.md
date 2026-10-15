# Phase 14: Report (steps)

## 14.1 Status

Determine the status: complete, complete with findings, incomplete (partial), failed, or blocked (not executable). If the user narrowed the scope at Gate 1, add the qualifier `narrowed` to complete or complete with findings, and list what was left out. A narrowed scope never makes an audit partial: partial means the approved scope was not finished. In non-interactive runs, map each status to a distinct exit code, separate from any policy-defined finding threshold.

## 14.2 Required sections

1. Executive summary.
2. Audit status.
3. Scope, exclusions, runtime versions, and repository baseline: run metadata (date, mode, versions, models), and what was omitted, unclassified, or out of scope, with counts and reasons.
4. Source inventory and instruction-loading and applicability map.
5. Full-read coverage ledger and reviewer completion status: loading mode, status, and lines read for each source.
6. Detailed intra-domain findings, ordered by severity, with all their evidence.
7. Cross-domain conflict clusters and resolutions, and the open decisions with both positions.
8. Prioritized recommendation table and remediation plan.
9. Material guidance reviewed and retained, with concise rationale.
10. Unverified claims and external verdicts, blockers, disagreements, consistency limitations, and the limitations of the run.
11. Rejected and discarded findings, with their reasons.
12. Final verification results, and the usage of each session: tokens, tool calls, and time for each agent as the harness reported them, and cost only where the harness reports it. Write `unavailable` for anything it did not give. Never estimate.
13. Recommended future reusable architecture, without implementing it (see below).

Clearly distinguish confirmed defects from optional simplifications. Mask again any model-produced text before writing it.

After writing, reopen the report and verify that it exists, is nonempty, and contains every required section. Verify too that it shows what the run recorded: every uncertainty, every changed or missing source, and every rejected finding.

## 14.3 Final chat response

Give the user:

1. The report location and the usage figures (tokens and time; cost only where available).
2. The audit status, any problems or failures, and the coverage summary.
3. The counts by severity and the executive summary.
4. Each high-severity finding: identifier, file, lines, problem, conflict, and disposition.
5. The open decisions and remaining blockers, if any.
6. Confirmation that no audited source file was modified.
7. An offer to review the medium- and low-severity findings, or those of a specific file, and to retry the external claims that stayed inconclusive.

If the user asks for the latest report, present it without running a new audit. Then STOP and wait for the user's instructions.
