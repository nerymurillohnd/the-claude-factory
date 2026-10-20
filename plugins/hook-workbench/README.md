<div align="center">

# 🪝 Hook Workbench

<p><strong>Designs, writes, audits and debugs Claude Code prompt hooks, agent hooks and background hooks, with workspace-trust and security review, checked against the live hooks reference.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fhook-workbench%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Automation-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.294-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Describe the hook you want, or point at one that misbehaves, and get a working prompt, agent or background hook, an audit with evidence, or the root cause from the debug log, checked against the current hooks docs.

## ✨ Why use it

- **Hooks that do what you meant** — each design states what `ok: false` does on that exact event, so a `PreToolUse` prompt hook doesn't end your turn when you expected Claude to retry.
- **No more endless Stop loops** — Stop and SubagentStop prompts handle `stop_hook_active` and the 8-block cap from the start.
- **Background work that actually reports back** — async and `asyncRewake` hooks print output Claude Code accepts, and you know when results arrive and when `claude -p` cancels them.
- **Know what runs on your machine** — audits check workspace trust by where a hook lives, safe-script practice, and how to run `claude -p` over a repository you didn't write.
- **Answers you can check** — every claim cites the exact docs section, and each answer states what it was verified against: the live docs, the changelog for releases newer than your `claude --version`, and your debug log when behavior is in question. Anything outside its scope is named, not guessed.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `hook-workbench:hook-design` | Designs, writes, audits and debugs prompt, agent and background hooks; reviews hook security, workspace trust and PowerShell placeholders | `/hook-workbench:hook-design` or automatically when you work on these hooks |
| 🤖 Agent | `hook-workbench:hook-engineer` | Runs a design, write, audit or debug task in its own context with the skill preloaded, and returns evidence, changed files and checks run | Delegated by Claude, or "use the hook-engineer agent" |

**Scope.** Prompt hooks, agent hooks, `async` and `asyncRewake` command hooks, hook security and workspace trust, the PowerShell `shell` field, and debugging these. Synchronous command-hook decision control, matcher syntax, HTTP and MCP tool hooks, `onFailure` and permission rules are out of scope: the plugin names them in a **Not covered** line and leaves them alone.

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.294 or later — check with `claude --version`. Earlier versions could let rule-style prompt and agent hooks allow what they should block. Some behaviors need newer versions; the plugin checks yours before relying on them |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | None. To reproduce a background hook script it pipes test input through the script, using the tools the script already calls, such as `bash` or `jq`, when they are on your `PATH` |
| **Accounts / API keys** | None |
| **Network** | Reads `code.claude.com/docs` to check facts against the current hooks reference |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install hook-workbench --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install hook-workbench@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install hook-workbench --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install hook-workbench@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Hook Workbench** in **Discover** and select **Add**.

In the desktop app's **Code** tab you can also click **+** → **Plugins** → **Add plugin**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

### Example: a Stop hook that won't let Claude quit early

```text
Add a prompt hook so Claude can't stop until every task in my request is done and the tests it ran passed.
```

**Result:** a complete `Stop` handler with a prompt that reads `last_assistant_message`, returns `{"ok": true}` when `stop_hook_active` is already set and nothing is left, uses `impossible` for unreachable conditions, and an explicit `timeout`, plus a test plan: what to trigger and which debug-log line proves it ran.

### Example: audit the hooks in a repository

```text
Audit the hooks in this repo before I run claude -p over it in CI.
```

**Result:** a report that lists each hook with its source and whether it runs under `-p`, findings by severity with file and line, corrected handlers, and the safe way to run that repository non-interactively.

### Example: a background hook that never reports

```text
My async test hook runs but Claude never mentions the results. Find out why.
```

**Result:** the root cause, confirmed from the debug log (for example, other text on stdout before the JSON, or the run being cancelled at `-p` teardown), the fixed script, and the log line that shows the fix worked.

### Example: a PowerShell hook that can't find its script

```text
On Windows my PowerShell hook says it can't find .claude\hooks\check.ps1.
```

**Result:** the placeholder fix (`$env:CLAUDE_PROJECT_DIR` in double quotes instead of bare `$CLAUDE_PROJECT_DIR`) and the corrected handler.

## 🔄 Updating

```bash
claude plugin update hook-workbench@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Hook Workbench** → **Update now**. Then run `/reload-plugins`.

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `hook-workbench@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall hook-workbench@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Hook Workbench** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Hook Workbench** → its menu → **Remove**.

## 🧭 Compatibility

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

In a chat conversation, where agents don't run, the skill does the work itself. The hooks it designs run only where Claude Code hooks run; the plugin itself installs no hooks.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/hook-workbench:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Does it install any hooks?</b></summary>

No. Hook Workbench ships a skill and an agent only. It writes hook configuration or scripts only when you ask it to, and an audit never changes files.

</details>

<details>
<summary><b>Will it run my hook scripts?</b></summary>

Only to reproduce a problem, with made-up input piped to the script, and only when the script reads no secrets and changes nothing outside a temporary folder. Scripts that deploy, call the network or delete files are read, not run. Your permission settings decide whether it may run.

</details>

<details>
<summary><b>It said part of my hook is "Not covered".</b></summary>

The plugin stays inside prompt hooks, agent hooks, background hooks, hook security, PowerShell placeholders and debugging. Synchronous command-hook decisions and exit codes, matcher syntax, HTTP and MCP tool hooks, `onFailure` and permission rules get named in that line instead of a guess. See the [hooks reference](https://code.claude.com/docs/en/hooks) for those.

</details>

<details>
<summary><b>Can a prompt hook keep Claude from doing something dangerous?</b></summary>

Treat it as an advisory layer. Its verdict is a model's judgment over input that may include text from files or web pages. For a hard allow or deny, the plugin recommends [permission rules](https://code.claude.com/docs/en/permissions) and keeps the prompt hook as a second check.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 🧪 [Plugin Evals](../plugin-evals/README.md) — test the plugins and hooks you build with `claude plugin eval`

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=hook-workbench) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=hook-workbench) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=hook-workbench)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
