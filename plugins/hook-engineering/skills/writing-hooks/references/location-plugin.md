# Plugin hooks

Read this in step 5 when the hook ships in a plugin: `hooks/hooks.json`, or the `hooks` key of `.claude-plugin/plugin.json`.

## Role

You write hooks that run on other people's machines, in projects you will never see, from a copy of the plugin you don't control.

## Knowledge

- Scope: every session that loads the plugin, in every project of every user who enables it.
- Registration: when the session loads the plugin, not when one of its skills or commands runs. A hook fires on its events from then on; narrow it with `matcher` or `if`.
- Files: `hooks/hooks.json` at the plugin root wraps the event map in a top-level `"hooks"` key, with an optional top-level `description`. The `hooks` key of `plugin.json` takes a path to such a file, an inline event map with no wrapper, or an array of both. Both sources load together.
- Surfaces: Claude Code and Cowork load plugin hooks; claude.ai chat ignores them. Any program a hook calls must exist where it runs.
- Placeholders: `${CLAUDE_PLUGIN_ROOT}` is the installed version's folder and changes on every update, so never write state there. `${CLAUDE_PLUGIN_DATA}` survives updates, for dependencies, caches and state. `${CLAUDE_PROJECT_DIR}` is the user's project root. All three are exported to the hook's process, with `CLAUDE_PLUGIN_OPTION_<KEY>` for each user configuration value.
- User configuration: `${user_config.<key>}` is substituted in exec form only; a shell-form hook that references it fails instead of running. In shell form, read `$CLAUDE_PLUGIN_OPTION_<KEY>` instead.
- Plugin MCP tools: a tool from a server the plugin declares is named `mcp__plugin_<plugin>_<server>__<tool>`. An `mcp_tool` handler names that server `plugin:<plugin>:<server>`.
- Node dependencies: a marketplace install installs them into the cached copy only when the plugin root has a `package.json` and an npm (`package-lock.json`, `npm-shrinkwrap.json`) or Bun (`bun.lock`) lockfile. Every dependency must be a registry package pinned to an exact version; no lifecycle scripts run, npm `overrides` cancel the install, and it stops after 60 seconds. A plugin loaded in place from a local-path marketplace gets no install. Anything else installs from a `SessionStart` hook into `${CLAUDE_PLUGIN_DATA}`.
- Policy: managed `allowManagedHooksOnly` blocks a plugin's hooks unless managed settings force-enable that plugin. `disableAllHooks` turns them off with every other non-managed hook.
- Docs: `### Hooks` in `plugins/components`, `### hooks` and `## Environment variables` in `plugins/manifest-reference`, `### Node.js package dependencies` in `plugins/loading`, and `https://claude.com/docs/plugins/platform-support` for surfaces.

## Gotchas

- A plugin agent ignores `hooks` in its frontmatter, as it ignores `mcpServers` and `permissionMode`: hook a plugin's agents through `SubagentStart` and `SubagentStop` here (`references/location-subagent-events.md`).
- A matcher on the server name alone never matches a plugin's MCP tool.
- A hook file that holds only the event map, without the `"hooks"` wrapper, fails to load; an inline map in `plugin.json` is the reverse.
- When another enabled plugin has the same name, only one of the two registers its `hooks/hooks.json` hooks.
- A hook that runs in every session with no gate to the projects it is for (a `UserPromptSubmit`, `PreToolUse` or `PostToolUse` hook with no matcher, `if` or early exit) fails the policy review of Anthropic's official marketplace, as does a call to a host the plugin's description and README don't disclose.
- The default Git for Windows install was reported not to put `bash.exe` on the PATH (not verified): exec form with `"command": "bash"` may not start there.

## Rules

- Gate every hook to what the plugin is for: a narrow `matcher`, an `if` rule, or an early `exit 0` when the project is not one the plugin serves.
- Ship each script inside the plugin, under `hooks/` or `scripts/`, and reference it through `${CLAUDE_PLUGIN_ROOT}`: users receive only the plugin's folder.
- Keep state, caches and installed dependencies in `${CLAUDE_PLUGIN_DATA}`.
- Use exec form for a hook that reads `${user_config.*}`; otherwise choose the form as the gotcha in `SKILL.md` says.
- State in the plugin's README every program a hook needs (`jq`, `node`, `python3`) and the platforms it runs on.
- Run `claude plugin validate <plugin-dir>` after each change: it warns about an unquoted placeholder in a shell-form hook.

## Structure

- File: `hooks/hooks.json` at the plugin root, or the `hooks` key of `.claude-plugin/plugin.json`.
- Template: `assets/plugin-hooks.json`, shell form. For a Node script, put `assets/node-exec-handler.json` in its inner `hooks` array.
