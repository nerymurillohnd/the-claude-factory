<div align="center">

# 🐙 GitHub Operations

<p><strong>Carries a GitHub pull request from open to merge, cleans up a Git repository without losing work, and brings the GitHub MCP server with it.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fgithub-operations%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Development-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.295-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Configuration](#-configuration) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it works on repositories on your computer through `git` and `gh`, and the cleanup's safety guard is a hook that has to check every command Claude runs, which a chat conversation in the Claude app doesn't run. The plugin is built and tested for Claude Code only.

> [!TIP]
> **TL;DR** — Type `/github-operations:auto-pr-lifecycle` and Claude takes your pull request all the way to merge: it watches the checks, fixes what fails, answers the reviews and stops only to ask you before the merge. Type `/github-operations:git-cleanup` and it audits a whole repository and runs only the cleanup steps you approve.

## ✨ Why use it

- **A pull request that finishes itself** — Claude opens or picks up the PR, then loops: a read-only agent watches CI, runs and reviews and reports what failed and why, Claude fixes it, pushes and sends the agent again, until everything is green and no findings remain.
- **You keep the one decision that matters** — Claude asks for your approval right before the merge, for that exact PR and that exact commit. A new push voids the approval.
- **Reports you can act on** — failed jobs with the step and the log excerpt, the jobs that took the longest, review findings counted without double counting, deprecation warnings and Dependabot alerts, each with a cause labeled confirmed, likely or uncertain.
- **Nothing valuable gets lost in a cleanup** — every branch is compared with the base branch commit by commit, a backup you can restore is made and tested before anything is deleted, and you approve each numbered step.
- **GitHub tools ready to use** — the GitHub MCP server comes with the plugin, so Claude reads and writes GitHub through structured tools, and falls back to `gh` when a tool is missing.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `github-operations:auto-pr-lifecycle` | Drives a pull request from any stage to merge: validate, push, watch, repair, resolve threads, ask, merge, clean up and sync | `/github-operations:auto-pr-lifecycle`, or automatically when you ask to open, ship, babysit or land a PR |
| 🎯 Skill | `github-operations:git-cleanup` | Audits a Git repository, builds the cleanup plan with you, then executes and verifies what you approve | `/github-operations:git-cleanup` only; Claude never starts it on its own |
| 🎯 Skill | `github-operations:pr-diagnostics` | The inspection procedure and report format the tracker agent follows | Preloaded by the agent; not meant to be run directly |
| 🤖 Agent | `github-operations:pr-tracker` | Read-only monitor of a PR's checks, jobs, logs, reviews, warnings and security alerts; reports to Claude | Launched by `auto-pr-lifecycle` on every monitoring cycle |
| 🪝 Hook | `PreToolUse` | Refuses dangerous commands and secret reads during a cleanup, and asks you to confirm every command that changes state | Automatically, from the moment you start `git-cleanup` until the session ends |
| 🔌 MCP server | `github` | GitHub's remote MCP server: pull requests, issues, Actions, security alerts and more | Tools appear as `mcp__plugin_github-operations_github__*` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.295 or later — check with `claude --version` |
| **Surfaces** | Claude Code only. See [Compatibility](#-compatibility) |
| **External tools** | `git` and `python3` 3.9 or later on `PATH`. `gh` signed in, to read run logs, rerun jobs, enable auto-merge and delete branches, and as the fallback when a GitHub MCP tool is missing. On Windows, Git for Windows |
| **Accounts / API keys** | A GitHub personal access token for the bundled MCP server, entered when you configure the plugin (see [Configuration](#-configuration)). Without it the server shows as failed in `/mcp` and Claude uses `gh` |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install github-operations --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install github-operations@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install github-operations --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install github-operations@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers it step by step.

### Coming from Git Hygiene?

Git Hygiene is now part of this plugin and no longer exists on its own. The marketplace renames it, so an existing install moves to GitHub Operations by itself. The command changed: type `/github-operations:git-cleanup` where you used to type `/git-hygiene:cleanup`. Nothing else about the cleanup changed.

## 🚀 Usage

### Take a pull request to merge

```text
/github-operations:auto-pr-lifecycle
```

You can also just say "open a PR for this", "get this PR merged" or "babysit PR 42". **Result:** Claude validates and pushes your work, opens the PR with the labels your repository uses, and starts the loop. While checks run, nothing interrupts you. When something fails, Claude reads the cause, fixes it, pushes and checks again. When everything is green and every review thread is answered, it stops with one question:

```text
PR #42 "Add invoice export" — head 4675bb2, squash merge into main.
All 9 checks pass, 0 unresolved threads, 1 non-blocking deprecation warning.
Merge this PR at this commit?
```

Answer yes and Claude merges, deletes the branch and syncs your local `main`. Say no or not yet and it stops there, with nothing merged.

### Clean up a repository

```text
/github-operations:git-cleanup
```

**Result:** Claude audits the repository: how many branches (local and remote), which are fully integrated, which hold work that exists nowhere else, worktrees pointing at folders that are gone, stashes, open pull requests, and noise such as `.DS_Store` or caches. It asks you about anything ambiguous, with its recommendation, then presents a plan like this:

```text
A-01  prep           Back up every ref, stash and file at risk to ~/git-backups/my-repo-2026-10-14
A-02  integrate      Merge feat/invoices into main (clean merge preview, 3 exclusive commits)
A-03  publish        Push main to origin (a plain push, never a force-push)
A-04  local-delete   Delete local branch feat/old-login (content already in main; patch-equivalent)
A-05  local-delete   Prune the worktree registration ../wt-hotfix (folder is gone; branch merged)
A-06  remote-delete  Delete origin/feat/old-login (no open pull request, you are the only author)
```

Approve the whole plan, tell Claude which IDs to run, or stop with the audit only. The backup (A-01) always comes first and is part of every approval. Nothing else happens.

Pass an absolute path to clean another repository, or text that is not a folder to investigate a problem:

```text
/github-operations:git-cleanup /Users/ada/code/other-repo
/github-operations:git-cleanup find out who introduced the failing date parsing
```

## 🔧 Configuration

Set both options from `/plugin` → **Installed** → **GitHub Operations** → **Configure options**.

| Option | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `github_token` | string, sensitive | — | A GitHub personal access token. The bundled MCP server sends it as a Bearer header. It is stored in your system keychain. |
| `github_mcp_url` | string | `https://api.githubcopilot.com/mcp/x/all` | Which tools the GitHub MCP server offers. The default exposes **every toolset, including tools that write and delete**. |

> [!WARNING]
> **The default is the full tool set.** `https://api.githubcopilot.com/mcp/x/all` offers every GitHub MCP toolset: pull requests, issues, Actions (including rerunning and cancelling runs), projects, discussions, notifications and more, and the tools that create, merge, delete and write. What Claude can actually do is also limited by your token, so create a fine-grained token for the repositories you work in and grant only the permissions you want Claude to have.

To offer fewer tools, change `github_mcp_url` and run `/reload-plugins`:

| Goal | URL |
| :-- | :-- |
| Everything, read-only | `https://api.githubcopilot.com/mcp/x/all/readonly` |
| GitHub's default toolsets | `https://api.githubcopilot.com/mcp/` |
| Default toolsets, read-only | `https://api.githubcopilot.com/mcp/readonly` |
| One toolset, for example issues | `https://api.githubcopilot.com/mcp/x/issues` |

The pull request loop needs the Actions and security toolsets to read job logs and Dependabot alerts. With a narrower URL, Claude reads them through `gh` instead. To block one tool, add a deny rule for it in your settings, for example `mcp__plugin_github-operations_github__delete_file`. To use your own GitHub MCP server instead, turn this one off in `/mcp`.

## 🔄 Updating

```bash
claude plugin update github-operations@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **GitHub Operations** → **Update now**. Then run `/reload-plugins`.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall github-operations@the-claude-factory
```

In a session: `/plugin` → **Installed** → **GitHub Operations** → **Uninstall**. Your saved token is removed with it.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ they load, but they need `git`, `gh` and your repository on your computer, and the cleanup guard hook that protects your repository doesn't run in a chat conversation, so use Claude Code |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |
| 🔌 MCP server (remote) | ✅ | ⚠️ the Claude app doesn't prompt for the token option |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/github-operations:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>The GitHub server shows as failed or "needs authentication" in <code>/mcp</code>.</b></summary>

You haven't set the token, or GitHub rejected it. Set `github_token` in `/plugin` → **Installed** → **GitHub Operations** → **Configure options**, then run `/reload-plugins`. Until then the monitoring agent has no GitHub tools, so Claude reads GitHub through `gh` itself.

</details>

<details>
<summary><b>Will Claude merge my PR without asking?</b></summary>

No. It always stops and asks before the merge, naming the PR, the commit, the merge method and any automatic deployment it knows about. Your approval covers that commit only: if anyone pushes again, Claude asks again. It never force-pushes, skips hooks or required checks, or uses admin rights to get around a rule.

</details>

<details>
<summary><b>Can the monitoring agent change anything on GitHub?</b></summary>

No. It has no shell and only read-only GitHub tools, so it cannot comment, resolve, rerun, merge or push. It reports, and Claude does everything else.

</details>

<details>
<summary><b>How long will Claude wait for a slow pipeline?</b></summary>

It keeps checking within a time budget and then hands control back with what it knows, so it never hangs on a pipeline that takes many minutes. Claude then starts another monitoring round.

</details>

<details>
<summary><b>Claude Code asks me to confirm almost every command during the cleanup.</b></summary>

That is the guard. Every `git` or `gh` command that changes the repository, its remotes or its pull requests, every file write, deletion or move, every MCP action that is not a plain read, and every command that prints file contents asks you first, with the reason. Approve a prompt only when it matches the action ID you approved in the plan. Approving the plan is not approving a prompt, and approving a prompt is not approving the plan: you get two checks on every change.

</details>

<details>
<summary><b>What does the cleanup refuse to do, even if I approve?</b></summary>

Force-push, delete `main` on the remote, rewrite published history (`filter-branch`, `filter-repo`), change the remote's default branch, run `git clean -x`, and print remote URLs or tokens that may contain credentials. If you need one of those, do it yourself outside the cleanup. The guard is a safety net against honest mistakes, not a sandbox, and a settings-file mod that approves tool calls can override a plugin hook's refusal.

</details>

<details>
<summary><b>Does the cleanup read my <code>.env</code> files?</b></summary>

No. Files that look like secrets (`.env`, keys, certificates, token and credential files) are listed by name only. The guard refuses commands and file reads that name them, and the cleanup never deletes or copies them. Commits can still contain secrets, so Claude audits with `--stat` and name listings, and any command that would print file contents asks for your confirmation first.

</details>

<details>
<summary><b>Should I run the cleanup in bypass-permissions mode?</b></summary>

No. Use the default permission mode, so every change reaches you as a prompt. The guard's refusals are applied before your permission rules, but Claude Code does not document how confirmation prompts behave when permissions are bypassed.

</details>

<details>
<summary><b>Every command is blocked with a "hook error" and <code>python3</code> not found.</b></summary>

The cleanup guard needs `python3` 3.9 or later on `PATH`. If it cannot run, Claude Code blocks the action instead of letting it through, so the cleanup stops safely. Install Python 3 (or fix `PATH`) and start the cleanup again.

</details>

<details>
<summary><b>Can I run them with <code>claude -p</code>?</b></summary>

Only the read-only cleanup audit is meant for it. The cleanup plan needs your approval and every command that changes anything needs your confirmation, and the pull request loop needs your approval before the merge. A headless run has nobody to give any of them, so Claude Code refuses them. Run both in an interactive session.

</details>

<details>
<summary><b>My remote is not on GitHub.</b></summary>

The cleanup of branches, worktrees, stashes and files works with any remote. Pull requests, repository visibility and branch protections come from GitHub; for other hosts they are reported as blocked and nothing that depends on them is touched. The pull request loop is GitHub only.

</details>

<details>
<summary><b>Where is the cleanup backup, and when is it deleted?</b></summary>

In a folder outside the repository that you choose in the plan. Claude never deletes it on its own: when the cleanup is verified it asks whether to keep or remove it, and removes it only after an explicit yes.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 🔁 [Session Handoff](../session-handoff#readme) — write down where a session stopped, including the repository state, before you start a cleanup

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=github-operations) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=github-operations) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=github-operations)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
