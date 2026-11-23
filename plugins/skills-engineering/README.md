<div align="center">

# 🧰 Skills Engineering

<p><strong>Writes and audits Claude skills wherever they live, from personal, project and plugin folders to Claude accounts, the Skills API and URLs: authoring-skills researches your goal, your setup and the skill's domain in current official sources, gets your approval on a versioned design and a plan, then builds the skill and self-reviews it with the plugin's skill checks, and auditing-skills runs the same checks, then nine specialized reviewer agents in parallel, each returning quoted file-and-line evidence, severity, an exact fix and a verdict.</strong></p>

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
[Configuration](#%EF%B8%8F-configuration) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

> [!TIP]
> **TL;DR** — Ask Claude to write a skill, or type `/skills-engineering:authoring-skills`, and get a skill built from current official docs after you approve its design and plan. Type `/skills-engineering:auditing-skills` to get an audit from nine specialized reviewers, each finding backed by the exact file and line.

Skills Engineering is two skills and nine reviewer agents for the whole life of a Claude skill. `authoring-skills` writes a new skill, or changes an existing one, wherever it lives: your personal folder, a project, a plugin, your claude.ai account, a Skills API upload or a subagent. It learns your goal and your setup first, researches the skill's domain in current primary sources, and builds nothing until you approve the design and the plan. `auditing-skills` then checks the finished skill with reviewers that each own one domain, so you fix what is wrong before the skill reaches anyone else.

## ✨ Why use it

- **Skills built from sources, not memory** — before it designs anything, `authoring-skills` reviews the code, data or documents the skill will act on, and reads the primary sources of everything the skill draws on, in any field, at the version you run: official documentation, standards, platform policies, repositories, release notes and the tools' own help.
- **You approve before anything is built** — you review a versioned design document and then a plan. After each correction the design is shown again in full, so the plan starts from what you approved. When the skill is built, Claude asks how to go on and preselects no option.
- **An audit you can check** — nine reviewers run in parallel, each on its own domain. Every finding quotes the file and the lines, gives a severity and an exact fix, and the reports reach you word for word.

## 🧩 What's inside

| Component | Name                                                  | What it does                                                                                                                                                                                       | How it runs                                                                                    |
| :-------- | :---------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------- |
| 🎯 Skill  | `skills-engineering:authoring-skills`                 | Writes or changes a skill in seven phases: your intent, a researched design you approve, a plan you approve, the build, a self-review, a report and a question, then the audit or evals you choose | `/skills-engineering:authoring-skills` or automatically when you ask for a skill               |
| 🎯 Skill  | `skills-engineering:auditing-skills`                  | Runs frontmatter checks, then the reviewer agents in parallel, and presents each report in full with a recommendation of where to start                                                            | `/skills-engineering:auditing-skills` or automatically when you ask to audit or review a skill |
| 🤖 Agent  | `skills-engineering:content-patterns-reviewer`        | Reviews a skill's examples and its embedded commands and code                                                                                                                                      | Launched by `auditing-skills`, or "use the content-patterns-reviewer agent"                    |
| 🤖 Agent  | `skills-engineering:runtime-contract-reviewer`        | Reviews whether a skill's files resolve, package, load and are discovered on every surface it targets                                                                                              | Launched by `auditing-skills`, or "use the runtime-contract-reviewer agent"                    |
| 🤖 Agent  | `skills-engineering:size-limits-and-budgets-reviewer` | Reviews every length, size, count and context budget the skill must stay within                                                                                                                    | Launched by `auditing-skills`, or "use the size-limits-and-budgets-reviewer agent"             |
| 🤖 Agent  | `skills-engineering:knowledge-delta-reviewer`         | Reviews whether each passage gives Claude something it lacks without the skill                                                                                                                     | Launched by `auditing-skills`, or "use the knowledge-delta-reviewer agent"                     |
| 🤖 Agent  | `skills-engineering:task-mechanisms-reviewer`         | Reviews whether the skill controls its task with the right workflows, checklists, validation loops and templates                                                                                   | Launched by `auditing-skills`, or "use the task-mechanisms-reviewer agent"                     |
| 🤖 Agent  | `skills-engineering:frontmatter-description-reviewer` | Reviews the frontmatter, the name and the description Claude chooses the skill by                                                                                                                  | Launched by `auditing-skills`, or "use the frontmatter-description-reviewer agent"             |
| 🤖 Agent  | `skills-engineering:comprehension-reviewer`           | Reviews whether a Claude reading the skill from top to bottom understands the task and is never left to guess                                                                                      | Launched by `auditing-skills`, or "use the comprehension-reviewer agent"                       |
| 🤖 Agent  | `skills-engineering:feature-fit-reviewer`             | Reviews whether each piece belongs in a skill or in another feature, and whether it collides with its environment                                                                                  | Launched by `auditing-skills`, or "use the feature-fit-reviewer agent"                         |
| 🤖 Agent  | `skills-engineering:scripts-reviewer`                 | Reviews the scripts a skill ships, as code Claude runs without reading                                                                                                                             | Launched by `auditing-skills`, or "use the scripts-reviewer agent"                             |

Together the descriptions of these components add about 2,100 tokens to every session. Each one costs more only when it runs: about 5,100 to 5,700 tokens when a skill loads and about 4,900 to 7,200 when a reviewer starts.

## 📋 Prerequisites

| Tool                  | Minimum version | Check                  |
| :-------------------- | :-------------- | :--------------------- |
| Claude Code           | 2.1.304         | `claude --version`     |
| Python                | 3.12            | `python3 --version`    |
| Git (optional)        | —               | `git --version`        |
| ShellCheck (optional) | —               | `shellcheck --version` |
| Ruff (optional)       | —               | `ruff --version`       |

Python runs the skill checks that both skills share: `auditing-skills` runs them before it briefs its reviewers, and `authoring-skills` runs them on the skill it writes. Without it the audit still runs and the reviewers are told those checks didn't run, and `authoring-skills` reports them as not run. Git, ShellCheck and Ruff are optional: the audit uses Git to read the version tags of a plugin dependency, and ShellCheck and Ruff to lint the shell and Python scripts of the skill it audits, each only when it is installed.

The plugin also uses `basename`, `cp`, `dirname`, `head`, `ls` and `mkdir`, which come with macOS and Linux.

### 🤖 Claude Code

Already installed? Bring it to the latest version the way you installed it, as the official [Update Claude Code](https://code.claude.com/docs/en/setup#update-claude-code) guide shows for each installation method. New to Claude Code? Follow the [official setup](https://code.claude.com/docs/en/setup).

### 🐍 Python

Many Linux distributions ship an older Python than 3.12: run the check after you install, and download a current release from [python.org](https://www.python.org/downloads/) when it reports an older one.

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

### 🌿 Git

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install git
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt install git
```

</details>
<details>
<summary>📦 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install git
```

</details>

### 🐚 ShellCheck

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install shellcheck
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt install shellcheck
```

</details>
<details>
<summary>📦 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install ShellCheck
```

</details>

### ⚡ Ruff

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install ruff
```

</details>
<details>
<summary>🚀 <b>uv</b> — macOS, Linux</summary>

```bash
uv tool install ruff@latest
```

</details>
<details>
<summary>🐍 <b>pip</b> — macOS, Linux</summary>

```bash
pip install ruff
```

</details>

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

### Write a new skill

```text
Write a skill that drafts our release notes from the pull requests merged since the last tag
```

**Result:** Claude loads `authoring-skills`, learns your goal, your project and the instructions Claude already loads there, and researches the skill's domain in current primary sources. It shows you a design document, shows it again in full after each correction you make, then writes a plan for you to approve. Once you approve, it builds the skill, reviews it as the model that will load it, and asks how to go on: keep it, run `auditing-skills`, build evals, or something else.

### Audit a skill with every reviewer

```text
/skills-engineering:auditing-skills .claude/skills/release-notes
```

**Result:** Claude runs the frontmatter checks, briefs the nine reviewers and launches them in parallel. You get each reviewer's report complete, with the quoted file and lines, the severity, the exact fix and a verdict, then a **Where to start** list that orders the findings by consequence.

### Audit with only some reviewers

```text
/skills-engineering:auditing-skills frontmatter-description comprehension .claude/skills/release-notes
```

**Result:** Claude runs only the two reviewers you name, and audits the skill at the path. The reviewer names are `content-patterns`, `runtime-contract`, `size-limits-and-budgets`, `knowledge-delta`, `task-mechanisms`, `frontmatter-description`, `comprehension`, `feature-fit` and `scripts`; every other word is read as the skill to audit.

### Improve a skill after an audit

```text
Fix the findings of the audit of the release-notes skill
```

**Result:** Claude loads `authoring-skills`, checks each finding against your skill and the official sources, since a finding can be wrong, and tells you which it applies and which it rejects, with the reason. It changes only what needs to change, after you approve the design and the plan, then reviews the skill again.

## ⚙️ Configuration

The plugin has no options. What it does depends on the skill and the project you point it at:

| What it reads                                                                              | What it does then                                                                                                          |
| :----------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------- |
| The skill you ask it to write or change, and the code, data or documents the skill acts on | Researches the domain and designs the skill around your own material, leaving the values of secrets and credentials unread |
| Your `CLAUDE.md` files, `.claude/rules/`, skills, subagents, hooks and settings keys       | Finds what the new skill would duplicate or collide with, and asks you to decide each overlap                              |
| The skill you ask it to audit, and every file it points to                                 | Reads the whole skill before it briefs any reviewer                                                                        |
| A skill on a claude.ai account, at a URL or in a repository                                | Downloads or exports it into a new empty directory first, because reviewers read files only by path                        |

## 🔍 What this plugin runs and sends

- **Hooks:** none.
- **MCP servers:** none.
- **Commands:** both skills run the plugin's own Python script, `scripts/skill-checks.py`, with `python3` (or `python`), pre-approved for that exact path in the turn that invokes the skill. `auditing-skills` runs it in that turn, so it asks nothing; `authoring-skills` runs it later, in its self-review, where Claude Code may ask you once to approve it. To gather what the reviewers receive it also runs `claude plugin validate`, `claude plugin details`, `claude plugin list --json` and `claude -p` with `/skill-doctor`, `/context` and `/doctor prompt-audit`, which start Claude Code sessions that use your usage. It runs `basename`, `cp`, `head` and `ls` on your skill's files, `git ls-remote --tags` for each plugin dependency that has its own repository, and ShellCheck and Ruff on the skill's scripts when they are installed. `authoring-skills` runs `claude plugin validate` on the skill it writes. The reviewer agents have no Edit, Write or Agent tool, and are told to change none of your files.
- **Network:** the plugin's own script makes no network call. Claude uses its web and documentation tools to read official sources while it researches a skill and while the reviewers verify their findings, and `git ls-remote` contacts a dependency's repository, so search queries and page requests leave your machine as your session's tools and permissions allow. `authoring-skills` writes no credential's value into a skill.
- **Files written:** the skill files you approve in the plan, in the location you chose. The design document, as `design-<skill name>.md`, in the session's scratchpad or in your project's plans folder, never in the skill's folder. During an audit, a results folder named `auditing-skills-fm-…` in your temporary folder (`TMPDIR`, `TEMP` or `TMP`), a temporary copy of the skill or plugin for `claude plugin validate` when the skill sits where validate doesn't read it, and a new empty directory for a skill it downloads or exports. The audit removes its results folder when it ends, and each later audit removes any left by an interrupted one that is older than 24 hours. `auditing-skills` applies no fix until you ask. The plugin writes nothing to its data directory.
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

Update each tool the way you installed it:

```bash
brew upgrade python git shellcheck ruff
sudo apt install --only-upgrade python3 git shellcheck
sudo dnf upgrade python3 git ShellCheck
uv tool upgrade ruff
pip install --upgrade ruff
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall skills-engineering@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall skills-engineering@the-claude-factory --scope project
```

In Claude: **Customize** → **Plugins** → **Skills Engineering** → its menu → **Remove**.

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps nothing in its data directory. The skills it wrote for you, their design documents and the tools you installed for it stay where they are.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude

| Component | Claude Code |                       Claude                        |
| :-------- | :---------: | :-------------------------------------------------: |
| 🎯 Skills |     ✅      |                         ✅                          |
| 🤖 Agents |     ✅      | ⚠️ only in conversations where Claude can run tasks |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

In Claude, `authoring-skills` plans in its reply instead of in plan mode, since plan mode is a Claude Code feature. `auditing-skills` needs its reviewer agents: where Claude can't run tasks it tells you which reviewer it can't launch and stops, and it never audits in a reviewer's place. The skill checks need only Python 3.12 or later; where it is missing, the reviewers are told those checks didn't run.

**Platforms:** macOS and Linux.

## 🚧 Limitations

- `auditing-skills` reports and recommends only: it applies no fix until you ask for one after the reports.
- A full audit launches nine reviewer agents, each loading about 4,900 to 7,200 tokens before it reads your skill, so it uses a good part of your usage. Name only the reviewers you need to run fewer.
- Without Python 3.12 or later the skill checks don't run: the reviewers work without their results, and `authoring-skills` reports its self-check as not run.
- When a selected reviewer can't be launched in your session, the audit stops and names it.
- `authoring-skills` writes no credential's value into a skill: it names each credential by its environment variable and pushes back when you ask it to include a value.
- `authoring-skills` runs evals only when you choose them in its closing question, and each eval run uses your usage.
- When you didn't ask for an audit, `auditing-skills` asks before it runs one, right after a skill is created or edited.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/skills-engineering:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Claude asked whether to audit a skill I never asked it to audit.</b></summary>

`auditing-skills` loads right after Claude creates or edits a skill. It names the skill, tells you that each reviewer runs as its own agent, and offers the full audit or only the reviewers you name. It runs nothing until you agree.

</details>

<details>
<summary><b>Does the audit change my skill?</b></summary>

No. The reviewers have no Edit or Write tool and are told to change none of your files, and `auditing-skills` applies a fix only after the reports and only when you ask for it.

</details>

<details>
<summary><b>The audit says the frontmatter checks didn't run.</b></summary>

The checks need Python 3.12 or later. Check your version, then install or update Python as the Prerequisites section shows.

```bash
python3 --version
```

</details>

<details>
<summary><b>Can I audit a skill that lives on my claude.ai account or at a URL?</b></summary>

Yes. Reviewers read files only by path, so `auditing-skills` first downloads or exports the skill into a new empty directory and gives the reviewers that path.

</details>

<details>
<summary><b>Claude says a reviewer isn't available.</b></summary>

A reviewer runs only where the session can launch it. In Claude, agents work only in conversations where Claude can run tasks. Run the audit in Claude Code, or in a conversation that can run tasks.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Skills in Claude Code](https://code.claude.com/docs/en/skills) and [subagents](https://code.claude.com/docs/en/sub-agents), the two components this plugin ships

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=skills-engineering) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=skills-engineering) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=skills-engineering)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
