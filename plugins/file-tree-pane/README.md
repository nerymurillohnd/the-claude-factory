<div align="center">

# 🌳 File Tree Pane

<p><strong>Keeps a live file tree of your project beside the chat: git status and line counts, what Claude reads, writes and commits, search, previews, diffs and your editor one key away.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Ffile-tree-pane%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Productivity-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.299-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Prerequisites](#-prerequisites) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it is a mod: it draws a pane in Claude Code's own interface, which the Claude app's chat and Cowork don't load.

> [!TIP]
> **TL;DR** — Type `/file-tree` and keep your project's tree beside the chat: see what changed, watch the files Claude reads and writes light up, and preview, diff or open any file without leaving the session.

## ✨ Why use it

- **See what Claude touches as it works** — files shimmer purple while Claude reads or searches them, orange when it writes them, and green when it commits them; collapsed folders open to show the file, and the footer reports each `git` and `gh` operation.
- **Know what changed at a glance** — every file and folder shows its git status in color, changed files show `+N -N` lines, folders show `?:N M:N D:N`, and the header shows the branch, its upstream and how far ahead or behind it is.
- **Point Claude at a file without typing its path** — while the pane is on screen, the file or folder you select is passed to Claude with each prompt, so you can ask "what changed here?", and an `@path` in your prompt reveals that file in the tree.
- **Preview, diff and edit in place** — a click previews a file, `d` shows its diff, `e` opens your editor at the line in view, and a double click opens it in its default app (never a script or program, which would run).
- **Light on huge repositories** — it draws only the rows on screen, lists a folder only when you open it, and scopes every git call to the folder it shows, so a tree of 50,000 files scrolls like one of fifty.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧩 Mod | `file-tree-pane` | Draws the file tree pane, highlights Claude's tool calls on it, passes the selected file to Claude, and adds the `/file-tree` command | Automatically in every Claude Code session once installed; the pane opens by itself where it can dock, or with `/file-tree` |

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.299 | `claude --version` |
| git | — | `git --version` |
| [tmux](https://github.com/tmux/tmux/wiki) (optional): opens a terminal editor or diff tool | — | `tmux -V` |
| [herdr](https://herdr.dev) (optional): opens a terminal editor or diff tool | — (0.9.1 for row clicks) | `herdr --version` |
| [Nerd Font](https://www.nerdfonts.com) (optional): file icons | — | — |
| [hunk](https://hunk.dev) (optional): your own diff tool | — | `hunk --version` |
| [lazygit](https://github.com/jesseduffield/lazygit) (optional): your own diff tool | — | `lazygit --version` |

`git` on `PATH` gives the tree its status, line counts and diffs; the tree works without it.

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

### 🌿 git

<details>
<summary>🍺 <b>Homebrew</b> — macOS</summary>

```bash
brew install git
```

</details>
<details>
<summary>⚓ <b>MacPorts</b> — macOS</summary>

```bash
sudo port install git
```

</details>
<details>
<summary>🛠️ <b>Xcode Command Line Tools</b> — macOS</summary>

```bash
xcode-select --install
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt-get install git
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install git
```

</details>
<details>
<summary>🏔️ <b>pacman</b> — Arch Linux</summary>

```bash
sudo pacman -S git
```

</details>
<details>
<summary>🦎 <b>zypper</b> — openSUSE</summary>

```bash
sudo zypper install git
```

</details>

### 🪟 tmux

<details>
<summary>🍺 <b>Homebrew</b> — macOS</summary>

```bash
brew install tmux
```

</details>
<details>
<summary>⚓ <b>MacPorts</b> — macOS</summary>

```bash
sudo port install tmux
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt install tmux
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install tmux
```

</details>
<details>
<summary>🏔️ <b>pacman</b> — Arch Linux</summary>

```bash
sudo pacman -S tmux
```

</details>
<details>
<summary>🦎 <b>zypper</b> — openSUSE</summary>

```bash
sudo zypper install tmux
```

</details>

### 🐑 herdr

<details>
<summary>⬇️ <b>Install script</b> — macOS, Linux</summary>

```bash
curl -fsSL https://herdr.dev/install.sh | sh
```

</details>
<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install herdr
```

</details>
<details>
<summary>🧰 <b>mise</b> — macOS, Linux</summary>

```bash
mise use -g herdr
```

</details>

### 🔤 Nerd Font

<details>
<summary>🍺 <b>Homebrew</b> — macOS</summary>

```bash
brew install font-hack-nerd-font
```

</details>
<details>
<summary>🍺 <b>Homebrew</b> — Linux</summary>

```bash
brew install --cask font-hack-nerd-font
```

</details>
<details>
<summary>⬇️ <b>Install script</b> — macOS, Linux</summary>

```bash
curl -s https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/install.sh -o install.sh
chmod u+x install.sh
./install.sh install Hack
```

</details>

### 🔍 hunk

<details>
<summary>⬇️ <b>Install script</b> — macOS, Linux</summary>

```bash
curl -fsSL https://hunk.dev/install.sh | sh
```

</details>
<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install hunk
```

</details>
<details>
<summary>📦 <b>npm</b> (Node.js 22+) — macOS, Linux</summary>

```bash
npm install --global hunkdiff
```

</details>
<details>
<summary>🧰 <b>mise</b> — macOS, Linux</summary>

```bash
mise use -g hunk
```

</details>

### 🦥 lazygit

<details>
<summary>🍺 <b>Homebrew</b> — macOS</summary>

```bash
brew install lazygit
```

</details>
<details>
<summary>⚓ <b>MacPorts</b> — macOS</summary>

```bash
sudo port install lazygit
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian 13+, Ubuntu 25.10+</summary>

```bash
sudo apt install lazygit
```

</details>
<details>
<summary>🎩 <b>dnf</b> (COPR) — Fedora</summary>

```bash
sudo dnf copr enable dejan/lazygit
sudo dnf install lazygit
```

</details>
<details>
<summary>🏔️ <b>pacman</b> — Arch Linux</summary>

```bash
sudo pacman -S lazygit
```

</details>
<details>
<summary>🐹 <b>Go</b> — macOS, Linux</summary>

```bash
go install github.com/jesseduffield/lazygit@latest
```

</details>

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install file-tree-pane@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install file-tree-pane --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install file-tree-pane@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install file-tree-pane@the-claude-factory
```

## 🚀 Usage

### Example: keep the tree beside the chat

```text
/file-tree
```

**Result:** the pane docks beside the transcript (in a terminal at least 110 columns wide in fullscreen mode; above the prompt otherwise) and follows your working directory: when the session's working directory changes, the tree re-roots there. Where the terminal is wide enough, it opens by itself when a session starts; turn that off with **Open at start**.

### Example: pin another folder

```text
/file-tree ../shared-config
```

**Result:** the tree shows that folder and stays there, whatever the working directory does. `/file-tree` alone goes back to following the working directory.

### Example: ask about the file you selected

Click `src/config.yaml` in the tree, then ask:

```text
What did you change in this file?
```

**Result:** Claude receives, beside your prompt, that you have `src/config.yaml` selected in the File Tree Pane, and answers about that file. Type `@docs/setup.md` in a prompt and the tree opens its folder and selects it.

### Example: review what changed

Select a changed file or folder and press `d`.

**Result:** the pane shows its diff against `HEAD`, drawn in Claude Code's diff colors: an untracked file shows as all added, and a folder shows every changed file under it, each under its name. `j`/`k` jump to the next or previous file (or hunk, for one file), the arrows scroll a line, `f`/`b` a page, and `d` goes back to the file. Set **Diff with** to `hunk diff --` or `lazygit -f` to open your own diff tool instead.

### Keys

Click a row to give the tree the keys; Esc gives them back to the prompt. Ctrl+X Tab focuses the pane, where the shortcut buttons and the header's `p`, `d` and `e` take their keys.

| Key | In the tree | In a preview or diff |
| :-- | :-- | :-- |
| `j` / `k`, ↓ / ↑ | Move down / up | Next / previous line; in a diff `j`/`k` jump by file or hunk |
| `l` / `h`, → / ← | Open a folder / close it, or go to the parent | `h` and ← go back to the tree |
| `o` or Enter | Open the file with **Open with**, or open and close a folder | — |
| Space | Quick Look on macOS; opens and closes a folder | Next page |
| `p` | Preview the file | Back to the tree |
| `d` | Diff the changed file or folder | In a preview, that file's diff; in a diff, back to the file, or the tree |
| `e` | Open the file in your editor | Open your editor at the top line shown |
| `s` | Focus the search field; type, then Enter jumps to the first match | — |
| `f` / `b`, PgDn / PgUp, Home / End | Page and jump | Page and jump |

A single click selects a row and previews a file; a double click opens the file with **Open with**. The mouse wheel and the scrollbar scroll the tree to its last row. Hover a header button (`Σ`, `p`, `d`, `e`) to see what it does: `Σ` switches the right column to sizes and back, with each folder's disk usage worked out in the background for the rows on screen. The `j`/`k`/`h`/`l`/open/search buttons under the search field press with their keys once the pane has focus, before you click a row.

Resize the pane by dragging its edge where your terminal reports the mouse, or with Ctrl+X ← / ↑ (larger) and Ctrl+X → / ↓ (smaller). Rebind those in `~/.claude/keybindings.json` under the `Pane` context: the actions are `pane:grow` and `pane:shrink`.

## ⚙️ Configuration

Change them in `/config`, where they are listed as `file-tree-pane.<option>` and the options with fixed values are pickers (v2.1.271+), or in `/plugin` → **Installed** → **File Tree Pane** → **Configure options**. From the shell, pass `--config <option>=<value>` to `claude plugin install`. A change takes effect at once.

| Option | Values | Default | What it does |
| :-- | :-- | :-- | :-- |
| `activity` | `reads and writes`, `writes`, `reads`, `none` | `reads and writes` | What shimmers. Git status, line counts and the git footer always show. |
| `followClaude` | `true`, `false` | `true` | Scroll to what Claude reads, writes or commits, opening its folders. Off keeps the view where you put it; the highlights still show, on the closed folder that holds the file. |
| `openAtStart` | `true`, `false` | `true` | Open the pane when a session starts, where it can dock. Off keeps it closed until `/file-tree`. |
| `rightColumn` | `date`, `age`, `size` | `date` | The right column when a session starts. `age` reads `now`, `12m`, `3h`, `5d`, then the day (`Oct 9`) past a week and the year past a year. |
| `hints` | `true`, `false` | `true` | Outside a git repository, a line saying git status starts after `git init`. |
| `searchSpacing` | `true`, `false` | `true` | A blank line above and below the search field. Off gives the tree those two rows. |
| `shortcutRow` | `true`, `false` | `true` | The `j`/`k`/`h`/`l`/open/search buttons. Off hides them; the keys still work in the tree. |
| `openWith` | empty, `editor`, a command | empty | Empty opens files in their default app, except files that app would run, which need a command here: scripts, programs, installers and shortcuts such as `.command`, `.sh`, `.exe` or `.desktop`, any file with its executable bit set on macOS and Linux, a name ending in a dot or a space, and a link whose target is any of these. A link opens the file it leads to, checked by its own name. `editor` opens `$VISUAL`, then `$EDITOR`, then `vi`, in a new tmux window or a herdr pane; in tmux, nvim reuses a running nvim in the same session. A command such as `code -g {path}` runs as is, `{path}` being the file. |
| `editWith` | empty, a command | empty | What `e` opens, at the top line shown: empty is the same editor as `editor` with `+line`; a command takes `{path}` and `{line}`, such as `code -g {path}:{line}` or `zed {path}:{line}`. |
| `diffWith` | empty, a command | empty | Empty shows diffs in the pane. A terminal command such as `hunk diff --`, `lazygit -f`, `git difftool -y --` or `nvim -c Gvdiffsplit` runs on the path, given as `./path`, in a tmux window, a herdr pane or, on Linux, a new terminal window through `xdg-terminal-exec`. |
| `ignore` | names | empty | Names left out of the tree, the search and the highlights, separated by spaces or commas, such as `.cache .tmp`. Exact names at any depth, like the built-in `.git` and `node_modules`. |
| `palette` | `tone=#rrggbb` pairs | empty | Your own colors over the theme's. Tones: `read`, `write`, `commit`, `modified`, `added`, `deleted`, `untracked`, `conflict`, `muted`, `accent`, `selected`, `hovered`. The pane names any pair it ignores. |
| `glyphs` | `auto`, `nerd`, `plain` | `auto` | `auto` uses Nerd Font icons in a terminal when a Nerd Font was installed before the terminal started, and over SSH; plain Unicode in the desktop app and wherever no Nerd Font is found. |

The pane takes its colors from your theme and follows a theme switch. On a light theme, built in or custom with a light `base`, it uses its own palette, where every text color reaches WCAG AAA contrast (7:1 or more), on the selected and hovered rows too. With the `auto` theme, or a custom theme whose file it can't read, every color comes from the theme itself.

A terminal editor needs a terminal to run in: a mod can't hand Claude Code's own terminal to another program. Outside tmux and herdr, `editor` and an empty **Edit with** show a notice instead; set a GUI command such as `code -g {path}:{line}` to edit from anywhere. In herdr, the editor opens in a pane to the right of Claude's, in the file's folder, and that pane closes when the editor exits; the file name reaches the editor through the pane's environment, so names with spaces or shell characters are safe.

## 🔍 What this plugin runs and sends

- **Hooks:** a mod, with no shell hooks. It hooks the start of each session, each tool call, each prompt you send, a working directory change, a theme change, the `/file-tree` command and the pane's drawing, scrolling and input.
- **Commands:** read-only `git` (`rev-parse`, `status`, `diff`, `ls-files`, `log`) in the folder it shows, again every 5 seconds while the pane is on screen, and the others listed under [What does the mod reach on my machine?](#-faq--troubleshooting)
- **Files read:** the folders you open and the file you preview.
- **MCP servers:** none.
- **Network:** none. It never calls the model.
- **Files written:** none.
- **Before you install:** a mod runs with your permissions and no sandbox. Install it only if you trust this marketplace; this README lists everything it hooks and calls.

## 🔄 Updating

```bash
claude plugin update file-tree-pane@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update the tools you installed for it the way you installed them, for example a Homebrew formula:

```bash
brew upgrade tmux
```

herdr installed with its script updates itself:

```bash
herdr update
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall file-tree-pane@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall file-tree-pane@the-claude-factory --scope project
```

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps no data and writes no files, so nothing is left behind; the tools you installed for it stay.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🧩 Mods | ✅ every Claude Code session except a Desktop session on WSL | ⚠️ the plugin directory lists a mod for Claude Code only |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

The pane draws in the terminal, the desktop app's **Code** tab and the VS Code extension (extension v2.1.299+; v2.1.304+ in a session that doesn't fetch feature flags, such as one on Amazon Bedrock). In VS Code each row is a button: clicks and the shortcut buttons work, while the shimmer, double click, hover and the row keys need the terminal or the desktop app. In `claude -p` and cloud sessions nothing draws, and the mod only passes the selected file along when a pane is on screen.

### Limitations

- Claude's searches through the built-in Grep and Glob tools light up the folder they search. Searches run through the shell (`grep`, `rg`, `find`) light up the paths their command names.
- The pane refreshes every 5 seconds while it is on screen, and right after Claude's tool calls: a change another program makes shows within those 5 seconds.
- Line counts for untracked files cover the first 200 of them, up to 64 MiB each; a folder's diff shows its first 50 untracked files.
- A submodule shows as changed when its commit moves; changes inside its own working tree don't show.
- Search covers the first 4 MiB of file names `git` lists (about 50,000 to 100,000 files), or the first 100,000 entries outside a repository; the match line says when it stopped early. Files made outside Claude become searchable within 30 seconds.
- Under herdr 0.9.0 and older the rows ignore the mouse, because those versions report clicks at the wrong cells; keys and everything else keep working. Run `herdr update` to get row clicks (herdr 0.9.1 or later).
- On Windows, set **Open with**, **Edit with** and **Diff with** to GUI commands, such as `code -g {path}:{line}`: the built-in terminal editor and diff tools run in tmux, or in herdr on macOS and Linux.
- These settings turn the mod off: `"disableAllHooks": true` in your own `~/.claude/settings.json` or in managed settings, `allowManagedModsOnly` and `allowManagedHooksOnly` in managed settings, and starting Claude Code with `--safe-mode` or `--bare`.
- In organizations with managed settings or a Team or Enterprise login, Claude Code's built-in guard runs ahead of every mod and can refuse to load it.

## ❓ FAQ & Troubleshooting

<details open>
<summary><b>The pane doesn't open by itself, or <code>/file-tree</code> says it is open but not shown.</b></summary>

A pane that opens by itself waits for a terminal at least 144 columns wide (110 once you have opened it there before); `/file-tree` opens it at any width. The reply names the reason when a surface can't place it. Run `/plugin` to check that `file-tree-pane` is listed among active mods; if it is missing, start Claude Code with `claude --debug` and look in the debug log for `file-tree-pane`, where a line names why the module was not loaded or a hook was skipped.

</details>

<details>
<summary><b>The keys type into the prompt instead of moving in the tree.</b></summary>

The prompt has the keys. Click a row to give the tree the keys; Esc gives them back to the prompt. Ctrl+X Tab focuses the pane without giving the tree its keys: there, the shortcut buttons (`j`, `k`, `h`, `l`, `o`, `s`) and the header's `p`, `d` and `e` take their keys.

</details>

<details>
<summary><b>The icons show as empty boxes, or as plain triangles when I have a Nerd Font.</b></summary>

`glyphs: auto` uses Nerd Font icons only when it finds a Nerd Font file installed before your terminal started, so a font you just installed takes effect after you restart the terminal. If your terminal uses a Nerd Font the mod can't find, set `glyphs` to `nerd`; set it to `plain` to keep Unicode everywhere.

</details>

<details>
<summary><b>Does it slow down Claude's tool calls?</b></summary>

No. Each call passes on unchanged: before it, the mod marks the files it names; after it, it schedules a refresh a quarter second later. If anything in that bookkeeping fails, the call still runs exactly once with its own result. The mod never blocks, rewrites or approves a call.

</details>

<details>
<summary><b>What does the mod reach on my machine?</b></summary>

It hooks the start of each session (to add `/file-tree` and open the pane), each tool call (to highlight the files it names and report git operations), each prompt you send (to pass the selected file and reveal `@path` files), a working directory change, a theme change in `/config`, the `/file-tree` command, and the pane's drawing, scrolling and input.

It reads directory listings, the file you preview, your `theme` setting through `/config` (and, for a custom theme, its file in `~/.claude/themes/`, or under `CLAUDE_CONFIG_DIR`), and your font folders (`~/Library/Fonts` and `/Library/Fonts` on macOS, the Windows font folders, `fc-list` on Linux). It runs `git` (read-only, with every program a repository's own config can name turned off: fsmonitor, clean and process filters, textconv, external diff and signature checks; it reads the filter names with `git config` first, skips git in a repository whose filter names it can't turn off, and never runs git inside a submodule's working tree), `wc -l` on untracked files, `du -sk` for folder sizes, `uname -s`, `herdr --version` at session start inside herdr, and, when it finds a Nerd Font, `ps` with `sh -c 'echo $PPID'` to learn when your terminal started. When you ask, it runs `test -x` on macOS and Linux to check that a file isn't executable, then `open`, `xdg-open` or PowerShell's `Start-Process` for the default app, `qlmanage -p` and `killall qlmanage` for Quick Look, `tmux`, `herdr` or `xdg-terminal-exec` for an editor or diff tool, and the commands you set in **Open with**, **Edit with** and **Diff with**. It reads the `HOME`, `CLAUDE_CONFIG_DIR`, `VISUAL`, `EDITOR`, `TMUX`, `HERDR_ENV`, `HERDR_PANE_ID`, `SSH_CONNECTION`, `SSH_TTY`, `OS`, `LOCALAPPDATA`, `SystemRoot` and `USERPROFILE` environment variables.

It never writes files, never reaches the network and never calls the model.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code mods docs](https://code.claude.com/docs/en/plugins/mods/overview)
- 📖 [Claude Code keybindings](https://code.claude.com/docs/en/keybindings)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=file-tree-pane) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=file-tree-pane) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=file-tree-pane)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
