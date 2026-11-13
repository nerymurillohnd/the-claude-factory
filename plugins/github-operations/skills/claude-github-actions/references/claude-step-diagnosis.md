# Diagnose a Claude step that failed, did nothing or posted nothing

Six steps, in order. Read the tools for each call in [ci-tooling.md](ci-tooling.md). A green Claude step can still be the failure to diagnose, so read every log in full, not only its failed lines.

## 1. Find the run, or prove there is none

1. **Start from what the user saw:** the repository, the event (a comment on issue #N, a review on pull request #N, a push) and roughly when.
2. **List the runs for that event and time:** MCP `actions_list` with `list_workflow_runs`, or

   ```
   gh run list --event <event> --created '>=<YYYY-MM-DDTHH:MM:SSZ>' --json databaseId,attempt,workflowName,event,headSha,status,conclusion,displayTitle,createdAt
   ```

   `--event` and `--created` filter on GitHub's side; `--created` takes GitHub's date-range syntax. Comment events are `issue_comment` (issues and pull requests alike), `pull_request_review_comment` and `pull_request_review`.
3. **Match the run** to the request by event, time and title, and record its ID, attempt, job, step and head commit.
4. **Read the state:**
   - `action_required`: the run waits for a maintainer's approval. Report it as waiting, never as failed or passed.
   - A job `skipped`: evaluate its `if:` against the event (for example, the comment doesn't contain the trigger phrase). That is the cause.
   - No run at all: go to [step 2](#2-when-there-is-no-run).
   - Otherwise: go to [step 3](#3-read-the-workflow-and-the-action-as-the-run-used-them).

## 2. When there is no run

Check these in order, and stop at the first that explains it:

1. **The default branch's copy.** Comment, issue and schedule events run the workflow file on the default branch. Read that copy: does `on:` list the event, and do its `types:` include the action that happened? `types: [edited]` never runs on a new comment.
2. **The workflow's state:** `gh workflow list --all`, or `gh api repos/<owner>/<repo>/actions/workflows`. `disabled_manually` and `disabled_inactivity` start nothing.
3. **An invalid workflow file:** runs of that workflow with zero jobs and `failure`, or `startup_failure`, on recent commits; or a file over 500 KB. The workflow's state doesn't show a parse error. This is W-12.
4. **The Actions policy:** `gh api repos/<owner>/<repo>/actions/permissions` answering `enabled: false`.
5. **An event caused by `GITHUB_TOKEN`:** a comment or label made by another workflow with the job's token starts no run.
6. **A comment edited, not created**, against a trigger that lists only `created`, or the other way round.

When none explains it, say so, with what you checked. A fix that changes what starts the workflow (`on:` or `types:`) is its own approval ([Build the patches](workflow-audit.md#build-the-patches)).

## 3. Read the workflow and the action as the run used them

- **The workflow** at the run's head commit.
- **The claude-code-action commit** the step ran: the "Set up job" log line `Download action repository 'anthropics/claude-code-action@<ref>' (SHA:<sha>)` ([Find the commit a step runs](version-drift.md#find-the-commit-a-step-runs)). Compare it with the snapshot ([Compare with the snapshot](version-drift.md#compare-with-the-snapshot)); for a changed topic, read the code at that commit, not action-contract.md.
- **`action.yml` at that commit:** MCP `get_file_contents` with `sha`, or `gh api -H 'Accept: application/vnd.github.raw' 'repos/anthropics/claude-code-action/contents/action.yml?ref=<sha>'`.
- **The step's effective mode** in that run, from [Permission mode](action-contract.md#permission-mode).

## 4. Match the catalog

Compare the log lines and the workflow against every entry in [sharp-edges.md](sharp-edges.md). When one matches, its fix is the answer: name its ID. When none does, say "none matched".

A green run needs this step too:

- **A no-op, never a success:** it logged `No trigger found` (SE-04), or a workflow-validation skip (SE-15).
- **Green, but degraded:** the untrusted-PR denial warning (SE-19), a non-zero `permission_denials_count` in the result, the tag-mode auto fallback warnings (SE-18), the session-guard restore warning (SE-21), or inline comments dropped or posted unclassified (SE-16). Report each as "green, degraded" with its line.
- An agent run whose auto mode was unavailable stays in Manual **without a warning**: look for denied calls instead.

## 5. Classify what is left

When nothing matched, decide between these, and rank the hypotheses, each with the log line that supports it and the next check that would confirm it:

- a workflow-definition defect;
- a command denied by the untrusted-PR list, or a call refused by auto's review or denied in acceptEdits or Manual;
- a git wrapper's rejection;
- a later step broken by the session guard's restore, or by `origin` without credentials after the session;
- the bot pull-request-author gate;
- an action or Claude Code defect;
- a credential or permission problem;
- a rate or budget limit, or a provider outage;
- a cause in the project's own code or tests.

## 6. Hand off or propose the fix

- **A cause in the project's code or tests** is CI repair ([ci-repair.md](ci-repair.md)) on the default branch, or `github-operations:auto-pr-lifecycle`'s work on a pull request. Report it and stop.
- **A workflow cause:** write the patch by [Build the patches](workflow-audit.md#build-the-patches), check it by [Validate the patches](workflow-audit.md#validate-the-patches), and apply it only after the user approves.
- **Reruns:** only with evidence that the failure was transient, and at most once (SE-09).
- **A debug rerun needs the user's approval.** The action prints the session's full output only when `show_full_output` is true or `ACTIONS_STEP_DEBUG` is `true` in the step's environment [unverified: whether re-running with debug logging alone puts it there]. In a public repository that output is public (C-14).
