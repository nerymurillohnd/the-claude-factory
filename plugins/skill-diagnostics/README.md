<div align="center">

# 🩺 Skill Diagnostics

<p><strong>Audits Claude skills for best-practice conformance, portability and whether a model can run them without guessing, with file-and-line evidence and one verdict.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fskill-diagnostics%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Testing%20%26%20Quality-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.176-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Type `/skill-diagnostics:audit <skill folder>` and get one report that says whether the skill follows the official rules, works where you plan to use it, and can be run by a model without guessing, with the exact line behind every finding.

## ✨ Why use it

A skill can look finished to the person who wrote it and still fail the model that runs it: a placeholder nothing defines, a reference that contradicts `SKILL.md`, a description that never triggers, a field that breaks the upload to claude.ai.

- **Two audits in one pass** — conformance (official rules, recommendations, portability) and executability (could a model follow it without guessing) run in parallel and come back as one report with one verdict.
- **Reads every line** — both auditors read every file of the skill from start to end, scripts and hidden files included; nothing is sampled or skimmed. If a file can't be listed or read, the report names it, and a gap that matters gives *not determinable* instead of a pass.
- **Evidence, not opinions** — every finding quotes the exact text with its file and line, and says how to fix it.
- **Verified before it counts** — before the verdict, every finding is checked again: its quote against your files, any rule or platform claim against the live official Claude documentation (with the URL and the exact sentence), and the official Claude Code changelog from your version on. Findings that don't hold up are corrected or withdrawn.
- **Checks what validation skips** — `claude plugin validate` confirms the structure; Skill Diagnostics also checks name and description limits, quoting that breaks strict YAML, argument placeholders, broken links and script setup, with whatever tools your session has.
- **Ready for every surface** — every audit covers Claude Code, the Claude app, claude.ai skill uploads and the Skills API, flags what each one rejects or skips, and ranks it by whether your skill reaches that surface today.
- **Catches new skills as you write them** — after a `SKILL.md` is created or changed, for example with Anthropic's `skill-creator`, Claude offers an audit before you move on.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `skill-diagnostics:audit` | Lists the skill's files, launches both lenses in parallel, verifies and merges the results, and gives the verdict | `/skill-diagnostics:audit <path>`, or ask Claude to audit, review or check a skill |
| 🤖 Agent | `skill-diagnostics:conformance-auditor` | Checks one skill against the documented rules and recommendations, on all four surfaces | Launched by the skill, one per skill |
| 🤖 Agent | `skill-diagnostics:executability-auditor` | Traces every workflow of one skill as the model that must run it | Launched by the skill, one per skill |
| 🪝 Hook | `PostToolUse` | After a `SKILL.md` is written or edited, asks Claude to offer an audit once the skill is finished (or to run it, if you [configure](#️-configuration) that) | Automatically, once per skill per session |

Skill Diagnostics only audits. To create a skill, use Anthropic's `skill-creator`, then audit the result.

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.176 | `claude --version` |
| Python, as `python3` on your `PATH` | 3.12 | `python3 --version` |
| git (optional: to audit a skill from a URL; on Windows, Git for Windows is required) | — | `git --version` |

Python runs the hook. On Windows the hook runs through Git Bash, which comes with [Git for Windows](https://git-scm.com/downloads/win), so run `python3 --version` there.

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

Or download the installer from [python.org](https://www.python.org/downloads/). On Windows, Python's install manager adds the `python3` command; the older full installer (`python-3.x.exe`) adds only `python` and `py`, so the hook can't find Python.

### 🔀 git

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
<summary>🚢 <b>MacPorts</b> — macOS</summary>

```bash
sudo port install git
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt-get install git
```

</details>
<details>
<summary>📦 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install git
```

</details>
<details>
<summary>📦 <b>pacman</b> — Arch Linux</summary>

```bash
sudo pacman -S git
```

</details>
<details>
<summary>📦 <b>zypper</b> — openSUSE</summary>

```bash
sudo zypper install git
```

</details>
<details>
<summary>🪟 <b>Git for Windows (winget)</b> — Windows</summary>

```bash
winget install --id Git.Git -e --source winget
```

</details>

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install skill-diagnostics@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install skill-diagnostics --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install skill-diagnostics@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install skill-diagnostics@the-claude-factory
```

### 🖥️ Claude app (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Skill Diagnostics** in **Discover** and select **Add**.

## 🚀 Usage

### Audit one skill

```text
/skill-diagnostics:audit ~/.claude/skills/release-notes
```

**Result:** a report in the conversation with the verdict (**pass**, **pass with warnings**, **fail** or **not determinable**), a findings table sorted by severity, the verbatim evidence for each finding and what was not checked. No file is written.

You can also pass a file inside the skill, or several paths at once.

### Audit every skill in a plugin

```text
/skill-diagnostics:audit ./plugins/my-plugin
```

**Result:** one report per skill and, when there are several, a summary table with each skill's verdict and its high, medium and low findings. The plugin folder and its `skills/` folder both work, and so does any folder whose subfolders are skills.

### Check a skill before you install it

```text
/skill-diagnostics:audit https://github.com/owner/repo/tree/main/skills/meeting-notes
```

**Result:** the same audit on a skill you haven't installed yet. Every audit covers Claude Code, the Claude app, claude.ai skill uploads and the Skills API: the report says where the skill comes from, which surfaces it reaches, and what would break if you moved it to another one.

### Run one lens only

```text
/skill-diagnostics:audit ./skills/invoice-note --lens executability
```

**Result:** only the executability lens runs, which halves the work on a large set of skills. Structure checks belong to the conformance lens, so they run only with `--lens conformance` or with both lenses.

### Audit a skill you just wrote

Create or edit a skill as usual, for example with `skill-creator`. When the skill is finished, Claude offers the audit; answer yes and the report follows.

## ⚙️ Configuration

| Option | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `on_skill_write` | string | `suggest` | What happens after a `SKILL.md` is created or changed: `suggest` (Claude offers an audit once the skill is finished), `run` (Claude runs the audit when the skill is finished) or `off`. Set via `/plugin` → **Installed** → **Skill Diagnostics** → **Configure options**, or in `/config` (v2.1.269+). |

In the Claude app the option can't be changed and keeps its default, `suggest`.

## 🔄 Updating

```bash
claude plugin update skill-diagnostics@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `skill-diagnostics@synced`: update and uninstall it in the app (**Customize** → **Plugins**).

If you install it both in the Claude app and in Claude Code, Claude Code loads its own copy and reports the synced one as not loaded, so update the copy you use.

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update Python and git the way you installed them, for example with Homebrew:

```bash
brew upgrade python git
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall skill-diagnostics@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall skill-diagnostics@the-claude-factory --scope project
```

In the Claude app: **Customize** → **Plugins** → **Skill Diagnostics** → its menu → **Remove**.

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The audit never changes your files, so nothing else is left behind.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |
| 🪝 Hooks | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

In a chat conversation, where agents don't run, the skill applies both lenses itself, one after the other. Hooks don't run there either, so ask for the audit yourself after writing a skill.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/skill-diagnostics:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>How is this different from <code>skill-creator</code>?</b></summary>

`skill-creator` helps you write a skill and measure it with test prompts. Skill Diagnostics reads a finished skill and reports, with evidence, what breaks the rules, what a surface rejects and where a model would have to guess. Use both: create with `skill-creator`, then audit.

</details>

<details>
<summary><b>Does it change my skill?</b></summary>

No. The audit only reads files and reports. If you then ask Claude to fix the findings, that is a normal edit you approve as usual.

</details>

<details>
<summary><b>Claude asks for permission during an audit.</b></summary>

The audit pre-approves nothing: your permission settings decide what asks first, so these prompts are expected. The audit never changes your files; it only clones a skill from a URL into a temporary folder it deletes afterwards:

- **Running commands**, such as listing your skill's files or checking your Claude Code version.
- **Reading your skill**, when it lives outside your working directory, for example in `~/.claude/skills/`. Allow it and the audit continues.
- **Reading the plugin's own guides**, which live in Claude Code's plugin folder. Safe to allow.
- **Fetching an official page**, to verify a finding. If you deny it, the finding stays in the report, marked *not verified live*, and the verdict is *provisional*.
- **Cloning a skill with `git`**, when you audit one from a URL, into a temporary folder deleted after the report.

</details>

<details>
<summary><b>The report lists files as "not inspected".</b></summary>

Both auditors read every file of the skill from its first line to its last, scripts and hidden files included, and exclude nothing on their own. A file is listed as not inspected only when it can't be opened as text or an image (a binary), when a folder can't be listed, or when your settings or hooks block it, for example a `Read` deny rule; the audit respects the block and gives the reason.

</details>

<details>
<summary><b>The report warns that my description is too long for the skill listing.</b></summary>

Claude Code cuts each skill's `description` (plus `when_to_use`) in its skill listing at the `skillListingMaxDescChars` setting, 1,536 characters by default. The warning uses that default. If you raised the setting, the warning does not apply to you, but users of a skill you share may still see the cut text, so keep the key use case first.

</details>

<details>
<summary><b>How much does an audit cost?</b></summary>

Each skill is read in full by two agents in parallel, and every finding is then verified against the live documentation, so a large folder of skills uses more of your plan's usage than a single one. Use `--lens` to run one lens, or audit a few skills at a time.

</details>

<details>
<summary><b>What does it fetch from the internet?</b></summary>

It uses the network to verify findings against the official Claude documentation and the Claude Code changelog, and to download a skill you audit from a URL. It fetches pages from `code.claude.com`, `claude.com`, `platform.claude.com`, `support.claude.com` and `agentskills.io`. It only downloads public documentation pages; it never uploads your skill's files to those sites. Without network access the audit still runs; findings that need an official page are marked *not verified live* and the verdict is *provisional*.

</details>

<details>
<summary><b>What happens without Python?</b></summary>

The audit still runs, but the hook can't start: Claude Code shows a hook error after each `SKILL.md` write.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Claude Code skills](https://code.claude.com/docs/en/skills)
- 📖 [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=skill-diagnostics) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=skill-diagnostics) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=skill-diagnostics)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
