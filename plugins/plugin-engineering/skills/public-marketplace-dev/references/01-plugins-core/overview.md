# Plugins overview

What a Claude Code plugin is, when a plugin is needed instead of a standalone skill or MCP server, and which page covers installing or creating one.

## Contents

- [Understand what a plugin is](#understand-what-a-plugin-is)
  - [Decide whether you need a plugin](#decide-whether-you-need-a-plugin)
  - [What an enabled plugin adds to your sessions](#what-an-enabled-plugin-adds-to-your-sessions)
- [Get plugins from a marketplace](#get-plugins-from-a-marketplace)
  - [Make an installed plugin available in your session](#make-an-installed-plugin-available-in-your-session)
- [Tell Anthropic's marketplaces from third-party ones](#tell-anthropics-marketplaces-from-third-party-ones)
- [Understand install scopes](#understand-install-scopes)
- [Documentation References](#documentation-references)

A Claude Code plugin is a directory of skills, agents, hooks, MCP servers, or other components that Claude Code installs and loads as one unit. Most plugins come from a marketplace, which is a catalog that lists plugins and where to fetch each one. A plugin can also be loaded from a folder someone provides, or [built from scratch](https://code.claude.com/docs/en/plugins/create.md).

> **Note:** These cases are covered on other pages:
>
> * **The user works in claude.ai chat or Cowork, not Claude Code**: see [Plugins on claude.ai and in Cowork](https://claude.com/docs/plugins/overview)

To try a plugin, run `/plugin` in a Claude Code terminal session and install one from the **Discover** tab, which lists the plugins from the user's marketplaces. From there:

* [Install and manage plugins](https://code.claude.com/docs/en/plugins/install.md): the full install steps, scopes, and other surfaces
* [Create a plugin](https://code.claude.com/docs/en/plugins/create.md): build a new plugin
* [Decide whether you need a plugin](#decide-whether-you-need-a-plugin): whether a plugin is the right tool for the goal

## Understand what a plugin is

A plugin is a directory of components, usually with a manifest. The manifest, a JSON file at `.claude-plugin/plugin.json`, gives the plugin its name and can add a version, a description, and other [metadata](https://code.claude.com/docs/en/plugins/manifest-reference.md). The components are what the plugin adds to Claude Code, such as:

* [**Skills**](https://code.claude.com/docs/en/plugins/components.md#skills): `SKILL.md` instructions Claude loads when relevant, which the user can also run as a command
* [**Agents**](https://code.claude.com/docs/en/plugins/components.md#agents): subagent definitions Claude can delegate to
* [**Hooks**](https://code.claude.com/docs/en/plugins/components.md#hooks): commands Claude Code runs at points in its lifecycle, such as after every edit
* [**A hooks module**](https://code.claude.com/docs/en/plugins/mods/overview.md): hooks written as JavaScript functions, which can also draw panes and add commands. A plugin that has one is called a mod. Some mods are [built into Claude Code](https://code.claude.com/docs/en/plugins/mods/overview.md#mods-built-into-claude-code).
* [**MCP servers**](https://code.claude.com/docs/en/plugins/components.md#mcp-servers): tool servers Claude Code connects to while the plugin is enabled

The following diagram shows a plugin named `my-plugin` that holds a skill, an agent, hooks, and an MCP server, and what each file provides once the plugin loads.

![Diagram in two columns joined by five straight arrows. Left, the directory of a plugin named my-plugin, holding a manifest at .claude-plugin/plugin.json, skills/review/SKILL.md, agents/reviewer.md, hooks/hooks.json, .mcp.json, and other components. Right, what each file gives you in your session: the manifest sets the plugin name, my-plugin; the skill runs as /my-plugin:review; the agent file is a subagent Claude can delegate to; the hooks file holds hooks that run on lifecycle events; and .mcp.json adds an MCP server that gives Claude tools.](https://mintcdn.com/claude-code/2Q_GtOEovg5qaBem/images/plugin-directory.svg?fit=max\&auto=format\&n=2Q_GtOEovg5qaBem\&q=85\&s=f623b64e82713b830e48174f0a922888)

> **Description of the diagram:** Light off-white canvas with the bold centered title "A plugin is one directory of components". Two small gray bold column headings: "In the plugin directory" on the left and "In your session" on the right. Left: a light-gray panel with rounded corners and a tan outline, headed "my-plugin/" in bold monospace, holding five white rows in monospace, top to bottom: ".claude-plugin/plugin.json", "skills/review/SKILL.md", "agents/reviewer.md", "hooks/hooks.json", ".mcp.json"; below them, centered in gray, "and other components". From the right end of each white row, an unlabeled gray horizontal arrow points to a light-gray rounded box of the same height on the right, which has a bold label on its left and gray text right-aligned: "Plugin name" / "my-plugin" (monospace), "Skill" / "/my-plugin:review" (monospace), "Subagent" / "Claude can delegate to it", "Hooks" / "run on lifecycle events", "MCP server" / "gives Claude tools". "and other components" has no arrow and no right-hand box.

For every component type a plugin can hold, with an example of each, see [Plugin components](https://code.claude.com/docs/en/plugins/components.md). To see where each piece is located in a plugin's directory, use the [plugin explorer](https://code.claude.com/docs/en/plugins/components.md#explore-the-plugin-directory) on that page.

### Decide whether you need a plugin

Skills, subagents, hooks, and MCP servers all work on their own, without a plugin. A skill saved in `~/.claude/skills/`, for example, is available in every project on that machine. To set one up on its own, see [Skills](https://code.claude.com/docs/en/skills.md), [Subagents](https://code.claude.com/docs/en/sub-agents.md), [Hooks](https://code.claude.com/docs/en/hooks-guide.md), or [MCP](https://code.claude.com/docs/en/mcp.md).

Use a plugin when several skills, subagents, hooks, or MCP servers should be packaged as one unit. Installing a plugin gives a user a setup someone else built, with one command and updates from its marketplace. Making a plugin lets an author give their setup to teammates, install it in many projects, or publish versioned releases.

### What an enabled plugin adds to your sessions

An enabled plugin is part of every session, not only the sessions where it is used. Account for these consequences before installing one or shipping one to users:

* **Context and usage**: for each skill, agent, and command that [Claude can invoke on its own](https://code.claude.com/docs/en/skills.md#control-who-invokes-a-skill), the name and description are in Claude's context on every turn so that Claude knows it exists. Those tokens count toward the user's usage and leave less room in the [context window](https://code.claude.com/docs/en/context-window.md) even in sessions where nothing from the plugin runs. The full text of a skill or agent loads only when it is used. What the plugin's MCP servers add per turn follows [MCP tool search](https://code.claude.com/docs/en/mcp.md#scale-with-mcp-tool-search).
* **Processes**: MCP servers the plugin defines run alongside each session where the plugin is enabled, and its hooks fire at their events.
* **Permissions**: whatever the plugin runs, it runs as the user. See [Plugin security and trust](https://code.claude.com/docs/en/plugins/security.md) for what to review first.

Check a plugin's footprint at each stage:

* **Before installing**: open the plugin from the **Marketplaces** tab in `/plugin`. Plugins in Anthropic's official marketplace show a **Context cost** estimate there.
* **After installing**: [Measure what a plugin costs](https://code.claude.com/docs/en/plugins/measure.md#measure-what-a-plugin-costs) shows how to read a plugin's footprint, and the **Installed** tab's **Not used recently** group lists plugins the user could turn off.
* **To stop it without uninstalling**: disable the plugin with `/plugin` or, in the shell, `claude plugin disable`. See [Manage installed plugins](https://code.claude.com/docs/en/plugins/install.md#manage-installed-plugins).

## Get plugins from a marketplace

A marketplace is a repository or directory with a `.claude-plugin/marketplace.json` file that lists plugins and where to fetch each one. It is a catalog, not a hosted store. A user adds a marketplace once, then installs plugins from it by name, such as `commit-commands@claude-plugins-official`.

Claude Code adds Anthropic's official marketplace the first time the user starts an interactive terminal session, unless a [managed policy](https://code.claude.com/docs/en/plugins/org.md#allow-the-official-marketplace-and-your-own) blocks it. Claude Code does not add Anthropic's community marketplace on its own. To distinguish Anthropic's marketplaces, read [Anthropic's marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces.md). To see what the official one lists, open the **Discover** tab of `/plugin` in a session or browse [Claude Marketplace](https://claude.com/marketplace/plugins) on the web.

The following diagram shows the path from a marketplace to a session: a marketplace lists a plugin, the user installs that plugin, and Claude Code loads its components.

![Diagram of the marketplace path in three boxes, left to right. A marketplace, a catalog of plugins, lists a plugin. The plugin is one directory installed as a unit, holding skills, agents, hooks, MCP servers, and other components. You install the plugin into Claude Code, which loads its components.](https://mintcdn.com/claude-code/2Q_GtOEovg5qaBem/images/plugins-model.svg?fit=max\&auto=format\&n=2Q_GtOEovg5qaBem\&q=85\&s=4196344954b7c2e27fc0bd6a9a1113a1)

> **Description of the diagram:** Light off-white canvas with the bold centered title "You install a plugin from a marketplace". Three boxes in one row, joined by two gray rightward arrows. Left: a white rounded box with a thin light-gray border, "Marketplace" in bold over "a catalog of plugins" in gray. First arrow, labeled "lists" in gray above it. Middle, the largest and tallest box: light-gray fill with a tan outline, "Plugin" in bold over "one directory, installed as a unit" in gray, then a two-by-two grid of white tiles, "Skills" and "Agents" on top, "Hooks" and "MCP servers" below, and "and other components" in gray under the grid. Second arrow, labeled "you install". Right: a light-gray rounded box with no visible border, "Claude Code" in bold over "loads its components" in gray.

[Install and manage plugins](https://code.claude.com/docs/en/plugins/install.md#install-a-plugin) has the install steps for each place Claude Code runs, including the terminal, the desktop app and VS Code. While developing a plugin, no marketplace is needed: load the plugin straight from its folder with `--plugin-dir`, as [Develop without a marketplace](https://code.claude.com/docs/en/plugins/create.md#develop-without-a-marketplace) shows.

### Make an installed plugin available in your session

Before an installed plugin provides a skill the user can run, the plugin must be present at each of these layers:

* **Settings**: the user's settings list the marketplaces added and the plugins enabled.
* **Disk**: `~/.claude/plugins/` holds what Claude Code has fetched and installed.
* **Session**: plugins load at startup, or when the user [reloads plugins](https://code.claude.com/docs/en/plugins/loading.md#check-which-stage-a-plugin-reached).

Read [Plugin loading reference](https://code.claude.com/docs/en/plugins/loading.md) for the rules at each layer, including which settings file takes precedence and where the files are on disk.

## Tell Anthropic's marketplaces from third-party ones

A marketplace's name places it in one of three tiers. Claude Code accepts the official and community names only for marketplaces sourced from `github.com/anthropics/` repositories:

* **Official**: marketplaces with one of Anthropic's [official marketplace names](https://code.claude.com/docs/en/plugins/security.md#official-marketplace-names), including `claude-plugins-official` and `claude-code-plugins`.
* **Community**: marketplaces with one of Anthropic's community names, such as `claude-community`. [Identify Anthropic's marketplaces by name](https://code.claude.com/docs/en/plugins/security.md#marketplace-tiers) lists them.
* **Third-party**: every other marketplace. A marketplace published by a coworker or an organization is third-party.

Whatever the tier, an installed plugin can run code with the user's privileges. Read [Plugin security and trust](https://code.claude.com/docs/en/plugins/security.md) for how to review a plugin before installing it.

Through [managed settings](https://code.claude.com/docs/en/settings.md#settings-files), an organization can allowlist or block marketplaces, force-install plugins, and turn off session-only loading. Read [Manage plugins for your organization](https://code.claude.com/docs/en/plugins/org.md) for those controls.

## Understand install scopes

Installing a plugin means picking a scope, and the scope decides who the plugin is enabled for:

* **User scope**: enabled for the user in every project on this computer
* **Project scope**: enabled for everyone who works in this repository, through the committed `.claude/settings.json`. Each collaborator still [installs it on their own machine](https://code.claude.com/docs/en/plugins/loading.md#enabled-in-project-settings-but-not-installed)
* **Local scope**: enabled for the user in this repository only

A plugin installed at user scope in the terminal, the desktop app's local sessions, or the VS Code extension is available in the other two on that computer, because all three read the same settings files. See [Choose an install scope](https://code.claude.com/docs/en/plugins/install.md#choose-an-install-scope) for how to pick one.

A cloud session, including one in the browser at claude.ai/code, does not load the plugins in the user's local settings. For install steps in the terminal, VS Code, and the desktop app, and for what a cloud session loads, see [Install a plugin](https://code.claude.com/docs/en/plugins/install.md#install-a-plugin).

> **Note:** The same plugin format also installs on claude.ai and in Cowork, where a different set of components loads. For those surfaces, see [Plugins on claude.ai and in Cowork](https://claude.com/docs/plugins/overview) on claude.com and its [component support table](https://claude.com/docs/plugins/platform-support#compare-component-support-by-app).

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/overview
- https://code.claude.com/docs/en/plugins/create.md — create a plugin from an empty directory, and develop without a marketplace
- https://code.claude.com/docs/en/plugins/install.md — install steps per surface (terminal, desktop app, VS Code), scopes, managing installed plugins, what a cloud session loads
- https://code.claude.com/docs/en/plugins/manifest-reference.md — `plugin.json` fields and metadata
- https://code.claude.com/docs/en/plugins/components.md — every component type with examples, and the plugin explorer
- https://code.claude.com/docs/en/plugins/mods/overview.md — hooks modules (mods), including mods built into Claude Code
- https://code.claude.com/docs/en/plugins/loading.md — how plugins load at the settings, disk and session layers
- https://code.claude.com/docs/en/plugins/security.md — plugin security and trust, official and community marketplace names
- https://code.claude.com/docs/en/plugins/org.md — organization controls over marketplaces and plugins
- https://code.claude.com/docs/en/plugins/anthropic-marketplaces.md — Anthropic's official and community marketplaces
- https://code.claude.com/docs/en/plugins/measure.md — measure plugin cost and usage
- https://code.claude.com/docs/en/plugins/publish.md — publish and distribute a plugin, including submitting to Anthropic's directory
- https://code.claude.com/docs/en/plugin-evals.md — test plugins with evals
- https://code.claude.com/docs/en/plugins/create-marketplace.md — create a marketplace
- https://code.claude.com/docs/en/plugins/host-marketplace.md — host and maintain a marketplace
- https://code.claude.com/docs/en/plugins/troubleshooting.md — troubleshoot plugins
- https://code.claude.com/docs/en/skills.md — standalone skills and who can invoke a skill
- https://code.claude.com/docs/en/sub-agents.md — standalone subagents
- https://code.claude.com/docs/en/hooks-guide.md — standalone hooks
- https://code.claude.com/docs/en/mcp.md — standalone MCP servers and MCP tool search
- https://code.claude.com/docs/en/context-window.md — the context window
- https://code.claude.com/docs/en/settings.md — settings files, including managed settings
- https://claude.com/docs/plugins/overview — plugins on claude.ai and in Cowork
- https://claude.com/docs/plugins/platform-support — component support by app
- https://claude.com/marketplace/plugins — browse the official marketplace on the web
