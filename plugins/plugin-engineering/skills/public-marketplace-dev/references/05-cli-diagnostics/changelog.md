> ## Documentation Index
>
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.
>
> Source: https://code.claude.com/docs/en/changelog
> Pruned copy (2026-11-07): this file keeps only the passages that apply to developing and distributing Claude Code plugins through a marketplace hosted in a public GitHub repository and served to third parties. Removed passages are listed in REMOVALS.md.
>
> Sections in this file:
>
> - (no sections remain beyond the title)

# Claude Code changelog

> Release notes for Claude Code, including new features, improvements, and bug fixes by version.

This page is generated from the [CHANGELOG.md on GitHub](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md). Longer releases are grouped by type of change, with long lists of improvements and bug fixes collapsed.

Run `claude --version` to check your installed version.

**2.1.319**

November 6, 2026

**Added**

* Added support for MCP tasks in the terminal: when an MCP server runs a tool call as a task, Claude Code moves it to the background right away and tells Claude the result when it finishes

**Changed**

* Changed auto mode so that a project's settings files or a plugin can no longer switch its server-side check back on once you have switched it off outside the project
* Changed PostToolUse hooks to run, with up to 10 seconds to finish, on tool calls that finish after a new message interrupts the turn

**16 improvements**

* \[VSCode] Improved the confirmation for removing a plugin marketplace: it now checks which of its plugins are installed at that moment

**90 bug fixes**

* Fixed MCP servers on the older handshake failing to connect, or returning empty results, because Claude Code declared an extension that it only uses with newer servers
* Fixed `claude plugin eval` warnings suggesting `max: 0` for a tool that must not be called, which could never pass
* Fixed background plugin auto-update not installing a dependency added by the updated plugin version
* Fixed a mod's hot reload in `.claude/skills` missing a file that was deleted just after it appeared, and missing its return
* Fixed `${CLAUDE_PLUGIN_ROOT}` not being substituted in a plugin-provided `subagentStatusLine` command, which can now reference the plugin's own scripts
* Fixed `claude plugin update` and `/plugin` "Update now" not installing dependencies added by the new plugin version

**2.1.318**

November 4, 2026

**Added**

* Added an `effort` option to a mod's `$.model.fork`, so a quick side job can run at `low` whatever effort the session uses; the result reports the effort sent

**Changed**

* Changed what a mod attaches at `prompt.submit` to stay in the user's turn rather than go out as a system message

**47 bug fixes**

* Fixed `claude plugin` commands exiting before a slow token refresh was saved, which could sign you out on the next run
* Fixed `claude plugin validate` passing a custom-named marketplace file that `claude plugin marketplace add` rejects
* Fixed stdio MCP servers that exit on the version probe being re-probed on every start; a server that dies in under 3s for its own reason is also pinned to the legacy handshake for 7 days
* Fixed `claude -p` and Agent SDK sessions reporting success when an API error cut off a reply while a mod hooked `turn.step`
* Fixed a mod's `turn.step` hook making a stopped reply finish as a success in headless runs

**2.1.317**

November 3, 2026

**Changed**

* Changed exit to skip the "Background work is running" prompt for plugin monitors

**62 bug fixes**

* Fixed high memory use and slow startup in headless sessions with many plugins that register commands

**2.1.316**

October 31, 2026

**34 bug fixes**

* Fixed PowerShell hooks not blocking on exit code 2 when the command begins with a type cast, `param`, `using` or an attribute
* Fixed plugin MCP `headersHelper` scripts receiving a corrupted `CLAUDE_PLUGIN_ROOT` and server URL when a credential-named environment variable was set to a switch value such as `1`

**2.1.314**

October 30, 2026

**Changed**

* Changed hook `if` conditions such as `Monitor(tail *)` to match the Monitor tool's shell commands as `Bash(tail *)` matches Bash's
**81 bug fixes**

* Fixed model switching being refused on machines with managed plugin settings when one of your own `--plugin-dir` or `--plugin-url` plugins had a broken manifest or failed to download
* Fixed a PreCompact hook with very large output making compaction fail or repeat; each hook's output is now cut at 10,000 characters
* Fixed hooks matching Bash not running on shell commands started by the Monitor tool; such hooks can block or ask, but not approve or rewrite those commands

**2.1.312**

October 27, 2026

**Changed**

* Changed prompt and agent hooks to run at most 24 at a time per session, sub-agents included, plus at most 12 that have waited longer than their event's timeout; a `timeout` under 1 second now counts as 1 second
* Changed a subagent's `autoCompactWindow` to lower the window set by `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, where it had no effect before; it still never raises that window

**2.1.311**

October 26, 2026

**Changed**

* Changed `DISABLE_COMPACT` in settings files and in a mod's `$.env.set` so they can only turn compaction off, not back on
**56 bug fixes**

* Fixed `SubagentStop` hooks running about twice a minute for each running subagent instead of once when it finishes
* Fixed a `--plugin-dir` folder of plugins loading as one plugin when an empty `.mcp.json` was at its top

**2.1.310**

October 23, 2026

**Added**

* Added the Monitor tool and plugin monitors on Bedrock, Vertex, and Foundry, and when telemetry or nonessential traffic is disabled; long foreground sleeps are now blocked there too

**14 bug fixes**

* Windows: Fixed PreToolUse and PermissionRequest hooks letting a tool call through when Git Bash is missing and the hook's command is only quoted strings, such as a quoted path

**2.1.309**

October 22, 2026

**8 improvements**

* Improved the error when a hooks module is nested too deep to load: it now names the file instead of showing a bare stack-overflow message

**62 bug fixes**

* Fixed hooks that run in PowerShell not blocking when the hook's program exits with code 2, and on Windows `PreToolUse` and `PermissionRequest` hooks with `"shell": "powershell"` failing open when Git for Windows isn't installed
* Fixed a mod's `turn.step` hook that names a model by alias, such as `haiku`, failing every request with a model error: the alias now resolves to its model
**2.1.305**

October 20, 2026

**Changed**

* Changed a mod's docked pane to stay within 45% of the terminal's width, including a width kept from a wider terminal

**2.1.304**

October 19, 2026

**Added**

* Added a transcript line when a plugin that runs first skips one of your mod's hooks, naming the event and the plugin
* Added `decider: "person"` to a mod's `tool.check` answer: only the permission dialog or a host's callback can approve the ask, and it is refused with the mod's reason where nobody can be asked
* Added `e.isReadOnly` to a mod's `tool.check` event, set when the tool call is read-only

**Changed**

* Changed skill hooks: the skills of one source (a repo, your own folder, or a plugin) can register at most 1,024 hooks and 16,384 matcher characters per session
* Changed skills under a policy that allows hooks from plugins only: a skill used in the main conversation whose hooks are kept out no longer gets its `allowed-tools`
* Removed the notes from `claude plugin validate` that predicted where a mod's hooks would run
**43 bug fixes**

* Fixed a plugin keeping a headless run going past `--max-turns`, Stop, or ended input by spawning subagents or re-running a finished one
* Fixed a failed mod reload removing the tools and commands of the version that stays loaded, and its messages being wrong or silent about whether the previous version is still loaded
* Fixed a click on a mod's button being lost when buttons with the same label and no `key` were redrawn unchanged
* Fixed a skill's `once` hook also removing another skill's identical hook after it ran
**2.1.302**

October 16, 2026

**Changed**

* Changed prompt and agent hooks so that at most 12 of one event run at a time; the rest wait their turn

**7 improvements**

* Improved startup time with many plugins enabled: plugin command and agent files now take far fewer file system calls to load, most of all on Windows

**43 bug fixes**

* Fixed `claude plugin` and other subcommands sometimes exiting before a queued settings or config write finished, which could lose the change or leave a `.tmp` file behind
* Fixed plugin marketplaces re-cloning on every refresh, and newly installed git plugins showing version "unknown", when git defaults to the reftable ref format
* Fixed the PowerShell tool not finding commands in a plugin's `bin/` folder, and reporting an error when a search that finds nothing (rg, grep, findstr, git grep) is piped into `Select-Object` or another formatting cmdlet

**2.1.301**

October 15, 2026

**Added**

* Added `rows` to a mod's `Input`: a text field of several lines in the terminal, where Enter submits and Shift+Enter or a backslash before Enter starts a new line

**Changed**

* Changed a mod hook's `.catch` handler to run only when the hook throws or times out; events raised beneath the hook's own calls now skip that hook without asking its `.catch`
* Changed a mod's `$.env.set` to resolve with `{}` once the variable is set or unset, or with `{ deny }` saying why when the write is not made

**Improved**

* Improved mods: in VS Code and the desktop and mobile apps, a tree drawn above the question dialog can now hold Markdown and up to 48 rows; the terminal keeps 12 plain rows

**37 bug fixes**

* Fixed skills and commands with very many or very long argument names stalling for seconds when invoked; only the first 64 names, each up to 64 characters, are now filled in
* Fixed skills, commands and hooks using very large amounts of memory when their arguments fill many placeholders
* Fixed the permission prompt for a plugin or skill hook's `ask` decision not showing which plugin or skill the hook comes from
* Fixed a mod's `$.model.fork` returning `nothing-to-fork` when called before the first response of a new Claude Code process had finished, as in `claude -p` runs and cloud sessions

**2.1.300**

October 14, 2026

**Added**

* Added `virtualText` to a mod's prompt decorations: text drawn in the prompt box that never enters the draft or the submitted prompt
* Added `$.ui.view({ agentId })` for mods: shows an agent's transcript in the main view when you ask, and `$.ui.view({})` goes back
* Added a `dir` prop on a mod's `Text` for right-to-left text: on Windows and in VS Code's terminal its rows read in that direction and sit flush right
* Added support for rewriting a workflow agent's `prompt` and `model` in the `agent.spawn` mod hook, which could only refuse workflow agents before
* Added the `prompt.change` mod hook, raised when the prompt box's text changes without a typed edit: a recalled history entry, a clear, an undo, or a plugin's fill

**Changed**

* Changed hooks: `updatedInput` from PreToolUse and PermissionRequest hooks is now validated like Claude's own input: unknown keys are dropped, and input the tool rejects denies the call

**Improved**

* Improved mod sharing in the built-in `plugin-authoring` skill: Claude scans a mod's files for keys before opening them, and asks before scanning a folder outside the project

**59 bug fixes**

* Fixed plugin `WorktreeCreate` and `WorktreeRemove` hooks not running when Claude Code starts with `--worktree` (not yet with `--tmux`)
* Fixed agent hooks ignoring their `model`: aliases like `haiku` now resolve, a subagent's model no longer overrides it, and an unavailable model falls back to the caller's instead of allowing the action
* Fixed a mod's `prompt.edit` hook not being raised for a newline entered with the `chat:newline` keybinding (Ctrl+J, or a rebound Enter)
* Fixed a conversation failing on every turn with a 400 error when the API rejected an MCP tool's input schema; Claude Code now sends that tool without parameters for the rest of the conversation

**2.1.299**

October 14, 2026

**Added**

* Added `size`, `weight`, `mono` and `tabular` to a mod's `Text` and named spacing steps (`xs` to `xl`) to its `Box`; `bold` is deprecated in favor of `weight`
* Added the skill's frontmatter, source, plugin name and file path to what a mod's `skill.prompt` hook receives
* Added `--disallow-tools` and a `disallowed_tools` case field to `claude plugin eval` to keep specific built-in tools, such as Agent, out of eval runs
* Added a `queue` door to the `session.append` mod hook, so a mod can make the transcript's queue records differ from the prompt as sent
* Added a note in `/plugin` and `claude plugin validate` naming a mod's hooks that are skipped where an organization manages Claude Code

**Changed**

* Changed plugin hooks and workflow scripts to refuse values they hand back that nest deeper than 28,000 levels, with an error naming the limit (workflow scripts allowed 100,000)
* Changed actions a plugin hook can block to be refused, not let through, when the hook cannot be handed them or cannot hand back its answer; a tool that already ran has its result withheld
* Changed skill and command loading: one whose file or folder name has hidden, direction-changing or blank-like characters, `<` or `>` is no longer offered until renamed; such a `name:` is ignored
* Changed `ui.render` trees in `claude plugin test`: each mod's Box or Text root now carries `part: { plugin }` naming the mod, so exact-tree assertions must include it
* Changed `claude plugin test` to fail a call to a mod's served `$` method that has not answered within ten seconds, as a session does
* Changed agent `tools:` lists to take only the named MCP server's tools; list a server whose name contains `__` as `mcp__<whole name>__*`
* Changed `UserPromptSubmit` hooks to run before a skill or custom slash command expands, so a hook that blocks the prompt now also stops its embedded shell commands
* Changed a skill's own front-matter `UserPromptSubmit` hook to first run on the prompt after the one that invokes the skill
* Changed the `turn.start` mod hook to also hear subagents' and teammates' turns, not only the main loop's; tell them apart by `e.agentId` (absent on the main loop)

**16 improvements**

* Improved the plugin-authoring skill's steps for sharing a mod: Claude asks public or private and checks the files before creating a GitHub repository

**131 bug fixes**

* Fixed a mod's `prompt.submit` rewrite being silently dropped, sending the prompt as typed, for some prompts with a pasted image or an image that can't be read
* Fixed a mod hook, with or without a `.catch`, being run again without end when it waits on another mod's noun that does its work outside the call
* Fixed a mod's `tool.describe` or `prompt.section` answer that changed after `$.ui.invalidate` never reaching Claude; the new answer is now sent on the next turn
* Fixed `claude plugin test` pausing a hook's time budget while a served `$` method it had called kept making `$` calls after answering
* Fixed plugin hooks being skipped when they pass a very deeply nested tool input or message on with next()
* Fixed a value a mod's hook passes to `next()`, returns, or sends to a `$` method being refused whole when one of its getters throws a `RangeError`; now only that key is refused
* Fixed a mod's hot reload ignoring a fix saved right after a failed reload; saving a mod file without changing it no longer reloads the mod
* Fixed mods loaded from source files being refused when a hook hands `$` to a function declaration imported from another file of the mod
* Fixed mods' hooks being handed values with `__proto__` keys silently removed, which could skip a `tool.check` guard on a tool call another mod made
* Fixed `/reload-plugins` not loading a plugin installed from another terminal a moment earlier
* Fixed `$.http.fetch` in mods refusing a `304`, `204` or `205` response that declares a `Content-Length` over the 4 MiB body limit
* Fixed `claude plugin eval` passing runs that the API refused: a run that ends on an API error now scores 0 without grading and makes the suite exit 1
* Fixed `$.ui.open` reporting a mod's pane as placed in sessions where no surface draws it, such as Claude Code for VS Code and `claude -p`
* Fixed the `agent.spawn` mod hook not running when a finished subagent or a killed teammate is resumed: the hook's event now carries `resume`, and a mod can refuse it
* Fixed `claude plugin validate` rejecting a mod's `$.state` references when `plugin.json` has no `types` key and the contract is at `./types/index.d.ts`
* Fixed a mod's `dimColor` text looking the same as plain text under the dark ANSI theme and on 16-color terminals
* Fixed plan mode running a write (an MCP tool's, a file's, a shell command's) that a `PreToolUse` hook or a mod's `tool.check` hook allowed
* Windows: Fixed PreToolUse and PermissionRequest hooks that set no shell failing open when Git for Windows isn't installed; a guard that fails now blocks the call

**2.1.296**

October 9, 2026

**Added**

* Added `autoCompactWindow` to subagent frontmatter and `--agents` definitions, so a subagent can auto-compact earlier than the main conversation's window
* Added a note in `/plugin` on a plugin whose hooks are left out because another enabled plugin has the same name

**Changed**

* Changed the default limit on MCP tool descriptions sent up front and on MCP server instructions from 2,048 to 4,096 characters

**9 improvements**

* Improved `--debug` output to name unrecognized frontmatter fields in custom agent files, with a hint for likely typos
* Improved `--debug` output for hooks: command hooks on tool calls, prompts, SessionStart and Stop now log their command, plugin, outcome and duration when they finish, so a slow hook is identifiable

**56 bug fixes**

* Fixed headless sessions starting a folder's `.mcp.json` or plugin MCP server that was switched off for that folder, after changing directory or reloading plugins
* Fixed hook output being altered when it contained text resembling a plugin hint tag
* Fixed SessionStart hooks of a plugin loaded after a headless session starts being skipped when a different plugin with the same name, or another spelling of it, had already run
* Fixed a plugin's served `$` methods running in the main session's working directory instead of the calling agent's, and ignoring the turn their calling hook holds
* Fixed `$.agent.register` succeeding from a mod's hook that was still running after the mod was reloaded or removed; the call is now refused
* Fixed `$.http.fetch` in mods refusing a `HEAD` request when the response declares a `Content-Length` over the 4 MiB body limit
* Fixed `claude plugin marketplace add`, `marketplace update` and `plugin install` failing with an internal error for a marketplace named like `constructor`; `add` now refuses such names clearly
* Fixed a plugin secret named `constructor` or `prototype` being deleted by the next save of that plugin's options
* Fixed PowerShell commands not seeing variables that hooks write to CLAUDE\_ENV\_FILE (when the file holds only plain assignments)
* Windows: Fixed `claude plugin install` failing for GitHub `owner/repo` plugin sources on machines with no GitHub SSH key; the clone is now retried over HTTPS

**2.1.295**

October 8, 2026

**Added**

* Added `onFailure: "block"` for command and HTTP hooks: a hook that can't start, times out, or exits with an unexpected code blocks the action instead of letting it through
* Added a warning to `claude plugin install`, `enable`, `disable` and `marketplace add` when the settings file they write to does not load
* Added advice to `claude plugin validate` when a plugin's README has no install line: it prints the line to paste and never changes the exit code, even with `--strict`
* Added `$.ui.notify` for mods: raises a native notification through your own notification setting and says which channel sent it
* Added children to a mod's `Button`: strings and `Text`, so a row of a list is one pressable with a chip or a dim detail inside

**Changed**

* Changed MCP tool descriptions the model loads through tool search to be cut at 16,384 characters instead of 2,048
* Changed subagents to preload at most 32 skills from the `skills` field, each once; a subagent with the Skill tool can still invoke the rest
* Changed what Claude and you read when a mod denies a tool call after the tool ran: it now says the tool ran and a plugin withheld its result

**13 improvements**

* Improved `claude plugin validate` and plugin loading: when a hooks module is refused over a rebound top-level `var`, the error now names the line that rebinds it, the cause, and a fix

**97 bug fixes**

* Fixed `/plugin`'s Errors tab removing a marketplace that failed to load, and uninstalling its plugins, on Enter without asking first
* Fixed `claude plugin marketplace add` reporting success for a marketplace whose name no plugin can be installed under; such an add is now refused
* Fixed a mod's hook being handed a deeply nested tool input cut short with no error, so a guard could pass content it never saw
* Fixed plugin marketplaces whose repository has large git submodules failing to add or refresh: only the submodules that hold plugin files are now fetched
* Fixed calls a mod makes while it reloads during a plugin hooks worker restart getting past another mod's guard hook that has a `.catch`; such calls are now refused
* Fixed plugins whose hooks module nests code thousands of levels deep failing to load or validate with a bare stack-overflow message
* Fixed `claude plugin test` passing a `session.append` hook that removes tool call, tool result or thinking blocks that a real session keeps
* Fixed plugin options named `constructor` or `prototype` always reading as their default and never reloading the plugin when edited
* Fixed a mod's hot reload missing a save made while `/reload-plugins` or session start was reading the mod's files
* Fixed the mod hot-reloading question being asked again every turn for the whole session when it is approved without picking an answer
* Fixed `/model`, `/fast` and `/output-style` saving their setting without asking a plugin's `config.set` hook
* Fixed a mod's hot reload missing a save made within a few milliseconds of its last reload, which left the mod on its old version until the next save
* Fixed an async SessionStart hook's unchanged context being added to the conversation again on every resume
* Fixed variables a SessionStart hook writes to `CLAUDE_ENV_FILE` not reaching the Bash tool after an in-app `/resume` or `/branch`
* Fixed a skill's `allowed-tools` and `effort` being dropped when the Skill tool finished before the response stream ended, which denied the skill's Bash commands in `-p` runs
* Fixed generated type files being written into a `--plugin-dir` plugin's folder in `-p` and SDK sessions; they are now written only where a mod is being developed
* Fixed an async hook's JSON output being ignored when it is printed over several lines
* Fixed project-scope plugins not loading in VS Code on Windows due to drive-letter casing (anthropics/claude-code#74612)
* Fixed `plugin install` and `uninstall` at project or local scope on Windows missing the install record, or adding a second one, when only the drive letter's case differs
* Fixed a plugin that adds very large interfaces getting another plugin unloaded when the plugin hooks worker stalls
* Fixed changing the auto-update channel in `/config` saving before a plugin's `config.set` hook was asked

**2.1.294**

October 8, 2026

* Fixed `prompt` and `agent` hooks written as instructions (such as "Block commands that...") allowing what they should block
* Improved how `prompt` hooks on Stop and SubagentStop written as instructions (such as "Carry on if the build is broken") are judged, so Claude is less likely to stop early

**2.1.293**

October 7, 2026

**Added**

* Added `isDeferred` to `$.tool.register` for mods: `false` lists the tool's schema in the prompt from the start instead of behind tool search

**38 bug fixes**

* Fixed a mod's hooks on `classic.*` events being skipped while the plugin hooks worker restarts, which left settings hooks to answer without them
* Fixed `claude plugin test` failing for mods that call `$.session.append`; tests can read the appended rows back with the new `mock.session`
* Fixed `claude plugin eval` refusing every Bash-granting run on Macs with Docker Desktop (links under `~/.docker/bin`); the refusal now names which part of a credential store held the link

**2.1.292**

October 6, 2026

**Added**

* Added `--marketplace <source>` to `claude plugin install`: adds the marketplace if needed, under the same policy checks as `claude plugin marketplace add`, then installs the plugin from it
* Added `prompt.autocomplete`, an event a mod hooks to add its own rows to the prompt box's autocomplete list
* Added prompt caching to `$.model.complete` for mods: `prompt` and `system` take blocks of text, and `cache: true` on a block caches the request up to it
* Added workflow agents to the `agent.spawn` mod hook, with their run and index, so a mod can refuse them

**Changed**

* Changed `claude plugin test`: a failed `expect` inside a hook the test registered, or a stub answer the engine refuses, now fails the test instead of passing silently
* Changed agent names to allow at most 256 characters: a longer one is rejected, and a skill's or a plugin file's `name` longer than that is ignored

**13 improvements**

* Improved hook output handling: `<system-reminder>` tags written in a hook's output are escaped before they reach Claude
* Improved the steps shown when a marketplace declared in a settings file has a name that looks like an official Anthropic marketplace

**64 bug fixes**

* Fixed a skill's or slash command's `allowed-tools` rule coming back in a later turn when you leave auto mode or plan mode partway through that turn
* Fixed an MCP tool with a name longer than 128 characters making every request fail; that tool is now left out and an MCP error names it
* Fixed `claude plugin` commands such as `marketplace add` and `install` running before an organization's managed settings had loaded on a first run
* Fixed Write, Edit, NotebookEdit and LSP rows, and single Read, Grep and Glob rows, hiding why a mod denied the call: the row now shows the reason
* Fixed plugins whose hooks module makes many `$.state` calls through one const taking minutes to load or validate
* Fixed `claude plugin validate` listing a matcher or state value for a hooks module that the engine reads from elsewhere
* Fixed `claude plugin validate` listing a `$.state` value read through a top-level `var` that was declared again or reassigned; such a module is now refused
* Fixed a plugin's served `$` method restarting the hook origin, which could run a guard hook with a `.catch` above it again without end
* Fixed plugin interface calls made while the plugin hooks worker restarts running without the hooks other plugins put on them
* Fixed a mod's `config.set`, `state.set`, `env.set` or `agent.spawn` hook that denies after calling `next(e)` being answered as a refusal: the hook is now reported as failed, by name
* Fixed `/theme`, the `/config` Theme menu and the first-run theme step saving a theme before a plugin's `config.set` hook was asked
* Fixed a plugin's `tool.check` hook answering allow running a tool that requires your answer (a question, a plan approval) without showing its dialog
* Fixed a mod's start-up prompt, command or subagent being queued a second time when the hooks worker was replaced
* Fixed a mod's hook that called `next(e)` and then failed while the turn was interrupted letting the call through; the call is now rejected
* Fixed a plugin's prompt drop or setting deny being ignored when its reason was longer than 4,096 characters
* Fixed tool calls made while the plugin hooks worker restarts being answered without the plugins' permission hooks
* Fixed plugin `tool.call` hooks seeing some tool calls before misnamed parameters were repaired; a hook now sees the arguments the tool will run with
* Fixed a mod's guard hook with a `.catch` being skipped silently for calls another mod's hook makes beneath the guard's own `$` call; its `.catch` is now asked

**2.1.290**

October 5, 2026

**Added**

* Added `serverToolUses` to the result of a mod's `turn.step` hook: the tool calls the API ran itself (the advisor), each with its id, name, input, start and end
* Added `agentId` to the `tool.check` event of plugin hooks, so a hook can tell a subagent's permission check from the main session's
* Added `ceiling` to the question and verdict a mod's `tool.check` hook reads, naming the approval an organization requires for a tool
* Added `ThemeKey` and `Color` types to the plugin hooks typings, so an editor lists the theme colors a mod's drawing can name
* Added to `claude plugin validate`: each hook a mod registers at a gating site is listed with whether it has a `.catch` (`gatingHooks` under `--json`)
* \[VSCode] Added a way to review and run a plugin marketplace's install or update command from the Manage plugins dialog

**Changed**

* Changed what a mod's `$.process.spawn` rejects with when another mod denies it after the child ran: it now says the call ran and a plugin withheld its result
* Changed skills and custom commands to refuse a `!` shell command that contains raw control characters other than tab and newline, with a message that shows where they are
* Changed plugin hooks so long text is clipped and logged instead of being refused or dropped silently
* Changed `claude plugin update` on a plugin loaded from a directory to print just its reason, without the "Failed to update plugin" prefix, as for built-in plugins

**19 improvements**

* Improved the built-in `plugin-authoring` skill: Claude now gives the one command another person runs to install a mod you made, and writes it in a README's install section
* Improved the reply to `/plugin` in the desktop app's Code tab: it now says where to install and manage plugins there

**131 bug fixes**

* Fixed a plugin hook with a `.catch` being unloaded, and its `.catch` skipped, when the hook kept the hooks worker busy on a prompt or tool call
* Fixed a mod's `turn.step` result listing a tool call that a mid-response model fallback had discarded
* Fixed `claude plugin validate` and plugin loading refusing a hooks module that destructures an option named like one of its top-level functions
* Windows: Fixed multi-line `!` shell blocks in skills and commands failing when the file is saved with CRLF line endings
* Fixed plugin hooks reading an empty `answer` on `turn.complete` for a subagent that hands its report back in auto mode
* Fixed a mod being unloaded without a message when a refresh followed its failed reload; its failure line now says the version loaded before is unloaded
* Fixed a mod's `prompt.submit` hook that drops a prompt after calling `next(e)` being ignored silently: the hook is now reported as failed, by name
* Fixed a mod's pane or band being redrawn without end when it followed its end over a tree that changed height at every drawing
* Fixed `disableClaudeAiConnectors` and `allowedMcpServers` URL rules not being applied to some MCP entries declared in `.mcp.json`, plugins or agents
* Fixed a mod's inline pane being redrawn without end when its tree changed height at every drawing
* Fixed plugin hooks stalling each redraw when a mod draws a long multi-line text holding non-Latin characters
* Fixed `claude plugin test` refusing to run after an upgrade because of an out-of-date saved setting
* Fixed skills not being found when asked for by the name in SKILL.md when their folder has a different name (for example a non-English name): the skill listing now shows both names
* Fixed a marketplace named after another GitHub marketplace's download folder stopping that marketplace from downloading
* Fixed Claude replying in an endless loop when a plugin's async Stop hook passes an unquoted script path under a folder with a space, such as Application Support
* Fixed some permission rules and safety checks not being applied to a tool call after a PreToolUse hook rewrote its input

**2.1.289**

October 3, 2026

**Added**

* Added `agent.spawn` for teammates, one agent id across plugin hook events, and idle and waiting states in `$.agent.list()`

**Improved**

* Improved how quickly large files open in a plugin code pane by laying the highlighted view out once at its final width
* Improved the line a mod's author sees when its band or pane fails to draw: it names the mod and says nothing was drawn

**23 bug fixes**

* Fixed `plugin list`, `plugin eval` and `plugin update` showing a stale copy of a plugin installed from a local folder marketplace, and hot reload for a symlinked `--plugin-dir`
* Fixed installed mods not loading in the first session after an upgrade
* Fixed a plugin's rows above the prompt showing a stale row while the Background tasks dialog was open in fullscreen
* Fixed plugin panes drawing nothing when a link used a localhost address, an `@` in its path, an uppercase host or a `file:` path
* Fixed a freeze or forced quit at launch when a plugin drew a Box with a border style the terminal does not know
* Fixed supervised and background sessions ending when a plugin's on-screen handler threw asynchronously
* Fixed sessions ending with an interface error when a plugin region with no height kept growing
* Fixed `claude plugin validate` skipping the plugin when the folder also holds a marketplace manifest
* Fixed sessions ending with "unrecoverable interface error" when a value a mod's `ui.render` hook wrote made a row throw while drawn; the engine now draws its own row instead
* Fixed right-aligned content in a mod's pane or band drawing under the close mark or `[-]`, which now also keep one column in from the terminal's edge
* Fixed a mod's `Client` that fails while drawn taking down everything the mod drew around it; it now fails alone and raises `ui.fault`
* Fixed a mod's band that fails to draw briefly telling the cards under it to step aside
* Fixed a failed plugin component showing `Error` or nothing as its reason when the failure carried no message
* Fixed a mod's Client region staying failed for the whole session after the terminal threw while drawing it

**2.1.288**

October 2, 2026

**Added**

* Added `$.ui.selection()` for mods: returns the text you last selected in fullscreen mode and, when the selection lies within one transcript row, that row

**64 bug fixes**

* Fixed a mod's button sometimes running a different button's action when pressed on a view drawn before Claude Code restarted
* Fixed a plugin's pane showing nothing when one `Code` element held a diff that does not parse; it now draws as plain code
* Fixed plugin LSP servers receiving literal `${user_config.*}` and `${CLAUDE_PLUGIN_ROOT}` placeholders in `initializationOptions` and `settings` instead of substituted values or manifest defaults
* Fixed a plugin's `tool.call` hook making Bash fail and file searches read the wrong folder in subagents that run in a worktree
* Fixed `git-subdir` plugin installs failing, or caching an incomplete plugin, on older git (before 2.39, e.g. Ubuntu 22.04's 2.34)
* Fixed plugins loaded with `--plugin-dir` not showing "Configure options" in `/plugin`
* Fixed fullscreen sessions exiting with "unrecoverable interface error" when opening the background tasks dialog while a plugin or mod showed rows above the prompt
* Fixed agent teams: a plugin-defined agent spawned by name now runs with its own prompt, tools, disallowedTools and effort instead of the defaults
* Fixed `claude plugin install` failing for GitHub-source plugins on macOS and Linux machines with no GitHub SSH key: the clone now falls back to HTTPS and prints a notice
* Fixed a stall when launching an agent whose `tools:` lists very many `Agent(...)` entries
* Fixed `owner/repo` plugin marketplaces showing only the second attempt's error when both the SSH and HTTPS fetch fail; both errors are now shown, with the transport tried first on top
* Fixed LSP tool calls hanging indefinitely when a language server uses dynamic capability registration or stops responding; requests now time out after 60s (per-server `requestTimeout`)
* Fixed `idle_prompt` notification hooks firing while background agents are still running (anthropics/claude-code#93672)
* Fixed PreToolUse and PermissionRequest hooks being skipped when matching them failed or the tool's input could not be serialized to JSON; the call is now blocked
* Fixed the InstructionsLoaded hook omitting agent\_id and agent\_type when a subagent's file access loads a rule or nested CLAUDE.md; rules and nested CLAUDE.md files loaded on file access now also report effort
* Fixed `claude plugin test` reporting mods as turned off remotely when it had only read an out-of-date saved setting

**2.1.287**

October 1, 2026

**Added**

* Added Claude Mods: plugins may now modify deeper behavior
* Added URL prompts from MCP servers on the 2025-11-25 protocol, for example to sign in. If a server no longer connects after this update, add "bareElicitationCapability": true to its MCP config entry

**Changed**

* Changed MCP server `alwaysLoad: false` to defer all of that server's tools behind tool search

**20 improvements**

* Improved plugin marketplace errors to say in plain words why a marketplace was ignored or refused, and what to do
* Improved plugin listings to note when a plugin's dependencies were not installed, and updating a plugin now retries an install that did not finish
* Improved `/skill` names typed mid-message: Claude is now told they are skills, including `disable-model-invocation` ones
* \[VSCode] Improved the Manage plugins dialog: a failed marketplace add, remove or refresh now says what went wrong

**67 bug fixes**

* Fixed hooks configured with `asyncRewake` waking Claude over and over with "found issues" notifications when the hook's script file is missing; the broken hook is now reported once
* Fixed the transcript's "N hooks ran" summary and the verbose debug log's matched-hooks count including Claude Code's internal callbacks, so one configured hook no longer shows as two

**2.1.286**

September 30, 2026

**16 improvements**

* \[VSCode] Improved the Manage plugins dialog: it says when a turned-off plugin is still on because of other settings, and explains a plugin folder clash

**49 bug fixes**

* Fixed plugin errors for a marketplace Claude Code refuses to load: they now say why and how to fix it instead of "not found"

**2.1.285**

September 29, 2026

**Added**

* Added `claude plugin configure <plugin>` to show a plugin's options and which are unset, or save new values read from stdin with `--values-stdin`
* Added `<server>.<key>=<value>` to `claude plugin install --config`, so a bundled `.mcpb` MCP server's own settings can be set at install time and it starts without visiting `/plugin` → Configure
* \[VSCode] Added a plugin options form to Manage plugins: installing a plugin that has options asks for the unset ones, and a gear on its row changes them later

**Changed**

* Changed MCP tools so a tool that sets its own `_meta['anthropic/alwaysLoad']` to false stays deferred when its `--mcp-config`, Agent SDK or plugin server is set to `alwaysLoad`
* Changed `claude mcp get` to hide the command, arguments, and environment values of stdio MCP servers provided by plugins; variable names are still shown
* \[VSCode] Changed the Manage plugins dialog to ask before removing a marketplace or turning off a plugin that your project's shared `.claude/settings.json` turns on

**17 improvements**

* Improved plugin marketplace errors to name why a git address is refused instead of citing enterprise policy
* Improved validation of git URLs for plugins, marketplaces and the current repository's remote
* \[VSCode] Improved the Manage plugins dialog: a failed plugin action now opens a popup that explains it and, where there is one, offers the fix

**86 bug fixes**

* Fixed plugin and marketplace installs and updates over SSH ignoring the ssh program set in `GIT_SSH` or in your git config's `core.sshCommand`
* Fixed `claude plugin disable` and `enable` with a full `name@marketplace` id changing a settings entry in another letter case instead of the installed plugin's own
* Fixed installing a plugin with `claude plugin install` or `/plugin` putting it into an installed plugin's cache or data folder when their ids differ only in `.`, `-`, `@` or (macOS, Windows) capitals; the install is now refused
* Fixed hooks and SDK permission callbacks seeing a missing or outdated plan on ExitPlanMode when the plan was written in the same response
* Fixed synchronous hooks hanging Claude Code while a background process the hook started (for example `some-daemon &`) kept its output open; the hook now finishes shortly after its own process exits
* Fixed a cancelled shell command or hook still starting, and running to its end, when the cancel arrived while it was being set up
* Fixed plugins silently skipping a bundled `.mcpb` MCP server that still needs configuration: `/plugin`, the install message and `claude plugin install` now say so and point to Configure
* \[VSCode] Fixed uninstalling a plugin from the Manage plugins dialog, which removed the wrong installation or failed for a plugin installed for the project

**2.1.284**

September 28, 2026

**Added**

* \[VSCode] Added plugin load errors and notes to the Manage plugins rows, with a popup to disable, uninstall or copy the error

**18 improvements**

* Improved `claude plugin marketplace add` to say when it replaces a marketplace already added under the same name from a different source, and how to undo it

**57 bug fixes**

* Fixed `claude mcp add` reporting success when managed settings restrict MCP servers to plugins; it now refuses and says what to do, instead of saving a server that never loads
* Fixed the `/plugin` configure screen: boolean options are now a true/false choice instead of free text, number options refuse invalid input, and ←/→ change an options field instead of switching tabs
* Fixed Bash tool failing on Windows with many plugins enabled: plugin `bin/` directories that don't exist are no longer added to PATH, and inherited entries aren't added twice
* Fixed `sparsePaths` plugin marketplaces cloning empty and replacing a working local copy on older git (before 2.39), which failed every refresh with "marketplace.json file is no longer present"
* Fixed plugins from marketplaces, claude.ai and npm pre-approving their own tools via `allowed-tools` under managed `allowManagedPermissionRulesOnly`; only plugins from an official Anthropic source or a source that managed settings vouch for keep that pre-approval
* Fixed a failed first `claude plugin install` leaving the plugin enabled and recorded when a dependency's version range could not be met
* Fixed the debug log dropping a failed hook's stderr when the hook also wrote to stdout, and logging nothing for a failed hook with no output; failed hooks now also log their status code
* Fixed `{"decision":"block"}` returned by Elicitation and ElicitationResult hooks being ignored; it now declines the MCP elicitation, as exit code 2 does
* \[VSCode] Fixed plugin install links replacing a marketplace you already have that uses the same name

**2.1.283**

September 25, 2026

**Added**

* Added `path` to `--plugin-dir` load-failure entries in the stream-json `system/init` `plugin_errors`, naming the directory that did not load

**Changed**

* Changed `claude plugin eval` to require git 2.31 or later when git is installed; a run on an older git is refused with a message naming the version
* Reverted the 2.1.282 reservation of the `claude-ai` name: skills, commands, workflows and MCP servers' skills and prompts so named load again, and `Skill(claude-ai:*)` rules are ordinary prefix rules

**16 improvements**

* Improved the Skill tool's reply when a skill belongs to a plugin that failed to load, so Claude tells you the plugin could not be loaded instead of calling the skill uninstalled
* Improved recovery from an `installed_plugins.json` that cannot be read at all: its contents are kept in a file beside it before it is rebuilt, and `claude plugin list` names that file

**53 bug fixes**

* Fixed `claude plugin validate` saying Claude Code accepts a plugin or marketplace name it cannot install; such names in `marketplace.json` now fail validation
* Fixed `claude plugin validate` passing plugins whose `outputStyles`, `themes`, `monitors`, or `lspServers` paths are missing or point outside the plugin directory
* Fixed `claude plugin details` showing 0 MCP servers for plugins that declare their servers in `plugin.json`
* Fixed `claude plugin marketplace remove` not saying which installed plugins it uninstalled with the marketplace; it now lists them
* Fixed `claude plugin uninstall` removing the other of two installed plugins whose ids differ only in case, with its options and secrets, when the one named had no `enabledPlugins` entry at that scope
* Fixed plugins that declare no version being silently restored at their source's newest commit, not the installed one, when their cached files were missing
* Fixed user-installed plugins and marketplaces failing to load with "cache-miss" after the home or config directory was moved, for example in bind-mounted devcontainers
* Fixed `installed_plugins.json` showing no plugins when it holds a record under an invalid plugin id; such a file loads again
* Fixed `installed_plugins.json` being rewritten, losing records, when it holds a record this version cannot read; `claude plugin` commands now name the record and say how to recover

**2.1.282**

September 24, 2026

**Changed**

* Changed skill folders, command files and workflow commands in the `anthropic-skills` or `claude-ai` namespace to no longer load; a plugin so named still loads but yields name ties to synced skills

**59 bug fixes**

* Fixed repository, user and `--add-dir` skills, commands and skills-directory plugin manifests pre-approving their own tools via `allowed-tools` under managed `allowManagedPermissionRulesOnly`
* Fixed plugin uninstall reporting success and deleting the plugin's saved options when its settings file still enabled it or could not be read; it now stops and names the file
* Fixed plugin uninstall deleting a plugin's saved options and secrets when the list of installed plugins could not be read after the removal; they are now kept and the uninstall says so

**2.1.281**

September 23, 2026

**Added**

* Added MCP server checks to `claude plugin validate`: it reports `.mcp.json` entries that would be silently dropped at load, undeclared `${user_config.*}` references, and insecure URLs

**Changed**

* Changed `claude plugin uninstall --json` and the /plugin dialog to say a plugin's data was kept when its folder stays because another installed plugin uses it or install records cannot be read

**33 improvements**

* Improved plugin hook-failure errors to name the offending plugin, and added a `claude plugin validate` warning when a shell-form hook leaves `${CLAUDE_PLUGIN_ROOT}` unquoted (it breaks on plugin paths with spaces)

**112 bug fixes**

* Fixed `mcp_tool` hooks on blocking events (PreToolUse and similar) being skipped while their MCP server was still connecting; they now wait for it, up to the MCP connect timeout
* Fixed the same MCP server being connected twice when a plugin or claude.ai connector and a configured server spell its URL differently (host letter case, default port, trailing slash)
* Fixed `MCP_CONNECTION_NONBLOCKING=0` giving up on claude.ai connectors after 1s instead of honoring `MCP_CONNECT_TIMEOUT_MS`
* Fixed `--channels` plugin entries being checked against the installed plugin's marketplace alone; the installed plugin's name must now match the entry as well
* Fixed `--plugin-dir` on a folder of plugins that also has a `.claude-plugin/marketplace.json` loading one empty plugin instead of the plugins in it
* Fixed `claude plugin uninstall` refusing to remove a project-scope plugin that isn't enabled, saying it is "enabled at project scope" while `claude plugin disable` says it is already disabled
* Fixed `claude plugin update` failing for project-scoped plugins when `--scope` is omitted — it now resolves the scope the plugin is installed at instead of assuming user
* Fixed `claude plugin validate` reporting `privacyPolicyUrl`, `supportUrl` and other listing metadata keys in plugin.json as unknown fields
* Fixed `known_marketplaces.json` recording a marketplace as refreshed when its remote could not be reached and `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` kept the existing clone
* Fixed the `/plugin` Errors tab showing no confirmation after its last error is resolved
* Fixed `/plugin` starting a second uninstall or update of the same plugin when Enter was pressed again while the first was still running
* Fixed a `y` held while `/plugin` checks a marketplace source adding the marketplace the instant the "Add marketplace?" question appears, before it can be read

**2.1.280**

September 22, 2026

**Changed**

* Changed plugin marketplaces whose name imitates a reserved marketplace name to be refused when added, and to stop loading if one was already added
* Changed `PermissionRequest` hooks: an agent-type hook no longer runs there, since its answer could never allow or deny the request; it now shows an error pointing to command or http hooks

**21 improvements**

* Improved the UserPromptSubmit hook timeout notice and the debug log to name which hook command timed out

**69 bug fixes**

* Fixed `installed_plugins.json` keeping the install-time commit after updating a plugin from a GitHub repository or git URL that tracks a branch or tag
* Fixed background subagents being unable to use the LSP tool when an LSP plugin is active
**2.1.277**

September 18, 2026

**10 improvements**

* Improved `/plugin` Installed: an MCP server listed apart from its plugin now shows which plugin it belongs to
* Improved `claude plugin install` on an already-installed plugin: it now says when the marketplace offers a newer version and names the `claude plugin update` command

**57 bug fixes**

* Fixed `claude plugin install` sometimes failing and breaking the installed copy when reinstalling a plugin version that a session or another program was using; an unchanged copy is now left alone
* Fixed background sessions (`claude --bg`) exiting when a plugin's LSP server exited or closed its stdin
* Fixed one malformed `strictKnownMarketplaces` or `blockedMarketplaces` entry silently disabling the whole enterprise marketplace policy
* Fixed `/plugin` not stripping terminal control characters from messages on the Installed tab, such as the error of a failed plugin update
* Fixed `/plugin` → Installed and `/skills` crashing when a skill or legacy command is named like a built-in Object property such as `constructor` or `toString`
* Fixed `/plugin` closing with no message when every install in a multi-select failed
* Fixed uninstalled plugins reappearing as "failed to load" rows in `/plugin` Installed, and Remove not clearing such a row
* Fixed plugins from the official marketplace being recorded without their commit in `installed_plugins.json`, and `installed_plugins.json` keeping the old commit after updating a pinned-commit plugin

**2.1.275**

September 17, 2026

**Added**

* Added `/plugin install <plugin> --marketplace <source>`, which offers to add the marketplace before installing the plugin

**Changed**

* Changed plugins installed from an npm source to be fetched with `npm pack --ignore-scripts` and integrity-verified, so a package's install scripts no longer run

**60 bug fixes**

* Fixed `claude plugin marketplace update` deleting a GitHub marketplace's local copy when the fetch failed and the marketplace was named after its repository
* Fixed plugin messages, logs and the VS Code plugin dialog showing the wrong server for some git addresses
* Fixed plugin reload previews replacing a running session's extracted plugin files when the plugin was loaded from a `--plugin-dir` or `--plugin-url` archive
* Fixed `SubagentStop` hooks with a specific `matcher` firing for every stopping subagent whose agent type was empty
* \[VSCode] Fixed plugin install links opening the Manage plugins dialog for plugin names and marketplace addresses that can't be used in a link

**2.1.274**

September 17, 2026

**Changed**

* Changed `"type": "sdk"` MCP entries in `.mcp.json`, settings, plugins and agent files to be skipped with a warning: only an SDK host application can register in-process servers
* Changed plugin and marketplace clones to leave Git LFS files as pointers instead of downloading them; `git lfs pull` in the checkout fetches them

**71 bug fixes**

* Fixed a plugin or marketplace directory with no git repository of its own taking its version from an enclosing git repository, such as a git-managed `~/.claude`
* Fixed the Bash tool re-sourcing the shell profile (a multi-second stall on the next command) after every plugin reload; it now does so only when the plugins' `bin/` directories changed
* Fixed plugins with a top-level `$schema` in `hooks/hooks.json` showing an "unknown key" notice

**2.1.271**

September 14, 2026

**Added**

* Added `omitClaudeMd` to agent frontmatter and `--agents` JSON, letting custom and plugin subagents run without user, project and local CLAUDE.md files; managed policy files still load
* Added `--accept-command <sha256>` to `claude plugin install` and `claude plugin update` to accept exactly the command a previous `--json` run displayed, instead of `-y`

**Changed**

* Changed auto mode so that a skill's or slash command's inline `!` shell commands follow default-mode permission rules instead of the classifier; a command no rule decides runs as a reviewed tool call

**59 bug fixes**

* Fixed an enterprise `managed-mcp.json` that can't be read or parsed being ignored: it now keeps exclusive MCP control (user, project and plugin servers don't load) and warns at startup

**2.1.269**

September 11, 2026

**Added**

* Added `claude plugin eval`: run a plugin's eval suite against Claude Code and get scored, reproducible results (JSON + HTML report); see `claude plugin eval --help`

**11 improvements**

* Improved the Skill tool's "Unknown skill" error to name the plugin skill's full name when a bare name matches exactly one plugin skill

**66 bug fixes**

* Fixed plugin `headersHelper` consent prompts showing a URL path that could be misread as a different host
* Fixed plugin LSP servers that reject `shutdown` params (e.g. rust-analyzer) being left running at session end; `exit` is now sent even if `shutdown` fails

**2.1.268**

September 10, 2026

**Added**

* Added `--json` to `claude plugin install`, `uninstall`, `update`, `enable` and `disable`, and `errorDetails`/`noteDetails` to each row of `claude plugin list --json`

**Changed**

* \[VSCode] Changed the Manage plugins dialog to apply installs, enables, disables and uninstalls to open sessions without a restart

**16 improvements**

* Improved `/plugin`: installing, enabling or disabling a plugin now takes effect when you close the menu; `/reload-plugins` is no longer needed afterwards

**59 bug fixes**

* Fixed `claude plugin validate` rejecting plugin paths whose directory name begins with two dots, which the plugin loader accepts
* Fixed plugins silently skipping a default monitors file or root SKILL.md that could not be checked

**2.1.267**

September 9, 2026

**41 bug fixes**

* Fixed a case where a marketplace entry path containing a backslash could bypass the containment check for fetched marketplaces on macOS and Linux
* Fixed `effort:` frontmatter on custom commands, skills, and subagents being ignored on models whose default effort is still pinned (Opus 4.7, Opus 4.8, Fable 5)

**2.1.265**

September 8, 2026

**Added**

* Added support for pointing `--plugin-dir` at a folder of plugins: each child folder with a manifest loads, and children added or removed while running are picked up

**Changed**

* Changed plugin display metadata to prefer the marketplace entry over `plugin.json` on the Installed tab and `claude plugin details`, filling gaps from `plugin.json`

**7 improvements**

* Improved slash commands typed mid-prompt: matches now show in a list (Tab opens it outside fullscreen) instead of a single suggestion, and a plugin skill is now found by its bare name

**34 bug fixes**

* Fixed a plugin path containing a backslash bypassing the symlink containment check on macOS and Linux
* Fixed plugin directories whose names begin with two dots being wrongly refused as outside the plugin root
* Fixed a plugin's default component folder that the OS cannot check, such as a symlink loop, being silently skipped; it is now reported in `/plugin` with the error code
* Fixed `/plugin` Discover/Browse and `claude plugin list --json --available` showing no description or display name for marketplace plugins whose metadata lives only in their `plugin.json`

**2.1.261**

September 4, 2026

**Added**

* Added `/skill-doctor` to show which loaded skills go unused and what they cost in context, so you can prune them

**47 bug fixes**

* Fixed plugin install hints from CLIs run in background Bash commands: they are now detected, and the raw `<claude-code-hint>` tag no longer leaks into the conversation
* \[VSCode] Fixed install-plugin links opening the Claude sidebar without the install dialog in a window where only the session list had been shown

**2.1.260**

September 3, 2026

**Added**

* Added `/reload-plugins` to headless sessions, so it appears in the Claude Code Desktop and SDK command lists

**38 bug fixes**

* Fixed model switching staying blocked for the rest of the session after a plugin hook load failure; each switch now re-checks and the refusal names the cause

**2.1.259**

September 2, 2026

**Added**

* Added `--json` to `claude plugin validate` for a machine-readable validation report

**26 bug fixes**

* Fixed auto mode running a turn on a model it doesn't support when a command or skill's frontmatter `model:` named one; the turn now keeps the session model
* Fixed frontmatter `model:` on custom commands and skills being ignored in interactive sessions
* Fixed marketplace repo URLs on github.com with a trailing slash or dangling `?`/`#` producing an unusable `.git` clone URL
* Fixed blocking Stop hooks causing the turn after a block to lose the model's reasoning from that turn and, on some models, miss the prompt cache
**2.1.257**

September 1, 2026

**Added**

* Added `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` to apply `CLAUDE_CODE_SUBAGENT_MODEL` (or the main model) to every subagent, ignoring per-spawn and agent-definition model overrides
**67 bug fixes**

* Fixed `/mcp` reconnect and enable still connecting a settings-file MCP server that a managed MCP allow/deny list or `strictPluginOnlyCustomization` loaded after startup should block
* Fixed `claude mcp remove` leaving a remote server's stored OAuth credentials behind when `strictPluginOnlyCustomization` locks MCP to plugin-only servers
* Fixed plugins being able to read files outside their own directory through a declared command, agent, skill, hooks or other component path that is a symlink; such paths are now refused with an error
**2.1.251**

August 28, 2026

**Added**

* Added `PreModelSwitch` and `PostModelSwitch` hook events (block, confirm, or annotate a model switch); `SessionStart` resume hooks now receive session staleness and the estimated re-cache cost
**Changed**

* Changed `CLAUDE_CODE_SUBAGENT_MODEL` to set the default subagent model rather than override everything: an agent definition's `model:` and an explicit per-spawn model now take precedence over it
**41 bug fixes**

* Fixed plugin commands declared in a marketplace entry being able to point outside the plugin directory; such paths are now rejected with a path-traversal error
* Fixed background sessions occasionally starting without any plugin skills (and staying that way) when another Claude Code process was refreshing the plugin marketplace at the same moment
**2.1.248**

August 27, 2026

**Added**

* Added `experimental.cacheTtl` (`"5m"` or `"1h"`) to agent frontmatter: a per-agent prompt cache TTL used when no subagent TTL setting is configured
**32 bug fixes**

* Fixed background sessions waiting silently when a `PermissionRequest` or `PreToolUse` hook prints an invalid answer: the `claude agents` row now names the hook and the schema error
* Fixed hooks silently treating a stdout `{…}` object that isn't valid JSON as plain text; it's now reported as a hook error with the parse message
* Fixed MCP servers whose `headersHelper` supplies the `Authorization` header falling into OAuth discovery on a 401 instead of re-running the helper and retrying the call as documented
**2.1.247**

August 26, 2026

**Improved**

* Improved plugin marketplace hardening: names containing control or invisible characters are rejected, and marketplace-supplied text in `/plugin` and `claude plugin` output is escape-safe

**19 bug fixes**

* Fixed a version-less marketplace plugin's live cache directory being deleted and recreated on a second-scope install, which could disrupt a running session using it
**2.1.246**

August 25, 2026

**5 improvements**

* Improved subagent results: a subagent that stops at its `maxTurns` limit now returns its output marked as partial, with a hint to continue it via `SendMessage`, instead of appearing finished
**49 bug fixes**

* Fixed the plugin cache creating duplicate SHA-named directories for the same plugin
* Fixed plugin skills whose frontmatter `name` already includes the `<plugin>:` prefix showing it doubled in the slash menu (e.g. `/plugin:plugin:skill`)
* Fixed `claude plugin update` failing for an installed plugin given its bare name (only the fully-qualified name worked)
* Fixed plugin installation failing when `plugin.json` was saved with a UTF-8 byte-order mark (BOM)
* Fixed `/reload-plugins` reporting 0 skills for plugins that define skills under `skills/*/SKILL.md`
* Fixed hook error messages showing a literal `${CLAUDE_PLUGIN_ROOT}` instead of the resolved plugin path
* Fixed `claude plugin install <name>` exiting silently (or hanging in a terminal) instead of reporting an error when `~/.claude/plugins/known_marketplaces.json` is empty or corrupted
* Fixed the `Notification` hook not firing while the sandbox "Network request outside of sandbox" permission prompt is waiting
**2.1.243**

August 25, 2026

**33 bug fixes**

* Fixed hook `if` conditions like `Bash(cat *)` firing on unrelated Bash commands when the command contained `$()` or backtick command substitution followed by more arguments
* Fixed plugin dependencies declared with a `marketplace` field never resolving when both plugins are loaded together via `--plugin-dir`
* Fixed `/reload-plugins` keeping the LSP tool after the last LSP plugin is disabled; it now also warns before an LSP plugin change that would re-read the conversation
**2.1.239**

August 21, 2026

**38 bug fixes**

* Fixed agents, skills, and commands whose `.md` file starts with a UTF-8 BOM being silently ignored
* Fixed marketplace `metadata.pluginRoot` having no effect: bare plugin source names now resolve under it as the docs describe
* Fixed hooks failing with "posix\_spawn ENOENT" after the session's working directory was deleted; they now run from the project root or home directory instead
**2.1.238**

August 20, 2026

**Changed**

* MCP `headersHelper` from a project `.mcp.json`, plugin, or agent file runs without inherited credential env vars; user, managed and claude.ai-scope helpers now run from the Claude config dir
**23 bug fixes**

* Fixed custom, project, and plugin output styles drifting back to the default voice mid-session
**2.1.234**

August 17, 2026

**24 bug fixes**

* Fixed `strictKnownMarketplaces` allowlists accepting SCP-style git marketplace sources whose host differs from the one git would actually connect to
**2.1.233**

August 14, 2026

**8 bug fixes**

* Fixed Notification hooks not firing for permission prompts when running under Claude Desktop or VS Code
* Fixed skill/command argument substitution to prevent argument values from being re-expanded as template markers
**2.1.232**

August 13, 2026

**Changed**

* Settings: `additionalMarketplaces` and `allowedMarketplaces` are now accepted as friendlier aliases for `extraKnownMarketplaces` and `strictKnownMarketplaces`
* Enterprise policy: a url-typed `blockedMarketplaces` entry for a bare repo URL keeps blocking that URL when the CLI classifies it as a git clone
* `/plugin install plugin@marketplace` now refreshes the marketplace first, so newly published plugins install without a manual marketplace update
**19 bug fixes**

* Fixed a startup race that could silently unregister a plugin marketplace due to concurrent writes to `known_marketplaces.json`
**2.1.229**

August 12, 2026

**18 bug fixes**

* Fixed one-shot `claude plugin` commands leaving a stray liveness file that could prevent cleanup of outdated plugin versions
**2.1.228**

August 11, 2026

**11 bug fixes**

* Fixed background plugin-cache cleanup deleting a plugin's cache when its only version is a symlinked development checkout
**2.1.224**

August 7, 2026

**15 bug fixes**

* Fixed plugin install records being silently corrupted when the same plugin is installed in multiple projects
**2.1.223**

August 6, 2026

**Added**

* Added owner wildcard entries (`"owner/*"`) to the `strictKnownMarketplaces` and `blockedMarketplaces` managed settings for allowing or blocking all marketplace repos under a GitHub org
**2.1.222**

August 4, 2026

**Improved**

* Improved the refusal when Claude tries to invoke a skill with `disable-model-invocation`: Claude is now told to ask you to run the skill instead of replicating its workflow
**16 bug fixes**

* Fixed PreToolUse auto-allow hooks bypassing tool restrictions in background agent tasks (summaries, compaction, renames)
**2.1.221**

August 4, 2026

**Added**

* Added warnings to `claude plugin validate` when a marketplace or plugin name would be rejected by Claude Desktop's managed marketplace sync
**Changed**

* Changed `/plugin install` to refresh a stale marketplace catalog and retry before reporting a plugin not found
* Changed plugins installed from `/plugin` to activate immediately when safe, instead of always requiring `/reload-plugins`
* Changed plugins to accept `"."` as a `skills` path, and the root-level `SKILL.md` validation error now suggests using the plugin root
**17 bug fixes**

* Fixed plugin- and org-delivered skills named after terminal-only built-ins (e.g. `/help`, `/feedback`) being un-invocable in non-interactive sessions
**2.1.219**

July 24, 2026

**Added**

* Added `DirectoryAdded` hook that fires after `/add-dir` or the SDK `register_repo_root` control request registers a new working directory mid-session
**2.1.218**

July 22, 2026

**Added**

* Added `yes`/`no`/`on`/`off`/`1`/`0` (case-insensitive) as accepted values for skill and plugin frontmatter booleans, alongside `true`/`false`

**Changed**

* Changed agent markdown files to reject agent names containing `:`, which is reserved for plugin namespacing
* Changed skills with `context: fork` to run in the background by default; opt out per skill with `background: false`
**2.1.217**

July 21, 2026

**13 bug fixes**

* Fixed a `CLAUDE.md` or `SKILL.md` paths frontmatter value with many brace groups OOM-killing or stalling the CLI at startup — brace expansion is now budget-bounded
**2.1.216**

July 20, 2026

**30 bug fixes**

* Fixed skills and commands changed during a session not appearing in the slash menu until restart
* Fixed plugin skills with a `name` frontmatter field losing their plugin prefix in slash-command autocomplete

**2.1.214**

July 18, 2026

**Added**

* Added reasoning effort to the `subagentStatusLine` payload, so custom agent rows can render model and effort

**Changed**

* Changed single-segment `dir/**` hook `if:` conditions to match only `<cwd>/dir`; write `**/dir/**` for any-depth matching. `deny`/`ask` permission rules keep their any-depth match.
* Changed SessionStart hooks to report source `"fork"` when a session begins as a fork instead of `"resume"`

**35 bug fixes**

* Fixed plugins enabled via the `--settings` CLI flag not loading (regression since v2.1.181)
* Fixed hooks with exit code 2 not blocking as documented when the hook's stdout JSON fails schema validation

**2.1.212**

July 17, 2026

**28 bug fixes**

* Fixed a `continue:false` hook's halt being dropped when the tool fails or completes mid-stream, and hook infrastructure errors being misreported as user rejections
* Fixed @-mentions attaching nothing after a partial file read, plugin uninstall targeting the wrong marketplace, and false "Command timed out" on exit code 143

**2.1.211**

July 15, 2026

**24 bug fixes**

* Fixed auto mode overriding a PreToolUse hook's `ask` decision for unsandboxed Bash — a hook `ask` now floors the decision at a prompt
* Fixed plugin MCP servers not reconnecting after an idle web session woke, leaving MCP calls failing until the next message

**2.1.210**

July 14, 2026

**22 bug fixes**

* Fixed a hook callback timeout being misreported to the model as a user rejection, which made unattended sessions stop and wait
* Fixed plugin-provided MCP servers being torn down when MCP servers are re-synced mid-session
* Fixed unmatched `$1`/`$2` positional placeholders in skills and commands being silently stripped; they are now preserved verbatim
* Fixed plugin cache writes leaving temp files behind on failure and failing on locked-file renames on Windows and network filesystems

**2.1.208**

July 14, 2026

**28 bug fixes**

* Fixed the Agent tool launching with no tools when a subagent's `tools` list resolves to nothing — it now returns a clear error naming the unrecognized entries

**2.1.207**

July 11, 2026

**Changed**

* Plugin hooks/monitors/MCP headersHelper: `${user_config.*}` in shell-form commands is now rejected (shell-injection fix). Hooks: use exec form (`args` array) or `$CLAUDE_PLUGIN_OPTION_<KEY>`; monitors and headersHelper: read the value inside the script (config file or the server's `env` block).
* Plugin option values (`pluginConfigs`) are no longer read from project-level `.claude/settings.json`; only user, `--settings`, and managed settings are honored

**17 bug fixes**

* Fixed malformed bracket patterns in rules globs, skill paths, `.ignore`, and `.worktreeinclude` breaking file reads, file suggestions, and worktree creation

**2.1.206**

July 9, 2026

**18 bug fixes**

* Fixed MCP servers configured via `--mcp-config` or `.mcp.json` ignoring a per-server `request_timeout_ms`, which caused long-running MCP tool calls to time out at the 60s default in fresh sessions
* Fixed false "disused plugin" tips and skewed disuse telemetry for LSP plugins

**2.1.205**

July 8, 2026

**15 bug fixes**

* Fixed a plugin LSP server that fails to initialize preventing a valid LSP server from another plugin handling the same file extension

**2.1.203**

July 7, 2026

**26 bug fixes**

* Fixed LSP-only plugins being incorrectly flagged for disuse when their language servers deliver diagnostics or answer navigation requests

**2.1.202**

July 6, 2026

**Improved**

* Improved MCP error messages: clearer error when a server config has `url` but no `type`, suggesting `"type": "http"` instead of the misleading "command: expected string"

**13 bug fixes**

* Fixed re-invoking an already-loaded skill appending a duplicate copy of its instructions to context

**2.1.200**

July 3, 2026

**13 bug fixes**

* Fixed `claude agents --plugin-dir <dir>` not showing the plugin's agents and skills in the agent view when the flag is placed after `agents`
* Fixed project-scoped plugins not loading correctly from git worktrees of the same repository
**2.1.199**

July 2, 2026

**Changed**

* Stacked slash-skill invocations like `/skill-a /skill-b do XYZ` now load all leading skills (up to 5), not just the first

**20 bug fixes**

* Fixed `SessionStart`, `Setup`, and `SubagentStart` hooks silently hiding stderr when exiting with code 2 — the error is now shown in the transcript
**2.1.198**

July 1, 2026

**Added**

* Added background agent notifications in `claude agents` — sessions that need input or finish now fire the `Notification` hook (`agent_needs_input` / `agent_completed`)
**2.1.196**

June 29, 2026

**16 bug fixes**

* Fixed `claude plugin validate` skipping local plugins whose source is "." and stopping after the first error class
* Fixed plugin dependency version pins not being honored when the marketplace was added as a local folder path backed by a git repo
**2.1.195**

June 26, 2026

**8 bug fixes**

* Fixed hook matchers with hyphenated identifiers (e.g. `code-reviewer`, `mcp__brave-search`) accidentally substring-matching — they now exact-match. Use `mcp__brave-search__.*` to match all tools from a hyphenated MCP server.
* Fixed external plugins enabled only by project `.claude/settings.json` not requiring explicit install consent on every loader path
* Fixed `/plugin` Enable/Disable not working when a plugin's `plugin.json` `name` differs from its marketplace entry name
**2.1.193**

June 25, 2026

**Improved**

* Improved MCP `headersHelper` auth: the helper now re-runs and reconnects automatically when a tool call returns 401/403
* Improved plugin auto-rename: marketplace `renames` maps are now followed automatically, updating your settings to the new name
**2.1.191**

June 24, 2026

**12 bug fixes**

* Fixed hooks with comma-separated matchers (e.g. `"Bash,PowerShell"`) silently never firing
**2.1.186**

June 22, 2026

**Improved**

* Improved skill frontmatter: `display-name`, `default-enabled`, `fallback`, and `metadata.*` keys now accept kebab-case, snake\_case, and camelCase
* Improved malformed `SKILL.md` YAML frontmatter handling: loads the skill body with empty metadata instead of failing silently
**2.1.183**

June 19, 2026

**Added**

* Added a warning when the requested model is deprecated or automatically updated to a newer model, shown on stderr in print mode (`-p`) and now also covering models set in agent frontmatter
**11 bug fixes**

* Fixed user-level skills appearing multiple times in slash-command autocomplete when multiple plugins are enabled
**2.1.178**

June 15, 2026

**14 bug fixes**

* Fixed `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` preventing fresh marketplace installs from cloning
* Fixed MCP server-level specs (`mcp__server`, `mcp__server__*`, `mcp__*`) in subagent `disallowedTools` being silently ignored
**2.1.176**

June 12, 2026

**18 bug fixes**

* Fixed hook `if` conditions for Read/Edit/Write tool paths: documented patterns like `Edit(src/**)`, `Read(~/.ssh/**)`, and `Read(.env)` now match correctly
**2.1.169**

June 8, 2026

**Added**

* Added `--safe-mode` flag (and `CLAUDE_CODE_SAFE_MODE`) to start Claude Code with all customizations (CLAUDE.md, plugins, skills, hooks, MCP servers) disabled for troubleshooting
**14 bug fixes**

* Fixed MCPB plugin cache being spuriously invalidated on Windows, causing unnecessary re-extraction
* Fixed plugin `.in_use` PID lock files accumulating without bound; stale markers from crashed sessions are now swept once per day
**2.1.163**

June 4, 2026

**Added**

* Added `/plugin list` command to list installed plugins, with `--enabled`/`--disabled` filters
* Skills: added `\$` escape syntax to include a literal `$` before a digit in command bodies

**Changed**

* Hooks: Stop and SubagentStop hooks can now return `hookSpecificOutput.additionalContext` to give Claude feedback and keep the turn going without being labeled a hook error
* stdio MCP servers now receive the same `CLAUDE_CODE_SESSION_ID` as hooks/Bash on `--resume`

**12 bug fixes**

* Fixed hook `if: "Bash(...)"` conditions firing on every Bash command containing `$()` or `$VAR`; the pattern now matches against commands inside subshells and backticks too
**2.1.162**

June 3, 2026

**15 bug fixes**

* Fixed MCP per-server `timeout` config values below 1000 ms being floored to a 1-second watchdog that aborted every tool call; sub-1000 ms values are now ignored (falling back to `MCP_TOOL_TIMEOUT` or default), and `claude mcp get` annotates them accordingly
* Fixed the LSP tool's `workspaceSymbol` operation returning no results; it now accepts a `query` parameter and passes it to the language server
**2.1.161**

June 2, 2026

**14 bug fixes**

* Fixed Windows hooks that invoke bash explicitly (e.g., `/usr/bin/bash script.sh`) failing with "command not found" or "cannot execute binary file"
**2.1.157**

May 29, 2026

**Added**

* Added `claude plugin init <name>` to scaffold a new plugin in `.claude/skills`

**Changed**

* Plugins in `.claude/skills` directories are now automatically loaded, no marketplace required
**2.1.154**

May 28, 2026

**Changed**

* Plugins can now declare `defaultEnabled: false` in `plugin.json` or a marketplace entry; enable them with `/plugin` or `claude plugin enable`. Dependencies of enabled plugins are still enabled automatically
* The `/plugin` Discover tab now pins plugins whose relevance signals match the current directory with a "suggested for this directory" annotation
* Stdio MCP server subprocesses now receive `CLAUDE_CODE_SESSION_ID` and `CLAUDECODE=1` in their environment
**2.1.153**

May 28, 2026

**Added**

* Added `skipLfs` option to `github`/`git` plugin marketplace sources to skip Git LFS downloads during clone and update
**2.1.152**

May 27, 2026

**Added**

* Added `/reload-skills` command to re-scan skill directories without restarting the session
* Added a `MessageDisplay` hook event that lets hooks transform or hide assistant message text as it is displayed

**Changed**

* Skills and slash commands can now set `disallowed-tools` in frontmatter to remove tools from the model while the skill is active
* `SessionStart` hooks can now return `reloadSkills: true` to re-scan skill directories, making skills installed by the hook available in the same session
* `SessionStart` hooks can now set the session title via `hookSpecificOutput.sessionTitle` on startup and resume
* `claude plugin marketplace remove` now accepts `--scope user|project|local` for symmetry with `marketplace add`, `install`, and `uninstall`

**16 bug fixes**

* Fixed plugin MCP servers with the same command but different environment variables being incorrectly deduplicated
* Fixed `/doctor` reporting "marketplace not found" or "plugin not found" for stale `enabledPlugins` entries referencing removed marketplaces or dropped plugins
* Fixed plugins that track a git branch silently no longer receiving updates after the plugin registry was rebuilt
**2.1.149**

May 22, 2026

**21 bug fixes**

* Fixed argument-hint and progressive arg suggestions not appearing after Tab-completing a skill whose frontmatter `name:` differs from its directory basename
* Fixed the status bar showing the user's baseline `/effort` setting instead of the effort level applied by skill/agent `effort:` frontmatter
**2.1.147**

May 21, 2026

**Changed**

**28 bug fixes**

* Fixed plugin agents that declare multiple `Agent(...)` types in `tools:` frontmatter dropping all but the last entry
* Fixed hook `if` conditions like `PowerShell(git push*)` never matching — only `PowerShell(*)` worked
* Fixed paginating MCP servers dropping resources, templates, and prompts past page 1
* Fixed auto mode suppressing `AskUserQuestion` when the user or a skill explicitly relies on it; the auto-mode classifier now sees the user's answers as intent signal
* Fixed plugin component counts in `claude plugin details` and `/plugin` being doubled when a plugin's manifest listed paths overlapping its default directories

**2.1.145**

May 19, 2026

**Changed**

* `/plugin` Discover and Browse screens now show a plugin's commands, agents, skills, hooks, and MCP/LSP servers before installation
* Stop and SubagentStop hook input now includes `background_tasks` and `session_crons` fields

**12 bug fixes**

* Fixed `claude plugin validate` not flagging `skills:` entries that point at a file instead of a directory — the error now suggests the parent directory
* Fixed an infinite loop where a skill using `context: fork` could repeatedly re-invoke itself instead of running

**2.1.144**

May 19, 2026

**Changed**

* The `/plugin` browse and discover panes now show when a plugin was last updated
* Plugin marketplace add/update now respects `CLAUDE_CODE_PLUGIN_PREFER_HTTPS`
* `/doctor` now shows an exec-form example when a command hook is missing the `command` field
* Skill-listing truncation is no longer shown as a startup notification — run `/doctor` for the full breakdown

**30 bug fixes**

* Fixed MCP servers with paginated `tools/list` responses only returning the first page, silently dropping tools
* Fixed MCP images with unsupported MIME types (e.g. SVG) breaking the conversation — now saved to disk and referenced in the tool result
* Fixed file descriptor exhaustion when a build runs inside a skill directory — non-`.md` files no longer trigger skill reloads
* Fixed Skill tool failing with permission error in headless mode (regression in v2.1.141)
* Fixed plugins enabled in your own settings showing "not cached" errors after first load on a fresh machine; plugins enabled only by a project's `.claude/settings.json` now show an actionable `claude plugin install` hint

**2.1.143**

May 15, 2026

**Added**

* Added plugin dependency enforcement: `claude plugin disable` now refuses when another enabled plugin depends on the target (with a copy-pasteable disable-chain hint), and `claude plugin enable` force-enables transitive dependencies
* Added projected context cost (per-turn and per-invocation token estimates) to the `/plugin` marketplace browse pane

**18 bug fixes**

* Fixed stop hooks that block repeatedly looping forever — the turn now ends with a warning after 8 consecutive blocks (override via `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`)
* Fixed `--agent <name>` not finding plugin-contributed agents without the `plugin:` prefix

**2.1.142**

May 14, 2026

**Changed**

* Plugins with a root-level `SKILL.md` and no `skills/` subdirectory are now surfaced as a skill
* The `/plugin` details pane and `claude plugin details` now show LSP servers a plugin provides

**Improved**

* Improved hook configuration error: configuring a prompt- or agent-type hook for `SessionStart`/`Setup`/`SubagentStart` now shows a clear "use a command-type hook instead" error

**16 bug fixes**

* Fixed plugins using `skills: ["./"]` showing a false "path escapes plugin directory" error
* Fixed plugin cache cleanup deleting the active plugin version directory when no installation metadata is present
* Fixed `/plugin` browse pane showing "0 installs" for newly published plugins
* Fixed plugin advisories not naming every `plugin.json` key that shadows a default folder

**2.1.141**

May 13, 2026

**Added**

* Added `terminalSequence` field to hook JSON output so hooks can emit desktop notifications, window titles, and bells without a controlling terminal
* Added `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` to clone GitHub plugin sources over HTTPS instead of SSH, for environments without a GitHub SSH key

**44 bug fixes**

* Fixed hooks receiving a non-existent `transcript_path` after `EnterWorktree` switches the working directory
* Fixed `claude plugin install` failing for plugins whose marketplace `ref` no longer exists upstream when a `sha` is also pinned
* Fixed plugin details pane showing 0 MCP servers for plugins that declare them via `.mcp.json`
* Fixed plugin MCP servers with unset config variables showing a generic connection failure instead of a "config issue" message with a fix-it hint; malformed `.mcp.json` entries no longer drop other MCP servers
* Fixed MCP server configs using POSIX shell parameter expansions (e.g. `${var%pattern}`) being incorrectly flagged as missing environment variables

**2.1.140**

May 12, 2026

**Changed**

* Plugins now warn when a default component folder (e.g. `commands/`) is silently ignored because `plugin.json` sets the matching key. Shown in `/doctor`, `claude plugin list`, and `/plugin`.

**Improved**

* Improved Agent tool `subagent_type` matching to accept case- and separator-insensitive values (e.g. `"Code Reviewer"` resolves to `code-reviewer`)

**2.1.139**

May 11, 2026

**Added**

* Added `claude plugin details <name>` to show a plugin's component inventory and projected per-session token cost
* Added hook `args: string[]` field (exec form) that spawns the command directly without a shell, so path placeholders never need quoting
* Added hook `continueOnBlock` config option for `PostToolUse` — set to `true` to feed the hook's rejection reason back to Claude and continue the turn

**Changed**

* MCP stdio servers now receive `CLAUDE_PROJECT_DIR` in their environment, matching hooks. Plugin configs can reference `${CLAUDE_PROJECT_DIR}` in commands
* `/context all` per-skill token estimates now account for the model's tokenizer and show rounded values
* `claude plugin install <name>@<marketplace>` now auto-refreshes the marketplace and retries before reporting a plugin as not found
* `/plugin` installed-plugin details now show hook event names and MCP server names cleanly
* `/context` now shows the providing plugin's name for plugin-sourced skills

**32 bug fixes**

* Fixed a bug where a hook writing to the terminal could corrupt an on-screen interactive prompt; hooks now run without terminal access
* Fixed `Skill(name *)` permission rules — the wildcard form now works as a prefix match, matching `Bash(ls *)` behavior
* Fixed plugin details failing to load when the marketplace key differs from the manifest name
* Fixed skill argument names containing regex metacharacters breaking argument substitution
* Fixed plugin dependency resolution leaving a stale count when the manifest name differs from the source identifier
* Fixed `claude plugin update` not preserving cross-plugin symlinks inside a marketplace

**2.1.136**

May 8, 2026

**46 bug fixes**

* Fixed MCP servers configured in `.mcp.json`, plugins, and claude.ai connectors silently disappearing after `/clear` in the VS Code extension, JetBrains plugin, and Agent SDK
* Fixed plugin `Stop`/`UserPromptSubmit` hooks failing when cache cleanup deletes a version still in use by a running session
* Fixed a `skills` entry in `plugin.json` hiding the plugin's default `skills/` directory, and listing a file path now shows an error instead of failing silently
* Fixed plugin uninstall and enable/disable not matching slugs case-insensitively
* Fixed env vars from `CLAUDE_ENV_FILE` SessionStart hooks going stale after `/resume` or `/clear`
* Fixed plugin slash commands with spaces (e.g. `/myplugin review`) not resolving to their namespaced form
* Fixed MCP tool results being invisible when the server returns content blocks

**2.1.133**

May 7, 2026

**Changed**

* Hooks now receive the active effort level via the `effort.level` JSON input field and the `$CLAUDE_EFFORT` environment variable, and Bash tool commands can read `$CLAUDE_EFFORT`

**10 bug fixes**

* Fixed subagents not discovering project, user, or plugin skills via the Skill tool

**2.1.129**

May 6, 2026

**Changed**

* Plugin manifests: `themes` and `monitors` should now be declared under `"experimental": { ... }`. Top-level declarations still work but `claude plugin validate` will warn
* `skillOverrides` setting now works: `off` hides from model and `/`, `user-invocable-only` hides from model only, `name-only` collapses description

**2.1.128**

May 4, 2026

**Changed**

* `--channels` now works with console (API key) authentication — console orgs with managed settings must set `channelsEnabled: true` to enable
* MCP: `workspace` is now a reserved server name — existing servers with that name will be skipped with a warning
* Headless `--output-format stream-json`: `init.plugin_errors` now includes `--plugin-dir` load failures in addition to dependency demotions

**25 bug fixes**

* Fixed `/plugin` Components panel showing "Marketplace 'inline' not found" for plugins loaded via `--plugin-dir`
* Fixed stale `installed_plugins.json` entries pointing at deleted cache directories polluting PATH

**2.1.126**

May 1, 2026

**19 bug fixes**

* Fixed deferred tools (WebSearch, WebFetch, etc.) not being available to skills with `context: fork` and other subagents on their first turn

**2.1.121**

April 28, 2026

**Added**

* Added `alwaysLoad` option to MCP server config — when `true`, all tools from that server skip tool-search deferral and are always available
* Added `claude plugin prune` to remove orphaned auto-installed plugin dependencies; `plugin uninstall --prune` cascades

**Changed**

* PostToolUse hooks can now replace tool output for all tools via `hookSpecificOutput.updatedToolOutput` (previously MCP-only)

**2.1.120**

April 28, 2026

**Changed**

* Skills can now reference the current effort level with `${CLAUDE_EFFORT}` in their content
* `claude plugin validate` now accepts `$schema`, `version`, and `description` at the top level of `marketplace.json` and `$schema` in `plugin.json`

**10 bug fixes**

* Fixed `/plugin` marketplace failing to load when one entry uses an unrecognized source format — that entry is shown but installing it prompts you to update

**2.1.119**

April 23, 2026

**Changed**

* `--print` mode now honors the agent's `tools:` and `disallowedTools:` frontmatter, matching interactive-mode behavior
* Hooks: `PostToolUse` and `PostToolUseFailure` hook inputs now include `duration_ms` (tool execution time, excluding permission prompts and PreToolUse hooks)
* Plugins pinned by another plugin's version constraint now auto-update to the highest satisfying git tag
* Security: `blockedMarketplaces` now correctly enforces `hostPattern` and `pathPattern` entries

**32 bug fixes**

* Fixed async `PostToolUse` hooks that emit no response payload writing empty entries to the session transcript
* Fixed `${ENV_VAR}` placeholders in `headers` for HTTP/SSE/WebSocket MCP servers not being substituted before requests
* Fixed MCP servers from plugins not spawning on Windows when the plugin cache was incomplete
* Fixed plugin MCP servers failing when `${user_config.*}` references an optional field left blank
* Fixed skills invoked before auto-compaction being re-executed against the next user message
* Fixed `/reload-plugins` and `/doctor` reporting load errors for disabled plugins

**2.1.118**

April 23, 2026

**Added**

* Added `claude plugin tag` to create release git tags for plugins with version validation

**Changed**

* Create and switch between named custom themes from `/theme`, or hand-edit JSON files in `~/.claude/themes/`; plugins can also ship themes via a `themes/` directory
* Hooks can now invoke MCP tools directly via `type: "mcp_tool"`
* When auto-update skips a plugin due to another plugin's version constraint, the skip now appears in `/doctor` and the `/plugin` Errors tab

**21 bug fixes**

* Fixed agent-type hooks failing with "Messages are required for agent hooks" when configured for events other than `Stop` or `SubagentStop`
* Fixed `prompt` hooks re-firing on tool calls made by an agent-hook verifier subagent
* Fixed `plugin install` on an already-installed plugin not re-resolving a dependency installed at the wrong version

**2.1.117**

April 22, 2026

**Changed**

* `plugin install` on an already-installed plugin now installs any missing dependencies instead of stopping at "already installed"
* Plugin dependency errors now say "not installed" with an install hint, and `claude plugin marketplace add` now auto-resolves missing dependencies from configured marketplaces
* Managed-settings `blockedMarketplaces` and `strictKnownMarketplaces` are now enforced on plugin install, update, refresh, and autoupdate

**14 bug fixes**

* \[VSCode] Fixed "Manage Plugins" panel breaking when multiple large marketplaces are configured

**2.1.116**

April 20, 2026

**Changed**

* `/reload-plugins` and background plugin auto-update now auto-install missing plugin dependencies from marketplaces you've already added

**2.1.113**

April 17, 2026

**22 bug fixes**

* Fixed `plugin install` succeeding when a dependency version conflicts with an already-installed plugin — now reports `range-conflict`
**2.1.111**

April 16, 2026

**Changed**

* Headless `--output-format stream-json` now includes `plugin_errors` on the init event when plugins are demoted for unsatisfied dependencies
* Windows: `CLAUDE_ENV_FILE` and SessionStart hook environment files now apply (previously a no-op)

**Improved**

* Improved plugin error handling: dependency errors now distinguish conflicting, invalid, and overly complex version requirements; fixed stale resolved versions after `plugin update`; `plugin install` now recovers from interrupted prior installs

**2.1.110**

April 15, 2026

**19 bug fixes**

* Fixed plugin install not honoring dependencies declared in `plugin.json` when the marketplace entry omits them; `/plugin` install now lists auto-installed dependencies
* Fixed skills with `disable-model-invocation: true` failing when invoked via `/<skill>` mid-message
* Fixed `PermissionRequest` hooks returning `updatedInput` not being re-checked against `permissions.deny` rules; `setMode:'bypassPermissions'` updates now respect `disableBypassPermissionsMode`
* Fixed `PreToolUse` hook `additionalContext` being dropped when the tool call fails

**2.1.105**

April 13, 2026

**Added**

* Added PreCompact hook support: hooks can now block compaction by exiting with code 2 or returning `{"decision":"block"}`
* Added background monitor support for plugins via a top-level `monitors` manifest key that auto-arms at session start or on skill invoke

**9 improvements**

* Improved skill description handling: raised the listing cap from 250 to 1,536 characters and added a startup warning when descriptions are truncated

**24 bug fixes**

* Fixed marketplace plugins with `package.json` and lockfile not having dependencies installed automatically after install/update

**2.1.101**

April 10, 2026

**12 improvements**

* Improved plugin hooks from plugins force-enabled by managed settings to run when `allowManagedHooksOnly` is set
* Improved `/plugin` and `claude plugin update` to show a warning when the marketplace could not be refreshed, instead of silently reporting a stale version
**31 bug fixes**

* Fixed several plugin issues: slash commands resolving to the wrong plugin with duplicate `name:` frontmatter, `/plugin update` failing with `ENAMETOOLONG`, Discover showing already-installed plugins, directory-source plugins loading from a stale version cache, and skills not honoring `context: fork` and `agent` frontmatter fields

**2.1.98**

April 9, 2026

**Changed**

* LSP: Claude Code now identifies itself to language servers via `clientInfo` in the initialize request

**9 improvements**

* Improved `/reload-plugins` to pick up plugin-provided skills without requiring a restart
* Improved hook errors in the transcript to include the first line of stderr for self-diagnosis without `--debug`

**38 bug fixes**

* Fixed slash command picker breaking when a plugin's frontmatter `name` is a YAML boolean keyword
* Fixed prompt-type Stop/SubagentStop hooks failing on long sessions, and hook evaluator API errors showing "JSON validation failed" instead of the real message

**2.1.97**

April 8, 2026

**28 bug fixes**

* Fixed prompt-type `Stop`/`SubagentStop` hooks failing on long sessions, and hook evaluator API errors displaying "JSON validation failed" instead of the actual message
* Fixed `claude plugin update` reporting "already at the latest version" for git-based marketplace plugins when the remote had newer commits
* Fixed slash command picker breaking when a plugin's frontmatter `name` is a YAML boolean keyword
**2.1.94**

April 7, 2026

**Added**

* Added `keep-coding-instructions` frontmatter field support for plugin output styles
* Added `hookSpecificOutput.sessionTitle` to `UserPromptSubmit` hooks for setting the session title

**Changed**

* Plugin skills declared via `"skills": ["./"]` now use the skill's frontmatter `name` for the invocation name instead of the directory basename, giving a stable name across install methods

**16 bug fixes**

* Fixed plugin skill hooks defined in YAML frontmatter being silently ignored
* Fixed plugin hooks failing with "No such file or directory" when `CLAUDE_PLUGIN_ROOT` was not set
* Fixed `${CLAUDE_PLUGIN_ROOT}` resolving to the marketplace source directory instead of the installed cache for local-marketplace plugins on startup

**2.1.92**

April 4, 2026

**11 bug fixes**

* Fixed prompt-type Stop hooks incorrectly failing when the small fast model returns `ok:false`, and restored `preventContinuation:true` semantics for non-Stop prompt-type hooks
* Fixed plugin MCP servers stuck "connecting" on session start when they duplicate a claude.ai connector that is unauthenticated

**2.1.91**

April 2, 2026

**Added**

* Added `disableSkillShellExecution` setting to disable inline shell execution in skills, custom slash commands, and plugin commands

**Changed**

* Plugins can now ship executables under `bin/` and invoke them as bare commands from the Bash tool

**2.1.90**

April 1, 2026

**Added**

* Added `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` env var to keep the existing marketplace cache when `git pull` fails, useful in offline environments

**9 bug fixes**

* Fixed `Edit`/`Write` failing with "File content has changed" when a PostToolUse format-on-save hook rewrites the file between consecutive edits
* Fixed `PreToolUse` hooks that emit JSON to stdout and exit with code 2 not correctly blocking the tool call

**2.1.89**

April 1, 2026

**Added**

* Added `"defer"` permission decision to `PreToolUse` hooks — headless sessions can pause at a tool call and resume with `-p --resume` to have the hook re-evaluate
* Added `PermissionDenied` hook that fires after auto mode classifier denials — return `{retry: true}` to tell the model it can retry

**Changed**

* Changed hook output over 10,000 characters to be saved to disk with a file path + a 2,000-character preview instead of being injected directly into context
* Documented `TaskCreated` hook event and its blocking behavior

**30 bug fixes**

* Fixed LSP server zombie state after crash — server now restarts on next request instead of failing until session restart
* Fixed PreToolUse/PostToolUse hooks to receive `file_path` as an absolute path for Write/Edit/Read tools, matching the documented behavior
* Fixed hooks `if` condition filtering not matching compound commands (`ls && git push`) or commands with env-var prefixes (`FOO=bar git push`)
**2.1.86**

March 27, 2026

**16 bug fixes**

* Fixed `/plugin` uninstall dialog: pressing `n` now correctly uninstalls the plugin while preserving its data directory

**2.1.85**

March 26, 2026

**Added**

* Added conditional `if` field for hooks using permission rule syntax (e.g., `Bash(git *)`) to filter when they run, reducing process spawning overhead

**Changed**

* Plugins blocked by organization policy (`managed-settings.json`) can no longer be installed or enabled, and are hidden from marketplace views
* PreToolUse hooks can now satisfy `AskUserQuestion` by returning `updatedInput` alongside `permissionDecision: "allow"`, enabling headless integrations that collect answers via their own UI

**17 bug fixes**

* Fixed `/plugin enable` and `/plugin disable` failing when a plugin's install location differs from where it's declared in settings
* Fixed `--worktree` exiting with an error in non-git repositories before the `WorktreeCreate` hook could run

**2.1.84**

March 26, 2026

**Added**

* Added `TaskCreated` hook that fires when a task is created via `TaskCreate`
* Added `WorktreeCreate` hook support for `type: "http"` — return the created worktree path via `hookSpecificOutput.worktreePath` in the response JSON
* Added `allowedChannelPlugins` managed setting for team/enterprise admins to define a channel plugin allowlist

**Changed**

* Rules and skills `paths:` frontmatter now accepts a YAML list of globs
* MCP tool descriptions and server instructions are now capped at 2KB to prevent OpenAPI-generated servers from bloating context

**2.1.83**

March 25, 2026

**Added**

* Added `CwdChanged` and `FileChanged` hook events for reactive environment management (e.g., direnv)
* Added `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` to strip Anthropic and cloud provider credentials from subprocess environments (Bash tool, hooks, MCP stdio servers)

**Changed**

* Agents can now declare `initialPrompt` in frontmatter to auto-submit a first turn
* Plugin MCP servers that duplicate an org-managed connector are now suppressed instead of running a second connection
* Plugin options (`manifest.userConfig`) now available externally — plugins can prompt for configuration at enable time, with `sensitive: true` values stored in keychain (macOS) or protected credentials file (other platforms)

**5 improvements**

* Improved plugin startup — commands, skills, and agents now load from disk cache without re-fetching

**41 bug fixes**

* Fixed uninstalled plugin hooks continuing to fire until the next session

**2.1.81**

March 20, 2026

**Added**

* Added `--bare` flag for scripted `-p` calls — skips hooks, LSP, plugin sync, and skill directory walks; requires `ANTHROPIC_API_KEY` or an `apiKeyHelper` via `--settings` (OAuth and keychain auth disabled); auto-memory fully disabled

**Improved**

* Improved plugin freshness — ref-tracked plugins now re-clone on every load to pick up upstream changes

**17 bug fixes**

* Fixed plugin hooks blocking prompt submission when the plugin directory is deleted mid-session

**2.1.80**

March 19, 2026

**Added**

* Added CLI tool usage detection to plugin tips, in addition to file pattern matching
* Added `effort` frontmatter support for skills and slash commands to override the model effort level when invoked

**Changed**

* Simplified plugin install tips to use a single `/plugin install` command instead of a two-step flow

**6 bug fixes**

* Fixed managed settings (`enabledPlugins`, `permissions.defaultMode`, policy-set env vars) not being applied at startup when `remote-settings.json` was cached from a prior session

**2.1.79**

March 18, 2026

**11 bug fixes**

* Fixed `SessionEnd` hooks not firing when using interactive `/resume` to switch sessions

**2.1.78**

March 17, 2026

**Added**

* Added `StopFailure` hook event that fires when the turn ends due to an API error (rate limit, auth failure, etc.)
* Added `${CLAUDE_PLUGIN_DATA}` variable for plugin persistent state that survives plugin updates; `/plugin uninstall` prompts before deleting it
* Added `effort`, `maxTurns`, and `disallowedTools` frontmatter support for plugin-shipped agents

**19 bug fixes**

* Fixed infinite loop when API errors triggered stop hooks that re-fed blocking errors to the model
* Fixed `--worktree` flag not loading skills and hooks from the worktree directory

**2.1.77**

March 17, 2026

**Improved**

* Improved `claude plugin validate` to check skill, agent, and command frontmatter plus `hooks/hooks.json`, catching YAML parse errors and schema violations

**28 bug fixes**

* Fixed PreToolUse hooks returning `"allow"` bypassing `deny` permission rules, including enterprise managed settings
* Fixed `git-subdir` plugins at different subdirectories of the same monorepo commit colliding in the plugin cache

**2.1.76**

March 14, 2026

**Added**

* Added MCP elicitation support — MCP servers can now request structured input mid-task via an interactive dialog (form fields or browser URL)
* Added new `Elicitation` and `ElicitationResult` hooks to intercept and override responses before they're sent back
* Added `PostCompact` hook that fires after compaction completes

**Changed**

* Updated `--plugin-dir` to only accept one path to support subcommands — use repeated `--plugin-dir` for multiple directories

**20 bug fixes**

* Fixed spurious "Context limit reached" when invoking a skill with `model:` frontmatter on a 1M-context session
* Fixed LSP plugins not registering servers when the LSP Manager initialized before marketplaces were reconciled

**2.1.75**

March 13, 2026

**Added**

* Added hook source display (settings/plugin/skill) in permission prompts when a hook requires confirmation

**Changed**

* Suppressed async hook completion messages by default (visible with `--verbose` or transcript mode)

**11 bug fixes**

* Fixed managed-disabled plugins showing up in the `/plugin` Installed tab — plugins force-disabled by your organization are now hidden
* Fixed corrupted marketplace config path handling

**2.1.74**

March 12, 2026

**Changed**

* Changed `--plugin-dir` so local dev copies now override installed marketplace plugins with the same name (unless that plugin is force-enabled by managed settings)

**13 bug fixes**

* Fixed managed policy `ask` rules being bypassed by user `allow` rules or skill `allowed-tools`
* Fixed full model IDs (e.g., `claude-opus-4-5`) being silently ignored in agent frontmatter `model:` field and `--agents` JSON config — agents now accept the same model values as `--model`
* Fixed `SessionEnd` hooks being killed after 1.5 s on exit regardless of `hook.timeout` — now configurable via `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`
* Fixed `/plugin install` failing inside the REPL for marketplace plugins with local sources
* Fixed marketplace update not syncing git submodules — plugin sources in submodules no longer break after update

**2.1.73**

March 11, 2026

**16 bug fixes**

* Fixed SessionStart hooks firing twice when resuming a session via `--resume` or `--continue`
* Fixed JSON-output hooks injecting no-op system-reminder messages into the model's context on every turn

**2.1.72**

March 10, 2026

**6 improvements**

* Improved marketplace clone failure messages to show diagnostic info even when git produces no stderr

**33 bug fixes**

* Fixed skill hooks firing twice per event when a hooks-enabled skill is invoked by the model
* Fixed several plugin issues: installation failing on Windows with `EEXIST` error in OneDrive folders, marketplace blocking user-scope installs when a project-scope install exists, `CLAUDE_CODE_PLUGIN_CACHE_DIR` creating literal `~` directories, and `plugin.json` with marketplace-only fields failing to load
* Fixed several hooks issues: `transcript_path` pointing to the wrong directory for resumed/forked sessions, agent `prompt` being silently deleted from settings.json on every settings write, PostToolUse block reason displaying twice, async hooks not receiving stdin with bash `read -r`, and validation error message showing an example that fails validation

**2.1.71**

March 7, 2026

**Improved**

* Improved `/plugin uninstall` to disable project-scoped plugins in `.claude/settings.local.json` instead of modifying `.claude/settings.json`, so changes don't affect teammates
* Improved plugin-provided MCP server deduplication — servers that duplicate a manually-configured server (same command/URL) are now skipped, preventing duplicate connections and tool sets. Suppressions are shown in the `/plugin` menu.

**18 bug fixes**

* Fixed plugin installations being lost when running multiple Claude Code instances
* Fixed `/plugin marketplace update` failing with merge conflicts when the marketplace is pinned to a branch/tag ref
* Fixed `/plugin marketplace add owner/repo@ref` incorrectly parsing `@` — previously only `#` worked as a ref separator, causing undiagnosable errors with `strictKnownMarketplaces`

**2.1.70**

March 6, 2026

**20 bug fixes**

* Fixed plugins showing as inaccurately installed in `/plugin`
* Fixed plugins showing "not found in marketplace" errors on fresh startup by auto-refreshing after marketplace installation

**2.1.69**

March 5, 2026

**Added**

* Added `/reload-plugins` command to activate pending plugin changes without restarting
* Added `${CLAUDE_SKILL_DIR}` variable for skills to reference their own directory in SKILL.md content
* Added `InstructionsLoaded` hook event that fires when CLAUDE.md or `.claude/rules/*.md` files are loaded into context
* Added `agent_id` (for subagents) and `agent_type` (for subagents and `--agent`) to hook events
* Added plugin source type `git-subdir` to point to a subdirectory within a git repo
* Added `oauth.authServerMetadataUrl` config option for MCP servers to specify a custom OAuth metadata discovery URL when standard discovery fails

**58 bug fixes**

* Fixed plugin Stop/SessionEnd/etc hooks not firing after any `/plugin` operation
* Fixed plugin hooks being silently dropped when two plugins use the same `${CLAUDE_PLUGIN_ROOT}/...` command template
* Fixed interactive tools (e.g., `AskUserQuestion`) being silently auto-allowed when listed in a skill's allowed-tools, bypassing the permission prompt and running with empty answers
* Fixed `TeammateIdle` and `TaskCompleted` hooks to support `{"continue": false, "stopReason": "..."}` to stop the teammate, matching `Stop` hook behavior
* Fixed `WorktreeCreate` and `WorktreeRemove` plugin hooks being silently ignored
* Fixed skill descriptions with colons (e.g., "Triggers include: X, Y, Z") failing to load from SKILL.md frontmatter
* Fixed project skills without a `description:` frontmatter field not appearing in Claude's available skills list

**2.1.63**

February 28, 2026

**Added**

* Added HTTP hooks, which can POST JSON to a URL and receive JSON instead of running a shell command

**2.1.51**

February 24, 2026

**Changed**

* Updated plugin marketplace default git timeout from 30s to 120s and added `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` to configure.

**Fixed**

* Fixed slash command autocomplete crashing when a plugin's SKILL.md description is a YAML array or other non-string type

**2.1.50**

February 20, 2026

**Added**

* Added support for `startupTimeout` configuration for LSP servers
* Added `WorktreeCreate` and `WorktreeRemove` hook events, enabling custom VCS setup and teardown when agent worktree isolation creates or removes worktrees.
* Added support for `isolation: worktree` in agent definitions, allowing agents to declaratively run in isolated git worktrees.

**2.1.49**

February 19, 2026

**Added**

* Added `ConfigChange` hook event that fires when configuration files change during a session, enabling enterprise security auditing and optional blocking of settings changes.

**Changed**

* Subagents support `isolation: "worktree"` for working in a temporary git worktree
* Agent definitions support `background: true` to always run as a background task
* Plugins can ship `settings.json` for default configuration

**10 bug fixes**

* Fixed `plugin enable` and `plugin disable` to auto-detect the correct scope when `--scope` is not specified, instead of always defaulting to user scope
* Fixed `disableAllHooks` setting to respect managed settings hierarchy — non-managed settings can no longer disable managed hooks set by policy (#26637)

**2.1.47**

February 18, 2026

**Added**

* Added `last_assistant_message` field to Stop and SubagentStop hook inputs, providing the final assistant response text so hooks can access it without parsing transcript files.
**53 bug fixes**

* Fixed plugin agent skills silently failing to load when referenced by bare name instead of fully-qualified plugin name (anthropics/claude-code#25834)
* Fixed crash when a skill's `name` or `description` in SKILL.md frontmatter is a bare number (e.g., `name: 3000`) — the value is now properly coerced to a string (anthropics/claude-code#25837)
* Fixed React crash (error #31) when a skill's `argument-hint` in SKILL.md frontmatter uses YAML sequence syntax (e.g., `[topic: foo | bar]`) — the value is now properly coerced to a string (anthropics/claude-code#25826)
* Fixed non-interactive subcommands like `claude doctor` and `claude plugin validate` being blocked inside nested Claude sessions (anthropics/claude-code#25803)
* Fixed hooks (PreToolUse, PostToolUse) silently failing to execute on Windows by using Git Bash instead of cmd.exe (anthropics/claude-code#25981)

**2.1.45**

February 17, 2026

**Added**

* Added support for reading `enabledPlugins` and `extraKnownMarketplaces` from `--add-dir` directories

**7 bug fixes**

* Fixed plugin-provided commands, agents, and hooks not being available immediately after installation without requiring a restart

**2.1.41**

February 13, 2026

**15 bug fixes**

* Fixed hook blocking errors (exit code 2) not showing stderr to the user
* Fixed hook blocking errors showing stderr content in UI

**2.1.33**

February 6, 2026

**Added**

* Added `TeammateIdle` and `TaskCompleted` hook events for multi-agent workflows
* Added support for restricting which sub-agents can be spawned via `Task(agent_type)` syntax in agent "tools" frontmatter
* Added `memory` frontmatter field support for agents, enabling persistent memory with `user`, `project`, or `local` scope
* Added plugin name to skill descriptions and `/skills` menu for better discoverability

**2.1.32**

February 5, 2026

**Changed**

* Skill character budget now scales with context window (2% of context), so users with larger context windows can see more skill descriptions without truncation

**2.1.20**

January 27, 2026

**12 bug fixes**

* Fixed marketplace source removal not properly deleting settings

**2.1.19**

January 23, 2026

**Added**

* Added shorthand `$0`, `$1`, etc. for accessing individual arguments in custom commands

**Changed**

* Changed skills without additional permissions or hooks to be allowed without requiring approval
* Changed indexed argument syntax from `$ARGUMENTS.0` to `$ARGUMENTS[0]` (bracket syntax)

**8 bug fixes**

* Fixed backgrounded hook commands not returning early, potentially causing the session to wait on a process that was intentionally backgrounded

**2.1.16**

January 22, 2026

* \[VSCode] Added native plugin management support

**2.1.14**

January 20, 2026

**Added**

* Added search to installed plugins list - type to filter by name or description
* Added support for pinning plugins to specific git commit SHAs, allowing marketplace entries to install exact versions

**2.1.10**

January 17, 2026

* Added new `Setup` hook event that can be triggered via `--init`, `--init-only`, or `--maintenance` CLI flags for repository setup and maintenance operations

**2.1.9**

January 16, 2026

* Added support for `PreToolUse` hooks to return `additionalContext` to the model
* Added `${CLAUDE_SESSION_ID}` string substitution for skills to access the current session ID

**2.1.7**

January 14, 2026

**9 bug fixes**

* Fixed plugins with git submodules not being fully initialized when installed

**2.1.3**

January 9, 2026

**Changed**

* Merged slash commands and skills, simplifying the mental model with no change in behavior
* Changed tool hook execution timeout from 60 seconds to 10 minutes

**2.1.2**

January 9, 2026

**Added**

* Added `FORCE_AUTOUPDATE_PLUGINS` environment variable to allow plugin autoupdate even when the main auto-updater is disabled
* Added `agent_type` to SessionStart hook input, populated if `--agent` is specified

**2.1.0**

January 7, 2026

**Added**

* Added support for running skills and slash commands in a forked sub-agent context using `context: fork` in skill frontmatter
* Added support for `agent` field in skills to specify agent type for execution
* Added hooks support to agent frontmatter, allowing agents to define PreToolUse, PostToolUse, and Stop hooks scoped to the agent's lifecycle
* Added hooks support for skill and slash command frontmatter
* Added support for `once: true` config for hooks
* Added support for YAML-style lists in frontmatter `allowed-tools` field for cleaner skill declarations
* Added support for prompt and agent hook types from plugins (previously only command hooks were supported)

**19 improvements**

* Improved skills from `/skills/` directories to be visible in the slash command menu by default (opt-out with `user-invocable: false` in frontmatter)

**54 bug fixes**

* Fixed PreToolUse hooks to allow `updatedInput` when returning `ask` permission decision, enabling hooks to act as middleware while still requesting user consent
* Fixed `${CLAUDE_PLUGIN_ROOT}` not being substituted in plugin `allowed-tools` frontmatter, which caused tools to incorrectly require approval

**2.0.74**

December 19, 2025

**Added**

* Added LSP (Language Server Protocol) tool for code intelligence features like go-to-definition, find references, and hover documentation

**6 bug fixes**

* Fixed skill `allowed-tools` not being applied to tools invoked by the skill

**2.0.70**

December 15, 2025

**Added**

* Added auto-update toggle for plugin marketplaces, allowing per-marketplace control over automatic updates

**2.0.67**

December 12, 2025

**7 bug fixes**

* Windows: Fixed plugin MCP servers failing due to colons in log directory paths

**2.0.59**

December 4, 2025

* Added `agent` setting to configure main thread with a specific agent's system prompt, tool restrictions, and model

**2.0.54**

November 26, 2025

* Hooks: Enable PermissionRequest hooks to process 'always allow' suggestions and apply permission updates

**2.0.45**

November 18, 2025

* Added `PermissionRequest` hook to automatically approve or deny tool permission requests with custom logic

**2.0.43**

November 18, 2025

* Added `permissionMode` field for custom agents
* Added `tool_use_id` field to `PreToolUseHookInput` and `PostToolUseHookInput` types
* Added skills frontmatter field to declare skills to auto-load for subagents
* Added the `SubagentStart` hook event

**2.0.42**

November 15, 2025

* Added `agent_id` and `agent_transcript_path` fields to `SubagentStop` hooks.

**2.0.41**

November 14, 2025

**Added**

* Added `model` parameter to prompt-based stop hooks, allowing users to specify a custom model for hook evaluation
* Plugins: Added support for sharing and installing output styles

**6 bug fixes**

* Fixed crash when plugin command hooks timeout during execution

**2.0.37**

November 11, 2025

* Hooks: Added matcher values for Notification hook events
* Output Styles: Added `keep-coding-instructions` option to frontmatter

**2.0.32**

November 4, 2025

* Un-deprecate output styles based on community feedback
* Fixed hook progress messages not updating correctly during PostToolUse hook execution

**2.0.31**

October 31, 2025

* Fixed plugin uninstall not removing plugins

**2.0.30**

October 30, 2025

**Added**

* Added `disallowedTools` field to custom agent definitions for explicit tool blocking
* Added prompt-based stop hooks

**7 bug fixes**

* Fixed hooks and plugins not executing when using --dangerously-skip-permissions flag

**2.0.28**

October 27, 2025

* Add branch and tag support for git-based plugins and marketplaces using fragment syntax (e.g., `owner/repo#branch`)

**2.0.22**

October 17, 2025

* Add support for enterprise managed MCP allowlist and denylist

**2.0.20**

October 16, 2025

* Added support for Claude Skills

**2.0.12**

October 9, 2025

**Changed**

* **Plugin System Released**: Extend Claude Code with custom commands, agents, hooks, and MCP servers from marketplaces
* `/plugin install`, `/plugin enable/disable`, `/plugin marketplace` commands for plugin management
* Repository-level plugin configuration via `extraKnownMarketplaces` for team collaboration
* `/plugin validate` command for validating plugin structure and configuration

**2.0.10**

October 8, 2025

* PreToolUse hooks can now modify tool inputs

**1.0.112**

September 12, 2025

* Hooks: Added systemMessage support for SessionEnd hooks

**1.0.85**

August 19, 2025

* Hooks: Introduced SessionEnd hook

**1.0.68**

August 4, 2025

* Added `disableAllHooks` setting

**1.0.64**

July 30, 2025

* Agents: Added model customization support - you can now specify which model an agent should use
* Hooks: Added systemMessage field to hook JSON output for displaying warnings and context

**1.0.62**

July 28, 2025

* Hooks: Added SessionStart hook for new session initialization

**1.0.60**

July 24, 2025

* You can now create custom subagents for specialized tasks! Run /agents to get started

**1.0.59**

July 23, 2025

* Hooks: Exposed PermissionDecision to hooks (including "ask")
* Hooks: UserPromptSubmit now supports additionalContext in advanced JSON output

**1.0.58**

July 23, 2025

* Hooks: Added CLAUDE\_PROJECT\_DIR env var for hook commands

**1.0.57**

July 23, 2025

* Added support for specifying a model in slash commands

**1.0.54**

July 19, 2025

* Hooks: Added UserPromptSubmit hook and the current working directory to hook inputs
* Custom slash commands: Added argument-hint to frontmatter

**1.0.48**

July 10, 2025

* Added expanding variables support for MCP server configuration
* Hooks: Added a PreCompact hook

**1.0.45**

July 10, 2025

* Custom slash commands: Restored namespacing in command names based on subdirectories. For example, .claude/commands/frontend/component.md is now /frontend:component, not /component.

**1.0.41**

July 3, 2025

* Hooks: Split Stop hook triggering into Stop and SubagentStop
* Hooks: Enabled optional timeout configuration for each command
* Hooks: Added "hook\_event\_name" to hook input

**1.0.38**

June 30, 2025

* Released hooks. Special thanks to community input in [https://github.com/anthropics/claude-code/issues/712](https://github.com/anthropics/claude-code/issues/712). Docs: [https://code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks.md)

**1.0.30**

June 24, 2025

* Custom slash commands: Run bash output, @-mention files, enable thinking with thinking keywords

**1.0.27**

June 18, 2025

* Streamable HTTP MCP servers are now supported
