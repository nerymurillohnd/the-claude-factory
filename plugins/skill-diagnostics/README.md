<div align="center">

# 🩺 Skill Diagnostics

<p><strong>Audits Claude skills for best-practice conformance, portability and whether a model can run them without guessing, with file-and-line evidence and one verdict.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fskill-diagnostics%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Cowork-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Testing%20%26%20Quality-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.176-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Type `/skill-diagnostics:audit <skill folder>` and get one report that says whether the skill follows the official rules, works where you plan to use it, and can be run by a model without guessing, with the exact line behind every finding.

## ✨ Why use it

A skill can look finished to the person who wrote it and still fail the model that runs it: a placeholder nothing defines, a reference that contradicts `SKILL.md`, a description that never triggers, a field that breaks the upload to claude.ai.

- **Two audits in one pass** — conformance (official rules, recommendations, portability) and executability (could a model follow it without guessing) run in parallel and come back as one report with one verdict.
- **Reads every line** — both auditors read every file of the skill from start to end, scripts and hidden files included; nothing is sampled or skimmed. If a file can't be listed or read, the report names it, and a gap that matters gives *not determinable* instead of a pass.
- **Evidence, not opinions** — every finding quotes the exact text with its file and line, and says how to fix it.
- **Checks what validation skips** — `claude plugin validate` confirms the structure; Skill Diagnostics also checks name and description limits, quoting that breaks strict YAML, argument placeholders, broken links and script setup.
- **Ready for every surface** — tell it where the skill must work (Claude Code, Cowork, a claude.ai upload, the Skills API) and it flags what that surface rejects or skips.
- **Catches new skills as you write them** — after a `SKILL.md` is created or changed, for example with Anthropic's `skill-creator`, Claude offers an audit before you move on.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `skill-diagnostics:audit` | Runs the structure checker, launches both lenses in parallel, merges the results and gives the verdict | `/skill-diagnostics:audit <path>`, or ask Claude to audit, review or check a skill |
| 🤖 Agent | `skill-diagnostics:conformance-auditor` | Checks one skill against the documented rules, recommendations and target surfaces | Launched by the skill, one per skill |
| 🤖 Agent | `skill-diagnostics:executability-auditor` | Traces every workflow of one skill as the model that must run it | Launched by the skill, one per skill |
| 🪝 Hook | `PostToolUse` | After a `SKILL.md` is written or edited, asks Claude to offer an audit once the skill is finished (or to run it, if you [configure](#️-configuration) that) | Automatically, once per skill per session |

Skill Diagnostics only audits. To create a skill, use Anthropic's `skill-creator`, then audit the result.

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.176 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | Python 3.9 or later on `PATH` as `python3`, for the structure checker and the hook. On Windows, Git for Windows, so scripts run by their path. Without Python the audit still runs without the checker, but the hook can't start and Claude Code shows a hook error after each `SKILL.md` write |
| **Network** | Optional. To confirm a rule that may have changed, the audit can fetch the official Claude documentation page that owns it. Claude Code asks before each fetch, and nothing from your skill is sent |
| **Accounts / API keys** | None |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install skill-diagnostics --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install skill-diagnostics@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install skill-diagnostics --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install skill-diagnostics@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude desktop app &amp; Cowork</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Skill Diagnostics** and click **Install**.

In the desktop app's **Code** tab you can also click **+** → **Plugins** → **Add plugin**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step. Installed both in the Claude app and from the terminal, Claude Code uses the terminal copy and skips the synced one, so update the copy you use.

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

**Result:** one report per skill, then a summary table with each skill's verdict and its high, medium and low findings. The plugin folder and its `skills/` folder both work, and so does any folder whose subfolders are skills.

### Check a skill before uploading it to claude.ai

```text
/skill-diagnostics:audit ./skills/meeting-notes --target upload
```

**Result:** the same audit, judged by upload rules: only the six fields claude.ai accepts, a description of at most 1,024 characters, no load-time commands, scripts called through their interpreter. Use `--target cowork` or `--target api` for those surfaces, and repeat the option for several (`--target code --target upload`).

Without `--target`, the audit picks the surfaces from where the skill lives: Claude Code for your personal and project skills, Claude Code and Cowork for skills inside a plugin. The report says which surfaces it assumed.

### Run one lens only

```text
/skill-diagnostics:audit ./skills/invoice-note --lens executability
```

**Result:** only the executability lens runs, which halves the work on a large set of skills. The structure checker belongs to the conformance lens, so it runs only with `--lens conformance` or with both lenses.

### Audit a skill you just wrote

Create or edit a skill as usual, for example with `skill-creator`. When the skill is finished, Claude offers the audit; answer yes and the report follows.

## ⚙️ Configuration

| Option | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `on_skill_write` | string | `suggest` | What happens after a `SKILL.md` is created or changed: `suggest` (Claude offers an audit once the skill is finished), `run` (Claude runs the audit when the skill is finished) or `off`. Set via `/plugin` → **Installed** → **Skill Diagnostics** → **Configure options**, or in `/config` (v2.1.269+). |

In Cowork the option can't be changed and keeps its default, `suggest`.

## 🔄 Updating

```bash
claude plugin update skill-diagnostics@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Skill Diagnostics** → **Update now**. Then run `/reload-plugins`.

Installed from the Claude app or Cowork? In Claude Code it appears as `skill-diagnostics@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only disable it.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall skill-diagnostics@the-claude-factory
```

Installed with `--scope project`? Add `--scope project` here too.

In a session: `/plugin` → **Installed** → **Skill Diagnostics** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Skill Diagnostics** → **Uninstall**.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🤝 Cowork

| Component | Claude Code | Cowork | Claude chat |
| :-- | :--: | :--: | :--: |
| 🎯 Skills | ✅ | ✅ | ✅ |
| 🤖 Agents | ✅ | ✅ | ➖ |
| 🪝 Hooks | ✅ | ✅ | ➖ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there</sub>

Where agents are not available, the skill applies both lenses itself, one after the other. Where the hook does not run, ask for the audit yourself.

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

These prompts are expected, and the audit only reads:

- **Reading your skill**, when it lives outside your working directory, for example in `~/.claude/skills/`. Allow it and the audit continues.
- **Reading the plugin's own guides**, which live in Claude Code's plugin folder. Safe to allow.
- **Fetching an official documentation page**, to confirm a rule against the live docs. If you deny it, the finding stays in the report, marked *not verified live*.

</details>

<details>
<summary><b>The report lists files as "not inspected".</b></summary>

Both auditors read every file of the skill from its first line to its last, scripts and hidden files included, and exclude nothing on their own. A file is listed as not inspected only when it can't be opened as text or an image (a binary), or when your settings or hooks block it, for example a `Read` deny rule; the audit respects the block and gives the reason.

</details>

<details>
<summary><b>The report says "checker not run".</b></summary>

The structure checker needs Python 3.9 or later as `python3` on your `PATH` (on Windows, with Git for Windows). The rest of the audit still ran; install Python and run the audit again to add the checker's findings. Without Python the file inventory comes from the session's own listing tool, which can stop at 100 files; the report says which tool listed the files. Without Python, Claude Code also shows a hook error after each `SKILL.md` write; installing Python removes it.

</details>

<details>
<summary><b>The report warns that my description is too long for the skill listing.</b></summary>

Claude Code cuts each skill's `description` (plus `when_to_use`) in its skill listing at the `skillListingMaxDescChars` setting, 1,536 characters by default. The warning uses that default. If you raised the setting, the warning does not apply to you, but users of a skill you share may still see the cut text, so keep the key use case first.

</details>

<details>
<summary><b>How much does an audit cost?</b></summary>

Each skill is read in full by two agents in parallel, so a large folder of skills uses more of your plan's usage than a single one. Use `--lens` to run one lens, or audit a few skills at a time.

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
