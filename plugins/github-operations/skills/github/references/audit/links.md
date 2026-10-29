# Audit: everything outside the repository that still points at it

A copy or a link of any kind that ties the repository to a place outside it and is still alive: another clone, a mirror, a registry entry, a scheduled job, a tunnel. The audit cannot prove that none exists beyond what these commands see, so each domain ends in the coverage ledger as `checked`, `BLOCKED`, `not reachable` or `declined` (see `intake-local.md`).

Three classes decide how each domain is handled:

- **Reachable**: a read-only `git`, `gh` or public-registry query. Run it.
- **Needs consent**: a scan outside the repository (other clones, workspace files, scheduled jobs, processes and ports). Run it only within the scopes the user allowed at step 0, and only in the folders they named. A scope they declined is recorded as `declined`.
- **Not reachable**: other people's machines, third-party services without credentials, deleted forks, anything behind a credential you must not read. Record the reason and what the user can check themselves.

Everything here is read-only. Never read a credential store, a key file or a secret value, and never print a token.

Below, `<repo>` is the absolute repository path, `<o>/<r>` the GitHub name and `<roots>` the folders the user allowed.

## Remote and mirrors (reachable)

```sh
git remote -v | sed -E 's#(//)[^/@[:space:]]*@#\1***@#'              # every remote, including mirrors on other hosts
git config --get-regexp '^remote\..*\.(mirror|pushurl)$'
git ls-remote --heads --tags <remote>                               # what each remote really has
```

A remote on a host other than GitHub, a `pushurl` that differs from `url`, or `remote.<name>.mirror=true` is a live copy: record it, and the host. Compare the GitHub name with the URL in the remote (`gh api repos/<o>/<r> --jq .full_name`): a different name means the repository was renamed or transferred and the old URL still redirects.

## Configuration committed in the tree (reachable, references only)

```sh
git ls-files | grep -E '(^|/)(\.circleci/|Jenkinsfile|\.gitlab-ci\.yml|azure-pipelines\.yml|netlify\.toml|vercel\.json|render\.yaml|fly\.toml|app\.yaml|Procfile|\.travis\.yml|bitbucket-pipelines\.yml|cloudbuild\.ya?ml|buildspec\.ya?ml)$'
git grep -nIE 'https?://[^ "'"'"')]*(netlify|vercel|herokuapp|fly\.dev|onrender|ngrok|trycloudflare|loca\.lt|pages\.dev|workers\.dev)[^ "'"'"')]*'
```

Record these as "reference found, live state unverified": the skill has no credentials for those services, so it cannot say whether the deployment is alive. Tell the user which dashboards to check.

## Registries and marketplaces (reachable, public)

Read the package name from the tree (`package.json` `name`, `pyproject.toml` `[project] name`, `Cargo.toml` `[package] name`, a plugin manifest), then ask the registry where that name points:

```sh
npm view <name> repository.url                                         # npm
curl -fsS https://pypi.org/pypi/<name>/json | jq '.info.project_urls'    # PyPI
```

A published package whose repository field points here is a live link: report the name and the latest version. Plugin marketplaces that list the repository are found with the code search in `github.md` (`gh search code '"<o>/<r>"' --filename marketplace.json`) and with `gh search code '"<o>/<r>"' --match file`.

## This machine, outside the repository (needs consent)

Search only inside `<roots>`. Prune `node_modules` so the scan stays fast.

```sh
# other clones of the same remote
find <roots> -name node_modules -prune -o -path '*/.git/config' -type f -exec grep -l '<o>/<r>' {} + 2>/dev/null
# repositories whose object store borrows from this one
find <roots> -name node_modules -prune -o -path '*/.git/objects/info/alternates' -type f -exec grep -l '<repo>' {} + 2>/dev/null
# submodules of other local repositories that use this one
find <roots> -name node_modules -prune -o -name .gitmodules -type f -exec grep -l '<o>/<r>' {} + 2>/dev/null
# symlinks into the repository
find <roots> -name node_modules -prune -o -type l -lname '<repo>*' -print 2>/dev/null
# editor workspaces that open it
find <roots> -name node_modules -prune -o \( -name '*.code-workspace' -o -name workspace.xml \) -type f -exec grep -l '<repo>' {} + 2>/dev/null
```

Linked worktrees that live elsewhere but belong to this repository are already in `git worktree list --porcelain`. A clone whose `HEAD` is ahead of what the remote has holds unpushed work: for each clone found, report its path, its current branch and `git -C <clone> status -sb`. Never change another clone.

### Scheduled jobs (needs consent)

```sh
grep -rlE '<repo>|<o>/<r>' ~/Library/LaunchAgents /Library/LaunchAgents /Library/LaunchDaemons 2>/dev/null       # macOS launchd
crontab -l 2>/dev/null | grep -nE '<repo>|<o>/<r>'                                                            # cron
grep -rlE '<repo>|<o>/<r>' ~/.config/systemd/user /etc/systemd/system 2>/dev/null                           # systemd
git config --global --get-all maintenance.repo | grep -F '<repo>'                                            # git maintenance schedule
```

### Tunnels and listeners (needs consent)

A process forwarding to the repository's dev server or serving files from it keeps it reachable from outside. List processes and listening ports, then match each candidate's working directory with the repository:

```sh
ps -axo pid,ppid,etime,command | grep -E 'cloudflared|ngrok|localtunnel|(^|[[:space:]])lt[[:space:]]|tailscale|ssh .*-[LR][[:space:]]|git[[:space:]]+daemon|instaweb|http-server|python3? -m http\.server' | grep -v grep
lsof -nP -iTCP -sTCP:LISTEN
lsof -a -p <pid> -d cwd -Fn                    # the working directory of a candidate: does it sit inside <repo>?
tailscale serve status; tailscale funnel status  # only if tailscale is installed
```

Also look at `<repo>/.git` for `git-daemon-export-ok`, `info/refs` left by `update-server-info`, and a running `git daemon` or `git instaweb`. Report the process, how long it has run and what it exposes. Stopping a tunnel or job is an `external-unlink` action in the plan, one per action, with its own approval; the audit only reports it.
