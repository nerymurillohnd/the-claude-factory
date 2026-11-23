# Validate and load a plugin

What `claude plugin validate` checks and what it never reads, and how to load a plugin from its folder and check what loaded, without a paid run.

## Contents

- [Gotchas](#gotchas)
- [What validate checks](#what-validate-checks)
- [What validate never reads](#what-validate-never-reads)
- [Load the plugin from its folder](#load-the-plugin-from-its-folder)
- [Check what loaded](#check-what-loaded)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- Validation checks files and schema, never behavior: a clean run proves the plugin parses, not that its skills trigger or its hooks act.
- `--strict` turns warnings into exit 1. Top-level unknown fields and a missing frontmatter block fail only with it; an unknown key inside `userConfig`, a `channels` entry, an `lspServers` config or a `monitors` entry, YAML that doesn't parse, a missing or escaping path, a reserved name and a bad `engines` range always fail.
- Validate again after every round of fixes: a warning can hide another. In a run on the installed CLI (observed, not documented), a hook under a misspelled event warned `unknown hook event; entry ignored at runtime`, and the warning that the same hook leaves its plugin-root placeholder unquoted appeared only once the event name was fixed.
- A marketplace run doesn't read the component files of the plugins it lists: validate each plugin folder too.
- `claude plugin details` listed an invalid `.lsp.json` server in a probe (observed, not documented): never take its listing as proof that a component is valid.
- A plugin loaded with `--plugin-dir` replaces an installed plugin of the same name in silence; only the debug log records `Plugin "<name>" from --plugin-dir overrides installed version`.

## What validate checks

- The manifest, and the frontmatter of every skill, agent and command file, `hooks/hooks.json` and `.mcp.json`. For MCP it errors on an entry the loader would drop, an undeclared `user_config` reference and an invalid remote URL, and warns on `http://` or `ws://` to a host that isn't loopback and on headers that look like literal credentials.
- Unsafe paths and links in the plugin's folder, a mod's TypeScript hooks module (its findings are warnings, so `--strict` fails on them) and the one accepted form of a mod's `engine.create` hook.
- From a folder, it reads `marketplace.json` first, else `plugin.json`, else the component folders it finds by name (`skills`, `agents`, `commands`, `.claude`). With both manifests it validates the marketplace and the plugin.
- A symlinked `skills`, `agents` or `commands` folder under the root warns that nothing was read; a linked entry inside one is skipped with a count; a named folder that is itself a symlink is an error.
- A marketplace run checks JSON, required fields, names, `..` in a source, unknown fields (as warnings), each entry's `plugin.json` and version mismatches. A reserved official name, a relative source folder that doesn't exist and a wrong remote `repo` or `path` surface only when the marketplace is added or the plugin installed.
- Runs on the installed CLI print a "Plugin directory checks" block, which the docs pages don't describe: in it a missing README or LICENSE blocks a directory submission and a missing icon warns (observed). `--help` documents that `--profile directory` makes such checks change the exit code, and with `--strict` their warnings too.
- The README advice block never changes the verdict or the exit code, even with `--strict`.
- Exit codes: 0 passes, with or without warnings; 1 fails, or a warning under `--strict`; 2 is a validator error, with empty stdout.

## What validate never reads

Check each by hand:

- a `SKILL.md` at the plugin root;
- a `skills/` folder placed inside `.claude-plugin/`, which the loader never scans; the docs don't say whether validate reports it;
- `.lsp.json`;
- a `CLAUDE.md` at the plugin root, which only warns that it isn't loaded as project context;
- files a script reads outside the plugin, such as a parent-folder `require`, which work in place and break in the installed copy;
- hook matchers and what each hook script does;
- `disable-model-invocation: true` left on a skill Claude should invoke;
- `${user_config.*}` in a monitor, which never receives it, and a top-level `bin/`, which blocks the install in Claude and Cowork.

## Load the plugin from its folder

- Develop against the folder, never an installed copy: `claude --plugin-dir ./my-plugin`, repeatable and one path per flag; it takes a folder or a `.zip`.
- A folder with no `.claude-plugin/` and no components of its own loads each immediate subfolder that has a manifest and no leading `.`. At a marketplace root with no `plugin.json`, the immediate subfolders still load, but plugins two levels down, such as under `plugins/`, don't, and no error says so: pass `--plugin-dir ./plugins` instead.
- `--plugin-url <zip URL>` fetches a `.zip` at startup; a failed fetch starts without it and records an Errors tab entry. `CLAUDE_CODE_PLUGIN_DIRS` takes absolute or `~` paths, separated by `:` on macOS and Linux or `;` on Windows; relative paths are skipped.
- A plugin loaded this way is `<name>@inline` with scope `session`, loaded in place. Turn it off for one test with `"<name>@inline": false`.
- After each edit, run `/reload-plugins` in the session. It prints `Reloaded: N plugins · N skills · N agents · N hooks · …`, plus `N errors during load. Run /plugin for details.` on errors. A reload that adds or removes a plugin MCP server or the LSP tool needs `/reload-plugins --force`. In `-p`, the desktop app and the Agent SDK it runs only when typed into the session, and it never connects or disconnects plugin MCP servers there.
- Test a plugin with its dependency by loading both: `claude --plugin-dir ./my-dependency --plugin-dir ./my-plugin`. The version constraint isn't checked against a local copy, and a disabled or absent local copy disables the dependent.

## Check what loaded

Without a session, which costs nothing:

```bash
claude --plugin-dir ./my-plugin plugin list --json
claude --plugin-dir ./my-plugin plugin details my-plugin
```

- `list --json`: read `errors`, `notes`, `scope` and `enabled` for the plugin's row.
- `details`: the component inventory and the projected always-on token cost; every skill, agent, hook and server should be listed.

In a session, per component:

| Component | Check |
| :-- | :-- |
| Skill | run `/<plugin>:<skill>`; ask "What skills are available?"; `/skills` marks a skill with `disable-model-invocation: true` as user-only. Malformed frontmatter still loads the body, but Claude can't match the skill, and `--debug` shows the parse error. A root `SKILL.md` needs `name`, or an install names it after its cache folder |
| Agent | invoke `@agent-<plugin>:<name>`; a subfolder gives `<plugin>:<sub>:<name>`. Unparseable frontmatter still loads the agent, named after its file, with the description `Agent from <plugin> plugin` |
| Hook | `/hooks` lists it; it fires from load, not from skill use. Exercise its script without a session: `echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' \| ./my-hook.sh; echo $?`. A `PostToolUse` hook that exits 0 shows nothing: confirm it in the debug log, which records `Hooks: <Event>:<match> [<command>] … finished with status 0` |
| MCP server | `/mcp` lists it under "Plugin MCPs" as `plugin:<plugin>:<server>`, its tools as `mcp__plugin_<plugin>_<server>__<tool>`; `claude --debug=mcp` shows why it didn't start. An entry that fails the schema appears only in the debug log, not the Errors tab |
| LSP server | its binary comes from `PATH`; the Errors tab shows `Executable not found in $PATH`; one invalid entry skips the whole `.lsp.json` with `Invalid LSP server config for ".lsp.json"`; its stdout must carry the protocol only |
| Output style, theme | `/output-style` lists an output style as `<plugin>:<name>`; `/theme` lists a theme under its file's `name` |
| Channel | needs `--dangerously-load-development-channels plugin:<plugin>@<marketplace>`, and the server named in `--channels` |
| Monitor | doesn't start under `-p`, and keeps running after the plugin is disabled |
| `bin/` | on the Bash tool's `PATH` after the user's own entries |
| `userConfig` | `--plugin-dir` and `claude plugin install` never show the dialog: set values with `/plugin configure <name>@<marketplace>`, `claude plugin configure <name>@<marketplace> --values-stdin` or `install --config KEY=VALUE` |
| Mod | `claude plugin test <dir>` runs every `*.test.ts` and `*.test.tsx` under the folder, with no session, and exits 1 when a test fails |

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Validate a directory](https://code.claude.com/docs/en/plugins/cli-reference#validate-a-directory) when a validate result is in question. It gives what each target reads, the symlink rules and the exit codes.
- Read [Test and debug](https://code.claude.com/docs/en/plugins/create#test-and-debug) when you set up the local loop. It gives `--plugin-dir`, folders of plugins and `--plugin-url`.
- Read [Plugin components reference](https://code.claude.com/docs/en/plugins/components) when a component's check is not in the table. It gives each component's loading rules and names.
- Read [Unrecognized fields](https://code.claude.com/docs/en/plugins/manifest-reference#unrecognized-fields) when a field fails only sometimes. It gives which objects are strict.

## Exit

Validation passes with `--strict` on every plugin folder and on the marketplace, each item validate never reads is checked, and every component shows as loaded. Return to the step in `SKILL.md` that sent you here.
