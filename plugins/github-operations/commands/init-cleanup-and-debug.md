---
description: Audits a repository and turns the audit into a cleanup and debugging plan you approve before anything changes.
---

You are authorized to use the `github-operations:cleanup-and-debug` skill to orchestrate an end-to-end audit, plan and cleanup of this repository, delegating the audit to the `github-operations:repo-hygiene:health-diagnostics` agent and planning and executing the approved plan yourself.

## Start

1. Load the `github-operations:cleanup-and-debug` skill and follow it.
2. Identify the repository: the one the user names, or the current one.
3. Determine the stage it is in: not audited, audited and not planned, planned and not approved, approved and not executed, or executed and not validated.
4. Run the workflow from that stage.

## Stage: not audited

1. Measure the repository, and deploy one or more `github-operations:repo-hygiene:health-diagnostics` agents for the audit phases, each with its brief.
2. Require evidence for every item, and verify each report against its evidence.
3. Show the user the findings and the recommendations, and ask which to pursue.

## Stage: audited, not planned

1. Investigate the approved findings that need a diagnosis.
2. Write the plan, then show the user the exact actions and ask for approval.

## Stage: approved, not executed

1. Execute the approved actions yourself, in the plan's order, with the proof each one requires.
2. Stop and ask the user when an action fails or the repository differs from what the plan expected.

## Stage: executed, not validated

1. Validate every action against its proof.
2. Report what was done, what was not and why, and what is left for the user.

## Done when

- Execute only actions the user approved, after the audit is verified.
- Report at once anything that cannot be completed, with the reason.
