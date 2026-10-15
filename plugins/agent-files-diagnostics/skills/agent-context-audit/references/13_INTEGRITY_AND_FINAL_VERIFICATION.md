# Phase 13: Integrity and final verification (steps)

## 13.1 Integrity

1. Recompute the hash of each audited source, with the command used in Phase 4, and recheck the relevant evidence files.
2. Report every source that changed or disappeared during the run.
3. Compare the git state and HEAD with the baseline.
4. If a source changed or disappeared, make a fresh masked copy of each changed one and revalidate the findings on it with `audit-verifier` in mode `finding-validation`. If HEAD or the working tree differs from the baseline, revalidate in the same way the findings that rest on repository evidence. A finding that passes stands. One that cannot be revalidated is marked `stale`, with the limitation, and the report states the appropriate rerun scope.
5. Do not claim a consistent snapshot merely because the git commit is unchanged. Account for uncommitted instruction files and for external and global sources.
6. Mark the audit partial if any audited source changed or disappeared, because its current content was not fully read: revalidating its findings does not change that. Mark it partial too if any finding stays `stale`. A change in git state alone, with every source unchanged and every affected finding revalidated, does not make the audit partial.

## 13.2 Verification pass

Use a dedicated verifier when practical; otherwise run a coordinator verification pass labeled as such.

The checklist is carried out by `audit-verifier` in mode `final-verification` (`agents/audit-verifier.md` at the plugin root). A coordinator pass applies the same checklist from that file.

Attempt bounded recovery for missing or failed work. If recovery fails, publish an explicitly incomplete report identifying the gaps.
