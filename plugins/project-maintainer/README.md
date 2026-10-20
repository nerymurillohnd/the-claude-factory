<div align="center">

# 🧾 Project Maintainer

<p><strong>Keeps a project's memory in its .claude folder: decisions recorded as ADRs, technical debt tracked in a ledger, and a handoff that carries each session's state to the next one.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fproject-maintainer%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Documentation%20%26%20Writing-6B7280)](../../README.md#-catalog)
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
> **TL;DR** — Make a decision, or find a problem you cannot fix yet, and Claude writes it down in your project's `.claude` folder: an ADR for the decision, a debt entry for the problem. Type `/project-maintainer:write-handoff` before you stop, and your next session starts with the whole story, including every debt item still open.

## ✨ Why use it

Months later, nobody remembers why the project uses one database over another, or that the export job still breaks on large files. A new session starts with an empty conversation. The answers live in chats that are gone.

- **Remember why, not only what** — each decision keeps its context, the options you rejected and the consequences you accepted, in one file per decision.
- **Debt that waits does not disappear** — each entry holds its evidence, owner, next action and the condition that lets you close it, so a problem you chose to postpone stays visible.
- **Closed means proven** — an item moves to resolved only after a check shows the fix works and a second check shows the original failure no longer happens.
- **History stays true** — an accepted record is never rewritten. A new decision supersedes the old one and both point at each other.
- **Start where you stopped** — the handoff carries what was done, decided, corrected, learned and left open, and the next session reads it before it does what you ask.
- **One story, not two** — each handoff is checked against the records. Every pending debt item is in it, resolved items are closed with their evidence, and decisions you recorded since the last handoff are added. The next session reads the handoff and already knows what is open.
- **Facts, not memory** — records and handoffs mark what could not be verified, and the handoff is built from the repository itself: branch, uncommitted work, stashes, unpushed commits and open pull requests.
- **Only what matters** — renames, typos and small refactors are not recorded, and a problem that can be fixed now is fixed instead of logged.
- **Plain Markdown in your project** — no service and no account. Everything lives in your project's `.claude` folder.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `project-maintainer:write-records` | Writes decisions as ADRs from a template and keeps a pending and a resolved debt ledger. It searches for an existing record first, asks only for facts it is missing, and tells you in one line what it saved and where | Automatically when a decision is made or a problem is postponed, or with `/project-maintainer:write-records` |
| 🎯 Skill | `project-maintainer:write-handoff` | Reads the project's state, summarizes the session, compares it with the previous handoff and with your records, drafts the new handoff with you, saves it in `.claude/session-handoff/` and offers to commit and push it | `/project-maintainer:write-handoff`, or ask Claude to write a handoff when you wrap up |
| 🪝 Hook | `SessionStart` | When a session starts or is cleared in a project with handoffs, shows you a one-line notice naming the newest one and has Claude read it in full, do what you ask and end its reply with the open items | Automatically, at the start of a session and after `/clear` |

The ADR template follows [MADR 4.0](https://adr.github.io/madr/) and adds a scope, a risks table and a confirmation table.

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | `bash` on `PATH`, for the hook and the skills' commands; on Windows, Git for Windows. `ls`, `grep` and `date`, which macOS and Linux include, to search and number records. `git`, so the handoff can record the repository's state; outside a git repository the handoff says so and skips it. `gh` signed in, optional, to list the repository's open pull requests |
| **Network** | Records: none. The handoff runs `git fetch` to compare your branch with its remote, and `gh pr list` to list pull requests, when the repository has a remote. Without network access it marks those lines as not verified |
| **Accounts / API keys** | None. `git` and `gh` use the credentials you already have |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install project-maintainer --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install project-maintainer@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install project-maintainer --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install project-maintainer@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Project Maintainer** in **Discover** and select **Add**.

In the desktop app's **Code** tab you can also click **+** → **Plugins** → **Add plugin**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step. Already use the separate Session Handoff plugin? This plugin includes it. Turn the separate one off, or you get the start-of-session reminder twice.

## 🚀 Usage

### Record a decision

```text
We decided to keep sessions in Postgres instead of Redis. Record it.
```

**Result:** Claude searches your existing records, asks only for what it is missing (for example, why Redis was rejected), and saves `.claude/maintainer/decisions/ADR_2026-03-14_keep-sessions-in-postgres.md` with the context, the options, the outcome and its consequences. It then tells you the file name in one line. The record is `accepted` when you made the decision in the conversation and `proposed` when it is still open.

### Record several decisions at once

**Result:** Claude asks you once how to register them, with a recommendation: one ADR per decision (the default, because each can be superseded alone), one ADR for the whole package, or one ADR per theme such as process, architecture or security.

### Log a problem you cannot fix yet

```text
The nightly export fails on files over 2 GB. We cannot fix it until the vendor ships the new API. Log it as debt.
```

**Result:** Claude searches both ledgers for the same problem, then adds `DEBT-001` to `.claude/maintainer/technical-debt/pending-debt.md`, creating the ledger the first time. The entry separates confirmed facts from inferences and records the impact, why it is not fixed now, the next action and the event that lets you close it.

### Resolve a debt item

```text
DEBT-001 is fixed.
```

**Result:** Claude runs two checks itself: that the fix works and that the original failure no longer reproduces. With both passing, it moves the entry to `resolved-debt.md` under the same ID, with the evidence. If either check fails, the item stays open and its entry is updated.

### Change a decision

```text
We are moving sessions back to Redis. Update the record.
```

**Result:** Claude writes a new ADR that supersedes the old one, then marks the old one `superseded` and links the two. The reasoning of the earlier record is not touched.

### Write a handoff before you stop

```text
/project-maintainer:write-handoff
```

**Result:** Claude checks the project's state (branch, uncommitted work, stashes, unpushed commits, open pull requests), summarizes the session from its start and compares it with the previous handoff. Then it reconciles the handoff with your records: every pending debt item is listed in the open items with its first action, debt resolved since the last handoff is closed with its evidence, and the decisions you recorded since then are added. It shows you the complete proposal in six sections: where the project stands, the open items in priority order, the context the next session needs, the decisions, what was done and what could not be verified. Once you approve it, the handoff is saved as `.claude/session-handoff/2026-03-14-1730.md` (the date and time in UTC). In a git repository, Claude asks whether to commit and push it. The handoff marks the end of the session.

### Pick up in the next session

Start Claude Code in the same project, at its root or in any subfolder of the repository, and type your first request as usual.

**Result:** Claude reads the newest handoff in full and does what you asked. If your request differs from the pending work, it does your request anyway. It works with the handoff's decisions, corrections and learnings as background, so past mistakes are not repeated. At the end of its reply it lists the open items, debt included, one short line each, so you can decide what to do next. It opens a debt entry only when it needs the detail.

### Start fresh in the same session

```text
/clear
```

**Result:** the conversation is emptied and the newest handoff is read again, as at the start of a session. After `/resume` the handoff is still in the conversation. After a compaction only a summary of it remains: ask Claude to reread the newest handoff if you need the details.

### Carry open items forward

Run `/project-maintainer:write-handoff` again at the end of the next session.

**Result:** every open item of the previous handoff gets a verdict (done with its evidence, partial, still open, or dropped by you), and the open ones are carried into the new handoff with their original date. Only items that are still pending, in part or in full, are carried. Claude asks you about the ones that look obsolete or outside the project, and only you can drop an item. A result you report from outside the session, such as a test you ran in another app, closes an item as done, noted as reported by you. Items open for more than 30 days are marked for you to confirm or drop. If a record contradicts the previous handoff, the record wins and the handoff lists the conflict.

### Bring in records you already keep

The first time Claude is about to create a records folder, it looks through your project for documents that already track the same thing: an `ADR` or `decisions` folder, a `DECISIONS.md`, a `TECH_DEBT.md`, a known-issues or pending list, or any path your `CLAUDE.md` or `AGENTS.md` names.

**Result:** Claude shows you what it found, one line per document, and asks whether to consolidate and migrate it. If you agree, each decision becomes an ADR and each postponed problem becomes a debt item, using the original wording and writing "not recorded in the source" where the original says nothing. Task lists that can be done now stay where they are. Afterwards Claude asks, for each original, whether to replace it with a one-line pointer, delete it or keep it, and it changes nothing until you answer. This way each fact lives in one place.

### Where everything is saved

| What | Where |
| :-- | :-- |
| Decisions | `.claude/maintainer/decisions/ADR_<YYYY-MM-DD>_<slug>.md`, one file per decision |
| Pending debt | `.claude/maintainer/technical-debt/pending-debt.md` |
| Resolved debt | `.claude/maintainer/technical-debt/resolved-debt.md` |
| Handoffs | `.claude/session-handoff/<YYYY-MM-DD-HHMM>.md`, one file per handoff, never overwritten |

The files live in the `.claude/` folder of your project because they are Claude's working documentation about it. The locations are fixed, so every session finds them in the same place.

The first time Claude is about to create `.claude/maintainer/` in a git repository, it asks you once whether git should **track** it (recommended, so your team shares it) or **ignore** it (it stays on your machine). If you choose to ignore it, Claude adds `.claude/maintainer/` to the `.gitignore` at the root of your checkout and never asks again. It does not ask when the folder already exists, and in a non-interactive run such as `claude -p` it tracks the records and says so. Handoffs follow your own git settings: the plugin never edits your `.gitignore` for them.

### Permissions

Claude Code protects the `.claude/` folder, so the first record or handoff you save in a session can open a permission prompt. Reading them never asks.

| Your permission mode | What happens when Claude saves a record or a handoff |
| :-- | :-- |
| Default or accept edits | Claude Code asks. Choose **Yes, and allow Claude to edit files in this project's .claude folder for this session** and it stops asking until the session ends. |
| Auto | A classifier decides instead of you. |
| Bypass permissions | No prompt. |
| Non-interactive (`claude -p`, don't ask) | Nobody can answer the prompt, so Claude shows you the record as a draft. |

> [!NOTE]
> A rule in your `settings.json`, such as `Edit(.claude/**)`, does not remove this prompt: Claude Code checks protected folders before it reads allow rules. See [Protected paths](https://code.claude.com/docs/en/permission-modes#protected-paths) in the Claude Code docs.

## 🔄 Updating

```bash
claude plugin update project-maintainer@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Project Maintainer** → **Update now**. Then run `/reload-plugins`.

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `project-maintainer@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall project-maintainer@the-claude-factory
```

Installed with `--scope project`? Add `--scope project` here too.

In a session: `/plugin` → **Installed** → **Project Maintainer** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Project Maintainer** → its menu → **Remove**.

Your records and handoffs stay in your project's `.claude/` folder; they are ordinary Markdown files. Delete `.claude/maintainer/` and `.claude/session-handoff/` if you no longer want them.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads everywhere; saves records and handoffs only where it can reach your project folder |
| 🪝 Hooks | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

Records and handoffs live in your project folder, so the plugin needs a session that works in one: Claude Code, or a Cowork session on your computer. In a chat conversation there is no project folder, so Claude can draft a record or a handoff there but cannot save it. If the start-of-session reminder does not appear in a Cowork session, ask Claude to read the newest handoff in `.claude/session-handoff/`.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/project-maintainer:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Does Claude record things without asking me?</b></summary>

Yes, that is the purpose of the plugin. When it sees an important decision or a problem you are postponing, it writes the record and tells you in one line which file it saved. It asks only for facts it is missing, plus the one question about git described under [Where everything is saved](#where-everything-is-saved). It never commits or pushes a record, so delete the file if you did not want it. To record on demand only, tell Claude to wait for your request.

</details>

<details>
<summary><b>Will it touch the decision or debt files I already have?</b></summary>

Not without your OK. Claude lists them, asks whether to migrate, and asks again, for each original, before it replaces, deletes or keeps it. In a non-interactive run such as `claude -p` it migrates nothing and only names what it found.

</details>

<details>
<summary><b>Does the plugin change my <code>.gitignore</code>?</b></summary>

Only if you answer that you want the records kept local, and then it adds exactly one line: `.claude/maintainer/`. Otherwise it never touches the file. To change your mind later, edit `.gitignore` yourself. Claude does not ask again because the folder already exists.

</details>

<details>
<summary><b>What counts as an important decision?</b></summary>

A choice between approaches with lasting consequences, a change to the architecture, a process, a dependency, security, or how the project is built, released or distributed, a choice that would be hard to undo, or one someone may later question. Renames, typos, formatting, comments and small refactors that keep behavior are not recorded.

</details>

<details>
<summary><b>Why did Claude fix a problem instead of logging it?</b></summary>

The ledger holds only what cannot be fixed now: it waits on a decision, access, spend or an outside party, or you accepted the risk on purpose. A problem that can be fixed now is fixed. Improvement ideas and backlog tasks do not belong in it.

</details>

<details>
<summary><b>Can I edit a record by hand?</b></summary>

Yes, they are plain Markdown. Claude does not rewrite an accepted ADR or a resolved entry; it supersedes them so the history stays true. Pending debt entries are revised in place as the evidence changes, and the index row is kept equal to its entry.

</details>

<details>
<summary><b>Can I use my own ADR template?</b></summary>

Not yet. Claude writes every record from the plugin's templates.

</details>

<details>
<summary><b>The handoff lists debt. Is it a second copy of my ledger?</b></summary>

It is a snapshot, refreshed every time you write a handoff, and the ledger stays the source of truth. Each debt line names its `DEBT-NNN` ID, so Claude opens the full entry only when it needs the detail. If you edit the ledger between handoffs, the next handoff picks the change up and, where it contradicts the previous one, lists it under Conflicts.

</details>

<details>
<summary><b>The first reply of a new session didn't mention my handoff.</b></summary>

The plugin tells Claude to read the newest handoff, but nothing forces the reply to follow it. Ask Claude to read the newest handoff in `.claude/session-handoff/`. Also check that the handoff is in the folder of the project you opened: each project keeps its own.

</details>

<details>
<summary><b>Should I commit my handoffs to git?</b></summary>

That's your choice. The plugin creates `.claude/session-handoff/` and never edits your `.gitignore` for it. Commit the folder to share handoffs with your team or keep them across machines; ignore it to keep them local.

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
<summary><b>Does writing a handoff change my code or repository?</b></summary>

No. It reads the repository and saves one new file in `.claude/session-handoff/`. It commits and pushes that file only when you accept its offer, and `git fetch` only updates your remote-tracking branches.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [MADR, the decision record format](https://adr.github.io/madr/)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Claude Code hooks](https://code.claude.com/docs/en/hooks)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=project-maintainer) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=project-maintainer) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=project-maintainer)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
