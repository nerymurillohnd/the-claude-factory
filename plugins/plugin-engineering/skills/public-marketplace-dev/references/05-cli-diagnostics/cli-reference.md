# CLI reference

Reference for the Claude Code command-line interface: the commands and the flags Claude uses to start, script, diagnose and extend sessions.

## Contents

- [CLI commands](#cli-commands)
- [CLI flags](#cli-flags)
- [Documentation References](#documentation-references)

## CLI commands

Use these commands to start sessions, pipe content, resume conversations and manage updates:

| Command | Description | Example |
| :- | :- | :- |
| `claude` | Start interactive session | `claude` |
| `claude "query"` | Start interactive session with initial prompt | `claude "explain this project"` |
| `claude -p "query"` | Query via SDK, then exit | `claude -p "explain this function"` |
| `cat file \| claude -p "query"` | Process piped content | `cat logs.txt \| claude -p "explain"` |
| `claude update` | Update to latest version | `claude update` |
| `claude install [version]` | Install or reinstall the native binary. Accepts a version like `2.1.118`, or `stable` or `latest`. See [Install a specific version](https://code.claude.com/docs/en/setup.md#install-a-specific-version) | `claude install stable` |
| `claude doctor` | Print read-only installation and settings diagnostics from the terminal without starting a session, including install health, settings-file validation errors, and Remote Control eligibility. For the in-session setup checkup that can also apply fixes, run [`/doctor`](https://code.claude.com/docs/en/commands#all-commands) | `claude doctor` |
| `claude mcp` | Configure Model Context Protocol (MCP) servers | See the [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp.md). |
| `claude mcp login <name>` | Run a configured MCP server's OAuth flow without opening the interactive `/mcp` panel. Works for HTTP, SSE, and claude.ai connector servers. Add `--no-browser` over SSH to print the authorization URL instead of opening a browser. For an HTTP or SSE server, paste the redirect URL back at the prompt. For a claude.ai connector, see [Authorize a connector again from your shell](https://code.claude.com/docs/en/remote-control.md#authorize-a-connector-again-from-your-shell). See [Authenticate from the command line](https://code.claude.com/docs/en/mcp.md#authenticate-from-the-command-line) | `claude mcp login sentry` |
| `claude plugin` | Manage Claude Code [plugins](https://code.claude.com/docs/en/plugins/overview.md). Alias: `claude plugins`. See [plugin reference](https://code.claude.com/docs/en/plugins/cli-reference.md#claude-plugin-commands) for subcommands | `claude plugin install code-review@claude-plugins-official` |

## CLI flags

These command-line flags customize Claude Code's behavior. `claude --help` does not list every flag, so do not conclude that a flag is unavailable because `--help` omits it.

| Flag | Description | Example |
| :- | :- | :- |
| `--agent` | Specify an agent for the current session (overrides the `agent` setting) | `claude --agent my-custom-agent` |
| `--allowedTools`, `--allowed-tools` | Tools that execute without prompting for permission, apart from reads from [network paths](https://code.claude.com/docs/en/permissions.md#network-paths). See [permission rule syntax](https://code.claude.com/docs/en/settings-reference.md#permission-rule-syntax) for pattern matching. To restrict which tools are available, use `--tools` instead. If you name one of the [task-tracking tools](https://code.claude.com/docs/en/tools-reference.md#task-tool-availability) here, Claude Code also opts the session in | `"Bash(git log *)" "Bash(git diff *)" "Read"` |
| `--bare` | Minimal mode: skip auto-discovery of hooks, skills, custom commands, subagents, installed plugins, MCP servers, auto memory, and CLAUDE.md so scripted calls start faster. Skills in a directory you pass with `--add-dir` still load. Claude has access to Bash, file read, and file edit tools. Sets [`CLAUDE_CODE_SIMPLE`](https://code.claude.com/docs/en/env-vars). See [bare mode](https://code.claude.com/docs/en/headless.md#start-faster-with-bare-mode) | `claude --bare -p "query"` |
| `--channels` | (Research preview) MCP servers whose [channel](https://code.claude.com/docs/en/channels.md) notifications Claude should listen for in this session. Space-separated list of `plugin:<name>@<marketplace>` entries. Requires Anthropic authentication through claude.ai or a Console API key | `claude --channels plugin:my-notifier@my-marketplace` |
| `--dangerously-load-development-channels` | Enable [channels](https://code.claude.com/docs/en/channels-reference.md#test-during-the-research-preview) that are not on the approved allowlist, for local development. Accepts `plugin:<name>@<marketplace>` and `server:<name>` entries. Prompts for confirmation, so it takes effect in interactive sessions. With `-p`, Claude Code ignores the flag | `claude --dangerously-load-development-channels server:webhook` |
| `--debug` | Enable debug mode with optional category filtering, such as `--debug='mcp,startup'` or `--debug='!mcp'`. The filter binds only in the `=` form; a space-separated filter enables debug mode without filtering | `claude --debug='mcp,startup'` |
| `--debug-file <path>` | Write debug logs to a specific file path. Implicitly enables debug mode. Takes precedence over `CLAUDE_CODE_DEBUG_LOGS_DIR` | `claude --debug-file /tmp/claude-debug.log` |
| `--init` | Run [Setup hooks](https://code.claude.com/docs/en/hooks.md#setup) with the `init` matcher before the session (print mode only) | `claude -p --init "query"` |
| `--init-only` | Run [Setup](https://code.claude.com/docs/en/hooks.md#setup) and `SessionStart` hooks, then exit without starting a conversation | `claude --init-only` |
| `--include-hook-events` | Include hook lifecycle events in the output stream. `SessionStart` and `Setup` hook events are always included and don't need this flag. Some hook events, such as `Notification`, `SessionEnd`, `PreCompact`, and `PostCompact`, never produce a `hook_started` event, even with this flag. For those events, Claude Code still emits `hook_progress` while a command hook that runs for more than a second produces output, and emits `hook_response` only when a [hook that runs in the background](https://code.claude.com/docs/en/hooks.md#run-hooks-in-the-background) finishes. Requires `--output-format stream-json` | `claude -p --output-format stream-json --verbose --include-hook-events "query"` |
| `--maintenance` | Run [Setup hooks](https://code.claude.com/docs/en/hooks.md#setup) with the `maintenance` matcher before the session (print mode only) | `claude -p --maintenance "query"` |
| `--output-format` | Specify output format for print mode (options: `text`, `json`, `stream-json`) | `claude -p "query" --output-format json` |
| `--plugin-dir` | Load a plugin from a directory or `.zip` archive, or several from a [folder of plugins](https://code.claude.com/docs/en/plugins/create.md#load-a-directory-or-archive-for-one-session), for this session only. Each flag takes one path. Repeat the flag for more paths: `--plugin-dir A --plugin-dir B.zip`. Passing a folder of plugins requires Claude Code v2.1.265 or later | `claude --plugin-dir ./my-plugin` |
| `--print`, `-p` | Print response without interactive mode (see [Agent SDK documentation](https://code.claude.com/docs/en/agent-sdk/overview.md) for programmatic usage details). For `--resume` on a background session that is still running, see [Resume a running background session](https://code.claude.com/docs/en/sessions.md#resume-a-running-background-session) | `claude -p "query"` |
| `--safe-mode` | Start with all customizations disabled to troubleshoot a broken configuration: CLAUDE.md, skills, plugins, hooks, MCP servers, custom commands and agents, output styles, workflows, custom themes, custom keybindings, status line and file-suggestion commands, LSP servers, and auto memory do not load. Authentication, model selection, built-in tools, and permissions work normally, which differs from [`--bare`](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode). Managed settings policy still applies, including policy-configured hooks, status line, and file-suggestion commands; managed plugins, managed skills, managed CLAUDE.md, and policy-configured MCP servers do not. Useful for checking whether a customization is what triggers [automatic model fallback](https://code.claude.com/docs/en/model-config.md#automatic-model-fallback). Sets [`CLAUDE_CODE_SAFE_MODE`](https://code.claude.com/docs/en/env-vars) | `claude --safe-mode` |
| `--setting-sources` | Comma-separated list of setting sources to load (`user`, `project`, `local`). See [agent view](https://code.claude.com/docs/en/agent-view.md#what-carries-over-when-you-background) and [agent teams](https://code.claude.com/docs/en/agent-teams.md#context-and-communication) for the sessions you start from this one that inherit the list | `claude --setting-sources user,project` |
| `--settings` | Path to a settings JSON file or an inline JSON string. Values you set here override the same keys in your `settings.json` files for this session. Keys you omit keep their file-based values. The file must be a regular file no larger than 2 MiB. See [settings precedence](https://code.claude.com/docs/en/settings.md#settings-precedence) | `claude --settings ./settings.json` |
| `--verbose` | Enable verbose logging, shows full turn-by-turn output. Overrides the [`viewMode`](https://code.claude.com/docs/en/settings-reference#viewmode) setting for this session | `claude --verbose` |
| `--version`, `-v` | Output the version number | `claude -v` |

## Documentation References

- Source page: https://code.claude.com/docs/en/cli-reference — the full CLI reference, including commands and flags this pruned copy omits.
- https://code.claude.com/docs/en/setup.md — installing Claude Code and pinning a specific version.
- https://code.claude.com/docs/en/commands — every built-in slash command, including `/doctor`.
- https://code.claude.com/docs/en/mcp.md — MCP server configuration and command-line authentication.
- https://code.claude.com/docs/en/remote-control.md — Remote Control and re-authorizing a claude.ai connector from the shell.
- https://code.claude.com/docs/en/plugins/overview.md — what plugins are and how they are managed.
- https://code.claude.com/docs/en/plugins/cli-reference.md — the `claude plugin` subcommands.
- https://code.claude.com/docs/en/permissions.md — permission behavior, including network paths.
- https://code.claude.com/docs/en/settings-reference.md — permission rule syntax and settings keys such as `viewMode`.
- https://code.claude.com/docs/en/settings-reference — the same settings reference, linked without the `.md` suffix for `viewMode`.
- https://code.claude.com/docs/en/tools-reference.md — built-in tools and task-tool availability.
- https://code.claude.com/docs/en/env-vars — environment variables such as `CLAUDE_CODE_SIMPLE` and `CLAUDE_CODE_SAFE_MODE`.
- https://code.claude.com/docs/en/headless.md — bare mode and running Claude Code programmatically.
- https://code.claude.com/docs/en/headless — the same headless page, linked without the `.md` suffix.
- https://code.claude.com/docs/en/channels.md — channels (research preview).
- https://code.claude.com/docs/en/channels-reference.md — channels reference and testing during the research preview.
- https://code.claude.com/docs/en/hooks.md — hooks reference, including Setup hooks and background hooks.
- https://code.claude.com/docs/en/plugins/create.md — creating plugins and loading a directory or archive for one session.
- https://code.claude.com/docs/en/agent-sdk/overview.md — the Agent SDK for programmatic use.
- https://code.claude.com/docs/en/sessions.md — sessions, including resuming a running background session.
- https://code.claude.com/docs/en/model-config.md — model configuration and automatic model fallback.
- https://code.claude.com/docs/en/agent-view.md — agent view and what carries over when a session is backgrounded.
- https://code.claude.com/docs/en/agent-teams.md — agent teams, context and communication.
- https://code.claude.com/docs/en/settings.md — settings files, configuration options and settings precedence (moved here from the removed "See also" section).
