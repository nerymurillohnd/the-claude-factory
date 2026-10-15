# Phase 11: Cross-domain reconciliation (steps)

1. Gather all validated findings from all reviewers.
2. Build a topic index by concept and behavioral intent, not by keywords alone, comparing scope, runtime, activation conditions, exceptions, and provenance.
3. Decide each finding: accept, adjust, or discard with evidence. For mechanical findings, only the disposition may be adjusted.
4. Group related findings into conflict clusters. For each cluster:
   1. Identify every relevant source and exact line range.
   2. Classify the relationship: duplicate, overlap, contradiction, intentional specialization, misplaced, unrelated, or merely related subject matter.
   3. Identify the authoritative home for the guidance.
   4. Explain which side wins in a contradiction under the precedence rules.
   5. Resolve it with a concise, evidence-based recommendation.
5. Look for what no single reviewer could see: contradictions across files, wrong scopes, and Claude-specific instructions inside `AGENTS.md`.
6. Do not delete a policy merely because current code contradicts it. Do not relocate runtime-specific guidance into a shared file unless both runtimes will receive the correct instruction under verified loading behavior.
7. Validate every new finding by the criteria of Phase 10. Launch `audit-verifier` in mode `finding-validation` with those findings only, and tell it that coverage was settled in Phase 10.

## Challenge round

1. A finding is disputed when the cluster holds evidence against it: another reviewer's finding on the same units that conflicts with it, or a fact of the inventory or of the repository evidence that contradicts it. Send each disputed finding to the reviewer that created it, with the opposing finding or fact as data. The reviewer answers `defend`, `concede`, or `adjust`, with its evidence.
2. Decide each dispute with the evidence from both sides. A conceded finding is rejected with the reason `conceded`. An adjusted finding, and a defended one that brings new evidence, go to `audit-verifier` with the other new findings.
3. Use one round by default, and at most two if the user asks. Do not require unanimity.
4. Leave as an open decision, stating both positions, whatever remains unresolved. The coordinator owns the final synthesis.
