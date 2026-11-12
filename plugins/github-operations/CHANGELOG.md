# Changelog

All notable changes to **GitHub Operations** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- A `labels-sync.py` script for the `github-files-setup` skill. It compares the repository's labels with a label list through REST, or through the GitHub MCP server's `list_label` output with `--current`. It needs one mode, `--dry-run` or `--apply`, never both. `--apply` creates the missing labels and updates the ones that differ. It never deletes or renames a label. It prints extra labels as a count unless you pass `--show-extra`. A failed write names the label and keeps the output of `gh`. The skill no longer only reports label differences: it can apply the labels you approve.
- `check-forms.py` catches more of GitHub's form rules: similar or blocked field labels (for example "password"), "n/a" as a dropdown default, form names of 3 characters or fewer that GitHub hides, and unreplaced placeholders such as `<OWNER>`. It also checks `dependabot.yml` with `--kind dependabot`.
- A fourth way to label issues by component in `github-files-setup`: triage by Claude. It is either a `claude-code-action` workflow modeled on Anthropic's own `claude-issue-triage.yml` and `/triage-issue` (audited with the `claude-github-actions` skill), or a cloud scheduled task with a GitHub issue trigger, which needs the Claude GitHub App and no secret. The labels step now uses the exact lifecycle labels a triage automation applies, and the label model adds `status: needs-repro`.
- A `CODEOWNERS` reference for `github-files-setup`: valid owners (teams, or users with write access, never an organization), rule order, the 3 MB limit, self-protection, and checking for errors after the merge.

### Changed

- Scripts run as `python3 <script>` on any Python 3.12 or later, whoever installed it. `check-forms.py` no longer uses uv. It needs `ruamel.yaml` 0.19.1 and `check-jsonschema` 0.39.0 installed in the Python that runs it. Without them it stops and prints the `python3 -m pip install ...` command, and Claude checks the files by reading instead. It never installs anything. `labels-sync.py` needs only the standard library. Both scripts stop with a clear message on a Python older than 3.12 that says what to do next. Both exit 0 when they ran, with a summary (`check-forms.py`: "pass" or how many files have findings; `labels-sync.py`: a `summary` field with the missing, different and extra counts), and exit 2 when they could not run. Before, findings exited 1, which Claude Code treats as a failed command and truncates.
- The `github-files-setup` skill keeps the branch you are on when it is not the default branch, instead of always creating a new branch.
- Dependabot guidance follows GitHub's current options: both `dependabot.yml` and `.yaml`, cooldown (3 days by default for version updates since 2026-07-14), groups, multi-ecosystem groups, the uv ecosystem and the full ecosystem list. The Dependabot model holds only the required keys, and the skill offers the cooldown, groups and other options before it writes.
- The merge message setting reads the repository's commit-title convention first. It offers all four squash options and the merge-commit options with their trade-offs, including that "title and description" copies the whole PR template into history. It no longer assumes Conventional Commits. The merge guide keeps only the trade-offs.
- Issue form guidance explains that a dropdown answer applies no label, and gives four ways to label by component. Each form gets an issue type (Bug, Feature, Task or none), and a component dropdown when the repository has a fixed list. Forms set `type:` from the issue types the repository can use, on personal and organization accounts alike (read through `repos/{owner}/{repo}/issue-types`), and keep the type label, because issue types do not exist on pull requests. The guidance also covers projects, upload fields, dropdown defaults, `min_length`, ids that stay stable for prefill, and chooser order. It links only to features that are on (private vulnerability reporting, Discussions).
- The PR template models no longer assume CI: the checks line follows where the repository's checks run (CI, local or both). The standard PR template is the default and is headed "Standard".
- When the `github-files-setup` skill starts, Claude Code runs `check-forms.py` and `labels-sync.py --dry-run` without a permission prompt, because the skill pre-approves them through `allowed-tools`. Both are read-only. The approval lasts only the turn that starts the skill. `labels-sync.py --apply` writes labels, so it still asks.
- The `github-files-setup` description now says exactly which files the skill writes, that it can turn merge methods off with your approval, and that it does not write `CONTRIBUTING`, `SECURITY`, `SUPPORT`, code of conduct or README files.
- The `github-files-setup` workflow chooses the models and label names before it writes any file. It replaces templates inherited from the owner's `.github` repository after a warning. A declined label or a declined push has a defined outcome, and the report says "not opened". The checklist has one item per validation.

### Removed

- The `labels-diff.py` script, replaced by `labels-sync.py`. Only the skill ran it, so nothing changes for you.

### Fixed

- `github-files-setup` works where `gh` is missing or GitHub's GraphQL API is blocked, for example in Claude Code on the web, where GitHub answers HTTP 403 "GitHub GraphQL is not available". It reads and writes GitHub through the GitHub MCP server first, then through `gh api` REST, and says what to change in GitHub's settings when neither works. The new `skills/github-files-setup/references/github-access.md` holds the steps.
- `pr-fixer`, `pr-tracker` and `pr-finalizer`, and the `cleanup-and-debug` skill with its `health-diagnostics` agent, read through REST when GraphQL is blocked, instead of reporting a missing permission.
- `github-files-setup` creates labels after it writes every other file, so the labels named by Dependabot and the PR templates are created too.
- `github-files-setup` no longer writes `* @<owner>` to `CODEOWNERS`, which is invalid for an organization-owned repository. It writes only valid owners.
- `check-forms.py` no longer flags the documented `min_length` key.
- `check-forms.py` exits 2 with a message on a file that is not UTF-8, instead of a traceback.
- The Idea issue form model linked to `feature-request.yml`, a file that does not exist. It now links to `feature_request.yml`. Links that hard-coded `main` no longer do.

## [0.7.3] - 2026-11-09

### Fixed

- `pr-finalizer` no longer reports a pull request ready to merge when it conflicts with commits added to the base branch after GitHub last checked it. It reads the base branch as it is now, compares the branch with it and tests the merge, and never relies on GitHub's `mergeable_state` alone. `pr-tracker` does the same and reports the result.
- `pr-finalizer` and `pr-tracker` no longer treat a pull request as passing when a workflow run failed but every check they could see was green. They take each workflow run's own conclusion at the head, and name the jobs a workflow defines that never started, which leave no check behind.
- A base branch with no required checks no longer makes every check count as passing: both agents now require every workflow run and check at the head to pass, and say when the base requires none.
- The reports show the base commit compared, whether the branch merges cleanly, and the base commits added after the checks ran, which those checks do not cover.
- When your base branch requires branches to be up to date before merging, a branch behind it is no longer reported as ready.
- Before the merge, the `auto-pr-lifecycle` skill reads your base branch again, not only the branch, and runs the finalizer again when the base moved. When the base changed after the checks ran, it tells you and recommends updating the branch first.

## [0.7.2] - 2026-11-06

### Changed

- The plugin's description now names the tools and terms people type when they search for a plugin like this one in `/plugin`, which matches only the plugin's name, display name and description. Nothing changes in how the plugin works.

## [0.7.1] - 2026-11-05

### Added

- A listing icon and links to this README, the issue forms and the marketplace's privacy policy, which Anthropic's plugin directory shows on the plugin's page. Claude Code ignores these fields when it loads the plugin, so nothing changes in how it works.

## [0.7.0] - 2026-11-05

### Removed

- **Breaking:** the plugin no longer bundles the GitHub MCP server, nor the `github_token` option that held its token. After you update, `plugin:github-operations:github` leaves `/mcp`, and Claude works through `gh` until you add GitHub's server yourself. The README's Prerequisites give the `claude mcp add-json` command, with `claude mcp add` as the fallback, both with every toolset and early-access mode as before, and say which header to change for fewer toolsets or no early access. The token you saved in the plugin is no longer read: create a new one, and delete the old one on GitHub.

### Changed

- **Breaking:** the GitHub tools take the name of the server you add. For a server added as `github`, deny rules name `mcp__github__…` instead of `mcp__plugin_github-operations_github__…`.
- The README shows how to add GitHub's server to the desktop app's chat and Cowork as a custom connector with request headers, and says the Code tab uses the server you added in the terminal.

## [0.6.1] - 2026-11-05

### Fixed

- The read-only `repo-hygiene:health-diagnostics` agent can no longer launch other agents or edit files: Claude Code now removes its Agent, Edit and NotebookEdit tools, and it keeps only Write, for its notes outside your repository. Before, it could start an agent able to change your repository during an audit.
- `pr-tracker` and `pr-fixer` read a failed job's log as text, including the first error, instead of receiving download links or only its last 500 lines.
- `pr-tracker` no longer works from a wrong claim about where a pull request's requested reviewers come from.
- `pr-finalizer` reads review threads with the query that carries each comment's ID and whether its author is a bot, so it replies and resolves without a wasted call first.
- The agents no longer treat a command that Claude Code moved to the background as finished: they wait for it before recording a result, committing or reporting, and `pr-tracker` counts its wait limit by elapsed time.

## [0.6.0] - 2026-11-04

### Added

- The `auto-pr-lifecycle` skill takes a pull request from the stage it is in to merge: it opens it, has its agents watch, fix and finalize it, and asks you before every push and before the merge. After each fix round you choose **Push**, **Push without asking again on this pull request** or **Don't push**.
- A `/github-operations:init-pr-lifecycle` command that starts that lifecycle on the current pull request, or the one you name.
- A `pr-lifecycle` team of three agents: `pr-tracker` watches a pull request and reports what it finds, `pr-fixer` fixes reported failures and review findings in your local clone without pushing, and `pr-finalizer` answers the review threads, resolves the ones bots opened, and reports whether the pull request is ready to merge.
- The `cleanup-and-debug` skill audits a repository, local and remote, in fourteen phases, then plans and runs only the cleanup you approve at two gates, behind a backup bundle it proves restores. The `/github-operations:init-cleanup-and-debug` command starts it, and the read-only `repo-hygiene:health-diagnostics` agent runs its audit phases, several at once on a large repository.
- The `claude-github-actions` skill works on GitHub Actions workflows, specializing in those that run Claude: it diagnoses a claude-code-action step that failed, did nothing or posted nothing against fourteen known failure patterns, audits and hardens workflow files with an exact patch per finding (shell injection, excess permissions, unpinned actions, `pull_request_target` designs, claude-code-action misconfiguration), and repairs failing CI on the default branch. It pins every action it writes to a full commit and looks up versions and model IDs when it writes them; it asks before any rerun, workflow change or push.
- The `github-files-setup` skill writes a repository's own PR templates, issue and discussion forms, labels, Dependabot file and `CODEOWNERS`, adapted to that repository from the plugin's models, and sets the merge message you approve. It maps each model to the exact path GitHub reads, and looks for the repository's own copy in every place GitHub accepts one before writing anything.

### Changed

- **Breaking:** GitHub work runs through focused skills instead of one `github` contract: the pull request lifecycle, repository setup, and repository audit and cleanup. Each skill hands a request it does not cover to the one that does.
- **Breaking:** the plugin no longer ships hooks, and no longer needs `python3` for them. Claude Code still removes some tools from the PR lifecycle agents: none of them can launch another agent, and the tracker and the finalizer cannot use the file-writing tools. Their other limits (the tracker, the auditor and the finalizer change no code, the fixer never pushes) are kept only by their instructions; the README shows how to add hard limits yourself.
- The PR tracker reads a green AI reviewer's run log before calling it a no-op, lists a reviewer that produced nothing as a blocker, tells a claude-code-action actor-gate failure or a missing OIDC token apart from missing secrets, and hands Claude-step and workflow failures to the Actions skill with the run, job, commit and log lines.
- The PR lifecycle stops after five fix rounds and asks you whether to continue, and the fixer reads the hooks a commit runs before committing on another author's code.
- The cleanup audit also reads the repository's Actions settings, including whether fork pull requests receive write tokens, and hands workflow-file risks to the Actions skill.
- The PR lifecycle no longer requires signed commits: Claude and the fixer commit as your git setup does, signed when it signs, so a repository without commit signing no longer stops the lifecycle.
- `python3` 3.12 and uv are needed only for the repository setup's label comparison and form checks.

### Removed

- **Breaking:** the `github-operations:pr-tracker` agent. Use `github-operations:pr-lifecycle:pr-tracker`, which reports the same findings and adds the failure's run and attempt, its cause class, and a rerun only for a failure shown to be transient.
- **Breaking:** the `github-operations:github` skill. Its tasks moved: `pr` to `auto-pr-lifecycle`, `audit` and `cleanup` to `cleanup-and-debug`, `setup` to `github-files-setup`, and `ci` to `claude-github-actions`. Writing, triaging and answering issues and discussions (`issue`, `discussion`), and fixing an issue through a pull request ("fix issue #N"), are not part of this version. Its template models now ship with `github-files-setup`.
- **Breaking:** the `github-operations:repo-auditor` agent. The cleanup's audit runs in `github-operations:repo-hygiene:health-diagnostics`.

## [0.5.1] - 2026-11-02

### Changed

- The README lists every command the reviewer agents cannot run, `git fetch` and `GIT_EXEC_PATH` included, names `bash` as a prerequisite of the hooks, and gives Claude Code 2.1.314 as the minimum: from that version the hooks also check the shell commands the Monitor tool starts.

### Fixed

- A reviewer agent's denied configuration change now names `GIT_EXEC_PATH` among the variables it cannot set.
- The changelog no longer marks the removal of the internal `pr-diagnostics` skill in 0.3.0 as breaking, counts seven issue forms in 0.5.0, folds 0.4.0's restored agent into Changed, and states the `python3` requirement of 0.1.0's `git-cleanup` guard.

## [0.5.0] - 2026-10-29

### Changed

- **Breaking:** the `auto-pr-lifecycle` and `git-cleanup` skills are replaced by one skill, `github`, the operating contract for every GitHub task. Type `/github-operations:github pr` where you typed `/github-operations:auto-pr-lifecycle`, and `/github-operations:github cleanup` (or `audit`) where you typed `/github-operations:git-cleanup`. The skill loads before Claude's first GitHub call and holds the rules every task follows: your approval for each push, PR, merge, deletion or settings change, the merge asked at the freshly read head commit, evidence before "done", your own signing setup, no force pushes outside an approved history rewrite, and the repository's own templates first. Each task's procedure is read only when it starts.
- **Breaking:** the plugin now ships hooks, which need `python3` 3.12 or later. They deny the `pr-tracker` and `repo-auditor` agents the `git` and `gh` commands that change state, the GitHub MCP tools that write (on any server whose name contains `github` or `GitHub`) and file writes in your project. They also name the skill on a session's first GitHub call, and give Claude its pull request or cleanup state back after a compaction. Your own session and every other agent are never blocked.
- Claude now creates and merges pull requests with `gh`, falling back to the GitHub MCP tools, and a merge goes through only at the head commit you approved.
- The audit's read-only steps run in the new `repo-auditor` agent. What an agent could not inspect, Claude checks itself in the same run.
- The `pr-tracker` agent can no longer write files.

### Added

- PR titles, bodies and labels written from the repository's templates, or the plugin's four (standard, bug fix, hotfix, maintenance), and checked by a script before the PR is opened. Squash and merge messages from a template.
- Issues: written in the layout of the repository's forms, triaged, and marked as duplicates. Discussions: started in the right category or answered.
- Repository setup: PR templates, seven issue forms with their `config.yml`, four discussion forms, a label set, Dependabot for GitHub Actions and `CODEOWNERS` through one pull request; missing labels and the default merge message as settings you approve. Files the repository already has are never overwritten.
- Fixing an issue ends in a pull request that resolves it. CI repair finds the workflows that fail, hang or stopped running on the default branch and lands the fix through a pull request.
- Seven scripts: PR body check, cleanup plan check, lifecycle state, branch classification, backup verification, issue and discussion form check (through uv), and a label diff.

### Fixed

- Typing the skill without a subject no longer leaves an empty subject in Claude's instructions.

## [0.4.1] - 2026-10-24

### Changed

- The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works.

## [0.4.0] - 2026-10-21

### Changed

- **Breaking:** `git-cleanup` is rewritten as an exhaustive audit and a nine-step lifecycle with two approval gates. The audit now covers the whole history from the first commit, every ref against the base (merged, squash or rebase already in the base, conflicting, unrelated), worktrees, stashes, residue of interrupted operations, large files and secret-like file names, and, through `gh`, pull requests in all states, issues, discussions, forks, Actions (failed and never re-run, stuck, scheduled, artifacts and caches), protection and rulesets, integrations and alerts. It also looks for every clone, mirror, registry entry, scheduled job and tunnel that still points at the repository. What it cannot see is listed in a coverage ledger as blocked, not reachable or declined.
- You now approve twice: first the recommendations, then the exact actions. The plan orders actions by class (backup first, then investigate, fix, integrate, publish, deletions, closing, unlinking, files, maintenance), runs a containment check before every deletion, and defines each action's proof before it runs. Validation re-reads everything and quotes raw output.
- The skill is only `SKILL.md` and ten references with the commands. It runs ordinary `git` and `gh` commands from a scratch folder, writes no scripts and installs nothing. Findings that need a bisect, a refactor or a fix go through the same report, plan and approval.
- The `pr-tracker` agent now waits for the PR's checks to finish, for up to 30 minutes or the limit you set, and then reports once, instead of returning while jobs still run. Its report adds workflows that should have run and didn't, skipped, cancelled, slow, stuck and retried jobs, runner problems, whether a failure also happens on the base branch, breaking changes, out-of-scope changes and secrets in the diff, and a comparison with the previous report.
- `auto-pr-lifecycle` no longer waits on its own and delegates every observation to the read-only `pr-tracker` agent. The skill briefs it, checks its report against a fixed list, maps its status to a lifecycle state and decides readiness itself. When the agent's wait ends with jobs still running, the skill reports `timeout` and asks you whether to keep waiting.

### Fixed

- The `pr-tracker` agent now finds your GitHub tools under any server name: this plugin's server, a server you added yourself, or a Claude app connector. It used to accept only two fixed names, so with a connector it started with no GitHub tools and reported `BLOCKED` without inspecting the PR. It now inherits your session's tools.
- `auto-pr-lifecycle` is corrected against the GitHub MCP schemas and `gh` help. State and outcome names are all snake_case (`ready_without_approval`, `awaiting_merge`, `externally_merged`, `closed_without_merge`). The skill takes an optional PR number or URL, opens a PR only when asked for one, and stops when signing fails instead of committing unsigned. A wait that ends with checks still running now has the `timeout` state it was missing. Repair replies come after the push, a branch that is behind or conflicting is updated by merging the base (never a rebase), and the same failure surviving two fixes stops the loop. Labels are discovered, created if none fits, and applied without wiping the existing ones. Cleanup sync and branch deletion have exact steps, including squash landings and stacked PRs. The tool matrix drops a `gh discussion` command that does not exist and a leftover "not run in this session" note, and adds draft-to-ready, label commands and the head guard on branch updates.

### Removed

- **Breaking:** the cleanup guard hook, `inventory.py` and the Python requirement. The README no longer asks for `python3` or a minimum Git version.

## [0.3.2] - 2026-10-19

### Changed

- The `pr-tracker` agent's instructions are reorganized into a role, a mission, rules and numbered modules (inputs, tools, procedure, status, report), in shorter sentences. The report summary and the five statuses are unchanged. The tracker no longer says it re-reads pending checks every 30 seconds, because it has no way to wait: it returns `PENDING`. The steps are numbered 1 to 8 consistently.
- The GitHub MCP tool catalog the PR skill reads is now a short reference: the tools that write (with the destructive ones marked), the tools outside GitHub's default toolsets, the early-access tools, how the token changes the list, and the tools with several operations. The full per-tool tables stay in the GitHub MCP tools page.

## [0.3.1] - 2026-10-18

### Changed

- The `pr-tracker` agent now writes every report in one fixed template: a summary of up to eight labeled lines (status, head, blockers, coverage, next action), then the snapshot, coverage, failed jobs, review findings, warnings, Dependabot, durations, changes since the last report, optimizations and next actions, with tables where items repeat. Reports read the same way every round, so a change between two of them is easy to spot.
- Every `pr-tracker` pass now also compares with the previous report (step 7), even after a docs-only change. For a merged or closed PR it stops after the snapshot and returns only the summary. It reads a `pending` combined status with zero statuses as "no commit statuses", not as checks still running.

### Fixed

- The README now shows how to use the GitHub server in the Claude app. The app can't read the plugin's token option, so it lists the server as a connector that is not added and starts its form on an OAuth sign-in that needs an OAuth app registered with GitHub. The new _In the Claude app_ section connects it with your token instead: **No sign in**, then an `authorization` header with `Bearer <token>`. It also says who can add a connector on Team and Enterprise plans, and where the app keeps the token. _Compatibility_ and _FAQ & Troubleshooting_ point there.

## [0.3.0] - 2026-10-18

### Changed

- The `pr-tracker` agent now carries its whole procedure in its own instructions: what to inspect, how to diagnose, how to pick the status, how to write the report, and which read-only GitHub tool to use for each task, with the exact parameters. It no longer reads plugin files when it starts, so it also drops its `Read`, `Grep` and `Glob` tools.

### Removed

- The internal `github-operations:pr-diagnostics` skill, which you could not invoke: only the `pr-tracker` agent loaded it, and its content now lives in the agent itself. Nothing changes in how you use the plugin.

### Fixed

- The README now covers a plugin you turned on in claude.ai. Claude Code loads it as `github-operations@synced` and doesn't ask for its token, so the GitHub server doesn't start and `/plugin` lists `github` under **Needs attention** with `Plugin option "github_token" isn't set`. _Configuration_ and _Troubleshooting_ now give the fix: `/plugin configure github-operations@synced`, then `/reload-plugins`.
- The `pr-tracker` report now opens with a short summary that stands on its own: the status and why, each merge blocker with who must act, the coverage gaps and the next action. A report that reaches Claude cut short no longer loses them.
- The `pr-tracker` agent now reports `BLOCKED`, not `ACTION_REQUIRED`, when the only thing standing in the way is something only an outside party can clear, such as an expired CI secret or a service outage. It also says when the failing check isn't required. When every outside blocker is a check that isn't required, `auto-pr-lifecycle` doesn't stop there: it checks readiness itself and names the failure when it asks you to approve the merge.
- Every `pr-tracker` round re-reads everything, Dependabot alerts included, even after a docs-only change. Anything taken from an earlier report is labeled as carried over, never shown as current.

## [0.2.0] - 2026-10-18

### Changed

- **Breaking:** the GitHub MCP server takes your token from the plugin's new `github_token` option instead of the `GITHUB_PAT` environment variable. Claude Code asks for it when you install the plugin from a session and keeps it in your system's secure credential store, so the server now connects when you start Claude Code from the desktop app or an editor, not only from a shell that sets the variable. Updating doesn't ask for the token or move it, and the GitHub server stays out of `/mcp` until you set it: run `/plugin configure github-operations@the-claude-factory`, or `jq -n '{github_token: env.GITHUB_PAT}' | claude plugin configure github-operations@the-claude-factory --values-stdin` from a shell where `GITHUB_PAT` is set and restart Claude Code. The README's _Coming from 0.1.x?_ has the details.

### Fixed

- The command guard now also denies commands that print the secure store where Claude Code keeps plugin tokens: reading `.credentials.json`, also through a wildcard such as `~/.claude/.cred*`, searching your Claude Code config folder or a folder above it recursively (`~/.claude`, its absolute path or `$CLAUDE_CONFIG_DIR`), and macOS `security` commands that print a password (`find-generic-password` or `find-internet-password` with `-w` or `-g`, `dump-keychain`, `export`, and `security -i`, which reads its commands from input). Looking up a keychain entry without printing its password still passes. A recursive search of a secret folder itself, such as `grep -r … ~/.ssh`, is now denied too, as reading a file inside it already was; listings such as `git log --stat -- .docker` still pass.

## [0.1.1] - 2026-10-17

### Fixed

- The command guard now denies commands that print your GitHub token variable, `$GITHUB_PAT`, as it already did for `$GH_TOKEN` and similar names.
- The GitHub MCP tool list now includes `delete_repository`, which a classic token hides without the `delete_repo` scope and a fine-grained token lists, leaving GitHub to refuse the call without permission, and the README shows how to block it. The `X-MCP-Readonly` note lists every value that counts as false: `f` and `n` join `false`, `no`, `0` and `off`, and spaces and letter case are ignored.
- The README now says that Git 2.38 or later adds the merge preview of each branch, and that older Git reports it as unavailable and the audit continues.

## [0.1.0] - 2026-10-15

### Added

- `github-operations:auto-pr-lifecycle` skill: takes a pull request from any stage to merge. It validates and pushes your work, opens or finds the PR, sends the `pr-tracker` agent to watch the checks and reviews, fixes what fails, answers review threads and repeats until the PR is ready, then asks for your approval for that exact commit before it merges, deletes the branch and syncs.
- `github-operations:pr-tracker` agent: a read-only monitor with no shell. It reports failed jobs with their step and log excerpt, job durations, review findings, deprecation warnings and Dependabot alerts, with each cause labeled confirmed, likely or uncertain.
- `github-operations:pr-diagnostics` skill: the inspection procedure and report format the agent follows, preloaded into it.
- The GitHub MCP server, bundled. It reads your token from the `GITHUB_PAT` environment variable and connects with every toolset and GitHub's early-access mode. The README explains where to keep the token and how to reduce what Claude can use, and [GitHub MCP tools](../../docs/github-mcp-tools.md) lists every tool.
- `github-operations:git-cleanup` skill, started only with `/github-operations:git-cleanup [path] [problem]`: audits a repository end to end (context, every local and remote branch with its exclusive work, linked worktrees, stashes, pull requests, files and noise, history, reflog), presents findings and a numbered cleanup plan with a mandatory backup that is part of every approval, and executes and verifies only the actions you approve. It includes the read-only `inventory.py` and a `PreToolUse` guard that refuses force-pushes, deleting `main` on the remote, history-rewriting tools, `git clean -x`, default-branch changes and secret reads, and asks before every command that changes state. Its guard hook and `inventory.py` need `python3` 3.9 or later on `PATH`; without it the guard blocks every action.

### Changed

- **Git Hygiene is now part of this plugin.** Its `cleanup` skill is `git-cleanup`: type `/github-operations:git-cleanup` where you used to type `/git-hygiene:cleanup`. The marketplace renames the old plugin, so existing installs move over. The temporary backup refs are now `refs/git-cleanup-backup/*` and the guard's messages start with `git-cleanup:`.

### Fixed

- `git-cleanup` inventory: `--from` with a saved file that is not a JSON object reports a JSON error and exits 0, instead of ending with a traceback.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/github-operations--v0.7.3...HEAD
[0.7.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.7.3
[0.7.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.7.2
[0.7.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.7.1
[0.7.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.7.0
[0.6.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.6.1
[0.6.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.6.0
[0.5.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.5.1
[0.5.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.5.0
[0.4.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.4.1
[0.4.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.4.0
[0.3.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.3.2
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.3.0
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.2.0
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.1.0
