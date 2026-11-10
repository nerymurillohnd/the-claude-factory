<div align="center">

# 🩺 Skill Diagnostics

<p><strong>Audits Claude skills against the official best practices and gates them: five validation scripts, four independent reviewers, a cold executor and an adversarial verifier give one report with file-and-line evidence and one verdict, and a gate has Claude audit every skill it creates or changes before it finishes.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fskill-diagnostics%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Testing%20%26%20Quality-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.271-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Ask Claude to audit a skill, or type `/skill-diagnostics:skills-best-practices`, and get one report with the exact line behind every finding and one verdict. In Claude Code, every skill Claude changes is audited before Claude finishes its turn.

A skill can look finished to the person who wrote it and still fail the model that runs it: a description that never triggers, a placeholder nothing defines, a reference that contradicts `SKILL.md`, a field that one surface rejects. Skill Diagnostics reads a finished skill and tells you, with evidence, what to fix before you release it, and in Claude Code it makes Claude audit every skill it creates or changes.

## ✨ Why use it

- **Audit only** — it writes no skill. Write or edit a skill with any skill-writing skill, such as Anthropic's `skill-creator`, or by hand; then this plugin checks it against Anthropic's published best practices for the description, frontmatter, body, workflows, scripts and security.
- **An audit you can trust** — five scripts check what can be checked mechanically, four reviewers each judge one area, a cold executor follows the skill as a model that has nothing else, and an adversarial verifier tries to refute every finding against your files and the live official docs. You get one report and one verdict.
- **Evidence, not opinions** — every finding quotes the exact text with its file and line and says how to fix it.
- **Nothing slips through** — in Claude Code, a gate makes Claude audit every skill it creates or changes before it ends its turn, including skills written by a shell command.
- **Measure before you release** — the `/skill-diagnostics:evals` workflow runs a skill's trigger and output-quality evals, with and without the skill, and reports pass rates, time and tokens.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `skill-diagnostics:skills-best-practices` | Audits a skill, and its evals when it has them, with 5 scripts, 4 reviewers, a cold executor and an adversarial verifier, and gives one report and one verdict | `/skill-diagnostics:skills-best-practices`, automatically when you ask Claude to review or audit a skill, and after Claude creates or changes one |
| 🤖 Agent | `skill-diagnostics:description-reviewer` | Reviews the description, frontmatter and the surfaces the skill reaches | Launched by the skill during an audit only |
| 🤖 Agent | `skill-diagnostics:instructions-reviewer` | Reviews the body, structure and workflows passage by passage | Launched by the skill during an audit only |
| 🤖 Agent | `skill-diagnostics:scripts-runtime-reviewer` | Reviews bundled scripts and Claude Code runtime features | Launched by the skill during an audit only |
| 🤖 Agent | `skill-diagnostics:security-reviewer` | Reviews network calls, sensitive reads and actions the description doesn't announce | Launched by the skill during an audit only |
| 🤖 Agent | `skill-diagnostics:cold-executor` | Follows the skill on one realistic task and marks every point where it would have to guess | Launched by the skill during an audit only |
| 🤖 Agent | `skill-diagnostics:adversarial-verifier` | Tries to refute each finding and rules it upheld, downgraded or withdrawn | Launched by the skill during an audit only |
| 🪝 Hook | `SessionStart` | Marks the session's start time and clears its own state older than 7 days | Automatically when a session starts |
| 🪝 Hook | `PostToolUse` | After a `Write` or `Edit` inside a skill folder, records the skill and tells Claude to audit it (or to offer an audit) | Automatically on matching tool calls |
| 🪝 Hook | `Stop` | Keeps Claude working until every changed skill has an audit verdict newer than the change | Automatically when Claude is about to end its turn |
| 🪝 Hook | `SubagentStop`, `PostToolUse` on `SubagentHandback` | Saves each audit agent's report unchanged, so the final report can be checked against what every agent found | Automatically when one of this plugin's agents finishes |
| 🪝 Hook | `PermissionRequest` on `Bash` | Approves the skill's own scripts, run exactly as the skill writes them, when Claude Code would otherwise ask you in a later turn of an audit | Automatically when Claude Code is about to ask for permission |
| 🔁 Workflow | `skill-diagnostics:evals` | Runs trigger and output-quality evals on one skill and reports the results | `/skill-diagnostics:evals`, on request only |

All six agents are read-only: they have the Read, Glob and Grep tools, and the verifier also WebFetch. None of them can change a file.

Each agent sets its own model and effort level, whatever your session uses: the four reviewers run on Sonnet, the cold executor and the verifier on Opus; the description and instructions reviewers and the cold executor at `high` effort, the scripts-and-runtime and security reviewers and the verifier at `xhigh`. If one of these models isn't available to your account, Claude Code switches that agent to another model only when you've configured a [fallback model chain](https://code.claude.com/docs/en/model-config#fallback-model-chains). `CLAUDE_CODE_EFFORT_LEVEL`, when you set it, overrides every agent's level, and `maxEffortLevel` or your organization's limit caps it.

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.271 | `claude --version` |
| Bash (runs the hooks; on Windows, Git Bash) | 3.2 | `bash --version` |
| jq (the hooks read and write JSON with it) | — | `jq --version` |
| Python, as `python3` on your `PATH` (runs the skill's scripts) | 3.12 | `python3 --version` |

The plugin also uses `cat`, `find`, `mkdir`, `mv`, `rm`, `rmdir`, `sed`, `touch` and `tr`, which come with macOS and Linux, and with Git Bash on Windows.

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

### 🐚 Bash

Linux and macOS already have Bash: macOS ships Bash 3.2, which the hooks support. On Windows, install Git for Windows, which includes Git Bash.

<details>
<summary>🪟 <b>Git for Windows (winget)</b> — Windows</summary>

```bash
winget install --id Git.Git -e --source winget
```

</details>

### 🧰 jq

If `jq --version` prints a version, you're set. Otherwise install it from the [official jq downloads](https://jqlang.org/download/).

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install jq
```

</details>
<details>
<summary>🚢 <b>MacPorts</b> — macOS</summary>

```bash
sudo port install jq
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt-get install jq
```

</details>
<details>
<summary>📦 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install jq
```

</details>
<details>
<summary>📦 <b>pacman</b> — Arch Linux</summary>

```bash
sudo pacman -S jq
```

</details>
<details>
<summary>📦 <b>zypper</b> — openSUSE</summary>

```bash
sudo zypper install jq
```

</details>
<details>
<summary>🪟 <b>winget</b> — Windows</summary>

```bash
winget install jqlang.jq
```

</details>

On Windows, open a new Git Bash window afterwards and run `jq --version` there.

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

Or download the installer from [python.org](https://www.python.org/downloads/). On Windows, Python's install manager adds the `python3` command; the older full installer (`python-3.x.exe`) adds only `python` and `py`, so the skill's scripts can't start.

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

### 🖥️ Claude (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Skill Diagnostics** in **Discover** and select **Add**.

## 🚀 Usage

### Audit a skill

```text
/skill-diagnostics:skills-best-practices audit ~/.claude/skills/release-notes
```

**Result:** a report in the conversation with the verdict (**pass**, **pass with warnings**, **fail** or **not determinable**), the findings by severity, each with its file, line, quoted text and fix, and what couldn't be checked. Every audit is complete: all five scripts and all six agents read every file of the skill, whichever files changed. The audit changes nothing in the skill; fixing the findings is a separate step you ask for. When the skill has no evals, Claude then asks whether you want some; it's your call.

You can also just ask: "review my skill in `./skills/invoice-note` before I publish it".

### Let the gate catch it

Ask Claude to change a skill, for example "tighten the description of my `pdf-forms` skill". With the default `gate` setting, Claude makes the change, audits the skill, and only then finishes its turn. Skills written by a shell command or another program are caught too, as long as they sit in your project folder or in `~/.claude/skills`.

### Measure a skill before release

```text
/skill-diagnostics:evals ./skills/release-notes
```

**Result:** about 20 trigger queries, each run 3 times in a fresh `claude -p` session, and 2 or 3 output cases, each run with and without the skill and graded with quoted evidence. You get the trigger pass rates, the output pass rates, the time and tokens the skill adds, and a proposed description to try next. Claude Code asks before it starts the workflow.

## ⚙️ Configuration

| Option | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `on_skill_write` | string: `gate`, `suggest` or `off` | `gate` | What happens after Claude creates or changes a skill. `gate`: Claude audits the skill before it finishes its turn, and the `Stop` hook keeps it working until the audit's verdict is recorded. `suggest`: once per skill per session, Claude offers you an audit when you've finished with the skill, and runs it only if you ask; nothing keeps Claude working. `off`: the hooks do nothing and write nothing. |

Set the option when installing:

```bash
claude plugin install skill-diagnostics@the-claude-factory --config on_skill_write=suggest
```

Later, in a session, open the options dialog:

```text
/plugin configure skill-diagnostics@the-claude-factory
```

You can also use `/plugin` → **Installed** → **Skill Diagnostics** → **Configure options**, or the plugin's row in `/config` (v2.1.269+). From the shell (v2.1.285+), `claude plugin configure skill-diagnostics@the-claude-factory` shows the current state; restart Claude Code after saving a value there.

In Claude the option can't be changed and keeps its default, `gate`.

## 🔍 What this plugin runs and sends

- **Hooks:** five Bash scripts, run as `bash` with `"shell": "bash"`, so on Windows they run in Git Bash. Each reads the event Claude Code passes it with `jq`, never blocks a tool call, and on any failure writes one line to stderr and exits 1, so Claude Code shows a hook error and goes on. With `on_skill_write` set to `off`, the gate's three scripts exit at once (`session-start.sh` still deletes old audit folders); the report and approval scripts serve the audit itself, so they run in every mode.
  - `SessionStart` runs `hooks/session-start.sh` (10 s timeout). It creates an empty marker file named after the session, whose time is the session start; a compaction keeps the old time. It also deletes this plugin's session files and audit files untouched for more than 7 days. Prints nothing.
  - `PostToolUse` on `Write|Edit` runs `hooks/skill-changed.sh` (10 s timeout), also for tool calls made by subagents. It finds the skill folder of the written file (the nearest folder upwards that holds `SKILL.md`), adds it to the session's pending list, and the first time in the session adds one line to Claude's context: in `gate` mode, to audit the skill before finishing; in `suggest` mode, to offer you an audit. It skips files outside any skill, skills inside Claude Code's `plugins/` and `skills/synced/` folders (which Claude Code overwrites), and this plugin's own files.
  - `Stop` runs `hooks/audit-gate.sh` (15 s timeout), in `gate` mode only. It looks for skill folders changed since the session started under your project folder and under `~/.claude/skills`, skipping `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `dist`, `build` and `target`, and adds them to the pending list. A pending skill is cleared once its verdict file is newer than every file in it, or when it's gone. For the rest, it tells Claude to run the audit before finishing. After 2 such reminders for a skill that hasn't changed since, it lets Claude stop and shows you a warning that the skill wasn't audited.
  - `SubagentStop`, matched on this plugin's six agents, and `PostToolUse` on `SubagentHandback` (how a subagent reports in auto mode) run `hooks/save-agent-report.sh` (10 s timeout). It writes the agent's report, exactly as the agent wrote it, to the session's audit folder. Reports of other agents are ignored. Prints nothing.
  - `PermissionRequest` on `Bash` runs `hooks/approve-own-scripts.sh` (10 s timeout) only when Claude Code is about to ask you to approve a `python3` command. It answers "allow" only when the command is `python3` followed by the full path of one of the skill's six scripts in this plugin's folder, with no shell operator, substitution, redirect or line break after it. Anything else prints nothing, so you're asked as usual. It never denies, never adds a permission rule to your settings, and your own deny and ask rules still apply before it. Without `jq` it prints nothing and you're asked.
- **The skill's scripts:** `check-metadata.py`, `check-structure.py`, `check-runtime.py`, `check-size.py` and `check-evals.py` read the skill you audit, and `check-evals.py` also the plugin eval cases that name it, print their results and write them to the session's audit folder for the next script. When the skill sits inside a plugin and `claude` is on your `PATH`, `check-size.py` also runs `claude --plugin-dir <plugin folder> plugin details <plugin name>` (60 s timeout) to read Claude Code's token figure for the skill; that command lists the plugin's components and starts none of its MCP servers or hooks. Otherwise, or if it fails, the script estimates the tokens from the characters. `record-verdict.py` writes the audit's verdict. The skill pre-approves exactly these six `python3` commands for the turn that invokes it; in the audit's later turns, where that approval has ended, the `PermissionRequest` hook approves the same commands.
- **MCP servers:** none.
- **Network:** the adversarial verifier reads public pages from `code.claude.com`, `claude.com`, `platform.claude.com`, `support.claude.com`, `agentskills.io` and the Claude Code changelog on `github.com` to check findings. The hooks make no network calls, and the scripts make none of their own; the `claude plugin details` call that `check-size.py` makes may use your Claude Code sign-in to count the tokens. Nothing from your skill is uploaded. The evals workflow starts `claude -p` sessions, which use your plan like any other session.
- **Files written:** in the plugin's data directory (`~/.claude/plugins/data/<id>/`):
  - `sessions/<session id>`: the empty session marker.
  - `pending/<session id>`: the skill folders that still need an audit, one per line; short-lived work files next to it are deleted when the gate finishes.
  - `guard/<session id>/<skill key>`: how many times the gate has reminded Claude about that skill.
  - `verdicts/<skill key>`: the last verdict for that skill, as `{"skill", "verdict", "recorded_at"}`.
  - `audits/<session id>/`: each audit's script results (under the skill's name) and `agents/<agent>-<agent id>.md`, each agent's report as the agent wrote it.

  The `<skill key>` is the skill's full path with `/`, `:` and `%` encoded. Files under `sessions/`, `pending/`, `guard/` and `audits/` are deleted after 7 days; verdict files stay until you uninstall. The plugin never changes your skill. The evals workflow writes its runs in a `<skill>-workspace` folder next to the skill. An audit writes nothing in your project: its results and reports stay in the audit folder, which the report names, and Claude copies them into your project only when you ask.
- **Privacy:** the author collects no data. The marketplace's [privacy policy](https://github.com/nerymurillohnd/the-claude-factory/blob/main/PRIVACY.md) covers this plugin and the outside services it can reach.

## 🔄 Updating

```bash
claude plugin update skill-diagnostics@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

Installed from Claude? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `skill-diagnostics@synced`: update and uninstall it in Claude (**Customize** → **Plugins**).

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update jq and Python the way you installed them, for example with Homebrew:

```bash
brew upgrade jq python
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall skill-diagnostics@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall skill-diagnostics@the-claude-factory --scope project
```

In Claude: **Customize** → **Plugins** → **Skill Diagnostics** → its menu → **Remove**.

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, with the session files and verdicts in it, unless you add `--keep-data`. Skills you wrote with it and `<skill>-workspace` folders from the evals workflow stay; delete them yourself if you no longer need them. jq and Python stay installed.

To remove the marketplace too (this also uninstalls every plugin you installed from it):

```bash
claude plugin marketplace remove the-claude-factory
```

Or, inside a session:

```text
/plugin marketplace remove the-claude-factory
```

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude

| Component | Claude Code | Claude |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |
| 🤖 Agents | ✅ | ⚠️ only in conversations where Claude can run tasks |
| 🪝 Hooks | ✅ | ⚠️ only in conversations where Claude can run tasks |
| 🔁 Workflows | ✅ | ➖ not documented for Claude |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

Where Claude can't run tasks, agents and hooks don't run, and the skill still audits inline: Claude applies the four reviewers' checks, the cold executor's trace and the verification itself, one after another, and the report says that no independent agents ran. The five scripts need the code execution sandbox; without it they can't run and the verdict is *not determinable*. No gate runs there, so ask for the audit yourself after writing a skill. Where Claude can run tasks, the hooks run where Claude runs them, so they need Bash and `jq` there. The `/skill-diagnostics:evals` workflow runs only in Claude Code, on paid plans and with API access; on Pro, turn on **Dynamic workflows** in `/config` first.

**Platforms:** macOS and Linux, and Windows through Git Bash, which comes with [Git for Windows](https://git-scm.com/downloads/win): the hooks run there, so check `bash`, `jq` and `python3` in a Git Bash window.

## 🚧 Limitations

- The gate works in Claude Code and in conversations where Claude can run tasks. Elsewhere in Claude hooks don't run, so nothing gates a skill there.
- It's a barrier for Claude, not a guarantee. If a gate script fails, for example because `jq` is missing, Claude Code shows a hook error and Claude can stop without an audit.
- `disableAllHooks` in your settings turns the hooks off, and an organization's `allowManagedHooksOnly` blocks them unless managed settings force-enable this plugin.
- Claude Code ends a turn after 8 consecutive `Stop` continuations with no tool call between them, whatever the gate says. The `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` environment variable raises that cap.
- The scan for skills written by shell commands or other programs covers your project folder and `~/.claude/skills` only. When the project folder is your home folder or `/`, only `~/.claude/skills` is scanned, because the whole tree can't be searched in time.
- If you press `Esc` while Claude is changing a skill, or interrupt the turn, the skill may not be recorded or the gate may not run until Claude next stops.
- A skill whose full path is longer than about 200 characters may give a verdict or guard file name longer than your file system allows; the gate then shows a hook error.
- Under an organization's `allowManagedPermissionRulesOnly`, the skill's pre-approved commands may not apply: Claude asks before running the scripts, and in `dontAsk` mode they are denied, so the verdict can't be recorded.
- With hooks turned off, the agents' reports aren't saved (the report says which are missing), and in an audit's later turns Claude Code asks you before running the skill's scripts.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/skill-diagnostics:` to list its skill and workflow. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>I see a "hook error" from skill-diagnostics after every edit.</b></summary>

A hook couldn't run, most often because `jq` is missing or not on the `PATH` that Claude Code uses. Run `jq --version` (on Windows, in Git Bash), install jq if needed, and start a new session. Until then the gate doesn't work, but your work goes on as usual.

</details>

<details>
<summary><b>Claude keeps going after I thought it was done.</b></summary>

With `on_skill_write` set to `gate`, Claude audits every skill it changed before it finishes. That's the point of the gate. To be asked instead, set the option to `suggest`; to turn it off, set it to `off` ([Configuration](#%EF%B8%8F-configuration)).

</details>

<details>
<summary><b>The gate warned that a skill "wasn't audited after the change".</b></summary>

Claude was reminded twice and still didn't record a verdict, so the gate let it stop. Ask Claude to audit the skill, for example `/skill-diagnostics:skills-best-practices audit <path>`.

</details>

<details>
<summary><b>The verdict is "not determinable".</b></summary>

Something the audit needs couldn't be checked: a script couldn't run (for example without `python3`, or where Claude can't run tasks and has no code execution sandbox), a file couldn't be read, or an agent's report stayed incomplete. The report names what was missing.

</details>

<details>
<summary><b>Does it change my skill?</b></summary>

No. The plugin only audits and changes no file of your skill. Fixes, and evals if you want them, are separate steps you ask for.

</details>

<details>
<summary><b>How much does an audit cost?</b></summary>

Each audit runs six agents over every file of the skill and checks findings against the live docs, so it uses noticeably more of your plan than a single reply, and two of its agents run on Opus. The evals workflow runs dozens of `claude -p` sessions and costs more still; run it before a release, not after every edit.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Claude Code skills](https://code.claude.com/docs/en/skills)
- 📖 [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- 📖 [Subagents](https://code.claude.com/docs/en/sub-agents) · [Hooks](https://code.claude.com/docs/en/hooks) · [Dynamic workflows](https://code.claude.com/docs/en/workflows)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=skill-diagnostics) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=skill-diagnostics) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=skill-diagnostics)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
