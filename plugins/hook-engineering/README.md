<div align="center">

# 🪝 Hook Engineering

<p><strong>Designs, writes, audits and debugs Claude Code hooks end to end: the event and configuration that decide when a hook runs, the input and output contract that decides what it does, prompt, agent and background hooks, workspace trust and security, and how mods interact with hooks, checked against the current docs and changelog.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fhook-engineering%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Automation-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.292-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Describe the hook you want, or the hook that misbehaves, and get a working configuration, an audit or a root cause, each checked against the official hooks docs and the changelog for your Claude Code version. Type `/hook-engineering:hook-development` followed by your request, or ask for the `hook-engineer` agent.

## ✨ Why use it

A hook looks simple until it never fires, fires on the wrong calls, or returns a block that Claude Code quietly ignores. Whether a hook works depends on three things lining up: the event, the matcher and the handler. Its effect depends on the exit code, the shape of stdout and the event it runs on. Hooks also change in most Claude Code releases, and the docs lag behind.

- **The right event first** — you describe a goal; the plugin picks the event, the matcher, the handler type and the location, and says why the nearest alternatives would not work.
- **Output you can trust** — every design comes with the exact stdin it reads, the exit code or JSON it returns for each outcome, what a failure does and a test plan. A linter and a probe check the result before you get it.
- **Audits with evidence** — every finding names the file and line, the rule it breaks, the official URL with its anchor, a severity and a complete fix. An audit changes nothing.
- **Root causes, not guesses** — debugging starts from your debug log and a real input sample, reproduces the hook outside Claude Code, and names one cause at a time.
- **Current, not remembered** — the plugin compares your installed Claude Code version with the changelog at run time and tells you when a behavior needs a newer release, or when an older one has a bug that affects your hook.
- **Safe by default** — it never runs a hook that deploys, sends requests or deletes files, and it treats hook files, prompts and logs as data, never as instructions.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `hook-engineering:hook-development` | Workflows to design, write, audit and debug hooks, with condensed references for every event and handler type, a config linter, a hook probe and a changelog script | `/hook-engineering:hook-development <request>` or automatically when you work on a hook |
| 🤖 Agent | `hook-engineering:hook-engineer` | A hooks specialist that works from your task message in one of four modes (design, write, audit, debug) and reports what it changed, checked and could not verify | Delegated by Claude, or "use the hook-engineer agent to audit my hooks" |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later (the one-step install command needs it) — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | `python3` for the config linter and the hook probe, and `bash`, `curl` and `awk` for the changelog script, all on `PATH`. Get Python 3 from [python.org](https://www.python.org/downloads/) or your package manager. `bash`, `curl` and `awk` come with macOS and most Linux distributions; otherwise install them with your package manager. On Windows, [Git for Windows](https://git-scm.com/downloads/win) provides Git Bash with all three. `jq` is what the hooks the plugin writes use to read their input: install it with `brew install jq`, `apt install jq` or from [jqlang.org](https://jqlang.org/download/) |
| **Claude Code docs server** | Recommended: Anthropic's official docs MCP server, so Claude reads the current hooks pages instead of recalling them. You add it once; the plugin doesn't install it. See [Add the docs server](#add-the-docs-server) |
| **Accounts / API keys** | None |

If a tool is missing, the plugin tells you which check it could not run and marks the affected conclusions as unverified.

### Add the docs server

In Claude Code, run this once in your terminal (not inside a session). `--scope user` makes it available in every project:

```bash
claude mcp add --transport http --scope user claude-code-docs https://code.claude.com/docs/mcp
```

Check it with `claude mcp list`: `claude-code-docs` should show `✔ Connected`. It needs no sign-in and no credentials.

Keep the name `claude-code-docs`, the one the [official MCP quickstart](https://code.claude.com/docs/en/mcp-quickstart) uses. The `hook-engineer` agent and the skill call the server's tools as `mcp__claude-code-docs__*`; under another name they have to search for the tools first.

In the Claude app, add it as a custom connector instead; the steps are under [Installation](#-installation).

Without the docs server, the plugin still works: it tells you the command above once, then reads the raw docs pages (see [Network calls](#-network-calls)).

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install hook-engineering --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install hook-engineering@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install hook-engineering --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install hook-engineering@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Hook Engineering** in **Discover** and select **Add**.
4. Add the docs server as a custom connector. On a Pro or Max plan: **Customize** → **Connectors** → **+ Add** → **Add custom connector**. Enter a name such as `Claude Code Docs` and the URL `https://code.claude.com/docs/mcp`, select **Continue**, check the detected settings and select **Continue** again, choose **No sign in** under **Authentication**, then select **Add**. On a Team or Enterprise plan, an Owner adds it under **Organization settings** → **Connectors** → **Add** → **Custom** → **Web**, and you select **Connect** on it in **Customize** → **Connectors**. A Free plan allows one custom connector. Source: [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

In the desktop app's **Code** tab you can also click **+** → **Plugins** → **Add plugin**.

> [!NOTE]
> A connector you add in the Claude app also reaches Claude Code when you sign in there with the same claude.ai account, with tools named `mcp__claude_ai_<connector name>__*`. The skill and the `hook-engineer` agent find and use it under that name. If you also add `claude-code-docs` in Claude Code, Claude Code connects that one and hides the connector, because both point at the same URL.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

### Example: design a hook

```text
/hook-engineering:hook-development I want a hook that blocks any Bash command that reads a .env file, and tells Claude to try another way
```

**Result:** Claude picks the event and the mechanism, writes the complete `hooks` block and the script, lints and probes them with an input that must be blocked, one that must pass and one it cannot read, and hands back the test plan with the debug-log line that proves the hook ran.

### Example: audit your hooks

```text
Use the hook-engineer agent to audit the hooks in .claude/settings.json. Don't change anything.
```

**Result:** The agent inventories every hook source, runs the checklist item by item and returns one report: a verdict (ready, ready with risks or not ready) and the ranked findings, each with file and line, the rule, its official URL and a complete fix. Your files stay as they are.

### Example: find out why a hook does nothing

```text
My SessionEnd hook uploads the session log to S3. It works by hand, but when I exit Claude Code the upload almost never finishes. Why?
```

**Result:** Claude collects your configured command and timeout, your version and the debug log, reads the hook instead of running it (it never runs a hook that sends data over the network), and names the cause with the evidence that shows it, such as the time limit Claude Code gives `SessionEnd` hooks.

## 🔄 Updating

```bash
claude plugin update hook-engineering@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Hook Engineering** → **Update now**. Then run `/reload-plugins`.

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `hook-engineering@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall hook-engineering@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Hook Engineering** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Hook Engineering** → its menu → **Remove**.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |

The docs server isn't part of the plugin: you add it yourself in Claude Code or as a connector in the Claude app (see [Add the docs server](#add-the-docs-server)).

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## 🌐 Network calls

The plugin makes these calls and no others:

| Call | When | What it sends |
| :-- | :-- | :-- |
| `https://code.claude.com/docs/mcp` (Anthropic's Claude Code docs server, once you add it) | Whenever Claude reads the official docs for a hook question | The search terms and page paths Claude asks for. No credentials. From the Claude app, the call goes through Anthropic's servers |
| `https://code.claude.com/docs/en/<page>.md` | When the docs server is not connected, or a heading is missing from its copy, Claude fetches the raw page with `curl` or WebFetch; it also reads `https://code.claude.com/docs/en/changelog` for a version-gated rule | A plain `GET` for that page |
| `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` | When the skill or the agent runs `hook-changes.sh` to compare your installed version with the changelog | A plain `GET`; the script keeps nothing and prints only the hook-related entries |
| `https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md` | When the docs changelog doesn't list your installed version yet, Claude opens the GitHub changelog with WebFetch | A plain `GET` for that page |

The linter and the probe make no network calls. The probe runs the hook script you point it at, with the input you give it and nothing else; the agent runs it only on scripts that read no secrets and change nothing outside a temporary directory.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/hook-engineering:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Does it work for git hooks such as <code>pre-commit</code>?</b></summary>

No. It covers Claude Code hooks only: the ones configured in `settings.json`, a plugin's `hooks/hooks.json`, or a skill's or agent's frontmatter. For a git hook, ask Claude directly.

</details>

<details>
<summary><b>Will it change my hooks or my settings?</b></summary>

Only when you ask. In audit mode the agent changes nothing and offers each fix as a complete handler or diff. In write mode it edits only the hook files your request names or clearly implies, and it edits `settings.json` or an existing hooks file only when you authorize that file. It never edits this plugin's own files.

</details>

<details>
<summary><b>What does it decide for me?</b></summary>

How a hook is wired and what its output does. Not what the hook should decide: which commands count as dangerous, which files are protected, which lint rules apply. It writes those as clearly marked parameters for you to fill in. Permission rules and writing a mod are out of scope too, and it says so and points to the official page.

</details>

<details>
<summary><b>How current are its answers?</b></summary>

The references were checked against the Claude Code docs and changelog on 2026-10-20, through v2.1.305. Before it answers, the agent compares your installed version with the changelog at run time, and the skill does the same whenever a rule is version-gated. If it can't reach the changelog, it says so and marks the version-sensitive conclusions as unverified.

</details>

<details>
<summary><b>I added the docs server as a connector in the Claude app. Do I need it in Claude Code too?</b></summary>

No. Signed in to Claude Code with the same claude.ai account, the connector reaches Claude Code with tools named `mcp__claude_ai_<connector name>__*`, and both the skill and the `hook-engineer` agent use it. Connectors don't load when Claude Code signs in another way, such as an API key or a cloud provider; add `claude-code-docs` there with the command in [Add the docs server](#add-the-docs-server). With both, Claude Code connects the one you added in Claude Code and hides the connector.

</details>

<details>
<summary><b>The hook-engineer agent isn't available in the Claude app.</b></summary>

Agents run in Cowork sessions, not in a chat conversation. In a chat conversation the skill still works; ask for it directly instead of the agent.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 🪝 [Claude Code hooks reference](https://code.claude.com/docs/en/hooks)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=hook-engineering) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=hook-engineering) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=hook-engineering)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
