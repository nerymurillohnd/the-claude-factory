# Push events into a running session with channels

> A channel is an MCP server, installed as a plugin, that pushes messages, alerts, and webhooks (CI results, chat messages, monitoring events) into a running Claude Code session so Claude can react while the user is away. Use this file to understand how channel plugins are installed, enabled, secured, restricted by organizations, and tested during the research preview.

## Contents

- [Requirements and availability](#requirements-and-availability)
- [How a channel works](#how-a-channel-works)
- [Quickstart](#quickstart)
- [Security](#security)
- [Enterprise controls](#enterprise-controls)
  - [Enable channels for your organization](#enable-channels-for-your-organization)
  - [Restrict which channel plugins can run](#restrict-which-channel-plugins-can-run)
- [Research preview](#research-preview)
- [Documentation References](#documentation-references)

## Requirements and availability

> **Note:** Channels are in [research preview](#research-preview). They require Anthropic authentication through claude.ai or a Console API key, and are not available on Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry. Team and Enterprise organizations must [explicitly enable them](#enterprise-controls).

## How a channel works

- A channel is an MCP server that pushes events into the user's running Claude Code session, so Claude can react to things that happen while the user is not at the terminal.
- Channels can be two-way: Claude reads the event and replies back through the same channel, like a chat bridge.
- Events arrive only while the session is open. For an always-on setup, the user runs Claude in a background process or persistent terminal.
- Unlike integrations that spawn a fresh cloud session or wait to be polled, the event arrives in the session already open: see [how channels compare](https://code.claude.com/docs/en/channels#how-channels-compare).
- A channel is installed as a plugin and configured with the user's own credentials. Telegram, Discord, and iMessage are included in the research preview.
- When Claude replies through a channel, the terminal shows the inbound message but not the reply text. The terminal shows the tool call and a confirmation (like "sent"); the actual reply appears on the other platform.

For organization administration (Team, Enterprise, or Console), see [Enable channels for your organization](#enterprise-controls). To build a channel, read the [Channels reference](https://code.claude.com/docs/en/channels-reference.md).

## Quickstart

Fakechat is an officially supported demo channel that runs a chat UI on localhost, with nothing to authenticate and no external service to configure. Once fakechat is installed and enabled, a message typed in the browser arrives in the Claude Code session; Claude replies, and the reply shows up back in the browser. After fakechat, the other channels to try are [Telegram](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram), [Discord](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/discord), and [iMessage](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/imessage).

Prerequisites for the fakechat demo:

* Claude Code [installed and authenticated](https://code.claude.com/docs/en/quickstart.md#step-1-install-claude-code) with a claude.ai account or a Claude Console API key
* [Bun](https://bun.sh) installed. The pre-built channel plugins are Bun scripts. Check with `bun --version`; if that fails, [install Bun](https://bun.sh/docs/installation).
* **Team, Enterprise, or managed Console org**: an admin must [enable channels](#enterprise-controls) in managed settings

**1. Install the fakechat channel plugin**

Start Claude Code by running `claude` in the terminal, then enter the install command at its prompt:

```text theme={null}
/plugin install fakechat@claude-plugins-official
```

If the install fails, match the message Claude Code reports:

* `Marketplace "claude-plugins-official" not found`: add the marketplace with `/plugin marketplace add anthropics/claude-plugins-official`, then retry the install.
* `Plugin "<name>" not found in marketplace "claude-plugins-official"`: the local copy of the marketplace catalog may be out of date. Refresh it with `/plugin marketplace update claude-plugins-official`, then retry the install. If the retry prints the same message, see [Plugin not found in marketplace](https://code.claude.com/docs/en/plugins/troubleshooting.md#plugin-not-found-in-marketplace).

When the install asks for an installation scope, choose the user scope option so the plugin is available across all projects.

If the install summary reports `Run /reload-plugins to apply.`, no action is needed here, because the restart in the next step picks up the plugin.

**2. Restart with the channel enabled**

Exit Claude Code, then restart with `--channels` and pass the installed fakechat plugin:

```bash theme={null}
claude --channels plugin:fakechat@claude-plugins-official
```

The fakechat server starts automatically. The startup screen shows a channels notice stating that messages from `plugin:fakechat@claude-plugins-official` inject directly in this session. If the plugin is not installed or is not on the approved allowlist, a warning line naming the problem appears below that notice.

> **Tip:** `--channels` accepts several plugins, space-separated.

**3. Push a message in**

Open the fakechat UI at [http://localhost:8787](http://localhost:8787) and type a message:

```text theme={null}
what's in my working directory?
```

The message arrives in the Claude Code session:

- The terminal shows it as an inbound channel line like `← fakechat · web: what's in my working directory?`.
- The model receives it as a `<channel source="plugin:fakechat:fakechat">` event, using the plugin's scoped server name.
- Claude reads it, does the work, and calls fakechat's `reply` tool. If Claude Code asks for permission for the first reply, approve it. The answer shows up in the chat UI.

Permission prompts while the user is away:

- If Claude hits a permission prompt while the user is away from the terminal, the session pauses until the user responds.
- Channel servers that declare the [permission relay capability](https://code.claude.com/docs/en/channels-reference.md#relay-permission-prompts) can forward these prompts so the user can approve or deny remotely.
- For unattended use, [`--dangerously-skip-permissions`](https://code.claude.com/docs/en/permission-modes#skip-all-checks-with-bypasspermissions-mode) bypasses most prompts; use it only in trusted environments. Even then, the [actions no mode auto-approves](https://code.claude.com/docs/en/permission-modes.md#actions-no-mode-auto-approves) still apply.

When channels run in non-interactive mode with `-p`, tools that need terminal input, such as multiple-choice questions and plan mode approval, are disabled so the session never stalls waiting for input.

## Security

Every approved channel plugin maintains a sender allowlist: only IDs the user has added can push messages, and everyone else is silently dropped.

Telegram and Discord bootstrap the list by pairing:

1. Find the bot in Telegram or Discord and send it any message
2. The bot replies with a pairing code
3. In the Claude Code session, approve the code when prompted
4. The sender ID is added to the allowlist

iMessage works differently: texting yourself bypasses the gate automatically, and other contacts are added by handle with `/imessage:access allow`.

Further gates on top of the sender allowlist:

- The user controls which servers are enabled each session with `--channels`.
- The organization controls availability with [`channelsEnabled`](#enterprise-controls) on claude.ai Team and Enterprise plans and on Console organizations that deploy managed settings.
- Being in `.mcp.json` is not enough to push messages: a server also has to be named in `--channels`.

The allowlist also gates [permission relay](https://code.claude.com/docs/en/channels-reference.md#relay-permission-prompts) if the channel declares it. Anyone who can reply through the channel can approve or deny tool use in the session, so allowlist only senders trusted with that authority.

## Enterprise controls

Admins control availability through two [managed settings](https://code.claude.com/docs/en/settings.md) that users cannot override. The default depends on how the user authenticates:

* **claude.ai Team and Enterprise**: channels are blocked until an Owner [enables them](#enable-channels-for-your-organization).
* **Anthropic Console with API key authentication**: channels are permitted by default. This setting is needed only if the organization deploys managed settings.

In all cases, no channel runs until a user opts it in for the session with `--channels`.

| Setting | Purpose | When not configured |
| :- | :- | :- |
| `channelsEnabled` | Master switch. Must be `true` for any channel to deliver messages. Blocks all channels including the development flag when off. See [Enable channels for your organization](#enable-channels-for-your-organization). | claude.ai Team and Enterprise: channels blocked. Console: channels allowed unless your organization deploys managed settings, in which case channels are blocked until this key is set |
| `allowedChannelPlugins` | Which plugins can register once channels are enabled. Replaces the Anthropic-maintained list when set. | Anthropic default list applies |

Pro, Max, and Ultra users without an organization skip these checks entirely: channels are available and users opt in per session with `--channels`.

### Enable channels for your organization

Enable channels for an organization from [**Organization settings > Claude Code > Channels**](https://claude.ai/admin-settings/claude-code), which requires the Owner role, or by setting `channelsEnabled` to `true` in managed settings.

Once enabled, users in the organization can use `--channels` to opt channel servers into individual sessions. If the setting is disabled or unset, the MCP server still connects and its tools work, but channel messages do not arrive. A startup warning tells the user to have an admin enable the setting.

### Restrict which channel plugins can run

By default, any plugin on the Anthropic-maintained allowlist can register as a channel. Admins on Team and Enterprise plans can replace that allowlist with their own by setting `allowedChannelPlugins` in managed settings, to restrict which official plugins are allowed, to approve channels from an internal marketplace, or both. Each entry names a plugin and the marketplace it comes from:

```json theme={null}
{
  "channelsEnabled": true,
  "allowedChannelPlugins": [
    { "marketplace": "claude-plugins-official", "plugin": "telegram" },
    { "marketplace": "claude-plugins-official", "plugin": "discord" },
    { "marketplace": "acme-corp-plugins", "plugin": "internal-alerts" }
  ]
}
```

Rules for `allowedChannelPlugins`:

- An empty array blocks all channel plugins from the allowlist, but `--dangerously-load-development-channels` can still bypass that block for local testing. To block channels entirely, including the development flag, leave `channelsEnabled` unset instead.
- The setting requires `channelsEnabled: true`.
- If a user passes a plugin to `--channels` that is not on the list, Claude Code starts normally but the channel does not register, and the startup notice explains that the plugin is not on the organization's approved list.
- On the v2 MCP client runtime, a channel can also fail to register because Claude Code [doesn't register a channel server that negotiates protocol revision 2026-07-28](https://code.claude.com/docs/en/mcp.md#push-messages-with-channels).

## Research preview

Channels are a research preview feature. Availability is rolling out gradually, and the `--channels` flag syntax and protocol contract may change based on feedback.

- Neither `--channels` nor `--dangerously-load-development-channels` appears in `claude --help` while the feature is in preview. The flags work even though they are not listed.
- During the preview, `--channels` accepts only plugins from an Anthropic-maintained allowlist, or from the organization's allowlist if an admin has set [`allowedChannelPlugins`](#restrict-which-channel-plugins-can-run). The channel plugins in [claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins) are the default approved set.
- If something not on the effective allowlist is passed, Claude Code starts normally but the channel does not register, and the startup notice says why.

To test a channel under development, pass it to `--dangerously-load-development-channels` in the `plugin:<name>@<marketplace>` or `server:<name>` form. For testing custom channels, read [Test during the research preview](https://code.claude.com/docs/en/channels-reference.md#test-during-the-research-preview).

Report issues or feedback on the [Claude Code GitHub repository](https://github.com/anthropics/claude-code/issues).

## Documentation References

- Source page: https://code.claude.com/docs/en/channels (full channels guide, including how channels compare to other integrations)
- https://code.claude.com/docs/en/channels-reference.md - build a custom channel for systems that don't have plugins yet, permission relay, testing during the research preview
- https://code.claude.com/docs/en/quickstart.md - install and authenticate Claude Code
- https://code.claude.com/docs/en/plugins/troubleshooting.md - fixing "Plugin not found in marketplace"
- https://code.claude.com/docs/en/permission-modes.md - bypassPermissions mode and actions no mode auto-approves (also linked as https://code.claude.com/docs/en/permission-modes)
- https://code.claude.com/docs/en/settings.md - managed settings where `channelsEnabled` and `allowedChannelPlugins` live
- https://code.claude.com/docs/en/mcp.md - pushing messages with channels and the protocol revision registration limit
