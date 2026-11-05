# Phase 6: External links

Find everything outside the repository that still points to it. This phase is read-only. Scans on this machine run only within the consent recorded in Phase 0.

## Other GitHub repositories

- `uses: <owner>/<repo>@` lines in workflows.
- Submodule URLs.
- Marketplace manifests.
- Dependency specifications.

Code search limits what can be found ([GitHub REST: search][search-rest], [Searching code][search-code]):

- Only the default branch is indexed, and only files smaller than 384 KB.
- At most 1,000 results per search, and 10 code-search requests per minute.

Split a query that hits the result cap. Record what code search cannot see in the coverage ledger.

## Other hosts and services

- Mirrors and remotes on other hosts, found in the configuration.
- Committed configuration for other CI and deploy services: `.circleci`, `Jenkinsfile`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `netlify.toml`, `vercel.json`, `render.yaml`, `fly.toml` and similar. Report each as "referenced, live state unverified".

## Package registries

- Public registries whose packages point to this repository, queried read-only.

## This machine

Only with consent:

- Other clones of the same remote.
- Worktrees and alternates that point here.
- Symlinks into the repository.
- IDE workspace files.
- cron, launchd and systemd jobs that reference the path or the remote.
- Tunnels and listening ports that serve from the repository or forward to it.

## Done when

- [ ] Every code-search query ran to completion or was split, and what code search cannot see is in the coverage ledger.
- [ ] Every mirror, other host and committed service configuration is listed.
- [ ] Every registry package that points to this repository is listed.
- [ ] Every scan on this machine stayed inside the approved roots, and every refused scope is in the coverage ledger.

## Sources

Checked on 2026-11-04.

- [GitHub REST: search][search-rest]: "The Search code endpoint requires you to authenticate and limits you to 10 requests per minute"; "up to 1,000 results for each search".
- [Searching code][search-code]: "Only the default branch is indexed for code search"; "Only files smaller than 384 KB are searchable."

[search-rest]: https://docs.github.com/en/rest/search/search
[search-code]: https://docs.github.com/en/search-github/searching-on-github/searching-code
