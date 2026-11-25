# Plugin messages by stage

Every documented plugin message, grouped by the stage that produces it, with its cause and fix. Search this file for the text the user pasted.

## Contents

- [Gotchas](#gotchas)
- [Where /plugin runs](#where-plugin-runs)
- [Add a marketplace](#add-a-marketplace)
- [Install](#install)
- [Dependencies](#dependencies)
- [Enable, disable, update, uninstall, configure](#enable-disable-update-uninstall-configure)
- [Installed but not working](#installed-but-not-working)
- [Hooks](#hooks)
- [MCP and LSP servers](#mcp-and-lsp-servers)
- [Build: paths, skills and validation](#build-paths-skills-and-validation)
- [Host a marketplace](#host-a-marketplace)
- [Organization policy](#organization-policy)
- [Results and exit codes](#results-and-exit-codes)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- In a terminal, success lines drop the word `Successfully`, as in `Installed plugin: <plugin>@<marketplace>`; when stdout or stderr isn't a terminal they keep it. Match the message without that word. A working install in a session prints a summary that starts with `✓ Installed <plugin>.`
- A message sits under the stage that produces it, which isn't always the command the user ran: an install can fail because its marketplace is missing, so that message is under "Add a marketplace".
- Some causes appear only in the debug log, never in the Errors tab: a `.mcp.json` entry that fails the schema, a `--plugin-dir` override, a custom commands folder with nothing in it.
- A message that names a hooks module (`hooks module not loaded`, `hooks module did not load`) belongs to a mod: its causes are mod refusals, not plugin messages, and this file doesn't list them.

## Where /plugin runs

| Message | Cause and fix |
| :-- | :-- |
| `/plugin isn't available in this environment` | `/plugin` runs only in an interactive terminal session, not in `claude -p`, the Agent SDK or VS Code's panel (where bare `/plugin` opens Manage plugins). Use the `claude plugin` shell command |
| `zsh: no such file or directory: /plugin`, `bash: /plugin: No such file or directory`, PowerShell `The term '/plugin' is not recognized` | a session command typed in the shell: run `claude plugin …` there, or `/plugin` inside a session |
| `claude: command not found`, `'claude' is not recognized` | Claude Code isn't on `PATH` |
| `error: unknown command 'add'`, `error: unknown option '--project'`, `Unknown command: /install` | wrong spellings: the commands are `claude plugin install`, `--scope project` and `/plugin install`. Aliases that work: `claude plugins`, `claude plugin remove`, `rm`, `i`, `new`, `autoremove`, `/plugins`, `/marketplace` |
| a message ending `installed in this project` | `/plugin enable`, `disable`, `uninstall` or `configure` on a plugin that isn't on the Installed tab |

`init`, `update`, `details`, `restore-set-aside`, `prune`, `eval`, `eval init` and `test` have no session form.

## Add a marketplace

| Message | Cause and fix |
| :-- | :-- |
| `Marketplace "claude-plugins-official" not found` | the official marketplace registers on the first interactive terminal session, never from a shell command; also skipped under a policy block or `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL`, which, once set, skips it for good |
| `Marketplace "<name>" not found` | the marketplace isn't added, or `/plugin install <source>` was given a path, a URL or `owner/repo`; a `claudeai-` name needs `claude plugin marketplace add --claudeai <name>` |
| `Invalid marketplace source format`, `That isn't a marketplace source`, `'<source>' is not a valid GitHub owner/repo shorthand`, `Invalid git URL` | accepted forms: `owner/repo`, an `https://` or `http://` URL, `user@host:path`, and paths starting with `./`, `../`, `/` or `~` |
| `Path does not exist: <path>`, `File path must point to a .json file (marketplace.json)`, `Marketplace file not found at <path>/.claude-plugin/marketplace.json` | the local path or the file is wrong |
| `Cannot add marketplace "<name>": Claude Code cannot install plugins from a marketplace with this name`, `… reserves this name`, `"<x>" is another spelling of "<y>", a reserved marketplace name`, `Marketplace name impersonates an official Anthropic/Claude marketplace` | rename the marketplace; a registered entry under such a name is ignored with a `Remove it with: claude plugin marketplace remove …` warning |
| `Failed to clone marketplace repository:` with `SSH authentication failed` or `HTTPS authentication failed` | prompts are off during the clone; set up a key or token, or `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` to skip SSH for `owner/repo`. `GIT_SSH_COMMAND`, `GIT_SSH` and `core.sshCommand` are honored |
| `SSH host key is not in your known_hosts file`, `SSH host key has changed` | add or fix the host key: the clone runs with `StrictHostKeyChecking=yes` |
| `Git clone timed out after 120s` | raise `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS`, or add with `--sparse` |
| `Marketplace "<name>" is already added from a different source (…)`, `its source doesn't match its extraKnownMarketplaces entry in user or managed settings` | the name is taken by another source; remove one, or match the settings entry |
| `Marketplace '<name>' is not declared in project settings. Omit --scope to remove it from all scopes.` | remove from the scope that declares it. Removing from the last scope deletes the clone and uninstalls its plugins with their options, secrets and data |
| a notice that a marketplace can't be fetched because its repository isn't one of the session's | a cloud or self-hosted session reaches only its own repositories |

Offline: `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` keeps a checkout that has `.claude-plugin/marketplace.json`, and `CLAUDE_CODE_PLUGIN_SEED_DIR` seeds images.

## Install

| Message | Cause and fix |
| :-- | :-- |
| `Plugin "<name>" not found in marketplace "<marketplace>"` | with the hint `Your local copy may be out of date — try claude plugin marketplace update <marketplace>`, refresh; without a hint the name is wrong. The entry name and the manifest `name` must match |
| `Plugin "<name>" not found in any marketplace` (shell: `… in any configured marketplace`) | no added marketplace lists it |
| `Plugin "<name>@<marketplace>" is already installed (scope: user)` | exits 0 and downloads a missing cache again |
| `"<plugin>" was not installed: it would share its folder with "<other>"`, `… its saved data with` | two plugins resolve to one folder: only one of the two can be installed |
| `This plugin uses a source type your Claude Code version does not support` | update Claude Code |
| `Plugin archive integrity check failed for <url>` | the archive's sha256 doesn't match the entry; nothing was installed |
| `An npm plugin source must name a registry package` | the `npm` source names something else |
| `Marketplace "<name>" is registered from an untrusted source`, `… can only be used with GitHub sources from the 'anthropics' organization` | the name is reserved for Anthropic's sources |
| `Marketplace "<name>" is added but ignored` | the reason follows; `(see the debug log)` means a refused name |
| `Plugin <name> has a corrupt manifest file` (`JSON parse error:`), `… has an invalid manifest file` (`Validation errors:`) | fix `plugin.json`; the install exits 1 |
| `Plugin not loaded: its manifest <path> was not read, because it resolves to <path>, outside …` | the manifest is a link out of the plugin |
| `Plugin directory not found at path: <path>`, `Marketplace directory not found at path: <path>` | the source path is wrong |
| `No plugins yet`, `No marketplaces configured` | Discover is empty: add a marketplace |
| `Couldn't install: <plugin> (<reason>)`, `Failed to install: <plugin> (<reason>)` | a shortened line ends `Installing a plugin from its details (Enter) in /plugin shows its full error.` |
| `Could not move the new copy of this plugin version into <path>` | another program, such as a scanner or another Claude Code session, was using the version folder; the message says whether the previous copy was moved back. Run the install again once the folder is free; `Left on disk` copies are cleaned up later |
| `Run this command now? [y/N]`, `Aborted — the command was not run.` | the marketplace declares an install command. Without a terminal it is refused unless `-y` or `--accept-command <sha256>`; `-y` is ignored when Claude runs the install through Bash or a hook |
| `Marketplace "<name>", which managed settings declare, stands from another source and cannot be taken back while its declared source is unreachable` | restore access to the declared source and start a new interactive session. Options and secrets set aside by such a take-over come back with `claude plugin restore-set-aside <plugin>@<marketplace>` |

## Dependencies

`Dependency "<dep>" is not installed`, `… is disabled`, `Requires "<dep>" <range>, installed <version>`, conflicting or invalid ranges, `no git tag satisfying`, a cross-marketplace dependency not on the allowlist, `… still unresolved: <names>` and `Dependencies are not installed while non-essential traffic is turned off.` In `errorDetails`, `is not installed` (with its synced variant) and `is disabled` carry `type: dependency-unsatisfied`, and `Requires "<dep>" <range>, installed <version>` carries `dependency-version-unsatisfied`. Install or enable the dependency, or widen the range, then reload.

## Enable, disable, update, uninstall, configure

| Message | Cause and fix |
| :-- | :-- |
| `Plugin "<name>" is already enabled` or `disabled` | exits 1; under `--json`, `failureCode: "already_in_goal_state"` |
| `Plugin "<name>" is installed at project scope, not user. Use --scope project or omit --scope to auto-detect.` | without `--scope`, enable and disable act on the first of local, project and user that mentions the plugin |
| `Please specify a plugin name or use --all to disable all plugins` | name a plugin; `--all` takes neither a name nor `--scope` |
| `<name> is already at the latest version (<version>).` | the computed version didn't change: bump `version`, or leave it out of the manifest and the entry to track commits |
| `Failed to update plugin "<name>"` | the dependency install retry failed |
| `"<name>" was not uninstalled:` with a settings file | `failureCode: "settings_still_on"`: the plugin is still switched on in that file, which couldn't be changed or read |
| `Configuration saved. Restart Claude Code to apply it.`, `Failed to save configuration:`, `No installed plugin has the id "<plugin>".` | `claude plugin configure` and `restore-set-aside` take only the full `<plugin>@<marketplace>` id |
| `Plugin "<name>" not found. Run claude plugin list to see installed plugins, or pass --plugin-dir <path> to load one from disk.` | `claude plugin details` needs a loaded plugin: installed, in a skills directory, or passed with `--plugin-dir` or `--plugin-url` before the subcommand; an `@builtin` id never appears in `claude plugin list` |
| `--data-size names a plugin that is not installed` | pass `name@marketplace` of an installed plugin |
| `Not a TTY — run claude plugin prune -y to remove.` | `prune` without a terminal removes nothing and exits 0 whatever happened |

Uninstalling from the last scope deletes the plugin's options, secrets, `~/.claude/plugins/data/<id>/` and its unpacked MCP bundles, unless `--keep-data`.

## Installed but not working

| Message | Cause and fix |
| :-- | :-- |
| `Run /reload-plugins to apply.` instead of `Plugin is now active.` | run it; the install is on disk but not in the session |
| `Plugin "<name>" not cached at <path>` with `Run /plugin to refresh the plugin cache` | no usable copy, such as after the cache was cleared |
| `Plugin "<name>" is on in project settings but isn't installed here` | run `claude plugin install <name>@<marketplace> --scope project`, then reload |
| `The packages it lists are not installed` | the Node.js install failed or was skipped: retry with `claude plugin update`; skipped under `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` |
| `installed_plugins.json holds a record under "<id>" that this version of Claude Code cannot read` | another Claude Code version, usually a newer one, wrote it: run `claude update`, else uninstall the plugin with the version that wrote it, or delete the record by hand; `installed_plugins.json could not be read and was rebuilt` needs nothing |
| `⚠ <file> does not load (its "permissions" is not valid), so Claude Code ignores the whole file` | fix that settings file: everything in it is ignored |
| `Version: unknown` on a git-sourced plugin | update Claude Code, the marketplace and the plugin, then check the 12-character commit |
| `Default <folder>/ folder is ignored because the manifest sets "<key>"` | the manifest replaces that default folder |
| `skills path couldn't be checked: <path> (ELOOP)`, `Path not found: <path> (skills, ELOOP)` | a link loop (`ELOOP`), a disk error (`EIO`, `ESTALE`) or a missing execute permission (`EACCES`) |
| `Plugin source path refused: ./<path> does not stay inside its marketplace directory` | the entry's `source` leaves the marketplace folder |

## Hooks

| Message | Cause and fix |
| :-- | :-- |
| `Couldn't load hooks from <path>: <reason>`, `Failed to load hooks from <path>: <reason>` | often a missing top-level `"hooks"` key: `hooks/hooks.json` wraps the event map in it, while an inline map in `plugin.json` has none |
| `hooks path not found: <path>`, `hooks path escapes plugin directory: <path>` | the path in the manifest is wrong or leaves the plugin |
| `<Event> hook error: Failed with non-blocking status code: <stderr>`, `/bin/sh: node: command not found` | the hook ran and failed, or its program isn't installed where it runs |
| `Failed to run: Plugin directory does not exist: <path>` | the installed version moved: run `/reload-plugins` |
| `Hook from plugin <id> references ${user_config.*} in a shell-form command` | read `$CLAUDE_PLUGIN_OPTION_<KEY>` instead, or switch the hook to exec form with `args` |
| `<Event> hook needs quotes around a path with a space (<script>)`, such as `Stop hook …` | an `asyncRewake` hook in shell form leaves a path unquoted: quote the plugin-root placeholder in its command |
| a block reason ending `This hook comes from the <plugin> plugin.` | the plugin's hook exited 2 |

A hook that never fires: check that `/hooks` lists it, the event's case (`PostToolUse`), that the matcher is a string (an array is invalid) with tool names spelled as the tools are, then trigger it on purpose and read the debug log.

## MCP and LSP servers

| Message | Cause and fix |
| :-- | :-- |
| `Invalid MCP server config for "<server>": <error>` | `Missing environment variables: <names>`, `URL is unset or invalid`, or a `headersHelper` that references `user_config` |
| `Bundled MCP server "<name>" was not started: it needs configuration` | set its options with `claude plugin configure` |
| `Skipping connection (recent failure cached; retries automatically in 15 min, or edit the plugin config to retry now)` | a stdio server failed less than 15 minutes ago: Reconnect in `/mcp`, or edit its `command`, `args` or `env` |
| `Invalid MCP server config for <server> in <path>` in the debug log only | the entry fails the schema; `claude plugin validate` reports it |
| `mcp-servers path not read: <path> is absolute or has a ".." part` | use a `./` path inside the plugin |
| `Executable not found in $PATH: "<binary>"`, `LSP server <name> failed to start: <reason>` | install the language server where Claude Code runs |
| `Invalid LSP server config for ".lsp.json"` | one invalid entry skips the whole file |

## Build: paths, skills and validation

| Message | Cause and fix |
| :-- | :-- |
| `File not found: <path>`, `No manifest found in directory. Expected .claude-plugin/marketplace.json or .claude-plugin/plugin.json` | run validate on the root that holds `.claude-plugin/` |
| `Invalid JSON syntax: <parse error>` | fix the manifest or `hooks/hooks.json`; until then a session loads the plugin without that file's hooks |
| `Path not found: <path>. The runtime loader will report this as a load failure.`, `Path contains ".." which could be a path traversal attempt: <path>` | fix the component path, inside the plugin root |
| `YAML frontmatter failed to parse: <error>` | fix the frontmatter between `---` delimiters |
| `Plugin name "<name>" is reserved: it passes as one of Anthropic's own` | rename the plugin for what it does |
| `commands path not found: <path>` (also `skills`, `agents`, `hooks`) | the path, resolved against the plugin root, holds nothing: compare the absolute path in the message with the disk, fix the path or create the folder, then `/reload-plugins`. Component paths start with `./`; `skills` also accepts `"."` |
| `Path escapes plugin directory: <path> (commands)`, `— it resolves to <path>, outside the plugin directory` | a path or symlink leaves the plugin (on macOS and Linux, any backslash too); the plugin loads without that component |
| `path is a file; skills entries must be directories containing SKILL.md` | point `skills` at the folder |
| `Plugin <name> has conflicting manifests: both plugin.json and marketplace entry specify components.` | with `strict: false`, declare components in one place |
| `Warning: No commands found in plugin <name> custom directory: <path>` | debug log only: the custom folder is empty |
| `Must be a version range such as ">=2.1.0"; got "<value>". It will be ignored at load time.` | fix `engines["claude-code"]` |
| names that `differ only by letter case or Unicode form`, `Windows can open this path as another file` | rename one of the two files |
| `No frontmatter block found`, `Unknown field '<key>'` | fail only with `--strict`; an unknown key inside `userConfig`, `channels`, `lspServers` or `monitors` always fails |
| `Plugin name "<name>" reads as one of Anthropic's own` | a warning; names starting `claude-`, `anthropic-`, `anthropics-` or `cc-plugin-` are errors |
| `<directory> is not a plugin or skill folder` from `claude plugin eval init` | run it from the plugin root, or pass `--eval-dir` |

A skill that is never invoked: `disable-model-invocation: true`, a description that doesn't match the request, or a description cut short by the listing budget.

## Host a marketplace

| Message or symptom | Cause and fix |
| :-- | :-- |
| `its marketplace entry path does not stay inside the marketplace directory`, `Plugin source path refused`, for a marketplace added by an `https://…/marketplace.json` URL | a URL marketplace downloads only `marketplace.json`, so relative-path sources point at nothing: give each entry a fetchable source such as `{ "source": "github", "repo": "owner/repo" }`, or host the marketplace in git |
| a root plugin's files from a git submodule are missing after install | only submodules that hold plugin files are fetched, judged from the paths written in the plugin's files: write the path in full, such as `${CLAUDE_PLUGIN_ROOT}/vendor/tool/run.sh` |
| `Duplicate plugin name "<name>" found in marketplace`, `Path contains "..": <path>` under `plugins[N].source`, control or bidirectional characters in a name, a name outside the plugin-id rule | errors: fix the entry the message names |
| `Marketplace has no plugins defined`, `No marketplace description provided`, `Plugin name "<name>" is not kebab-case`, `Entry declares version "<a>" but <path>/plugin.json says "<b>"`, `Marketplace name "<name>" is reserved in Claude Desktop`, `… is not accepted by Claude Desktop` | warnings: `plugin.json` wins on the version; Claude Desktop's sync rejects `org`, `org-provisioned`, `unknown` and names over 128 characters |

Entry-level problems carry the prefix `plugins[N] plugin.json →`.

## Organization policy

- `Marketplace source '<source>' is blocked by enterprise policy`, with `Allowed sources:` or `No external marketplaces are allowed.`
- `Marketplace "<name>" is not in the allowed marketplace list`, `… is blocked by enterprise policy`.
- `Plugin "<name>" is blocked by your organization's policy and cannot be installed` (or `cannot be enabled`).
- `--plugin-dir is disabled by your organization's managed settings (disableSideloadFlags)`, also for `--plugin-url`.
- `Plugins from ~/.claude/skills/ are blocked by your organization's managed settings`, `Command-sourced plugins are disabled by your organization's managed settings`, `Marketplace '<name>' is seed-managed (<dir>)`.
- `Plugin "<name>@synced" is required by your organization and can't be disabled here. Contact your admin to change it.`

Each is the organization's setting: say which one, and send the user to their administrator.

## Results and exit codes

- Every `claude plugin` command exits 0 on success and 1 on failure; `validate` adds 2 for a validator error, and `eval` adds 2 for a partial run, 130 when interrupted and 143 when terminated.
- The install family's `--json` result is the last stdout line, with `command`, `outcome` (`ok` or `failed`), `message`, and `pluginId`, `scope`, `failureCode`, `commandPrinted` and `commandFailed` when they apply. A usage error prints no result line.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Troubleshoot plugins](https://code.claude.com/docs/en/plugins/troubleshooting) when the message is not here. It gives every documented message by stage.
- Read [Error reference](https://code.claude.com/docs/en/errors) when the message names a path, a reserved name or an uninstall. It gives the exact forms of those errors.
- Read [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference) when a command's output or exit code is in question. It gives every command's results.

## Exit

The message is matched to its cause, quoted with the row or page that gives it. Return to step 4 of the diagnosis in `SKILL.md`.
