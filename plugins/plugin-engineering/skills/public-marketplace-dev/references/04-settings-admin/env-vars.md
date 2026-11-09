# Environment variables

> Reference for the environment variables that control Claude Code behavior: how to set them, which value applies when a behavior is set more than one way, and the variables relevant to building and distributing plugins.

## Contents

- [Set environment variables](#set-environment-variables)
  - [Set variables in the shell](#set-variables-in-the-shell)
  - [Set variables in settings files](#set-variables-in-settings-files)
- [Precedence](#precedence)
- [Variables](#variables)
- [Documentation References](#documentation-references)

Environment variables control Claude Code behavior such as model selection, authentication, request routing, and feature toggles. Many of the same behaviors can also be configured through a [settings file](https://code.claude.com/docs/en/settings.md) field, a [CLI flag](https://code.claude.com/docs/en/cli-reference.md), or an in-session command like `/model`.

This file covers how to:

* [Set environment variables](#set-environment-variables) in the shell or in a settings file
* [Check which value applies](#precedence) when a behavior can be set more than one way
* [Look up the variables Claude Code reads](#variables)

## Set environment variables

A variable set in the shell lasts for that terminal session; a variable in a settings file applies every time `claude` runs.

### Set variables in the shell

Set the variable before launching `claude`:

> [tab] macOS, Linux, WSL
>
> ```bash theme={null}
> export API_TIMEOUT_MS="1200000"
> claude
> ```
>
> To set it for every session, add the `export` line to `~/.bashrc`, `~/.zshrc`, or the shell's profile file.

> [tab] Windows PowerShell
>
> ```powershell theme={null}
> $env:API_TIMEOUT_MS = "1200000"
> claude
> ```
>
> To set it for every session, run `[Environment]::SetEnvironmentVariable("API_TIMEOUT_MS", "1200000", "User")` and open a new terminal.

> [tab] Windows CMD
>
> ```batch theme={null}
> set API_TIMEOUT_MS=1200000
> claude
> ```
>
> To set it for every session, run `setx API_TIMEOUT_MS "1200000"` and open a new terminal.

The assignment line prints nothing on success. To confirm the variable is set, print it in the same shell:

> [tab] macOS, Linux, WSL
>
> ```bash theme={null}
> echo $API_TIMEOUT_MS
> ```

> [tab] Windows PowerShell
>
> ```powershell theme={null}
> echo $env:API_TIMEOUT_MS
> ```

> [tab] Windows CMD
>
> ```batch theme={null}
> echo %API_TIMEOUT_MS%
> ```

### Set variables in settings files

Add variables under the `env` key in a `settings.json` file, creating the file if it doesn't exist. Claude Code reads them directly from the file, so they take effect no matter how `claude` was launched.

* **New and changed values**: a running session applies them to its environment when the file is saved. A feature that reads its variables once at startup, such as [OpenTelemetry monitoring](https://code.claude.com/docs/en/monitoring-usage.md), keeps its startup values until relaunch.
* **Removed values**: removing a variable from the file doesn't unset it in a running session; the removal takes effect the next time `claude` launches.

```json ~/.claude/settings.json theme={null}
{
  "env": {
    "API_TIMEOUT_MS": "1200000",
    "BASH_DEFAULT_TIMEOUT_MS": "300000"
  }
}
```

Claude Code copies these values into its environment as written. No shell processes them, so shorthand such as `~` or `$HOME` stays as typed. For a variable that takes a path, such as `CLAUDE_CONFIG_DIR`, write the absolute path: `"CLAUDE_CONFIG_DIR": "/home/you/.claude-work"`.

The file chosen controls who the variables apply to:

| File | Applies to |
| :- | :- |
| `~/.claude/settings.json` | You, in every project |
| `.claude/settings.json` | Everyone working in the project, checked into source control |
| `.claude/settings.local.json` | You, in this project only, gitignored when Claude Code saves a setting to it; add it to your gitignore if you create it by hand |

See [Settings files](https://code.claude.com/docs/en/settings.md#where-settings-live) for where each file lives and [Settings precedence](https://code.claude.com/docs/en/settings.md#settings-precedence) for how they combine when more than one sets the same variable.

## Precedence

When the same variable is set in both the shell and a settings file `env` block, the settings file value applies in most sessions: Claude Code writes each `env` entry into the process environment, replacing the value inherited from the shell. [How `env` values interact with your shell](https://code.claude.com/docs/en/settings-reference#how-env-values-interact-with-your-shell) covers the sessions that keep the inherited value instead, and the [`env` setting](https://code.claude.com/docs/en/settings-reference#when-claude-code-applies-env-values) states when Claude Code applies them. A few variables are special-cased; the [`env` setting](https://code.claude.com/docs/en/settings-reference#env) lists the exceptions.

Claude Code reads shell environment variables at startup, so changes to them take effect the next time `claude` launches. Variables set under the `env` key in settings files are reapplied to a running session when the file changes, with the startup-only exception described in [Set variables in settings files](#set-variables-in-settings-files).

## Variables

Numeric variables such as timeouts, token budgets, and retry counts accept scientific notation and digit-separator spellings in addition to plain digits, except where a variable's row notes it takes plain digits only. For example, Claude Code reads `2e3` as 2000 and `64_000` as 64000. Before v2.1.211, these spellings could silently set a much smaller value, such as `1e6` setting a timeout to 1.

> **Note:** For variables that turn a behavior on or off, set `1`, `true`, `yes`, or `on` to turn it on and `0`, `false`, `no`, or `off` to turn it off, in any casing. Each variable's row also states its own rule.

| Variable | Purpose |
| :- | :- |
| `CLAUDECODE` | Set to `1` in subprocesses Claude Code spawns (Bash and PowerShell tools, tmux sessions, [hook](https://code.claude.com/docs/en/hooks.md) commands, [status line](https://code.claude.com/docs/en/statusline.md) commands, stdio [MCP server](https://code.claude.com/docs/en/mcp.md) subprocesses). IDE extensions also set this in their integrated terminals. Use to detect when a script is running inside a subprocess spawned by Claude Code. To check whether the current process was spawned directly by a tool call or hook, rather than inside a stdio MCP server that Claude Code started, use `CLAUDE_CODE_CHILD_SESSION` instead |
| `CLAUDE_CODE_CHILD_SESSION` | Set to `1` in subprocesses Claude Code spawns via the Bash, PowerShell, and Monitor tools, [hook](https://code.claude.com/docs/en/hooks.md) commands, and [status line](https://code.claude.com/docs/en/statusline.md) commands. Not set for stdio [MCP server](https://code.claude.com/docs/en/mcp.md) subprocesses, which are long-lived and outlive the session that spawned them. Unlike `CLAUDECODE`, this is only set by Claude Code itself when it launches a subprocess and not by IDE extensions, so it reliably distinguishes a nested session from a top-level `claude` launched in an IDE-integrated terminal. A nested interactive `claude` TUI started this way is automatically excluded from `--resume`, `--continue`, up-arrow history, and the `claude agents` list. Non-interactive `claude -p` sessions still persist. Set `CLAUDE_CODE_FORCE_SESSION_PERSISTENCE=1` to override this exclusion. Requires Claude Code v2.1.172 or later |
| `CLAUDE_CODE_DEBUG_LOGS_DIR` | Override the debug log file path. Despite the name, this is a file path, not a directory. Requires debug mode to be enabled separately via `--debug`, `/debug`, or the `DEBUG` environment variable: setting this variable alone does not enable logging. The [`--debug-file`](https://code.claude.com/docs/en/cli-reference#cli-flags) flag does both at once. Defaults to `~/.claude/debug/<session-id>.txt` |
| `CLAUDE_CODE_DEBUG_LOG_LEVEL` | Minimum log level written to the debug log file. Values: `verbose`, `debug` (default), `info`, `warn`, `error`. Set to `verbose` to include high-volume diagnostics like full status line command output, or raise to `error` to reduce noise |
| `CLAUDE_CODE_ENABLE_BACKGROUND_PLUGIN_REFRESH` | Set to `1` to refresh plugin state at turn boundaries in [non-interactive mode](https://code.claude.com/docs/en/headless.md) after a background install completes. Off by default because the refresh changes the system prompt mid-session, which invalidates [prompt caching](https://code.claude.com/docs/en/prompt-caching.md) for that turn |
| `CLAUDE_CODE_FORCE_TERMINAL_IMAGES` | Set to `1` to draw [mod `Image` elements](https://code.claude.com/docs/en/plugins/mods/reference#elements) as pictures when your terminal draws kitty graphics protocol images with Unicode placeholders and you still see an `Image`'s dimmed `alt` text. See [which terminals draw an `Image` and where not to set this variable](https://code.claude.com/docs/en/plugins/mods/gallery#image-and-client) |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | How many [subagents](https://code.claude.com/docs/en/sub-agents.md#concurrent-subagent-limit) can be running in one session before the Agent tool refuses to spawn another (default: 20). Accepts a positive whole number in plain digits; anything else is ignored, so the variable can adjust the cap but can't disable it. Requires Claude Code v2.1.217 or later |
| `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` | Maximum length in characters of MCP tool descriptions and MCP server instructions that Claude Code sends to the model. The value you set replaces both [default limits](https://code.claude.com/docs/en/mcp.md#for-mcp-server-authors): 4096, and 16384 for the description of a tool that Claude loads through tool search. Accepts a positive whole number in plain digits. Anything else is ignored and the defaults apply. Requires Claude Code v2.1.280 or later |
| `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` | Number of [subagent layers](https://code.claude.com/docs/en/sub-agents.md#let-subagents-spawn-their-own-subagents) allowed below the main conversation (default: 3). At the default, subagents can spawn their own subagents, and a subagent at the third layer can't spawn further; set `1` to turn nesting off. In v2.1.217 through v2.1.218, the default was 1, so a subagent couldn't spawn its own unless you raised the limit; v2.1.219 raised the default to 3. Accepts a positive whole number in plain digits; anything else is ignored, so the limit can be adjusted but not removed. Requires Claude Code v2.1.217 or later |
| `CLAUDE_CODE_MCP_ALLOWLIST_ENV` | Set to `1` to spawn stdio MCP servers with only a safe baseline environment plus the server's configured `env`, instead of inheriting your shell environment |
| `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` | Idle timeout in milliseconds for MCP tool calls. When a stdio, HTTP, SSE, WebSocket, or [claude.ai connector](https://code.claude.com/docs/en/mcp.md#use-mcp-servers-from-claude-ai) MCP server sends no response and no progress notification for this long, the tool call aborts with an error instead of waiting for the overall `MCP_TOOL_TIMEOUT`. Overrides the per-transport defaults of 300000 (5 minutes) for network servers and 1800000 (30 minutes) for stdio servers. Set to `0` to disable the idle check. Values below 1000 are raised to one second, and the value is capped at the effective `MCP_TOOL_TIMEOUT`. A per-server `timeout` in `.mcp.json` of at least 1000 raises that server's idle window to at least the `timeout` value. Doesn't apply to IDE servers or SDK in-process servers. Requires Claude Code v2.1.187 or later. Before v2.1.203, stdio servers were exempt from the idle timeout |
| `CLAUDE_CODE_PLUGIN_CACHE_DIR` | Override the plugins root directory. Despite the name, this sets the parent directory, not the cache itself: marketplaces and the plugin cache live in subdirectories under this path. Defaults to `~/.claude/plugins` |
| `CLAUDE_CODE_PLUGIN_DIRS` | Plugin directories to load for the session, each loaded the way a [`--plugin-dir`](https://code.claude.com/docs/en/plugins/cli-reference#flags-that-load-a-plugin-for-one-session) flag loads it. Separate multiple paths with `:` on Unix or `;` on Windows. Give each path as an absolute path or start it with `~`, because Claude Code skips relative paths. Requires Claude Code v2.1.280 or later. See [Load a plugin for one session](https://code.claude.com/docs/en/plugins/create.md#load-a-directory-or-archive-for-one-session) |
| `CLAUDE_CODE_PLUGIN_DIR_WATCH` | Controls whether Claude Code reloads a [mod](https://code.claude.com/docs/en/plugins/mods/overview.md) when the mod's files change. Reloading applies to a mod you load from a directory with `--plugin-dir`, and it's on by default in interactive sessions. Set to `1` to turn it on in non-interactive sessions as well, or `0` to turn it off in every session. Requires Claude Code v2.1.287 or later. See [mod settings and environment variables](https://code.claude.com/docs/en/plugins/mods/reference.md#settings-and-environment-variables) |
| `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` | Timeout in milliseconds for cloning or refreshing a plugin marketplace (default: 120000). Increase this value for large repositories or slow network connections. See [Git clone timed out](https://code.claude.com/docs/en/plugins/troubleshooting.md#git-clone-timed-out-after-120s) |
| `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` | Set to `1` to clone GitHub `owner/repo` shorthand sources over HTTPS instead of SSH. Applies to plugin install and update, and to `/plugin marketplace add` and `update`. Useful in CI runners, containers, or any environment without a configured SSH key for `github.com` |
| `CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY` | Set to `1` to stop Claude Code from passing `-ExecutionPolicy Bypass` when spawning PowerShell for tool calls, hooks, and status line commands, and respect the machine's effective execution policy instead. By default Claude Code bypasses execution policy at process scope so `.ps1` scripts and module imports work on default-Restricted Windows installs. Process-scope bypass never overrides Group Policy `MachinePolicy` or `UserPolicy` regardless of this setting |
| `CLAUDE_CODE_REMOTE` | Set automatically to `true` when Claude Code is running as a [cloud session](https://code.claude.com/docs/en/claude-code-on-the-web.md). Read this from a hook or setup script to detect whether you are in a cloud session |
| `CLAUDE_CODE_SAFE_MODE` | Set to `1` to start in safe mode: CLAUDE.md, skills, plugins, hooks, MCP servers, custom commands and agents, output styles, workflows, custom themes, custom keybindings, status line and file-suggestion commands, LSP servers, and auto memory do not load, for troubleshooting a broken configuration. Managed settings policy still applies, including policy-configured hooks, status line, and file-suggestion commands; managed plugins, managed skills, managed CLAUDE.md, and policy-configured MCP servers do not. Equivalent to passing [`--safe-mode`](https://code.claude.com/docs/en/cli-reference#cli-flags). Directly spawned child processes inherit the variable |
| `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` | Override the time budget in milliseconds for [SessionEnd](https://code.claude.com/docs/en/hooks.md#sessionend) hooks. The value is also the timeout for each hook that sets no `timeout` of its own. Applies to session exit, `/clear`, and switching sessions via interactive `/resume`. By default the budget is 1.5 seconds, automatically raised to the highest per-hook `timeout` configured in settings files, up to 60 seconds. Timeouts on plugin-provided hooks do not raise the budget |
| `CLAUDE_CODE_SESSION_ID` | Set automatically to the current session ID in Bash and PowerShell tool subprocesses, [hook command](https://code.claude.com/docs/en/hooks.md) subprocesses, and stdio [MCP server](https://code.claude.com/docs/en/mcp.md) subprocesses. For Bash, PowerShell, and hooks this matches the `session_id` field in the hook JSON input and is updated on `/clear`. An MCP server subprocess retains the ID it was spawned with. On `--resume <session-id>` it receives the resumed ID, matching hooks and Bash. On `--continue` or `--resume` without an explicit ID it may receive the initial startup ID instead. Use to correlate scripts and external tools with the Claude Code session that launched them |
| `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` | Maximum number of consecutive times a [Stop](https://code.claude.com/docs/en/hooks.md#stop) or [SubagentStop](https://code.claude.com/docs/en/hooks.md#subagentstop) hook may block the turn from ending before Claude Code overrides it and ends the turn anyway (default: 8). Set to `0` to disable the cap. Raise this if your hook legitimately needs more iterations to resolve |
| `CLAUDE_CODE_SYNC_PLUGIN_INSTALL` | Set to `1` in non-interactive mode (the `-p` flag) to wait for plugin installation to complete before the first query. Without this, plugins install in the background and may not be available on the first turn. Combine with `CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS` to bound the wait |
| `CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS` | Timeout in milliseconds for synchronous plugin installation. When exceeded, Claude Code proceeds without plugins and logs an error. No default: without this variable, synchronous installation waits until complete |
| `CLAUDE_CONFIG_DIR` | Override the configuration directory (default: `~/.claude`). All settings, session history, and plugins are stored under this path. For credentials, see [where Claude Code stores credentials](https://code.claude.com/docs/en/authentication.md#credential-management). Useful for running multiple accounts side by side: for example, `alias claude-work='CLAUDE_CONFIG_DIR=~/.claude-work claude'`. Set it in your shell, user settings, or managed settings. In a settings file, write the [absolute path](#set-variables-in-settings-files). Ignored in [project and local settings](https://code.claude.com/docs/en/settings-reference.md#variables-claude-code-ignores-in-env) |
| `CLAUDE_ENV_FILE` | Path to a shell script whose contents Claude Code runs before each Bash command in the same shell process, so exports in the file are visible to the command. Use to persist virtualenv or conda activation across commands. PowerShell commands receive its variables too, in v2.1.296 or later, under the conditions in [Persisted variables in PowerShell commands](https://code.claude.com/docs/en/hooks.md#persisted-variables-in-powershell-commands). Also populated dynamically by [SessionStart](https://code.claude.com/docs/en/hooks.md#persist-environment-variables), [Setup](https://code.claude.com/docs/en/hooks.md#setup), [CwdChanged](https://code.claude.com/docs/en/hooks.md#cwdchanged), and [FileChanged](https://code.claude.com/docs/en/hooks.md#filechanged) hooks |
| `DEBUG` | Set to `1` to enable debug mode, equivalent to launching with [`--debug`](https://code.claude.com/docs/en/cli-reference#cli-flags). Debug logs are written to `~/.claude/debug/<session-id>.txt`, or to the path set by `CLAUDE_CODE_DEBUG_LOGS_DIR`. Only the truthy values `1`, `true`, `yes`, and `on` enable debug mode, so namespace patterns like `DEBUG=express:*` set for other tools do not trigger it |
| `FORCE_AUTOUPDATE_PLUGINS` | Set to `1` to force plugin auto-updates even when the main auto-updater is disabled via `DISABLE_AUTOUPDATER` |
| `MAX_MCP_OUTPUT_TOKENS` | Maximum number of tokens allowed in MCP tool responses (default: 25000). Claude Code displays a warning when output exceeds 10,000 tokens. Tools that declare [`anthropic/maxResultSizeChars`](https://code.claude.com/docs/en/mcp#raise-the-limit-for-a-specific-tool) use that character limit for text content instead, but image content from those tools is still subject to this variable. A successful text result longer than 50,000 characters from a tool without that annotation is [saved to a file](https://code.claude.com/docs/en/mcp.md#mcp-output-limits-and-warnings) regardless of this variable |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | Override the character budget for skill metadata shown to the [Skill tool](https://code.claude.com/docs/en/skills.md#control-who-invokes-a-skill). The budget scales dynamically at 1% of the context window, with a fallback of 8,000 characters. Legacy name kept for backwards compatibility |

## Documentation References

- Source page: https://code.claude.com/docs/en/env-vars (every environment variable Claude Code reads, how to set them, and precedence)
- https://code.claude.com/docs/en/settings.md (all `settings.json` configuration, including the `env` key, where settings files live, and settings precedence)
- https://code.claude.com/docs/en/cli-reference.md (launch-time CLI flags, including `--debug`, `--debug-file`, and `--safe-mode`)
- https://code.claude.com/docs/en/monitoring-usage.md (OpenTelemetry monitoring)
- https://code.claude.com/docs/en/settings-reference.md (the `env` setting, how `env` values interact with the shell, and variables ignored in project and local `env`)
- https://code.claude.com/docs/en/hooks.md (hook events such as SessionEnd, Stop, SubagentStop, SessionStart, Setup, CwdChanged, FileChanged, and persisted variables)
- https://code.claude.com/docs/en/statusline.md (status line commands)
- https://code.claude.com/docs/en/mcp.md (MCP servers, description length limits, claude.ai connectors, and output limits)
- https://code.claude.com/docs/en/headless.md (non-interactive mode)
- https://code.claude.com/docs/en/prompt-caching.md (prompt caching)
- https://code.claude.com/docs/en/plugins/mods/reference.md (mod elements, settings, and environment variables)
- https://code.claude.com/docs/en/plugins/mods/gallery (which terminals draw a mod `Image`)
- https://code.claude.com/docs/en/plugins/mods/overview.md (mods overview)
- https://code.claude.com/docs/en/sub-agents.md (subagent concurrency and nesting limits)
- https://code.claude.com/docs/en/plugins/cli-reference (plugin CLI, including flags that load a plugin for one session)
- https://code.claude.com/docs/en/plugins/create.md (creating plugins and loading a directory or archive for one session)
- https://code.claude.com/docs/en/plugins/troubleshooting.md (plugin troubleshooting, including Git clone timeouts)
- https://code.claude.com/docs/en/claude-code-on-the-web.md (cloud sessions)
- https://code.claude.com/docs/en/authentication.md (credential management)
- https://code.claude.com/docs/en/skills.md (skills and the Skill tool)
