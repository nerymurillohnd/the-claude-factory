# Hooks reference

Use this file to configure, write and debug hooks, above all hooks that ship in a plugin: where hooks live, matchers, handler fields for command, HTTP, MCP tool, prompt and agent hooks, exit codes, JSON output and decision control, async hooks, security and debugging. It opens with the things to know about hooks in plugins. When each event fires, its input and its decision control are in [hooks-events.md](hooks-events.md).

> [!TIP]
>
> For a quickstart guide with examples, see [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide.md).

Hooks are user-defined shell commands, HTTP endpoints, MCP tool calls, LLM prompts, or subagents that execute automatically at specific points in Claude Code's lifecycle. Claude Code fires the same hook events wherever it runs: sessions in the terminal, IDE extensions, the [Desktop app](https://code.claude.com/docs/en/desktop-quickstart.md), and [cloud sessions](https://code.claude.com/docs/en/claude-code-on-the-web.md). Use this reference to look up event schemas, configuration options, JSON input/output formats, and advanced features like async hooks, HTTP hooks, and MCP tool hooks.

A plugin can also register hooks as JavaScript functions that Claude Code calls in its own process, which can draw in the interface as well as act on events. A plugin that does is a [mod](https://code.claude.com/docs/en/plugins/mods/overview.md), and those function hooks are covered in [React to events](https://code.claude.com/docs/en/plugins/mods/events.md) rather than here. The hooks on this page keep working alongside mods.

## Contents

- [Things to know about hooks in plugins](#things-to-know-about-hooks-in-plugins)
- [Hook lifecycle](#hook-lifecycle)
  - [How a hook resolves](#how-a-hook-resolves)
- [Configuration](#configuration)
  - [Hook locations](#hook-locations)
  - [Matcher patterns](#matcher-patterns)
    - [Match MCP tools](#match-mcp-tools)
    - [Match Monitor commands](#match-monitor-commands)
  - [Hook handler fields](#hook-handler-fields)
    - [Common fields](#common-fields)
    - [How `if` patterns match Bash commands](#how-if-patterns-match-bash-commands)
    - [Command hook fields](#command-hook-fields)
    - [HTTP hook fields](#http-hook-fields)
    - [MCP tool hook fields](#mcp-tool-hook-fields)
    - [Prompt and agent hook fields](#prompt-and-agent-hook-fields)
  - [Reference scripts by path](#reference-scripts-by-path)
  - [Hooks in skills and agents](#hooks-in-skills-and-agents)
    - [Limits on skill hooks](#limits-on-skill-hooks)
  - [The `/hooks` menu](#the-hooks-menu)
  - [Disable or remove hooks](#disable-or-remove-hooks)
- [Hook input and output](#hook-input-and-output)
  - [Common input fields](#common-input-fields)
  - [Exit code output](#exit-code-output)
    - [Exit code 0](#exit-code-0)
    - [Exit code 2](#exit-code-2)
    - [Other exit codes](#other-exit-codes)
    - [Timeouts](#timeouts)
    - [Hooks that start a background process](#hooks-that-start-a-background-process)
    - [Block the action when a hook fails](#block-the-action-when-a-hook-fails)
    - [Failed hooks on Windows without Git Bash](#failed-hooks-on-windows-without-git-bash)
    - [PowerShell started no program](#powershell-started-no-program)
    - [Exit code 2 behavior per event](#exit-code-2-behavior-per-event)
  - [HTTP response handling](#http-response-handling)
  - [JSON output](#json-output)
    - [Emit terminal notifications](#emit-terminal-notifications)
    - [Add context for Claude](#add-context-for-claude)
    - [Decision control](#decision-control)
- [Hook events](#hook-events)
- [Prompt-based hooks](#prompt-based-hooks)
  - [How prompt-based hooks work](#how-prompt-based-hooks-work)
  - [Prompt hook configuration](#prompt-hook-configuration)
  - [Response schema](#response-schema)
  - [Check multiple conditions before stopping](#check-multiple-conditions-before-stopping)
- [Agent-based hooks](#agent-based-hooks)
  - [How agent hooks work](#how-agent-hooks-work)
  - [Agent hook configuration](#agent-hook-configuration)
- [Run hooks in the background](#run-hooks-in-the-background)
  - [Configure an async hook](#configure-an-async-hook)
  - [How async hooks execute](#how-async-hooks-execute)
  - [Run tests after file changes](#run-tests-after-file-changes)
  - [Limitations](#limitations)
- [Security considerations](#security-considerations)
  - [Disclaimer](#disclaimer)
  - [Workspace trust](#workspace-trust)
  - [Security best practices](#security-best-practices)
- [Windows PowerShell tool](#windows-powershell-tool)
  - [Reference scripts by path in PowerShell hooks](#reference-scripts-by-path-in-powershell-hooks)
- [Debug hooks](#debug-hooks)
- [Documentation References](#documentation-references)

## Things to know about hooks in plugins

Read this block before writing, reviewing or debugging a hook that ships in a plugin. It collects the rules on this page that catch plugin authors, and the hook changes in the Claude Code release notes from 2.1.299 to 2.1.319, checked on 2026-11-09 (there is no 2.1.298 release). Items marked *not yet on this page* come from the release notes only: the official page had not caught up when they were checked. Everything below the block applies to plugin hooks as written; where an example registers a hook in `.claude/settings.json`, put the same entry in the plugin's `hooks/hooks.json`.

**Where plugin hooks live and when they run**

* **File**: put the hooks in `hooks/hooks.json` at the plugin root, under a top-level `"hooks"` key, in the same shape as the `hooks` object of a settings file. Hooks under the `hooks` manifest key load too. They merge with the user's and the project's hooks; read [Hook locations](#hook-locations) and the [Hooks section of the plugin components reference](../01-plugins-core/components.md#hooks).
* **Registration**: Claude Code registers a plugin's hooks when the session loads the plugin, and they fire on their events from then on, whether or not the plugin's skills or commands are used. Narrow the `matcher` to limit when they run.
* **Subagents**: plugin hooks also fire on the tool calls of every subagent; the `agent_id` and `agent_type` input fields tell those calls apart.
* **Duplicates**: a handler defined in several settings files runs once, but a plugin's copy of the same handler stays separate, so a user who also has it in a settings file runs it twice; read [Hook handler fields](#hook-handler-fields).
* **Same-name plugins**: when two enabled plugins share a manifest name, only one of them registers its `hooks/hooks.json` hooks; read [Hooks when two enabled plugins share a name](../01-plugins-core/loading.md#hooks-when-two-enabled-plugins-share-a-name).
* **Plugin agents**: Claude Code ignores the `hooks` field in a plugin agent's frontmatter. Put the hooks in `hooks/hooks.json` instead; read [Plugin agents](sub-agents.md#plugin-agents).
* **Plugin skills**: frontmatter hooks in a plugin's skills follow [Hooks in skills and agents](#hooks-in-skills-and-agents). Since 2.1.304 each plugin is one source with a limit of 1,024 skill hooks and 16,384 matcher characters per session; read [Limits on skill hooks](#limits-on-skill-hooks). `once` is honored only in skill frontmatter, and since 2.1.304 a skill's `once` hook no longer removes another skill's identical hook. Since 2.1.299 a skill's own frontmatter `UserPromptSubmit` hook first runs on the prompt after the one that invokes the skill.
* **Mods**: hooks written as JavaScript functions in a hooks module are a different system, covered in [React to events](../02-mods/mod-events.md), not on this page.

**Names a plugin hook must use**

* **The plugin's MCP tools**: match `mcp__plugin_<plugin>_<server>__<tool>`, such as `mcp__plugin_my-plugin_db__.*`. A matcher on the bare server key never fires; use the same scoped name in `if`. Read [Match MCP tools](#match-mcp-tools).
* **`mcp_tool` hooks**: set `server` to `plugin:<plugin>:<server>`, such as `plugin:my-plugin:db`, not the bare key; read [MCP tool hook fields](#mcp-tool-hook-fields).
* **The plugin's agents**: `SubagentStart` and `SubagentStop` matchers compare against the agent's scoped name, so anchor them, as in `^my-plugin:db-agent$`; read [Project-level hooks for subagent events](sub-agents.md#project-level-hooks-for-subagent-events).
* **claude.ai connectors**: since 2.1.319, hook matchers written with a connector's terminal name, such as `mcp__claude_ai_Slack`, also apply in Claude Desktop, once Claude Desktop includes that version.

**Commands, paths and options**

* **Exec form**: use exec form (`args` set) for any command that holds `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_PLUGIN_DATA}`. In shell form, wrap each placeholder in double quotes, or an install path with a space splits the command; read [Exec form and shell form](#exec-form-and-shell-form).
* **User options**: `${user_config.*}` is substituted in exec form only. A shell-form plugin hook that references it fails with an error instead of running (since v2.1.207); in shell form read `$CLAUDE_PLUGIN_OPTION_<KEY>` instead.
* **Fixed choices**: when a hook script reads an option that takes one of a few fixed values, declare them in `options` on the `userConfig` field instead of leaving it free text. `/config` then shows them as a picker, and `claude plugin validate` rejects a `default` outside the list. Users before v2.1.271 can't load a plugin that declares `options`; read [Limit a field to fixed options](../01-plugins-core/manifest-reference.md#limit-a-field-to-fixed-options).
* **Environment**: every hook process receives `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` as environment variables, whichever form it runs in.
* **Windows shims**: exec form needs a real executable. The `.cmd` and `.bat` shims in `node_modules/.bin` can't be spawned that way, so run `node` with the script path, as in `"command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/node_modules/eslint/bin/eslint.js"]`.
* **PowerShell**: in a PowerShell shell-form command, write `${CLAUDE_PLUGIN_ROOT}` inside double quotes, which Claude Code rewrites to `${env:CLAUDE_PLUGIN_ROOT}`. The bare `$CLAUDE_PLUGIN_ROOT` resolves to `$null`; read [Reference scripts by path in PowerShell hooks](#reference-scripts-by-path-in-powershell-hooks).
* **`CLAUDE_ENV_FILE`**: only `SessionStart`, `Setup`, `CwdChanged` and `FileChanged` hooks get it, and never a hook that runs in PowerShell; read [Persist environment variables](hooks-events.md#persist-environment-variables). Since 2.1.318, variables a `Setup` hook writes there also reach the Bash tool in the cloud sessions where they used to be lost.
* **Dependencies and state**: keep them in `${CLAUDE_PLUGIN_DATA}`, which survives plugin updates. `Setup` doesn't fire on a normal launch, so check for a dependency on first use and install it on a miss; read [Setup](hooks-events.md#setup).

**Blocking and failure**

* **Exit codes**: exit 2 blocks on the events that can block. Exit 1 and every other code is a non-blocking error, so the action goes ahead; read [Exit code output](#exit-code-output).
* **Guards**: for a hook that must stop an action, exit 2 or return a deny, and set `"onFailure": "block"` (v2.1.295 or later, `command` and `http` hooks) so a crash, a missing script or a timeout also blocks; read [Block the action when a hook fails](#block-the-action-when-a-hook-fails).
* **Timeouts**: a `PreToolUse` hook that times out doesn't block the tool call unless `onFailure` is `"block"`; read [Timeouts](#timeouts).
* **Missing script**: a plugin's `UserPromptSubmit` hook, and any `Stop`, `SubagentStop` or `TaskCompleted` hook, that exits 2 with nothing on stdout and a missing-file message such as `No such file or directory` on stderr counts as a non-blocking error, so a script missing from a broken install doesn't block.
* **Windows**: without Git Bash, a shell-form `PreToolUse` or `PermissionRequest` hook with no `shell` set and `onFailure` unset now blocks the call when it fails (2.1.299). The same holds for hooks with `"shell": "powershell"` (2.1.309) and for commands made only of quoted strings (2.1.310). PowerShell hooks block on exit 2 since 2.1.309, including commands that begin with a type cast, `param`, `using` or an attribute since 2.1.316. Set `onFailure` explicitly; read [Failed hooks on Windows without Git Bash](#failed-hooks-on-windows-without-git-bash).
* **Hand-off failures** (2.1.299, *not yet on this page*): an action a plugin hook can block is refused, not let through, when Claude Code can't hand the hook its input or can't read back the hook's answer; a tool that already ran has its result withheld. Values a plugin hook hands back that nest deeper than 28,000 levels are refused with an error naming the limit. The release notes don't say whether these two changes cover command hooks or only a mod's function hooks, so treat a failed hand-off as a block.
* **`if` is best-effort**: when Claude Code can't tell which commands a Bash input runs, the hook runs regardless of the pattern. Enforce a hard allow or deny with permission rules; read [How `if` patterns match Bash commands](#how-if-patterns-match-bash-commands).
* **Attribution**: an `ask` from a plugin hook shows `[plugin:<name>]` in the permission prompt (the label was missing before 2.1.301), and a plugin hook's blocking message ends with `This hook comes from the <plugin> plugin.` (v2.1.281 or later).

**Output**

* **JSON only**: a hook that isn't async must print nothing on stdout but the one JSON object; read [JSON output](#json-output).
* **Size cap**: `additionalContext`, `systemMessage`, `initialUserMessage` and plain stdout are capped at 10,000 characters each. Longer text goes to a file and Claude gets the path and a 2,000-character preview, without being asked to read the file. `PreCompact` stdout is cut at 10,000 characters per hook (2.1.314).
* **Background work**: print the decision before you start a background process, and redirect that process's stdout and stderr, or Claude Code blocks the call with `refusing to honor the suspect capture`; read [Hooks that start a background process](#hooks-that-start-a-background-process).
* **`updatedInput`** (2.1.300, *not yet on this page*): `updatedInput` from `PreToolUse` and `PermissionRequest` hooks is validated like Claude's own input. Unknown keys are dropped, and input the tool rejects denies the call. It still replaces the whole input, so send the unchanged fields too.
* **Late install**: Claude Code ignores `initialUserMessage` and `sessionTitle` from a plugin's `SessionStart` hook when the plugin finishes installing after the `SessionStart` hooks ran.

**Events and timing**

* **No MCP at launch**: `mcp_tool` hooks are skipped on `SessionStart` at launch and on every `Setup`, so use a `command` hook there; read [Events that fire before MCP servers are available](#events-that-fire-before-mcp-servers-are-available).
* **Default timeouts**: 600 seconds for `command`, `http` and `mcp_tool` hooks, 30 for `prompt` and 60 for `agent`. The default drops to 30 on `UserPromptSubmit`, `PreModelSwitch` and `PostModelSwitch`, and to 10 on `MessageDisplay`.
* **`SessionEnd`**: all `SessionEnd` hooks share a 1.5-second budget, and a `timeout` set on a plugin's hook doesn't raise it, so a plugin's `SessionEnd` hook must finish in time unless the user sets `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`; read [SessionEnd](hooks-events.md#sessionend). Since 2.1.300 they also run when the user exits while a background command is running.
* **Prompt and agent hook concurrency** (2.1.312, *this page still says 12 per event*): at most 24 prompt and agent hooks run at a time per session, subagents included, plus at most 12 that have waited longer than their event's timeout. A `timeout` under 1 second counts as 1 second.
* **Agent hook model** (2.1.300): agent hooks honor `model`. Aliases such as `haiku` resolve, a subagent's model no longer overrides it, and an unavailable model falls back to the caller's model instead of allowing the action. Agent hooks are experimental.
* **Supported types**: `PermissionRequest` skips `agent` hooks. `SessionStart` and `Setup` take only `command` and `mcp_tool` hooks; read [Prompt-based hooks](#prompt-based-hooks).
* **Worktrees**: plugin `WorktreeCreate` and `WorktreeRemove` hooks run with `--worktree` since 2.1.300, but a plugin's `WorktreeCreate` hook doesn't run with `--worktree --tmux`, because the worktree is created before plugins load; read [WorktreeCreate](hooks-events.md#worktreecreate).
* **Prompt order** (2.1.299): `UserPromptSubmit` runs before a skill or custom command expands. The hook sees the line as typed, and a block also stops the skill's `` !`<command>` `` lines. Match on a command's name with `UserPromptExpansion`.
* **Monitor**: since 2.1.314, hooks with a `Bash` matcher run on shell commands that the Monitor tool starts. They can deny or ask, but not allow or rewrite them, and `if` accepts `Monitor(tail *)`; read [Match Monitor commands](#match-monitor-commands).
* **Interrupts**: since 2.1.319, `PostToolUse` hooks run, with up to 10 seconds to finish, on tool calls that finish after a new message interrupts the turn; read [PostToolUse after an interrupt](hooks-events.md#posttooluse-after-an-interrupt).
* **Other fixes to rely on**: `SubagentStop` fires once per subagent when it finishes, not about twice a minute (2.1.311), and plan mode no longer runs a write that a `PreToolUse` hook allowed (2.1.299). Declare at least the version that fixed a behavior your hook depends on as the plugin's minimum Claude Code version.

**Where the user's settings or surface overrule the plugin**

* **`allowManagedHooksOnly`**: an organization that sets it blocks plugin hooks, except for plugins force-enabled in managed `enabledPlugins`; read [Hook locations](#hook-locations).
* **`disableAllHooks`**: it turns off the plugin's hooks too, and no setting turns off a single hook; read [Disable or remove hooks](#disable-or-remove-hooks).
* **`strictPluginOnlyCustomization`**: under this lock, plugin skills keep their frontmatter hooks. Since 2.1.304, a skill used in the main conversation whose hooks the lock keeps out no longer gets its `allowed-tools`.
* **Cowork cloud sessions in auto mode**: a `PermissionRequest` hook can't approve shell commands or subagents (2.1.299), a `setMode` update in its allow is ignored (2.1.300), and a hook's allow of an MCP tool call counts as no answer (2.1.314).
* **Cloud sessions**: since 2.1.319, session deny and ask rules that a `PermissionRequest` hook adds survive the session moving to a new worker.
* **VS Code**: since 2.1.304, time a `SessionStart` command hook spends running no longer counts toward the 60-second start limit, up to 10 minutes in total.

**Debugging**

* **`/hooks`**: it lists every hook with its source, and a plugin's hooks with the plugin's name.
* **Debug log**: run `claude --debug` or `claude --debug-file <path>`. Since v2.1.296 the `Hooks:` lines name the plugin a hook came from and how long it ran; read [Debug hooks](#debug-hooks).
* **Hooks that don't fire**: read [`Failed to load hooks from <path>` and hooks that don't fire](../01-plugins-core/troubleshooting.md#failed-to-load-hooks-from-path-and-hooks-that-dont-fire) and [Hook not firing](hooks-guide.md#hook-not-firing).

## Hook lifecycle

Claude Code runs hooks at specific points during a session. When an event fires and a matcher matches, Claude Code passes JSON context about the event to your hook handler. For command hooks, input arrives on stdin. For HTTP hooks, it arrives as the POST request body. Your handler can then inspect the input, take action, and optionally return a decision.

Events fall into three cadences:

* per session: `SessionStart` and `SessionEnd`
* per turn: `UserPromptSubmit`, `Stop`, and `StopFailure`
* on every tool call inside the agentic loop: `PreToolUse` and `PostToolUse`, except [`EndConversation`](https://code.claude.com/docs/en/tools-reference#endconversation-tool-behavior) calls, which skip both

![Hook lifecycle diagram](https://mintcdn.com/claude-code/x7pO8l4XcvAXCoVc/images/hooks-lifecycle.svg?fit=max\&auto=format\&n=x7pO8l4XcvAXCoVc\&q=85\&s=81b9256c1bbe8832553485f5d9e9c746)

> **View the image** [`assets/hooks-lifecycle.png`](../../assets/hooks-lifecycle.png) **to** see the order in which every hook event fires in a session and inside the agentic loop.

The table below summarizes when each event fires. The [Hook events](#hook-events) section documents the full input schema and decision control options for each one.

| Event | When it fires |
| :- | :- |
| `SessionStart` | When a session begins or resumes |
| `Setup` | When you start Claude Code with `--init-only`, or with `--init` or `--maintenance` in `-p` mode. For one-time preparation in CI or scripts |
| `UserPromptSubmit` | When a prompt is submitted, before Claude processes it. Also fires on [turns Claude Code starts on its own](https://code.claude.com/docs/en/hooks.md#userpromptsubmit) |
| `UserPromptExpansion` | When a user-typed command expands into a prompt, before it reaches Claude. Can block the expansion |
| `PreToolUse` | Before a tool call executes. Can block it |
| `PermissionRequest` | When a tool call needs a permission decision |
| `PermissionDenied` | When auto mode denies a tool call, including denials without a classifier verdict. Use JSON `hookSpecificOutput.retry: true` to tell the model it may retry the denied tool call. Claude Code ignores `retry` when the classifier produced no verdict |
| `PostToolUse` | After a tool call succeeds |
| `PostToolUseFailure` | After a tool call fails |
| `PostToolBatch` | After a full batch of parallel tool calls resolves, before the next model call |
| `Notification` | When Claude Code sends a notification |
| `MessageDisplay` | While assistant message text is displayed |
| `SubagentStart` | When a subagent is spawned |
| `SubagentStop` | When a subagent finishes |
| `TaskCreated` | When a task is being created via `TaskCreate` |
| `TaskCompleted` | When a task is being marked as completed |
| `Stop` | When Claude finishes responding |
| `StopFailure` | When the turn ends due to an API error |
| `TeammateIdle` | When an [agent team](https://code.claude.com/docs/en/agent-teams.md) teammate is about to go idle |
| `InstructionsLoaded` | When a CLAUDE.md or `.claude/rules/*.md` file is loaded into context. Fires at session start and when files are lazily loaded during a session |
| `ConfigChange` | When a configuration file changes during a session |
| `CwdChanged` | When the working directory changes, for example when Claude executes a `cd` command. Useful for reactive environment management with tools like direnv |
| `DirectoryAdded` | When a working directory is added mid-session via `/add-dir` or the SDK `register_repo_root` control request |
| `FileChanged` | When a watched file changes on disk. The `matcher` field specifies which filenames to watch |
| `WorktreeCreate` | When a worktree is being created via `--worktree`, `isolation: "worktree"`, or for a background session. Replaces default git behavior |
| `WorktreeRemove` | When a worktree that a `WorktreeCreate` hook created is being removed |
| `PreCompact` | Before context compaction |
| `PostCompact` | After context compaction completes |
| `PreModelSwitch` | Before Claude Code applies a model switch that you or a client requested. Can block the switch |
| `PostModelSwitch` | After the session's model changes, including changes Claude Code makes on its own, such as restoring the model when you resume a session |
| `Elicitation` | When an MCP server requests user input during a tool call |
| `ElicitationResult` | After a user responds to an MCP elicitation, before the response is sent back to the server |
| `SessionEnd` | When a session terminates |

### How a hook resolves

> **Official walkthrough**: [How a hook resolves](https://code.claude.com/docs/en/hooks#how-a-hook-resolves) traces one `PreToolUse` hook from event to block: `"matcher": "Bash"`, `"if": "Bash(rm *)"`, and a `jq` script that prints `permissionDecision: "deny"` when the command contains `rm -rf`, with a Windows PowerShell version.

> **View the image** [`assets/hook-resolution.png`](../../assets/hook-resolution.png) **to** see how a matcher and an `if` condition decide whether a hook runs.

**Key facts:**

* Claude Code checks the matcher first, then `if`, and spawns the handler only when both match, so `if` avoids starting the process at all. A matcher that is omitted or `"*"` activates the group on every occurrence of the event; without `if`, every handler in the matched group runs.
* A `Bash` matcher also covers [Monitor commands](#match-monitor-commands).
* `"args": []` runs a command that takes no arguments in [exec form](#exec-form-and-shell-form).
* The [PowerShell tool](hooks-events.md#powershell) needs a `Bash|PowerShell` matcher, and one `if` rule names exactly one tool, so each tool needs its own handler, such as `"if": "Bash(rm *)"` and `"if": "PowerShell(Remove-Item *)"`. Run a PowerShell script as `"command": "powershell.exe"` with `"args": ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "<script>"]`: `-NoProfile` skips the profile so the hook starts fast, and `-ExecutionPolicy Bypass` lets PowerShell run the local script.
* Exit 0 with no output means no decision: the call continues through the normal [permission flow](https://code.claude.com/docs/en/permissions.md). A hook can deny a call, but staying silent doesn't approve it.
* The Bash examples on this page that parse JSON input use `jq`, which must be installed and on `PATH`.

## Configuration

Hooks are defined in JSON settings files. The configuration has three levels of nesting:

1. Choose a [hook event](#hook-events) to respond to, like `PreToolUse` or `Stop`
2. Add a [matcher group](#matcher-patterns) to filter when it fires, like "for the Bash tool"
3. Define one or more [hook handlers](#hook-handler-fields) to run when matched

See [How a hook resolves](#how-a-hook-resolves) above for a complete walkthrough with an annotated example.

> [!NOTE]
>
> This page uses specific terms for each level: **hook event** for the lifecycle point, **matcher group** for the filter, and **hook handler** for the shell command, HTTP endpoint, MCP tool, prompt, or agent that runs. "Hook" on its own refers to the general feature.

### Hook locations

Where you define a hook determines its scope:

| Location | Scope | Shareable |
| :- | :- | :- |
| `~/.claude/settings.json` | All your projects | No, local to your machine |
| `.claude/settings.json` | Single project | Yes, can be committed to the repo |
| `.claude/settings.local.json` | Single project | No, gitignored when Claude Code saves a setting to it |
| [Plugin](https://code.claude.com/docs/en/plugins/overview.md) `hooks/hooks.json` | When plugin is enabled | Yes, bundled with the plugin |
| [Skill](https://code.claude.com/docs/en/skills.md) frontmatter | The rest of the session once the skill is invoked. See [Hooks in skills and agents](#hooks-in-skills-and-agents) | Yes, defined in the skill file |
| [Subagent](https://code.claude.com/docs/en/sub-agents.md) frontmatter | While that subagent is running | Yes, defined in the subagent file |

[Cloud sessions](https://code.claude.com/docs/en/claude-code-on-the-web.md) don't read your local `~/.claude/settings.json`. In a [self-hosted environment](https://code.claude.com/docs/en/self-hosted-environments-configuration.md#permissions-and-tool-approval), Claude Code also runs the hooks the operator seeded from the runner host's `~/.claude/`, and it runs the hooks in the runner image's managed settings file when that file is among the [managed sources Claude Code applies](https://code.claude.com/docs/en/managed-settings.md#how-claude-code-combines-managed-sources), which by default means only when neither server-managed settings nor an MDM-delivered Claude Code policy supplies the managed tier. See [what carries over from your setup](https://code.claude.com/docs/en/cloud-environments.md#what-carries-over-from-your-setup) for which settings files and plugins, and so which hooks, reach a cloud session.

For details on settings file resolution, see [settings](https://code.claude.com/docs/en/settings.md).

Hooks from settings files, managed policy settings, and plugins also run inside [subagents](https://code.claude.com/docs/en/sub-agents.md). When a subagent calls a tool, tool events such as `PreToolUse` and `PostToolUse` fire the same configured hooks as in the main conversation, and the input carries the `agent_id` and `agent_type` [common input fields](#common-input-fields) that identify the subagent.

Administrators can use [`allowManagedHooksOnly`](https://code.claude.com/docs/en/settings-reference#allowmanagedhooksonly) in [managed settings](https://code.claude.com/docs/en/managed-settings.md) to restrict which hooks run:

* Your user, project, local, and plugin hooks are blocked. Hooks from plugins force-enabled in managed settings `enabledPlugins` are exempt
* Claude Code also narrows your [`statusLine`](https://code.claude.com/docs/en/statusline), [`fileSuggestion`](https://code.claude.com/docs/en/settings-reference#filesuggestion), and [`subagentStatusLine`](https://code.claude.com/docs/en/statusline#subagent-status-lines) settings to managed settings

See [what runs under `allowManagedHooksOnly`](https://code.claude.com/docs/en/settings-reference#what-runs-under-allowmanagedhooksonly).

Hook entries merge across settings levels rather than replacing each other: user, project, and local settings add their own hooks without removing managed ones, and the [`disableAllHooks`](#disable-or-remove-hooks) setting can't disable managed hooks from outside managed settings.

The [HTTP hook allowlists](https://code.claude.com/docs/en/settings-reference.md#hook-and-skill-settings) apply to hooks from every source, including managed policy settings:

* `allowedHttpHookUrls`: when defined at any settings level, Claude Code runs an HTTP hook handler only if its URL matches the merged allowlist
* `httpHookAllowedEnvVars`: when defined, Claude Code interpolates only the environment variables on that list into hook headers

### Matcher patterns

The `matcher` field filters when hooks fire. How a matcher is evaluated depends on the characters it contains:

| Matcher value | Evaluated as | Example |
| :- | :- | :- |
| `"*"`, `""`, or omitted | Match all | fires on every occurrence of the event |
| Only letters, digits, `_`, `-`, spaces, `,`, and `\|` | Exact string, or list of exact strings separated by `\|` or `,` with optional surrounding whitespace | `Bash` matches the Bash tool, and on `PreToolUse` and `PermissionRequest` also [Monitor commands](#match-monitor-commands); `Edit\|Write` and `Edit, Write` each match either tool exactly; `code-reviewer` matches only that agent type |
| Contains any other character | JavaScript regular expression, unanchored | `^Notebook` matches any tool whose name starts with `Notebook`; `mcp__memory__.*` matches every tool from the `memory` server |

A matcher on the regular-expression path is tested with JavaScript's `RegExp.prototype.test`, which succeeds on a match anywhere in the value. `Edit.*` matches both `Edit` and `NotebookEdit`; wrap the pattern in `^` and `$`, as in `^Edit$`, when you need a whole-string match.

`FileChanged` and `StopFailure` use a narrower exact-match set of letters, digits, `_`, and `|` only. A hyphen, space, or comma in a matcher for those two events keeps it on the regular-expression path, and only `|` separates alternatives. Every other event with matcher support in the table that follows accepts `|` or `,`.

The `FileChanged` event doesn't follow these rules when building its watch list. See [FileChanged](hooks-events.md#filechanged).

Each event type matches on a different field:

| Event | What the matcher filters | Example matcher values |
| :- | :- | :- |
| `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied` | tool name | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | how the session started | `startup`, `resume`, `clear`, `compact`, `fork` |
| `Setup` | which CLI flag triggered setup | `init`, `maintenance` |
| `SessionEnd` | why the session ended | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` |
| `Notification` | notification type | `permission_prompt`, `idle_prompt`, `auth_success`, `auth_storage_failure`, `elicitation_dialog`, `elicitation_url_dialog`, `elicitation_complete`, `elicitation_response`, `agent_needs_input`, `agent_completed`, `quota_auto_resume_fired`, `quota_auto_resume_stale`, `quota_auto_resume_disabled`, `plugin_notification` |
| `SubagentStart` | agent type | `general-purpose`, `Explore`, `Plan`, custom agent names, or plugin-scoped names like `^my-plugin:reviewer$` |
| `PreCompact`, `PostCompact` | what triggered compaction | `manual`, `auto` |
| `PreModelSwitch`, `PostModelSwitch` | canonical name of the model the session switches to, as described under [PreModelSwitch](hooks-events.md#premodelswitch) | `claude-opus-5`, `claude-opus-4-6\|claude-opus-5`, `.*opus.*` |
| `SubagentStop` | agent type | same values as `SubagentStart` |
| `ConfigChange` | configuration source | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` |
| `CwdChanged` | no matcher support | always fires on every occurrence |
| `DirectoryAdded` | how the directory was added | `slash_command`, `register_repo_root` |
| `FileChanged` | literal filenames to watch (see [FileChanged](hooks-events.md#filechanged)) | `.envrc\|.env` |
| `StopFailure` | error type | `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `account_on_hold`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `cloud_credential_error`, `unknown` |
| `InstructionsLoaded` | load reason | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` |
| `UserPromptExpansion` | command name | your skill or command names |
| `Elicitation` | MCP server name | your configured MCP server names |
| `ElicitationResult` | MCP server name | same values as `Elicitation` |
| `UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, `MessageDisplay` | no matcher support | always fires on every occurrence |

Matching `StopFailure` on `cloud_credential_error` requires Claude Code v2.1.267 or later, the first version that reports credential-load failures under that value rather than `server_error` or `unknown`.

For most events, Claude Code evaluates the matcher against a field from the [JSON input](#hook-input-and-output) it sends to your hook on stdin. For tool events, that field is `tool_name`. For `PreModelSwitch` and `PostModelSwitch`, Claude Code evaluates the matcher against the canonical name it derives from `to_model`, as described under [PreModelSwitch](hooks-events.md#premodelswitch). Each [hook event](#hook-events) section lists the full set of matcher values and the input schema for that event.

If you add a `matcher` field to an event without matcher support, it is silently ignored.

For tool events, you can filter more narrowly by setting the [`if` field](#common-fields) on individual hook handlers. `if` uses [permission rule syntax](https://code.claude.com/docs/en/permissions.md) to match against the tool name and arguments together, so `"Bash(git *)"` runs when any subcommand of the Bash input matches `git *` and `"Edit(*.ts)"` runs only for TypeScript files.

#### Match MCP tools

[MCP](https://code.claude.com/docs/en/mcp.md) server tools appear as regular tools in tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`), so you can match them the same way you match any other tool name.

MCP tools follow the naming pattern `mcp__<server>__<tool>`, such as `mcp__memory__create_entities`. To match every tool from a server, append `.*` to the server prefix. The `.*` is required: a matcher like `mcp__memory` or `mcp__brave-search` contains only exact-match characters, so it is compared as an exact string and matches no tool.

* `mcp__memory__.*` matches all tools from the `memory` server
* `mcp__brave-search__.*` matches all tools from a server whose name contains a hyphen
* `mcp__.*__write.*` matches any tool whose name starts with `write` from any server

Tools from a [plugin-bundled MCP server](https://code.claude.com/docs/en/mcp.md#plugin-provided-mcp-servers) use a scoped server segment that includes the plugin name: `mcp__plugin_<plugin-name>_<server-name>__<tool>`. A matcher written against the bare server key never fires for these tools. For a plugin named `my-plugin` that bundles a server under the key `db`, a `query` tool appears as `mcp__plugin_my-plugin_db__query`, so the matcher for every tool from that server is `mcp__plugin_my-plugin_db__.*`. Use the same scoped tool name in a handler's [`if` field](#common-fields). See [Plugin-provided MCP servers](https://code.claude.com/docs/en/mcp.md#plugin-provided-mcp-servers) for how the scoped name is built.

#### Match Monitor commands

A [`PreToolUse`](hooks-events.md#pretooluse) or [`PermissionRequest`](hooks-events.md#permissionrequest) hook with a `Bash` matcher also runs on shell commands Claude starts with the [Monitor tool](https://code.claude.com/docs/en/tools-reference.md#monitor-tool), but its `allow` and [`updatedInput`](hooks-events.md#pretooluse-decision-control) have no effect on them. Requires Claude Code v2.1.314 or later. Matchers such as `Bash|PowerShell`, `^Bash$`, and `Bash.*` are `Bash` matchers too. A hook with a `Bash` matcher doesn't run for a [WebSocket watch](https://code.claude.com/docs/en/tools-reference.md#websocket-source), and a `PostToolUse` hook with one doesn't run for Monitor.

A hook that runs for a Monitor command can deny it or have Claude Code ask you about it. To allow or rewrite the command, switch from a `Bash` matcher to one that includes Monitor:

* **Matcher that includes Monitor**: with a matcher such as `Bash|Monitor` or `.*`, or with no matcher, the hook gets the Monitor call's own input, and `allow` and `updatedInput` apply. In [`if`](#common-fields), name Monitor, as in `Monitor(tail *)`, which matches by [the rules `Bash(tail *)` follows](#how-if-patterns-match-bash-commands). If its `if` names Bash, the hook still gets the Monitor call's input, but `allow` and `updatedInput` have no effect
* **`Bash` matcher**: the hook gets a Bash call. In `if`, name Bash, as in `Bash(tail *)`. The hook doesn't run if its `if` names Monitor

### Hook handler fields

Each object in the inner `hooks` array is a hook handler: the shell command, HTTP endpoint, MCP tool, LLM prompt, or agent that runs when the matcher matches. There are five types:

* **[Command hooks](#command-hook-fields)** (`type: "command"`): run a shell command. Your script receives the event's [JSON input](#hook-input-and-output) on stdin and communicates results back through exit codes and stdout.
* **[HTTP hooks](#http-hook-fields)** (`type: "http"`): send the event's JSON input as an HTTP POST request to a URL. The endpoint communicates results back through the response body using the same [JSON output format](#json-output) as command hooks.
* **[MCP tool hooks](#mcp-tool-hook-fields)** (`type: "mcp_tool"`): call a tool on a configured [MCP server](https://code.claude.com/docs/en/mcp.md). The tool's text output is treated like command-hook stdout.
* **[Prompt hooks](#prompt-and-agent-hook-fields)** (`type: "prompt"`): send a prompt to a Claude model for single-turn evaluation. The model returns its decision as JSON. See [Prompt-based hooks](#prompt-based-hooks).
* **[Agent hooks](#prompt-and-agent-hook-fields)** (`type: "agent"`): spawn a subagent that can use tools like Read, Grep, and Glob to verify conditions before returning a decision. Agent hooks are experimental and may change. See [Agent-based hooks](#agent-based-hooks).

When an event fires, its matching hooks run in parallel. If more than 12 of them are prompt or agent hooks, 12 of those run at once and the rest start as running ones finish. Each waiting hook's [`timeout`](#common-fields) starts counting when that hook starts.

If you define the same handler in more than one settings file, it runs once. A plugin's or skill's copy of the same handler stays separate.

Handlers run in the current directory with Claude Code's environment. If the current directory no longer exists, for example a worktree or temp directory that another shell deleted mid-session, Claude Code runs command hooks from the first of these that still exists: the directory the session started in, the project root, your home directory, or the system temp directory. Claude Code records a warning naming the fallback directory in the [debug log](#debug-hooks). For a worktree session that you start from the desktop app, see [What worktrees share with the main checkout](https://code.claude.com/docs/en/worktrees.md#what-worktrees-share-with-the-main-checkout).

The `$CLAUDE_CODE_REMOTE` environment variable is `"true"` in remote web environments and not set in the local CLI. Claude Code v2.1.199 and later sets [`$CLAUDE_CODE_BRIDGE_SESSION_ID`](https://code.claude.com/docs/en/env-vars) to the [Remote Control](https://code.claude.com/docs/en/remote-control.md) session ID while the local session has an active Remote Control connection.

#### Common fields

These fields apply to all hook types:

| Field | Required | Description |
| :- | :- | :- |
| `type` | yes | `"command"`, `"http"`, `"mcp_tool"`, `"prompt"`, or `"agent"` |
| `if` | no | [Permission rule syntax](https://code.claude.com/docs/en/permissions.md#permission-rule-syntax) to filter when this hook runs, such as `"Bash(git *)"` or `"Edit(*.ts)"`. The hook command only runs if the tool call matches the pattern. See the [Bash matching table](#how-if-patterns-match-bash-commands) for how Bash patterns evaluate against subcommands, `$()`, and backticks. Only evaluated on tool events: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, and `PermissionDenied`. On other events, a hook with `if` set never runs |
| `timeout` | no | Seconds before canceling. Claude Code doesn't enforce it on a command hook you run with [`async: true`](#run-hooks-in-the-background). Defaults: 600 for `command`, `http`, and `mcp_tool`; 30 for `prompt`; 60 for `agent`. Claude Code lowers the `command`, `http`, and `mcp_tool` default to 30 on [`UserPromptSubmit`](hooks-events.md#userpromptsubmit), [`PreModelSwitch`](hooks-events.md#premodelswitch), and [`PostModelSwitch`](hooks-events.md#postmodelswitch), and to 10 on [`MessageDisplay`](hooks-events.md#messagedisplay). [`SessionEnd`](hooks-events.md#sessionend) hooks share a 1.5-second budget; if your settings set a longer per-hook `timeout`, Claude Code raises the budget to match, up to 60 seconds |
| `statusMessage` | no | Custom spinner message displayed while the hook runs |
| `once` | no | If `true`, Claude Code removes the hook after its first successful run. A run that fails, blocks with exit code 2, or times out leaves the hook in place, so it runs again on the next matching event. Only honored for hooks declared in [skill frontmatter](#hooks-in-skills-and-agents); ignored in settings files and agent frontmatter |

The `if` field holds exactly one permission rule. There is no `&&`, `||`, or list syntax for combining rules; to apply multiple conditions, define a separate hook handler for each.

In an `if` condition for a file tool, a single-segment directory pattern like `"Edit(src/**)"` matches only the `src` directory in the working directory and the files under it. To match a directory named `src` at any depth, write `"Edit(**/src/**)"`.

#### How `if` patterns match Bash commands

For Bash patterns in the [`if` field](#common-fields), whether your hook command runs depends on the shape of the pattern and the Bash command Claude is invoking. Leading `VAR=value` assignments are stripped before matching.

| `if` pattern | Bash command | Hook runs? | Why |
| :- | :- | :- | :- |
| `Bash(git *)` | `FOO=bar git push` | yes | leading assignments are stripped; `git push` matches |
| `Bash(git *)` | `npm test && git push` | yes | each subcommand is checked; `git push` matches |
| `Bash(rm *)` | `echo $(rm -rf /)` | yes | commands inside `$()` and backticks are checked; `rm -rf /` matches |
| `Bash(rm *)` | `echo $(date)` | no | no subcommand matches `rm *` |
| `Bash(git push *)` | `echo $(date)` | yes | patterns that specify more than the command name run the hook anyway on `$()`, backticks, or `$VAR` |

When Claude Code can't determine which commands the Bash input runs, it runs your hook regardless of the pattern. Because the `if` filter is best-effort, use the [permission system](https://code.claude.com/docs/en/permissions.md) rather than a hook to enforce a hard allow or deny.

#### Command hook fields

In addition to the [common fields](#common-fields), command hooks accept these fields:

| Field | Required | Description |
| :- | :- | :- |
| `command` | yes | Shell command to execute. With `args`, the executable to spawn directly. See [Exec form and shell form](#exec-form-and-shell-form) |
| `args` | no | Argument list. When present, `command` is resolved as an executable and spawned directly with `args` as the argument vector, with no shell involved. See [Exec form and shell form](#exec-form-and-shell-form) |
| `async` | no | If `true`, runs in the background without blocking. See [Run hooks in the background](#run-hooks-in-the-background) |
| `asyncRewake` | no | If `true`, runs in the background and wakes Claude on exit code 2. The hook's stderr, or stdout if stderr is empty, is shown to Claude as a [system reminder](https://code.claude.com/docs/en/glossary.md#system-reminder) so it can react to a long-running background failure |
| `shell` | no | Shell to use for this hook. Accepts `"bash"` or `"powershell"`. Defaults to `"bash"`, or to `"powershell"` on Windows when Git Bash isn't installed. Setting `"powershell"` runs the command via PowerShell on Windows. Does not require `CLAUDE_CODE_USE_POWERSHELL_TOOL` since hooks spawn PowerShell directly. Ignored when `args` is set |
| `onFailure` | no | Whether the action that triggered the hook goes ahead when the hook fails: `"continue"` or `"block"`. See [Block the action when a hook fails](#block-the-action-when-a-hook-fails) for `"block"` and for leaving the field unset. Requires Claude Code v2.1.295 or later |

##### Exec form and shell form

A command hook runs as exec form when `args` is set, and shell form when `args` is omitted. Set `args` whenever the hook references a [path placeholder](#reference-scripts-by-path), since each element is passed as one argument with no quoting. Omit `args` when you need shell features like pipes or `&&`, or when neither concern applies.

**Exec form** runs when `args` is present. Claude Code resolves `command` as an executable on `PATH` and spawns it directly with `args` as the argument vector. There is no shell, so each `args` element is one argument exactly as written, and path placeholders like `${CLAUDE_PLUGIN_ROOT}` are substituted into `command` and into each `args` element as plain strings. Special characters such as apostrophes, `$`, and backticks pass through verbatim because there is no shell to interpret them. No shell tokenization happens on any platform.

**Shell form** runs when `args` is absent. The `command` string is passed to a shell: `sh -c` on macOS and Linux, Git Bash on Windows, or PowerShell when Git Bash isn't installed. Set the `shell` field to choose explicitly. The shell tokenizes the string, expands variables, and interprets pipes, `&&`, redirects, and globs.

> [!NOTE]
>
> On Windows, exec form requires `command` to resolve to a real executable such as a `.exe`. The `.cmd` and `.bat` shims that npm, npx, eslint, and other tools install in `node_modules/.bin` are not executables and can't be spawned without a shell. To run them in exec form, invoke the underlying script with `node` directly, for example `"command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/node_modules/eslint/bin/eslint.js"]`. The `node` plus script-path pattern works on every platform because `node.exe` is a real binary. To run a `.cmd` or `.bat` shim by name, use shell form.

This example runs a Node script bundled with a plugin. Exec form passes the resolved script path as one argument with no quoting:

```json theme={null}
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"]
}
```

The equivalent shell form needs quoting to handle paths with spaces or special characters:

```json theme={null}
{
  "type": "command",
  "command": "node \"${CLAUDE_PLUGIN_ROOT}\"/scripts/format.js --fix"
}
```

Both forms support the same [path placeholders](#reference-scripts-by-path), and both export them as the environment variables `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT`, and `CLAUDE_PLUGIN_DATA` on the spawned process, so a script can read `process.env.CLAUDE_PLUGIN_ROOT` regardless of how it was launched.

Plugin hooks additionally substitute [`${user_config.*}`](https://code.claude.com/docs/en/plugins/manifest-reference#user-configuration) values, in exec form only: the value is substituted into `command` and into each `args` element as a plain string, so no shell re-parses it.

A shell-form plugin hook whose `command` references `${user_config.*}` fails with an [error](https://code.claude.com/docs/en/errors.md#plugin-command-references-user-config) instead of running. To use an option value from a shell-form hook, read the `$CLAUDE_PLUGIN_OPTION_<KEY>` environment variable, such as `$CLAUDE_PLUGIN_OPTION_WEBHOOK_URL` for a `webhook_url` option, or set `args` to switch the hook to exec form. Before v2.1.207, shell-form plugin hook commands also substituted `${user_config.*}`.

> [!NOTE]
>
> In exec form, `command` is the executable name or path only. If `command` is a bare name with no path separator and contains whitespace alongside `args`, Claude Code logs a warning because the spawn will fail: there is no executable named `node script.js`. Move the extra tokens into `args`. Absolute paths with spaces, such as `C:\Program Files\nodejs\node.exe`, are a single valid executable and don't trigger the warning.

#### HTTP hook fields

In addition to the [common fields](#common-fields), HTTP hooks accept these fields:

| Field | Required | Description |
| :- | :- | :- |
| `url` | yes | URL to send the POST request to |
| `headers` | no | Additional HTTP headers as key-value pairs. Values support environment variable interpolation using `$VAR_NAME` or `${VAR_NAME}` syntax. Only variables listed in `allowedEnvVars` are resolved |
| `allowedEnvVars` | no | List of environment variable names that may be interpolated into header values. References to unlisted variables are replaced with empty strings. Required for any env var interpolation to work |
| `onFailure` | no | What happens to the action when the hook fails: `"continue"`, the default, or `"block"`. See [Block the action when a hook fails](#block-the-action-when-a-hook-fails). Requires Claude Code v2.1.295 or later |

Claude Code sends the hook's [JSON input](#hook-input-and-output) as the POST request body with `Content-Type: application/json`. The response body uses the same [JSON output format](#json-output) as command hooks.

Error handling differs from command hooks; see [HTTP response handling](#http-response-handling).

#### MCP tool hook fields

In addition to the [common fields](#common-fields), MCP tool hooks accept these fields:

| Field | Required | Description |
| :- | :- | :- |
| `server` | yes | Name of a configured MCP server. For a [plugin-bundled server](https://code.claude.com/docs/en/mcp.md#plugin-provided-mcp-servers), this is the scoped name `plugin:<plugin-name>:<server-name>`, such as `plugin:my-plugin:db`, not the bare server key |
| `tool` | yes | Name of the tool to call on that server |
| `input` | no | Arguments passed to the tool. String values support `${path}` substitution from the hook's [JSON input](#hook-input-and-output), such as `"${tool_input.file_path}"` |

##### How the tool's result is read

Claude Code reads the tool's text content the same way it reads command-hook stdout, following the [parsing rule under exit code 0](#exit-code-0). If the tool returns `isError: true`, the hook produces a non-blocking error and execution continues.

##### When the server is still connecting

On events where a hook can block or change the result, such as `PreToolUse` or `Stop`, Claude Code waits for a connecting server before it calls the tool, for at most [`MCP_TIMEOUT`](https://code.claude.com/docs/en/env-vars) and within the hook's own [`timeout`](#common-fields). On observational events, such as `Notification` or `SessionEnd`, it doesn't wait.

A server showing the [`cached` status](https://code.claude.com/docs/en/mcp#server-status-detail) connects when the hook calls its tool. If the server isn't connected at that point, the hook produces a non-blocking error and execution continues. The hook never starts an OAuth flow, so [authenticate the server from `/mcp`](https://code.claude.com/docs/en/mcp#authenticate-with-remote-mcp-servers) first.

##### Events that fire before MCP servers are available

`SessionStart` at launch, including with `--continue` or `--resume`, and every `Setup` event fire before the session's MCP servers are available to hooks. Claude Code skips their `mcp_tool` hooks without calling the tool, and the [debug log](#debug-hooks) records `mcp_tool hooks are not available for the 'SessionStart' hook event (no MCP client context)`, or the same message naming `Setup`. When `SessionStart` fires again later in the session, after `/clear` or a compaction, its `mcp_tool` hooks run. For anything the session needs at launch, use a `type: "command"` hook on `SessionStart` instead.

#### Prompt and agent hook fields

In addition to the [common fields](#common-fields), prompt and agent hooks accept these fields:

| Field | Required | Description |
| :- | :- | :- |
| `prompt` | yes | Prompt text to send to the model. Use `$ARGUMENTS` as a placeholder for the hook input JSON. Escape with a backslash to include literal text: `\$1.00` renders as `$1.00` |
| `model` | no | Model to use for evaluation. Defaults to the model Claude Code uses for [background functionality](https://code.claude.com/docs/en/model-config.md#environment-variables) |

### Reference scripts by path

Use these placeholders to reference hook scripts relative to the project or plugin root, regardless of the working directory when the hook runs:

* `${CLAUDE_PROJECT_DIR}`: the project root where the session started. Claude Code also sets this variable in the environment of [stdio MCP servers](https://code.claude.com/docs/en/mcp.md#option-3-add-a-local-stdio-server) and plugin LSP servers.
* `${CLAUDE_PLUGIN_ROOT}`: the plugin's installation directory, for scripts bundled with a [plugin](https://code.claude.com/docs/en/plugins/overview.md). See [plugin environment variables](https://code.claude.com/docs/en/plugins/manifest-reference.md#environment-variables) for how the path behaves across updates.
* `${CLAUDE_PLUGIN_DATA}`: the plugin's [persistent data directory](https://code.claude.com/docs/en/plugins/components.md#path-variables-and-persistent-data), for dependencies and state that should survive plugin updates.

> [!NOTE]
>
> **Worktrees are different.** If Claude enters a [worktree](https://code.claude.com/docs/en/worktrees.md) during the session, Claude Code keeps `${CLAUDE_PROJECT_DIR}` where it was and passes the worktree path to your hooks a different way:
>
> * **`${CLAUDE_PROJECT_DIR}` stays put**: it still points at the project root where the session started, so a command such as `${CLAUDE_PROJECT_DIR}/.claude/hooks/check-style.sh` still runs the script in the main checkout.
> * **`cwd` follows Claude**: the `cwd` field in the hook's [input JSON](#common-input-fields) is the worktree root after Claude enters a worktree, and the new directory after Claude runs `cd`. Read it when a hook needs to know which directory Claude is working in.
>
> For a worktree session that you start from the desktop app, see [What worktrees share with the main checkout](https://code.claude.com/docs/en/worktrees.md#what-worktrees-share-with-the-main-checkout) for where `${CLAUDE_PROJECT_DIR}` points.

Prefer [exec form](#exec-form-and-shell-form) for any hook that references a path placeholder. In shell form, wrap each placeholder in double quotes.

> **Plugin scripts**
>
> Define plugin hooks in `hooks/hooks.json` with an optional top-level `description` field. When a plugin is enabled, its hooks merge with your user and project hooks.
>
> This example runs a formatting script bundled with the plugin:
>
> ```json theme={null}
> {
>   "description": "Automatic code formatting",
>   "hooks": {
>     "PostToolUse": [
>       {
>         "matcher": "Write|Edit",
>         "hooks": [
>           {
>             "type": "command",
>             "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format.sh",
>             "args": [],
>             "timeout": 30
>           }
>         ]
>       }
>     ]
>   }
> }
> ```
>
> See the [plugin components reference](https://code.claude.com/docs/en/plugins/components.md#hooks) for details on creating plugin hooks.

### Hooks in skills and agents

In addition to settings files and plugins, hooks can be defined directly in [skills](https://code.claude.com/docs/en/skills.md) and [subagents](https://code.claude.com/docs/en/sub-agents.md) using frontmatter, in the same configuration format as settings-based hooks. How long Claude Code keeps them registered depends on the component:

* **Subagent hooks**: Claude Code runs them only while that subagent is running and removes them when it finishes. Claude Code converts a `Stop` hook here to `SubagentStop`, the event it fires when a subagent completes.
* **Skill hooks**: Claude Code registers them when you or Claude invoke the skill and keeps running them for the rest of the session, on turns after the skill's own turn as well. To have Claude Code remove a hook after its first successful run instead, set [`once: true`](#common-fields) on it.

The frontmatter takes a `hooks` key in the same shape as the `hooks` object of a settings file, as in `hooks: { PreToolUse: [ { matcher: "Bash", hooks: [ { type: command, command: "./scripts/security-check.sh" } ] } ] }` written as YAML. Subagents use the same format in their YAML frontmatter.

Frontmatter hooks in a project skill follow the same [workspace trust rule as hooks in settings files](#workspace-trust). Claude Code registers them when you or Claude invoke the skill, including in a `-p` run in a folder you haven't trusted.

Frontmatter hooks in a project subagent run only after you accept the [workspace trust dialog](https://code.claude.com/docs/en/permissions.md#project-allow-rules-and-workspace-trust) for the folder the agent file came from. A `-p` session doesn't count as accepting it. [What runs before you trust a folder](https://code.claude.com/docs/en/permissions.md#what-runs-before-you-trust-a-folder) compares this with the settings-file rule, and the subagents page lists [which scopes are exempt](https://code.claude.com/docs/en/sub-agents.md#hooks-in-subagent-frontmatter).

#### Limits on skill hooks

When a skill's frontmatter hooks don't fire after you or Claude invoke the skill, run [`/hooks`](#the-hooks-menu) in that session. If it lists them, see [Hook not firing](https://code.claude.com/docs/en/hooks-guide.md#hook-not-firing). If it lists none of them, the skill may be under a plugin-only lock or past a hook limit, and runs without any of its frontmatter hooks. Check for each case:

* **Plugin-only lock**: your organization's administrator can lock hooks to plugins and managed settings with the [`strictPluginOnlyCustomization`](https://code.claude.com/docs/en/settings-reference#strictpluginonlycustomization-hooks) managed setting. A skill keeps its frontmatter hooks under that lock only if it's a plugin skill, a [bundled skill](https://code.claude.com/docs/en/skills.md#bundled-skills), or a skill in the [managed settings directory](https://code.claude.com/docs/en/managed-settings.md#delivery-mechanisms). The hooks in your own settings files don't run either.
  * **Check**: type `/status` in a Claude Code session. If the [`Setting sources` line](https://code.claude.com/docs/en/settings#check-what-your-organization-enforces) includes `Enterprise managed settings`, ask your administrator whether `strictPluginOnlyCustomization` locks hooks.
  * **Fix**: move the skill into a [plugin](https://code.claude.com/docs/en/plugins/create.md#convert-an-existing-claude-setup), because plugin skills keep their frontmatter hooks. List the plugin in a [marketplace](https://code.claude.com/docs/en/plugins/create-marketplace.md#create-a-marketplace), then install it from there. If Claude Code refuses the marketplace with [`is blocked by enterprise policy`](https://code.claude.com/docs/en/plugins/troubleshooting#marketplace-source-is-blocked-by-enterprise-policy), ask your administrator to allow that marketplace.
* **Hook limit**: in Claude Code v2.1.304 or later, each source of skills has its own limit per session. Your project, your personal skills folder, and each plugin count as separate sources. The skills from one source can register at most 1,024 hooks. Those hooks' matchers can total at most 16,384 characters. A matcher with several hooks under it counts once for each hook.
  * **Check**: repeat the session where the hook didn't fire, with debug logging on:
    1. Start a new session from your shell with `claude --debug`. If you don't start sessions from a shell, type [`/debug`](https://code.claude.com/docs/en/commands#all-commands) first in the new session instead.
    2. Invoke the same skills in the same order, including the ones Claude invoked, because both totals build up skill by skill. Ask Claude to invoke any skill you can't type as a command.
    3. Search the [debug log](#debug-hooks) for `registers none of its hooks`. A line containing that text names the skill that went past the limit.
  * **Fix**: declare fewer hooks or shorter matchers in that skill or in the other skills from its source, then start a new session. If those skills aren't yours to edit, ask their author for that change. Until then, start a new session and invoke the skill you need before any other skill from its source.

If neither case is yours, check for [frontmatter that didn't parse](https://code.claude.com/docs/en/skills.md#skill-not-triggering).

### The `/hooks` menu

Type `/hooks` in Claude Code to open a read-only browser for your configured hooks. The list labels each hook with where it comes from, such as user settings, project settings, local settings, a plugin, or the current session.

Select a hook to see the full text of what it runs and where it's defined, such as the path of its settings file or the name of its plugin.

To browse all hook events, including ones with no hooks configured, select `All events` at the end of the list.

### Disable or remove hooks

To remove a hook defined in a settings file, delete its entry from that file.

To temporarily disable all hooks without removing them, set `"disableAllHooks": true` in your settings file. Claude Code reads the value left after [settings precedence](https://code.claude.com/docs/en/settings.md#settings-precedence) applies, so a `"disableAllHooks": false` in a project's `.claude/settings.json` overrides a `true` in your user settings. To turn hooks off for one run whatever the project's settings say, pass `--settings '{"disableAllHooks": true}'`, which takes precedence over project and local settings. There is no way to disable an individual hook while keeping it in the configuration.

Direct edits to hooks in settings files are normally picked up automatically by the file watcher.

## Hook input and output

Command hooks receive JSON data via stdin and communicate results through exit codes, stdout, and stderr. HTTP hooks receive the same JSON as the POST request body and communicate results through the HTTP response body. This section covers fields and behavior common to all events. Each event's section under [Hook events](#hook-events) includes its specific input schema and decision control options.

On macOS and Linux, command hooks run in their own session without a controlling terminal. The hook process and any child processes can't open `/dev/tty` or send escape sequences directly to the Claude Code interface. Windows has no `/dev/tty`.

To surface a message to the user on any platform, return [`systemMessage`](#json-output) in JSON output. Some events discard it or deliver it elsewhere, and each [event's section](#hook-events) says so. To trigger a desktop notification, set a window title, or ring the bell, return [`terminalSequence`](#emit-terminal-notifications) instead.

### Common input fields

Hook events receive these fields as JSON, in addition to event-specific fields documented in each [hook event](#hook-events) section. For command hooks, this JSON arrives via stdin. For HTTP hooks, it arrives as the POST request body.

| Field | Description |
| :- | :- |
| `session_id` | Current session identifier |
| `prompt_id` | UUID identifying the user prompt currently being processed. Matches the [`prompt.id` attribute on OpenTelemetry events](https://code.claude.com/docs/en/monitoring-usage#event-correlation-attributes), so you can correlate hook output with telemetry for a single prompt. Absent until the first user input |
| `transcript_path` | Path to conversation JSON. The transcript file is written asynchronously and may lag the in-memory conversation, so it may not yet include the current turn's most recent messages when a hook fires. Hooks that need the final assistant text of the current turn should use `last_assistant_message` on [Stop](hooks-events.md#stop) and [SubagentStop](hooks-events.md#subagentstop) instead of reading the transcript |
| `cwd` | Current working directory when the hook is invoked |
| `scratchpad_dir` | Path to the session's [scratchpad directory](https://code.claude.com/docs/en/claude-directory.md#session-scratchpad-directory), where Claude keeps temporary working files. Absent when the session has no scratchpad or the temp directory is unavailable. Requires Claude Code v2.1.257 or later |
| `permission_mode` | Current [permission mode](https://code.claude.com/docs/en/permissions.md#permission-modes): `"default"`, `"plan"`, `"acceptEdits"`, `"auto"`, `"dontAsk"`, or `"bypassPermissions"`. The mode labeled **Manual** arrives as `"default"`, never as `"manual"`, so scripts that match `"default"` keep working. Not all events receive this field. In the official per-event examples it appears on `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionDenied`, `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `SubagentStop`, `TaskCompleted` and `TeammateIdle`, and not on the other events |
| `effort` | Object whose `level` is the [effort level](https://code.claude.com/docs/en/model-config.md#adjust-effort-level) setting when the hook runs, including a skill's, subagent's, or `ultrathink` level: `"low"`, `"medium"`, `"high"`, `"xhigh"`, or `"max"`. Present for `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, and other events with a tool-use context, on models with effort. If the model doesn't support your level, `level` is the level that ran. A level you changed can show here before it [starts](https://code.claude.com/docs/en/model-config.md#when-a-new-effort-level-starts). `$CLAUDE_EFFORT` holds the same level. |
| `hook_event_name` | Name of the event that fired |

`agent_id` and `agent_type` tell your script which agent a hook fired in, such as a subagent, an [in-process teammate](https://code.claude.com/docs/en/agent-teams.md#choose-a-display-mode), or the agent you chose with `--agent`:

| Field | Description |
| :- | :- |
| `agent_id` | Unique identifier for the subagent or in-process teammate the hook fires in. |
| `agent_type` | Agent name (for example, `"Explore"` or `"security-reviewer"`). Present when the session uses `--agent` or the hook fires inside a subagent. For subagents, the subagent's type takes precedence over the session's `--agent` value. See [SubagentStart](hooks-events.md#subagentstart) for the values custom and plugin subagents report and how to write a matcher against a plugin-scoped name. |

Only [`SessionStart`](hooks-events.md#sessionstart) hooks can receive a `model` field, and Claude Code doesn't always include it. [`PreModelSwitch`](hooks-events.md#premodelswitch) and [`PostModelSwitch`](hooks-events.md#postmodelswitch) hooks receive `from_model` and `to_model` instead, so use a PostModelSwitch hook to follow the model as it changes during a session.

There is no `$CLAUDE_MODEL` environment variable. The hook can read `$ANTHROPIC_MODEL` if you set it in your shell, but that value doesn't change when you switch models with `/model` during a session.

A hook process inherits the parent environment, apart from the `OTEL_*` exporter variables that Claude Code [removes from every subprocess it spawns](https://code.claude.com/docs/en/monitoring-usage.md#administrator-configuration) and, when [`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`](https://code.claude.com/docs/en/env-vars#variables) is set to `1`, the variables it strips. In a session that [gets the HIPAA configuration](https://code.claude.com/docs/en/hipaa-setup.md#check-how-developers-sign-in-and-connect), Claude Code also [removes Anthropic credentials](https://code.claude.com/docs/en/hipaa-setup.md#anthropic-credentials-in-commands-hooks-and-mcp-servers) from the hook's environment.

In the input, `transcript_path` is a `.jsonl` file under `~/.claude/projects/`, and `scratchpad_dir` has the form `/tmp/claude-<uid>/-<project-path-with-dashes>/<session_id>/scratchpad`. A `PreToolUse` input for Bash adds `tool_name`, `tool_input` (`command`, `description`, `timeout`, `run_in_background`) and `tool_use_id`. The `tool_name`, `tool_input`, and `tool_use_id` fields are event-specific. Each [hook event](#hook-events) section documents the additional fields for that event.

### Exit code output

When your hook's run finishes, Claude Code uses its exit code to decide whether to continue with the action that triggered it, such as a tool call or a prompt:

* **Success**: your hook exits 0. Claude Code applies any [JSON output](#json-output) fields your hook printed, and the action goes ahead unless those fields block or deny it. [Hooks that start a background process](#hooks-that-start-a-background-process) covers the exception.
* **Blocking error**: your hook exits 2. On [events that can block](#exit-code-2-behavior-per-event), Claude Code stops the action.
* **Non-blocking error**: your hook exits with any other code, or fails in some other way, such as not starting or printing invalid JSON. The action goes ahead, except for hooks [whose failure blocks the action](#block-the-action-when-a-hook-fails), for example a hook with `onFailure` set to `"block"`. On events such as `PreToolUse`, you see a `<hook name> hook error` notice in the transcript.

What your hook prints to stdout can change the outcome. For example, when a `PreToolUse` hook exits 1 but prints JSON that passes validation, that JSON can still decide what happens. To find your hook's outcome on an event such as `PreToolUse`, match what it printed to stdout in the first column with its exit code along the top:

| Stdout | Exit 0 | Exit 2 | Any other exit code |
| :- | :- | :- | :- |
| JSON object that passes [schema validation](#json-output) | Success. The fields apply | Blocking error. Claude Code still reads the fields, but they can't override the block | Success. Claude Code ignores the exit code, and the fields alone decide. For hooks [whose failure blocks the action](#block-the-action-when-a-hook-fails), the run counts as a failure instead |
| JSON that [can't be parsed](#exit-code-0) or fails schema validation | Non-blocking error. The notice carries the parse or validation message | Blocking error. Your stderr is the reason | Non-blocking error. The notice carries the parse or validation message |
| [Plain text](#exit-code-0), or nothing | Success | Blocking error. Your stderr is the reason | Non-blocking error. The notice carries the first line of your stderr |

Some events have their own rules:

* **`WorktreeCreate`**: any non-zero exit code makes worktree creation fail, whatever your JSON says.
* **`WorktreeRemove`**: any non-zero exit code makes worktree removal fail if the directory still exists afterward.
* **`Stop`, `SubagentStop`, `TaskCompleted`, and a plugin's `UserPromptSubmit` hook**: when your hook exits 2 with nothing on stdout and its stderr says a file is missing, such as `No such file or directory`, Claude Code treats the run as a non-blocking error.
* **`Elicitation` and `ElicitationResult`**: Claude Code applies your `hookSpecificOutput` when your hook exits 0, and ignores it on any other exit code.
* **Events that discard hook output, such as `StopFailure`**: Claude Code ignores your JSON on any exit code, apart from side-effect fields like `terminalSequence`, which still fire.

To check what exit code 2 does on your event, see [Exit code 2 behavior per event](#exit-code-2-behavior-per-event). To check which decision fields it honors, see [Decision control](#decision-control).

#### Exit code 0

Exit 0 means success, and is the intended exit code when you print JSON for structured control. When your hook exits 0 but prints JSON that can't be parsed or fails [schema validation](#json-output), the action goes ahead unless the hook is one [whose failure blocks the action](#block-the-action-when-a-hook-fails). Instead of a success with your fields applied, the run is a [non-blocking error](#exit-code-output).

To fix your output, use the parse or validation message that the `<hook name> hook error` notice carries. For a hook that isn't [async](#how-async-hooks-execute), your stdout counts as [JSON output](#json-output) only when you print one JSON object, on one line or several, with nothing around it but whitespace. Claude Code reads any other stdout as plain text or a parse failure:

* **Output that doesn't start with `{`, or that starts with `{` and doesn't end with `}`**: plain text. A JSON array and a quoted JSON string are plain text by this rule.
* **Two or more lines that each parse as JSON on their own, the first starting with `{` and the last ending with `}`**: plain text when no line is a JSON output object that sets a field. When one line is, the output is a parse failure, so print that object with nothing else on stdout.
* **Anything else that starts with `{` and ends with `}` but isn't valid JSON**: a parse failure.

For most events, Claude Code writes stdout to the debug log and doesn't show it in the transcript. On these events, your stdout reaches Claude or the compaction summary:

* **`UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, and `PostModelSwitch`**: Claude Code adds plain-text stdout as context that Claude can see and act on. It doesn't add stdout it failed to parse.
* **`PreCompact`**: your stdout becomes [instructions for the compaction summary](hooks-events.md#precompact-output)

Claude never sees stderr from a hook that exits 0. To read it yourself on events such as `PreToolUse`, enable [debug logging](#debug-hooks). To surface a warning to Claude from a `PostToolUse` or `PostToolUseFailure` hook, exit 2 instead so [Claude sees the stderr](#exit-code-2-behavior-per-event) even though the tool already ran.

#### Exit code 2

Exit with code 2 to block the action. On [events that can block](#exit-code-2-behavior-per-event), Claude Code stops the action: a `PreToolUse` hook blocks the tool call, for example, and a `UserPromptSubmit` hook rejects the prompt.

The message that comes with the block is your hook's stderr. If your hook also printed JSON that makes a blocking decision, Claude Code uses that decision's reason instead.

Exit 2 blocks even when your hook prints JSON:

* **JSON that passes schema validation**: Claude Code still reads the [JSON output](#json-output) fields, but they can't override the block. Even a `permissionDecision` of `"allow"` doesn't let the action through. On `Elicitation` and `ElicitationResult`, an exit-2 hook's `hookSpecificOutput` is ignored.
* **JSON that fails schema validation**: the hook still blocks. Claude Code uses your stderr as the blocking reason and records the validation failure in the debug log.

This script blocks `rm` commands by exiting 2 and leaves every other command to the normal permission flow:

```bash theme={null}
#!/bin/bash
# Reads JSON input from stdin, checks the command
input=$(cat)
command=$(jq -r '.tool_input.command' <<<"$input")

if [[ "$command" == rm* ]]; then
  echo "Blocked: rm commands are not allowed" >&2
  exit 2  # Blocking error: tool call is prevented
fi

exit 0  # No decision: the normal permission flow applies
```

With this script registered as a `PreToolUse` hook on `Bash`, a command that starts with `rm` is blocked, and Claude receives the hook's stderr as the tool's error, prefixed with the event name, the tool name, and the hook's command:

```text theme={null}
PreToolUse:Bash hook error: [${CLAUDE_PROJECT_DIR}/.claude/hooks/no-rm.sh]: Blocked: rm commands are not allowed
```

#### Other exit codes

A `<hook name> hook error` notice with `Failed with non-blocking status code:` means your hook's exit code wasn't 0 or 2 and its stdout was plain text or empty. Unless the hook is one [whose failure blocks the action](#block-the-action-when-a-hook-fails), this is a [non-blocking error](#exit-code-output), so your hook didn't stop the action. To capture your hook's full stderr rather than the first line the notice shows, enable [debug logging](#debug-hooks).

For example, when a `PreToolUse` hook on `Bash` prints `something broke` to stderr and exits 1, the `PreToolUse:Bash hook error` notice carries this line:

```text theme={null}
Failed with non-blocking status code: something broke
```

If the notice carries the shell's `No such file or directory` message, as in the following line, the hook never ran, for example because its script path doesn't exist:

```text theme={null}
Failed with non-blocking status code: /bin/sh: /path/to/hook.sh: No such file or directory
```

If the path is wrong, correct it where the hook is configured. In shell form, when the script path doesn't exist or isn't executable, the shell exits with a code like 127 and the notice carries the interpreter's message. Unless the hook is one [whose failure blocks the action](#block-the-action-when-a-hook-fails), a hook that can't start is a non-blocking error too.

When you set up a policy hook, watch for this notice on its first run, because a mistyped path in `settings.json` means the hook never runs. To block the action when the hook can't start, set [`onFailure: "block"`](#block-the-action-when-a-hook-fails).

> [!WARNING]
>
> Exit code 1 without valid JSON output is a non-blocking error unless the hook is one [whose failure blocks the action](#block-the-action-when-a-hook-fails), even though 1 is the conventional Unix failure code. If your hook is meant to enforce a policy, use `exit 2`.

#### Timeouts

Apart from a command hook you run with [`async: true`](#run-hooks-in-the-background), Claude Code cancels a `command`, `http`, or `mcp_tool` hook that reaches its [`timeout`](#common-fields), discarding the hook's output, so on most events a timed-out hook renders no decision. On [`PreModelSwitch`](hooks-events.md#premodelswitch), a hook canceled at its timeout blocks the model switch.

On `PreToolUse`, a timed-out `command`, `http`, or `mcp_tool` hook doesn't block the tool call, except for hooks [whose failure blocks the action](#block-the-action-when-a-hook-fails). The call continues through the normal [permission flow](https://code.claude.com/docs/en/permissions.md), so don't count on a stalled hook to act as a gate. To block the call when a `command` or `http` hook times out, set [`onFailure: "block"`](#block-the-action-when-a-hook-fails). An [Agent SDK callback hook](https://code.claude.com/docs/en/agent-sdk/hooks.md) that exceeds its timeout [blocks the tool call](hooks-events.md#pretooluse).

#### Hooks that start a background process

If your command hook makes its decision in a background process and exits, a deny that process prints after Claude Code has stopped reading doesn't block the tool call. For a hook that isn't [async](#run-hooks-in-the-background), Claude Code finishes reading the hook's output shortly after the hook's own process exits.

Print the decision before you start a background process, and redirect that process's stdout and stderr. If your script prints an allow, then starts a background process without redirecting that process's stdout and stderr, Claude Code blocks the tool call. The hook error includes `refusing to honor the suspect capture`.

This `PreToolUse` hook script prints the decision with `policy-check.sh`, then uploads metrics in the background:

```bash theme={null}
#!/bin/bash
"$CLAUDE_PROJECT_DIR"/.claude/hooks/policy-check.sh || exit $?
"$CLAUDE_PROJECT_DIR"/.claude/hooks/upload-metrics.sh >/dev/null 2>&1 &
```

The rest of the script does this:

* **`|| exit $?`**: makes the check's exit code the hook's own, so a check that exits 2 to deny still blocks. Otherwise the hook exits with the last line's code, which is 0.
* **`>/dev/null 2>&1 &`**: runs `upload-metrics.sh` in the background with its output redirected, so it doesn't keep the hook's output open.

To test the script, make `policy-check.sh` exit 2, then trigger a tool call that the hook matches. The tool call is blocked.

#### Block the action when a hook fails

On most events, when a hook fails or times out, Claude Code still carries out the action. A policy hook with a wrong path or a crashing script then lets everything through. To block the action instead, set `"onFailure": "block"` on a `command` or `http` hook. Requires Claude Code v2.1.295 or later. For Agent SDK callback hooks, see [Block the action when a callback fails](https://code.claude.com/docs/en/agent-sdk/hooks.md#block-the-action-when-a-callback-fails).

> [!NOTE]
>
> On Windows without Git Bash, a shell-form `PreToolUse` or `PermissionRequest` command hook that fails with `onFailure` unset can instead [block the tool call](#failed-hooks-on-windows-without-git-bash).

This `PreToolUse` hook in `.claude/settings.json` runs a project script before each Bash command, and blocks the command if the script fails:

```json theme={null}
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/check-command.js"],
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

To test it, leave `check-command.js` missing and ask Claude to run a Bash command such as `ls`. Claude Code blocks the call, and the error includes `failed; blocking because onFailure is "block"` followed by node's own error output, trimmed here to one line:

```text theme={null}
PreToolUse:Bash hook error: [node ${CLAUDE_PROJECT_DIR}/.claude/hooks/check-command.js]: failed; blocking because onFailure is "block"
Error: Cannot find module '/path/to/project/.claude/hooks/check-command.js'
```

After a timeout, the message says `timed out` instead of `failed`. Without `onFailure` set, the same missing script is a non-blocking error and `ls` runs.

Each of these counts as a failure:

* **Can't start**: a command hook fails to start, for example because the script or executable doesn't exist
* **Exit code other than 0 or 2**: counts for a command hook even if it printed JSON that allows the action, such as `permissionDecision: "allow"`. To return a JSON decision, exit 0
* **HTTP error**: an HTTP hook's connection fails, or the response status isn't 2xx
* **Timeout**: the hook reaches its [`timeout`](#common-fields)
* **Invalid output**: the JSON output [can't be parsed](#exit-code-0) or fails [schema validation](#json-output). For an HTTP hook, a 2xx body that is neither empty nor a JSON object also counts. Plain-text stdout from a command hook isn't a failure

With `"block"` set, a failure does what [exit code 2 does on that event](#exit-code-2-behavior-per-event), except on `PermissionRequest`, where it denies the request. For example, a `PreToolUse` failure blocks the tool call and a `UserPromptSubmit` failure blocks the prompt.

The field has no effect on these hooks:

* **`Stop`, `SubagentStop`, `TaskCompleted`, and `TeammateIdle` hooks**: exit code 2 on these events sends Claude back to keep working, and Claude can't repair a hook that won't run
* **Background command hooks**: command hooks that set [`async` or `asyncRewake`](#run-hooks-in-the-background)

#### Failed hooks on Windows without Git Bash

If the error for a blocked tool call includes this text, a `PreToolUse` or `PermissionRequest` command hook failed or timed out and blocked the call:

```text theme={null}
blocking because Git Bash wasn't found, so only exit code 0 or 2 counts as this hook's verdict.
```

If the error also says `PowerShell started no program`, start with [the fixes for a `command` that is only quoted strings](#powershell-started-no-program), which PowerShell prints instead of running.

Without Git Bash, any exit code other than 0 or 2 from that hook counts as a [failure](#block-the-action-when-a-hook-fails), even when it prints JSON that doesn't deny the call. To find out why the hook failed, check the [debug log](#debug-hooks). Then pick the fix that matches your hook:

* **The call should go ahead when the hook fails**: add [`"onFailure": "continue"`](#block-the-action-when-a-hook-fails) to the hook
* **The hook exits 1 to warn but must block when it crashes**: with `"onFailure": "continue"`, the call goes ahead on exit code 1, warning or crash alike. Add `"onFailure": "block"` instead, and have the script exit 0 where it warns, so those calls go ahead. To still show the warning on `PreToolUse`, print it to stdout as the [`systemMessage`](#json-output) field of one JSON object.
* **The hook is written for Bash**: without Git Bash, a [shell-form](#exec-form-and-shell-form) hook with no `shell` set runs in PowerShell, where it can fail. Install [Git for Windows](https://git-scm.com/downloads/win), or set [`CLAUDE_CODE_GIT_BASH_PATH`](https://code.claude.com/docs/en/env-vars) if Git Bash is installed where Claude Code doesn't find it. Then start a new session.
* **The hook runs one `.exe`, not a `.cmd` or `.bat` file**: put the program in `command` and its arguments in `args` to use exec form, and add `"onFailure": "block"`. Claude Code then starts the program with no shell. Without `"onFailure": "block"`, the call can go ahead when the program fails, is missing, or times out
* **A PowerShell guard hook that must block on failure**: with `onFailure` unset, it stops doing so once Git for Windows is installed and Claude Code finds Git Bash. Add `"onFailure": "block"` so a failure or a timeout blocks the call with or without Git Bash. Also set `"shell": "powershell"` so the hook keeps running in PowerShell from then on instead of in Git Bash

Before v2.1.309, the message read `blocking because Git Bash wasn't found and this hook doesn't set "shell" to "powershell", so only exit code 0 or 2 counts as its verdict.`

#### PowerShell started no program

A hook with this error ran in PowerShell, which prints a `command` that is only quoted strings, such as `"command": "\"C:\\Tools\\guard.exe\""`, instead of running it.

* **To print text, such as JSON**: set `"shell": "powershell"`, and the hook exits 0
* **To run a `.ps1`, `.cmd`, or `.bat` file, or a `.exe` whose path has a variable**: set `"shell": "powershell"` and put `&` before the quoted path. Leave `$HOME` as written, and spell environment variables as the [`check.ps1` example](#reference-scripts-by-path-in-powershell-hooks) spells `$env:CLAUDE_PROJECT_DIR`
* **To run one `.exe` at a path without `$`**: remove the inner quotes from `command`, then apply the [fix for a hook that runs one `.exe`](#failed-hooks-on-windows-without-git-bash), writing `"args": []` if the program takes no arguments
* **To run a script written for Bash**: apply the [fix for a hook written for Bash](#failed-hooks-on-windows-without-git-bash)

#### Exit code 2 behavior per event

Exit code 2 is the way a hook signals "stop, don't do this." The effect depends on the event, because some events represent actions that can be blocked (like a tool call that hasn't happened yet) and others represent things that already happened or can't be prevented.

| Hook event | Can block? | What happens on exit 2 |
| :- | :- | :- |
| `PreToolUse` | Yes | Blocks the tool call |
| `PermissionRequest` | No | Exit code 2 isn't honored for this event and the permission flow proceeds unchanged. Deny through the [`decision` object](hooks-events.md#permissionrequest-decision-control) instead |
| `UserPromptSubmit` | Yes | Blocks the prompt, so it never reaches Claude. See [What a blocked prompt leaves behind](hooks-events.md#what-a-blocked-prompt-leaves-behind) |
| `UserPromptExpansion` | Yes | Blocks the expansion |
| `Stop` | Yes | Prevents Claude from stopping, continues the conversation |
| `SubagentStop` | Yes | Prevents the subagent from stopping |
| `TeammateIdle` | Yes | Prevents the teammate from going idle, so it continues working |
| `TaskCreated` | Yes | Rolls back the task creation |
| `TaskCompleted` | Yes | Prevents the task from being marked as completed |
| `ConfigChange` | Yes | Blocks the configuration change from taking effect (except `policy_settings`) |
| `StopFailure` | No | Output and exit code are ignored, except `terminalSequence` |
| `PostToolUse` | No | Shows stderr to Claude; the tool already ran |
| `PostToolUseFailure` | No | Shows stderr to Claude; the tool already failed |
| `PostToolBatch` | Yes | Stops the agentic loop before the next model call |
| `PermissionDenied` | No | Exit code and stderr are ignored because the denial already occurred. Use JSON `hookSpecificOutput.retry: true` to tell the model it may retry; Claude Code ignores `retry: true` for [no-verdict denials](hooks-events.md#permissiondenied-decision-control) |
| `Notification` | No | Exit code and stderr are ignored |
| `SubagentStart` | No | Shows stderr to user only |
| `SessionStart` | No | Shows stderr to user only |
| `Setup` | No | Exit code and stderr are ignored |
| `SessionEnd` | No | Shows stderr to user only |
| `CwdChanged` | No | Shows stderr to user only |
| `DirectoryAdded` | No | Stderr goes to the debug log; the directory is already added |
| `FileChanged` | No | Shows stderr to user only |
| `PreCompact` | Yes | Blocks compaction |
| `PostCompact` | No | Shows stderr to user only |
| `PreModelSwitch` | Yes | Blocks the model switch and shows stderr to the user |
| `PostModelSwitch` | No | Shows stderr to user only; the model already switched |
| `Elicitation` | Yes | Declines the request, and no dialog appears |
| `ElicitationResult` | Yes | Blocks the response (action becomes decline) |
| `WorktreeCreate` | Yes | Any non-zero exit code causes worktree creation to fail |
| `WorktreeRemove` | Yes | Any non-zero exit code causes worktree removal to fail if the directory still exists afterward. See [WorktreeRemove](hooks-events.md#worktreeremove) for what happens to the directory |
| `InstructionsLoaded` | No | Exit code is ignored |
| `MessageDisplay` | No | The original text is displayed |

For `SessionStart`, `SubagentStart`, and `PostModelSwitch`, Claude Code renders the exit code 2 stderr in the transcript as a `<hook name> hook error` notice, the same way it renders a [non-blocking error](#exit-code-output). Claude doesn't see it, and the session or subagent proceeds. For `SubagentStart`, the notice appears in the subagent's own transcript, not in the parent conversation.

### HTTP response handling

HTTP hooks use HTTP status codes and response bodies instead of exit codes and stdout. To block the action when the request fails or returns a non-2xx status, set [`onFailure: "block"`](#block-the-action-when-a-hook-fails). To block a tool call or deny a permission, return a 2xx response with a JSON body containing the appropriate [decision fields](#decision-control).

After a [non-blocking error](#exit-code-output), the action goes ahead unless the hook is one [whose failure blocks the action](#block-the-action-when-a-hook-fails). Except on events with their own failure contract in the [per-event table](#exit-code-2-behavior-per-event), such as `WorktreeCreate`, you get these results for each response or failure:

* **2xx with an empty body**: success, equivalent to exit code 0 with no output
* **2xx with a JSON object body**: parsed using the same [JSON output](#json-output) schema as command hooks. A body that fails schema validation is a non-blocking error
* **2xx with any other body, such as plain text**: non-blocking error, handled the same as a non-2xx status. Claude Code doesn't add the text to Claude's context
* **Non-2xx status**: non-blocking error
* **Connection failure**: non-blocking error
* **Timeout**: the hook is canceled, as described under [Timeouts](#timeouts)

### JSON output

Exit codes only let you block or stay silent, but JSON output gives you finer-grained control. Instead of exiting with code 2 to block, exit 0 and print a JSON object to stdout. Claude Code reads specific fields from that JSON to control behavior, including [decision control](#decision-control) for blocking, allowing, or escalating to the user.

> [!NOTE]
>
> Choose one approach per hook: either use exit codes alone for signaling, or exit 0 and print JSON for structured control. If you mix them, exit 2 keeps its [blocking effect](#exit-code-2-behavior-per-event), and Claude Code still reads the JSON fields, with the one elicitation exception noted under [Exit code 2](#exit-code-2).

Print nothing but the JSON object to stdout. For a hook that isn't [async](#how-async-hooks-execute), other text there, such as a line your shell profile echoes at startup, keeps Claude Code from reading the object as JSON, and [Hook JSON has no effect](https://code.claude.com/docs/en/hooks-guide.md#hook-json-has-no-effect) shows how to find and silence that text.

A hook's `additionalContext`, `systemMessage`, and `initialUserMessage` strings, and its plain stdout, are capped at 10,000 characters:

* **Scope**: Claude Code measures each string on its own, even when several hooks run for the same event. For JSON output, each field is measured separately; plain stdout is measured whole.
* **Over the limit**: except for [PreCompact stdout](hooks-events.md#precompact-output), Claude Code saves the output to a file in the session directory. It replaces the output with the file path and a preview of up to the first 2,000 characters. A large valid Bash result is handled the same way, described under [Output limits](https://code.claude.com/docs/en/tools-reference.md#output-limits). Unlike that Bash ceiling, this cap has no setting or environment variable to raise it.
* **Reading the file**: Claude Code doesn't ask Claude to read the file, so keep anything Claude must always see within the cap.

The JSON object supports three kinds of fields:

* **Universal fields** like `continue` are listed in the table below. Every event accepts them, but some events discard them or deliver `systemMessage` somewhere other than the transcript. Each event's section says so. `terminalSequence` works on those events too, with the exceptions listed under [Emit terminal notifications](#emit-terminal-notifications).
* **Top-level `decision` and `reason`** are used by some events to block or provide feedback.
* **`hookSpecificOutput`** is a nested object for events that need richer control. It requires a `hookEventName` field set to the event name.

| Field | Default | Description |
| :- | :- | :- |
| `continue` | `true` | If `false`, Claude stops processing entirely after the hook runs. Takes precedence over any event-specific decision fields |
| `stopReason` | none | Message shown to the user when `continue` is `false`. It stays in the conversation, so Claude sees it if the conversation continues |
| `suppressOutput` | `false` | Has no effect: Claude Code accepts the field but doesn't act on it. A successful hook's stdout is never shown in the transcript and is recorded in the debug log |
| `systemMessage` | none | Warning message shown to the user. In [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) and [`--output-format stream-json`](https://code.claude.com/docs/en/headless) output, it can arrive as an [`SDKInformationalMessage`](https://code.claude.com/docs/en/agent-sdk/typescript#sdkinformationalmessage) |
| `terminalSequence` | none | A terminal escape sequence for Claude Code to emit on your behalf, such as a desktop notification, window title, or bell. Restricted to OSC `0`/`1`/`2`/`9`/`99`/`777` and BEL. If the value contains anything outside the allowlist, the field is ignored. Use this instead of writing to `/dev/tty`, which is unavailable to hooks |

To stop Claude entirely:

```json theme={null}
{ "continue": false, "stopReason": "Build failed, fix errors before continuing" }
```

For `PreToolUse` and `PostToolUse` hooks, the stop applies even when the tool call fails or completes while Claude is still streaming a response.

#### Emit terminal notifications

Hooks run without a controlling terminal, so writing escape sequences directly to `/dev/tty` fails. Instead, return the escape sequence in the `terminalSequence` field and Claude Code emits it for you through its own terminal write path. This is race-free, works inside tmux and GNU screen, and works on Windows where there is no `/dev/tty`.

The field accepts a string of one or more allowlisted escape sequences:

* OSC `0`, `1`, `2`: window and icon titles
* OSC `9`: iTerm2, ConEmu, Windows Terminal, and WezTerm notifications, including `9;4` taskbar progress
* OSC `99`: Kitty notifications
* OSC `777`: urxvt, Ghostty, and Warp notifications
* Bare BEL

Sequences may be terminated with BEL or with ST. Anything outside the allowlist, including CSI cursor and color sequences, OSC palette sequences, OSC 8 hyperlinks, OSC 52 clipboard writes, and OSC 1337, is rejected and the field is ignored.

Claude Code writes the sequence itself when it processes your hook's output, so the field works on events that discard `systemMessage` and `continue`, such as `Notification` and `StopFailure`. It has two limits:

* Claude Code writes the sequence only in an interactive session, and only while its interface is on screen. In non-interactive mode with the `-p` flag and in the Agent SDK, it ignores the field.
* A `WorktreeCreate` command hook can't return JSON, because Claude Code reads its stdout as the worktree path. An HTTP `WorktreeCreate` hook returns JSON and can include the field.

The example below fires a desktop notification from a `Notification` hook. The escape sequence is built with `printf` octal escapes so the control bytes never appear on the shell command line, and `jq -n --arg` builds the JSON output so quotes, backslashes, and newlines in the notification message are escaped correctly:

```bash theme={null}
#!/bin/bash
# Notification hook: ping the desktop when Claude Code needs attention.
input=$(cat)
title="Claude Code"
body=$(jq -r '.message // "Needs your attention"' <<<"$input")
seq=$(printf '\033]777;notify;%s;%s\007' "$title" "$body")
jq -nc --arg seq "$seq" '{terminalSequence: $seq}'
```

The `{ "terminalSequence": "..." }` shape is the same from any shell or language.

#### Add context for Claude

The `additionalContext` field passes a string from your hook into Claude's context window. Claude Code wraps the string in a [system reminder](https://code.claude.com/docs/en/glossary.md#system-reminder) and inserts it into the conversation at the point where the hook fired. Claude reads the reminder on the next model request, but it doesn't appear as a chat message in the interface.

Return `additionalContext` inside `hookSpecificOutput` alongside the event name:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "This file is generated. Edit src/schema.ts and run `bun generate` instead."
  }
}
```

Where the reminder appears depends on the event:

* [SessionStart](hooks-events.md#sessionstart) and [SubagentStart](hooks-events.md#subagentstart): at the start of the conversation, before the first prompt
* [UserPromptSubmit](hooks-events.md#userpromptsubmit) and [UserPromptExpansion](hooks-events.md#userpromptexpansion): alongside the submitted prompt
* [PreToolUse](hooks-events.md#pretooluse), [PostToolUse](hooks-events.md#posttooluse), [PostToolUseFailure](hooks-events.md#posttoolusefailure), and [PostToolBatch](hooks-events.md#posttoolbatch): next to the tool result
* [Stop](hooks-events.md#stop) and [SubagentStop](hooks-events.md#subagentstop): at the end of the turn. The conversation continues so Claude can act on the feedback. See [Stop decision control](hooks-events.md#stop-decision-control)
* [PostModelSwitch](hooks-events.md#postmodelswitch): with the next request after the switch. See [PostModelSwitch decision control](hooks-events.md#postmodelswitch-decision-control) for timing

When several hooks return `additionalContext` for the same event, Claude receives all of the values.

If your string contains a `<system-reminder>` or `</system-reminder>` tag, Claude receives the string with that tag's `<` replaced by `&lt;`.

If a value exceeds 10,000 characters, Claude Code writes the text to a file in the session directory and passes Claude the file path with a preview of up to the first 2,000 characters instead. Claude can read the file, but Claude Code doesn't ask it to.

Use `additionalContext` for information Claude should know about the current state of your environment or the operation that just ran:

* **Environment state**: the current branch, deployment target, or active feature flags
* **Conditional project rules**: which test command applies to the file just edited, which directories are read-only in this worktree
* **External data**: open issues assigned to you, recent CI results, content fetched from an internal service

For instructions that never change, prefer [CLAUDE.md](https://code.claude.com/docs/en/memory.md). It loads without running a script and is the standard place for static project conventions.

Write the text as factual statements rather than imperative system instructions. Phrasing such as "The deployment target is production" or "This repo uses `bun test`" reads as project information. Text framed as out-of-band system commands can trigger Claude's prompt-injection defenses, which causes Claude to surface the text to you instead of treating it as context.

Claude Code saves the injected text in the session transcript. For mid-session events like `PostToolUse` or `UserPromptSubmit`, when you resume with `--continue` or `--resume`, Claude Code replays the saved text rather than re-running the hook for past turns, so values like timestamps or commit SHAs become stale. `SessionStart` hooks run again on resume with `source` set to `"resume"`, or `"fork"` if you added `--fork-session`, so they can refresh their context.

#### Decision control

Not every event supports blocking or controlling behavior through JSON. The events that do each use a different set of fields to express that decision. Use this table as a quick reference before writing a hook:

| Events | Decision pattern | Key fields |
| :- | :- | :- |
| UserPromptSubmit, UserPromptExpansion, PostToolUse, PostToolUseFailure, PostToolBatch, Stop, SubagentStop, ConfigChange, PreCompact | Top-level `decision` | `decision: "block"`, `reason`. Stop and SubagentStop also accept `hookSpecificOutput.additionalContext` for [non-error feedback that continues the conversation](hooks-events.md#stop-decision-control) |
| TeammateIdle, TaskCompleted | Exit code or `continue: false` | Exit code 2 blocks the action with stderr feedback. JSON `{"continue": false, "stopReason": "..."}` also stops the teammate entirely, matching `Stop` hook behavior; [TaskCompleted ignores it when the `TaskUpdate` tool triggered the event](hooks-events.md#taskcompleted-decision-control) |
| TaskCreated | Exit code or top-level `decision` | Exit code 2 or `decision: "block"` [cancels the task](hooks-events.md#taskcreated-decision-control) and returns the message to Claude. `continue: false` is ignored |
| PreToolUse | `hookSpecificOutput` | `permissionDecision` (allow/deny/ask/defer), `permissionDecisionReason` |
| PreModelSwitch | `hookSpecificOutput` or top-level `decision` | `permissionDecision` (allow/deny/ask), `permissionDecisionReason`. `decision: "block"` also [cancels the switch](hooks-events.md#premodelswitch-decision-control) |
| PermissionRequest | `hookSpecificOutput` | `decision.behavior` (allow/deny) |
| PermissionDenied | `hookSpecificOutput` | `retry: true` tells the model it may retry the denied tool call; Claude Code ignores it for [no-verdict denials](hooks-events.md#permissiondenied-decision-control) |
| WorktreeCreate | path return | Command hook prints path on stdout; HTTP hook returns `hookSpecificOutput.worktreePath`. Hook failure or missing path fails creation |
| WorktreeRemove | Exit code | Any non-zero exit code makes the removal fail if the directory still exists afterward. JSON output is discarded |
| Elicitation, ElicitationResult | `hookSpecificOutput` or top-level `decision` | `action` (accept/decline/cancel), `content` (form field values). `decision: "block"` also [declines](hooks-events.md#other-ways-to-decline-an-elicitation) |
| MessageDisplay | `hookSpecificOutput` | `displayContent` replaces the displayed text on screen. Display-only: the transcript and what Claude sees keep the original |
| SessionStart, SubagentStart, PostModelSwitch | Context only | `hookSpecificOutput.additionalContext` adds context for Claude. SessionStart also accepts [`initialUserMessage`, `watchPaths`, `sessionTitle`, and `reloadSkills`](hooks-events.md#sessionstart-decision-control). No blocking or decision control |
| Setup, Notification, SessionEnd, PostCompact, InstructionsLoaded, StopFailure, CwdChanged, DirectoryAdded, FileChanged | None | No decision control. Used for side effects like logging or cleanup |

A few events can also rewrite content rather than only allow or block it:

* `PreToolUse`: `updatedInput` directly under `hookSpecificOutput` replaces a tool's arguments before it runs. See [PreToolUse decision control](hooks-events.md#pretooluse-decision-control)
* `PermissionRequest`: `updatedInput` inside the `decision` object. See [PermissionRequest decision control](hooks-events.md#permissionrequest-decision-control)
* `PostToolUse`: `updatedToolOutput` replaces the tool's result. See [PostToolUse decision control](hooks-events.md#posttooluse-decision-control)
* `UserPromptSubmit`: can't replace the prompt; it only injects `additionalContext` alongside it

For redaction or transformation use cases, intercept at `PreToolUse` for outbound tool inputs and `PostToolUse` for inbound tool results.

Here are examples of each pattern in action:

> [tab] Top-level decision
>
> The only value for `decision` is `"block"`. To allow the action to proceed, omit `decision` from your JSON, or exit 0 without any JSON at all:
>
> ```json theme={null}
> {
>   "decision": "block",
>   "reason": "Test suite must pass before proceeding"
> }
> ```

> [tab] PreToolUse
>
> Uses `hookSpecificOutput` for richer control: allow, deny, or escalate to the user. You can also modify tool input before it runs or inject additional context for Claude. See [PreToolUse decision control](hooks-events.md#pretooluse-decision-control) for the full set of options.
>
> ```json theme={null}
> {
>   "hookSpecificOutput": {
>     "hookEventName": "PreToolUse",
>     "permissionDecision": "deny",
>     "permissionDecisionReason": "Database writes are not allowed"
>   }
> }
> ```

> [tab] PermissionRequest
>
> Uses `hookSpecificOutput` to allow or deny a permission request on behalf of the user. When allowing, you can also modify the tool's input or apply permission rules so the user isn't prompted again. See [PermissionRequest decision control](hooks-events.md#permissionrequest-decision-control) for the full set of options.
>
> ```json theme={null}
> {
>   "hookSpecificOutput": {
>     "hookEventName": "PermissionRequest",
>     "decision": {
>       "behavior": "allow",
>       "updatedInput": {
>         "command": "npm run lint"
>       }
>     }
>   }
> }
> ```

For extended examples including Bash command validation, prompt filtering, and auto-approval scripts, see [What you can automate](https://code.claude.com/docs/en/hooks-guide.md#what-you-can-automate) in the guide and the [Bash command validator reference implementation](https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py).

## Hook events

Each event's input schema, matcher values and decision control are in [hooks-events.md](hooks-events.md), one section per event: [SessionStart](hooks-events.md#sessionstart), [Setup](hooks-events.md#setup), [InstructionsLoaded](hooks-events.md#instructionsloaded), [UserPromptSubmit](hooks-events.md#userpromptsubmit), [UserPromptExpansion](hooks-events.md#userpromptexpansion), [MessageDisplay](hooks-events.md#messagedisplay), [PreToolUse](hooks-events.md#pretooluse), [PermissionRequest](hooks-events.md#permissionrequest), [PostToolUse](hooks-events.md#posttooluse), [PostToolUseFailure](hooks-events.md#posttoolusefailure), [PostToolBatch](hooks-events.md#posttoolbatch), [PermissionDenied](hooks-events.md#permissiondenied), [Notification](hooks-events.md#notification), [SubagentStart](hooks-events.md#subagentstart), [SubagentStop](hooks-events.md#subagentstop), [TaskCreated](hooks-events.md#taskcreated), [TaskCompleted](hooks-events.md#taskcompleted), [Stop](hooks-events.md#stop), [StopFailure](hooks-events.md#stopfailure), [TeammateIdle](hooks-events.md#teammateidle), [ConfigChange](hooks-events.md#configchange), [CwdChanged](hooks-events.md#cwdchanged), [DirectoryAdded](hooks-events.md#directoryadded), [FileChanged](hooks-events.md#filechanged), [WorktreeCreate](hooks-events.md#worktreecreate), [WorktreeRemove](hooks-events.md#worktreeremove), [PreCompact](hooks-events.md#precompact), [PostCompact](hooks-events.md#postcompact), [PreModelSwitch](hooks-events.md#premodelswitch), [PostModelSwitch](hooks-events.md#postmodelswitch), [SessionEnd](hooks-events.md#sessionend), [Elicitation](hooks-events.md#elicitation), [ElicitationResult](hooks-events.md#elicitationresult).

## Prompt-based hooks

In addition to command, HTTP, and MCP tool hooks, Claude Code supports prompt-based hooks (`type: "prompt"`) that use an LLM to evaluate whether to allow or block an action, and agent hooks (`type: "agent"`) that spawn an agentic verifier with tool access. Not all events support every hook type.

Events that support all five hook types (`command`, `http`, `mcp_tool`, `prompt`, and `agent`):

* `PermissionDenied`
* `PostToolBatch`
* `PostToolUse`
* `PostToolUseFailure`
* `PreToolUse`
* `Stop`
* `SubagentStop`
* `TaskCompleted`
* `TaskCreated`
* `TeammateIdle`
* `UserPromptExpansion`
* `UserPromptSubmit`

`PermissionRequest` supports `command`, `http`, `mcp_tool`, and `prompt` hooks but not `agent` hooks. If you configure an agent hook on this event, Claude Code skips it and the permission flow proceeds unchanged. To allow or deny from a hook, return the [decision object](hooks-events.md#permissionrequest-decision-control) from a command or HTTP hook.

Events that support `command`, `http`, and `mcp_tool` hooks but not `prompt` or `agent`:

* `ConfigChange`
* `CwdChanged`
* `DirectoryAdded`
* `Elicitation`
* `ElicitationResult`
* `FileChanged`
* `InstructionsLoaded`
* `MessageDisplay`
* `Notification`
* `PostCompact`
* `PostModelSwitch`
* `PreCompact`
* `PreModelSwitch`
* `SessionEnd`
* `StopFailure`
* `SubagentStart`
* `WorktreeCreate`
* `WorktreeRemove`

`SessionStart` and `Setup` support `command` and `mcp_tool` hooks, and [MCP tool hook fields](#mcp-tool-hook-fields) describes when their `mcp_tool` hooks run. They don't support `http`, `prompt`, or `agent` hooks.

### How prompt-based hooks work

Instead of executing a Bash command, prompt-based hooks:

1. Send the hook input and your prompt to a Claude model, by default the one Claude Code uses for [background functionality](https://code.claude.com/docs/en/model-config.md#environment-variables)
2. The LLM responds with structured JSON containing a decision
3. Claude Code processes the decision automatically

### Prompt hook configuration

Set `type` to `"prompt"` and provide a `prompt` string instead of a `command`. Use the `$ARGUMENTS` placeholder to inject the hook's JSON input data into your prompt text.

In a prompt or [agent hook](#agent-based-hooks), you can write the `prompt` as a rule about what to block or allow, such as "Block any Bash command that reads `.env` files", or as a condition that must hold, such as "All unit tests pass".

For example, a `Stop` hook `{"type": "prompt", "prompt": "Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks are complete."}` asks the model whether all tasks are complete before Claude finishes.

| Field | Required | Description |
| :- | :- | :- |
| `type` | yes | Must be `"prompt"` |
| `prompt` | yes | The prompt text to send to the LLM. Use `$ARGUMENTS` as a placeholder for the hook input JSON. If `$ARGUMENTS` is not present, input JSON is appended to the prompt |
| `model` | no | Model to use for evaluation. Defaults to the model Claude Code uses for [background functionality](https://code.claude.com/docs/en/model-config.md#environment-variables) |
| `timeout` | no | Timeout in seconds. Default: 30 |
| `continueOnBlock` | no | On the events it applies to, `true` feeds an `ok: false` reason back to Claude and continues instead of ending the turn. Default: `false`. See [Response schema](#response-schema) for per-event behavior |

### Response schema

The LLM must respond with JSON containing:

```json theme={null}
{
  "ok": true | false,
  "reason": "Explanation for the decision",
  "impossible": true | false
}
```

| Field | Description |
| :- | :- |
| `ok` | `true` to allow. For `false`, see the per-event behavior below |
| `reason` | Required when `ok` is `false` |
| `impossible` | Optional. The model returns it with `ok: false` when it judges the condition can never be satisfied. On `Stop` and `SubagentStop`, Claude Code then lets the turn end instead of feeding the reason back. Agent hooks and other events ignore it |

What happens on `ok: false` depends on the event:

* `Stop` and `SubagentStop`: the reason is fed back to Claude as its next instruction and the turn continues, unless the response also sets `impossible: true`, in which case Claude Code allows the stop and the turn ends
* `PreToolUse`: the tool call is denied; by default the turn ends and the deny reason appears in the chat as a warning line. Set `continueOnBlock: true` to instead return the reason to Claude as the tool error so it can adjust and continue, equivalent to a command hook's `permissionDecision: "deny"`
* `PostToolUse`: by default the turn ends and the reason appears in the chat as a warning line. Set `continueOnBlock: true` to feed the reason back to Claude and continue the turn instead
* `PostToolBatch`, `UserPromptSubmit`, and `UserPromptExpansion`: the turn ends and the reason appears as a warning line. These events end the turn on `decision: "block"` regardless of `continue`
* `PostToolUseFailure` and `TaskCreated`: the reason is returned to Claude as a tool error and the turn continues, regardless of `continueOnBlock`
* `TaskCompleted`: when it fires because a task is marked completed during a turn, the reason is returned to Claude as a tool error and the turn continues, regardless of `continueOnBlock`. When it fires because a teammate stops, it behaves like `TeammateIdle` and halts the teammate by default
* `TeammateIdle`: by default the teammate stops and the reason appears as a warning line. Set `continueOnBlock: true` to feed the reason back to the teammate and keep it working instead
* `PermissionRequest`: `ok: false` has no effect. To deny an approval from a hook, use a [command hook](#command-hook-fields) returning `hookSpecificOutput.decision.behavior: "deny"`
* `PermissionDenied`: `ok: false` has no effect because the denial already happened. The only output this event reads is `hookSpecificOutput.retry`, which prompt and agent hooks can't set. They run on this event, but their output is discarded. Use a [command hook](#command-hook-fields) to return `retry`

If you need finer control on any event, use a [command hook](#command-hook-fields) with the per-event fields described in [Decision control](#decision-control).

### Check multiple conditions before stopping

> **Official example**: [Check multiple conditions before stopping](https://code.claude.com/docs/en/hooks#check-multiple-conditions-before-stopping) shows a `Stop` prompt hook that checks three conditions and asks the model to answer `{"ok": true}` or `{"ok": false, "reason": "..."}`. `SubagentStop` uses the same format, and on `ok: false` the reason becomes Claude's next instruction.

## Agent-based hooks

> [!WARNING]
>
> Agent hooks are experimental. Behavior and configuration may change in future releases. For production workflows, prefer [command hooks](#command-hook-fields).

Agent-based hooks (`type: "agent"`) are like prompt-based hooks but with multi-turn tool access. Instead of a single LLM call, an agent hook spawns a subagent that can read files, search code, and inspect the codebase to verify conditions. Agent hooks support the same events as [prompt-based hooks](#prompt-based-hooks), except `PermissionRequest`.

### How agent hooks work

When an agent hook fires:

1. Claude Code spawns a subagent with your prompt and the hook's JSON input
2. The subagent can use tools like Read, Grep, and Glob to investigate
3. After up to 50 turns, the subagent returns a structured `{ "ok": true/false }` decision
4. Claude Code allows the action if `ok` is `true`. If `ok` is `false`, Claude Code handles the block the same way as a prompt hook with `continueOnBlock: true` on that event, as listed under [Response schema](#response-schema)

Agent hooks are useful when verification requires inspecting actual files or test output, not just evaluating the hook input data alone.

### Agent hook configuration

Set `type` to `"agent"` and provide a `prompt` string, using `$ARGUMENTS` as a placeholder for the hook input JSON. The configuration fields are the same as [prompt hooks](#prompt-hook-configuration), except that agent hooks have a longer default timeout of 60 seconds and no `continueOnBlock` field.

The response schema is `{ "ok": true }` to allow or `{ "ok": false, "reason": "..." }` to block. On `ok: false`, Claude Code handles an agent hook the way it handles a [prompt hook with `continueOnBlock: true`](#response-schema) on the same event; agent hooks have no `continueOnBlock` field, and don't support the prompt-hook `impossible` field.

For example, a `Stop` hook `{"type": "agent", "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS", "timeout": 120}` lets Claude finish only when the tests pass.

## Run hooks in the background

By default, hooks block Claude's execution until they complete. For long-running tasks like deployments, test suites, or external API calls, set `"async": true` to run the hook in the background while Claude continues working. Async hooks can't block or control Claude's behavior: response fields like `decision`, `permissionDecision`, and `continue` have no effect, because the action they would have controlled has already completed.

### Configure an async hook

Add `"async": true` to a command hook's configuration to run it in the background without blocking Claude. This field is only available on `type: "command"` hooks.

For example, `{"type": "command", "command": "/path/to/run-tests.sh", "async": true}` under a `PostToolUse` matcher on `Write` lets Claude keep working while the script runs; its output is delivered on the next conversation turn.

Once an async hook is running in the background, Claude Code doesn't enforce `timeout` on it. Claude Code still enforces `timeout` on a hook you run with `asyncRewake`.

Claude Code delivers an async hook's results only while the session runs:

* In [non-interactive mode](https://code.claude.com/docs/en/headless.md) with the `-p` flag, Claude Code kills any async hook still running at teardown and finalizes it with outcome `cancelled`
* If your hook's work must outlive a `claude -p` session, start a fully detached process from it

### How async hooks execute

When an async hook fires, Claude Code starts the hook process and immediately continues without waiting for it to finish. The hook receives the same JSON input via stdin as a synchronous hook.

After the background process exits, Claude Code delivers the `additionalContext` and `systemMessage` fields from the hook's JSON response to Claude on the next conversation turn, except for [repeated `SessionStart` output](#limitations). Unlike a synchronous hook's `systemMessage`, neither field is shown to you.

Print the JSON response alone on stdout or on one line of its own:

* **Alone on stdout**: when the response is the only text on stdout, it can span several lines, such as pretty-printed `jq` output. Spanning several lines requires Claude Code v2.1.295 or later.
* **On one line of its own**: an async hook can print other text to stdout when the response fits on one line by itself, for example with `jq -c`.

Claude Code validates that JSON response against the same [output schema](#json-output) as synchronous hooks, and drops any field whose value has the wrong type, such as a `systemMessage` that isn't a string, instead of delivering it. Run with `--debug` to see a warning naming each dropped field.

Async hook completion notifications are suppressed by default. To see them, enable verbose mode with `Ctrl+O` or start Claude Code with `--verbose`.

### Run tests after file changes

> **Official example**: [Run tests after file changes](https://code.claude.com/docs/en/hooks#run-tests-after-file-changes) runs `npm test` from an `async: true` `PostToolUse` hook on `Write|Edit`, only for `.ts` and `.js` files, and reports the result to Claude on the next turn.

**Key facts:** the script prints its result as one line with `jq -nc --arg msg "$MSG" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $msg}}'`, so the JSON sits on one line of its own as an async hook needs.

### Limitations

Async hooks have additional constraints compared to synchronous hooks:

* Hook output is delivered on the next conversation turn. If the session is idle, the response waits until the next user interaction. Exception: an `asyncRewake` hook that exits with code 2 wakes Claude immediately even when the session is idle.
* Each execution creates a separate background process.
* An async `SessionStart` hook runs every time the event fires. Claude Code skips the hook's output when the `additionalContext` and `systemMessage` text matches what Claude last received from that hook, unless a synchronous `SessionStart` hook has added other text since. Claude Code delivers the text when it changes, and again the next time the hook runs after a compaction or `/clear`. Before v2.1.295, Claude Code added the same text to the conversation again on every resume.

## Security considerations

### Disclaimer

> [!WARNING]
>
> Command hooks execute shell commands with your full user permissions. They can modify, delete, or access any files your user account can access. Review and test all hook commands before adding them to your configuration.

### Workspace trust

Claude Code checks workspace trust before it runs any hook from a settings file. What counts as trusted depends on the session type:

* **Interactive session**: Claude Code holds back hooks from every settings file, including your own `~/.claude/settings.json`, until you accept the [workspace trust dialog](https://code.claude.com/docs/en/permissions.md#project-allow-rules-and-workspace-trust) for the folder, or for a parent directory whose trust extends to it
* **`-p` or SDK session**: Claude Code never shows the dialog and treats the folder as trusted, so hooks committed in a repository's `.claude/settings.json` run in a folder you've never trusted

Before you script `claude -p` over a repository you didn't write, review its `.claude/` settings files, start with [`--bare`](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode), or [turn hooks off for that run](#disable-or-remove-hooks) with `--settings '{"disableAllHooks": true}'`. Frontmatter hooks in a project subagent follow a stricter rule than settings-file hooks. [What runs before you trust a folder](https://code.claude.com/docs/en/permissions.md#what-runs-before-you-trust-a-folder) lists each kind of repository content by session type.

### Security best practices

Keep these practices in mind when writing hooks:

* **Validate and sanitize inputs**: never trust input data blindly
* **Always quote shell variables**: use `"$VAR"` not `$VAR`
* **Block path traversal**: check for `..` in file paths
* **Use absolute paths**: specify full paths for scripts. In exec form, use `${CLAUDE_PROJECT_DIR}` and the path needs no quoting. In shell form, wrap it in double quotes
* **Skip sensitive files**: avoid `.env`, `.git/`, keys, etc.

## Windows PowerShell tool

On Windows, you can run individual hooks in PowerShell by setting `"shell": "powershell"` on a command hook. Claude Code auto-detects `pwsh.exe`, the PowerShell 7 and later executable, and falls back to `powershell.exe` for Windows PowerShell 5.1.

For example, `{"type": "command", "shell": "powershell", "command": "Write-Host 'File written'"}`.

### Reference scripts by path in PowerShell hooks

To reference the project root from a PowerShell shell-form command, write `${CLAUDE_PROJECT_DIR}` or `$env:CLAUDE_PROJECT_DIR`. Claude Code rewrites the `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, and `${CLAUDE_PLUGIN_DATA}` placeholders in a PowerShell shell-form command to PowerShell's `${env:NAME}` form, whether the hook is defined in `settings.json`, a plugin, or a skill. PowerShell then resolves the value from the exported environment after parsing, so the placeholder works inside double-quoted strings but not inside single-quoted strings, where PowerShell never expands variables.

Don't write the bare `$CLAUDE_PROJECT_DIR` spelling in a PowerShell hook. PowerShell parses it as an undefined local variable and resolves it to `$null`, which leaves the script path without its project-root prefix. Claude Code doesn't rewrite that form; it logs a warning in the [debug log](#debug-hooks) instead.

The example below shows a `settings.json` hook that runs a project script with the `$env:` form:

```json theme={null}
{
  "type": "command",
  "shell": "powershell",
  "command": "& \"$env:CLAUDE_PROJECT_DIR\\.claude\\hooks\\check.ps1\""
}
```

## Debug hooks

Hook execution details are written to the debug log file. Start Claude Code with `claude --debug-file <path>` to write the log to a known location, or run `claude --debug` and read the log at `~/.claude/debug/<session-id>.txt`. The `--debug` flag doesn't print to the terminal.

For example, a `PostToolUse` hook on `Write` whose command prints `hook-ran` produces entries like:

```text theme={null}
2026-07-19T02:03:24.382Z [DEBUG] Hook output does not start with {, treating as plain text
2026-07-19T02:03:24.382Z [DEBUG] "Hook PostToolUse:Write (PostToolUse) success:\nhook-ran"
```

To find a slow hook, search the log for `Hooks:` lines that end in a duration. In Claude Code v2.1.296 or later, each command hook on a tool event, `UserPromptSubmit`, `SessionStart`, `Stop`, and several other events leaves one when it finishes, whatever it printed. The line gives the event name, joined by a colon to the tool name or other value the hook matched on, then the hook's command in brackets, the plugin it came from if any, how the run ended, and how long it took, as in `Hooks: PostToolUse:Write [.claude/hooks/log-write.sh] finished with status 0 (31ms)`. A run can also end as `timed out after <N>ms`, `cancelled`, `moved to the background`, or `failed to start`. On some events, such as `Notification`, `SessionEnd`, and `PreCompact`, a command hook leaves a `completed with status` line without a duration instead.

For more granular hook matching details, set `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose` to see additional log lines such as hook matcher counts and query matching.

For troubleshooting common issues like hooks not firing, Stop hooks that keep blocking, or configuration errors, see [Limitations and troubleshooting](https://code.claude.com/docs/en/hooks-guide.md#limitations-and-troubleshooting) in the guide. For a broader diagnostic walkthrough covering `/context`, `/doctor`, and settings precedence, see [Debug your config](https://code.claude.com/docs/en/debug-your-config.md).

## Documentation References

- Source page: https://code.claude.com/docs/en/hooks
- [Hooks reference](https://code.claude.com/docs/en/hooks): the official examples and walkthroughs this file points to instead of copying them, such as How a hook resolves, Check multiple conditions before stopping and Run tests after file changes.
- [Claude Code changelog](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md): the release notes from 2.1.299 to 2.1.319 behind the items marked *not yet on this page*; also published at https://code.claude.com/docs/en/changelog.
- [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide): the hooks quickstart, What you can automate, Hook not firing, Hook JSON has no effect, and Limitations and troubleshooting. Local copy: [hooks-guide.md](hooks-guide.md).
- [Desktop app](https://code.claude.com/docs/en/desktop-quickstart): one of the places where hooks fire.
- [Cloud sessions](https://code.claude.com/docs/en/claude-code-on-the-web): cloud sessions, where hooks also fire.
- [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview): what a mod is.
- [React to events](https://code.claude.com/docs/en/plugins/mods/events): hooks written as JavaScript functions in a mod.
- [Tools reference](https://code.claude.com/docs/en/tools-reference): `EndConversation`, the Monitor tool and its WebSocket watch, and output limits.
- [Agent teams](https://code.claude.com/docs/en/agent-teams): agent teams and in-process teammates.
- [Permissions](https://code.claude.com/docs/en/permissions): the permission flow, the permission rule syntax that `if` uses, permission modes, the workspace trust dialog and what runs before you trust a folder.
- [Plugins overview](https://code.claude.com/docs/en/plugins/overview): plugins.
- [Skills](https://code.claude.com/docs/en/skills): skills, bundled skills, and frontmatter that didn't parse.
- [Subagents](https://code.claude.com/docs/en/sub-agents): subagents, and which scopes are exempt.
- [Self-hosted environments configuration](https://code.claude.com/docs/en/self-hosted-environments-configuration): settings in a self-hosted environment.
- [Managed settings](https://code.claude.com/docs/en/managed-settings): managed settings, their directory, and the managed sources Claude Code applies.
- [Cloud environments](https://code.claude.com/docs/en/cloud-environments): what carries over from your setup into a cloud session.
- [Settings](https://code.claude.com/docs/en/settings): settings files, settings precedence, and the `Setting sources` line.
- [Settings reference](https://code.claude.com/docs/en/settings-reference): `allowManagedHooksOnly` and what runs under it, HTTP hook allowlists, `strictPluginOnlyCustomization` and `fileSuggestion`.
- [Status line](https://code.claude.com/docs/en/statusline): `statusLine` and `subagentStatusLine`.
- [MCP](https://code.claude.com/docs/en/mcp): MCP servers, plugin-provided MCP servers, the `cached` status, authenticating a server from `/mcp`, and stdio servers.
- [Worktrees](https://code.claude.com/docs/en/worktrees): worktrees and what they share with the main checkout.
- [Environment variables](https://code.claude.com/docs/en/env-vars): `MCP_TIMEOUT`, `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`, `CLAUDE_CODE_GIT_BASH_PATH` and `$CLAUDE_CODE_BRIDGE_SESSION_ID`.
- [Remote Control](https://code.claude.com/docs/en/remote-control): Remote Control sessions.
- [Glossary](https://code.claude.com/docs/en/glossary): system reminder and other terms.
- [Plugins manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference): `${user_config.*}` and the plugin environment variables.
- [Errors](https://code.claude.com/docs/en/errors): the error a shell-form plugin hook that references `${user_config.*}` fails with.
- [Model configuration](https://code.claude.com/docs/en/model-config): the effort level, the model used for background functionality, and when a changed setting starts.
- [Plugins components reference](https://code.claude.com/docs/en/plugins/components): the plugin components, including hooks and the persistent data directory.
- [Create plugins](https://code.claude.com/docs/en/plugins/create): creating a plugin.
- [Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace): listing a plugin in a marketplace.
- [Plugins troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting): the `is blocked by enterprise policy` message for a marketplace.
- [Commands](https://code.claude.com/docs/en/commands): `/debug`.
- [Monitoring usage](https://code.claude.com/docs/en/monitoring-usage): the `prompt.id` attribute on OpenTelemetry events, and the `OTEL_*` variables Claude Code removes from every subprocess it spawns.
- [The .claude directory](https://code.claude.com/docs/en/claude-directory): the scratchpad directory.
- [HIPAA setup](https://code.claude.com/docs/en/hipaa-setup): sessions that get the HIPAA configuration, and the Anthropic credentials Claude Code removes there.
- [Agent SDK hooks](https://code.claude.com/docs/en/agent-sdk/hooks): Agent SDK callback hooks, and blocking the action when a callback fails.
- [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview): the Agent SDK.
- [Headless mode](https://code.claude.com/docs/en/headless): non-interactive mode, `--output-format stream-json` and `--bare`.
- [Agent SDK TypeScript reference](https://code.claude.com/docs/en/agent-sdk/typescript): `SDKInformationalMessage`.
- [Memory](https://code.claude.com/docs/en/memory): CLAUDE.md.
- [Debug your config](https://code.claude.com/docs/en/debug-your-config): a diagnostic walkthrough with `/context`, `/doctor` and settings precedence.
- [Bash command validator example](https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py): a complete reference implementation of a hook.
