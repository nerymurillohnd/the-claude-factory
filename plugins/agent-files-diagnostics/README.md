<div align="center">

# 🩺 Agent Files Diagnostics

<p><strong>Keeps the files that steer Claude Code and Codex accurate: audits CLAUDE.md, AGENTS.md, rules, memory, subagent definitions, output styles, loop.md and every Markdown file they point to with read-only agents, and writes one evidence-backed report of broken links and false, stale, duplicated, conflicting and misplaced instructions.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fagent-files-diagnostics%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Testing%20%26%20Quality-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.300-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it audits the instruction files Claude Code loads on your computer, including `~/.claude`, and it runs its agents through Claude Code's dynamic workflows, which the Claude app (chat or Cowork) doesn't have. Its read-only guarantee comes from the agents' tool lists, not from a prompt.

> [!TIP]
> **TL;DR** — Type `/agent-files-diagnostics:agent-context-audit`, approve the scope Claude shows you, and get one report that tells you, line by line, which of your instructions are false, stale, dead, duplicated, contradictory or in the wrong file, with the evidence behind each one and who checked it. Nothing is edited.

## ✨ Why use it

- **Your instruction files drift.** A `CLAUDE.md` names a script that was renamed, a rule's `paths` match nothing anymore, a memory entry contradicts the project guide, `AGENTS.md` repeats half of `CLAUDE.md`. Every session pays for that text, and some of it steers Claude the wrong way.
- **Every finding is proven.** Each one names the file and lines, quotes the text, and says what it conflicts with: another file and line, a fact in the repository, an official doc, or a documented default. Findings without a conflict are refused.
- **Nobody's word is taken for it.** The auditors read every line (the script proves it from their transcripts), a reviewer compares meaning across files and challenges the auditors, independent verifiers re-read every finding, and Claude inspects each one itself before it reaches the report.
- **It never touches your files.** Agents have no write tool, the script writes only the report folder, and a hash of every source before and after the run proves nothing changed.
- **It knows what loads.** The inventory says for each file whether it loads automatically, on demand or not at all, whether the documentation says so or nobody could tell, how much of it the audit could read, and whether it still governs anything.

## 🧩 What's inside

| Component | Name | What it does |
| :-- | :-- | :-- |
| 🎯 Skill | `agent-context-audit` | Runs the audit end to end: agrees the scope with you, prepares the inventory, starts the two workflows, inspects every finding, writes the report and stops. Started only with `/agent-files-diagnostics:agent-context-audit`; Claude never starts it on its own. `latest` shows the newest report. |
| 🔁 Workflow | `audit-domains` | One read-only `domain-auditor` per package, in parallel, each reading every assigned line. |
| 🔁 Workflow | `review-and-verify` | The cross-domain reviewer, the challenge round with the auditors, independent verifiers over every finding, and researchers for claims about tools and versions. |
| 🤖 Agent | `domain-auditor` | Reads one package completely and reports evidence-backed findings; answers the reviewer's challenges. Read, Grep and Glob only. |
| 🤖 Agent | `cross-domain-reviewer` | Decides every finding, judges similar instructions across files, finds conflicts no single auditor could see. Read, Grep and Glob only. |
| 🤖 Agent | `finding-verifier` | Re-reads the cited lines and conflicts of every finding and says whether it holds. Read, Grep and Glob only. |
| 🤖 Agent | `claim-researcher` | Checks claims about third-party tools and versions against official documentation, repositories and registries. WebFetch and WebSearch only: it has no tool that reads a file, and the claims reach it as one-sentence statements with no path or project name. |

The skill also ships a Python script that does the deterministic work: the inventory, the redacted working copies, the mechanical checks, the coverage proof, the validation of every finding, the integrity check and the report.

## ✅ Requirements

- **Claude Code 2.1.300 or later**, signed in, with **dynamic workflows** available: they come with every paid plan; on Pro, turn them on from the **Dynamic workflows** row in `/config`. If `disableWorkflows` or `CLAUDE_CODE_DISABLE_WORKFLOWS` is set, the skill says so and stops; it never audits by other means.
- **Python 3.9 or later** as `python3` on `PATH` (standard library only), and **git**. macOS, Linux or WSL; native Windows is refused with a message.
- **Network**, for two things: the script compares its bundled knowledge of how Claude Code and Codex load files with the live documentation on `code.claude.com`, `developers.openai.com` and `learn.chatgpt.com` (skip it with `--offline`), and the `claim-researcher` fetches official documentation, official repositories and package registries. Both send only tool and package names and generic terms, never your files. Everything else runs on your machine.
- **Codex CLI is optional.** Its `AGENTS.md` chain and memories are audited whenever its files exist.

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

Open Claude Code in the repository you want audited. Every audit starts with the slash command; Claude never starts one on its own, because it costs agent time on your plan.

### Audit everything this repository loads

```text
/agent-files-diagnostics:agent-context-audit
```

Claude tells you what it will read (the project's files and the user-level files Claude Code and Codex load for it), where the report goes (`.claude/agent-context-audit/<run>/` in the repository, git-ignored), and that nothing changes. After your approval it prepares the inventory, starts the two workflows (`/workflows` shows their progress), inspects every finding, and comes back with the report. Unless your settings already allow them, you approve the script's commands, each workflow's launch, and the researcher's web access as they come.

### Read a finding

Each finding in `report.md` has an ID that survives across runs, the file and lines, the excerpt, what it conflicts with, the evidence, a recommendation (keep, remove, merge, move, revise with the replacement shown, or investigate), and who checked it: the independent verifier and Claude itself. Open decisions show both positions.

### Come back to the report

```text
/agent-files-diagnostics:agent-context-audit latest
```

Shows the newest report without running anything. Each run also records what changed since the previous one: new, resolved, persisting and regressed findings.

### Ask for a cleanup

An audit never applies fixes, and finishing one doesn't authorize any. Read the report, then ask for the changes you want in a new request, naming the finding IDs.

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

Reports stay in each repository's `.claude/agent-context-audit/` folder; delete it when you no longer want them.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads, but stops at its first check: dynamic workflows exist only in Claude Code |
| 🤖 Agents | ✅ | ⚠️ Cowork sessions only, and unused without the workflows |
| 🔁 Workflows | ✅ | ➖ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>I asked Claude to audit my CLAUDE.md and nothing happened.</b></summary>

The skill only starts from its slash command, `/agent-files-diagnostics:agent-context-audit`, so that an audit never runs agents on your plan without you asking. Type the command.

</details>

<details>
<summary><b>Claude says dynamic workflows aren't available.</b></summary>

The audit runs its agents through Claude Code's dynamic workflows and doesn't replace them with anything else. They come with every paid plan; on Pro, turn them on from the **Dynamic workflows** row in `/config`. Check that `disableWorkflows` isn't set in your settings or by your organization, and that `CLAUDE_CODE_DISABLE_WORKFLOWS` isn't in your environment.

</details>

<details>
<summary><b>Will it change my files?</b></summary>

No. The agents have no write tool, the script writes only the report folder, and every audited file is hashed before and after the run; a difference is reported as a problem and makes the run `partial`. Fixes are a separate request after you read the report.

</details>

<details>
<summary><b>What leaves my computer?</b></summary>

Two things: the fixed documentation pages the script compares with the live docs (on `code.claude.com`, `developers.openai.com` and `learn.chatgpt.com`), and, for claims about third-party tools, the tool or package names the `claim-researcher` looks up on official sites. No file content, path or project name is sent. The auditors, the reviewer and the verifiers have no web tools, and the researcher has no file tool.

</details>

<details>
<summary><b>The report says `partial`. What does it mean?</b></summary>

Something was not covered: a package of files could not be audited, an agent skipped lines (the script proves coverage from each agent's transcript), the review did not finish, a finding was not inspected, or a file changed during the run. The findings shown passed validation; the list may be incomplete. The report's Limitations section names each gap.

</details>

<details>
<summary><b>Why isn't my settings.json (or a hook, or an MCP server) in the findings?</b></summary>

Configuration is consulted only to learn which Markdown files load; it is never audited. Skills, commands and plugins are counted, never reviewed. The audit covers the instruction and memory Markdown and the files it imports.

</details>

<details>
<summary><b>I don't use Codex.</b></summary>

Then there is nothing of Codex to audit and the report says so. An `AGENTS.md` in the project is still inventoried, because Claude Code can read it too.

</details>

<details>
<summary><b>How much does a run cost?</b></summary>

The report lists the tokens of every agent whose transcript was found, summed from it. A small repository with a handful of instruction files takes a few agents and a few minutes; the count grows with the files. Cost in money isn't available to the audit; `/usage` shows your plan's usage and a session estimate.

</details>

<details>
<summary><b>A finding is wrong.</b></summary>

Tell Claude which ID and why. Dismissed findings and rejected items are listed in the report's Limitations section with their reason, so nothing disappears silently, and the next run shows what changed. Open an issue if a check itself is wrong.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🩺 [Skill Diagnostics](../skill-diagnostics#readme) — audit the skills this plugin only lists
- 📖 [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- 📖 [Dynamic workflows](https://code.claude.com/docs/en/workflows)
- 📖 [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=agent-files-diagnostics) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=agent-files-diagnostics) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=agent-files-diagnostics)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
