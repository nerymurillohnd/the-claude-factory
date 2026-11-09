> ## Documentation Index
>
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.
>
> Source: https://code.claude.com/docs/en/errors
> Pruned copy (2026-11-07): this file keeps only the passages that apply to developing and distributing Claude Code plugins through a marketplace hosted in a public GitHub repository and served to third parties. Removed passages are listed in REMOVALS.md.
>
> Sections in this file:
>
> - Find your error
> - Server errors
>   - The server returned no safety verdict
>     - `a hook changed this call's input after auto mode reviewed it`
>   - Agent terminated early due to an API error
> - Authentication errors
>   - MCP server needs you to sign in again
>   - Couldn't read the stored credentials for MCP server
>   - MCP server URL is missing or not a valid URL
> - Network and connection errors
>   - MCP server connection timed out during a sleep or clock change
> - Request errors
>   - Tool input schema is invalid
>   - MCP tool name over 128 characters
>   - Model is restricted by your organization's settings
>   - Model switch was blocked by a PreModelSwitch hook
>   - Safeguards flagged a request for Claude's reasoning
> - Command-line errors
>   - Cannot add MCP server when managed settings allow only plugin servers
>   - Server rejected the Authorization header minted by the configured headersHelper
>   - MCP server rejected the elicitation capability
>   - OAuth callback port is already in use
>   - No available ports for OAuth redirect
>   - /security-review fails without origin/HEAD
>   - No shell command in a skill or command was run
>   - Unknown command
> - Plugin errors
>   - plugin eval is currently in early access
>   - Marketplace is registered from an untrusted source
>   - Marketplace name is another spelling of a reserved name
>   - Claude Code refuses the marketplace name
>   - Marketplace is already added from a different source
>   - Plugin command references user\_config in a shell command
>   - Path escapes plugin directory
>   - Plugin not loaded: its manifest was not read
>   - Path could not be checked
>   - Marketplace entry path does not stay inside the marketplace directory
>   - Failed to load marketplace configuration
>   - Plugin was not uninstalled
>   - Skipping connection (recent failure cached; retries automatically in 15 min, or edit the plugin config to retry now)
> - Tool errors
>   - Agent would be spawned with zero tools
>   - Command contains an invisible character
> - Configuration warnings
>   - Agent descriptions are over the 15.0k-token limit
>   - Hook needs quotes around a path with a space
>   - A skill, command, or workflow wasn't loaded because its name is reserved
>   - Skill or command name refused
>   - Managed settings need your approval
>   - MCP server is blocked by enterprise managed policy
>   - MCP server name is reserved
> - Report an error

# Error reference

> Look up Claude Code runtime error messages with what each one means and how to fix it.

## Find your error

Match the message you see to a section below.

| Message | Section |
| :- | :- |
| `Agent terminated early due to an API error` | [Server errors](#agent-terminated-early-due-to-an-api-error) |
| `MCP server "<name>" needs you to sign in again (run /mcp to re-authenticate)` | [Authentication](#mcp-server-needs-you-to-sign-in-again) |
| `rejected the credential from its headersHelper` / `rejected the Authorization header in its config` | [Authentication](#mcp-server-needs-you-to-sign-in-again) |
| `MCP server "<name>" needs additional permissions (scope: "<scope>") — run /mcp to re-authenticate` | [Authentication](#mcp-server-needs-you-to-sign-in-again) |
| `MCP server "<name>" requires re-authorization (token expired)` | [Authentication](#mcp-server-needs-you-to-sign-in-again) |
| `Couldn't read the stored credentials for MCP server "<name>", so the request didn't run` | [Authentication](#couldnt-read-the-stored-credentials-for-mcp-server) |
| `A request to MCP server "<name>" was sent without your stored credentials` | [Authentication](#couldnt-read-the-stored-credentials-for-mcp-server) |
| `This server's URL is missing or not a valid URL, so sign-in can't start` | [Authentication](#mcp-server-url-is-missing-or-not-a-valid-url) |
| `Issuer mismatch in authorization response (RFC 9207)` | [Authentication](https://code.claude.com/docs/en/errors#issuer-mismatch-in-authorization-response) |
| `Refusing to send credentials to non-https token endpoint` / `<short-name> from the MCP SDK for <server-url>` | [Authentication](https://code.claude.com/docs/en/errors#refusing-to-send-credentials-to-non-https-token-endpoint) |
| `API Error: 400 ... tools.N.custom.input_schema: JSON schema is invalid` / `Property keys should match pattern` | [Request errors](#tool-input-schema-is-invalid) |
| `Tool "mcp__<server>__<tool>" is not sent to Claude: its name has <N> characters and the API accepts at most 128` | [Request errors](#mcp-tool-name-over-128-characters) |
| `tools.N.custom.name: String should have at most 128 characters` | [Request errors](#mcp-tool-name-over-128-characters) |
| `tool_use.name: String should have at most 200 characters` | [Request errors](#tool-use-name-over-200-characters) |
| `Model switch ... blocked by a PreModelSwitch hook` | [Request errors](#model-switch-was-blocked-by-a-premodelswitch-hook) |
| `couldn't be resolved to a real location, so its skills, commands, and agents weren't loaded` | [Command-line errors](https://code.claude.com/docs/en/errors#directory-couldnt-be-resolved-to-a-real-location) |
| `Cannot add MCP server: your organization's managed settings allow only MCP servers that plugins provide` | [Command-line errors](#cannot-add-mcp-server-when-managed-settings-allow-only-plugin-servers) |
| `Can't read .mcp.json: it isn't a regular file or is larger than 2097152 bytes` | [Command-line errors](#cant-read-mcp-json) |
| `Server rejected the Authorization header minted by the configured headersHelper` | [Command-line errors](#server-rejected-the-authorization-header-minted-by-the-configured-headershelper) |
| `This server (Java MCP SDK 0.17.0 or older) rejected Claude Code's elicitation capability` | [Command-line errors](#mcp-server-rejected-the-elicitation-capability) |
| `Shell command failed for pattern "..."`, from `/security-review` or any skill that injects dynamic context | [Command-line errors](#security-review-fails-without-origin-head) |
| `Shell command permission check failed for pattern "..."`, from a skill that injects dynamic context | [Command-line errors](#security-review-fails-without-origin-head) |
| ``Skill <name> requires bash (`shell: bash` in frontmatter) but Git Bash was not found`` | [Command-line errors](#security-review-fails-without-origin-head) |
| `No shell command in <name> was run, because the <tool> tool does not accept one of them` | [Command-line errors](#no-shell-command-was-run) |
| `Unknown command: /<name>`, with or without a `Did you mean` suggestion | [Command-line errors](#unknown-command) |
| `` `plugin eval` is currently in early access `` / `` `plugin eval` is currently unavailable `` | [Plugin errors](#plugin-eval-is-currently-in-early-access) |
| `cannot be evaluated where sessions load it` | [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals.md#cannot-be-evaluated-where-sessions-load-it) |
| `Marketplace "<name>" is registered from an untrusted source` | [Plugin errors](#marketplace-is-registered-from-an-untrusted-source) |
| `Claude Code refuses the marketplace name "<name>"` | [Plugin errors](#claude-code-refuses-the-marketplace-name) |
| `Marketplace name impersonates an official Anthropic/Claude marketplace` | [Plugin errors](#claude-code-refuses-the-marketplace-name) |
| `Marketplace "<name>" is already added from a different source` | [Plugin errors](#marketplace-is-already-added-from-a-different-source) |
| `"<name>" is another spelling of "<reserved>", a reserved marketplace name` | [Plugin errors](#marketplace-name-is-another-spelling-of-a-reserved-name) |
| `Cannot add marketplace "<name>": Claude Code cannot install plugins from a marketplace with this name` | [Plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md#cannot-install-plugins-from-a-marketplace-with-this-name) |
| `Cannot add marketplace "<name>": Claude Code reserves this name and cannot register a marketplace under it` | [Plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md#claude-code-reserves-this-name) |
| `Marketplace "<name>" is added but ignored` | [Plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md#marketplace-is-added-but-ignored) |
| `Marketplace "<name>" is registered but was refused (see the debug log)` | [Plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md#marketplace-is-added-but-ignored) |
| `references ${user_config.*} in a shell-form command` | [Plugin errors](#plugin-command-references-user-config) |
| `Monitor "<name>" from plugin <plugin> references ${user_config.*} in its command` | [Plugin errors](#plugin-command-references-user-config) |
| `headersHelper for MCP server '<name>' references ${user_config.*}` | [Plugin errors](#plugin-command-references-user-config) |
| `An npm plugin source must name a registry package` | [Plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md#an-npm-plugin-source-must-name-a-registry-package) |
| `The packages it lists are not installed` / `The packages it lists were not installed, because` | [Plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md#the-packages-it-lists-are-not-installed) |
| `does not load (...), so Claude Code ignores the whole file` | [Plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md#does-not-load-so-claude-code-ignores-the-whole-file) |
| `path escapes plugin directory` | [Plugin errors](#path-escapes-plugin-directory) |
| `Plugin not loaded: its manifest <path> was not read` | [Plugin errors](#plugin-not-loaded-its-manifest-was-not-read) |
| `path could not be checked` | [Plugin errors](#path-could-not-be-checked) |
| `its marketplace entry path does not stay inside the marketplace directory` | [Plugin errors](#marketplace-entry-path-does-not-stay-inside-the-marketplace-directory) |
| `Plugin source path refused` | [Plugin errors](#marketplace-entry-path-does-not-stay-inside-the-marketplace-directory) |
| `Failed to load marketplace configuration` | [Plugin errors](#failed-to-load-marketplace-configuration) |
| `Marketplace configuration file is corrupted` | [Plugin errors](#failed-to-load-marketplace-configuration) |
| `"<plugin>" was not uninstalled: it is still switched on in <file>` | [Plugin errors](#plugin-was-not-uninstalled) |
| `"<plugin>" was not uninstalled: <file> is there and could not be read` | [Plugin errors](#plugin-was-not-uninstalled) |
| `Plugin "<plugin>" was not uninstalled: installed_plugins.json` | [Plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md#installed-plugins-json-holds-a-record-this-version-cannot-read) |
| `Plugin directory does not exist: <path>` | [Plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md#plugin-directory-does-not-exist) |
| `Skipping connection (recent failure cached; retries automatically in 15 min, or edit the plugin config to retry now)` | [Plugin errors](#skipping-connection-recent-failure-cached) |
| `Error: No such tool available: <tool name>` | [Tool errors](https://code.claude.com/docs/en/errors#no-such-tool-available) |
| `MCP server "<name>" connection closed before the tool call was answered` | [Tool errors](#connection-closed-before-the-tool-call-was-answered) |
| `MCP server "<name>" is disabled — re-enable it via /mcp to use its tools` | [Tool errors](https://code.claude.com/docs/en/errors#mcp-server-is-disabled) |
| `MCP server "<name>" tool "<tool>" timed out after <N>s. The server asked the user a question, and no answer came before the time limit.` | [Tool errors](https://code.claude.com/docs/en/errors#mcp-tool-call-timed-out-with-the-servers-question-unanswered) |
| `would be spawned with zero tools — refusing` | [Tool errors](#agent-would-be-spawned-with-zero-tools) |
| `Agent descriptions are over the 15.0k-token limit` | [Configuration warnings](#agent-descriptions-are-over-the-15000-token-limit) |
| `hook needs quotes around a path with a space` | [Configuration warnings](#hook-needs-quotes-around-a-path-with-a-space) |
| `Not loaded: rename <path>, then restart — its name uses "<name>", a name reserved for the skills synced from your claude.ai account` | [Configuration warnings](#a-skill-command-or-workflow-wasnt-loaded-because-its-name-is-reserved) |
| `N skill or command names refused: run with --debug to see which ([names]), rename, then restart` | [Configuration warnings](#skill-or-command-name-refused) |
| `MCP server <name> is blocked by enterprise managed policy` | [Configuration warnings](#mcp-server-is-blocked-by-enterprise-managed-policy) |
| `"<name>" is a reserved MCP server name and was not loaded` | [Configuration warnings](#mcp-server-name-is-reserved) |

## Server errors

### The server returned no safety verdict

#### `a hook changed this call's input after auto mode reviewed it`

This denial means a hook or mod [changed the call's input](https://code.claude.com/docs/en/hooks.md#pretooluse-updatedinput-in-auto-mode) after the server reviewed it, so the review doesn't cover what would run. It isn't a judgment that the action is unsafe.

Later calls in the same Claude response can be denied with this reason:

```text theme={null}
another call in this response was changed by a hook after auto mode reviewed it, or could not be confirmed unchanged
```

Claude can then issue each denied call again so the server reviews it. If a permission prompt opens, answer it. You don't need to do anything else unless Claude says in its reply that auto mode couldn't check the call. Then stop the change or approve the call yourself, and ask Claude to try the call again:

* **Stop the change**: turn off the [hook](https://code.claude.com/docs/en/hooks.md#disable-or-remove-hooks) or [mod](https://code.claude.com/docs/en/plugins/mods/overview.md#turn-mods-on-or-off) that changed the call or an earlier call in the same Claude response, or ask your administrator to turn it off. To look for a hook, run [`/hooks`](https://code.claude.com/docs/en/hooks#the-%2Fhooks-menu) at the Claude Code prompt. In a terminal session, run `/plugin` to see the active mods.
* **Approve the call yourself**: [switch to Manual mode](https://code.claude.com/docs/en/permission-modes.md#switch-permission-modes)

### Agent terminated early due to an API error

A [subagent](https://code.claude.com/docs/en/sub-agents.md)'s API request failed terminally, for example because a usage limit was reached or retries for a server error ran out, so the subagent stopped before finishing its task. This message requires Claude Code v2.1.199 or later; before then the API error text was returned to Claude as if it were the subagent's result.

```text theme={null}
Agent terminated early due to an API error: <error detail>
```

**What to do:**

* Match the error detail after the colon to its own section on this page, such as [Usage limits](https://code.claude.com/docs/en/errors#usage-limits) or [Server errors](#server-errors), and follow that section's steps
* Once the underlying error clears, ask Claude to retry the task or [resume the subagent](https://code.claude.com/docs/en/sub-agents.md#resume-subagents)

When a rate limit, overload, or server error interrupts a foreground subagent that already produced text output, Claude receives that partial output marked as incomplete instead of this error. A subagent whose only output was tool calls gets this error too; in v2.1.199 that shape returned an empty partial result instead. See [API errors in subagents](https://code.claude.com/docs/en/sub-agents.md#api-errors-in-subagents).

## Authentication errors

### MCP server needs you to sign in again

A remote [MCP server](https://code.claude.com/docs/en/mcp.md) rejected the credential on a tool call mid-session, usually because a sign-in or token expired or because the token lacks a permission the tool needs. The tool call fails, and `/mcp` marks the server as [needing authentication](https://code.claude.com/docs/en/mcp.md#authenticate-with-remote-mcp-servers).

For a server you sign in to from Claude Code, including a claude.ai connector, the sign-in expired or was revoked:

```text theme={null}
MCP server "<name>" needs you to sign in again (run /mcp to re-authenticate)
```

Run `/mcp`, select the server, and sign in again from its menu.

For a server configured with a [`headersHelper`](https://code.claude.com/docs/en/mcp#use-dynamic-headers-for-custom-authentication) script, Claude Code has already re-run the helper and retried the call once before showing this:

```text theme={null}
MCP server "<name>" rejected the credential from its headersHelper (check the helper and run /mcp to reconnect, or to authenticate if the server also uses OAuth)
```

Check that the helper returns a credential the server accepts, then reconnect from `/mcp`, which runs the helper again.

For a server with a static `Authorization` header in its configuration:

```text theme={null}
MCP server "<name>" rejected the Authorization header in its config (update it, then run /mcp to reconnect)
```

Update the header value where the server is configured, then reconnect from `/mcp`.

In a [Cowork](https://claude.com/docs/cowork/overview) session on your machine in the Claude Desktop app, these messages mean the MCP server rejected a credential it was given. Fix the one the message names, then start a new task or chat in Cowork:

```text theme={null}
MCP server "<name>" rejected the credential from its headersHelper (check the helper, then start a new task or chat)
MCP server "<name>" rejected the Authorization header in its config (update it, then start a new task or chat)
```

* **`headersHelper` credential rejected**: check that the helper returns a credential the server accepts, then start a new task or chat in Cowork
* **`Authorization` header rejected**: update the `Authorization` value under `headers` in that server's configuration, then start a new task or chat in Cowork

Before v2.1.302, a Cowork session showed the `run /mcp to reconnect` endings instead, although `/mcp` isn't available there. If you see such an ending in Cowork, still check the helper or update the header, then start a new task or chat. Before v2.1.273, the expired sign-in, `headersHelper`, and `Authorization` header cases all showed `MCP server "<name>" requires re-authorization (token expired)`.

A server can also refuse a tool call with HTTP 403 `insufficient_scope` to ask you to authorize a scope, sometimes one your token already lists. The message names that scope:

```text theme={null}
MCP server "<name>" needs additional permissions (scope: "<scope>") — run /mcp to re-authenticate
```

Run `/mcp`, select the server, and authenticate again from its menu.

When the server's configuration sets neither [`oauth.scopes`](https://code.claude.com/docs/en/mcp#restrict-oauth-scopes) nor [`authServerMetadataUrl`](https://code.claude.com/docs/en/mcp#override-oauth-metadata-discovery), Claude Code requests the scope the server named. With either setting, Claude Code requests that setting's scopes instead. If you pinned `oauth.scopes`, add the missing scope to that list before you authenticate again.

Before v2.1.274, this case showed the `needs you to sign in again` message, and before v2.1.273 it showed `requires re-authorization (token expired)` like the other cases.

### Couldn't read the stored credentials for MCP server

Claude Code keeps your sign-ins for OAuth [MCP servers](https://code.claude.com/docs/en/mcp.md) in a credential store. This message means Claude Code couldn't read that store, so a request to the server didn't run:

```text theme={null}
Couldn't read the stored credentials for MCP server "<name>", so the request didn't run. If your Mac's keychain is locked, unlock it, then try again.
Couldn't read the stored credentials for MCP server "<name>", so the request didn't run. Try again.
```

Your stored sign-ins are unchanged: try again once the store can be read, and sign in again only if the server then asks you to.

In a [`claude -p`](https://code.claude.com/docs/en/headless) or [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) run on macOS, the keychain can become readable after a request has already gone out without the stored sign-in. That request fails with:

```text theme={null}
A request to MCP server "<name>" was sent without your stored credentials, so the server rejected it. The credentials are available now. Try again.
```

**What to do:**

* If the message asks you to unlock your Mac's keychain, run [`claude doctor`](https://code.claude.com/docs/en/cli-reference#cli-commands) in the shell session you run Claude Code from, and check its report for a keychain warning:
  * If the report lists a warning that starts with `macOS Keychain is not writable`, or your shell has no `claude` command, run this unlock command in that shell session:

    ```bash theme={null}
    security unlock-keychain ~/Library/Keychains/login.keychain-db
    ```

  * If the report lists no keychain warning, skip the unlock command

* Try again where you saw the message:
  * For `claude -p`, run the command again
  * In an interactive session, reconnect the server from `/mcp` if it shows as failed there, then ask Claude to try again
  * In an Agent SDK application that keeps running, call [`reconnectMcpServer()`](https://code.claude.com/docs/en/agent-sdk/typescript#methods) in TypeScript or [`ClaudeSDKClient.reconnect_mcp_server()`](https://code.claude.com/docs/en/agent-sdk/python#methods) in Python, or start a new session

* If the server then reports that it needs authentication, Claude Code found no sign-in it can use for that server. Sign in interactively: run `/mcp` in a Claude Code session, or [`claude mcp login <name>`](https://code.claude.com/docs/en/mcp#authenticate-from-the-command-line) in your shell. In an Agent SDK application, see [OAuth2 authentication in the Agent SDK](https://code.claude.com/docs/en/agent-sdk/mcp.md#oauth2-authentication).

Before v2.1.307, a `claude -p` or Agent SDK run on a Mac with a locked login keychain reported the server as needing authentication instead of showing either message.

### MCP server URL is missing or not a valid URL

Claude Code refused to start an OAuth sign-in for a remote MCP server because the server's configured `url` doesn't parse as a URL. Unless Claude Code has a more specific configuration problem to report for the server, running [`claude mcp login <name>`](https://code.claude.com/docs/en/mcp#authenticate-from-the-command-line) in your shell prints the refusal as:

```text theme={null}
Couldn't complete authentication for "<name>": This server's URL is missing or not a valid URL, so sign-in can't start. Fix the URL in its MCP config (or set the environment variable it uses) and try again.
```

**What to do:**

* Set the entry's `url` to the server's real endpoint where the server is configured, or set the environment variable that its [`${VAR}` reference](https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcp-json) names, then run the sign-in again.

## Network and connection errors

### MCP server connection timed out during a sleep or clock change

This message means a connection to an [MCP server](https://code.claude.com/docs/en/mcp.md) timed out, and Claude Code found that your system clock jumped forward during the attempt:

```text theme={null}
MCP server "<name>" connection timed out. Your computer went to sleep or its clock changed while connecting.
```

Claude Code can't tell whether your computer slept or its clock was set forward, so the message names both.

**What to do:**

Connect to the server again, and keep your computer awake until the attempt finishes. If the server connects, you have nothing to fix.

* **In an interactive session**: run `/mcp`, select the server, and select **Reconnect**
* **In your shell**: run the [`claude -p`](https://code.claude.com/docs/en/headless), [`claude mcp list`](https://code.claude.com/docs/en/mcp#managing-your-servers), or `claude mcp get` command again. If the server then fails with a message that starts `Skipping connection (recent failure cached`, wait 15 minutes and run the command again.
* **In an [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) application**: call [`reconnectMcpServer()`](https://code.claude.com/docs/en/agent-sdk/typescript#methods) in TypeScript or [`ClaudeSDKClient.reconnect_mcp_server()`](https://code.claude.com/docs/en/agent-sdk/python#methods) in Python
* **If the server fails again**: if the message differs from this one, see [what to check when an MCP server doesn't connect](https://code.claude.com/docs/en/mcp-quickstart.md#troubleshooting). If this message comes back although your computer stayed awake and nothing changed its clock, see [Report an error](#report-an-error).

Before v2.1.307, Claude Code showed a timeout message such as `MCP server "<name>" connection timed out after <N>ms` instead of this one.

## Request errors

### Tool input schema is invalid

A tool in the request declared an `input_schema` that fails the API's JSON Schema validation, so the API rejected the whole request. The number after `tools.` is the failing tool's position in the request's tool list, not a name you can look up.

```text theme={null}
API Error: 400 ... tools.N.custom.input_schema: JSON schema is invalid
API Error: 400 ... tools.N.custom.input_schema.properties: Property keys should match pattern '^[a-zA-Z0-9_.-]{1,64}$'
```

The first form means the schema isn't valid JSON Schema draft 2020-12. The second means a top-level property name doesn't match the pattern the message quotes.

Claude Code [excludes MCP tools whose input schema would fail this validation](https://code.claude.com/docs/en/mcp.md#tools-with-invalid-input-schemas) when it loads a server's tools, so requests normally never include one.

On a [deployment where flag fetching is off](https://code.claude.com/docs/en/env-vars.md#features-that-need-feature-flag-fetching), or on a machine whose flags have never arrived, Claude Code records in the server's log which tool would be rejected but sends it anyway, so this error can still occur.

The error can also occur for a tool whose schema declares a JSON Schema dialect other than draft 2020-12 in `$schema`. Claude Code doesn't check those schemas against the JSON Schema meta-schema, though the top-level property-name check still applies.

Before v2.1.216, no deployment ran the exclusion checks.

**What to do:**

* If your Claude Code version is earlier than v2.1.300, run [`claude update`](https://code.claude.com/docs/en/setup#update-claude-code) in your shell. Before v2.1.300, Claude Code didn't [retry the request without the rejected tool's parameters](https://code.claude.com/docs/en/mcp.md#tools-whose-input-schema-the-api-refuses), so this error repeated on every request that included the tool.
* Remove or [disable](https://code.claude.com/docs/en/mcp.md#disable-a-server-without-removing-it) the MCP server that declares the invalid schema. The error names the tool only by position. On v2.1.216 or later, check each server's log for a line naming a tool whose input schema would be rejected. If no log names one, disable servers one at a time.
* If you maintain the server, fix the tool's `input_schema`. The schema must be valid JSON Schema, and top-level property names must be 1 to 64 characters long and use only ASCII letters and digits, `_`, `.`, and `-`. See [Tools with invalid input schemas](https://code.claude.com/docs/en/mcp.md#tools-with-invalid-input-schemas).

### MCP tool name over 128 characters

An MCP server lists a tool whose full name, such as `mcp__<server>__<tool>`, is longer than the 128 characters the API accepts. Claude Code [leaves that tool out of the tools it sends to Claude](https://code.claude.com/docs/en/mcp.md#tools-with-names-longer-than-128-characters), and the server's other tools keep working. In a session you start with `claude --debug` from your shell, Claude Code writes this message to the debug log at `~/.claude/debug/<session-id>.txt`:

```text theme={null}
Tool "mcp__<server>__<tool>" is not sent to Claude: its name has <N> characters and the API accepts at most 128
```

**What to do:**

* If you maintain the server, shorten the tool's name.
* If the server is in your [MCP configuration](https://code.claude.com/docs/en/mcp.md#mcp-installation-scopes), give it a shorter name there, such as `db` in place of `analytics-database`. Then update what refers to the server or its tools by the old name, such as [permission rules](https://code.claude.com/docs/en/permissions.md#mcp) and [hook matchers](https://code.claude.com/docs/en/hooks.md#match-mcp-tools).
* If a [plugin bundles the server](https://code.claude.com/docs/en/mcp.md#plugin-provided-mcp-servers), the tool's full name also includes the plugin name. Ask the plugin's maintainer to shorten the server or tool name.

Before v2.1.292, Claude Code sent the tool anyway, and the API rejected every request that included it with `API Error: 400 ... tools.N.custom.name: String should have at most 128 characters`.

### Model is restricted by your organization's settings

Your organization admin has disabled this model in the claude.ai admin console, or managed settings exclude it through an [`availableModels`](https://code.claude.com/docs/en/model-config#restrict-model-selection) allowlist or a [`deniedModels`](https://code.claude.com/docs/en/model-config#block-specific-models-or-versions) list. The notice appears at startup when `--model`, `ANTHROPIC_MODEL`, or the `model` setting named the restricted model, and it names the model the session uses instead. If managed settings leave no permitted model for the session to use, see [Managed settings block the default model](https://code.claude.com/docs/en/errors#managed-settings-block-the-default-model). The substitution notice can also appear mid-session after an admin disables the model a session is running on in the claude.ai admin console.

```text theme={null}
Model "claude-opus-4-8" is restricted by your organization's settings. Using claude-sonnet-4-6 instead.
```

Typing `/model <name>` for a restricted model is rejected and the session keeps its current model. For a model disabled in the admin console, the rejection reads `Model '<name>' is restricted by your organization's settings. Run /model to choose a different model.` For a model that managed settings exclude, it reads `Model '<name>' is not available. Your organization restricts model selection.`

A notice prefixed with an agent, skill, or command name means the restriction applied to that [subagent's requested model](https://code.claude.com/docs/en/sub-agents.md#choose-a-model): the subagent runs on the substituted model and your session's model is unchanged. Before v2.1.223, Claude Code showed the notice only for subagents launched with the Agent tool.

Claude Code treats a model family alias, one of `opus`, `sonnet`, `haiku`, or `fable`, as a request for that family rather than for its newest version. On the Anthropic API and on [Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws.md), a restricted family alias resolves to the newest version of the family that your organization's settings permit, and the substitution notice names that version. Claude Code rejects `/model <alias>` only when every version of the family is restricted. Before v2.1.205, a family alias was substituted or rejected based on its newest version alone, even when an older version of the same family was allowed.

**What to do:**

* Run `/model` to pick from the models your organization allows. Restricted models are hidden from the picker.
* If the restricted model was set in `--model`, `ANTHROPIC_MODEL`, the `model` field of a settings file, or the `model` frontmatter of a [subagent](https://code.claude.com/docs/en/sub-agents.md#choose-a-model), skill, or command, remove or update that value so the notice doesn't recur
* If you need access to the restricted model, ask your organization admin to enable it. See [Organization model restrictions](https://code.claude.com/docs/en/model-config.md#organization-model-restrictions).

### Model switch was blocked by a PreModelSwitch hook

A [PreModelSwitch hook](https://code.claude.com/docs/en/hooks.md#premodelswitch) didn't approve the model switch you or a client requested, so the session keeps its current model. When the switch came from an [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) host or [Remote Control](https://code.claude.com/docs/en/remote-control.md) rather than a command you typed, the message reads `Model switch blocked by a PreModelSwitch hook` without naming the target model.

```text theme={null}
Model switch to Opus 4.6 was blocked by a PreModelSwitch hook: Opus 4.6 is retired for this project. Use a newer model.
```

The reason after the colon says what refused the switch:

* **A reason a hook wrote**: a PreModelSwitch hook supplied that reason when it [denied the switch or asked for confirmation](https://code.claude.com/docs/en/hooks.md#premodelswitch-decision-control). Address what it asks, or pick a model your hooks allow.
* **`PreModelSwitch hook <name> did not respond before its timeout`**: a hook that doesn't answer before its [timeout](https://code.claude.com/docs/en/hooks.md#timeouts) blocks the switch. Fix the hanging command or raise that hook's `timeout`, then switch again.
* **`confirmation required, and this session cannot ask`**: a hook answered `ask` without a reason, and a control request has no way to show the confirmation prompt. A `/model` command in a [`-p` run](https://code.claude.com/docs/en/headless) reports the same condition with `(run /model interactively to confirm)` after the reason. Make the switch from an interactive session, or change the hook's decision for this model.
* **`so organization-managed PreModelSwitch hooks could not be checked`**: Claude Code couldn't tell which PreModelSwitch hooks your organization's [managed plugins](https://code.claude.com/docs/en/settings-reference.md#enabledplugins) deliver, for example because a managed plugin failed to load. One of those hooks might block the switch, so Claude Code refuses rather than apply the switch unchecked. The start of the reason names what failed. Claude Code re-checks on every switch attempt, so a failure that has since cleared stops blocking; if it keeps failing, run `claude --debug` and switch again to capture the details, then fix the plugin or ask your admin to fix it.
* **`a PreModelSwitch hook failed before answering`** or **`PreModelSwitch hooks were cancelled (the control stream closed) before answering`**: the hook run ended without a verdict, and Claude Code doesn't treat that as approval. Run `claude --debug` to see what failed, then switch again.

Before v2.1.260, the managed-plugin refusal read `plugin hooks could not be loaded, so PreModelSwitch hooks could not be checked; see the debug log`. Claude Code retried the plugin load once and then refused later switches in the session, even when your organization managed no plugins. Restart the session to run the plugin load again on those versions.

### Safeguards flagged a request for Claude's reasoning

The API declined the request because safeguards flagged it as asking the model to reproduce its internal reasoning in the response. The API names this [refusal category](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#refusal-response) `reasoning_extraction`, and the refusal message includes this line:

```text theme={null}
Details: `[reasoning_extraction]`
```

Before v2.1.234, refusal messages didn't include the `Details` line.

**What to do:**

* Remove or reword any instruction that asks Claude to write out its thinking or reasoning verbatim or in a fixed format, such as a `<thinking>` section, a scratchpad section, or a `reasoning` field in JSON output. The instruction can be in your prompt or in a customization that Claude Code loads with it, such as CLAUDE.md, a skill, a subagent prompt, an output style, or an MCP tool description.
* To check whether a customization is the trigger, run [`claude --safe-mode`](https://code.claude.com/docs/en/cli-reference#cli-flags) in your terminal to start a session with customizations disabled, then send the same prompt
* After you change a customization, start a new session
* To reword a prompt you already sent, see [Rewind and summarize](https://code.claude.com/docs/en/checkpointing.md#rewind-and-summarize)
* You can still ask Claude to explain its answer. Ask for a short explanation, the evidence behind a result, or a summary of the actions it took. To read summaries of Claude's thinking, see [`showThinkingSummaries`](https://code.claude.com/docs/en/settings-reference#showthinkingsummaries).
* For more examples, and what to do if a reworded request is still declined, see [Keep reasoning in thinking blocks](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#keep-reasoning-in-thinking-blocks)

## Command-line errors

### Cannot add MCP server when managed settings allow only plugin servers

You ran `claude mcp add` or `claude mcp add-json` while your organization's managed settings set [`strictPluginOnlyCustomization`](https://code.claude.com/docs/en/settings-reference#strictpluginonlycustomization) to `true` or to a list that includes `mcp`. With that setting, Claude Code doesn't load MCP servers from `~/.claude.json` or `.mcp.json`, so the command exits with code 1 instead of saving a server that would never load:

```text theme={null}
Cannot add MCP server: your organization's managed settings allow only MCP servers that plugins provide. Install a plugin that provides this server, or ask your administrator to make it available.
```

`claude mcp add-from-claude-desktop` reports each server you select as not imported, with this message as the reason. [`/import`](https://code.claude.com/docs/en/commands#all-commands) reports this message for each MCP server it tries to add and still imports the other items it found.

Before v2.1.284, these commands saved the server and reported success, and the server never loaded.

**What to do:**

* Install a [plugin](https://code.claude.com/docs/en/plugins/install.md) that provides the server
* Ask your administrator to distribute the server in a [plugin](https://code.claude.com/docs/en/plugins/org.md), or to provide it through [`managedMcpServers`](https://code.claude.com/docs/en/settings-reference#managedmcpservers) if it's a remote HTTP or SSE server

### Server rejected the Authorization header minted by the configured headersHelper

An MCP server whose [`headersHelper`](https://code.claude.com/docs/en/mcp#use-dynamic-headers-for-custom-authentication) supplies the `Authorization` header answered the connection with HTTP 401 or 403, so Claude Code reports the connection as failed. Because the helper supplies the `Authorization` header, Claude Code [doesn't fall back to OAuth](https://code.claude.com/docs/en/mcp.md#authenticate-with-remote-mcp-servers) for the server:

```text theme={null}
Server rejected the Authorization header minted by the configured headersHelper (HTTP 401). Check that the helper command returns a valid credential for this MCP endpoint — OAuth fallback is disabled when the helper supplies Authorization.
```

Claude Code re-runs the helper on each connection attempt, so a retry after a transient rejection, such as a token-rotation race, can succeed with a fresh credential.

**What to do:**

* Run the `headersHelper` command yourself the way Claude Code runs it: from the [directory Claude Code runs it in](https://code.claude.com/docs/en/mcp.md#where-the-helper-runs), with the [environment variables Claude Code sets for it](https://code.claude.com/docs/en/mcp.md#use-dynamic-headers-for-custom-authentication), and without the [credential variables Claude Code removes](https://code.claude.com/docs/en/mcp.md#which-variables-a-helper-can-read) for a server from a project `.mcp.json`, a plugin, or a project agent file. Check that it prints an `Authorization` value the server's endpoint accepts
* After fixing the helper or its credential source, select the server in `/mcp` and choose **Reconnect**

Before v2.1.248, Claude Code ran OAuth discovery for a server whose helper supplied the `Authorization` header. That discovery could fail with `Incompatible auth server: does not support dynamic client registration` instead of reporting the rejected credential.

### MCP server rejected the elicitation capability

An MCP server built on Java MCP SDK 0.11.0 through 0.17.0 refused the connection. Those SDK versions can't parse the `form` and `url` [elicitation modes](https://code.claude.com/docs/en/mcp.md#elicitation-modes-claude-code-declares) that Claude Code declares in its handshake. The message reads:

```text theme={null}
This server (Java MCP SDK 0.17.0 or older) rejected Claude Code's elicitation capability. Set "bareElicitationCapability": true for it, or upgrade to Java MCP SDK 0.17.1+ (Spring AI 1.0.7+ or 1.1.6+).
```

**What to do:**

* Upgrade the server to Java MCP SDK 0.17.1 or later, or to one of the Spring AI releases the message names
* Or add `"bareElicitationCapability": true` to that server's entry in your MCP configuration, then restart Claude Code. The field is accepted on stdio, `sse`, `http`, and `ws` entries and requires Claude Code v2.1.281 or later

This `.mcp.json` entry sets the field for one HTTP server:

```json theme={null}
{
  "mcpServers": {
    "inventory": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "bareElicitationCapability": true
    }
  }
}
```

After the restart, `/mcp` shows the server as connected. Claude Code declares form mode only to that server, so remove the field once you upgrade it.

A server can also fail with its own error text, such as one containing `Unrecognized field "form"`. The same fixes apply.

### OAuth callback port is already in use

When you sign in to a remote MCP server with OAuth, Claude Code starts a local listener to receive the sign-in callback. If the port that listener needs is held by another process, the sign-in fails with this message. This mostly happens with a [fixed callback port](https://code.claude.com/docs/en/mcp.md#use-a-fixed-oauth-callback-port) set through the [`MCP_OAUTH_CALLBACK_PORT`](https://code.claude.com/docs/en/env-vars) variable or `--callback-port`, since without one Claude Code picks an available port.

```text theme={null}
OAuth callback port <port> is already in use — another process may be holding it. Run `lsof -ti:<port> -sTCP:LISTEN` to find it.
```

On Windows, the suggested command is `netstat -ano | findstr :<port>` instead.

**What to do:**

* Run the command from the message to find the process holding the port, and stop it or wait for it to finish
* If another program needs that port permanently, register a different redirect URI with the server and set its port with `MCP_OAUTH_CALLBACK_PORT` or `--callback-port`, whichever you use
* Then start the sign-in again, for example by selecting the server in `/mcp`

### No available ports for OAuth redirect

When you sign in to a remote MCP server with [OAuth](https://code.claude.com/docs/en/mcp.md#authenticate-with-remote-mcp-servers), Claude Code starts a local listener to receive the sign-in callback. The sign-in fails with this message when Claude Code can't bind a local port for it. Something on the machine is preventing it from listening on `127.0.0.1`, for example security software or a sandbox policy that denies local listeners.

```text theme={null}
No available ports for OAuth redirect
```

Before v2.1.268, Claude Code didn't fall back to an operating-system-assigned port, so the message also appeared when only its self-picked ports couldn't be bound. That can happen on Windows hosts where Hyper-V reserves port ranges that cover the ports Claude Code picks from.

**What to do:**

* Check whether security software or a sandbox policy blocks processes from listening on `127.0.0.1`, and allow Claude Code to bind a local port
* Then start the sign-in again, for example by selecting the server in `/mcp`

### /security-review fails without origin/HEAD

[`/security-review`](https://code.claude.com/docs/en/commands#all-commands) builds its review context by diffing your branch against `origin/HEAD`, the local ref that records which branch is the default on your `origin` remote. When that ref doesn't exist, the git commands that gather the diff fail and the review stops before it starts.

```text theme={null}
Error: Shell command failed for pattern "!`git diff --name-only origin/HEAD...`": [stderr]
fatal: ambiguous argument 'origin/HEAD...': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
```

Claude Code shows the same error for any skill that [injects dynamic context](https://code.claude.com/docs/en/skills.md#when-an-injected-command-fails), and a failed injected command aborts that skill's invocation.

Sibling strings fire before the command runs at all:

* `Shell command permission check failed for pattern "..."`: the command's permission check didn't allow it. [Permission checks on injected commands](https://code.claude.com/docs/en/skills.md#permission-checks-on-injected-commands) covers which results abort in each permission mode and how to pre-approve a command with `allowed-tools`
* ``Skill <name> requires bash (`shell: bash` in frontmatter) but Git Bash was not found``: the skill's frontmatter demands bash on a machine without it. Install Git for Windows or change the frontmatter to `shell: powershell`. See [How injected commands run](https://code.claude.com/docs/en/skills.md#how-injected-commands-run)

### No shell command in a skill or command was run

`No shell command in <name> was run` means a `` !`<command>` `` [dynamic context command](https://code.claude.com/docs/en/skills.md#inject-dynamic-context) in that skill or command file contains a character that the Bash or PowerShell tool refuses:

* **Either tool**: a raw control character other than a tab or newline
* **PowerShell tool**: also U+FEFF or U+180E

The message ends with the refused command, showing each refused character as `�`, as in this Bash tool example:

```text theme={null}
No shell command in /my-skill was run, because the Bash tool does not accept one of them: command contains control characters that would be hidden in the approval dialog. Unprintable characters are shown as � below: remove them from the skill or command file, or from the arguments or options substituted into it.
build.sh --target�dist
```

**What to do:**

* Find each `�` in the command quoted at the end of the message. Remove the character it stands for from the [skill or command file](https://code.claude.com/docs/en/skills.md#where-skills-live), or from the arguments or [options](https://code.claude.com/docs/en/plugins/manifest-reference.md#user-configuration) substituted into the file.

### Unknown command

In an interactive terminal session, you submitted a `/` name that doesn't match any command in this session, so Claude Code reports the name instead of running anything:

```text theme={null}
Unknown command: /hepl. Did you mean /help?
```

Claude Code suggests the closest command name or alias that the menu lists in this session. When nothing is close, the message ends after the name. The cause is usually one of the following:

* A typo, such as `/hepl` for `/help`. [How the command menu matches what you type](https://code.claude.com/docs/en/commands.md#how-the-command-menu-matches-what-you-type) covers picking a close match before you submit
* A command from a [plugin](https://code.claude.com/docs/en/plugins/overview.md) or [MCP server](https://code.claude.com/docs/en/mcp.md#use-mcp-prompts-as-commands) that isn't installed or connected in this session

**What to do:**

* Run the suggested name, or type `/` followed by part of the name to see what's available in this session
* If Claude Code reports a documented command as unknown, check its row in the [commands reference](https://code.claude.com/docs/en/commands.md) for the requirement it names

## Plugin errors

These errors come from [plugin](https://code.claude.com/docs/en/plugins/overview.md) and [marketplace](https://code.claude.com/docs/en/plugins/overview.md) configuration. For plugin problems that don't produce one of the messages on this page, such as a marketplace URL that doesn't load or a plugin that installs but doesn't appear, see [Plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md).

### plugin eval is currently in early access

You ran [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals) or `claude plugin eval init` and it exited 1 with one of these messages before doing anything:

```text theme={null}
`plugin eval` is currently in early access
```

```text theme={null}
`plugin eval` is currently unavailable
```

The first message means your build is older than v2.1.269, the first version where the command is generally available. The second means Anthropic has switched the command off server-side; nothing on your machine turns it back on.

**What to do:**

* Run `claude --version`, then `claude update`, and run the command again in a fresh session. See the [requirements for plugin evals](https://code.claude.com/docs/en/plugin-evals.md#requirements)
* If you see the second message on a current build, try again later after another `claude update`

### Marketplace is registered from an untrusted source

The marketplace is registered under a name that is [reserved for official Anthropic marketplaces](https://code.claude.com/docs/en/plugins/marketplace-reference.md#marketplace-file), but its registered source isn't an `anthropics` GitHub repository. Claude Code re-checks reserved names every time it loads or refreshes a marketplace, so the marketplace and the plugins installed from it stop loading. Before v2.1.205, an entry registered before its name became reserved kept loading.

```text theme={null}
Marketplace "claude-community" is registered from an untrusted source: The name 'claude-community' is reserved for official Anthropic marketplaces. Only repositories from 'github.com/anthropics/' can use this name. To fix it, remove the marketplace and re-add it from the official source.
```

For a marketplace whose source isn't a GitHub repository or a Git URL, such as a local directory, the middle sentence reads `can only be used with GitHub sources from the 'anthropics' organization` instead. `claude plugin marketplace add` runs the same check, and refuses a reserved name with `Failed to add marketplace:` followed by the same reserved-name sentence.

**What to do:**

* If the marketplace is already registered, run `claude plugin marketplace remove <name>`, then add it again from the official `github.com/anthropics` repository
* If you publish a third-party marketplace that used the name before it became reserved, rename it and ask users to re-add it from your source
* See the reserved name list under [Marketplace schema](https://code.claude.com/docs/en/plugins/marketplace-reference.md#marketplace-file)

### Marketplace name is another spelling of a reserved name

The marketplace's name isn't itself a reserved name, but Claude Code treats it as another spelling of one. [Reserved names](https://code.claude.com/docs/en/plugins/marketplace-reference.md#reserved-name-spellings) lists which spellings count as a reserved name. Claude Code refuses such a name when you add the marketplace:

```text theme={null}
Failed to add marketplace: "claude.code.plugins" is another spelling of "claude-code-plugins", a reserved marketplace name.
```

When a marketplace is already registered under such a name, its entry stops loading, and `/plugin`, `claude plugin install`, and `claude plugin update` warn:

```text wrap theme={null}
known_marketplaces.json has an entry named "claude.code.plugins", another spelling of the reserved marketplace name "claude-code-plugins", so it is ignored. Remove it with: claude plugin marketplace remove claude.code.plugins
```

When the name would need shell quoting, the add-time refusal reads `This marketplace's name is another spelling of "<reserved>", a reserved marketplace name. It is not exactly the reserved name it appears to be.`

**What to do:**

* Rename the marketplace to a name that doesn't spell a reserved name and add it again
* For the ignored-entry warning, run the `claude plugin marketplace remove` command it gives, or remove the entry from `~/.claude/plugins/known_marketplaces.json`

### Claude Code refuses the marketplace name

A registered marketplace's name [impersonates an official Anthropic marketplace](https://code.claude.com/docs/en/plugins/marketplace-reference.md#reserved-names) under the rules that section lists.

If a marketplace was registered under such a name before the check blocked it, the marketplace and the plugins installed from it stop loading, because Claude Code checks the name every time it reads the marketplace's catalog. When the name imitates an official one, `claude plugin list` and the `/plugin` **Errors** tab report each affected plugin with a message that begins:

```text theme={null}
Claude Code refuses the marketplace name "anthropic-plugins-v2"
```

For an imitating name, the marketplace's own error reads `Claude Code refuses this marketplace's name: it looks like one of Anthropic's own` instead. `claude plugin marketplace add` refuses any impersonating name with `Marketplace name impersonates an official Anthropic/Claude marketplace`.

Before v2.1.282, `claude plugin list` and `/plugin` reported the plugins of an imitating name as failed to load too, without naming the marketplace's name as the cause.

**What to do:**

* To keep a marketplace that a settings file declares inline with `"source": "settings"`, rename it before you remove the old name, because removing the marketplace also deletes its entry from your settings files. Claude Code v2.1.292 or later lists these steps in the message:
  1. In each settings file that lists the marketplace under `extraKnownMarketplaces`, give the entry's key and its `source.name` one new plain-ASCII name that doesn't look like an official one. If an administrator adds the marketplace through your organization's managed settings, the administrator does this step
  2. Run `claude plugin marketplace remove <old-name>`, or remove the old name in the **Marketplaces** tab in `/plugin`. This also uninstalls its plugins and deletes their data, options, and secrets
  3. Start Claude Code again, in the project's folder if the file is a project's settings file. Then install the plugins from the renamed marketplace
* To keep any other marketplace, wait until its maintainer renames it, then run `claude plugin marketplace update <name>`
* To remove the marketplace, run `claude plugin marketplace remove <name>`. This also uninstalls the plugins installed from the marketplace and deletes their data, options, and secrets
* If you publish the marketplace, rename it in your `marketplace.json`; users then update the marketplace instead of removing it

### Marketplace is already added from a different source

You named a new marketplace source with [`--marketplace <source>` on the install command](https://code.claude.com/docs/en/plugins/install#add-a-marketplace-and-install-in-one-command), in a session or from your shell. The catalog Claude Code fetched from that source has the same name as a marketplace you already added from a different source. Claude Code keeps the existing marketplace instead of replacing it, and the plugin isn't installed.

```text theme={null}
Marketplace "acme-tools" is already added from a different source (github:acme/plugins). To use this source instead, remove that marketplace first with /plugin marketplace remove acme-tools.
```

**What to do:**

* If the marketplace you already added is the one you want, install from it by name: `/plugin install <plugin>@<name>`
* To switch to the new source, run `/plugin marketplace remove <name>`, then retry the install

### Plugin command references user\_config in a shell command

A plugin hook, [monitor](https://code.claude.com/docs/en/plugins/components.md#monitors), or MCP [`headersHelper`](https://code.claude.com/docs/en/mcp#use-dynamic-headers-for-custom-authentication) command references a `${user_config.KEY}` [plugin option](https://code.claude.com/docs/en/plugins/manifest-reference.md#user-configuration), and the substituted string would be passed to a shell. A configured value containing `$(...)`, backticks, or `;` would run as code there, so Claude Code refuses to start the component instead of substituting the value. The check runs on the command template, so the error appears even when no value is configured yet. Before v2.1.207, the value was substituted into the shell command.

The wording depends on which surface referenced the option. A shell-form hook reports:

```text theme={null}
Hook from plugin formatter@acme-tools references ${user_config.*} in a shell-form command. The substituted value would be re-parsed by the shell. Use exec form instead — {"command": "<executable>", "args": ["${user_config.KEY}", ...]} — or read $CLAUDE_PLUGIN_OPTION_<KEY> from the hook's environment. Command: ./scripts/notify.sh ${user_config.webhook_url}
```

A monitor reports:

```text theme={null}
Monitor "deploy-status" from plugin deploy-tools references ${user_config.*} in its command. The substituted value would be passed to a shell. Monitor commands cannot safely reference ${user_config.*}; have the monitor script read the value from a config file or prompt instead.
```

An MCP `headersHelper` reports:

```text theme={null}
headersHelper for MCP server 'internal-api' references ${user_config.*}. The substituted value would be passed to a shell; read the value inside the helper script instead (e.g. from an env var set in the server's "env" block).
```

**What to do:**

* For a hook, add an `args` array so it runs in [exec form](https://code.claude.com/docs/en/hooks.md#exec-form-and-shell-form), where each `${user_config.KEY}` becomes one argument with no shell in between. Or drop the reference and read the `$CLAUDE_PLUGIN_OPTION_<KEY>` environment variable inside the script
* For a monitor, drop the reference and have the monitor script read the value from a config file
* For a `headersHelper`, move `${user_config.KEY}` into the server's `headers` field, which isn't shell-parsed, or read the value inside the helper script

### Path escapes plugin directory

One of the plugin's component paths leads outside the plugin directory or couldn't be confirmed inside it, so Claude Code drops that path and loads the rest of the plugin. For a path the plugin declares in `plugin.json` or its [marketplace entry](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-entries), the component name in the message, such as `commands` or `hooks`, names the field that declared the path.

```text theme={null}
commands path escapes plugin directory: ./../shared.md
```

In `claude plugin` command output, the same error reads `Path escapes plugin directory: ./../shared.md (commands)`.

Claude Code rejects both a path that points outside the plugin as written, such as `../shared-utils`, and a symlink that leads outside the plugin and isn't one the [marketplace symlink rules](https://code.claude.com/docs/en/plugins/host-marketplace.md#share-files-within-a-marketplace-with-symlinks) allow. For a symlink, the message also says where the path resolves:

```text theme={null}
commands path escapes plugin directory: ./commands/deploy.md — it resolves to /home/user/shared/deploy.md, outside the plugin directory
```

A message that gives the full path of one of a marketplace plugin's own files, such as `hooks/hooks.json`, means Claude Code skipped that file. That happens when Claude Code can't confirm the file is inside the plugin or, for a plugin in a [local marketplace](https://code.claude.com/docs/en/plugins/loading.md#in-place-and-copied-plugins), inside that marketplace. The message reports each of these files under the component name shown:

* `hooks/hooks.json`: `hooks`
* `monitors/monitors.json`: `monitors`
* `settings.json`: `settings`
* `SKILL.md` at the plugin root: `skills`

For example, this message is for a `hooks/hooks.json` that resolves outside both the plugin and its local marketplace:

```text theme={null}
hooks path escapes plugin directory: /home/user/my-marketplace/my-plugin/hooks/hooks.json — it resolves to /home/user/dotfiles/hooks.json, outside the plugin directory and its marketplace directory
```

On macOS and Linux, Claude Code also rejects a component path that contains a backslash anywhere in it, even when the path stays inside the plugin. A plugin whose component paths use Windows-style separators loads on Windows and triggers this rejection on the other platforms:

```text theme={null}
commands path escapes plugin directory: ./commands\deploy.md — its path contains a backslash, which is not resolved reliably on this platform
```

Before v2.1.251, Claude Code loaded a `commands` path declared in a marketplace entry even when it pointed outside the plugin directory.

Before v2.1.257, the check on paths the plugin declares looked only at the path's spelling, not at where a symlink leads.

**What to do:**

* If you installed the plugin and don't maintain it, report the message to its author
* For a path the plugin declares, move the referenced file inside the plugin directory and point the path at it with a `./` relative path
* If the path, or a folder above it inside the plugin, is a symlink leading outside the plugin, replace the symlink with a copy of what it points to
* If the message says a path the plugin declares contains a backslash, write the path with forward slashes, for example `./commands/deploy.md`
* If the message ends with `EACCES`, restore your execute permission on every directory leading to the file or folder the path names. Check the directories above the path, then follow each symlink you reach and check the directories leading to where it points. For any other error code, look it up in the [causes and steps for a path that couldn't be checked](#path-could-not-be-checked).
* To share files with other plugins in the same marketplace, link them with a symlink inside the plugin directory, following the [symlink rules](https://code.claude.com/docs/en/plugins/host-marketplace.md#share-files-within-a-marketplace-with-symlinks)

### Plugin not loaded: its manifest was not read

Claude Code couldn't confirm that a marketplace plugin's [manifest](https://code.claude.com/docs/en/plugins/manifest-reference.md) at `.claude-plugin/plugin.json` is inside the plugin, so it loads nothing from that plugin. For a plugin in a [local marketplace](https://code.claude.com/docs/en/plugins/loading.md#in-place-and-copied-plugins), Claude Code also couldn't confirm that the manifest is inside that marketplace. The message appears in the `/plugin` **Errors** tab, and the reason at its end says what Claude Code found.

For example, this message is for a plugin in a local marketplace whose `.claude-plugin` folder is a symlink leading outside the marketplace:

```text theme={null}
Plugin not loaded: its manifest /home/user/my-marketplace/my-plugin/.claude-plugin/plugin.json was not read, because it resolves to /home/user/dotfiles/my-plugin/.claude-plugin/plugin.json, outside the plugin directory and its marketplace directory
```

**What to do:**

* If the reason ends with `EACCES`, restore your execute permission on every directory leading to the manifest. Check the directories above the manifest, then follow each symlink you reach and check the directories leading to where it points. For any other error code, look it up in the [causes and steps for a path that couldn't be checked](#path-could-not-be-checked).
* If you maintain the plugin and the reason says where the manifest resolves, the `.claude-plugin` folder or `plugin.json` itself is a symlink that leads there. Replace that link with a copy of what it points to.
* If you installed the plugin and don't maintain it, report the message to its author

### Path could not be checked

Claude Code asked the operating system whether a plugin path exists and got an error other than "not found", so it doesn't load what the path names. How much of the plugin loads depends on which path failed:

* One of a plugin's [default component locations](https://code.claude.com/docs/en/plugins/manifest-reference.md#standard-layout), such as the `skills/` folder, the `monitors/monitors.json` file, or a [`SKILL.md` at the plugin root](https://code.claude.com/docs/en/plugins/components#skills): the plugin's other components still load
* The plugin's own directory: nothing from that plugin loads

You don't see this error for a path that doesn't exist at all. In `/plugin`, the error appears under the plugin and names the path and the code the operating system returned:

```text theme={null}
skills path could not be checked: /home/user/my-plugin/skills (ELOOP)
```

In `claude plugin list`, the same error reads `Path not found: /home/user/my-plugin/skills (skills, ELOOP)`.

Causes that produce this error include:

* `ELOOP`: a symlink in the path points at itself or forms a loop
* `EIO` or `ESTALE`: the path is on a network mount that is broken or stale
* `EACCES`: one of the directories above the path denies you permission to traverse it

**What to do:**

* Replace a symlink that points at itself with a real folder, or delete it
* If the path is on a network mount, remount the share
* If the code is `EACCES`, restore your execute permission on the directories above the path
* Run `/reload-plugins` after fixing the path, or restart Claude Code, to load the plugin or component

Before v2.1.265, Claude Code treated a default component folder it couldn't check as absent and loaded the plugin without that component, with no error.

### Marketplace entry path does not stay inside the marketplace directory

The plugin's [marketplace entry](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-entries) declares a source path that Claude Code can't resolve to a location inside the marketplace's own directory, so the plugin doesn't install or load. The refusal covers:

* An entry path that is absolute, climbs out of the marketplace with `..`, or is spelled like a network path
* On macOS and Linux, an entry path that contains a backslash anywhere after the leading `./`
* An entry in a marketplace fetched from a remote source, such as git or a URL, that reaches its target through a symlink resolving outside the marketplace directory
* A relative entry in a marketplace added from a direct URL to its `marketplace.json`: Claude Code downloads only that file, so no local plugin files exist for the path to name. See [Plugins with relative paths fail in URL-based marketplaces](https://code.claude.com/docs/en/plugins/troubleshooting.md#plugins-with-relative-paths-fail-in-url-based-marketplaces)

`claude plugin install` reports the refusal like this:

```text theme={null}
Cannot install my-plugin@my-marketplace: its marketplace entry path does not stay inside the marketplace directory (an absolute, climbing, network-shaped, backslash-containing or link-traversing entry, an entry of a fetched marketplace that resolves or opens outside its tree — or a relative entry in a url-catalog marketplace, which has no local directory)
```

When an already-installed plugin's entry fails the same check, `claude plugin list` shows the plugin as `failed to load` with:

```text theme={null}
Plugin source path refused: ./my-plugin does not stay inside its marketplace directory. Check that the marketplace entry has a plain relative path.
```

**What to do:**

* If you maintain the marketplace, write the entry's `source` as a plain relative path with forward slashes, such as `./plugins/my-plugin`, and keep any symlink it crosses pointed inside the marketplace directory
* If you added the marketplace from a direct URL, relative entries can't resolve. Ask the marketplace author to use [another plugin source](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-sources), or add the marketplace from its git repository instead

### Failed to load marketplace configuration

Claude Code keeps the plugin marketplaces you've added in a registry file at `~/.claude/plugins/known_marketplaces.json`. A plugin command that needs the registry, such as `claude plugin install`, fails with one of two messages when Claude Code can't use the file:

* `Failed to load marketplace configuration`: the file exists but isn't valid JSON or can't be read. An empty file fails this way too.
* `Marketplace configuration file is corrupted`: the file is valid JSON but its contents don't match the registry schema.

With an empty file, `claude plugin install` reports:

```text theme={null}
✘ Failed to install plugin "my-plugin": Failed to load marketplace configuration: JSON Parse error: Unexpected EOF
```

Before v2.1.246, `claude plugin install` didn't report this failure.

**What to do:**

* Open `~/.claude/plugins/known_marketplaces.json` and repair the JSON, or fix the entries the message names as not matching the registry schema
* If you can't repair it, delete the file or replace its contents with `{}`, then re-add each marketplace with `claude plugin marketplace add <source>`. Claude Code re-registers the marketplaces your user or managed settings declare in [`extraKnownMarketplaces`](https://code.claude.com/docs/en/settings-reference#extraknownmarketplaces) the next time you start it in a folder you've trusted.

### Plugin was not uninstalled

You ran [`claude plugin uninstall`](https://code.claude.com/docs/en/plugins/cli-reference#plugin-uninstall), or chose **Uninstall** in the `/plugin` **Installed** tab, and the uninstall stopped with a message starting `"<plugin>" was not uninstalled:`. If the text after that colon starts with `installed_plugins.json` instead of naming a settings file, the cause is content in `installed_plugins.json` that this version of Claude Code can't read. For that form, see [`installed_plugins.json` holds a record this version can't read](https://code.claude.com/docs/en/plugins/troubleshooting#installed-plugins-json-holds-a-record-this-version-cannot-read).

When Claude Code removed the plugin's entry from `enabledPlugins` and read that scope's settings files back, either the plugin was still switched on there, or a file that could switch it on couldn't be read or checked. Deleting the plugin's saved options, secrets, and data while a settings entry could switch it back on would lose them, so the uninstall stops instead: the plugin stays installed and nothing it saved is deleted.

```text theme={null}
✘ Failed to uninstall plugin "formatter": "formatter" was not uninstalled: it is still switched on in /home/user/project/.claude/settings.local.json, although the settings change reported no error. It is still installed. Take it out of "enabledPlugins" in that file yourself, then uninstall it again.
```

The middle of the message names the file and the cause:

* `it is still switched on in <file>, although the settings change reported no error`: the settings write reported success but the entry is still there when the file is read back
* `it is still switched on in <file>, and the settings change failed (<error>)`: the file couldn't be saved, for the reason in parentheses
* `<file> is there and could not be read`: the file exists but couldn't be read as settings, for example because it isn't valid JSON, so it may still enable the plugin
* `<file> (not read: it is on a network path or is a link to one, or could not be checked)`: Claude Code didn't read the project or local settings file because the file, or the `.claude` folder that holds it, is a link that leads to a network location, or because it couldn't examine that path

`claude plugin uninstall` exits 1, and with `--json` the result carries `failureCode: "settings_still_on"`. `/plugin` shows the same message.

**What to do:**

* Follow the last sentence of the message: repair or replace the settings file it names, or remove the plugin's entry from `enabledPlugins` in that file yourself, then run the uninstall again

### Skipping connection (recent failure cached; retries automatically in 15 min, or edit the plugin config to retry now)

This message means Claude Code didn't start a stdio [MCP server that a plugin provides](https://code.claude.com/docs/en/mcp.md#plugin-provided-mcp-servers), because a connection to that server failed less than 15 minutes earlier:

```text theme={null}
Skipping connection (recent failure cached; retries automatically in 15 min, or edit the plugin config to retry now)
```

The session continues without the server's tools, and Claude Code doesn't try the server again in that session when the 15 minutes end. When you start a new session or [`claude -p`](https://code.claude.com/docs/en/headless) run at least 15 minutes after the most recent failed connection, Claude Code tries the server again.

**What to do:**

To have Claude Code try the server again without waiting:

* **In an interactive session**: run `/mcp`, select the server, and select **Reconnect**
* **In an [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md) application**: call [`reconnectMcpServer()`](https://code.claude.com/docs/en/agent-sdk/typescript#methods) in TypeScript or [`ClaudeSDKClient.reconnect_mcp_server()`](https://code.claude.com/docs/en/agent-sdk/python#methods) in Python with the server's name
* **In `claude -p`**: start an interactive session that loads the same plugin, on the same machine and with the same operating system account and [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars) value as your runs. Reconnect the server there from `/mcp`. Once it connects, Claude Code tries the connection in your next run.
* **If you're developing the plugin**: change the server's `command`, `args`, or `env` in the plugin's `.mcp.json` or `plugin.json`. Claude Code tries the connection in the next session or `claude -p` run that loads the changed entry.

The message replaces the error from the failed connection. If the new attempt fails too, Claude Code reports that attempt's error instead of this message.

## Tool errors

These errors come from Claude's tool calls. Claude corrects most tool errors on its own. When one needs a change from you, that error's **What to do** list says what to change.

### Agent would be spawned with zero tools

Every entry in the subagent's [`tools` list](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields) failed to match a usable tool, so Claude Code refused to launch the subagent: with no tools, it couldn't act. The message groups your entries by what went wrong:

* **Unrecognized**: the entry matches no tool name, usually a typo such as `Grpe` for `Grep`.
* **Not available to subagents**: the entry names a real tool that [subagents can't use](https://code.claude.com/docs/en/sub-agents.md#available-tools). Background subagents keep a smaller built-in tool set, so an entry that only a foreground subagent can use lands here when the subagent would run in the background, which is the default. If you list `Agent`, the message reports it under the next group instead.
* **Matched no tools in this session**: the entry is valid but no tool in the current session matches it right now, such as `mcp__github__*` with no GitHub MCP server connected, or `Agent` for a subagent at the [depth limit](https://code.claude.com/docs/en/sub-agents.md#let-subagents-spawn-their-own-subagents).

Omitting the `tools` field never triggers this refusal. If you leave the `tools` list empty, or `disallowedTools` removes every entry in it, Claude Code also skips the refusal and launches the subagent without tools.

Before v2.1.208, the subagent launched with no tools and could return an empty or confusing result.

```text theme={null}
Agent 'code-reviewer' would be spawned with zero tools — refusing. Its tools list resolved to nothing: unrecognized [Grpe]. Fix the agent's tools frontmatter or pass a different subagent_type.
```

**What to do:**

* Correct each entry the error names against the [tools available to subagents](https://code.claude.com/docs/en/sub-agents.md#available-tools)
* Remove entries for tools the session doesn't have, such as MCP tools from a server that isn't connected
* If the entry names a connected MCP server, compare the entry with that server's name as the server's [tool names](https://code.claude.com/docs/en/permissions.md#mcp) spell it, such as `reports__v2` in `mcp__reports__v2__get_totals`. For that server, write `mcp__reports__v2__*`, which is `mcp__` followed by the whole name and `__*`. With the shorter `mcp__reports`, which names a server called `reports`, the subagent gets none of the `reports__v2` tools
* For a tool that [background subagents drop](https://code.claude.com/docs/en/sub-agents.md#available-tools), such as `CronCreate`, remove the entry
* To keep a tool such as `CronCreate` instead, [let Claude wait for the subagent](https://code.claude.com/docs/en/sub-agents.md#let-claude-wait-for-a-subagent), since a subagent Claude waits for runs in the foreground and keeps the tool. If the definition sets `background: true`, remove that field first, because it keeps the subagent in the background
* Delete the `tools` field instead of listing tools to give the subagent every [tool available to subagents](https://code.claude.com/docs/en/sub-agents.md#available-tools)
* For a `tools` list that contains only `Agent`, raise the [depth limit](https://code.claude.com/docs/en/sub-agents.md#let-subagents-spawn-their-own-subagents) or give the agent at least one other tool: Claude Code withholds `Agent` at that limit, so a list with nothing else in it resolves to no tools

### Command contains an invisible character

The [PowerShell tool](https://code.claude.com/docs/en/tools-reference.md#powershell-tool) refused to run a command that contains U+FEFF or U+180E:

```text theme={null}
Error: command contains the invisible character U+FEFF (byte order mark) or U+180E (Mongolian vowel separator), and was not run. Remove the character, keep the text that needs it in a file that the command reads, or write it as $([char]0xFEFF) or $([char]0x180E) inside a double-quoted string
```

**What to do:**

* **For a command Claude wrote**: you have nothing to fix. The message tells Claude how to rewrite the command.
* **For a skill or command file**: the message follows `No shell command in <name> was run`. See [where to find the character and remove it](#no-shell-command-was-run).

## Configuration warnings

To find a warning that Claude Code gave at startup in an interactive session, look below the startup banner first, then in the debug log:

* **Row below the startup banner**: some warnings about [permission rules](https://code.claude.com/docs/en/permissions.md), such as [`⚠ Deny rule Bsh matches no tool · check for typos`](#matches-no-tool)
* **Debug log**: Claude Code keeps this log only in debug mode. To read the warnings in it, start Claude Code from your shell with `claude --debug-file <path>`, then open the file at that path.

In [non-interactive mode](https://code.claude.com/docs/en/headless.md) with text output, outside a [background session](https://code.claude.com/docs/en/agent-view.md), look for startup warnings on stderr.

Before v2.1.305, look on stderr in an interactive session as well, including for the permission-rule warnings that now show as rows below the banner.

### Agent descriptions are over the 15.0k-token limit

Claude Code shows this warning as a startup notice in the conversation view rather than on stderr. The combined descriptions of your [subagents](https://code.claude.com/docs/en/sub-agents.md), except the built-in ones, exceed 15,000 tokens as Claude Code estimates them. Each agent counts its name plus its `description` frontmatter. Claude Code loads every agent whether or not the total is over the limit, so the warning doesn't change what loads.

```text theme={null}
Agent descriptions are over the 15.0k-token limit (~16.2k tokens) · ask Claude to trim agent descriptions in .claude/agents/
```

**What to do:**

* Shorten the `description` frontmatter of your agent files, or ask Claude to trim them for you.
* Remove agent files you no longer use.

### Hook needs quotes around a path with a space

This notification in the conversation view means a hook's script didn't run because its path has a space and isn't quoted. That hook is an [`asyncRewake`](https://code.claude.com/docs/en/hooks#run-hooks-in-the-background) hook in shell form. In its `command`, an interpreter such as `python3` is followed by an unquoted path placeholder, and the resolved path contains a space.

The notification starts with the hook's event name and names the script:

```text theme={null}
Stop hook needs quotes around a path with a space (check.py)
```

**What to do:**

* In the `command` of the hook that runs the script the notification names, wrap the path in double quotes. In a JSON file, write it as `"command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/check.py\""`.

### A skill, command, or workflow wasn't loaded because its name is reserved

A skill folder, a frontmatter `name`, a file or subfolder in `.claude/commands/`, or a [saved workflow](https://code.claude.com/docs/en/workflows.md#save-the-workflow-for-reuse) uses the name `anthropic-skills` or a name that starts with `anthropic-skills:`. Claude Code [reserves that name for skills synced from claude.ai](https://code.claude.com/docs/en/skills.md#names-reserved-for-synced-skills) and doesn't load that item.

Claude Code shows this warning as a startup notice in the conversation view rather than on stderr:

```text theme={null}
Not loaded: rename .claude/skills/anthropic-skills, then restart — its name uses "anthropic-skills", a name reserved for the skills synced from your claude.ai account
```

The notice names what to change for the first item it refused: a folder or file to rename, a `name:` line to edit, or a workflow to rename. When more than one item was refused, the notice ends with a count such as `· 2 more`, and the [debug log](https://code.claude.com/docs/en/debug-your-config.md) names each one.

**What to do:**

* Rename the item the notice names, or edit the `name:` line it points to, then restart the session.

Before v2.1.282, Claude Code loaded skills and commands with these names.

### Skill or command name refused

This startup notice means Claude Code refused the name of at least one [skill or custom command](https://code.claude.com/docs/en/skills.md), so it didn't load or loaded without its `name` field:

```text theme={null}
1 skill or command name refused: run with --debug to see which ([names]), rename, then restart — a name may not hold hidden, direction-changing or blank-like characters, < or >, or be over 256 characters
```

* **Not loaded**: Claude Code refused the name a skill or command goes by, such as its directory name or a command file's name or subfolder. It's missing from the `/` menu and Claude can't invoke it. Its line in the debug log reads `<name> is not offered`.
* **`name` field ignored**: Claude Code refused a skill's frontmatter `name`. The skill still loads, but the `/` menu doesn't show the `name` value and typing it doesn't invoke the skill. Its line in the debug log reads `<name value> is not shown for <skill>`.

**What to do:**

* Start Claude Code with `claude --debug` from your shell and search the [debug log](https://code.claude.com/docs/en/debug-your-config.md) for `[names]`. Each name the notice counts has one line there. The line spells out some hidden characters as codes, such as `\u{200B}` for a zero-width space, so you can see where they are.
* Remove the [characters a skill name can't hold](https://code.claude.com/docs/en/skills.md#characters-a-skill-name-cant-hold) by renaming the folder or file or editing the `name:` line, or shorten a name that is over 256 characters. Then restart the session, unless the file is in a directory Claude Code [watches for changes](https://code.claude.com/docs/en/skills.md#live-change-detection). For a skill from a plugin you didn't write, ask the plugin's author to rename it.

### Managed settings need your approval

Your organization's [server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md) include settings that need your approval in the [security approval dialog](https://code.claude.com/docs/en/server-managed-settings.md#security-approval-dialogs). The `claude plugin` command you ran couldn't read from the keyboard, so it couldn't show that dialog. That happens when you pipe or redirect its input and, on macOS and Linux, it also can't open `/dev/tty`. The command stopped before making any changes:

```text theme={null}
Your organization's managed settings need your approval, which couldn't be asked for here. Run `claude` in a terminal and approve them, then run this command again.
```

**What to do:**

* Run `claude` in a terminal and approve the settings when the dialog appears, then run the same `claude plugin` command again. Claude Code keeps the approval and the approved settings in your [configuration directory](https://code.claude.com/docs/en/server-managed-settings.md#approval-memory). If the command that stopped ran as another user or with `CLAUDE_CONFIG_DIR` set, run `claude` the same way so that both use the same directory.

### MCP server is blocked by enterprise managed policy

You selected **Reconnect** on a server in `/mcp`, or turned a disabled server back on there, and a setting that [restricts MCP servers](https://code.claude.com/docs/en/managed-mcp.md) blocks that server. Claude Code refuses to connect it and shows:

```text theme={null}
MCP server <name> is blocked by enterprise managed policy
```

Any of these settings can produce the message:

* A [`deniedMcpServers`](https://code.claude.com/docs/en/managed-mcp#policy-based-control-with-allowlists-and-denylists) entry that matches the server, including one in your own `~/.claude/settings.json` or the project's `.claude/settings.json`
* An [`allowedMcpServers`](https://code.claude.com/docs/en/managed-mcp#policy-based-control-with-allowlists-and-denylists) list that the server doesn't match
* [`strictPluginOnlyCustomization`](https://code.claude.com/docs/en/settings-reference#strictpluginonlycustomization) with `mcp` locked, which blocks servers configured in `~/.claude.json` and `.mcp.json`
* [`disableClaudeAiConnectors`](https://code.claude.com/docs/en/mcp#disable-claude-ai-connectors), when the server is a claude.ai connector

**What to do:**

* Check your own user and project settings files for one of these settings and change or remove it
* If none of your own settings explains the block, ask your administrator which managed setting blocks the server

Before v2.1.257, **Reconnect** and re-enable in `/mcp` could connect a server that a mid-session policy update blocked.

### MCP server name is reserved

This message names one of your MCP servers, whose name is among those Claude Code reserves, such as the names of its built-in servers:

```text theme={null}
"workspace" is a reserved MCP server name and was not loaded
```

**What to do:**

* Rename the server where you define it, for example from `workspace` to `my-workspace`
* For other reserved names to avoid, see [MCP configuration warnings](https://code.claude.com/docs/en/mcp.md#configuration-warnings)

## Report an error

For errors from components this page doesn't cover, see the relevant guide:

* MCP server failed to connect or authenticate: [MCP](https://code.claude.com/docs/en/mcp.md)
* Hook script failed or blocked a tool: [Debug hooks](https://code.claude.com/docs/en/hooks.md#debug-hooks)
* Permission denied or filesystem errors during install: [Troubleshoot installation and login](https://code.claude.com/docs/en/troubleshoot-install.md)

If an error is not listed here or the suggested fix does not help:

* Run `/feedback` inside Claude Code to send the transcript and a description to Anthropic. The command also offers to open a prefilled GitHub issue. Sending to Anthropic requires [authentication](https://code.claude.com/docs/en/authentication.md). On Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, and other third-party providers, or when no Anthropic credentials are configured, `/feedback` saves a local archive you can send to your Anthropic account representative instead.
* Run `claude doctor` from your shell for a read-only diagnostic of your installation, or run the `/doctor` checkup inside Claude Code to find and fix setup problems
* Check [status.claude.com](https://status.claude.com) for active incidents
* Search [existing issues](https://github.com/anthropics/claude-code/issues) on GitHub
