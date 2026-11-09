# Code intelligence plugins

How a language server plugin lets Claude see type errors after edits and navigate code by symbol, and what each choice in the LSP plugin recommendation dialog does.

## Contents

- [Overview](#overview)
- [Install a code intelligence plugin](#install-a-code-intelligence-plugin)
- [See what Claude gains](#see-what-claude-gains)
  - [Read the diagnostics yourself](#read-the-diagnostics-yourself)
- [Accept or dismiss the recommendation dialog](#accept-or-dismiss-the-recommendation-dialog)
  - [When the recommendation dialog appears](#when-the-recommendation-dialog-appears)
  - [Respond to the recommendation dialog](#respond-to-the-recommendation-dialog)
  - [Turn recommendations back on](#turn-recommendations-back-on)
- [Troubleshoot code intelligence](#troubleshoot-code-intelligence)
- [Add a language without an official plugin](#add-a-language-without-an-official-plugin)
- [Documentation References](#documentation-references)

## Overview

A code intelligence plugin gives Claude the live diagnostics and go-to-definition that an editor has. Claude then catches type errors and missing imports that its own edits introduce before the user runs a build, and finds definitions and references by symbol instead of by text search.

Each plugin connects Claude Code to a language server for one language through the Language Server Protocol (LSP). The user installs the plugin from Anthropic's official marketplace and the language server binary on their machine.

> **Note:** Code intelligence plugins work in terminal sessions. In [cloud sessions](https://code.claude.com/docs/en/claude-code-on-the-web.md), Claude Code doesn't start plugin language servers, so Claude gets no diagnostics or code navigation there. To write a language server plugin, or to connect a language server that has no plugin, read [LSP servers in plugin components](https://code.claude.com/docs/en/plugins/components.md#lsp-servers).

If the user already saw an **LSP plugin recommendation** dialog, read [Accept or dismiss the recommendation dialog](#accept-or-dismiss-the-recommendation-dialog) for what each choice does.

## Install a code intelligence plugin

A code intelligence plugin tells Claude Code which command starts the language server and which file extensions it handles. It doesn't include the language server. Install the language server binary first, then the plugin, then confirm the server starts.

**1. Install the language server binary**

After installing the binary, confirm it's on the `PATH` of the shell `claude` is started from, for example with `which typescript-language-server`, or `Get-Command typescript-language-server` in PowerShell.

**3. Confirm the server starts**

The language server starts the first time Claude edits a file with one of the plugin's extensions. To see it work, introduce a type error in a file of that language and then fix it. Then check the conversation for a diagnostics line:

* **A diagnostics line appears**: `Found N new diagnostic issues in M files (ctrl+o to expand)` under the edit that introduced the error means the server started.
* **No diagnostics line appears**: run `/plugin` and open the **Errors** tab. A row reading `Executable not found in $PATH: "<binary>"` names the binary to install. If the tab has no such row, read [Troubleshoot code intelligence](#troubleshoot-code-intelligence).

After a missing binary is installed, Claude Code tries again the next time Claude edits a matching file. If the binary was installed into a directory that isn't on the `PATH` of the shell `claude` was started from, start a new session from a shell where it is.

## See what Claude gains

With a language server running, Claude gains diagnostics and code navigation:

* **Diagnostics after edits**: each time Claude edits or writes a file the server handles, Claude gets the errors and warnings the server reports. It sees a type error, missing import, or syntax error it introduced without running a compiler.
* **Code navigation**: Claude gets an `LSP` tool that looks up symbols through the server instead of searching text for them. The tool is read-only. For what Claude can look up with the tool and how permissions apply to it, read [LSP tool behavior](https://code.claude.com/docs/en/tools-reference.md#lsp-tool-behavior).

### Read the diagnostics yourself

After Claude edits a file the server handles, the conversation shows only the `Found N new diagnostic issues` summary. To read the issues themselves, the user presses **Ctrl+O**.

## Accept or dismiss the recommendation dialog

If a language server binary is already on the user's `PATH` and the plugin that uses it isn't installed, Claude Code offers to install the plugin in a dialog titled **LSP plugin recommendation**.

### When the recommendation dialog appears

The **LSP plugin recommendation** dialog can appear after Claude edits a file. These conditions decide whether it appears and which plugin it offers:

* **A plugin matches the file**: one of the marketplaces the user has added, or the official marketplace Claude Code registered for them, lists a code intelligence plugin for that file's extension, and the plugin's binary is installed.
* **Official first**: when more than one marketplace offers a plugin for the extension, the dialog offers the official marketplace's plugin.
* **Once per session**: the dialog appears at most once in a session, for the first matching file Claude edits.
* **Not for cloud sessions**: the dialog never appears when the terminal is attached to a cloud session, such as one started with [`claude --cloud`](https://code.claude.com/docs/en/claude-code-on-the-web#from-terminal-to-cloud).

### Respond to the recommendation dialog

The **LSP plugin recommendation** dialog names the plugin and offers these choices:

* **Yes, install**: Claude Code installs the plugin for the user account and prints `<plugin> installed · restart to apply`. Start a new session to load the server.
* **No, not now**: the dialog closes, and a later session can offer the plugin again. Pressing **Esc** does the same.
* **Never for this plugin**: the dialog stops appearing for that plugin and still appears for others.
* **Disable all LSP recommendations**: the dialog stops appearing for every language.

If no option is chosen, Claude Code closes the dialog after 30 seconds and counts that as ignored. The count is kept across sessions. After five ignored dialogs, Claude Code stops recommending plugins, the same as if **Disable all LSP recommendations** had been chosen.

### Turn recommendations back on

The **LSP plugin recommendation** dialog stops appearing after **Disable all LSP recommendations** is chosen or the dialog is ignored five times.

* **Disabled or ignored five times**: to turn it back on in either case, remove the `lspRecommendationDisabled` and `lspRecommendationIgnoredCount` keys from `~/.claude.json`, Claude Code's own configuration file.
* **Never for this plugin**: to have a plugin offered again after **Never for this plugin** was chosen, remove its `name@marketplace` id from the `lspRecommendationNeverPlugins` list in the same file.

## Troubleshoot code intelligence

The plugins troubleshooting page covers the symptoms specific to code intelligence plugins under [Language server doesn't start, uses too much memory, or reports wrong diagnostics](https://code.claude.com/docs/en/plugins/troubleshooting.md#language-server-doesnt-start):

* **The language server doesn't start**: `Executable not found in $PATH` appears in the **Errors** tab of `/plugin`, or Claude never reports diagnostics for the language.
* **High memory use**: memory use increases while the server indexes the project.
* **False positive diagnostics in a monorepo**: diagnostics report imports as unresolved when they aren't.

## Add a language without an official plugin

If a language isn't in the [table of official plugins](#install-a-code-intelligence-plugin), a language server can still be connected:

1. Write a plugin with an `.lsp.json` file that names the server command and the file extensions it handles.
2. Load the plugin with [`--plugin-dir`](https://code.claude.com/docs/en/plugins/cli-reference#flags-that-load-a-plugin-for-one-session) or publish it to a marketplace.

For the file's fields and a worked example, read [LSP servers in plugin components](https://code.claude.com/docs/en/plugins/components.md#lsp-servers).

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/code-intelligence
- https://code.claude.com/docs/en/claude-code-on-the-web.md: cloud sessions, where plugin language servers don't start
- https://code.claude.com/docs/en/claude-code-on-the-web: starting a cloud session from the terminal with `claude --cloud`
- https://code.claude.com/docs/en/plugins/components.md: LSP servers in plugin components, the `.lsp.json` fields and a worked example
- https://code.claude.com/docs/en/tools-reference.md: LSP tool behavior and how permissions apply to it
- https://code.claude.com/docs/en/plugins/troubleshooting.md: language server and other plugin load errors
- https://code.claude.com/docs/en/plugins/cli-reference: flags that load a plugin for one session, such as `--plugin-dir`
- https://code.claude.com/docs/en/plugins/install.md: scopes, updates, and uninstalling
