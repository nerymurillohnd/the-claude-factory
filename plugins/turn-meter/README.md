<div align="center">

# ⏱️ Turn Meter

<p><strong>Shows how long each turn took, how many tools it used in the main thread and in subagents, and the tokens it spent, in a band above the prompt, and alerts you when a long turn ends.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fturn-meter%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
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

💻 **Claude Code only** — it is a mod: it draws in Claude Code's own interface, which the Claude app's chat and Cowork don't load.

> [!TIP]
> **TL;DR** — After every turn, one line above the prompt tells you how long it took, how many tools Claude and its subagents ran and how many tokens it spent, and a long turn sends you a notification when it ends.

## ✨ Why use it

- **See what a turn cost at a glance** — time, tool calls and tokens in one line, without opening `/cost` or the transcript.
- **Know how much work subagents did** — tool calls are split between the main thread and subagents, and their tokens are added in.
- **Walk away from long turns** — a toast or a native notification tells you when a turn that ran past your threshold is done.
- **Spot what went wrong** — an interrupted turn, an API error and a refusal each say so, with how long they ran.
- **Stays out of the way** — it only observes: it never changes a prompt, a tool call or a reply, and one keystroke hides it.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧩 Mod | `turn-meter` | Counts each turn's tools and tokens, draws the last-turn band above the prompt, alerts on long turns, and adds the `/turn-meter` command | Automatically in every Claude Code session once installed |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.295 or later — check with `claude --version`. Tested with v2.1.308. |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | None |
| **Accounts / API keys** | None |
| **Native notifications** (optional) | A terminal Claude Code can notify through: iTerm2, kitty or Ghostty, or the terminal bell. Claude Code picks it with its `preferredNotifChannel` setting. Where none is available, the alert falls back to a toast. |

> [!NOTE]
> Turn Meter makes no network calls, runs no commands, and reads or writes no files. It keeps the last turn's summary in the session's memory only, so nothing carries over between sessions.

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install turn-meter --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install turn-meter@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install turn-meter --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install turn-meter@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude desktop app — Code tab</b></summary>

Click **+** → **Plugins** → **Add plugin**, and add `turn-meter` from `nerymurillohnd/the-claude-factory`.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

A mod runs with your permissions and no sandbox. Before you install it, you can see everything it hooks and calls with `claude plugin validate <path to the plugin folder>`.

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
| A narrow terminal (under 60 columns) | `3m12s · 24 tools · 48k tok` |

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

## 🔄 Updating

```bash
claude plugin update turn-meter@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Turn Meter** → **Update now**. Then run `/reload-plugins`.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall turn-meter@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Turn Meter** → **Uninstall**.

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
