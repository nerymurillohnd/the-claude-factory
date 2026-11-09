# Channels reference

> How to build an MCP server that pushes webhooks, alerts, and chat messages into a Claude Code session, and the channel contract it must follow: capability declaration, notification events, reply tools, sender gating, and permission relay.

## Contents

- [Overview](#overview)
- [What you need](#what-you-need)
- [Example: build a webhook receiver](#example-build-a-webhook-receiver)
- [Test during the research preview](#test-during-the-research-preview)
- [Server options](#server-options)
- [Notification format](#notification-format)
- [Expose a reply tool](#expose-a-reply-tool)
- [Gate inbound messages](#gate-inbound-messages)
- [Relay permission prompts](#relay-permission-prompts)
  - [How relay works](#how-relay-works)
  - [Permission request fields](#permission-request-fields)
  - [Add relay to a chat bridge](#add-relay-to-a-chat-bridge)
  - [Full example](#full-example)
- [Package as a plugin](#package-as-a-plugin)
- [Documentation References](#documentation-references)

> [!NOTE]
>
> Channels are in [research preview](https://code.claude.com/docs/en/channels.md#research-preview). Team and Enterprise organizations must [explicitly enable them](https://code.claude.com/docs/en/channels.md#enterprise-controls).

A channel is an MCP server that pushes events into a Claude Code session so Claude can react to things happening outside the terminal.

A channel is either one-way or two-way:

- A one-way channel forwards alerts, webhooks, or monitoring events for Claude to act on.
- A two-way channel, such as a chat bridge, also [exposes a reply tool](#expose-a-reply-tool) so Claude can send messages back.

A channel with a trusted sender path can also opt in to [relay permission prompts](#relay-permission-prompts), so the user can approve or deny tool use remotely.

To use an existing channel instead of building one, read [Channels](https://code.claude.com/docs/en/channels.md). Telegram, Discord, iMessage, and fakechat are included in the research preview.

## Overview

A channel is an [MCP](https://modelcontextprotocol.io) server that runs on the same machine as Claude Code. Claude Code spawns it as a subprocess and communicates with it over stdio. The channel server is the bridge between external systems and the Claude Code session:

* **Chat platforms** (Telegram, Discord): the plugin runs locally and polls the platform's API for new messages. When someone DMs the bot, the plugin receives the message and forwards it to Claude. There is no URL to expose.
* **Webhooks** (CI, monitoring): the server listens on a local HTTP port. External systems POST to that port, and the server pushes the payload to Claude.

![Architecture diagram showing external systems connecting to your local channel server, which communicates with Claude Code over stdio](https://mintcdn.com/claude-code/9FG0ZKj9uKYiHmbi/images/channel-architecture.svg?fit=max\&auto=format\&n=9FG0ZKj9uKYiHmbi\&q=85\&s=9a037b7da80184ae49015c0256b21a1f)

> **View the image** [`assets/channel-architecture.png`](../../assets/channel-architecture.png) **to** see how external systems, your channel server, and Claude Code connect.

## What you need

The only hard requirements are the [`@modelcontextprotocol/sdk`](https://www.npmjs.com/package/@modelcontextprotocol/sdk) package and a Node.js-compatible runtime. [Bun](https://bun.sh), [Node](https://nodejs.org), and [Deno](https://deno.com) all work. The pre-built plugins in the research preview use Bun, but a channel does not have to.

The server must:

1. Declare the `claude/channel` capability, so Claude Code registers a notification listener.
2. Emit `notifications/claude/channel` events when something happens.
3. Connect over [stdio transport](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio).

[Server options](#server-options) and [Notification format](#notification-format) cover each requirement in detail. [Example: build a webhook receiver](#example-build-a-webhook-receiver) is a full walkthrough.

During the research preview, custom channels are not on the [approved allowlist](https://code.claude.com/docs/en/channels.md#supported-channels). To test one locally, use `--dangerously-load-development-channels`, as described in [Test during the research preview](#test-during-the-research-preview).

## Example: build a webhook receiver

This walkthrough builds a single-file server that listens for HTTP requests and forwards them into the Claude Code session. When it is done, anything that can send an HTTP POST, such as a CI pipeline, a monitoring alert, or a `curl` command, can push events to Claude.

The example uses [Bun](https://bun.sh) as the runtime for its built-in HTTP server and TypeScript support. [Node](https://nodejs.org) or [Deno](https://deno.com) work instead; the only requirement is the [MCP SDK](https://www.npmjs.com/package/@modelcontextprotocol/sdk).

**1. Create the project**

The [permission relay](#relay-permission-prompts) examples import `zod` directly, so install it alongside the MCP SDK. Create a new directory and install both:

```bash theme={null}
mkdir webhook-channel && cd webhook-channel
bun add @modelcontextprotocol/sdk zod
```

**2. Write the channel server**

Create a file called `webhook.ts`. It is the entire channel server: it connects to Claude Code over stdio and listens for HTTP POSTs on port 8788. When a request arrives, it pushes the body to Claude as a channel event.

```ts title="webhook.ts" theme={null}
#!/usr/bin/env bun
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'

// Create the MCP server and declare it as a channel
const mcp = new Server(
  { name: 'webhook', version: '0.0.1' },
  {
    // this key is what makes it a channel — Claude Code registers a listener for it
    capabilities: { experimental: { 'claude/channel': {} } },
    // Claude Code delivers this to Claude as context when the server connects, so it knows how to handle these events
    instructions: 'Events from the webhook channel arrive as <channel source="webhook" ...>. They are one-way: read them and act, no reply expected.',
  },
)

// Connect to Claude Code over stdio (Claude Code spawns this process)
await mcp.connect(new StdioServerTransport())

// Start an HTTP server that forwards every POST to Claude
Bun.serve({
  port: 8788,  // any open port works
  // localhost-only: nothing outside this machine can POST
  hostname: '127.0.0.1',
  async fetch(req) {
    const body = await req.text()
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: {
        content: body,  // becomes the body of the <channel> tag
        // each key becomes a tag attribute, e.g. <channel path="/" method="POST">
        meta: { path: new URL(req.url).pathname, method: req.method },
      },
    })
    return new Response('ok')
  },
})
```

The file does three things, in this order:

* **Server configuration**: creates the MCP server with `claude/channel` in its capabilities, which tells Claude Code that the server is a channel. Claude Code delivers the [`instructions`](#server-options) string to Claude as context when the server connects. Use it to tell Claude what events to expect, whether to reply, and, if it should reply, how to route replies.
* **Stdio connection**: connects to Claude Code over stdin/stdout, as any [MCP server](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio) does.
* **HTTP listener**: starts a local web server on port 8788. Every POST body is forwarded to Claude as a channel event through `mcp.notification()`. The `content` becomes the event body, and each `meta` entry becomes an attribute on the `<channel>` tag. The listener needs access to the `mcp` instance, so it runs in the same process. A larger project can split it into separate modules.

**3. Register the server with Claude Code**

Add the server to the MCP config so Claude Code knows how to start it. In a project-level `.mcp.json` in the same directory, use a relative path. In user-level config in `~/.claude.json`, use the full absolute path, so the server can be found from any project:

```json title=".mcp.json" theme={null}
{
  "mcpServers": {
    "webhook": { "command": "bun", "args": ["./webhook.ts"] }
  }
}
```

Claude Code reads the MCP config at startup and spawns each server as a subprocess.

**4. Test it**

During the research preview, custom channels are not on the allowlist, so start Claude Code with the development flag:

```bash theme={null}
claude --dangerously-load-development-channels server:webhook
```

Expect this startup sequence:

1. Claude Code shows a full-screen warning dialog that lists the development channels being loaded. Select **I am using this for local development** to continue, or **Exit** to quit.
2. The first time a session starts in this project, Claude Code also asks for consent before using the new server from `.mcp.json`. The dialog reports "New MCP server found in this project: webhook". Select **Use this MCP server** to continue.
3. After acceptance, Claude Code spawns `webhook.ts` as a subprocess, and the HTTP listener starts automatically on the configured port, 8788 in this example. The server does not need to be run separately.
4. A dim notice below the startup banner confirms the channel is registered: `Channels (experimental) messages from server:webhook inject directly in this session · restart without --dangerously-load-development-channels to stop`.

If the session shows "blocked by org policy," the organization admin must [enable channels](https://code.claude.com/docs/en/channels.md#enterprise-controls) first.

In a separate terminal, simulate a webhook by sending an HTTP POST with a message to the server. This example sends a CI failure alert to port 8788 (or whichever port was configured):

```bash theme={null}
curl -X POST localhost:8788 -d "build failed on main: https://ci.example.com/run/1234"
```

The payload arrives in Claude's context as a `<channel>` tag:

```text theme={null}
<channel source="webhook" path="/" method="POST">
build failed on main: https://ci.example.com/run/1234
</channel>
```

The terminal renders the event as a one-line summary, `← webhook: build failed on main: https://ci.example.com/run/1234`, rather than the raw tag. Claude then starts responding: reading files, running commands, or whatever the message calls for. This is a one-way channel, so Claude acts in the session but sends nothing back through the webhook. To add replies, follow [Expose a reply tool](#expose-a-reply-tool).

If the event does not arrive, diagnose by what `curl` returned:

* **`curl` succeeds but nothing reaches Claude**: run `/mcp` in the session to check the server's status. A `failed` status usually means a dependency or import error in the server file. To see the stderr trace, restart with `claude --debug --dangerously-load-development-channels server:webhook` and check the debug log at `~/.claude/debug/<session-id>.txt`.
* **`curl` fails with "connection refused"**: either the port is not bound yet, or a stale process from an earlier run is holding it. Run `lsof -i :<port>` to see what is listening, and `kill` the stale process before restarting the session.

The [fakechat server](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/fakechat) extends this pattern with a web UI, file attachments, and a reply tool for two-way chat.

## Test during the research preview

During the research preview, every channel must be on the [approved allowlist](https://code.claude.com/docs/en/channels.md#research-preview) to register. The development flag bypasses the allowlist for specific entries after a confirmation prompt. This example shows both entry types:

```bash theme={null}
# Testing a plugin you're developing
claude --dangerously-load-development-channels plugin:yourplugin@yourmarketplace

# Testing a bare .mcp.json server (no plugin wrapper yet)
claude --dangerously-load-development-channels server:webhook
```

Rules for the development flag:

- Pass it in an interactive session, where Claude Code can show the confirmation prompt. In non-interactive mode (`-p`) or through the Agent SDK, Claude Code ignores the flag and the channel does not register.
- The bypass is per-entry. Combining this flag with `--channels` does not extend the bypass to the `--channels` entries.
- During the research preview, a custom channel is not on the approved allowlist, so keep it on the development flag while building and testing.

> [!NOTE]
>
> This flag skips the allowlist only. The `channelsEnabled` organization policy still applies. Don't use it to run channels from untrusted sources.

## Server options

A channel sets these options in the [`Server`](https://modelcontextprotocol.io/docs/learn/server-concepts) constructor. The `instructions` and `capabilities.tools` fields are [standard MCP](https://modelcontextprotocol.io/docs/learn/server-concepts); `capabilities.experimental['claude/channel']` and `capabilities.experimental['claude/channel/permission']` are the channel-specific additions:

| Field | Type | Description |
| :- | :- | :- |
| `capabilities.experimental['claude/channel']` | `object` | Required. Always `{}`. Presence registers the notification listener. |
| `capabilities.experimental['claude/channel/permission']` | `object` or `false` | Optional. Set it to `{}` to declare that this channel can receive permission relay requests. When declared, Claude Code forwards tool approval prompts to your channel so you can approve or deny them remotely. To opt out, omit the key or set it to `false`. Before v2.1.234, Claude Code treated `false` as declared. See [Relay permission prompts](#relay-permission-prompts). |
| `capabilities.tools` | `object` | Two-way only. Always `{}`. Standard MCP tool capability. See [Expose a reply tool](#expose-a-reply-tool). |
| `instructions` | `string` | Recommended. Claude Code delivers it to Claude as context when the server connects. Tell Claude what events to expect, what the `<channel>` tag attributes mean, whether to reply, and if so which tool to use and which attribute to pass back (like `chat_id`). |

To create a one-way channel, omit `capabilities.tools`. This example shows a two-way setup with the channel capability, tools, and instructions set:

```ts theme={null}
import { Server } from '@modelcontextprotocol/sdk/server/index.js'

const mcp = new Server(
  { name: 'your-channel', version: '0.0.1' },
  {
    capabilities: {
      experimental: { 'claude/channel': {} },  // registers the channel listener
      tools: {},  // omit for one-way channels
    },
    // Claude Code delivers this to Claude as context when the server connects, so it knows how to handle your events
    instructions: 'Messages arrive as <channel source="your-channel" ...>. Reply with the reply tool.',
  },
)
```

## Notification format

The server emits `notifications/claude/channel` with two params:

| Field | Type | Description |
| :- | :- | :- |
| `content` | `string` | The event body. Delivered as the body of the `<channel>` tag. |
| `meta` | `Record<string, string>` | Optional. Each entry becomes an attribute on the `<channel>` tag for routing context like chat ID, sender name, or alert severity. Keys must be identifiers: letters, digits, and underscores only. Keys containing hyphens or other characters are silently dropped. |

The server pushes events by calling `mcp.notification()` on the `Server` instance. This example pushes a CI failure alert with two meta keys:

```ts theme={null}
await mcp.notification({
  method: 'notifications/claude/channel',
  params: {
    content: 'build failed on main: https://ci.example.com/run/1234',
    meta: { severity: 'high', run_id: '1234' },
  },
})
```

The event arrives in Claude's context wrapped in a `<channel>` tag. Claude Code sets the `source` attribute automatically from the server's configured name:

```text theme={null}
<channel source="your-channel" severity="high" run_id="1234">
build failed on main: https://ci.example.com/run/1234
</channel>
```

Delivery behavior:

- Claude Code does not acknowledge notifications. The `await` on `mcp.notification()` resolves when the message is written to the transport, not when Claude has processed it.
- If the session has not loaded the server as a channel, or the organization policy blocks it, Claude Code drops the events silently and returns no error to the server.
- To get delivery confirmation, track event state in the server and expose a [reply tool](#expose-a-reply-tool) that Claude can call to report status back.
- Events queue into the session and are processed in order. If several notifications arrive while Claude is busy, they are delivered together on the next turn and Claude handles them as a group. To process independent event streams concurrently, run separate sessions.

## Expose a reply tool

When a channel is two-way, such as a chat bridge rather than an alert forwarder, expose a standard [MCP tool](https://modelcontextprotocol.io/docs/concepts/tools) that Claude can call to send messages back. Nothing about the tool registration is channel-specific. A reply tool has three components:

1. A `tools: {}` entry in the `Server` constructor capabilities, so Claude Code discovers the tool.
2. Tool handlers that define the tool's schema and implement the send logic.
3. An `instructions` string in the `Server` constructor that tells Claude when and how to call the tool.

To add these to the [webhook receiver above](#example-build-a-webhook-receiver), follow these steps.

**1. Enable tool discovery**

In the `Server` constructor in `webhook.ts`, add `tools: {}` to the capabilities so Claude Code knows the server offers tools:

```ts theme={null}
capabilities: {
  experimental: { 'claude/channel': {} },
  tools: {},  // enables tool discovery
},
```

**2. Register the reply tool**

Add the following to `webhook.ts`. Put the `import` at the top of the file with the other imports, and put the two handlers between the `Server` constructor and `mcp.connect()`. This registers a `reply` tool that Claude can call with a `chat_id` and `text`:

```ts theme={null}
// Add this import at the top of webhook.ts
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js'

// Claude queries this at startup to discover what tools your server offers
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'reply',
    description: 'Send a message back over this channel',
    // inputSchema tells Claude what arguments to pass
    inputSchema: {
      type: 'object',
      properties: {
        chat_id: { type: 'string', description: 'The conversation to reply in' },
        text: { type: 'string', description: 'The message to send' },
      },
      required: ['chat_id', 'text'],
    },
  }],
}))

// Claude calls this when it wants to invoke a tool
mcp.setRequestHandler(CallToolRequestSchema, async req => {
  if (req.params.name === 'reply') {
    const { chat_id, text } = req.params.arguments as { chat_id: string; text: string }
    // send() is your outbound: POST to your chat platform, or for local
    // testing the SSE broadcast shown in the full example below.
    send(`Reply to ${chat_id}: ${text}`)
    return { content: [{ type: 'text', text: 'sent' }] }
  }
  throw new Error(`unknown tool: ${req.params.name}`)
})
```

**3. Update the instructions**

Update the `instructions` string in the `Server` constructor so Claude knows to route replies back through the tool. This example tells Claude to pass `chat_id` from the inbound tag:

```ts theme={null}
instructions: 'Messages arrive as <channel source="webhook" chat_id="...">. Reply with the reply tool, passing the chat_id from the tag.'
```

This is the complete `webhook.ts` with two-way support. Outbound replies stream over `GET /events` using [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) (SSE), so `curl -N localhost:8788/events` can watch them live; inbound chat arrives on `POST /`:

```ts title="Full webhook.ts with reply tool" expandable theme={null}
#!/usr/bin/env bun
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js'

// --- Outbound: write to any curl -N listeners on /events --------------------
// A real bridge would POST to your chat platform instead.
const listeners = new Set<(chunk: string) => void>()
function send(text: string) {
  const chunk = text.split('\n').map(l => `data: ${l}\n`).join('') + '\n'
  for (const emit of listeners) emit(chunk)
}

const mcp = new Server(
  { name: 'webhook', version: '0.0.1' },
  {
    capabilities: {
      experimental: { 'claude/channel': {} },
      tools: {},
    },
    instructions: 'Messages arrive as <channel source="webhook" chat_id="...">. Reply with the reply tool, passing the chat_id from the tag.',
  },
)

mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'reply',
    description: 'Send a message back over this channel',
    inputSchema: {
      type: 'object',
      properties: {
        chat_id: { type: 'string', description: 'The conversation to reply in' },
        text: { type: 'string', description: 'The message to send' },
      },
      required: ['chat_id', 'text'],
    },
  }],
}))

mcp.setRequestHandler(CallToolRequestSchema, async req => {
  if (req.params.name === 'reply') {
    const { chat_id, text } = req.params.arguments as { chat_id: string; text: string }
    send(`Reply to ${chat_id}: ${text}`)
    return { content: [{ type: 'text', text: 'sent' }] }
  }
  throw new Error(`unknown tool: ${req.params.name}`)
})

await mcp.connect(new StdioServerTransport())

let nextId = 1
Bun.serve({
  port: 8788,
  hostname: '127.0.0.1',
  idleTimeout: 0,  // don't close idle SSE streams
  async fetch(req) {
    const url = new URL(req.url)

    // GET /events: SSE stream so curl -N can watch Claude's replies live
    if (req.method === 'GET' && url.pathname === '/events') {
      const stream = new ReadableStream({
        start(ctrl) {
          ctrl.enqueue(': connected\n\n')  // so curl shows something immediately
          const emit = (chunk: string) => ctrl.enqueue(chunk)
          listeners.add(emit)
          req.signal.addEventListener('abort', () => listeners.delete(emit))
        },
      })
      return new Response(stream, {
        headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
      })
    }

    // POST: forward to Claude as a channel event
    const body = await req.text()
    const chat_id = String(nextId++)
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: {
        content: body,
        meta: { chat_id, path: url.pathname, method: req.method },
      },
    })
    return new Response('ok')
  },
})
```

The [fakechat server](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/fakechat) shows a more complete example with file attachments and message editing.

## Gate inbound messages

An ungated channel is a prompt injection vector: anyone who can reach the endpoint can put text in front of Claude. When a channel listens to a chat platform or a public endpoint, give it a real sender check before it emits anything.

Check the sender against an allowlist before calling `mcp.notification()`. This example drops any message from a sender not in the set:

```ts theme={null}
const allowed = new Set(loadAllowlist())  // from your access.json or equivalent

// inside your message handler, before emitting:
if (!allowed.has(message.from.id)) {  // sender, not room
  return  // drop silently
}
await mcp.notification({ ... })
```

Gate on the sender's identity, not the chat or room identity: `message.from.id` in the example, not `message.chat.id`. In group chats the two differ, and gating on the room would let anyone in an allowlisted group inject messages into the session.

Reference implementations:

- The [Telegram](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram) and [Discord](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/discord) channels gate on a sender allowlist the same way. They bootstrap the list by [pairing](https://code.claude.com/docs/en/channels.md#security). Read either implementation for the full pairing flow.
- The [iMessage](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/imessage) channel takes a different approach: it detects the user's own addresses from the Messages database at startup and lets them through automatically, with other senders added by handle.

## Relay permission prompts

When Claude calls a tool that needs approval, the local terminal dialog opens and the session waits. A two-way channel can opt in to receive the same prompt in parallel and relay it to the user on another device. Both stay live: the user can answer in the terminal or on their phone, and Claude Code applies whichever answer arrives first and closes the other.

Scope and requirements:

- Relay covers tool-use approvals such as `Bash`, `Write`, and `Edit`. Project trust and MCP server consent dialogs do not relay; they appear only in the local terminal.
- Claude Code v2.1.234 and later sends permission requests only to servers it registered as channels for the session, so relay sits behind the same [session opt-in and organization controls](https://code.claude.com/docs/en/channels.md#security) as message delivery.
- Relay also requires the user to opt the server in with `--channels` or the development flag, and requires the server to declare the permission capability.

### How relay works

When a permission prompt opens, the relay loop has four steps:

1. Claude Code generates a short request ID and notifies the server.
2. The server forwards the prompt and ID to the chat app.
3. The remote user replies with a yes or no and that ID.
4. The server's inbound handler parses the reply into a verdict, and Claude Code applies it only if the ID matches an open request.

The local terminal dialog stays open through all of this. If someone at the terminal answers before the remote verdict arrives, Claude Code applies that answer instead and drops the pending remote request.

![Sequence diagram: Claude Code sends a permission\_request notification to the channel server, the server formats and sends the prompt to the chat app, the human replies with a verdict, and the server parses that reply into a permission notification back to Claude Code](https://mintcdn.com/claude-code/9FG0ZKj9uKYiHmbi/images/channel-permission-relay.svg?fit=max\&auto=format\&n=9FG0ZKj9uKYiHmbi\&q=85\&s=97d57f128f0da55f105ab1e3a7e10240)

> **View the image** [`assets/channel-permission-relay.png`](../../assets/channel-permission-relay.png) **to** see the message sequence of a permission request relayed through a chat app.

### Permission request fields

The outbound notification from Claude Code is `notifications/claude/channel/permission_request`. As with the [channel notification](#notification-format), the transport is standard MCP, but the method and schema are Claude Code extensions. The `params` object has four string fields that the server formats into the outgoing prompt:

| Field | Description |
| - | - |
| `request_id` | Five lowercase letters drawn from `a`-`z` without `l`, so it never reads as a `1` or `I` when typed on a phone. Include it in your outgoing prompt so it can be echoed in the reply. Claude Code only accepts a verdict that carries an ID it issued. The local terminal dialog doesn't display this ID, so your outbound handler is the only way to learn it. |
| `tool_name` | Name of the tool Claude wants to use, for example `Bash` or `Write`. |
| `description` | Human-readable summary of what this specific tool call does, never the command itself. For a Bash call this is Claude's description of the command; when the model gives no description, the field is the constant `Run shell command` and carries zero command detail. Render `input_preview` when you have room. |
| `input_preview` | The tool's arguments as JSON-shaped display text, keyed per top-level field. For Bash this is the command; for Write, the file path and the content. Omit it from your prompt if you only have room for a one-line message. Your server decides what to show. |

**Sanitization (v2.1.211 and later).** Clients on Claude Code v2.1.211 or later sanitize `description` and `input_preview` before relaying them. Expect three changes in the received text:

* Claude Code neutralizes direction-override characters, invisible characters, and quote and angle-bracket lookalikes.
* Claude Code folds each run of whitespace to a single space.
* Claude Code relays text whole up to 3,500 code points. For a longer value, the server receives its start and its end around a counted `⋯ N code points elided ⋯` marker. The end of a long command still reaches the approver.

For `input_preview`, Claude Code applies the 3,500 limit to each top-level field of the arguments separately and keeps the JSON's own structural quotes. Clients before v2.1.211 relay `description` raw and cut `input_preview` to 200 UTF-16 units with a trailing ellipsis.

**Unserializable values (v2.1.234 and later).** Clients on Claude Code v2.1.234 or later relay the marker `(value unserializable)` in place of an `input_preview` field value they cannot serialize safely, such as a circular structure or an extremely large array. The server still receives the field's key, and the preview's other fields are unchanged.

**Credential masking (v2.1.234 and later).** Clients on Claude Code v2.1.234 or later also mask credentials in `description` and `input_preview`. The server receives `[REDACTED]` in place of a recognizable provider credential token, such as an API key or a personal access token. Account for three effects of the masking when rendering the fields:

* Claude Code masks key names inside `input_preview` as well as their values. A displayed key name may not match the key name in the input.
* Claude Code never masks a span that contains shell syntax, path characters, or URL characters. A mask cannot hide the command, file path, or destination being approved.
* Claude Code does not mask a secret that lacks a recognizable prefix, or a secret that spans whitespace, such as a private-key block. Both reach the server unmasked.

Masking does not change who receives the fields. Whatever stays unmasked goes only to servers the user opted in with `--channels` or the development flag. Treat both fields as untrusted unless you control the client fleet.

**The verdict.** The server sends back `notifications/claude/channel/permission` with two fields: `request_id`, echoing the ID above, and `behavior`, set to `'allow'` or `'deny'`. Allow lets the tool call proceed; deny rejects it. Neither verdict affects future calls.

### Add relay to a chat bridge

Adding permission relay to a two-way channel takes three components:

1. A `claude/channel/permission: {}` entry under `experimental` capabilities in the `Server` constructor, so Claude Code knows to forward prompts.
2. A notification handler for `notifications/claude/channel/permission_request` that formats the prompt and sends it out through the platform API.
3. A check in the inbound message handler that recognizes `yes <id>` or `no <id>` and emits a `notifications/claude/channel/permission` verdict instead of forwarding the text to Claude.

Declare the capability only if the channel [authenticates the sender](#gate-inbound-messages), because anyone who can reply through the channel can approve or deny tool use in the session.

To add these to a two-way chat bridge like the one assembled in [Expose a reply tool](#expose-a-reply-tool), follow these steps.

**1. Declare the permission capability**

In the `Server` constructor, add `claude/channel/permission: {}` alongside `claude/channel` under `experimental`:

```ts theme={null}
capabilities: {
  experimental: {
    'claude/channel': {},
    'claude/channel/permission': {},  // opt in to permission relay
  },
  tools: {},
},
```

**2. Handle the incoming request**

Register a notification handler between the `Server` constructor and `mcp.connect()`. Claude Code calls it with the [four request fields](#permission-request-fields) when a permission dialog opens. The handler formats the prompt for the platform and includes instructions for replying with the ID:

```ts theme={null}
import { z } from 'zod'

// setNotificationHandler routes by z.literal on the method field,
// so this schema is both the validator and the dispatch key
const PermissionRequestSchema = z.object({
  method: z.literal('notifications/claude/channel/permission_request'),
  params: z.object({
    request_id: z.string(),     // five lowercase letters, include verbatim in your prompt
    tool_name: z.string(),      // e.g. "Bash", "Write"
    description: z.string(),    // summary of this call. Treat as untrusted.
    input_preview: z.string(),  // tool args as JSON-shaped text. Treat as untrusted.
  }),
})

mcp.setNotificationHandler(PermissionRequestSchema, async ({ params }) => {
  // send() is your outbound: POST to your chat platform, or for local
  // testing the SSE broadcast shown in the full example below.
  send(
    `Claude wants to run ${params.tool_name}: ${params.description}\n` +
    // input_preview carries the actual arguments; render it when you
    // have room: for Bash the description alone may be just
    // "Run shell command" with zero command detail
    `${params.input_preview}\n\n` +
    // the ID in the instruction is what your inbound handler parses in Step 3
    `Reply "yes ${params.request_id}" or "no ${params.request_id}"`,
  )
})
```

**3. Intercept the verdict in the inbound handler**

The inbound handler is the loop or callback that receives messages from the platform: the same place that [gates on sender](#gate-inbound-messages) and emits `notifications/claude/channel` to forward chat to Claude. Before the chat-forwarding call, add a check that recognizes the verdict format and emits the permission notification instead.

The regex matches the ID format Claude Code generates: five letters, never `l`. The `/i` flag tolerates phone autocorrect capitalizing the reply; lowercase the captured ID before sending it back.

```ts theme={null}
// matches "y abcde", "yes abcde", "n abcde", "no abcde"
// [a-km-z] is the ID alphabet Claude Code uses (lowercase, skips 'l')
// /i tolerates phone autocorrect; lowercase the capture before sending
const PERMISSION_REPLY_RE = /^\s*(y|yes|n|no)\s+([a-km-z]{5})\s*$/i

async function onInbound(message: PlatformMessage) {
  if (!allowed.has(message.from.id)) return  // gate on sender first

  const m = PERMISSION_REPLY_RE.exec(message.text)
  if (m) {
    // m[1] is the verdict word, m[2] is the request ID
    // emit the verdict notification back to Claude Code instead of chat
    await mcp.notification({
      method: 'notifications/claude/channel/permission',
      params: {
        request_id: m[2].toLowerCase(),  // normalize in case of autocorrect caps
        behavior: m[1].toLowerCase().startsWith('y') ? 'allow' : 'deny',
      },
    })
    return  // handled as verdict, don't also forward as chat
  }

  // didn't match verdict format: fall through to the normal chat path
  await mcp.notification({
    method: 'notifications/claude/channel',
    params: { content: message.text, meta: { chat_id: String(message.chat.id) } },
  })
}
```

If a remote reply has no effect and the local terminal dialog stays open, check for these causes:

* **The format is wrong**: the inbound handler's regex fails to match, so text such as `approve it` or `yes` without an ID falls through as a normal message to Claude.
* **The ID is wrong**: the server emits a verdict, but Claude Code finds no open request with that ID and drops it silently.
* **The ID was used by an earlier prompt**: the server emits a verdict with the ID from the request, but an earlier prompt in the session had the same ID. Once an ID repeats, Claude Code drops any channel verdict carrying it, so that a reply meant for one prompt cannot approve the other. An ID is five random letters, so a repeat is rare. In that case, answer at the terminal instead.

### Full example

The assembled `webhook.ts` below combines all three extensions from this file: the reply tool, sender gating, and permission relay. When starting from this example, also apply the [project setup and `.mcp.json` entry](#example-build-a-webhook-receiver) from the initial walkthrough.

To make both directions testable from curl, the HTTP listener serves two paths:

* **`GET /events`**: holds an SSE stream open and pushes each outbound message as a `data:` line, so `curl -N` can watch Claude's replies and permission prompts arrive live.
* **`POST /`**: the inbound side, the same handler as earlier, now with the verdict-format check inserted before the chat-forward branch.

```ts title="Full webhook.ts with permission relay" expandable theme={null}
#!/usr/bin/env bun
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js'
import { z } from 'zod'

// --- Outbound: write to any curl -N listeners on /events --------------------
// A real bridge would POST to your chat platform instead.
const listeners = new Set<(chunk: string) => void>()
function send(text: string) {
  const chunk = text.split('\n').map(l => `data: ${l}\n`).join('') + '\n'
  for (const emit of listeners) emit(chunk)
}

// Sender allowlist. For the local walkthrough we trust the single X-Sender
// header value "dev"; a real bridge would check the platform's user ID.
const allowed = new Set(['dev'])

const mcp = new Server(
  { name: 'webhook', version: '0.0.1' },
  {
    capabilities: {
      experimental: {
        'claude/channel': {},
        'claude/channel/permission': {},  // opt in to permission relay
      },
      tools: {},
    },
    instructions:
      'Messages arrive as <channel source="webhook" chat_id="...">. ' +
      'Reply with the reply tool, passing the chat_id from the tag.',
  },
)

// --- reply tool: Claude calls this to send a message back -------------------
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'reply',
    description: 'Send a message back over this channel',
    inputSchema: {
      type: 'object',
      properties: {
        chat_id: { type: 'string', description: 'The conversation to reply in' },
        text: { type: 'string', description: 'The message to send' },
      },
      required: ['chat_id', 'text'],
    },
  }],
}))

mcp.setRequestHandler(CallToolRequestSchema, async req => {
  if (req.params.name === 'reply') {
    const { chat_id, text } = req.params.arguments as { chat_id: string; text: string }
    send(`Reply to ${chat_id}: ${text}`)
    return { content: [{ type: 'text', text: 'sent' }] }
  }
  throw new Error(`unknown tool: ${req.params.name}`)
})

// --- permission relay: Claude Code (not Claude) calls this when a dialog opens
const PermissionRequestSchema = z.object({
  method: z.literal('notifications/claude/channel/permission_request'),
  params: z.object({
    request_id: z.string(),
    tool_name: z.string(),
    description: z.string(),
    input_preview: z.string(),
  }),
})

mcp.setNotificationHandler(PermissionRequestSchema, async ({ params }) => {
  send(
    `Claude wants to run ${params.tool_name}: ${params.description}\n` +
    `${params.input_preview}\n\n` +
    `Reply "yes ${params.request_id}" or "no ${params.request_id}"`,
  )
})

await mcp.connect(new StdioServerTransport())

// --- HTTP on :8788: GET /events streams outbound, POST routes inbound -------
const PERMISSION_REPLY_RE = /^\s*(y|yes|n|no)\s+([a-km-z]{5})\s*$/i
let nextId = 1

Bun.serve({
  port: 8788,
  hostname: '127.0.0.1',
  idleTimeout: 0,  // don't close idle SSE streams
  async fetch(req) {
    const url = new URL(req.url)

    // GET /events: SSE stream so curl -N can watch replies and prompts live
    if (req.method === 'GET' && url.pathname === '/events') {
      const stream = new ReadableStream({
        start(ctrl) {
          ctrl.enqueue(': connected\n\n')  // so curl shows something immediately
          const emit = (chunk: string) => ctrl.enqueue(chunk)
          listeners.add(emit)
          req.signal.addEventListener('abort', () => listeners.delete(emit))
        },
      })
      return new Response(stream, {
        headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
      })
    }

    // everything else is inbound: gate on sender first
    const body = await req.text()
    const sender = req.headers.get('X-Sender') ?? ''
    if (!allowed.has(sender)) return new Response('forbidden', { status: 403 })

    // check for verdict format before treating as chat
    const m = PERMISSION_REPLY_RE.exec(body)
    if (m) {
      await mcp.notification({
        method: 'notifications/claude/channel/permission',
        params: {
          request_id: m[2].toLowerCase(),
          behavior: m[1].toLowerCase().startsWith('y') ? 'allow' : 'deny',
        },
      })
      return new Response('verdict recorded')
    }

    // normal chat: forward to Claude as a channel event
    const chat_id = String(nextId++)
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: { content: body, meta: { chat_id, path: url.pathname } },
    })
    return new Response('ok')
  },
})
```

Test the verdict path in three terminals. In the first terminal, start the Claude Code session with the [development flag](#test-during-the-research-preview), so it spawns `webhook.ts`:

```bash theme={null}
claude --dangerously-load-development-channels server:webhook
```

This walkthrough tests the permission dialog itself, so once the session is open, press `Shift+Tab` until the status bar shows `⏸ manual mode on`. In auto mode the classifier would decide the `reply` call instead of the user, and no dialog would open for the remote side to answer.

In the second terminal, stream the outbound side to see Claude's replies and any permission prompts as they fire:

```bash theme={null}
curl -N localhost:8788/events
```

In the third terminal, send a message that makes Claude try to run a command:

```bash theme={null}
curl -d "list the files in this directory" -H "X-Sender: dev" localhost:8788
```

Listing files is read-only, so Claude runs it without approval. The permission dialog opens when Claude calls the `reply` tool to send its answer back. The local dialog opens in the Claude Code terminal, and a moment later the prompt for `mcp__webhook__reply` appears in the `/events` stream, including the five-letter ID. Approve it from the remote side:

```bash theme={null}
curl -d "yes <id>" -H "X-Sender: dev" localhost:8788
```

The local dialog closes, the `reply` tool runs, and Claude's reply appears in the stream.

The three channel-specific pieces in this file:

* **Capabilities** in the `Server` constructor: `claude/channel` registers the notification listener, `claude/channel/permission` opts in to permission relay, and `tools` lets Claude discover the reply tool.
* **Outbound paths**: Claude calls the `reply` tool handler for conversational responses; Claude Code calls the `PermissionRequestSchema` notification handler when a permission dialog opens. Both call `send()` to broadcast over `/events`, but different parts of the system trigger them.
* **HTTP handler**: `GET /events` holds an SSE stream open so curl can watch outbound live; `POST` is inbound, gated on the `X-Sender` header. A `yes <id>` or `no <id>` body goes to Claude Code as a verdict notification and never reaches Claude; anything else is forwarded to Claude as a channel event.

## Package as a plugin

To make a channel installable and shareable, wrap it in a [plugin](https://code.claude.com/docs/en/plugins/overview.md) and publish it to a [marketplace](https://code.claude.com/docs/en/plugins/overview.md). Users install it with `/plugin install`, then enable it per session with `--channels plugin:<name>@<marketplace>`.

Allowlist constraints for a channel published to the plugin author's own marketplace:

- A channel published to your own marketplace still needs `--dangerously-load-development-channels` to run, because it is not on the [approved allowlist](https://code.claude.com/docs/en/channels.md#supported-channels).
- The default allowlist is the channel plugins in `claude-plugins-official`. The community marketplace is not on the channel allowlist.
- To get onto an allowlist: when working with an Anthropic partner contact, reach out to them to coordinate an official-marketplace listing. On Team and Enterprise plans, an admin can instead include the plugin in the organization's own [`allowedChannelPlugins`](https://code.claude.com/docs/en/channels#restrict-which-channel-plugins-can-run) list, which replaces the default Anthropic allowlist.

## Documentation References

- [Channels reference](https://code.claude.com/docs/en/channels-reference) (source page): the full channel contract this file is drawn from.
- [Channels](https://code.claude.com/docs/en/channels.md): install and use Telegram, Discord, iMessage, or the fakechat demo; the research preview, supported channels and the approved allowlist; security and pairing; enterprise controls for enabling channels in a Team or Enterprise org.
- [Channels, without the `.md` suffix](https://code.claude.com/docs/en/channels): the same Channels page, including how to restrict which channel plugins can run (`allowedChannelPlugins`).
- [Plugins](https://code.claude.com/docs/en/plugins/overview.md): package a channel as a plugin and publish it to a marketplace, so users can install it with `/plugin install`.
- [MCP](https://code.claude.com/docs/en/mcp.md): MCP in Claude Code, the underlying protocol that channel servers implement.
- [Working channel implementations](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins): complete server code with pairing flows, reply tools, and file attachments.
- [Model Context Protocol](https://modelcontextprotocol.io): the protocol itself.
- [MCP transports](https://modelcontextprotocol.io/docs/concepts/transports): the stdio transport a channel connects over.
- [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts): the `Server` constructor and its standard options.
- [MCP tools](https://modelcontextprotocol.io/docs/concepts/tools): the standard tool mechanism behind a reply tool.
- [`@modelcontextprotocol/sdk`](https://www.npmjs.com/package/@modelcontextprotocol/sdk): the MCP SDK package a channel server requires.
