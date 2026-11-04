# Diagnose a Claude step that failed, did nothing or posted nothing

1. **Identify the run.** Record the repository, run ID, attempt, job, step and head commit. Read the step's full log, not only the failed lines: a green Claude step can still be a failure to diagnose. Use the read tools in `ci-tooling.md`.
2. **Read the workflow as that run used it.** Read the workflow file at the run's head commit and the `action.yml` at the commit the step pinned.
3. **Match the catalog first.** Compare the log lines and the workflow against every entry in `sharp-edges.md`. When one matches, its fix is the answer: name its ID.
4. **Classify what is left.** When nothing matches, decide between: a workflow-definition defect, an action or Claude Code defect, a credential or permission problem, a rate or budget limit, a provider outage, and a cause in the project's own code or tests. Rank the hypotheses, each with the log line that supports it and the next check that would confirm it.
5. **Hand off what is not a workflow cause.** A cause in the project's code or tests is CI repair (`ci-repair.md`) on the default branch, or the pull request skill's work on a pull request. Report it and stop.
6. **Propose the fix.** For a workflow cause, write the exact patch as `workflow-audit.md` says, and apply it only after the user approves.

A green run that logged "No trigger found" is a no-op (SE-04), never a success. Rerun a step only with evidence that its failure was transient, and at most once (SE-09).
