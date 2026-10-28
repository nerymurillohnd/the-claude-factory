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
[Prerequisites](#-prerequisites) •
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

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.292 (the one-step install command needs it) | `claude --version` |
| Python, as `python3` | 3 | `python3 --version` |
| `bash`, `curl` and `awk` | — | `bash --version` |
| `jq` (for the hooks it writes) | — | `jq --version` |
| Claude Code docs MCP server (recommended) | — | `claude mcp list` |

Python runs the config linter and the hook probe; `bash`, `curl` and `awk` run the changelog script; all must be on your `PATH`. `jq` is what the hooks the plugin writes use to read their input. The docs server is Anthropic's official docs MCP server, so Claude reads the current hooks pages instead of recalling them; you add it once, the plugin doesn't install it.

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

### 🐍 Python

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install python
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt install python3
```

</details>
<details>
<summary>📦 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install python3
```

</details>
<details>
<summary>🪟 <b>Python install manager (winget)</b> — Windows</summary>

```bash
winget install 9NQ7512CXL7T -e --accept-package-agreements --disable-interactivity
```

</details>

Or download the installer from [python.org](https://www.python.org/downloads/).

### 🐚 bash, curl and awk

They come with macOS and most Linux distributions; otherwise install them with your package manager. On Windows, Git for Windows provides Git Bash with all three:

<details>
<summary>🪟 <b>Git for Windows (winget)</b> — Windows</summary>

```bash
winget install --id Git.Git -e --source winget
```

</details>

### 🧰 jq

<details>
<summary>🍺 <b>Homebrew</b> — macOS</summary>

```bash
brew install jq
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt-get install jq
```

</details>
<details>
<summary>📦 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install jq
```

</details>
<details>
<summary>📦 <b>pacman</b> — Arch Linux</summary>

```bash
sudo pacman -S jq
```

</details>
<details>
<summary>📦 <b>zypper</b> — openSUSE</summary>

```bash
sudo zypper install jq
```

</details>
<details>
<summary>🪟 <b>winget</b> — Windows</summary>

```bash
winget install jqlang.jq
```

</details>

### 📖 Claude Code docs server

Run this once in your terminal, not inside a session. `--scope user` makes it available in every project:

<details>
<summary>💻 <b>Claude Code</b> — any platform</summary>

```bash
claude mcp add --transport http --scope user claude-code-docs https://code.claude.com/docs/mcp
```

</details>

Check it with `claude mcp list`: `claude-code-docs` should show `✔ Connected`. It needs no sign-in and no credentials.

Use the name `claude-code-docs`, the one the [official MCP quickstart](https://code.claude.com/docs/en/mcp-quickstart) uses: the skill and the `hook-engineer` agent look for `mcp__claude-code-docs__*` first. Another name works too, because they find the docs tools by the tools' own names.

In the Claude app, add it as a custom connector instead:

1. On a Pro or Max plan: **Customize** → **Connectors** → **+ Add** → **Add custom connector**.
2. Enter a name such as `Claude Code Docs` and the URL `https://code.claude.com/docs/mcp`, select **Continue**, check the detected settings and select **Continue** again.
3. Choose **No sign in** under **Authentication**, then select **Add**.

On a Team or Enterprise plan, an Owner adds it under **Organization settings** → **Connectors** → **Add** → **Custom** → **Web**, and you select **Connect** on it in **Customize** → **Connectors**. A Free plan allows one custom connector. Source: [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

> [!NOTE]
> A connector you add in the Claude app also reaches Claude Code when you sign in there with the same claude.ai account, with tools named `mcp__claude_ai_<connector name>__*`. The skill and the `hook-engineer` agent find and use it under that name. If you also add `claude-code-docs` in Claude Code, Claude Code connects that one and hides the connector, because both point at the same URL.

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install hook-engineering@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install hook-engineering --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install hook-engineering@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install hook-engineering@the-claude-factory
```

### 🖥️ Claude app (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Hook Engineering** in **Discover** and select **Add**.

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

Then, in an open session:

```text
/reload-plugins
```

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `hook-engineering@synced`: update and uninstall it in the app (**Customize** → **Plugins**).

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update Python and `jq` the way you installed them, for example with Homebrew:

```bash
brew upgrade python jq
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall hook-engineering@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall hook-engineering@the-claude-factory --scope project
```

In the Claude app: **Customize** → **Plugins** → **Hook Engineering** → its menu → **Remove**.

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps no data of its own. Hooks Claude wrote at your request stay in your settings, and the docs server stays until you remove it:

```bash
claude mcp remove claude-code-docs --scope user
```

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |

The docs server isn't part of the plugin: you add it yourself in Claude Code or as a connector in the Claude app (see [Claude Code docs server](#-claude-code-docs-server)).

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

No. Signed in to Claude Code with the same claude.ai account, the connector reaches Claude Code with tools named `mcp__claude_ai_<connector name>__*`, and both the skill and the `hook-engineer` agent use it. Connectors don't load when Claude Code signs in another way, such as an API key or a cloud provider; add `claude-code-docs` there with the command in [Claude Code docs server](#-claude-code-docs-server). With both, Claude Code connects the one you added in Claude Code and hides the connector.

</details>

<details>
<summary><b>The hook-engineer agent isn't available in the Claude app.</b></summary>

Agents run in Cowork sessions, not in a chat conversation. In a chat conversation the skill still works; ask for it directly instead of the agent.

</details>

<details>
<summary><b>Does it work without the docs server or one of the tools?</b></summary>

Yes. Without the docs server, the plugin tells you the command in [Claude Code docs server](#-claude-code-docs-server) once, then reads the raw docs pages (see [Network calls](#-network-calls)). If a tool is missing, the plugin tells you which check it could not run and marks the affected conclusions as unverified.

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
