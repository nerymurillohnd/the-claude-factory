# Host and maintain a marketplace

Publish a plugin marketplace where users can reach it, grant access to a private one, and release updates and renames without breaking installs.

## Contents

- [Overview](#overview)
- [Host your marketplace](#host-your-marketplace)
  - [Register the marketplace for everyone in a repository](#register-the-marketplace-for-everyone-in-a-repository)
  - [Keep plugin files out of Git LFS](#keep-plugin-files-out-of-git-lfs)
  - [Share files within a marketplace with symlinks](#share-files-within-a-marketplace-with-symlinks)
- [Grant access to a private marketplace](#grant-access-to-a-private-marketplace)
  - [Serve users who have no git-host account](#serve-users-who-have-no-git-host-account)
  - [What background auto-update does with credentials](#what-background-auto-update-does-with-credentials)
- [Keep users up to date](#keep-users-up-to-date)
  - [Turn on auto-update](#turn-on-auto-update)
  - [Release a new version](#release-a-new-version)
  - [Hold users on one version](#hold-users-on-one-version)
- [Run release channels](#run-release-channels)
- [Rename or remove a plugin](#rename-or-remove-a-plugin)
  - [Migrate users with a renames map](#migrate-users-with-a-renames-map)
  - [Uninstall removed plugins from users' machines](#uninstall-removed-plugins-from-users-machines)
- [Depend on and recommend other plugins](#depend-on-and-recommend-other-plugins)
- [Work around what a marketplace can't do](#work-around-what-a-marketplace-cant-do)
- [Documentation References](#documentation-references)

## Overview

Hosting a marketplace means putting the `marketplace.json` catalog where other people can add it with `/plugin marketplace add`, install its plugins, and keep receiving changes after each push.

This file is for the person who operates a marketplace.

> **Note:** These cases are covered on other pages:
>
> * **The catalog file isn't written yet**: start with [Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace.md)

Start with [Host your marketplace](#host-your-marketplace) to pick a host and the command users run. Read [Keep users up to date](#keep-users-up-to-date) before the first release. Read [Rename or remove a plugin](#rename-or-remove-a-plugin) before changing a plugin's `name`.

## Host your marketplace

A marketplace can be hosted on GitHub, on another git host, as a hosted `marketplace.json` URL, or in a directory on a shared filesystem. Give users the add command for the host and tell them what they need on their machine:

| Host | Users run, in a Claude Code session | What users need |
| :- | :- | :- |
| GitHub | `/plugin marketplace add your-org/your-marketplace` | `git`, and for a private repository the access described under [Grant access to a private marketplace](#grant-access-to-a-private-marketplace) |

To pin a branch or tag of a GitHub or git-URL marketplace, tell users to append `#<ref>`, as in `your-org/your-marketplace#stable`. The [plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-marketplace-add) lists every form the command accepts.

A successful add prints `Successfully added marketplace: your-marketplace`. Claude Code takes that name from the `name` field in `marketplace.json`, not from the repository name.

Users then install a plugin by its entry's `name` and the marketplace's `name`, as in `/plugin install code-formatter@your-marketplace`.

### Register the marketplace for everyone in a repository

To share the marketplace with everyone who works in one repository, run `claude plugin marketplace add your-org/your-marketplace --scope project` there once from the shell and commit the `.claude/settings.json` it writes. Claude Code then registers the marketplace for each teammate who [trusts the folder](https://code.claude.com/docs/en/plugins/org.md#require-plugins-per-repository).

### Keep plugin files out of Git LFS

Keep the files plugins need out of [Git LFS](https://git-lfs.com). When users add a marketplace hosted in a git repository, or install a git-based plugin it lists, Claude Code clones that marketplace or plugin repository onto their machine. The clone never downloads LFS content, so LFS-tracked files arrive as pointer files.

### Share files within a marketplace with symlinks

To share files between a plugin and other parts of the same marketplace, create symbolic links inside the plugin directory. When Claude Code copies the plugin into its cache, it handles each symlink by where the target resolves:

* **Within the plugin's own directory**: the symlink is preserved as a relative symlink in the cache, so it keeps resolving to the copied target at runtime.
* **Elsewhere within the same marketplace**: the symlink is dereferenced. The target's content is copied into the cache in its place. This lets a meta-plugin's `skills/` directory link to skills defined by other plugins in the marketplace.
* **Outside the marketplace**: the symlink is skipped for security.

For plugins installed from a local path, or from a [`command` source](https://code.claude.com/docs/en/plugins/marketplace-reference#command-plugin-source) whose `mode` is the default `copy`, Claude Code preserves only symlinks that resolve within the plugin's own directory and skips all others.

The following command creates a link from inside a marketplace plugin to a shared skill defined by a sibling plugin. On Windows, use `mklink /D` from an elevated Command Prompt or enable Developer Mode:

```bash theme={null}
ln -s ../../shared-plugin/skills/foo ./skills/foo
```

## Grant access to a private marketplace

When a user adds, installs from, or updates the marketplace, Claude Code runs `git` on their machine with interactive prompts turned off and relies on whatever credentials that machine already holds. Claude Code has no git token of its own, and `marketplace.json` has no field for one.

The form of the add command given to users decides whether the clone runs over SSH or HTTPS:

* **GitHub `owner/repo`**: Claude Code probes `ssh -T git@github.com` and clones over SSH when the probe succeeds. If the probe fails, or the SSH clone itself fails, it clones over HTTPS. Users on machines without a GitHub SSH key can set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` to skip the probe and clone over HTTPS.
* **`git@host:path.git`**: SSH.
* **`https://example.com/repo.git`**: HTTPS.

Tell users what each protocol needs on their machine:

* **SSH**: the key must work without a passphrase prompt, for example because it's loaded in `ssh-agent`. The host must already be in `known_hosts`.

### Serve users who have no git-host account

These entry sources need no git account:

* **`archive`**: a zip downloaded over HTTPS. Users need neither `git` nor an account, only network access to the URL. Requires Claude Code v2.1.224 or later. Pin each archive with `sha256` so Claude Code refuses a changed download. To send credentials with the download, read [Authenticate archive downloads](https://code.claude.com/docs/en/plugins/host-marketplace#authenticate-archive-downloads).
* **A public git repository**: Claude Code clones a public `url` or `git-subdir` source over HTTPS without credentials when the entry gives an `https://` URL. For a `github` source, or a `git-subdir` source written as `owner/repo`, tell users without a GitHub SSH key to set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`.

Keep `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` in user instructions even if `claude plugin install` succeeds without it from the shell on a machine with no SSH key. For a `github` source, that command can fall back to HTTPS on its own, printing `SSH not configured, cloning via HTTPS`. Installs from `/plugin` inside a session and plugin updates don't fall back, so without the variable they fail for users who have no GitHub SSH key.

### What background auto-update does with credentials

Background auto-update is Claude Code's unattended refresh of marketplaces and installed plugins after a session starts. It's off for a marketplace until a user or admin turns it on, as covered under [Keep users up to date](#keep-users-up-to-date).

After the check, Claude Code does one of the following:

* **The checkout is up to date**: Claude Code leaves it as it is.
* **The check finds new commits, or fails because it can't reach or authenticate to the remote**: Claude Code clones the marketplace again and replaces the existing checkout with the new clone. If that clone fails, the existing checkout stays in place. The re-clone can [time out on large repositories](https://code.claude.com/docs/en/plugins/troubleshooting.md#git-clone-timed-out-after-120s).

To keep a private marketplace current, a user has this option:

* **Keep the checkout on failure**: if the user sets `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`, Claude Code keeps the existing checkout without attempting the re-clone when the background check can't reach or authenticate to the remote. Plugins keep working from the last synced state.

## Keep users up to date

Changes reach users through background auto-update, once it's turned on for the marketplace, or when users update the plugin themselves. In both cases a user gets a new copy of a plugin only when its computed version changes, as described under [Release a new version](#release-a-new-version).

### Turn on auto-update

Background auto-update is off for a marketplace by default, and `marketplace.json` has no field to turn it on. A user or an admin turns it on:

* **Tell users to turn it on**: each user goes to **Marketplaces** in `/plugin`, selects the marketplace, and selects **Enable auto-update**.
* **Ask an admin to set it**: if an admin sets `"autoUpdate": true` on the marketplace's `extraKnownMarketplaces` entry in managed settings, it's on for everyone who receives those settings. Read [Set update policy](https://code.claude.com/docs/en/plugins/org.md#set-update-policy).

Without auto-update, users receive changes when they run `/plugin marketplace update <name>` in a session or `claude plugin update <plugin>@<name>` in the shell.

For what users see when an update reaches them, read [When auto-update runs](https://code.claude.com/docs/en/plugins/loading.md#when-auto-update-runs).

### Release a new version

To release a new version to users, change the plugin's `version`. Users get a new copy only when the plugin's computed version differs from the one they have. That version comes from `plugin.json` first, then from the marketplace entry, per [Versions and updates](https://code.claude.com/docs/en/plugins/loading.md#versions-and-updates).

A plugin that users [load in place](https://code.claude.com/docs/en/plugins/loading.md#find-plugins-on-disk) from a marketplace they added from a local path isn't controlled by `version`. It loads the current files at every session start, whatever its version string says.

For every install other than an in-place load or one from a `command` source, either increase `version` on each release or omit it:

* **Bump `version` on each release**: users stay on their cached copy until the string changes. If `"version": "1.0.0"` is set and new commits are pushed without changing it, users don't receive them.
* **Omit `version`**: users track the commits instead. Leave `version` out of both `plugin.json` and the marketplace entry.

Don't set `version` in both `plugin.json` and the marketplace entry. If both are set, Claude Code uses the `plugin.json` value without warning, and `claude plugin validate` reports the mismatch as `Entry declares version "<a>" but <path>/plugin.json says "<b>"`.

### Hold users on one version

One marketplace serves one version of each plugin at a time, so users are held on a version by choosing what each entry points at:

* **`ref` and `sha` on the plugin entry**: `ref` names a branch or tag and `sha` names a commit for a `github`, `url`, or `git-subdir` source. Read [Plugin sources](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-sources).
* **`#<ref>` on the add command**: users who add `your-org/your-marketplace#stable` get that branch or tag of the catalog. For two release lines at once, read [Run release channels](#run-release-channels).
* **`<plugin>--v<version>` tags**: a dependency's version range resolves against these tags. Read [Release a plugin that others depend on](https://code.claude.com/docs/en/plugins/dependencies.md#tag-plugin-releases-for-version-resolution).

[Release a new version](#release-a-new-version) says when a changed entry reaches users.

## Run release channels

To offer stable and early-access tracks, host two marketplaces whose entries point at different refs of the same plugin, and let each user add the one they want. Claude Code has no release-channel concept, and one marketplace serves one version of each plugin at a time.

Give the two `marketplace.json` files different `name` values. Claude Code identifies a marketplace by its `name`, so a user can't have two marketplaces with the same name registered at once.

With these two catalogs, users who add `stable-tools` install `code-formatter` from the `stable` branch, and users who add `latest-tools` install it from `latest`:

```json theme={null}
{
  "name": "stable-tools",
  "owner": { "name": "Your Org" },
  "plugins": [
    { "name": "code-formatter", "source": { "source": "github", "repo": "your-org/code-formatter", "ref": "stable" } }
  ]
}
```

```json theme={null}
{
  "name": "latest-tools",
  "owner": { "name": "Your Org" },
  "plugins": [
    { "name": "code-formatter", "source": { "source": "github", "repo": "your-org/code-formatter", "ref": "latest" } }
  ]
}
```

Give the two refs different `plugin.json` versions, or omit `version` so the commit SHA distinguishes them. Updates are detected by comparing versions, so a ref that moves without a version change leaves users on the cached copy.

## Rename or remove a plugin

A plugin's `name` is its identifier. Users reference it in the `enabledPlugins` and `pluginConfigs` settings keys and in `/plugin install`, so changing it breaks every existing install.

To change the label users see in `/plugin` without breaking anything, set `displayName` in `plugin.json` and keep `name` unchanged.

### Migrate users with a renames map

When a `name` must change, add a top-level `renames` map to `marketplace.json` so Claude Code migrates existing users instead of reporting [`Plugin "<name>" not found in marketplace`](https://code.claude.com/docs/en/plugins/troubleshooting#plugin-not-found-in-marketplace). Do the same when removing an entry from `plugins`.

Map each former name to its current name, or to `null` when the plugin is gone. This marketplace renames `formatter` to `code-formatter` and records that `legacy-linter` was removed:

```json theme={null}
{
  "name": "your-marketplace",
  "owner": { "name": "Your Org" },
  "plugins": [
    { "name": "code-formatter", "source": "./plugins/code-formatter" }
  ],
  "renames": {
    "formatter": "code-formatter",
    "legacy-linter": null
  }
}
```

After the push, a user who still has the old name enabled sees one of these results:

* **Renamed entry**: the plugin loads under its new name. `claude plugin list` and the plugin's details under `/plugin` show `Renamed to "code-formatter" in the "your-marketplace" marketplace` once, and Claude Code rewrites the old key to the new one in `enabledPlugins` and `pluginConfigs` in the user, project, and local settings scopes.
* **`null` entry**: the old key is dropped from those scopes and the user sees `Removed from the "your-marketplace" marketplace`.
* **Enabled in managed settings**: the plugin still loads under its new name, but Claude Code can't rewrite managed settings, so the notice recurs until an admin updates `enabledPlugins` there.

For a marketplace users added from a git repository or URL, a renamed plugin reports [`Plugin "<name>" not cached at <path>`](https://code.claude.com/docs/en/plugins/troubleshooting#plugin-not-cached-at) until the user runs `/plugin install code-formatter@your-marketplace` once in a session.

Treat `renames` as append-only history. Keep old entries after everyone has migrated. When renaming again, add a second entry rather than editing the first, because Claude Code follows the chain from the oldest name.

In the shell, run `claude plugin validate .` after editing the map. It rejects a chain that cycles or that ends anywhere other than `null` or a name in `plugins`, with `renames.<name>: chain does not resolve`.

### Uninstall removed plugins from users' machines

To uninstall a removed plugin from users' machines rather than leave a copy behind, set `"forceRemoveDeletedPlugins": true` at the top level of `marketplace.json`. Without the field, a removed plugin stays installed and reports `Plugin "<name>" not found in marketplace` when a session loads it. With it, Claude Code does the following at each session start:

1. Compares what users installed from the marketplace against the entries and the `renames` map, and treats any plugin that is neither listed nor renamed as removed.
2. Uninstalls each removed plugin from the user, project, and local scopes. Plugins that only managed settings installed stay in place.
3. Lists each removed plugin under a **Flagged** heading in `/plugin` with the status `Removed from marketplace`.

## Depend on and recommend other plugins

An entry can declare dependencies on other plugins.

* **Version ranges**: a dependency can carry a semver range.
* **Cross-marketplace dependencies**: a dependency from another marketplace installs only when the root marketplace lists that marketplace in `allowCrossMarketplaceDependenciesOn`.

For version ranges, the `<plugin>--v<version>` git-tag convention they resolve against, and cross-marketplace trust, read [Plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies.md).

To have Claude Code suggest a plugin when a project matches it, add a `relevance` block to the entry with the signals that identify the project. Users see these suggestions only when an admin lists the marketplace in `pluginSuggestionMarketplaces`. For the signals and the enablement step, read [Plugin relevance](https://code.claude.com/docs/en/plugins/relevance.md).

## Work around what a marketplace can't do

Some things owners ask for have no field in `marketplace.json`. The nearest option for each:

* **Restrict what else users install**: the marketplace allowlist is a managed setting, `strictKnownMarketplaces`. Read [Restrict what users can install](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install).
* **Install or enable a plugin without the user asking**: no entry field installs a plugin. Managed `enabledPlugins` does that for a fleet; read [Pre-install and require plugins](https://code.claude.com/docs/en/plugins/org.md#pre-install-and-require-plugins).
* **Show different entries to different users**: entries carry no audience field, and every user who adds the marketplace sees the whole catalog. Host separate marketplaces for separate audiences.
* **Mark a plugin deprecated**: there is no deprecation state. The option is to remove the entry, map its name to `null` in `renames`, and optionally set `forceRemoveDeletedPlugins`.
* **Turn on auto-update for users**: each user turns it on under **Marketplaces** in `/plugin`, or an admin sets `autoUpdate` in managed settings. Read [Turn on auto-update](#turn-on-auto-update).
* **Carry git credentials**: no marketplace field holds a git token. Access to a git-hosted marketplace or plugin follows the user's git setup, per [Grant access to a private marketplace](#grant-access-to-a-private-marketplace). For `archive` sources, an entry can set [`headers` or `headersHelper`](https://code.claude.com/docs/en/plugins/host-marketplace#authenticate-archive-downloads) instead.

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/host-marketplace
- https://code.claude.com/docs/en/plugins/create-marketplace.md: write the `marketplace.json` catalog before hosting it
- https://code.claude.com/docs/en/plugins/cli-reference.md: every form `plugin marketplace add` accepts
- https://code.claude.com/docs/en/plugins/org.md: require plugins per repository, set update policy, restrict what users can install, pre-install and require plugins
- https://git-lfs.com: Git LFS, whose content a marketplace clone never downloads (external, not Claude Code docs)
- https://code.claude.com/docs/en/plugins/marketplace-reference: the `command` plugin source
- https://code.claude.com/docs/en/plugins/marketplace-reference.md: `marketplace.json` fields, plugin sources (`ref`, `sha`), and validation messages
- https://code.claude.com/docs/en/plugins/troubleshooting.md: git clone timeouts and the errors users see when adding or updating from a marketplace
- https://code.claude.com/docs/en/plugins/troubleshooting: `Plugin "<name>" not found in marketplace` and `Plugin "<name>" not cached at <path>`
- https://code.claude.com/docs/en/plugins/loading.md: when auto-update runs, versions and updates, finding plugins on disk
- https://code.claude.com/docs/en/plugins/dependencies.md: tag releases so plugins that depend on this one can resolve versions; cross-marketplace trust
- https://code.claude.com/docs/en/plugins/relevance.md: the `relevance` block and how suggestions are enabled
