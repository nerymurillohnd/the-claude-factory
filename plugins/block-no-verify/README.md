<!-- TEMPLATE: every double-brace placeholder and every TODO comment must be resolved before release. check-repo.mjs fails on leftovers. -->
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
> **TL;DR** — <!-- TODO: one sentence on the outcome a user gets, e.g. "Type `/block-no-verify:run` and get X without doing Y." -->

## ✨ Why use it

<!-- TODO: sell the outcome, not the mechanics. 3–5 bullets, each starting with a bold benefit. -->

- **Benefit one** — what pain disappears.
- **Benefit two** — what becomes faster or safer.
- **Benefit three** — what you no longer have to remember.

## 🧩 What's inside

<!-- TODO: one row per component. Delete rows you don't ship. Invocation column shows exactly what users type or what triggers it. -->

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `block-no-verify:example` | Short description | `/block-no-verify:example` or automatically when relevant |
| 🤖 Agent | `block-no-verify:example-agent` | Short description | Delegated by Claude, or "use the example-agent agent" |
| 🪝 Hook | `PreToolUse` | Short description | Automatically on matching tool calls |
| 🔌 MCP server | `example` | Short description | Tools appear as `mcp__plugin_block-no-verify_example__*` |
| 🧠 LSP server | `example-lsp` | Short description | Automatically for matching file types |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.295 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | <!-- TODO: e.g. `node` ≥ 22 on PATH, `gh` authenticated, or "None" --> |
| **Accounts / API keys** | <!-- TODO: e.g. "A GitHub token (prompted on enable)" or "None" --> |

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

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install block-no-verify@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

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

<!-- TODO: 2–4 realistic examples. Show what the user types and what they get back. -->

### Example: <!-- TODO: task name -->

```text
/block-no-verify:example <argument>
```

**Result:** <!-- TODO: what Claude does / produces. -->

## ⚙️ Configuration

<!-- TODO: document every userConfig option, env var and setting. Delete this section if there is nothing to configure. -->

| Option | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `example_option` | string | — | What it controls. Set via `/plugin` → **Installed** → **Block No Verify** → **Configure options**. |

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

## 🧭 Compatibility

<!-- TODO: keep one row per component type this plugin ships (check-repo.mjs enforces it) and delete the rest. Values come from docs/compatibility.md. -->

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |
| ⌨️ Commands | ✅ | ✅ loaded as a skill in a chat conversation |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |
| 🪝 Hooks | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |
| 🔌 MCP server (remote) | ✅ | 🔗 connect it on the plugin's **Connectors** tab |
| 🖥️ MCP server (local) | ✅ | ⚠️ only in Cowork sessions on your computer |
| 🧠 LSP server | ✅ | ➖ |
| 🎨 Output styles | ✅ | ➖ |
| 📡 Monitors | ✅ | ➖ |
| 🔁 Workflows | ✅ | ➖ |
| 🌈 Themes | ✅ | ➖ |
| ⚙️ Executables (`bin/`) | ✅ | ❌ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/block-no-verify:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<!-- TODO: add plugin-specific questions. -->

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
<!-- TODO: link sibling plugins that pair well with this one. -->

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=block-no-verify) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=block-no-verify) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=block-no-verify)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
