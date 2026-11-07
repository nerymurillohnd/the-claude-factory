---
name: plugin-commands
description: Exact reference for the Claude Code plugin CLI - every claude plugin and claude plugin marketplace subcommand, every /plugin form, /reload-plugins, --plugin-dir and --plugin-url, with flags, defaults, aliases, output and error messages, JSON fields, exit codes, scopes and minimum versions. Use when installing, uninstalling, enabling, disabling, updating, configuring, listing, validating, tagging, releasing, evaluating, testing or pruning plugins; adding, refreshing or removing marketplaces of any source type; reloading plugins in a session; loading a plugin for one session; scripting plugin commands with --json; or debugging a plugin command's output, error or exit code.
---

# Claude Code plugin commands

The reference files in `references/` hold every flag, message, JSON field, exit code and minimum version, checked against Claude Code 2.1.319, its docs and its changelog. Read the gotchas, pick the command, then load only the reference file the task needs.

## Before you rely on a version-gated flag or behavior

Claude Code ships often, and the user's version may differ from 2.1.319.

1. Run `claude --version`, then `claude plugin <subcommand> --help` (or `claude plugin marketplace <subcommand> --help`) on the user's machine.
2. For a flag or behavior marked "Requires Claude Code vX" or "(changelog X)", check the live page `https://code.claude.com/docs/en/plugins/cli-reference.md` or the changelog (`https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md`).
3. Tell the user what differs from these references before acting on it. The installed binary wins over the docs, and the newest official source wins over an older one.

Never write version checks or fallback paths into a script for the user. When a command fails, report its message and exit code.

## Which installation you are changing

- `claude plugin …` and `/plugin` change the machine Claude Code runs on (`~/.claude` and the project's `.claude/` settings).
- claude.ai chat and Cowork read plugins from the claude.ai account. Those are added in Customize > Plugins, not with the CLI. Account plugins reach Claude Code as `<name>@synced`; CLI installs never reach the account.
- Before running a command, check `command -v claude` in the shell and that this shell is the machine the user means to change. Otherwise give the user the exact command or the Customize > Plugins path, and never say it ran.

## Gotchas

- `/plugin install <source>` with a path, URL or `owner/repo` installs nothing. It reports `Marketplace "<source>" not found`, even for a source already added. Add the marketplace first, or use `/plugin install <plugin> --marketplace <source>` (v2.1.275+) or `claude plugin install <plugin> --marketplace <source>` (v2.1.292+).
- `/plugin install <plugin>` in a session opens the details pane. It doesn't install until a scope is chosen there.
- `claude plugin configure` accepts only `name@marketplace`, never a bare name.
- Before v2.1.281, `claude plugin update` without `--scope` used `user` and failed for a plugin installed only at project or local scope with `Plugin "<name>" is not installed at scope user`. On those versions, pass `--scope`.
- No command updates every plugin at once. `claude plugin marketplace update` with no name refreshes listings but leaves installed plugins at their versions.
- `claude plugin validate` doesn't follow symlinks in the directory you name. A marketplace run doesn't open the listed plugins' skill, agent, command, hook or MCP files: validate each plugin directory too.
- `claude plugin validate` output symbols change when output isn't a TTY (✔ ⚠ ✘ become √ ‼ ×). Scripts read the exit code or `--json`, not the symbols.
- `claude plugin eval`: put the target before `--tag`, `--allow-tools` and `--json`. Each of these takes the following words as its value.
- `-y` and `--accept-command` have no effect inside a Claude Code session (Bash tool, hook). The user runs those commands from their own terminal.
- Without a TTY, an install or update that shows a marketplace-declared command is refused unless `-y` or `--accept-command <sha256>` is passed.
- `claude plugin tag` needs a `version` in `plugin.json` or the marketplace entry, a clean working tree, a tag that doesn't exist yet, and a git repository. `/plugin tag` accepts only `--push`, `--dry-run` and `--force`/`-f`.
- `claude plugin marketplace remove` uninstalls every plugin installed from that marketplace and deletes their options, secrets and data where it can, once no scope declares the marketplace. Confirm with the user first. To refresh, use `marketplace update`.
- `claude plugin uninstall` from the last scope deletes the plugin's options, secrets and data directory unless `--keep-data` is passed. Confirm with the user first.
- `enable` on an enabled plugin, and `disable` on a disabled one, exit `1`. With `--json`, `alreadyInGoalState: true` marks it.
- A `/reload-plugins` that adds or removes a plugin MCP server or the `LSP` tool isn't applied without `--force`, because it would invalidate the prompt cache.
- `/plugin` doesn't run in `claude -p` or other non-interactive runs (`/plugin isn't available in this environment.`). Use `claude plugin` from the shell. `/reload-plugins` does run there (v2.1.260+).
- `/marketplace` is an alias of `/plugin`, so `/marketplace list` lists plugins. Use `/plugin marketplace list`.
- `/plugin help` printed nothing on 2.1.319. Use `claude plugin --help`.
- A `--plugin-dir` plugin silently replaces a same-named installed plugin for that session, and `claude plugin list` still shows the installed row as enabled.
- `--plugin-dir` at a marketplace root loads nothing and shows no error. Point it at the plugin directory.

## Which command fits the task

- Install from a marketplace: `claude plugin install <plugin>@<marketplace> [--scope]`. In a session, `/plugin install <plugin>@<marketplace>`, then pick a scope.
- Add a marketplace and install in one step: `claude plugin install <plugin> --marketplace <source>`.
- Add, list, refresh or remove a marketplace: `claude plugin marketplace add|list|update|remove`.
- See what is installed: `claude plugin list [--json] [--available] [--data-size]`.
- See what a plugin costs and contains: `claude plugin details <name>`.
- Set a plugin's options: `claude plugin configure <name@marketplace> [--values-stdin] [--json]`, or `install --config`.
- Turn a plugin on or off: `claude plugin enable|disable <plugin> [--scope]`. Use `disable --all` for everything.
- Update a plugin: `claude plugin update <plugin> [--scope]`. In a session, use Update now on the Installed tab.
- Remove a plugin: `claude plugin uninstall <plugin> [--scope] [--keep-data] [--prune]`. Remove orphaned dependencies with `claude plugin prune`.
- Apply changes to a running session: `/reload-plugins [--force]`.
- Create a plugin: `claude plugin init <name> [--with ...]` (writes under `~/.claude/skills/`).
- Test a plugin without installing it: `claude --plugin-dir <path>` or `claude --plugin-url <url>`.
- Check a plugin or marketplace before publishing: `claude plugin validate <path> --strict [--json] [--profile directory]`.
- Run a mod's tests: `claude plugin test [dir]`.
- Score a plugin with evals: `claude plugin eval [target] [options]`. Create a suite with `claude plugin eval init`.
- Tag a release: `claude plugin tag [path] --dry-run`, then without `--dry-run`, and with `--push` only when the user approves the push.

## Which reference to load

- `references/plugin-commands.md`: every `claude plugin` subcommand (init, install, uninstall, enable, disable, update, list, details, configure, prune, eval, eval init, tag, test, validate), the shared exit codes, scopes and aliases, and the `--json` result format.
- `references/marketplace-commands.md`: `claude plugin marketplace add|list|remove|update`, every source form, private marketplace credentials and claude.ai marketplaces.
- `references/session-commands.md`: every `/plugin` form, where `/plugin` runs on each surface, the panel tabs, and `/reload-plugins`.
- `references/session-flags.md`: `--plugin-dir`, `--plugin-url`, `CLAUDE_CODE_PLUGIN_DIRS`, `@inline` plugins and their precedence.

Each reference opens with a contents list. Search it with grep for the flag or message you need instead of reading it whole.
