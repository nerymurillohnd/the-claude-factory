<div align="center">

# 🐙 GitHub Operations

<p><strong>Runs GitHub work through focused skills: takes pull requests from branch to merge with a tracker, a fixer and a finalizer agent, writes a repository's templates, forms, labels and Dependabot setup adapted to it, and audits and cleans up repositories, local and remote, behind a verified backup.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fgithub-operations%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Development-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.314-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Prerequisites](#-prerequisites) •
[Install](#-installation) •
[Usage](#-usage) •
[Configuration](#-configuration) •
[What it runs and sends](#-what-this-plugin-runs-and-sends) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it works on repositories on your computer through `git` and `gh`, which a chat conversation in the Claude app can't run. The plugin is built and tested for Claude Code only. In the Claude app you can still use GitHub's MCP server once you add it as a connector with your token: see [In the Claude app](#in-the-claude-app).

> [!TIP]
> **TL;DR** — Say "open a PR for this", "set up issue templates" or "clean up this repository". Claude takes the pull request to merge, asking you before every push and before the merge; writes your repository's own templates, forms and labels from tested models; or audits the whole repository and cleans up only what you approve, after a backup it has proven it can restore.

## ✨ Why use it

- **A pull request that finishes itself** — three agents share the work: one watches CI and reviews and finds each failure's root cause, one fixes the failures and review findings in your clone and commits them, and one verifies every fix, answers the review threads and resolves the ones bots opened. Claude checks each report against its evidence before acting on it.
- **You hold every push and the merge** — after each round of fixes, Claude shows you what failed, what changed and how it was checked, then asks: push, push without asking again on this pull request, or don't push. The merge waits for your approval of that exact pull request at that exact commit.
- **Reports you can act on** — failed jobs with the failing step, the first error and its root cause, whether the same job fails on the base branch, required checks, warnings, review threads with their links, breaking changes and secrets in the diff, and Dependabot alerts.
- **Templates written for your repository** — PR templates, issue and discussion forms, labels, Dependabot and `CODEOWNERS` are written from tested models but with your components, versions, environments, commands and labels. Your own files always win: Claude proposes changes to them and never overwrites them.
- **Nothing valuable gets lost in a cleanup** — the audit compares your clone with GitHub branch by branch and commit by commit, and covers worktrees, stashes, history, lost commits, pull requests, workflows, Dependabot, forks and every link outside the repository. You approve the recommendations, then the exact actions. A backup comes first, and Claude proves it restores before it changes anything.
- **Workflows that run Claude, checked against the action's real behavior** — Claude matches a failed or silent claude-code-action step against fourteen known failure patterns, and audits workflow files for shell injection, excess permissions, unpinned actions, unsafe `pull_request_target` designs and claude-code-action misconfiguration, with the exact patch for each finding. Action versions and model IDs are looked up when they are written, never copied from examples, which lag behind.
- **Each skill knows its place** — the PR lifecycle, the repository setup, the cleanup and the Actions work are separate skills. When you ask one for another's job, it hands you to the right one.
- **Works with GitHub's own MCP server** — add GitHub's official remote MCP server once, as [Prerequisites](#-github-mcp-server-recommended) shows, and Claude reads GitHub through its structured tools; without it, Claude does the same work through `gh`. `git` and `gh` handle what touches your clone.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `github-operations:auto-pr-lifecycle` | Takes a pull request from its current stage to merge with three agents, asking you before every push and before the merge | `/github-operations:auto-pr-lifecycle`, or when you ask to open, babysit, fix or merge a pull request |
| 🎯 Skill | `github-operations:cleanup-and-debug` | Audits a repository local and remote, plans the cleanup and debugging you approve, and runs it behind a verified backup | `/github-operations:cleanup-and-debug`, or when you ask to audit or clean up a repository. It asks before it starts |
| 🎯 Skill | `github-operations:github-files-setup` | Writes a repository's PR templates, issue and discussion forms, labels, Dependabot, `CODEOWNERS` and merge-message setting, adapted to it, and lands them through a pull request | `/github-operations:github-files-setup`, or when you ask to set up templates, forms or labels |
| 🎯 Skill | `github-operations:claude-github-actions` | Diagnoses a Claude step in GitHub Actions that failed, did nothing or posted nothing; audits and hardens workflow files with an exact patch per finding; and repairs failing CI on the default branch, asking before any rerun, workflow change or push | `/github-operations:claude-github-actions`, or when you ask why a Claude workflow did nothing, to audit a workflow, or to fix CI on the default branch |
| ⌨️ Command | `/github-operations:init-pr-lifecycle` | Picks up the current pull request at the stage it is in and runs the PR lifecycle from there | You type it |
| ⌨️ Command | `/github-operations:init-cleanup-and-debug` | Picks up a repository at its cleanup stage (not audited, audited, planned, approved, executed) and runs from there | You type it |
| 🤖 Agent | `github-operations:pr-lifecycle:pr-tracker` | Waits for a pull request's checks, then reports failures and their root cause, review threads, breaking changes, secrets in the diff, warnings and Dependabot alerts | Launched by the PR lifecycle after a pull request opens and after every push |
| 🤖 Agent | `github-operations:pr-lifecycle:pr-fixer` | Fixes the verified failures and review findings in your local clone, validates each fix and commits it. It never pushes | Launched by the PR lifecycle when findings need a fix |
| 🤖 Agent | `github-operations:pr-lifecycle:pr-finalizer` | Verifies each finding at the current head, replies to review threads, resolves the threads bots opened, and gives the merge verdict | Launched by the PR lifecycle once the checks pass |
| 🤖 Agent | `github-operations:repo-hygiene:health-diagnostics` | Audits one assigned part of a repository read-only and reports every item with its evidence | Launched by the cleanup, one or several at a time depending on the repository's size |

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.314 | `claude --version` |
| git, on your `PATH` (on Windows, Git for Windows) | — | `git --version` |
| GitHub CLI (`gh`), signed in | — | `gh auth status` |
| GitHub MCP server, recommended | — | `claude mcp get github` |
| Python 3, on your `PATH` as `python3`, only to compare labels when setting up a repository | 3.12 | `python3 --version` |
| uv, only to check issue forms, discussion forms and Dependabot files when setting up a repository | — | `uv --version` |

Claude Code 2.1.314 or later is required.

`gh` creates and merges pull requests, reads run logs, creates labels and is the fallback when a GitHub MCP tool is missing. The GitHub MCP server is optional: the plugin doesn't install it, and works through `gh` without it. `python3` runs the label comparison of the repository setup. uv runs the form and Dependabot checks of the same setup.

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

### 🔌 GitHub MCP server (recommended)

The plugin doesn't install an MCP server. With GitHub's official remote MCP server added to Claude Code, Claude reads GitHub through structured tools; without it, Claude does the same work through `gh`. You add the server once, and it serves every project.

**Step 1. Create a token.** Make a [fine-grained personal access token](https://github.com/settings/personal-access-tokens/new) for the repositories you work in, with only the permissions you want Claude to have. GitHub only lets a tool do what this token allows.

**Step 2. Add the server.** Run option A in your terminal, not inside a Claude Code session, with `<your token>` replaced by the token. If it fails, for example with `Invalid input`, which GitHub's guide reports on Windows, run option B instead. Both add the same server, named `github`, for you in every project (`--scope user`). If option A worked, skip option B: Claude Code refuses it with `MCP server github already exists in user config`.

Option A, the form GitHub's [installation guide](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-claude.md) gives for Claude Code 2.1.1 and later:

```bash
claude mcp add-json --scope user github '{"type":"http","url":"https://api.githubcopilot.com/mcp/","headers":{"Authorization":"Bearer <your token>","X-MCP-Toolsets":"all","X-MCP-Insiders":"true"}}'
```

Option B, the fallback when option A fails, with one flag per header:

```bash
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp/ \
  -H "Authorization: Bearer <your token>" \
  -H "X-MCP-Toolsets: all" \
  -H "X-MCP-Insiders: true"
```

Claude Code saves the server, token included, in `~/.claude.json` (on Windows, `%USERPROFILE%\.claude.json`), its file for your personal MCP servers. Keep that file private and never commit or share it.

Keep `github` in the server's name: the plugin's agents find the GitHub tools by searching for `github`.

**Keep the token out of `~/.claude.json` (optional).** Write `${GITHUB_PAT}` in place of the token, inside single quotes so your shell doesn't replace it, and set `GITHUB_PAT` to your token in the environment Claude Code starts from. Claude Code saves the reference and reads the variable each time it connects:

```bash
claude mcp add-json --scope user github '{"type":"http","url":"https://api.githubcopilot.com/mcp/","headers":{"Authorization":"Bearer ${GITHUB_PAT}","X-MCP-Toolsets":"all","X-MCP-Insiders":"true"}}'
```

```bash
claude mcp add --scope user --transport http github https://api.githubcopilot.com/mcp/ \
  -H 'Authorization: Bearer ${GITHUB_PAT}' \
  -H "X-MCP-Toolsets: all" \
  -H "X-MCP-Insiders: true"
```

> [!NOTE]
> Claude Code sees the variable only when it starts from a shell that sets it. Started from the desktop app, an editor or your system's app launcher, it may not have it, and the server then fails with `401`. If that happens, add the server with the token itself, as in Step 2.

**Step 3. Check it.** Run `claude mcp get github`, then `/mcp` in a session, and look for `github` marked as connected.

**Choose what the server offers.** The commands send two optional headers. Change them before you run the command:

| Header | In the commands | What it does | To change it |
| :-- | :-- | :-- | :-- |
| `X-MCP-Toolsets` | `all` | Every toolset: pull requests, reviews, issues, Actions, security alerts, projects, discussions, notifications and more, including the tools that create, merge and delete | Put a comma-separated list instead, such as `repos,issues,pull_requests,actions`. Remove the header to get GitHub's default toolsets. The toolset names are in GitHub's [remote server guide](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md). A misspelled name is ignored, with no error |
| `X-MCP-Insiders` | `true` | GitHub's early-access mode: new tools and changes before they reach everyone. Optional | Remove the header to use only GitHub's released tools |
| `X-MCP-Readonly` | not sent | Offers only the tools that read | Add `-H "X-MCP-Readonly: true"` (option B) or `"X-MCP-Readonly":"true"` (option A) |

The pull request loop uses the pull request, Actions and security tools when they are there, and `gh` when they are not. To change the token or the headers later, run `claude mcp remove --scope user github` and add the server again. To stop using it, run only the `remove`, and delete the token on GitHub.

The desktop app's Code tab reads the same `~/.claude.json`, so the server is there too. For the app's chat and Cowork, add it as a connector: see [In the Claude app](#in-the-claude-app).

### 🐍 Python 3.12 or later

Needed only when Claude compares your repository's labels during a setup. Your system may already have it: check with `python3 --version`. An older release's package manager can install a version below 3.12; then use the [official installers](https://www.python.org/downloads/) or uv.

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

Needed only when Claude checks issue forms, discussion forms or a Dependabot file during a setup. See [installing uv](https://docs.astral.sh/uv/getting-started/installation/).

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

Git Hygiene is now part of this plugin and no longer exists on its own. The marketplace renames it, so an existing install moves to GitHub Operations by itself. The cleanup is now the `cleanup-and-debug` skill: type `/github-operations:cleanup-and-debug` where you used to type `/git-hygiene:cleanup`.

### Coming from 0.5.x?

The single `github` skill became four skills:

| You typed | Type now |
| :-- | :-- |
| `/github-operations:github pr` | `/github-operations:auto-pr-lifecycle`, or `/github-operations:init-pr-lifecycle` to pick up a pull request where it stands |
| `/github-operations:github audit` or `cleanup` | `/github-operations:cleanup-and-debug`, or `/github-operations:init-cleanup-and-debug` |
| `/github-operations:github setup` | `/github-operations:github-files-setup` |
| `/github-operations:github ci` | `/github-operations:claude-github-actions` |
| `/github-operations:github issue` or `discussion` | Not part of this version |
| *"Fix issue #N"*, which ended in a pull request | Not part of this version |

What else changed:

- **Every push asks you first.** Fixes are made in your clone by the `pr-fixer` agent and pushed only after you approve them, or after you choose not to be asked again on that pull request.
- **Review threads people opened stay open** for their reviewer. Claude resolves only the threads bots and AI reviewers opened, once the fix is verified.
- **The `pr-tracker` and `repo-auditor` agents were replaced** by `pr-lifecycle:pr-tracker` and `repo-hygiene:health-diagnostics`.
- **The plugin no longer ships hooks.** The agents keep to their limits through their own instructions; see [What this plugin runs and sends](#-what-this-plugin-runs-and-sends).
- **Templates are written for your repository**, not copied as they are.

### Coming from 0.6.x?

The plugin no longer brings the GitHub MCP server or asks for a token. After you update, `plugin:github-operations:github` leaves `/mcp`, and Claude uses `gh` until you add GitHub's server yourself:

1. Create a new [fine-grained token](https://github.com/settings/personal-access-tokens/new). Claude Code never shows the token you saved in the plugin again, so you can't copy it.
2. Add the server as in [GitHub MCP server](#-github-mcp-server-recommended). It keeps every toolset and early-access mode, as before.
3. Delete the old token on GitHub.
4. Rename deny rules that name `mcp__plugin_github-operations_github__…` to `mcp__github__…`.

In the Claude app, a GitHub connector you already added keeps working. To add one, see [In the Claude app](#in-the-claude-app).

## 🚀 Usage

Ask in your own words. Claude picks the skill from what you asked, and when it loaded a skill on its own, it asks you before it starts. To pick it yourself, type the skill or one of the two commands.

### Take a pull request to merge

```text
/github-operations:auto-pr-lifecycle
```

You can also say "open a PR for this", "fix the PR's CI", "address the review comments" or "get PR 42 merged". To pick up an existing pull request at whatever stage it is in:

```text
/github-operations:init-pr-lifecycle 42
```

**Result:** when there is no pull request yet, Claude validates and commits your work, then asks before it pushes and before it opens the PR with your repository's template and labels. Then the loop runs:

1. **Track.** The tracker waits for the checks and reports what failed and why, every review thread, and the risks in the diff.
2. **Fix.** The fixer corrects the verified findings in your clone and commits each fix. It never pushes.
3. **Your push.** Claude shows you what was found, what was fixed and how it was validated, then asks:

```text
PR #42 "Add invoice export": 2 failures fixed in 2 commits (tests pass), 1 review finding fixed.
Push · Push without asking again on this pull request · Don't push
```

4. **Finalize.** Once the checks pass, the finalizer verifies each fix in the diff, replies to the review threads and resolves the ones bots opened.
5. **Your merge.** Claude stops with one question, naming the pull request, the commit, the merge method and the threads left open for people.

Asking only to commit, or to commit and push, never opens a pull request.

### Set up a repository's GitHub files

```text
/github-operations:github-files-setup
```

You can also say "add issue templates", "set up PR templates", "sync the labels" or "add Dependabot". **Result:** Claude reads your repository first (its README, contribution guide, manifests, CI, labels and recent issues and pull requests), then shows you which files it would write and why. After you agree, it writes them for your repository: dropdowns with your components and versions, PR checklists with your real test and lint commands, labels in your naming style, and a Dependabot entry for each package ecosystem it finds. It checks every form until it passes, asks before it creates a label or changes a repository setting, and opens one pull request with the whole setup. Files your repository already has are never overwritten: Claude shows you the change as a diff and asks.

### Audit and clean up a repository

```text
/github-operations:cleanup-and-debug
```

To pick up a cleanup at the stage it is in:

```text
/github-operations:init-cleanup-and-debug
```

**Result:** Claude audits the repository read-only, from its first commit to today: every branch and whether its work is already in the base, even after a squash merge; your clone compared with GitHub; worktrees, stashes, lost commits, large files and secrets ever committed; leftovers of interrupted merges and rebases; open and stale pull requests, failed or stuck workflows, failed Dependabot updates and forks; and every clone, mirror or scheduled job that still points at the repository. It asks before it looks outside the repository. Anything it cannot see is listed as blocked or not reachable, with the reason, never as empty.

Then it stops twice:

1. **Report.** Findings (`F-1`, `F-2`, …) and recommendations (`R-1`, `R-2`, …), each with its risk and whether it can be undone. You approve recommendations by ID; "clean it up" approves nothing.
2. **Plan.** For the recommendations you approved, the exact actions (`A-1`, `A-2`, …) with their commands, in a fixed order: backup first, then fixes, integration, a plain push, deletions, maintenance last. You approve actions by ID.

Before the first action, Claude bundles every ref outside the repository and proves the bundle restores. It runs only the approved actions, checks each one before it runs, stops an action and everything that depends on it when one fails, and ends with fresh proof and a results report. A fix found during the audit, such as a bug to bisect, is made on a new branch and lands through a pull request, never straight on your base branch.

## 🔧 Configuration

The plugin has no options. The GitHub MCP server is yours to add and configure: see [GitHub MCP server](#-github-mcp-server-recommended).

### Diagnose, audit or repair GitHub Actions workflows

Ask *"Why did the Claude review on PR 42 post nothing?"*, *"Audit our workflows"* or *"CI on main is broken"*. Claude reads the run's log and the workflow file at the commit it ran, matches them against the known failure patterns of `anthropics/claude-code-action`, and names the cause with the log lines that prove it. An audit lists each finding with its file and line, what triggers it, its impact and the exact patch. Claude changes a workflow only after you approve the patch, pins every action it writes to a full commit, and lands the change through a pull request. Writing a new workflow from scratch is not covered yet.

### In the Claude app

- **Desktop app, Code tab (local sessions):** it reads the same `~/.claude.json` as the terminal, so the server you added in [GitHub MCP server](#-github-mcp-server-recommended) is already there. Check it with `/mcp` in a Code tab session.
- **Chat and Cowork, in the desktop app or on claude.ai:** they don't read `~/.claude.json`. Add GitHub's server once as a custom connector. On a Team or Enterprise plan only an Owner (or, on Enterprise, a role that manages the organization's libraries) can add it; on the Free plan it counts as your one custom connector.

1. Go to **Customize** → **Connectors** and choose **Add custom connector**. On a Team or Enterprise plan, the Owner adds it under **Organization settings** → **Connectors** → **Add** → **Custom**, and members then choose **Connect**.
2. Name it `github` and enter this URL:

   ```text
   https://api.githubcopilot.com/mcp/
   ```

3. Under **Authentication**, choose **No sign-in**.
4. Under **Request headers**, add these headers. For `x-mcp-toolsets` and `x-mcp-insiders`, choose **Custom header** and type the name; keep them even if the form warns about custom header names.

   | Header | Value | |
   | :-- | :-- | :-- |
   | `authorization` | `Bearer <your token>`, with one space after `Bearer`, for example `Bearer github_pat_11AB…`. Use a [fine-grained token](https://github.com/settings/personal-access-tokens/new) | Required |
   | `x-mcp-toolsets` | `all`, or a comma-separated list from GitHub's [remote server guide](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md) | Optional. Without it, GitHub's default toolsets |
   | `x-mcp-insiders` | `true` | Optional. GitHub's early-access mode |

5. Choose **Add**, then ask Claude in a new conversation: *"Use the GitHub get_me tool and tell me my username."*

> [!IMPORTANT]
> Anthropic's [custom connector guide](https://claude.com/docs/connectors/custom) describes **Request headers** as a beta available to a limited set of organizations. If the dialog has no **Request headers** section, the app can't send your token to GitHub's server. You can't change a connector's headers after you add it: remove it and add it again.

The app keeps this token with your claude.ai connectors, apart from the copy in `~/.claude.json`, so changing one doesn't change the other. It reaches GitHub from Anthropic's cloud, not from your computer, and Claude Code's deny rules don't apply there: limit what Claude can do in the app through the token's repositories and permissions. On a Team or Enterprise plan, everyone who uses the connector reaches GitHub with that same token.

### What the GitHub server includes

With the commands in [GitHub MCP server](#-github-mcp-server-recommended), the server offers **every toolset** (`X-MCP-Toolsets: all`) and GitHub's **early-access mode** (`X-MCP-Insiders: true`). That covers pull requests, reviews, issues, Actions (including rerunning and cancelling runs), security alerts, projects, discussions, notifications and more, including the tools that create, merge and delete. The full list, tool by tool, with the ones that only read marked, is in [GitHub MCP tools](../../docs/github-mcp-tools.md).

> [!IMPORTANT]
> **Your token decides what works.** The server offers these tools, but GitHub only lets a tool do what your token is allowed to do, and it can hide tools your token can't use. Manage Claude's reach through the token's repositories and permissions.

### Reduce what Claude can use

| Way | What it does |
| :-- | :-- |
| Limit the token | Fewer repositories or permissions. GitHub enforces it whatever Claude asks for |
| Block tools in your settings | A deny rule such as `mcp__github__delete_file` or `mcp__github__delete_repository` removes that tool from Claude's context. Use `mcp__github` for the whole server. These names fit a server named `github`; for another name, use `mcp__<name>__…` |
| Change the headers | Remove the server and add it again with `X-MCP-Readonly: true` or a shorter `X-MCP-Toolsets` list |

[GitHub MCP tools](../../docs/github-mcp-tools.md#️-reduce-what-claude-can-use) has the settings to copy. The PR tracker reads job logs and Dependabot alerts through the Actions and security tools; when you remove them, it reads that data through `gh` instead.

## 🔍 What this plugin runs and sends

- **Hooks:** none.
- **MCP servers:** none. When you add GitHub's remote server yourself, as [GitHub MCP server](#-github-mcp-server-recommended) shows, the skills and agents use its tools.
- **Commands it runs:** `git` and `gh` in your repository, through Claude Code's Bash tool, so your permission settings and prompts apply to each one. The repository setup also runs its two scripts: a label comparison with `python3`, and a form check through `uv`.
- **Network:** `git` and `gh` reach GitHub and your remotes. The GitHub MCP server you add yourself sends your requests and token to `api.githubcopilot.com`. The form and Dependabot checks run through `uv`, which downloads `check-jsonschema` 0.39.0 and `ruamel.yaml` 0.19.1, pinned exactly, from PyPI on their first run.
- **Files written:** the PR lifecycle writes only your own commits, in your clone. The repository setup writes its files on a new branch of your repository. The cleanup writes a backup bundle and its working notes to folders outside your repository; it tells you where the backup is and asks whether to keep it.
- **Privacy:** the author collects no data. The marketplace's [privacy policy](https://github.com/nerymurillohnd/the-claude-factory/blob/main/PRIVACY.md) covers this plugin and the outside services it can reach.

### The agents' limits

Claude Code removes some tools from the agents: none of the four can launch another agent, the tracker and the finalizer have no file-writing tools (Write, Edit, NotebookEdit), and the auditor keeps only Write, for its notes, with no Edit or NotebookEdit. Everything else, such as which shell commands they run or what they write to GitHub, is kept only by each agent's instructions, and Claude checks each report against its evidence before acting on it.

| Agent | May | May not |
| :-- | :-- | :-- |
| `pr-lifecycle:pr-tracker` | Read everything and run commands that only read | Change files, commit, push or write anything to GitHub |
| `pr-lifecycle:pr-fixer` | Edit files, run your validation commands and commit in your clone | Push, write anything to GitHub, change your git configuration, rewrite pushed history or skip your commit hooks |
| `pr-lifecycle:pr-finalizer` | Reply in review threads and resolve review threads | Edit files, commit, push, submit reviews or approvals, or merge |
| `repo-hygiene:health-diagnostics` | Read everything and run commands that only read; write notes in a folder outside your repository | Change anything in your repository, on GitHub or on your machine, or launch another agent |

Before running a command from a pull request whose code is another author's, the fixer stops and asks you, because a command such as a test run executes that code. For a hard limit, add the deny rules in [Add hard limits yourself](#add-hard-limits-yourself): they apply to every agent too.

### Add hard limits yourself

The plugin can't ship permission rules. To block an action for every session and agent, add `deny` or `ask` rules to your own `~/.claude/settings.json` or the project's `.claude/settings.json`, for example:

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
    "ask": ["Bash(git push *)", "Bash(gh pr merge *)", "mcp__*__merge_pull_request"]
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

Uninstalling from the last scope it's installed at also deletes its data directory, unless you add `--keep-data`. The GitHub MCP server you added stays: remove it with `claude mcp remove --scope user github`, and delete the token on GitHub. git and `gh` stay installed. A cleanup backup you chose to keep stays where Claude told you it is.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ they load, but they need `git`, `gh` and your repository on your computer, so use Claude Code |
| ⌨️ Commands | ✅ | ⚠️ they load, but they need `git`, `gh` and your repository on your computer, so use Claude Code |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/github-operations:` to see the skills and commands. If they still don't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>The GitHub server is missing, failed or "needs authentication" in <code>/mcp</code>.</b></summary>

Look at the message, then fix the server. Until you do, the agents have no GitHub tools, so they read GitHub through `gh`.

| What you see | Why | What to do |
| :-- | :-- | :-- |
| `github` is missing from `/mcp` | The server isn't added, or was added at local scope in another project | Add it as in [GitHub MCP server](#-github-mcp-server-recommended), with `--scope user` |
| `plugin:github-operations:github` disappeared after updating | From 0.7.0 the plugin no longer brings the server | Add it yourself, as in [Coming from 0.6.x?](#coming-from-06x) |
| `claude.ai github` is listed in `/mcp`, and GitHub tools work | Claude Code is using your claude.ai GitHub connector | Nothing to do, or add the server to Claude Code with its own token |
| The server is marked failed, or `401` | The token is wrong or expired, or `${GITHUB_PAT}` isn't set where Claude Code started | Remove the server and add it again with a new token, or start Claude Code from a shell that sets `GITHUB_PAT` |
| Some tools work and others don't | The token lacks a permission those tools need | Add the permission to the token |
| In the Claude app, the connector dialog has no **Request headers** section | Request headers are a beta not open to your organization yet | Use the server from Claude Code; the app can't send your token yet |

</details>

<details>
<summary><b>Will Claude push or merge without asking?</b></summary>

No. It asks before every push, unless you chose **Push without asking again on this pull request**, which covers later rounds of that pull request only and never a commit that changes tests, CI, dependencies or files outside the pull request. It always asks before the merge, naming the pull request, the commit and the merge method; a new push voids that approval. It never force-pushes, pushes to the base branch, or merges with admin rights.

</details>

<details>
<summary><b>Why are some review threads still open after the merge question?</b></summary>

Claude resolves only the threads that bots and AI reviewers opened, once it has verified the fix in the diff. On a thread a person opened, it replies and leaves it open, because resolving it is that reviewer's call. The merge question lists those threads for you.

</details>

<details>
<summary><b>How long will Claude wait for a slow pipeline?</b></summary>

The PR tracker waits for the checks to finish, for up to 30 minutes or the limit you set. When the limit ends with jobs still running, it reports what it knows and which jobs are still running, and Claude asks you whether to keep waiting.

</details>

<details>
<summary><b>Will the setup overwrite my existing templates or labels?</b></summary>

No. When your repository already has a file of a kind, Claude shows you what it would change as a diff and asks. It creates a label or changes a repository setting only after you approve that change, and it never edits or deletes your existing labels unless you ask.

</details>

<details>
<summary><b>What does the cleanup refuse to do, even if I approve?</b></summary>

It never runs `git reset --hard`, a `checkout` or `restore` that discards work, or `git clean -x`, and never force-pushes outside a history rewrite you asked for by name. A history rewrite (to remove a secret or a huge file) is never part of a bulk approval. Deploy keys, tokens, secrets, installed apps and collaborator access are reported, never changed, and other people's branches, forks, comments and pull requests are never touched.

</details>

<details>
<summary><b>Does the cleanup read my secrets?</b></summary>

No. Files that look like secrets are named by file only and never read. A secret that was ever committed is reported as exposed, with the instruction to rotate it first, because rewriting history doesn't remove it from clones, forks or cached views.

</details>

<details>
<summary><b>Should I run these in bypass-permissions mode?</b></summary>

No. Use the default permission mode, so Claude Code asks you before each command that changes something. Approving a plan or a push and approving a prompt are two separate checks.

</details>

<details>
<summary><b>Can I run them with <code>claude -p</code>?</b></summary>

Only a read-only audit is meant for it. Every push, the merge, the cleanup plan and every command that changes anything need your approval, and a headless run has nobody to give it. Run them in an interactive session.

</details>

<details>
<summary><b>My remote is not on GitHub.</b></summary>

The cleanup of branches, worktrees, stashes and history works with any remote. Pull requests, workflows, Dependabot and forks come from GitHub; for other hosts they are reported as not reachable and nothing that depends on them is touched. The PR lifecycle and the repository setup are GitHub only.

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

This plugin ships none of GitHub's software. Its skills and agents use the hosted remote server of the official [GitHub MCP Server](https://github.com/github/github-mcp-server) (MIT license, © GitHub). The URL forms, toolsets and tool names come from GitHub's documentation: the [remote server guide](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md) and the guide to [installing it in Claude applications](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-claude.md). We re-checked them against the live server, and if GitHub changes them, GitHub's documentation is the reference.

The Actions skill's knowledge of [`anthropics/claude-code-action`](https://github.com/anthropics/claude-code-action) (MIT license, © Anthropic) was read from its source code and documentation, and of GitHub Actions from [GitHub's documentation](https://docs.github.com/en/actions), and rewritten in this plugin's own words; no upstream text or example is copied. The version each fact was checked against is named at the end of each reference file.

GitHub also publishes its own [agent plugin](https://github.com/github/github-mcp-server/tree/main/agent-plugin) for the same server, which declares only the server connection. This plugin adds the skills and agents around that server (the pull request lifecycle, the repository setup, and the audit and cleanup), and leaves the server connection to you.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by GitHub. *GitHub* is a trademark of GitHub, Inc.
