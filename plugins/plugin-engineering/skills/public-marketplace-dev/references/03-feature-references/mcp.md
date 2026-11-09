# Connect Claude Code to tools via MCP

This file is the reference for connecting Claude Code to tools through the Model Context Protocol (MCP): transports, server management, reconnection, time limits, MCP tasks, plugin-provided servers, scopes, authentication, output limits, tool schemas and annotations, elicitation, resources, tool search, and MCP prompts.

## Contents

- [Find and build MCP servers](#find-and-build-mcp-servers)
- [Installing MCP servers](#installing-mcp-servers)
  - [Option 1: Add a remote HTTP server](#option-1-add-a-remote-http-server)
  - [Option 2: Add a remote SSE server](#option-2-add-a-remote-sse-server)
  - [Option 3: Add a local stdio server](#option-3-add-a-local-stdio-server)
    - [How Claude Code stops a stdio server](#how-claude-code-stops-a-stdio-server)
  - [Option 4: Add a remote WebSocket server](#option-4-add-a-remote-websocket-server)
  - [Managing your servers](#managing-your-servers)
    - [Server status](#server-status)
    - [Server status detail](#server-status-detail)
    - [Configuration warnings](#configuration-warnings)
    - [Tool availability](#tool-availability)
  - [Disable a server without removing it](#disable-a-server-without-removing-it)
  - [MCP client runtimes](#mcp-client-runtimes)
  - [Dynamic tool updates](#dynamic-tool-updates)
    - [Notification streams on the v2 runtime](#notification-streams-on-the-v2-runtime)
  - [Automatic reconnection](#automatic-reconnection)
    - [Mid-session drops of a remote server](#mid-session-drops-of-a-remote-server)
    - [Failed first connections](#failed-first-connections)
    - [Stdio servers that exit or fail to start](#stdio-servers-that-exit-or-fail-to-start)
    - [Failed discovery requests](#failed-discovery-requests)
    - [Retry failed servers yourself](#retry-failed-servers-yourself)
    - [How Claude learns that a server failed](#how-claude-learns-that-a-server-failed)
  - [Push messages with channels](#push-messages-with-channels)
  - [Time limits on MCP tool calls](#time-limits-on-mcp-tool-calls)
  - [Automatic backgrounding of long tool calls](#automatic-backgrounding-of-long-tool-calls)
  - [MCP tasks that run on the server](#mcp-tasks-that-run-on-the-server)
    - [Stop an MCP task or get its result](#stop-an-mcp-task-or-get-its-result)
    - [Answer a question from an MCP task](#answer-a-question-from-an-mcp-task)
    - [Exit, clear, or resume while an MCP task runs](#exit-clear-or-resume-while-an-mcp-task-runs)
    - [What a call needs to become an MCP task](#what-a-call-needs-to-become-an-mcp-task)
    - [Status messages on an MCP task](#status-messages-on-an-mcp-task)
    - [Time limits on MCP tasks](#time-limits-on-mcp-tasks)
    - [Make Claude wait for the result of an MCP task](#make-claude-wait-for-the-result-of-an-mcp-task)
  - [MCP tasks for server authors](#mcp-tasks-for-server-authors)
    - [Answer the call with a task](#answer-the-call-with-a-task)
    - [Report status, results, and questions](#report-status-results-and-questions)
  - [Plugin-provided MCP servers](#plugin-provided-mcp-servers)
- [MCP installation scopes](#mcp-installation-scopes)
  - [Scope hierarchy and precedence](#scope-hierarchy-and-precedence)
  - [Environment variable expansion in `.mcp.json`](#environment-variable-expansion-in-mcpjson)
    - [Example with variable expansion](#example-with-variable-expansion)
    - [Unset variables without a default](#unset-variables-without-a-default)
    - [Variables set to an empty string](#variables-set-to-an-empty-string)
    - [Credential variables that read as empty](#credential-variables-that-read-as-empty)
    - [How references appear in `/mcp` and CLI output](#how-references-appear-in-mcp-and-cli-output)
- [Authenticate with remote MCP servers](#authenticate-with-remote-mcp-servers)
  - [Authenticate from the command line](#authenticate-from-the-command-line)
  - [Use a fixed OAuth callback port](#use-a-fixed-oauth-callback-port)
  - [Override OAuth metadata discovery](#override-oauth-metadata-discovery)
  - [Restrict OAuth scopes](#restrict-oauth-scopes)
  - [Use OAuth with a server behind an authenticating proxy](#use-oauth-with-a-server-behind-an-authenticating-proxy)
  - [Use dynamic headers for custom authentication](#use-dynamic-headers-for-custom-authentication)
    - [Where the helper runs](#where-the-helper-runs)
    - [Which variables a helper can read](#which-variables-a-helper-can-read)
    - [Trust a folder before its headersHelper runs](#trust-a-folder-before-its-headershelper-runs)
  - [Sign in to an MCP server behind a gateway that requires a header](#sign-in-to-an-mcp-server-behind-a-gateway-that-requires-a-header)
- [Use MCP servers from claude.ai](#use-mcp-servers-from-claudeai)
- [MCP output limits and warnings](#mcp-output-limits-and-warnings)
  - [Raise the limit for a specific tool](#raise-the-limit-for-a-specific-tool)
  - [Images in tool results](#images-in-tool-results)
- [Tool input schemas with a root-level combinator](#tool-input-schemas-with-a-root-level-combinator)
- [Tools with invalid input schemas](#tools-with-invalid-input-schemas)
  - [Tools whose input schema the API refuses](#tools-whose-input-schema-the-api-refuses)
- [Tools with names longer than 128 characters](#tools-with-names-longer-than-128-characters)
- [Require approval for a specific tool](#require-approval-for-a-specific-tool)
- [Mark tools that are safe to call twice](#mark-tools-that-are-safe-to-call-twice)
- [Respond to MCP elicitation requests](#respond-to-mcp-elicitation-requests)
  - [Answer an elicitation request in a cloud session](#answer-an-elicitation-request-in-a-cloud-session)
  - [Elicitation modes Claude Code declares](#elicitation-modes-claude-code-declares)
- [Use MCP resources](#use-mcp-resources)
  - [Reference MCP resources](#reference-mcp-resources)
- [Scale with MCP tool search](#scale-with-mcp-tool-search)
  - [Tool search for MCP server authors](#tool-search-for-mcp-server-authors)
    - [Change the description length limits](#change-the-description-length-limits)
    - [Mark a tool to load upfront or stay deferred](#mark-a-tool-to-load-upfront-or-stay-deferred)
  - [Configure tool search](#configure-tool-search)
    - [Tools that stay deferred below the `ENABLE_TOOL_SEARCH=auto` threshold](#tools-that-stay-deferred-below-the-enable_tool_searchauto-threshold)
  - [Exempt a server from deferral](#exempt-a-server-from-deferral)
  - [Defer a server's tools](#defer-a-servers-tools)
- [Use MCP prompts as commands](#use-mcp-prompts-as-commands)
  - [Execute MCP prompts](#execute-mcp-prompts)
- [Managed MCP configuration](#managed-mcp-configuration)
- [Documentation References](#documentation-references)

Claude Code can connect to hundreds of external tools and data sources through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction), an open source standard for AI-tool integrations. An MCP server gives Claude Code access to a user's tools, databases, and APIs.

A server is worth connecting when the user keeps copying data into the chat from another tool, such as an issue tracker or a monitoring dashboard. Once the server is connected, Claude reads and acts on that system directly instead of working from pasted text.

For a first server, the [MCP quickstart](https://code.claude.com/docs/en/mcp-quickstart.md) gives a step-by-step walkthrough. This file is the full reference.

## Find and build MCP servers

To build a server, read the [MCP server guide](https://modelcontextprotocol.io/docs/develop/build-server) for protocol fundamentals and the [Claude connector building docs](https://claude.com/docs/connectors/building) for authentication, testing, and Directory submission.

To have Claude scaffold a server, use the official [`mcp-server-dev` plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/mcp-server-dev):

**1. Install the plugin**

In the VS Code extension or the desktop app, follow [Install a plugin](https://code.claude.com/docs/en/plugins/install.md#install-a-plugin) instead of this step. In a terminal, start Claude Code with `claude`, then enter this at its prompt:

```
/plugin install mcp-server-dev@claude-plugins-official
```

If the install fails, act on the message Claude Code reports:

* `Marketplace "claude-plugins-official" not found`: add the marketplace with `/plugin marketplace add anthropics/claude-plugins-official`, then retry the install.
* `Plugin "<name>" not found in marketplace "claude-plugins-official"`: the local copy of the marketplace catalog may be out of date. Refresh it with `/plugin marketplace update claude-plugins-official`, then retry the install. If the retry prints the same message, follow [Plugin not found in marketplace](https://code.claude.com/docs/en/plugins/troubleshooting.md#plugin-not-found-in-marketplace).

If the install summary reports `Run /reload-plugins to apply.`, Claude Code runs that reload itself. If the reload warns that the next message would re-read the conversation, run `/reload-plugins --force`.

**2. Run the build skill**

```
/mcp-server-dev:build-mcp-server
```

Claude asks about the use case and scaffolds a remote HTTP or local stdio server.

## Installing MCP servers

Claude Code supports four transports for an MCP server. Choose the one that fits the server:

### Option 1: Add a remote HTTP server

Use HTTP for remote MCP servers: it is the recommended option and the most widely supported transport for cloud-based services.

In JSON configuration (`.mcp.json`, `~/.claude.json`, or `claude mcp add-json`), the `type` field accepts `streamable-http` as an alias for `http`. The MCP specification calls this transport `streamable-http`, so configurations copied from server documentation work without modification.

Always give a JSON entry that has a `url` a `type`. Claude Code reads an entry with no `type` as a stdio server, so a `url` without a `type` is a configuration error: Claude Code skips that server and reports `MCP server "<name>" has a "url" but no "type"; add "type": "http" (or "sse" / "ws") to this entry`.

### Option 2: Add a remote SSE server

> [!WARNING]
>
> The SSE (Server-Sent Events) transport is deprecated. Use HTTP servers instead, where available.

### Option 3: Add a local stdio server

A stdio server runs as a local process on the user's machine. Use it for tools that need direct system access or custom scripts.

Claude Code sets `CLAUDE_PROJECT_DIR` in the spawned server's environment to the project root, so the server can resolve project-relative paths without depending on the working directory. It is the same directory hooks receive in their `CLAUDE_PROJECT_DIR` variable. Read it from inside the server process, for example `process.env.CLAUDE_PROJECT_DIR` in Node or `os.environ["CLAUDE_PROJECT_DIR"]` in Python.

`CLAUDE_PROJECT_DIR` is the stable project root and doesn't change when working directories are added or removed mid-session. A server that limits its own filesystem access to a set of allowed directories should implement the MCP `roots/list` request instead. Claude Code answers `roots/list` with the session's launch directory plus every [additional working directory](https://code.claude.com/docs/en/permissions.md#working-directories) granted with `--add-dir`, `/add-dir`, or the `additionalDirectories` setting, and sends `notifications/roots/list_changed` when that set changes.

The variable is set in the server's environment, not in Claude Code's own environment. To reference it through `${VAR}` expansion in the `command` or `args` of a project-scoped `.mcp.json` entry, or of a local- or user-scoped server entry in `~/.claude.json`, give it a default such as `${CLAUDE_PROJECT_DIR:-.}`. Plugin-provided MCP configurations substitute `${CLAUDE_PROJECT_DIR}` directly and don't need the default.

#### How Claude Code stops a stdio server

When Claude Code disconnects a stdio server, for example when the session ends, it signals the server process and waits briefly for it to exit before forcing it to stop. If the server saves state or removes lock files at shutdown, handle the signal for each platform and finish within that time:

* **On macOS and Linux**: Claude Code sends `SIGINT`, then `SIGTERM` if the process is still running 100 milliseconds later, then `SIGKILL` after a further 400 milliseconds.
* **On Windows**: Claude Code closes the server's stdin, then ends the server's process tree if the process is still running 300 milliseconds later.

Before v2.1.296, Claude Code on Windows ended the server's process tree at once, without closing stdin first or waiting.

### Option 4: Add a remote WebSocket server

A WebSocket server holds a persistent bidirectional connection, which suits a remote MCP server that pushes events to Claude unprompted. Use HTTP instead when the server only responds to requests: HTTP supports OAuth and the `claude mcp add --transport` flag, and WebSocket supports neither.

The `type: "ws"` entry accepts the same `url`, `headers`, `headersHelper`, `timeout`, and `alwaysLoad` fields as `http`. Authentication is header-only: pass a static token in `headers`, or generate one at connect time with [`headersHelper`](#use-dynamic-headers-for-custom-authentication). The `claude mcp add --transport` flag doesn't accept `ws`.

### Managing your servers

Manage configured MCP servers with these commands:

```bash theme={null}
# List all configured servers
claude mcp list

# Get details for a specific server
claude mcp get notion

# Remove a server
claude mcp remove notion

# (within Claude Code) Check server status
/mcp
```

#### Server status

`claude mcp list` shows a health status next to each server it lists, such as `✔ Connected`, `! Needs authentication`, or `✘ Failed to connect`. A failure status means Claude Code couldn't connect to that server, not that the list command failed.

The following statuses report a configuration decision rather than a connection attempt, so Claude Code prints them without connecting to the server:

* `⊘ Disabled for this project (re-enable via /mcp)`: a server named in the project's [`disabledMcpServers`](#disable-a-server-without-removing-it) list. Claude Code shows it in both `claude mcp list` and `claude mcp get <name>`. Turn the server back on from the `/mcp` panel.
* `✘ Blocked by enterprise managed policy`: a server that one of the organization's policies refuses. Claude Code shows it in both `claude mcp list` and `claude mcp get <name>`. A server blocked by an allowlist, a denylist, or another restriction in [managed MCP configuration](https://code.claude.com/docs/en/managed-mcp.md#how-restrictions-appear-to-users) is hidden from both commands instead of shown with this status. Tell the user to ask the organization's administrator which policy blocks the server.

#### Server status detail

In `/mcp` (including a server's menu there) and in the [`/plugin`](https://code.claude.com/docs/en/plugins/install) manager, a remote HTTP or SSE server used before can show a `cached` status such as `cached 2h ago · connects on first use · 5 tools`. Claude Code loaded the server's tool list from its discovery cache, saved in a previous session, instead of connecting at startup, and connects the server the first time Claude calls one of its tools. The tools are available from the first message, so no action is needed. The discovery cache and its `cached` status require Claude Code v2.1.221 or later.

The discovery cache is off by default unless a gradual rollout has enabled it for the account. Set [`MCP_DISCOVERY_CACHE=1`](https://code.claude.com/docs/en/env-vars) to turn it on, or `0` to keep it off even when the rollout has enabled it. Before v2.1.238, the cache was on by default.

Selecting **Disable** or **Clear authentication** from a server's menu in `/mcp` also discards that server's cache entry. **Reconnect** discards it too on a connected or failed server; on a `cached` server, **Reconnect** connects the server now and keeps the entry. After the entry is discarded, the next connection fetches the tool list from the server instead of from the cache.

##### Connection failures and unconfigured servers

When a server's status is `✘ Failed to connect`, `claude mcp list` appends the failure detail to that status line, and `claude mcp get <name>` shows it on an `Issue:` line. The detail is the HTTP status or error code, plus any error text the server returned. The server's detail view in `/mcp` includes the same server-reported text in its `Issue:` row.

Claude Code redacts credential-like text from this detail and never includes the expanded server URL, which can carry secrets. It appends no detail to a `✘ Connection error` status, because the exception text it would print there can embed that URL.

When authentication completed from `/mcp` is followed by a connection that still fails with an HTTP status or a transport error code, Claude Code adds that code and the origin of the server's URL to the message it prints after the attempt. The origin is the scheme and host, plus the port when the URL names one, such as `https://mcp.example.com`.

* The path and query never appear in that message.
* For a server in the local, project, or user [scope](#mcp-installation-scopes) or in managed MCP configuration, the origin shows the host as written in that configuration, so a `${VAR}` reference in the host isn't expanded in the message.
* For a failure with no status or error code, Claude Code shows the error text without the origin.

A remote server whose configuration has an empty `url` shows as `not configured` in `/mcp`, in `claude mcp list`, and in the [`/plugin`](https://code.claude.com/docs/en/plugins/install) manager, and Claude Code doesn't attempt to connect to it. A plugin can ship such a placeholder entry for a connector the user configures later, and Claude Code doesn't report it as an error or a setup issue. The server's detail view in `/mcp` reads `No URL configured for this server`; set the entry's `url` to connect it.

#### Configuration warnings

Claude Code warns about the following configuration problems. Each entry says what Claude Code checks and how to clear the warning:

* **Hidden whitespace**: Claude Code warns when an MCP config value carries hidden leading or trailing whitespace, which often comes from pasting a token with a trailing newline. It checks `command`, `url`, each `args` entry, and the values and key names under `env` and `headers`. The warning appears in `claude mcp list` output and in `/mcp`, naming the affected fields without echoing their values, for example `Leading or trailing whitespace in: headers.Authorization`. Claude Code doesn't trim the whitespace and uses the values exactly as written, so edit the configuration to remove it.
* **Same name in more than one scope**: when the same server name is defined in more than one [scope](#mcp-installation-scopes) with different endpoints, Claude Code warns about the conflict in `claude mcp list` output and in `/mcp`. OAuth sign-ins are stored per endpoint, so authenticating the definition that loads in one project doesn't sign in a project where a different definition loads. Keep the intended endpoint and remove the others with `claude mcp remove <name> --scope <scope>`. The warning quotes each scope's endpoint as written in the configuration, with [`${VAR}` references](#environment-variable-expansion-in-mcpjson) unexpanded, so it never shows a resolved value such as an API key.
* **Reserved names**: Claude Code reserves the names of its built-in servers, including `workspace`, `claude-in-chrome`, `computer-use`, `Claude Preview`, and `Claude Browser`. A configured server with a reserved name is skipped at load time, with a warning asking for a rename. `claude mcp add` rejects a reserved name with an error. `Claude Preview` and `Claude Browser` both name the built-in server that the [Claude Code desktop app's preview pane](https://code.claude.com/docs/en/desktop.md#preview-your-app) uses.
* **Missing environment variable**: when a [`${VAR}` reference](#environment-variable-expansion-in-mcpjson) in a server's configuration names a variable that isn't set and has no `:-default`, Claude Code warns in `claude mcp list` output and in `/mcp`, naming the variable, and still loads the server with the `${VAR}` text unexpanded. Set the variable or add a `${VAR:-default}` fallback. In a remote server's `url` and `headers`, some credential variables [read as empty](#credential-variables-that-read-as-empty) instead, with no warning.

#### Tool availability

The `/mcp` panel shows the tool count next to each connected server and flags servers that advertise the tools capability but expose no tools.

##### Tool counts in a cloud session

In a [cloud session](https://code.claude.com/docs/en/claude-code-on-the-web.md), a count such as `3 of 13 tools available` means Claude can't use the other 10. Check for these causes, among others:

* **A deny rule in the repository's `.claude/settings.json` names the tool or its whole server**: remove the [rule](https://code.claude.com/docs/en/permissions.md#mcp), if [the session reads that file](https://code.claude.com/docs/en/settings.md#settings-in-cloud-sessions)
* **The tool's full name is over 128 characters**: follow [the steps for an over-long name](https://code.claude.com/docs/en/errors.md#mcp-tool-name-over-128-characters)
* **The server lists the tool for its own interface and not for Claude**: when maintaining the server, add `model` to the tool's `_meta.ui.visibility` to give Claude the tool. Otherwise, there's nothing to fix.

##### Tools from a server that is still connecting

When a request needs tools from a server that is still connecting in the background, Claude waits for that server before continuing. How the wait happens depends on the configuration:

* **With [tool search](#scale-with-mcp-tool-search), the default**: the wait happens inside the `ToolSearch` call.
* **Without tool search**: Claude uses the `WaitForMcpServers` tool instead. Configurations without tool search include `ENABLE_TOOL_SEARCH=false` and a model earlier than Claude Opus 4.5, Claude Sonnet 4.5, and Claude Haiku 4.5 on Google Cloud's Agent Platform. For an `ANTHROPIC_BASE_URL` gateway, see [Tool search through an LLM gateway](https://code.claude.com/docs/en/mcp#tool-search-through-a-gateway).

With tool search enabled, when a server finishes connecting while Claude is working, Claude Code lists the server's tool names to Claude on its next request in the same turn, so Claude can search for and call those tools without waiting for the user's next message.

After a session is resumed, Claude can call a tool from the saved conversation while the tool's MCP server is still connecting. While the server is on its first connection attempt, Claude Code holds the call for up to 10 seconds and runs it once the tool is available. If the server doesn't connect in time, or it is already [retrying after a failed attempt](#automatic-reconnection), the call fails with the `No such tool available` [tool error](https://code.claude.com/docs/en/errors.md#no-such-tool-available).

### Disable a server without removing it

To stop Claude Code from connecting to a server without losing its configuration, toggle the server off in the `/mcp` panel. Claude Code still lists the server in `/mcp`, marked as disabled.

Claude Code records each toggle per project in `~/.claude.json`, in one of two lists that cover disjoint sets of servers:

* `disabledMcpServers`: an opt-out list for user-configured servers, plugin servers, servers the organization [provides through managed settings](https://code.claude.com/docs/en/managed-mcp.md#provide-servers-through-managed-settings), the claude.ai connectors Claude Code [fetches itself](https://code.claude.com/docs/en/mcp#how-connectors-reach-claude-code), and built-in servers that default to on. Claude Code doesn't connect to a server listed here. When a claude.ai connector is disabled with the per-project `/mcp` toggle described in [Disable claude.ai connectors](https://code.claude.com/docs/en/mcp#disable-claude-ai-connectors), Claude Code writes it to this list under its display name, for example `claude.ai Slack`.
* `enabledMcpServers`: an opt-in list for built-in servers that default to off, such as `computer-use`. Claude Code connects to a default-off server only when it is listed here.

Claude Code consults exactly one of the two lists for each server, so neither list overrides the other. A regular server added to `enabledMcpServers`, or a default-off built-in server added to `disabledMcpServers`, is ignored.

`disabledMcpServers` and `enabledMcpServers` are unrelated to [`enabledMcpjsonServers`](https://code.claude.com/docs/en/settings-reference#enabledmcpjsonservers) and [`disabledMcpjsonServers`](https://code.claude.com/docs/en/settings-reference#disabledmcpjsonservers), which control approval of servers defined in a project's `.mcp.json` file.

### MCP client runtimes

Claude Code connects to MCP servers through one of two client runtimes. The v1 runtime is built on MCP TypeScript SDK 1.x. The v2 runtime is the same code on [MCP TypeScript SDK 2.0](https://ts.sdk.modelcontextprotocol.io/v2/), which adds MCP protocol revision 2026-07-28. The rest of this file applies to both runtimes, except where a section names the v2 runtime.

Claude Code picks a runtime at each start and keeps it until exit. In sessions where it [fetches feature flags](https://code.claude.com/docs/en/env-vars.md#features-that-need-feature-flag-fetching), it uses the v2 runtime on Claude Code v2.1.232 or later.

On v2, Claude Code also:

* Asks HTTP, stdio, and claude.ai connector servers whether they support the newer revision and uses it with those that do. That includes the connectors of cloud and [Remote Control](https://code.claude.com/docs/en/remote-control.md) sessions. Claude Code connects to every other server as v1 does.
* Receives `list_changed` notifications from servers on the newer revision over a [stream it holds open](#notification-streams-on-the-v2-runtime).
* Doesn't register a [channel](#push-messages-with-channels) server that connects on the newer revision, because that revision can't carry channel messages.
* Fails an [MCP OAuth sign-in](#authenticate-with-remote-mcp-servers) whose authorization response names an unexpected issuer.
* Sends [MCP OAuth](#authenticate-with-remote-mcp-servers) credentials only to a token endpoint served over HTTPS or at `localhost`, `127.0.0.1`, or `::1`. Sign-in fails for a server whose token endpoint is plain `http://` anywhere else, such as a device on the local network. See [Refusing to send credentials to non-https token endpoint](https://code.claude.com/docs/en/errors.md#refusing-to-send-credentials-to-non-https-token-endpoint).

Anthropic can keep a specific server on the earlier protocol, or off that stream, with a feature flag Claude Code fetches. To pick the runtime manually, set [`MCP_SDK_GENERATION`](https://code.claude.com/docs/en/env-vars) to `v1` or `v2`.

To decide whether Claude Code asks servers about the newer revision, set [`MCP_PROTOCOL_NEGOTIATION`](https://code.claude.com/docs/en/env-vars) to `auto` or `legacy`. With that variable unset, Claude Code can skip asking a stdio server for 7 days, for example after the server exits when asked. To have an upgraded server asked sooner, set `auto`.

### Dynamic tool updates

An MCP server can change the tools, prompts, or resources it offers while connected and send a `list_changed` notification. When one arrives:

* **In an interactive terminal session**, Claude Code fetches the updated list from that server, so the server doesn't need a reconnect.
* **In [non-interactive mode](https://code.claude.com/docs/en/headless.md) with the `-p` flag and in the [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md)**, Claude Code refreshes only the tool list on these notifications.

If a refresh request fails, Claude Code keeps the server's previously discovered tools, prompts, and resources until a later refresh succeeds.

#### Notification streams on the v2 runtime

On the [v2 runtime](#mcp-client-runtimes), Claude Code receives `list_changed` notifications from a server on the newer protocol revision over a stream it holds open. When the stream closes, Claude Code reopens it, with two limits:

* **The stream closes again within 10 seconds**: Claude Code reopens it up to three times, then stops for that connection.
* **The stream stays open longer than 10 seconds, then closes**, as streams to serverless hosts commonly do: after five reopens in an hour, Claude Code waits about six hours before the next one.

Until the stream reopens, the session keeps the server's last fetched tools, prompts, and resources. To pick up its changes sooner, reconnect the server from `/mcp`.

### Automatic reconnection

Claude Code reconnects a remote server that drops mid-session and retries an HTTP or SSE server's first connection after a transient error. For a stdio server, see [Stdio servers that exit or fail to start](#stdio-servers-that-exit-or-fail-to-start).

#### Mid-session drops of a remote server

Claude Code first tries to reconnect a dropped remote server up to five times with exponential backoff, starting at a one-second delay and doubling it each time:

* **In an interactive session**: `/mcp` shows the server as pending while Claude Code reconnects. After five failed attempts, Claude Code marks the server as failed, or as needing authentication when the server needs authorizing again. When it marks the server as failed, the user sees an `MCP server "<name>" disconnected · open /mcp to reconnect` notification. A manual retry is available from `/mcp`.
* **In [`claude -p`](https://code.claude.com/docs/en/headless) runs and [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) sessions**: Claude Code makes the same five attempts, with no `/mcp` panel to show them. If all five fail, the run continues without the server's tools:
  * **After a transient error, such as a 5xx response or a timeout**: Claude Code keeps retrying an HTTP or SSE server in the background. Retries last up to about half an hour, and the server's tools become available again when one connects. Until then, an Agent SDK session reports the [status](https://code.claude.com/docs/en/agent-sdk/mcp.md#error-handling) `failed`, and the application code can [reconnect the server](https://code.claude.com/docs/en/agent-sdk/mcp.md#error-handling). To reconnect it in `claude -p`, start the run again.
  * **When the server [needs a new sign-in](#authenticate-with-remote-mcp-servers)**: Claude Code stops retrying, and an Agent SDK session reports the server's status as `needs-auth`. Sign in with [`claude mcp login <name>`](#authenticate-from-the-command-line) in a shell. Then start the run again or, in an Agent SDK session, [reconnect the server](https://code.claude.com/docs/en/agent-sdk/mcp.md#error-handling) instead.

#### Failed first connections

When an HTTP or SSE server's first connection fails with a transient error, such as a 5xx response, a connection refused, or a timeout, Claude Code retries up to three times. If the connection still fails, Claude Code marks the server as failed.

Those retries don't apply in these cases:

* A stdio server's first connection. To try it again, see [Stdio servers that exit or fail to start](#stdio-servers-that-exit-or-fail-to-start)
* A WebSocket server's first connection. To try it again in an interactive terminal session, select **Reconnect** from the server's menu in `/mcp`
* An authentication or not-found error, because it requires a configuration change to resolve. When a [`headersHelper`](#use-dynamic-headers-for-custom-authentication) is the server's only source of the `Authorization` header, Claude Code retries an authentication error anyway, because it re-runs the helper on each attempt and can pick up a fresh credential

#### Stdio servers that exit or fail to start

To start a stdio server again, pick the row for how Claude Code runs (an interactive session, a `claude -p` run, or an Agent SDK session) and the column for what happened to the server.

| How you run Claude Code | The server's process exits mid-session | The server's first connection fails |
| - | - | - |
| Interactive session | Claude Code marks the server as failed. To start it again, select **Reconnect** from the server's menu in `/mcp` | Claude Code marks the server as failed. To start it again, select **Reconnect** from the server's menu in `/mcp` |
| `claude -p` run | Claude Code starts the server again the next time Claude calls one of the server's tools, and the call runs once the server connects | The run continues without the server's tools. To have Claude Code try the connection again, start the run again. When a plugin provides the server, new runs skip the connection for 15 minutes after a failure, so wait that long first or [retry sooner](https://code.claude.com/docs/en/errors.md#skipping-connection-recent-failure-cached) |
| Agent SDK session | Claude Code starts the server again the next time Claude calls one of the server's tools, and the call runs once the server connects | The session continues without the server's tools. Your code can [reconnect the server](https://code.claude.com/docs/en/agent-sdk/mcp.md#error-handling) |

#### Failed discovery requests

After a server connects, Claude Code sends it capability discovery requests such as `tools/list`, `prompts/list`, and `resources/list`. It retries those requests up to three times with short backoff after a transient network or server error. It doesn't retry authentication errors, 4xx responses, or request timeouts.

#### Retry failed servers yourself

To retry every server that failed or needs authentication, run `/mcp reconnect all` at the Claude Code prompt in an interactive terminal session. This requires Claude Code v2.1.284 or later. Earlier versions print `MCP server "all" not found`.

#### How Claude learns that a server failed

Whether Claude Code tells Claude about a configured server that failed to connect depends on [tool search](#scale-with-mcp-tool-search), which is on by default:

* With tool search, Claude Code tells Claude which server failed and its connection error, so Claude reports the connection failure in its response. Claude Code includes the same information in `ToolSearch` results that find no matching tool.
* In any [configuration without tool search](#configure-tool-search), Claude Code doesn't report failed server connections to Claude.

### Push messages with channels

An MCP server can also push messages directly into a session so Claude can react to external events such as CI results, monitoring alerts, or chat messages. To enable this, the server declares the `claude/channel` capability and the user opts it in with the `--channels` flag at startup. See [Channels](https://code.claude.com/docs/en/channels.md) to use an officially supported channel, or [Channels reference](https://code.claude.com/docs/en/channels-reference.md) to build one.

On the [v2 runtime](#mcp-client-runtimes), a channel server that negotiates MCP protocol revision 2026-07-28 can't deliver channel messages, so Claude Code doesn't register it as a channel. A channel server that doesn't support that revision connects on the earlier handshake and registers as before.

Claude Code asks stdio servers for that revision by default. To keep a stdio channel server on the earlier handshake, set [`MCP_PROTOCOL_NEGOTIATION`](https://code.claude.com/docs/en/env-vars) to `legacy`, which keeps every server on it.

> [!TIP]
>
> Tips:
>
> * Configure the MCP server startup timeout with the `MCP_TIMEOUT` environment variable (for example, `MCP_TIMEOUT=10000 claude` sets a 10-second timeout)
> * Set a per-server tool execution timeout by adding a `timeout` field in milliseconds to that server's `.mcp.json` entry, for example `"timeout": 600000` for ten minutes. This overrides the `MCP_TOOL_TIMEOUT` environment variable for that server only
> * Claude Code displays a warning when MCP tool output exceeds 10,000 tokens and limits output to 25,000 tokens by default. To change the token limit, set the `MAX_MCP_OUTPUT_TOKENS` environment variable, for example `MAX_MCP_OUTPUT_TOKENS=50000`. The warning threshold is fixed. Unless the server raises a tool's own limit, successful text results longer than 50,000 characters are saved to a file regardless of this variable. See [MCP output limits and warnings](#mcp-output-limits-and-warnings)
> * Use `/mcp` to authenticate with remote servers that require OAuth 2.0 authentication

### Time limits on MCP tool calls

To limit how long an MCP tool call can run:

* **Per server**: add a `timeout` field in milliseconds to that server's configuration entry
* **Across servers**: set [`MCP_TOOL_TIMEOUT`](https://code.claude.com/docs/en/env-vars)

The per-server `timeout` is a hard wall-clock limit per tool call, and progress notifications from the server don't extend it. Values below 1000 are ignored and fall through to `MCP_TOOL_TIMEOUT`, or to its default of about 28 hours when that variable is unset. An HTTP, SSE, or [claude.ai connector](https://code.claude.com/docs/en/mcp.md#use-mcp-servers-from-claude-ai) server also has a second, per-request timer that covers each request through to the server's first response byte. Claude Code sets that timer to the greatest of three values: 60 seconds, the tool timeout that applies to the server, and `MCP_TIMEOUT`. The 28-hour default of an unset `MCP_TOOL_TIMEOUT` doesn't enter that comparison, and a value below 60 seconds doesn't shorten the timer. Stdio and WebSocket servers have no per-request timer.

A per-server `timeout` of at least 1000 also acts as a floor on the idle timeout described below: Claude Code never aborts that server's tool calls for idleness sooner than the per-server `timeout`.

A tool call to an MCP server that sends no response and no progress notification for the idle window aborts with an error instead of waiting for the wall-clock limit. The idle timeout applies to every server type except IDE servers and SDK in-process servers. The idle window defaults to five minutes for HTTP, SSE, WebSocket, and [claude.ai connector](#use-mcp-servers-from-claudeai) servers, and to 30 minutes for stdio servers.

To change the idle window, set the [`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`](https://code.claude.com/docs/en/env-vars) environment variable in milliseconds; set it to `0` to disable the check.

These timeouts bound how long a call can run, not always how long it blocks the session: a main-conversation call that runs past two minutes moves to a background task first. See [Automatic backgrounding of long tool calls](#automatic-backgrounding-of-long-tool-calls).

### Automatic backgrounding of long tool calls

If a background call's detail view in [`/tasks`](https://code.claude.com/docs/en/commands#all-commands) shows `runs on the server; survives exiting this session`, the call is an MCP task: see [MCP tasks that run on the server](#mcp-tasks-that-run-on-the-server).

An MCP tool call in the main conversation that is still running after two minutes moves to a background task instead of blocking the session. Claude receives the task ID immediately and keeps working, and the result arrives as a task notification when the call settles.

The task appears in [`/tasks`](https://code.claude.com/docs/en/commands#all-commands), where it can also be stopped, and it doesn't survive exiting the session. The task's entry shows the latest progress the server has reported. Stopping the task makes Claude Code cancel the call and tell Claude that no result is coming. Stopping doesn't guarantee the server stops: it may already have done some of the work, or may still finish it.

The per-call limits still apply while the call runs in the background: the wall-clock limit set by the per-server `timeout` or [`MCP_TOOL_TIMEOUT`](https://code.claude.com/docs/en/env-vars), and the idle timeout set by [`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`](https://code.claude.com/docs/en/env-vars).

To change or turn off automatic backgrounding:

* Set the [`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`](https://code.claude.com/docs/en/env-vars) environment variable in milliseconds to change the threshold, or set it to `0` to turn automatic backgrounding off. With `0`, Claude also [waits for MCP tasks](#make-claude-wait-for-the-result-of-an-mcp-task) in an interactive session
* Set [`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`](https://code.claude.com/docs/en/env-vars) to `1` to turn off automatic backgrounding and [background commands](https://code.claude.com/docs/en/tools-reference.md#background-commands)

Some calls never move to the background:

* Calls from [subagents](https://code.claude.com/docs/en/sub-agents.md); Claude Code backgrounds only main-conversation calls
* Calls to IDE servers
* Calls in [non-interactive mode](https://code.claude.com/docs/en/headless.md), unless `CLAUDE_AUTO_BACKGROUND_TASKS` is set to `1`, since a one-shot run can end before the result arrives

A call waiting on an open [elicitation dialog](#respond-to-mcp-elicitation-requests) isn't backgrounded while the dialog is open: the server is blocked on the user's input, not slow, so Claude Code defers the move until the dialog closes.

### MCP tasks that run on the server

An MCP task is a long job, such as a report export or a build, that an MCP server runs itself using the [MCP tasks extension](https://modelcontextprotocol.io/extensions/tasks/overview). Claude's tool call returns once the server accepts the job, so Claude keeps working unless the user [makes Claude wait](#make-claude-wait-for-the-result-of-an-mcp-task). When the job ends, the transcript says so and Claude gets the result; the user asks Claude for it.

Meanwhile, the footer shows a count such as `1 MCP task`, and Claude Code follows the task by checking its status with the server. A task on a remote server keeps running after exit. To follow it again, [resume the same session](#exit-clear-or-resume-while-an-mcp-task-runs).

> [!NOTE]
>
> MCP tasks are in public beta in the Claude Code CLI and require Claude Code v2.1.304 or later. [What a call needs to become an MCP task](#what-a-call-needs-to-become-an-mcp-task) lists the sessions and servers that get them.

#### Stop an MCP task or get its result

To stop a running task, select it in [`/tasks`](https://code.claude.com/docs/en/commands#all-commands) and press `x`, or ask Claude to stop it. Claude Code stops following the task and asks the server to cancel it, though the server may still finish it. Reconnect a disconnected server from `/mcp` first; otherwise no cancel request goes out, and Claude Code forgets the task and can't follow it again. Pressing `Esc` doesn't stop a background task.

When the task ends, a line such as this one appears in the transcript:

```text theme={null}
MCP task <server task id> (<server>/<tool>) completed.
```

The result goes to Claude, not into the transcript, so the user asks Claude for it. If Claude is idle when the result arrives, Claude starts on it unprompted.

#### Answer a question from an MCP task

A running task can open an [elicitation dialog](#respond-to-mcp-elicitation-requests) to ask the user for input. While `/tasks` is open, the dialog stays hidden, so close `/tasks` to answer. Declining or pressing `Esc` is an answer to the server, which then decides whether the task goes on.

In a [non-interactive](https://code.claude.com/docs/en/headless.md) session, Claude Code asks the server to cancel a task that requests input, without running [`Elicitation` hooks](https://code.claude.com/docs/en/hooks#elicitation) or calling the Agent SDK's `onElicitation` callback.

#### Exit, clear, or resume while an MCP task runs

A task on a remote server keeps running after exit. A stdio server's process stops when Claude Code exits, though its tasks show `runs on the server; survives exiting this session` in `/tasks`. Unless that server's documentation says the work outlives the process, let those tasks finish or stop them in `/tasks` first.

| Situation | What happens to the task | What you can do |
| - | - | - |
| You run `/clear` or `/branch`, or `/resume` another session | While Claude Code stays open, the result arrives in your current conversation | After an exit, `claude --resume` the session the task started in |
| You exit Claude Code | No exit option cancels a remote server's task, even when the exit dialog lists it under `The following will stop when you exit:` | Stop it in `/tasks` first, or resume the same session later |
| You return to the task's session interactively: `claude --resume`, `claude --continue`, or `/resume` | Once the server connects, Claude Code follows the task again, and Claude gets the result if it finished meanwhile and the server still knows it | Keep the server's name and connection settings unchanged |
| You resume the task's session with `--resume` or `--continue` in a one-shot `claude -p "<prompt>"` run | That run doesn't follow the task | Resume interactively, or with `--input-format stream-json` |
| You start a new session or use `--fork-session` | The new session doesn't follow the task | Resume the session that started it |

#### What a call needs to become an MCP task

A tool call becomes an MCP task only when all of these conditions hold:

* The server supports tasks
* The server is an HTTP, stdio, or claude.ai connector server connected on [protocol revision 2026-07-28](#mcp-client-runtimes). Setting [`MCP_SDK_GENERATION=v1` or `MCP_PROTOCOL_NEGOTIATION=legacy`](https://code.claude.com/docs/en/env-vars) rules that out
* The session [fetches feature flags](https://code.claude.com/docs/en/env-vars.md#features-that-need-feature-flag-fetching), so not on a third-party provider such as Amazon Bedrock, and not with telemetry or flag fetching turned off
* Anthropic has turned MCP tasks on for that kind of session. On v2.1.304 or later that covers terminal CLI sessions, [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) sessions, and [GitHub Actions](https://code.claude.com/docs/en/github-actions.md) runs. Other surfaces, such as the [VS Code extension](https://code.claude.com/docs/en/vs-code.md) and the [desktop app](https://code.claude.com/docs/en/desktop.md), don't have MCP tasks
* The call comes from the main conversation, not from a [subagent](https://code.claude.com/docs/en/sub-agents.md)
* Either the session is interactive, or an [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) session or a `claude -p` run reading `--input-format stream-json` has:
  * [`CLAUDE_AUTO_BACKGROUND_TASKS`](https://code.claude.com/docs/en/env-vars) at `1`
  * `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND` not `1`
  * `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` not `0`

Any other call is a plain tool call, and [Automatic backgrounding of long tool calls](#automatic-backgrounding-of-long-tool-calls) says which of those move to the background.

Keep an Agent SDK or stream-json session's input open, because the run [doesn't wait for MCP tasks](https://code.claude.com/docs/en/headless.md#mcp-work-when-a-non-interactive-run-ends) after input closes. A one-shot `claude -p "<prompt>"` run doesn't get MCP tasks.

#### Status messages on an MCP task

These messages, in a task's `/tasks` entry or its closing transcript line, mean Claude Code can't reach the server or the task. While one shows in `/tasks`, the job may still be running: Claude Code leaves it alone and keeps checking. The `300s` and configuration messages stay on the entry even after contact returns.

| Message | What is happening | What you can do |
| - | - | - |
| `reconnecting…` | The server hasn't answered since a resume, or status checks get no answer | If it stays, reconnect from `/mcp` |
| `needs a sign-in to <server>` | The server refused a status check | Sign in from `/mcp` |
| `status requests come back with errors; retrying…` | The server, or a proxy in front of it, answers status checks with errors | Wait while Claude Code retries |
| `server '<name>' did not reconnect within 300s` | No answered check for five minutes, for example with the connection down or the server disabled | Reconnect from `/mcp` |
| `server '<name>' asked for a sign-in, and none was accepted within 300s` | After five minutes the server still wants a sign-in | Sign in from `/mcp` |
| `status requests to server '<name>' came back with errors, and none succeeded in 300s` | Five minutes of error answers | Check the server's own health or logs |
| `server '<name>' is not configured in this session; the task may still be running on it` | The session has no server by that name, for example it was removed, renamed, or left out of `--mcp-config`, or a claude.ai connector is still loading | Restore the server under the same name, then resume the session again. For a loading connector, nothing: Claude Code follows the task once it appears |
| A message beginning `server '<name>' was reconfigured to a different transport since this task was created` | A server by that name exists with connection settings that changed since the task started, such as its URL, command, args, env, headers, or timeout | Restore the earlier settings, then resume the session again |
| `the server rejected this task's id; asking again…` | The server says it doesn't know the task ID. Claude Code keeps asking for up to five minutes | Wait: the message clears if the server recognizes the ID again, or the `outcome unknown.` line follows |
| A transcript line ending `outcome unknown.`, in one form `expired on the server: outcome unknown.` | The server rejected the ID or refused with another permanent error, and Claude Code stopped following the task | A second call may repeat the work. Before calling the tool again, find out from the server what was done, for example by asking Claude to use the server's other tools |

#### Time limits on MCP tasks

By default, a task in the background has no Claude Code time limit. The [tool call time limits](#time-limits-on-mcp-tool-calls), including the wall-clock limit and the idle timeout, apply until the server answers the call with the task. When Claude is [made to wait](#make-claude-wait-for-the-result-of-an-mcp-task), they apply for the whole task. Answered status checks count as activity for the idle timeout.

#### Make Claude wait for the result of an MCP task

To make Claude wait for a task's result in an interactive session, set one of two environment variables, for example in the `env` block of [`settings.json`](https://code.claude.com/docs/en/settings):

* **[`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`](https://code.claude.com/docs/en/env-vars) set to `0`**: Claude waits for every MCP tool call until the call ends
* **[`CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND`](https://code.claude.com/docs/en/env-vars) set to `1`**: Claude waits for a task's result. While [automatic backgrounding](#automatic-backgrounding-of-long-tool-calls) is on, it moves the call after two minutes by default, so short tasks finish in place and long ones don't block the session. The moved call is a plain background call rather than an MCP task. It doesn't survive exiting the session

While Claude waits, pressing `Esc` or reaching the [wall-clock limit or idle timeout](#time-limits-on-mcp-tasks) ends the call, and Claude Code asks the server to cancel the task.

Setting `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` to `1` or starting in [bare mode](https://code.claude.com/docs/en/headless.md#start-faster-with-bare-mode) doesn't by itself make Claude wait for MCP tasks. This example sets `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` to `0`, so Claude waits for every MCP tool call:

```json settings.json theme={null}
{
  "env": {
    "CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS": "0"
  }
}
```

### MCP tasks for server authors

When building an MCP server, a long-running `tools/call` can be answered with a task. The [MCP tasks extension](https://modelcontextprotocol.io/extensions/tasks/overview) defines the messages the server sends. On a [protocol revision 2026-07-28](#mcp-client-runtimes) connection, each request carries Claude Code's client capabilities at `params._meta["io.modelcontextprotocol/clientCapabilities"]`, with `"io.modelcontextprotocol/tasks": {}` under `extensions`. A `tools/call` request that [can't become a task](#what-a-call-needs-to-become-an-mcp-task) omits that extension.

#### Answer the call with a task

Answer with a task only when the request carries the extension; otherwise the call fails with the tool error `Unsupported result type 'task' for tools/call`. The call fails the same way if the answer has no `taskId` or no valid `status`. The task object is the JSON-RPC `result` of the `tools/call` response and needs no `content` array. This example includes the optional `statusMessage` and `pollIntervalMs`:

```json theme={null}
{
  "resultType": "task",
  "taskId": "build-7f3a9c2e",
  "status": "working",
  "statusMessage": "Compiling, 40 of 212 files done",
  "createdAt": "2026-10-22T14:03:07Z",
  "lastUpdatedAt": "2026-10-22T14:03:07Z",
  "ttlMs": null,
  "pollIntervalMs": 5000
}
```

| Field | How Claude Code handles it |
| - | - |
| `resultType` | Set it to `"task"` to mark the reply as a task. Without it, Claude Code reads the reply as a plain result |
| `taskId` | Required. At most 128 printable ASCII characters with no spaces, or Claude gets a tool error beginning `MCP server "<name>" returned a malformed task handle for tool "<tool>"`. Keep the ID answerable across connections, because after a resume Claude Code asks about it on a new connection |
| `status` | Required. One of `working`, `input_required`, `completed`, `failed`, or `cancelled`. Another value gives the `Unsupported result type` error |
| `createdAt`, `lastUpdatedAt`, `ttlMs` | Required by the tasks extension, and `ttlMs` may be `null`. Claude Code doesn't drop a task because its `ttlMs` has passed |
| `pollIntervalMs` | Optional. Milliseconds between `tasks/get` requests, clamped to between 250 and 30000. Claude Code uses 2000 when the field is absent or `null`, and reads the value again from each `tasks/get` response |
| `statusMessage` | Optional. `/tasks` shows the value from your latest `tasks/get` response, not this first one, and a response that omits the field clears it. A [status message from Claude Code](#status-messages-on-an-mcp-task) can take its place |

Claude Code accepts a task answer that omits `createdAt`, `lastUpdatedAt`, or `ttlMs`, or that sets `pollIntervalMs` to `null`. Before v2.1.317, the call failed with the `Unsupported result type` error instead. To work with those versions too, send the three fields that the tasks extension requires, and send `pollIntervalMs` as a number or not at all.

On an HTTP or claude.ai connector server, the task answer has to start within the [per-request timer](#time-limits-on-mcp-tool-calls), so accept the job and answer first, then do the work.

#### Report status, results, and questions

Right after the task answer, Claude Code sends `tasks/get` with `{ "taskId": ... }`, then repeats it once per poll interval. The tasks extension requires the response to carry `"resultType": "complete"` along with `taskId`, `status`, `createdAt`, `lastUpdatedAt`, and `ttlMs`. `ttlMs` may be `null`, and `statusMessage` and `pollIntervalMs` are optional. This example reports the build as done:

```json theme={null}
{
  "resultType": "complete",
  "taskId": "build-7f3a9c2e",
  "status": "completed",
  "createdAt": "2026-10-22T14:03:07Z",
  "lastUpdatedAt": "2026-10-22T14:09:41Z",
  "ttlMs": null,
  "result": {
    "content": [{ "type": "text", "text": "Build succeeded: 212 files, 0 warnings" }]
  }
}
```

| Status, method, or response | How Claude Code handles it |
| - | - |
| `working` | Keeps polling |
| `completed` | Gives Claude the normal `tools/call` result in the top-level `result` object. `isError: true` in it is reported as a failure |
| `failed` | Tells Claude the `message` of the top-level `error` object `{ code, message, data }`, which the tasks extension requires on a failed task. Without that `message`, Claude gets `statusMessage` instead, or else `Task failed` |
| `cancelled` | Tells Claude `statusMessage`, or else `Task was cancelled by the server` |
| `input_required` | Reads `inputRequests`, an object that maps a key you choose to `{ method, params }`. Claude Code answers each key once through `tasks/update` with `{ taskId, inputResponses }`, where `inputResponses` maps the same key to that request's result. Keys beyond 16 per task are ignored |
| Methods in `inputRequests` | `elicitation/create` is served only in interactive terminal sessions, and `roots/list` everywhere. When Claude Code can't serve a request, it asks the server to cancel the task |
| Another `status` value | Claude Code asks the server to cancel the task and reports it to Claude as failed |
| JSON-RPC error `-32602` | Read as an unknown task ID. For a task in the background, Claude Code keeps asking for up to five minutes, then reports the outcome to Claude as unknown |
| `tasks/cancel` | Sent, for example, when Claude or the person stops the task while the server is connected. Not sent on exit |
| `tasks/result`, `tasks/list`, `notifications/tasks` | Not used, so put the outcome in your `tasks/get` responses |

### Plugin-provided MCP servers

[Plugins](https://code.claude.com/docs/en/plugins/overview.md) can bundle MCP servers that provide tools and integrations when the plugin is enabled.

**How plugin MCP servers work**:

* A plugin defines MCP servers in `.mcp.json` at the plugin root or inline in `plugin.json`
* When a plugin is enabled, Claude Code starts its MCP servers automatically
* Claude Code offers plugin MCP tools alongside manually configured MCP tools
* Plugin servers are added and removed by installing or uninstalling the plugin, not with `/mcp` commands. An installed plugin server can still be [toggled off](#disable-a-server-without-removing-it) in `/mcp`, which stops Claude Code from connecting to it without removing the plugin

**Example plugin MCP configuration**:

In `.mcp.json` at the plugin root:

```json theme={null}
{
  "mcpServers": {
    "database-tools": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_URL": "${DB_URL}"
      }
    }
  }
}
```

Or inline in `plugin.json`:

```json theme={null}
{
  "name": "my-plugin",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}
```

**Plugin MCP features**:

* **Automatic lifecycle**: servers connect and disconnect at these points:
  * At session startup, Claude Code connects the servers for enabled plugins automatically. In `/mcp`, a remote (HTTP or SSE) plugin server used before can show the [`cached` status](#server-status-detail) instead; Claude Code connects it when Claude first calls one of its tools. When a stdio plugin server's connection failed less than 15 minutes earlier, Claude Code [skips the connection](https://code.claude.com/docs/en/errors.md#skipping-connection-recent-failure-cached)
  * When a plugin is enabled or disabled during a session, Claude Code connects or disconnects its MCP servers when the change applies. [Apply plugin changes without restarting](https://code.claude.com/docs/en/plugins/cli-reference.md#reload-plugins) describes when that is. In a session without an interactive terminal, `/reload-plugins` doesn't connect or disconnect plugin MCP servers; those changes take effect in the next session
  * On a reload, Claude Code keeps the live connections of plugin servers whose configuration is unchanged, and does the same when the Agent SDK [replaces the session's MCP server list](https://code.claude.com/docs/en/agent-sdk/typescript.md#mcpsetserversresult) without naming them
  * When the session is [moved with `/cd`](https://code.claude.com/docs/en/permissions#move-the-session-to-another-directory) on v2.1.246 or later, Claude Code connects the servers of plugins the new directory's settings enable and disconnects the servers of plugins that are no longer enabled, so `/reload-plugins` isn't needed after the move
  * In [cloud sessions](https://code.claude.com/docs/en/claude-code-on-the-web.md), an MCP call to a plugin server that isn't connected yet, such as right after an idle session wakes, starts the server on demand and waits for it to connect
* **Path placeholders**: `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's installation directory, `${CLAUDE_PLUGIN_DATA}` to its [persistent state](https://code.claude.com/docs/en/plugins/components.md#path-variables-and-persistent-data) directory, and `${CLAUDE_PROJECT_DIR}` to the stable project root. Substitution applies to:
  * `stdio` servers: `command`, `args`, `env`
  * `http`, `sse`, and `ws` servers: `url`, `headers`, and `headersHelper`
* **User environment access**: plugin servers access the same environment variables as manually configured servers
* **Multiple transport types**: stdio, SSE, HTTP, and WebSocket transports are supported, though transport support may vary by server

Plugin servers appear in `/mcp` with indicators showing they come from plugins.

`claude mcp get` hides the values configured for a plugin's stdio or WebSocket server, because they can carry credentials:

* **stdio server**: it prints `Command: stdio`, an empty `Args:` line, and each environment variable as `NAME=[REDACTED]`
* **WebSocket server**: it prints `URL: ws` and each header as `<name>: [REDACTED]`, and `claude mcp list` shows `ws` in place of the URL

To see what the plugin configured, [find the plugin on disk](https://code.claude.com/docs/en/plugins/loading.md#find-plugins-on-disk) and read its `.mcp.json` or `plugin.json`.

**Plugin MCP tool names**:

Tools from a plugin-bundled MCP server include both the plugin name and the server key in their callable name. The full form is `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`, where any character outside `A-Z`, `a-z`, `0-9`, `_`, and `-` is replaced with `_`. For the `database-tools` server bundled in a plugin named `my-plugin`, a `query` tool is callable as:

```
mcp__plugin_my-plugin_database-tools__query
```

Use this full name when referencing the tool in [permission rules](https://code.claude.com/docs/en/permissions.md), a skill's `allowed-tools` list, a [subagent's `tools` field](https://code.claude.com/docs/en/sub-agents#available-tools), or a [hook matcher](https://code.claude.com/docs/en/hooks.md#match-mcp-tools). A hook matcher written against the bare server key, such as `mcp__database-tools__.*`, never fires for a plugin-bundled server.

The server itself registers under the scoped name `plugin:<plugin-name>:<server-name>`, such as `plugin:my-plugin:database-tools`. Use that name where a configured server name is expected, such as an [`mcp_tool` hook's `server` field](https://code.claude.com/docs/en/hooks#mcp-tool-hook-fields).

For details on bundling MCP servers with plugins, read the [plugin components reference](https://code.claude.com/docs/en/plugins/components.md#mcp-servers).

## MCP installation scopes

An MCP server can be configured at three scopes. The scope controls which projects the server loads in and whether the configuration is shared with a team. Administrators can also deploy or provide servers for every user through [managed configuration](#managed-mcp-configuration).

| Scope | Loads in | Shared with team | Stored in |
| - | - | - | - |
| [Local](https://code.claude.com/docs/en/mcp#local-scope) | Current project only | No | `~/.claude.json` |
| [Project](https://code.claude.com/docs/en/mcp#project-scope) | Current project only | Yes, via version control | `.mcp.json` in project root |
| [User](https://code.claude.com/docs/en/mcp#user-scope) | All your projects | No | `~/.claude.json` |

### Scope hierarchy and precedence

When the same server is defined in more than one place, Claude Code connects to it once, using the definition from the highest-precedence source in this order. It uses the entire server entry from that source; fields are not merged across scopes.

1. Local scope
2. Project scope
3. User scope
4. [Plugin-provided servers](https://code.claude.com/docs/en/plugins/components.md#mcp-servers)
5. [claude.ai connectors](#use-mcp-servers-from-claudeai)

Claude Code matches duplicates across the three scopes by name. It matches plugins and connectors by endpoint, so a plugin server or connector that points at the same URL or command as an enabled server above it counts as a duplicate.

Two URL spellings count as the same endpoint when they differ only in the letter case of the scheme or host, the scheme's default port, such as `:443` on `https`, or a trailing slash. A different path, query string, userinfo, or non-default port makes two servers.

A server the organization provides through the [`managedMcpServers`](https://code.claude.com/docs/en/managed-mcp#provide-servers-through-managed-settings) managed setting ranks above all of these, so when one of them duplicates it, Claude Code connects the organization's definition. Requires Claude Code v2.1.259 or later.

### Environment variable expansion in `.mcp.json`

Claude Code expands environment variables in `.mcp.json` files, so a team can share one configuration while machine-specific paths and sensitive values such as API keys stay out of it.

Reference an environment variable in a server's `command`, `args`, `env`, `url`, or `headers` value, in either of two forms:

* `${VAR}`: expands to the value of environment variable `VAR`
* `${VAR:-default}`: expands to the value of `VAR` if `VAR` is set, or to `default` if it is unset

#### Example with variable expansion

In this server entry, the URL is the value of `API_BASE_URL` followed by `/mcp`, with `https://api.example.com` as the default, and the API key comes from `API_KEY`:

```json theme={null}
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

#### Unset variables without a default

If a referenced environment variable isn't set and has no default value, the config still loads: Claude Code reports a missing-variable warning for that server in `claude mcp list` output and uses the unexpanded `${VAR}` text as-is. Set the variable or add a `:-default` fallback so the server starts with the intended value. In a remote server's `url` and `headers`, some credential variables [read as empty](#credential-variables-that-read-as-empty) instead, with no warning.

#### Variables set to an empty string

A variable set to an empty string counts as set, so a `${VAR:-default}` reference expands to the empty string, not to `default`. With the [example server](#example-with-variable-expansion), setting `API_BASE_URL` to an empty string makes its `url` `/mcp`, and `claude mcp list` reports `'url' is not a valid URL`. To use the default, unset the variable instead of setting it to an empty string.

#### Credential variables that read as empty

In a remote server's `url` and `headers`, Claude Code reads credential variables from the user's environment as empty instead of expanding them. This keeps a project's `.mcp.json` or a plugin from sending the user's Claude Code or cloud provider credentials to a server it names. For `Bearer ${ANTHROPIC_AUTH_TOKEN}`, the server receives `Bearer ` with no credential and rejects the request, usually with a `401`. Claude Code reports that as a failed connection.

The covered names are:

* Claude Code's own credentials, such as `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN`
* The cloud provider's credentials, such as `AWS_BEARER_TOKEN_BEDROCK`
* Other credentials the environment carries, such as `HTTPS_PROXY` and `NPM_TOKEN`

A covered name reads as empty whether or not the variable is set, and a `:-default` fallback on it is ignored. A provider base URL such as `ANTHROPIC_BASE_URL` still expands, so `"url": "${ANTHROPIC_BASE_URL}/mcp"` works, unless the URL's value itself embeds a credential such as a username and password.

A name outside this set, such as `API_KEY`, expands as written. To give the server one of the covered credentials, copy it into a variable with a different name and reference that name instead.

When a remote server's `url` or `headers` references a covered variable that is set, Claude Code names it in a debug-log line. To read the line, run `claude --debug-file /tmp/claude-debug.log` and search that file for `never expanded toward a remote server`.

#### How references appear in `/mcp` and CLI output

For a server in the local, project, or user [scope](#mcp-installation-scopes), the following surfaces show a `${VAR}` reference by name instead of as its resolved value:

* The URL or command line in a server's `/mcp` detail view
* `claude mcp list` and `claude mcp get` output

The `/mcp` detail view shows references this way in Claude Code v2.1.268 or later.

For what `claude mcp list`, `claude mcp get`, and `/mcp` show when a connection fails, see [Server status detail](#server-status-detail).

## Authenticate with remote MCP servers

Many cloud-based MCP servers require authentication. Claude Code supports OAuth 2.0 for secure connections.

Claude Code marks a remote server as needing authentication when the server responds with `401 Unauthorized` or `403 Forbidden`. What Claude Code shows depends on the server:

* For a server the user hasn't signed in to, either status code flags it in `/mcp` so the user can complete the OAuth flow.
* For a server whose `Authorization` header is configured, in `headers` or through a [`headersHelper`](#use-dynamic-headers-for-custom-authentication), a `401` or `403` while connecting doesn't flag the server, because the credential to fix is the configured one. Claude Code reports the connection as failed instead. If that header comes from a `${VAR}` reference, check whether that variable is one Claude Code [reads as empty](#credential-variables-that-read-as-empty).

When an OAuth server the user already signed in to rejects the stored token with `401 Unauthorized`, Claude Code reconnects with or without a new token:

* **The stored login has a refresh token**: it refreshes the token, reconnects, and retries the request once. The server is flagged in `/mcp` only if that retry also fails.
* **The stored login has no refresh token**: it connects once without the token. If the server answers, its tools work while signed out, and the rejected token is deleted. If the server rejects that connection too, `/mcp` shows that the server needs authentication.

In a `claude -p` or Agent SDK run on macOS, a request that Claude Code sent while it couldn't read the stored token fails with a [stored-credentials error](https://code.claude.com/docs/en/errors.md#couldnt-read-the-stored-credentials-for-mcp-server).

When the server rejects the stored refresh token, Claude Code immediately shows a notice pointing at `/mcp`. Open `/mcp` and select **Re-authenticate** on the server to sign in again before the next tool call fails.

A custom server that returns a `WWW-Authenticate` header pointing to its authorization server gets the same automatic discovery as any other remote server.

Claude Code also shows a startup notice when one or more configured servers need authentication, so `/mcp` doesn't have to be opened to discover which servers need sign-in. The notice counts only servers that can be signed in to from Claude Code. Before v2.1.218, it also counted [claude.ai connectors](#use-mcp-servers-from-claudeai) that weren't connected in claude.ai, which can be connected only from claude.ai settings.

The notice announces each server once and leaves it out of the count at later launches until that server has connected and needs sign-in again. `/mcp` still lists every server that needs sign-in.

A `claude -p` or Agent SDK run has no `/mcp` panel, so Claude Code can't run the OAuth flow there. To use a server that needs authentication, complete the sign-in from an interactive session first: run `/mcp` in the session, or `claude mcp login <name>` in a shell. When a configured server needs authentication during a `claude -p` or Agent SDK run with [tool search](#scale-with-mcp-tool-search) enabled, Claude Code tells Claude that the server's tools are unavailable until the user authorizes it.

If `headers.Authorization` is configured for the server and the server rejects that header, Claude Code reports the connection as failed instead of falling back to OAuth. Check that the token is valid for the MCP endpoint, or remove the header to use the OAuth flow.

**Sign in with the /mcp command within Claude Code**

In Claude Code, run the command:

```text wrap theme={null}
/mcp
```

Then follow the steps in the browser to log in.

> [!TIP]
>
> Tips:
>
> * Authentication tokens are stored securely and refreshed automatically
> * Use "Clear authentication" in the `/mcp` menu to revoke access
> * If the browser doesn't open automatically, copy the provided URL and open it manually
> * If the browser redirect fails with a connection error after authenticating, paste the full callback URL from the browser's address bar into the URL prompt that appears in Claude Code
> * OAuth authentication works with HTTP servers

### Authenticate from the command line

`claude mcp login <name>` runs a configured server's OAuth flow directly from the shell, without opening the `/mcp` panel inside a session. For a claude.ai connector, follow [Authorize a connector again from your shell](https://code.claude.com/docs/en/remote-control.md#authorize-a-connector-again-from-your-shell) instead.

```bash theme={null}
claude mcp login sentry
```

To clear stored credentials later, run `claude mcp logout <name>`.

`claude mcp login` detects when no local browser is available, such as during an SSH session or on Linux without a display server, and prints the authorization URL instead of trying to open a browser. Open the URL on the local machine, then paste the full redirect URL from the browser's address bar back at the prompt. The command needs an interactive terminal for the paste step, so connect with `ssh -t`. Pass `--no-browser` to force the URL prompt even when a local browser is detected.

```bash theme={null}
claude mcp login sentry --no-browser
```

### Use a fixed OAuth callback port

Some MCP servers require a specific redirect URI registered in advance. By default, Claude Code picks a random available port for the OAuth callback. Use `--callback-port` to fix the port so it matches a pre-registered redirect URI of the form `http://localhost:PORT/callback`. If sign-in on Claude Code v2.1.229 fails with a redirect URI mismatch, read the version note under [Use pre-configured OAuth credentials](https://code.claude.com/docs/en/mcp#use-pre-configured-oauth-credentials).

Use `--callback-port` on its own (with dynamic client registration) or together with `--client-id` (with pre-configured credentials).

**Authenticate in Claude Code**

Run `/mcp` in Claude Code and follow the browser login flow.

> [!TIP]
>
> Tips:
>
> * The client secret is stored securely in the system keychain (macOS) or a credentials file, not in the config
> * The client secret can be set only when the server is added. When authenticating with `claude mcp login` or from `/mcp`, Claude Code uses the stored secret and doesn't prompt for one or read `MCP_CLIENT_SECRET`
> * To add or change the secret later, remove the server with `claude mcp remove <name>`, then add it again with `--client-secret` and the same `--scope`
> * If the server uses a public OAuth client with no secret, use only `--client-id` without `--client-secret`
> * These flags only apply to HTTP and SSE transports. They have no effect on stdio servers
> * Use `claude mcp get <name>` to verify that OAuth credentials are configured for a server

### Override OAuth metadata discovery

To bypass the default discovery chain, point Claude Code at a specific OAuth authorization server metadata URL. Set `authServerMetadataUrl` when the MCP server's standard endpoints error, or to route discovery through an internal proxy. By default, Claude Code first checks RFC 9728 Protected Resource Metadata at `/.well-known/oauth-protected-resource`, then falls back to RFC 8414 authorization server metadata at `/.well-known/oauth-authorization-server`.

Set `authServerMetadataUrl` in the `oauth` object of the server's config in `.mcp.json`:

```json theme={null}
{
  "mcpServers": {
    "my-server": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "oauth": {
        "authServerMetadataUrl": "https://auth.example.com/.well-known/openid-configuration"
      }
    }
  }
}
```

The URL must use `https://`. The metadata URL's `scopes_supported` overrides the scopes the upstream server advertises.

### Restrict OAuth scopes

Set `oauth.scopes` to pin the scopes Claude Code requests during the authorization flow. This is the supported way to restrict an MCP server to a security-team-approved subset when the upstream authorization server advertises more scopes than should be granted. The value is a single space-separated string, matching the `scope` parameter format in RFC 6749 §3.3.

```json theme={null}
{
  "mcpServers": {
    "slack": {
      "type": "http",
      "url": "https://mcp.slack.com/mcp",
      "oauth": {
        "scopes": "channels:read chat:write search:read"
      }
    }
  }
}
```

`oauth.scopes` takes precedence over both `authServerMetadataUrl` and the scopes the server discovers at `/.well-known`. Leave it unset to let the MCP server determine the requested scope set.

When `oauth.scopes` isn't set, Claude Code doesn't request the full `scopes_supported` catalog from automatically discovered authorization server metadata. Metadata fetched from a configured `authServerMetadataUrl` still supplies its `scopes_supported` as the requested scopes.

If the authorization server advertises `offline_access` in `scopes_supported`, Claude Code appends it to the pinned scopes so the access token can be refreshed without a new browser sign-in.

If the server later returns a 403 `insufficient_scope` for a tool call, the call fails with a [`needs additional permissions`](https://code.claude.com/docs/en/errors#mcp-server-needs-you-to-sign-in-again) message that names the scope the server asks for, and the server shows as needing authentication in `/mcp`.

If that scope isn't in the pinned `oauth.scopes`, add it, then run `/mcp` and authenticate the server again. Claude Code requests the pinned scopes, not the scope the server named, so authenticating again without adding it yields a token that still lacks it.

### Use OAuth with a server behind an authenticating proxy

When an MCP server uses OAuth behind a proxy or gateway that checks a header of its own, sign-in fails if the OAuth requests arrive without that header. Signing in through the proxy requires Claude Code v2.1.299 or later, with the header and the sign-in both configured:

* **The proxy's header**: pass it with [`--header`](#option-1-add-a-remote-http-server), the `headers` field, or a [`headersHelper`](#use-dynamic-headers-for-custom-authentication), under the name the proxy reads
* **The OAuth sign-in**: keep `Authorization` out of the configured headers, then sign in with `claude mcp login <name>` in a shell. If an `Authorization` header is configured, Claude Code uses it as the server's credential and doesn't fall back to OAuth for that server.

### Use dynamic headers for custom authentication

When authentication such as Kerberos, short-lived tokens, or internal SSO needs headers generated at connection time, set the server's `headersHelper` to a command. Claude Code runs it when connecting and merges its output into the headers it sends. This example uses a script:

```json theme={null}
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com",
      "headersHelper": "/opt/bin/get-mcp-auth-headers.sh"
    }
  }
}
```

The command can also be inline:

```json theme={null}
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com",
      "headersHelper": "echo '{\"Authorization\": \"Bearer '\"$(get-token)\"'\"}'"
    }
  }
}
```

**Requirements:**

* The command must write a JSON object of string key-value pairs to stdout
* Claude Code runs the command in a shell and gives up on it after 10 seconds
* Claude Code picks the command's working directory by [where the server is configured](#where-the-helper-runs), so give the script as an absolute path or put it on `PATH`
* Dynamic headers override any static `headers` with the same name

Claude Code runs the helper fresh on each connection, at session start and on reconnect, once the [trust rule for project and local-scope servers](#trust-a-folder-before-its-headershelper-runs) lets it run. It doesn't cache the result, so the script is responsible for any token reuse.

If a tool call returns `401 Unauthorized` or `403 Forbidden`, Claude Code automatically re-runs the helper under the same rule, reconnects with the fresh headers, and retries the call once. It marks the server as needing authentication in `/mcp` only if that retry also fails.

When the helper's output includes an `Authorization` header, Claude Code uses that credential as the server's authentication and doesn't fall back to OAuth for the server.

If the server rejects the helper's credential while connecting, Claude Code reports the connection as failed instead of marking the server as needing authentication. Fix the credential the helper returns, then reconnect from `/mcp` to re-run the helper.

Claude Code sets these environment variables when executing the helper:

| Variable | Value |
| :- | :- |
| `CLAUDE_CODE_MCP_SERVER_NAME` | the name of the MCP server |
| `CLAUDE_CODE_MCP_SERVER_URL` | the URL of the MCP server |
| `CLAUDE_PLUGIN_ROOT` | the plugin's root directory. Set only when a [plugin](https://code.claude.com/docs/en/plugins/components.md#mcp-servers) provides the server |

Use these to write a single helper script that serves multiple MCP servers.

A plugin-provided `headersHelper` can't reference the plugin's [`${user_config.*}`](https://code.claude.com/docs/en/plugins/manifest-reference#user-configuration) values, because the command runs through a shell. Claude Code reports the server as misconfigured with an [error](https://code.claude.com/docs/en/errors.md#plugin-command-references-user-config) and doesn't substitute the value. Put `${user_config.KEY}` in the server's `headers` field instead, which isn't shell-parsed, or have the helper script read the value from a config file. Before v2.1.207, `headersHelper` substituted `${user_config.*}` values.

#### Where the helper runs

Claude Code picks the `headersHelper` command's working directory from the configuration that declares the server. A `cd` that Claude runs in Bash doesn't move it, and [`/cd`](https://code.claude.com/docs/en/permissions#move-the-session-to-another-directory) moves it only for servers that run from the session's primary working directory. Each row gives the directory that a relative path in the `headersHelper` command resolves against.

| Where you configured the server | Working directory |
| :- | :- |
| A [plugin](https://code.claude.com/docs/en/plugins/components.md#mcp-servers) | The plugin's root directory |
| A project `.mcp.json` or a [local-scope](https://code.claude.com/docs/en/mcp#local-scope) server | The project directory the server is declared in |
| An agent file in your project, a server from the SDK's `mcpServers` option or `setMcpServers()` method, or [`--mcp-config`](https://code.claude.com/docs/en/cli-reference) | The session's [primary working directory](https://code.claude.com/docs/en/permissions.md#working-directories) |
| [User scope](https://code.claude.com/docs/en/mcp#user-scope), [managed MCP](https://code.claude.com/docs/en/managed-mcp.md), a [claude.ai connector](#use-mcp-servers-from-claudeai), or an agent file from outside your project, including one from an `--add-dir` directory | Your configuration directory, `~/.claude` unless you set [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars) |

Before v2.1.238, Claude Code also ran the helpers of user-scope, managed, and claude.ai connector servers, and of agent files from outside the project, from the directory Claude Code was started in.

#### Which variables a helper can read

A `headersHelper` that a repository or plugin supplies is a command the user didn't write, so Claude Code runs it without the credential variables from the user's environment, such as `ANTHROPIC_API_KEY`. Where the server is configured decides whether this applies:

* **Removed**: a server in a project `.mcp.json` or in a plugin, and an inline server in an agent file from the project or from an `--add-dir` directory
* **Not removed**: a server at [user](https://code.claude.com/docs/en/mcp#user-scope) or [local scope](https://code.claude.com/docs/en/mcp#local-scope), in [managed MCP](https://code.claude.com/docs/en/managed-mcp.md), from a [claude.ai connector](#use-mcp-servers-from-claudeai), or supplied by the SDK or [`--mcp-config`](https://code.claude.com/docs/en/cli-reference), and an inline server in an agent file from `~/.claude/agents/`, from managed settings, or passed with `--agents`

Apart from Git's `GIT_CONFIG_KEY_<n>` variables, Claude Code removes every environment variable whose name looks like a credential, such as a name with `TOKEN`, `SECRET`, `PASSWORD`, `KEY`, or `AUTH` in it in either letter case, so `ANTHROPIC_API_KEY` and `MY_REGISTRY_TOKEN` are both removed. It also removes a fixed list of credential variables whose names don't follow that pattern, such as `ANTHROPIC_CUSTOM_HEADERS`.

When this applies to a helper, have the script read its credential from a file or a credential store. If the server's `url` [carries the live value of one of these variables](#environment-variable-expansion-in-mcpjson), such as `MY_REGISTRY_TOKEN`, the `CLAUDE_CODE_MCP_SERVER_URL` value the helper receives has that part replaced with `REDACTED` as well.

#### Trust a folder before its headersHelper runs

Claude Code executes a `headersHelper` as an arbitrary shell command. For a server in a project `.mcp.json` or at [local scope](https://code.claude.com/docs/en/mcp#local-scope), it runs the helper only after the user accepts the [trust dialog](https://code.claude.com/docs/en/permissions.md#project-allow-rules-and-workspace-trust) for the project directory the server is declared in. Before v2.1.238, a `claude -p` or SDK session ran these helpers without checking trust, and an interactive session ran them once a parent folder was trusted.

* **Trust that doesn't count**: a parent folder's trust, and the automatic trust a `claude -p` or SDK session gets for [hooks in settings files](https://code.claude.com/docs/en/permissions.md#what-runs-before-you-trust-a-folder)
* **Until the folder is trusted**: Claude Code connects the server with its static `headers` alone. In a `claude -p` or SDK session it also prints one [`headersHelper not run`](https://code.claude.com/docs/en/errors#headershelper-not-run) line per server to stderr, saying how to grant the trust.
* **Trust without a dialog**: set `projects["<path>"].hasTrustDialogAccepted` to `true` in `~/.claude.json`. `<path>` is the folder [Project allow rules and workspace trust](https://code.claude.com/docs/en/permissions.md#project-allow-rules-and-workspace-trust) says Claude Code keys the trust on.

Claude Code applies the same rule to a server declared inline in an [agent file](https://code.claude.com/docs/en/sub-agents.md#scope-mcp-servers-to-a-subagent), checking where that agent file came from: the project, for a file in its `.claude/agents/` directory, or an `--add-dir` directory. Until [that project or directory itself is trusted](https://code.claude.com/docs/en/permissions.md#what-runs-before-you-trust-a-folder), Claude Code doesn't load the server at all, so its helper never runs either.

### Sign in to an MCP server behind a gateway that requires a header

OAuth sign-in to an MCP server fails when a gateway requires a header, such as `X-API-Key`, and Claude Code doesn't send it. To have Claude Code send that header, add it to the server's configuration and use Claude Code v2.1.299 or later:

* **A server whose [configuration](#mcp-installation-scopes) the user can edit**: set it in [`headers`](#example-with-variable-expansion) or return it from a [`headersHelper`](#use-dynamic-headers-for-custom-authentication)
* **A server that [managed MCP](https://code.claude.com/docs/en/managed-mcp.md) or a [plugin](#plugin-provided-mcp-servers) supplies**: tell the user to ask the administrator or the plugin's author to add the header to the server's entry

Claude Code then adds the configured headers except `Authorization` to the sign-in, token refresh, and token revocation requests it sends to the server's origin. The server's origin is the scheme, host, and port in its `url`. A gateway that requires the header can still stop sign-in at the authorization page or at an authorization server on another origin:

* **The authorization page**: the user signs in on this page in the browser, which doesn't send the configured headers. If the browser gets the gateway's error instead of the page, tell the user to ask whoever runs the gateway to let the page through without the header.
* **An authorization server on another origin**: if a gateway in front of that server requires the header too, sign-in fails there. Tell the user to ask whoever runs that gateway to let OAuth requests through without the header.

## Use MCP servers from claude.ai

When Claude Code is logged in with a [claude.ai](https://claude.ai) account, MCP servers added in claude.ai, known as [connectors](https://claude.com/docs/connectors), are automatically available in Claude Code:

A server added in Claude Code takes [precedence](#scope-hierarchy-and-precedence) over a claude.ai connector that points at the same URL. In that case, `/mcp` lists the connector as hidden and shows how to remove the duplicate if the connector is preferred.

Some Anthropic-hosted connectors, such as Microsoft 365, Gmail, and Google Calendar, don't support local OAuth from Claude Code, because the upstream identity provider only accepts the redirect URL that claude.ai registered. When a server added with `claude mcp add` or in `.mcp.json` points at one of these hosts and the user signs in to it from `/mcp` or with `claude mcp login`, Claude Code shows [`is Anthropic-hosted and doesn't support local OAuth`](https://code.claude.com/docs/en/errors#anthropic-hosted-and-doesnt-support-local-oauth), directing the user to connect the service at [claude.ai/customize/connectors](https://claude.ai/customize/connectors) instead.

After the entry is removed with `claude mcp remove <name>` and the service is connected on claude.ai, the connector appears in Claude Code automatically.

## MCP output limits and warnings

When MCP tools produce large outputs, Claude Code limits their token usage so they don't overwhelm the conversation context:

* **Output warning threshold**: Claude Code displays a warning when any MCP tool output exceeds 10,000 tokens
* **Configurable limit**: the `MAX_MCP_OUTPUT_TOKENS` environment variable sets the maximum allowed MCP output tokens
* **Default limit**: the default maximum is 25,000 tokens
* **Scope**: the environment variable applies to tools that don't declare their own limit. Tools that set [`anthropic/maxResultSizeChars`](#raise-the-limit-for-a-specific-tool) use that value instead for text content, regardless of what `MAX_MCP_OUTPUT_TOKENS` is set to. Tools that return image data are still subject to `MAX_MCP_OUTPUT_TOKENS`
* **Over the limit**: when a successful result with no image content exceeds the token limit, Claude Code saves it to a file and replaces it in the conversation with a message that names the file path, so Claude reads the file when it needs the content. The file goes in the session's `tool-results` directory under [`~/.claude/projects/`](https://code.claude.com/docs/en/claude-directory#cleaned-up-automatically).
* **Response size from HTTP and SSE servers**: when a response from an [HTTP](#option-1-add-a-remote-http-server) or [SSE](#option-2-add-a-remote-sse-server) server passes 16 MiB, Claude Code stops reading it and the request fails. The limit applies after decompression to one JSON response body or one event of an event stream. When maintaining the server, return less data per response to stay under the limit, for example by paginating results
* **Message size from WebSocket servers**: when a [WebSocket](#option-4-add-a-remote-websocket-server) server sends one message over 16 MiB, Claude Code [closes the connection](#mid-session-drops-of-a-remote-server), and calls in progress on that server fail. When maintaining the server, return less data per message to stay under the limit

A call that Claude Code has [moved to a background task](#automatic-backgrounding-of-long-tool-calls) reports its result through the task notification. Two more limits apply to a call that completes in the foreground:

* **Character limit for text results**: for a tool that doesn't declare [`anthropic/maxResultSizeChars`](#raise-the-limit-for-a-specific-tool), Claude Code saves a successful result with no image content to a file once it's longer than 50,000 characters, whatever its token count. Setting `MAX_MCP_OUTPUT_TOKENS` doesn't change this threshold
* **Error results**: when a tool returns a result marked `isError: true`, Claude receives the result's text as the tool's error message. Error text longer than about 11,000 characters keeps only its first 5,000 and last 5,000 characters, with a marker between them that says how many characters were removed

To change the token limit, set `MAX_MCP_OUTPUT_TOKENS` in the shell before starting Claude Code:

```bash theme={null}
export MAX_MCP_OUTPUT_TOKENS=50000
claude
```

### Raise the limit for a specific tool

When building an MCP server, let an individual tool return results larger than the default persist-to-disk threshold of 50,000 characters by setting `_meta["anthropic/maxResultSizeChars"]` in the tool's `tools/list` response entry. Claude Code raises that tool's threshold to the annotated value, up to a hard ceiling of 500,000 characters.

Use it for tools that return inherently large but necessary outputs, such as database schemas or full file trees. Without the annotation, successful results that exceed the default threshold are persisted to disk and replaced with a file reference in the conversation.

```json theme={null}
{
  "name": "get_schema",
  "description": "Returns the full database schema",
  "_meta": {
    "anthropic/maxResultSizeChars": 200000
  }
}
```

The annotation applies independently of `MAX_MCP_OUTPUT_TOKENS` for text content, so users don't need to raise the environment variable for tools that declare it. Tools that return image data are still subject to the token limit.

### Images in tool results

When an MCP tool returns a PNG, JPEG, GIF, or WebP image, Claude sees the image inline in the conversation. The inline copy may be scaled down or compressed to fit the model's image size limits. Claude Code also saves the original bytes to a file in the session's `tool-results` directory under [`~/.claude/projects/`](https://code.claude.com/docs/en/claude-directory#cleaned-up-automatically) and gives Claude the path, so Claude can crop, convert, or reuse the full-resolution file with tools such as Bash.

When session persistence is disabled with [`--no-session-persistence`](https://code.claude.com/docs/en/cli-reference#cli-flags) or [`CLAUDE_CODE_SKIP_PROMPT_HISTORY`](https://code.claude.com/docs/en/env-vars), Claude Code writes no image file and Claude receives only the inline copy.

Saving MCP image results to a file requires Claude Code v2.1.283 or later.

## Tool input schemas with a root-level combinator

Some MCP servers declare a tool's input schema as a JSON Schema union, with `anyOf`, `oneOf`, or `allOf` at the top level of the schema. The Claude API doesn't accept those keywords at the schema root. It does accept combinators nested inside `properties`, which Claude Code sends unchanged.

Tools with a root-level combinator stay available. Before sending the tool to the API, Claude Code flattens the schema into a single object and prepends a sentence to the tool's description that tells Claude which parameter groups belong together:

* `allOf`: properties from every branch are merged, and each branch's `required` list still applies
* `anyOf` and `oneOf`: properties from every branch are merged, and each branch's `required` list is described in the tool description instead of enforced by the schema

The server receives whichever arguments Claude chose, so keep validating the combination server-side.

When Claude Code can't produce a schema the API accepts, or on a deployment that doesn't receive the remote configuration that enables the rewrite, it skips that one tool, records the reason in the server's log, and leaves the server's other tools available.

## Tools with invalid input schemas

> [!NOTE]
>
> If the session fails with a 400 error that names a tool by its position, follow the steps in [Tool input schema is invalid](https://code.claude.com/docs/en/errors.md#tool-input-schema-is-invalid).

If one of an MCP server's tools has an input schema that breaks either of two rules the API enforces, Claude Code excludes that tool. The server's other tools are unaffected. Claude Code checks both rules as it loads the server's tools:

* Top-level property names must be 1 to 64 characters long and use only ASCII letters and digits, `_`, `.`, and `-`
* The schema must be valid against the JSON Schema draft 2020-12 meta-schema. Claude Code applies this check to schemas that declare no `$schema` and schemas that declare draft 2020-12. A schema that declares any other dialect skips this check, though the property-name check above still applies

When Claude Code excludes a tool, it records the reason in the server's log and tells Claude which tools it excluded and why, so Claude can answer why a tool is missing. After the schema is fixed on the server, the tool comes back the next time Claude Code loads the server's tools.

When [feature flag fetching](https://code.claude.com/docs/en/env-vars.md#features-that-need-feature-flag-fetching) is off or the flags have never arrived, as on an air-gapped machine, a tool that breaks a rule isn't excluded:

* Claude gets the tool unchanged, and the server's log records `input schema would be rejected by the Anthropic API` for it
* If the API then rejects the schema, see [Tools whose input schema the API refuses](#tools-whose-input-schema-the-api-refuses)

Before v2.1.216, no deployment ran these checks.

The [root-level combinator handling](#tool-input-schemas-with-a-root-level-combinator) is separate and keeps its own behavior when flag fetching is off or the flags have never arrived.

### Tools whose input schema the API refuses

A debug-log line that contains `the API refused this tool's input schema` names a tool whose schema the API rejected in a request. Claude Code resends that request with the tool declared without parameters.

* **If the session fails with a 400 error that names a tool by its position**: follow the steps in [Tool input schema is invalid](https://code.claude.com/docs/en/errors.md#tool-input-schema-is-invalid)
* **For a user of the server**: no action is needed. Claude can still call the tool, but doesn't see its parameters
* **For the server's maintainer**: fix the tool's input schema on the server. The log line ends with `The API said:` and the API's reason for rejecting the schema. Validate the arguments the server receives, because Claude calls the tool without seeing its parameters

Before v2.1.300, every turn that included the refused schema failed with [a 400 error naming the tool by its position](https://code.claude.com/docs/en/errors.md#tool-input-schema-is-invalid).

## Tools with names longer than 128 characters

If `/mcp` lists a tool that Claude can't call, check whether the tool's full name is longer than 128 characters: run `/mcp` in the session and select the tool to see its full name, such as `mcp__<server>__<tool>`. Claude Code leaves an MCP tool out of the tools it sends to Claude when its full name is over 128 characters. The Claude API rejects a request that includes such a tool, so leaving the tool out keeps the server's other tools working.

For the message that names the tool and the ways to shorten its full name, see [MCP tool name over 128 characters](https://code.claude.com/docs/en/errors.md#mcp-tool-name-over-128-characters).

## Require approval for a specific tool

When building an MCP server, mark a tool as requiring explicit approval on every call by setting `_meta["anthropic/requiresUserInteraction"]` to `true` in the tool's `tools/list` response entry. The value must be the JSON Boolean `true`; any other value is ignored.

Claude Code shows that tool's permission prompt on every call, even in `acceptEdits`, `auto`, and `bypassPermissions` [permission modes](https://code.claude.com/docs/en/permissions.md#permission-modes), and doesn't offer a "don't ask again" option for it. [Allow rules](https://code.claude.com/docs/en/permissions.md#permission-rule-syntax) that match the tool don't skip the prompt either. In `dontAsk` mode, which never prompts, Claude Code denies the call instead.

The prompt has to reach a person. In non-interactive mode with [`--permission-prompt-tool`](https://code.claude.com/docs/en/cli-reference#cli-flags), an `allow` result from the prompt tool for a flagged tool is converted to a deny with the message `MCP tool requires user interaction; not supported via --permission-prompt-tool`. The Agent SDK's [`canUseTool` callback](https://code.claude.com/docs/en/agent-sdk/permissions) does receive these calls and can approve them, because the SDK application is expected to show them to a user.

Use this for tools whose permission prompt is itself the point, such as a consent or access-grant step where auto-approval would mean no human ever agreed. Other tools from the same server keep their normal permission behavior.

The following `tools/list` entry marks one tool as always requiring approval.

```json theme={null}
{
  "name": "grant_access",
  "description": "Requests access to a protected resource",
  "_meta": {
    "anthropic/requiresUserInteraction": true
  }
}
```

Some surfaces, such as [Remote Control](https://code.claude.com/docs/en/remote-control.md) and applications built on the [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md), normally allow approving tool calls with one tap. For a tool marked with this annotation, Claude Code withholds the one-tap action and shows the tool's full permission prompt instead, so approval still comes from a person answering the prompt, not from a tap.

Claude Code withholds one-tap approval the same way for any permission request that only the terminal dialog can render in full, such as one that carries a safety warning or an always-allow option the remote surface can't show. Such a request is answered in the terminal dialog, not from Remote Control.

## Mark tools that are safe to call twice

When building an MCP server, mark the tools that are safe to call twice so Claude Code can repeat a call that was pending when a connection closed. Claude Code can repeat such a call to an HTTP server or a [claude.ai connector](#use-mcp-servers-from-claudeai) once, on a new connection. A call Claude Code doesn't repeat can fail with [`connection closed before the tool call was answered`](https://code.claude.com/docs/en/errors#connection-closed-before-the-tool-call-was-answered).

To mark a tool, set one of these `annotations` to `true` in its `tools/list` entry:

* **`idempotentHint`**: the tool can change something, and calling it again with the same arguments is safe
* **`readOnlyHint`**: the tool changes nothing. Claude Code also runs the tool's calls in parallel with other read-only calls.

For example, these fields in a `tools/list` entry mark the `set_issue_status` tool as safe to repeat:

```json theme={null}
{
  "name": "set_issue_status",
  "annotations": {
    "idempotentHint": true
  }
}
```

## Respond to MCP elicitation requests

An MCP server can request structured input from the user mid-task through elicitation. When a server needs information it can't get on its own, Claude Code displays an interactive dialog in the terminal and passes the user's response back to the server. No configuration is required: elicitation dialogs appear automatically when a server requests them.

Servers can request input in two ways:

* **Form mode**: Claude Code shows a dialog with form fields defined by the server (for example, a username and password prompt). The user fills in the fields and submits.
* **URL mode**: Claude Code asks whether to open a link in the browser. Servers use this mode for a flow that finishes outside the terminal, such as sign-in.

In URL mode, Claude Code passes the URL as a command-line argument to the system's URL handler, and caps how long that argument can be. When the URL, once escaped for the command line, is over that cap, the request can only be declined. Every character that needs escaping, such as `%` or `&`, counts four times toward the cap: its own character plus three escape characters. A URL with none of them reaches the cap at about 8,000 characters. A URL built largely of percent-escapes, where every third character is a `%`, reaches it at roughly 4,000.

To auto-respond to elicitation requests without showing a dialog, use the [`Elicitation` hook](https://code.claude.com/docs/en/hooks#elicitation).

When building an MCP server that uses elicitation, read the [MCP elicitation specification](https://modelcontextprotocol.io/docs/learn/client-concepts#elicitation) for protocol details and schema examples.

### Answer an elicitation request in a cloud session

When Claude's task in a cloud session waits on an MCP server's request, the server needs something from the user, such as a value or a sign-in. If the request appears as a card at claude.ai/code or in the Desktop app's **Code** tab, answer on the card:

* **Form mode**: fill in the fields, then click **Submit**
* **URL mode**: click **Open link**, finish the flow it opens, then click **I’m done, continue** on the card

To refuse the request, click **Decline**. Claude continues once the server responds.

If no card appears in either place, the request can't be answered there. In the user's own session, click the stop button there to end the turn.

### Elicitation modes Claude Code declares

For an MCP server author: the client capabilities Claude Code sends when it connects tell the server which elicitation modes it can request. Claude Code declares `elicitation: {form: {}, url: {}}` on the following connections, so a server on any of them can request both modes:

* Connections that use [protocol revision 2026-07-28](#mcp-client-runtimes)
* Connections on the earlier protocol revisions, 2025-11-25 and older, to the stdio, `sse`, `http`, and `ws` servers in a user's Claude Code MCP configuration. Requires Claude Code v2.1.287 or later

On its other connections on the earlier revisions, such as to [claude.ai connectors](#use-mcp-servers-from-claudeai), Claude Code declares the bare `elicitation: {}`, which permits elicitation requests in form mode only.

A server built on Java MCP SDK 0.17.0 or earlier can refuse a declaration that has `form` and `url` in it. See [MCP server rejected the elicitation capability](https://code.claude.com/docs/en/errors.md#mcp-server-rejected-the-elicitation-capability).

## Use MCP resources

MCP servers can expose resources that are referenced with @ mentions, the same way files are referenced.

### Reference MCP resources

**1. List available resources**

Type `@` in the prompt to see available resources from all connected MCP servers. Resources appear alongside files in the autocomplete menu.

**2. Reference a specific resource**

Use the format `@server:protocol://resource/path` to reference a resource:

```text wrap theme={null}
Can you analyze @github:issue://123 and suggest a fix?
```

```text wrap theme={null}
Please review the API documentation at @docs:file://api/authentication
```

**3. Multiple resource references**

A single prompt can reference multiple resources:

```text wrap theme={null}
Compare @postgres:schema://users with @docs:file://database/user-model
```

> [!TIP]
>
> Tips:
>
> * Resources are automatically fetched and included as attachments when referenced
> * Resource paths are fuzzy-searchable in the @ mention autocomplete
> * Claude Code automatically provides tools to list and read MCP resources when servers support them
> * Resources can contain any type of content that the MCP server provides (text, JSON, structured data, etc.)

MCP Apps UI resources are entries with a `ui://` URI or the `text/html;profile=mcp-app` media type: pages for a host application to render, not content for Claude to read. They don't appear in the `@` suggestions or in the resource list tool's results, and a server that offers only UI resources shows an empty resource list. Reading a UI resource by its URI still works.

## Scale with MCP tool search

Tool search keeps MCP context usage low by deferring tool definitions until Claude needs them. Only tool names and server instructions load at session start, so adding more MCP servers has minimal impact on the context window. Claude Code doesn't impose a fixed per-server tool cap; the practical limit is the context window budget.

### Tool search for MCP server authors

When building an MCP server, the server instructions field matters more with tool search enabled: server instructions tell Claude when to search for the server's tools, similar to how [skills](https://code.claude.com/docs/en/skills.md) work.

Write clear, descriptive server instructions that explain:

* What category of tasks the tools handle
* When Claude should search for the tools
* Key capabilities the server provides

Claude Code cuts a tool description or server instructions that run past these default limits, and Claude sees only the text before the cut:

* **Server instructions, and the description of a tool that loads upfront**: 4,096 characters
* **The description of a tool that Claude loads through tool search**: 16,384 characters

Keep descriptions and instructions concise, and put critical details near the start. When tool search matches Claude's query against a tool's description, it reads only the part within the shorter limit, so put the words Claude would search for near the start too. A tool loads upfront and keeps the shorter limit whenever it isn't deferred, for example when [tool search is off](#configure-tool-search), when the tool is [marked to load upfront](#mark-a-tool-to-load-upfront-or-stay-deferred), or when its server is [exempt from deferral](#exempt-a-server-from-deferral).

Before v2.1.296, the shorter limit was 2,048 characters, and before v2.1.295 it applied to every tool description, including one loaded through tool search.

#### Change the description length limits

To change the [default limits](#tool-search-for-mcp-server-authors) of 4,096 and 16,384 characters for the MCP servers in a session, set [`CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH`](https://code.claude.com/docs/en/env-vars#variables) to a number of characters. Claude Code uses that number for both limits. With `8192`, for example, the 4,096-character limit on server instructions and tool descriptions loaded upfront rises, and the 16,384-character limit on tool descriptions loaded through tool search falls. This variable requires Claude Code v2.1.280 or later.

Descriptions and instructions from some of the MCP servers that Anthropic hosts at `api.anthropic.com` reach Claude in full, and setting this variable doesn't cut them.

#### Mark a tool to load upfront or stay deferred

To control how one of a server's tools loads, set `"anthropic/alwaysLoad"` in that tool's `_meta` object. The person who adds the server to Claude Code can also set [`alwaysLoad`](#exempt-a-server-from-deferral) for the whole server in their configuration, and that setting can override the tool's value:

| Your tool's value | What happens |
| :- | :- |
| `true` | The tool loads upfront. Startup doesn't wait for your server because of this value. The person configuring your server can still [defer all of its tools](#defer-a-servers-tools) |
| `false` | The tool stays deferred when their configuration sets `"alwaysLoad": true`. This applies when your server is passed with [`--mcp-config`](https://code.claude.com/docs/en/cli-reference#cli-flags), supplied by an [Agent SDK application](https://code.claude.com/docs/en/agent-sdk/mcp.md#in-code), or provided by a [plugin](#plugin-provided-mcp-servers). On other servers the tool loads upfront. Requires Claude Code v2.1.285 or later |

The following `tools/list` entry asks for one tool to load upfront:

```json theme={null}
{
  "name": "search_tickets",
  "description": "Searches the ticket tracker by keyword",
  "_meta": {
    "anthropic/alwaysLoad": true
  }
}
```

### Configure tool search

Tool search is enabled by default: MCP tools are deferred and discovered on demand.

Claude Code uses tool search on Claude Opus 4, Claude Sonnet 4, Claude Haiku 4.5, and later models, or Opus 4.5, Sonnet 4.5, Haiku 4.5, and later models on Google Cloud's Agent Platform. On earlier models, Claude Code loads all MCP tools upfront, and `ENABLE_TOOL_SEARCH=true` doesn't override this.

Control tool search behavior with the `ENABLE_TOOL_SEARCH` environment variable:

| Value | Behavior |
| :- | :- |
| (unset) | All MCP tools deferred and loaded on demand. Loaded upfront on models earlier than Opus 4 and Sonnet 4, on the [earlier Agent Platform models](#configure-tool-search), and on Microsoft Foundry deployments hosted on Azure |
| `true` | MCP tools deferred, with the same fallbacks as (unset) |
| `auto` | Threshold mode. Tools that would otherwise be deferred load upfront while their definitions total under 10% of the context window. At 10% or more, tool search turns on, and those tools can [stay deferred](#tools-that-stay-deferred-below-the-enable_tool_searchauto-threshold) even if the total falls under 10% |
| `auto:N` | Threshold mode with a custom percentage, where `N` is 0-100. For example, `auto:5` for 5% |
| `false` | All MCP tools loaded upfront, no deferral |

```bash theme={null}
# Use a custom 5% threshold
ENABLE_TOOL_SEARCH=auto:5 claude

# Disable tool search entirely
ENABLE_TOOL_SEARCH=false claude
```

Or set the value in the [settings.json `env` field](https://code.claude.com/docs/en/settings-reference#env).

To disable the `ToolSearch` tool specifically, deny it:

```json theme={null}
{
  "permissions": {
    "deny": ["ToolSearch"]
  }
}
```

When `ToolSearch` is denied or left out of [`--tools`](https://code.claude.com/docs/en/cli-reference#cli-flags), MCP tools load upfront instead, but a request can still carry a placeholder `defer_loading` entry. If a gateway rejects that entry, see [Tool search through an LLM gateway](https://code.claude.com/docs/en/mcp#tool-search-through-a-gateway).

#### Tools that stay deferred below the `ENABLE_TOOL_SEARCH=auto` threshold

If [`/context`](https://code.claude.com/docs/en/commands#all-commands) labels tools `(deferred)` or `(loaded on-demand)` though their definitions total under the `auto` threshold, tool search was already on in this conversation and stayed on. The total can drop later, for example while MCP servers reconnect after a session is resumed. No action is needed: Claude loads each of those tools when a task needs it.

### Exempt a server from deferral

When a server's tools should always be visible to Claude without a search step, set `alwaysLoad` to `true` in that server's configuration. The server's tools then load into context regardless of the `ENABLE_TOOL_SEARCH` setting. Reserve this for a small number of tools that Claude needs on every turn, since each upfront tool consumes context that would otherwise be available for the conversation.

The following `.mcp.json` entry exempts one HTTP server while leaving other servers deferred:

```json theme={null}
{
  "mcpServers": {
    "core-tools": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "alwaysLoad": true
    }
  }
}
```

The `alwaysLoad` field is available on all server types.

Setting `alwaysLoad: true` also makes startup wait for the server's tools, capped at the standard 5-second connect timeout, since they must be present when the first prompt is built. A remote server with a valid [`cached` entry](#server-status-detail) supplies its tools from the cache without connecting, so it doesn't hold startup. Other servers connect in the background by default; set [`MCP_CONNECTION_NONBLOCKING=0`](https://code.claude.com/docs/en/env-vars) to make startup wait for them too.

### Defer a server's tools

To keep all of a server's tools behind tool search, set `"alwaysLoad": false` in that server's entry in the MCP configuration. That includes tools that the server's author has [marked to load upfront](#mark-a-tool-to-load-upfront-or-stay-deferred). With `alwaysLoad` left out, those marked tools load upfront. Requires Claude Code v2.1.287 or later.

## Use MCP prompts as commands

MCP servers can expose prompts that become available as commands in Claude Code.

Prompts from a server named `anthropic-skills` don't appear, because Claude Code [reserves that name](https://code.claude.com/docs/en/skills.md#names-reserved-for-synced-skills) for skills synced from claude.ai. The server's tools still work. To list its prompts, rename the server in the MCP configuration.

### Execute MCP prompts

**1. Discover available prompts**

Type `/` to see the available commands, including those from MCP servers. Claude Code lists each MCP prompt as `/servername:promptname (MCP)`. Typing `/mcp__servername__promptname` also runs it.

**2. Execute a prompt without arguments**

```text wrap theme={null}
/mcp__github__list_prs
```

**3. Execute a prompt with arguments**

Many prompts accept arguments. Pass them space-separated after the command. Claude Code splits the arguments on whitespace, so each argument is a single token:

```text wrap theme={null}
/mcp__github__pr_review 456
```

```text wrap theme={null}
/mcp__jira__create_issue login-bug high
```

> [!TIP]
>
> Tips:
>
> * MCP prompts are dynamically discovered from connected servers
> * Arguments are parsed based on the prompt's defined parameters
> * Prompt results are injected directly into the conversation
> * In the `/mcp__servername__promptname` form, Claude Code replaces any character in the server name outside `A-Z`, `a-z`, `0-9`, `_`, and `-` with `_`, and uses the prompt name as the server declares it

## Managed MCP configuration

For organizations that need centralized control over which MCP servers users can connect to, read [Managed MCP configuration](https://code.claude.com/docs/en/managed-mcp.md). It covers deploying a fixed server set with `managed-mcp.json`, providing servers to every user with `managedMcpServers`, restricting servers with `allowedMcpServers` and `deniedMcpServers`, and what users see when a server is blocked.

## Documentation References

- Source page: https://code.claude.com/docs/en/mcp (read it for the sections this copy omits, such as the scope subsections, pre-configured OAuth credentials, claude.ai connector controls, and tool search through a gateway)
- https://code.claude.com/docs/en/mcp-quickstart.md (step-by-step walkthrough for connecting a first MCP server)
- https://code.claude.com/docs/en/plugins/overview.md (what plugins are and what they can bundle)
- https://code.claude.com/docs/en/plugins/components.md (bundling MCP servers in a plugin, path variables and persistent data)
- https://code.claude.com/docs/en/plugins/manifest-reference (plugin manifest fields, including user configuration values)
- https://code.claude.com/docs/en/plugins/install.md (installing plugins and the `/plugin` manager)
- https://code.claude.com/docs/en/plugins/cli-reference.md (plugin CLI commands, including `/reload-plugins`)
- https://code.claude.com/docs/en/plugins/loading.md (where installed plugins live on disk)
- https://code.claude.com/docs/en/plugins/troubleshooting.md (plugin install errors such as "Plugin not found in marketplace")
- https://code.claude.com/docs/en/managed-mcp.md (managed MCP configuration, `managedMcpServers`, allowlists and denylists)
- https://code.claude.com/docs/en/env-vars.md (every MCP environment variable and feature-flag fetching)
- https://code.claude.com/docs/en/errors.md (the MCP error messages this file links to and their fixes)
- https://code.claude.com/docs/en/permissions.md (permission modes, rule syntax, working directories, workspace trust, `/cd`)
- https://code.claude.com/docs/en/settings.md (settings files and the `env` block, settings in cloud sessions)
- https://code.claude.com/docs/en/settings-reference (`env`, `enabledMcpjsonServers` and `disabledMcpjsonServers`)
- https://code.claude.com/docs/en/hooks.md (the `Elicitation` hook, MCP tool matchers and `mcp_tool` hook fields)
- https://code.claude.com/docs/en/sub-agents.md (subagent `tools` field and MCP servers scoped to a subagent)
- https://code.claude.com/docs/en/skills.md (skills, and names reserved for synced skills)
- https://code.claude.com/docs/en/channels.md (officially supported channels that push messages into a session)
- https://code.claude.com/docs/en/channels-reference.md (building a channel server)
- https://code.claude.com/docs/en/headless.md (non-interactive `-p` mode, bare mode, MCP work when a run ends)
- https://code.claude.com/docs/en/cli-reference (CLI flags such as `--mcp-config`, `--tools`, `--permission-prompt-tool`, `--no-session-persistence`)
- https://code.claude.com/docs/en/commands (built-in commands such as `/tasks` and `/context`)
- https://code.claude.com/docs/en/tools-reference.md (built-in tools and background commands)
- https://code.claude.com/docs/en/claude-directory (the `~/.claude/projects/` directory and what is cleaned up automatically)
- https://code.claude.com/docs/en/claude-code-on-the-web.md (cloud sessions)
- https://code.claude.com/docs/en/remote-control.md (Remote Control sessions and re-authorizing a connector from the shell)
- https://code.claude.com/docs/en/desktop.md (the desktop app and its preview pane)
- https://code.claude.com/docs/en/vs-code.md (the VS Code extension)
- https://code.claude.com/docs/en/github-actions.md (Claude Code in GitHub Actions)
- https://code.claude.com/docs/en/agent-sdk/overview.md (the Agent SDK)
- https://code.claude.com/docs/en/agent-sdk/mcp.md (MCP in the Agent SDK, error handling and in-code servers)
- https://code.claude.com/docs/en/agent-sdk/permissions (the Agent SDK `canUseTool` callback)
- https://code.claude.com/docs/en/agent-sdk/typescript.md (the TypeScript SDK reference, including `setMcpServers()`)
- https://claude.com/docs/connectors (claude.ai connectors)
- https://claude.com/docs/connectors/building (building connectors, authentication, testing, and Directory submission)
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins/mcp-server-dev (the official `mcp-server-dev` plugin that scaffolds a server)
- https://modelcontextprotocol.io/introduction (introduction to the Model Context Protocol)
- https://modelcontextprotocol.io/docs/develop/build-server (MCP server guide and protocol fundamentals)
- https://modelcontextprotocol.io/docs/learn/client-concepts (client concepts, including the elicitation specification)
- https://modelcontextprotocol.io/extensions/tasks/overview (the MCP tasks extension)
- https://ts.sdk.modelcontextprotocol.io/v2/ (MCP TypeScript SDK 2.0, which the v2 client runtime uses)
