<div align="center">

# 🩺 Agent Files Diagnostics

<p><strong>Keeps the files that steer Claude Code and Codex accurate: audits CLAUDE.md, AGENTS.md, rules, memory, subagent definitions, output styles, loop.md and every Markdown file they point to with read-only agents, and writes one evidence-backed report of broken links and false, stale, duplicated, conflicting and misplaced instructions.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fagent-files-diagnostics%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Testing%20%26%20Quality-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.271-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it audits the instruction files Claude Code loads on your computer, including `~/.claude` and managed settings, and its read-only guarantee comes from Claude Code's per-agent tool lists. It doesn't install in the Claude app (chat or Cowork).

> [!TIP]
> **TL;DR** — Type `/agent-files-diagnostics:agent-context-audit`, approve the plan Claude shows you, and get one report that tells you, line by line, which of your instructions are false, stale, dead, duplicated, contradictory or in the wrong file, with the evidence behind each one. Nothing is edited.

## ✨ Why use it

Instruction files grow by accretion. A `CLAUDE.md` mentions a script that was renamed months ago, a rule repeats what a memory file already says, an `AGENTS.md` contradicts the `CLAUDE.md` that imports it, and an import points at a file that no longer exists. The model reads all of it every session, and you only notice when it does something odd.

- **One report, every file** — every `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, rule, memory file, subagent definition, output style and `loop.md` that Claude Code or Codex loads, plus every Markdown file they point to, read from the first line to the last. The report shows which lines each reviewer read, so coverage is proven, not assumed.
- **Evidence, not opinions** — a finding exists only when it conflicts with something you can check: another file and line, a fact in your repository, a documented default or a current official page. Every finding carries the exact lines, the excerpt and what it conflicts with.
- **Checked against today's documentation** — how each file loads, the import depth, the size limits and the valid frontmatter keys come from the official Claude Code and Codex pages fetched during the audit, never from the model's memory. Claims your files make about tools and versions are verified on GitHub, package registries and official docs.
- **Independent verification** — a separate agent that produced no finding checks every one of them against your files before it reaches the report, and rejects what it can't confirm.
- **Read-only, by construction** — the agents have no tool that writes, reviewers read masked copies instead of your originals, and the only files the audit creates are the report and its temporary working copies. Nothing is corrected for you: the report proposes, you decide.
- **You approve before anything runs** — the first response is a plan: which files it will read, how many agents, where the report goes, what leaves your machine. The audit starts only when you say so, and runs in background agents while you keep working.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `agent-files-diagnostics:agent-context-audit` | Plans the audit, asks for your approval, runs the 14 phases, directs the four agents, validates every finding and writes the one report | `/agent-files-diagnostics:agent-context-audit` only; Claude never starts it on its own |
| 🤖 Agent | `agent-files-diagnostics:evidence-collector` | Inventories every instruction file with how it loads, follows pointers, and collects the repository facts instructions are checked against | Launched by the skill |
| 🤖 Agent | `agent-files-diagnostics:docs-researcher` | Builds the current official baseline for how Claude Code and Codex load files, and verifies the claims your files make about tools and versions | Launched by the skill; the only agent that reaches the web |
| 🤖 Agent | `agent-files-diagnostics:instruction-reviewer` | Reads every assigned line of a package of files and reports findings with line evidence | Launched by the skill, one per package |
| 🤖 Agent | `agent-files-diagnostics:audit-verifier` | Checks that every reviewer read its lines and that every finding is real, correctly located and correctly sourced, then verifies the finished run | Launched by the skill |

Skills, saved commands, plugins and configuration files are counted and recorded but never audited: an instruction that points at one of them is checked, the target is not. To audit a skill, use [Skill Diagnostics](../skill-diagnostics#readme).

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.271 or later — check with `claude --version`. The agents start without your `CLAUDE.md` files, which needs this version |
| **Surfaces** | Claude Code only. See [Compatibility](#-compatibility) |
| **External tools** | A POSIX shell with `perl`, `cp`, `wc` and `shasum` or `sha256sum` (macOS and Linux ship them), for the masked copies and the hashes. `git`, when the repository uses it, for the baseline. Codex is optional: without it, its files are still audited from the documentation |
| **Network** | Used to fetch the official Claude Code and Codex documentation and to verify the claims your files make about tools and versions. It reaches `code.claude.com`, `platform.claude.com`, `developers.openai.com`, `learn.chatgpt.com`, `github.com` (official repositories), `registry.npmjs.org`, `www.npmjs.com` and `pypi.org`, through the Claude Code docs and GitHub MCP servers when your session has them, or `WebFetch` and `WebSearch` otherwise. Queries carry tool names, package names and versions only, never the content of your files. You approve the list of domains in the plan |
| **Accounts / API keys** | None |
| **Usage** | Every agent sends its own requests, counted against your plan or API bill. The plan tells you how many agents it proposes before anything runs |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install agent-files-diagnostics --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install agent-files-diagnostics@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install agent-files-diagnostics --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install agent-files-diagnostics@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

Start every audit with `/agent-files-diagnostics:agent-context-audit`; Claude doesn't start the skill on its own, so an audit, and the agents it pays for, never begins without you typing it.

### Audit everything this repository loads

```text
/agent-files-diagnostics:agent-context-audit
```

**Result:** Claude answers with a plan, not an audit: the files it intends to read, including the user-level and managed ones outside the repository, how the files are grouped into review packages, how many agents will run, where the report will be written, which temporary files it will create and delete, the domains it may fetch from, the depth to which it follows imports and links, and the limits of the run. You approve or adjust it. The audit then runs in the background and ends with the report's location, the audit status, the counts by severity, each high-severity finding with its file and lines, the open decisions, and confirmation that no audited file was modified.

### Narrow it to what you care about

```text
/agent-files-diagnostics:agent-context-audit only the rules in .claude/rules, not Codex
```

**Result:** the same plan-then-audit flow, with the plan limited to what you asked for. The report says what was left out at your request, and the status carries the qualifier `narrowed`.

### Read a finding

Every finding in the report has the same shape: a stable identifier, one category (`false`, `wrong`, `obsolete`, `dead`, `ambiguous`, `duplicated`, `overlapping`, `misplaced`, `contradictory`, `redundant-with-defaults` or `non-conformant`), a severity, the exact path and lines, the excerpt, what it conflicts with (another file and line, a repository fact, a documented default or an official page with its quote), and a recommendation: retain, remove, rewrite, relocate, consolidate or investigate, with the replacement text when it proposes one.

### Come back to the report

```text
Show me the medium-severity findings in .claude/rules/testing.md from the last audit.
```

**Result:** Claude presents them from the existing report without running a new audit.

## 🔄 Updating

```bash
claude plugin update agent-files-diagnostics@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Agent Files Diagnostics** → **Update now**. Then run `/reload-plugins`.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall agent-files-diagnostics@the-claude-factory
```

Installed with `--scope project`? Add `--scope project` here too.

In a session: `/plugin` → **Installed** → **Agent Files Diagnostics** → **Uninstall**.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ➖ the files it audits and the agents it relies on live in Claude Code |
| 🤖 Agents | ✅ | ➖ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/agent-files-diagnostics:` to list its skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>I asked Claude to audit my CLAUDE.md and nothing happened.</b></summary>

The skill starts only from `/agent-files-diagnostics:agent-context-audit`. Claude can't start it from a plain request, so an audit that runs several agents at your cost never begins by accident. Type the command, add any narrowing after it, and approve the plan.

</details>

<details>
<summary><b>Does it change my files?</b></summary>

No. The audited files, your git state and your configuration are never modified. The audit writes the report at the location you approved, and temporary masked copies of the audited files that it deletes at the end. The report proposes corrections; applying them is a separate task you start yourself.

</details>

<details>
<summary><b>What leaves my machine?</b></summary>

Only documentation fetches and verification queries, and they carry tool names, package names and versions, never the text of your files. The agents that read your files have no web tools; the one agent that reaches the web never reads them. The plan lists the domains before you approve it.

</details>

<details>
<summary><b>Why does it ask for approval before starting?</b></summary>

Because the audit reads files outside your repository, such as `~/.claude/CLAUDE.md`, your rules, your memory and any managed policy, and runs several agents at your cost. The plan shows exactly what it will read, write and spend, so you decide with the facts in front of you. The run starts only after you approve.

</details>

<details>
<summary><b>I don't use Codex. Does the audit still work?</b></summary>

Yes. Codex is optional: when it isn't installed, its files, if you have any, are still inventoried and audited from the documentation, and whatever only the installed program could settle is marked as unverified in the report.

</details>

<details>
<summary><b>Does it audit my skills and settings too?</b></summary>

No. Skills, saved commands, plugins, settings, hooks and MCP configuration are counted and listed, and configuration is read only to learn which Markdown files load. An instruction that points at one of them is audited; the target is not. For skills, use [Skill Diagnostics](../skill-diagnostics#readme).

</details>

<details>
<summary><b>What does an audit cost?</b></summary>

Every agent sends its own requests, counted against your plan or API bill, and the number of reviewer agents follows from how many files you have. The plan states the agent count and the limits of each one before anything runs. To spend less, narrow the scope in the plan, for example to one directory or one runtime.

</details>

<details>
<summary><b>The report says the audit is partial.</b></summary>

An audited file changed or disappeared while the audit ran, or a reviewer could not finish its lines within the limits of the plan. The report names the file or the unread lines and the scope to rerun. A `narrowed` status is different: it means you limited the scope on purpose.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🩺 [Skill Diagnostics](../skill-diagnostics#readme) — audit the skills this plugin only lists
- 📖 [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- 📖 [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=agent-files-diagnostics) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=agent-files-diagnostics) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=agent-files-diagnostics)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
