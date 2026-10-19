# Audit: GitHub

Everything GitHub knows about the repository, from the day it was created. Read-only: `gh` list/view commands and `gh api` GET requests only. Take `<o>/<r>` from the remote URL and always name it (`gh -R <o>/<r>`, or the path in `gh api`): without it `gh` reads the repository of the current directory, which may not be the target. If `gh` is missing or not signed in, use the read-only tools of a connected GitHub server (never one that writes); with neither, record every item below as `BLOCKED`. Never print a token. A 403 or 404 on a permission-gated call is "unknown" in the ledger, not "none": say which permission it needed.

Page everything. `gh api --paginate` follows every page; `--jq` filters each page. Write outputs to files in the scratch folder and aggregate with `jq`, `awk`, `sort | uniq -c`. The REST list endpoints return up to 100 items per page.

## Repository and access

```sh
gh repo view -R <o>/<r> --json nameWithOwner,visibility,isFork,isArchived,isMirror,defaultBranchRef,viewerPermission,hasWikiEnabled,hasDiscussionsEnabled,hasIssuesEnabled,hasProjectsEnabled,forkCount,diskUsage,pushedAt,parent,deleteBranchOnMerge
gh api repos/<o>/<r> --jq '.full_name'          # if it differs from the remote URL, the repository was renamed or transferred
gh api repos/<o>/<r>/collaborators --paginate --jq '.[]|[.login,.permission]|@tsv'
gh api repos/<o>/<r>/teams --paginate --jq '.[]|[.slug,.permission]|@tsv'
```

### Protection and rulesets

Protection can come from classic branch protection or from rulesets: check both, for the base and for every branch you may judge.

```sh
gh api repos/<o>/<r>/branches/<branch>/protection       # 404 means "not protected" only with ADMIN or MAINTAIN; with less it means unknown
gh api repos/<o>/<r>/rules/branches/<branch>            # the rules that apply to the branch
gh api repos/<o>/<r>/rulesets --paginate
```

## Pull requests, all states

```sh
gh pr list -R <o>/<r> --state all --limit 100000 --json number,title,state,isDraft,headRefName,baseRefName,headRefOid,createdAt,updatedAt,closedAt,mergedAt,author,mergeable,reviewDecision,isCrossRepository > prs.json
jq -r '.[]|.state' prs.json | sort | uniq -c
jq -r '.[]|select(.state=="OPEN")|[.number,.isDraft,.createdAt[0:10],.updatedAt[0:10],.headRefName,.author.login,.mergeable]|@tsv' prs.json     # open pull requests with their age
```

An open pull request is unfinished work: record its head branch, base, age (stale over 90 days), draft state, whether it conflicts, and whether its head branch is also a branch the audit is judging. A remote branch with an open pull request is never a deletion candidate on its own. Closed-but-unmerged pull requests whose head branch still exists are findings too. `git ls-remote origin 'refs/pull/*/head'` lists every pull request head (open or not), which also shows what GitHub keeps after a history rewrite.

## Issues and discussions

```sh
gh issue list -R <o>/<r> --state all --limit 100000 --json number,title,state,labels,createdAt,updatedAt,closedAt,author,comments > issues.json
jq -r '.[]|select(.state=="OPEN")|[.number,.createdAt[0:10],.updatedAt[0:10],.title]|@tsv' issues.json | sort -k3     # open the longest without activity
```

Discussions exist only through GraphQL. `--paginate` needs the `$endCursor` variable and `pageInfo` in the query:

```sh
gh api graphql --paginate -f owner=<o> -f name=<r> -f query='
query($owner:String!, $name:String!, $endCursor:String) {
  repository(owner:$owner, name:$name) {
    discussions(first:100, after:$endCursor) {
      pageInfo { hasNextPage endCursor }
      nodes { number title closed isAnswered createdAt updatedAt category { name } comments { totalCount } }
    }
  }
}' --jq '.data.repository.discussions.nodes[]|[.number,.closed,.isAnswered,.updatedAt[0:10],.category.name,.title]|@tsv'
```

Report open issues and discussions that wait for an answer or have been quiet for a long time (deferred work), and any that mention the cleanup's findings.

## Forks and the fork network

```sh
gh api repos/<o>/<r>/forks --paginate --jq '.[]|[.full_name,.pushed_at[0:10],.stargazers_count]|@tsv'
gh api repos/<o>/<r> --jq '{network:.network_count,forks:.forks_count,parent:.parent.full_name,source:.source.full_name}'
```

A fork can still hold objects you rewrite or delete. List forks that are ahead or recently pushed.

## Actions: failed and forgotten automation

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
- Open code-scanning alerts that come from a failing analysis (see Alerts).

### Artifacts, caches, runners

```sh
gh api repos/<o>/<r>/actions/artifacts --paginate --jq '.artifacts[]|[.name,.size_in_bytes,.created_at[0:10],.expired]|@tsv' > artifacts.tsv
gh cache list -R <o>/<r> --limit 1000 --sort size_in_bytes --json id,key,sizeInBytes,createdAt,lastAccessedAt
gh api repos/<o>/<r>/actions/runners --jq '.runners[]|[.name,.status,.os,(.labels|map(.name)|join(","))]|@tsv'       # self-hosted runners
```

## Integrations: what GitHub keeps tied to the repository

Report names, scope, age and last use. Never print a value.

```sh
gh api repos/<o>/<r>/hooks --paginate --jq '.[]|[.id,.name,.active,.config.url,(.events|join(","))]|@tsv'     # webhooks (needs admin; redact the URL's credentials)
gh api repos/<o>/<r>/keys --paginate --jq '.[]|[.id,.title,.read_only,.created_at[0:10],.last_used]|@tsv'     # deploy keys
gh api repos/<o>/<r>/environments --jq '.environments[]|[.name,.protection_rules]|@json'
gh secret list -R <o>/<r>; gh secret list -R <o>/<r> --app dependabot; gh variable list -R <o>/<r>               # names only
gh api repos/<o>/<r>/pages                                                                                     # 404 means no Pages
gh release list -R <o>/<r> --limit 1000 --json tagName,publishedAt,isDraft,isPrerelease
gh api repos/<o>/<r>/deployments --paginate --jq '.[]|[.environment,.ref,.created_at[0:10]]|@tsv'
gh api repos/<o>/<r>/codespaces --jq '.codespaces[]|[.name,.state,.last_used_at]|@tsv'
gh api graphql -f query='{repository(owner:"<o>",name:"<r>"){projectsV2(first:50){nodes{title closed url}}}}'
git ls-remote https://github.com/<o>/<r>.wiki.git HEAD                                                         # exit 0 and a SHA means a wiki repository exists
```

Packages tied to the repository: list the owner's packages and keep those whose `repository.full_name` is this one (`gh api 'users/<o>/packages?package_type=container' --paginate`, or `orgs/<o>/packages?...`; repeat for `npm`, `maven`, `rubygems`, `nuget`, `docker`).

Installed GitHub Apps are not readable with a repository token (the repository installation endpoint needs an app JWT, and the organization one needs organization admin): record them as `not reachable` and tell the user to check Settings → Integrations → GitHub Apps. Rotating or removing a deploy key, webhook, secret or app is the user's decision: these items are report-only.

## Alerts

```sh
gh api repos/<o>/<r>/secret-scanning/alerts --paginate --jq '.[]|select(.state=="open")|[.number,.secret_type_display_name,.created_at[0:10]]|@tsv'
gh api repos/<o>/<r>/dependabot/alerts --paginate --jq '.[]|select(.state=="open")|[.number,.security_advisory.severity,.dependency.package.name,.created_at[0:10]]|@tsv'
gh api repos/<o>/<r>/code-scanning/alerts --paginate --jq '.[]|select(.state=="open")|[.number,.rule.severity,.rule.id,.created_at[0:10]]|@tsv'
```

An open secret-scanning alert is a secret that is already exposed: the report says to rotate it. A 403 usually means the feature is off or the token lacks the scope: record which.

## References from other repositories

```sh
gh search code '"<o>/<r>"' --match file --limit 100 --json repository,path,url
gh search code 'uses: <o>/<r>' --limit 100 --json repository,path,url
```

GitHub documents that code search covers only the default branch, only files under 384 KB, returns at most 1,000 results and allows 10 requests per minute: results are a lower bound, and the ledger says so. Look for `uses: <o>/<r>@` workflow references, git and submodule URLs, marketplace manifests and dependency specifications.
