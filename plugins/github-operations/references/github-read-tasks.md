# Read-only GitHub tasks

Exact forms for inspecting a pull request and its CI without changing anything. For each task, the first form is preferred and the other is the fallback, in both directions: when a tool is missing or fails, use the other layer, and report a gap only after both failed with the exact error of each. The main session uses either layer; the `pr-tracker` agent has no shell and carries the MCP forms in its own instructions. Replace `<owner>/<repo>`, `<n>`, `<sha>`, `<run-id>`. MCP tool names are bare; in a session they carry the prefix of the configured GitHub server. The Actions, Dependabot and rulesets MCP tools exist only with all toolsets on, which is how the plugin connects. The `gh` forms were checked against `gh --help` field lists, and most were run read-only against a real PR. The MCP forms follow the tool schemas and were not executed.

## PR snapshot

- MCP: `pull_request_read` with `method: get`.
- gh: `gh pr view <n> -R <owner>/<repo> --json headRefOid,state,isDraft,mergeable,mergeStateStatus,baseRefName,headRefName,reviewDecision`.
- Not: `gh pr view` without `--json`, or the local checkout's `git status`, as the PR's state.

## Checks on the current head

- gh: `gh pr checks <n> -R <owner>/<repo> --json name,bucket,workflow,link,startedAt,completedAt`. `bucket` is `pass`, `fail`, `pending`, `skipping` or `cancel`; exit code 8 means pending. `--watch --fail-fast -i 30` waits for the checks to finish.
- MCP: `pull_request_read` with `get_check_runs` for per-check detail, on the PR's current head only.
- Not: the combined status (`get_status`) alone as proof that checks pass.

## Workflow runs for the head

- MCP: `actions_list` with `list_workflow_runs` and `workflow_runs_filter.branch`; it cannot filter by SHA, so keep the runs whose `head_sha` is the head.
- gh: `gh run list -R <owner>/<repo> --commit <sha> --json databaseId,name,workflowName,status,conclusion,attempt,url`.
- Not: `gh run list` without `--commit`, which mixes older heads.

## Jobs, durations and failure logs

- gh: `gh run view <run-id> -R <owner>/<repo> --json jobs` gives job and step `startedAt` and `completedAt`; durations come from these. Then `gh run view <run-id> -R <owner>/<repo> --log-failed` for the cause.
- MCP: `actions_list` with `list_workflow_jobs`, and `get_job_logs` with `run_id`, `failed_only: true`, `return_content: true` and `tail_lines` to bound the size. If the tail lacks the error, read that job again by `job_id` with more lines.
- Not: `--log` for the whole run unless `--log-failed` lacks the cause; it can be huge.

## Is the failure real?

- Read the failing step's log lines, then the workflow file at the head (see "A file at a commit"), then the same job on the base branch: `gh run list -R <owner>/<repo> --branch <base> --workflow <name> --limit 5 --json conclusion,headSha,url`. That tells a branch-caused failure from a pre-existing or intermittent one.
- Not: reporting the first error line as the cause, or calling a failure flaky because a rerun passed.

## Reviews, threads and conversation

- MCP: `pull_request_read` with `get_reviews` for review records, `get_review_comments` for threads (thread node ids, resolved and outdated state, paginated with `perPage` and `after`), `get_comments` for the PR conversation.
- gh: `gh pr view <n> -R <owner>/<repo> --json reviews,comments`, and for threads a read-only `gh api graphql -f query='query(...) { ... reviewThreads ... }'`.
- Not: counting conversation comments as reviews, or any GraphQL `mutation`.

## Dependabot

- MCP: `list_dependabot_alerts`, `get_dependabot_alert`.
- gh: `gh api 'repos/<owner>/<repo>/dependabot/alerts?state=open&per_page=100'` for security alerts, and `gh pr list -R <owner>/<repo> --app dependabot --state open --json number,title,url` for update PRs.
- Not: reporting zero alerts when the call returned 403 or 404; that is incomplete coverage.

## A file at a commit

- MCP: `get_file_contents` with `ref` or `sha`.
- git: `git show <sha>:<path>`.
- Not: reading the working tree without first checking that `git rev-parse HEAD` equals the PR head.
