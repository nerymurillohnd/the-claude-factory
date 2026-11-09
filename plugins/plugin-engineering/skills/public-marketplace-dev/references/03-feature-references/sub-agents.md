# Create custom subagents

This file covers how to define, configure, scope, invoke and manage Claude Code subagents, including the rules that apply to subagents shipped in a plugin's `agents/` directory.

## Contents

- [Plugin agents](#plugin-agents)
- [Configure subagents](#configure-subagents)
  - [Choose the subagent scope](#choose-the-subagent-scope)
  - [Write subagent files](#write-subagent-files)
  - [Frontmatter reference](#frontmatter-reference)
    - [Subagent files Claude Code skips](#subagent-files-claude-code-skips)
  - [Choose a model](#choose-a-model)
  - [Choose an effort level](#choose-an-effort-level)
    - [When a subagent has no `effort` field or parameter](#when-a-subagent-has-no-effort-field-or-parameter)
  - [Control subagent capabilities](#control-subagent-capabilities)
    - [Available tools](#available-tools)
    - [Restrict which tools a subagent can use](#restrict-which-tools-a-subagent-can-use)
    - [Restrict which subagents can be spawned](#restrict-which-subagents-can-be-spawned)
    - [Preload skills into subagents](#preload-skills-into-subagents)
    - [Enable persistent memory](#enable-persistent-memory)
  - [Define hooks for subagents](#define-hooks-for-subagents)
    - [Project-level hooks for subagent events](#project-level-hooks-for-subagent-events)
- [Work with subagents](#work-with-subagents)
  - [Understand automatic delegation](#understand-automatic-delegation)
  - [Invoke subagents explicitly](#invoke-subagents-explicitly)
  - [Run subagents in foreground or background](#run-subagents-in-foreground-or-background)
    - [Which subagents run in the background](#which-subagents-run-in-the-background)
    - [Tools, permissions, and results of background subagents](#tools-permissions-and-results-of-background-subagents)
  - [API errors in subagents](#api-errors-in-subagents)
  - [Subagent output scanning](#subagent-output-scanning)
  - [Choose between subagents and main conversation](#choose-between-subagents-and-main-conversation)
  - [Let subagents spawn their own subagents](#let-subagents-spawn-their-own-subagents)
  - [Concurrent subagent limit](#concurrent-subagent-limit)
  - [Manage subagent context](#manage-subagent-context)
    - [What loads at startup](#what-loads-at-startup)
    - [Resume subagents](#resume-subagents)
    - [Auto-compaction](#auto-compaction)
- [Example subagents](#example-subagents)
  - [Code reviewer](#code-reviewer)
  - [Debugger](#debugger)
  - [Data scientist](#data-scientist)
- [Documentation References](#documentation-references)

A subagent is a specialized AI assistant that handles one type of task. Use a subagent when a side task would flood the main conversation with search results, logs, or file contents that will not be referenced again: the subagent does that work in its own context and returns only the summary. Define a custom subagent when the same kind of worker keeps being spawned with the same instructions.

Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions. It sends its own requests, which count toward the same [usage limits](https://code.claude.com/docs/en/costs.md#plan-usage-breakdown) as the main conversation. When Claude encounters a task that matches a subagent's description, it delegates to that subagent, which works independently and returns results. The [context window visualization](https://code.claude.com/docs/en/context-window.md) walks through a session where a subagent handles research in its own separate window, showing the context savings in practice.

Claude decides when to delegate from each subagent's description. When writing a subagent, give it a clear description so Claude knows when to use it.

Descriptions take up context, so keep them short. When the combined descriptions of all subagents except the built-in ones exceed 15,000 tokens, Claude Code shows a [warning at startup with the total token count](https://code.claude.com/docs/en/errors.md#agent-descriptions-are-over-the-15000-token-limit). To fix it, trim the subagents' `description` fields and move detail into each subagent's system prompt, which loads only when that subagent runs.

## Plugin agents

When working on subagents that ship in a plugin, apply these plugin rules on top of the rest of this file. A plugin agent uses the same file format and frontmatter as every other subagent, so everything else here applies to it. The [Agents section of the plugin components reference](../01-plugins-core/components.md#agents) covers them in full.

* **Location**: each Markdown file under `agents/` at the plugin root defines one agent. Claude Code scans `agents/` recursively. The [`agents` manifest key](../01-plugins-core/components.md#organize-agents-in-subfolders) replaces that scan.
* **Name**: the agent loads as `<plugin>:<subfolders>:<name>`, where `<name>` comes from the frontmatter `name` field, or from the file name when that field is missing. A file listed in the manifest `agents` key loads without subfolder names.
* **Ignored fields**: Claude Code ignores `permissionMode`, `hooks`, `mcpServers` and `initialPrompt` in a plugin agent. Ship hooks in the plugin's `hooks/hooks.json` and MCP servers in its `.mcp.json` instead; read the note under [Choose the subagent scope](#choose-the-subagent-scope).
* **Broken frontmatter**: an agent whose frontmatter does not parse still loads, with every field ignored, named after its file. Find these files with `claude plugin validate`; read [Subagent files Claude Code skips](#subagent-files-claude-code-skips).
* **Main-thread agent**: the plugin's own `settings.json` can set `agent` to make one of its agents run the whole session while the plugin is enabled. A user's own `agent` setting overrides it. Read [Default settings](../01-plugins-core/components.md#default-settings).
* **Hooks on the plugin's agents**: `SubagentStart` and `SubagentStop` hooks in the plugin's `hooks/hooks.json` match the agent's scoped name; read [Project-level hooks for subagent events](#project-level-hooks-for-subagent-events).
* **Delegation**: measure how reliably Claude delegates to the agent with `claude plugin eval`; read [Understand automatic delegation](#understand-automatic-delegation).

## Configure subagents

A subagent file's location determines who can use the subagent, and its frontmatter determines what the subagent can do. This section covers where subagent files live and every field they support.

### Choose the subagent scope

Subagent files live in different locations depending on scope. When multiple subagents share the same name, Claude Code uses the one from the higher-priority location.

| Location | Scope | Priority | How to create |
| :- | :- | :- | :- |
| Managed settings | Organization-wide | 1 (highest) | Deployed via [managed settings](https://code.claude.com/docs/en/settings.md) |
| `--agents` CLI flag | Current session | 2 | Pass JSON when launching Claude Code |
| `.claude/agents/` | Current project | 3 | Ask Claude, or create the file manually |
| `~/.claude/agents/` | All your projects | 4 | Ask Claude, or create the file manually |
| Plugin's `agents/` directory | Where plugin is enabled | 5 (lowest) | Installed with [plugins](https://code.claude.com/docs/en/plugins/overview.md) |

Claude Code scans plugin `agents/` directories recursively. Unlike project and user scopes, a subfolder inside a plugin's `agents/` directory becomes part of the [scoped identifier](#invoke-subagents-explicitly): a file at `agents/review/security.md` in plugin `my-plugin` registers as `my-plugin:review:security`.

**Plugin subagents** come from installed [plugins](https://code.claude.com/docs/en/plugins/overview.md). They load automatically alongside custom subagents and appear in the @-mention typeahead under their scoped name. For how to create plugin subagents, read the [plugin components reference](https://code.claude.com/docs/en/plugins/components.md#agents).

> [!NOTE]
>
> For security reasons, plugin subagents don't support the `hooks`, `mcpServers`, or `permissionMode` frontmatter fields. Claude Code ignores these fields when it loads agents from a plugin. A user who needs them can copy the agent file into `.claude/agents/` or `~/.claude/agents/`. A user can also add rules to [`permissions.allow`](https://code.claude.com/docs/en/settings-reference#permissions-allow) in `settings.json` or `settings.local.json`, but those rules apply to the entire session, not only to the plugin subagent.
>
> As the plugin's author, ship the hooks in the plugin's [`hooks/hooks.json`](https://code.claude.com/docs/en/plugins/components#hooks) and the MCP servers in its [`.mcp.json`](https://code.claude.com/docs/en/plugins/components#mcp-servers) instead. They then apply whenever the plugin is enabled, not only inside the subagent.

### Write subagent files

Write a subagent file as YAML frontmatter for configuration, followed by the system prompt in Markdown:

```markdown .claude/agents/code-reviewer.md theme={null}
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

The frontmatter defines the subagent's metadata and configuration. The body becomes the system prompt that guides the subagent's behavior. A subagent receives only this system prompt plus basic environment details such as the working directory, not the Claude Code system prompt.

A subagent starts in the main conversation's current working directory. Within a subagent, `cd` commands don't persist between Bash or PowerShell tool calls and don't affect the main conversation's working directory. To give the subagent an isolated copy of the repository instead, set [`isolation: worktree`](#frontmatter-reference).

A subagent with `isolation: worktree` runs its Bash and PowerShell commands inside its worktree. A command whose working directory resolves to the main checkout instead fails with an error, for example because the worktree directory was removed while the subagent was running.

This working-directory check covers the whole repository that contains the directory Claude Code was launched from. When the session itself runs in a linked [worktree](https://code.claude.com/docs/en/worktrees.md), the check also covers the main checkout that worktree is linked from.

For Bash commands, Claude Code also checks the command itself in two ways:

* It blocks a command that redirects git into the main checkout.
* It refuses a command when it can't verify from the command text that any git the command runs stays inside the worktree, for example when the command name is computed at runtime.

The redirect vectors and the shape rules are listed under [How Claude Code enforces isolation](https://code.claude.com/docs/en/worktrees.md#how-claude-code-enforces-isolation). PowerShell commands get only the working-directory check.

[Monitor](https://code.claude.com/docs/en/tools-reference.md#monitor-tool) commands go through the same working-directory and command-content checks as Bash commands.

### Frontmatter reference

Configure a subagent with YAML [frontmatter](https://code.claude.com/docs/en/glossary.md#frontmatter) between `---` markers at the top of its file, and write its system prompt as Markdown after the closing `---`. Only `name` and `description` are required.

Write multi-word field names in camelCase, such as `maxTurns` and `disallowedTools`, exactly as the table spells them: Claude Code ignores a field it doesn't recognize without reporting an error.

* To find a misspelled field in a subagent that loaded, run [`claude --debug`](https://code.claude.com/docs/en/cli-reference#cli-flags) in the shell and search the debug log at `~/.claude/debug/<session-id>.txt` for `does not recognize or apply`. The debug log names up to five top-level fields in the subagent's file that Claude Code doesn't recognize, with the likely intended name when a supported field is close. Requires Claude Code v2.1.296 or later.
* To find out why a subagent file didn't load, read [Subagent files Claude Code skips](#subagent-files-claude-code-skips).

| Field | Required | Description |
| :- | :- | :- |
| `name` | Yes | Unique identifier of at most 256 characters, such as `code-reviewer` or `reviewer-v2`. [Hooks](https://code.claude.com/docs/en/hooks.md#subagentstart) receive this value as `agent_type`. The filename doesn't have to match. Names can't contain `:`, which is reserved for [plugin-scoped identifiers](https://code.claude.com/docs/en/plugins/overview.md) such as `my-plugin:reviewer` |
| `description` | Yes | When Claude should delegate to this subagent |
| `tools` | No | [Tools](#available-tools) the subagent can use, as a comma-separated string such as `Read, Grep, Bash` or a YAML list. Inherits every tool available to subagents if omitted. If no entry in the list resolves to a tool, the subagent usually [fails to launch](https://code.claude.com/docs/en/errors.md#agent-would-be-spawned-with-zero-tools) with an error naming the entries. To preload Skills into context, use the `skills` field rather than listing `Skill` here |
| `disallowedTools` | No | Tools to deny, removed from inherited or specified list. Same format as `tools`. An entry with a specifier, such as `Bash(git push *)`, still [removes the whole tool](#restrict-which-tools-a-subagent-can-use) |
| `model` | No | [Model](#choose-a-model) to use: `sonnet`, `opus`, `haiku`, `fable`, a full model ID such as `claude-opus-5-5`, or `inherit`. When you omit it, Claude Code picks the model in the [subagent model order](#choose-a-model) |
| `permissionMode` | No | [Permission mode](https://code.claude.com/docs/en/sub-agents#permission-modes): `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, or `manual` as an alias for `default`. Ignored for [plugin subagents](#choose-the-subagent-scope) |
| `maxTurns` | No | Maximum number of agentic turns before the subagent stops. When the subagent reaches the limit, Claude Code returns its output marked as partial, and Claude can [resume it](#resume-subagents) to continue. The partial marking requires Claude Code v2.1.246 or later |
| `autoCompactWindow` | No | Lower the [auto-compact window](#set-the-auto-compact-window-for-one-subagent) for this subagent to a token count from `100000` to `1000000`. Requires Claude Code v2.1.296 or later |
| `skills` | No | [Skills](https://code.claude.com/docs/en/skills.md) to preload into the subagent's context at startup. The full skill content is injected, not only the description. Subagents can still invoke unlisted project, user, and plugin skills through the Skill tool |
| `mcpServers` | No | [MCP servers](https://code.claude.com/docs/en/mcp.md) available to this subagent. Each entry is either a server name referencing an already-configured server (e.g., `"slack"`) or an inline definition with the server name as key and a full [MCP server config](https://code.claude.com/docs/en/mcp.md#installing-mcp-servers) as value. Ignored for [plugin subagents](#choose-the-subagent-scope) |
| `hooks` | No | [Lifecycle hooks](#define-hooks-for-subagents) scoped to this subagent. Ignored for [plugin subagents](#choose-the-subagent-scope) |
| `memory` | No | [Persistent memory scope](#enable-persistent-memory): `user`, `project`, or `local`. Enables cross-session learning |
| `background` | No | Set to `true` to keep this subagent in the background even when Claude asks to wait for it. By default, subagents Claude spawns from the main conversation already [start in the background](#run-subagents-in-foreground-or-background) |
| `omitClaudeMd` | No | Set to `true` to start this subagent without the user, project, and local CLAUDE.md files in its [initial context](#what-loads-at-startup); [managed policy files](https://code.claude.com/docs/en/memory.md#how-claude-md-files-load) still load, except for [managed subagents](#choose-the-subagent-scope). Use it for subagents that take everything they need from the delegation prompt. Ignored when the agent runs as the main session agent via `--agent` or the `agent` setting. Requires Claude Code v2.1.271 or later |
| `effort` | No | Effort level when this subagent is active. Overrides the session effort level, but not the [`CLAUDE_CODE_EFFORT_LEVEL`](https://code.claude.com/docs/en/env-vars#variables) environment variable. Options: `low`, `medium`, `high`, `xhigh`, `max`; available levels depend on the model. See [Choose an effort level](#choose-an-effort-level) |
| `isolation` | No | Set to `worktree` to run the subagent in a temporary [git worktree](https://code.claude.com/docs/en/worktrees.md), giving it an isolated copy of the repository branched by default from your [default branch](https://code.claude.com/docs/en/worktrees.md#choose-the-base-branch) rather than the parent session's `HEAD`. The worktree is automatically cleaned up if the subagent makes no changes |
| `color` | No | Display color for the subagent in the task list and transcript. Accepts `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, or `cyan` |
| `initialPrompt` | No | Auto-submitted as the first user turn when this agent runs as the main session agent (via `--agent` or the `agent` setting). [Commands](https://code.claude.com/docs/en/commands.md) and [skills](https://code.claude.com/docs/en/skills.md) are processed. Prepended to any user-provided prompt. Ignored for [plugin subagents](#choose-the-subagent-scope) |
| `experimental` | No | Map of experimental options. Set its `cacheTtl` key to `5m` or `1h` to choose the [prompt cache lifetime](https://code.claude.com/docs/en/prompt-caching.md#choose-the-ttl-yourself) for this subagent's requests, at the frontmatter's place in the [cache lifetime precedence](https://code.claude.com/docs/en/prompt-caching.md#choose-the-ttl-yourself). Claude Code ignores any other value, ignores `1h` while your Claude subscription is using usage credits, and reads the field only from subagent files. Requires Claude Code v2.1.248 or later |

Write `cacheTtl` inside the `experimental` map, not at the top level of the frontmatter:

```yaml theme={null}
---
name: repo-auditor
description: Audits a large repository and reports what it finds
experimental:
  cacheTtl: 1h
---
```

#### Subagent files Claude Code skips

A [plugin subagent](https://code.claude.com/docs/en/plugins/components.md#agents) whose frontmatter has no `name` or doesn't parse still loads, under its filename.

##### Check an `agents` directory before a session

To find files in an `agents` directory whose frontmatter doesn't parse, run `claude plugin validate` against the directory, for example `.claude/agents` or `~/.claude/agents`. Claude Code checks only [the directory named in the command](https://code.claude.com/docs/en/plugins/cli-reference.md#validate-a-directory), and doesn't flag a file whose frontmatter parses but has no `name`. Requires Claude Code v2.1.233 or later.

### Choose a model

The `model` field controls which model the subagent uses:

* **Model alias**: one of the available aliases: `sonnet`, `opus`, `haiku`, or `fable`
* **Full model ID**: a full model ID such as `claude-opus-5-5` or `claude-sonnet-5`. Accepts the same values as the `--model` flag
* **inherit**: the same model as the main conversation

When Claude invokes a subagent, it can also pass a `model` parameter for that specific invocation. On an Agent tool call, that parameter takes a model alias: `sonnet`, `opus`, `haiku`, or `fable`. Claude can't pass a full model ID or `inherit` on that call. Claude Code resolves the subagent's model in this order:

1. The per-invocation `model` parameter
2. The subagent definition's `model` frontmatter, where `inherit` selects the main conversation's model
3. The [`CLAUDE_CODE_SUBAGENT_MODEL`](https://code.claude.com/docs/en/model-config#environment-variables) environment variable, when it is set to a model alias or model ID
4. The main conversation's model

If an installed [mod](https://code.claude.com/docs/en/plugins/mods/overview.md) sets a model in its [`agent.spawn`](https://code.claude.com/docs/en/plugins/mods/reference#subagents) hook, Claude Code uses that model in place of the per-invocation parameter.

In two cases, a family alias such as `opus` in the per-invocation parameter or the frontmatter resolves to the main conversation's model instead of the [version the alias points to](https://code.claude.com/docs/en/model-config.md#model-aliases):

* **The main conversation's model belongs to that family**: the subagent runs on the main conversation's exact model, including any `[1m]` suffix, so it gets the same [extended context](https://code.claude.com/docs/en/model-config.md#extended-context) window as the main conversation.
* **Claude Code can't tell the main conversation's model family, on [a provider other than the Anthropic API](https://code.claude.com/docs/en/third-party-integrations.md)**: this can happen with an [application inference profile ARN](https://code.claude.com/docs/en/amazon-bedrock.md#iam-configuration) on Amazon Bedrock that Claude Code hasn't resolved to a backing model. This case covers only the `opus` alias, and doesn't apply when [`ANTHROPIC_DEFAULT_OPUS_MODEL`](https://code.claude.com/docs/en/model-config#environment-variables) is set, since `opus` then resolves to the model set there.

An alias in `CLAUDE_CODE_SUBAGENT_MODEL` always resolves to the version the alias points to, even when it names the main conversation's family. Setting the variable to `inherit` is the same as leaving it unset.

Setting `CLAUDE_CODE_SUBAGENT_MODEL` by itself doesn't change the model the built-in Explore and Plan subagents run on. To change it, read [Run every subagent on one model](https://code.claude.com/docs/en/sub-agents#run-every-subagent-on-one-model).

Before v2.1.251, `CLAUDE_CODE_SUBAGENT_MODEL` came first in this order and overrode both the per-invocation parameter and the frontmatter, including `model: inherit`.

Claude Code checks the per-invocation parameter, frontmatter, and environment variable values against the organization's [`availableModels`](https://code.claude.com/docs/en/model-config#restrict-model-selection) allowlist. For a blocked value, it substitutes another model:

* When the blocked value is a family alias such as `opus`, Claude Code runs the subagent on the newest version of that family the allowlist permits, following the same [substitution rules and provider scope](https://code.claude.com/docs/en/model-config.md#restrict-model-selection) as `/model`. Before v2.1.222, Claude Code ran the subagent on the inherited model for a blocked family alias as well.
* For any other blocked value, on providers where that substitution doesn't operate, or when the allowlist permits no version of the family, Claude Code runs the subagent on the inherited model instead. If `CLAUDE_CODE_SUBAGENT_MODEL` is set, Claude Code tries that model first, under these same rules.

In interactive sessions, Claude Code shows a warning naming the requested model and the model the subagent runs on, for either substitution.

To check which model a subagent is running on, run [`/tasks`](https://code.claude.com/docs/en/commands). Claude Code names the model on the subagent's row, and adds the [effort level](https://code.claude.com/docs/en/model-config.md#adjust-effort-level) set for that subagent, if any. Requires Claude Code v2.1.242 or later.

A per-invocation `model` parameter also applies when the subagent is [resumed or sent a follow-up message](#resume-subagents), so the subagent stays on that model.

As of v2.1.198, subagents inherit the main conversation's [extended thinking](https://code.claude.com/docs/en/model-config.md#extended-thinking) configuration: if thinking is on in the session, it's on for the subagent, and if it's off, it stays off. There is no per-subagent thinking setting. Before v2.1.198, subagents ran with extended thinking disabled regardless of the main conversation's setting.

### Choose an effort level

To run a subagent at its own [effort level](https://code.claude.com/docs/en/model-config.md#adjust-effort-level), set the [`effort`](#frontmatter-reference) field in its definition.

When the user asks Claude to run a non-fork subagent at a specific effort level, Claude can also pass an `effort` parameter for that invocation. The parameter overrides the `effort` field and stays in effect when the subagent is [resumed](#resume-subagents). The [`CLAUDE_CODE_EFFORT_LEVEL`](https://code.claude.com/docs/en/env-vars#variables) environment variable takes precedence over both. The per-invocation parameter requires Claude Code v2.1.292 or later.

#### When a subagent has no `effort` field or parameter

On the main conversation's model, the subagent runs at the level picked in the session, such as with `/effort`, or set with `--effort`. On another model, [that level doesn't apply](https://code.claude.com/docs/en/model-config.md#effort-level-of-subagents-and-teammates). To choose the subagent's level, set the `effort` field.

### Control subagent capabilities

Control what a subagent can do through tool access, permission modes, and conditional rules.

#### Available tools

Subagents inherit the [built-in tools](https://code.claude.com/docs/en/tools-reference.md) and MCP tools available in the main conversation, narrowed by two filters: the first removes a short list of tools from every subagent, and the second reduces the built-in tool set for subagents that run in the [background](#run-subagents-in-foreground-or-background), which is the default. On macOS, Linux, and WSL, a subagent can also receive the Glob and Grep tools when the main conversation doesn't have them, as described under [Glob tool behavior](https://code.claude.com/docs/en/tools-reference.md#glob-tool-behavior). [Forks](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation) skip both filters and receive the main conversation's exact tool pool. The first filter removes these tools, even when they are listed in the `tools` field:

* `Agent`, when the subagent is at the [depth limit](#let-subagents-spawn-their-own-subagents); in a [fork](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation) the tool stays listed but returns an error instead of spawning
* `AskUserQuestion`
* `EndConversation`, which can end only the main conversation; see [EndConversation tool behavior](https://code.claude.com/docs/en/tools-reference.md#endconversation-tool-behavior)
* `EnterPlanMode`
* `ExitPlanMode`, unless the subagent's [`permissionMode`](https://code.claude.com/docs/en/sub-agents#permission-modes) is `plan`
* `ScheduleWakeup`
* `WaitForMcpServers`
* `Workflow`

The second filter applies to subagents running in the background. Apart from `Agent` and `ExitPlanMode`, which follow the first filter's conditions wherever the subagent runs, a background subagent keeps every MCP tool but only these built-in tools: `Read`, `Grep`, `Glob`, `LSP`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, and `Artifact`, plus [`SubagentHandback`](https://code.claude.com/docs/en/tools-reference) for a subagent that reports through it. Claude Code removes every other built-in tool from a background subagent, whether inherited or listed in the `tools` field, so the same definition can resolve to different tools in the foreground and the background. The removal reports no error unless it leaves the `tools` list [resolving to nothing](https://code.claude.com/docs/en/errors.md#agent-would-be-spawned-with-zero-tools).

Before v2.1.280, background subagents couldn't use `LSP`.

#### Restrict which tools a subagent can use

To restrict tools, use the `tools` field as an allowlist or the `disallowedTools` field as a denylist. When both are set, Claude Code applies `disallowedTools` first, then resolves `tools` against the remaining pool. A tool listed in both is removed.

This example uses `tools` to allow only Read, Grep, Glob, and Bash. The subagent can't edit files, write files, or use any MCP tools:

```yaml theme={null}
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash
---
```

This example uses `disallowedTools` to inherit the subagent's tool pool except Write and Edit. The subagent keeps Bash, MCP tools, and the rest of its pool:

```yaml theme={null}
---
name: no-writes
description: Inherits the available tools except file writes
disallowedTools: Write, Edit
---
```

When nothing in the `tools` list resolves to a tool, for example because every entry is misspelled or names a tool that isn't available to subagents, Claude Code usually refuses to launch the subagent and the Agent tool returns an error naming the unresolved entries. For the message and how to fix each entry, read [Agent would be spawned with zero tools](https://code.claude.com/docs/en/errors.md#agent-would-be-spawned-with-zero-tools).

The `tools` and `disallowedTools` fields also take entries for a whole MCP server:

| Goal | Field | Example entry |
| :- | :- | :- |
| Give the subagent every tool from one server | `tools` | `mcp__github__*` |
| Withhold one server's tools | `disallowedTools` | `mcp__github` or `mcp__github__*` |
| Withhold every MCP tool from any server | `disallowedTools` | `mcp__*` |

This example removes every tool from the `github` MCP server while keeping tools from other servers and the built-in tools in the subagent's pool:

```yaml theme={null}
---
name: local-only
description: Inherits every tool except those from the github MCP server
disallowedTools: mcp__github
---
```

A `disallowedTools` entry with a specifier, such as `Bash(git push *)`, still removes the whole tool from the subagent, not only the matching commands. To keep Bash and block specific commands, add a [Bash deny rule](https://code.claude.com/docs/en/permissions.md#bash) such as `Bash(git push *)` to `permissions.deny` in settings instead. That rule applies to the main conversation and to subagents.

##### MCP server names that contain a double underscore

When a subagent gets none of the tools from an MCP server whose name contains `__`, such as `reports__v2`, check the subagent's `mcp__` entries:

* **In `tools`**: write `mcp__` followed by the [server's whole name](https://code.claude.com/docs/en/permissions.md#mcp) and `__*`, as in `mcp__reports__v2__*`. Without the trailing `__*`, `mcp__reports__v2` matches none of that server's tools.
* **In `disallowedTools`**: look for `mcp__reports` or `mcp__reports__*`, the entries that withhold a server named `reports`. With either entry, the subagent loses every `reports__v2` tool as well, because those tool names also begin with `mcp__reports__`. To withhold only the `reports` server's tools, list them one by one instead, such as `mcp__reports__run_query`.

#### Restrict which subagents can be spawned

When an agent runs as the main thread with `claude --agent`, it can spawn subagents using the Agent tool. To restrict which subagent types it can spawn, use `Agent(agent_type)` syntax in the `tools` field.

> [!NOTE]
>
> In version 2.1.63, the Task tool was renamed to Agent. Existing `Task(...)` references in settings and agent definitions still work as aliases.

```yaml theme={null}
---
name: coordinator
description: Coordinates work across specialized agents
tools: Agent(worker, researcher), Read, Bash
---
```

This is an allowlist: only the `worker` and `researcher` subagents can be spawned. If the agent tries to spawn any other type, the request fails, and the agent sees only the allowed types in its prompt. To block specific agents while allowing all others, use [`permissions.deny`](https://code.claude.com/docs/en/sub-agents#disable-specific-subagents) instead.

To allow spawning any subagent without restrictions, use `Agent` without parentheses:

```yaml theme={null}
tools: Agent, Read, Bash
```

When `Agent` is omitted from the `tools` list entirely, the agent can't spawn any subagents with the Agent tool.

The `Agent(agent_type)` allowlist syntax applies only to an agent running as the main thread with `claude --agent`. In a subagent definition, listing `Agent` in `tools` lets that subagent spawn subagents of its own while the [depth limit](#let-subagents-spawn-their-own-subagents) allows it, but Claude Code ignores any type list inside the parentheses.

#### Preload skills into subagents

Use the `skills` field to inject skill content into a subagent's context at startup. This gives the subagent domain knowledge without requiring it to discover and load skills during execution.

```yaml theme={null}
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

Claude Code injects the full content of each listed skill into the subagent's context at startup, up to the first 32 distinct names in the list. This field controls which skills are preloaded, not which skills the subagent can access: without it, the subagent can still discover and invoke project, user, and plugin skills through the Skill tool during execution. To prevent a subagent from invoking skills entirely, omit `Skill` from the [`tools`](#available-tools) list or add it to `disallowedTools`.

Skills that set [`disable-model-invocation: true`](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill) can't be preloaded, since preloading draws from the same set of skills Claude can invoke. This includes the bundled `/verify` skill, which Claude can't run on its own.

If a listed skill is missing or disabled, for example by the organization's policy, Claude Code skips it and logs a warning to the debug log.

> [!NOTE]
>
> This is the inverse of [running a skill in a subagent](https://code.claude.com/docs/en/skills.md#run-skills-in-a-subagent). With `skills` in a subagent, the subagent controls the system prompt and loads skill content. With `context: fork` in a skill, the skill content is injected into the agent the skill specifies. In both cases the subagent starts without the conversation history.

#### Enable persistent memory

The `memory` field gives the subagent a persistent directory that survives across conversations. The subagent uses this directory to build up knowledge over time, such as codebase patterns, debugging insights, and architectural decisions.

```yaml theme={null}
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

You are a code reviewer. As you review code, update your agent memory with
patterns, conventions, and recurring issues you discover.
```

Choose a scope based on how broadly the memory should apply:

| Scope | Location | Use when |
| :- | :- | :- |
| `user` | `~/.claude/agent-memory/<name-of-agent>/` | the subagent should remember learnings across all projects |
| `project` | `.claude/agent-memory/<name-of-agent>/` | the subagent's knowledge is project-specific and shareable via version control |
| `local` | `.claude/agent-memory-local/<name-of-agent>/` | the subagent's knowledge is project-specific but shouldn't be checked into version control |

Subagent memory is part of [auto memory](https://code.claude.com/docs/en/memory.md#auto-memory): when auto memory is turned off, with the `autoMemoryEnabled` setting or `CLAUDE_CODE_DISABLE_AUTO_MEMORY`, the `memory` field has no effect and the subagent launches without the memory instructions or the memory tool access described below.

When memory is enabled:

* The subagent's system prompt includes instructions for reading and writing to the memory directory.
* The subagent's system prompt also includes the first 200 lines or 25KB of `MEMORY.md` in the memory directory, whichever comes first, with instructions to curate `MEMORY.md` if it exceeds that limit.
* Read, Write, and Edit tools are automatically enabled so the subagent can manage its memory files.

##### Persistent memory tips

* Use `project` as the default scope; it is the recommended one. It makes subagent knowledge shareable via version control.
* Ask the subagent to consult its memory before starting work: "Review this PR, and check your memory for patterns you've seen before."
* Ask the subagent to update its memory after completing a task: "Now that you're done, save what you learned to your memory." Over time, this builds a knowledge base that makes the subagent more effective.
* Include memory instructions directly in the subagent's markdown file so it proactively maintains its own knowledge base:

  ```markdown theme={null}
  Update your agent memory as you discover codepaths, patterns, library
  locations, and key architectural decisions. This builds up institutional
  knowledge across conversations. Write concise notes about what you found
  and where.
  ```

### Define hooks for subagents

Subagents can define [hooks](https://code.claude.com/docs/en/hooks.md) that run during the subagent's lifecycle. Configure them in one of two places:

* **In the subagent's frontmatter**: hooks that run only while that subagent is active
* **In `settings.json`**: session-wide hooks that also fire inside subagents. Tool events such as `PreToolUse` and `PostToolUse` fire for the subagent's tool calls the same way they do in the main conversation, and `SubagentStart` and `SubagentStop` fire when a subagent starts or finishes

Hooks from [settings files, managed policy settings, and plugins](https://code.claude.com/docs/en/hooks.md#hook-locations) all apply inside subagents, so a `PreToolUse` hook in `settings.json` also runs before every tool a subagent uses.

#### Project-level hooks for subagent events

Configure hooks in `settings.json` that respond to subagent lifecycle events in the main session.

| Event | Matcher input | When it fires |
| :- | :- | :- |
| `SubagentStart` | Agent type name | When a subagent begins execution |
| `SubagentStop` | Agent type name | When a subagent completes |

Both events support matchers that target specific agent types by name. The matcher value is the agent's frontmatter `name` for project-level and user-level subagents, or the plugin-scoped identifier such as `my-plugin:db-agent` for [plugin subagents](https://code.claude.com/docs/en/plugins/components.md#agents). A scoped name contains a colon, so it is evaluated as an [unanchored regular expression](https://code.claude.com/docs/en/hooks.md#matcher-patterns); anchor it with `^` and `$`, as in `^my-plugin:db-agent$`, to match only that agent.

This example runs a setup script only when the `db-agent` subagent starts, and a cleanup script when any subagent stops:

```json theme={null}
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/setup-db-connection.sh" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          { "type": "command", "command": "./scripts/cleanup-db-connection.sh" }
        ]
      }
    ]
  }
}
```

A plugin puts the same `SubagentStart` and `SubagentStop` entries in its `hooks/hooks.json`, under the top-level `"hooks"` key, and points each command at a bundled script through `${CLAUDE_PLUGIN_ROOT}`, as the [plugin Hooks section](../01-plugins-core/components.md#hooks) shows. To match one of the plugin's own agents, use its anchored scoped name, such as `^my-plugin:db-agent$`.

For the complete hook configuration format, read [Hooks](https://code.claude.com/docs/en/hooks.md).

## Work with subagents

### Understand automatic delegation

Claude delegates tasks automatically based on the task description in the request, the `description` field in subagent configurations, and the current context. To encourage proactive delegation, include phrases such as "use proactively" in the subagent's `description` field.

Keep descriptions brief: Claude Code shows a startup warning when the subagents' combined descriptions pass [the 15,000-token limit](https://code.claude.com/docs/en/errors.md#agent-descriptions-are-over-the-15000-token-limit), and still loads every subagent.

When the subagent ships in a [plugin](https://code.claude.com/docs/en/plugins/overview.md), measure how reliably Claude delegates to it across realistic prompts instead of checking one prompt at a time: [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals) runs each prompt with and without the plugin and scores the results.

### Invoke subagents explicitly

When automatic delegation isn't enough, the user can request a subagent directly. Three patterns escalate from a one-off suggestion to a session-wide default:

* **Natural language**: name the subagent in the prompt; Claude decides whether to delegate
* **@-mention**: guarantees the subagent runs for one task
* **Session-wide**: the whole session runs as that subagent via the `--agent` flag or the `agent` setting

Natural language needs no special syntax. Name the subagent and Claude typically delegates:

```text wrap theme={null}
Use the test-runner subagent to fix failing tests
Have the code-reviewer subagent look at my recent changes
```

**@-mention the subagent.** Type `@` and pick the subagent from the typeahead, the same way files are @-mentioned. This ensures that specific subagent runs instead of leaving the choice to Claude:

```text wrap theme={null}
@"code-reviewer (agent)" look at the auth changes
```

The full message still goes to Claude, which writes the subagent's task prompt based on what was asked. The @-mention controls which subagent Claude invokes, not what prompt it receives.

Subagents provided by an enabled [plugin](https://code.claude.com/docs/en/plugins/overview.md) appear in the typeahead under their scoped name, such as `my-plugin:code-reviewer`, or `my-plugin:review:security` when the plugin [organizes agents into subfolders](#choose-the-subagent-scope). Named background subagents currently running in the session also appear in the typeahead, with their status next to the name.

The mention can also be typed manually without the picker: `@agent-<name>` for local subagents, or `@agent-` followed by the scoped name for plugin subagents, for example `@agent-my-plugin:code-reviewer`. While this form is being typed, the typeahead shows file matches rather than agents. The agent mention still resolves on submit.

**Run the whole session as a subagent.** Pass [`--agent <name>`](https://code.claude.com/docs/en/cli-reference) to start a session where the main thread itself takes on that subagent's tool restrictions and model:

```bash theme={null}
claude --agent code-reviewer
```

Unless the agent's [prompt is empty](#choose-the-subagent-scope), a custom subagent's system prompt replaces the default Claude Code system prompt entirely, the same way [`--system-prompt`](https://code.claude.com/docs/en/cli-reference) does. `CLAUDE.md` files and project memory still load through the normal message flow, even when the agent's definition sets [`omitClaudeMd`](#frontmatter-reference). When the session runs with `-p` as a custom agent that has its own prompt, it also starts without the [git status snapshot](https://code.claude.com/docs/en/settings-reference.md#includegitinstructions).

The agent name appears as `@<name>` in the startup header, which confirms the agent is active.

This works with built-in and custom subagents, and the choice persists when the session is resumed: Claude Code restores the agent's tool restrictions and model along with the conversation. If the agent no longer exists at resume, the session continues with the default tools and shows a [warning naming the agent](https://code.claude.com/docs/en/errors.md#session-agent-no-longer-available). For the system prompt in either case, read [System prompt flags in resumed conversations](https://code.claude.com/docs/en/cli-reference.md#system-prompt-flags-in-resumed-conversations).

For a plugin-provided subagent, passing only the agent name is enough; Claude Code finds it:

```bash theme={null}
claude --agent security-reviewer
```

When multiple plugins provide agents with the same name, pass the scoped name to disambiguate:

```bash theme={null}
claude --agent my-plugin:security-reviewer
```

When the plugin places the agent in a subfolder of its `agents/` directory, include the subfolder in the scoped name, for example `claude --agent my-plugin:review:security`.

To make an agent the default for every session in a project, set `agent` in `.claude/settings.json`:

```json theme={null}
{
  "agent": "code-reviewer"
}
```

The CLI flag overrides the setting when both are present.

### Run subagents in foreground or background

Subagents run in the foreground or the background:

* **Foreground subagents** block the main conversation until they complete. Permission prompts are passed through to the user as they come up.
* **Background subagents** run concurrently while the user keeps working. When a background subagent reaches a tool call that needs permission, Claude Code surfaces the prompt in the main session and names the subagent that is asking. Approving lets the subagent continue; pressing Esc denies that one tool call without stopping the subagent.

#### Which subagents run in the background

With nothing configured, a subagent that Claude spawns from the main conversation starts in the background.

* **`claude -p` and the Agent SDK**: Claude can wait, on its own judgment or when asked.
* **Interactive terminal session, VS Code, and desktop app sessions on the user's machine**: to let Claude wait for a subagent, [turn off fork mode](https://code.claude.com/docs/en/sub-agents#let-claude-wait-for-a-subagent), which is [on by default](https://code.claude.com/docs/en/sub-agents#turn-fork-mode-on-or-off).

For a skill with `context: fork`, Claude Code follows the rules in [Run skills in a subagent](https://code.claude.com/docs/en/skills.md#run-skills-in-a-subagent) instead, whether or not fork mode is on.

#### Tools, permissions, and results of background subagents

Background subagents run with a [smaller built-in tool set](#available-tools) than foreground subagents, except for conversation forks and [resumed](#resume-subagents) foreground subagents.

Background subagents surface every permission prompt in the main session. When the user answers one of those prompts with a choice that lasts beyond that one tool call, such as a grant that lasts for the rest of the session, Claude Code applies the answer to the whole session, including the main conversation.

A background subagent can leave a background [Bash or PowerShell command](https://code.claude.com/docs/en/tools-reference.md#background-commands) [running past the end of its turn](https://code.claude.com/docs/en/interactive-mode.md#how-backgrounding-works). When that command ends, Claude Code sends the subagent a notification.

A background subagent's results reach Claude as a completion notification in a later turn. Claude waits for that notification before reporting the subagent's results; if the user asks about progress first, Claude reports that the subagent is still running.

### API errors in subagents

When something [cuts off a subagent's response mid-stream](https://code.claude.com/docs/en/errors.md#the-response-above-may-be-incomplete), and the partial response contains text but no tool calls, Claude Code prompts the subagent to continue instead of ending the run. This happens in interactive sessions too. The run ends on the error only once those continuations are used up.

A subagent whose run ends on an API error, such as a usage limit or a repeated server error, reports that failure back to Claude. What Claude receives depends on where the subagent ran:

* **Foreground**: if a rate limit, overload, or server error cuts off a subagent that already produced text output, the Agent tool returns that partial output with a note that the subagent was cut off and didn't finish its task. A subagent that produced nothing, or whose only output was tool calls, fails with [`Agent terminated early due to an API error`](https://code.claude.com/docs/en/errors#agent-terminated-early-due-to-an-api-error), followed by the error detail.
* **Background**: the subagent is marked failed, and the message Claude receives when it ends names the API error and includes the subagent's last output, so partial work isn't lost.

When a subagent's report opens with the following line, the subagent finished on a fallback model:

```text theme={null}
⚠ This agent switched to <model> because its earlier model could not be used.
```

When a [fallback model chain](https://code.claude.com/docs/en/model-config.md#fallback-model-chains) is configured and a subagent encounters a failure the chain covers, such as its model being unavailable, Claude Code switches the subagent to the first model in the chain that accepts the request. The subagent keeps working instead of ending on the error.

Once the underlying API error clears, retry the task or [resume the subagent](#resume-subagents).

### Subagent output scanning

Claude Code scans each subagent's final report before Claude reads it. A subagent may have read files, web pages, or command output the user never reviewed, and text from those sources can carry instructions aimed at the main conversation. The scan never removes or rewords anything; it makes two kinds of change that can be visible in a report:

* **Backslash insertion**: the scan inserts a backslash into text that imitates Claude Code's own output, such as a `<system-reminder>` tag or a line starting with `Human:` or `Assistant:`, so the imitation reads as ordinary text instead of being mistaken for part of the conversation.
* **Marker line**: the scan prepends a line starting with `[harness: subagent output matched instruction-shaped pattern(s):` when the report imitates a tag like `<system-reminder>` or mentions permission settings such as `bypassPermissions` or `--dangerously-skip-permissions`. Permission-setting mentions get the marker line, but the text itself stays as written.

The scan doesn't judge whether content is malicious, and it doesn't change what an instruction in a report can do: a tool call the report leads Claude to make still goes through the session's [permission checks](https://code.claude.com/docs/en/permissions.md) and [sandboxing](https://code.claude.com/docs/en/sandboxing.md). It isn't a substitute for [restricting what a subagent can reach](#control-subagent-capabilities).

A report that returns to Claude as the subagent's result also arrives under a header marking it as subagent output. The header states that instructions or approval claims inside the report are the subagent's words and carry no authority from the user.

A [background subagent's report](#run-subagents-in-foreground-or-background) arrives inside a completion notification, which is marked as an automated event, not a message from the user.

### Choose between subagents and main conversation

Use the **main conversation** when:

* The task needs frequent back-and-forth or iterative refinement
* Multiple phases share significant context, such as planning, implementation, and testing
* The change is quick and targeted
* Latency matters. A subagent that isn't a [fork](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation) starts fresh and may need time to gather context

Use **subagents** when:

* The task produces verbose output that the main context doesn't need
* Specific tool restrictions or permissions must be enforced
* The work is self-contained and can return a summary

Use [Skills](https://code.claude.com/docs/en/skills.md) instead for reusable prompts or workflows that should run in the main conversation context, not in an isolated subagent context.

### Let subagents spawn their own subagents

By default, a subagent can spawn subagents of its own, up to three layers below the main conversation. At the depth limit, Claude Code withholds the `Agent` tool from every subagent except a [fork](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation), so a subagent at the limit does its delegated work itself and returns one summary. A fork at the limit keeps `Agent` in its inherited tool list, but the tool returns an error instead of spawning.

Nested subagents suit a delegated task that itself splits into parallel subtasks, such as a reviewer subagent that dispatches a verifier per finding. By default the spawning subagent waits for each nested subagent's report:

* **Interactive terminal session**: only the top-level subagent's summary returns to the user, because a subagent that launches background subagents waits for their results before it finishes.
* **`claude -p` and the Agent SDK**: the spawning subagent waits while [fork mode](https://code.claude.com/docs/en/sub-agents#turn-fork-mode-on-or-off) is on. With fork mode off, nested subagents start in the [background](#run-subagents-in-foreground-or-background) instead. The spawning subagent doesn't wait for a background nested subagent, which reports to the main conversation if it outlasts the spawning subagent.

To change the limit, set [`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`](https://code.claude.com/docs/en/env-vars) to the number of subagent layers wanted below the main conversation. For example, this entry in [`settings.json`](https://code.claude.com/docs/en/settings) caps nesting at two layers:

```json theme={null}
{
  "env": {
    "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "2"
  }
}
```

With this value, top-level subagents can delegate to a second layer of their own, and that second layer can't delegate further. Set `1` to turn nesting off.

Configure a nested subagent the same way as a top-level one; it resolves from the same [scopes](#choose-the-subagent-scope). To keep one subagent from spawning while nesting is on, such as a reviewer that should stay read-only, omit `Agent` from its [`tools`](#available-tools) list or add it to `disallowedTools`.

### Concurrent subagent limit

Two limits control subagent use, each with its own variable: this one stops Claude from spawning more subagents while too many are running, and the [depth limit](#let-subagents-spawn-their-own-subagents) caps how deeply subagents nest. There's no limit on the total number of subagents Claude can spawn over a session.

By default, when 20 subagents are running in a session, spawning another with the Agent tool fails with `Concurrent subagent limit reached`, and the error tells Claude not to retry. Spawning succeeds again when the running count drops below the limit. To change the limit, set [`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`](https://code.claude.com/docs/en/env-vars) to any positive whole number. Sessions with [ultracode](https://code.claude.com/docs/en/model-config.md#adjust-effort-level) active are exempt: the limit isn't enforced there. Requires Claude Code v2.1.217 or later.

The limit blocks only subagents Claude spawns with the Agent tool, but other runs occupy the same slots:

* An in-session fork started with [`/subtask`](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation) takes a slot while it runs and is never blocked by the limit.
* [Resuming a subagent](#resume-subagents) that already finished takes a fresh slot without checking the limit, so resumes can push the running count past it.

Agents that other features run, such as [workflow](https://code.claude.com/docs/en/workflows.md) agents and [agent team](https://code.claude.com/docs/en/agent-teams.md) teammates, follow their own limits instead.

### Manage subagent context

#### What loads at startup

Each subagent starts with a fresh, isolated context window. It doesn't see the conversation history, the skills already invoked, or the files Claude has already read. Claude composes a delegation message that summarizes the task, and the subagent works from there. The exception is a [fork](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation), which inherits the parent conversation instead of starting fresh.

A non-fork subagent's initial context contains:

* **System prompt**: the agent's own prompt plus environment details that Claude Code appends, not the Claude Code system prompt. Custom subagents define theirs in the [markdown body](#write-subagent-files) or `prompt` field. Built-in agents have predefined prompts.
* **Task message**: the delegation prompt Claude writes when it hands off the work.
* **CLAUDE.md files**: every level of the [CLAUDE.md hierarchy](https://code.claude.com/docs/en/memory.md#how-claude-md-files-load) the main conversation loads, including `~/.claude/CLAUDE.md`, project rules, `CLAUDE.local.md`, managed policy files, and any [`AGENTS.md` files](https://code.claude.com/docs/en/memory#agents-md) loaded as project instructions. The built-in Explore and Plan agents skip this. A subagent whose definition sets [`omitClaudeMd`](#frontmatter-reference) loads only the managed policy files, or none at all when the definition comes from [managed settings](#choose-the-subagent-scope).
* **Git status**: a snapshot Claude Code reads from the repository when the subagent starts. For a subagent in [its own worktree](https://code.claude.com/docs/en/worktrees.md#isolate-subagents-with-worktrees) of that repository, the snapshot shows the worktree's branch, status, and recent commits. Absent outside a Git repository or whenever the snapshot is turned off; see [`includeGitInstructions`](https://code.claude.com/docs/en/settings-reference#includegitinstructions). Explore and Plan skip it regardless.
* **Preloaded skills**: full content of any skill named in the agent's [`skills` field](#preload-skills-into-subagents). Built-in agents don't preload skills.
* **Sibling roster**: a [system reminder](https://code.claude.com/docs/en/glossary.md#system-reminder) listing `main` and every other named agent in the session, each a valid `to` value for [`SendMessage`](#resume-subagents). The roster appears only when the subagent's tools include `SendMessage` and at least one other agent has a name, whether Claude named it when spawning it or it runs as an [agent team](https://code.claude.com/docs/en/agent-teams.md) teammate. It is a snapshot taken when the subagent starts, so agents named later don't appear.

To launch a custom subagent without the user, project, and local CLAUDE.md files, set [`omitClaudeMd: true`](#frontmatter-reference) in its frontmatter or `--agents` JSON. For Explore, Plan, and subagents with `omitClaudeMd`, a subdirectory's `CLAUDE.md` and matching [path-scoped rules](https://code.claude.com/docs/en/memory.md#path-specific-rules) still [load](https://code.claude.com/docs/en/memory.md#how-claude-md-files-load) when the subagent works with files there.

The main conversation still has the full CLAUDE.md when it reads these subagents' results, so most rules don't need to reach the subagent itself. When a rule must reach it, such as "ignore the `vendor/` directory," restate the rule in the delegation prompt.

Which subagents receive git status can't be changed. Only Explore and Plan skip it.

Some main-conversation state never reaches a non-fork subagent:

* **Output style**: a subagent runs its own system prompt, so the session's [output style](https://code.claude.com/docs/en/output-styles.md) doesn't shape its responses, except in a [fork](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation).
* **Auto memory**: the main conversation's [auto memory](https://code.claude.com/docs/en/memory.md#auto-memory) isn't loaded. To give a subagent persistent memory of its own, use the [`memory` field](#enable-persistent-memory).
* **Context window size**: a subagent's context window is sized by its own model, not the parent's. Delegating to a model with a smaller window gives that subagent the smaller window.

#### Resume subagents

Each subagent invocation creates a new instance instead of continuing an earlier one. To continue an existing subagent's work instead of starting over, resume it.

Resumed subagents retain their full conversation history, including all previous tool calls, results, and reasoning. If the subagent spawned [background subagents of its own](#let-subagents-spawn-their-own-subagents), that history includes the results they delivered while it ran. Before v2.1.304, a subagent that Claude messaged or resumed right after it finished could forget its most recent work.

* When a subagent completes, Claude receives its agent ID.
* The built-in Explore and Plan agents are one-shot and return no agent ID, so Claude can't resume them. Use `general-purpose` or a custom subagent when the work must continue later.
* When a subagent stops at its [`maxTurns`](#frontmatter-reference) limit, Claude Code marks the returned output as partial, and Claude can resume the subagent to continue its work.

The user can also ask Claude for the agent ID to reference it explicitly. Agent IDs are also in the transcript files at `~/.claude/projects/{project}/{sessionId}/subagents/`, where each transcript is stored as `agent-{agentId}.jsonl`.

Subagent transcripts persist independently of the main conversation:

* **Main conversation compaction**: when the main conversation compacts, subagent transcripts are unaffected. They're stored in separate files.
* **Session persistence**: subagent transcripts persist within their session. To [resume a subagent](#resume-subagents) after restarting Claude Code, resume the same session.
* **Automatic cleanup**: Claude Code deletes subagent transcripts after the `cleanupPeriodDays` retention period, 30 days by default, following the [retention sweep rules](https://code.claude.com/docs/en/claude-directory.md#cleaned-up-automatically).

#### Auto-compaction

Subagents support automatic compaction. Compaction triggers as the subagent's own context window fills, and `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` applies to subagents as well. For when the override takes effect, read [environment variables](https://code.claude.com/docs/en/env-vars.md).

Compaction events are logged in subagent transcript files:

```json theme={null}
{
  "type": "system",
  "subtype": "compact_boundary",
  "compactMetadata": {
    "trigger": "auto",
    "preTokens": 167189
  }
}
```

The `preTokens` value shows how many tokens were used before compaction occurred.

##### Set the auto-compact window for one subagent

To make one subagent compact earlier than it otherwise would, set `autoCompactWindow` in its [frontmatter](#frontmatter-reference) to a token count from `100000` to `1000000`. When [`CLAUDE_CODE_AUTO_COMPACT_WINDOW`](https://code.claude.com/docs/en/env-vars#variables) is set, the subagent uses that variable's window instead and the field has no effect, unless Claude Code [ignores the variable's value](https://code.claude.com/docs/en/model-config.md#claude_code_auto_compact_window-values). Requires Claude Code v2.1.296 or later.

This frontmatter sets `autoCompactWindow` to 200,000 tokens for a subagent that reads long log files:

```yaml theme={null}
---
name: log-reader
description: Reads long log files and reports the errors it finds
autoCompactWindow: 200000
---
```

Write the value as a plain integer such as `200000`, because in frontmatter Claude Code reads `200k` as 200, which is outside the allowed range. The subagent then still loads and compacts as if the field were absent. To check whether Claude Code ignored the value, run `claude --debug` in the shell and search the [debug log](#frontmatter-reference) for `invalid autoCompactWindow`.

When the value is in range and there is still no change, check for these causes:

* **The value isn't below the [auto-compact window](https://code.claude.com/docs/en/model-config.md#context-window-and-auto-compaction) the subagent would otherwise inherit**: to compact earlier, set a value below that window.
* **The whole session runs as this subagent with `--agent` or the `agent` setting**: the field has no effect there. To set the session's window, read [Set the auto-compact window](https://code.claude.com/docs/en/model-config.md#set-the-auto-compact-window).

## Example subagents

These examples demonstrate effective patterns for building subagents. Use them as starting points, or have Claude generate a customized version.

> [!TIP]
>
> **Best practices:**
>
> * **Design focused subagents:** make each subagent excel at one specific task
> * **Write descriptions that single out one subagent:** Claude uses the description to decide when to delegate. Make each description specific enough to route to the right subagent, and keep the combined set within the [15,000-token description budget](#understand-automatic-delegation)
> * **Limit tool access:** grant only necessary permissions, for security and focus

### Code reviewer

A read-only subagent that reviews code without modifying it. This example shows a focused subagent with limited tool access that excludes Edit and Write, and a detailed prompt that specifies exactly what to look for and how to format output.

```markdown theme={null}
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### Debugger

A subagent that can both analyze and fix issues. Unlike the code reviewer, it includes Edit, because fixing bugs requires modifying code. The prompt provides a clear workflow from diagnosis to verification.

```markdown theme={null}
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

Debugging process:
- Analyze error messages and logs
- Check recent code changes
- Form and test hypotheses
- Add strategic debug logging
- Inspect variable states

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not the symptoms.
```

### Data scientist

A domain-specific subagent for data analysis work. This example shows a subagent for a specialized workflow outside typical coding tasks. It explicitly sets `model: sonnet` for more capable analysis.

```markdown theme={null}
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly

Key practices:
- Write optimized SQL queries with proper filters
- Use appropriate aggregations and joins
- Include comments explaining complex logic
- Format results for readability
- Provide data-driven recommendations

For each analysis:
- Explain the query approach
- Document any assumptions
- Highlight key findings
- Suggest next steps based on data

Always ensure queries are efficient and cost-effective.
```

## Documentation References

- Source page: https://code.claude.com/docs/en/sub-agents — the official subagents page this file is derived from, including sections not kept here (permission modes, fork mode, forks, disabling specific subagents, running every subagent on one model).
- https://code.claude.com/docs/en/plugins/components.md — plugin components reference: shipping agents, hooks and MCP servers in a plugin (formerly the "Distribute subagents with plugins" next step).
- https://code.claude.com/docs/en/plugins/overview.md — plugins overview and plugin-scoped identifiers.
- https://code.claude.com/docs/en/plugins/cli-reference.md — plugin CLI, including `claude plugin validate` on a directory.
- https://code.claude.com/docs/en/plugin-evals — `claude plugin eval` for measuring delegation reliability.
- https://code.claude.com/docs/en/plugins/mods/overview.md — mods overview.
- https://code.claude.com/docs/en/plugins/mods/reference — mods reference, including the `agent.spawn` hook.
- https://code.claude.com/docs/en/hooks.md — hooks reference: `SubagentStart`, hook locations, matcher patterns.
- https://code.claude.com/docs/en/settings.md — settings files and managed settings.
- https://code.claude.com/docs/en/settings-reference.md — settings keys such as `permissions.allow` and `includeGitInstructions`.
- https://code.claude.com/docs/en/permissions.md — permission rules for Bash and MCP tools.
- https://code.claude.com/docs/en/sandboxing.md — sandboxing.
- https://code.claude.com/docs/en/model-config.md — model aliases, environment variables, `availableModels`, effort, extended thinking, fallback chains, auto-compact window.
- https://code.claude.com/docs/en/env-vars.md — environment variables such as `CLAUDE_CODE_EFFORT_LEVEL` and the subagent limits.
- https://code.claude.com/docs/en/errors.md — error messages referenced here (description budget, zero tools, API errors, missing session agent).
- https://code.claude.com/docs/en/tools-reference.md — built-in tools, Monitor, Glob, EndConversation, background commands.
- https://code.claude.com/docs/en/skills.md — skills, `disable-model-invocation`, running skills in a subagent.
- https://code.claude.com/docs/en/mcp.md — MCP servers and their configuration.
- https://code.claude.com/docs/en/memory.md — CLAUDE.md loading, `AGENTS.md`, path-specific rules, auto memory.
- https://code.claude.com/docs/en/worktrees.md — worktrees, base branch, isolation enforcement, subagent worktrees.
- https://code.claude.com/docs/en/cli-reference.md — CLI flags such as `--agent`, `--debug`, `--system-prompt`, and resumed-conversation behavior.
- https://code.claude.com/docs/en/commands.md — slash commands such as `/tasks`.
- https://code.claude.com/docs/en/prompt-caching.md — prompt cache TTL and its precedence.
- https://code.claude.com/docs/en/glossary.md — glossary: frontmatter, system reminder.
- https://code.claude.com/docs/en/costs.md — usage limits.
- https://code.claude.com/docs/en/context-window.md — context window visualization.
- https://code.claude.com/docs/en/third-party-integrations.md — providers other than the Anthropic API.
- https://code.claude.com/docs/en/amazon-bedrock.md — Amazon Bedrock and application inference profiles.
- https://code.claude.com/docs/en/interactive-mode.md — how backgrounding works.
- https://code.claude.com/docs/en/output-styles.md — output styles.
- https://code.claude.com/docs/en/claude-directory.md — the `~/.claude` directory and its retention sweep.
- https://code.claude.com/docs/en/workflows.md — workflows.
- https://code.claude.com/docs/en/agent-teams.md — agent teams.
