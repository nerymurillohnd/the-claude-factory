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
- **Claude gets the reason, not a dead end** — the denial names what it found and says what to do: run the command without it and fix the cause.
- **It reads the command, not just the flag** — it catches `-n` on `git commit`, the abbreviations git accepts (`--no-veri`), `sudo`, `env`, `time` and `exec` in front, a subshell, a brace group, `if` and loops, `$(…)` and backticks, `$'…'` quoting, `bash -c` and `eval`, and a heredoc that a shell runs.
- **It guards the configuration too** — `git config commit.gpgsign false`, `-c core.hooksPath=/dev/null`, `HUSKY=0`, `GIT_CONFIG_*` and an inline `-c alias.ci='commit --no-verify'` are stopped like the flag.
- **Normal work is untouched** — a commit message that mentions `--no-verify`, `git push -n`, a heredoc that only writes a file, and Claude's usual `git commit -m "$(cat <<'EOF' …)"` all pass.
- **Nothing to set up** — one hook, no accounts, no network, no files written. It also checks the PowerShell tool.
- **Fast** — about 30 ms per Bash command, measured inside a Claude Code session.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🪝 Hook | `PreToolUse` on Bash and PowerShell | Reads each command and denies one that runs git so that it skips commit hooks or signing. Every other command passes without a word | Automatically, on every Bash and PowerShell command, in the main conversation and in subagents |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.295 or later — check with `claude --version`. The hook uses the `onFailure` field, which older versions ignore: a hook that cannot start would then let the command through without a word |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | `bash` 3.2 or later and `jq` 1.6 or later, on your `PATH` — check with `jq --version`. macOS has both (`/usr/bin/jq`, checked on macOS 27). On Linux, install `jq` with your package manager (`sudo apt install jq`, `sudo dnf install jq`). On Windows, use Git Bash and install `jq` with `winget install jqlang.jq`. `git` is optional: the hook only reads your aliases with it. Without `jq` the hook cannot read Claude's command: see [Limitations](#-limitations) |
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

There is nothing to run: the guard watches every Bash and PowerShell command. Work as you always do.

### See it stop a bypass

```text
Commit my changes. The pre-commit hook fails, so just skip it with --no-verify.
```

**Result:** the command never runs. Claude reads this and goes back to fix the failing hook:

```text
block-no-verify: git commit --no-verify skips hooks (--no-verify). Do not retry with another bypass. Run the command without it and fix the underlying hook or signing failure; if the hook itself is wrong, ask the user to fix or skip it themselves.
```

Claude Code labels the message `PreToolUse:Bash hook error`. That is how it shows any denial from a hook, not a fault in the plugin.

### What it stops and what it lets through

| Claude runs | Result |
| :-- | :-- |
| `git commit --no-verify -m "x"`, `git push --no-verify`, `git merge --no-verify b` | 🚫 Denied |
| `git commit -n`, `git commit -nm "x"`, `git am -n p.patch` | 🚫 Denied: `-n` is `--no-verify` in `commit` and `am` |
| `git commit --no-veri -m "x"` | 🚫 Denied: git runs the abbreviation as the full flag |
| `git commit --no-gpg-sign`, `git -c commit.gpgsign=false commit`, `git -c commit.gpgsign= commit`, `git -c tag.gpgsign=off tag v1` | 🚫 Denied: unsigned commits and tags, with every spelling of false that git reads |
| `git config commit.gpgsign false`, `git -c core.hooksPath=/dev/null commit`, `HUSKY=0 git commit` | 🚫 Denied: signing or hooks switched off through configuration |
| `sudo -n git commit --no-verify`, `env git commit --no-verify`, `time git commit --no-verify`, `exec git commit --no-verify` | 🚫 Denied: what stands in front is looked through |
| `(git commit --no-verify)`, `{ git commit --no-verify; }`, `if true; then git commit --no-verify; fi`, `sleep 1 & git commit --no-verify` | 🚫 Denied: grouping, control flow and background are looked through |
| `echo "$(git commit --no-verify)"`, `` echo `git commit -n` ``, `git commit $'--no-verify'`, `g"i"t commit --no-verify` | 🚫 Denied: substitutions and quoting are read |
| `bash -c 'git commit --no-verify'`, `eval "git commit -n"`, a heredoc fed to `bash` | 🚫 Denied: text that a shell runs is checked as commands |
| `git commit -m "docs: explain --no-verify"`, `echo 'never run git commit --no-verify'` | ✅ Passes: the flag is text |
| `git push -n`, `git merge -n`, `git pull -n`, `git cherry-pick -n` | ✅ Pass: `-n` means dry run, no diffstat or no commit there |
| `cat > f <<'EOF' …`, `python3 - <<'EOF' …`, `gh pr create --body "$(cat <<'EOF' …)"`, even with an odd quote or a line that mentions `git commit --no-verify` | ✅ Pass: the heredoc only feeds a reader, so it is text |
| ``git commit -m "$(cat <<'EOF' … EOF)"`` | ✅ Passes: Claude's usual commit form |

A command the guard cannot read, such as an unterminated quote, is denied with that reason, so a parse failure never lets a bypass through.

## 🔐 Permissions

| Access | What the plugin does |
| :-- | :-- |
| Read | The command Claude is about to run, which Claude Code passes to the hook. To resolve an alias it runs `git config --get alias.<name>` in the call's folder, which only reads |
| Write | None |
| Process | `jq` to read the payload, and the read-only `git config` above. It never runs, changes or re-runs your command |
| Network | None |
| Credentials | None |

## 🚧 Limitations

The guard is a barrier for Claude, not a security boundary. Claude Code's own documentation says to enforce a hard allow or deny through [permissions](https://code.claude.com/docs/en/permissions); use branch protection and CI for what must hold for everyone.

| Limitation | What you see | What to do |
| :-- | :-- | :-- |
| It only sees commands Claude runs | A bypass you type in your own terminal runs | Nothing: that is your decision |
| Some spellings are not read: comma brace lists (`{git,} commit -n`, `git commit --{no-verify,message=x}`), `bash -c -- '…'` and `bash -c -e '…'` with options between `-c` and the script, `xargs git` fed by a heredoc, and `source <(…)` | The command runs | Protect what must hold with CI and branch protection |
| Values that come from outside the command: functions, earlier exports and scripts run from files | The command runs | Same |
| Your organization can turn hooks off with `allowManagedHooksOnly`, or you with `disableAllHooks` | The guard does nothing | Check `/plugin` and your settings |
| No `jq` on `PATH` | A command that could involve git is denied with the message `jq is not installed`; every other command runs | Install `jq` (see [Requirements](#-requirements)) |
| A command too large to analyze within the hook's time that mentions a bypass | It is denied with that reason | Run smaller commands |
| The guard itself fails | Claude Code blocks the command and shows the error | Run `/reload-plugins`; if it keeps failing, [report it](#-found-a-problem) |
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
<summary><b>A harmless command was denied. Why?</b></summary>

A message in quotes, a heredoc that only writes text and Claude's `git commit -m "$(cat <<'EOF' …)"` all pass. A command the guard cannot read is denied with the reason: an unterminated quote is the usual cause. If a harmless command is denied, [report it](#-found-a-problem) with the command.

</details>

<details>
<summary><b>I need to skip a hook once. What do I do?</b></summary>

Run the command yourself in your terminal: the guard only watches Claude. To turn it off for good, run `claude plugin disable block-no-verify@the-claude-factory`.

</details>

<details>
<summary><b>Does it block <code>git push --force</code>?</b></summary>

No. It only blocks what skips commit hooks or signing: `--no-verify`, `--no-gpg-sign`, `-n` on `commit` and `am`, and a false signing setting or a hooks setting that points away from your repository.

</details>

<details>
<summary><b>Does it slow Claude down?</b></summary>

By about 30 ms per Bash command: Claude Code logged 26 to 39 ms for the hook inside a live session. A command that has nothing to do with git or hooks is let through before any parsing.

</details>

<details>
<summary><b>The message says "jq is not installed".</b></summary>

The guard needs `jq` to read Claude's command. Install it (see [Requirements](#-requirements)); until then it denies commands that could involve git and lets the others run.

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
