<div align="center">

# ⏱️ Turn Meter

<p><strong>Shows how long each turn took, how many tools it used in the main thread and in subagents, and the tokens it spent, in a band above the prompt, and alerts you when a long turn ends.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fturn-meter%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Mods-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.295-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Prerequisites](#-prerequisites) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it is a mod: it draws in Claude Code's own interface, which the Claude app's chat and Cowork don't load.

> [!TIP]
> **TL;DR** — After every turn, one line above the prompt tells you how long it took, how many tools Claude and its subagents ran and how many tokens it spent, and a long turn alerts you when it ends: a toast by default, or a native notification.

## ✨ Why use it

- **See what a turn cost at a glance** — time, tool calls and tokens in one line, without opening `/cost` or the transcript.
- **Know how much work subagents did** — tool calls are split between the main thread and subagents, and their tokens are added in.
- **Walk away from long turns** — a toast or a native notification tells you when a turn that ran past your threshold is done.
- **Spot what went wrong** — an interrupted turn, an API error and a refusal each say so, with how long they ran.
- **Stays out of the way** — it only observes: it never changes a prompt, a tool call or a reply, and the **Hide** button or `/turn-meter` hides it.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧩 Mod | `turn-meter` | Counts each turn's tools and tokens, draws the last-turn band above the prompt, alerts on long turns, and adds the `/turn-meter` command | Automatically in every Claude Code session once installed |

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.295 | `claude --version` |
| Notifying terminal (optional): iTerm2, kitty or Ghostty, for native notifications | — | — |

Without one, the terminal bell can still notify; where nothing can, the alert falls back to a toast.

### 🤖 Claude Code

Already installed? Bring it to the latest version the way you installed it. New to Claude Code? Follow the [official setup](https://code.claude.com/docs/en/setup).

<details>
<summary>⬇️ <b>Native installer</b> — macOS, Linux, WSL</summary>

```bash
claude update
```

</details>
<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew upgrade claude-code
```

</details>
<details>
<summary>📦 <b>npm</b> — any platform</summary>

```bash
npm install -g @anthropic-ai/claude-code@latest
```

</details>

### 🔔 Notifying terminal

Get iTerm2 from its [download page](https://iterm2.com/downloads.html) (macOS). Claude Code picks the channel with its `preferredNotifChannel` setting.

<details>
<summary>🐱 <b>kitty installer</b> — macOS, Linux</summary>

```bash
curl -L https://sw.kovidgoyal.net/kitty/installer.sh | sh /dev/stdin
```

</details>
<details>
<summary>👻 <b>Ghostty (Homebrew)</b> — macOS</summary>

```bash
brew install --cask ghostty
```

</details>
<details>
<summary>👻 <b>Ghostty (distribution package)</b> — Arch Linux</summary>

```bash
sudo pacman -S ghostty
```

</details>
<details>
<summary>👻 <b>Ghostty (distribution package)</b> — Ubuntu 26.04+</summary>

```bash
sudo apt install ghostty
```

</details>
<details>
<summary>👻 <b>Ghostty (Snap)</b> — Linux</summary>

```bash
sudo snap install ghostty --classic
```

</details>

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install turn-meter@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install turn-meter --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install turn-meter@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install turn-meter@the-claude-factory
```

## 🚀 Usage

Install it and work as usual. The band appears after your first turn ends.

### Example: a turn with a subagent

```text
Last turn: 3m 12s · 24 tools (9 in 2 subagents) · 41.2k in / 6.3k out   [ Hide ]
```

**Result:** the turn took 3 minutes 12 seconds. Claude ran 15 tools itself and two subagents ran 9 more. Input tokens count uncached input, cache reads and cache writes, for the main thread and its subagents together.

### Example: a turn that did not finish

| How the turn ended | The band reads |
| :-- | :-- |
| You pressed Esc | `Last turn: interrupted after 1m 05s · 7 tools` |
| An API error ended it | `Last turn: ended by API error after 40s · 3 tools` |
| The model refused | `Last turn: refused after 12s` |
| A narrow band (under 60 columns of room) | `3m12s · 24 tools · 48k tok` |

### Example: hide or show the band

```text
/turn-meter
```

**Result:** the band hides if it is showing and comes back if it is hidden. The **Hide** button on the band hides it too.

### Example: get a notification when a long turn ends

```bash
claude plugin install turn-meter@the-claude-factory --config alert=notify --config alertAfterSeconds=90
```

**Result:** a turn that runs 90 seconds or more sends a native notification ("That turn took 3m 12s") when it ends. A turn you interrupt never alerts: you were there.

## ⚙️ Configuration

| Option | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `alert` | `toast`, `notify` or `off` | `toast` | How a long turn alerts you: a message inside Claude Code, a native notification (a toast when none can be sent), or nothing |
| `alertAfterSeconds` | number, at least 1 | `120` | A main turn that runs at least this long alerts you |
| `showTokens` | boolean | `true` | Show the turn's tokens in the band; turn it off to see only time and tools |

Change them in `/config`, where `alert` is a picker (v2.1.271+), or in `/plugin` → **Installed** → **Turn Meter** → **Configure options**. From the shell, pass `--config <option>=<value>` to `claude plugin install`.

## 🔍 What this plugin runs and sends

- **Hooks:** a mod, with no shell hooks. It hooks the start of each session, the start and end of each turn, each tool call, the band above the prompt and the `/turn-meter` command; see [What does the mod reach on my machine?](#-faq--troubleshooting)
- **MCP servers:** none.
- **Network:** none. It runs no commands and never calls the model.
- **Files written:** none; it reads no files either. It keeps the last turn's summary in the session's memory only, so nothing carries over between sessions.
- **Before you install:** a mod runs with your permissions and no sandbox; `claude plugin validate <path to the plugin folder>` shows everything it hooks and calls.

## 🔄 Updating

```bash
claude plugin update turn-meter@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update your terminal the way you installed it, for example:

```bash
brew upgrade --cask ghostty
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall turn-meter@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall turn-meter@the-claude-factory --scope project
```

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps the last turn's summary in the session's memory only, so nothing is left behind.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🧩 Mods | ✅ every Claude Code session except a Desktop session on WSL | ⚠️ the plugin directory lists a mod for Claude Code only |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

The band draws in the terminal and the desktop app's **Code** tab. The VS Code extension does not draw it yet: there the mod still counts and alerts, and `/turn-meter` still works.

### Limitations

- A tool call counts when Claude makes it, even if a permission rule or a hook then denies it.
- A background subagent that finishes after its turn ended counts toward the next turn.
- If the plugin reloads in the middle of a turn, such as when you update it, that turn's counts start over.
- These settings turn the mod off: `disableAllHooks`, `allowManagedModsOnly` and `allowManagedHooksOnly` in managed settings, and starting Claude Code with `--safe-mode` or `--bare`.
- In organizations with managed settings or a Team or Enterprise login, Claude Code's built-in guard runs ahead of every mod and can refuse to load it.

## ❓ FAQ & Troubleshooting

<details open>
<summary><b>The band doesn't show up.</b></summary>

The band appears only after the first turn of a session ends, and it steps aside while Claude Code shows a survey above the prompt. If you hid it, type `/turn-meter`. Then run `/plugin`: it lists active mods as `N mod active · <names>`. If `turn-meter` is missing there, start Claude Code with `claude --debug` and look in the debug log for `turn-meter`: a line saying the module was not loaded, or a hook was skipped, names the reason.

</details>

<details>
<summary><b>I chose <code>notify</code> but get a toast instead.</b></summary>

Claude Code could not send a native notification: your terminal has no notification channel it supports, notifications are turned off, or the session has no terminal, as in the desktop app. Turn Meter then shows a toast so you still see the alert. Check the `preferredNotifChannel` setting in `/config`.

</details>

<details>
<summary><b>What does the mod reach on my machine?</b></summary>

It hooks the start of each session (to add `/turn-meter`), the start and end of each turn, each tool call, the band above the prompt, and the `/turn-meter` command. It calls only Claude Code's interface: registering the command, the session's own memory, drawing, toasts and notifications. It never changes a prompt, a tool call or a reply, and it never touches files, processes, the network or the model. `claude plugin validate` lists the same hooks and calls.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code mods docs](https://code.claude.com/docs/en/plugins/mods/overview)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=turn-meter) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=turn-meter) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=turn-meter)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
