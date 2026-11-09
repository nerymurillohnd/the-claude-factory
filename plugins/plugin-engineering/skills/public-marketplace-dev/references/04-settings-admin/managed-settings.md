# Deploy managed settings

> Covers deploying managed settings to every developer's machine: delivery mechanisms per OS, how Claude Code combines managed sources, and how to verify enforcement. This pruned copy keeps only where a policy applies in Cowork sessions and the managed-only keys that control permissions, plugins, and delivery.

## Contents

- [Choose a delivery mechanism](#choose-a-delivery-mechanism)
  - [Where and when a policy applies](#where-and-when-a-policy-applies)
- [Keys only a managed source can set](#keys-only-a-managed-source-can-set)
- [Documentation References](#documentation-references)

## Choose a delivery mechanism

### Where and when a policy applies

A deployed policy reaches the developer's sessions as follows:

* **Cowork sessions**: [Cowork](https://claude.com/docs/cowork/overview) in the Claude Desktop app runs its sessions on Claude Code. In a Cowork session, Claude Code never fetches server-managed settings from the claude.ai admin console, even when the user signs in with a Team or Enterprise account, so which policy applies depends on where the session runs:

  * **On the user's machine**: by default, Claude Code in a Cowork session reads the MDM or OS-level policy and the managed settings file on that device, so deploy policy there.
  * **In a full VM sandbox**: when the Claude Desktop managed configuration sets [`requireCoworkFullVmSandbox`](https://claude.com/docs/third-party/claude-desktop/configuration#requirecoworkfullvmsandbox), Claude Code runs inside a virtual machine where the device's MDM policy and managed settings file aren't present.
  * **Remote Cowork sessions**: these run on Anthropic-managed VMs, where Claude Code has no device policy to read.

  Wherever the session runs, claude.ai itself applies the admin console's [`strictKnownMarketplaces`](https://code.claude.com/docs/en/settings-reference#strictknownmarketplaces) and [`blockedMarketplaces`](https://code.claude.com/docs/en/settings-reference#blockedmarketplaces) lists when anyone adds a marketplace from a git repository on claude.ai or from **Customize** in Cowork. [How restrictions work](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install) describes that check. The [surface coverage](https://code.claude.com/docs/en/model-config.md#surface-coverage) table compares Cowork with the other surfaces.

## Keys only a managed source can set

Claude Code reads the following keys only from a managed source; placing them in user or project settings files has no effect.

Most of these keys are locks. The value a lock governs, such as permission rules or `sandbox.network.allowedDomains`, is an ordinary key that any level can set; the lock tells Claude Code to honor only the managed value.

The table covers the permission, plugin, and delivery controls. For any key not listed here, check the Scope column of the [settings reference](https://code.claude.com/docs/en/settings-reference.md#all-settings) index to see whether it is managed-only.

| Setting | Description |
| :- | :- |
| [`allowedChannelPlugins`](https://code.claude.com/docs/en/settings-reference#allowedchannelplugins) | Allowlist of channel plugins that may push messages. Replaces the default Anthropic allowlist when set. Requires `channelsEnabled: true`. See [Restrict which channel plugins can run](https://code.claude.com/docs/en/channels.md#restrict-which-channel-plugins-can-run) |
| [`allowManagedHooksOnly`](https://code.claude.com/docs/en/settings-reference#allowmanagedhooksonly) | When `true`, restricts which hooks run; see [what runs under `allowManagedHooksOnly`](https://code.claude.com/docs/en/settings-reference#what-runs-under-allowmanagedhooksonly) for the full effect list |
| [`allowManagedMcpServersOnly`](https://code.claude.com/docs/en/settings-reference#allowmanagedmcpserversonly) | When `true`, only `allowedMcpServers` from managed settings are respected. `deniedMcpServers` still merges from all sources. See [Keys read from every admin source](https://code.claude.com/docs/en/managed-settings#keys-read-from-every-admin-source) for which managed sources can set it, and [Managed MCP configuration](https://code.claude.com/docs/en/managed-mcp.md) |
| [`blockedMarketplaces`](https://code.claude.com/docs/en/settings-reference#blockedmarketplaces) | Blocklist of marketplace sources. Blocked sources are checked before downloading, so they never touch the filesystem. See [managed marketplace restrictions](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install) |
| [`channelsEnabled`](https://code.claude.com/docs/en/settings-reference#channelsenabled) | Allow [channels](https://code.claude.com/docs/en/channels.md) for the organization. See [enterprise controls](https://code.claude.com/docs/en/channels.md#enterprise-controls) for the default on each plan |
| [`disableSideloadFlags`](https://code.claude.com/docs/en/settings-reference#disablesideloadflags) | Reject the `--plugin-dir`, `--plugin-url`, `--agents`, and `--mcp-config` flags at startup. In cloud sessions, Claude Code instead starts the session and drops the server-delivered `--mcp-config` servers, apart from the exceptions its [reference entry](https://code.claude.com/docs/en/settings-reference.md#disablesideloadflags) lists. Requires Claude Code v2.1.193 or later |
| [`pluginSuggestionMarketplaces`](https://code.claude.com/docs/en/settings-reference#pluginsuggestionmarketplaces) | Marketplaces whose plugins Claude Code may suggest to users in the terminal |
| [`pluginTrustMessage`](https://code.claude.com/docs/en/settings-reference#plugintrustmessage) | Custom message appended to the plugin trust warning shown before installation |
| [`strictKnownMarketplaces`](https://code.claude.com/docs/en/settings-reference#strictknownmarketplaces) | Controls which plugin marketplace sources users can add and install plugins from. See [managed marketplace restrictions](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install) |
| [`strictPluginOnlyCustomization`](https://code.claude.com/docs/en/settings-reference#strictpluginonlycustomization) | Block skills, agents, hooks, and MCP servers from user and project sources; `true` locks all four, an array names which |

## Documentation References

- Source page: https://code.claude.com/docs/en/managed-settings (deploying managed settings: delivery mechanisms, combining managed sources, verifying enforcement)
- https://claude.com/docs/cowork/overview (Cowork in the Claude Desktop app)
- https://claude.com/docs/third-party/claude-desktop/configuration (Claude Desktop managed configuration, including `requireCoworkFullVmSandbox`)
- https://code.claude.com/docs/en/settings-reference.md (every settings key with its scope, including the managed-only keys above)
- https://code.claude.com/docs/en/plugins/org.md (organization plugin controls and marketplace restrictions)
- https://code.claude.com/docs/en/model-config.md (model configuration, including the surface coverage table)
- https://code.claude.com/docs/en/channels.md (channels and their enterprise controls)
- https://code.claude.com/docs/en/managed-mcp.md (managed MCP configuration)
