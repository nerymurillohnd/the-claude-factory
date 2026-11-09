# Install and manage plugins

How users install Claude Code plugins from a marketplace on each surface, choose an install scope, and update or remove them later. Use it to write accurate install, update and uninstall instructions for a marketplace's users and to predict what they see.

## Contents

- [Overview](#overview)
- [Install a plugin](#install-a-plugin)
  - [Choose an install scope](#choose-an-install-scope)
  - [JetBrains, non-interactive runs, and the Agent SDK](#jetbrains-non-interactive-runs-and-the-agent-sdk)
  - [Install from your shell](#install-from-your-shell)
- [Add a marketplace](#add-a-marketplace)
  - [Add a marketplace and install in one command](#add-a-marketplace-and-install-in-one-command)
    - [Add and install in a session](#add-and-install-in-a-session)
    - [Add and install from your shell](#add-and-install-from-your-shell)
  - [Add a private marketplace](#add-a-private-marketplace)
- [Manage installed plugins](#manage-installed-plugins)
  - [Uninstall a plugin the project enables](#uninstall-a-plugin-the-project-enables)
  - [See what an installed plugin adds to your sessions](#see-what-an-installed-plugin-adds-to-your-sessions)
  - [Find plugins you no longer use](#find-plugins-you-no-longer-use)
  - [Plugins with dependencies](#plugins-with-dependencies)
  - [Manage plugins from your shell](#manage-plugins-from-your-shell)
- [Keep plugins updated](#keep-plugins-updated)
  - [Turn auto-update on or off for a marketplace](#turn-auto-update-on-or-off-for-a-marketplace)
  - [Update plugins now](#update-plugins-now)
- [Manage marketplaces](#manage-marketplaces)
- [Documentation References](#documentation-references)

## Overview

Installing a plugin adds its skills, agents, hooks, and MCP servers to Claude Code on the user's machine.

This file covers using plugins on one's own machine or account, whether in the terminal, the desktop app, an IDE, or a cloud session: installing, choosing a scope, adding marketplaces, and keeping plugins updated.

> **Note:** These cases are covered on other pages:
>
> * **The user is on claude.ai chat or Cowork, not Claude Code**: read [Plugins on claude.ai and in Cowork](https://claude.com/docs/plugins/overview)
> * **Claude Code printed an error**: find it in [Troubleshoot plugins](https://code.claude.com/docs/en/plugins/troubleshooting.md)

Start with [Install a plugin](#install-a-plugin). If an install command's `@` name isn't `claude-plugins-official`, [add that marketplace](#add-a-marketplace) first.

## Install a plugin

As an example, this section installs [`commit-commands`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/commit-commands) from [Anthropic's official marketplace](https://code.claude.com/docs/en/plugins/anthropic-marketplaces.md), which adds commands for committing, pushing, and opening pull requests.

The same steps install any other plugin: substitute its name and its marketplace's name wherever `commit-commands` and `claude-plugins-official` appear. If that plugin comes from a different marketplace, [add the marketplace](#add-a-marketplace) first.

Each tab below is one surface where Claude Code runs.

> [tab] Terminal
>
> Start Claude Code with `claude` in the project, then:
>
> **1. Open the plugin's details with the install command**
>
> Run `/plugin install` with the plugin's name and marketplace. In a session, this command doesn't install right away: it opens the `/plugin` panel on that plugin's details so the user can review it and choose a scope first.
>
> ```text theme={null}
> /plugin install commit-commands@claude-plugins-official
> ```
>
> To browse instead, run `/plugin` with no plugin name: the panel opens on the **Discover** tab, which lists the plugins from the user's marketplaces; type to search, then press **Enter** on a plugin to open its details.
>
> **2. Review what the plugin adds**
>
> The details pane shows the plugin's description. It can also show:
>
> * **Will install**: the commands, agents, skills, hooks, and MCP and LSP servers the plugin adds.
>
> Plugins from a local or custom marketplace can show `Components will be discovered at installation` instead.
>
> A plugin can run hooks and MCP servers, so read the pane before installing. Read [Plugin security and trust](https://code.claude.com/docs/en/plugins/security.md).
>
> **3. Choose a scope**
>
> Select one of the three install options:
>
> * **Install for you (user scope)**: the user gets the plugin in every project on this machine
> * **Install for all collaborators on this repository (project scope)**: it's enabled for everyone who works in this repository
> * **Install for you, in this repo only (local scope)**: the user gets it in this repository only
>
> [Choose an install scope](#choose-an-install-scope) says which settings file each one writes to and which applies when the same plugin is set at more than one.
>
> After a scope is selected, Claude Code installs the plugin along with any dependencies it declares, then prints an install summary.
>
> **4. Read the install summary**
>
> The last sentence of the summary says whether the plugin is usable in this session yet:
>
> * **Active now**: `Plugin is now active.` No reload is needed.
> * **Active, but a server needs setup**: `Plugin is now active.` is followed by `Its bundled MCP server needs configuration before it can start`. The plugin's [bundled MCP server](https://code.claude.com/docs/en/plugins/components.md#include-a-packaged-mcpb-server) can't start until its options are set. Select the plugin on the **Installed** tab in `/plugin` and choose **Configure** to set the server's options.
> * **Reload needed**: `Run /reload-plugins to apply.` The panel closes and Claude Code runs that reload automatically. If the reload would [invalidate the prompt cache](https://code.claude.com/docs/en/prompt-caching.md#enabling-or-disabling-a-plugin), it warns and leaves the plugin pending instead. Run `/reload-plugins --force` to activate it anyway, which costs one uncached request.
> * **Load failed**: `The plugin couldn't be loaded`. Open the **Errors** tab in `/plugin` for the reason, then read [After install: plugin not working](https://code.claude.com/docs/en/plugins/troubleshooting.md#plugin-installed-but-not-working).
>
> **5. Confirm the plugin works**
>
> Type `/` and look for the plugin's skills under its name, in the form `/<plugin>:<skill>`. For `commit-commands`, `/commit-commands:commit` appears. Two other places list the plugin too:
>
> * Open the **Installed** tab in `/plugin`, which lists the plugin with its scope.
> * In the shell, run `claude plugin list`, which prints the same list with `Version`, `Scope`, and `Status` lines.
>
> If `/commit-commands:commit` doesn't appear, read [After install: plugin not working](https://code.claude.com/docs/en/plugins/troubleshooting.md#plugin-installed-but-not-working).
>
> Installing from any other marketplace requires one extra step first: [add the marketplace](#add-a-marketplace). Claude Code adds Anthropic's official marketplace automatically the first time an interactive terminal session starts, which is why the example skips that step. For a plugin found on [claude.com/marketplace](https://claude.com/marketplace), its **Claude Code** button copies the install command in its [shell form](#install-from-your-shell), `claude plugin install <name>@claude-plugins-official`.

> [tab] Desktop app
>
> In a local or SSH session in the desktop app's **Code** tab:
>
> **1. Open the plugin browser**
>
> Click the **+** button next to the prompt box and select **Add plugins**. If the **+** menu shows **Plugins** instead of **Add plugins**, select **Plugins**, then **Browse plugins**. The plugin browser opens with the plugins from the user's marketplaces.
>
> **2. Select the plugin**
>
> Find `commit-commands` and select it.
>
> **3. Choose a scope**
>
> Choose a [scope](#choose-an-install-scope): the user account, this project, or local-only.
>
> To enable, disable, or uninstall a plugin later, read [Install plugins in the desktop app](https://code.claude.com/docs/en/desktop.md#install-plugins).

> [tab] VS Code
>
> In the Claude Code panel in VS Code:
>
> **1. Open Manage plugins**
>
> Type `/plugins` in the prompt box to open **Manage plugins**.
>
> **2. Install the plugin**
>
> On the **Plugins** tab, search for `commit-commands` and click **Install**. If the tab lists no plugins, add `anthropics/claude-plugins-official` on the **Marketplaces** tab first.
>
> **3. Choose a scope**
>
> Choose a [scope](#choose-an-install-scope): **Install for you**, **Install for this project**, or **Install locally**.
>
> Changes apply to open sessions without a restart. Read [Manage plugins in VS Code](https://code.claude.com/docs/en/vs-code.md#manage-plugins).

> [tab] Cloud session
>
> A [cloud session](https://code.claude.com/docs/en/cloud-environments.md), including [the browser at claude.ai/code](https://code.claude.com/docs/en/claude-code-on-the-web.md), has no plugin browser and doesn't load the plugins installed on the user's own machine or the ones the repository's `.claude/settings.json` turns on. For plugins an organization distributes through managed settings, read [Manage plugins for your organization](https://code.claude.com/docs/en/plugins/org.md).
>
> Read [which parts of your setup are also available in a cloud session](https://code.claude.com/docs/en/cloud-environments.md#what-carries-over-from-your-setup) for the rest of the setup.

### Choose an install scope

A plugin's install scope decides who gets the plugin and which settings file records it as enabled:

* **User scope**: the plugin is enabled for the user in every project on this machine. The entry goes in `enabledPlugins` in `~/.claude/settings.json`.
* **Project scope**: the plugin is enabled for everyone who works in this repository. The entry goes in `.claude/settings.json`, which is committed. Committing that entry turns the plugin on for collaborators but doesn't download it to their machines, so each collaborator also runs `claude plugin install <name>@<marketplace> --scope project` once; read [Enabled in project settings but not installed](https://code.claude.com/docs/en/plugins/loading.md#enabled-in-project-settings-but-not-installed).
* **Local scope**: the plugin is enabled for the user in this repository only. The entry goes in `.claude/settings.local.json`.

A plugin author can set a plugin to start turned off, through the [`defaultEnabled`](https://code.claude.com/docs/en/plugins/manifest-reference#defaultenabled) field. Such a plugin is installed but stays off until the user turns it on with `claude plugin enable <name>` in the shell, or from the **Installed** tab of `/plugin` in a session.

When the same plugin is set at several scopes, the local setting overrides the project setting, and the project setting overrides the user setting. Read [Find where a plugin is enabled](https://code.claude.com/docs/en/plugins/loading.md#find-where-a-plugin-is-enabled) for the full rule.

The terminal, the desktop app's local sessions, and the VS Code extension on one computer read the same settings files, so a plugin installed at user scope in any of them is available in the other two.

### JetBrains, non-interactive runs, and the Agent SDK

Some places Claude Code runs have no plugin browser of their own:

* **JetBrains IDEs**: the JetBrains plugin runs Claude Code in the IDE's terminal, so use the **Terminal** tab's steps there.
* **`claude -p` and other non-interactive runs**: `/plugin` doesn't run, and Claude replies `/plugin isn't available in this environment.` Plugins already installed do load. Install and manage them from the shell with [`claude plugin` commands](#install-from-your-shell).
* **Agent SDK**: load plugins through the SDK's plugin option. Read [Load plugins in the Agent SDK](https://code.claude.com/docs/en/agent-sdk/plugins.md).

If Claude Code reports that a plugin enabled in the repository's `.claude/settings.json` isn't installed, read [Enabled in project settings but not installed](https://code.claude.com/docs/en/plugins/loading.md#enabled-in-project-settings-but-not-installed).

> **Tip:** To test a copy of a plugin on disk as its author, start Claude Code from the shell with `--plugin-dir` to load it for one session instead of installing it. Read [Flags that load a plugin for one session](https://code.claude.com/docs/en/plugins/cli-reference.md#flags-that-load-a-plugin-for-one-session).

### Install from your shell

Run `claude plugin install` in the shell to install a plugin without starting a Claude Code session, for example from a setup script.

* **Scope**: user scope by default. Pass `--scope project` or `--scope local` to change it.
* **When the plugins load**: plugins it installs load the next time Claude Code starts, or after `/reload-plugins` runs in a session that's already open.
* **The marketplace on a new machine**: on a machine where no one has opened an interactive Claude Code session yet, the official marketplace isn't registered, so a script that installs from it runs `claude plugin marketplace add anthropics/claude-plugins-official` before the install. Read [Add and install from your shell](#add-and-install-from-your-shell).

```bash theme={null}
claude plugin install formatter@your-org --scope project
```

The command prints `Successfully installed plugin: formatter@your-org (scope: project)` when it finishes.

For the other `claude plugin install` flags, read [plugin install](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-install).

## Add a marketplace

This section applies only when the wanted plugin isn't in Anthropic's official marketplace, for example one a coworker published or one from Anthropic's community marketplace.

A marketplace is a catalog of plugins, and Claude Code has to know about a marketplace before installing from it. A marketplace is added once. After that, its plugins appear on the **Discover** tab and install with `/plugin install <plugin>@<marketplace>` in a session or `claude plugin install <plugin>@<marketplace>` in the shell, where `<marketplace>` is the name the marketplace registered under. To do both in one step, read [Add a marketplace and install in one command](#add-a-marketplace-and-install-in-one-command).

In a Claude Code session, run `/plugin marketplace add` followed by the marketplace's source: a GitHub repository, a git repository on any host, a local directory or file, or a hosted `marketplace.json`.

| Source | What you type | Example |
| :- | :- | :- |
| GitHub repository | `owner/repo`. Add `#ref` to pin a branch or tag. | `/plugin marketplace add anthropics/claude-plugins-official`, or `/plugin marketplace add your-org/plugins#v1.2.0` to pin the `v1.2.0` tag |
| Local directory or file | A relative or absolute path to a directory that holds `.claude-plugin/marketplace.json`, or to the JSON file itself. Start a relative path with `./` or `../`, because Claude Code reads a bare `name/name` as a GitHub repository. | `/plugin marketplace add ./my-marketplace` |

From the shell, `claude plugin marketplace add` takes the same sources.

> **Tip:** `/plugin market` also works as a shorter form of `/plugin marketplace`.

Include the `https://` prefix on every URL, or use the `git@host:path` form for SSH. A bare `gitlab.example.com/your-group/your-marketplace.git` is read as GitHub `owner/repo` shorthand and rejected.

When the command succeeds, it prints `Successfully added marketplace: <name>`, and the marketplace's plugins appear on the **Discover** tab the next time `/plugin` opens, with no reload needed. If it fails, match the error message in [Troubleshoot plugins](https://code.claude.com/docs/en/plugins/troubleshooting.md#add-a-marketplace).

### Add a marketplace and install in one command

To install a plugin from a marketplace not added yet, name the marketplace source with `--marketplace` on the install command, in a session or from the shell. The source takes [the same forms as `/plugin marketplace add`](#add-a-marketplace), such as GitHub `owner/repo`, a git URL, or a local path. Give the plugin name by itself, without an `@marketplace` suffix.

#### Add and install in a session

Run `/plugin install` in a Claude Code session with the plugin and the source. Requires Claude Code v2.1.275 or later. In a session, the source can't contain spaces.

```text theme={null}
/plugin install deploy-helper --marketplace your-org/plugins
```

If that marketplace isn't added yet, Claude Code shows the source it resolved and asks for confirmation before adding it. Once the marketplace is added, the plugin's details open and the user chooses an [installation scope](#install-a-plugin). If the source matches a marketplace already added, Claude Code skips the confirmation and opens the plugin's details in that marketplace.

#### Add and install from your shell

In the shell, without starting a session, run `claude plugin install` with the plugin and the source. Requires Claude Code v2.1.292 or later.

```bash theme={null}
claude plugin install deploy-helper --marketplace your-org/plugins
```

The shell command adds the marketplace without a confirmation step. A marketplace already added from that source is reused. A new one is added under the same [organization policy checks](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install) as `claude plugin marketplace add`, and is declared in user settings even when `--scope project` is passed.

If that marketplace isn't added yet, the command prints `Successfully added marketplace: <name> (declared in user settings)` and then [installs the plugin](#install-from-your-shell).

### Add a private marketplace

A private marketplace is one in a repository that needs credentials to clone, on GitHub or any other git host. It is added with the same `/plugin marketplace add` or `claude plugin marketplace add` command as a public one. Claude Code clones it with the git credentials already on the machine and never prompts, so each way of connecting has a requirement:

* **SSH**: the host must already be in the `known_hosts` file and the key must work without a passphrase prompt. If the git setup names an SSH program in `GIT_SSH_COMMAND`, `GIT_SSH`, or the git config's `core.sshCommand`, Claude Code runs that program.
* **GitHub `owner/repo` shorthand**: Claude Code checks whether the SSH key authenticates to `github.com`, then clones over SSH if it does and over HTTPS if it doesn't. Set [`CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`](https://code.claude.com/docs/en/env-vars#variables) to skip that check and always clone over HTTPS.

The same credentials apply when running `/plugin install`, `/plugin marketplace update`, and `claude plugin update`.

## Manage installed plugins

The **Installed** tab in `/plugin` lists installed plugins with actions to enable, disable, update, or uninstall each one. In a Claude Code session, run `/plugin` and press **Tab** to reach it, or run `/plugin enable`, `/plugin disable`, or `/plugin uninstall` to open the panel and make that change there. Disabled plugins are grouped under a collapsed header at the bottom of the list. Use these keys on the list:

* Type to filter by name or description.
* Press **Space** to enable or disable the selected plugin, and **f** to favorite it.
* Press **Enter** to open a plugin's details.

A plugin's details menu offers **Disable plugin** or **Enable plugin**, **Update now**, and **Uninstall**. Two more items appear for plugins that take settings, and a plugin can show both:

* **Configure options**: shown when the plugin's manifest declares [`userConfig` options](https://code.claude.com/docs/en/plugins/manifest-reference#user-configuration). Opens the dialog for those options
* **Configure**: shown when the plugin includes a [bundled MCP server](https://code.claude.com/docs/en/plugins/components.md#include-a-packaged-mcpb-server). Sets that server's own `user_config` settings

When the `/plugin` panel closes with pending changes made in it, Claude Code runs `/reload-plugins` automatically to apply them. If the reload would [invalidate the prompt cache](https://code.claude.com/docs/en/prompt-caching.md#enabling-or-disabling-a-plugin), it warns and leaves the changes pending instead. Run `/reload-plugins --force` to apply them anyway.

### Uninstall a plugin the project enables

When **Uninstall** is chosen for a plugin that this repository's `.claude/settings.json` enables, whether from the **Installed** tab or with `/plugin uninstall`, Claude Code asks whether to disable it for the user or uninstall it for everyone:

* **Disable for me**: press **y**. Claude Code writes `false` for the plugin in the user's `.claude/settings.local.json` and leaves it installed for the project.
* **Uninstall for everyone**: press **u**. Claude Code removes the plugin from the shared `.claude/settings.json`.

### See what an installed plugin adds to your sessions

In the shell, run `claude plugin details <name>` for an installed plugin. The `Always-on` line is the number of tokens the plugin adds to every session where it's enabled, and the per-component rows show which skill or agent contributes most. For the full output and what each figure means, read [Measure what a plugin costs](https://code.claude.com/docs/en/plugins/measure.md#measure-what-a-plugin-costs).

### Find plugins you no longer use

On the **Installed** tab in `/plugin`, plugins the user installed and hasn't used recently appear under a **Not used recently** header, and each plugin's details show a **Last used** line. Use that header and that line to find plugins that still add startup and context cost, then disable or uninstall them.

### Plugins with dependencies

A plugin can declare other plugins that it depends on. When such a plugin is installed, disabled, or uninstalled from a marketplace, Claude Code acts on those dependencies too:

* **Install**: Claude Code also installs and enables the plugin's declared dependencies at the same scope. The success message lists them.
* **Enable**: Claude Code also enables the plugin's dependencies that are installed but disabled. If a declared dependency isn't installed, the enable fails and the message says to install it first.
* **Disable**: when another enabled plugin still needs the named plugin, Claude Code refuses and prints a chained command that disables both in the right order.
* **Uninstall**: auto-installed dependencies stay until `claude plugin prune` runs in the shell; read [plugin prune](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-prune).

If the plugin was loaded with `--plugin-dir` instead, read [Test a plugin and its dependency locally](https://code.claude.com/docs/en/plugins/dependencies.md#test-a-plugin-and-its-dependency-locally).

### Manage plugins from your shell

Plugins can also be managed without starting a Claude Code session. In the shell, run `claude plugin install`, `enable`, `disable`, or `uninstall` as ordinary terminal commands; they change the same settings the `/plugin` panel does. Each takes `--scope` to target one scope, and uses a default scope when it is omitted:

* `enable` and `disable` act on the most specific scope whose settings already list the plugin.
* `install` and `uninstall` act on user scope.

For example, these commands disable and re-enable a plugin, then uninstall it at project scope:

```bash theme={null}
claude plugin disable formatter@your-org
claude plugin enable formatter@your-org
claude plugin uninstall formatter@your-org --scope project
```

## Keep plugins updated

Plugins update automatically when the marketplace they came from has auto-update turned on. After a session starts, Claude Code refreshes those marketplaces and updates the on-disk copies of the plugins installed from them.

The running session keeps the versions it already loaded. After an update, the user sees `Plugin updated: <name> · Run /reload-plugins to apply`, and the next session loads the new versions automatically.

These are the auto-update defaults for each kind of marketplace:

* **On by default**: `claude-plugins-official` and the other [official marketplace names](https://code.claude.com/docs/en/plugins/security.md#official-marketplace-names) except `knowledge-work-plugins` and `first-party-plugins`, plus [marketplaces added from claude.ai](https://code.claude.com/docs/en/plugins/install#add-from-claude-ai).
* **Off by default**: every other marketplace, including the community marketplace, third-party marketplaces, and local development marketplaces.

For when auto-update runs, which plugins it skips, and the environment variables that turn it off, read [When auto-update runs](https://code.claude.com/docs/en/plugins/loading.md#when-auto-update-runs).

### Turn auto-update on or off for a marketplace

In a Claude Code session, run `/plugin` and go to the **Marketplaces** tab. Select the marketplace, then select **Enable auto-update** or **Disable auto-update**.

### Update plugins now

To update one plugin, open it on the **Installed** tab in `/plugin` during a session and select **Update now**, or run `claude plugin update <plugin>@<marketplace>` in the shell.

There's no command that updates every plugin at once. To update the plugins installed from one marketplace at once, go to the **Marketplaces** tab in `/plugin`, select the marketplace, and choose **Update marketplace**. That refreshes the marketplace's listing, updates the plugins installed from it, and reports any plugin it left for the user to update. A plugin with a [`command` source](https://code.claude.com/docs/en/plugins/marketplace-reference#command-plugin-source) or with a marketplace entry that sets a `headersHelper` command isn't updated this way; update it from its view on the **Installed** tab or with `claude plugin update <plugin>@<marketplace>`.

Running `claude plugin marketplace update` in the shell with no name refreshes every marketplace's listing but leaves installed plugins at their current versions.

## Manage marketplaces

The **Marketplaces** tab in `/plugin` lists every registered marketplace, along with its source. Select one to browse its plugins, update its listing, turn auto-update on or off, or remove it.

Marketplaces can also be listed, updated, and removed with commands, from the shell or inside a session:

| Action | In your shell | Inside a session |
| :- | :- | :- |
| List marketplaces | `claude plugin marketplace list` | `/plugin marketplace list` |
| Update a marketplace's listing | `claude plugin marketplace update <name>` | `/plugin marketplace update <name>` |
| Remove a marketplace | `claude plugin marketplace remove <name>` | `/plugin marketplace remove <name>` |

When a marketplace is removed, Claude Code uninstalls every plugin installed from it and removes their `enabledPlugins` entries from the settings files. The **Marketplaces** tab names those plugins before it asks for confirmation.

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/install
- https://claude.com/docs/plugins/overview: plugins on claude.ai and in Cowork
- https://code.claude.com/docs/en/plugins/troubleshooting.md: install and marketplace error messages with their fixes
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins/commit-commands: the `commit-commands` example plugin
- https://code.claude.com/docs/en/plugins/anthropic-marketplaces.md: Anthropic's official marketplace
- https://code.claude.com/docs/en/plugins/security.md: what to review before installing a plugin from an unknown marketplace, and the official marketplace names
- https://code.claude.com/docs/en/plugins/components.md: bundled (packaged MCPB) MCP servers
- https://code.claude.com/docs/en/prompt-caching.md: enabling or disabling a plugin and the prompt cache
- https://claude.com/marketplace: the public plugin marketplace site and its **Claude Code** install button
- https://code.claude.com/docs/en/desktop.md: install plugins in the desktop app
- https://code.claude.com/docs/en/vs-code.md: manage plugins in VS Code
- https://code.claude.com/docs/en/cloud-environments.md: cloud sessions and what carries over from the local setup
- https://code.claude.com/docs/en/claude-code-on-the-web.md: Claude Code in the browser at claude.ai/code
- https://code.claude.com/docs/en/plugins/org.md: manage plugins for an organization, restrict what users can install
- https://code.claude.com/docs/en/plugins/loading.md: why a plugin loaded, didn't load, or didn't change after an update; enabled-but-not-installed; where a plugin is enabled; when auto-update runs
- https://code.claude.com/docs/en/plugins/manifest-reference: `defaultEnabled` and `userConfig` fields
- https://code.claude.com/docs/en/agent-sdk/plugins.md: load plugins in the Agent SDK
- https://code.claude.com/docs/en/plugins/cli-reference.md: flags that load a plugin for one session, `plugin install`, `plugin prune`
- https://code.claude.com/docs/en/env-vars: `CLAUDE_CODE_PLUGIN_PREFER_HTTPS`
- https://code.claude.com/docs/en/plugins/measure.md: measure what a plugin costs
- https://code.claude.com/docs/en/plugins/dependencies.md: test a plugin and its dependency locally
- https://code.claude.com/docs/en/plugins/marketplace-reference: the `command` plugin source
- https://code.claude.com/docs/en/plugins/create.md: build your own plugin
