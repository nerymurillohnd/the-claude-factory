<div align="center">

# 🛑 Block No Verify

<p><strong>Blocks Claude's git commands that skip commit hooks or signing (--no-verify, --no-gpg-sign, commit.gpgsign=false), so your quality gates always run.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fblock-no-verify%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Security-6B7280)](../../README.md#-catalog)
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

> [!TIP]
> **TL;DR** — Install it once. When Claude tries `git commit --no-verify`, `--no-gpg-sign` or `-c commit.gpgsign=false`, the command is stopped before it runs, and Claude is told to run it properly and fix the failing hook instead. There is nothing to configure.

## ✨ Why use it

A pre-commit hook fails, and the quickest way for an agent to get past it is to skip it. Your linter, your tests, your secret scan and your commit signing then check nothing.

- **Your gates keep their meaning** — a hook that fails gets fixed, not skipped. Claude cannot talk its way past a check that runs before the command does.
- **Claude gets the reason, not a dead end** — the denial names the flag it found and says what to do: run the command without it and fix the cause.
- **It reads the command, not just the flag** — it catches `-n` on `commit` and `am`, the abbreviations git accepts (`--no-veri`), a flag moved to the next line with a backslash, `sudo`, `env` and `timeout` in front, and `bash -c` or `eval` up to three levels deep.
- **Normal work is untouched** — a commit message that mentions `--no-verify`, `git push -n` (a dry run), and Claude's usual `git commit -m "$(cat <<'EOF' …)"` all pass.
- **Nothing to set up** — one hook, no accounts, no network, no files written.
- **Fast** — about 40 ms per Bash command, most of it Python starting up.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🪝 Hook | `PreToolUse` on Bash | Reads each Bash command and denies a git command that skips commit hooks or signing. Every other command passes without a word | Automatically, on every Bash command, in the main conversation and in subagents |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.295 or later — check with `claude --version`. The hook uses the `onFailure` field, which older versions ignore: a hook that cannot start would then let the command through without a word |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | `python3` 3.9 or later on your `PATH`, to run the guard — check with `python3 --version`. Install it with `xcode-select --install` or `brew install python` on macOS, your package manager on Linux (`sudo apt install python3`, `sudo dnf install python3`), or the installer from [python.org](https://www.python.org/downloads/) on any system. On Windows, use Git Bash with `python3` on your `PATH`: the python.org installer names the program `python`, so add a `python3` alias. Without Python the guard tells you it is inactive and blocks nothing: see [Limitations](#-limitations) |
| **Accounts / API keys** | None |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install block-no-verify --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install block-no-verify@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install block-no-verify --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install block-no-verify@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**. Run `/reload-plugins` to start the guard in the session you are in.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Block No Verify** in **Discover** and select **Add**.

In the desktop app's **Code** tab you can also click **+** → **Plugins** → **Add plugin**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

There is nothing to run: the guard watches every Bash command. Work as you always do.

### See it stop a bypass

```text
Commit my changes. The pre-commit hook fails, so just skip it with --no-verify.
```

**Result:** the command never runs. Claude reads this and goes back to fix the failing hook:

```text
block-no-verify: this command skips Git's commit hooks or signing (--no-verify). Run it without --no-verify so the project's checks run. If a hook fails, fix the cause; do not bypass it.
```

Claude Code labels the message `PreToolUse:Bash hook error`. That is how it shows any denial from a hook, not a fault in the plugin.

### What it stops and what it lets through

| Claude runs | Result |
| :-- | :-- |
| `git commit --no-verify -m "x"`, `git push --no-verify`, `git merge --no-verify b` | 🚫 Denied |
| `git commit -n`, `git commit -nm "x"`, `git am -n p.patch` | 🚫 Denied: `-n` is `--no-verify` in `commit` and `am` |
| `git commit --no-veri -m "x"`, `git commit --no-g -m "x"` | 🚫 Denied: git runs these abbreviations as the full flags |
| `git commit --no-gpg-sign`, `git -c commit.gpgsign=false commit`, `git -c tag.gpgsign=off tag v1` | 🚫 Denied: unsigned commits and tags |
| `sudo git commit --no-verify`, `env X=1 git push --no-verify`, `timeout 5 git commit -n` | 🚫 Denied: wrappers and variables in front are looked through |
| `bash -c 'git commit --no-verify'`, `eval "git commit -n"` | 🚫 Denied: up to three levels deep. A fourth is denied as too deep to inspect |
| `git commit -m "docs: explain --no-verify"` | ✅ Passes: the message is text |
| `git push -n`, `git merge -n`, `git pull -n`, `git cherry-pick -n` | ✅ Pass: `-n` means dry run, no diffstat or no commit there |
| ``git commit -m "$(cat <<'EOF' … EOF)"``, even with quotes or a line that starts with `git` in the message | ✅ Passes: a quoted heredoc that feeds a plain `git commit` or `git tag` is the message |
| `bash <<'EOF' … EOF`, `cat <<'EOF' \| bash` | 🚫 Checked as commands: a shell runs that text |

A command the guard cannot read, such as an unterminated quote, is denied with that reason, so a parse failure never lets a bypass through.

## 🔐 Permissions

| Access | What the plugin does |
| :-- | :-- |
| Read | The Bash command Claude is about to run, which Claude Code passes to the hook. Nothing else |
| Write | None |
| Process | Starts `python3` to run its own script. It never runs, changes or re-runs your command |
| Network | None |
| Credentials | None |

## 🚧 Limitations

The guard is a barrier for Claude, not a security boundary. Claude Code's own documentation says to enforce a hard allow or deny through [permissions](https://code.claude.com/docs/en/permissions); use branch protection and CI for what must hold for everyone.

| Limitation | What you see | What to do |
| :-- | :-- | :-- |
| It only sees commands Claude runs | A bypass you type in your own terminal runs | Nothing: that is your decision |
| Other ways to skip hooks are not checked: `-c core.hooksPath=…`, switches such as `HUSKY=0`, git aliases, scripts that run git, and a command built from variables or command substitution | The command runs | Protect what must hold with CI and branch protection |
| Only the Bash tool is guarded. The PowerShell tool, if you turn it on with `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`, is not | Its commands run unchecked | Leave the PowerShell tool off, or deny what you care about with a `PowerShell(...)` [permission rule](https://code.claude.com/docs/en/permissions#powershell) |
| Your organization can turn hooks off with `allowManagedHooksOnly`, or you with `disableAllHooks` | The guard does nothing | Check `/plugin` and your settings |
| No Python 3.9 or later on `PATH` | Every Bash command shows a notice that the guard is inactive; nothing is blocked | Install Python (see [Requirements](#-requirements)) and run `/reload-plugins` |
| The guard itself fails after Python starts | Claude Code blocks the Bash command and shows the error | Run `/reload-plugins`; if it keeps failing, [report it](#-found-a-problem) |
| In a Claude app chat conversation hooks do not run | No guard | Use a Cowork session or Claude Code |

## 🔄 Updating

```bash
claude plugin update block-no-verify@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Block No Verify** → **Update now**. Then run `/reload-plugins`.

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `block-no-verify@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall block-no-verify@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Block No Verify** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Block No Verify** → its menu → **Remove**.

The plugin keeps no data and writes no files, so nothing is left behind.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🪝 Hooks | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

In Claude Code the guard also covers subagents, and it keeps running under `bypassPermissions`.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>How do I know it is working?</b></summary>

In a scratch repository, ask Claude to run `git commit --no-verify -m test`. It should come back with the message shown in [Usage](#-usage), and no commit should appear in `git log`. A plain `git commit -m test` is not touched.

</details>

<details>
<summary><b>A command with a quoted message was denied. Why?</b></summary>

A message in quotes, a `-m "$(cat <<'EOF' …)"` heredoc and `-F -` with a quoted heredoc all pass. A command the guard cannot read is denied with the reason `could not inspect this command`: an unterminated quote is the usual cause. An unquoted heredoc (`<<EOF`) is checked line by line, because the shell expands `$(…)` inside it. If a harmless command is denied, [report it](#-found-a-problem) with the command.

</details>

<details>
<summary><b>I need to skip a hook once. What do I do?</b></summary>

Run the command yourself in your terminal: the guard only watches Claude. To turn it off for good, run `claude plugin disable block-no-verify@the-claude-factory`.

</details>

<details>
<summary><b>Does it block <code>git push --force</code>?</b></summary>

No. It only blocks what skips commit hooks or signing: `--no-verify`, `--no-gpg-sign`, `-n` on `commit` and `am`, and a false `commit.gpgsign` or `tag.gpgsign`.

</details>

<details>
<summary><b>Does it slow Claude down?</b></summary>

By about 40 ms per Bash command, measured on an Apple M4 with Python 3.15: 36 ms at the median and under 42 ms for 95 of 100. Almost all of it is Python starting up; reading the command takes a few microseconds.

</details>

<details>
<summary><b>Every Bash command shows "block-no-verify is inactive".</b></summary>

Python 3.9 or later is missing or not on `PATH`. Install it (see [Requirements](#-requirements)), then run `/reload-plugins`. Until then nothing is blocked.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- 🐙 [GitHub Operations](../github-operations/README.md) — takes a pull request from branch to merge, and pairs with a guard that keeps its commits honest

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=block-no-verify) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=block-no-verify) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=block-no-verify)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
