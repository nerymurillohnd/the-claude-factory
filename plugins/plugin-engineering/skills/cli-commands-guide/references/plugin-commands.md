# `claude plugin` commands

Every `claude plugin <subcommand>` you run from a shell or a script, outside a Claude Code session. Facts come from the CLI reference page (`https://code.claude.com/docs/en/plugins/cli-reference.md`), the `--help` of Claude Code 2.1.319, and the Claude Code changelog through 2.1.319. A line marked "(binary 2.1.319)" or "(changelog X)" is newer than the docs page or absent from it.

## Contents

- Shared rules: exit codes, plugin arguments, scopes, aliases
- JSON result format (`--json` on install, uninstall, update, enable, disable)
- plugin init
- plugin install
- plugin uninstall
- plugin enable
- plugin disable
- plugin update
- plugin list
- plugin details
- plugin configure
- plugin prune
- plugin eval
- plugin eval init
- plugin tag
- plugin test
- plugin validate
- Synced plugins (`@synced`)

## Shared rules

- `claude plugins` is an alias for `claude plugin`.
- Exit codes: `0` on success and `1` on failure. `validate` adds `2` for an unexpected error. `eval` adds its own codes (see plugin eval).
- Plugin arguments: a `<plugin>` is a plugin `name` or `name@marketplace`. When two marketplaces offer the same name, use the qualified form. `configure` takes only the qualified form.
- Scopes: `--scope` takes `user`, `project` or `local` and names the settings file the command writes to. `update` also takes `managed`.
  - `user`: `enabledPlugins` in `~/.claude/settings.json`, every project on the machine.
  - `project`: `.claude/settings.json`, committed, for everyone in the repository. Committing it enables the plugin for collaborators but does not download it: each one still runs `claude plugin install <name>@<marketplace> --scope project`.
  - `local`: `.claude/settings.local.json`, this repository, you only.
  - When the same plugin is set at several scopes, local overrides project, and project overrides user.
- Aliases (all verified on binary 2.1.319): `init` = `new`; `install` = `i`; `uninstall` = `remove` = `rm` (`rm` is accepted but not shown in `--help`); `prune` = `autoremove`.
- Usage errors, such as an invalid `--scope`, print no JSON result line and exit `1` with the reason on stderr.
- Run `claude plugin --help` for the subcommands your version has, and `claude plugin <subcommand> --help` for a subcommand's full option list. The docs tables list only commonly used options.

## JSON result format

Applies to `--json` on `install`, `uninstall`, `update`, `enable` and `disable`.

- The last line of stdout is one JSON object. Parse only that line: Claude Code prints any command the marketplace declares ahead of it.
- Always present: `command` (the subcommand that ran, such as `install`), `outcome` (`ok` or `failed`), `message` (human-readable).
- Present only when they apply: `pluginId`, `scope`, `failureCode`, and the subcommand's own fields (for example `keptData`, `savedKept`, `alreadyInGoalState`, `shownCommand`).
- Same exit codes as without `--json`.
- A marketplace-declared command is still shown and must be confirmed: pass `-y` when not interactive (binary 2.1.319 help).

### Accept a displayed install command (`shownCommand`)

- When a `--json` run displays a marketplace-declared command (a command-source install, or the `headersHelper` that fetches the archive) and doesn't run it, the `failed` result carries a `shownCommand` object: the command as displayed, the plugin it belongs to, and its `sha256`.
- Re-run with `--accept-command <sha256>` from your own terminal. Requires Claude Code v2.1.271 or later.
- The `sha256` counts as acceptance for exactly that command, that plugin and that marketplace catalog. If any of them changed, including a change the run's own marketplace refresh fetches, Claude Code refuses the `sha256` and shows the command again, to be shown to a person again.
- `shownCommand.acceptCommandMatched: false` means the `sha256` you passed doesn't match the command now displayed. Review that command before re-running with its `sha256`.

## plugin init

`claude plugin init <name> [options]` (alias `new`). Scaffolds a new plugin at `~/.claude/skills/<name>/`. Unless an administrator blocked skills-directory plugins, it loads in the next session as `<name>@skills-dir` with no install step.

- `<name>` becomes the directory name under `~/.claude/skills/` and the manifest's `name`.
- No flag chooses another location. To scaffold inside a project, follow `https://code.claude.com/docs/en/plugins/create.md`.

Flags:
- `--description <text>`: manifest description.
- `--author <name>`: author name. Default: `git config user.name`.
- `--author-email <email>`: author email. Default: `git config user.email`.
- `--with <components...>`: also scaffold starter files for `skills`, `agents`, `hooks`, `mcp`, `lsp`, `output-style` or `channel`.
- `-f, --force`: overwrite an existing `.claude-plugin/` at the target.

Output: Claude Code validates what it wrote and prints `Created plugin "my-helper" at ~/.claude/skills/my-helper`, followed by the id it loads as and the `claude plugin disable` command that turns it off.

Exits `1` without writing when it can't scaffold safely, naming the reason. Common reasons:
- An unknown `--with` value.
- An existing scaffold at the target without `--force`.
- A managed marketplace allowlist without the `skills-dir` source, or a blocklist that names it: `Plugins from ~/.claude/skills/ are blocked by your organization's managed settings`.

Example: `claude plugin init my-helper --with skills hooks`

## plugin install

`claude plugin install <plugin> [options]` (alias `i`). Installs a plugin from one of your marketplaces.

Flags:
- `-s, --scope <scope>`: `user`, `project` or `local`. Default `user`.
- `--config <key=value>`: set a `userConfig` option the plugin's manifest declares. Repeat for each option. A key written `<server>.<key>` sets a setting that a bundled `.mcpb` MCP server declares in its own `user_config`; a bare key works when only one bundled server declares it (binary 2.1.319). The `<server>.<key>` form requires Claude Code v2.1.285 or later. Values are validated against the schema and stored as the interactive `/plugin` configure flow stores them.
- `-y, --yes`: accept the displayed marketplace-declared command (a plugin installed by running a command, or one whose archive is fetched through a `headersHelper` command) without the `Run this command now?` prompt. Required when stdin or stdout is not a TTY. Ignored when the command runs inside a Claude Code session, such as from the Bash tool or a hook. Requires Claude Code v2.1.229 or later.
- `--accept-command <sha256>`: accept the displayed command whose `sha256` a previous `--json` run reported in `shownCommand`, in place of `-y`. Can't be combined with `-y`. Has no effect inside a Claude Code session. Requires Claude Code v2.1.271 or later.
- `--json`: print the result as one JSON object on the last line of stdout instead of the human message. Requires Claude Code v2.1.268 or later.
- `--marketplace <source>`: install `<plugin>`, given by its bare name, from the marketplace at `<source>` (`owner/repo`, a git or https URL, or a path), adding the marketplace first if not added yet. A new marketplace is added under the same organization policy checks as `claude plugin marketplace add` and is declared in user settings even when you pass `--scope project`. Requires Claude Code v2.1.292 or later.
- `--registry <url>`: for a `<package>@npm` install, resolve and download from this npm registry instead of the one your npm configuration selects (binary 2.1.319; not on the docs page).

Prompts and TTY:
- Most plugins install without a prompt. A plugin whose marketplace entry runs a command to install it, or sets a `headersHelper` for its download, first prints the command and asks `Run this command now? [y/N]`.
- stdin or stdout isn't a TTY, and you pass neither `-y` nor `--accept-command`: the install is refused, the output says the command was only displayed, exit `1`.
- Claude runs the command through its Bash tool: `-y` is ignored. The user runs it from their own terminal.

Output:
- Success: `Successfully installed plugin: formatter@my-marketplace (scope: project)`.
- With `--marketplace` and a marketplace not added yet, first: `Successfully added marketplace: <name> (declared in user settings)`.
- Already installed at that scope: `Plugin "formatter@my-marketplace" is already installed (scope: project)`, exit `0`.
- You decline a command-source prompt: `Aborted.`, exit `1`.
- You decline a `headersHelper` prompt, or it can't be confirmed without a TTY: `Aborted — the command was not run.`, exit `1`.

When it loads: the next time Claude Code starts, or after `/reload-plugins` in a running session.

On a new machine where no interactive session has run yet, the official marketplace isn't registered: a script runs `claude plugin marketplace add anthropics/claude-plugins-official` before installing from it.

Examples:
- `claude plugin install formatter@my-marketplace --scope project`
- `claude plugin install deploy-helper --marketplace your-org/plugins`

## plugin uninstall

`claude plugin uninstall <plugin> [options]` (aliases `remove`, `rm`). Removes an installed plugin from one scope.

Flags:
- `-s, --scope <scope>`: `user`, `project` or `local`. Default `user`.
- `--keep-data`: preserve the plugin's persistent data directory, `~/.claude/plugins/data/<id>/`.
- `--prune`: also remove auto-installed dependencies that no remaining plugin needs.
- `-y, --yes`: skip the `--prune` confirmation prompt. Required with `--prune` when stdin or stdout isn't a TTY.
- `--json`: JSON result line. Can't be combined with `--prune`. Requires Claude Code v2.1.268 or later.

Output:
- Success: `Successfully uninstalled plugin: formatter (scope: project)`.
- Not installed at that scope: a line that starts `Failed to uninstall plugin "formatter@my-marketplace":`, exit `1`.
- The failure line continues with `"formatter" was not uninstalled:` and names a settings file: Claude Code couldn't confirm that the scope's settings no longer switch the plugin on, so the plugin stays installed with everything it saved. With `--json`, `failureCode: "settings_still_on"`. Requires Claude Code v2.1.282 or later.

What an uninstall from the last installed scope deletes: the plugin's stored options and secrets, and its data directory `~/.claude/plugins/data/<id>/`. Exceptions:
- With `--keep-data`, the data directory stays.
- When another installed plugin uses the same folder, such as one whose ID differs only in letter case, the data directory stays.
- When Claude Code can't read the list of installed plugins back after removing the plugin from that scope, the options, secrets and data directory all stay, because the plugin may still be installed at another scope. The uninstall still succeeds; the message lists what stayed and how to delete it. With `--json`: `savedKept: "install_records_unreadable"`.

JSON fields: `keptData` reports whether the directory stayed (for a directory that stays without `--keep-data`, requires v2.1.281 or later). `savedKept` requires v2.1.282 or later. `/plugin` shows `· data preserved` when the directory stayed.

Auto-installed dependencies stay after an uninstall until `claude plugin prune` (or `--prune`).

## plugin enable

`claude plugin enable <plugin> [options]`. Enables a disabled plugin. For a plugin synced from claude.ai, pass `<name>@synced`.

Flags:
- `-s, --scope <scope>`: `user`, `project` or `local`. Auto-detected when omitted.
- `--json`: JSON result line. Requires Claude Code v2.1.268 or later.

Scope rules:
- Without `--scope`, it checks settings files in the order local, project, user, and uses the first scope that mentions the plugin.
- `--scope` where the plugin isn't declared, at a scope that takes precedence over the declaring one: Claude Code writes an override at that scope.
- Any other undeclared scope: fails with `Plugin "formatter" is installed at project scope, not user. Use --scope project or omit --scope to auto-detect.`

Output:
- Success: `Successfully enabled plugin: formatter (scope: project)`, naming the detected scope.
- Already enabled at the resolved scope: `Plugin "formatter" is already enabled`, exit `1`. With `--json`: `"failureCode": "already_in_goal_state"` and `"alreadyInGoalState": true`, so a script can treat it as success.

Dependencies: Claude Code enables declared dependencies too. Enable fails when:
- A dependency is not installed: it prints the `claude plugin install` command for each missing dependency.
- A dependency is blocked by your organization's plugin policy: it names the blocked dependency.
- A dependency is set to `false` at a scope with higher precedence than the target scope: enable the dependency at that scope, or pass `--scope` to write there.

A plugin whose manifest sets `defaultEnabled` to off installs but stays off until enabled with this command or from the Installed tab of `/plugin`.

## plugin disable

`claude plugin disable [plugin] [options]`. Disables a plugin without uninstalling it. For a synced plugin, pass `<name>@synced`.

Flags:
- `-a, --all`: disable every enabled plugin. Can't be combined with a plugin name or `--scope`.
- `-s, --scope <scope>`: `user`, `project` or `local`. Auto-detected when omitted, in the same local, project, user order as `enable`.
- `--json`: JSON result line. Requires Claude Code v2.1.268 or later.

Output:
- Success: `Successfully disabled plugin: formatter (scope: project)`.
- Neither a name nor `--all`: `Please specify a plugin name or use --all to disable all plugins`, exit `1`.
- Already disabled: `Plugin "formatter" is already disabled`, exit `1`.
- `--scope local` on a project-enabled plugin writes an override that turns it off for you alone: `claude plugin disable formatter --scope local`.

Fails for a plugin still required:
- Another enabled plugin depends on it: the command names the dependents to disable first (and prints a chained command that disables both in the right order).
- Your organization requires it as a synced plugin: fails and saves nothing, with `Plugin "<name>@synced" is required by your organization and can't be disabled here. Contact your admin to change it.`

Disabling a synced plugin (`<name>@synced`), here or on the Installed tab, saves `"<name>@synced": false` in your user-level `enabledPlugins`. See Synced plugins below.

## plugin update

`claude plugin update <plugin> [options]`. Updates a plugin to the latest version its marketplace offers. The new version loads in the next session, or after `/reload-plugins` in a running one. (The binary's help line says "restart required to apply"; the docs page and the install guide state `/reload-plugins` applies it in a running session.)

Flags:
- `-s, --scope <scope>`: `user`, `project`, `local` or `managed`. Auto-detected when omitted.
- `-y, --yes`: accept a changed install command from a command-source plugin, or the `headersHelper` command that fetches its archive, without the prompt. Required when stdin or stdout isn't a TTY, unless you pass `--accept-command`. Requires Claude Code v2.1.229 or later.
- `--accept-command <sha256>`: accept the marketplace-declared command whose `sha256` a previous `--json` run reported in `shownCommand`, in place of `-y`. Can't be combined with `-y`. Requires Claude Code v2.1.271 or later.
- `--json`: JSON result line. Requires Claude Code v2.1.268 or later.

Which scope it updates:
- Without `--scope`, the most specific scope the plugin is installed at for the current project, checking local, project, user, then managed.
- Before v2.1.281, it used `user` when `--scope` was omitted, so updating a plugin installed only at project or local scope failed with `Plugin "<name>" is not installed at scope user`. On those versions, pass `--scope`.
- `managed` is the one scope you can update but not install to.

Bare name: matched against installed plugins. When installed plugins from different marketplaces share the name, the command refuses and lists the qualified `plugin-name@marketplace-name` commands to run instead. Requires Claude Code v2.1.246 or later.

Output:
- `Checking for updates for plugin "formatter@my-marketplace"…`, then the result.
- Nothing newer: `formatter is already at the latest version (1.0.0).`, exit `0`, unless it retries the plugin's dependency install and that install fails.
- Dependency retry: when the plugin is already at its latest version, the command can retry an unfinished dependency install in its cached copy. If the retry fails: `Failed to update plugin "formatter@my-marketplace"` with the reason, exit `1`. Before v2.1.287, it reported the plugin at its latest version without retrying.
- A plugin loaded from a directory: prints just its reason, without the `Failed to update plugin` prefix (changelog 2.1.290).
- Since 2.1.319, `update` installs dependencies added by the new plugin version (changelog 2.1.319).

There is no command that updates every plugin at once. `claude plugin marketplace update` with no name refreshes every marketplace's listing but leaves installed plugins at their current versions. To update all plugins from one marketplace, use the Marketplaces tab of `/plugin` → Update marketplace (it skips command-source and `headersHelper` plugins, which are updated one by one).

## plugin list

`claude plugin list [options]`. Lists installed plugins with version, scope and status.

Flags:
- `--json`: print the list as JSON.
- `--available`: also list plugins your marketplaces offer that you haven't installed. Has no effect without `--json` (binary help: "requires --json").
- `--data-size [plugin]`: measure each installed plugin's saved data directory, or only the named plugin's, given as `name@marketplace`. Has no effect without `--json`. If the name has no install record: `--data-size names a plugin that is not installed`, exit `1`, no list. Requires Claude Code v2.1.285 or later.

Human-readable groups:
- `Installed plugins:`: installed from a marketplace.
- `Session-only plugins (--plugin-dir / --plugin-url):`: loaded by those flags in the same command, as in `claude --plugin-dir ./my-plugin plugin list`.
- `Skills-directory plugins (.claude/skills/*):`: found in a skills directory.
- `Synced from claude.ai`: synced from your claude.ai account. A plugin your organization requires is marked `required by your org`.
- Nothing in any group: ``No plugins installed. Use `claude plugin install` to install a plugin.``

`--json`: an array, one object per installation. Always present: `id`, `version`, `scope`, `enabled`, `installPath`. The others only when they apply:
- `id` (string): `name@marketplace` for installs, `name@inline` for session-only plugins, `name@skills-dir` for skills-directory plugins, `name@synced` for synced plugins.
- `version` (string): for a marketplace install, the version Claude Code computed at install. For a session-only, skills-directory or synced plugin, the manifest's `version`, or `unknown` when it declares none.
- `scope` (string): `user`, `project`, `local` or `managed` for installs; `user` or `project` for skills-directory plugins; `session` for session-only plugins; `synced` for synced plugins.
- `enabled` (boolean): enabled in your merged settings.
- `installPath` (string): directory the plugin loads from, except for a plugin that sessions load in place from its marketplace's folder.
- `readFromFolder` (string): for a plugin loaded in place from its marketplace's folder, its source directory inside that folder. Requires v2.1.289 or later.
- `folderVersion` (string): with `readFromFolder`, the plugin's `version` as loaded from that folder, which can differ from `version`. Absent when the plugin didn't load or declares no version. Requires v2.1.289 or later.
- `installedAt` (string): ISO timestamp of the install. Marketplace installs only.
- `lastUpdated` (string): ISO timestamp of the last update. Marketplace installs only.
- `projectPath` (string): project the install belongs to. `project` and `local` scope only.
- `mcpServers` (object): the plugin's MCP server definitions, for a marketplace-installed plugin that has any.
- `errors` (array of strings): load errors, when the plugin failed to load.
- `notes` (array of strings): warnings that aren't load errors, such as authoring issues or packages that aren't installed.
- `errorDetails` (array of objects): one per `errors` entry, giving its diagnostic `type` and the names it refers to (plugin, marketplace, server, file). Requires v2.1.268 or later.
- `noteDetails` (array of objects): the same detail objects for each `notes` entry. Requires v2.1.268 or later.
- `hasUserConfig` (boolean): present and `true` when the plugin loaded and its manifest declares `userConfig` options. Absent for a plugin that failed to load. Saved values are never included. Requires v2.1.285 or later.
- `projectEnabled` (boolean): whether the project's shared `.claude/settings.json` turns the plugin on. Marketplace installs only. Requires v2.1.285 or later.
- `dataDirSize` (object): with `--data-size`, the saved data directory's size as `bytes` and `human`; absent when the directory is missing or empty. Marketplace installs only. Requires v2.1.285 or later.
- `dataDirUnreadable` (boolean): with `--data-size`, `true` when the directory exists but couldn't be measured. Marketplace installs only. Requires v2.1.285 or later.

`--json --available`: one object instead of an array. `installed` holds the array above; `available` holds one object per uninstalled marketplace plugin:
- `pluginId` (string): `name@marketplace`.
- `name` (string): the plugin's name in the marketplace.
- `marketplaceName` (string): the marketplace that offers it.
- `source` (string or object): the entry's source; a string for a relative path, an object otherwise.
- `description` (string): when the entry has one.
- `version` (string): when the entry declares one.
- `installCount` (number): when Claude Code has one.

Built-in plugins (`@builtin`) never appear in `claude plugin list`; they show on the Installed tab of `/plugin`.

## plugin details

`claude plugin details <name>`. Shows a plugin's component inventory and projected token cost. No flags beyond `--help`, and no `--json`.

- The plugin must be loaded: installed, found in a skills directory, or passed with `--plugin-dir` or `--plugin-url` before the subcommand in the same command, as in `claude --plugin-dir ./my-plugin plugin details my-plugin`. After the subcommand the flag fails with `error: unknown option '--plugin-dir'`, exit `1` (verified on 2.1.319). `<name>` is a `name` or `name@marketplace`.
- Output: name, version, description and source, then:
  - `Component inventory`: skills, agents, hooks, MCP servers and LSP servers.
  - `Projected token cost`: the always-on tokens the plugin adds to every session (the `Always-on` line).
  - `Per-component (rounded)`: always-on and on-invoke estimates per skill, agent and command, in one table with no type column, rounded as in `~240` and `~7.1k`. Omitted when the plugin has none.
- Not loaded, exit `1`: ``Plugin "formatter" not found. Run `claude plugin list` to see installed plugins, or pass --plugin-dir <path> to load one from disk.``
- An ID ending in `@builtin` that isn't found: ``Plugin "<name>@builtin" not found. Built-in plugins don't appear in `claude plugin list`. To see the ones available in a session, run /plugin in Claude Code and open the Installed tab.`` (changelog 2.1.302).

## plugin configure

`claude plugin configure <plugin> [options]`. Shows an installed plugin's `userConfig` options and which are set, or saves values piped on stdin. Requires Claude Code v2.1.285 or later.

- Takes only the full `name@marketplace` id, as `claude plugin list` shows it. A bare `name` is not accepted. No loaded plugin with that id: `No installed plugin has the id "<plugin>".`, exit `1`.

Flags:
- `--values-stdin`: read option values from stdin as a JSON object of single-line strings and save them. Options left out keep their saved values.
- `--json`: one JSON object on stdout. Without `--values-stdin`: the options' `schema` and `choices`, their starting `inputs`, and the `configured` and `unconfigured` option names. With `--values-stdin`: the `saved` option names and, when they could be read back, the `unconfigured` ones.

Output:
- Without flags: each option with up to three labels: `required` or `optional`, then `sensitive` when the manifest declares it sensitive, then `set` or `not set`. No saved values printed.
- With `--json`: includes saved values of non-sensitive options, never the text of a sensitive one.
- Save success: `Configuration saved. Restart Claude Code to apply it.`
- A key the manifest doesn't declare, or a value that fails validation: saves nothing, prints `Failed to save configuration:` with the reason, exit `1`. With `--json`, a refused value also prints an object whose `refused` field carries the `message` and, when one option is at fault, its `option` key.

Example: `claude plugin configure formatter@my-marketplace --values-stdin < values.json` with `values.json` containing `{"api_url": "https://example.com"}`.

A bundled MCP server's own settings are set with `claude plugin install --config <server>.<key>=<value>` or the Configure item in `/plugin`.

## plugin prune

`claude plugin prune [options]` (alias `autoremove`). Removes auto-installed dependencies that no installed plugin needs anymore. Never removes a plugin you installed yourself.

Flags:
- `-s, --scope <scope>`: `user`, `project` or `local`. Default `user`.
- `--dry-run`: list what would be removed without removing it.
- `-y, --yes`: skip the confirmation prompt. Required when stdin or stdout isn't a TTY.

Behavior:
- `--dry-run`: lists the orphaned dependencies and ends with `(dry run — nothing removed)`. None to remove: a line that starts `Nothing to prune`.
- Interactive terminal, no `-y`: lists them and asks `Remove? [y/N]`.
- Any terminal, `-y`: removes them and prints `Removed N auto-installed plugins: <names>`.
- Non-TTY stdin or stdout, no `-y`: prints the list and ``Not a TTY — run `claude plugin prune -y` to remove.``, removing nothing.
- Exit `0` whatever you answer at the prompt.

## plugin eval

`claude plugin eval [target] [options]`. Runs a plugin's eval cases and reports scored results. Requires Claude Code v2.1.269 or later. Case format, graders, results and CI usage: `https://code.claude.com/docs/en/plugin-evals.md`.

- Each case is a prompt plus graders, run several times in an isolated session with only the target plugin loaded, and by default also without the plugin (the baseline arm).
- Cases: `<eval dir>/**/case.yaml`, or `prompt.md` + `graders/*.md`.
- It runs the plugin and its suite on your machine, as you. Only evaluate plugins you trust: sandboxing is not a guarantee, and a bundled suite passing is not a security vetting. The first run in an untrusted plugin directory asks you to confirm.

Target (optional, defaults to the current directory):
- A plugin directory.
- A single `prompt.md` or `case.yaml` file.
- An installed plugin as `name` or `name@marketplace`.
- `name@skills-dir`.

Put the target before `--tag`, `--allow-tools` and `--json`. Each of these takes the words that follow it as its value, so a target written after one of them is read as a tag, a tool name or the JSON output path.

Options (full set on binary 2.1.319):
- `--runs <n>`: runs per case in each arm. Default: each case's `runs`, else `3`.
- `-j, --concurrency <n>`: agent runs at once, `1` to `8`. Default `1`. Each run is a full claude child on your credential; they share one rate limit.
- `--model <model>`: model for the agent under test. Default: each case's `model`, else `ANTHROPIC_MODEL` if set, else Claude Code's default.
- `--judge-model <model>`: model for `llm` and `baseline` graders. Docs: the model for background tasks; binary 2.1.319 help: `haiku`.
- `--ablation <mode>`: `none` or `with-without`. Binary 2.1.319: default `with-without` whenever a plugin resolves (by name or from the target path), `none` when nothing does; under `with-without`, graders marked with-only, including `tool_used: Skill`, are a plugin-fired indicator rather than part of the score. Docs: decided per case.
- `--threshold <0..1>`: exit `1` if any case scores below this. Default `1.0`.
- `--max-cost-usd <usd>`: stop before the next run once spend reaches this, exit `2`, report partial results. Checked before each run launches, so overrun is bounded to runs in flight; when a run breaches, paid graders (`llm`/`baseline`) are skipped while free graders still score it. Default: no limit.
- `--allow-tools <tools...>`: grant gated tools beyond the read-only set, such as `Bash`, `Write`, `Edit`, `WebFetch` or `"mcp__plugin_<plugin>_<server>__*"`. Supports `Tool(pattern:*)` syntax.
- `--disallow-tools <tools...>`: built-in tools kept from Claude in every case even if granted, such as `Agent` or `TaskStop` (changelog 2.1.299; also a `disallowed_tools` case field).
- `--case <glob>`: filter cases by name glob.
- `--tag <tag...>`: filter cases by tag (repeatable).
- `--scaffold`: run each case's `scaffold_script` (author-supplied bash, as you). Default off.
- `--no-scaffold`: explicitly skip `scaffold_script` (binary 2.1.319).
- `--trust-plugin`: assert you trust the plugin's code and suite and skip the first-run trust prompt, for CI. Does not imply `--scaffold`, `--allow-tools` or `--mocks off`.
- `--mocks <mode>`: `record` or `off`, stand-ins from `<eval dir>/mocks/`. Default `record`. `record`: a plugin server with no mock is not started. `off`: no stand-ins, every real server starts, as you, outside the OS sandbox, its tools gated by `--allow-tools`.
- `--allow-real-servers`: with `--mocks record`, also start the plugin's real MCP server processes for servers with no mock (as you, outside the OS sandbox).
- `--eval-dir <dir>`: directory below the plugin that holds the cases. Default: the manifest's `experimental.evals`, else `evals`. Results go to `<plugin>/<dir>/results/`; for an installed-plugin target, `./<dir>/results/` with this flag, else `./evals/results/`.
- `--output-dir <dir>`: directory for `aggregate-result.json`. Default `./<eval dir>/results/<timestamp>/`.
- `--json [path]`: print the result document (prompts, graders, per-run scores) to stdout, or write it to a `.json` path.
- `--report <path>`: write the self-contained HTML report to `<path>` instead of the results dir.
- `--no-publish`: keep the HTML report local; skip publishing it to claude.ai.
- `--publish-report`: also require publishing the report to claude.ai (already the default when your account supports it); explains why if unavailable (binary 2.1.319).
- `--keep-temp`: preserve scaffold dirs for debugging.
- `--verbose`: log per-message trace events to the debug log (read them with `--debug-file`).

Exit codes:
- `0`: the suite passed: every case meets the threshold and nothing else failed the run.
- `1`: a failing case, a load error, an untrusted plugin directory, a run that ended on an API error (such a run scores 0 without grading since changelog 2.1.299), or another cause listed under Run evals in CI in the evals docs.
- `2`: a partial run.
- `130`: interrupted.
- `143`: terminated.

## plugin eval init

`claude plugin eval init [name] [options]`. Creates an eval suite for the plugin in the current directory. Requires Claude Code v2.1.269 or later.

- Run it from the plugin's root folder, the one that holds `.claude-plugin/plugin.json` or the skill's `SKILL.md`. To scaffold elsewhere on purpose, pass `--eval-dir`.
- In a terminal: opens an interactive session for an authoring interview. Claude reads the plugin, asks what it should do well, proposes cases and graders, writes the case files, then runs the cases and reviews the grades with you.
- With `--bare`, or without a terminal: writes a blank single-case template instead.
- Run by Claude from inside a Claude Code session: prints the interview instructions for that session to follow rather than writing a template.
- `name` is a case name, required with `--bare` or without a terminal. It starts with a letter or digit and contains only letters, digits, `.`, `_` and `-`. Names Windows can't store, such as `con` or a name ending in `.`, are refused on every platform.

Options:
- `--bare`: write a blank `prompt.md` and `graders/criteria.md` for `<name>` instead of the interview.
- `-i, --interactive`: require the interview (already the default in a terminal); fails without a terminal instead of writing a template.
- `--eval-dir <dir>`: directory below the current directory to write cases into. Default: `experimental.evals` from the `plugin.json` in the current directory, else `evals`.

## plugin tag

`claude plugin tag [path] [options]`. Creates an annotated git tag named `<name>--v<version>` for a plugin release. Before tagging, it checks that the plugin's `plugin.json` and any marketplace entry that lists it agree on the version.

- `[path]`: the plugin directory, default the current directory. The marketplace entry is found by walking up from that directory to a `.claude-plugin/marketplace.json` that lists the plugin.

Flags:
- `--push`: push the tag to `--remote` after creating it.
- `--dry-run`: print what would be tagged without creating the tag.
- `-f, --force`: skip the dirty-working-tree and tag-already-exists checks.
- `-m, --message <msg>`: tag annotation message; `%s` stands for the version. Default `<name> <version>`.
- `--remote <name>`: remote for `--push`. Default `origin`.

Output:
- `--dry-run` prints the plan: the plugin name, the version and which file it came from, the matching marketplace entry when there is one, the tag name, and the `git tag` and `git push` commands it would run.
- Otherwise: `Created tag formatter--v1.0.0`, then either `Pushed to origin` or the push command to run yourself. If the push fails, the tag stays created locally and the command exits with an error.
- Exits `1` with the reason when it can't tag safely. Common reasons: no `version` in `plugin.json` or the marketplace entry; the tag already exists; the working tree is dirty.

Example: `claude plugin tag plugins/formatter --dry-run`

## plugin test

`claude plugin test [dir]`. Runs the tests of a mod (a plugin whose code registers event handlers). Needs no session, sign-in or network.

- `[dir]`: the mod's folder, default the current folder.
- Runs every `*.test.ts` and `*.test.tsx` under it, each file in a child of the Claude Code binary, in an environment like the one the mod's hooks run in. A test file imports its kit from `'claude-code/testing'`.
- Exits `1` when a test fails.
- Behavior changes in changelog 2.1.299: a served `$` method that hasn't answered within ten seconds fails the call, as in a session; each mod's Box or Text root in `ui.render` trees carries `part: { plugin }`, so exact-tree assertions must include it.

Example: `claude plugin test ./first-mod`

## plugin validate

`claude plugin validate <path> [options]`. Validates a plugin manifest, a marketplace manifest, or the skills, agents and commands in a directory, with an exit code CI can act on.

Flags:
- `--strict`: treat warnings as errors, so unrecognized fields, missing metadata and other issues the runtime tolerates fail the run.
- `--json`: output the report as one JSON object with the same exit codes. Requires Claude Code v2.1.259 or later.
- `--profile <name>`: only `directory`. Also exit `1` when the plugin directory (Anthropic's catalog that plugins are submitted to) would refuse a submission on a check this command runs, such as a missing README, or when such a check could not be made: `plugin.json` lists more than 16 files for MCP servers or for hooks (16 of each are checked), or an MCP or hooks file is one these checks cannot use, such as invalid JSON. With `--strict`, also fail on its warnings. The directory runs more checks (binary 2.1.319; not on the docs page).

What a directory `<path>` validates:
- `.claude-plugin/marketplace.json`, when it exists.
- Otherwise `.claude-plugin/plugin.json`.
- Otherwise the component files, chosen by the directory's name (requires v2.1.233 or later): a directory named `skills`, `agents` or `commands`: the files inside it; a directory named `.claude`: the `skills`, `agents` and `commands` directories inside it; any other directory: those three under its `.claude`.
- A directory with both `marketplace.json` and `plugin.json`: the marketplace, plus the plugin's manifest and component files. Requires v2.1.289 or later.

Symlinks inside the named directory are not followed:
- A linked `skills`, `agents` or `commands` directory under the plugin or `.claude` root: warns that nothing in it was read.
- A linked entry inside a `skills`, `agents` or `commands` directory: skipped, with a per-directory warning of how many entries a session would load.
- The `skills`, `agents` or `commands` directory you name is itself a symlink, or its parent `.claude` is: error, nothing checked. Name the real directory.

Not read by a validation run:
- A `SKILL.md` at the plugin root.
- A `CLAUDE.md` at the plugin root: in a plugin run, Claude Code warns about it.
- In a marketplace run: the skill, agent, command and hook files of plugins the marketplace lists in other directories, and the MCP server files they bundle. Validate each plugin directory to find errors there.

A manifest file `<path>`:
- Not named `plugin.json` or `marketplace.json` and not in a `.claude-plugin` directory: validated as a marketplace when `plugins` is an array, or `plugins` and `owner` are both present, or it has a field only `marketplace.json` defines (such as `owner`) and none only `plugin.json` defines (such as `author`); otherwise as a plugin manifest.
- Any other file in a `.claude-plugin` directory: a plugin manifest.
- To choose the checks yourself, name the file `plugin.json` or `marketplace.json`.
- Since 2.1.318, `validate` no longer passes a custom-named marketplace file that `claude plugin marketplace add` rejects (changelog 2.1.318).

Output and exit codes: the file validated, errors and warnings with their paths, and a verdict line.
- `0`: `Validation passed` or `Validation passed with warnings`. The manifest loads; with `--strict`, no warnings either.
- `1`: `Validation failed` or `Validation failed (--strict treats warnings as errors)`. An error, or a warning under `--strict`. Advice never counts.
- `2`: `Unexpected error during validation: <reason>`. The validator itself failed, such as on an unreadable path. Nothing on stdout; the error goes to stderr.

`--json` top-level fields:
- `success`: the same verdict as the exit code.
- `strict`: whether warnings were treated as errors.
- `target`: the resolved path validated.
- `manifest`: the manifest's own result, or `null` for a run without a manifest. For a directory with both manifests, the `marketplace.json` result.
- `contents`: per-file results, each naming its `file` with `errors`, `warnings` and `notes` arrays. Files with nothing to report get no entry. For a directory with both manifests, `plugin.json` results go here.
  - `gatingHooks`: for each mod hook that can refuse an action (such as a `tool.call` hook), whether it has a `.catch` handler: `module`, `pattern`, `hook`, `hasCatch`. Requires v2.1.290 or later.
- `advice`: each entry names the README as `file`, with a `message` and the `installLine` to paste. Empty when none. Requires v2.1.295 or later.

Notes on mods (changelog): 2.1.299 added a note naming a mod's hooks that are skipped where an organization manages Claude Code; 2.1.304 removed the notes that predicted where a mod's hooks would run.

Advice on the README (requires v2.1.295 or later):
- An `ℹ Advice (does not change the verdict):` block means a plugin's README has no line that installs the plugin from a marketplace, with a suggested line. It changes neither the verdict nor the exit code, with or without `--strict`.
- To clear it, paste the suggested line into the named README and validate again.
- A suggestion holding the placeholder `<owner>/<repo>` doesn't clear the advice if pasted unchanged. Validating the plugin's own directory: when the marketplace lists the plugin from a directory inside its own, validate that directory instead; otherwise fill in `<owner>/<repo>` yourself. Validating the marketplace's directory: Claude Code fills the source from the `origin` remote of the `.git` at the top of that directory; with no usable remote, replace `<owner>/<repo>` yourself.
- An existing line counts when `plugin install`, or `plugin i`, is followed on the same line by `<plugin>@<marketplace>` (`/plugin install deploy-helper@acme-tools`) or by the plugin's name and `--marketplace <source>` (`/plugin install deploy-helper --marketplace acme/tools`). The `/plugin` and `claude plugin` spellings both count.

Example: `claude plugin validate ./my-plugin --strict`

## Synced plugins (`@synced`)

Plugins turned on for a claude.ai account, by the user or by their organization. Source: `https://code.claude.com/docs/en/plugins/loading.md`, "Plugins synced from claude.ai", and the changelog.

What they are:
- Each loads as `<name>@synced`, with no marketplace and no install record. In terminal sessions their skills, agents, hooks, MCP servers and LSP servers all load, with the same trust as an installed marketplace plugin.
- The sync goes one way only: `claude plugin install` and `/plugin` installs stay on the machine and never reach the claude.ai account.
- `synced` is a reserved origin name: no marketplace can be named `inline`, `skills-dir` or `synced`.
- Precedence: a synced plugin loads last. When an enabled plugin from any other origin has the same manifest name, that plugin loads and the synced copy is reported as not loaded. To use the claude.ai copy, disable your own copy.

When they sync:
- Cowork: downloaded into the session's own environment when the session starts. In a cloud Cowork session, a plugin turned on or off mid-session may arrive after a few messages; if nothing changes, start a new session.
- Terminal sessions: each start of Claude Code syncs once in the background, downloading new and updated plugins and removing the ones turned off. Requires Claude Code v2.1.273 or later.
- The background sync can finish after the session starts. In an interactive session it then shows `Plugins changed. Run /reload-plugins to activate.` Run `/reload-plugins`, or leave it for the next start.
- A plugin turned on or off on claude.ai during a terminal session is downloaded or removed the next time Claude Code starts.

When a synced plugin is missing (the terminal neither downloads nor loads synced plugins, even after `/login`):
- The session isn't signed in with the claude.ai account: plugins sync only in sessions that are.
- `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` or an `apiKeyHelper` script supplies the credential in place of that sign-in.
- The session doesn't fetch feature flags from Anthropic, such as with `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` set.
- Bare mode, or a session started with `--safe-mode`.
- A `--setting-sources` list that leaves out `user`.
- A sign-in made on an earlier Claude Code version doesn't cover plugins until Claude Code renews it in the background. Run `/login` again; sync starts at the next start of Claude Code.
- `syncClaudeAiPlugins` is `false` in user or managed settings, or the organization turned off Skills on claude.ai.

Controlling them:
- One plugin: `claude plugin disable <name>@synced`, or the Installed tab of `/plugin`, saves `"<name>@synced": false` in the user-level `enabledPlugins`. To keep it out of a project in every environment, set the same key in the project's committed `.claude/settings.json`.
- Every synced plugin on a machine: set `syncClaudeAiPlugins` to `false` in user settings (an organization can set it in managed settings). Claude Code stops downloading and, at the next start, moves the plugins it already synced to `~/.claude/plugins/.trash/` and no longer loads them. `syncClaudeAiSkills: false` opts out of synced skills the same way (changelog 2.1.275).
- A plugin the organization marks as required on claude.ai loads even if disabled earlier. `claude plugin disable` refuses it with `Plugin "<name>@synced" is required by your organization and can't be disabled here. Contact your admin to change it.`, and `claude plugin list` marks it `required by your org`.
- Remove one: turn it off on claude.ai (Customize > Plugins), as the install guide says; it has no install record to uninstall.
