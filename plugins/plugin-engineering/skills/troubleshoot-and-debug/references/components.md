# Components that load but misbehave

Why a plugin's agent lacks a tool or ignores a field, why a hook or MCP tool never matches, and why a mod does nothing, when the plugin itself loaded.

## Contents

- [Gotchas](#gotchas)
- [Plugin agents](#plugin-agents)
- [Hooks](#hooks)
- [MCP and LSP servers](#mcp-and-lsp-servers)
- [Mods](#mods)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- A plugin's agent ignores `permissionMode`, `hooks`, `mcpServers` and `initialPrompt` with no error: declare hooks in `hooks/hooks.json` and MCP servers in the plugin's MCP configuration.
- An MCP entry in an agent's `tools` matches only the server's name as the session spells it; any other spelling matches none of that server's tools, and when no entry in `tools` resolves, the launch is usually refused with `would be spawned with zero tools`.
- A hook's plugin-root and data placeholders are exported to the hook's process, never to commands Claude runs through the Bash tool.
- A mod hook that throws, times out or returns the wrong shape is skipped, and the action goes on as if the mod weren't there, unless the hook has a `.catch` handler.

## Plugin agents

- A plugin agent reads only `name`, `description`, `model`, `effort`, `maxTurns`, `autoCompactWindow`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `omitClaudeMd`, `isolation` (only `"worktree"` is valid), `color` and the `cacheTtl` key of `experimental`. Other fields are ignored silently; search the debug log for `does not recognize or apply` to find a misspelled one.
- A `name` over 256 characters, or none, names the agent after its file; unparseable frontmatter still loads it, every field ignored, with the description `Agent from <plugin> plugin`. `agents/review/security.md` becomes `<plugin>:review:security`.
- A background subagent keeps every MCP tool, `SubagentHandback` when it reports through it, and these built-in tools: `Read`, `Grep`, `Glob`, `LSP`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, `Artifact`, `ListPlugins`, `ListSkills`, `SearchPlugins` and `SearchSkills`. Claude Code removes most other built-in tools, even when `tools` lists them, with no error unless `tools` then resolves to nothing; to keep one, let the agent run in the foreground and drop `background: true`.
- No subagent gets `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ExitPlanMode` (unless `permissionMode: plan`), `propose_skills`, `ScheduleWakeup`, `WaitForMcpServers`, `Workflow`, or `Agent` past the depth limit.
- When no entry in `tools` resolves, Claude Code usually refuses to launch the agent: `Agent '<name>' would be spawned with zero tools — refusing.`, naming each entry as unrecognized, not available to subagents, or matching no tools in this session. Omitting `tools` never triggers it, and an empty `tools` list or a `disallowedTools` that removes every entry launches the agent with no tools.
- An MCP entry in `tools` is `mcp__plugin_<plugin>_<server>__*` for the plugin's own server, `mcp__claude_ai_<server>__*` for a claude.ai connector, and `mcp__<name>__*` for a server the user added. A server name that holds `__` needs the whole name, as `mcp__reports__v2__*`. To reach whatever docs server the user has, omit `tools` and restrict with `disallowedTools`.
- A `disallowedTools` entry with a specifier removes the whole tool.
- `isolation: worktree` branches from the repository's default branch, not from the session's `HEAD`, unless the user's settings set `worktree.baseRef` to `"head"`: an agent that must see the current branch or its unpushed commits gets neither.
- Agent descriptions over 15,000 tokens in all trigger `Agent descriptions are over the 15.0k-token limit` at startup; every agent still loads.

## Hooks

- Hooks register when the plugin loads, not when one of its skills runs, and they fire inside subagents too.
- Event names are case-sensitive, a `matcher` is a string (an array is invalid, and under `PreToolUse` or `PermissionRequest` it blocks the file's other hooks), and tool names are spelled as the tools are.
- The same handler in several settings files runs once, but a plugin's copy of it stays separate, and every matching hook runs in parallel.
- The hook process receives the plugin root, the plugin data folder, the project folder and `CLAUDE_PLUGIN_OPTION_<KEY>` for each option; a monitor receives none of them.
- Quote the plugin-root placeholder in a shell-form command, or use exec form: an unquoted one breaks on a path with a space, and validate warns about it unless `shell` is `"powershell"`.
- On Windows, a shell-form hook that runs through Git Bash receives the plugin root with forward slashes; exec form and `"shell": "powershell"` keep backslashes, and PowerShell is the default where Git Bash isn't installed.
- Managed `allowManagedHooksOnly` blocks every plugin hook except those of plugins that managed `enabledPlugins` force-enables; `disableAllHooks` turns them all off. Cloud sessions never read the user's local `~/.claude/settings.json` hooks.
- In the debug log, a hook that ran shows as `Hooks: <Event>:<match> [<command>] … finished with status <n> (<ms>)`, or as `timed out after <N>ms`, `cancelled`, `moved to the background` or `failed to start`.

## MCP and LSP servers

- A plugin's MCP tool is `mcp__plugin_<plugin>_<server>__<tool>`, with characters outside `A-Za-z0-9_-` turned into `_`; `/mcp` lists the server under "Plugin MCPs" as `plugin:<plugin>:<server>`.
- A server connected with zero tools: run `claude --debug=mcp` and read its stderr in the log.
- LSP servers run over stdio from a binary on `PATH`; `requestTimeout` defaults to 60000 ms, and `restartOnCrash` and `maxRestarts` control restarts.

## Mods

A message that names a hooks module means the plugin is a mod.

- Where to read why: a dim transcript line in a hot-reloading `--plugin-dir` session, the debug log for an installed mod, stderr for `claude -p --plugin-dir`. The debug log records `hooks module <name>@inline loaded (…); events: …` or `hooks module <name> not loaded: <reason>`.
- `claude plugin test` in a folder tells whether mods can load there at all: `no hooks module to load`, `hooks modules are turned off here`, or a rollout switch served or saved off.
- A refusal after `hooks module <name> not loaded:` names `disableAllHooks in managed settings`, `only managed plugins and built-in plugins run`, `--bare`, a rollout switch, or `another plugin of that name loads first`.
- `claude plugin validate` passes with no `hooks` line when `hooks/hooks.json` lacks `modules`: add `"modules": ["./register.js"]`.
- `hooks module did not load:` names its reason, such as options that don't fit the plugin's `userConfig`, or nesting limits.
- A failed hook prints one line naming the mod, the event and the reason, such as `my-mod: tool.call hook skipped: threw Error: boom`. Failing before it called `next`, it is skipped and the next handler runs instead; failing after `next` resolved, that result stands. A guard must fail closed with a `.catch` handler on its registration that answers in its place, testing `next.called`: return `{ deny: … }` for `tool.call` and `config.set`, `{ drop: … }` for `prompt.submit`. At `tool.check` and `plugin.register` a refusal after `next` still holds, so return it without the test. The handler has a shorter time limit of its own, and a handler that fails too leaves the hook skipped.
- A built-in guard, `sec-default@builtin` (listed as `cc-plugin-sec-default`), loads ahead of every user-installed mod when the machine has managed settings or a `managed-mcp.json`, or the session signs in with a Team or Enterprise login. Where it loads, a user's mod hooks on `classic.<Event>`, `prompt.compose`, `prompt.section`, `prompt.context`, `prompt.attachment`, `skill.prompt`, `attribution.text`, `telemetry.log`, `session.compact`, `settings.read` and some `session.append` rows never run, and `/plugin` notes `Its hooks on <events> do not run here: where an organization manages Claude Code, these events pass over the plugins you install`. Only an administrator can change it, by installing the mod as the organization's own or removing the guard from `prependPlugins`.
- `hook skipped:`, `no command.run hook answered it`, `it crashed the hooks worker`, `reload failed`, and `mods that run in the hooks worker are off for this session: it crashed 3 times`: fix the cause, then `/reload-plugins`.
- No mod loads in a new folder until the trust prompt is answered; `claude --safe-mode` turns every installed mod off, to show whether a mod causes a problem.
- `CLAUDE_CODE_PLUGIN_DIR_WATCH=1` reloads skills-directory mods in any multi-prompt session; `--plugin-dir` mods hot-reload only in an interactive terminal.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Agents](https://code.claude.com/docs/en/plugins/components#agents) when a plugin agent's field or name is in question. It gives the fields a plugin agent reads.
- Read [Available tools](https://code.claude.com/docs/en/sub-agents#available-tools) when a subagent lacks a tool. It gives each filter that removes tools.
- Read [Debug hooks](https://code.claude.com/docs/en/hooks#debug-hooks) when a hook's run is in question. It gives the log lines and levels.
- Read [Troubleshoot a mod](https://code.claude.com/docs/en/plugins/mods/troubleshoot) when a mod does nothing. It gives every refusal and where it appears.
- Read [Handle a hook that fails](https://code.claude.com/docs/en/plugins/mods/events#handle-a-hook-that-fails) when a mod guard must fail closed. It gives the `.catch` pattern for each event.
- Read [Know what happens by default](https://code.claude.com/docs/en/plugins/mods/admin#know-what-happens-by-default) when a mod behaves differently on a managed machine. It gives the built-in guard and the hooks it passes over.

## Exit

The component's behavior is explained by a rule here or by the page. Return to step 4 of the diagnosis in `SKILL.md`.
