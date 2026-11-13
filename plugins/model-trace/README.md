<div align="center">

# 🔭 Model Trace

<p><strong>Shows, as Claude works, each skill, agent, MCP server, plugin, hook and web tool it uses in the session, how many times and at what time, with an export to Markdown or HTML.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fmodel-trace%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Mods-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.299-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Prerequisites](#-prerequisites) •
[Install](#-installation) •
[Usage](#-usage) •
[Configuration](#%EF%B8%8F-configuration) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it is a mod: it draws a pane in Claude Code's own interface. Claude can install it, but the mod doesn't run there: the plugin directory lists a mod for Claude Code only.

> [!TIP]
> **TL;DR** — Type `/model-trace` and watch, live, which of your skills, agents, MCP servers, plugins, hooks and web tools Claude reaches for, how often, and exactly when.

Model Trace is a Claude Code mod that keeps a live record of the capabilities Claude uses in your session: skills, agents, MCP servers, plugins, hooks and the web tools. It shows each one with its count and the time of every use, in a pane beside the transcript, and saves the session as a Markdown or HTML report. It only observes, so you learn what your setup really does for you without changing how Claude works.

## ✨ Why use it

- **See what your setup really does for you** — each capability appears the moment Claude first uses it, and its count grows with every use.
- **Know when it happened** — every use keeps its exact time; press a row to see them all.
- **Spot the habits** — the skill Claude calls on every turn, the MCP server it leans on, the hook that fires on every edit.
- **Keep a record** — save the session as a Markdown or a self-contained HTML report, or copy it as Markdown.
- **Never in the way** — it only observes: it doesn't block, rewrite or approve anything, and if it fails, Claude Code goes on as if it weren't installed. It records no commands, arguments or prompts: only capability names, such as a skill, a server or the WebSearch and WebFetch tools, with their counts and times.

## 🧩 What's inside

| Component | Name          | What it does                                                                                       | How it runs                                                                                   |
| :-------- | :------------ | :------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| 🧩 Mod    | `model-trace` | Counts each capability Claude uses, draws the Model Trace pane and adds the `/model-trace` command | Automatically in every Claude Code session once installed; the pane opens with `/model-trace` |

## 📋 Prerequisites

| Tool        | Minimum version | Check              |
| :---------- | :-------------- | :----------------- |
| Claude Code | 2.1.299         | `claude --version` |

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
brew upgrade claude-code  # claude-code@latest if you installed that cask
```

</details>
<details>
<summary>📦 <b>npm</b> — any platform</summary>

```bash
npm install -g @anthropic-ai/claude-code@latest
```

</details>

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install model-trace@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install model-trace --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install model-trace@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install model-trace@the-claude-factory
```

## 🚀 Usage

### Watch the session as it happens

```text
/model-trace
```

**Result:** a pane opens beside the transcript in a wide fullscreen terminal, or above the prompt otherwise, and keeps up with the session:

```text
4 capabilities · 9 uses · since 09:14:02

Skills                                         2 · 3 uses
▸ docs-kit:write-guide  docs-kit                ×2  09:31:40
▸ release-notes  user                           ×1  09:20:15

MCP servers                                    1 · 4 uses
▸ search  docs-kit                              ×4  09:33:02

Plugins                                        1 · 6 uses
▸ docs-kit  via skill, MCP server               ×6  09:33:02

Web                                            1 · 2 uses
▸ WebSearch  built-in                           ×2  09:25:48

m: Save .md   h: Save .html   c: Copy Markdown
```

A section appears the first time Claude uses something of its kind, and each row the first time that capability is used. Press a row to see the time of every use. Up to eight rows show per section; **+ N more** shows the rest.

| Section     | What counts as a use                                                                                                                                   |
| :---------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Skills      | A skill Claude calls, a `/skill` you type, and a skill a subagent starts with                                                                          |
| Agents      | Each subagent or teammate Claude starts, by its type                                                                                                   |
| MCP servers | Each call to a server's tools, shown under the server's name only                                                                                      |
| Plugins     | The uses of a plugin's skills, agents and MCP servers, regrouped under the plugin                                                                      |
| Hooks       | Each time a hook from your settings files runs, by its status message or the name of the script it runs; and the hook output Claude received, by event |
| Web         | Each WebSearch and WebFetch call                                                                                                                       |

A call that a permission rule or a hook refused is not counted. The header counts each use once: the Plugins section and the hook output rows regroup uses that other rows already count, so they are left out of it.

### Save or share the report

Press **Save .md** or **Save .html** in the pane, or run:

```text
/model-trace html
```

**Result:** the report is written to your Downloads folder as `model-trace-<date>-<time>.html`, and a notice names the path. It lists every capability with its uses and times, and a timeline of the session. The HTML file is one self-contained page, in light or dark to match your system. **Copy Markdown** puts the same report on your clipboard instead.

### Check what you never use

Model Trace shows only what Claude uses. To find skills and plugins that never run, and what they cost you in context, use Claude Code's own commands:

```text
/skill-doctor
/doctor
/usage
```

Then check the **Not used recently** list in `/plugin` → **Installed**.

## ⚙️ Configuration

| Option       | Type    | Default       | Description                                                                                                                                              |
| :----------- | :------ | :------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exportDir`  | string  | `~/Downloads` | The folder reports are saved to. `~` is your home folder. The folder must already exist: Model Trace never creates folders                               |
| `statusLine` | boolean | `false`       | Also show the count in the status line, such as `5 used · 12 uses`. Claude Code starts every mod's status line with a warning sign and the plugin's name |

Set an option when you install:

```bash
claude plugin install model-trace@the-claude-factory --config exportDir=~/Documents/reports
```

Change it later:

```text
/plugin configure model-trace@the-claude-factory
```

Or open `/plugin` → **Installed** → **Model Trace** → **Configure options**. In `/config`, each option is a row of its own.

## 🔍 What this plugin runs and sends

- **Hooks:** none; the plugin runs no shell commands.
- **Mod:** it hooks `session.start`, `classic.SessionStart` (on clear, resume and fork), `classic.*` (your settings hook events), `skill.prompt`, `agent.spawn`, `tool.call`, `session.append`, its own `/model-trace` command and the drawing of its own pane. Each hook passes the event on unchanged and only records a capability name and a time. It reads the `hooks` of your settings files (user, project, local, `--settings` and managed), to name your hooks; the `HOME` environment variable, to expand `~` in `exportDir`; and whether the `exportDir` folder exists before it saves. It writes only the report you save, in `exportDir`, and puts the report on your clipboard only when you press **Copy Markdown**. It never reads other files, runs no command, makes no network call and calls no model. It runs inside Claude Code with your access and no sandbox.
- **MCP servers:** none.
- **Network:** none.
- **Files written:** only the report you save, in `exportDir`. A permission rule such as `Write(~/Downloads/**)` doesn't apply to a mod, so choose `exportDir` with that in mind. Nothing is kept between sessions: the trace lives in the session's memory, and `/clear`, `/resume` and `/branch` start it over.
- **Privacy:** the author collects no data. The marketplace's [privacy policy](https://github.com/nerymurillohnd/the-claude-factory/blob/main/PRIVACY.md) covers this plugin and the outside services it can reach.
- **Before you install:** a mod runs with your permissions and no sandbox. Install it only if you trust this marketplace; the Mod line above lists everything it reaches.

## 🔄 Updating

```bash
claude plugin update model-trace@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall model-trace@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall model-trace@the-claude-factory --scope project
```

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps nothing in its data directory. The reports you saved stay in `exportDir`; delete them yourself if you no longer want them.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component |                                                                                                                                  Claude Code                                                                                                                                   |                          Claude                          |
| :-------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------: |
| 🧩 Mods   | ✅ v2.1.287+ (Desktop v2.1.286+); hooks run in every session except Desktop on WSL; ⚠️ drawing depends on where: panes in the terminal, Desktop and VS Code (extension v2.1.299+, v2.1.304+ without feature flags), the band above the prompt only in the terminal and Desktop | ⚠️ the plugin directory lists a mod for Claude Code only |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

Model Trace itself needs Claude Code 2.1.299 or later. Its pane draws in the terminal, the desktop app's **Code** tab and the VS Code extension (extension v2.1.299+, or v2.1.304+ in a session that doesn't fetch feature flags, such as one on Amazon Bedrock). In VS Code, press the buttons with a click or Enter: hotkeys don't apply there. In `claude -p` and cloud sessions nothing draws; there `/model-trace` answers with a short text summary, and its `md` and `html` forms still save the report.

**Platforms:** macOS and Linux.

## 🚧 Limitations

- **Plugin hooks:** Claude Code doesn't tell a mod which plugin a hook belongs to, so hooks from plugins show only as hook output by event, and a plugin that works only through hooks doesn't appear under Plugins.
- **Hooks with an `if` condition:** the count is how often the hook's event and matcher selected it, so it's an upper bound; the row says so.
- **Organizations:** with managed settings or a Team or Enterprise login, Claude Code's built-in guard `cc-plugin-sec-default` loads ahead of user mods. It can refuse to load the mod, and it withholds settings hook events and skill expansions from mods you install: Hooks stays empty, a `/skill` you type isn't counted, and a skill's origin is read from its name. Skills Claude calls, agents, MCP servers, plugins and web tools are still counted.
- **Managed mods only:** an organization's `allowManagedModsOnly` refuses any mod installed from a GitHub source, such as this marketplace, even one the organization enables.
- **What turns it off:** `disableAllHooks` in your settings or managed settings, and `allowManagedModsOnly` or `allowManagedHooksOnly` in managed settings; starting Claude Code with `--safe-mode` or `--bare`.
- **The permission prompt:** the mod can't restyle the permission prompt or change what it shows, and it doesn't try to.
- **Diagnosis:** `/plugin` names the mods the session loaded; only Claude Code's debug log shows why one was refused or a hook skipped (see [FAQ](#-faq--troubleshooting)).
- **A reload mid-call:** if the plugin reloads while Claude is calling a skill, such as when you update it, that one skill may show "user or built-in" instead of its origin.

## ❓ FAQ & Troubleshooting

<details>
<summary><b><code>/model-trace</code> doesn't open a pane.</b></summary>

Run `/plugin` and check that the dim line under its tabs, such as `1 mod active · model-trace`, names it. If it doesn't, start Claude Code in debug mode:

```bash
claude --debug
```

Then look in the debug log for `model-trace`: a line names why the module wasn't loaded or a hook was skipped. In `claude -p`, cloud sessions and a Desktop session on WSL, no pane draws.

</details>

<details>
<summary><b>The Hooks section is empty.</b></summary>

It lists hooks from your settings files and the hook output Claude received. It stays empty when no such hook ran yet, and always where an organization's built-in guard runs (see [Limitations](#-limitations)).

</details>

<details>
<summary><b>"Not saved: the folder … does not exist".</b></summary>

Model Trace never creates folders. Create the folder, or set `exportDir` to one that exists, as in [Configuration](#%EF%B8%8F-configuration).

</details>

<details>
<summary><b>Can Model Trace slow down or change my session?</b></summary>

No. Each hook records a name and a time and passes the event on unchanged; a recording that fails is dropped and the call goes on. It sends nothing anywhere and calls no model.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 🧩 [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)
- 📊 [Measure plugin cost and usage](https://code.claude.com/docs/en/plugins/measure)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=model-trace) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=model-trace) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=model-trace)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
