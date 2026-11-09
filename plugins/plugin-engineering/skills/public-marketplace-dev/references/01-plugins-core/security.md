# Plugin security and trust

What a plugin can do on a user's machine, how to tell Anthropic's marketplaces from third-party ones, how to review a plugin before installing it, and how to remove one.

## Contents

- [Understand what a plugin can do](#understand-what-a-plugin-can-do)
- [Identify Anthropic's marketplaces by name](#identify-anthropics-marketplaces-by-name)
  - [Official marketplace names](#official-marketplace-names)
- [Review a plugin before you install](#review-a-plugin-before-you-install)
  - [Remove a plugin you no longer trust](#remove-a-plugin-you-no-longer-trust)
- [Recognize when Claude Code refuses or warns](#recognize-when-claude-code-refuses-or-warns)
  - [Trust warning before you install](#trust-warning-before-you-install)
  - [Untrusted marketplace sources and failed integrity checks](#untrusted-marketplace-sources-and-failed-integrity-checks)
- [Enforce plugin controls for your organization](#enforce-plugin-controls-for-your-organization)
- [Documentation References](#documentation-references)

An installed Claude Code plugin can execute arbitrary code on the user's machine with the user's privileges.

Plugins are installed from a marketplace, which is the catalog Claude Code fetches them from. Some marketplace names are [reserved for Anthropic's own marketplaces](#marketplace-tiers), and every other marketplace is third-party. A marketplace's name tells who publishes the catalog, not what each plugin in it does, so [review a plugin before installing it](#review-a-plugin-before-you-install) whichever marketplace it comes from.

This file applies when deciding whether to install a plugin, when reviewing tools before a team can use them, and when designing a plugin that users will review this way.

> **Note:** These cases are covered on other pages:
>
> * **Claude Code's own security model**: see [Security](https://code.claude.com/docs/en/security.md)

Start with [what a plugin can do](#understand-what-a-plugin-can-do) and [which marketplaces are Anthropic's](#marketplace-tiers), then [review the plugin before installing it](#review-a-plugin-before-you-install).

## Understand what a plugin can do

A plugin can carry content that runs code on the user's machine with the user's privileges, and content that enters Claude's context as instructions, so [review a plugin before installing it](#review-a-plugin-before-you-install). An installed plugin can do the following:

* **Hooks**: a plugin's [hooks](https://code.claude.com/docs/en/hooks.md) run as shell commands at points in Claude Code's lifecycle, such as before or after a tool call.
* **Monitors**: a plugin's [monitors](https://code.claude.com/docs/en/plugins/components.md#monitors) run as background shell commands that Claude Code starts on its own when the session starts, when the user reloads plugins, or the first time a named skill runs.
* **Mods**: a plugin's [mod](https://code.claude.com/docs/en/plugins/mods/overview.md) runs JavaScript inside Claude Code with the user's permissions. To list what a mod does before installing it, see [Decide whether to trust a mod](https://code.claude.com/docs/en/plugins/mods/overview.md#decide-whether-to-trust-a-mod).
* **MCP and LSP servers**: Claude Code connects to the [MCP servers](https://code.claude.com/docs/en/mcp.md) an enabled plugin declares and gives Claude their tools. A stdio MCP server runs as a process that Claude Code starts on the user's machine. Claude Code also starts the language servers the plugin declares.
* **`bin/` directory**: Claude Code adds each enabled plugin's `bin/` directory to the `PATH` of the Bash tool's shell, so Claude's Bash commands can run any executable there. A command that Claude runs with the [PowerShell tool](https://code.claude.com/docs/en/tools-reference.md#powershell-tool) gets those directories on its `PATH` when it runs outside the [sandbox](https://code.claude.com/docs/en/sandboxing.md), and not when it runs inside it.
* **Skills, commands, and agents**: these enter Claude's context as instructions, so they influence what Claude does with the tools it already has.
* **Updates**: when auto-update is on for the marketplace a plugin was installed from, Claude Code updates that plugin in the background, so the files that were reviewed can change on disk. [When auto-update runs](https://code.claude.com/docs/en/plugins/loading.md#when-auto-update-runs) has the timing. To turn auto-update on or off per marketplace, see [Keep plugins updated](https://code.claude.com/docs/en/plugins/install.md#keep-plugins-updated).

Claude Code's [permission rules](https://code.claude.com/docs/en/permissions.md) and [sandbox](https://code.claude.com/docs/en/sandboxing.md) cover the tool calls Claude makes, not the code a plugin runs by itself:

* **Hooks, monitors, and server processes**: command hooks and monitors are shell commands that run with the user's full permissions. Claude Code runs hooks, monitors, MCP servers, LSP servers, and the processes a [mod](https://code.claude.com/docs/en/plugins/mods/overview.md#what-a-mod-can-reach) starts outside the sandbox.
* **Claude's tool calls**: a call to one of the plugin's MCP tools, and a Bash command that runs an executable from the plugin's `bin/`, are tool calls, so the user's permission rules apply to them. For what a mod can do to a tool call, see [Decide whether to trust a mod](https://code.claude.com/docs/en/plugins/mods/overview.md#decide-whether-to-trust-a-mod).

Installing a plugin also enables it, unless its manifest or marketplace entry sets [`defaultEnabled: false`](https://code.claude.com/docs/en/plugins/install#choose-an-install-scope) and the user has not enabled it themselves.

To remove a plugin that is no longer trusted, see [Remove a plugin you no longer trust](#remove-a-plugin-you-no-longer-trust).

## Identify Anthropic's marketplaces by name

A marketplace's name places it in one of three tiers: official, community, or third-party. Claude Code accepts the official and community names only for marketplaces sourced from `github.com/anthropics/` repositories, so a third-party marketplace cannot present itself as an Anthropic one. A marketplace that a coworker or an organization publishes is third-party.

The table lists which names fall in each tier:

| Tier | Which marketplaces |
| :- | :- |
| Official | The [official marketplace names](#official-marketplace-names), such as `claude-plugins-official` |
| Community | `claude-community`, `claude-plugins-community`, and `healthcare` |
| Third-party | Every other marketplace |

### Official marketplace names

These marketplace names make up the official tier:

* `claude-plugins-official`
* `claude-code-marketplace`
* `claude-code-plugins`
* `anthropic-marketplace`
* `anthropic-plugins`
* `agent-skills`
* `anthropic-agent-skills`
* `life-sciences`
* `knowledge-work-plugins`
* `claude-for-legal`
* `claude-for-financial-services`
* `financial-services-plugins`
* `first-party-plugins`
* `claude-tag-plugins`

## Review a plugin before you install

Before installing a plugin, check what it adds and where it comes from.

**1. Check the marketplace's source**

In the shell, run `claude plugin marketplace list` to print the source each marketplace was added from, such as a GitHub repository or a directory.

**2. Read the details pane**

In a Claude Code session, run `/plugin` and select the plugin. The details pane shows a **Will install** section listing the plugin's commands, agents, skills, hooks, and MCP and LSP servers. For a plugin Anthropic has no published component data for, the section shows what the marketplace entry declares, or a note: `Components will be discovered at installation` for a plugin stored inside the marketplace, or `Component summary not available for remote plugin` for one fetched from elsewhere.

**3. Read the plugin's source**

In the details pane, select **Open homepage** or **View on GitHub** below the install options. If the pane offers neither, open the marketplace repository found in the first step. Find the plugin's directory there. The **Will install** section shows that a hook exists but not what it runs, so read these files in the plugin's directory:

* **`hooks/hooks.json`**: the command each hook runs
* **`.mcp.json`**: each server's command or URL
* **`bin/`**: every file in the directory

**4. List what the plugin contains**

Clone the repository that holds the plugin's directory, then run `claude --plugin-dir <plugin directory> plugin details <plugin name>` in the shell to see what Claude Code finds in it. The command reads the plugin's files without starting a session and prints a `Component inventory` listing the plugin's skills and commands, agents, hooks with each hook's event, and MCP and LSP servers.

After installing a plugin, run `claude plugin details <plugin name>` in the shell to print the same `Component inventory` for the installed copy under `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`.

### Remove a plugin you no longer trust

In the shell, run [`claude plugin uninstall <plugin>`](https://code.claude.com/docs/en/plugins/cli-reference#plugin-uninstall) with the `--scope` the plugin was installed at. Then check what the uninstall removed and what it left:

* **Persistent data**: by default, when that was the last scope the plugin was installed at, uninstalling also deletes the plugin's persistent data directory. For `--keep-data` and the other cases where it stays, see [plugin uninstall](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-uninstall).
* **Cached files**: the plugin's files stay on disk under `~/.claude/plugins/cache/` for 14 days before a [background sweep removes them](https://code.claude.com/docs/en/plugins/loading.md#cleanup-of-previous-versions). After the last plugin is uninstalled, orphaned directories stay until another plugin is installed. To delete the files now, remove the plugin's directory under `~/.claude/plugins/cache/<marketplace>/<plugin>/` manually.
* **The marketplace**: if the marketplace's owner is not trusted either, [remove the marketplace](https://code.claude.com/docs/en/plugins/install.md#manage-marketplaces) too, which uninstalls every plugin installed from it.

## Recognize when Claude Code refuses or warns

The details pane opened from the **Discover** or **Marketplaces** tab in `/plugin` shows the same trust warning for each plugin. Claude Code refuses instead of warning in cases such as those under [Untrusted marketplace sources and failed integrity checks](#untrusted-marketplace-sources-and-failed-integrity-checks).

### Trust warning before you install

The warning reads the same whatever marketplace the plugin comes from:

```text theme={null}
Make sure you trust a plugin before installing, updating, or using it. Anthropic does not control what MCP servers, files, or other software are included in plugins and cannot verify that they will work as intended or that they won't change. See each plugin's homepage for more information.
```

If the organization sets `pluginTrustMessage` in [managed settings](https://code.claude.com/docs/en/plugins/org.md), Claude Code appends that text to the warning.

### Untrusted marketplace sources and failed integrity checks

Claude Code refuses to load a marketplace or to install a plugin in these cases, each with its own error message:

* **Untrusted marketplace source**: when a marketplace uses an official or community name but its source is outside `github.com/anthropics/`, Claude Code stops loading the marketplace and the plugins installed from it. The error is [Marketplace is registered from an untrusted source](https://code.claude.com/docs/en/errors.md#marketplace-is-registered-from-an-untrusted-source).

## Enforce plugin controls for your organization

With [managed settings](https://code.claude.com/docs/en/plugins/org.md), an administrator can enforce these plugin controls:

* Allowlist or blocklist marketplace sources
* Force-enable plugins
* Turn off the `--plugin-dir` and `--plugin-url` flags and the `CLAUDE_CODE_PLUGIN_DIRS` variable
* Limit hooks to those from managed settings and force-enabled plugins

The [control matrix](https://code.claude.com/docs/en/plugins/org.md#control-matrix) says what each key does and does not cover.

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/security
- https://code.claude.com/docs/en/security.md — Claude Code's own security model
- https://code.claude.com/docs/en/hooks.md — hooks reference
- https://code.claude.com/docs/en/plugins/components.md — plugin components, including monitors
- https://code.claude.com/docs/en/plugins/mods/overview.md — mods, what a mod can reach, and deciding whether to trust one
- https://code.claude.com/docs/en/mcp.md — MCP servers
- https://code.claude.com/docs/en/tools-reference.md — tools reference, including the PowerShell tool
- https://code.claude.com/docs/en/sandboxing.md — the sandbox
- https://code.claude.com/docs/en/plugins/loading.md — when auto-update runs and cleanup of previous versions
- https://code.claude.com/docs/en/plugins/install.md — install and manage plugins and marketplaces, scopes, keeping plugins updated, reviewing the details pane before choosing a scope
- https://code.claude.com/docs/en/permissions.md — permission rules
- https://code.claude.com/docs/en/plugins/cli-reference.md — `claude plugin uninstall` and other CLI commands
- https://code.claude.com/docs/en/plugins/org.md — managed settings for plugins and the control matrix
- https://code.claude.com/docs/en/errors.md — error reference, including the untrusted marketplace source error
