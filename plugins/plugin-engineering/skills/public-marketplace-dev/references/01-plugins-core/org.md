# Manage Claude Code plugins for your organization

How an organization controls which plugins Claude Code installs and allows through managed settings, and what those controls mean for a marketplace that organizations may allowlist, block or require.

## Contents

- [Pre-install and require plugins](#pre-install-and-require-plugins)
  - [Require plugins per repository](#require-plugins-per-repository)
  - [When each surface applies the plugin keys](#when-each-surface-applies-the-plugin-keys)
  - [Confirm the rollout](#confirm-the-rollout)
- [Restrict what users can install](#restrict-what-users-can-install)
  - [Control matrix](#control-matrix)
    - [Aliases for the marketplace keys](#aliases-for-the-marketplace-keys)
  - [Allowlist with `strictKnownMarketplaces`](#allowlist-with-strictknownmarketplaces)
    - [How entries match](#how-entries-match)
    - [Keep skills-directory plugins loading](#keep-skills-directory-plugins-loading)
    - [Lock every source out](#lock-every-source-out)
  - [Blocklist with `blockedMarketplaces`](#blocklist-with-blockedmarketplaces)
  - [Allow the official marketplace and your own](#allow-the-official-marketplace-and-your-own)
- [Set update policy](#set-update-policy)
  - [Turn auto-update on or off per marketplace](#turn-auto-update-on-or-off-per-marketplace)
  - [Turn updates off for the whole fleet](#turn-updates-off-for-the-whole-fleet)
- [Recommend plugins](#recommend-plugins)
- [Troubleshoot policy](#troubleshoot-policy)
- [Documentation References](#documentation-references)

> **Note:** These cases are covered on other pages:
>
> * **Installing plugins for oneself**: start at [Install plugins](https://code.claude.com/docs/en/plugins/install.md)

## Pre-install and require plugins

A marketplace is a catalog of plugins that Claude Code fetches from a git repository, a URL, or a local path. Once a marketplace is registered on a machine, Claude Code can install plugins from it.

### Require plugins per repository

To cover one repository's contributors instead of the whole fleet, set `extraKnownMarketplaces` and `enabledPlugins` in that repository's `.claude/settings.json`. The `extraKnownMarketplaces` entries apply only in a folder the contributor has trusted; in an untrusted folder Claude Code ignores them without a message:

* **Interactive sessions**: Claude Code registers the marketplace only after the contributor accepts the [workspace trust dialog](https://code.claude.com/docs/en/permissions.md#what-runs-before-you-trust-a-folder) for that folder.
* **[Non-interactive `-p` runs](https://code.claude.com/docs/en/headless)**: the entries apply only in a folder whose trust the user already accepted interactively, or whose `hasTrustDialogAccepted` flag is set in `~/.claude.json`.

A plugin that the marketplace lists by a relative path loads from the marketplace copy once the repository's `extraKnownMarketplaces` entries apply. A plugin whose marketplace entry points at an external source instead, such as the plugin's own GitHub repository, does not install from the repository's settings alone. Each contributor sees `Plugin "<name>" is enabled in project settings but isn't installed` until they run `claude plugin install <name>@<marketplace> --scope project`, as [Install plugins](https://code.claude.com/docs/en/plugins/install.md) describes.

To roll out a bundle of plugins with dependencies, put the bundle plugin in `enabledPlugins`, as [Plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies.md) describes.

### When each surface applies the plugin keys

The table shows when each kind of Claude Code session applies `extraKnownMarketplaces` and `enabledPlugins`, from managed settings and from a repository's `.claude/settings.json`. For the Desktop app and the IDE extensions, see [Install a plugin](https://code.claude.com/docs/en/plugins/install.md#install-a-plugin).

| Surface | Managed `extraKnownMarketplaces` and `enabledPlugins` | Repository `.claude/settings.json` |
| :- | :- | :- |
| Terminal, interactive | Applied at session start on every machine that receives the settings | `extraKnownMarketplaces` applied after trust; `enabledPlugins` applied at session start |
| `-p` and CI | Applied at session start, with installs running in the background | `extraKnownMarketplaces` in trusted folders only; `enabledPlugins` applied |
| Cloud sessions | In an Anthropic-hosted environment, only server-managed settings reach the session, which waits for them before it installs plugins. MDM policies and managed settings files stay on the user's machine. For a self-hosted environment, see [Where and when a policy applies](https://code.claude.com/docs/en/managed-settings.md#where-and-when-a-policy-applies) | See the **Cloud session** tab under [Install a plugin](https://code.claude.com/docs/en/plugins/install.md#install-a-plugin) |

In a `-p` or CI run, marketplaces and plugins install in the background, so a plugin can be missing from the first turn. Set `CLAUDE_CODE_SYNC_PLUGIN_INSTALL=1` to make the run wait for the install before its first query.

### Confirm the rollout

Check that the marketplace and plugins arrived on a machine or in a CI run:

* **On one machine**: start Claude Code and run `/plugin`. The marketplace and the plugins are listed.
* **In CI**: run `claude -p` with `--output-format stream-json --verbose`. The `init` event lists the loaded plugins under `plugins`.

## Restrict what users can install

The managed `strictKnownMarketplaces` allowlist and `blockedMarketplaces` blocklist decide which marketplace sources plugins may come from. A marketplace's source is the git repository, URL, or local path that Claude Code fetches it from. Both lists match the source of the marketplace a plugin comes from, not the plugin's own entry inside that marketplace.

For the common lockdown, which allows the official marketplace and the organization's own, see [Allow the official marketplace and your own](#allow-the-official-marketplace-and-your-own). Pair it with [`disableSideloadFlags`](#control-matrix) so users cannot load plugins from a local directory or URL either.

Both lists apply before anything downloads and again at session start:

* **Before a download**: the lists apply when a user adds a marketplace and on every install, update, refresh, and auto-update.
* **At session start**: the lists apply again to plugins that are already installed, so an installed plugin whose marketplace source no longer matches does not load. `/plugin` lists it with `Marketplace "<name>" is not in the allowed marketplace list` or `Marketplace "<name>" is blocked by enterprise policy`.

Where the two lists are enforced depends on where they are set:

* **The claude.ai admin console**: Claude Code enforces both lists in the sessions that [read server-managed settings](https://code.claude.com/docs/en/managed-settings.md#where-and-when-a-policy-applies). claude.ai also checks them when anyone in the organization adds a new marketplace from a git repository on claude.ai, or from **Customize** in the Claude Desktop app outside its Code tab. That covers a marketplace a member adds for their own account and one added for the whole organization under [**Organization settings > Plugins**](https://claude.ai/admin-settings/plugins). claude.ai refuses a repository that the allowlist does not admit or that the blocklist names. It does not re-check a marketplace that was added in either place before the lists were set, and it does not check uploaded plugins.
* **A managed settings file, OS-level policy, or other managed source**: Claude Code enforces both lists where it reads that source. claude.ai does not read it.

While any allowlist is set, or a blocklist names any source other than [`skills-dir`](#blocklist-with-blockedmarketplaces), a plugin whose marketplace Claude Code cannot find does not load. `/plugin` shows the policy error for it rather than a not-found error. The common case is a stale `enabledPlugins` entry for a marketplace nobody registered.

### Control matrix

The table lists each plugin policy key, what it enforces, and what it can't do.

| Key | What it enforces | What it can't do |
| :- | :- | :- |
| `strictKnownMarketplaces` | Allowlist of marketplace sources. `[]` blocks every source, including the official marketplace. Alias: `allowedMarketplaces` | Doesn't register a marketplace, restrict entries inside an allowed marketplace, or block `--plugin-dir` |
| `blockedMarketplaces` | Blocklist of marketplace sources, checked before the allowlist | Doesn't block a marketplace already registered from a source it doesn't match |
| `syncClaudeAiPlugins` | Set `false` to stop Claude Code downloading and loading the plugins [synced from claude.ai](https://code.claude.com/docs/en/plugins/loading.md#synced-plugins) for each user's account. Requires Claude Code v2.1.273 or later | Doesn't turn off one synced plugin. For that, set `"<name>@synced": false` in [`enabledPlugins`](https://code.claude.com/docs/en/settings-reference#enabledplugins) |
| `enabledPlugins` | `true` force-enables, `false` blocks at every scope and hides the plugin | Doesn't install a plugin whose marketplace isn't registered or allowed |
| `disableSideloadFlags` | Rejects `--plugin-dir`, `--plugin-url`, `--agents`, the Agent SDK `plugins` option, and folders named in the [`CLAUDE_CODE_PLUGIN_DIRS`](https://code.claude.com/docs/en/env-vars#variables) variable at startup, and `--mcp-config` too unless every server in it is an in-process `type: "sdk"` entry. Refuses plugin folders an Agent SDK application adds mid-session with [`addPlugins`](https://code.claude.com/docs/en/agent-sdk/typescript#load-more-plugin-folders-with-addplugins) | Doesn't restrict `.mcp.json`, `claude mcp add`, or SDK-provided servers. Pair it with [`allowedMcpServers`](https://code.claude.com/docs/en/managed-mcp) |
| `allowManagedHooksOnly` | Restricts which hooks run. See [`allowManagedHooksOnly`](https://code.claude.com/docs/en/settings-reference#allowmanagedhooksonly) | Doesn't trust hooks from plugins users enable themselves |
| `strictPluginOnlyCustomization` | Blocks skills, agents, hooks, and MCP servers that don't come from a plugin, managed settings, or Claude Code's built-ins. It also stops [skills-directory plugins](#keep-skills-directory-plugins-loading) loading. Set `true` to cover all four types, or an array of `skills`, `agents`, `hooks`, and `mcp` values such as `["skills", "hooks"]` to cover some | Doesn't restrict which plugins users install. Pair it with `strictKnownMarketplaces` |
| `pluginSuggestionMarketplaces` | Marketplaces whose plugins may appear as install suggestions in the terminal. See [Recommend plugins](#recommend-plugins) | Doesn't affect the built-in tips |
| `pluginTrustMessage` | Appends your text to the trust warning that `/plugin` shows before a plugin installs | Doesn't change the warning's own text |
| `allowedChannelPlugins` | Replaces the default list of plugins allowed to push channel messages. Requires `channelsEnabled: true` | See [Restrict which channel plugins can run](https://code.claude.com/docs/en/channels.md#restrict-which-channel-plugins-can-run) |
| [`CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL=1`](https://code.claude.com/docs/en/env-vars) | Stops interactive terminal sessions from auto-registering the official marketplace | Doesn't remove a marketplace already registered. The allowlist and blocklist gate the same auto-registration without it. A machine that started once with it set doesn't resume auto-registration after you unset it |
| [`allowManagedModsOnly`](https://code.claude.com/docs/en/plugins/mods/admin#stop-user-installed-mods-from-loading) | Stops every installed [mod](https://code.claude.com/docs/en/plugins/mods/overview.md) that doesn't [count as your organization's](https://code.claude.com/docs/en/plugins/mods/admin.md#install-your-organizations-mods) from running its hooks | Doesn't stop a plugin that contains a mod from installing. For that, use the marketplace keys in this table |

Every key in the table is a managed setting, apart from `enabledPlugins`, `syncClaudeAiPlugins`, `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL`, and `allowManagedModsOnly`:

* **`enabledPlugins`**: can be set in any scope, and managed settings lock it.
* **`syncClaudeAiPlugins`**: each user can also set it in their own user or local settings. See its [scope in the settings reference](https://code.claude.com/docs/en/settings-reference.md#syncclaudeaiplugins).
* **`CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL`**: an environment variable, delivered through the managed `env` block shown under [Turn updates off for the whole fleet](#turn-updates-off-for-the-whole-fleet).
* **`allowManagedModsOnly`**: an option on a built-in plugin, set under `pluginConfigs` in managed settings. See [Stop user-installed mods from loading](https://code.claude.com/docs/en/plugins/mods/admin.md#stop-user-installed-mods-from-loading).

Each settings key here has an entry in the [settings reference](https://code.claude.com/docs/en/settings-reference.md).

#### Aliases for the marketplace keys

`strictKnownMarketplaces` can also be spelled `allowedMarketplaces`, and `extraKnownMarketplaces` can also be spelled `additionalMarketplaces`.

* **Version**: the aliases require Claude Code v2.1.232 or later, and older clients ignore them. In a file that a mixed fleet reads, keep the canonical names.
* **Both spellings set**: when a file sets both spellings, the canonical key's value applies.

### Allowlist with `strictKnownMarketplaces`

Set the allowlist to a list of these source objects. Most entries match exactly, `hostPattern` and `pathPattern` entries match as regular expressions, and `github` owner wildcards match by owner:

* **`github`**: `{ "source": "github", "repo": "your-org/approved-plugins" }`, with optional `ref` and `path`.
* **`github` owner wildcard**: `{ "source": "github", "repo": "your-org/*" }` matches every repository under that owner. The `*` must stand for the whole repository name. Claude Code ignores entries such as `*/plugins` and `your-org/tools-*` as invalid, so they match nothing. Requires Claude Code v2.1.223 or later.
* **`git`**: `{ "source": "git", "url": "https://gitlab.example.com/tools/plugins.git" }`, with optional `ref` and `path`.
* **`url`**: `{ "source": "url", "url": "https://plugins.example.com/marketplace.json" }`, with optional `headers`.
* **`file` and `directory`**: `{ "source": "file", "path": "/opt/marketplace/marketplace.json" }` or `{ "source": "directory", "path": "/opt/marketplace/plugins" }`, with absolute paths.
* **`hostPattern`**: `{ "source": "hostPattern", "hostPattern": "^github\\.example\\.com$" }`, matched against the host of `github`, `git`, and `url` sources. The pattern matches anywhere in the hostname, so anchor it with `^` and `$` as shown to match the whole host. A `github` source always counts as `github.com`. Use a `hostPattern` entry for a GitHub Enterprise Server or GitLab host where developers create their own marketplaces. The [GHES page](https://code.claude.com/docs/en/github-enterprise-server.md#allowlist-ghes-marketplaces-in-managed-settings) has the worked example.
* **`pathPattern`**: `{ "source": "pathPattern", "pathPattern": "^/opt/approved/" }`, matched against the `path` of `file` and `directory` sources. The pattern matches anywhere in the path, so start it with `^` to pin a directory prefix. `".*"` allows every local path.
* **`skills-dir`**: `{ "source": "skills-dir" }` matches no marketplace. For what it does, see [Keep skills-directory plugins loading](#keep-skills-directory-plugins-loading).

#### How entries match

A `url` entry matches on its `url` value; `headers` are not compared. For `github` and `git` entries, the `repo` or `url`, the `ref`, and the `path` must all match, or be absent on both sides:

* An entry without `ref` does not cover a source with `ref: "main"`.
* An entry for `your-org/your-marketplace` does not cover a `git` URL that clones the same repository.
* A trailing slash, a `.git` suffix, or `ssh://` in place of `https://` is a different value. When a marketplace can be cloned by more than one URL, prefer a `hostPattern` entry.

Owner-wildcard entries follow the exact rules for `ref` and match any `path` inside the repository unless the entry pins one. Wildcard matching is case-sensitive on the allowlist.

#### Keep skills-directory plugins loading

Skills-directory plugins are the plugins users keep under `~/.claude/skills/` or a project's `.claude/skills/` in folders that carry a `.claude-plugin/plugin.json`. If any allowlist is set without a `{ "source": "skills-dir" }` entry, they stop loading. If any customization type is locked with [`strictPluginOnlyCustomization`](https://code.claude.com/docs/en/settings-reference#strictpluginonlycustomization), they stop loading whether or not the entry is present. The allowlist does not apply to plain [skills](https://code.claude.com/docs/en/skills.md), meaning a `SKILL.md` without that manifest.

#### Lock every source out

An empty allowlist, `[]`, locks every marketplace source out, including the official marketplace.

### Blocklist with `blockedMarketplaces`

`blockedMarketplaces` takes the same source objects as [`strictKnownMarketplaces`](#allowlist-with-strictknownmarketplaces) and is checked first, so a source on both lists is blocked. Blocklist matching is wider than allowlist matching:

* Git URLs are canonicalized, so the `git@` and `https://` forms, `.git` suffixes, and trailing slashes of one `github.com` repository all match the same entry.
* A `github` entry also blocks the equivalent `git` URL, and the other way around.
* For an `owner/*` entry, the owner comparison is case-insensitive.
* An entry without `ref` or `path` blocks every ref and path of the repositories it matches.

This entry blocks every repository under one GitHub owner:

```json theme={null}
{
  "blockedMarketplaces": [
    { "source": "github", "repo": "untrusted-org/*" }
  ]
}
```

The `url` entries in `blockedMarketplaces` also apply when a user adds an `https://` repository URL that Claude Code [clones rather than fetches](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-marketplace-add), such as a bare `github.com` or `gitlab.com` repository URL. The user cannot add that URL if an entry names it. The match ignores the `.git` suffix and any ref the user appends after `#`. Requires Claude Code v2.1.232 or later.

### Allow the official marketplace and your own

Most organizations allow the official marketplace and their own, and register both so every machine has them. This managed settings policy allows both marketplaces, registers both, force-enables two plugins, and rejects `--plugin-dir`:

```json theme={null}
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "anthropics/claude-plugins-official" },
    { "source": "github", "repo": "your-org/*" },
    { "source": "skills-dir" }
  ],
  "extraKnownMarketplaces": {
    "claude-plugins-official": {
      "source": { "source": "github", "repo": "anthropics/claude-plugins-official" }
    },
    "your-marketplace": {
      "source": { "source": "github", "repo": "your-org/your-marketplace" }
    }
  },
  "enabledPlugins": {
    "code-formatter@your-marketplace": true,
    "deploy-helper@your-marketplace": true
  },
  "disableSideloadFlags": true
}
```

On a machine with this policy, adding any source outside the list, for example `/plugin marketplace add https://example.com/other-marketplace.git`, fails with a message containing `is blocked by enterprise policy` followed by the allowed sources. `claude --plugin-dir ./x` exits with a message naming `disableSideloadFlags`.

If the `{ "source": "skills-dir" }` entry is removed from this allowlist, [skills-directory plugins](#keep-skills-directory-plugins-loading) stop loading.

Register both marketplaces with explicit `extraKnownMarketplaces` entries, as this policy does, rather than relying on the allowlist or on the official marketplace registering itself:

* **The allowlist does not register anything**: an `extraKnownMarketplaces` entry does, and it must itself pass the allowlist. Claude Code refuses to register a managed marketplace whose source the allowlist does not match.
* **The official marketplace registers itself only in an interactive terminal session**: even there, it registers only when the allowlist permits it. A `-p` run or a terminal attached to a cloud session never registers it.
* **A blocked attempt is remembered**: if a machine ever ran under a policy that blocked the official marketplace, Claude Code records the blocked attempt and does not retry after the policy changes. An `[]` lockdown is one such policy. That machine registers it again only through an `extraKnownMarketplaces` entry such as the one in this policy, an `enabledPlugins` entry for one of its plugins, or a manual `/plugin marketplace add`.

## Set update policy

Update policy can be set per marketplace, for the whole fleet, or per user group through release channels.

### Turn auto-update on or off per marketplace

Plugin auto-update runs in the background after startup for marketplaces that have it turned on. For which marketplaces have it on by default, see [When auto-update runs](https://code.claude.com/docs/en/plugins/loading.md#when-auto-update-runs). To decide for the fleet, set `"autoUpdate": true` or `false` on a managed `extraKnownMarketplaces` entry:

* If the managed entry sets the field, Claude Code refuses the user's `/plugin` toggle with an error that starts `Auto-update for '<name>' is set by`.
* If the managed entry leaves the field unset, the user's toggle persists.

### Turn updates off for the whole fleet

To turn plugin auto-update off for every marketplace, set `DISABLE_AUTOUPDATER` in the managed `env` block, as this example does. The same variable also stops Claude Code's own updates:

```json theme={null}
{
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

To stop Claude Code's own updates but keep plugin auto-update, add `"FORCE_AUTOUPDATE_PLUGINS": "1"` to the same block. The other [environment variables that stop plugin auto-update](https://code.claude.com/docs/en/plugins/loading.md#when-auto-update-runs) work the same way.

## Recommend plugins

Marketplace owners can attach `relevance` signals to entries so Claude Code suggests the plugin when a project matches.

Suggestions from a marketplace appear only when all three hold: the marketplace is registered on the user's machine, its name is listed in `pluginSuggestionMarketplaces` in managed settings, and its source is declared in the same policy. Declare the source either as the marketplace's `extraKnownMarketplaces` entry or as an allowlist entry. The official marketplace needs only the name. See [Enable suggestions in managed settings](https://code.claude.com/docs/en/plugins/relevance.md#enable-suggestions-in-managed-settings).

> **Note:** In a cloud session's conversation, Claude can suggest plugins whether or not `pluginSuggestionMarketplaces` is set. To turn those suggestions off, see [Turn off plugin suggestions](https://code.claude.com/docs/en/claude-code-on-the-web.md#turn-off-plugin-suggestions).

## Troubleshoot policy

When plugin policy does not behave as expected on a machine, check for these symptoms first:

* **A user reports `blocked by enterprise policy`**: the message names the marketplace or its source. For an allowlist, it also lists the allowed sources. The user-facing entries are on [Troubleshoot plugins](https://code.claude.com/docs/en/plugins/troubleshooting.md).
* **A plugin the user disabled in `~/.claude/settings.json` still loads**: another settings source re-enabled it, such as a managed `enabledPlugins` entry that force-enables it. `/plugin` and `claude plugin list` show `Disabled in ~/.claude/settings.json but still loads` with that settings source.

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/org
- https://code.claude.com/docs/en/plugins/install.md — install plugins, including the Desktop app, IDE extensions and cloud sessions
- https://code.claude.com/docs/en/permissions.md — what runs before a folder is trusted (workspace trust dialog)
- https://code.claude.com/docs/en/headless — non-interactive `-p` runs
- https://code.claude.com/docs/en/plugins/dependencies.md — plugin dependencies and bundles
- https://code.claude.com/docs/en/managed-settings.md — where and when a managed policy applies
- https://code.claude.com/docs/en/plugins/loading.md — synced plugins and when auto-update runs
- https://code.claude.com/docs/en/settings-reference.md — every settings key, including `enabledPlugins`, `allowManagedHooksOnly`, `strictPluginOnlyCustomization`, `syncClaudeAiPlugins`
- https://code.claude.com/docs/en/env-vars — environment variables, including `CLAUDE_CODE_PLUGIN_DIRS` and `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL`
- https://code.claude.com/docs/en/agent-sdk/typescript — Agent SDK `addPlugins`
- https://code.claude.com/docs/en/managed-mcp — managed MCP servers and `allowedMcpServers`
- https://code.claude.com/docs/en/channels.md — restrict which channel plugins can run
- https://code.claude.com/docs/en/plugins/mods/admin.md — administering mods, `allowManagedModsOnly`, the organization's mods
- https://code.claude.com/docs/en/plugins/mods/overview.md — mods overview
- https://code.claude.com/docs/en/github-enterprise-server.md — allowlisting GHES marketplaces
- https://code.claude.com/docs/en/skills.md — plain skills
- https://code.claude.com/docs/en/plugins/cli-reference.md — `claude plugin marketplace add` and when a URL is cloned rather than fetched
- https://code.claude.com/docs/en/plugins/relevance.md — enable plugin suggestions in managed settings
- https://code.claude.com/docs/en/claude-code-on-the-web.md — turn off plugin suggestions in cloud sessions
- https://code.claude.com/docs/en/plugins/troubleshooting.md — user-facing policy messages, including blocked by your organization
- https://code.claude.com/docs/en/plugins/marketplace-reference.md — the `source` values `extraKnownMarketplaces`, `strictKnownMarketplaces`, and `blockedMarketplaces` accept
- https://code.claude.com/docs/en/plugins/host-marketplace.md — host and maintain the marketplace a policy points at
- https://code.claude.com/docs/en/plugins/security.md — what a plugin can do on a machine and how to review one before installing
- https://claude.ai/admin-settings/plugins — the claude.ai Organization settings > Plugins page
