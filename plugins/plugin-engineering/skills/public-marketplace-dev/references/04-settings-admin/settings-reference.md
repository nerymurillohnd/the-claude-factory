> ## Documentation Index
>
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.
>
> Source: https://code.claude.com/docs/en/settings-reference
> Pruned copy (2026-11-07): this file keeps only the passages that apply to developing and distributing Claude Code plugins through a marketplace hosted in a public GitHub repository and served to third parties. Removed passages are listed in REMOVALS.md.
>
> Sections in this file:
>
> - Settings index
> - Model and responses
>   - `outputStyle`
> - Permission settings
>   - `allowManagedPermissionRulesOnly`
> - Memory and context
>   - `skillListingBudgetFraction`
>   - `skillListingMaxDescChars`
> - Interface and terminal
>   - `subagentStatusLine`
>   - `theme`
>   - `verbose`
> - Hooks and automation
>   - `allowedHttpHookUrls`
>   - `allowManagedHooksOnly`
>     - What runs under `allowManagedHooksOnly`
>   - `disableAllHooks`
>     - Status line and file suggestion gates
>   - `httpHookAllowedEnvVars`
> - Plugins and skills
>   - `disableSkillShellExecution`
>   - `allowedChannelPlugins`
>   - `blockedMarketplaces`
>   - `channelsEnabled`
>   - `pluginSuggestionMarketplaces`
>   - `strictKnownMarketplaces`
>     - Allowed source types
>     - Owner wildcards
>     - Exact matching
>     - Combine with `extraKnownMarketplaces`
>   - `strictPluginOnlyCustomization`
>   - `strictPluginOnlyCustomization.skills`
>   - `strictPluginOnlyCustomization.agents`
>   - `strictPluginOnlyCustomization.hooks`
>   - `strictPluginOnlyCustomization.mcp`
>   - `enabledPlugins`
>   - `extraKnownMarketplaces`
>     - Marketplace source types
>     - Marketplace key aliases
>   - `pluginConfigs`
> - MCP
>   - `allowedMcpServers`
>   - `allowManagedMcpServersOnly`
>   - `deniedMcpServers`
> - Agents, sessions, and worktrees
>   - `agent`
> - Enterprise and managed settings
>   - `disableSideloadFlags`
> - See also

# All settings

> Complete reference for every Claude Code settings.json key: where each one goes, its type and default, and a paste-ready example, with an index of every key.

[Back to index](#all-settings)

This reference page lists each key Claude Code reads from a settings file, plus the [short group of keys](https://code.claude.com/docs/en/settings-reference#global-config-settings) it keeps in `~/.claude.json` instead. To pick a file, or check precedence, start with [Settings files and precedence](https://code.claude.com/docs/en/settings.md).

## Settings index

Every key below links to its entry. Scope lists the [files](https://code.claude.com/docs/en/settings.md#settings-files-and-who-they-affect) it can go in: `User` is `~/.claude/settings.json`, `Project` is `.claude/settings.json`, `Local` is `.claude/settings.local.json`, and `Managed` is [what your organization deploys](https://code.claude.com/docs/en/managed-settings.md). `Any file` means all four, and `Global config` means [`~/.claude.json`](https://code.claude.com/docs/en/settings-reference#global-config-settings).

| Key | Description | Topic | Scope |
| :- | :- | :- | :- |
| [`agent`](#agent) | Start every session as a named [subagent](https://code.claude.com/docs/en/sub-agents.md) with its prompt, tools, and model | Agents, sessions, and worktrees | Any file |
| [`allowedChannelPlugins`](#allowedchannelplugins) | Replace the default allowlist of [channel plugins](https://code.claude.com/docs/en/channels.md#restrict-which-channel-plugins-can-run) that can push messages | Plugins and skills | Managed |
| [`allowedHttpHookUrls`](#allowedhttphookurls) | Limit which URLs [HTTP hooks](https://code.claude.com/docs/en/hooks.md) can target | Hooks and automation | Any file |
| [`allowedMcpServers`](#allowedmcpservers) | Allowlist which [MCP servers](https://code.claude.com/docs/en/mcp.md) users can add | MCP | Any file |
| [`allowManagedHooksOnly`](#allowmanagedhooksonly) | Run only the [hooks](https://code.claude.com/docs/en/hooks.md) your organization deploys | Hooks and automation | Managed |
| [`allowManagedMcpServersOnly`](#allowmanagedmcpserversonly) | Make the managed [MCP](https://code.claude.com/docs/en/mcp.md) allowlist the only one that applies | MCP | Managed |
| [`blockedMarketplaces`](#blockedmarketplaces) | Block [plugin marketplace](https://code.claude.com/docs/en/plugins/overview.md) sources for your organization | Plugins and skills | Managed |
| [`deniedMcpServers`](#deniedmcpservers) | Block specific [MCP servers](https://code.claude.com/docs/en/mcp.md) by URL, command, or name | MCP | Any file |
| [`disableAllHooks`](#disableallhooks) | Turn off [hooks](https://code.claude.com/docs/en/hooks.md), a custom [status line](https://code.claude.com/docs/en/statusline.md), and a custom [`@` file suggestion](https://code.claude.com/docs/en/interactive-mode#quick-commands) command at once | Hooks and automation | Any file |
| [`disableSideloadFlags`](#disablesideloadflags) | Reject the CLI flags that sideload [plugins](https://code.claude.com/docs/en/plugins/overview.md), [subagents](https://code.claude.com/docs/en/sub-agents.md), and [MCP servers](https://code.claude.com/docs/en/mcp.md) | Enterprise and managed settings | Managed |
| [`disableSkillShellExecution`](#disableskillshellexecution) | Stop [skills](https://code.claude.com/docs/en/skills.md) and custom commands from running inline shell | Plugins and skills | Any file |
| [`enabledPlugins`](#enabledplugins) | Turn individual [plugins](https://code.claude.com/docs/en/plugins/overview.md) on or off per scope | Plugins and skills | Any file |
| [`extraKnownMarketplaces`](#extraknownmarketplaces) | Register [marketplaces](https://code.claude.com/docs/en/plugins/overview.md) for a repository or an organization | Plugins and skills | Any file |
| [`httpHookAllowedEnvVars`](#httphookallowedenvvars) | Limit which env vars [HTTP hooks](https://code.claude.com/docs/en/hooks.md) can put in headers | Hooks and automation | Any file |
| [`outputStyle`](#outputstyle) | Change Claude's role, tone, and output format with an [output style](https://code.claude.com/docs/en/output-styles.md) | Model and responses | Any file |
| [`pluginConfigs`](#pluginconfigs) | Store the answers you gave a [plugin](https://code.claude.com/docs/en/plugins/overview.md)'s configuration dialog | Plugins and skills | User or managed |
| [`pluginSuggestionMarketplaces`](#pluginsuggestionmarketplaces) | Choose which [marketplaces](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install) can surface plugin install suggestions in `/plugin` | Plugins and skills | Managed |
| [`pluginTrustMessage`](https://code.claude.com/docs/en/settings-reference#plugintrustmessage) | Add your own text to the [plugin](https://code.claude.com/docs/en/plugins/overview.md) trust warning | Plugins and skills | Managed |
| [`skillListingBudgetFraction`](#skilllistingbudgetfraction) | Reserve more or less context for the [skill listing](https://code.claude.com/docs/en/skills.md#skill-descriptions-are-cut-short) | Memory and context | Any file |
| [`skillListingMaxDescChars`](#skilllistingmaxdescchars) | Cap each skill's description length in the [skill listing](https://code.claude.com/docs/en/skills.md#skill-descriptions-are-cut-short) | Memory and context | Any file |
| [`skillOverrides`](https://code.claude.com/docs/en/settings-reference#skilloverrides) | [Hide or collapse a skill](https://code.claude.com/docs/en/skills.md#override-skill-visibility-from-settings) without editing its SKILL.md | Plugins and skills | Any file |
| [`strictKnownMarketplaces`](#strictknownmarketplaces) | Allowlist the [marketplace](https://code.claude.com/docs/en/plugins/overview.md) sources users can add and install from | Plugins and skills | Managed |
| [`strictPluginOnlyCustomization`](#strictpluginonlycustomization) | Block [skills](https://code.claude.com/docs/en/skills.md), [agents](https://code.claude.com/docs/en/sub-agents.md), [hooks](https://code.claude.com/docs/en/hooks.md), and [MCP servers](https://code.claude.com/docs/en/mcp.md) from user and project sources | Plugins and skills | Managed |
| [`strictPluginOnlyCustomization.agents`](#strictpluginonlycustomization-agents) | Lock [agents](https://code.claude.com/docs/en/sub-agents.md) to plugin and managed sources | Plugins and skills | Managed |
| [`strictPluginOnlyCustomization.hooks`](#strictpluginonlycustomization-hooks) | Lock [hooks](https://code.claude.com/docs/en/hooks.md) to plugin and managed sources | Plugins and skills | Managed |
| [`strictPluginOnlyCustomization.mcp`](#strictpluginonlycustomization-mcp) | Lock [MCP servers](https://code.claude.com/docs/en/mcp.md) to plugin and managed sources | Plugins and skills | Managed |
| [`strictPluginOnlyCustomization.skills`](#strictpluginonlycustomization-skills) | Lock [skills](https://code.claude.com/docs/en/skills.md) to plugin and managed sources | Plugins and skills | Managed |
| [`subagentStatusLine`](#subagentstatusline) | Rewrite rows in the [subagent](https://code.claude.com/docs/en/sub-agents.md) task display with your own command | Interface and terminal | Any file |

## Model and responses

### `outputStyle`

Select an [output style](https://code.claude.com/docs/en/output-styles.md) by name. An output style is a saved set of instructions that changes Claude's role, tone, and output format, such as the built-in Explanatory and Learning styles or one you wrote yourself.

If you change this key during a session, Claude uses the new style starting with your next message. For what that message costs in prompt caching, see [Changing output style](https://code.claude.com/docs/en/prompt-caching.md#changing-output-style). Before v2.1.251, the edit applied only after you ran `/clear` or started a new session.

* **Scope**: [`Any file`](#scopes)
* **Type**: string, the name of a [built-in](https://code.claude.com/docs/en/output-styles.md#built-in-output-styles) or [custom](https://code.claude.com/docs/en/output-styles.md#create-a-custom-output-style) output style
* **Default**: unset, so Claude Code uses the default style

This example selects the built-in Explanatory style, which adds educational insights between tasks:

```json settings.json theme={null}
{
  "outputStyle": "Explanatory"
}
```

## Permission settings

Decide what Claude can do without asking, the default permission mode for new sessions, and what auto mode's classifier allows. For rule syntax and the permission model, see [Configure permissions](https://code.claude.com/docs/en/permissions.md).

### `allowManagedPermissionRulesOnly`

Make managed settings the only settings source of permission rules. Claude Code then ignores `allow`, `ask`, and `deny` rules in user, project, local, and `--settings` files, ignores `--allowedTools`, hides the always-allow choices in permission prompts, and stops saving new rules.

When [parent settings from an embedding host](https://code.claude.com/docs/en/managed-settings.md#let-an-embedding-host-add-policy) apply, Claude Code treats them as part of the managed tier. It drops their `allow` rules and `additionalDirectories`, and keeps their `deny` and `ask` rules except `Read` and `Edit` rules whose pattern starts with `!`. A host can't carve paths out of the managed rules with a `!` rule, whether or not you set this key.

`--disallowedTools` rules and the current session's `deny` and `ask` rules still apply, including after Claude Code reloads settings mid-session. They only restrict, so they can't widen what the managed rules grant. Before v2.1.257, Claude Code dropped those command-line and session rules at the first settings reload.

For what a `!` pattern in a `--disallowedTools` or session rule can carve out, see [Read and Edit rules](https://code.claude.com/docs/en/permissions.md#read-and-edit).

When you set this key, Claude Code v2.1.282 or later also ignores the [`allowed-tools`](https://code.claude.com/docs/en/skills#pre-approve-tools-for-a-skill) frontmatter in skills and `.claude/commands/` files from these sources:

* A repository's `.claude/` directory
* Your `~/.claude/skills/` and `~/.claude/commands/` directories, including [skills synced from claude.ai](https://code.claude.com/docs/en/skills.md#where-synced-skills-load)
* An `--add-dir` directory
* [Plugins declared with a `.claude-plugin` manifest](https://code.claude.com/docs/en/plugins/loading#plugins-shared-through-a-repository) inside `~/.claude/skills/` or the project's `.claude/skills/`
* Plugins loaded for one session only, whose ids end in [`@inline`](https://code.claude.com/docs/en/plugins/loading#find-where-a-plugin-came-from), when all of these hold:
  * The session is a [Code session](https://code.claude.com/docs/en/desktop.md#environment-configuration) or [Cowork session](https://code.claude.com/docs/en/managed-settings.md#where-and-when-a-policy-applies), other than a cloud session, for which the Claude Desktop app itself starts Claude Code
  * Your managed settings set the key, not only an embedding host's [parent settings](https://code.claude.com/docs/en/managed-settings.md#let-an-embedding-host-add-policy)
  * The session runs Claude Code v2.1.305 or later

Skills from managed settings and bundled skills keep their `allowed-tools`. `@inline` plugins outside those Desktop sessions keep theirs too, except one named [`anthropic-skills`](https://code.claude.com/docs/en/skills#names-reserved-for-synced-skills). A skill's `disallowed-tools` still applies. For what a developer sees when Claude Code ignores the field, see [When only managed permission rules apply](https://code.claude.com/docs/en/skills.md#when-only-managed-permission-rules-apply).

* **Scope**: [`Managed`](#scopes)
* **Type**: Boolean
  * `true`: managed settings become the only settings source of permission rules
  * `false`: Claude Code applies permission rules from user, project, local, and `--settings` files in addition to the managed ones
* **Default**: unset, so Claude Code applies permission rules from user, project, and local settings and from `--settings`, in addition to the managed ones

```json managed-settings.json theme={null}
{
  "allowManagedPermissionRulesOnly": true
}
```

This key doesn't lock down the MCP server allowlist; for that, set [`allowManagedMcpServersOnly`](#allowmanagedmcpserversonly). See [Managed-only settings](https://code.claude.com/docs/en/managed-settings.md#managed-only-settings).

## Memory and context

Control what Claude Code loads into context, how it compacts, and where it keeps memory and plans. See [Manage context](https://code.claude.com/docs/en/context-window.md) and [Memory](https://code.claude.com/docs/en/memory.md).

### `skillListingBudgetFraction`

Each turn, Claude sees a [listing of your skills](https://code.claude.com/docs/en/skills.md#skill-descriptions-are-cut-short) with their descriptions, and Claude Code caps that listing at a share of the context window. When the listing is over the cap, Claude Code keeps every skill's name but drops the descriptions of the least-used skills, so Claude can still invoke those skills but is less likely to choose one on its own. Raise this key to keep more descriptions visible at the cost of more context per turn.

* **Scope**: [`Any file`](#scopes)
* **Type**: number, a fraction greater than `0` and at most `1`
* **Default**: `0.01`, which reserves 1% of the context window

```json settings.json theme={null}
{
  "skillListingBudgetFraction": 0.02
}
```

To see how much context the listing uses and which skills contribute most, run `/doctor`.

### `skillListingMaxDescChars`

Each turn, Claude sees a [listing of your skills](https://code.claude.com/docs/en/skills.md#skill-descriptions-are-cut-short) that shows each skill's `description` and `when_to_use` text. This key caps how many characters of that text Claude Code shows per skill; longer text is cut at the cap.

* **Scope**: [`Any file`](#scopes)
* **Type**: number of characters, a positive integer
* **Default**: `1536`

```json settings.json theme={null}
{
  "skillListingMaxDescChars": 2048
}
```

Raise it to keep long descriptions intact at the cost of more context per turn; lower it to fit more skills under [`skillListingBudgetFraction`](#skilllistingbudgetfraction).

## Interface and terminal

Change how Claude Code looks and behaves in your terminal: theme, editor mode, status line, spinner, notifications inside the session, and accessibility. See [Terminal configuration](https://code.claude.com/docs/en/terminal-config.md).

### `subagentStatusLine`

When Claude runs [subagents](https://code.claude.com/docs/en/sub-agents.md), Claude Code lists them in a task display below the prompt, one row per subagent showing `name · description · token count`. This key lets you run your own command to rewrite those rows, for example to show each subagent's context usage as a percentage. On each refresh, Claude Code sends the visible rows as one JSON object on stdin, with a `tasks` array carrying each subagent's `id`, `name`, `status`, `model`, `tokenCount`, and more, and replaces the row for each `id` you write back as a `{"id", "content"}` line. Rows you don't write back keep the default rendering.

* **Scope**: [`Any file`](#scopes). When [`allowManagedHooksOnly`](#allowmanagedhooksonly) is on, or [`disableAllHooks`](#disableallhooks) is set outside managed settings, only the managed settings value runs.
* **Type**: object with `type` set to `"command"` and a `command` string
* **Default**: unset, so Claude Code renders the default rows

```json settings.json theme={null}
{
  "subagentStatusLine": {
    "type": "command",
    "command": "jq -c '.tasks[] | {id, content: \"\\(.name): \\(.tokenCount) tokens\"}'"
  }
}
```

See [Subagent status lines](https://code.claude.com/docs/en/statusline.md#subagent-status-lines).

### `theme`

Pick the color theme for the interface. Appears in `/config` as **Theme**.

* **Scope**: [`Any file`](#scopes). A value in `~/.claude.json` from an older version applies when no settings file sets it.
* **Type**: string, one of:
  * `"auto"`: matches your terminal's light or dark background
  * `"dark"`: the dark theme
  * `"light"`: the light theme
  * `"dark-daltonized"`: the dark theme with colorblind-friendly colors
  * `"light-daltonized"`: the light theme with colorblind-friendly colors
  * `"dark-ansi"`: the dark theme using only your terminal's ANSI color palette
  * `"light-ansi"`: the light theme using only your terminal's ANSI color palette
  * `"custom:<slug>"` or `"custom:<plugin-name>:<slug>"`: a custom theme from `~/.claude/themes/` or a plugin
* **Default**: `"dark"`

```json settings.json theme={null}
{
  "theme": "light-daltonized"
}
```

See [Create a custom theme](https://code.claude.com/docs/en/terminal-config.md#create-a-custom-theme).

### `verbose`

By default, the transcript collapses each tool call to a short summary, such as the command Claude ran and a line count of its output, and you press `Ctrl+O` to switch the whole transcript to the expanded view when you want the details. Set this key to `true` to show every tool call's full input and output inline as it happens, which is useful when you're debugging a hook, an MCP server, or a long shell command. Appears in `/config` as **Verbose output**.

* **Scope**: [`Any file`](#scopes). A value in `~/.claude.json` from an older version applies when no settings file sets it.
* **Type**: Boolean
  * `true`: you see full tool output
  * `false`: you see truncated summaries of tool output
* **Default**: `false`
* **Per-session overrides**: [`--verbose`](https://code.claude.com/docs/en/cli-reference#cli-flags) takes precedence over this key for one session

```json settings.json theme={null}
{
  "verbose": true
}
```

A [`viewMode`](https://code.claude.com/docs/en/settings-reference#viewmode) value or a sticky `/focus` selection overrides this key every session.

## Hooks and automation

Register hooks, restrict which hooks run, and control workflows. For hook events and payloads, see the [hooks reference](https://code.claude.com/docs/en/hooks.md).

### `allowedHttpHookUrls`

Limit which URLs [HTTP hooks](https://code.claude.com/docs/en/hooks.md#http-hook-fields) can target. When you define this key, Claude Code runs an HTTP hook only if its URL matches one of the patterns and blocks the rest without running them; an empty array blocks every HTTP hook.

* **Scope**: [`Any file`](#scopes). Arrays merge across settings files.
* **Type**: array of URL patterns, with `*` as a wildcard
* **Default**: unset, so any URL is allowed

This example allows any URL under `https://hooks.example.com/` and any `http://localhost` URL:

```json settings.json theme={null}
{
  "allowedHttpHookUrls": ["https://hooks.example.com/*", "http://localhost:*"]
}
```

Hostname matching is case-insensitive and treats `hooks.example.com.`, with the trailing dot that marks a fully qualified domain name, the same as `hooks.example.com`, which is how DNS treats them. The allowlist applies to hooks from every source, including managed settings.

### `allowManagedHooksOnly`

Restrict hook execution to hooks your organization deploys.

* **Scope**: [`Managed`](#scopes)
* **Type**: Boolean
  * `true`: only managed hooks run, plus Agent SDK hooks and hooks from plugins your managed settings force-enable. See [What runs under `allowManagedHooksOnly`](#what-runs-under-allowmanagedhooksonly)
  * `false`: hooks from every settings scope and plugin run
* **Default**: unset, so hooks from every settings scope and plugin run

```json managed-settings.json theme={null}
{
  "allowManagedHooksOnly": true
}
```

#### What runs under `allowManagedHooksOnly`

When you set it to `true`, Claude Code changes which hooks and hook-like commands load:

* **Managed and SDK hooks run**: hooks from managed settings and hooks the [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) registers in process
* **Force-enabled plugin hooks run**: hooks from plugins your managed settings force-enable through [`enabledPlugins`](#enabledplugins). Claude Code matches on the full `plugin@marketplace` ID, so a plugin with the same name from a different marketplace stays blocked. This lets you distribute vetted hooks through an organization marketplace while blocking everything else. A [mod](https://code.claude.com/docs/en/plugins/mods/overview.md) in such a plugin loads only when it [counts as your organization's](https://code.claude.com/docs/en/plugins/mods/admin.md#install-your-organizations-mods)
* **Monitors from other plugins are blocked**: a plugin's [monitors](https://code.claude.com/docs/en/plugins/components.md#monitors) don't start unless the plugin is force-enabled. Requires Claude Code v2.1.310 or later
* **Everything else is blocked**: user, project, and local hooks, hooks and mods from other installed plugins, and hooks declared in agent frontmatter. [Mods built into Claude Code](https://code.claude.com/docs/en/plugins/mods/overview.md#mods-built-into-claude-code) keep running. To block only users' mods, set [`allowManagedModsOnly`](https://code.claude.com/docs/en/plugins/mods/admin#set-options-on-the-built-in-guard) instead.
* **Status line and file suggestion narrow to managed settings**: Claude Code reads [`statusLine`](https://code.claude.com/docs/en/statusline), [`fileSuggestion`](https://code.claude.com/docs/en/settings-reference#filesuggestion), and [`subagentStatusLine`](https://code.claude.com/docs/en/statusline#subagent-status-lines) from managed settings only, following the [status line and file suggestion gates](#status-line-and-file-suggestion-gates)

The [`/goal`](https://code.claude.com/docs/en/goal) command can't run while this key is set, because it depends on hooks.

### `disableAllHooks`

Turn off [hooks](https://code.claude.com/docs/en/hooks.md#disable-or-remove-hooks), any custom [status line](https://code.claude.com/docs/en/statusline.md), and any custom [file suggestion](https://code.claude.com/docs/en/settings-reference#filesuggestion) command. Use it to turn all of these off temporarily without deleting them from your settings.

* **Scope**: [`Any file`](#scopes). Only managed settings can disable managed hooks.
* **Type**: Boolean
  * `true`: Claude Code turns off hooks, any custom status line, and any custom file suggestion command
  * `false`: hooks, the status line, and the file suggestion command run
* **Default**: unset, so hooks run

```json settings.json theme={null}
{
  "disableAllHooks": true
}
```

The reach depends on which file carries the key:

* **In managed settings**: Claude Code disables every configured hook, including managed ones, and keeps running the hooks the [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) registers in process
* **In any other settings file**: Claude Code disables user, project, local, and plugin hooks; managed hooks, Agent SDK hooks, and hooks from plugins force-enabled in managed [`enabledPlugins`](#enabledplugins) keep running

The key also stops [mods](https://code.claude.com/docs/en/plugins/mods/overview.md), which are plugins whose code registers hooks:

* **In managed settings**: the mods in every installed plugin stop, your organization's included
* **In any other settings file**: the mods you installed stop, and [your organization's mods](https://code.claude.com/docs/en/plugins/mods/admin.md#install-your-organizations-mods) keep running

Mods built into Claude Code keep running in both cases. Each has [its own switch](https://code.claude.com/docs/en/plugins/mods/overview.md#mods-built-into-claude-code).

The [`/goal`](https://code.claude.com/docs/en/goal) command can't run while hooks are disabled, and the `/hooks` menu shows a notice instead of your hooks.

#### Status line and file suggestion gates

Claude Code makes two decisions for `statusLine`, `fileSuggestion`, and `subagentStatusLine`, in this order:

* **Off entirely**: when managed settings set `disableAllHooks`, or when the folder isn't trusted under the same [workspace trust rule as hooks in settings files](https://code.claude.com/docs/en/permissions.md#what-runs-before-you-trust-a-folder)
* **Narrowed to managed settings**: when [`allowManagedHooksOnly`](#allowmanagedhooksonly) is set, when `disableAllHooks` is `true` outside managed settings after [settings precedence](https://code.claude.com/docs/en/hooks.md#disable-or-remove-hooks) applies, or when you start Claude Code with `--safe-mode`

Under narrowing, Claude Code runs a managed value if one is deployed. Otherwise it skips your value without warning: the status line is disabled, and `@` autocomplete falls back to the built-in file suggestion.

### `httpHookAllowedEnvVars`

An [HTTP hook](https://code.claude.com/docs/en/hooks.md#http-hook-fields) can put the value of an environment variable into a request header, for example an `Authorization: Bearer $HOOK_TOKEN` header, but only for variables the hook lists in its own `allowedEnvVars`. This key sets an outer limit on that list for every HTTP hook: a hook can use a variable only if both its own `allowedEnvVars` and this key name it. Use it to stop a hook from reading a secret it shouldn't, even when the hook's definition asks for it.

* **Scope**: [`Any file`](#scopes). Arrays merge across settings files.
* **Type**: array of environment variable names
* **Default**: unset, so each hook's own `allowedEnvVars` list applies

This example limits header interpolation to `MY_TOKEN` and `HOOK_SECRET`:

```json settings.json theme={null}
{
  "httpHookAllowedEnvVars": ["MY_TOKEN", "HOOK_SECRET"]
}
```

The allowlist applies to hooks from every source, including managed settings.

## Plugins and skills

Enable plugins, register marketplaces, restrict which plugin sources an organization allows, and control which skills load. For installing and building plugins, see [Plugins](https://code.claude.com/docs/en/plugins/overview.md).

### `disableSkillShellExecution`

Turn off inline shell execution for `` !`...` `` and ` ```! ` blocks in [skills](https://code.claude.com/docs/en/skills.md) and custom commands from user, project, plugin, or additional-directory sources. Claude Code replaces each command with `[shell command execution disabled by policy]` instead of running it.

* **Scope**: [`Any file`](#scopes). A `true` in managed settings can't be overridden by `false` elsewhere.
* **Type**: Boolean
  * `true`: Claude Code replaces each inline shell command with `[shell command execution disabled by policy]` instead of running it
  * `false`: inline shell runs
* **Default**: unset, so inline shell runs

```json settings.json theme={null}
{
  "disableSkillShellExecution": true
}
```

Bundled skills and skills deployed through managed settings are unaffected.

### `allowedChannelPlugins`

Choose which [channel](https://code.claude.com/docs/en/channels.md) plugins can push messages into sessions in your organization. When you set it, Claude Code uses your list in place of the default Anthropic allowlist; each entry names a plugin and the marketplace it comes from.

* **Scope**: [`Managed`](#scopes)
* **Type**: array of objects, each with `marketplace` and `plugin` strings. An entry can instead be a `"plugin@marketplace"` string such as `"telegram@claude-plugins-official"`, which Claude Code treats as the equivalent object. The string form requires Claude Code v2.1.267 or later; earlier versions reject the whole `allowedChannelPlugins` value when it contains one
* **Default**: unset, so Claude Code uses the default Anthropic allowlist

This example turns channels on and allows only the Telegram plugin from the official Anthropic marketplace:

```json managed-settings.json theme={null}
{
  "channelsEnabled": true,
  "allowedChannelPlugins": [
    { "marketplace": "claude-plugins-official", "plugin": "telegram" }
  ]
}
```

An empty array blocks every channel plugin.

This key takes effect once channels pass the [`channelsEnabled`](#channelsenabled) gate for the account: on Team and Enterprise plans, and on Console accounts with managed settings, that means `channelsEnabled: true`. See [Restrict which channel plugins can run](https://code.claude.com/docs/en/channels.md#restrict-which-channel-plugins-can-run).

### `blockedMarketplaces`

Block plugin marketplace sources for your organization. Claude Code checks the blocklist on marketplace add and on plugin install, update, refresh, and auto-update, so a marketplace someone added before you set the policy can't be used to fetch plugins either. Blocked sources are checked before download, so they never touch the filesystem.

If you set this key in the [claude.ai admin console](https://code.claude.com/docs/en/server-managed-settings.md), claude.ai also applies it when anyone in your organization adds a marketplace from a git repository on claude.ai, as [How restrictions work](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install) describes.

* **Scope**: [`Managed`](#scopes)
* **Type**: array of marketplace source objects, in the same forms as [`strictKnownMarketplaces`](#allowed-source-types)
* **Default**: unset, so no marketplace is blocked

This example blocks one GitHub repository as a marketplace source:

```json managed-settings.json theme={null}
{
  "blockedMarketplaces": [
    { "source": "github", "repo": "untrusted/plugins" }
  ]
}
```

A `github` entry may use the [owner-wildcard form](#owner-wildcards) `"owner/*"` to block every repository under that GitHub owner, which requires Claude Code v2.1.223 or later. Add `{ "source": "skills-dir" }` to stop Claude Code loading [`@skills-dir` plugins](https://code.claude.com/docs/en/plugins/loading#plugins-shared-through-a-repository) from both `~/.claude/skills/` and a project's `.claude/skills/`, without restricting any marketplace. See [Managed marketplace restrictions](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install).

### `channelsEnabled`

Allow [channels](https://code.claude.com/docs/en/channels.md) for your organization. On claude.ai Team and Enterprise plans, Claude Code blocks channels until you set this to `true`. For [Anthropic Console](https://code.claude.com/docs/en/authentication.md#claude-console-authentication) accounts that authenticate with an API key, channels are allowed by default. If your organization deploys managed settings, Claude Code blocks channels on those accounts too until you set this key to `true`.

* **Scope**: [`Managed`](#scopes)
* **Type**: Boolean
  * `true`: Claude Code allows channels for your organization
  * `false`: the same as unset; whether channels are blocked depends on your plan, as the Default says
* **Default**: unset; channels are blocked on Team and Enterprise plans and on Console accounts with managed settings, and allowed on Pro, Max, and Ultra plans and on Console accounts without managed settings

```json managed-settings.json theme={null}
{
  "channelsEnabled": true
}
```

To restrict which plugins can register as channels once they're enabled, set [`allowedChannelPlugins`](#allowedchannelplugins). See [Enterprise controls](https://code.claude.com/docs/en/channels.md#enterprise-controls).

### `pluginSuggestionMarketplaces`

Name the marketplaces whose plugins can appear as contextual install suggestions, in spinner tips and pinned at the top of the `/plugin` **Discover** tab. The built-in first-party frontend-design tip is unaffected. Suggestions come from each plugin's `relevance` declaration in its marketplace entry.

* **Scope**: [`Managed`](#scopes)
* **Type**: array of marketplace names
* **Default**: unset, so no marketplace-declared suggestions surface

```json managed-settings.json theme={null}
{
  "pluginSuggestionMarketplaces": ["acme-corp-plugins"]
}
```

A name takes effect only when the marketplace is registered on the machine and its registered source is also declared in the same managed settings, either as the [`extraKnownMarketplaces`](#extraknownmarketplaces) entry for that name or as an entry of [`strictKnownMarketplaces`](#strictknownmarketplaces). Claude Code ignores a marketplace registered from a different source under an allowlisted name. The official marketplace is exempt from the source requirement: allowlisting its name alone suffices, since that name can only register from the official Anthropic source. See [Suggest plugins by context](https://code.claude.com/docs/en/plugins/relevance.md).

### `strictKnownMarketplaces`

Restrict which plugin marketplace sources people in your organization can add and install plugins from. Claude Code enforces the allowlist on marketplace add and on plugin install, update, refresh, and auto-update, before any network or filesystem operation, so a marketplace someone added before you set the policy can't be used to fetch plugins once its source no longer matches. Blocked users see an error naming the managed policy.

If you set this key in the [claude.ai admin console](https://code.claude.com/docs/en/server-managed-settings.md), claude.ai also applies it when anyone in your organization adds a marketplace from a git repository on claude.ai, as [How restrictions work](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install) describes.

* **Scope**: [`Managed`](#scopes)
* **Type**: array of marketplace source objects; see [Allowed source types](#allowed-source-types)
* **Default**: unset, so users can add any marketplace. An empty array is a complete lockdown that blocks every marketplace source, including the official Anthropic marketplace

This example allows two GitHub repositories, one pinned to the `v2.0` ref, and one hosted `marketplace.json` URL:

```json managed-settings.json theme={null}
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/approved-plugins" },
    { "source": "github", "repo": "acme-corp/security-tools", "ref": "v2.0" },
    { "source": "url", "url": "https://plugins.example.com/marketplace.json" }
  ]
}
```

You can also write this key as `allowedMarketplaces`; [Marketplace key aliases](#marketplace-key-aliases) describes how Claude Code treats the alias and which version accepts it. This key is a policy gate: it controls what users may add but registers nothing. To restrict and pre-register in one file, see [Combine with `extraKnownMarketplaces`](#combine-with-extraknownmarketplaces). For the user-facing view, see [Managed marketplace restrictions](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install).

#### Allowed source types

Each entry below shows one allowlist entry per source type and the fields it accepts. Most types match exactly; `hostPattern` and `pathPattern` match by regex, and `github` entries can use an [owner wildcard](#owner-wildcards).

| Source | Example entry | Fields |
| :- | :- | :- |
| `github` | `{ "source": "github", "repo": "acme-corp/plugins", "ref": "main", "path": "marketplace" }` | `repo` required; `ref` is a branch or tag; `path` is a subdirectory |

#### Owner wildcards

A `github` entry whose `repo` value is `"<owner>/*"` matches every repository under that GitHub owner. Owner wildcards require Claude Code v2.1.223 or later and work only in `strictKnownMarketplaces` and `blockedMarketplaces`. Everywhere else a `github` source appears, such as `extraKnownMarketplaces` or `/plugin marketplace add`, the `repo` value must name a single repository. Before v2.1.223, Claude Code compared the entry literally, so an allowlist entry matched no repository and a blocklist entry blocked nothing; single-repository entries are enforced on every version.

This entry allows any marketplace repository in the `acme-corp` organization:

```json managed-settings.json theme={null}
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/*" }
  ]
}
```

Only the whole repository-name position can be a wildcard. Claude Code ignores entries such as `*`, `*/plugins`, or `acme-corp/tools-*` as invalid, so they match no repository.

The matching rules differ between the two settings:

| Rule | `strictKnownMarketplaces` | `blockedMarketplaces` |
| - | - | - |
| Matching source spellings | `owner/repo` form only. A git URL that clones the same repository doesn't match | Any spelling, including git URLs that resolve to the same github.com repository |
| Owner case | Case-sensitive | Case-insensitive |
| `ref` | Follows the exact-entry rules: an entry with a `ref` matches only sources with that exact ref, and an entry without one matches only sources that don't specify a ref | An entry without a `ref` blocks all refs of the repositories it matches |
| `path` | Looser than the exact-entry rules: an entry with a `path` requires that exact value, while an entry without one matches any path inside the repository | An entry without a `path` blocks all paths of the repositories it matches |

#### Exact matching

For every source type except owner-wildcard `github` entries and the regex-matched `hostPattern` and `pathPattern` entries, Claude Code allows a user's addition only when the marketplace source matches an entry exactly. For the git-based sources `github` and `git`, exact matching includes the optional fields:

* The `repo` or `url` must match exactly
* The `ref` field must match exactly, or both must be undefined
* The `path` field must match exactly, or both must be undefined

For example, Claude Code treats each pair below as two different sources:

* `{ "source": "github", "repo": "acme-corp/plugins" }` and `{ "source": "github", "repo": "acme-corp/plugins", "ref": "main" }`
* `{ "source": "github", "repo": "acme-corp/plugins", "path": "marketplace" }` and `{ "source": "github", "repo": "acme-corp/plugins" }`

#### Combine with `extraKnownMarketplaces`

The two keys do different jobs. This table compares them:

| Aspect | `strictKnownMarketplaces` | `extraKnownMarketplaces` |
| - | - | - |
| Purpose | Organizational policy enforcement | Team convenience |
| Settings file | Managed settings only | Any settings file |
| Behavior | Blocks non-allowlisted additions | Registers missing marketplaces |
| When enforced | Before network and filesystem operations | Immediately from user or managed settings; after the workspace trust dialog for a repository's files |
| Can be overridden | No, highest precedence | Yes, by higher-precedence settings |
| Source format | Direct source object | Named marketplace with a nested `source` object |

To both restrict and pre-register a marketplace for all users, set both in `managed-settings.json`:

```json managed-settings.json theme={null}
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/plugins" }
  ],
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": { "source": "github", "repo": "acme-corp/plugins" }
    }
  }
}
```

With only `strictKnownMarketplaces` set, users can still add an allowed marketplace themselves with `/plugin marketplace add`. The official Anthropic marketplace is the only one Claude Code registers automatically, and only when the allowlist allows it. [Allow only the official marketplace](https://code.claude.com/docs/en/settings-reference#allow-only-the-official-marketplace) lists the machines it misses.

### `strictPluginOnlyCustomization`

Block skills, agents, hooks, and MCP servers from user and project sources, so they can come only from plugins or managed settings. Combine it with [`strictKnownMarketplaces`](#strictknownmarketplaces) to control the full customization supply chain: the marketplace allowlist controls which plugins users can install.

* **Scope**: [`Managed`](#scopes)
* **Type**: `true` to lock all four kinds of customization, or an array naming the kinds to lock, from `"skills"`, `"agents"`, `"hooks"`, and `"mcp"`
* **Default**: unset, so nothing is locked

This example locks skills and hooks and leaves agents and MCP servers unlocked:

```json managed-settings.json theme={null}
{
  "strictPluginOnlyCustomization": ["skills", "hooks"]
}
```

If you lock any surface, Claude Code also stops loading [skills-directory plugins](https://code.claude.com/docs/en/plugins/loading.md#skills-directory-plugins-blocked-by-managed-settings), the plugin folders that users keep under `~/.claude/skills/` or `.claude/skills/`. Users place those folders themselves rather than installing them from a marketplace, so Claude Code treats them as user customization under this setting.

The four sub-key entries below list what else each surface blocks and what still loads. Claude Code ignores surface names it doesn't recognize rather than failing the settings file, so you can add new surface names before every client has updated.

### `strictPluginOnlyCustomization.skills`

Lock the `skills` surface. Claude Code stops loading skills from `~/.claude/skills/` and `.claude/skills/`, custom commands from `~/.claude/commands/` and `.claude/commands/`, skills and commands under `--add-dir` directories, and skills synced from your claude.ai account. It keeps loading bundled skills, skills in the managed policy directory, and skills from plugins other than [skills-directory plugins](https://code.claude.com/docs/en/plugins/loading.md#skills-directory-plugins-blocked-by-managed-settings).

* **Scope**: [`Managed`](#scopes)
* **Type**: the string `"skills"` in the [`strictPluginOnlyCustomization`](#strictpluginonlycustomization) array
* **Default**: not locked

```json managed-settings.json theme={null}
{
  "strictPluginOnlyCustomization": ["skills"]
}
```

### `strictPluginOnlyCustomization.agents`

Lock the `agents` surface. Claude Code stops loading agents from `~/.claude/agents/`, `.claude/agents/`, and `--add-dir` directories. It keeps loading built-in agents, agents in the managed policy directory, and agents from plugins other than [skills-directory plugins](https://code.claude.com/docs/en/plugins/loading.md#skills-directory-plugins-blocked-by-managed-settings).

* **Scope**: [`Managed`](#scopes)
* **Type**: the string `"agents"` in the [`strictPluginOnlyCustomization`](#strictpluginonlycustomization) array
* **Default**: not locked

```json managed-settings.json theme={null}
{
  "strictPluginOnlyCustomization": ["agents"]
}
```

### `strictPluginOnlyCustomization.hooks`

Lock the `hooks` surface:

* **Stops running**:
  * Hooks from user, project, and local `settings.json`
  * Frontmatter hooks in skills, custom commands, and agents, from the sources that a [`skills`](#strictpluginonlycustomization-skills) or [`agents`](#strictpluginonlycustomization-agents) lock would block
* **Keeps running**: hooks in managed settings, and hooks from plugins other than [skills-directory plugins](https://code.claude.com/docs/en/plugins/loading.md#skills-directory-plugins-blocked-by-managed-settings)

Skills, custom commands, and agents whose frontmatter hooks stop running still load while their own surface isn't locked.

A personal or project [skill](https://code.claude.com/docs/en/skills.md#where-skills-live) that declares `hooks` in its frontmatter also loses its [`allowed-tools`](https://code.claude.com/docs/en/skills#pre-approve-tools-for-a-skill) pre-approval, so your users get permission prompts for the tools that field lists. When such a skill runs in a subagent through [`context: fork`](https://code.claude.com/docs/en/skills#run-skills-in-a-subagent), it keeps the pre-approval. A skill that declares no `hooks` keeps its pre-approval too.

* **Scope**: [`Managed`](#scopes)
* **Type**: the string `"hooks"` in the [`strictPluginOnlyCustomization`](#strictpluginonlycustomization) array
* **Default**: not locked

```json managed-settings.json theme={null}
{
  "strictPluginOnlyCustomization": ["hooks"]
}
```

### `strictPluginOnlyCustomization.mcp`

Lock the `mcp` surface. Claude Code stops loading MCP servers from `~/.claude.json` and `.mcp.json`. It keeps loading [`managed-mcp.json`](https://code.claude.com/docs/en/managed-mcp) servers, servers from [`managedMcpServers`](https://code.claude.com/docs/en/settings-reference#managedmcpservers), and MCP servers from plugins other than [skills-directory plugins](https://code.claude.com/docs/en/plugins/loading.md#skills-directory-plugins-blocked-by-managed-settings).

* **Scope**: [`Managed`](#scopes)
* **Type**: the string `"mcp"` in the [`strictPluginOnlyCustomization`](#strictpluginonlycustomization) array
* **Default**: not locked

```json managed-settings.json theme={null}
{
  "strictPluginOnlyCustomization": ["mcp"]
}
```

### `enabledPlugins`

Turn individual [plugins](https://code.claude.com/docs/en/plugins/overview.md) on or off, keyed by `plugin-name@marketplace-name`. A plugin with no entry at any scope falls back to its [`defaultEnabled`](https://code.claude.com/docs/en/plugins/manifest-reference#fields) value. When you enable or disable a plugin with `/plugin` or `claude plugin enable`, Claude Code writes this key for you.

* **Scope**: [`Any file`](#scopes)
* **Type**: object mapping `plugin-name@marketplace-name` to a Boolean
* **Default**: unset, so each plugin follows its `defaultEnabled` value

This example enables two plugins from the `team-tools` marketplace and disables one from `personal`:

```json settings.json theme={null}
{
  "enabledPlugins": {
    "code-formatter@team-tools": true,
    "deployment-tools@team-tools": true,
    "experimental-features@personal": false
  }
}
```

Each scope serves a different purpose:

* **User settings**: your personal plugin preferences
* **Project settings**: plugins shared with everyone in the repository
* **Local settings**: per-machine overrides, gitignored when Claude Code saves a setting there
* **Managed settings**: organization-wide policy. A plugin set to `false` here is blocked from installation at every scope and hidden from the marketplace

Project settings take precedence over user settings, so setting a plugin to `false` in `~/.claude/settings.json` doesn't disable a plugin that the project's `.claude/settings.json` enables. To opt out of a project-enabled plugin on your machine, set it to `false` in `.claude/settings.local.json` instead. Plugins force-enabled by managed settings can't be disabled this way, since managed settings override local settings.

Enabling a plugin from an external source such as a GitHub repository or npm package in a project's `.claude/settings.json` doesn't install it for other people. On every path that loads plugins, Claude Code reports the plugin as not installed until each user [installs it themselves](https://code.claude.com/docs/en/plugins/org.md#require-plugins-per-repository).

### `extraKnownMarketplaces`

Register additional plugin marketplaces by name, so that people who open the repository, or everyone your managed settings reach, get the marketplace without adding it themselves. Claude Code registers each marketplace it doesn't already know. Whether a plugin that [`enabledPlugins`](#enabledplugins) names from it installs depends on the plugin's source and which file enables it; that entry has the rules.

* **Scope**: [`Any file`](#scopes). Claude Code honors entries in a repository's `.claude/settings.json` or `.claude/settings.local.json` only after you accept the workspace trust dialog for that folder; in a folder you haven't trusted, including a `-p` run there, it ignores them without a message.
* **Type**: object mapping a marketplace name to an object with a `source` object and an optional `autoUpdate` Boolean
* **Default**: unset

This example registers a GitHub marketplace and a marketplace from a self-hosted git URL:

```json settings.json theme={null}
{
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": {
        "source": "github",
        "repo": "acme-corp/claude-plugins"
      }
    },
    "security-plugins": {
      "source": {
        "source": "git",
        "url": "https://git.example.com/security/plugins.git"
      }
    }
  }
}
```

[What runs before you trust a folder](https://code.claude.com/docs/en/permissions.md#what-runs-before-you-trust-a-folder) compares the trust gate with the other content a repository can supply. You can also write this key as `additionalMarketplaces`; see [Marketplace key aliases](#marketplace-key-aliases).

Set `"autoUpdate": true` alongside `source` to make Claude Code refresh that marketplace and update its installed plugins in the background after startup. When omitted, `claude-plugins-official` and most other official Anthropic marketplaces default to `true`, and third-party marketplaces default to `false`. See [Configure auto-updates](https://code.claude.com/docs/en/plugins/install.md#keep-plugins-updated).

When more than one settings file defines a marketplace entry under the same name, Claude Code uses the entry from the [highest-precedence file](https://code.claude.com/docs/en/settings.md#settings-precedence) whole. That entry replaces the lower-precedence entry and inherits none of its fields, so a redefinition can't combine one file's `source.headers` credential with a URL another file controls. Before v2.1.228, Claude Code merged same-name entries field by field, so an entry in a higher-precedence file could inherit fields it didn't set, including another file's `headers`.

#### Marketplace source types

The `source` object takes one of these forms:

* **`github`**: a GitHub repository, with `repo`
* **`git`**: any git URL, with `url`
* **`directory`**: a local filesystem path, with `path`. Use it for development, or for a marketplace your organization [deploys to each machine](https://code.claude.com/docs/en/plugins/mods/admin.md#install-your-organizations-mods).
For `github` and `git` sources, Claude Code never downloads [Git LFS](https://git-lfs.com) content when it clones the marketplace repository to add or update it. LFS-tracked files are checked out as pointer files, and the add or update output reports how many.

The `skipLfs` field inside the `source` object is accepted and has no effect. Before v2.1.274, Claude Code downloaded LFS content unless you set `"skipLfs": true`.

#### Marketplace key aliases

On Claude Code v2.1.232 or later, you can write `extraKnownMarketplaces` as `additionalMarketplaces` and `strictKnownMarketplaces` as `allowedMarketplaces`. Claude Code treats each alias as follows:

* Earlier versions ignore the alias, so keep the canonical spelling in a file that older versions also read, such as a managed settings file for a fleet with mixed Claude Code versions.
* In any settings file that accepts the canonical key, Claude Code reads the alias exactly as it reads the canonical key.
* Claude Code may rewrite `additionalMarketplaces` to `extraKnownMarketplaces` when it updates the file.
* If you set both spellings in one file, Claude Code uses the canonical value and ignores the alias.

### `pluginConfigs`

Store the non-sensitive answers you give a plugin's [`userConfig`](https://code.claude.com/docs/en/plugins/manifest-reference#user-configuration) configuration dialog, keyed by plugin ID. Claude Code writes this key to your user settings when you fill in the dialog, so you don't need to edit it by hand. Claude Code stores sensitive options in the macOS Keychain instead, falling back to `~/.claude/.credentials.json` when the Keychain rejects the write; on platforms without a supported keychain, it stores them in `~/.claude/.credentials.json`.

* **Scope**: [`User or managed`](#scopes)
* **Type**: object mapping a plugin ID to an object with an `options` field, mapping each option name to a string, number, Boolean, or array of strings, and an optional `mcpServers` field holding per-server user configuration values in the same shape
* **Default**: unset

This example stores the `api_endpoint` option for the `deployer` plugin from `acme-tools`:

```json settings.json theme={null}
{
  "pluginConfigs": {
    "deployer@acme-tools": {
      "options": {
        "api_endpoint": "https://api.example.com"
      }
    }
  }
}
```

Claude Code ignores project and local entries because it substitutes these values into plugin hook, MCP, and LSP configurations, and a cloned repository must not be able to supply them.

## MCP

Control which MCP servers Claude Code connects to and which an organization allows. See [Connect to external tools with MCP](https://code.claude.com/docs/en/mcp.md) and [Managed MCP configuration](https://code.claude.com/docs/en/managed-mcp.md).

### `allowedMcpServers`

Allowlist the MCP servers people can add. Claude Code blocks any server that doesn't match an entry wherever it's defined, including plugin servers, servers a user passes with `--mcp-config`, and servers from claude.ai.

Built-in servers such as Claude in Chrome, the `ide` server Claude Code connects to in a running [VS Code](https://code.claude.com/docs/en/vs-code.md#the-built-in-ide-mcp-server) or [JetBrains](https://code.claude.com/docs/en/jetbrains.md#the-built-in-ide-mcp-server) IDE, and servers the CLI itself configures are exempt from the allowlist, and the denylist still applies to them. On Claude Code v2.1.268 or later, a [Claude Tag](https://code.claude.com/docs/en/claude-tag.md) session's Slack tools are also exempt from the allowlist, and the denylist still applies to them. In-process `type: "sdk"` servers are exempt from both lists; the [app that started the session](https://code.claude.com/docs/en/mcp.md#how-connectors-reach-claude-code) registers them.

Servers your organization delivers are also exempt from the allowlist, and the denylist still applies to them. The exemption covers every [`managedMcpServers`](https://code.claude.com/docs/en/settings-reference#managedmcpservers) entry, and any [`managed-mcp.json`](https://code.claude.com/docs/en/managed-mcp#exclusive-control-with-managed-mcp-json) entry whose values use [no `${VAR}` expansion outside `env`](https://code.claude.com/docs/en/managed-mcp#how-allowlists-and-denylists-apply-to-the-managed-set). See [How a server is evaluated](https://code.claude.com/docs/en/managed-mcp.md#how-a-server-is-evaluated) for the full check order. Before v2.1.259, servers from `managed-mcp.json` had to match too.

* **Scope**: [`Any file`](#scopes). Entries from every file merge into one allowlist unless [`allowManagedMcpServersOnly`](#allowmanagedmcpserversonly) is set. Deploy it in managed settings to enforce it.
* **Type**: array of objects, each with exactly one key. Use `serverName`, a string limited to letters, numbers, hyphens, and underscores; `serverCommand`, an array of the command and its arguments matched exactly; or `serverUrl`, a URL pattern with `*` wildcards
* **Default**: unset, so every server is allowed; an empty array blocks every server users add

This example allows only the stdio server that the listed `npx` command starts:

```json settings.json theme={null}
{
  "allowedMcpServers": [
    { "serverCommand": ["npx", "-y", "@modelcontextprotocol/server-filesystem"] }
  ]
}
```

A [`deniedMcpServers`](#deniedmcpservers) entry takes precedence, so a server on both lists is blocked. Once the list contains any `serverCommand` entry, a stdio server must match a `serverCommand` entry, and once it contains any `serverUrl` entry, a remote server must match a `serverUrl` entry: a `serverName` match no longer admits that kind of server. See [Policy-based control with allowlists and denylists](https://code.claude.com/docs/en/managed-mcp.md#policy-based-control-with-allowlists-and-denylists).

### `allowManagedMcpServersOnly`

Make the managed allowlist the only one that applies. Claude Code then reads [`allowedMcpServers`](#allowedmcpservers) from managed settings alone and ignores allowlists in user, project, and local settings; [`deniedMcpServers`](#deniedmcpservers) still merges from every settings scope, so users can still block servers for themselves. Administrators set it so a user's own settings can't broaden what the managed allowlist permits.

* **Scope**: [`Managed`](#scopes)
* **Type**: Boolean
  * `true`: Claude Code reads `allowedMcpServers` from managed settings alone and ignores allowlists in user, project, and local settings
  * `false`: allowlists from every settings scope merge
* **Default**: `false`, so allowlists from every settings scope merge

This example locks the allowlist to managed settings and allows only the server named `github`:

```json managed-settings.json theme={null}
{
  "allowManagedMcpServersOnly": true,
  "allowedMcpServers": [
    { "serverName": "github" }
  ]
}
```

Users can still add MCP servers of their own; only servers that match the managed allowlist load. See [Restrict the allowlist to managed settings only](https://code.claude.com/docs/en/managed-mcp.md#restrict-the-allowlist-to-managed-settings-only).

### `deniedMcpServers`

Block specific MCP servers. Claude Code refuses to load a matching server wherever it's defined, including plugin servers, servers passed with `--mcp-config`, servers from `managed-mcp.json`, servers from [`managedMcpServers`](https://code.claude.com/docs/en/settings-reference#managedmcpservers), and the claude.ai connectors [it fetches itself](https://code.claude.com/docs/en/mcp.md#how-connectors-reach-claude-code). In-process `type: "sdk"` servers are exempt; the app that started the session registers them.

* **Scope**: [`Any file`](#scopes). Entries from every file merge into one denylist, and [`allowManagedMcpServersOnly`](#allowmanagedmcpserversonly) doesn't change that. Deploy it in managed settings to enforce it.
* **Type**: array of objects, each with exactly one key: `serverName`, a string, so a claude.ai connector's display name such as `"claude.ai Slack"` works; `serverCommand`, an array of the command and its arguments matched exactly; or `serverUrl`, a URL pattern with `*` wildcards
* **Default**: unset, so no server is blocked; an empty array also blocks nothing

```json settings.json theme={null}
{
  "deniedMcpServers": [
    { "serverName": "filesystem" }
  ]
}
```

The denylist takes precedence over [`allowedMcpServers`](#allowedmcpservers), so a server on both lists is blocked. See [Policy-based control with allowlists and denylists](https://code.claude.com/docs/en/managed-mcp.md#policy-based-control-with-allowlists-and-denylists).

## Agents, sessions, and worktrees

Set the default agent, control teammates and cross-session messaging, and configure worktrees. See [Subagents](https://code.claude.com/docs/en/sub-agents.md) and [Worktrees](https://code.claude.com/docs/en/worktrees.md).

### `agent`

Run the main thread as a named [subagent](https://code.claude.com/docs/en/sub-agents.md#invoke-subagents-explicitly), so Claude Code applies that subagent's system prompt, tool restrictions, and model to your session. The same key sets the default agent for sessions you dispatch from `claude agents`.

* **Scope**: [`Any file`](#scopes)
* **Type**: string, the name of a built-in or custom agent
* **Default**: unset, so the main thread runs as Claude Code's default agent
* **Per-session overrides**: `--agent` takes precedence over this key for one session

```json settings.json theme={null}
{
  "agent": "code-reviewer"
}
```

A plugin's own `settings.json` can also supply this key; see [Ship default settings with your plugin](https://code.claude.com/docs/en/plugins/components.md#default-settings).

## Enterprise and managed settings

Keys an organization uses to compute, refresh, and combine managed settings. See [Set up managed settings](https://code.claude.com/docs/en/admin-setup.md).

### `disableSideloadFlags`

Reject the `--plugin-dir`, `--plugin-url`, `--agents`, and `--mcp-config` CLI flags at startup, which users could otherwise pass to bypass [`strictKnownMarketplaces`](#strictknownmarketplaces) for a single run. Claude Code exits with an error naming the rejected flags. In [cloud sessions](https://code.claude.com/docs/en/claude-code-on-the-web.md), Claude Code instead starts the session and drops every server-delivered `--mcp-config` entry except in-process `type: "sdk"` entries and a [Claude Tag](https://code.claude.com/docs/en/claude-tag.md) session's Slack tools. Requires Claude Code v2.1.193 or later.

* **Scope**: [`Managed`](#scopes)
* **Type**: Boolean
  * `true`: Claude Code rejects `--plugin-dir`, `--plugin-url`, `--agents`, and `--mcp-config` at startup and exits with an error naming them. In cloud sessions, it instead starts the session and drops every server-delivered `--mcp-config` entry except in-process `type: "sdk"` entries and a Claude Tag session's Slack tools
  * `false`: Claude Code accepts those flags
* **Default**: `false`

```json managed-settings.json theme={null}
{
  "disableSideloadFlags": true
}
```

Claude Code still accepts a `--mcp-config` whose servers are all in-process `type: "sdk"` entries, so the Agent SDK and VS Code extension keep working. Users can still add servers with `claude mcp add` or a `.mcp.json` file; for per-server control, set [`allowedMcpServers`](https://code.claude.com/docs/en/managed-mcp) as well. Requires Claude Code v2.1.193 or later.

`disableSideloadFlags` also rejects plugin folders from these sources:

* **The [`CLAUDE_CODE_PLUGIN_DIRS`](https://code.claude.com/docs/en/env-vars#variables) environment variable**: when the variable names a plugin folder, Claude Code exits at startup with an error that names the variable and says to unset it. Requires Claude Code v2.1.280 or later
* **The Agent SDK [`addPlugins`](https://code.claude.com/docs/en/agent-sdk/typescript#load-more-plugin-folders-with-addplugins) option**: when an application passes plugin folders to `reloadPlugins()` in `addPlugins`, that call fails with an error. The session keeps running with the plugins it already had. Requires Claude Code v2.1.301 or later

In cloud sessions, Claude Code also ignores server-delivered mid-session MCP updates, the path behind cloud session configuration and SDK `setMcpServers()` calls that reach those sessions. In-process `type: "sdk"` entries and a Claude Tag session's Slack tools stay exempt there too. Before v2.1.268, both this drop and the startup drop also removed a Claude Tag session's Slack tools. Before v2.1.239, a server-delivered `--mcp-config` blocked a cloud session from starting.

The desktop app manages some plugins itself, including plugins synced from claude.ai and plugins your organization deploys through the app. If you deploy this key to a device through MDM, OS-level policy, or a managed settings file, the desktop app doesn't pass those plugins to the following sessions on that device:

* **[Code sessions on the user's machine](https://code.claude.com/docs/en/desktop.md#environment-configuration)**: they also start without the skills enabled for the user's claude.ai account. Plugins that Claude Code installs from marketplaces in your managed settings still load. In [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview), MCP servers from plugins you deploy to the device's `org-plugins` directory stay available too, because the desktop app connects to them itself. Before Claude Desktop v1.37937.0, these sessions failed at startup instead.
* **[Cowork sessions on the user's machine](https://code.claude.com/docs/en/managed-settings.md#where-and-when-a-policy-applies)**: the skills inside those plugins and the skills enabled for the user's claude.ai account stay available. In [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview), MCP servers from plugins you deploy to the device's `org-plugins` directory stay available too, because the desktop app connects to them itself. Before Claude Desktop v1.44121.0, these sessions failed at startup instead.

## See also

* [Configure permissions](https://code.claude.com/docs/en/permissions.md): rule syntax, permission modes, and workspace trust
* [Environment variables](https://code.claude.com/docs/en/env-vars.md): every `CLAUDE_*`, `ANTHROPIC_*`, and provider variable Claude Code reads
* [Tools available to Claude](https://code.claude.com/docs/en/tools-reference.md): the built-in tools and which need approval
* [Debug your configuration](https://code.claude.com/docs/en/debug-your-config.md): `claude doctor` and the Settings Error dialog
