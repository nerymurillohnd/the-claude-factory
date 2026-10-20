<div align="center">

# 🧾 Project Maintainer

<p><strong>Records a project's important decisions as architecture decision records and tracks the technical debt it cannot fix yet in a ledger, so the next person knows why the project is the way it is.</strong></p>

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
> **TL;DR** — Make a decision, or find a problem you cannot fix yet, and Claude writes it down in your repository as a dated record: an ADR for the decision, a debt entry for the problem. A debt entry moves to resolved only when the fix is proven.

## ✨ Why use it

Months later, nobody remembers why the project uses one database over another, or that the export job still breaks on large files. The answer lives in a chat that is gone.

- **Remember why, not only what** — each decision keeps its context, the options you rejected and the consequences you accepted, in one file per decision.
- **Debt that waits does not disappear** — each entry holds its evidence, owner, next action and the condition that lets you close it, so a problem you chose to postpone stays visible.
- **Facts apart from guesses** — confirmed facts and inferences have separate fields, and planned evidence is marked pending until it is observed.
- **Closed means proven** — an item moves to resolved only after a check shows the fix works and a second check shows the original failure no longer happens.
- **History stays true** — an accepted record is never rewritten. A new decision supersedes the old one and both point at each other.
- **Only what matters** — renames, typos and small refactors are not recorded, and a problem that can be fixed now is fixed instead of logged.
- **Plain Markdown in your repository** — no service, no account and no setup. Existing records stay where you keep them.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `project-maintainer:write-records` | Writes decisions as ADRs from a template and keeps a pending and a resolved debt ledger. It searches for an existing record first, asks only for facts it is missing, and tells you in one line what it saved and where | Automatically when a decision is made or a problem is postponed, or with `/project-maintainer:write-records` |

The ADR template follows [MADR 4.0](https://adr.github.io/madr/) and adds a scope, a risks table and a confirmation table.

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | None to install. Claude Code searches and numbers records with `ls`, `grep` and `mkdir`, which macOS and Linux include; on Windows, use Git for Windows |
| **Network** | None. The plugin reads and writes files in your project only |
| **Accounts / API keys** | None |

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
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

### Record a decision

```text
We decided to keep sessions in Postgres instead of Redis. Record it.
```

**Result:** Claude searches your existing records, asks only for what it is missing (for example, why Redis was rejected), and saves `docs/decisions/ADR_2026-03-14_keep-sessions-in-postgres.md` with the context, the options, the outcome and its consequences. It then tells you the file name in one line. The record is `accepted` when you made the decision in the conversation and `proposed` when it is still open.

### Record several decisions at once

**Result:** Claude asks you once how to register them, with a recommendation: one ADR per decision (the default, because each can be superseded alone), one ADR for the whole package, or one ADR per theme such as process, architecture or security.

### Log a problem you cannot fix yet

```text
The nightly export fails on files over 2 GB. We cannot fix it until the vendor ships the new API. Log it as debt.
```

**Result:** Claude searches both ledgers for the same problem, then adds `DEBT-001` to `docs/technical-debt/pending-debt.md`, creating the ledger the first time. The entry separates confirmed facts from inferences and records the impact, why it is not fixed now, the next action and the event that lets you close it.

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

### Bring in records you already keep

The first time Claude is about to create a records folder, it looks through your project for documents that already track the same thing: an `ADR` or `decisions` folder, a `DECISIONS.md`, a `TECH_DEBT.md`, a known-issues or pending list, or any path your `CLAUDE.md` or `AGENTS.md` names.

**Result:** Claude shows you what it found, one line per document, and asks whether to consolidate and migrate it. If you agree, each decision becomes an ADR and each postponed problem becomes a debt item, using the original wording and writing "not recorded in the source" where the original says nothing. Task lists that can be done now stay where they are. Afterwards Claude asks, for each original, whether to replace it with a one-line pointer, delete it or keep it, and it changes nothing until you answer. This way each fact lives in one place.

### Where records are saved

| What | Where |
| :-- | :-- |
| Decisions | `docs/decisions/ADR_<YYYY-MM-DD>_<slug>.md`, one file per decision |
| Pending debt | `docs/technical-debt/pending-debt.md` |
| Resolved debt | `docs/technical-debt/resolved-debt.md` |

If your project already keeps ADRs in another folder, such as `docs/adr/`, or names a location in its `CLAUDE.md` or `AGENTS.md`, Claude uses that instead and never moves existing records. It also names a new ADR with the pattern of the ADRs already in the folder, such as `0008-use-postgres.md`, and uses the name above only in a folder without ADRs.

The first time Claude is about to create the records folders in a git repository, it asks you once whether git should **track** them (recommended, so your team shares them) or **ignore** them (they stay on your machine). If you choose to ignore them, it adds the two folders to the `.gitignore` at the root of your checkout and never asks again. It does not ask when a records folder already exists, and in a non-interactive run such as `claude -p` it tracks the records and says so.

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

Your records stay in your project's folders; they are ordinary Markdown files.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads everywhere; saves records only where it can reach your project folder |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

Records live in your project folder, so the plugin needs a session that works in one: Claude Code, or a Cowork session on your computer. In a chat conversation there is no project folder, so Claude can draft a record there but cannot save it.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/project-maintainer:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Does Claude record things without asking me?</b></summary>

Yes, that is the purpose of the plugin. When it sees an important decision or a problem you are postponing, it writes the record and tells you in one line which file it saved. It asks only for facts it is missing, plus the one question about git described under [Where records are saved](#where-records-are-saved). It never commits or pushes a record, so delete the file if you did not want it. To record on demand only, tell Claude to wait for your request.

</details>

<details>
<summary><b>Will it touch the decision or debt files I already have?</b></summary>

Not without your OK. Claude lists them, asks whether to migrate, and asks again, for each original, before it replaces, deletes or keeps it. In a non-interactive run such as `claude -p` it migrates nothing and only names what it found.

</details>

<details>
<summary><b>Does the plugin change my <code>.gitignore</code>?</b></summary>

Only if you answer that you want the records kept local, and then it adds exactly two lines: the decisions folder and the debt folder. Otherwise it never touches the file. To change your mind later, edit `.gitignore` yourself. Claude does not ask again because the folders already exist.

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

Not yet. Claude writes every record from the plugin's templates. If your project already has ADRs, Claude saves new ones in the same folder.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🔁 [Session Handoff](../session-handoff#readme) — carry the open work of a session to the next one; records keep the lasting decisions
- 📖 [MADR, the decision record format](https://adr.github.io/madr/)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=project-maintainer) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=project-maintainer) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=project-maintainer)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
