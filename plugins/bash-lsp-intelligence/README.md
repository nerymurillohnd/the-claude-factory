<div align="center">

# 🐚 Bash LSP Intelligence

<p><strong>Gives Claude Code bash-language-server for Bash and POSIX shell scripts, formats and checks every script Claude edits with shfmt and ShellCheck using your own configuration, and teaches Claude to trace sourced files and same-named functions before a rename.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fbash-lsp-intelligence%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Language%20Support-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.288-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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

💻 **Claude Code only** — it connects a language server, and only Claude Code runs language servers. Claude can install it, but there the language server doesn't start and the post-edit hook runs only where Claude can run tasks and finds `bash`, `shfmt` and `shellcheck`.

> [!TIP]
> **TL;DR** — Install bash-language-server, shfmt and ShellCheck, add this plugin, and every shell script Claude edits comes back formatted and checked with your own `.editorconfig` and `.shellcheckrc`, while Claude tells same-named functions apart by what each script sources.

Bash LSP Intelligence connects bash-language-server to Claude Code and adds a hook that formats and lints every shell script Claude changes with shfmt and ShellCheck. Your own `.editorconfig`, `.shellcheckrc` and `SHELLCHECK_OPTS` decide the style and rules; a strict baseline applies only when you have none. A skill teaches Claude to trace `source` chains before it trusts a same-named function, so a rename touches only the callers that really reach it.

## ✨ Why use it

- **Every edit is formatted and checked** — after each edit to a `.sh`, `.bash` or extensionless Bash script, the plugin runs `shfmt -w` and then `shellcheck` on that file. Findings go back to Claude as an error it must fix before moving on; after every check you get a one-line summary of what ran, what shfmt reformatted and whether it found errors.
- **Your style and rules, not the plugin's** — shfmt reads your `.editorconfig` and ShellCheck your `.shellcheckrc` and `SHELLCHECK_OPTS`. A strict baseline (two-space indent, every optional check) applies only when you have none.
- **ShellCheck findings as Claude edits** — the language server also pushes ShellCheck diagnostics for `.sh`, `.inc`, `.bash` and `.command` files, including scripts under `.github/` and `.claude/`.
- **Renames that respect `source`** — two `render` functions in unrelated scripts aren't one rename target; Claude traces which definition each caller reaches through `source` chains, traps and dispatch before editing.
- **The real dialect, respected** — a Zsh script with a `.sh` name isn't converted to Bash; ShellCheck can't analyze it, and the plugin says so instead of calling it clean.

## 🧩 What's inside

| Component     | Name                                          | What it does                                                                                                                                                                                         | How it runs                                                                                     |
| :------------ | :-------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------- |
| 🧠 LSP server | `shellscript`                                 | Connects `bash-language-server` for `.sh`, `.inc`, `.bash` and `.command` files, indexing `.github/` and `.claude/` too                                                                              | Automatically when Claude opens or edits a shell file                                           |
| 🪝 Hook       | `PostToolUse` · `PostToolUseFailure`          | Runs `shfmt -w` and `shellcheck` on the shell scripts an Edit, Write or Bash call changed, tells you what it did and sends Claude only the errors                                                    | Automatically after each Edit, Write or Bash call, and after a Bash call that fails             |
| 🪝 Hook       | `UserPromptSubmit`                            | Tells Claude to call the `bash-lsp-intelligence:bash-lsp-intelligence` skill with the Skill tool and apply it end to end before it creates, writes or edits a shell script, with any tool or command | Automatically with each prompt                                                                  |
| 🎯 Skill      | `bash-lsp-intelligence:bash-lsp-intelligence` | Teaches Claude to navigate with the language server first, trust its results only after five checks, and work with shfmt and ShellCheck the way your project configures them                         | Automatically when you work on shell scripts, or `/bash-lsp-intelligence:bash-lsp-intelligence` |

## 📋 Prerequisites

| Tool                 | Minimum version | Check                            |
| :------------------- | :-------------- | :------------------------------- |
| Claude Code          | 2.1.288         | `claude --version`               |
| bash-language-server | —               | `bash-language-server --version` |
| shfmt                | —               | `shfmt --version`                |
| ShellCheck           | —               | `shellcheck --version`           |
| Node.js              | 24              | `node --version`                 |
| Bash                 | 3.2             | `bash --version`                 |
| Git (optional)       | —               | `git --version`                  |

The plugin also uses `awk`, `cat`, `cksum`, `date`, `env`, `find`, `head`, `mktemp`, `readlink`, `rm`, `touch` and `uname`, which come with macOS and Linux.

Install them on the `PATH` of the shell you start `claude` from. The plugin doesn't install them: Claude Code starts `bash-language-server` by name, and the hook starts `shfmt` and `shellcheck` by name. Node.js runs bash-language-server and needs to be Node.js 24 or later, the oldest Node.js this plugin supports; the hook itself needs no Node.js. Claude Code starts the hook with `bash`, a Bash script that needs Bash 3.2 or later. Git is optional: in a Git repository the hook asks Git which files a Bash command changed, and without it the hook compares modification times. On Windows, run Claude Code from Git Bash with the same tools on its `PATH`.

### 🤖 Claude Code

Already installed? Bring it to the latest version the way you installed it, as the official [Update Claude Code](https://code.claude.com/docs/en/setup#update-claude-code) guide shows for each installation method. New to Claude Code? Follow the [official setup](https://code.claude.com/docs/en/setup).

### 🧠 bash-language-server

<details>
<summary>📦 <b>npm</b> — any platform</summary>

```bash
npm install -g bash-language-server
```

</details>
<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install bash-language-server
```

</details>
<details>
<summary>🐧 <b>snap</b> — Ubuntu</summary>

```bash
sudo snap install bash-language-server --classic
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install -y nodejs-bash-language-server
```

</details>

### 🧹 shfmt

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install shfmt
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian 12+, Ubuntu 24.04+</summary>

```bash
sudo apt install shfmt
```

</details>
<details>
<summary>🐹 <b>Go</b> — any platform</summary>

```bash
go install mvdan.cc/sh/v3/cmd/shfmt@latest
```

</details>

Or download a release binary from [GitHub](https://github.com/mvdan/sh/releases).

### 🔍 ShellCheck

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install shellcheck
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt install shellcheck
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install ShellCheck
```

</details>
<details>
<summary>🪟 <b>winget</b> — Windows (Git Bash)</summary>

```bash
winget install --id koalaman.shellcheck
```

</details>

### 🟢 Node.js

<details>
<summary>📥 <b>nvm</b> — macOS, Linux</summary>

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
\. "$HOME/.nvm/nvm.sh"
nvm install --lts
```

</details>
<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install node
```

</details>
<details>
<summary>🍫 <b>Chocolatey</b> — Windows, in PowerShell as administrator</summary>

```powershell
powershell -c "irm https://community.chocolatey.org/install.ps1|iex"
choco install nodejs
```

</details>

### 🐚 Bash

macOS and Linux ship Bash. On Windows, Git for Windows includes Git Bash; download it from [git-scm.com](https://git-scm.com/downloads/win) or install it with winget.

<details>
<summary>🪟 <b>winget, Git for Windows</b> — Windows</summary>

```powershell
winget install --id Git.Git -e --source winget
```

</details>

### 🌿 Git (optional)

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install git
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt install git
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install git
```

</details>

On Windows, Git for Windows includes Git Bash and Git: download it from [git-scm.com](https://git-scm.com/downloads/win).

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install bash-lsp-intelligence@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install bash-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install bash-lsp-intelligence@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install bash-lsp-intelligence@the-claude-factory
```

To confirm it works, ask Claude to write `echo $name` in a script and fix it. Under the edit you see `Found 1 new diagnostic issue in 1 file` from the language server and, once the file is clean, a line like `bash-lsp-intelligence: ran shfmt, shellcheck on scripts/deploy.sh · no formatting changes · no errors` from the hook.

## 🚀 Usage

You don't need to call anything: the language server starts with the first shell file Claude edits, the hook runs after each edit, and the skill loads when you work on shell scripts.

With each prompt you send, the plugin also tells Claude to call the `bash-lsp-intelligence:bash-lsp-intelligence` skill with the Skill tool and apply it end to end before it creates, writes or edits a shell script, so a passing check is never mistaken for the whole workflow. When the tools find errors, the hook's message to Claude repeats that: load the skill, audit the errors with it and fix them before continuing with anything else.

After every check, the hook shows you one line: which tools ran on which files, whether shfmt reformatted any of them and whether they found errors, or why nothing ran (a missing tool, a Zsh script, more files than the hook checks). Claude gets a message only when there are errors.

### Example: what happens after an edit

```text
Add a --dry-run flag to scripts/deploy.sh.
```

**Result:** Claude edits the script. If shfmt or ShellCheck finds something, Claude sees it right away:

```text
bash-lsp-intelligence's post-edit hook ran shfmt, shellcheck on scripts/deploy.sh and found errors:
shellcheck (/path/to/project/scripts/deploy.sh):
In /path/to/project/scripts/deploy.sh line 14:
  rsync $opts "$src" "$dest"
        ^-- SC2086 (info): Double quote to prevent globbing and word splitting.
Use the Skill tool to load "bash-lsp-intelligence:bash-lsp-intelligence", audit these errors with it and fix them before continuing with anything else.
```

You see `bash-lsp-intelligence: ran shfmt, shellcheck on scripts/deploy.sh · no formatting changes · errors in scripts/deploy.sh, sent to Claude to fix`. Claude loads the skill, turns `opts` into an array, the hook runs again, and you see `bash-lsp-intelligence: ran shfmt, shellcheck on scripts/deploy.sh · no formatting changes · no errors`.

### Example: rename a function used across scripts

```text
Rename render_report to build_report everywhere it's actually called.
```

**Result:** Claude takes the language server's reference list, keeps only the hits whose scripts reach this definition through `source`, greps traps, `bash -c` strings and hook commands for the rest, and edits only those.

### Example: format a script to the project's style

```text
Format scripts/backup.sh.
```

**Result:** Claude runs `shfmt -w`, which reads your `.editorconfig`, re-reads the file, and reports what changed.

## ⚙️ Configuration

The hook runs the tools the way you would from a terminal, so **your configuration wins**:

| Tool       | What it reads                                                                                                                                                  | When you have none                                                                                                        |
| :--------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| shfmt      | `.editorconfig`, searched from the script's folder upward (`[[shell]]` keys such as `indent_size`, `switch_case_indent`, `binary_next_line`)                   | `shfmt -i 2 -ci -bn`: two-space indent, indented `case` branches, binary operators at line start                          |
| ShellCheck | The first `.shellcheckrc` or `shellcheckrc` from the script's folder upward, then `~/.shellcheckrc` or `$XDG_CONFIG_HOME/shellcheckrc`, plus `SHELLCHECK_OPTS` | `shellcheck -o all -S style -x -a -P SCRIPTDIR`: every optional check, style severity, sourced files followed and checked |

An `.editorconfig`, a `.shellcheckrc` or `SHELLCHECK_OPTS` of your own replaces the corresponding default entirely; the plugin never creates or edits one.

**Optional, recommended:** let the hook see exactly which files a Bash command changed by adding this to your user settings (`~/.claude/settings.json`); without it the hook finds them by modification time:

```json
{
  "bashEditDiffEnabled": true
}
```

## 🔍 What this plugin runs and sends

- **Hooks:**
  - `PostToolUse` on `Edit|Write|NotebookEdit|Bash` runs `bash "${CLAUDE_PLUGIN_ROOT}/hooks/bash-gate.sh"` (60-second limit), which runs `shfmt -w` (it rewrites the file in place) and then `shellcheck` on each shell script an Edit, Write or Bash call changed. It ignores any other tool, including NotebookEdit. It shows you one line about every check and sends Claude a message only when the tools find errors.
  - `PostToolUseFailure` on `Bash` runs the same script after a command that fails, so scripts a failed command changed are checked too.
  - Both set `onFailure` to `block`: when the script itself crashes or runs past its limit, Claude receives that error like a finding.
  - `UserPromptSubmit` runs `cat "${CLAUDE_PLUGIN_ROOT}/hooks/bash-lsp-skill-instructions.txt"`, which adds a short instruction to each prompt you send: before Claude creates, writes or edits a shell script, with any tool or command, it calls the `bash-lsp-intelligence:bash-lsp-intelligence` skill with the Skill tool and applies it end to end, including its LSP and Grep steps. It sends nothing and writes nothing.

  To find the changed scripts of a Bash call, the script uses the list Claude Code passes, or else `git rev-parse --is-inside-work-tree` and `git ls-files --modified --others --exclude-standard` plus `git diff --cached --name-only --relative` (the staged files) in a Git repository, or a walk of at most 20,000 files of the project otherwise (never your home folder or the disk root). After that walk, a script inside a Git repository below your project counts only when those Git commands list it there, so a repository you clone, a branch you check out or a pull is never checked or reformatted. When the walk finds more than 20 shell scripts outside any Git repository, the hook checks none of them and tells you. From the list Claude Code passes, it drops the scripts Git ignores, which it finds with `git check-ignore --stdin -z`: what a command writes into an ignored folder, such as the hook scripts a package manager generates on install, is not checked or reformatted. It finds `shfmt` and `shellcheck` with `command -v`, and when one is missing it uses `command -v` and `uname -s` to pick the install command it shows you for your system. It runs the tools on at most 20 scripts per call. It skips `node_modules`, `.venv`, `venv` and `site-packages`, and its walk skips `.git`, `dist`, `build`, `__pycache__` and `.cache`. Hooks run on their own, with your access and without a permission prompt.
- **MCP servers:** none.
- **Network:** none.
- **Files written:** `shfmt -w` rewrites the shell scripts it formats, in place. On each Edit, Write or Bash call, the hook creates one temporary folder under `TMPDIR` (`/tmp` when unset) named `bash-lsp-intelligence.XXXXXX`, keeps its working files there and deletes it when it exits. The plugin writes nothing to its data folder and nothing else to your project.
- **Privacy:** the author collects no data. The marketplace's [privacy policy](https://github.com/nerymurillohnd/the-claude-factory/blob/main/PRIVACY.md) covers this plugin and the outside services it can reach.

## 🔄 Updating

```bash
claude plugin update bash-lsp-intelligence@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update bash-language-server, shfmt and ShellCheck the way you installed them, for example:

```bash
npm install -g bash-language-server@latest
brew upgrade shfmt shellcheck
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall bash-lsp-intelligence@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall bash-lsp-intelligence@the-claude-factory --scope project
```

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps nothing in its data directory. bash-language-server, shfmt and ShellCheck stay installed; remove them with the tool you installed them with.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component      | Claude Code |                       Claude                        |
| :------------- | :---------: | :-------------------------------------------------: |
| 🎯 Skills      |     ✅      |                         ✅                          |
| 🪝 Hooks       |     ✅      | ⚠️ only in conversations where Claude can run tasks |
| 🧠 LSP servers |     ✅      |                         ➖                          |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

The skill loads in Claude, but it relies on the language server, which Claude doesn't run. The hook runs `bash`, `shfmt` and `shellcheck`, so it works only on a machine where they're installed; in Claude Code that's your computer. Claude Code on the web doesn't start plugin language servers either, so there Claude gets no diagnostics or code navigation from this plugin.

**Platforms:** macOS and Linux, and Windows through Git Bash.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/bash-lsp-intelligence:` to list its skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Claude never reports diagnostics for shell files.</b></summary>

Open `/plugin` → **Errors**. `Executable not found in $PATH: "bash-language-server"` means the server isn't installed or isn't on the `PATH` of the shell you started `claude` from. Install it, check it with this command, and start a new session:

```bash
which bash-language-server
```

ShellCheck must be on the same `PATH` for the server to report its findings.

</details>

<details>
<summary><b>The hook says a tool is not installed.</b></summary>

The hook didn't find the tool, so it didn't check the script. It doesn't block Claude and adds nothing to its context: you get a line after every call that names the script and the tool and gives the install command for your system, for example:

```text
bash-lsp-intelligence: not run on scripts/deploy.sh: shfmt is not installed (install it with brew install shfmt)
```

The command comes from the package manager the hook finds: Homebrew or MacPorts on macOS; `apt`, `dnf`, `pacman`, `zypper` or `apk` on Linux; otherwise the tool's releases page. Install the tool on the `PATH` of the shell that starts `claude`; the next edit is checked.

</details>

<details>
<summary><b>The hook reformatted a file I was editing.</b></summary>

That is `shfmt -w` applying your `.editorconfig` (or the default style). The line the hook shows you after the check names the file under `reformatted`; Claude isn't told.

</details>

<details>
<summary><b>Claude got a message that the post-edit hook failed.</b></summary>

The script crashed or ran past its 60-second limit, so it didn't check the changed scripts, for example `bash-lsp-intelligence: the post-edit hook failed at line 123, so the changed shell scripts were not checked.` Claude receives that error like a finding. Run `bash --version` to confirm Bash is 3.2 or later, then ask Claude to edit the script again; open an issue from the link below if it keeps failing.

</details>

<details>
<summary><b>My scripts have hundreds of legacy findings. Will Claude chase them all?</b></summary>

No. The hook checks only the scripts Claude changes in the session, never the whole tree. Legacy scripts stay as they are until Claude edits them.

</details>

<details>
<summary><b>A Zsh script was "not checked".</b></summary>

ShellCheck supports sh, bash, dash and ksh only. The hook tells you the file was not checked (`not run on <file>: ShellCheck does not support zsh`) instead of reporting it clean; use Bash, or a Zsh-aware linter, for that script.

</details>

<details>
<summary><b>I already use another shell language server plugin.</b></summary>

Each file extension gets one server. When two enabled plugins claim `.sh`, the first registered handles it and `/plugin` → **Errors** shows that the other isn't used. Keep one of them enabled.

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

Through Git Bash: start Claude Code from a Git Bash shell that has `shfmt`, `shellcheck` and `bash-language-server` (with Node.js) on its `PATH`.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 🐍 [Python LSP Intelligence](../python-lsp-intelligence/README.md) · 🟦 [TypeScript 7 LSP Intelligence](../typescript7-lsp-intelligence/README.md) · 🟦 [TypeScript 6 LSP Intelligence](../typescript6-lsp-intelligence/README.md)
- 📖 [Claude Code code intelligence docs](https://code.claude.com/docs/en/plugins/code-intelligence)
- 📖 [ShellCheck wiki](https://www.shellcheck.net/wiki/) · [shfmt](https://github.com/mvdan/sh) · [bash-language-server](https://github.com/bash-lsp/bash-language-server)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=bash-lsp-intelligence) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=bash-lsp-intelligence) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=bash-lsp-intelligence)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
