<div align="center">

# ✍️ Prompt Writer

<p><strong>Turns a goal, idea or draft into one copy-ready prompt tuned to the target Claude model and effort: it clarifies intent, checks current official facts and recommends the setup to run it with.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fprompt-writer%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Productivity-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.292-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Run `/prompt-writer:prompt-writer`, describe what you want a prompt to achieve, even loosely, and Claude interviews you about the situation, then hands back one complete prompt written for the model you will run it on, plus the model, effort and session setup to use with it.

## ✨ Why use it

Most weak prompts come from a vague goal, not from missing tags or headings. Prompt Writer starts from the outcome you want and works backwards.

- **Say it loosely** — you describe the goal in plain language. Claude decides the structure, length and techniques, and asks you about the situation, the audience and what "good" looks like, never about XML tags or effort levels.
- **Written for the model that will run it** — guidance for Claude Fable 5.1, Fable 5, Opus 5.5, Opus 5 and Sonnet 5.5 is built in, so a prompt for one model does not carry habits that backfire on another.
- **No outdated facts inside your prompt** — when your prompt depends on products, APIs, prices or rules that change, Claude checks them against current official sources before writing.
- **One answer, ready to paste** — you get a single final prompt with a short header for your records, not a menu of variants; you paste the prompt below the header. When the next step depends on a result you have to bring back, you get the first prompt and what to bring back.
- **Setup advice included** — each prompt comes with the recommended model, effort and session mode, plan mode or direct execution in Claude Code, each with a one-line reason, and names the skills that would help.
- **Checked before you get it** — every delivery ends with the checklist Claude verified the prompt against.
- **Works on prompts you already have** — refine a draft, audit and fix an existing prompt or system prompt, or migrate a prompt to another target model.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `prompt-writer:prompt-writer` | Acts as your prompt partner: clarifies the goal, researches what the prompt depends on, and delivers one copy-ready prompt, the text of a system prompt, skill, slash command or agent, or a prompt that has Claude build one, with setup advice. It writes the prompt; you run it in another session | Only when you run `/prompt-writer:prompt-writer`; Claude doesn't start it on its own |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | None |
| **Accounts / API keys** | None. Checking current official documentation needs web access in your session; without it, Claude says which facts it could not verify. |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install prompt-writer --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install prompt-writer@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install prompt-writer --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install prompt-writer@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Prompt Writer** in **Discover** and select **Add**.

In the desktop app's **Code** tab you can also click **+** → **Plugins** → **Add plugin**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

Start every request with `/prompt-writer:prompt-writer`; Claude doesn't start the skill on its own. In the Claude app, type `/` or select **+** to pick it from your plugins' skills.

### Example: a prompt from a loose idea

```text
/prompt-writer:prompt-writer I need a prompt so Claude reviews my weekly sales report and tells me what changed
```

**Result:** Claude restates the goal, asks up to three or four questions about the situation, each with its recommendation (who reads the review, where the report lives, what counts as a useful answer), and then delivers one prompt in a fenced block. Below it you get the recommended model, effort and session mode, short design notes and any assumptions.

### Example: the text of a skill or slash command

```text
/prompt-writer:prompt-writer Write the SKILL.md for a Claude Code skill that takes a GitHub issue number and plans the fix
```

**Result:** you get the complete file in the skill's own format, with its own frontmatter and arguments in Claude Code's syntax. If your request could also mean a prompt that has Claude build the skill, Claude asks which one you want first.

### Example: improve a draft you already have

```text
/prompt-writer:prompt-writer Audit this system prompt and fix it for Sonnet 5.5: <paste your prompt>
```

**Result:** Claude names what the draft does and what it should cause, applies Sonnet 5.5's documented behavior, and returns the corrected prompt with design notes on the key decisions. You can ask in any language.

### Example: move a prompt to another model

```text
/prompt-writer:prompt-writer Migrate this prompt from Opus 5 to Fable 5.1: <paste your prompt>
```

**Result:** Claude adjusts the prompt to the target model's documented differences and explains the key decisions in the design notes, with the recommended model, effort and session setup.

### Example: save the prompt to a file

```text
/prompt-writer:prompt-writer Write a prompt for a weekly changelog summary and save it to prompts/changelog-summary.md
```

**Result:** the file holds a short metadata header (title, objective, prompt type, target model, surface, effort, session mode, Claude Code mode, output language, required capabilities, version) and the clean prompt. Without a location, Claude asks before creating any file.

> [!TIP]
> Your conversation stays in your own language, and prompts are written in English unless you ask otherwise. The language the target model answers in is a separate choice, and Claude asks about it when it matters.

## 🔄 Updating

```bash
claude plugin update prompt-writer@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Prompt Writer** → **Update now**. Then run `/reload-plugins`.

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `prompt-writer@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall prompt-writer@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Prompt Writer** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Prompt Writer** → its menu → **Remove**.

Prompts you saved to files stay where you put them.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

In Claude Code, after each delivery a check compares what the reply claims, such as the pages it cites and the verified checklist items, with what Claude actually did in the session, and sends Claude back to fix any claim without evidence. The check adds a short wait after each reply while the skill is in use. Elsewhere the checklist is Claude's own.

The skill works the same in a Cowork session and in a chat conversation. Saving a prompt to a file needs a session that can reach a folder on your computer; elsewhere Claude gives you the prompt in a code block.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/prompt-writer:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Which models does it write for?</b></summary>

Claude Fable 5.1, Fable 5, Opus 5.5, Opus 5 and Sonnet 5.5. If you name another model, Claude recommends the closest one it covers; if you keep yours, it writes with the general principles only. If you name no model, Claude picks one and tells you why.

</details>

<details>
<summary><b>What if the prompt doesn't get the result I wanted?</b></summary>

Bring the result back to the conversation. Claude checks it against your goal, tells you what worked and what didn't, and revises the prompt or writes the next one.

</details>

<details>
<summary><b>What happens when the official documentation has changed?</b></summary>

The built-in guidance is a snapshot of Anthropic's prompting documentation dated 2026-10-14. Each time, Claude also reads the target model's current page on what changed. If current official documentation contradicts the snapshot on something your prompt depends on, Claude follows the live page and tells you in the design notes what the snapshot says, what the live page says and how it affects your prompt.

</details>

<details>
<summary><b>Why did Claude ask me questions instead of writing the prompt right away?</b></summary>

When the answer would change the objective, the target model, the tools or the output, Claude asks, with a recommendation for each question. When your request is already clear, or you tell it to proceed, it writes the prompt directly.

</details>

<details>
<summary><b>Does it run my prompt or build tests for it?</b></summary>

No. It delivers one prompt and the advice to use it, and it does not build evaluation suites for that prompt. If you also ask it to run the prompt, you still get only the prompt, to run in a new session with the model and effort it recommends. A request written as an order, such as "audit my repo" or "fix this bug", is what the prompt gets done when you run it in another session.

</details>

<details>
<summary><b>What can it write besides a prompt for a task?</b></summary>

It also writes the complete text of something Claude loads, such as a system prompt, a skill, a slash command, an agent or a `CLAUDE.md`, in that file's own format. If it is unclear whether you want the file itself or a prompt so Claude creates it, Claude asks. Placeholders follow what fills them, and the design notes name anything Claude added beyond your request.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🩺 [Skill Diagnostics](../skill-diagnostics#readme) — audit the skills you write
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=prompt-writer) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=prompt-writer) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=prompt-writer)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
