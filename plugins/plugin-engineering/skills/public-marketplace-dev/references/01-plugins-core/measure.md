# Measure plugin cost and usage

How to measure a Claude Code plugin's token cost, lower it, and find out whether people still use the plugin.

## Contents

- [Measure what a plugin costs](#measure-what-a-plugin-costs)
  - [Lower the always-on figure](#lower-the-always-on-figure)
- [Check whether a plugin is used](#check-whether-a-plugin-is-used)
  - [Not used recently in `/plugin`](#not-used-recently-in-plugin)
  - [Find skills that never run](#find-skills-that-never-run)
  - [Unused plugins in `/doctor`](#unused-plugins-in-doctor)
  - [Usage share in `/usage`](#usage-share-in-usage)
- [Documentation References](#documentation-references)

Every session where a plugin is enabled includes the names and descriptions of its skills, agents, and commands in Claude's context. Those tokens count against the user's usage whether or not the plugin gets used. This file covers how to see that number for a plugin, how to reduce it as the plugin's maintainer, and where usage shows up so the maintainer can tell whether a plugin is still being used.

This file is for plugin authors and maintainers. For the same questions across every machine in an organization, see [Measure across a fleet](https://code.claude.com/docs/en/plugins/measure#measure-across-a-fleet).

> **Note:** These cases are covered on other pages:
>
> * **Testing how reliably the plugin changes Claude's behavior**: see [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals.md)
> * **Trimming one's own session's context**: see [Manage installed plugins](https://code.claude.com/docs/en/plugins/install.md#manage-installed-plugins) and the [context window](https://code.claude.com/docs/en/context-window.md) page

Start with [Measure what a plugin costs](#measure-what-a-plugin-costs).

## Measure what a plugin costs

To see what a plugin adds to Claude's context, run [`claude plugin details`](https://code.claude.com/docs/en/plugins/cli-reference#plugin-details) with the plugin's name. Run it in the shell, not at the prompt of a running Claude Code session. The plugin must be loaded: installed, in a skills directory, or passed with `--plugin-dir` in the same command, as in `claude --plugin-dir ./formatter plugin details formatter`.

This example reads an installed plugin named `formatter` that has two skills, a command, an agent, a hook, and an MCP server:

```bash theme={null}
claude plugin details formatter
```

```text theme={null}
formatter 1.0.0
  Description: Formats and lints code on save
  Source: formatter@my-marketplace

Component inventory
  Skills (3)  format-all, format-code, lint-fix
  Agents (1)  style-reviewer
  Hooks (1)  PostToolUse  (harness-only — no model context cost)
  MCP servers (1)  formatter-tools  (tool schemas resolved at runtime; not counted)
  LSP servers (0)

Projected token cost
  Always-on:   ~146 tok   added to every session

Per-component (rounded)
  component       always-on  on-invoke
  format-code           ~40        ~30
  lint-fix              ~50        ~30
  style-reviewer        ~40        ~40
  format-all           < 20        ~30

  On-invoke cost is paid each time a skill or agent fires.
  Token counts are estimates and may differ from actual usage.
```

Read each part of the output for a different question:

* **Component inventory**: what Claude Code found in the plugin. Commands are counted with skills, so `format-all` appears under `Skills`. Hooks and MCP servers get no cost estimate and no per-component row. To see what a plugin's MCP tools add, run `/context` in a session with the plugin enabled and read the `MCP tools` category.
* **Always-on**: the tokens that the names and descriptions of the plugin's skills, agents, and commands add to every session where the plugin is enabled, whether or not anything runs. Every user carries this number; it is the one to reduce.
* **Per-component**: each row splits one skill, agent, or command into its always-on share and its on-invoke cost, which is the body that loads only when that component runs. Use the always-on column to find which component contributes most.

### Lower the always-on figure

These changes are for the plugin's maintainer and reduce what the plugin adds to every session, its per-turn cost. A user who only uses the plugin can only disable or uninstall it; see [Manage installed plugins](https://code.claude.com/docs/en/plugins/install.md#manage-installed-plugins).

The always-on figure counts each component's name plus its `description` and `when_to_use` frontmatter. To lower it:

* Shorten skill and agent descriptions.
* Split a large plugin so users install only the components they need.

Claude also matches requests against a skill's description, so a shorter description can stop the skill triggering. After trimming descriptions, check triggering with a [`tool_used: Skill` grader](https://code.claude.com/docs/en/plugin-evals#create-your-first-eval-suite) in the eval suite.

For what each component type contributes, see [plugin components](https://code.claude.com/docs/en/plugins/components.md).

## Check whether a plugin is used

Claude Code does not report a plugin's usage back to its author. Usage is recorded on the machine of each person who installed the plugin, so what the author can learn depends on the author's relationship to those people:

* **They're teammates you can ask**: each user's own Claude Code shows them whether they still use the plugin, in four places: the [`/plugin` panel](#not-used-recently-in-/plugin), [`/skill-doctor`](#find-skills-that-never-run), [`/doctor`](#unused-plugins-in-/doctor), and [`/usage`](#usage-share-in-/usage). All four are commands the user runs at the Claude Code prompt in a session on their own machine.
* **Neither**: the author has no usage signal from Claude Code for that plugin.

### Not used recently in `/plugin`

On the **Installed** tab of `/plugin`, a plugin the user installed from a marketplace moves under a **Not used recently** header once it has gone unused for at least 14 days and 10 sessions. The plugin's details also show a `Last used:` line. For what users do with that header and line, see [Find plugins you no longer use](https://code.claude.com/docs/en/plugins/install.md#find-plugins-you-no-longer-use).

The **Not used recently** header never appears for:

* Plugins loaded with `--plugin-dir` or from a skills directory
* Plugins that include a theme, output style, monitor, or workflow, because those are in use without a tracked invocation

A plugin's [language server](https://code.claude.com/docs/en/plugins/components.md#lsp-servers) counts as used when it delivers diagnostics or answers a code navigation request, so an LSP plugin whose server is active in the user's sessions is not listed as unused.

When the user's organization sets [`strictKnownMarketplaces`](https://code.claude.com/docs/en/plugins/org#restrict-what-users-can-install), neither the header nor the `Last used:` line appears.

### Find skills that never run

`/skill-doctor` shows what each skill costs and how often it gets used. It flags skills that are in Claude's skill listing but have never been invoked, including skills from plugins.

In an interactive session, the report opens in the `/plugin` manager's **Stats** tab. See [Find unused skills](https://code.claude.com/docs/en/skills.md#find-unused-skills) for what the report covers and where it is available.

### Unused plugins in `/doctor`

The `/doctor` checkup lists each user-installed skill, MCP server, and plugin, and recommends disabling the ones that were not used. See [`/doctor` in the commands reference](https://code.claude.com/docs/en/commands#all-commands).

### Usage share in `/usage`

On a Pro, Max, Ultra, Team, or Enterprise plan, the `/usage` breakdown attributes recent usage to skills, subagents, plugins, and MCP servers as a share of the total. See [Using the `/usage` command](https://code.claude.com/docs/en/costs#using-the-/usage-command).

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/measure (also covers measuring across a fleet)
- https://code.claude.com/docs/en/plugin-evals.md — test how reliably a plugin steers Claude, including `tool_used: Skill` graders
- https://code.claude.com/docs/en/plugins/install.md — managing installed plugins and finding unused ones
- https://code.claude.com/docs/en/context-window.md — how the context window is filled
- https://code.claude.com/docs/en/plugins/cli-reference — `claude plugin details` and the other plugin CLI commands
- https://code.claude.com/docs/en/plugins/components.md — what each plugin component type contributes, including LSP servers
- https://code.claude.com/docs/en/plugins/org — organization controls such as `strictKnownMarketplaces`
- https://code.claude.com/docs/en/skills.md — skills, including finding unused skills with `/skill-doctor`
- https://code.claude.com/docs/en/commands — the commands reference, including `/doctor`
- https://code.claude.com/docs/en/costs — costs and the `/usage` command
