# How plugins load

The rules that decide whether a plugin loads, which copy, scope and version, and how to read the state on disk and in settings when there is no message to look up.

## Contents

- [Gotchas](#gotchas)
- [Stages and origins](#stages-and-origins)
- [Files on disk](#files-on-disk)
- [In place or copied](#in-place-or-copied)
- [Versions and updates](#versions-and-updates)
- [Which setting wins](#which-setting-wins)
- [Repository and skills-directory plugins](#repository-and-skills-directory-plugins)
- [Synced plugins](#synced-plugins)
- [Name conflicts](#name-conflicts)
- [Apply a change to the session](#apply-a-change-to-the-session)
- [The debug log and other views](#the-debug-log-and-other-views)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- Nothing on disk or in settings reaches a running session until `/reload-plugins` or a new session.
- A manifest `version` keeps every user on the cached copy however many commits follow: bump it, or leave `version` out of the manifest and the entry to track commits.
- A project `true` overrides the user's `false`; opt out for one person with `false` in `.claude/settings.local.json`, never in the committed file.
- A `--plugin-dir` plugin with the same manifest name replaces an installed one in silence: `claude plugin list` still shows the installed row enabled.
- A plugin under `.claude/skills/` loads only from the session's primary working directory, never from a parent, and managed settings can skip it with no error.

## Stages and origins

A plugin goes through three stages: declared in settings, fetched to disk under `~/.claude/plugins/`, and loaded in the running session. Place each problem at the last stage the plugin reached.

- `claude plugin marketplace add` writes the marketplace to `extraKnownMarketplaces` in user settings and to disk. At session start, plugins load from `installed_plugins.json` and the cache without the network; a declared marketplace missing from disk is cloned in the background, and uncached enabled plugins are downloaded.
- The id's suffix names the origin: `@<marketplace>` for an install, `@inline` for `--plugin-dir`, `--plugin-url`, `CLAUDE_CODE_PLUGIN_DIRS` or the SDK's `plugins` option, `@skills-dir` for a folder under `.claude/skills/`, `@synced` for a plugin from the claude.ai account. `inline`, `skills-dir` and `synced` are reserved marketplace names.
- `@inline` and `@synced` plugins are on unless the manifest sets `defaultEnabled: false` or a setting says `false`; `@skills-dir` follows `defaultEnabled` unless a setting decides.
- The entry name is the install and enable key, the cache folder's name and what `plugin list` shows; the manifest `name` is the component namespace and what name conflicts compare.
- Claude Code never scans a project's `.claude/plugins/`.

## Files on disk

| Path under `~/.claude/plugins/` | Holds |
| :-- | :-- |
| `known_marketplaces.json` | each marketplace's `source`, `installLocation`, `lastUpdated` and `autoUpdate`, once per user |
| `installed_plugins.json` | each install's `scope`, `installPath` and `version` |
| `cache/<marketplace>/<plugin>/<version>/` | the copied files; the plugin-root placeholder points here |
| `data/<plugin-id>/` | the plugin's data folder, with every character but letters, digits, `_` and `-` replaced by `-` |
| `marketplaces/<name>/` | clones of git and URL marketplaces; a local one has none, and its `installLocation` is the path given |
| `mcpb/` | files unpacked from plugin MCP bundles |
| `known_marketplaces_claudeai.json`, `flagged-plugins.json` | claude.ai-hosted marketplaces, and delisted plugins |

`CLAUDE_CODE_PLUGIN_CACHE_DIR` moves this root, but `synced/` and `.trash/` stay under `~/.claude/plugins`. An invalid `known_marketplaces.json` fails with `Failed to load marketplace configuration` or `Marketplace configuration file is corrupted`: fix it, or replace it with `{}` and add the marketplaces again. An old version gets an `.orphaned_at` marker and is removed 14 days later.

## In place or copied

- In place, never copied: `--plugin-dir` and skills-directory plugins, and relative-path plugins of a marketplace added from a local path, whose edits apply at the next start or reload without a version bump. A `--plugin-url` archive or a `.zip` is extracted to a session temporary folder.
- Every other marketplace plugin is copied into the cache, and nothing outside the plugin's folder is copied: "works with `--plugin-dir`, breaks after install" is almost always a path that reaches outside the plugin.
- A component path is rejected, and the plugin loads without it, when it leaves the plugin as written, is a symlink that resolves outside it (links between plugins of one marketplace excepted), or holds a backslash on macOS and Linux: `path escapes plugin directory`. `EACCES` at the end means a folder on the path lacks execute permission.
- Node.js dependencies install into each copied version, never into an in-place local source. They need a `package.json` and a `bun.lock`, `npm-shrinkwrap.json` or `package-lock.json` (in that order, with no fallback manager), exact-pinned registry packages, no install scripts, no `overrides`, and finish in 60 seconds; the install can't be turned off.

## Versions and updates

- The version comes from the manifest's `version`, then the entry's `version`, then the source: a 12-character commit for `github`, `url` and `git-subdir`, a 12-character SHA-256 for `archive`, the folder's commit for a relative path in a git marketplace, and `unknown` for a local folder when neither it nor its marketplace is in git, and for `npm`. It never comes from an enclosing repository such as a git-managed `~/.claude`.
- `<name> is already at the latest version (<version>).` means that computed version didn't change, and the update replaced nothing.
- Naming `name@marketplace` refreshes that marketplace before an install; a bare name in the shell refreshes nothing. A failed refresh installs from the cached catalog and prints `marketplace not refreshed`.
- Auto-update runs in an interactive session after the first message, with a random delay of up to 10 minutes, and prints `Plugin updated: <name> · Run /reload-plugins to apply`. It is on by default for Anthropic's official marketplace and for marketplaces added from claude.ai, off for others, and `DISABLE_UPDATES`, `DISABLE_AUTOUPDATER` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` turn it off unless `FORCE_AUTOUPDATE_PLUGINS=1`.
- After a mid-session update, hooks, monitors and MCP and LSP servers keep the old path; `/reload-plugins` switches all but monitors, which need a restart.
- `engines["claude-code"]` keeps a plugin from installing, updating or loading outside its range: check it when a plugin silently refuses on one machine.

## Which setting wins

`enabledPlugins` merges key by key across six sources, lowest first: `--add-dir`, `user`, `project`, `local`, `flag` (`--settings`), `managed`. The highest source that mentions the id wins, and a managed `true` or `false` can't be overridden.

- A plugin the user disabled shows `Disabled in ~/.claude/settings.json but still loads — project settings enable it, which overrides your user setting`, naming the source.
- Until trust is saved for an `--add-dir` folder, its `extraKnownMarketplaces` are skipped and, in an interactive terminal, its `true` entries too; answering the `--add-dir` prompt doesn't save that trust.
- A project can enable a plugin without installing it: the Errors tab then says it `isn't installed here`, and `claude plugin install <name>@<marketplace> --scope project` fixes it. An external-source plugin is fetched only when user settings, an untracked `.claude/settings.local.json`, `--settings` or managed settings set it `true`.
- Without `--scope`, enable and disable act on the first of local, project and user that mentions the plugin.

## Repository and skills-directory plugins

- A repository shares a plugin through `enabledPlugins` in `.claude/settings.json` or a folder under `.claude/skills/`; Claude Code never scans a project's `.claude/plugins/`.
- A project-scope plugin loads only after the workspace trust check; trusting a parent folder or running with `-p` isn't enough. Its MCP servers go through the same per-server approval as a project `.mcp.json`; a server it declares as a `.mcpb` or `.dxt` bundle, or from a file outside the plugin, is skipped (declare it inline or in a `.mcp.json` inside the plugin); and its background monitors don't load. Neither the trust check nor these limits apply to a plugin under the user's own `~/.claude/skills/`.
- A `.claude/skills/` plugin loads only from the session's primary working directory, with no search of parent folders: launch from the repository root, or move the session there with `/cd`. In a desktop worktree it loads from the main checkout's `.claude/skills/`, not the worktree's.
- Managed `strictPluginOnlyCustomization`, a `strictKnownMarketplaces` allowlist without `{ "source": "skills-dir" }`, or `blockedMarketplaces` with it, skip skills-directory plugins with no error. A skipped folder's root `SKILL.md` still loads as a plain skill unless skills are locked; `/status` shows `Enterprise managed settings` when that is the cause.
- A `.claude/skills` folder inside a `--plugin-dir` plugin doesn't load from a session started above it.

## Synced plugins

- A synced plugin is `<name>@synced`, with no marketplace and no install record, and loads with a marketplace plugin's trust. The terminal syncs once per start, in the background; a late finish shows `Plugins changed. Run /reload-plugins to activate.`, and a change on claude.ai during a session applies at the next start.
- Nothing syncs with `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` or `apiKeyHelper`, with non-essential traffic off, in `--bare` or `--safe-mode`, or with `--setting-sources` that leaves out `user`. An old sign-in may not cover plugins: run `/login` again.
- `claude plugin disable <name>@synced` writes `"<name>@synced": false` to user settings; `syncClaudeAiPlugins: false` moves synced plugins to `~/.claude/plugins/.trash/` at the next start. A required one says `is required by your organization and can't be disabled here`.

## Name conflicts

When two plugins share a manifest name, this order decides which loads: a managed `enabledPlugins` id, then an enabled session-only plugin, then an installed marketplace plugin, then a skills-directory plugin (`~/.claude/skills/` before the project's), then a synced plugin.

- A session-only plugin over an installed one is silent; only the debug log records `Plugin "<name>" from --plugin-dir overrides installed version`. Keep it from loading with `"<name>@inline": false`.
- A session-only plugin over a skills-directory one shows `Not loaded — the name "<name>" is already taken by a session-only plugin`.
- A managed lock shows `--plugin-dir copy of "<name>" ignored: plugin is locked by managed settings`.
- Of two enabled plugins with one name, only one registers `hooks/hooks.json` hooks and one loads a hooks module; the other's details say `Its hooks.json hooks do not run` or `Its hooks module does not load`.

## Apply a change to the session

- `/reload-plugins` applies what was installed, updated, enabled, disabled or edited since the session started, and prints `Reloaded: N plugins · N skills · N agents · N hooks · N plugin MCP servers · N plugin LSP servers`, with `N errors during load. Run /plugin for details.` when something failed.
- A reload that adds or removes a plugin MCP server or the LSP tool waits for `/reload-plugins --force`, and so does one whose summary says `installed but not applied`.
- In `-p`, the desktop app and the Agent SDK it runs only when typed into the session, and doesn't connect or disconnect plugin MCP servers until the next session; over Remote Control it says `isn't available over a remote connection in this session`.

## The debug log and other views

- `claude --debug` writes `~/.claude/debug/<session-id>.txt` and prints nothing to the terminal. `--debug-file <path>` picks the file, a category filter binds only in the `=` form (`--debug=mcp,startup`), and `/debug` turns logging on mid-session. `DEBUG` turns it on only as `1`, `true`, `yes` or `on`, and `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose` adds hook matcher detail.
- `/status` lists broken agent, skill, command and output style files, hook matchers that never match and a marketplace auto-update row; `/hooks`, `/mcp`, `/skills`, `/context` and `/doctor` show the rest, and `claude doctor` runs from the shell.
- `claude --safe-mode` turns off `CLAUDE.md`, skills, plugins, hooks, MCP servers, agents and LSP servers, managed plugins included: use it to show whether a plugin causes a problem. `CLAUDE_CONFIG_DIR=<tmp>/config claude --setting-sources user` from an empty folder rules out the user's own configuration.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Plugin loading reference](https://code.claude.com/docs/en/plugins/loading) when a stage, copy, version or precedence rule decides the answer. It gives every rule this file condenses, with its examples.
- Read [Debug your configuration](https://code.claude.com/docs/en/debug-your-config) when the cause may be in the user's settings rather than the plugin. It gives each inspection command and the clean-configuration test.

## Exit

One rule here explains what loaded, or why nothing did, and the state from the diagnosis's step 2 agrees with it. Return to step 4 of the diagnosis in `SKILL.md`.
