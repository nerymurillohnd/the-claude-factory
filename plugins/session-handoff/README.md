<div align="center">

# 🔁 Session Handoff

<p><strong>Carries a project's working state from one session to the next: write a handoff when you stop, and the next session reads it, does what you ask and ends its reply with what is still open.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fsession-handoff%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
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
> **TL;DR** — Type `/session-handoff:write-handoff` before you stop, and your next session in that project does what you ask with the whole story behind it, then lists what is still open.

## ✨ Why use it

A new session starts with an empty conversation. What you decided yesterday, the fix that is half done and the item you promised to come back to live only in a transcript you will not reread.

- **Start where you stopped** — the next session reads the newest handoff in full, works with its decisions, corrections and learnings as background, and ends its reply with what is still open.
- **Nothing gets lost between sessions** — every open item of the previous handoff is carried forward or closed with its evidence, so a pending task cannot quietly disappear.
- **Facts, not memory** — each handoff is built from the repository itself: branch, uncommitted work, stashes, unpushed commits, the commits since the last handoff and the open pull requests. What could not be checked is marked as such.
- **One project at a time** — a handoff belongs to the project you are working in and holds only that project's work.
- **You stay in charge** — the handoff is drafted with you and saved only after you approve it, and the next session does what you ask, never the pending work on its own, and ends its reply with the open items so you decide.
- **Quiet everywhere else** — in projects without handoffs, the plugin adds nothing to the conversation.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `session-handoff:write-handoff` | Reads the project's state, summarizes the session, compares it with the previous handoff, drafts the new one with you, saves it in `.claude/session-handoff/` and offers to commit and push it | `/session-handoff:write-handoff`, or ask Claude to write a handoff when you wrap up |
| 🪝 Hook | `SessionStart` | When a session starts or is cleared in a project with handoffs, shows you a one-line notice naming the newest one and has Claude read it in full, do what you ask and end its reply with the open items | Automatically, at the start of a session and after `/clear` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | `bash` on `PATH`, for the hook and the skill's commands; on Windows, Git for Windows. `git`, so the handoff can record the repository's state; outside a git repository the handoff says so and skips it. `gh` signed in, optional, to list the repository's open pull requests |
| **Network** | When the repository has a remote, the skill runs `git fetch` to compare your branch with it, and `gh pr list` to list pull requests. A commit or push of the handoff happens only if you accept the skill's offer. Without network access the handoff marks those lines as not verified |
| **Accounts / API keys** | None. `git` and `gh` use the credentials you already have |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install session-handoff --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install session-handoff@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install session-handoff --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install session-handoff@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Session Handoff** in **Discover** and select **Add**.

In the desktop app's **Code** tab you can also click **+** → **Plugins** → **Add plugin**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step. If you install it both in the Claude app and in Claude Code, Claude Code loads its own copy and reports the synced one as not loaded, so update the copy you use.

## 🚀 Usage

### Write a handoff before you stop

```text
/session-handoff:write-handoff
```

**Result:** Claude checks the project's state (branch, uncommitted work, stashes, unpushed commits, open pull requests), summarizes the session from its start and compares it with the previous handoff. It then shows you the complete proposal, in six sections: where the project stands, the open items in priority order with the first action of each, the context the next session needs (learnings, corrections and recommendations), the decisions with their reasons, what was done with its evidence, and what could not be verified. Once you approve it, the handoff is saved as `.claude/session-handoff/2026-03-14-1730.md` (the date and time in UTC), creating the folders the first time. In a git repository, Claude asks whether to commit and push it. The handoff marks the end of the session.

### Pick up in the next session

Start Claude Code in the same project, at its root or in any subfolder of the repository, and type your first request as usual.

**Result:** Claude reads the newest handoff in full and does what you asked. If your request differs from the pending work, it does your request anyway. It works with the handoff's decisions, corrections and learnings as background, so past mistakes are not repeated. At the end of its reply it lists the open items, one short line each, so you can decide what to do next.

### Start fresh in the same session

```text
/clear
```

**Result:** the conversation is emptied and the newest handoff is read again, as at the start of a session. After `/resume` the handoff is still in the conversation. After a compaction only a summary of it remains: ask Claude to reread the newest handoff if you need the details.

### Carry open items forward

Run `/session-handoff:write-handoff` again at the end of the next session.

**Result:** every open item of the previous handoff gets a verdict (done with its evidence, partial, still open, or dropped by you), and the open ones are carried into the new handoff with their original date. Only items that are still pending, in part or in full, are carried. Claude asks you about the ones that look obsolete or outside the project, and only you can drop an item. A result you report from outside the session, such as a test you ran in another app, closes an item as done, noted as reported by you. Items open for more than 30 days are marked for you to confirm or drop.

## 🔄 Updating

```bash
claude plugin update session-handoff@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Session Handoff** → **Update now**. Then run `/reload-plugins`.

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `session-handoff@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall session-handoff@the-claude-factory
```

Installed with `--scope project`? Add `--scope project` here too.

In a session: `/plugin` → **Installed** → **Session Handoff** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Session Handoff** → its menu → **Remove**.

Your handoffs stay in each project's `.claude/session-handoff/` folder; delete that folder if you no longer want them.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads everywhere; saves handoffs only where it can reach your project folder |
| 🪝 Hooks | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

Handoffs live in your project folder, so the plugin needs a session that works in one: Claude Code, or a Cowork session on your computer. In a chat conversation there is no project folder, so the skill cannot save a handoff there. If the start-of-session reminder does not appear in a Cowork session, ask Claude to read the newest handoff in `.claude/session-handoff/`.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/session-handoff:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Claude asks for permission to save the handoff.</b></summary>

That is expected. Claude Code protects your project's `.claude/` folder, so every new handoff is shown to you and saved only when you approve it. In auto mode the save is checked like any other protected write, and in bypass-permissions mode, or after you allow edits to `.claude` for the session, it saves without asking; you still approve the draft first. Running `git`, `gh` and `date` may also ask first, depending on your permission settings.

</details>

<details>
<summary><b>The first reply of a new session didn't mention my handoff.</b></summary>

The plugin tells Claude to read the newest handoff, but nothing forces the reply to follow it. Ask Claude to read the newest handoff in `.claude/session-handoff/`. Also check that the handoff is in the folder of the project you opened: each project keeps its own.

</details>

<details>
<summary><b>Should I commit my handoffs to git?</b></summary>

That's your choice. The plugin creates `.claude/session-handoff/` and never edits your `.gitignore`. Commit the folder to share handoffs with your team or keep them across machines; ignore it to keep them local.

Each handoff names the project's folder on your computer, its branches and pull requests, and whatever the session decided and learned. The skill is told never to write a secret or a git remote URL, but read a handoff before you push it to a public repository. Claude treats a handoff as a record and works from it as background, so load handoffs only from sources you trust.

</details>

<details>
<summary><b>Can I write a handoff from <code>claude -p</code>?</b></summary>

Not in the default permission mode: nobody is there to approve saving the file. Write the handoff in an interactive session.

</details>

<details>
<summary><b>Does the start-of-session reminder get in the way of <code>claude -p</code> or CI runs?</b></summary>

No. The hook does nothing in `claude -p` runs, the Agent SDK or the Claude Code GitHub Action, so they behave as if the plugin were not installed.

</details>

<details>
<summary><b>Does it change my code or repository?</b></summary>

No. Writing a handoff reads the repository and saves one new file in `.claude/session-handoff/`. It commits and pushes the handoff file only when you accept its offer, and `git fetch` only updates your remote-tracking branches.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Claude Code hooks](https://code.claude.com/docs/en/hooks)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=session-handoff) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=session-handoff) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=session-handoff)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
