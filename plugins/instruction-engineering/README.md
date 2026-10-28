<div align="center">

# 📐 Instruction Engineering

<p><strong>Writes, edits, reviews, audits, debugs and refactors Claude Code instruction files (CLAUDE.md, CLAUDE.local.md and .claude/rules at user and project scope) against the current loading rules, with a read-only checker and an independent reviewer agent.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Finstruction-engineering%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Documentation%20%26%20Writing-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.271-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Ask Claude to write, fix or audit your `CLAUDE.md` and `.claude/rules`, and get instructions that load when they should, say each thing once, and hold only what changes Claude's behavior.

## ✨ Why use it

- **Instructions that actually load** — Claude checks every rule against the current loader: only `paths` is read in rule frontmatter, an unquoted glob makes a scoped rule load everywhere, and `globs:` or `alwaysApply:` are silently ignored.
- **One instruction set, not a pile of files** — before any change, even a one-line addition, Claude reads everything that loads alongside it and tells you about contradictions, duplicates, ambiguous lines and lines that change nothing.
- **Each thing in the right place** — Claude decides between `CLAUDE.md`, an always-on rule, a path-scoped rule, a skill for procedures, and a hook or deny rule for what must never bend, and proposes the last ones instead of changing your settings.
- **Refactors that lose nothing** — a saturated `CLAUDE.md` becomes a smaller set with a keep / move / delete table, and an independent reviewer checks that no requirement disappeared.

## 🧩 What's inside

| Component     | Name                    | What it does        | How it runs                                             |
| :------------ | :---------------------- | :------------------ | :------------------------------------------------------ |
| 🎯 Skill      | `instruction-engineering:claude-md-and-rules` | Method and references for writing, editing, reviewing, auditing, debugging and refactoring instruction files at user and project scope: placement, wording, layout, loading rules, cross-file analysis, and when a procedure belongs in a skill or a rule in a hook | `/instruction-engineering:claude-md-and-rules` or automatically when your request is about instruction files |
| 🐍 Script     | `skills/claude-md-and-rules/scripts/check_instructions.py` | Read-only checker: inventory of what loads, rule frontmatter, glob matches, `--match` scope tests, imports, missing package scripts, duplicates, size limits, `AGENTS.md` shadowing, plus heuristic leads such as near-duplicates and procedures | Run by the skill or the agent through Bash, or by you |
| 🤖 Agent      | `instruction-engineering:reviewer` | Independent, read-only review of instruction changes in a fresh context, including a check that a refactor lost no requirement | Delegated by Claude, or "use the instruction-engineering reviewer agent" |

## ✅ Requirements

| Requirement             | Details                                                                   |
| :---------------------- | :------------------------------------------------------------------------ |
| **Claude Code**         | v2.1.271 or later — check with `claude --version`. The features the skill points you to have their own minimums: `AGENTS.md` support v2.1.277+, `/doctor prompt-audit` v2.1.283+ |
| **Surfaces**            | See [Compatibility](#-compatibility)                                      |
| **External tools**      | `python3` 3.12 or later on `PATH` for the checker (check with `python3 --version`; install from [python.org](https://www.python.org/downloads/) or your package manager). `git` is optional, used only to check whether `CLAUDE.local.md` is ignored |
| **Accounts / API keys** | None |
| **Network**             | See [What this plugin runs and sends](#-what-this-plugin-runs-and-sends)  |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install instruction-engineering --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install instruction-engineering@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

No GitHub SSH key? Set this first, so installs from `/plugin` and updates use HTTPS:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install instruction-engineering --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install instruction-engineering@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Instruction Engineering** in **Discover** and select **Add**.

In the desktop app's **Code** tab you can also click **+** next to the prompt box → **Add plugins** (or **Plugins** → **Browse plugins**), or open **Settings** → **Plugins** → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

Ask in your own words; Claude loads the skill when your request is about instruction files. You can also call it directly:

```text
/instruction-engineering:claude-md-and-rules audit this repository's instructions
```

### Write or add instructions

```text
Write a CLAUDE.md for this repo.
Add to CLAUDE.md: never edit files in src/gen.
```

**Result:** Claude reads the instructions that already load, places the new line where it applies (often a path-scoped rule rather than `CLAUDE.md`), words it as an action, and tells you what it noticed along the way, such as an existing rule that already says the same thing.

### Audit or refactor a saturated set

```text
Audit our Claude instruction files; don't change anything yet.
Our CLAUDE.md is 400 lines and Claude ignores half of it. Refactor it.
```

**Result:** a findings report with evidence for each item, or a target structure with a keep / move / delete table and the always-loaded size before and after. Nothing changes until you approve it, and the `instruction-engineering:reviewer` agent can check the result in a fresh context.

### Debug a rule that doesn't apply

```text
Why doesn't my rule in .claude/rules/api.md load when Claude edits src/api/v2/users.ts?
```

**Result:** Claude checks the rule's frontmatter and globs with the checker's `--match` test against the file, explains what the loader does with it, and proposes the fix.

### Stop a repeated misbehavior

```text
Claude keeps running npm instead of pnpm. Make it stop.
```

**Result:** Claude finds why the written instruction failed and recommends the right mechanism, a clearer line, a scoped rule, a hook or a deny rule, with an exact snippet. It never changes your settings or hooks unless you ask.

### Run the checker yourself

Find it in the installed plugin's folder, then run it from your project root:

```bash
find ~/.claude/plugins/cache -name check_instructions.py -path '*instruction-engineering*'
python3 /path/to/check_instructions.py --project .
python3 /path/to/check_instructions.py --project . --match src/api/users.ts README.md
```

Exit code `0` means no error-level finding, `1` at least one, `2` bad arguments. `--json` prints machine-readable output, `--no-user` skips your user configuration directory.

## 🔍 What this plugin runs and sends

- **Hooks:** none. **MCP servers:** none. **Background processes:** none.
- **The checker** only reads. It reads the instruction files (`CLAUDE.md`, `CLAUDE.local.md`, `.claude/CLAUDE.md`, `AGENTS.md`, `.claude/rules/**/*.md`) of the project you pass, of every directory above it up to the filesystem root, and of `~/.claude` (or `$CLAUDE_CONFIG_DIR`; skip it with `--no-user`). It reads files those instruction files `@import` when they sit inside the project or the user configuration directory; imports anywhere else are only checked for existence. It reads `package.json` files to verify script names and lists file names under the project to test globs (skipping `.git`, `node_modules` and `.claude/worktrees`). It runs `git check-ignore -q CLAUDE.local.md` when that file exists. It writes nothing, runs nothing from the files it reads, and its report shows paths, counts and findings, not file contents.
- **The skill** edits instruction files only when you ask for a write, edit or refactor. Audits stay read-only until you approve an edit set. It asks before running any project command (tests, linters) and before changing user-scope files, which affect every project. It never changes settings, hooks, permissions or source code on its own; it proposes them with exact snippets.
- **The agent** is told to stay read-only. It has Read, Grep, Glob and Bash; its Bash calls go through your normal permission settings, since a plugin agent can't set its own permission mode, and it is told to run only the checker and read-only commands (`ls`, `cat`, `wc`, `git status --short`, `git diff`, `git show`). It starts without your user, project and local `CLAUDE.md` files (`omitClaudeMd`); managed policy files still load, and a subdirectory's `CLAUDE.md` or matching rules still load when it reads files there.
- **Network:** none from the plugin. When your Claude Code is newer than the version the skill's loader facts were checked against, the skill asks Claude to read the official changelog, which uses your session's web access if you allow it.
- **Files written:** only the instruction files you ask Claude to change.

## 🔄 Updating

```bash
claude plugin update instruction-engineering@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Instruction Engineering** → **Update now**. Then run `/reload-plugins`.

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `instruction-engineering@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall instruction-engineering@the-claude-factory
```

Installed with `--scope project`? Add `--scope project` here too. Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you pass `--keep-data`.

In a session: `/plugin` → **Installed** → **Instruction Engineering** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Instruction Engineering** → its menu → **Remove**.

The plugin keeps no data of its own. Instruction files Claude changed at your request stay in your projects.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component                              |                         Claude Code                          |                                                                                                                                          Claude app                                                                                                                                           |
| :------------------------------------- | :----------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| 🎯 Skills                              |                              ✅                              |                                                                                                                                              ✅                                                                                                                                               |
| 🤖 Agents                              |                              ✅                              |                                                                                                                       ⚠️ in Cowork sessions, not in a chat conversation                                                                                                                       |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/instruction-engineering:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>What works in a Claude app chat conversation?</b></summary>

The skill loads and guides the work. The `instruction-engineering:reviewer` agent runs only in Cowork sessions and Claude Code, and the checker runs only where Claude can run `python3` 3.12+ on your files.

</details>

<details>
<summary><b>The checker says a rule matches, but Claude doesn't seem to follow it.</b></summary>

Discovery is not proof of loading. The checker's glob matcher approximates Claude Code's, and a match says the rule *should* load. Confirm in a session with `/context`, the `Loaded` line shown for subdirectory files, an `InstructionsLoaded` hook, or `claude --debug` for frontmatter parse errors. A rule that loads and is still ignored is a wording or mechanism problem: ask Claude why it keeps doing X.

</details>

<details>
<summary><b>What doesn't the checker evaluate?</b></summary>

Managed policy files, auto memory, plugins, skills and `claudeMdExcludes`. It also can't judge meaning: contradictions in what lines say need a reader, which is the skill's and the agent's job.

</details>

<details>
<summary><b>My Claude Code is newer than the version the plugin was checked against.</b></summary>

Loader behavior changes between releases. When `claude --version` is newer, the skill tells Claude to read the changelog entries about `CLAUDE.md`, rules and `paths` before relying on a detail.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [How Claude remembers your project](https://code.claude.com/docs/en/memory) — `CLAUDE.md` and `.claude/rules`
- 📖 [Skills](https://code.claude.com/docs/en/skills) · [Subagents](https://code.claude.com/docs/en/sub-agents)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=instruction-engineering) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=instruction-engineering) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=instruction-engineering)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
