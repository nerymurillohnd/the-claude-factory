# Changelog

All notable changes to **GitHub Operations** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2026-10-18

### Changed

- The `pr-tracker` agent now writes every report in one fixed template: a summary of up to eight labeled lines (status, head, blockers, coverage, next action), then the snapshot, coverage, failed jobs, review findings, warnings, Dependabot, durations, changes since the last report, optimizations and next actions, with tables where items repeat. Reports read the same way every round, so a change between two of them is easy to spot.
- Every `pr-tracker` pass now also compares with the previous report (step 7), even after a docs-only change. For a merged or closed PR it stops after the snapshot and returns only the summary. It reads a `pending` combined status with zero statuses as "no commit statuses", not as checks still running.

### Fixed

- The README now shows how to use the GitHub server in the Claude app. The app can't read the plugin's token option, so it lists the server as a connector that is not added and starts its form on an OAuth sign-in that needs an OAuth app registered with GitHub. The new *In the Claude app* section connects it with your token instead: **No sign in**, then an `authorization` header with `Bearer <token>`. It also says who can add a connector on Team and Enterprise plans, and where the app keeps the token. *Compatibility* and *FAQ & Troubleshooting* point there.

## [0.3.0] - 2026-10-18

### Changed

- The `pr-tracker` agent now carries its whole procedure in its own instructions: what to inspect, how to diagnose, how to pick the status, how to write the report, and which read-only GitHub tool to use for each task, with the exact parameters. It no longer reads plugin files when it starts, so it also drops its `Read`, `Grep` and `Glob` tools.

### Removed

- **Breaking:** the `github-operations:pr-diagnostics` skill. Only the `pr-tracker` agent loaded it, and its content now lives in the agent itself. Nothing changes in how you use the plugin.

### Fixed

- The README now covers a plugin you turned on in claude.ai. Claude Code loads it as `github-operations@synced` and doesn't ask for its token, so the GitHub server doesn't start and `/plugin` lists `github` under **Needs attention** with `Plugin option "github_token" isn't set`. *Configuration* and *Troubleshooting* now give the fix: `/plugin configure github-operations@synced`, then `/reload-plugins`.
- The `pr-tracker` report now opens with a short summary that stands on its own: the status and why, each merge blocker with who must act, the coverage gaps and the next action. A report that reaches Claude cut short no longer loses them.
- The `pr-tracker` agent now reports `BLOCKED`, not `ACTION_REQUIRED`, when the only thing standing in the way is something only an outside party can clear, such as an expired CI secret or a service outage. It also says when the failing check isn't required. When every outside blocker is a check that isn't required, `auto-pr-lifecycle` doesn't stop there: it checks readiness itself and names the failure when it asks you to approve the merge.
- Every `pr-tracker` round re-reads everything, Dependabot alerts included, even after a docs-only change. Anything taken from an earlier report is labeled as carried over, never shown as current.

## [0.2.0] - 2026-10-18

### Changed

- **Breaking:** the GitHub MCP server takes your token from the plugin's new `github_token` option instead of the `GITHUB_PAT` environment variable. Claude Code asks for it when you install the plugin from a session and keeps it in your system's secure credential store, so the server now connects when you start Claude Code from the desktop app or an editor, not only from a shell that sets the variable. Updating doesn't ask for the token or move it, and the GitHub server stays out of `/mcp` until you set it: run `/plugin configure github-operations@the-claude-factory`, or `jq -n '{github_token: env.GITHUB_PAT}' | claude plugin configure github-operations@the-claude-factory --values-stdin` from a shell where `GITHUB_PAT` is set and restart Claude Code. The README's *Coming from 0.1.x?* has the details.

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
- `github-operations:git-cleanup` skill, started only with `/github-operations:git-cleanup [path] [problem]`: audits a repository end to end (context, every local and remote branch with its exclusive work, linked worktrees, stashes, pull requests, files and noise, history, reflog), presents findings and a numbered cleanup plan with a mandatory backup that is part of every approval, and executes and verifies only the actions you approve. It includes the read-only `inventory.py` and a `PreToolUse` guard that refuses force-pushes, deleting `main` on the remote, history-rewriting tools, `git clean -x`, default-branch changes and secret reads, and asks before every command that changes state.

### Changed

- **Git Hygiene is now part of this plugin.** Its `cleanup` skill is `git-cleanup`: type `/github-operations:git-cleanup` where you used to type `/git-hygiene:cleanup`. The marketplace renames the old plugin, so existing installs move over. The temporary backup refs are now `refs/git-cleanup-backup/*` and the guard's messages start with `git-cleanup:`.

### Fixed

- `git-cleanup` inventory: `--from` with a saved file that is not a JSON object reports a JSON error and exits 0, instead of ending with a traceback.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/github-operations--v0.3.1...HEAD
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.3.0
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.2.0
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/github-operations--v0.1.0
