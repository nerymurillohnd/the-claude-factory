<div align="center">

# 🧪 Plugin Evals

<p><strong>Makes Claude an expert in Claude Code plugin evals: designs suites that prove what a plugin adds, writes cases, graders and mocks, runs and gates them in CI, and reads the results, always checked against the CLI and docs you have today.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fplugin-evals%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Testing%20%26%20Quality-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.269-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Ask Claude anything about testing your Claude Code plugin with evals, from "write me an eval suite" to "why did my CI eval fail", and get files and commands that work with the Claude Code you have installed today.

## ✨ Why use it

`claude plugin eval` is new and changes with nearly every Claude Code release. Without help, Claude has to look everything up on each question. It hedges on details the docs state plainly, and it misses the rules that decide whether a score means anything.

- **Scores you can trust**: every case is built to prove what your plugin adds over plain Claude. It grades both the result and whether your plugin produced it, and measures triggering as a rate, so a high score is never an accident.
- **Right the first time**: graders, mocks, fixtures and CI commands come out correct, with no `(?i)` that never matches, no "must not fire" check that silently stops counting, and no target swallowed by `--json`.
- **Always current**: before Claude relies on a flag, default or format, it checks your installed `claude` CLI, the live docs and the changelog. It tells you when they disagree with what it knew, and what it couldn't verify.
- **No surprise bills**: Claude tells you how many model runs and judge calls a step needs, pilots cheaply first, and waits for your go-ahead before anything paid runs.
- **Answers from the source**: one skill with focused references that load only when your task needs them, instead of a dozen web lookups per question.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `plugin-evals:plugin-evals` | Designs, writes, runs, debugs and CI-gates `claude plugin eval` suites and reads their results, checked against your installed CLI and the live docs | Automatically whenever your task involves plugin evals, or `/plugin-evals:plugin-evals` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.269 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | To run suites: the `claude` CLI in a terminal; git 2.31 or later if git is installed. Suites that grant Bash need the OS sandbox: `bubblewrap` and `socat` on Linux, WSL2 on Windows |
| **Accounts / API keys** | None for the plugin. Eval runs and judge graders use the credentials your Claude Code already uses, and count against your plan or API bill |
| **Web access** | Optional. With it, Claude checks the live docs and changelog; without it, Claude answers from the plugin's references and says what it could not verify |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install plugin-evals --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install plugin-evals@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install plugin-evals --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install plugin-evals@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Plugin Evals** in **Discover** and select **Add**.

In the desktop app's **Code** tab you can also click **+** → **Plugins** → **Add plugin**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

You don't need a command: describe what you want, and the skill loads when your request is about plugin evals.

### Start an eval suite for your plugin

```text
I want evals for my plugin in ./plugins/changelog-writer. Where do I start?
```

**Result:** Claude checks your Claude Code version, runs `claude plugin eval init` from the plugin root and conducts the interview it prints. It asks what a good and a bad result look like, then proposes cases that prove a difference, including prompts that must not trigger the skill. It writes each case's `prompt.md` and graders with the tools they need, and tells you how many runs the one-run pilot needs before running anything.

### Fix a case that never fails

```text
My "skill must not fire" case still passes when the skill fires. Why?
```

**Result:** Claude explains that in a run compared against no plugin, a `tool_used: Skill` grader is only an indicator and doesn't count, and rewrites it with `min: 0`, `max: 0` and `arm: both`, next to an outcome grader.

### Gate CI on the score

```text
Add a GitHub Actions step that runs my plugin's evals and fails under 0.8.
```

**Result:** a step with a pinned Claude Code install, credentials from your secrets, the target before `--json`, `--trust-plugin`, `--threshold 0.8`, pinned agent and judge models, `--no-publish` and a cost ceiling. If your suite grants Bash, it adds the sandbox packages. Claude explains each exit code your pipeline can see.

### Understand a result

```text
Here's my aggregate-result.json. Why is the delta zero on half the cases?
```

**Result:** a case-by-case reading that separates cases Claude passes without your plugin, a skill that didn't trigger on that wording, graders on the wrong target, and a small judge failing correct answers. Each comes with its fix.

## 🔄 Updating

```bash
claude plugin update plugin-evals@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Plugin Evals** → **Update now**. Then run `/reload-plugins`.

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `plugin-evals@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall plugin-evals@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Plugin Evals** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Plugin Evals** → its menu → **Remove**.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

In the Claude app, Claude designs and reviews suites, writes case files and reads the results you share, in a Cowork session or a chat conversation. Running `claude plugin eval` itself needs Claude Code in a terminal, and Claude tells you so when a step needs it.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/plugin-evals:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Does it replace <code>claude plugin eval init</code>?</b></summary>

No. Claude runs `init` and follows the interview it prints, so the authoring rules always match your Claude Code version. The plugin adds what the interview leaves out: exact formats, fixtures and mocks, CI, cost control and reading the results.

</details>

<details>
<summary><b>What if the docs changed after this plugin was released?</b></summary>

Claude checks your installed CLI with `claude plugin eval --help`, the live docs and the changelog before it relies on anything that changes between releases. When they disagree with what the plugin knew, Claude follows the live source and tells you what changed.

</details>

<details>
<summary><b>Does it run paid evals on its own?</b></summary>

No. Every eval run and every judged grader is a real model call on your account. Claude states how many runs a step needs and waits for your go-ahead.

</details>

<details>
<summary><b>Does it work with skill-creator's <code>evals/evals.json</code>?</b></summary>

The two formats aren't interchangeable. Claude explains when to use each one and converts `evals.json` entries into `claude plugin eval` cases when you ask.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=plugin-evals) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=plugin-evals) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=plugin-evals)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
