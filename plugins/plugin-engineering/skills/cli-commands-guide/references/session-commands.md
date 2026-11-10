# `/plugin` and `/reload-plugins` in a session

The slash commands typed inside a Claude Code session. Facts come from the CLI reference page, the install guide, the platform-support page (`https://claude.com/docs/plugins/platform-support.md`), the changelog through 2.1.319, and runs of each form in an interactive terminal session of Claude Code 2.1.319, with `/plugin`, `/plugin help`, `list`, `directory`, `tag`, `marketplace list` and `/reload-plugins` run again on 2.1.321. "Verified on X" marks output observed on that binary. Under each heading, `Official page:` links the matching section of the official docs: read it when a fact here looks outdated, and for anything this file doesn't cover.

## Contents

- Where `/plugin` runs
- Every `/plugin` form
- What the panel shows
- Messages
- `/reload-plugins`

## Where `/plugin` runs

Official page: <https://code.claude.com/docs/en/plugins/install#install-a-plugin>

- `/plugin` runs only in an interactive terminal session. `/plugins` and `/marketplace` are aliases of `/plugin` itself, so `/marketplace list` runs `/plugin list` and lists plugins, not marketplaces (verified on 2.1.319). Use `/plugin marketplace list` for marketplaces.
- `claude -p` and other non-interactive runs: Claude replies `/plugin isn't available in this environment.` Installed plugins still load. Manage them from the shell with `claude plugin` commands.
- Desktop app, Code tab (local or SSH session): the + button next to the prompt box → Add plugins (or Plugins → Browse plugins). 
- VS Code: type `/plugins` to open Manage plugins; changes apply to open sessions without a restart.
- JetBrains: the plugin runs Claude Code in the IDE's terminal, so the terminal forms apply.
- Cloud session (including claude.ai/code): no plugin browser. It doesn't load plugins installed on your own machine or the ones the repository's `.claude/settings.json` turns on. Plugins turned on for the claude.ai account arrive as `<name>@synced` (verified in a 2.1.319 cloud session with `claude plugin list`).
- Agent SDK: load plugins through the SDK's `plugins` option.
- The shell subcommands `init`, `update`, `details`, `prune`, `eval`, `eval init` and `test` have no session form. In a session, update a plugin from the Installed tab (Update now).
- `/plugin tag` takes only `--push`, `--dry-run` and `--force`/`-f`: for `-m`/`--message` and `--remote`, use `claude plugin tag`.

## Every `/plugin` form

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#plugin-in-a-session>

A `<plugin>` is a plugin `name` or `name@marketplace`.

- `/plugin`: opens the panel on the Discover tab. Any unrecognized first word after `/plugin` does the same (verified on 2.1.319: `/plugin zzqx` opened Discover with all marketplaces).
- `/plugin help` (aliases `/plugin --help`, `/plugin -h`): docs: shows the usage list of `/plugin` subcommands. Verified on 2.1.319 and again on 2.1.321 in a tmux terminal session: printed nothing; the transcript recorded `(no content)` for all three spellings. Use `claude plugin --help` in a shell for the command list.
- `/plugin list [--enabled|--disabled]` (alias `ls`): prints marketplace-installed plugins inline, with version, scope and status. A filter flag shows only that state. A plugin whose enable state hasn't been applied yet is marked `— run /reload-plugins to apply`. With none: ``No plugins installed. Use `/plugin install` to install a plugin.`` (verified on 2.1.319).
- `/plugin install` (alias `i`): opens the Discover tab.
- `/plugin install <plugin>`: opens the plugin's details in the Discover tab; with `name@marketplace`, in that marketplace's list. It doesn't install right away: you review the details and pick a scope (Install for you / for all collaborators on this repository / for you, in this repo only).
- `/plugin install <source>` with a path, URL or `owner/repo`: reports a marketplace-not-found error and installs nothing, even for a source already added. Verified on 2.1.319: `Marketplace "./tp" not found`, `Marketplace "owner/repo" not found`.
- `/plugin install <plugin> --marketplace <source>`: adds the marketplace at `<source>` when not added yet, asking you to confirm first, then opens the plugin's details. A source matching an added marketplace skips the confirmation. In a session the source can't contain spaces. Requires Claude Code v2.1.275 or later.
- `/plugin directory`: opens the Discover tab filtered to the Anthropic Directory (platform-support page: "Claude Code v2.1.287 and later"; not in the CLI reference table). Verified on 2.1.319: Discover showed `Discover plugins (1/3603)`, the Anthropic Directory count, where `/plugin` shows all marketplaces (`1/3699`).
- `/plugin manage`: opens the Installed tab.
- `/plugin stats`: opens the Stats tab in sessions where `/skill-doctor` is available; anywhere else, the Discover tab. Verified on 2.1.319: Stats showed `Skills loaded this session` with `context`, `7d tokens`, `uses` and `last used` columns.
- `/plugin enable <plugin>`: opens the Installed tab at the plugin and enables it.
- `/plugin disable <plugin>`: opens the Installed tab at the plugin and disables it.
- `/plugin uninstall <plugin>`: opens the Installed tab at the plugin and uninstalls it. For a plugin the repository's `.claude/settings.json` enables, it asks: `y` disables it for you (writes `false` in `.claude/settings.local.json`), `u` uninstalls it for everyone (removes it from `.claude/settings.json`).
- `/plugin configure <plugin>` (alias `config`): opens the plugin's `userConfig` dialog, or reports that it declares none.
- `/plugin validate <path>`: prints the same report as `claude plugin validate`, inline (verified on 2.1.319, including the Plugin directory checks block).
- `/plugin tag [path] [--push] [--dry-run] [--force]`: creates the release tag as `claude plugin tag` does; accepts `--push`, `--dry-run` and `--force` or `-f`. Any other flag or an extra argument prints usage. Verified on 2.1.319: ``✘ Unexpected argument "--bogus". Usage: /plugin tag [path] [--push] [--dry-run] [-f|--force] Create a {name}--v{version} git tag for the plugin at <path> (default: .). Validates plugin.json and any enclosing marketplace entry agree on the version. For -m/--message and --remote, use the CLI: claude plugin tag --help``. Outside a git repository: `<path> is not inside a git repository. Dependency tags are resolved via git ls-remote, so the plugin must live in a git repo.`
- `/plugin marketplace` (alias `market`): does nothing visible (verified: `(no content)`). Pass `add`, `list`, `update` or `remove`.
- `/plugin marketplace add [source]` (alias `market add`): with a source, adds it and reports the result. Without one, opens the Add Marketplace input (verified: `Enter marketplace source:` with examples `owner/repo (GitHub)`, `git@github.com:owner/repo.git (SSH)`, `https://example.com/marketplace.json`).
- `/plugin marketplace list` (alias `market list`): prints marketplace names inline. Verified on 2.1.319: `Configured marketplaces: • claude-plugins-official • anthropic-plugin-directory`.
- `/plugin marketplace update [name]` (alias `market update`): opens the Marketplaces tab; with a name, refreshes that marketplace there.
- `/plugin marketplace remove [name]` (aliases `market remove`, `market rm`, `marketplace rm`): opens the Marketplaces tab; with a name, removes that marketplace there. The tab names the plugins it will uninstall before asking to confirm.

## What the panel shows

Official page: <https://code.claude.com/docs/en/plugins/install#manage-installed-plugins>

- Tabs (verified on 2.1.319 and 2.1.321): Discover, Installed, Marketplaces, Errors, Stats.
- Discover: plugins from your marketplaces, filterable by marketplace with ctrl+s; type to search, Space to toggle, Enter to view, Esc to go back.
- A plugin's details can show Will install (commands, agents, skills, hooks, MCP and LSP servers), Last updated and Context cost (Every turn, When invoked) for Anthropic's official marketplace, or `Components will be discovered at installation` for a local or custom marketplace. The Context cost estimates appear only when you open the plugin by naming its marketplace (`/plugin install <plugin>@<marketplace>`) or from the Marketplaces tab, not from the Discover list.
- Install summary, last sentence: `Plugin is now active.`; `Plugin is now active.` followed by `Its bundled MCP server needs configuration before it can start`; `Run /reload-plugins to apply.`; or `The plugin couldn't be loaded` (reason on the Errors tab).
- Installed: type to filter, Space to enable or disable, `f` to favorite, Enter for details. Details menu: Disable plugin or Enable plugin, Update now, Uninstall, plus Configure options (manifest `userConfig`) and Configure (bundled MCP server's `user_config`). Disabled plugins are grouped under a collapsed header; unused ones under Not used recently, with a Last used line. Managed-scope plugins can't be enabled, disabled or uninstalled there. `· data preserved` marks an uninstall that kept the data directory.
- Marketplaces: browse a marketplace, Update marketplace (refreshes the listing, updates its installed plugins except command-source and `headersHelper` plugins, and reports each plugin it left for you to update yourself), Enable auto-update or Disable auto-update, remove.
- Auto-update is on by default for `claude-plugins-official` and the other official marketplace names except `knowledge-work-plugins` and `first-party-plugins`, and for marketplaces added from claude.ai; off for every other marketplace.
- `DISABLE_UPDATES=1`, `DISABLE_AUTOUPDATER=1` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` turns the whole auto-update pass off and hides the Enable auto-update toggle, unless `FORCE_AUTOUPDATE_PLUGINS=1` is also set (loading reference, When auto-update runs).
- Fixed in changelog 2.1.321: plugin auto-updates and `/plugin` marketplace updates downloading a plugin again for each worktree or folder of a repository.

## Messages

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#plugin-in-a-session>

- A plugin named in `/plugin enable`, `disable`, `uninstall` or `configure` that isn't installed in the current project: `Plugin "<plugin>" is not installed in this project` (verified on 2.1.319).
- A synced change arriving in an interactive session: `Plugins changed. Run /reload-plugins to activate.`
- After an auto-update: `Plugin updated: <name> · Run /reload-plugins to apply`.

## `/reload-plugins`

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#reload-plugins>

`/reload-plugins [--force]`. Applies pending plugin changes (plugins installed, updated, enabled, disabled or edited on disk since the session started) without restarting.

- `--force`: apply the reload even when it would invalidate the prompt cache. `force` without dashes works too (verified on 2.1.319).
- Closing the `/plugin` panel with pending changes made in it runs `/reload-plugins` for you. Run it yourself after changes made outside the panel, such as a `claude plugin` command in another terminal.

Summary line:
- `Reloaded: N plugins · N skills · N agents · N hooks · N plugin MCP servers · N plugin LSP servers`. Verified on 2.1.319: `Reloaded: 19 plugins · 62 skills · 22 agents · 9 hooks · 5 plugin MCP servers · 4 plugin LSP servers`.
- The plugin MCP server count is omitted in a session without an interactive terminal.
- Any plugin failed: the summary adds `N errors during load. Run /plugin for details.`
- The skills count covers every skill a plugin provides, `commands/` entries and `SKILL.md` skills. The agents count is every agent loaded in the session, including non-plugin ones.
- Missing dependencies of a reloaded plugin: Claude Code installs them, reloads again and appends `(+ N dependencies: <names>) resolved`.

Reloads that change MCP tools:
- When the reload would add or remove a plugin MCP server or the `LSP` tool, and that would invalidate the prompt cache, Claude Code doesn't apply it and prints a line such as `This reload changes MCP tools (<server>) — your next message will re-read the whole conversation instead of using the cache. Run /reload-plugins --force to apply.`
- `--force` applies it anyway, at the cost of one uncached request.

Sessions without an interactive terminal (desktop app, Agent SDK, `-p`):
- `/reload-plugins` runs there too. Requires Claude Code v2.1.260 or later.
- It runs only when typed into the session yourself (the `-p` prompt, the desktop app's prompt box). Arriving another way, such as through Remote Control or a message relayed from Slack: `/reload-plugins isn't available over a remote connection in this session.`, nothing reloaded.
- The reload there doesn't connect or disconnect plugin MCP servers; those changes take effect in the next session.
- Headless sessions reload mods in `.claude/skills` when their files change; `CLAUDE_CODE_PLUGIN_DIR_WATCH=0` turns this off (changelog 2.1.321).

Fixed in changelog 2.1.299: `/reload-plugins` not loading a plugin installed from another terminal a moment earlier.
