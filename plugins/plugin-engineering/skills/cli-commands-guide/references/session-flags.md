# Flags that load a plugin for one session

`--plugin-dir` and `--plugin-url` load a plugin for one session only, without installing it. Facts come from the CLI reference page, the plugin loading reference (`https://code.claude.com/docs/en/plugins/loading.md`), the troubleshooting page, `claude --help` on 2.1.319 (checked again on 2.1.321), runs on 2.1.319 and the changelog through 2.1.321. Under each heading that has an official section, `Official page:` links it: read it when a fact here looks outdated.

## Contents

- The two flags
- How a session-only plugin shows up
- Name conflicts and precedence
- Turning a session-only plugin off
- Where the files load from
- Managed settings and the Agent SDK
- Mistakes these flags invite

## The two flags

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#flags-that-load-a-plugin-for-one-session>

Both are repeatable. Plugin authors use them to test a plugin before publishing.

- `--plugin-dir <path>`: load a plugin from a directory or a `.zip` archive of one. A folder of plugins loads each child folder that holds a `.claude-plugin/plugin.json`. Each flag takes one path. Example: `claude --plugin-dir ./my-plugin --plugin-dir ./other.zip`.
- `--plugin-url <url>`: fetch a plugin `.zip` archive from a URL. Repeat the flag, or pass several URLs space-separated in one quoted value. Example: `claude --plugin-url "https://example.com/a.zip https://example.com/b.zip"`. The space-separated form is from the docs page; the `claude --help` of 2.1.321 shows only the repeated flag.
- `CLAUDE_CODE_PLUGIN_DIRS`: the environment variable that names folders to load the same way; its plugins are session-only too.

## How a session-only plugin shows up

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#flags-that-load-a-plugin-for-one-session>

- Its id is `<name>@inline`, where `<name>` is the `name` in the plugin's manifest.
- `claude plugin list` shows it only when the same flag precedes the subcommand: `claude --plugin-dir ./my-plugin plugin list`. It appears under `Session-only plugins (--plugin-dir / --plugin-url):` (verified on 2.1.319), and `--json` reports `"scope": "session"` with `id` `<name>@inline`.
- `claude plugin details <name>` and `claude plugin eval` need the plugin loaded: pass the flag before the subcommand in the same command. After the subcommand, `plugin details` rejects it with `error: unknown option '--plugin-dir'` (verified on 2.1.319).
- Enabled for the session unless the manifest sets `defaultEnabled: false` or a settings file sets `"<name>@inline": false`.

## Name conflicts and precedence

Official page: <https://code.claude.com/docs/en/plugins/loading#name-conflicts>

- A session-only plugin that shares a name with an installed plugin loads instead of it for that session.
  - An installed marketplace plugin is replaced silently. `claude plugin list` still shows the marketplace row as enabled, because that row reflects your settings. Only the debug log (start with `--debug`, written under `~/.claude/debug/`) records `Plugin "<name>" from --plugin-dir overrides installed version`.
  - A skills-directory plugin is replaced with an Errors-tab row: `Not loaded — the name "<name>" is already taken by a session-only plugin (--plugin-dir / --plugin-url), which takes precedence`.
- The comparison uses manifest names: a `--plugin-dir` plugin named `hello-plugin` replaces `hello@example-marketplace` when that plugin's manifest also says `"name": "hello-plugin"`.
- Managed settings win: a plugin whose id appears in managed `enabledPlugins` (as `true` or `false`) locks the name, and a matching `--plugin-dir` copy isn't loaded: `--plugin-dir copy of "<name>" ignored: plugin is locked by managed settings`.

## Turning a session-only plugin off

Official page: <https://code.claude.com/docs/en/plugins/loading#keep-a-session-only-plugin-from-loading>

- `claude plugin disable <name>@inline`, or set `"enabledPlugins": {"<name>@inline": false}` in any settings file. A disabled session-only plugin doesn't shadow, so the installed copy loads instead. Useful when a parent process passes the flag for you.

## Where the files load from

- A `--plugin-dir` directory loads in place and is never copied. Edits on disk apply after `/reload-plugins`.
- A `--plugin-url` archive or a `--plugin-dir` `.zip` is extracted into a session temp directory first.

## Managed settings and the Agent SDK

- An administrator can reject both flags, and folders named in `CLAUDE_CODE_PLUGIN_DIRS`, with the managed `disableSideloadFlags` setting. Claude Code then prints that the flag is disabled by your organization's managed settings and exits `1` without starting.
- From the Agent SDK, the `plugins` option is the equivalent of `--plugin-dir`.

## Mistakes these flags invite

- Pointing `--plugin-dir` at a marketplace root: Claude Code doesn't read `marketplace.json`, so the plugins under `plugins/` don't load, with no error. Point it at the plugin directory itself: `claude --plugin-dir ./my-marketplace/plugins/my-plugin`. Before v2.1.281, a marketplace root loaded as one empty plugin named after the directory.
- An MCP server that starts with `--plugin-dir` but fails once installed: the installed copy runs from the cache, so a path outside the plugin directory points at nothing. Keep every file the plugin needs inside its directory.
- Changelog fixes worth knowing: 2.1.321 fixed `--plugin-dir .` and `--plugin-dir ./builtin` writing generated type files for Claude Code's built-in plugins into a `builtin` folder; 2.1.311 fixed a `--plugin-dir` folder of plugins loading as one plugin when an empty `.mcp.json` was at its top; 2.1.299 stopped sandboxed shell commands from writing into a `--plugin-dir` folder, whose code Claude Code reloads and runs outside the sandbox; 2.1.314 fixed model switching being refused under managed plugin settings when a `--plugin-dir` or `--plugin-url` plugin had a broken manifest or failed to download.
