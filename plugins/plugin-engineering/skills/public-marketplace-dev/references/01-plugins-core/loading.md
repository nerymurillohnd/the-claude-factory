# Plugin loading reference

How to trace where Claude Code loads each plugin from, which settings file decides whether it loads, and why an update changed nothing.

## Contents

- [Check which stage a plugin reached](#check-which-stage-a-plugin-reached)
  - [Plugins and marketplaces that aren't on disk at session start](#plugins-and-marketplaces-that-arent-on-disk-at-session-start)
- [Find where a plugin came from](#find-where-a-plugin-came-from)
  - [Entry name and manifest name](#entry-name-and-manifest-name)
  - [Plugins shared through a repository](#plugins-shared-through-a-repository)
  - [Skills-directory plugins blocked by managed settings](#skills-directory-plugins-blocked-by-managed-settings)
- [Find where a plugin is enabled](#find-where-a-plugin-is-enabled)
  - [Disabled in user settings but still loads](#disabled-in-user-settings-but-still-loads)
  - [Enabled in project settings but not installed](#enabled-in-project-settings-but-not-installed)
- [Find plugins on disk](#find-plugins-on-disk)
  - [In-place and copied plugins](#in-place-and-copied-plugins)
  - [Paths that escape the plugin directory](#paths-that-escape-the-plugin-directory)
  - [Cleanup of previous versions](#cleanup-of-previous-versions)
  - [Node.js package dependencies](#nodejs-package-dependencies)
    - [When the dependency install runs](#when-the-dependency-install-runs)
    - [Limits on the dependency install](#limits-on-the-dependency-install)
    - [When the dependency install fails or is skipped](#when-the-dependency-install-fails-or-is-skipped)
- [Versions and updates](#versions-and-updates)
  - [How Claude Code computes the version](#how-claude-code-computes-the-version)
  - [When Claude Code refreshes a marketplace before an install](#when-claude-code-refreshes-a-marketplace-before-an-install)
  - [When auto-update runs](#when-auto-update-runs)
    - [Which marketplaces and plugins auto-update](#which-marketplaces-and-plugins-auto-update)
- [Name conflicts](#name-conflicts)
  - [Hooks when two enabled plugins share a name](#hooks-when-two-enabled-plugins-share-a-name)
  - [Keep a session-only plugin from loading](#keep-a-session-only-plugin-from-loading)
- [Documentation References](#documentation-references)

Use this file when a plugin did not load, loaded a different copy than expected, or did not pick up an update, to find which source, settings scope, or file on disk decided that. It gives the rules Claude Code applies when a session starts and each time `/reload-plugins` runs. Use it to diagnose a user's setup.

> **Note:** These cases are covered on other pages:
>
> * **Install, enable, disable, and update steps**: see [Install and manage plugins](https://code.claude.com/docs/en/plugins/install.md)
> * **A specific error message**: see [Troubleshoot plugins](https://code.claude.com/docs/en/plugins/troubleshooting.md)

Start with [Check which stage a plugin reached](#check-which-stage-a-plugin-reached) for the three stages an installed plugin passes through, or go to the section that matches the symptom:

* A plugin that was turned off still loads: [Find where a plugin is enabled](#find-where-a-plugin-is-enabled)
* An update changed nothing: [Versions and updates](#versions-and-updates)
* Inspecting the files under `~/.claude/plugins/`: [Find plugins on disk](#find-plugins-on-disk)
* A `--plugin-dir` plugin did not load, or a same-named plugin loaded instead: [Name conflicts](#name-conflicts)
* A plugin under `~/.claude/skills/` or `.claude/skills/` did not load, and no error says why: [Skills-directory plugins blocked by managed settings](#skills-directory-plugins-blocked-by-managed-settings)

## Check which stage a plugin reached

An `enabledPlugins` entry becomes a usable plugin in stages: the settings declare it, Claude Code fetches it to disk, and the running session loads it. When a plugin does not behave as a settings file suggests, check which stage it reached:

* **Declared, in settings**: `enabledPlugins` says which plugins should be on, and `extraKnownMarketplaces` says which marketplaces should exist. When `claude plugin marketplace add` runs, Claude Code writes the marketplace to `extraKnownMarketplaces` in the user settings as well as to disk
* **Fetched, on disk under `~/.claude/plugins/`**: the records of what Claude Code has fetched, and the fetched files themselves:
  * `known_marketplaces.json` records each marketplace Claude Code has fetched, with its `source`, `installLocation`, `lastUpdated`, and `autoUpdate`. There is one `known_marketplaces.json` per user, so a marketplace added in one project is available in every project
  * `installed_plugins.json` records each install with its `scope`, `installPath`, and `version`
  * `cache/` holds the plugin files
* **Loaded, in the running session**: the plugin set Claude Code loaded at startup or at the last `/reload-plugins`. Changes to settings or to disk do not reach this layer until `/reload-plugins` runs or a new session starts. That is why `claude plugin update` ends with `Restart to apply changes.` and background updates prompt with `Run /reload-plugins to apply`

### Plugins and marketplaces that aren't on disk at session start

Plugins load at session start from `installed_plugins.json` and the cache without using the network. After the session starts, Claude Code checks the declared marketplaces in the background:

* **A marketplace that settings declare but `known_marketplaces.json` lacks**: Claude Code clones it, then reloads plugins and downloads enabled plugins that are not cached yet
* **A declared marketplace whose source changed in settings**: Claude Code re-fetches it from the new source and shows `Plugins changed. Run /reload-plugins to activate.`

An enabled plugin that neither path fetched and that has no usable cache directory shows `Plugin "<name>" not cached at <path>` in the `/plugin` **Errors** tab. For the fix, see [`Plugin "<name>" not cached at <path>`](https://code.claude.com/docs/en/plugins/troubleshooting#plugin-not-cached-at).

## Find where a plugin came from

Every plugin has an id of the form `<name>@<origin>`, which appears in settings files and in `claude plugin list --json`. The part after `@` tells where Claude Code found the plugin:

| ID ends in | How the plugin got there | How you turn it on or off |
| :- | :- | :- |
| `@<marketplace>` | You installed it from a marketplace you added | `"<name>@<marketplace>": true` or `false` under `enabledPlugins` in a settings file |
| `@inline` | You started Claude Code with `--plugin-dir` or `--plugin-url`, set [`CLAUDE_CODE_PLUGIN_DIRS`](https://code.claude.com/docs/en/env-vars#variables), or an Agent SDK app passed the `plugins` option. It loads for that session only | On for the session unless the manifest sets `defaultEnabled: false` or a settings file sets `"<name>@inline": false` |

For a marketplace plugin, `<name>` is the entry name in `marketplace.json`; for `@inline` and `@skills-dir` it is the `name` in the plugin's manifest.

The origin names in this table are reserved, so no marketplace can be named `inline`, `skills-dir`, or `synced`.

### Entry name and manifest name

A marketplace plugin has two names, and they can differ:

* **The entry name in `marketplace.json`**: the install and enable key. It is what goes in `enabledPlugins`, what the cache directory is named after, and what `claude plugin list` shows
* **The `name` in the manifest**: what the plugin's components are namespaced under, and what [name conflicts](#name-conflicts) compare

### Plugins shared through a repository

To share a plugin through a repository, list it under `enabledPlugins` in `.claude/settings.json` or place it under `.claude/skills/`. Claude Code does not scan a project's `.claude/plugins/` directory.

A cloud session does not add the marketplaces a repository lists under [`extraKnownMarketplaces`](https://code.claude.com/docs/en/settings-reference#extraknownmarketplaces), because that requires the workspace trust dialog, which a cloud session never shows.

For how to write `--plugin-dir` and skills-directory plugins, see [Create plugins](https://code.claude.com/docs/en/plugins/create.md).

### Skills-directory plugins blocked by managed settings

If a plugin folder in `~/.claude/skills/` or a project's `.claude/skills/` did not load and no error appears, an administrator may have blocked it through [managed settings](https://code.claude.com/docs/en/managed-settings.md). These folders come from the user or the repository rather than from a marketplace, so Claude Code skips them when an administrator sets one of these restrictions:

* **Customization locked to plugins**: [`strictPluginOnlyCustomization`](https://code.claude.com/docs/en/settings-reference#strictpluginonlycustomization) set to `true` or to an array naming one or more kinds of customization to lock. The whole plugin is skipped when any one kind is locked, such as `mcp`, whichever components it has.
* **Marketplace sources restricted**: a [`strictKnownMarketplaces`](https://code.claude.com/docs/en/settings-reference#strictknownmarketplaces) allowlist without a `{ "source": "skills-dir" }` entry, or a [`blockedMarketplaces`](https://code.claude.com/docs/en/settings-reference#blockedmarketplaces) list with one.

`/plugin` and `claude plugin list` show no plugin and no error for a skipped folder. Its `/<name>:<skill>` commands and agents are missing, as are its hooks and MCP servers.

Unless skills are among the locked kinds, a `SKILL.md` at the folder's root still loads as a plain skill. In that case `/<name>` keeps working, and the `/plugin` **Installed** tab lists that skill under **Skills**.

* **Confirm the cause**: run `/status` in a Claude Code session. If the `Setting sources` line lists `Enterprise managed settings`, ask the administrator whether one of these settings applies. If it does not, see [Check why a repository plugin didn't load](https://code.claude.com/docs/en/plugins/loading#check-why-a-repository-plugin-didnt-load) for other causes.
* **Load the whole plugin**: add it to a [marketplace](https://code.claude.com/docs/en/plugins/create-marketplace.md#create-a-marketplace) the organization allows and install it from there. To load it for one session instead, start `claude` from the shell with [`--plugin-dir`](https://code.claude.com/docs/en/plugins/cli-reference#flags-that-load-a-plugin-for-one-session) and the folder's path, which works unless the administrator has also turned off that flag.

## Find where a plugin is enabled

An `enabledPlugins` entry can be set in any of six sources. The table lists them from lowest precedence to highest, and who each one applies to. For the settings files themselves, see [Settings files and who they affect](https://code.claude.com/docs/en/settings.md#where-settings-live).

| Source | Where you set it | Reaches |
| :- | :- | :- |
| `--add-dir` | `.claude/settings.json` or `.claude/settings.local.json` in a directory you pass with `--add-dir` | This session only. Only a `true` value has an effect, and every other source overrides it |
| `user` | `~/.claude/settings.json` | You, in every project |
| `project` | `.claude/settings.json` | Everyone who clones the repository |
| `local` | `.claude/settings.local.json` | You, in this repository only |
| `flag` | The `--settings` value you pass at launch | This session only |
| `managed` | [Managed settings](https://code.claude.com/docs/en/managed-settings.md) | Every user the policy covers. `true` force-enables and `false` blocks, and no other source overrides them |

These sources merge key by key. For each plugin id, the value that applies is the one from the highest-precedence source that mentions the id. A source that does not mention the id leaves the value from the lower-precedence source in effect.

### Disabled in user settings but still loads

If a plugin is set to `false` in `~/.claude/settings.json` and still loads, a `true` in a higher-precedence source is overriding it. The plugin's row in `claude plugin list` and in `/plugin` shows `Disabled in ~/.claude/settings.json but still loads — project settings enable it, which overrides your user setting`. The message names the overriding source: `project`, `project, gitignored` for `.claude/settings.local.json`, `cli flag`, or `managed`.

To opt out of a project-enabled plugin on one machine, set the id to `false` in `.claude/settings.local.json`, which has higher precedence than the project file.

### Enabled in project settings but not installed

When a plugin's only `true` is in the project's `.claude/settings.json`, Claude Code does not fetch it onto a machine where it is not installed, unless its marketplace entry has a [relative-path source](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-sources) or a [seed directory](https://code.claude.com/docs/en/plugins/org.md#seed-containers-and-ci) already holds it. Instead, the `/plugin` **Errors** tab shows `Plugin "<name>" is enabled in project settings but isn't installed here`.

A relative-path plugin needs no install record because it loads from the marketplace itself.

Claude Code fetches a plugin with an external source only when one of these sources sets it to `true`:

* The user settings
* A `.claude/settings.local.json` that git doesn't track
* The `--settings` flag

## Find plugins on disk

Claude Code keeps plugin files and state records under one plugins root, which is `~/.claude/plugins` unless [`CLAUDE_CODE_PLUGIN_CACHE_DIR`](https://code.claude.com/docs/en/env-vars) is set. Every path in the table is relative to that root.

| Path | What it holds |
| :- | :- |
| `cache/<marketplace>/<plugin>/<version>/` | One directory per installed version of a marketplace plugin. `<plugin>` is the marketplace entry name and `<version>` is the [resolved version](#versions-and-updates). `${CLAUDE_PLUGIN_ROOT}` points at this directory |
| `data/<plugin-id>/` | The plugin's persistent directory, exposed as `${CLAUDE_PLUGIN_DATA}`. For how `<plugin-id>` is formed, see [Path variables and persistent data](https://code.claude.com/docs/en/plugins/components.md#path-variables-and-persistent-data). Claude Code creates it when a plugin component first uses it and keeps it across updates. By default, Claude Code deletes it when you uninstall the plugin from its last scope. For `--keep-data` and the other cases where it stays, see [plugin uninstall](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-uninstall) |
| `marketplaces/<name>/` | The clone or download of a marketplace added from GitHub, another Git host, or a URL. A marketplace added from a local `file` or `directory` source has no copy here, and its `installLocation` in `known_marketplaces.json` is the path you gave |
| `installed_plugins.json` and `known_marketplaces.json` | The records of what Claude Code has installed and which marketplaces it has fetched, described under [Check which stage a plugin reached](#check-which-stage-a-plugin-reached). A [marketplace hosted on claude.ai](https://code.claude.com/docs/en/plugins/install.md#add-from-claude-ai) is recorded in `known_marketplaces_claudeai.json` instead |
| `flagged-plugins.json` | Plugins Claude Code uninstalled because their marketplace delisted them. They appear in the **Flagged** section of `/plugin`; see [Host a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace.md) |
| `installed_plugins.set-aside.<date>.<hash>.json` and `installed_plugins.unreadable.<date>.<hash>.kept` | Dated copies Claude Code keeps before it drops install records that no version of Claude Code can use or rebuilds an unreadable `installed_plugins.json`. See [the recovery notes](https://code.claude.com/docs/en/plugins/troubleshooting.md#installed-plugins-json-could-not-be-read-and-was-rebuilt). They age out on the [`cleanupPeriodDays`](https://code.claude.com/docs/en/settings-reference#cleanupperioddays) schedule |

Because `${CLAUDE_PLUGIN_ROOT}` points at a version directory, a plugin's root path changes with every version. Keep a plugin's durable files in `${CLAUDE_PLUGIN_DATA}` instead.

### In-place and copied plugins

Claude Code loads some plugins in place from where they are kept and copies the rest into the cache, according to their origin:

* **`--plugin-dir` and skills-directory plugins**: the directory loads in place and is never copied. A `--plugin-url` archive or a `--plugin-dir` `.zip` is extracted into a session temp directory first
* **Relative-path plugins in a marketplace added from a local path**: the plugin loads in place from its path inside the marketplace folder. Edits to the source directory take effect at the next session start or `/reload-plugins`, with no need to increase the version. The plugin's hook processes and MCP and LSP servers receive a `CLAUDE_PLUGIN_ROOT` that points at the source directory. For its Node.js package dependencies, see [When the dependency install runs](#when-the-dependency-install-runs)
* **Every other marketplace plugin**: Claude Code copies the plugin into `cache/<marketplace>/<plugin>/<version>/` at install and loads that copy. Files outside the plugin directory are not copied, so when a script inside a copied plugin reads a path above the plugin root, such as `../shared`, it does not find them

### Paths that escape the plugin directory

Whether a plugin loads in place or from a cached copy, Claude Code does not let it declare components outside its own directory. It rejects a component path that resolves outside the plugin root, whether the path is declared in `plugin.json` or in a marketplace entry:

* **A path that points outside the plugin as written**, such as `../shared-utils`
* **A symlink that leads outside the plugin**, other than [links between plugins within one marketplace](https://code.claude.com/docs/en/plugins/host-marketplace.md#share-files-within-a-marketplace-with-symlinks)
* **On macOS and Linux, a path that contains a backslash anywhere in it**, even when the path stays inside the plugin. Components declared with backslash paths therefore load on Windows only, so write component paths with forward slashes, such as `./commands/deploy.md`

A rejected path appears as a [`path escapes plugin directory`](https://code.claude.com/docs/en/errors#path-escapes-plugin-directory) error, and the plugin loads without that component.

### Cleanup of previous versions

When a plugin is updated or uninstalled, Claude Code writes an `.orphaned_at` marker into the previous version directory. It removes that directory in a background cleanup 14 days later, so a session that already loaded the old version keeps running.

The sweep runs only while `installed_plugins.json` records at least one install. After the last plugin is uninstalled, orphaned directories stay until another is installed.

### Node.js package dependencies

When Claude Code copies a plugin into the cache, it also installs the plugin's Node.js package dependencies there, so the plugin's hooks and MCP servers can load them.

This section covers the npm and Bun packages a plugin declares in its own `package.json`. For plugins that depend on other plugins, see [plugin dependency versions](https://code.claude.com/docs/en/plugins/dependencies.md).

#### When the dependency install runs

Claude Code installs the dependencies into the copied version directory each time it creates one:

* When a plugin is installed
* When Claude Code updates a plugin to a new version
* At session start when an enabled plugin isn't cached yet, such as on a new machine

For a relative-path plugin [loaded in place](#in-place-and-copied-plugins) from a marketplace added from a local path, Claude Code does not install the dependencies into the source directory. Install them there manually, or from a hook into [`${CLAUDE_PLUGIN_DATA}`](https://code.claude.com/docs/en/plugins/components#path-variables-and-persistent-data).

The install runs only when the plugin's root directory contains both a `package.json` and a supported lockfile.

The lockfile decides which package manager Claude Code runs:

| Lockfile | Package manager |
| :- | :- |
| `bun.lock` | Bun |
| `npm-shrinkwrap.json` or `package-lock.json` | npm |

If a plugin contains more than one of these lockfiles, Claude Code uses the first match, checking in order: `bun.lock`, `npm-shrinkwrap.json`, `package-lock.json`.

Claude Code skips the install in these lockfile cases:

* **`bun.lockb`**: Bun's binary lockfile can't be checked. Ship a text `bun.lock` or an npm lockfile instead
* **`yarn.lock` or `pnpm-lock.yaml`**: replace it with an npm lockfile
* **A lockfile in a format Claude Code doesn't read**: an npm lockfile needs a `lockfileVersion` of `2` or `3`, which npm 7 or later writes, and a `bun.lock` needs a `lockfileVersion` no higher than `2`

Include an npm lockfile to reach the most users. Claude Code runs the matched lockfile's package manager from the user's PATH and does not try the other lockfile instead if that package manager is missing.

#### Limits on the dependency install

Claude Code constrains this dependency install so that no code from the plugin or its packages executes during it, and bounds how long it can run:

* **Registry packages only**: every dependency must be a registry package pinned in the lockfile to an exact version. A plugin with a git, GitHub, folder, workspace, or linked dependency gets no install.
* **`https` downloads**: a download link in the lockfile must use `https`, unless it points at the installing user's own default npm registry.
* **A separate install folder**: the package manager runs in a folder of its own that holds only a copy of the checked dependency list, so npm and Bun don't read the plugin's `.npmrc`, `.env`, or `bunfig.toml`. When the install succeeds, Claude Code moves the resulting `node_modules` into the plugin.
* **Frozen resolution**: the install uses exactly the versions the lockfile pins, and Claude Code skips it when `package.json` and the lockfile don't list the same dependencies
* **No lifecycle scripts**: `--ignore-scripts` keeps `preinstall`, `install`, and `postinstall` scripts from running, so dependencies that build native modules in those scripts download but don't compile during this install
* **No overrides or patches**: a plugin whose `package.json` sets npm `overrides` gets no install from an npm lockfile, and a plugin that sets Bun `patchedDependencies` gets no install from `bun.lock`
* **60-second timeout**: Claude Code stops an install that runs longer and treats it as failed

The automatic install cannot be turned off. No setting or environment variable disables it.

In restricted networks, see the [network access requirements](https://code.claude.com/docs/en/network-config.md#network-access-requirements) for the hosts to allow.

#### When the dependency install fails or is skipped

If the install fails or is skipped, the plugin still loads, but the parts of it that need the missing packages may not work.

`/plugin` and `claude plugin list` show a note on an enabled plugin whose cached copy has a lockfile and a `package.json` that lists runtime dependencies, but no `node_modules` directory. The note says whether the install didn't finish or can't run for this plugin. See [the troubleshooting entry](https://code.claude.com/docs/en/plugins/troubleshooting.md#the-packages-it-lists-are-not-installed) for what to do about each.

When the automatic install cannot provide a dependency, install it from a hook into the [persistent data directory](https://code.claude.com/docs/en/plugins/components.md#path-variables-and-persistent-data). That includes packages that need their lifecycle scripts to build, Python dependencies, plugins locked with Yarn or pnpm, and dependencies that aren't registry packages, such as git dependencies.

## Versions and updates

If a plugin's author pushed new commits and `claude plugin update` prints `<name> is already at the latest version (<version>).`, the version Claude Code computes for the plugin is unchanged, so the plugin's files on disk do not change.

Claude Code computes a version for every plugin it installs, and that version is how it detects an update. `claude plugin update` and background auto-update compute the version again and do not replace the cached copy when it matches what `installed_plugins.json` records. An update started by the user can still [retry an unfinished dependency install](https://code.claude.com/docs/en/plugins/troubleshooting.md#the-packages-it-lists-are-not-installed) in that copy.

The version also names the plugin's cache directory.

A manifest that pins `"version"` is one way the computed version stays the same across commits. See [How Claude Code computes the version](#how-claude-code-computes-the-version) for the resolution order.

A plugin [loaded in place](#in-place-and-copied-plugins) from a marketplace added from a local path loads its current source files at every session start, whatever its version string says. For a plugin from a [marketplace hosted on claude.ai](https://code.claude.com/docs/en/plugins/install.md#add-from-claude-ai), the version claude.ai records for the plugin is its version, and the manifest's `version` is not read.

### How Claude Code computes the version

For a marketplace added by source, Claude Code picks the rule by the `source` type of the plugin's marketplace entry. The [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-sources) lists the source types. For every source type in that list except `command`:

1. The `version` field in the plugin's manifest comes first
2. Then the `version` field in the plugin's marketplace entry
3. When neither is set, the version comes from the source type:

| Source type | Version when no `version` field is set |
| :- | :- |
| `github`, `url`, or `git-subdir` | The commit SHA of the source, shortened to 12 characters. A `git-subdir` version also carries a hash of the subdirectory path |
| `archive` | The SHA-256 digest, shortened to 12 characters: the `sha256` pin in the marketplace entry, or the digest of the downloaded file when there is no pin |
| Relative path inside a Git-hosted marketplace | The commit SHA of the installed directory |
| Local directory, when neither the plugin directory nor its marketplace is a git repository | `unknown` |
| `npm` | `unknown` |

Claude Code does not take the version from a repository that encloses the install path, such as a git-managed `~/.claude`.

Because the manifest comes first, a manifest that pins `"version": "1.0.0"` keeps every user on the cached copy until its author changes the string, however many commits are pushed. To let users track commits instead, leave `version` out of both the manifest and the entry. [Host a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace.md) covers which choice fits which release setup.

### When Claude Code refreshes a marketplace before an install

When a plugin is installed, Claude Code looks it up in its local copy of the marketplace catalog. The install can run as `/plugin install` in a session or `claude plugin install` in the shell, and name the plugin with or without its marketplace. The table shows which of those combinations refresh the local copy.

| Plugin name | Command | What Claude Code refreshes |
| :- | :- | :- |
| `name@marketplace` | `/plugin install` or `claude plugin install` | The named marketplace, before the lookup |
| `name` alone | `/plugin install` | Only marketplaces that have auto-update on, and only after the lookup misses |
| `name` alone | `claude plugin install` | Nothing. It reads the cached catalogs without refreshing |

The refresh before a `name@marketplace` install does not depend on the marketplace's auto-update setting or on `DISABLE_AUTOUPDATER`.

When the refresh fails, the install proceeds from the cached catalog and `claude plugin install` reports `marketplace not refreshed`.

Claude Code skips the refresh before a `name@marketplace` install when:

* The marketplace was added from a local `file` or `directory` source, or is defined inline in settings with a [`settings` source](https://code.claude.com/docs/en/settings-reference#extraknownmarketplaces)
* Claude Code refreshed the marketplace within the last 30 seconds
* `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set
* [Managed settings](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install) block the marketplace, in which case Claude Code also refuses the install

### When auto-update runs

In an interactive session, after the user sends the first message, Claude Code waits a random delay of up to ten minutes. It then refreshes every marketplace with auto-update on and updates the plugins installed from them on disk.

The running session keeps the versions it loaded, and the user sees `Plugin updated: <name> · Run /reload-plugins to apply`. Whether or not the user reloads, the new versions load on the next launch.

#### Which marketplaces and plugins auto-update

Whether a marketplace auto-updates follows the first of these that is set:

1. **`autoUpdate` on its `extraKnownMarketplaces` entry** in a settings file
2. **`autoUpdate` on its `known_marketplaces.json` entry**, which the **Enable auto-update** toggle under `/plugin` **Marketplaces** writes. When a settings file also declares the marketplace under `extraKnownMarketplaces`, the toggle writes `autoUpdate` to that settings entry as well
3. **The default**: on for Anthropic's official marketplaces such as `claude-plugins-official`, off for `knowledge-work-plugins` and `first-party-plugins`, on for [marketplaces added from claude.ai](https://code.claude.com/docs/en/plugins/install.md#add-from-claude-ai), and off for every other marketplace

If `DISABLE_UPDATES=1`, `DISABLE_AUTOUPDATER=1`, or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` is set, the whole pass is off and the **Enable auto-update** toggle is hidden, unless `FORCE_AUTOUPDATE_PLUGINS=1` is also set. The [environment variables reference](https://code.claude.com/docs/en/env-vars.md) covers each variable's wider effect.

When a copied plugin updates mid-session, hook commands, monitors, MCP servers, and LSP servers keep using the previous version's path. Run `/reload-plugins` to switch hooks, MCP servers, and LSP servers to the new path. Monitors require a session restart.

## Name conflicts

When enabled plugins from different origins share a manifest name, this order decides which one loads, from highest precedence to lowest:

1. A plugin whose id appears in managed settings `enabledPlugins`, as `true` or `false`. A `--plugin-dir` copy whose manifest name matches the id's name part is not loaded, and the user sees `--plugin-dir copy of "<name>" ignored: plugin is locked by managed settings`
2. An enabled `--plugin-dir`, `--plugin-url`, or `CLAUDE_CODE_PLUGIN_DIRS` plugin. It replaces a same-named installed marketplace plugin or skills-directory plugin:
   * **An installed marketplace plugin**: replaced silently. `claude plugin list` still shows the marketplace row as enabled, because that row reflects the settings. Only the log Claude Code writes under `~/.claude/debug/` when started with `--debug` records `Plugin "<name>" from --plugin-dir overrides installed version`
   * **A skills-directory plugin**: replaced with a `/plugin` **Errors** tab row that reads `Not loaded — the name "<name>" is already taken by a session-only plugin (--plugin-dir / --plugin-url), which takes precedence`
3. An installed marketplace plugin. A skills-directory plugin of the same name gets the same `Not loaded` row, naming the installed plugin
4. A skills-directory plugin. Between two of these, the copy under `~/.claude/skills/` loads and the project's `.claude/skills/` copy is dropped, with a row that says which path shadowed it

Because the order compares manifest names, a `--plugin-dir` plugin named `hello-plugin` replaces `hello@example-marketplace` when that plugin's manifest also says `"name": "hello-plugin"`.

### Hooks when two enabled plugins share a name

When two plugins with the same manifest name are installed and enabled from different marketplaces, both appear as enabled in `/plugin`, but the hooks of one of them are left out. One plugin per name registers the hooks in its `hooks/hooks.json`, and one plugin per name loads a [hooks module](https://code.claude.com/docs/en/plugins/mods/overview.md). When the organization's managed settings turn on one of the copies, that copy holds the name. Otherwise the copy Claude Code loads first holds it.

To see which copy holds the name, run `/plugin` in the session and open the **Errors** tab. A note there for the copy whose hooks were left out names the copy that holds the name, and the left-out copy's details show the same note. For `hooks/hooks.json` hooks the note begins `Its hooks.json hooks do not run`, and for a hooks module it begins `Its hooks module does not load`. The note requires Claude Code v2.1.296 or later.

To run the left-out copy's hooks instead, disable or uninstall the copy that holds the name, then run `/reload-plugins` in the session. The reload registers the remaining copy's hooks and clears the note. When the copy that holds the name is one the managed settings turn on, it cannot be disabled, and the other copy's hooks stay off while both are installed.

### Keep a session-only plugin from loading

To keep a `--plugin-dir` plugin from shadowing anything, or to turn one off when a parent process passes the flag, set its id to `false` in any settings file. For a plugin whose manifest name is `hello-plugin`, the entry is `"enabledPlugins": {"hello-plugin@inline": false}`. A disabled session-only plugin does not shadow, so the marketplace or skills-directory copy loads instead.

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/loading (also covers checking why a repository plugin didn't load)
- https://code.claude.com/docs/en/plugins/install.md — install, enable, disable, and update steps; marketplaces added from claude.ai
- https://code.claude.com/docs/en/plugins/troubleshooting.md — error messages by the stage that produces them, including not-cached plugins, missing packages and rebuilt `installed_plugins.json`
- https://code.claude.com/docs/en/plugins/cli-reference.md — plugin CLI flags and commands, including `--plugin-dir` and `plugin uninstall`
- https://code.claude.com/docs/en/env-vars.md — environment variables such as `CLAUDE_CODE_PLUGIN_DIRS`, `CLAUDE_CODE_PLUGIN_CACHE_DIR` and the update switches
- https://code.claude.com/docs/en/settings-reference — settings keys such as `extraKnownMarketplaces`, `strictPluginOnlyCustomization`, `strictKnownMarketplaces`, `blockedMarketplaces`, `cleanupPeriodDays`
- https://code.claude.com/docs/en/plugins/create.md — write `--plugin-dir` and skills-directory plugins
- https://code.claude.com/docs/en/managed-settings.md — managed settings
- https://code.claude.com/docs/en/plugins/create-marketplace.md — create a marketplace
- https://code.claude.com/docs/en/settings.md — settings files and who they affect
- https://code.claude.com/docs/en/plugins/marketplace-reference.md — plugin source types
- https://code.claude.com/docs/en/plugins/org.md — seed containers and CI, restricting what users can install
- https://code.claude.com/docs/en/plugins/components.md — path variables and persistent data
- https://code.claude.com/docs/en/plugins/host-marketplace.md — hosting a marketplace, delisting, symlinks within a marketplace, versioning choices
- https://code.claude.com/docs/en/errors — the `path escapes plugin directory` error
- https://code.claude.com/docs/en/plugins/dependencies.md — plugin dependency versions
- https://code.claude.com/docs/en/network-config.md — network access requirements
- https://code.claude.com/docs/en/plugins/mods/overview.md — hooks modules (mods)
