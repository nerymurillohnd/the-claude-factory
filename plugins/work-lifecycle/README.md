<div align="center">

# 🧭 Work Lifecycle

<p><strong>Plans and builds work in stages, from goal to verified result: researches current official sources and the code, writes a self-contained, verifiable plan before anything changes, blocks Claude from finishing while a task lacks recorded evidence, and implements code test-first with each red and green run recorded and checked against a baseline. Work you can verify.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fwork-lifecycle%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Productivity-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.325-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Type `/work-lifecycle:planning-before-execution` before a multi-step task and Claude plans first, waits for your approval, then can't call the work finished until every task has the real output of its check on record.

Work Lifecycle makes Claude plan multi-step work before it changes anything, and write code test-first. The planning skill researches the code and the official sources, asks you about your goal and context (never about methods), writes a plan an implementer can follow without any other context, and executes it task by task. A Stop hook, the _plan gate_, keeps Claude from finishing while a task has no recorded evidence. The testing skill records a failing run before the code and a passing run after it, and compares the whole project with its baseline.

## ✨ Why use it

- **No more "done" without proof** — Each task's check command and its real output go into a state file. Claude can't end its turn while an approved plan has a task without evidence.
- **Plans that survive a fresh start** — The plan names the files, the tasks, the check and expected output of each one, the acceptance criteria and the actions that need your authorization, so a new session can carry it out.
- **Tests that catch something** — Each test names the break it catches and is seen failing for that reason before the code exists. The skill compares the full suite, lint and type check with the baseline, and reports failures that were already there without touching them.

## 🧩 What's inside

| Component | Name                                           | What it does                                                                                                                                                                                                 | How it runs                                                                    |
| :-------- | :--------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| 🎯 Skill  | `work-lifecycle:planning-before-execution`     | Plans multi-step work with research, a self-review and your approval, then executes it task by task and records each task's evidence.                                                                        | `/work-lifecycle:planning-before-execution` or automatically when relevant     |
| 🎯 Skill  | `work-lifecycle:testing-before-implementation` | Implements code test-first: baseline, a named break, a recorded red run, minimal code, a recorded green run and a comparison with the baseline.                                                              | `/work-lifecycle:testing-before-implementation` or automatically when relevant |
| 🤖 Agent  | `work-lifecycle:planning-researcher`           | Read-only, in-depth research of the code, official sources and installed versions, through your session's docs servers and skills; reports each claim with its evidence and what it could not verify.        | Delegated by Claude, or "use the planning-researcher agent"                    |
| 🤖 Agent  | `work-lifecycle:plan-verifier`                 | Read-only, adversarial review of a plan against its requirements, or of finished work against the plan and its state file, checked through your session's docs servers and skills; also checks test quality. | Delegated by Claude, or "use the plan-verifier agent"                          |
| 🪝 Hook   | `Stop` (the plan gate)                         | Blocks Claude from finishing while a task of an executing plan lacks evidence.                                                                                                                               | Automatically, in the session where you invoked the planning skill             |

## 📋 Prerequisites

| Tool          | Minimum version | Check               |
| :------------ | :-------------- | :------------------ |
| Claude Code   | 2.1.325         | `claude --version`  |
| python3       | 3.12            | `python3 --version` |
| git, optional | —               | `git --version`     |

Your project's own test, lint and type-check commands are also needed for test-first work; the testing skill finds them in your project's files.

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

### 🐍 python3

The plan gate and the state file validator are Python scripts written for Python 3.12 or later, using only the standard library. Claude Code runs them as `python3`, so they use the first `python3` on your `PATH`. Install Python any way you like; just make sure that `python3 --version` prints 3.12 or later. If `python3` is missing or older, the gate can't start and lets Claude stop, with only a hook error notice; the planning skill checks `python3 --version` first and tells you.

<details>
<summary>🐍 <b>Official installer</b> — macOS</summary>

Download the macOS installer for Python 3.12 or later from [python.org/downloads](https://www.python.org/downloads/) and run it.

</details>
<details>
<summary>⚡ <b>uv</b> — macOS, Linux</summary>

```bash
uv python install 3.12 --default
```

`--default` also installs the `python3` and `python` commands; uv marks it experimental. Run `uv python dir --bin` to see the folder it installs them in, which must be on your `PATH`.

</details>
<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install python@3.12
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

An older release's package manager can install a version below 3.12; then use another method above, or build it from [python.org/downloads](https://www.python.org/downloads/).

### 🌿 git

Optional. The testing skill uses it to set aside code that was written before its test on a local branch.

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install git
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt install git
```

</details>
<details>
<summary>📦 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install git
```

</details>

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install work-lifecycle@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install work-lifecycle --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install work-lifecycle@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install work-lifecycle@the-claude-factory
```

### 🖥️ Claude (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Work Lifecycle** in **Discover** and select **Add**.

## 🚀 Usage

The skills are meant for interactive sessions. Invoke one by name, or describe the work and let Claude pick it.

### Plan a migration before touching it

```text
/work-lifecycle:planning-before-execution Upgrade our API from Express 4 to Express 5 without changing any endpoint's behavior
```

**Result:** Claude enters plan mode when it can, asks you a few questions about the outcome, the constraints and what must not change, reads the code and the official migration guide, and writes a plan with a file map, tasks with their checks and expected output, acceptance criteria and authorization checkpoints. It reviews the plan itself, has `plan-verifier` review it when the stakes are high, and asks for your approval. After you approve, it works task by task and records each check's command and real output in `.work-lifecycle/`. It can't finish while a task lacks evidence.

### Fix a bug test-first

```text
/work-lifecycle:testing-before-implementation parse_price("1,299.50") returns 1.0 instead of 1299.5
```

**Result:** Claude finds your test, lint and type-check commands and records a baseline. It names the break the new test catches, runs the test and shows it failing for that reason, writes the minimal code, shows the same test passing, and compares the full suite, lint and types with the baseline. It reports failures that were already there by name and leaves existing tests unchanged. You get a report with each red and green run and its command.

### Run both as one flow

```text
Plan and implement a retry with backoff for our HTTP client, test-first
```

**Result:** Claude plans first. After you approve, it carries out each code task with the testing skill, and records the red and green runs in the state file the plan gate reads. A task marked test-first isn't complete until both runs are on record.

### Hand the plan to `/goal`

After a plan with more than one task and one measurable end state, Claude can give you a ready-to-paste `/goal` condition that points at the approved plan.

```text
/goal Execute the approved plan at <plan file path>, task by task, passing each task's check before the next. First invoke the work-lifecycle:planning-before-execution skill and follow its Execution section.
```

**Result:** Claude Code keeps working until the end state the condition names is printed in the conversation. Only you can type `/goal`, and typing it is your go-ahead to execute.

## ⚙️ Configuration

The plugin has no options to set. Its behavior depends on what it finds in your project:

| What it reads in your project                                                                                                     | What it does then                                                                                                                                                          |
| :-------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.work-lifecycle/<session id>.json`                                                                                               | The plan gate blocks Claude from finishing while the plan is executing and a task lacks evidence. With no file, or a status other than `executing`, the gate does nothing. |
| `CLAUDE.md`, the project manifest (`package.json`, `pyproject.toml`, `Makefile`, `Cargo.toml`, `go.mod`) and the CI configuration | The testing skill takes your test, lint and type-check commands from them, and prefers the exact command CI runs.                                                          |
| Your existing tests                                                                                                               | The testing skill matches their framework, layout, naming and style, and keeps them unchanged.                                                                             |

These optional settings of your own strengthen it. The plugin sets none of them.

| Setting                        | Effect                                                                           |
| :----------------------------- | :------------------------------------------------------------------------------- |
| `plansDirectory`               | Set it inside your repository to keep plans under version control.               |
| `showClearContextOnPlanAccept` | Set it to `true` to offer clearing the planning context when you approve a plan. |
| `permissions.defaultMode`      | Set it to `"plan"` for sensitive projects, so every session starts in plan mode. |
| `permissions.ask`              | Add rules for `git push` and your deploy commands, so auto mode can't skip them. |

## 🔍 What this plugin runs and sends

- **Hooks:** `Stop` (no matcher) runs `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/plan-gate.py` with a 30-second timeout. The planning skill registers it in its own frontmatter, so it exists only in a session where you invoked that skill, and never in other sessions. It reads the hook input from stdin and the project folder from `CLAUDE_PROJECT_DIR` (or the input's `cwd`), then reads only `<project>/.work-lifecycle/<session_id>.json`. With no file, or with the plan still planning or waiting for you, it does nothing. While an executing plan has tasks without evidence it blocks the stop, and it writes a small `<session_id>.gate` file beside the state file to count blocks. It lets Claude pause while subagents, workflows or other work that reports back are running, but not for a long-running shell command or monitor such as a dev server, and stops blocking after 3 continuations in a row without progress. When a plan is marked done with tasks still lacking evidence, it lets Claude stop and shows you once which tasks were left. Hooks run on their own, with your access and without a permission prompt.
- **Commands Claude runs:** the skill pre-approves one command, `python3 "${CLAUDE_SKILL_DIR}/scripts/validate-state.py" <state file>`, which only reads the state file and prints whether it is valid. The testing skill runs your project's own test, lint and type-check commands, and, when code predates its test, `git switch -c wip/<behavior>-before-test` with one local commit. It never pushes.
- **MCP servers:** none shipped. The two agents run on your session's model with every tool your session has, MCP tools included, except `Edit` and `Write`, to read documentation through them, and are told to change nothing. `planning-researcher` also runs at your session's effort level.
- **Network:** the plugin's scripts make no network call and send no telemetry. The planning skill and its two agents read current official documentation, through your session's docs servers and skills or by fetching web pages and running web searches, under your permission settings. Those requests go to the sites and search service Claude uses, with the URL or query.
- **Files written:** `<project>/.work-lifecycle/`, created with its own `.gitignore` that holds `*`, so nothing in it reaches your repository. It holds the state file `<session_id>.json` and the `<session_id>.gate` file. In plan mode, Claude Code stores the plan in its own plan file, or in your `plansDirectory`. The plugin writes nothing under `${CLAUDE_PLUGIN_DATA}`. The testing skill writes the tests and code you asked for.
- **Privacy:** the author collects no data. The marketplace's [privacy policy](https://github.com/nerymurillohnd/the-claude-factory/blob/main/PRIVACY.md) covers this plugin and the outside services it can reach.

## 🔄 Updating

```bash
claude plugin update work-lifecycle@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

Installed from Claude? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `work-lifecycle@synced`: update and uninstall it in Claude (**Customize** → **Plugins**).

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update python3 the way you installed it, for example with uv, Homebrew, apt or dnf:

```bash
uv python upgrade 3.12
```

```bash
brew upgrade python@3.12
```

```bash
sudo apt install --only-upgrade python3
```

```bash
sudo dnf upgrade python3
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall work-lifecycle@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall work-lifecycle@the-claude-factory --scope project
```

In Claude: **Customize** → **Plugins** → **Work Lifecycle** → its menu → **Remove**.

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps nothing in its data directory. Each project where you ran a plan keeps its `.work-lifecycle/` folder, which you can delete. Plans, tests, code and any local `wip/` branches the plugin helped create stay in your projects, and so do the python3 and git you installed.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude

| Component | Claude Code |                       Claude                        |
| :-------- | :---------: | :-------------------------------------------------: |
| 🎯 Skills |     ✅      |                         ✅                          |
| 🤖 Agents |     ✅      | ⚠️ only in conversations where Claude can run tasks |
| 🪝 Hooks  |     ✅      | ⚠️ only in conversations where Claude can run tasks |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

In Claude Code, you get everything. The plan gate is a hook that the planning skill registers, not one listed in `hooks/hooks.json`, so `/plugin` may count no hooks for this plugin.

In Claude, the planning skill plans without the agents, the plan gate or the state file, and says so in the plan. `testing-before-implementation` doesn't apply there, because Claude can't run your project's tests.

Cloud sessions on claude.ai/code load the plugin only when it is enabled for your claude.ai account: add the marketplace `nerymurillohnd/the-claude-factory` in **Customize** → **Plugins**. Installs from `/plugin` and repository settings don't reach cloud sessions.

**Platforms:** macOS and Linux.

## 🚧 Limitations

- Windows isn't supported.
- The skills are meant for interactive sessions. In scheduled tasks and `/loop`, Claude Code asks before it runs a skill that declares hooks or `allowed-tools`. To run the planning skill unattended, add `Skill(work-lifecycle:planning-before-execution)` to `permissions.allow` in your settings. An unattended run skips plan mode, lists each unanswered question with a recommended answer, and executes nothing that needs your authorization.
- After `--resume` or `--continue`, or after a cleared context, the plan gate isn't registered until the planning skill is invoked again. Every plan's handoff tells Claude to invoke it before Task 1 and after any resume or clear.
- The plan gate only checks that evidence is recorded. For high-stakes plans, `plan-verifier` re-runs the checks and reviews the evidence.
- The gate does nothing without a state file whose status is `executing`. It stops blocking after 3 continuations in a row without progress, and doesn't block while background tasks run.
- Plan mode can be weaker than it looks: in interactive terminal sessions where bypass permissions is available, it doesn't block edits. The skill treats read-only as its own rule.
- One option of the plan approval menu starts auto mode, or bypass permissions when it's enabled, and stops asking before push, deploy and similar actions. Choose manual approval unless your `permissions.ask` rules cover those actions.
- `/goal` holds at most 4,000 characters, its evaluator reads only the conversation, and only you can type it. It is unavailable in Claude and when hooks are disabled.
- `testing-before-implementation` is for code that can be tested. It isn't for configuration-only edits, documentation, visual styling, or adding tests to existing code without a behavior change.
- The testing skill keeps existing tests unchanged. When one looks wrong, it reports it to you with the evidence instead of editing it.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/work-lifecycle:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Claude keeps telling me tasks have no recorded evidence and won't stop.</b></summary>

That is the plan gate. It blocks while an executing plan has a task without evidence. Let Claude run each task's check and record its output. If Claude must stop to ask you something, it sets the state file's `status` to `awaiting-authorization` first. After 3 continuations in a row without progress, the gate lets Claude stop and says which tasks are still pending.

</details>

<details>
<summary><b>I see a hook error notice from the plan gate, and Claude stops without recording evidence.</b></summary>

`python3` is missing, older than 3.12, or not on your `PATH`. The gate can't start, so it lets Claude stop. Install Python 3.12 or later from [python3](#-python3) and check it:

```bash
python3 --version
```

</details>

<details>
<summary><b>I resumed a session and the plan gate isn't running.</b></summary>

A resumed or cleared session doesn't register the gate again until you invoke the planning skill. Ask Claude to invoke it, then run `/hooks` and confirm that a Stop hook running `plan-gate.py` is listed. If it isn't, completion rests on Claude's final report.

</details>

<details>
<summary><b>Does the plugin add files to my repository?</b></summary>

No. It writes `.work-lifecycle/` with its own `.gitignore` that holds `*`, so git ignores everything in it. Plans, tests and code you ask for are yours to commit as you choose; the plugin never pushes.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Skills](https://code.claude.com/docs/en/skills), [subagents](https://code.claude.com/docs/en/sub-agents) and [hooks](https://code.claude.com/docs/en/hooks) in Claude Code

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=work-lifecycle) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=work-lifecycle) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=work-lifecycle)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
