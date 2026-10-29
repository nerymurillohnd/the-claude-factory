<div align="center">

# 🐙 GitHub Operations

<p><strong>One operating contract for GitHub work: takes pull requests from branch to merge, writes PRs, issues and discussions from the repository's templates, repairs CI, and audits and cleans up repositories, with hooks that keep its reviewer agents read-only.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fgithub-operations%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Development-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.295-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Prerequisites](#-prerequisites) •
[Install](#-installation) •
[Usage](#-usage) •
[Configuration](#-configuration) •
[Hooks](#-hooks) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it works on repositories on your computer through `git` and `gh`, which a chat conversation in the Claude app can't run. The plugin is built and tested for Claude Code only. In the Claude app you can still use its GitHub server once you connect it with your token: see [In the Claude app](#in-the-claude-app).

> [!TIP]
> **TL;DR** — Ask for any GitHub task in your own words, or type `/github-operations:github pr`, and Claude follows one set of rules for it: it takes your pull request all the way to merge and stops only to ask you before the merge, writes PRs, issues and discussions from your repository's templates, repairs failing CI, sets up templates and labels, and audits a whole repository before changing it only after you approve twice.

## ✨ Why use it

- **One set of rules for every GitHub task** — the `github` skill loads before Claude's first GitHub call and holds the rules every task follows: your approval for each push, PR, merge, deletion or settings change, evidence for every "done", your own signing setup, no force pushes, and your repository's own templates and conventions first.
- **A pull request that finishes itself** — Claude opens or picks up the PR, then loops: a read-only agent watches CI, runs and reviews and reports what failed and why, Claude fixes it, pushes and sends the agent again, until everything is green and no findings remain.
- **You keep the one decision that matters** — Claude asks for your approval right before the merge, for that exact PR and that exact commit. A new push voids the approval.
- **Reports you can act on** — failed jobs with the step, the log excerpt and the root cause, whether the same job also fails on the base branch, slow or stuck jobs, unresolved review findings, breaking changes and secrets in the diff, deprecation warnings and Dependabot alerts.
- **Writing that matches the repository** — PR titles, bodies and labels, issues, discussions and squash messages follow the repository's own templates, or the plugin's when it has none. A script checks each PR body before it is sent.
- **Nothing valuable gets lost in a cleanup** — the audit covers history, branches, worktrees, stashes, pull requests, issues, Actions, forks and every copy or link outside the repository that is still alive. You approve the recommendations, then the exact actions. A backup that was restore-tested comes first, and every deletion is checked against what is already safe.
- **Reviewer agents that cannot write** — hooks stop the plugin's two reviewer agents from running `git` or `gh` commands that change state, calling GitHub tools that write, or writing files in your project. Your own session is never blocked.
- **GitHub tools ready to use** — the GitHub MCP server comes with the plugin, so Claude reads GitHub through structured tools, and uses `git` and `gh` for what touches your clone.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `github-operations:github` | The operating contract for GitHub work: the rules, the tool choice and a route to the procedure for each task (pull request to merge, PR and merge-message writing, issues, discussions, CI repair, repository setup, audit and cleanup). It ships templates, issue and discussion forms, a label set and seven scripts | `/github-operations:github [pr\|issue\|discussion\|ci\|setup\|audit\|cleanup]`, or automatically before Claude's first GitHub call. An audit or cleanup starts only when you ask for one |
| 🤖 Agent | `github-operations:pr-tracker` | Waits for a PR's checks to finish, then reports failures and their root cause, unresolved reviews, breaking changes and secrets in the diff, warnings and security alerts to Claude | Launched by the skill on every monitoring cycle of a pull request |
| 🤖 Agent | `github-operations:repo-auditor` | Runs the read-only part of a repository audit (intake, local Git, history, GitHub, links) and writes its findings and coverage to a scratch folder | Launched by the skill at the start of an audit or cleanup |
| 🪝 Hooks | four handlers | Deny the two agents above their writes, name the skill on a session's first GitHub call, and restore a pull request or cleanup run after a compaction. See [Hooks](#-hooks) | Run by Claude Code on the tool calls and events listed in [Hooks](#-hooks) |
| 🔌 MCP server | `github` | GitHub's remote MCP server with every toolset and early-access mode: pull requests, issues, Actions, security alerts and more. See [GitHub MCP tools](../../docs/github-mcp-tools.md) | Tools appear as `mcp__plugin_github-operations_github__*` |

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.295 | `claude --version` |
| git, on your `PATH` (on Windows, Git for Windows) | — | `git --version` |
| GitHub CLI (`gh`), signed in | — | `gh auth status` |
| GitHub personal access token | — | `/mcp` lists `plugin:github-operations:github` as connected |
| Python 3, on your `PATH` as `python3` | 3.12 | `python3 --version` |
| uv, only to check issue forms, discussion forms and Dependabot files | — | `uv --version` |

`gh` creates and merges pull requests, reads run logs, reruns jobs, enables auto-merge and deletes branches, and is the fallback when a GitHub MCP tool is missing. `python3` runs the hooks and the skill's Python scripts; without it, the hooks deny the plugin's two reviewer agents their `git`, `gh`, GitHub tool and file calls, and your own session is never blocked. uv runs those checks, which download `check-jsonschema` and `ruamel.yaml` from PyPI on their first run.

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

### 🔀 git

<details>
<summary>🍺 <b>Homebrew</b> — macOS</summary>

```bash
brew install git
```

</details>
<details>
<summary>🛠️ <b>Xcode Command Line Tools</b> — macOS</summary>

```bash
xcode-select --install
```

</details>
<details>
<summary>🚢 <b>MacPorts</b> — macOS</summary>

```bash
sudo port install git
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt-get install git
```

</details>
<details>
<summary>📦 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install git
```

</details>
<details>
<summary>📦 <b>pacman</b> — Arch Linux</summary>

```bash
sudo pacman -S git
```

</details>
<details>
<summary>📦 <b>zypper</b> — openSUSE</summary>

```bash
sudo zypper install git
```

</details>
<details>
<summary>🪟 <b>Git for Windows (winget)</b> — Windows</summary>

```bash
winget install --id Git.Git -e --source winget
```

</details>

### 🐙 GitHub CLI

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install gh
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
	&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
	&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
	&& sudo apt update \
	&& sudo apt install gh -y
```

</details>
<details>
<summary>📦 <b>dnf5</b> — Fedora, RHEL</summary>

```bash
sudo dnf install dnf5-plugins
sudo dnf config-manager addrepo --from-repofile=https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh
```

</details>
<details>
<summary>📦 <b>dnf4</b> — Fedora, RHEL</summary>

```bash
sudo dnf install 'dnf-command(config-manager)'
sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh
```

</details>
<details>
<summary>📦 <b>zypper</b> — openSUSE, SUSE</summary>

```bash
sudo zypper addrepo https://cli.github.com/packages/rpm/gh-cli.repo
sudo zypper ref
sudo zypper install gh
```

</details>
<details>
<summary>🪟 <b>winget</b> — Windows</summary>

```bash
winget install --id GitHub.cli --source winget
```

</details>

Then sign in:

```bash
gh auth login
```

### 🔑 GitHub token

1. Create a [fine-grained personal access token](https://github.com/settings/personal-access-tokens/new) for the repositories you work in, with only the permissions you want Claude to have.
2. Give it to Claude Code as [Configuration](#-configuration) shows. Claude Code keeps it in your system's secure credential store.

Without the token the GitHub MCP server doesn't start, and Claude uses `gh`.

### 🐍 Python 3.12 or later

Your system may already have it: check with `python3 --version`. An older release's package manager can install a version below 3.12; then use the [official installers](https://www.python.org/downloads/) or uv.

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install python
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt-get install python3
```

</details>
<details>
<summary>📦 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install python3
```

</details>
<details>
<summary>⚡ <b>uv</b> — any platform, once uv is installed</summary>

```bash
uv python install --default
```

</details>

### ⚡ uv

Needed only when Claude checks issue forms, discussion forms or a Dependabot file. See [installing uv](https://docs.astral.sh/uv/getting-started/installation/).

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install uv
```

</details>
<details>
<summary>📜 <b>Standalone installer</b> — macOS, Linux</summary>

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

</details>

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install github-operations@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install github-operations --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install github-operations@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install github-operations@the-claude-factory
```

### Coming from Git Hygiene?

Git Hygiene is now part of this plugin and no longer exists on its own. The marketplace renames it, so an existing install moves to GitHub Operations by itself. The command changed: type `/github-operations:github cleanup` where you used to type `/git-hygiene:cleanup`.

### Coming from 0.4.x?

The two skills became one, `github`, and their commands are gone:

| You typed | Type now |
| :-- | :-- |
| `/github-operations:auto-pr-lifecycle` | `/github-operations:github pr` |
| `/github-operations:git-cleanup` | `/github-operations:github cleanup` (or `audit`) |

The pull request loop and the cleanup work as before, with two changes: Claude now creates and merges pull requests with `gh`, and the audit's read-only steps run in the new `repo-auditor` agent. The plugin also ships hooks, which need `python3` 3.12 or later: see [Hooks](#-hooks).

## 🚀 Usage

Ask in your own words, such as "open a PR for this", "why did the workflow fail" or "file a bug for this crash". Claude loads the `github` skill before its first GitHub call and picks the procedure from what you asked. To name the task yourself, type the skill with a mode and an optional target (a number, a URL or a path):

| Mode | What Claude does |
| :-- | :-- |
| `pr` | Takes a pull request from your branch to merge (below) |
| `issue` | Writes an issue in the layout of the repository's forms, triages issues, or marks a duplicate |
| `discussion` | Starts a discussion in the right category, or answers one |
| `ci` | Finds the workflows that fail, hang or stopped running on the default branch, fixes their cause and lands the fix through a pull request |
| `setup` | Adds what the repository lacks: PR templates, issue and discussion forms, Dependabot and `CODEOWNERS` through one pull request; missing labels and the default merge message as repository settings, each after you approve. Files the repository already has are never overwritten |
| `audit`, `cleanup` | Audits the repository, then cleans it up only after you approve twice (below). Claude starts it only when you ask for it |

Asking to fix an issue ("fix issue 17") ends in a pull request that resolves it, opened after you approve the push and the PR. Asking only to commit, or to commit and push, never opens a pull request.

### Take a pull request to merge

```text
/github-operations:github pr
```

You can also just say "open a PR for this", "get this PR merged" or "babysit PR 42". **Result:** Claude validates and pushes your work, opens the PR with a title, body and labels that follow your repository's templates, and starts the loop. While checks run, nothing interrupts you. When something fails, Claude reads the cause, fixes it, pushes and checks again. When everything is green and every review thread is answered, it stops with one question:

```text
PR #42 "Add invoice export" — head 4675bb2, squash merge into main.
All 9 checks pass, 0 unresolved threads, 1 non-blocking deprecation warning.
Merge this PR at this commit?
```

Answer yes and Claude merges, deletes the branch and syncs your local `main`. Say no or not yet and it stops there, with nothing merged.

### Clean up a repository

```text
/github-operations:github cleanup
```

**Result:** Claude audits the repository from its first commit to today, read-only, and writes down everything it finds: branches and whether each one's work is already safe, worktrees, stashes, history, large files and secret-like file names, open and stale pull requests, issues and discussions, failed workflows nobody re-ran, forks, and every clone, mirror, registry entry, scheduled job or tunnel on your machine and on GitHub that still points at the repository. Anything it cannot see is listed as not checked, with the reason.

Then it stops twice:

1. **Report and recommendations.** A plain-language report with numbered findings and recommendations (`R-1`, `R-2`, ...). You approve by ID; "clean it up" approves nothing.
2. **Plan.** For the IDs you approved, a numbered plan of exact actions, like this:

```text
A-01  prep           Back up every ref, stash and uncommitted file at risk to ~/repo-cleanup-backups/my-repo-2026-10-14
A-02  integrate      Merge feat/invoices into main (clean merge preview, 3 exclusive commits)
A-03  publish        Push main to origin (a plain push, never a force-push)
A-04  local-delete   Delete local branch feat/old-login (content already in main; patch-equivalent)
A-05  local-delete   Remove the worktree ../wt-hotfix (clean; branch merged)
A-06  remote-delete  Delete origin/feat/old-login (no open pull request, you are the only author)
```

Approve the whole plan, tell Claude which IDs to run, or stop with the audit only. The backup (A-01) always comes first and is part of every approval. Claude runs the actions in order, checks each one before it runs, and finishes with fresh read-only proof and a results report. If the audit finds something that needs a refactor, a bisect or a fix, it goes into the same report and plan.

Pass an absolute path to clean another repository:

```text
/github-operations:github cleanup /Users/ada/code/other-repo
```

## 🔧 Configuration

The plugin has one option, your GitHub token.

| Option | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `github_token` | string, sensitive, required | none | The token the bundled GitHub MCP server sends as `Authorization: Bearer`. Claude Code keeps it in your system's secure credential store, the same place it keeps your Claude Code sign-in, never in `settings.json`, and never shows it again once saved |

**Step 1. Create a token.** Make a [fine-grained personal access token](https://github.com/settings/personal-access-tokens/new) for the repositories you work in, with only the permissions you want Claude to have.

**Step 2. Give it to Claude Code.** Pick one:

| Where | How |
| :-- | :-- |
| In a session | Installing with `/plugin install` opens **Configure GitHub Operations** right away: paste the token, then choose **Save configuration**. To set or change it later, run `/plugin configure github-operations@the-claude-factory`, or open `/plugin` → **Installed** → **GitHub Operations** → **Configure options**. Claude Code reloads the plugin as soon as you save |
| In your shell | `claude plugin install` doesn't ask; it tells you the option is not set yet. Run `claude plugin configure github-operations@the-claude-factory --values-stdin`, paste `{"github_token": "<your token>"}` and press `Ctrl+D`, then restart Claude Code. The token stays out of your shell history |
| Added in the Claude app | Claude Code loads a plugin you turned on in claude.ai as `github-operations@synced`, and as of v2.1.302 it doesn't ask for that copy's token, so `/plugin` → **Installed** lists `github` under **Needs attention** as `failed to load`. Run `/plugin configure github-operations@synced`, paste the token and save, then run `/reload-plugins` (or `/reload-plugins --force` if it asks). If you also installed the plugin from the marketplace, Claude Code loads that copy instead, so set the token there |

> [!WARNING]
> In Claude Code v2.1.302 the **Configure** dialog shows the token while you paste it. Paste it when nobody can see your screen, or use the shell form.

**Step 3. Check it.** Run `/mcp` and look for `plugin:github-operations:github` marked as connected.

The option isn't listed in `/config`, because Claude Code keeps sensitive options out of it. Uninstalling the plugin from every scope it's installed in deletes the stored token.

### In the Claude app

The Claude app can't read the plugin's token option. When you turn the plugin on there, the app lists its GitHub server as a connector that is not added yet, and its form starts on an OAuth sign-in that asks for an OAuth app you would have to register with GitHub yourself. Connect it with your token instead, once. On a Team or Enterprise plan only an Owner (or, on Enterprise, a role with **Manage access to Libraries**) can add it; on the Free plan it counts as your one custom connector.

1. Go to **Customize** → **Plugins** → **GitHub Operations**, open the **Connectors** tab and choose **Connect** next to `github`.
2. Leave the name and URL as they are and go on to the next step.
3. Under **Authentication**, choose **No sign in**.
4. Under **Request headers**, add a header, pick `authorization` as its name and enter `Bearer <your token>` as the value, with one space after `Bearer`, for example `Bearer github_pat_11AB…`. Use a [fine-grained token](https://github.com/settings/personal-access-tokens/new), as in Step 1 above. Keep the `x-mcp-toolsets` and `x-mcp-insiders` headers the plugin already filled in, even though the form warns about custom header names.
5. Add the connector, then ask Claude in a new conversation: *"Use the GitHub get_me tool and tell me my username."*

The app stores this token encrypted with your claude.ai connectors, apart from the copy Claude Code keeps, so changing one doesn't change the other. It reaches GitHub from Anthropic's cloud, not from your computer, and Claude Code's deny rules don't apply there: limit what Claude can do in the app through the token's repositories and permissions. On a Team or Enterprise plan, everyone who uses the connector reaches GitHub with that same token.

### Coming from 0.1.x?

Version 0.1.x read the token from a `GITHUB_PAT` environment variable. From 0.2.0 the plugin reads only its own `github_token` option, so the GitHub server also connects when you start Claude Code from the desktop app or an editor instead of a terminal. Updating doesn't ask for the token or copy it: until you set it, the GitHub server is missing from `/mcp`, with no error.

If `GITHUB_PAT` is still set in your shell, move it in one step with [`jq`](https://jqlang.org/download/):

```bash
jq -n '{github_token: env.GITHUB_PAT}' | claude plugin configure github-operations@the-claude-factory --values-stdin
```

Then restart Claude Code. `jq` reads the variable itself, so the token never appears on a command line. You can remove `GITHUB_PAT` from your shell startup file once nothing else uses it.

### What the GitHub server includes

The plugin connects to GitHub's official remote MCP server at `https://api.githubcopilot.com/mcp/` with **every toolset** (`X-MCP-Toolsets: all`) and GitHub's **early-access mode** (`X-MCP-Insiders: true`). That covers pull requests, reviews, issues, Actions (including rerunning and cancelling runs), security alerts, projects, discussions, notifications and more, including the tools that create, merge and delete. The full list, tool by tool, with the ones that only read marked, is in [GitHub MCP tools](../../docs/github-mcp-tools.md).

> [!IMPORTANT]
> **Your token decides what works.** The server offers these tools, but GitHub only lets a tool do what your token is allowed to do, and it can hide tools your token can't use. Manage Claude's reach through the token's repositories and permissions.

### Reduce what Claude can use

| Way | What it does |
| :-- | :-- |
| Limit the token | Fewer repositories or permissions. GitHub enforces it whatever Claude asks for |
| Block tools in your settings | A deny rule such as `mcp__plugin_github-operations_github__delete_file` or `mcp__plugin_github-operations_github__delete_repository` removes that tool from Claude's context. Use `mcp__plugin_github-operations_github` for the whole server |
| Use your own server | Turn this one off in `/mcp` and add yours with headers such as `X-MCP-Readonly: true` or a shorter `X-MCP-Toolsets` list |

[GitHub MCP tools](../../docs/github-mcp-tools.md#️-reduce-what-claude-can-use) has the settings and the `.mcp.json` to copy. The pull request loop reads job logs and Dependabot alerts through the Actions and security tools; when you remove them, Claude reads that data through `gh` instead.

## 🪝 Hooks

The plugin's hooks run on your computer with your permissions, through `python3` 3.12 or later, and make no network calls. They deny only the plugin's two reviewer agents, `pr-tracker` and `repo-auditor`; your own session and every other agent are never blocked. A hook that fails lets the call go ahead.

| Event | Calls | What the hook does |
| :-- | :-- | :-- |
| Before a tool runs | Bash and PowerShell commands | For the two reviewer agents, denies `git` commands that change state (commit, push, merge, rebase, reset, checkout and the like), `gh` commands that write (create, edit, merge, close, delete, rerun, and `gh api` calls that are not reads), and any command it cannot parse that mentions `git` or `gh`. On a session's first `gh` or `git push`, adds a line that names the `github` skill |
| Before a tool runs | GitHub MCP tools, on any server whose name contains `github` or `GitHub` | For the two reviewer agents, denies the tools that write, such as `create_pull_request`, `merge_pull_request`, `issue_write` or `push_files`. On a session's first GitHub tool call, adds the same line |
| Before a tool runs | Write, Edit and NotebookEdit | For the two reviewer agents, denies a write to a file inside your project. The agents' own instructions already leave these tools out |
| After a compaction | Session start, `compact` | Gives Claude the pull request or cleanup run it was in (repository, PR, phase, head commit, approval, next step), so it resumes where it stopped |

**What they write.** The skill keeps one small JSON file for a pull request or cleanup run while it lasts, and the hooks keep one empty folder per session so the skill line comes only once, both in the plugin's data folder under `~/.claude/plugins/data/`. A session's folder is removed after seven days, at the first GitHub call of a later session. Uninstalling the plugin deletes the data folder.

**Without `python3` 3.12 or later**, the hooks deny the two reviewer agents every `git`, `gh`, GitHub tool and file write call, with a message that says to install it, and they don't restore a run after a compaction. Your own session is not affected.

### Limitations

- A hook is a barrier for Claude, not a security boundary. It never sees what you type in your own terminal, and it reads only the commands Claude sends through the Bash and PowerShell tools.
- Shell commands other than `git` and `gh`, such as `curl` to the GitHub API, are not inspected.
- A GitHub MCP server whose name contains neither `github` nor `GitHub` is not checked.
- Hooks don't run when your settings or your organization set `disableAllHooks`, or `allowManagedHooksOnly`.
- On Windows the hooks need WSL: Claude Code starts their launcher directly, and Windows can't run it without a shell.
- In the Claude app they run only in Cowork sessions: see [Compatibility](#-compatibility).

### Add hard limits yourself

The plugin can't ship permission rules. To block an action for every session and agent, whatever the hooks do, add `deny` or `ask` rules to your own `~/.claude/settings.json` or the project's `.claude/settings.json`, for example:

```json
{
  "permissions": {
    "deny": [
      "mcp__*__push_files",
      "mcp__*__create_or_update_file",
      "mcp__*__delete_file",
      "Bash(git push --force*)",
      "Bash(git push -f*)",
      "Bash(* --no-verify*)"
    ],
    "ask": ["Bash(gh pr merge *)", "mcp__*__merge_pull_request"]
  }
}
```

A deny rule on a tool name removes that tool from Claude's context. Bash rules match the command as written, so a reworded command can slip past them: see [Bash rule limits](https://code.claude.com/docs/en/permissions#bash-rule-limits).


## 🔄 Updating

```bash
claude plugin update github-operations@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update git and `gh` the way you installed them, for example with Homebrew:

```bash
brew upgrade git gh
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall github-operations@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall github-operations@the-claude-factory --scope project
```

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. That includes your stored GitHub token. The token itself stays valid on GitHub until you delete it there, and git and `gh` stay installed.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ they load, but they need `git`, `gh` and your repository on your computer, so use Claude Code |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |
| 🪝 Hooks | ✅ needs `python3` 3.12 or later; on Windows, WSL | ⚠️ in Cowork sessions, not in a chat conversation |
| 🔌 MCP server (remote) | ✅ needs your token, set as in [Configuration](#-configuration) | 🔗 connect it once with your token, as in [In the Claude app](#in-the-claude-app) |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/github-operations:` to see the `github` skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>The GitHub server is missing, failed or "needs authentication" in <code>/mcp</code>.</b></summary>

Look at the message, then fix the token. Until you do, the monitoring agent has no GitHub tools, so Claude reads GitHub through `gh` itself.

| What you see | Why | What to do |
| :-- | :-- | :-- |
| `plugin:github-operations:github` is missing from `/mcp`, with no error | The token is not set, or no longer saved: you skipped the dialog, installed from the shell, or just updated from 0.1.x | Set it as in [Configuration](#-configuration) |
| `claude.ai github` is listed in `/mcp` instead of `plugin:github-operations:github`, and GitHub tools still work | The same missing token. Claude Code then connects your claude.ai GitHub connector in the server's place, so nothing reports an error | Set the token as in [Configuration](#-configuration). Once it is set, the plugin's server connects and hides the connector, because both point at the same URL |
| `/plugin` lists `github` under **Needs attention** as `failed to load`, with `Plugin option "github_token" isn't set` | You turned the plugin on in claude.ai, and Claude Code doesn't ask for the token of that copy | Run `/plugin configure github-operations@synced`, as in [Configuration](#-configuration) |
| In the Claude app, the plugin's **Connectors** tab shows `github` as not added, or its form asks for an OAuth client | The app can't read the plugin's token option | Connect it with your token, as in [In the Claude app](#in-the-claude-app) |
| The server is marked failed, or `401 — token authentication failed` | The token is wrong or expired | Create a new token and set it again with **Configure options** |
| Some tools work and others don't | The token lacks a permission those tools need | Add the permission to the token |

</details>

<details>
<summary><b>Will Claude merge my PR without asking?</b></summary>

No. It always stops and asks before the merge, naming the PR, the commit, the merge method and any automatic deployment it knows about. Your approval covers that commit only: if anyone pushes again, Claude asks again. It never force-pushes, skips hooks or required checks, or uses admin rights to get around a rule.

</details>

<details>
<summary><b>Can the monitoring agent change anything on GitHub?</b></summary>

No. Its job is to read and report: Claude makes every comment, reply, rerun and merge. The agent gets every tool your session has except Write, Edit and NotebookEdit, and the plugin's [hooks](#-hooks) deny it the `git` and `gh` commands that change state and the GitHub tools that write, on any server whose name contains `github` or `GitHub`. The same holds for the `repo-auditor` agent. A hook is a barrier, not a security boundary: for a hard limit, add the deny rules in [Add hard limits yourself](#add-hard-limits-yourself), which apply to every agent too.

</details>

<details>
<summary><b>Which GitHub tools does the monitoring agent use?</b></summary>

The ones your session already has, whatever the server is called: this plugin's `github` server, a GitHub server you added yourself, or the GitHub connector of the Claude app. You don't need to rename or duplicate a server for the agent to see it.

</details>

<details>
<summary><b>How long will Claude wait for a slow pipeline?</b></summary>

The PR tracker waits for the checks to finish, for up to 30 minutes or the limit you set. When the limit ends with jobs still running, it reports what it knows and which jobs are still running, and Claude asks you whether to keep waiting, so it never hangs on a pipeline that takes too long.

</details>

<details>
<summary><b>What does the cleanup refuse to do, even if I approve?</b></summary>

It never runs `git clean -x`, never deletes a branch with `-D` unless you approve that exact action, and never force-pushes or rewrites published history as part of a bulk approval. A history rewrite (to remove a secret or a huge file) happens only when you ask for it by name, in a fresh mirror clone made from the backup, and its force push runs only as the exact command the plan showed you. Deploy keys, tokens, secrets, installed apps and collaborator access are reported, never changed.

</details>

<details>
<summary><b>Does the cleanup read my <code>.env</code> files?</b></summary>

No. Files that look like secrets (`.env`, keys, certificates, token and credential files) are listed by name only and are never opened or copied into the backup. A secret that was ever committed is reported as exposed, with the instruction to rotate it.

</details>

<details>
<summary><b>Does the cleanup install anything or write scripts?</b></summary>

It installs nothing and writes no scripts. Claude runs ordinary `git` and `gh` commands, plus the plugin's own scripts that classify branches, verify the backup and check the plan, from a scratch folder outside your repository, and removes it at the end. A command that is not available is reported as not checked.

</details>

<details>
<summary><b>Should I run the cleanup in bypass-permissions mode?</b></summary>

No. Use the default permission mode, so Claude Code asks you before each command that changes something. Approving the plan and approving a prompt are two separate checks.

</details>

<details>
<summary><b>Can I run them with <code>claude -p</code>?</b></summary>

Only the read-only cleanup audit is meant for it. The cleanup plan needs your approval and every command that changes anything needs your confirmation, and the pull request loop needs your approval before the merge. A headless run has nobody to give any of them, so Claude Code refuses them. Run both in an interactive session.

</details>

<details>
<summary><b>My remote is not on GitHub.</b></summary>

The cleanup of branches, worktrees, stashes and files works with any remote. Pull requests, repository visibility and branch protections come from GitHub; for other hosts they are reported as blocked and nothing that depends on them is touched. The pull request loop is GitHub only.

</details>

<details>
<summary><b>Where is the cleanup backup, and when is it deleted?</b></summary>

In a folder outside the repository that you choose in the plan. Claude never deletes it on its own: when the cleanup is verified it asks whether to keep or remove it, and removes it only after an explicit yes.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 🔁 [Project Maintainer](../project-maintainer#readme) — write down where a session stopped, including the repository state, before you start a cleanup

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=github-operations) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=github-operations) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=github-operations)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 🙏 Credits

This plugin ships none of GitHub's software. It connects Claude Code to the hosted remote server of the official [GitHub MCP Server](https://github.com/github/github-mcp-server) (MIT license, © GitHub). The URL forms, toolsets and tool names come from GitHub's documentation: the [remote server guide](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md) and the guide to [installing it in Claude applications](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-claude.md). We re-checked them against the live server, and if GitHub changes them, GitHub's documentation is the reference.

GitHub also publishes its own [agent plugin](https://github.com/github/github-mcp-server/tree/main/agent-plugin) for the same server, which declares only the server connection. This plugin adds the operating contract and its workflows around that server (pull requests, writing, CI repair, setup, audit and cleanup), with a token option, a choice of tool set and hooks for its agents.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by GitHub. *GitHub* is a trademark of GitHub, Inc.
