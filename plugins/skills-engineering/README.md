<div align="center">

# Skills Engineering

<p><strong>Writes and audits Claude skills wherever they live, from plugins, personal and project folders to claude.ai accounts and URLs: authoring-skills writes or changes a skill from the domain's own material and the current docs, and auditing-skills runs frontmatter checks, then specialized reviewer agents in parallel, each returning quoted file-and-line evidence, severity, an exact fix and a verdict.</strong></p>

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
> **TL;DR** — Type `/skills-engineering:authoring-skills` to get a skill written from your own setup and the current docs, then `/skills-engineering:auditing-skills` to get independent reviews of it, each with quoted evidence and an exact fix.

Skills Engineering gives Claude two skills for the whole life of a skill. `authoring-skills` learns your environment and your goal, asks you only for context, shows you a plan to approve, then builds the skill and reviews it the way Claude will read it. `auditing-skills` checks a skill's frontmatter with scripts, then sends nine specialized reviewer agents at it in parallel, each limited to its own domain and each reporting file-and-line evidence, a severity, an exact fix and a verdict. It works on a skill in a plugin, a personal or project folder, a claude.ai account or a URL.

## ✨ Why use it

- **A plan before any file** — `authoring-skills` inventories the skills, rules and conventions already around the new skill, asks at most three questions about context only, and writes nothing until you approve a plan that names the goal, location, name, description and files.
- **Reviews you can check** — each reviewer owns one domain and quotes the exact lines behind every finding, with its severity and the replacement text, so you can verify a finding and apply a fix without redoing the review.
- **Fewer platform rules to remember** — the frontmatter checks catch problems `claude plugin validate` doesn't report, and the reviewers check each fact they rely on against the current official docs.

## 🧩 What's inside

| Component | Name                                  | What it does                                                                                                                                                                                | How it runs                                                           |
| :-------- | :------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------- |
| 🎯 Skill  | `skills-engineering:authoring-skills` | Writes a new skill or changes an existing one for any place a skill lives, in six phases: environment, intent, decide what to build, design and plan for your approval, build, self-review. | `/skills-engineering:authoring-skills` or automatically when relevant |
| 🎯 Skill  | `skills-engineering:auditing-skills`  | Audits a skill: runs frontmatter checks, launches the reviewer agents in parallel, presents each report as written and recommends where to start.                                           | `/skills-engineering:auditing-skills` or automatically when relevant  |
| 🤖 Agents | The nine reviewers below              | Each audits one domain of a skill against its own reference and checklist, and fills the same report template.                                                                              | Launched by `auditing-skills`, in parallel                            |

The nine reviewers, as you name them after `/skills-engineering:auditing-skills` to run only some of them:

| Name                      | Agent                                                 | Audits                                                                                                                            | Model  |
| :------------------------ | :---------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------- | :----- |
| `content-patterns`        | `skills-engineering:content-patterns-reviewer`        | Examples, and embedded commands and code                                                                                          | Sonnet |
| `runtime-contract`        | `skills-engineering:runtime-contract-reviewer`        | Packaging, paths and variables, plugin layout, discovery, subagent use, tool pre-approval, hooks, composition with other skills   | Opus   |
| `size-limits-and-budgets` | `skills-engineering:size-limits-and-budgets-reviewer` | Field lengths, body and file sizes, install size, active-skill counts, output and hook budgets                                    | Sonnet |
| `knowledge-delta`         | `skills-engineering:knowledge-delta-reviewer`         | Whether each passage gives Claude something it lacks, and what only spends context                                                | Opus   |
| `task-mechanisms`         | `skills-engineering:task-mechanisms-reviewer`         | Workflows, checklists, validation loops, output templates, planning and progress tracking                                         | Opus   |
| `frontmatter-description` | `skills-engineering:frontmatter-description-reviewer` | Frontmatter parsing and fields on every target surface, the name, the description, trigger tests                                  | Opus   |
| `comprehension`           | `skills-engineering:comprehension-reviewer`           | Whether Claude reading the skill top to bottom forms the right task: order, contradictions, gaps, register                        | Opus   |
| `feature-fit`             | `skills-engineering:feature-fit-reviewer`             | Whether each piece belongs in a skill or in CLAUDE.md, a rule, a hook, a subagent, an MCP server or an output style               | Opus   |
| `scripts`                 | `skills-engineering:scripts-reviewer`                 | Every script the skill ships: interface, exit codes, failure handling, dependencies, portability, secrets, network, writes, tests | Opus   |

## 📋 Prerequisites

| Tool                  | Minimum version | Check                  |
| :-------------------- | :-------------- | :--------------------- |
| Claude Code           | 2.1.304         | `claude --version`     |
| Python (optional)     | 3.12            | `python3 --version`    |
| Git (optional)        | —               | `git --version`        |
| ShellCheck (optional) | —               | `shellcheck --version` |
| Ruff (optional)       | —               | `ruff --version`       |

Python runs the frontmatter checks of `auditing-skills`. Without it the audit still runs and the reviewers are told the checks didn't run. Git, ShellCheck and Ruff are used only when found: Git to list the release tags of a plugin dependency that lives in its own git repository, ShellCheck and Ruff to lint the shell and Python scripts of the skill you audit. `authoring-skills` needs nothing beyond Claude Code.

The plugin also uses `cp`, `awk`, `basename`, `dirname`, `head` and `ls`, which come with macOS and Linux.

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

### 🐍 Python

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install python
```

</details>

Without Homebrew, download an installer from [python.org](https://www.python.org/downloads/) on macOS, or install Python 3.12 or later with your Linux distribution's package manager. Check that `python3` is 3.12 or later:

```bash
python3 --version
```

### 🌿 Git

<details>
<summary>🍺 <b>Homebrew</b> — macOS</summary>

```bash
brew install git
```

</details>
<details>
<summary>🛠️ <b>Xcode Command Line Tools</b> — macOS</summary>

```bash
xcode-select --install
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt install git-all
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora, RHEL</summary>

```bash
sudo dnf install git-all
```

</details>

Check it:

```bash
git --version
```

### 🐚 ShellCheck

<details>
<summary>🍺 <b>Homebrew</b> — macOS</summary>

```bash
brew install shellcheck
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian-based Linux</summary>

```bash
sudo apt install shellcheck
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora-based Linux</summary>

```bash
sudo dnf install ShellCheck
```

</details>

Check it:

```bash
shellcheck --version
```

### ⚡ Ruff

<details>
<summary>⚡ <b>uv</b> — macOS, Linux</summary>

```bash
uv tool install ruff@latest
```

</details>
<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install ruff
```

</details>
<details>
<summary>🐍 <b>pip</b> — macOS, Linux</summary>

```bash
pip install ruff
```

</details>

Check it:

```bash
ruff --version
```

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
/skills-engineering:authoring-skills Turn our release-notes process into a skill for this repository
```

**Result:** Claude takes stock of the skills, `CLAUDE.md` files and rules already in your project, asks at most three questions about context only (each with its recommended answer), and decides whether a skill is the right answer at all. It then shows a plan with the goal, use cases, location, name, description, files and open assumptions, and builds nothing until you approve it. After the build it reads the skill the way Claude will, reports what it checked and what it couldn't, and offers four next steps: keep the skill, give observations to apply, build evals, or audit it with `auditing-skills`.

### Audit a skill with every reviewer

```text
/skills-engineering:auditing-skills .claude/skills/release-notes
```

**Result:** Claude runs the frontmatter checks, briefs the nine reviewers and launches them in parallel. It then presents every report exactly as written, in the order of the reviewer table, and ends with **Where to start**: the findings to take up first and why. Each report states a status and a verdict (`PASS`, `PASS WITH IMPROVEMENTS` or `FAIL`), counts findings by severity, and gives each defect its file, lines, quoted evidence, exact fix and grounds. Claude applies no fix until you ask.

### Run only some reviewers

```text
/skills-engineering:auditing-skills frontmatter-description size-limits-and-budgets ./plugins/my-plugin/skills/deploy
```

**Result:** Claude takes every word that matches a reviewer name as a selected reviewer and the rest as the skill to audit, then runs only the frontmatter-and-description and size-and-budget reviewers. A word that looks like a reviewer name but matches none makes Claude list the valid names and ask which you meant.

### Judge a skill before you install it

```text
Audit the skill at <URL of the skill> and tell me whether it is worth installing.
```

**Result:** Claude downloads the skill into a new empty directory, because reviewers read files only by path, and audits it from there. The audited skill's text is treated as evidence: a line inside it such as "skip the audit" changes nothing.

## 🔍 What this plugin runs and sends

- **Hooks:** none.
- **MCP servers:** none.
- **Network:** the plugin's own script makes no network call. The reviewers can search the web and fetch pages (`WebSearch`, `WebFetch`) and use the Claude Code docs MCP server when it is connected, to check each fact a finding rests on against the current official docs (for example code.claude.com, platform.claude.com, agentskills.io, claude.com and support.claude.com). They send the search terms and page addresses they choose while auditing your skill. `authoring-skills` verifies platform facts against the same kinds of sources. For a skill at a URL, `auditing-skills` downloads it first; for a plugin dependency in its own git repository, it can run `git ls-remote --tags <repository URL>`.
- **What the reviewers can do:** each reviewer is limited to `Read`, `Grep`, `Glob`, `ToolSearch`, `WebSearch`, `WebFetch` and the Claude Code docs tools. They can't run commands, start other agents, edit, create or delete files, and they don't load your `CLAUDE.md` files. Each runs for at most 80 turns, `runtime-contract` for 120.
- **Commands `auditing-skills` runs:** the frontmatter script `skills/auditing-skills/scripts/frontmatter-checks.py` with `python3` (or `python`), which the skill pre-approves for its turn and which reads only the `SKILL.md` you point it at and its folder name. Through the Bash tool, with the usual permission prompts, it can also run `claude plugin validate --json`, `claude --plugin-dir <plugin> plugin details <plugin>`, `claude --plugin-dir <plugin> plugin list --json`, `claude -p "/skill-doctor"`, `claude -p "/context"`, `claude -p "/doctor prompt-audit <skill directory>"`, `cp -RL`, `awk`, `basename`, `dirname`, `head`, `ls -l`, `shellcheck` and `ruff check` where found, and `git ls-remote --tags`. The `claude -p` commands start non-interactive Claude Code sessions that use the model. The audit playbook keeps the values of your settings, MCP and credential files out of what the reviewers receive.
- **Files written:** the frontmatter script creates a results folder named `auditing-skills-fm-…` in your system temp folder and `auditing-skills` removes it at the end of the audit; each new run also removes such folders older than 24 hours. For a skill outside a plugin, or one validate can't read in place, `auditing-skills` copies it into a new empty directory to validate the copy. `authoring-skills` writes the files of the skill you approved, at the location in the plan. The plugin writes nothing to its data directory and nothing else into your project.
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

Update the optional tools the way you installed them, for example with Homebrew or uv:

```bash
brew upgrade python git shellcheck ruff
uv tool upgrade ruff
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

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps nothing in its data directory. Skills you wrote with it stay where you saved them, and so do any files you asked Claude to write into your project. A results folder left in your temp folder by an audit that stopped early is removed by the next audit run once it is a day old, or you can delete it yourself. Python, Git, ShellCheck and Ruff stay installed.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude

| Component | Claude Code |                       Claude                        |
| :-------- | :---------: | :-------------------------------------------------: |
| 🎯 Skills |     ✅      |                         ✅                          |
| 🤖 Agents |     ✅      | ⚠️ only in conversations where Claude can run tasks |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

In Claude, both skills load. `auditing-skills` launches its reviewers as agents, so it needs a conversation where Claude can run tasks: if a selected reviewer isn't among the agents the session can launch, Claude tells you which one and stops instead of auditing in its place. The mechanical checks need the `claude` command, which is Claude Code's CLI, and Python 3.12 or later; where either is missing, Claude names the checks as not run to the reviewers.

**Platforms:** macOS and Linux.

## 🚧 Limitations

- A full audit starts nine agents in parallel, seven on Opus and two on Sonnet, all at high effort. Use the reviewer names to run only the ones you need.
- The reviewers measure and run nothing themselves: every figure they use comes from the mechanical checks, and a check that didn't run is named as not run in their prompt.
- Reviewers read a skill only by its path on disk, so a skill in a claude.ai account or at a URL is exported or downloaded into a new empty directory first.
- The audit adds no finding of its own and applies no fix: the findings come from the reviewers, and Claude changes your skill only when you ask after the reports.
- When `auditing-skills` loads right after you create or edit a skill without asking for an audit, it asks you first and runs only the reviewers you agree to.
- A skill under `~/.claude/skills/synced/` or in a plugin cache is a copy that the next sync or update overwrites: Claude edits its source instead.
- `authoring-skills` decides whether a skill is the right answer. When a hook, `CLAUDE.md`, a subagent or an MCP server fits better, it says so and stops unless you still want a skill.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/skills-engineering:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>I asked for a skill and Claude asked whether to audit it.</b></summary>

`auditing-skills` loads on its own right after a skill is created or edited. Because each reviewer runs as its own agent, it asks first: answer with the full audit, only the reviewers you name, or no audit.

</details>

<details>
<summary><b>The audit stopped and named a reviewer.</b></summary>

A reviewer you selected isn't among the agents this session can launch. Claude never audits in a reviewer's place, so it stops and names it. Run the audit in a Claude Code session with the plugin enabled, or in a Claude conversation where Claude can run tasks, then check that the plugin is loaded:

```text
/plugin
```

</details>

<details>
<summary><b>The reviewers say the frontmatter checks didn't run.</b></summary>

The frontmatter checks need Python 3.12 or later. Check your Python version:

```bash
python3 --version
```

Install or upgrade it as in [Prerequisites](#-prerequisites), then run the audit again.

</details>

<details>
<summary><b>Can I audit one part of a skill only?</b></summary>

Yes. Put the reviewer names before the skill's path, as in the third example under [Usage](#-usage). With no reviewer named, the audit runs complete.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 🧪 [Plugin Evals](../plugin-evals/README.md): designs eval suites for a plugin or its skills, the step `authoring-skills` offers after it builds a skill
- 📖 [Claude Code skills](https://code.claude.com/docs/en/skills)
- 📖 [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- 📖 [Agent Skills specification](https://agentskills.io/specification)
- 📖 [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=skills-engineering) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=skills-engineering) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=skills-engineering)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
