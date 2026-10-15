# Phase 10: Coverage and validation (steps)

`audit-verifier` in mode `finding-validation` carries out items 1 to 12 of its Workflow (`agents/audit-verifier.md` at the plugin root):

| Items | What they check |
| :- | :- |
| 1 to 3 | Coverage: every assigned line was read, tool use and format were respected, and which reviewers or ranges need a retry |
| 4 to 6 | Finding evidence: lines, excerpts, units, references, and external verdicts |
| 7 to 9 | Hygiene: mechanical repeats, duplicate groups, and rejected findings with their reasons |
| 10 to 12 | Scope, validation of the Phase 7 findings, and the category of each finding |

Your part, with its report in hand (SKILL.md, Acting on what comes back):

1. Reject the results it flags for disallowed tool use or broken format.
2. Relaunch or resume the reviewers that failed or left lines unread, with bounded retries. If a package is still incomplete after the retries, mark the audit incomplete.
3. Discard the mechanical repeats, apply the duplicate groups, and keep every rejection with its reason.
