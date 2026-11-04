# CI tools: reads and the rerun

The GitHub MCP tools and `gh` overlap. Each row lists the layer that does the task best first. Check a `gh` command's own help for its exact options before its first use in a run. Reads go MCP, then `gh`, then `gh api`; a write falls back in either direction when its first layer is missing or fails.

## Reads

Read the current head only, report data you could not read as "not inspected", never zero, and read every list to its end.

| Fact | MCP | gh |
| :-- | :-- | :-- |
| Workflow runs for a commit | `actions_list`, method `list_workflow_runs` with `workflow_runs_filter.branch`; keep the runs whose `head_sha` is the commit | Run list filtered by commit |
| Jobs | `actions_list`, method `list_workflow_jobs`, `resource_id` = run id, `workflow_jobs_filter.filter` = `latest` | Run view with the jobs JSON field |
| Failure logs | `get_job_logs` with `run_id`, `failed_only`, `return_content`, `tail_lines` | Run view, failed logs |

The Actions tools exist only when the GitHub MCP server runs with its Actions toolset on.

## Writes

| Task | First | Fallback | Notes |
| :-- | :-- | :-- | :-- |
| Rerun failed jobs | MCP `actions_run_trigger` with `method: rerun_failed_jobs` and `run_id` (the server flags it destructive) | `gh` run rerun with the failed-only option | Only with evidence of a transient failure, or after the cause is fixed |
| Disable a workflow | — | `gh workflow disable <name or id> -R <o>/<r>` | Only with the user's approval; undone with `gh workflow enable` |
| Re-enable a disabled workflow | — | `gh workflow enable <workflow>` | Only with the user's approval, after the fix lands |
| Delete an artifact | — | `gh api -X DELETE repos/<o>/<r>/actions/artifacts/<id>` | Only with the user's approval; irreversible |
| Delete a cache | — | `gh cache delete <id> -R <o>/<r>` | Only with the user's approval; irreversible |
