# GitHub Actions inventory

Read-only commands that list a repository's workflows, runs, artifacts, caches and self-hosted runners, and find the ones that fail, hang or stopped running.

## Workflows and runs

```sh
gh workflow list -R <o>/<r> --all --json id,name,state,path        # includes disabled workflows
gh api repos/<o>/<r>/actions/permissions
```

A filtered run list returns at most 1,000 results (GitHub documents this for `status`, `branch`, `created`, `event` and the other filters). To be complete, split by creation date until each window returns fewer than 1,000:

```sh
gh run list -R <o>/<r> --branch <default branch> --created '2024-01-01..2024-12-31' --limit 1000 --json databaseId,workflowName,event,status,conclusion,createdAt,headSha,url >> runs-default-branch.json
```

Then, per workflow, find the ones whose latest run on the default branch failed and was never followed by a success:

```sh
jq -s 'add | group_by(.workflowName) | map({workflow:.[0].workflowName, last:(sort_by(.createdAt)|last|{at:.createdAt,conclusion:.conclusion,url:.url}), lastSuccess:([.[]|select(.conclusion=="success")]|sort_by(.createdAt)|last|.createdAt)}) | map(select(.last.conclusion!="success"))' runs-default-branch.json
```

Also look for:

- **Scheduled workflows that stopped running**: `schedule` runs (`--event schedule`) whose newest run is older than the schedule says it should be (GitHub disables schedules after 60 days of repository inactivity: verify in the current docs before stating it).
- **Runs stuck** in `queued`, `waiting` or `in_progress`: `gh run list -R <o>/<r> --status queued --limit 1000`, and the same for the others, older than a day.
- **Workflows that reference things that no longer exist**: branches in `on:` filters, secret names in `${{ secrets.NAME }}` that `gh secret list` does not show, files under `paths:`.
- **Dependabot updates that failed**: runs whose workflow name is `Dependabot Updates`.
- Open code-scanning alerts that come from a failing analysis.

## Artifacts, caches, runners

```sh
gh api repos/<o>/<r>/actions/artifacts --paginate --jq '.artifacts[]|[.name,.size_in_bytes,.created_at[0:10],.expired]|@tsv' > artifacts.tsv
gh cache list -R <o>/<r> --limit 1000 --sort size_in_bytes --json id,key,sizeInBytes,createdAt,lastAccessedAt
gh api repos/<o>/<r>/actions/runners --jq '.runners[]|[.name,.status,.os,(.labels|map(.name)|join(","))]|@tsv'       # self-hosted runners
```
