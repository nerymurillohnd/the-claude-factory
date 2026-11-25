# Install tests, mods and CI

How to install a plugin the way users receive it in a throwaway configuration, test a mod, gate a CI job on a plugin loading, and check a release before it is tagged.

## Contents

- [Gotchas](#gotchas)
- [Install it as users do](#install-it-as-users-do)
- [Rule out your own setup](#rule-out-your-own-setup)
- [Mods](#mods)
- [Headless runs and CI](#headless-runs-and-ci)
- [Surfaces other than the terminal](#surfaces-other-than-the-terminal)
- [Release checks](#release-checks)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- A marketplace added from a local path proves the install and the listing, not the copy users load: its relative-path plugins load in place from the marketplace folder (`readFromFolder` in `claude plugin list --json`), with no dependency install. Only a git-hosted marketplace, `owner/repo#ref` or a `.git` URL, gives the copied, cache-loaded install users get.
- `--plugin-dir` loads in place too, so "works with `--plugin-dir`, breaks after install" is usually a path that reaches outside the plugin or a file the install doesn't copy.
- Every `claude -p` run is a billed model call; validate, `list`, `details`, `plugin test` and installs into a throwaway configuration cost nothing.
- `--bare` skips plugin hooks, even for a plugin loaded with `--plugin-dir`: never use it for a run that needs them.

## Install it as users do

Run each command with a throwaway configuration, so the user's own `~/.claude` stays untouched; every setting, marketplace and plugin lands under `CLAUDE_CONFIG_DIR`:

```bash
T="$(mktemp -d)"
CLAUDE_CONFIG_DIR="${T}/config" claude plugin marketplace add owner/repo#my-branch
CLAUDE_CONFIG_DIR="${T}/config" claude plugin install my-plugin@my-marketplace
CLAUDE_CONFIG_DIR="${T}/config" claude plugin list --json
CLAUDE_CONFIG_DIR="${T}/config" claude plugin details my-plugin
rm -rf "${T}"
```

- In `list --json`, the plugin's row has no `errors`, its `installPath` is under `plugins/cache/<marketplace>/<plugin>/<version>/`, and it has no `readFromFolder` for a git-hosted source.
- Validate the marketplace folder before you add it, and install after: a reserved name, a missing source folder and an entry name that differs from the manifest's `name` (`Plugin "<name>" not found in marketplace`) surface only at add or install.
- Node.js dependencies install only into a copied plugin that has a `package.json` and a supported lockfile, run no install scripts, and stop after 60 seconds; `list` notes `The packages it lists are not installed` when they didn't.
- Without a terminal, installing a plugin whose marketplace declares a command is refused unless `-y` or `--accept-command`; inside a Claude Code session `-y` is ignored.
- A dependency resolved from a marketplace shows its version with a 12-character suffix in `claude plugin list`; `claude plugin prune --dry-run` previews the dependencies nothing needs.
- `CLAUDE_CODE_PLUGIN_CACHE_DIR` moves the plugins root instead of the whole configuration.

## Rule out your own setup

When a plugin works for you and not for a user, or the reverse, test against a clean configuration from an empty folder: `CLAUDE_CONFIG_DIR=<tmp>/config claude --setting-sources user`.

## Mods

- `claude plugin test [dir]` runs every `*.test.ts` and `*.test.tsx` under the folder, each file in a child of the installed binary, in an environment like the one the mod's hooks run in, and exits 1 when a test fails. It needs no session, sign-in or network.
- A test file imports its kit from `claude-code/testing`: `test`, `expect`, `mock` (`clock`, `store`, `env`, `session`) and `tier`. Register stubs with `on` before the first `$` call.
- A file that declares no `test()` fails with `declares no test(): nothing ran`. A stub that answers neither `{ value }` nor `{ deny }` fails with `returned neither { value } nor { deny }`, and a call with no stub with `no implementation for <name>`.
- Where mods can't load in that shell the command prints `claude plugin test: hooks modules are turned off` and exits 1.
- A mounted handle from `$.ui.mount` offers `press`, `input`, `select`, `keepsBeneath`, `find` and `unmount`; tests don't check painting, so check a new layout in a real session.
- Run `claude plugin validate` on a mod before a session: it applies the same static analysis as loading, and the build's `claude-code/index.d.ts` holds the types.

## Headless runs and CI

- `claude -p` loads hooks, skills, plugins and MCP servers like an interactive session, and runs project hooks and `.mcp.json` servers without a trust dialog. It starts in Manual mode when nothing sets a mode, so unapproved calls are denied: pre-approve with `--allowedTools`, or set `--permission-mode`.
- Fail a CI job when a plugin or server doesn't load: run with `--output-format stream-json --verbose` and read the `system/init` event, whose `plugins` list each loaded plugin (`name`, `path`) and whose `plugin_errors` (`plugin`, `type`, `message`, `path`) and `mcp_server_errors` must be empty.
- `CLAUDE_CODE_SYNC_PLUGIN_INSTALL=1` makes the run wait for marketplace installs and emit `system/plugin_install` events. `--max-budget-usd` caps a print-mode run's spend, and `--include-hook-events` adds hook lifecycle events to `stream-json`.
- `/plugin` doesn't exist in `-p`; `claude plugin` commands do.

## Surfaces other than the terminal

- Claude (web and desktop): zip the plugin (the folder as one entry, or its contents at the root), upload it under **Customize** > **Plugins** > **Add** > **Upload plugin**, ask "which skills do you have from plugins", connect a bundled connector on the Connectors tab, and run a Cowork task to exercise agents. Skills and commands run everywhere; agents and hooks in Cowork and Claude Code; local MCP servers only in Claude Code and local Cowork; LSP servers, output styles, themes and `settings` only in Claude Code; a top-level `bin/` blocks the install. Limits there: 25 marketplaces, 5,000 files, 200 MB.
- Cloud sessions: the repository's own `.claude/` skills, agents, commands, rules, hooks and `.mcp.json` load; user-scope plugins and `~/.claude` don't; a marketplace the repository declares in `extraKnownMarketplaces` isn't added, so its plugins don't load from it; plugins turned on for the user's claude.ai account arrive as `<name>@synced`.
- Agent SDK: plugins load only as `plugins: [{ type: "local", path }]`, relative to `cwd` and without `~`; a missing path is skipped. Check the `init` message's `plugins`, `skills`, `slash_commands` and `plugin_errors`.

## Release checks

- `claude plugin tag <dir> --dry-run` prints the plan: the name, the version and the file it came from, the matching marketplace entry, the tag `<name>--v<version>` and the git commands. Tagging itself validates the plugin, checks that the manifest and the entry agree on the version, and refuses a dirty tree or an existing tag.
- `engines["claude-code"]` keeps a plugin from installing, updating or loading outside its range, and install and update pick the newest version that fits. A bad range fails validation with `Must be a version range such as ">=2.1.0"`. Claude Code from v2.0.15 to v2.1.75 rejects the field as `Unrecognized key`, so leave it out to keep those versions working.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [In-place and copied plugins](https://code.claude.com/docs/en/plugins/loading#in-place-and-copied-plugins) when it matters which copy a test loads. It gives every source and how it loads.
- Read [Test against a clean configuration](https://code.claude.com/docs/en/debug-your-config#test-against-a-clean-configuration) when a result may come from your own setup. It gives the clean-config commands.
- Read [Test mods](https://code.claude.com/docs/en/plugins/mods/test) when you write or fix a mod test. It gives the kit, stubs and drawing tests.
- Read [Fail CI when a plugin or MCP server doesn't load](https://code.claude.com/docs/en/headless#fail-ci-when-a-plugin-or-mcp-server-doesn%E2%80%99t-load) when you write the CI gate. It gives the `init` fields to check.
- Read [Platform support](https://claude.com/docs/plugins/platform-support) when the plugin targets Claude or Cowork. It gives each component's support per surface.
- Read [Plugins in the Agent SDK](https://code.claude.com/docs/en/agent-sdk/plugins) when an application embeds the plugin. It gives the `plugins` option and reloads.

## Exit

The plugin installs from a git-hosted source into a throwaway configuration with no `errors`, its mod tests pass, and the CI gate reads `plugin_errors`. Return to the step in `SKILL.md` that sent you here.
