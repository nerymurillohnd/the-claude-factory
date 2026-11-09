# Run Claude Code programmatically

How to use the Agent SDK to run Claude Code programmatically from the CLI, Python or TypeScript.

The [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) provides the same tools, agent loop, and context management that power Claude Code. It is available as a CLI for scripts and CI/CD, or as [Python](https://code.claude.com/docs/en/agent-sdk/python.md) and [TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript.md) packages for full programmatic control.

To run Claude Code in non-interactive mode, pass `-p` with the prompt and the [CLI options](https://code.claude.com/docs/en/cli-reference.md) the run needs:

```bash theme={null}
claude -p "Find and fix the bug in auth.py" --allowedTools "Read,Edit,Bash"
```

This file covers the Agent SDK through the CLI (`claude -p`). For the Python and TypeScript SDK packages with structured outputs, tool approval callbacks, and native message objects, see the [full Agent SDK documentation](https://code.claude.com/docs/en/agent-sdk/overview.md).

## Contents

- [Basic usage](#basic-usage)
  - [Start faster with bare mode](#start-faster-with-bare-mode)
- [Examples](#examples)
  - [Get structured output](#get-structured-output)
  - [Stream responses](#stream-responses)
    - [Read session metadata](#read-session-metadata)
    - [Fail CI when a plugin or MCP server doesn't load](#fail-ci-when-a-plugin-or-mcp-server-doesnt-load)
    - [Track plugin installs](#track-plugin-installs)
  - [Create a commit](#create-a-commit)
- [Documentation References](#documentation-references)

## Basic usage

Add the `-p` (or `--print`) flag to any `claude` command to run it non-interactively. Not every [CLI option](https://code.claude.com/docs/en/cli-reference.md) combines with `-p`:

- Claude Code rejects `--bg`, and rejects `--cloud` with a task description, with an error naming the conflict.
- `--cloud` with a session ID and `-p` instead [queues a message into that cloud session](https://code.claude.com/docs/en/claude-code-on-the-web.md#send-follow-ups-from-the-cli) and exits.

Options commonly combined with `-p` include:

* `--continue` for [continuing conversations](https://code.claude.com/docs/en/headless#continue-conversations)
* `--allowedTools` for [auto-approving tools](https://code.claude.com/docs/en/headless#auto-approve-tools)
* `--output-format` for [structured output](#get-structured-output)

This example asks Claude a question about the codebase and prints the response:

```bash theme={null}
claude -p "What does the auth module do?"
```

Claude Code exits with code 0 on success and a non-zero code when the run fails, so scripts can branch on the exit status. An invalid flag is reported to stderr before the run starts. A failure inside the run, such as missing authentication, is printed as the result on stdout.

### Start faster with bare mode

Add `--bare` to reduce startup time by skipping auto-discovery of hooks, skills, custom commands, [subagents](https://code.claude.com/docs/en/sub-agents.md), installed plugins, MCP servers, auto memory, and CLAUDE.md. Without it, `claude -p` discovers and loads them as an interactive session would, including anything configured in the working directory or `~/.claude`.

Use bare mode for CI and scripts that must produce the same result on every machine. A hook in a teammate's `~/.claude` or an MCP server in the project's `.mcp.json` won't run, because bare mode never reads them. A directory named with `--add-dir` is a partial exception: bare mode loads skills from its `.claude/skills/` folder, but still skips its `.claude/commands/` and `.claude/agents/` folders. [Skills from additional directories](https://code.claude.com/docs/en/skills.md#skills-from-additional-directories) covers what does and doesn't load.

Without `--bare`, a `-p` session runs the hooks in a project's `.claude/settings.json` and connects the servers in its `.mcp.json`, even in a folder that was never trusted. A `-p` session shows no workspace trust dialog and no per-server approval prompt. [What runs before you trust a folder](https://code.claude.com/docs/en/permissions.md#what-runs-before-you-trust-a-folder) covers each kind of repository content under `-p` and how to keep it out.

This example runs a one-off summarize task in bare mode and pre-approves the Read tool so the call completes without a permission prompt. Set `ANTHROPIC_API_KEY` before running it, because bare mode doesn't use the subscription login:

```bash theme={null}
claude --bare -p "Summarize README.md" --allowedTools "Read"
```

In bare mode, Claude Code never reads OAuth credentials or the system keychain. For the Anthropic API, either set `ANTHROPIC_API_KEY` in the environment, with a key created in the [Claude Console](https://platform.claude.com), or supply an `apiKeyHelper` in the `--settings` JSON. Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry continue to read their own provider credentials as usual.

In bare mode Claude has access to the Bash, file read, and file edit tools. Pass any other context the run needs with a flag:

| To load | Use |
| - | - |
| System prompt additions | `--append-system-prompt`, `--append-system-prompt-file` |
| Settings | `--settings <file-or-json>` |
| MCP servers | `--mcp-config <file-or-json>` |
| [Custom agents](https://code.claude.com/docs/en/sub-agents.md#choose-the-subagent-scope) | `--agents <file-or-json>` |
| A plugin | `--plugin-dir <path>`, `--plugin-url <url>` |

Hooks still don't run in bare mode when passed with `--settings`, or when defined in the [`hooks/hooks.json`](https://code.claude.com/docs/en/plugins/components#hooks) or [`hooks` manifest key](https://code.claude.com/docs/en/plugins/manifest-reference#hooks) of a plugin loaded with a flag. Do not use bare mode for a run that needs hooks.

Bare mode also limits what happens while the session runs:

* **MCP servers**: only servers supplied on the command line connect, for example with `--mcp-config`. In an interactive session, Claude Code also skips the automatic IDE connection unless `--ide` is passed.
* **System reminders**: Claude gets the prompts and the tool results without the [system reminders](https://code.claude.com/docs/en/glossary.md#system-reminder) Claude Code would add alongside them. For example, Claude isn't told when a file it read earlier changes on disk, and it doesn't get the list of available skills, including skills from an `--add-dir` folder.
* **Background tasks**: Claude can't run background commands or background subagents, and the other features that [`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`](https://code.claude.com/docs/en/env-vars) turns off are off too. A command that reaches its [timeout](https://code.claude.com/docs/en/tools-reference.md#timeout-and-output-limits) stops instead of [moving to the background](https://code.claude.com/docs/en/tools-reference.md#background-commands).

Before v2.1.286, these limits held only partly: an interactive `--bare` session connected the MCP servers that a normal session would, every `--bare` session sent system reminders, and background tasks stayed available.

> **Note:** `--bare` is the recommended mode for scripted and SDK calls, and will become the default for `-p` in a future release.

## Examples

These examples show common CLI patterns. Where a command names a file such as `auth.py` or `build-error.txt`, substitute a file from the actual project. In CI or other scripted environments, add [`--bare`](#start-faster-with-bare-mode) so Claude Code starts without loading the host's hooks, plugins, auto memory, or `CLAUDE.md`.

### Get structured output

Use `--output-format` to control how responses are returned:

* `text` (default): plain text output
* `json`: structured JSON with result, session ID, and metadata
* `stream-json`: newline-delimited JSON for real-time streaming

This example returns a project summary as JSON with session metadata, with the text result in the `result` field:

```bash theme={null}
claude -p "Summarize this project" --output-format json
```

### Stream responses

To receive tokens as they're generated, use `--output-format stream-json` with `--verbose` and `--include-partial-messages`. Each line is a JSON object representing an event:

```bash theme={null}
claude -p "Explain recursion" --output-format stream-json --verbose --include-partial-messages
```

The last line of the stream is a `result` message with the final response text, cost, and session metadata.

#### Read session metadata

The `system/init` event reports session metadata including the model, tools, MCP servers, and loaded plugins. It is the first event in the stream unless these startup events precede it:

* `plugin_install` events, when [`CLAUDE_CODE_SYNC_PLUGIN_INSTALL`](https://code.claude.com/docs/en/env-vars) is set.
* [`hook_started`, `hook_progress`, and `hook_response` events](https://code.claude.com/docs/en/agent-sdk/typescript#sdkhookstartedmessage), while a configured [`SessionStart`](https://code.claude.com/docs/en/hooks#sessionstart) or [`Setup`](https://code.claude.com/docs/en/hooks#setup) hook runs. These stream as the hook produces them.

The event also carries an optional `capabilities` array of strings naming the protocol behaviors this Claude Code version implements, such as `interrupt_receipt_v1` or `interrupt_cancel_queued_v1`. Check it to feature-detect instead of comparing version strings, and ignore values that are not recognized. See [`SDKSystemMessage`](https://code.claude.com/docs/en/agent-sdk/typescript#sdksystemmessage) for the capability list.

#### Fail CI when a plugin or MCP server doesn't load

Use the plugin fields in the `system/init` event to catch a plugin that didn't load:

| Field | Type | Description |
| - | - | - |
| `plugins` | array | plugins that loaded successfully, each with `name` and `path` |
| `plugin_errors` | array | plugin load-time errors, each with `plugin`, `type`, and `message`. Includes unsatisfied dependency versions and `--plugin-dir` load failures such as a missing path or invalid archive. A plugin that didn't load is absent from `plugins`. The key is omitted when there are no errors |

When a `--plugin-dir` directory or archive itself fails to load, its `plugin_errors` entry includes the resolved absolute path as `path`. Use it to tell which of several `--plugin-dir` values failed. The `path` field requires Claude Code v2.1.283 or later.

Use the MCP server fields the same way. When [`--mcp-config`](https://code.claude.com/docs/en/cli-reference#cli-flags) is passed with `-p`, Claude Code waits for still-pending servers before running the first turn, up to the [`MCP_TIMEOUT`](https://code.claude.com/docs/en/env-vars) startup timeout, 30 seconds by default. The wait requires Claude Code v2.1.221 or later. Two exceptions apply:

- A remote server with a [cached tool list](https://code.claude.com/docs/en/agent-sdk/mcp.md#connection-timing) skips the wait, shows `pending` in `system/init`, and connects on its first tool call.
- In a [self-hosted environment](https://code.claude.com/docs/en/self-hosted-environments-configuration.md#connection-timing), a shorter wait applies instead.

Claude Code validates each `--mcp-config` entry at startup and skips entries that fail validation, for example a `url` entry with no `type`. The run continues and exits cleanly, so check these fields to catch a server that never loaded:

| Field | Type | Description |
| - | - | - |
| `mcp_servers` | array | MCP servers in the session, each with `name` and `status` |
| `mcp_server_errors` | array | `--mcp-config` entries skipped by config validation, each with `name`, `type`, and `message`. `type` is a skip category such as `unknown_type`, `url_missing_type`, `invalid_config`, or `reserved_name`; treat values you don't recognize as a generic skip. Affected servers are absent from `mcp_servers`. The key is omitted when there are no errors, so a CI gate can fail on a non-empty array |

When the command runs directly in a terminal, Claude Code also prints a startup warning to stderr, such as `Warning: 1 MCP server skipped due to invalid config:`, followed by the reason for each skipped entry.

When stderr is redirected, or when a program such as a CI runner or an SDK host captures it, Claude Code prints no warning. It reports the skipped entries only in the `mcp_server_errors` field.

#### Track plugin installs

When [`CLAUDE_CODE_SYNC_PLUGIN_INSTALL`](https://code.claude.com/docs/en/env-vars) is set, Claude Code emits `system/plugin_install` events while marketplace plugins install before the first turn. Use these to surface install progress in a custom UI.

| Field | Type | Description |
| - | - | - |
| `type` | `"system"` | message type |
| `subtype` | `"plugin_install"` | identifies this as a plugin install event |
| `status` | `"started"`, `"installed"`, `"failed"`, or `"completed"` | `started` and `completed` bracket the overall install; `installed` and `failed` report individual marketplaces |
| `name` | string, optional | marketplace name, present on `installed` and `failed` |
| `error` | string, optional | failure message, present on `failed` |
| `uuid` | string | unique event identifier |
| `session_id` | string | session the event belongs to |

### Create a commit

> **Note:** Command support differs in `-p` mode:
>
> * User-invoked [skills](https://code.claude.com/docs/en/skills.md) and custom commands work. Include `/skill-name` in the prompt string and Claude Code expands it before running.
> * Built-in commands that only run in the terminal interface, such as `/login`, aren't available.
> * `/model`, `/effort`, `/fast`, `/color`, and `/rename` accept the value as an argument, for example `/model sonnet`, and `/mcp` with no argument prints a text summary of server status. These forms follow each command's [availability notes](https://code.claude.com/docs/en/commands.md#all-commands).
> * To change a setting, pass `key=value` to `/config`, for example `/config thinking=false`.
> * `/output-style <style>` switches [output styles](https://code.claude.com/docs/en/output-styles.md) and `/output-style` alone lists them. Requires Claude Code v2.1.269 or later.

## Documentation References

- Source page: https://code.claude.com/docs/en/headless — the full page on running Claude Code programmatically, including the examples this pruned copy omits.
- https://code.claude.com/docs/en/agent-sdk/overview.md — the full Agent SDK documentation.
- https://code.claude.com/docs/en/agent-sdk/python.md — the Python Agent SDK package.
- https://code.claude.com/docs/en/agent-sdk/typescript.md — the TypeScript Agent SDK package and its message types, including `SDKSystemMessage` and hook messages.
- https://code.claude.com/docs/en/agent-sdk/mcp.md — MCP in the Agent SDK, including connection timing.
- https://code.claude.com/docs/en/cli-reference.md — all CLI flags and options (also listed in the removed "Next steps" section).
- https://code.claude.com/docs/en/cli-reference — the same CLI reference, linked without `.md` for `--mcp-config`.
- https://code.claude.com/docs/en/claude-code-on-the-web.md — Claude Code on the web and sending follow-ups from the CLI.
- https://code.claude.com/docs/en/sub-agents.md — subagents and subagent scope.
- https://code.claude.com/docs/en/skills.md — skills, including skills from additional directories.
- https://code.claude.com/docs/en/permissions.md — what runs before a folder is trusted.
- https://platform.claude.com — the Claude Console, where API keys are created.
- https://code.claude.com/docs/en/plugins/components — plugin components, including `hooks/hooks.json`.
- https://code.claude.com/docs/en/plugins/manifest-reference — the plugin manifest reference, including the `hooks` key.
- https://code.claude.com/docs/en/glossary.md — glossary, including system reminders.
- https://code.claude.com/docs/en/env-vars — environment variables such as `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`, `CLAUDE_CODE_SYNC_PLUGIN_INSTALL` and `MCP_TIMEOUT`.
- https://code.claude.com/docs/en/tools-reference.md — tool timeouts, output limits and background commands.
- https://code.claude.com/docs/en/hooks — hooks reference, including `SessionStart` and `Setup`.
- https://code.claude.com/docs/en/self-hosted-environments-configuration.md — self-hosted environment configuration and connection timing.
- https://code.claude.com/docs/en/commands.md — built-in commands and their availability notes.
- https://code.claude.com/docs/en/output-styles.md — output styles.
- https://code.claude.com/docs/en/github-actions.md — using the Agent SDK in GitHub workflows (moved here from the removed "Next steps" section).
