<div align="center">

# 🧹 Git Hygiene

<p><strong>Audits a Git repository end to end, plans the cleanup with you, and executes only what you approve, keeping every piece of valuable work safe.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fgit-hygiene%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Development-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.295-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it works on a repository on your computer, and its safety guard is a hook that has to check every command Claude runs, which a chat conversation in the Claude app doesn't run. The plugin is built and tested for Claude Code only.

> [!TIP]
> **TL;DR** — Type `/git-hygiene:cleanup` and Claude audits the whole repository, shows you a numbered cleanup plan, and carries out only the steps you approve, after a verified backup, until the repository is down to `main` and `origin/main`.

## ✨ Why use it

Old branches, forgotten stashes, worktrees whose folders are gone and pull requests nobody remembers pile up in every long-lived repository. Cleaning them by hand is risky, because the one branch you delete is the one with work that exists nowhere else.

- **Nothing valuable gets lost** — before anything is proposed, every branch is compared with the base branch, commit by commit for unmerged work, so "looks merged" is never taken for granted. Work that is already in `main` under other commits (a squash merge, a cherry-pick) is recognized; work that is not stays.
- **You approve every step** — the audit is read-only and changes nothing, not even a fetch. The plan gives each operation an ID, its evidence, risk and backup coverage, and Claude runs only the IDs you approve.
- **A backup you can restore** — before anything is deleted, Claude writes a bundle of every ref, stash and file at risk outside the repository, restores it into a scratch repository to prove it works, and keeps it until you say it can go.
- **Safe where it matters** — a guard refuses force-pushes, deleting `main` on the remote, history-rewriting tools and changing the default branch, and makes you confirm every command, file write or MCP action that changes anything. It watches shell commands, file reads and searches, file writes and MCP tools, and refuses to read or print your `.env` files and keys.
- **Built for big repositories** — a read-only inventory gathers branches, worktrees, stashes, noise and history in one pass, with aggregated queries instead of a history dump, and measures unmerged branches in depth, newest first, within a time budget, so a repository with thousands of commits and branches stays workable. Anything it had to skip is reported, never hidden.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `git-hygiene:cleanup` | Audits the repository, builds the cleanup plan with you, then executes and verifies what you approve | `/git-hygiene:cleanup` only; Claude never starts it on its own |
| 🪝 Hook | `PreToolUse` | Refuses dangerous commands and secret reads, and asks you to confirm every command that changes state | Automatically, on every command, from the moment you start the cleanup until the session ends |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.295 or later — check with `claude --version` |
| **Surfaces** | Claude Code only. See [Compatibility](#-compatibility) |
| **External tools** | `git` 2.38 or later (older versions work, without the merge preview) and `python3` 3.9 or later on `PATH`, for the guard and the inventory. `gh` signed in, optional, to read pull requests, repository visibility and branch protections; without it those items are reported as blocked. On Windows, Git for Windows |
| **Network** | Read-only queries of your remote (`git ls-remote`, `gh`). A `git fetch`, a push or a remote branch deletion happens only if you approve it |
| **Accounts / API keys** | None. `git` and `gh` use the credentials you already have |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install git-hygiene --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install git-hygiene@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install git-hygiene --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install git-hygiene@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers it step by step.

## 🚀 Usage

### Clean up the current repository

```text
/git-hygiene:cleanup
```

**Result:** Claude runs the audit and reports what it found: how many branches (local and remote), which are fully integrated, which hold work that exists nowhere else, worktrees pointing at folders that are gone, stashes, open pull requests, and noise such as `.DS_Store` or caches. It asks you about anything ambiguous, with its recommendation, then presents a plan like this:

```text
A-01  prep           Back up every ref, stash and file at risk to ~/git-backups/my-repo-2026-10-14
A-02  integrate      Merge feat/invoices into main (clean merge preview, 3 exclusive commits)
A-03  publish        Push main to origin (a plain push, never a force-push)
A-04  local-delete   Delete local branch feat/old-login (content already in main; patch-equivalent)
A-05  local-delete   Prune the worktree registration ../wt-hotfix (folder is gone; branch merged)
A-06  remote-delete  Delete origin/feat/old-login (no open pull request, you are the only author)
```

Approve the whole plan, tell Claude which IDs to run, or stop with the audit only. The backup (A-01) always comes first and is part of every approval. Nothing else happens.

### Clean up another repository

```text
/git-hygiene:cleanup /Users/ada/code/other-repo
```

Use an absolute path.

### Only audit

Choose "audit only" when Claude asks you to approve the plan (or refuse it). You keep the findings and the draft plan, and the repository is untouched.

### Look into a specific problem

```text
/git-hygiene:cleanup find out who introduced the failing date parsing
```

When the text is not a folder, Claude works on the current repository and treats it as a problem to investigate: it also uses `git grep`, `git blame` and, with your approval, `git bisect` in an isolated checkout.

## 🔄 Updating

```bash
claude plugin update git-hygiene@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Git Hygiene** → **Update now**. Then run `/reload-plugins`.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall git-hygiene@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Git Hygiene** → **Uninstall**.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads, but the guard hook that protects your repository doesn't run in a chat conversation, so use Claude Code |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

The guard is a hook declared inside the skill. Chat conversations in the Claude app don't run hooks, and the cleanup needs your repository on your computer, so use Claude Code.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/git-hygiene:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Claude Code asks me to confirm almost every command during the cleanup.</b></summary>

That is the guard. Every `git` or `gh` command that changes the repository, its remotes or its pull requests, every file write, deletion or move, every MCP action that is not a plain read, and every command that prints file contents asks you first, with the reason. Approve a prompt only when it matches the action ID you approved in the plan. Approving the plan is not approving a prompt, and approving a prompt is not approving the plan: you get two checks on every change.

</details>

<details>
<summary><b>Can Claude start the cleanup by itself?</b></summary>

No. The skill runs only when you type `/git-hygiene:cleanup`, and Claude cannot invoke it on its own.

</details>

<details>
<summary><b>What does Claude refuse to do, even if I approve?</b></summary>

Force-push, delete `main` on the remote, rewrite published history (`filter-branch`, `filter-repo`), change the remote's default branch, run `git clean -x`, and print remote URLs or tokens that may contain credentials. If you need one of those, do it yourself outside the cleanup. The guard is a safety net against honest mistakes, not a sandbox, and a settings-file mod that approves tool calls can override a plugin hook's refusal.

</details>

<details>
<summary><b>Does it read my <code>.env</code> files?</b></summary>

No. Files that look like secrets (`.env`, keys, certificates, token and credential files) are listed by name only. The guard refuses commands and file reads that name them, and the cleanup never deletes or copies them. Commits can still contain secrets, so Claude audits with `--stat` and name listings, and any command that would print file contents asks for your confirmation first.

</details>

<details>
<summary><b>What happens to branches that other people pushed?</b></summary>

They are kept unless you decide otherwise. Remote deletions are judged one by one against repository visibility, branch protections, the branch's authors and open pull requests; a branch with an open pull request is never a deletion candidate on its own.

</details>

<details>
<summary><b>Should I run it in bypass-permissions mode?</b></summary>

No. Use the default permission mode, so every change reaches you as a prompt. The guard's refusals are applied before your permission rules, but Claude Code does not document how confirmation prompts behave when permissions are bypassed.

</details>

<details>
<summary><b>Every command is blocked with a "hook error" and <code>python3</code> not found.</b></summary>

The guard needs `python3` 3.9 or later on `PATH`. If it cannot run, Claude Code blocks the action instead of letting it through, so the cleanup stops safely. Install Python 3 (or fix `PATH`) and start the cleanup again.

</details>

<details>
<summary><b>Can I run it with <code>claude -p</code>?</b></summary>

Only the read-only audit is meant for it. The plan needs your approval and every command that changes anything needs your confirmation, and a headless run has nobody to give either, so Claude Code refuses them. Run the cleanup in an interactive session.

</details>

<details>
<summary><b>My remote is not on GitHub.</b></summary>

The audit and the cleanup of branches, worktrees, stashes and files work with any remote. Pull requests, repository visibility and branch protections come from GitHub through `gh`; for other hosts they are reported as blocked and nothing that depends on them is touched.

</details>

<details>
<summary><b>Where is the backup, and when is it deleted?</b></summary>

In a folder outside the repository that you choose in the plan. Claude never deletes it on its own: when the cleanup is verified it asks whether to keep or remove it, and removes it only after an explicit yes.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 🔁 [Session Handoff](../session-handoff#readme) — write down where a session stopped, including the repository state, before you start a cleanup

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=git-hygiene) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=git-hygiene) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=git-hygiene)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
