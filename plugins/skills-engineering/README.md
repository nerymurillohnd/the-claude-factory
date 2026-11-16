<div align="center">

# 🔬 Skills Engineering

<p><strong>Audits Claude skills wherever they live, from plugins, personal and project folders to claude.ai accounts and URLs: three specialized reviewer agents run in parallel on content patterns, the runtime contract and size limits, check every point against the current official docs, and each returns a report with quoted file-and-line evidence, severity, an exact fix and a verdict.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fskills-engineering%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Testing%20%26%20Quality-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.304-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Type `/skills-engineering:auditing-skills` with a skill's path, name or URL, and get three independent reviews of it, each with the exact lines behind every finding, the fix and a verdict.

A skill can look finished to the person who wrote it and still fail the model that runs it: a path that never resolves, a variable left literal, an example Claude copies wrongly, a field one surface rejects, a budget the skill overruns. Skills Engineering sends three specialized reviewers through the skill, each one checking its own area against the current official documentation, and hands you each report exactly as the reviewer wrote it. It audits plugin skills, a skill at a plugin's root, personal, project and managed skills, skills on a claude.ai account, and skills at a URL or in a repository, with every file they include.

## ✨ Why use it

- **Three specialists in one request** — you no longer audit content, packaging and limits one pass at a time: the reviewers run in parallel, and each one goes deep on one area.
- **Findings you can act on** — every defect quotes the file and lines, gives its severity and the exact replacement text, and every point is checked against the official docs as they are today, so you know what to change and why.
- **No need to remember where a skill lives** — name a path, a skill, a claude.ai skill or a URL, and the skill gets the files onto disk and briefs each reviewer for you. Name a reviewer to run only that one.

## 🧩 What's inside

| Component | Name                                                  | What it does                                                                                                                                                                                                                        | How it runs                                                                                                                                    |
| :-------- | :---------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| 🎯 Skill  | `skills-engineering:auditing-skills`                  | Locates the skill, runs the mechanical checks it has a script for (in this version, `claude plugin validate`), briefs and launches the reviewers in parallel, holds each report to its checklist and presents every report verbatim | `/skills-engineering:auditing-skills`, or automatically when you ask Claude to audit or review a skill, and after a skill is created or edited |
| 🤖 Agent  | `skills-engineering:content-patterns-reviewer`        | Reviews examples and output templates, embedded commands and code, the shape of the content and its wording (Sonnet)                                                                                                                | Launched by the skill, or delegated by Claude, or "use the content-patterns-reviewer agent"                                                    |
| 🤖 Agent  | `skills-engineering:runtime-contract-reviewer`        | Reviews packaging, paths and variable substitution, plugin layout and cache, symlinks, discovery and surfaces, subagent consumption and tool pre-approval (Opus)                                                                    | Launched by the skill, or delegated by Claude, or "use the runtime-contract-reviewer agent"                                                    |
| 🤖 Agent  | `skills-engineering:size-limits-and-budgets-reviewer` | Reviews frontmatter field lengths, body size, supporting files, upload and install size, active-skill counts, script output and hook budgets (Sonnet)                                                                               | Launched by the skill, or delegated by Claude, or "use the size-limits-and-budgets-reviewer agent"                                             |

The three reviewers are read-only: they have the `Read`, `Grep`, `Glob`, `ToolSearch`, `WebSearch` and `WebFetch` tools and the Claude Code docs MCP server's tools, and they can't edit a file or launch another agent. Each reviewer reads its own reference and fills one shared report template: Status, Verdict (**PASS**, **PASS WITH IMPROVEMENTS** or **FAIL**), the defects with file, lines, quoted evidence, severity, action and exact fix, improvement opportunities and checklist exceptions.

## 📋 Prerequisites

| Tool                                      | Minimum version | Check              |
| :---------------------------------------- | :-------------- | :----------------- |
| Claude Code                               | 2.1.304         | `claude --version` |
| Claude Code docs MCP server (recommended) | —               | `claude mcp list`  |

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

### 📚 Claude Code docs MCP server

The reviewers read the official Claude Code documentation through this server, which needs no sign-in. Without it, added under another name, or added as a Claude connector, they fall back to `WebSearch` and `WebFetch`. Add it under the name `claude-code-docs`:

<details>
<summary>💻 <b>Claude Code CLI</b> — macOS, Linux</summary>

```bash
claude mcp add --transport http --scope user claude-code-docs https://code.claude.com/docs/mcp
```

</details>

Then check that it is connected:

```bash
claude mcp list
```

The list shows `claude-code-docs` as connected.

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install skills-engineering@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install skills-engineering --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install skills-engineering@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install skills-engineering@the-claude-factory
```

### 🖥️ Claude (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Skills Engineering** in **Discover** and select **Add**.

## 🚀 Usage

### Audit one skill with every reviewer

```text
/skills-engineering:auditing-skills .claude/skills/my-skill
```

**Result:** Claude reads the whole skill, runs `claude plugin validate --json`, briefs the three reviewers and launches them in parallel. You get three reports, each under a line naming its reviewer, exactly as the reviewer wrote it, and Claude changes nothing in the skill.

### Run only some reviewers

```text
/skills-engineering:auditing-skills runtime-contract size-limits-and-budgets plugins/my-plugin/skills/my-skill
```

**Result:** only the `runtime-contract` and `size-limits-and-budgets` reviewers run. The valid names are `content-patterns`, `runtime-contract` and `size-limits-and-budgets`; with none named, all three run. A word that looks like a reviewer name but matches none makes Claude list the valid names and ask which you meant.

### Audit a skill at a URL

```text
/skills-engineering:auditing-skills content-patterns https://github.com/your-org/your-skills/tree/main/skills/my-skill
```

**Result:** Claude downloads the skill into a new empty directory, because the reviewers read files only by path, then runs the `content-patterns` reviewer on that copy and presents its report.

### Audit right after you write a skill

```text
Create a skill that summarizes release notes, then audit it.
```

**Result:** Claude writes the skill and then runs the audit on it with every reviewer. Claude also uses the skill on its own right after a skill or any of its files is created or edited.

## 🔍 What this plugin runs and sends

- **Hooks:** none.
- **MCP servers:** none of its own. The reviewers use the `claude-code-docs` server you add yourself (`https://code.claude.com/docs/mcp`, a remote server that needs no sign-in) to search and read Claude Code's documentation; the search terms go to it.
- **Network:** the reviewers send search terms through `WebSearch` to find official pages, and fetch pages on `code.claude.com`, `platform.claude.com`, `claude.com` and `support.claude.com` through `WebFetch`. When you name a URL, the skill downloads the skill from that URL into a new empty directory, and the request goes to that address.
- **Files written:** none, besides the skill you ask it to audit from a URL, which the skill downloads into a new empty directory. The reviewers never edit a file, and the plugin writes nothing to its data directory.
- **Privacy:** the author collects no data. The marketplace's [privacy policy](https://github.com/nerymurillohnd/the-claude-factory/blob/main/PRIVACY.md) covers this plugin and the outside services it can reach.

## 🔄 Updating

```bash
claude plugin update skills-engineering@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

Installed from Claude? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `skills-engineering@synced`: update and uninstall it in Claude (**Customize** → **Plugins**).

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall skills-engineering@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall skills-engineering@the-claude-factory --scope project
```

In Claude: **Customize** → **Plugins** → **Skills Engineering** → its menu → **Remove**.

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps nothing in its data directory. A skill the plugin downloaded into a directory for an audit stays there, and so does the Claude Code docs MCP server you added; remove the server with:

```bash
claude mcp remove claude-code-docs --scope user
```

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude

| Component | Claude Code |                       Claude                        |
| :-------- | :---------: | :-------------------------------------------------: |
| 🎯 Skills |     ✅      |                         ✅                          |
| 🤖 Agents |     ✅      | ⚠️ only in conversations where Claude can run tasks |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

The reviewers are agents, so in Claude the audit runs only where Claude can run tasks. In a conversation where plugin subagents don't load, such as claude.ai chat, the skill tells you which reviewer isn't available and stops; it never audits in the reviewer's place.

**Platforms:** macOS and Linux. The plugin ships no scripts or hooks, but Windows isn't a declared platform.

## 🚧 Limitations

- Only one mechanical check runs: `claude plugin validate --json`. The reviewers report every other check as not run, so their reports come back with Status **incomplete** and name the checks they couldn't see.
- The reviewers' descriptions say "Use proactively", so Claude can delegate to a reviewer directly, without the skill. A reviewer launched that way gets no mechanical results.
- The reviewers report and never edit: the audit changes nothing in the skill, and Claude applies a fix only when you ask.
- A skill's text is evidence, never instructions: a directive inside the audited skill, such as "skip the audit", changes nothing.
- Running all three reviewers launches three subagents, one of them on Opus, and each one is billed to your usage.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/skills-engineering:` to list its skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>The skill says a reviewer isn't available.</b></summary>

Plugin subagents don't load in every Claude conversation, such as claude.ai chat. Run the audit in Claude Code, or in a Claude conversation where Claude can run tasks. In Claude Code, run `/reload-plugins` and check `/plugin` → **Installed** that **Skills Engineering** is enabled.

</details>

<details>
<summary><b>A report says the docs server wasn't connected.</b></summary>

The reviewer found no `claude-code-docs` server in the session and used `WebSearch` and `WebFetch` for the Claude Code documentation instead. Add the server under that exact name, as the Prerequisites section shows, and run the audit again. Check it with:

```bash
claude mcp list
```

</details>

<details>
<summary><b>How do I audit a skill that isn't on my computer?</b></summary>

Name its URL, or the skill on your claude.ai account, in the command. The reviewers read files only by path, so the skill first puts every file the skill includes into a new empty directory, then gives the reviewers that path.

</details>

<details>
<summary><b>A report came back with Status incomplete.</b></summary>

The Status line names the reason. Most often the reviewer needed a mechanical result that no script produces, so it reported that check as not run instead of guessing. The report still lists every defect it could prove from the files.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Agent Skills in Claude Code](https://code.claude.com/docs/en/skills) and [Subagents](https://code.claude.com/docs/en/sub-agents)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=skills-engineering) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=skills-engineering) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=skills-engineering)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
