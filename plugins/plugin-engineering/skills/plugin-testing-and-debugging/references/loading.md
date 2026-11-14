# Debug how a plugin loads (Part A)

Read this file when a plugin did not load, loaded a different copy than expected, kept loading after it was turned off, or did not pick up an update, and there is no exact message to look up. Sections B1 to B7 named below are in `messages.md`. Sources: "Plugin loading reference" (https://code.claude.com/docs/en/plugins/loading) and "Plugin commands reference" (https://code.claude.com/docs/en/plugins/cli-reference), as of Claude Code 2.1.325.

## Contents

- A1. Find the stage the plugin reached
  - Plugins and marketplaces not on disk at session start
  - Read each stage with the commands
  - Apply changes to the running session: `/reload-plugins`
- A2. Find where a plugin came from
  - Entry name and manifest name
  - Plugins shared through a repository
  - Skills-directory plugins blocked by managed settings
  - Plugins synced from claude.ai
- A3. Find where a plugin is enabled
  - Disabled in user settings but still loads
  - Enabled in an `--add-dir` directory but not loaded
  - Enabled in project settings but not installed
- A4. Find plugins on disk
  - In-place and copied plugins
  - Paths that escape the plugin directory
  - Cleanup of previous versions
  - Node.js package dependencies
- A5. Versions and updates
  - Version range: `engines["claude-code"]`
  - How the version is computed
  - Refresh before an install
  - Auto-update
  - When a command source re-runs
- A6. Name conflicts
  - Hooks when two enabled plugins share a name
  - Keep a session-only plugin from loading

Use this file when a plugin did not load, loaded a different copy than expected, or did not pick up an update. These are the rules Claude Code applies at session start and each time `/reload-plugins` runs.

Go to the section that matches the symptom:

- A plugin the user turned off still loads: A3.
- An update changed nothing: A5.
- Looking at files under `~/.claude/plugins/`: A4.
- A `--plugin-dir` plugin did not load, or a same-named plugin loaded instead: A6.
- A plugin under `~/.claude/skills/` or `.claude/skills/` did not load with no error: A2, "Skills-directory plugins blocked by managed settings".

## A1. Find the stage the plugin reached

An `enabledPlugins` entry becomes a usable plugin in three stages. Find which one it reached:

1. **Declared, in settings**: `enabledPlugins` says which plugins should be on; `extraKnownMarketplaces` says which marketplaces should exist. `claude plugin marketplace add` writes the marketplace to `extraKnownMarketplaces` in user settings as well as to disk.
2. **Fetched, on disk under `~/.claude/plugins/`**:
   - `known_marketplaces.json`: each fetched marketplace with `source`, `installLocation`, `lastUpdated`, `autoUpdate`. One per user, so a marketplace added in one project is available in every project.
   - `installed_plugins.json`: each install with `scope`, `installPath`, `version`.
   - `cache/`: the plugin files.
3. **Loaded, in the running session**: the set loaded at startup or at the last `/reload-plugins`. Changes to settings or disk do not reach this layer until `/reload-plugins` or a new session. That is why `claude plugin update` ends with `Restart to apply changes.` and background updates say `Run /reload-plugins to apply`.

### Plugins and marketplaces not on disk at session start

Plugins load at session start from `installed_plugins.json` and the cache, without the network. Afterwards Claude Code checks declared marketplaces in the background:

- Declared in settings but missing from `known_marketplaces.json`: Claude Code clones it, reloads plugins and downloads enabled plugins not cached yet.
- Declared with a source that changed in settings: Claude Code re-fetches it and shows `Plugins changed. Run /reload-plugins to activate.`

An enabled plugin that neither path fetched and that has no usable cache directory shows `Plugin "<name>" not cached at <path>` in the `/plugin` Errors tab (fix in `messages.md`, B4).

### Read each stage with the commands

- **`claude plugin list`** prints plugins grouped as `Installed plugins:`, `Session-only plugins (--plugin-dir / --plugin-url):`, `Skills-directory plugins (.claude/skills/*):` and `Synced from claude.ai`, or ``No plugins installed. Use `claude plugin install` to install a plugin.`` A session-only plugin appears only when the same flag precedes the subcommand, as in `claude --plugin-dir ./my-plugin plugin list`. A folder in `CLAUDE_CODE_PLUGIN_DIRS` needs no flag: with the variable set, a plain `claude plugin list` shows it under `Session-only plugins` as `<name>@inline` (observed on 2.1.325). Check the variable whenever a session-only copy appears that nobody passed with a flag.
- **`claude plugin list --json`** prints one object per installation. Always present: `id` (`name@marketplace`, `name@inline`, `name@skills-dir`, `name@synced`), `version` (for an install, the computed version; otherwise the manifest's, or `unknown`), `scope` (`user`, `project`, `local`, `managed`; `user` or `project` for skills-directory plugins; `session`; `synced`), `enabled` (in the merged settings), `installPath` (except for a plugin loaded in place from its marketplace folder). When they apply: `readFromFolder` and `folderVersion` for a plugin loaded in place (v2.1.289; `folderVersion` can differ from `version`), `installedAt`, `lastUpdated`, `projectPath` (project and local scope), `mcpServers`, `errors` (load errors), `notes` (warnings such as authoring issues or packages not installed), `errorDetails` and `noteDetails` with a diagnostic `type` and the names each refers to (v2.1.268), `hasUserConfig` (only for a plugin that loaded, v2.1.285), `projectEnabled` (whether the project's `.claude/settings.json` turns it on, v2.1.285).
  - `--available` with `--json` returns one object with `installed` and `available` (each uninstalled marketplace plugin's `pluginId`, `name`, `marketplaceName`, `source`, `description`, `version`, `installCount`).
  - `--data-size [plugin]` with `--json` adds `dataDirSize` (`bytes`, `human`) or `dataDirUnreadable` (v2.1.285). A name with no install record prints `--data-size names a plugin that is not installed` and exits 1.
- **`claude plugin details <name>`** shows a loaded plugin's name, version, description and source, then `Component inventory` (skills, agents, hooks, MCP servers, LSP servers), `Projected token cost` and `Per-component (rounded)`. The plugin must be loaded: installed, in a skills directory, or passed with `--plugin-dir` or `--plugin-url` in the same command. For one that is not loaded it prints ``Plugin "formatter" not found. Run `claude plugin list` to see installed plugins, or pass --plugin-dir <path> to load one from disk.`` and exits 1. For an id ending in `@builtin` that it does not find: ``Plugin "<name>@builtin" not found. Built-in plugins don't appear in `claude plugin list`. To see the ones available in a session, run /plugin in Claude Code and open the Installed tab.``
- **`claude plugin marketplace list`** prints `Configured marketplaces:` with one `Source:` line each, or `No marketplaces configured`. With `--json`: `name`, `source` (`github`, `git`, `url`, `directory`, `file`, `claudeai`), `repo`, `url`, `path`, `ref`, `installLocation`; a claude.ai marketplace carries `marketplaceId`, `organizationUuid`, `scope` and `status` instead of `installLocation`. With claude.ai sync on, the text output ends with a `From claude.ai:` section (v2.1.273) that `--json` leaves out.
- **`/plugin list [--enabled|--disabled]`** in a session prints marketplace-installed plugins inline; a plugin whose enable state is not applied yet is marked `— run /reload-plugins to apply`.

### Apply changes to the running session: `/reload-plugins`

- `/reload-plugins [--force]` applies plugins installed, updated, enabled, disabled or edited on disk since the session started. Closing the `/plugin` panel with pending changes runs it automatically; run it yourself after a `claude plugin` command in another terminal.
- It prints `Reloaded: N plugins · N skills · N agents · N hooks · N plugin MCP servers · N plugin LSP servers` (no MCP server count without an interactive terminal), and `N errors during load. Run /plugin for details.` when a plugin failed. The skills count covers `commands/` entries and `SKILL.md` skills; the agents count includes agents not from plugins.
- Missing dependencies of a reloaded plugin are installed, the reload runs again, and the summary ends `(+ N dependencies: <names>) resolved`.
- A reload that would add or remove a plugin MCP server or the `LSP` tool, and so invalidate the prompt cache, is not applied: `This reload changes MCP tools (<server>) — your next message will re-read the whole conversation instead of using the cache. Run /reload-plugins --force to apply.` `--force` (or `force`) applies it.
- It also runs without an interactive terminal (desktop app, Agent SDK, `-p`) from v2.1.260, only when typed into the session itself. Through Remote Control or a relayed message it replies `/reload-plugins isn't available over a remote connection in this session.` and reloads nothing. In those sessions it does not connect or disconnect plugin MCP servers; that happens in the next session.

## A2. Find where a plugin came from

Every plugin has an id `<name>@<origin>`, as shown in settings files and `claude plugin list --json`. The origin says how it got there and how it is turned on or off:

- `@<marketplace>`: installed from an added marketplace. On or off with `"<name>@<marketplace>": true|false` under `enabledPlugins`.
- `@inline`: loaded with `--plugin-dir`, `--plugin-url`, `CLAUDE_CODE_PLUGIN_DIRS`, or an Agent SDK app's `plugins` option, for that session only. On unless the manifest sets `defaultEnabled: false` or a settings file sets `"<name>@inline": false`.
  - `--plugin-dir <path>` loads a directory or a `.zip` of one; a folder of plugins loads each child folder that holds `.claude-plugin/plugin.json`; one path per flag, repeatable: `claude --plugin-dir ./my-plugin --plugin-dir ./other.zip`.
  - `--plugin-url <url>` fetches a `.zip`; repeat the flag or pass several URLs in one quoted value: `claude --plugin-url "https://example.com/a.zip https://example.com/b.zip"`.
  - A session-only plugin with the same name as an installed one loads instead of it for that session, unless it was disabled with `claude plugin disable <name>@inline` or managed settings lock that name.
  - `disableSideloadFlags` in managed settings rejects both flags and `CLAUDE_CODE_PLUGIN_DIRS` folders: Claude Code prints that the flag is disabled by managed settings and exits 1 without starting.
- `@skills-dir`: a plugin directory with `.claude-plugin/plugin.json` under `~/.claude/skills/` or the project's `.claude/skills/`. Follows the manifest's `defaultEnabled` unless a settings file sets `"<name>@skills-dir"`.
- `@synced`: turned on for the claude.ai account, by the user or the organization, and downloaded. On unless the manifest sets `defaultEnabled: false` or a settings file sets `"<name>@synced": false`. A plugin the organization marks required loads regardless.

For a marketplace plugin, `<name>` is the entry name in `marketplace.json`; for `@inline` and `@skills-dir` it is the manifest `name`. `inline`, `skills-dir` and `synced` are reserved, so no marketplace can use them.

### Entry name and manifest name

A marketplace plugin has two names, which can differ:

- The entry name in `marketplace.json`: the install and enable key, what `enabledPlugins` uses, what the cache directory is named after, what `claude plugin list` shows.
- The manifest `name`: what components are namespaced under, and what name conflicts (A6) compare.

### Plugins shared through a repository

- Share a plugin through a repository by listing it under `enabledPlugins` in `.claude/settings.json` or placing it under `.claude/skills/`. Claude Code does not scan a project's `.claude/plugins/`.
- A cloud session does not add marketplaces a repository lists under `extraKnownMarketplaces`, because that needs the workspace trust dialog, which a cloud session never shows.
- A project-scope plugin loads only after the same trust check as project allow rules in `.claude/settings.json`. Trusting a parent folder or running with `-p` is not enough. Components that run code are restricted further:
  - its MCP servers need the same per-server approval as a project `.mcp.json`;
  - MCP servers declared as an MCP bundle (`.mcpb` or `.dxt`) or from a file outside the plugin directory are skipped; declare them inline or in a `.mcp.json` inside the plugin;
  - background monitors do not load.
- Neither the trust check nor these limits apply to a plugin under the user's own `~/.claude/skills/`.

When a plugin in a repository's `.claude/skills/` does not load, check in this order:

1. **In a subdirectory**: Claude Code reads `.claude/skills/` of the session's primary working directory only and does not search parent directories for plugins. Launch from the repository root, or move the session with `/cd` (v2.1.246 or later).
2. **Desktop app, in a worktree**: the plugin loads from the main checkout's `.claude/skills/`, not the worktree's.
3. **Folder not trusted**: it loads only after the workspace trust dialog is accepted.
4. **Organization manages Claude Code**: see the next section.

### Skills-directory plugins blocked by managed settings

A plugin folder in `~/.claude/skills/` or `.claude/skills/` that did not load, with no error, may be blocked by managed settings. Claude Code skips these folders when:

- `strictPluginOnlyCustomization` is `true` or an array naming any kind of customization; the whole plugin is skipped when any one kind is locked, such as `mcp`, whatever components it has;
- a `strictKnownMarketplaces` allowlist has no `{ "source": "skills-dir" }` entry, or a `blockedMarketplaces` list has one.

`/plugin` and `claude plugin list` show no plugin and no error for a skipped folder; its `/<name>:<skill>` commands, agents, hooks and MCP servers are missing. Unless skills are among the locked kinds, a `SKILL.md` at the folder's root still loads as a plain skill, so `/<name>` works and the Installed tab lists it under Skills.

1. Confirm: run `/status`. If `Setting sources` lists `Enterprise managed settings`, ask the administrator whether one of these settings applies. If not, check the repository causes above.
2. Load the whole plugin: add it to a marketplace the organization allows and install from there, or load it for one session with `claude --plugin-dir <folder>`, unless the administrator also turned that flag off.

### Plugins synced from claude.ai

- A plugin turned on for the claude.ai account, including by the organization, loads in Claude Code as `<name>@synced`, with no marketplace and no install record.
- In terminal sessions its skills, agents, hooks, MCP servers and LSP servers all load, with the same trust as an installed marketplace plugin. For what Cowork loads, see the component support table at https://claude.com/docs/plugins/platform-support#compare-component-support-by-app.
- Cowork: downloaded into the session's environment at session start. In a cloud Cowork session, after turning a plugin on or off, keep working; if nothing changes after a few messages, start a new session.
- Terminal: syncs once in the background at each start (v2.1.273 or later), downloading new and updated plugins and removing turned-off ones. When the sync finishes after the session started, it shows `Plugins changed. Run /reload-plugins to activate.` A change on claude.ai during a terminal session is applied at the next start.

Synced plugins are neither downloaded nor loaded in terminal sessions, even after `/login`, when:

- `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` or an `apiKeyHelper` supplies the credential instead of the claude.ai sign-in;
- the session does not fetch feature flags, for example with `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`;
- the session is in bare mode or started with `--safe-mode`;
- `--setting-sources` leaves out `user`.

A sign-in from an earlier version does not cover plugins until it is renewed in the background; run `/login` again and the sync starts at the next start.

Control which synced plugins load:

- One plugin: `claude plugin disable <name>@synced`, or the Installed tab, saves `"<name>@synced": false` in user `enabledPlugins`. To keep it out of a project everywhere, set the key in the committed `.claude/settings.json`.
- Every synced plugin on a machine: `syncClaudeAiPlugins: false` in user settings, or in managed settings. Claude Code stops downloading and, at the next start, moves synced plugins to `~/.claude/plugins/.trash/`. If the organization turns off Skills on claude.ai, plugins stop syncing too.
- A required plugin loads even if disabled earlier. `claude plugin disable` refuses with `Plugin "<name>@synced" is required by your organization and can't be disabled here. Contact your admin to change it.`, and `claude plugin list` marks it `required by your org`.

## A3. Find where a plugin is enabled

`enabledPlugins` can be set in six sources, from lowest to highest precedence:

1. `--add-dir`: `.claude/settings.json` or `.claude/settings.local.json` in a directory passed with `--add-dir`. This session only; only `true` has an effect, and every other source overrides it.
2. `user`: `~/.claude/settings.json`. The user, in every project.
3. `project`: `.claude/settings.json`. Everyone who clones the repository.
4. `local`: `.claude/settings.local.json`. The user, in this repository.
5. `flag`: the `--settings` value at launch. This session only.
6. `managed`: managed settings. Every user the policy covers; `true` force-enables and `false` blocks, and nothing overrides them.

They merge key by key: for each plugin id, the highest-precedence source that mentions it wins; a source that does not mention it leaves the lower value in effect.

### Disabled in user settings but still loads

A `true` in a higher source overrides the user's `false`. The row in `claude plugin list` and `/plugin` reads `Disabled in ~/.claude/settings.json but still loads — project settings enable it, which overrides your user setting`, naming the source: `project`, `project, gitignored` (for `.claude/settings.local.json`), `cli flag` or `managed`. To opt out of a project-enabled plugin on this machine, set the id to `false` in `.claude/settings.local.json`.

### Enabled in an `--add-dir` directory but not loaded

A `true` in the added directory is read only when that file's setting sources are on: `settings.json` needs `project`; `settings.local.json` needs `project` and `local`. `user`, `project` and `local` are on by default in the CLI. Example: `claude --setting-sources user --add-dir ./shared` reads neither file; pass `--setting-sources user,project` for `settings.json`, or `user,project,local` for `settings.local.json`.

### Enabled in project settings but not installed

A plugin enabled only in `.claude/settings.json` does not load at session start until it is installed on the machine. With its marketplace on the machine, the Errors tab shows `Plugin "<name>" is enabled in project settings but isn't installed here` or `Plugin "<name>" not cached at <path>`. If it shows neither, add the marketplace first; its source is in `extraKnownMarketplaces` of `.claude/settings.json`, or ask the maintainer.

1. From the project, with the plugin's key in `enabledPlugins`: `claude plugin install <name>@<marketplace> --scope project`.
2. Run `/reload-plugins` or start a new session. Repeat in each clone, or use `--scope user` for all projects.

No install is needed when the plugin is in a seed directory; when it is listed by a relative path in a marketplace added from a local path (it loads at session start); or, for the current session only, when it is listed by a relative path in an added git marketplace: run `/reload-plugins`, or for one `-p` run set `CLAUDE_CODE_SYNC_PLUGIN_INSTALL=1`.

A plugin with an external source is fetched only when user settings, an untracked `.claude/settings.local.json`, the `--settings` flag or managed settings set it to `true`.

## A4. Find plugins on disk

The plugins root is `~/.claude/plugins` unless `CLAUDE_CODE_PLUGIN_CACHE_DIR` is set. Relative to it:

- `cache/<marketplace>/<plugin>/<version>/`: one directory per installed version; `<plugin>` is the entry name, `<version>` the resolved version (A5). `${CLAUDE_PLUGIN_ROOT}` points here.
- `data/<plugin-id>/`: the persistent directory, `${CLAUDE_PLUGIN_DATA}`. Created on first use, kept across updates, deleted by default when the plugin is uninstalled from its last scope.
- `marketplaces/<name>/`: the clone or download of a marketplace added from GitHub, another git host or a URL. A marketplace added from a local `file` or `directory` has no copy here; its `installLocation` is the given path.
- `synced/`: plugins synced from claude.ai. `.trash/`: plugins the sync removed.
- `installed_plugins.json` and `known_marketplaces.json`: the records (A1). A marketplace hosted on claude.ai is recorded in `known_marketplaces_claudeai.json`.
- `flagged-plugins.json`: plugins uninstalled because their marketplace delisted them; shown in the Flagged section of `/plugin`.
- `installed_plugins.set-aside.<date>.<hash>.json` and `installed_plugins.unreadable.<date>.<hash>.kept`: dated copies kept before dropping unusable records or rebuilding an unreadable file (B4). They age out on the `cleanupPeriodDays` schedule.

Because `${CLAUDE_PLUGIN_ROOT}` points at a version directory, the plugin's root changes with every version. Durable files belong in `${CLAUDE_PLUGIN_DATA}`.

### In-place and copied plugins

- `--plugin-dir` and skills-directory plugins: load in place, never copied. A `--plugin-url` archive or a `--plugin-dir` `.zip` is extracted into a session temp directory first.
- Relative-path plugins in a marketplace added from a local path: load in place from the marketplace folder. Edits apply at the next session start or `/reload-plugins`, with no version bump. Hooks, MCP and LSP servers get a `CLAUDE_PLUGIN_ROOT` pointing at the source directory.
- `command`-source plugins in link mode: the directory the command printed loads in place through links in the cache entry.
- Every other marketplace plugin: copied into `cache/<marketplace>/<plugin>/<version>/` at install, and that copy loads. Files outside the plugin directory are not copied, so a script that reads `../shared` does not find it.

### Paths that escape the plugin directory

In place or copied, Claude Code rejects a component path that resolves outside the plugin root, from `plugin.json` or a marketplace entry:

- a path outside the plugin as written, such as `../shared-utils`;
- a symlink leading outside the plugin, except links between plugins in one marketplace;
- on macOS and Linux, any path containing a backslash, even inside the plugin. Write component paths with forward slashes, such as `./commands/deploy.md`.

A rejected path shows `path escapes plugin directory`, and the plugin loads without that component.

### Cleanup of previous versions

On update or uninstall, the previous version directory gets an `.orphaned_at` marker and is removed 14 days later, so a session that loaded it keeps running. The sweep runs only while `installed_plugins.json` records at least one install.

### Node.js package dependencies

When a plugin is copied into the cache, Claude Code installs its npm or Bun dependencies there. (For plugin-to-plugin dependencies, see the plugin dependencies page.)

When it runs: on install, on update to a new version, and at session start when an enabled plugin is not cached yet. It does not install into the source directory of a relative-path plugin loaded in place from a local marketplace; install them there, or from a hook into `${CLAUDE_PLUGIN_DATA}`.

It runs only when the plugin root has both `package.json` and a supported lockfile. The lockfile picks the manager, first match in this order: `bun.lock` (Bun), `npm-shrinkwrap.json`, `package-lock.json` (npm). It runs that manager from the user's `PATH` and does not fall back to another if it is missing. Include an npm lockfile to reach the most users; for an npm-source plugin use `npm-shrinkwrap.json`, because npm excludes `package-lock.json` from published packages.

It is skipped for `bun.lockb` (ship `bun.lock` or an npm lockfile), for `yarn.lock` or `pnpm-lock.yaml` (replace with an npm lockfile), and for unreadable formats (npm `lockfileVersion` must be 2 or 3; `bun.lock` no higher than 2).

Limits: registry packages pinned to exact versions only (a git, GitHub, folder, workspace or linked dependency gets no install); `https` download links unless on the user's default npm registry; a separate install folder, so `.npmrc`, `.env` and `bunfig.toml` are not read; frozen resolution, skipped when `package.json` and the lockfile disagree; `--ignore-scripts`, so native builds download but do not compile; no npm `overrides` and no Bun `patchedDependencies`; a 60-second timeout. It cannot be turned off. For restricted networks, see the network access requirements.

When it fails or is skipped, the plugin still loads but parts needing the packages may not work, and `/plugin` and `claude plugin list` show a note (B4, "The packages it lists are not installed"). For what the automatic install cannot provide (packages that need lifecycle scripts, Python dependencies, Yarn or pnpm, git dependencies), install from a hook into `${CLAUDE_PLUGIN_DATA}`.

## A5. Versions and updates

If the author pushed commits and `claude plugin update` prints `<name> is already at the latest version (<version>).`, the computed version did not change, so nothing on disk changed. Update and auto-update recompute the version and do not replace the cache when it matches `installed_plugins.json`. An update can still retry an unfinished dependency install. The version also names the cache directory.

A plugin loaded in place from a local marketplace loads its current files at every start whatever its version. For a marketplace hosted on claude.ai, the version claude.ai records is the version, and the manifest `version` is not read.

### Version range: `engines["claude-code"]`

From v2.1.323, `plugin.json` can set `engines["claude-code"]` to a version range. A plugin outside its range is not installed, updated or loaded, and install and update pick the newest version that fits (changelog, 2.1.323; not yet on the manifest reference page). When a plugin installs on one machine and is skipped on another, compare `claude --version` on both with this range.

### How the version is computed

For every source type except `command`:

1. the manifest `version`;
2. then the marketplace entry's `version`;
3. when neither is set, by source type: `github`, `url`, `git-subdir` use the 12-character commit SHA (`git-subdir` also carries a hash of the subdirectory path); `archive` uses the 12-character SHA-256 (the entry's `sha256` pin, or the downloaded file's digest); a relative path in a git-hosted marketplace uses the installed directory's commit SHA; a local directory outside git and `npm` give `unknown`.

The version is never taken from a repository that encloses the install path, such as a git-managed `~/.claude`.

For `command` sources the version always comes from the command's output: a 12-character hash, or `<manifest version>-<hash>` when the manifest sets one. The entry's `version` is ignored.

Because the manifest comes first, a pinned `"version": "1.0.0"` keeps every user on the cached copy until the author changes it, however many commits follow. To let users track commits, leave `version` out of both the manifest and the entry.

### Refresh before an install

- `name@marketplace` with `/plugin install` or `claude plugin install`: refreshes the named marketplace before the lookup, regardless of auto-update or `DISABLE_AUTOUPDATER`.
- `name` alone with `/plugin install`: refreshes only auto-update marketplaces, and only after the lookup misses.
- `name` alone with `claude plugin install`: no refresh; reads the cached catalogs.

If the refresh fails, the install uses the cached catalog and `claude plugin install` reports `marketplace not refreshed`. The refresh is skipped when the marketplace was added from a local `file` or `directory` or is an inline `settings` source, when a seed directory supplies it, when it was refreshed in the last 30 seconds, when `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set, or when managed settings block it (the install is then refused).

### Auto-update

- In an interactive session, after the first message and a random delay of up to ten minutes, Claude Code refreshes every auto-update marketplace and updates their plugins on disk. The running session keeps its versions and shows `Plugin updated: <name> · Run /reload-plugins to apply`; new versions load on the next launch regardless.
- Whether a marketplace auto-updates is the first of: `autoUpdate` on its `extraKnownMarketplaces` entry; `autoUpdate` on its `known_marketplaces.json` entry (written by the Enable auto-update toggle, also into the settings entry when one exists); the default (on for Anthropic's official marketplaces such as `claude-plugins-official`, off for `knowledge-work-plugins` and `first-party-plugins`, on for marketplaces added from claude.ai, off for all others).
- `DISABLE_UPDATES=1`, `DISABLE_AUTOUPDATER=1` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` turn the pass off and hide the toggle, unless `FORCE_AUTOUPDATE_PLUGINS=1` is also set.
- A plugin whose entry declares a `headersHelper` is skipped by auto-update.
- When a copied plugin updates mid-session, hooks, monitors, MCP and LSP servers keep the previous version's path. `/reload-plugins` switches hooks, MCP and LSP servers; monitors need a restart.

### When a command source re-runs

A `command`-source plugin re-runs its accepted command on every install or update; once per session in the background shortly after start (independent of auto-update and `DISABLE_AUTOUPDATER`); and at startup or `/reload-plugins` when the installed version is missing from the cache. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` skips the two background runs. When the hashed output changed, the result installs as a new version and reloads in the interactive session with a notification; if that would invalidate the prompt cache, Claude Code asks for `/reload-plugins`, which warns about the cost and applies with `--force`.

## A6. Name conflicts

When enabled plugins from different origins share a manifest name, the highest of these loads:

1. A plugin whose id is in managed `enabledPlugins`, `true` or `false`. A matching `--plugin-dir` copy is not loaded: `--plugin-dir copy of "<name>" ignored: plugin is locked by managed settings`.
2. An enabled `--plugin-dir`, `--plugin-url` or `CLAUDE_CODE_PLUGIN_DIRS` plugin. It replaces an installed marketplace plugin silently (`claude plugin list` still shows that row as enabled; only the `--debug` log records `Plugin "<name>" from --plugin-dir overrides installed version`), and a skills-directory plugin with an Errors row `Not loaded — the name "<name>" is already taken by a session-only plugin (--plugin-dir / --plugin-url), which takes precedence`.
3. An installed marketplace plugin. A same-named skills-directory plugin gets the same `Not loaded` row naming it.
4. A skills-directory plugin. Between two, `~/.claude/skills/` wins over the project's `.claude/skills/`, with a row saying which path shadowed it.
5. A synced plugin. Any other enabled origin with its name loads instead and the synced copy is reported as not loaded; to use the claude.ai copy, disable the other.

The order compares manifest names: a `--plugin-dir` plugin named `hello-plugin` replaces `hello@example-marketplace` when that plugin's manifest also says `"name": "hello-plugin"`.

### Hooks when two enabled plugins share a name

Two installed plugins with the same manifest name from different marketplaces both show as enabled, but only one registers its `hooks/hooks.json` hooks and only one loads a hooks module. The copy managed settings turn on holds the name; otherwise the copy loaded first. In `/plugin`, the Errors tab and the left-out copy's details show a note naming the holder: `Its hooks.json hooks do not run` or `Its hooks module does not load` (v2.1.296 or later). To use the other copy's hooks, disable or uninstall the holder, then `/reload-plugins`. A holder turned on by managed settings cannot be disabled.

### Keep a session-only plugin from loading

Set its id to `false` in any settings file, such as `"enabledPlugins": {"hello-plugin@inline": false}`. A disabled session-only plugin does not shadow, so the marketplace or skills-directory copy loads.
