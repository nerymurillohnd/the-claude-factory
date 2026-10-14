<div align="center">

# 🔎 Agent Context Audit

<p><strong>Audits everything Claude Code and Codex load as context in a project, read-only and in parallel, and writes one evidence-backed report of false, stale, duplicated, conflicting and misplaced instructions, from a session, a terminal or a schedule.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fagent-context-audit%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Testing%20%26%20Quality-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.300-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — the audit runs `claude` and Python on your computer and reads your local Claude Code and Codex configuration, which the Claude app (chat or Cowork) can't reach. Install it in Claude Code.

> [!TIP]
> **TL;DR** — Type `/agent-context-audit:audit` and get one report that proves every instruction file your agents load was read line by line, and lists each instruction that is wrong, outdated, duplicated, contradictory, never loaded or in the wrong place, with the exact lines, the evidence and a proposed fix. Nothing in your project changes.

## ✨ Why use it

Your agents follow whatever their instruction files say, including the line that names a script you renamed last month, the rule whose paths match no file, and the two files that tell them opposite things.

- **See what your agents really load** — every CLAUDE.md in the chain, its imports, rules and their paths, auto memory, subagents, output styles, settings, hooks, permissions, MCP servers, AGENTS.md files and Codex config, each with how and when it loads (always, for some paths, on demand, cut off by a size limit, shadowed, or never).
- **Findings you can check** — every finding quotes the exact lines and names what it conflicts with: another file and line, a file in your repository, an official doc, or a documented default. A finding without that proof is rejected before it reaches the report.
- **Proof of a complete read** — the report shows, file by file, that every line was read. If anything was skipped, a worker failed or a file changed during the run, the report says *partial* and why. It never calls a partial audit complete.
- **Safe to run anywhere** — the auditors can only read copies of your files, with secrets masked, in sessions that load none of your settings, hooks, plugins or memory. Before and after hashes prove no audited file changed, and your git state stays untouched.
- **Track it over time** — finding IDs stay the same between runs, so each report says what is new, resolved, back again or still open. Run it on a schedule and get a note in your next session when a new report is ready.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `agent-context-audit:audit` | Starts an audit of the project, waits for it, and walks you through the report; `latest` shows the newest report | `/agent-context-audit:audit` (you start it; Claude never starts an audit on its own) |
| 🪝 Hook | `SessionStart` | Says once, at the start of a session, that a new report exists, for example after a scheduled run | Automatically at session start; turn it off with the `session_notice` option |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.300 or later, signed in — check with `claude --version` |
| **Operating system** | macOS, Linux, or Windows through WSL. Native Windows is not supported |
| **Python** | 3.9 or later, as `python3` on your `PATH` (standard library only, nothing to install) |
| **Git** | Recommended: the audit records your git state before and after to prove it changed nothing. Folders that aren't git repositories work too |
| **Codex CLI** | Optional. Codex files are audited whenever they exist; with the CLI installed, the report also names its version |
| **Accounts / API keys** | None beyond your Claude Code sign-in. Each audit runs several `claude -p` sessions on your account: on a subscription it counts toward your plan's usage limits, with an API key it is billed |
| **Surfaces** | See [Compatibility](#-compatibility) |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install agent-context-audit --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install agent-context-audit@the-claude-factory
```

Pick where it is enabled with `--scope`:

| Scope | Command | Enabled for |
| :-- | :-- | :-- |
| User (default) | `claude plugin install agent-context-audit@the-claude-factory` | You, in every project on this machine |
| Project | add `--scope project` | Everyone working in this repository; each collaborator still installs it once on their own machine |
| Local | add `--scope local` | You, in this repository only |

The audit works the same at every scope. Its own enablement entry in your settings is never reported as a problem.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install agent-context-audit --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install agent-context-audit@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

### Audit the project you're in

```text
/agent-context-audit:audit
```

**Result:** Claude starts the audit in the background and you can keep working. A small project takes a few minutes; a large one with many instruction files can take up to an hour. When it ends, Claude tells you the status, the findings by severity, the executive summary and each high-severity finding (file, lines, what is wrong, what it conflicts with, the proposed fix), then offers to go through the rest. The full report is in `.claude/agent-context-audit/<run>/report.md`, a folder the audit keeps out of git on its own.

### Review the newest report

```text
/agent-context-audit:audit latest
```

**Result:** Claude reads the newest report and presents it the same way, without running a new audit.

### Check claims about other tools on the web

```text
/agent-context-audit:audit --verify-online
```

**Result:** some instructions make claims nothing in your repository can settle, such as "don't upgrade X past 5.2". The audit lists them apart as *external claims*. With `--verify-online`, a verifier checks each one on GitHub, the package registries and the Claude Code and Codex docs, and the report gives each a verdict with its sources. Without it, Claude offers to check them in your session, with your own permissions.

### Ask for more

```text
/agent-context-audit:audit --repo ~/code/api --repo ~/code/web --max-budget-usd 2
```

**Result:** both repositories are audited one after the other, with a spending cap per worker session. Every option is listed under [Configuration](#️-configuration).

### Run it from a terminal

The skill runs a script inside the installed plugin. To run it from a terminal or a scheduler, save this launcher as `~/.local/bin/agent-context-audit` and make it executable (`chmod +x ~/.local/bin/agent-context-audit`). It finds the installed copy each time, so it keeps working after updates.

```sh
#!/bin/sh
# Runs the installed agent-context-audit plugin's audit script.
root=$(claude plugin list --json | python3 -c '
import json, sys
for plugin in json.load(sys.stdin):
    if plugin.get("id", "").startswith("agent-context-audit@") and plugin.get("enabled"):
        print(plugin.get("installPath") or plugin.get("readFromFolder") or "")
        break
')
if [ -z "$root" ]; then
  echo "agent-context-audit: the plugin is not installed and enabled here" >&2
  exit 4
fi
exec "$root/skills/audit/scripts/agent_context_audit.py" "$@"
```

Then, from inside a repository:

```bash
agent-context-audit run
```

It prints the status, the finding counts, the report path and a `claude-cli://` link that opens the repository in Claude Code with `/agent-context-audit:audit latest` ready to send. `agent-context-audit latest` shows the newest report, and `--json` prints the status as JSON.

| Exit code | Meaning |
| :-- | :-- |
| `0` | Complete, no findings |
| `1` | Complete, with findings |
| `2` | Partial: something was not covered; the report says what |
| `3` | Failure: no valid report was written |
| `4` | Couldn't start: a requirement is missing, or a usage error |

Add `--exit-zero` when a caller treats any non-zero exit as a crash; the status still prints.

### Run it on a schedule

A scheduled audit is the same terminal command. Pass `--mode scheduled` so the report records how it ran, and the next Claude Code session you open in that repository says a new report is ready. Each recipe below runs every Monday at 07:00; replace `/path/to/repo` with your repository and put the folders of `command -v claude` and `command -v python3` in `PATH`.

<details>
<summary><b>🍎 macOS: launchd</b></summary>

Save as `~/Library/LaunchAgents/local.agent-context-audit.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>local.agent-context-audit</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/sh</string>
    <string>-c</string>
    <string>cd /path/to/repo &amp;&amp; "$HOME/.local/bin/agent-context-audit" run --mode scheduled</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string>
  </dict>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key>
    <integer>1</integer>
    <key>Hour</key>
    <integer>7</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>/tmp/agent-context-audit.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/agent-context-audit.log</string>
</dict>
</plist>
```

Load it, and remove it when you no longer want it:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.agent-context-audit.plist
```

```bash
launchctl bootout gui/$(id -u)/local.agent-context-audit
```

launchd runs a missed job when your Mac wakes up.

</details>

<details>
<summary><b>🐧 Linux and WSL: systemd user timer</b></summary>

Save as `~/.config/systemd/user/agent-context-audit.service`:

```ini
[Unit]
Description=Agent Context Audit

[Service]
Type=oneshot
WorkingDirectory=/path/to/repo
Environment=PATH=/usr/local/bin:/usr/bin:/bin:%h/.local/bin
ExecStart=%h/.local/bin/agent-context-audit run --mode scheduled
```

And as `~/.config/systemd/user/agent-context-audit.timer`:

```ini
[Unit]
Description=Weekly Agent Context Audit

[Timer]
OnCalendar=Mon *-*-* 07:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Turn it on:

```bash
systemctl --user daemon-reload && systemctl --user enable --now agent-context-audit.timer
```

</details>

<details>
<summary><b>⏰ cron (macOS, Linux and WSL)</b></summary>

Run `crontab -e` and add these lines:

```text
PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin
0 7 * * 1 cd /path/to/repo && "$HOME/.local/bin/agent-context-audit" run --mode scheduled >> "$HOME/agent-context-audit.log" 2>&1
```

</details>

<details>
<summary><b>🖥️ Claude Code Desktop: scheduled task</b></summary>

1. In the **Code** tab, click **Routines**, then **New routine**, and choose **Local**.
2. **Name**: `agent-context-audit`. **Instructions**: ``Run `~/.local/bin/agent-context-audit run --mode scheduled --exit-zero` with the Bash tool, wait for it to finish, and tell me the status and the report path it prints.``
3. Pick the repository as the working folder, and a **Weekly** schedule.
4. Click **Run now** once and choose to always allow the command, so later runs don't stop for approval.

Desktop tasks run only while the app is open and your computer is awake.

</details>

> [!IMPORTANT]
> A scheduled job signs in to Claude the way your terminal does. If it reports an authentication error, create a token with `claude setup-token`, store it in a file only you can read, and set `CLAUDE_CODE_OAUTH_TOKEN` from that file in the job. The plugin never installs a schedule for you.

## ⚙️ Configuration

| Option | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `session_notice` | boolean | `true` | At session start, say once when a new report exists. Set it in `/plugin` → **Installed** → **Agent Context Audit** → **Configure options**, or in `/config` |

Command-line options (the skill passes the ones you ask for):

| Option | Default | What it does |
| :-- | :-- | :-- |
| `--repo PATH` | the current folder | Repository to audit; repeat it for several |
| `--out DIR` | `<repo>/.claude/agent-context-audit` | Write reports under `DIR/<project>/` instead of inside the repository |
| `--mode MODE` | `terminal` | `interactive`, `terminal` or `scheduled`, recorded in the report |
| `--json` | off | Print the status as JSON |
| `--exit-zero` | off | Always exit 0 after printing the status |
| `--verify-online` | off | Check external claims on the web (see [Privacy and network](#-privacy-and-network)) |
| `--online-domain DOMAIN` | none | Allow one more website for `--verify-online`; repeatable |
| `--offline` | off | Skip the check of the bundled docs knowledge against the live docs |
| `--max-budget-usd X` | none | Spending cap for each worker session, at API list price |
| `--auditor-model`, `--reconciler-model` | `sonnet`, `opus` | Models for the auditors and for the reviewer that reconciles their findings |
| `--auditor-effort`, `--reconciler-effort` | `high` | Effort level of each |
| `--concurrency N` | `4` | Auditors that run at the same time |
| `--worker-timeout S` | `1800` | Seconds before a worker session is stopped |
| `--retries N` | `1` | Retries for a worker that fails or misses lines |
| `--challenge-rounds N` | `1` | Rounds of challenge on disputed findings (`1` or `2`) |

Environment variables:

| Variable | What it does |
| :-- | :-- |
| `AGENT_CONTEXT_AUDIT_REPORT_DIR` | The same as `--out` for every run. The session note finds these reports when your Claude Code sessions have the variable too |
| `AGENT_CONTEXT_AUDIT_CLAUDE` | Path of the `claude` executable to use, when it isn't the one on `PATH` |

## 🔒 Privacy and network

- **What it reads**: the instruction and configuration files listed under [Why use it](#-why-use-it), plus your repository's package scripts, build targets, CI steps and tool configs as evidence. It never reads `.env` files, private keys or credential files.
- **What leaves your computer**: copies of the audited files go to Claude through your own `claude -p` sessions, like any request you make in Claude Code. Secrets in those copies, such as API keys, tokens, passwords in URLs and private-key blocks, are masked first. The copies are deleted when the run ends; the report keeps only the lines each finding quotes.
- **Web access**: unless you pass `--offline`, the audit downloads a fixed list of public Claude Code and Codex docs pages over HTTPS to check that its bundled knowledge is current. Only with `--verify-online` do the verifier sessions fetch pages, and only from GitHub, the npm, PyPI, crates.io, Go, RubyGems, Packagist and NuGet registries, the Claude and Anthropic docs and the OpenAI developer docs, plus any `--online-domain` you add. They see only the external claims, with secrets masked, and put nothing in a URL but the name of the tool or package a claim is about.
- **What it changes**: nothing in your project except its own report folder. The auditor sessions have read-only tools, no hooks, no MCP servers, no memory and none of your settings or plugins.

## 🔄 Updating

```bash
claude plugin update agent-context-audit@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Agent Context Audit** → **Update now**. Then run `/reload-plugins`. The terminal launcher picks up the new version on its own.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall agent-context-audit@the-claude-factory
```

Installed with `--scope project` or `--scope local`? Add the same `--scope` here too.

In a session: `/plugin` → **Installed** → **Agent Context Audit** → **Uninstall**. Your reports stay in `.claude/agent-context-audit/`; delete that folder when you no longer need them, and remove any schedule you added.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads, but the audit needs `claude` and Python on your computer |
| 🪝 Hooks | ✅ | ⚠️ in Cowork sessions, but there are no local reports to announce |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/agent-context-audit:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>What does an audit cost?</b></summary>

It depends on how much your agents load. The audit runs one auditor session per group of files (Sonnet by default), one reviewer session (Opus by default) and, when findings are disputed, a short challenge round. The report ends with the time, tokens and cost of every session. On a subscription the cost figures are API-equivalent estimates and the run counts toward your plan's usage limits. Use `--max-budget-usd` to cap each session, or `--auditor-model haiku` for a cheaper first pass.

</details>

<details>
<summary><b>The report says <i>partial</i>. What happened?</b></summary>

The report's **Coverage** section says which file or group wasn't fully covered and why: a worker session failed, timed out or missed lines, its output didn't pass validation, or a file changed while the audit ran. The findings shown are valid, but the list isn't complete. Run the audit again; if the same group keeps failing, raise `--worker-timeout` or check the error the report quotes.

</details>

<details>
<summary><b>How is this different from <code>/doctor prompt-audit</code>?</b></summary>

`/doctor prompt-audit` (Claude Code v2.1.283+) reviews your CLAUDE.md, AGENTS.md, rules, skills, commands, subagents and output styles inside your session and proposes edits. This audit also covers settings, hooks, permissions, MCP servers, imports, auto memory and Codex config; proves every line was read; validates each finding against your files and the official docs; runs from a terminal or a schedule; and tracks findings between runs. It leaves skills and commands out. The two work well together.

</details>

<details>
<summary><b>Why isn't a skill or a plugin's own file in the report?</b></summary>

Skills, commands and saved workflows are out of scope; the report lists how many it skipped. Files that come from installed plugins or from your organization's managed settings can't be changed by you, so they are used only as evidence.

</details>

<details>
<summary><b>Will it fix the problems it finds?</b></summary>

No. Every finding has a proposed disposition (keep, remove, merge, move, revise or investigate), with replacement text where it helps, and nothing is applied. Ask Claude to apply the fixes you agree with after you read the report.

</details>

<details>
<summary><b>It says the <code>claude</code> CLI is too old or not found.</b></summary>

Update Claude Code to v2.1.300 or later. If `claude` isn't on the `PATH` the audit sees, for example in a scheduled job, add its folder to `PATH` or set `AGENT_CONTEXT_AUDIT_CLAUDE` to its full path.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🧪 [Skill Diagnostics](../skill-diagnostics#readme) — audit your skills, which this audit leaves out
- 📖 [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- 📖 [Claude Code settings](https://code.claude.com/docs/en/settings)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=agent-context-audit) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=agent-context-audit) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=agent-context-audit)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
