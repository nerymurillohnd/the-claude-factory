<div align="center">

# 📒 Tool Ledger

<p><strong>Lists every tool call of the session in a live panel: what ran, on what, whether Claude or a subagent made it, and whether it finished, failed or was denied.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Ftool-ledger%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Productivity-6B7280)](../../README.md#-catalog)
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

💻 **Claude Code only** — it is a mod: it draws a panel in Claude Code's own interface, which the Claude app's chat and Cowork don't load.

> [!TIP]
> **TL;DR** — Type `/tool-ledger` and see, call by call, what Claude and each of its subagents actually ran, and which calls your hooks or permission rules stopped.

## ✨ Why use it

- **Audit what subagents really did** — their calls are grouped under each subagent's type and task, not buried in a collapsed transcript.
- **See your guardrails work** — a call that a `PreToolUse` hook or a permission rule refuses shows as `denied`, apart from calls that failed on their own.
- **Spot failures fast** — **Errors only** narrows the panel to failed and denied calls, with a running count in the header.
- **Safe to share your screen** — one option hides commands, paths and patterns and keeps only tool names.
- **Never in the way** — it only observes: it doesn't block, rewrite or approve a call, and if the ledger itself fails, the call still runs once with its own result.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧩 Mod | `tool-ledger` | Records each tool call with its status and duration, draws the ledger panel and adds the `/tool-ledger` command | Automatically in every Claude Code session once installed; the panel opens with `/tool-ledger` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.295 or later — check with `claude --version`. Tested with v2.1.308. |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | None |
| **Accounts / API keys** | None |

> [!NOTE]
> Tool Ledger makes no network calls, runs no commands, and reads or writes no files. The ledger lives only in the session's memory: nothing is saved to disk or carried to the next session. The panel shows what the transcript already shows.

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install tool-ledger --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install tool-ledger@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install tool-ledger --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install tool-ledger@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude desktop app — Code tab</b></summary>

Click **+** → **Plugins** → **Add plugin**, and add `tool-ledger` from `nerymurillohnd/the-claude-factory`.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

A mod runs with your permissions and no sandbox. Before you install it, you can see everything it hooks and calls with `claude plugin validate <path to the plugin folder>`.

## 🚀 Usage

### Example: open the ledger

```text
/tool-ledger
```

**Result:** a panel that keeps up with the session:

```text
Tool calls · 142 · 3 running · 2 errors · 1 denied      [ Errors only ]
done   Read     src/lib/catalog.ts                 0.1s
done   Bash     pnpm test --filter api             14.2s
error  Bash     tsc -p .                           6.0s
denied Read     .env
▸ Explore · "Find pricing references"
  done   MCP      docs › search                    0.3s
  runs   Read     docs/pricing.md
```

Each row shows the status, the tool, what it acted on and how long it took. The panel shows the latest rows that fit.

| Tool | What the row shows |
| :-- | :-- |
| Bash | The first 60 characters of the command |
| Read, Edit, Write | The file path, relative to the working directory |
| Grep, Glob | The pattern |
| Agent | The task description |
| MCP tools | `server › tool` |
| Any other tool | Only its name |

### Example: see only what went wrong

Press **Errors only** in the panel. It shows failed and denied calls, and the button becomes **All calls**.

### Example: keep the ledger open beside the transcript

```bash
claude plugin install tool-ledger@the-claude-factory --config autoOpen=sidebar
```

**Result:** in a fullscreen terminal session, the panel opens by itself beside the transcript once the terminal is at least 144 columns wide. When you open it yourself with `/tool-ledger`, it fits any width.

## ⚙️ Configuration

| Option | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `autoOpen` | `never` or `sidebar` | `never` | `sidebar` opens the panel by itself in a fullscreen terminal, beside the transcript, from 144 columns |
| `showTargets` | boolean | `true` | Turn it off to hide commands, paths, patterns and subagent tasks, for example while you share your screen |
| `maxRows` | number, 10 to 2000 | `500` | How many of the latest calls the session keeps |

Change them in `/config`, where `autoOpen` is a picker (v2.1.271+), or in `/plugin` → **Installed** → **Tool Ledger** → **Configure options**. From the shell, pass `--config <option>=<value>` to `claude plugin install`.

## 🔄 Updating

```bash
claude plugin update tool-ledger@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Tool Ledger** → **Update now**. Then run `/reload-plugins`.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall tool-ledger@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Tool Ledger** → **Uninstall**.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🧩 Mods | ✅ every Claude Code session except a Desktop session on WSL | ⚠️ the plugin directory lists a mod for Claude Code only |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

The panel draws in the terminal and the desktop app's **Code** tab. The VS Code extension and `claude -p` don't place panels: there the mod still records calls, but you can't see the ledger.

### Limitations

- **Denied** covers a `{ deny }` from another mod, a `PreToolUse` hook in your settings, and a deny rule that refuses the call at the permission check, such as `Bash(cat:*)`. A Read, Edit or Write of a path a deny rule covers is refused earlier, by the tool's own input check, so it shows as `error`. A call you decline at a permission prompt shows as `error`, and its duration includes the time the prompt waited for you.
- A `PreToolUse` hook in managed settings runs ahead of every mod, so a call it denies shows as `error`.
- A call that is interrupted before it returns can stay at `runs`.
- If the plugin reloads in the middle of a call, such as when you update it, that call's row may not close.
- Claude Code's own internal tools, such as the one a subagent uses to hand its report back, appear as rows too.
- These settings turn the mod off: `disableAllHooks`, `allowManagedModsOnly` and `allowManagedHooksOnly` in managed settings, and starting Claude Code with `--safe-mode` or `--bare`.
- In organizations with managed settings or a Team or Enterprise login, Claude Code's built-in guard runs ahead of every mod and can refuse to load it.

## ❓ FAQ & Troubleshooting

<details open>
<summary><b><code>/tool-ledger</code> says the panel is open but not shown.</b></summary>

The surface you are on can't place panels yet, or the terminal is too narrow for a panel that opened by itself. The reply names the reason. Panels show in the terminal and the desktop app's **Code** tab. Run `/plugin` to check that `tool-ledger` is listed among active mods; if it is missing, start Claude Code with `claude --debug` and look in the debug log for `tool-ledger`, where a line names why the module was not loaded or a hook was skipped.

</details>

<details>
<summary><b>Can Tool Ledger change or slow down my tool calls?</b></summary>

No. It records a row before the call and closes it after, and always passes the call on unchanged. If recording fails, the call still runs exactly once and returns its own result. It never blocks or approves anything: keep using permission rules and hooks for that.

</details>

<details>
<summary><b>What does the mod reach on my machine?</b></summary>

It hooks the start of each session (to add `/tool-ledger`), each tool call, the `PreToolUse` and permission-check decisions (to tell denied calls apart), the `/tool-ledger` command, the panel and the band above the prompt (to open the sidebar when you choose `autoOpen`). It calls only Claude Code's interface: the clock, the list of subagents, registering the command, the session's own memory, and opening and drawing the panel. It never touches files, processes, the network or the model. `claude plugin validate` lists the same hooks and calls.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code mods docs](https://code.claude.com/docs/en/plugins/mods/overview)
- 📖 [Claude Code permissions](https://code.claude.com/docs/en/permissions)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=tool-ledger) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=tool-ledger) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=tool-ledger)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
