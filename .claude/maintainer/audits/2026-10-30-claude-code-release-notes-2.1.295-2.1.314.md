# Claude Code release notes 2.1.295 to 2.1.314: entries on mods, plugins, LSP, MCP, rules, CLAUDE.md, marketplace, skills, test, plugin.json, hooks and tools

## Source and method

- **Repository:** `anthropics/claude-code`, read only through the GitHub MCP server (`github-operations` plugin): `list_releases` with release bodies, `get_release_by_tag`, `list_tags`, and the MCP resource `repo://anthropics/claude-code/sha/b3f291d131924810e2b7713ededc144843a229d5/contents/CHANGELOG.md` (the CHANGELOG at the `v2.1.314` commit, blob SHA `d4e57ac0e7cf114b3868dcb227619c325f6f1cd5`).
- **Two sources, compared:** each release body and its `## <version>` section of `CHANGELOG.md` hold the same entries, in the same order, for all 17 versions that exist.
- **Text:** every entry is copied verbatim from the release body, by script, with no rewording. The `[patch:position]` id is the entry's 1-based position in its release (`[299:128]` is the 128th entry of 2.1.299).
- **Inclusion rule 1, keywords.** An entry is listed when its text contains one of: mod, plugin, LSP (or language server), MCP, rule, CLAUDE.md, marketplace, skill, test (tests, testing, tested), plugin.json, hook, tool. Plural forms count, and so do identifiers split into words (`enabledMcpjsonServers` counts as MCP, `PreToolUse` as tool, `disableAllHooks` as hooks). The tag after each entry names the keywords it matched.
- **Inclusion rule 2, named tool.** An entry is also listed when it names a built-in Claude Code tool (Read, Edit, Write, NotebookEdit, Bash, PowerShell, Grep, Glob, WebFetch, WebSearch, AskUserQuestion, PushNotification, SendMessage, TaskStop, ScheduleWakeup, Workflow, Agent card) as the subject of the change, without the word "tool". Its tag is `tools (named tool)`.
- **Reviewed and not listed:** entries that only concern subagents, managed settings, the VS Code extension, Cloud sessions, Claude Tag, Code Review, the Claude apps gateway, sandboxing or terminal rendering match no requested topic. Entries that touch a requested topic without using its keyword or a tool name are in Appendix B for Nery to rule on.

## Coverage

| Version | Published (UTC) | Entries in the release | Listed by keyword | Listed by named tool | Total listed |
| :-- | :-- | --: | --: | --: | --: |
| 2.1.295 | 2026-10-08 19:48 | 143 | 64 | 7 | 71 |
| 2.1.296 | 2026-10-09 19:28 | 79 | 33 | 2 | 35 |
| 2.1.297 | none | none | none | none | none |
| 2.1.298 | none | none | none | none | none |
| 2.1.299 | 2026-10-14 02:49 | 190 | 79 | 6 | 85 |
| 2.1.300 | 2026-10-14 18:24 | 88 | 30 | 2 | 32 |
| 2.1.301 | 2026-10-15 19:22 | 51 | 21 | 4 | 25 |
| 2.1.302 | 2026-10-16 20:53 | 63 | 17 | 0 | 17 |
| 2.1.303 | 2026-10-18 22:26 | 1 | 0 | 0 | 0 |
| 2.1.304 | 2026-10-19 21:34 | 76 | 27 | 5 | 32 |
| 2.1.305 | 2026-10-20 20:46 | 38 | 12 | 3 | 15 |
| 2.1.306 | 2026-10-21 03:16 | 2 | 1 | 0 | 1 |
| 2.1.307 | 2026-10-21 22:17 | 43 | 14 | 1 | 15 |
| 2.1.308 | 2026-10-22 04:34 | 1 | 0 | 0 | 0 |
| 2.1.309 | 2026-10-22 22:18 | 79 | 26 | 8 | 34 |
| 2.1.310 | 2026-10-23 23:39 | 26 | 4 | 0 | 4 |
| 2.1.311 | 2026-10-26 21:51 | 92 | 28 | 3 | 31 |
| 2.1.312 | 2026-10-27 20:24 | 39 | 5 | 1 | 6 |
| 2.1.313 | none | none | none | none | none |
| 2.1.314 | 2026-10-30 01:06 | 119 | 29 | 3 | 32 |
| **Total** | | **1130** | **390** | **45** | **435** |

Versions 2.1.297, 2.1.298 and 2.1.313 were never published: `get_release_by_tag` returns 404 for each, `list_tags` has no such tag, and the `CHANGELOG.md` at the `v2.1.314` commit has no section for them. They have no entries to list.

## Entries by keyword

| Keyword | Entries that match it |
| :-- | --: |
| mods | 78 |
| plugins | 88 |
| LSP | 1 |
| MCP | 79 |
| rules | 22 |
| CLAUDE.md | 6 |
| marketplace | 8 |
| skills | 58 |
| test | 5 |
| plugin.json | 1 |
| hooks | 98 |
| tools | 130 |
| tools (named tool) | 45 |

An entry that matches several keywords is counted under each of them.

## Entries

### 2.1.295

Published 2026-10-08 19:48 UTC. Source: [release v2.1.295](https://github.com/anthropics/claude-code/releases/tag/v2.1.295).

- [295:001] Added `onFailure: "block"` for command and HTTP hooks: a hook that can't start, times out, or exits with an unexpected code blocks the action instead of letting it through  
  _Matches: hooks_
- [295:004] Added a warning to `claude plugin install`, `enable`, `disable` and `marketplace add` when the settings file they write to does not load  
  _Matches: plugins, marketplace_
- [295:007] Added a "Backgrounding cancelled" message when you stop the turn while `←` is waiting for the current tool to finish  
  _Matches: tools_
- [295:010] Added advice to `claude plugin validate` when a plugin's README has no install line: it prints the line to paste and never changes the exit code, even with `--strict`  
  _Matches: plugins_
- [295:012] Added `$.ui.notify` for mods: raises a native notification through your own notification setting and says which channel sent it  
  _Matches: mods_
- [295:013] Added children to a mod's `Button`: strings and `Text`, so a row of a list is one pressable with a chip or a dim detail inside  
  _Matches: mods_
- [295:018] Fixed remote MCP servers in headless and SDK sessions staying disconnected after an outage longer than 15 seconds, or reconnecting in a tight loop to a server that drops each connection right after it connects; repeated drops now back off, up to 30s  
  _Matches: MCP_
- [295:019] Fixed remote MCP connections being dropped when a server's error reply happened to contain a network error name  
  _Matches: MCP_
- [295:020] Fixed MCP servers that repeat a pagination cursor being asked for the same page up to 20 times at every connect  
  _Matches: MCP_
- [295:021] Fixed CSS, JavaScript and XML files returned by MCP tools being saved as .bin, which the Read tool refuses; font and icon files now get their own extension too  
  _Matches: MCP, tools_
- [295:022] Fixed Bash tool calls failing when the model passes `command_description` instead of `description`  
  _Matches: tools_
- [295:023] Fixed Claude in Chrome not applying a site deny rule written with port 80 (`host:80`) to plain `http://` pages on that host  
  _Matches: rules_
- [295:024] Fixed `/plugin`'s Errors tab removing a marketplace that failed to load, and uninstalling its plugins, on Enter without asking first  
  _Matches: plugins, marketplace_
- [295:025] Fixed `claude plugin marketplace add` reporting success for a marketplace whose name no plugin can be installed under; such an add is now refused  
  _Matches: plugins, marketplace_
- [295:027] Fixed PushNotification saying a push was not sent in `claude remote-control` sessions right after a phone message, without the `/config` toggle, or when started from inside Claude Code  
  _Matches: tools (named tool)_
- [295:036] Fixed Claude stopping at the end of the current tool when text typed in the prompt cancelled backgrounding with `←`; Claude now keeps working in the foreground  
  _Matches: tools_
- [295:037] Fixed `--tools` and `--restricted` not applying to built-in tools that register after launch, and deprecated tool names reaching tools outside the caller's tool set  
  _Matches: tools_
- [295:038] Fixed an interrupt not ending the turn until a timeout while Claude waited for an MCP server's resource list  
  _Matches: MCP_
- [295:039] Fixed a mod's hook being handed a deeply nested tool input cut short with no error, so a guard could pass content it never saw  
  _Matches: mods, hooks, tools_
- [295:041] Fixed commands and hooks in background sessions inheriting `FORCE_COLOR=3`, which put color escape codes into the output Claude reads  
  _Matches: hooks_
- [295:044] Fixed Bash permission checks for for-loops over glob patterns, improving permission-check accuracy  
  _Matches: tools (named tool)_
- [295:045] Fixed forked skills invoked from Workflow subagents delivering their results to the main conversation instead of the invoking agent  
  _Matches: skills_
- [295:046] Fixed in-process agent teammates failing their first SendMessage call until they loaded the tool through tool search  
  _Matches: tools_
- [295:047] Fixed Claude being told on resume that an unfinished background workflow may have been stopped by `TaskStop`, which can never be the cause  
  _Matches: tools (named tool)_
- [295:048] Fixed Claude not being told when you stop a long-running MCP tool call from the tasks panel or a connected client  
  _Matches: MCP, tools_
- [295:051] Fixed plugin marketplaces whose repository has large git submodules failing to add or refresh: only the submodules that hold plugin files are now fetched  
  _Matches: plugins, marketplace_
- [295:053] Fixed the notification for an MCP tool call that moved to the background showing a shortened task id  
  _Matches: MCP, tools_
- [295:057] Fixed calls a mod makes while it reloads during a plugin hooks worker restart getting past another mod's guard hook that has a `.catch`; such calls are now refused  
  _Matches: mods, plugins, hooks_
- [295:058] Fixed plugins whose hooks module nests code thousands of levels deep failing to load or validate with a bare stack-overflow message  
  _Matches: plugins, hooks_
- [295:059] Fixed `claude plugin test` passing a `session.append` hook that removes tool call, tool result or thinking blocks that a real session keeps  
  _Matches: plugins, test, hooks, tools_
- [295:060] Fixed Claude not being told it can resume background subagents with SendMessage after a session was killed and resumed a second time  
  _Matches: tools (named tool)_
- [295:061] Fixed a file being treated as already read after a Bash command such as `cat` ran without printing it  
  _Matches: tools (named tool)_
- [295:062] Fixed plugin options named `constructor` or `prototype` always reading as their default and never reloading the plugin when edited  
  _Matches: plugins_
- [295:063] Fixed a mod's hot reload missing a save made while `/reload-plugins` or session start was reading the mod's files  
  _Matches: mods, plugins_
- [295:064] Fixed the mod hot-reloading question being asked again every turn for the whole session when it is approved without picking an answer  
  _Matches: mods_
- [295:065] Fixed `/model`, `/fast` and `/output-style` saving their setting without asking a plugin's `config.set` hook  
  _Matches: plugins, hooks_
- [295:068] Fixed a mod's hot reload missing a save made within a few milliseconds of its last reload, which left the mod on its old version until the next save  
  _Matches: mods_
- [295:069] Fixed `claude mcp serve` background Bash results not naming the output file, and its tool description promising a notification that never arrives  
  _Matches: MCP, tools_
- [295:070] Fixed an async SessionStart hook's unchanged context being added to the conversation again on every resume  
  _Matches: hooks_
- [295:071] Fixed variables a SessionStart hook writes to `CLAUDE_ENV_FILE` not reaching the Bash tool after an in-app `/resume` or `/branch`  
  _Matches: hooks, tools_
- [295:072] Fixed a skill's `allowed-tools` and `effort` being dropped when the Skill tool finished before the response stream ended, which denied the skill's Bash commands in `-p` runs  
  _Matches: skills, tools_
- [295:073] Fixed a tampered cache of server-managed settings making a person's own plugin count as organization-managed on machines whose managed settings list or enable plugins  
  _Matches: plugins_
- [295:074] Fixed Claude 3 Opus and Claude 3.x Sonnet sessions being offered tool search, which those models reject, where feature flags are unavailable  
  _Matches: tools_
- [295:075] Fixed generated type files being written into a `--plugin-dir` plugin's folder in `-p` and SDK sessions; they are now written only where a mod is being developed  
  _Matches: mods, plugins_
- [295:078] Fixed an async hook's JSON output being ignored when it is printed over several lines  
  _Matches: hooks_
- [295:079] Fixed the Read tool rejecting calls with an empty `pages` parameter instead of treating it as omitted  
  _Matches: tools_
- [295:080] Fixed project-scope plugins not loading in VS Code on Windows due to drive-letter casing (anthropics/claude-code#74612)  
  _Matches: plugins_
- [295:081] Fixed `plugin install` and `uninstall` at project or local scope on Windows missing the install record, or adding a second one, when only the drive letter's case differs  
  _Matches: plugins_
- [295:083] Fixed mod hot-reloading turning off for the whole session when an SDK host closed its enable question before anyone answered; the question is now asked up to three times  
  _Matches: mods_
- [295:084] Fixed a prompt that a mod's `prompt.submit` hook rewrote or dropped still being saved as typed to prompt history and to the transcript's queued-prompt records  
  _Matches: mods, hooks_
- [295:085] Fixed non-interactive sessions telling you about MCP servers that need authentication when your request doesn't use them  
  _Matches: MCP_
- [295:087] Fixed a plugin that adds very large interfaces getting another plugin unloaded when the plugin hooks worker stalls  
  _Matches: plugins, hooks_
- [295:088] Fixed Edit treating a file as fully read when its contents changed without its modification time advancing  
  _Matches: tools (named tool)_
- [295:094] Fixed claude.ai-synced plugin hooks failing with "Plugin directory does not exist" in long-running sessions after another session synced a plugin update  
  _Matches: plugins, hooks_
- [295:096] Fixed cloud sessions hanging when a mod's `session.receive` hook asked for permission before passing a message on  
  _Matches: mods, hooks_
- [295:098] Fixed an MCP sign-in or reconnect that finishes late in headless and SDK sessions relisting a server set with `setMcpServers()` as your own  
  _Matches: MCP_
- [295:099] Fixed changing the auto-update channel in `/config` saving before a plugin's `config.set` hook was asked  
  _Matches: plugins, hooks_
- [295:103] Improved the status shown in Remote Control, claude.ai and the desktop app for a session waiting on a permission prompt to name an MCP tool by its server and readable name instead of its `mcp__server__tool` identifier  
  _Matches: MCP, tools_
- [295:107] Improved the built-in `plugin-authoring` skill: it no longer tells a session with no terminal to run terminal commands, and explains sharing a mod only when asked  
  _Matches: mods, plugins, skills_
- [295:108] Improved Grep input handling: a search sent with grep's `-l`, `-c` or `-r` flag now runs instead of failing the call  
  _Matches: tools (named tool)_
- [295:109] Improved `claude plugin validate` and plugin loading: when a hooks module is refused over a rebound top-level `var`, the error now names the line that rebinds it, the cause, and a fix  
  _Matches: plugins, hooks_
- [295:110] Improved the Workflow tool's `scriptPath` refusal: it now says to pass the script inline via `script`, the route that works in sessions without a Read tool  
  _Matches: tools_
- [295:112] Changed MCP tool descriptions the model loads through tool search to be cut at 16,384 characters instead of 2,048  
  _Matches: MCP, tools_
- [295:113] Changed subagents to preload at most 32 skills from the `skills` field, each once; a subagent with the Skill tool can still invoke the rest  
  _Matches: skills, tools_
- [295:116] Changed claude.ai connectors to negotiate MCP protocol version 2026-07-28 by default on installs that fetch no flags; `MCP_PROTOCOL_NEGOTIATION=legacy` opts out  
  _Matches: MCP_
- [295:118] Changed what Claude and you read when a mod denies a tool call after the tool ran: it now says the tool ran and a plugin withheld its result  
  _Matches: mods, plugins, tools_
- [295:120] Changed the Artifact tool's permission prompts with telemetry disabled to the same five questions other installs get, instead of asking before each read of someone else's artifact and each data edit  
  _Matches: tools_
- [295:122] Changed toasts from your organization's mods to show ahead of other mods' toasts instead of waiting behind them  
  _Matches: mods_
- [295:124] Changed WebSocket (`ws`) MCP servers: a message over 16 MiB is no longer parsed and closes the connection, the limit the other transports already have  
  _Matches: MCP_
- [295:142] [Code Review] Fixed Code Review still skipping a large CLAUDE.md's rules when the pull request edits that file  
  _Matches: rules, CLAUDE.md_
- [295:143] Fixed web searches and `agent` hook evaluations taking much longer at `xhigh` and `max` effort  
  _Matches: hooks_

### 2.1.296

Published 2026-10-09 19:28 UTC. Source: [release v2.1.296](https://github.com/anthropics/claude-code/releases/tag/v2.1.296).

- [296:005] Added a note in `/plugin` on a plugin whose hooks are left out because another enabled plugin has the same name  
  _Matches: plugins, hooks_
- [296:006] Added an `allow_large` option to the Read tool so Claude can read a text file past the usual size limits in one call when it needs the whole file and the context has room  
  _Matches: tools_
- [296:007] Fixed managed-settings `PreToolUse` hooks that deny a tool call with `"continue": false`, and managed `prompt` hooks that block one, refusing the call but not ending the turn  
  _Matches: hooks, tools_
- [296:008] Fixed PostToolUse hooks in managed settings not applying `updatedMCPToolOutput` in some sessions  
  _Matches: MCP, hooks, tools_
- [296:009] Fixed headless sessions starting a folder's `.mcp.json` or plugin MCP server that was switched off for that folder, after changing directory or reloading plugins  
  _Matches: plugins, MCP_
- [296:014] Fixed resumed subagents being told that the user rejected a tool call that a session shutdown had interrupted  
  _Matches: tools_
- [296:015] Fixed hook output being altered when it contained text resembling a plugin hint tag  
  _Matches: plugins, hooks_
- [296:019] Fixed Esc or an interrupt during a `UserPromptSubmit` hook or a mod's `prompt.submit` hook ending headless sessions, clearing the typed prompt, or letting the unchecked prompt through  
  _Matches: mods, hooks_
- [296:020] Fixed SessionStart hooks of a plugin loaded after a headless session starts being skipped when a different plugin with the same name, or another spelling of it, had already run  
  _Matches: plugins, hooks_
- [296:024] Fixed a plugin's served `$` methods running in the main session's working directory instead of the calling agent's, and ignoring the turn their calling hook holds  
  _Matches: plugins, hooks_
- [296:025] Fixed `$.agent.register` succeeding from a mod's hook that was still running after the mod was reloaded or removed; the call is now refused  
  _Matches: mods, hooks_
- [296:026] Fixed `$.http.fetch` in mods refusing a `HEAD` request when the response declares a `Content-Length` over the 4 MiB body limit  
  _Matches: mods_
- [296:027] Fixed `claude plugin marketplace add`, `marketplace update` and `plugin install` failing with an internal error for a marketplace named like `constructor`; `add` now refuses such names clearly  
  _Matches: plugins, marketplace_
- [296:028] Fixed a plugin secret named `constructor` or `prototype` being deleted by the next save of that plugin's options  
  _Matches: plugins_
- [296:030] Fixed `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` re-running a finished turn after a restart when an MCP tool result had ended that turn  
  _Matches: MCP, tools_
- [296:031] Fixed Bash permission checks auto-approving some commands that assign the `BASH_ARGV0` shell variable and then use it; these now prompt for approval  
  _Matches: tools (named tool)_
- [296:032] Fixed Edit and NotebookEdit replacing every non-ASCII character in files that are not valid UTF-8 (Windows-1252, Shift-JIS, GBK); such edits are now refused  
  _Matches: tools (named tool)_
- [296:034] Fixed a prompt sent while SessionStart hooks were still running vanishing when `←` moved the session to the background; it is still not sent, but `↑` now brings it back  
  _Matches: hooks_
- [296:035] Fixed a late-loading plugin's SessionStart hook output reaching the new conversation after `/clear` in headless sessions  
  _Matches: plugins, hooks_
- [296:036] Fixed PowerShell commands not seeing variables that hooks write to CLAUDE_ENV_FILE (when the file holds only plain assignments)  
  _Matches: hooks_
- [296:037] Fixed Claude calling cloud sessions non-interactive and suggesting `/mcp` or `claude mcp` when an MCP server needs authentication  
  _Matches: MCP_
- [296:040] Fixed skills synced from claude.ai never finishing their install, and being downloaded again at every sync, when several sessions share a config directory  
  _Matches: skills_
- [296:041] Fixed a plugin synced from claude.ai being disabled when the marketplace dependency it declares was also synced from claude.ai  
  _Matches: plugins, marketplace_
- [296:042] Fixed a startup hang on macOS when plugin paths copied from a Linux machine pointed under /home  
  _Matches: plugins_
- [296:043] Fixed the Workflow tool refusing script files with CRLF line endings, such as files checked out on Windows  
  _Matches: tools_
- [296:044] Fixed OpenTelemetry `tool_result` events missing `git_commit_id` after `git commit -q` or `git -C <dir> commit`  
  _Matches: tools_
- [296:047] Windows: Fixed PowerShell commands longer than about 1 KB always asking for permission, so allow rules and read-only detection now apply up to 32 KB  
  _Matches: rules_
- [296:048] Windows: Fixed stdio MCP servers being force-killed at shutdown; stdin now closes first and the process tree is killed only if the server is still running after 300 ms  
  _Matches: MCP_
- [296:049] Windows: Fixed `claude plugin install` failing for GitHub `owner/repo` plugin sources on machines with no GitHub SSH key; the clone is now retried over HTTPS  
  _Matches: plugins_
- [296:056] Improved auto mode: a tool call that wasn't run because auto mode's check had no usable answer now shows as a dim "Not run" row instead of a red error  
  _Matches: tools_
- [296:057] Improved `--debug` output for hooks: command hooks on tool calls, prompts, SessionStart and Stop now log their command, plugin, outcome and duration when they finish, so a slow hook is identifiable  
  _Matches: plugins, hooks, tools_
- [296:060] Updated the bundled dataviz skill: lighter violet for the seventh series in light mode, softer primary text in dark mode, and compact y-axis labels like 1K  
  _Matches: skills_
- [296:061] Changed the default limit on MCP tool descriptions sent up front and on MCP server instructions from 2,048 to 4,096 characters  
  _Matches: MCP, tools_
- [296:075] [Claude Tag] Fixed the plugin confirmation card Claude posts in a Slack channel showing a plugin's ID instead of its name  
  _Matches: plugins_
- [296:076] [Claude Tag] Fixed Claude in Slack posting a card to remove a plugin the channel's own settings don't include; it now explains where the plugin comes from instead  
  _Matches: plugins_

### 2.1.299

Published 2026-10-14 02:49 UTC. Source: [release v2.1.299](https://github.com/anthropics/claude-code/releases/tag/v2.1.299).

- [299:001] Added `CLAUDE_CODE_DISABLE_FILE_MENTIONS` environment variable: Claude gets the paths of `@` file mentions to read with its file tools, not the files' contents  
  _Matches: tools_
- [299:004] Added `$.prompt.media` so a `prompt.submit` hook of a mod installed by managed settings can read the bytes of an image or document attached to the prompt  
  _Matches: mods, hooks_
- [299:005] Added `$.session.identity()` for mods installed by managed settings: how the session is signed in, and its organization and email when managed `forceLoginOrgUUID` lists that organization  
  _Matches: mods_
- [299:006] Added `size`, `weight`, `mono` and `tabular` to a mod's `Text` and named spacing steps (`xs` to `xl`) to its `Box`; `bold` is deprecated in favor of `weight`  
  _Matches: mods_
- [299:007] Added `--shutdown-drain-sec` to `claude self-hosted-runner orchestrator`: on SIGTERM it stops polling and gives the poll in flight and running spawn hooks up to that many seconds to finish  
  _Matches: hooks_
- [299:008] Added the skill's frontmatter, source, plugin name and file path to what a mod's `skill.prompt` hook receives  
  _Matches: mods, plugins, skills, hooks_
- [299:012] Added `--disallow-tools` and a `disallowed_tools` case field to `claude plugin eval` to keep specific built-in tools, such as Agent, out of eval runs  
  _Matches: plugins, tools_
- [299:015] Added a `queue` door to the `session.append` mod hook, so a mod can make the transcript's queue records differ from the prompt as sent  
  _Matches: mods, hooks_
- [299:016] Added a note in `/plugin` and `claude plugin validate` naming a mod's hooks that are skipped where an organization manages Claude Code  
  _Matches: mods, plugins, hooks_
- [299:017] Added `/usage` warnings for max effort, workflows, always-on context and large tool results  
  _Matches: tools_
- [299:020] Fixed a mod that submits a prompt at the end of every turn keeping a headless run going past `--max-turns`, `--max-budget-usd`, an interrupt, or the end of the host's conversation  
  _Matches: mods_
- [299:021] Fixed cloud sessions sometimes showing the model's follow-up text after a tool group's one-line label  
  _Matches: tools_
- [299:022] Fixed the Write and Edit tools creating a mod in a session's mods folder without asking in accept-edits mode when the config directory's path has no `.claude` in it  
  _Matches: mods, tools_
- [299:023] Fixed installed mods that kept running in an open session after being turned off remotely; they now unload between turns  
  _Matches: mods_
- [299:024] Fixed Edit and Retry in Cowork and claude.ai cloud sessions failing on a message stopped while its `UserPromptSubmit` or mod `prompt.submit` hooks were still running (regression in 2.1.296)  
  _Matches: mods, hooks_
- [299:027] Fixed a sandboxed shell command being able to write into a `--plugin-dir` folder, whose code Claude Code reloads and runs outside the sandbox  
  _Matches: plugins_
- [299:032] Fixed `claude mcp list`, `claude doctor` and `/status` reporting an empty `.mcp.json` as invalid  
  _Matches: MCP_
- [299:035] Fixed scheduled wakeups (ScheduleWakeup) not firing while a background task was running in Agent SDK, IDE and `claude remote-control` sessions  
  _Matches: tools (named tool)_
- [299:036] Fixed a mod's `prompt.submit` rewrite being silently dropped, sending the prompt as typed, for some prompts with a pasted image or an image that can't be read  
  _Matches: mods_
- [299:038] Fixed a Remote Control prompt that had passed its hooks being dropped from prompt history when Stop interrupted the next queued prompt's hook  
  _Matches: hooks_
- [299:039] Fixed sign-in, MCP servers and project trust appearing lost on Linux after a sandboxed command left an empty `.config.json` in the config directory  
  _Matches: MCP_
- [299:042] Fixed MCP servers named `constructor` or `prototype` in an MCP config never being connected  
  _Matches: MCP_
- [299:043] Fixed tools of an MCP server named `constructor` or `toString` asking for permission in auto mode and bypass permissions mode  
  _Matches: MCP, tools_
- [299:044] Fixed a spurious "synced[0] commands path not found" plugin error at startup when another Claude Code process had just updated a claude.ai-synced plugin  
  _Matches: plugins_
- [299:045] Fixed the Artifact tool advising a retry when a publish that requests connectors or other access was refused by the server or a proxy (HTTP 403); it now says so and what to tell the user  
  _Matches: tools_
- [299:046] Fixed Cowork cloud sessions staying on an old account plugin after a plugin reload that timed out or a restart that reused a recent sync  
  _Matches: plugins_
- [299:050] Fixed a mod hook, with or without a `.catch`, being run again without end when it waits on another mod's noun that does its work outside the call  
  _Matches: mods, hooks_
- [299:054] Fixed a mod's `tool.describe` or `prompt.section` answer that changed after `$.ui.invalidate` never reaching Claude; the new answer is now sent on the next turn  
  _Matches: mods, tools_
- [299:055] Fixed a settings file being ignored when `enabledMcpjsonServers` or `disabledMcpjsonServers` held a single server name (letters, digits, - or _) as a plain string  
  _Matches: MCP_
- [299:056] Fixed `claude plugin test` pausing a hook's time budget while a served `$` method it had called kept making `$` calls after answering  
  _Matches: plugins, test, hooks_
- [299:058] Fixed plugin hooks being skipped when they pass a very deeply nested tool input or message on with next()  
  _Matches: plugins, hooks, tools_
- [299:059] Fixed a value a mod's hook passes to `next()`, returns, or sends to a `$` method being refused whole when one of its getters throws a `RangeError`; now only that key is refused  
  _Matches: mods, hooks_
- [299:064] Fixed Cowork cloud sessions running the old version of an account plugin changed, removed or disabled from another device until the session restarted  
  _Matches: plugins_
- [299:065] Fixed deny and ask rules for an MCP server (`mcp__<server>`) not applying when the server's normalized name contains a double underscore  
  _Matches: MCP, rules_
- [299:067] Fixed the `plugin_loaded` telemetry event reporting `has_hooks` as false for plugins whose hooks are a hooks module, built-in plugins included  
  _Matches: plugins, hooks_
- [299:071] Fixed a mod's hot reload ignoring a fix saved right after a failed reload; saving a mod file without changing it no longer reloads the mod  
  _Matches: mods_
- [299:072] Fixed mods loaded from source files being refused when a hook hands `$` to a function declaration imported from another file of the mod  
  _Matches: mods, hooks_
- [299:073] Fixed a regression in 2.1.296 where cloud and headless sessions could run an approved tool call twice if a new message arrived as the session resumed after a restart  
  _Matches: tools_
- [299:074] Fixed scheduled tasks being announced for the wrong minute: the scheduling tools now report each job's actual next run time  
  _Matches: tools_
- [299:075] Fixed mods' hooks being handed values with `__proto__` keys silently removed, which could skip a `tool.check` guard on a tool call another mod made  
  _Matches: mods, hooks, tools_
- [299:079] Fixed MCP connections over HTTP hanging for 30 seconds and failing when a server never ends the body of its reply to a notification (anthropics/claude-code#99014)  
  _Matches: MCP_
- [299:080] Fixed MCP servers added to a running headless or SDK session being connected before some policy checks ran; a blocked server is now reported as failed without being contacted  
  _Matches: MCP_
- [299:081] Fixed `claude mcp list`, `claude mcp get` and subagent MCP servers starting a server that a policy check blocks; it is now reported as blocked without being started  
  _Matches: MCP_
- [299:082] Fixed `/reload-plugins` not loading a plugin installed from another terminal a moment earlier  
  _Matches: plugins_
- [299:087] Fixed `$.http.fetch` in mods refusing a `304`, `204` or `205` response that declares a `Content-Length` over the 4 MiB body limit  
  _Matches: mods_
- [299:090] Fixed Read failing on PDF page ranges in remote sessions on Linux that run without elevated privileges  
  _Matches: tools (named tool)_
- [299:094] Fixed self-hosted runner sessions shutting down MCP servers added through an `--exec-path` wrapper's own `--mcp-config` when connectors change mid-session  
  _Matches: MCP_
- [299:095] Fixed `claude plugin eval` passing runs that the API refused: a run that ends on an API error now scores 0 without grading and makes the suite exit 1  
  _Matches: plugins_
- [299:098] Fixed `--bare` sessions leaving out an MCP server named `constructor` or `prototype` that `--channels` asked for  
  _Matches: MCP_
- [299:104] Fixed MCP tool calls in headless and SDK sessions sometimes failing or running twice when a background reconnect closed the connection they were running on  
  _Matches: MCP, tools_
- [299:110] Fixed `claude mcp add <name> -- <command> --background` being started as a background session  
  _Matches: MCP_
- [299:116] Fixed MCP OAuth sign-in, token refresh and sign-out not sending configured `headers`/`headersHelper` values, which broke servers behind an authenticating proxy  
  _Matches: MCP_
- [299:117] Fixed the Artifact tool reporting a spurious one-line difference against the live page, and refusing the publish, when a large page with a line break after `<head>` is published again unchanged  
  _Matches: tools_
- [299:118] Fixed `$.ui.open` reporting a mod's pane as placed in sessions where no surface draws it, such as Claude Code for VS Code and `claude -p`  
  _Matches: mods_
- [299:119] Fixed the `agent.spawn` mod hook not running when a finished subagent or a killed teammate is resumed: the hook's event now carries `resume`, and a mod can refuse it  
  _Matches: mods, hooks_
- [299:120] Fixed `claude plugin validate` rejecting a mod's `$.state` references when `plugin.json` has no `types` key and the contract is at `./types/index.d.ts`  
  _Matches: mods, plugins, plugin.json_
- [299:121] Fixed a mod's `dimColor` text looking the same as plain text under the dark ANSI theme and on 16-color terminals  
  _Matches: mods_
- [299:122] Fixed plan mode running a write (an MCP tool's, a file's, a shell command's) that a `PreToolUse` hook or a mod's `tool.check` hook allowed  
  _Matches: mods, MCP, hooks, tools_
- [299:124] Fixed `SendMessage` not finding a subagent by name after the CLI restarted and resumed the session (names given before the last compaction still need the agent ID)  
  _Matches: tools (named tool)_
- [299:126] Fixed Read garbling UTF-16LE files with a byte-order mark, and Write dropping byte-order marks or silently converting Windows-1252, Shift-JIS, GBK or UTF-16BE files to UTF-8 (now refused)  
  _Matches: tools (named tool)_
- [299:128] Fixed cloud sessions and `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` sometimes answering a finished turn again after a restart, when a tool ended the turn and a skill loaded in the same step  
  _Matches: skills, tools_
- [299:132] Fixed a user-installed mod's `$.env.set` changing the environment or shell prefix that command hooks from managed settings start with  
  _Matches: mods, hooks_
- [299:134] Windows: Fixed PreToolUse and PermissionRequest hooks that set no shell failing open when Git for Windows isn't installed; a guard that fails now blocks the call  
  _Matches: hooks, tools_
- [299:135] Windows: Fixed Bash commands failing with "command not found" for a whole session when Git Bash did not report its PATH at startup  
  _Matches: tools (named tool)_
- [299:139] Improved enforcement of managed permission rules, managed hooks and organization MCP tool names against user-installed mods  
  _Matches: mods, MCP, rules, hooks, tools_
- [299:141] Improved sandboxed Bash on Linux: Esc and Ctrl-C now work while wildcard read rules are being expanded for a command  
  _Matches: rules_
- [299:143] Improved the plugin-authoring skill's steps for sharing a mod: Claude asks public or private and checks the files before creating a GitHub repository  
  _Matches: mods, plugins, skills_
- [299:144] Improved the Skill tool's "Unknown skill" error to suggest a skill's listed name when Claude wrongly adds the `anthropic-skills:` prefix to it  
  _Matches: skills, tools_
- [299:145] Improved `/reload-skills` to say it re-sends the full skill list to Claude, which is how to get skills back after compaction  
  _Matches: skills_
- [299:150] Changed plugin hooks and workflow scripts to refuse values they hand back that nest deeper than 28,000 levels, with an error naming the limit (workflow scripts allowed 100,000)  
  _Matches: plugins, hooks_
- [299:151] Changed actions a plugin hook can block to be refused, not let through, when the hook cannot be handed them or cannot hand back its answer; a tool that already ran has its result withheld  
  _Matches: plugins, hooks, tools_
- [299:152] Changed requests to claude.ai's connector proxy and to Anthropic-hosted MCP servers to no longer follow HTTP redirects; redirects by a connector's own server are unaffected  
  _Matches: MCP_
- [299:153] Changed MCP requests in cloud and self-hosted runner sessions to no longer follow HTTP redirects from the session's MCP proxy  
  _Matches: MCP_
- [299:154] Changed skill and command loading: one whose file or folder name has hidden, direction-changing or blank-like characters, `<` or `>` is no longer offered until renamed; such a `name:` is ignored  
  _Matches: skills_
- [299:155] Changed `ui.render` trees in `claude plugin test`: each mod's Box or Text root now carries `part: { plugin }` naming the mod, so exact-tree assertions must include it  
  _Matches: mods, plugins, test_
- [299:156] Changed WebFetch page reads to pick their effort as web searches do: the caller's level on the caller's own model, otherwise the level settings give the small model  
  _Matches: tools (named tool)_
- [299:157] Changed `claude plugin test` to fail a call to a mod's served `$` method that has not answered within ten seconds, as a session does  
  _Matches: mods, plugins, test_
- [299:158] Changed MCP allow rules to reach only the server they name: `mcp__a` no longer allows a server named `a__b` or `a_`; write `mcp__<server>__*` with the server's whole normalized name  
  _Matches: MCP, rules_
- [299:159] Changed agent `tools:` lists to take only the named MCP server's tools; list a server whose name contains `__` as `mcp__<whole name>__*`  
  _Matches: MCP, tools_
- [299:161] Changed cloud session and Remote Control MCP connectors to negotiate MCP protocol version 2026-07-28 by default on installs that fetch no flags; `MCP_PROTOCOL_NEGOTIATION=legacy` opts out  
  _Matches: MCP_
- [299:162] Changed MCP tool descriptions and server instructions from Anthropic's first-party MCP servers at `api.anthropic.com` to reach Claude in full instead of being cut at 4,096 characters  
  _Matches: MCP, tools_
- [299:163] Changed auto mode in Cowork cloud sessions: a `PermissionRequest` hook can no longer approve shell commands or subagents; those prompts wait or are denied  
  _Matches: hooks_
- [299:167] Changed `UserPromptSubmit` hooks to run before a skill or custom slash command expands, so a hook that blocks the prompt now also stops its embedded shell commands  
  _Matches: skills, hooks_
- [299:168] Changed a skill's own front-matter `UserPromptSubmit` hook to first run on the prompt after the one that invokes the skill  
  _Matches: skills, hooks_
- [299:169] Changed the `turn.start` mod hook to also hear subagents' and teammates' turns, not only the main loop's; tell them apart by `e.agentId` (absent on the main loop)  
  _Matches: mods, hooks_

### 2.1.300

Published 2026-10-14 18:24 UTC. Source: [release v2.1.300](https://github.com/anthropics/claude-code/releases/tag/v2.1.300).

- [300:001] Added `virtualText` to a mod's prompt decorations: text drawn in the prompt box that never enters the draft or the submitted prompt  
  _Matches: mods_
- [300:003] Added `$.ui.view({ agentId })` for mods: shows an agent's transcript in the main view when you ask, and `$.ui.view({})` goes back  
  _Matches: mods_
- [300:004] Added a `dir` prop on a mod's `Text` for right-to-left text: on Windows and in VS Code's terminal its rows read in that direction and sit flush right  
  _Matches: mods_
- [300:005] Added `/advisor` on Claude Platform on AWS; no advisor runs until you pick one with `/advisor`, `advisorModel` or `--advisor`, and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` turns it off  
  _Matches: tools_
- [300:006] Added OpenTelemetry GenAI semantic-convention attributes to trace spans, such as `gen_ai.provider.name`, `gen_ai.conversation.id`, `gen_ai.tool.name` and `error.type`  
  _Matches: tools_
- [300:007] Added support for rewriting a workflow agent's `prompt` and `model` in the `agent.spawn` mod hook, which could only refuse workflow agents before  
  _Matches: mods, hooks_
- [300:008] Added the `prompt.change` mod hook, raised when the prompt box's text changes without a typed edit: a recalled history entry, a clear, an undo, or a plugin's fill  
  _Matches: mods, plugins, hooks_
- [300:011] Fixed SessionEnd hooks sometimes not running when you exit while a background command is still running  
  _Matches: hooks_
- [300:012] Fixed `claude --help` naming a removed tool in its description of `--restricted`  
  _Matches: tools_
- [300:018] Fixed automatic tool search (`ENABLE_TOOL_SEARCH=auto`) turning off part-way through a conversation, for example while MCP servers reconnect after a resume  
  _Matches: MCP, tools_
- [300:021] Fixed the Artifact tool's verbose and ctrl+o line reading `Artifact("(unprintable path)")` while a call's input arrives; its row now shows "Waiting…" and "Running…" as Bash's does  
  _Matches: tools_
- [300:024] Fixed plugin `WorktreeCreate` and `WorktreeRemove` hooks not running when Claude Code starts with `--worktree` (not yet with `--tmux`)  
  _Matches: plugins, hooks_
- [300:025] Fixed OpenTelemetry `tool_result` events missing `git_commit_id` after `git commit -q` in repositories using reftable ref storage  
  _Matches: tools_
- [300:026] Fixed a prompt that a mod's `prompt.submit` hook rewrote or dropped still being recorded as typed in the OpenTelemetry `user_prompt` event and interaction span, and in session title requests  
  _Matches: mods, hooks_
- [300:027] Fixed a note meant for Claude about mod hot-reloading appearing in the transcript as if you had typed it  
  _Matches: mods_
- [300:028] Fixed agent hooks ignoring their `model`: aliases like `haiku` now resolve, a subagent's model no longer overrides it, and an unavailable model falls back to the caller's instead of allowing the action  
  _Matches: hooks_
- [300:034] Fixed starting Claude Code in a VS Code, Cursor or Devin Desktop integrated terminal launching the editor's command-line tool twice to check for the extension; it now launches it once  
  _Matches: tools_
- [300:035] Fixed a mod's `prompt.edit` hook not being raised for a newline entered with the `chat:newline` keybinding (Ctrl+J, or a rebound Enter)  
  _Matches: mods, hooks_
- [300:036] Fixed a conversation failing on every turn with a 400 error when the API rejected an MCP tool's input schema; Claude Code now sends that tool without parameters for the rest of the conversation  
  _Matches: MCP, tools_
- [300:038] Fixed Claude not being told about an MCP server's tools and instructions until its next tool call, when the server finished connecting after a compaction  
  _Matches: MCP, tools_
- [300:045] Fixed Write, Edit and NotebookEdit in Cowork cloud sessions reporting success for a path on your own computer, where the file never arrived  
  _Matches: tools (named tool)_
- [300:046] Fixed Claude searching for deferred tools already loaded earlier in the conversation when a session resumes a history that never listed them  
  _Matches: tools_
- [300:051] Improved WebFetch in Cowork cloud sessions to tell Claude that a page failed moments ago instead of fetching it again  
  _Matches: tools (named tool)_
- [300:052] Improved mod sharing in the built-in `plugin-authoring` skill: Claude scans a mod's files for keys before opening them, and asks before scanning a folder outside the project  
  _Matches: mods, plugins, skills_
- [300:055] Changed `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` sessions to ignore CA-bundle, tool-proxy, git TLS and git config variables like `SSL_CERT_FILE` in settings; under Claude Desktop, only in project settings  
  _Matches: tools_
- [300:060] Changed the `claude-api` skill to leave Managed Agents sessions in place unless you ask to archive or delete them  
  _Matches: skills_
- [300:061] Changed background sessions to resume a carried workflow through the Workflow tool's approval instead of running it from the handoff file  
  _Matches: tools_
- [300:062] Changed local session transcripts to also record each API request's system prompt, tools and parameters, so a transcript you choose to share can reproduce a request exactly  
  _Matches: tools_
- [300:063] Changed the `/sandbox` mode options to read "Sandbox commands" instead of "Sandbox BashTool"  
  _Matches: tools_
- [300:064] Changed `PermissionRequest` hooks in Cowork cloud sessions: a `setMode` update in a hook's allow is now ignored; the rest of the approval still applies  
  _Matches: hooks_
- [300:065] Changed hooks: `updatedInput` from PreToolUse and PermissionRequest hooks is now validated like Claude's own input: unknown keys are dropped, and input the tool rejects denies the call  
  _Matches: hooks, tools_
- [300:079] [Cloud sessions] Fixed "Allow for this task" missing from Cowork's approval prompts for connector tools where an organization turns off "Always allow" (regression in 2.1.292)  
  _Matches: tools_

### 2.1.301

Published 2026-10-15 19:22 UTC. Source: [release v2.1.301](https://github.com/anthropics/claude-code/releases/tag/v2.1.301).

- [301:002] Added OpenTelemetry tracing guidance to the `claude-api` skill, including setting up trace destinations with the `ant` CLI  
  _Matches: skills_
- [301:004] Added `rows` to a mod's `Input`: a text field of several lines in the terminal, where Enter submits and Shift+Enter or a backslash before Enter starts a new line  
  _Matches: mods_
- [301:005] Added `classifier_verdict` and `permission_mode` to OpenTelemetry `tool_decision` events, so auto mode classifier decisions can be told apart from permission rules  
  _Matches: rules, tools_
- [301:006] Added `classifier_category` to OpenTelemetry `tool_decision` events, naming the built-in rule a classifier block matched, when `OTEL_LOG_TOOL_DETAILS=1`  
  _Matches: rules, tools_
- [301:007] Fixed quitting removing a worktree made by a `WorktreeCreate` hook without asking when it may hold unpushed commits  
  _Matches: hooks_
- [301:010] Fixed Grep and Glob reporting no matches when the search program failed unexpectedly before returning any results; they now return an error saying the search failed  
  _Matches: tools (named tool)_
- [301:012] Fixed artifact updates being refused where a PreToolUse hook covers Edit or Write; Claude now edits the file and then republishes instead of changing it in the publish call  
  _Matches: hooks, tools_
- [301:013] Fixed skills and commands with very many or very long argument names stalling for seconds when invoked; only the first 64 names, each up to 64 characters, are now filled in  
  _Matches: skills_
- [301:014] Fixed skills, commands and hooks using very large amounts of memory when their arguments fill many placeholders  
  _Matches: skills, hooks_
- [301:017] Fixed switching to a model whose name contains `application-inference-profile` running your `awsAuthRefresh` command and delaying model-switch hooks when the provider is not Bedrock  
  _Matches: hooks_
- [301:018] Fixed sign-in refresh timeouts and unexpected sign-outs after a short command such as `claude auth status` or `claude plugin list` exited in the middle of a token refresh  
  _Matches: plugins_
- [301:019] Fixed a tool call cut off by a message sent mid-turn during its permission check being reported to the model as rejected by the user  
  _Matches: tools_
- [301:023] Fixed Esc discarding a typed AskUserQuestion answer in vim mode: the free-text field now supports vim NORMAL mode, and Esc cancels only from NORMAL  
  _Matches: tools (named tool)_
- [301:024] Fixed the Read tool reading binary files such as .xlsm, .parquet, .epub and .heic as text  
  _Matches: tools_
- [301:026] Fixed the /claude-api skill saying CMEK external-key endpoints aren't available on Claude Platform on AWS  
  _Matches: skills_
- [301:027] Fixed skills no longer being listed to the model after using `/rewind`  
  _Matches: skills_
- [301:030] Fixed the permission prompt for a plugin or skill hook's `ask` decision not showing which plugin or skill the hook comes from  
  _Matches: plugins, skills, hooks_
- [301:032] Fixed workflow scripts asking for permission or being refused when read, edited or re-run after a Bash `cd` in the same session  
  _Matches: tools (named tool)_
- [301:034] Fixed a mod's `$.model.fork` returning `nothing-to-fork` when called before the first response of a new Claude Code process had finished, as in `claude -p` runs and cloud sessions  
  _Matches: mods_
- [301:036] Self-hosted runner: Fixed sessions started from Slack being unable to find or attach a repository when managed settings restrict MCP servers; use `deniedMcpServers` to keep those tools off  
  _Matches: MCP, tools_
- [301:039] Windows: Fixed stopped background PowerShell commands missing the closing `[killed]` line in their output file  
  _Matches: tools (named tool)_
- [301:043] Improved mods: in VS Code and the desktop and mobile apps, a tree drawn above the question dialog can now hold Markdown and up to 48 rows; the terminal keeps 12 plain rows  
  _Matches: mods_
- [301:044] Changed a mod hook's `.catch` handler to run only when the hook throws or times out; events raised beneath the hook's own calls now skip that hook without asking its `.catch`  
  _Matches: mods, hooks_
- [301:045] Changed a mod's `$.env.set` to resolve with `{}` once the variable is set or unset, or with `{ deny }` saying why when the write is not made  
  _Matches: mods_
- [301:050] [VSCode] Fixed diagnostics showing "[object Object]" instead of the rule code (e.g. MD013) for some language servers  
  _Matches: LSP, rules_

### 2.1.302

Published 2026-10-16 20:53 UTC. Source: [release v2.1.302](https://github.com/anthropics/claude-code/releases/tag/v2.1.302).

- [302:006] Fixed the Read tool loading an image file of any size, or a pipe or device named like an image, entirely into memory; image sources over 128 MB are now refused  
  _Matches: tools_
- [302:008] Fixed a prompt cache miss when a tool added mid-session was loaded again through ToolSearch or after compaction  
  _Matches: tools_
- [302:009] Fixed `claude plugin` and other subcommands sometimes exiting before a queued settings or config write finished, which could lose the change or leave a `.tmp` file behind  
  _Matches: plugins_
- [302:010] Fixed plugin marketplaces re-cloning on every refresh, and newly installed git plugins showing version "unknown", when git defaults to the reftable ref format  
  _Matches: plugins, marketplace_
- [302:011] Fixed the PowerShell tool not finding commands in a plugin's `bin/` folder, and reporting an error when a search that finds nothing (rg, grep, findstr, git grep) is piped into `Select-Object` or another formatting cmdlet  
  _Matches: plugins, tools_
- [302:012] Fixed Claude in the desktop app pointing you to claude.ai settings or `/mcp` to authorize or reconnect an MCP server where that option isn't available  
  _Matches: MCP_
- [302:014] Fixed `classifier_category` missing from OpenTelemetry `tool_decision` events for most auto mode classifier blocks, and new `tool_decision` attributes pushing out `tool_use_id`, `tool_source` and `tool_parameters` when `OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT` is low  
  _Matches: tools_
- [302:018] Fixed MCP servers showing no tools, or every tool call failing, when the server negotiates protocol version 2026-07-28 but omits `resultType`, `ttlMs` or `cacheScope`  
  _Matches: MCP, tools_
- [302:021] Fixed `claude plugin details <name>@builtin` suggesting `claude plugin list`, which never shows built-in plugins, when the plugin isn't found; it now points to `/plugin`  
  _Matches: plugins_
- [302:026] Windows: Fixed every file write being refused or asked about for projects on exFAT or FAT32 drives, including in sessions started with `--plugin-dir`  
  _Matches: plugins_
- [302:027] Improved startup time with many plugins enabled: plugin command and agent files now take far fewer file system calls to load, most of all on Windows  
  _Matches: plugins_
- [302:028] Improved auto mode with the server-side classifier: a conversation too long for the safety check is now compacted, instead of every checked tool call being denied  
  _Matches: tools_
- [302:031] Changed fork subagents (`subagent_type: "fork"`) to be on by default in `claude -p`, the Agent SDK, the desktop app and VS Code, as they already are in the terminal; `CLAUDE_CODE_FORK_SUBAGENT=0` turns them off, and `claude mcp serve` never offers them  
  _Matches: MCP_
- [302:035] Changed prompt and agent hooks so that at most 12 of one event run at a time; the rest wait their turn  
  _Matches: hooks_
- [302:038] [VSCode] Fixed MCP server sign-in from the panel opening a broken authorization page when the server URL contains a query string  
  _Matches: MCP_
- [302:053] [Claude Tag] Fixed custom connectors whose MCP servers share one host showing as a single connector in Claude Tag admin settings; each server is now its own connector  
  _Matches: MCP_
- [302:061] [Claude Tag] Changed Claude Tag admin settings to organize Claude's access into four tabs: Bundles, Connectors, Skills and plugins, and Channels  
  _Matches: plugins, skills_

### 2.1.303

Published 2026-10-18 22:26 UTC. Source: [release v2.1.303](https://github.com/anthropics/claude-code/releases/tag/v2.1.303).


### 2.1.304

Published 2026-10-19 21:34 UTC. Source: [release v2.1.304](https://github.com/anthropics/claude-code/releases/tag/v2.1.304).

- [304:001] Added a transcript line when a plugin that runs first skips one of your mod's hooks, naming the event and the plugin  
  _Matches: mods, plugins, hooks_
- [304:002] Added `decider: "person"` to a mod's `tool.check` answer: only the permission dialog or a host's callback can approve the ask, and it is refused with the mod's reason where nobody can be asked  
  _Matches: mods, tools_
- [304:003] Added `e.isReadOnly` to a mod's `tool.check` event, set when the tool call is read-only  
  _Matches: mods, tools_
- [304:006] Added the names of the tools called earlier to the compaction summary in the transcript view (Ctrl+O)  
  _Matches: tools_
- [304:012] Fixed a plugin keeping a headless run going past `--max-turns`, Stop, or ended input by spawning subagents or re-running a finished one  
  _Matches: plugins_
- [304:013] Fixed a failed mod reload removing the tools and commands of the version that stays loaded, and its messages being wrong or silent about whether the previous version is still loaded  
  _Matches: mods, tools_
- [304:014] Fixed a click on a mod's button being lost when buttons with the same label and no `key` were redrawn unchanged  
  _Matches: mods_
- [304:015] Fixed mod sharing in the built-in `plugin-authoring` skill stopping at the secret scan on machines with managed settings and on Team and Enterprise plans  
  _Matches: mods, plugins, skills_
- [304:016] Fixed scheduled Cowork cloud sessions waiting five minutes again for each subagent whose WebFetch needed a URL approval that nobody was there to give  
  _Matches: tools (named tool)_
- [304:017] Fixed Write results and rejected edits showing a file outside the working directory as `../../…`; they now show `~/…` or the full path  
  _Matches: tools (named tool)_
- [304:018] Fixed a claude.ai Directory plugin's skills not running as commands when picked from the "/" menu in Cowork cloud sessions  
  _Matches: plugins, skills_
- [304:024] Fixed unsandboxed Bash commands in Claude Desktop Code tab sessions on macOS and Linux not seeing environment variables exported in shell startup files such as ~/.zshrc  
  _Matches: tools (named tool)_
- [304:029] Fixed `claude --help` text for `--tools`, `--resume`, `--debug`, `--json-schema`, `--disable-slash-commands`, `--system-prompt-snapshot` and `claude update` to match actual behavior  
  _Matches: tools_
- [304:031] Fixed resumed and cloud sessions sending Claude the whole skill list again each time plugins reloaded at startup  
  _Matches: plugins, skills_
- [304:032] Fixed an interrupt not ending a Read that waits on an idle pipe or device named like an image  
  _Matches: tools (named tool)_
- [304:034] Fixed a PreToolUse hook's deny reason being replaced by a timeout error when an Agent SDK callback hook on the same tool call timed out  
  _Matches: hooks, tools_
- [304:035] Fixed Bash and PowerShell deleting a large command's output file when it could not be copied to the session's tool-results folder, unless the disk is full  
  _Matches: tools_
- [304:039] Fixed a skill's `once` hook also removing another skill's identical hook after it ran  
  _Matches: skills, hooks_
- [304:044] Improved the lines shown when a mod written in the session loads, reloads or fails to load  
  _Matches: mods_
- [304:046] Improved cloud sessions: a new conversation's first turn no longer waits for the local (stdio) MCP servers of plugins synced from claude.ai, unless a server sets `alwaysLoad: true`  
  _Matches: plugins, MCP_
- [304:055] Changed mods' `settings.read` hooks to receive each settings layer and rewrite the merged settings, so a managed mod can make an organization's setting a ceiling, including the `cleanupPeriodDays` the retention sweep uses  
  _Matches: mods, hooks_
- [304:057] Changed the question that turns on the mods Claude writes in a session to plain text with no link or session id; it stays up when a new turn starts, and Claude tells you what loaded when you turn them on  
  _Matches: mods_
- [304:058] Changed tool search to be on by default behind a custom `ANTHROPIC_BASE_URL`; a 400 or 422 from the gateway is retried without it  
  _Matches: tools_
- [304:059] Changed compaction to send Claude the skill list again afterwards; `/reload-skills` now sends only new or changed skills  
  _Matches: skills_
- [304:060] Changed skill hooks: the skills of one source (a repo, your own folder, or a plugin) can register at most 1,024 hooks and 16,384 matcher characters per session  
  _Matches: plugins, skills, hooks_
- [304:061] Changed skills under a policy that allows hooks from plugins only: a skill used in the main conversation whose hooks are kept out no longer gets its `allowed-tools`  
  _Matches: plugins, skills, hooks, tools_
- [304:062] Updated the /claude-api skill to use the `ant` CLI on Claude Platform on AWS instead of falling back to the SDK or curl  
  _Matches: skills_
- [304:063] Removed the notes from `claude plugin validate` that predicted where a mod's hooks would run  
  _Matches: mods, plugins, hooks_
- [304:065] [VSCode] Added mod drawing in the chat panel for sessions on Amazon Bedrock, Google Vertex AI and Microsoft Foundry, behind an LLM gateway, or with telemetry turned off  
  _Matches: mods_
- [304:066] [VSCode] Fixed one cause of sessions failing to start with "Subprocess initialization did not complete within 60000ms": time a SessionStart command hook spends running no longer counts toward the limit, up to 10 minutes in total  
  _Matches: hooks_
- [304:068] [VSCode] Fixed a mod's drawings disappearing from a long-open panel until the next turn on machines that also run an older Claude Code  
  _Matches: mods_
- [304:070] [VSCode] Changed background sub-agents to show as one status line under their Agent card instead of streaming every step into the chat; the full transcript stays in /tasks  
  _Matches: tools (named tool)_

### 2.1.305

Published 2026-10-20 20:46 UTC. Source: [release v2.1.305](https://github.com/anthropics/claude-code/releases/tag/v2.1.305).

- [305:003] Fixed every request failing on Vertex, Bedrock and other providers when the endpoint or a gateway rejects tool search, and behind gateways with ToolSearch disallowed or left out of `--tools` (a 2.1.304 regression): Claude Code now retries without it  
  _Matches: tools_
- [305:006] Fixed Bash commands on a full disk failing with a raw `ENOSPC` file path: the error now says the disk is full and that nothing ran  
  _Matches: tools (named tool)_
- [305:007] Fixed an MCP server passed by a cloud session or by the SDK's `setMcpServers` being replaced later in the session by a same-named server from your own settings  
  _Matches: MCP_
- [305:010] Fixed more cases of scheduled Cowork cloud sessions waiting five minutes for each subagent whose WebFetch needed a URL approval that nobody was there to give  
  _Matches: tools (named tool)_
- [305:011] Fixed Workflow resume re-running already-completed `pipeline()` and `parallel()` agents instead of serving them from the run's journal  
  _Matches: tools (named tool)_
- [305:014] Fixed startup warnings printing as raw text above the logo: they now go to the debug log, and permission rules that restrict nothing show as warning rows under the banner  
  _Matches: rules_
- [305:018] Self-hosted runner: Fixed the orchestrator reporting a spawn-runner hook as timed out when a runner it started in the background kept its output open  
  _Matches: hooks_
- [305:020] Improved MCP consent dialogs so an Enter meant for the prompt is less likely to be taken as Accept  
  _Matches: MCP_
- [305:021] Improved a mod's `Image` to draw its picture in iTerm2 3.5 and later with fullscreen rendering, where it showed only its `alt` text  
  _Matches: mods_
- [305:023] Changed `allowedMcpServers` to stop filtering `managed-mcp.json` stdio servers that use `${VAR}` only in `env`: one your allowlist left out now loads on upgrade; use `deniedMcpServers` to keep it off  
  _Matches: MCP_
- [305:024] Changed plugins that Claude Desktop mounts by path to no longer keep their `allowed-tools` when your organization's managed settings set `allowManagedPermissionRulesOnly`  
  _Matches: plugins, rules, tools_
- [305:026] Changed a mod's docked pane to stay within 45% of the terminal's width, including a width kept from a wider terminal  
  _Matches: mods_
- [305:027] [VSCode] Added a "Running start-up hooks" spinner status, with a screen reader announcement, while SessionStart or Setup hooks run  
  _Matches: hooks_
- [305:029] [VSCode] Changed the message shown when a session does not start in time and no hook is running: it now leads with the output logs and lists causes instead of pointing to sign-in and network first  
  _Matches: hooks_
- [305:036] [Claude Tag] Improved Claude Tag admin pages in large organizations so plugin, skill and bundle edits work while the channel list is still loading  
  _Matches: plugins, skills_

### 2.1.306

Published 2026-10-21 03:16 UTC. Source: [release v2.1.306](https://github.com/anthropics/claude-code/releases/tag/v2.1.306).

- [306:002] Fixed an API error being replaced by "prompt is too long", and an unneeded compaction, in sessions with many MCP tools  
  _Matches: MCP, tools_

### 2.1.307

Published 2026-10-21 22:17 UTC. Source: [release v2.1.307](https://github.com/anthropics/claude-code/releases/tag/v2.1.307).

- [307:002] Added the `claude_code.safety_event` OpenTelemetry event for each tool call a permission rule, auto mode, a safety check, a hook or the sandbox stopped, prompted or sent back  
  _Matches: rules, hooks, tools_
- [307:005] Fixed MCP servers showing "needs authentication" in `claude -p` on macOS while the login keychain was locked; they now say why, and the next run after an unlock connects without a new sign-in  
  _Matches: MCP_
- [307:006] Fixed MCP servers being reported as timed out, and staying failed in headless runs, when a macOS or Linux computer went to sleep while they were connecting  
  _Matches: MCP_
- [307:007] Fixed HTTP MCP tool calls being sent twice when the connection closed mid-call; only read-only or idempotent tools are now retried  
  _Matches: MCP, tools_
- [307:008] Fixed a turn sometimes starting without an SDK MCP server's latest tools when a background task was running  
  _Matches: MCP, tools_
- [307:009] Fixed some "Autocompact is thrashing" errors in turns that read many PDF pages, images or other large tool results  
  _Matches: tools_
- [307:015] Fixed `/help` and the `/` command menu showing long model-facing descriptions for bundled skills such as `/claude-api` instead of their short descriptions  
  _Matches: skills_
- [307:019] Fixed WebFetch in Cowork cloud sessions reporting a tool error when a site answered with a 4xx status or a robots.txt refusal; it is now a normal result, as in local sessions  
  _Matches: tools_
- [307:020] Fixed write tools on a directly configured GitHub MCP server showing a form that closed without creating anything in the desktop app's Code tab  
  _Matches: MCP, tools_
- [307:021] Fixed Artifact tool reads failing with a connection reset when the server had closed a reused connection  
  _Matches: tools_
- [307:023] Self-hosted runner: Fixed archiving or requeueing a session, or stopping the runner, during its checkout hook leaving the hook's processes running and the runner's slot held  
  _Matches: hooks_
- [307:024] Improved recovery from unparseable tool calls: Claude Code now retries the call up to twice before ending the turn with an error  
  _Matches: tools_
- [307:028] Improved the time to the first reply in cloud sessions when one of the desktop app's MCP servers can't connect  
  _Matches: MCP_
- [307:030] Changed the notice Claude gets when the WebSearch budget is used up to also tell it not to query search engines in a browser or through computer use  
  _Matches: tools (named tool)_
- [307:032] Self-hosted runner: Changed checkout hooks to be stopped after 30 minutes by default, failing the session's setup; if yours needs longer, raise `--checkout-hook-timeout-min` or set it to `0`  
  _Matches: hooks_

### 2.1.308

Published 2026-10-22 04:34 UTC. Source: [release v2.1.308](https://github.com/anthropics/claude-code/releases/tag/v2.1.308).


### 2.1.309

Published 2026-10-22 22:18 UTC. Source: [release v2.1.309](https://github.com/anthropics/claude-code/releases/tag/v2.1.309).

- [309:001] Fixed sandboxed Bash commands on macOS and Linux running the shell's startup files outside the sandbox before each command  
  _Matches: tools (named tool)_
- [309:003] Fixed sandboxed commands and auto-accepted edits being able to modify the MCP config file passed with `--mcp-config`  
  _Matches: MCP_
- [309:004] Fixed a disabled MCP server being reconnected by a later permission prompt in print and SDK sessions  
  _Matches: MCP_
- [309:005] Fixed the Bash permission check trusting a variable set by a command whose redirect can fail to open  
  _Matches: tools (named tool)_
- [309:006] Fixed Bash permission checks not prompting for some compound commands that change directory before running git when the `cd` is wrapped or prefixed, as they do for a plain `cd`  
  _Matches: tools (named tool)_
- [309:007] Fixed an `Edit(path)` deny rule not blocking a Bash redirect to that path in some commands that also held a subshell  
  _Matches: rules_
- [309:012] Fixed sessions compacting repeatedly after reading files under a very large nested CLAUDE.md; a nested CLAUDE.md over the size limit now loads only its start  
  _Matches: CLAUDE.md_
- [309:013] Fixed ctrl+enter (send now) only queuing a message when pressed before the response had started, and restarting a prompt's hooks while leaving the message queued when pressed while those hooks were running  
  _Matches: hooks_
- [309:016] Fixed long tool output previews being cut through an emoji, leaving session transcripts that `jq` could not parse  
  _Matches: tools_
- [309:017] Fixed Read reporting "File does not exist" for PDF page ranges in Linux sandboxes that share the parent's `/proc`  
  _Matches: tools (named tool)_
- [309:021] Fixed split-pane agent teammates not inheriting the tool deny and `--tools` rules given on the leader's command line  
  _Matches: rules, tools_
- [309:027] Fixed a skill in an `--add-dir` folder being unreachable when another skill already held its name; it is now offered as `<folder>:<name>`  
  _Matches: skills_
- [309:028] Fixed `/verify` and `/code-review` not finding a nested package's own skill when its files were changed from the shell  
  _Matches: skills_
- [309:029] Fixed the /claude-api skill saying that `ant beta:worker poll --on-work` passes trace context to the command  
  _Matches: skills_
- [309:030] Fixed the /claude-api skill's C# tracing setup missing spans from the cloud platform clients  
  _Matches: skills_
- [309:031] Fixed the /claude-api skill saying that API spans for requests to Claude Platform on AWS can't join the caller's trace  
  _Matches: skills_
- [309:032] Fixed hooks that run in PowerShell not blocking when the hook's program exits with code 2, and on Windows `PreToolUse` and `PermissionRequest` hooks with `"shell": "powershell"` failing open when Git for Windows isn't installed  
  _Matches: hooks, tools_
- [309:033] Fixed a mod's `turn.step` hook that names a model by alias, such as `haiku`, failing every request with a model error: the alias now resolves to its model  
  _Matches: mods, hooks_
- [309:034] Fixed plugins and skills synced from claude.ai being removed, sometimes mid-session, after a disk read error  
  _Matches: plugins, skills_
- [309:037] Fixed fine-grained tool streaming staying off on Amazon Bedrock when `ANTHROPIC_BEDROCK_BASE_URL` is set to the default `bedrock-runtime.<region>.amazonaws.com` endpoint  
  _Matches: tools_
- [309:041] Windows: Fixed PowerShell permission checks auto-approving some `Set-Location` or `cd` commands that target the current directory and carry extra arguments; these now prompt for approval  
  _Matches: tools (named tool)_
- [309:042] macOS: Fixed the "Install Command Line Developer Tools" dialog opening each time Claude Code starts on a Mac without Xcode or the Command Line Tools  
  _Matches: tools_
- [309:045] Improved the error when a hooks module is nested too deep to load: it now names the file instead of showing a bare stack-overflow message  
  _Matches: hooks_
- [309:046] Improved disk-full handling: a Bash command cut off by a full disk now says so and names the folder to free up, and starting on a full temp volume prints a clear message, not a raw ENOSPC error  
  _Matches: tools (named tool)_
- [309:047] Improved the /claude-api skill to offer API tracing alongside SDK tracing when asked to add OpenTelemetry  
  _Matches: skills_
- [309:048] Improved the /claude-api skill to check the live docs before saying a feature is unsupported  
  _Matches: skills_
- [309:049] Self-hosted runner: Improved sessions that move to a new runner: Claude now sees the tool call that was interrupted, marked as outcome unknown  
  _Matches: tools_
- [309:050] Updated the bundled dataviz skill to accept APCA as a text-contrast measure (keeping WCAG 2 ratios where AA conformance is required), add an `apca(text, background)` function to its palette validator scripts, and say whether a label inside a colored chart fill should be white or near-black  
  _Matches: skills_
- [309:051] Updated the /claude-api skill: service account keys and Workload Identity Federation tokens can now manage OpenTelemetry destinations  
  _Matches: skills_
- [309:052] Changed `sed -i` to get the standard Bash prompt and run as written, not a simulated file-edit preview; like other Bash edits, it is no longer restored by `/rewind`  
  _Matches: tools (named tool)_
- [309:057] Changed the `/claude-api` skill to build Managed Agents subagent teams on `multiagent_20261001` with dynamic workflows on by default, instead of `coordinator`  
  _Matches: skills_
- [309:064] [VSCode] Fixed a mod's "From the … plugin" label above the prompt being drawn over the slash command and @-mention menus (anthropics/claude-code#102981)  
  _Matches: mods, plugins_
- [309:067] [VSCode] Improved Edit and Write speed in the chat panel: the wait for new problems after each edit is now 0.75 seconds in most cases, down from 1 to 1.5 seconds  
  _Matches: tools (named tool)_
- [309:071] [Cloud sessions] Fixed the "read documentation" tool row in cloud sessions, which showed escaped JSON instead of a readable page  
  _Matches: tools_

### 2.1.310

Published 2026-10-23 23:39 UTC. Source: [release v2.1.310](https://github.com/anthropics/claude-code/releases/tag/v2.1.310).

- [310:001] Added the Monitor tool and plugin monitors on Bedrock, Vertex, and Foundry, and when telemetry or nonessential traffic is disabled; long foreground sleeps are now blocked there too  
  _Matches: plugins, tools_
- [310:007] Windows: Fixed PreToolUse and PermissionRequest hooks letting a tool call through when Git Bash is missing and the hook's command is only quoted strings, such as a quoted path  
  _Matches: hooks, tools_
- [310:010] Improved a mod's `Image` to draw inside tmux with `allow-passthrough` and `focus-events` on, in kitty, Ghostty, and iTerm2 3.5+ with fullscreen rendering, where it showed only its `alt` text  
  _Matches: mods_
- [310:012] Changed the error for an MCP tool call that times out in a non-interactive session while the server's elicitation is unanswered: it now tells Claude that no answer came and not to repeat the call  
  _Matches: MCP, tools_

### 2.1.311

Published 2026-10-26 21:51 UTC. Source: [release v2.1.311](https://github.com/anthropics/claude-code/releases/tag/v2.1.311).

- [311:003] Fixed long freezes at startup and after reading or editing files when a CLAUDE.md file holds a very long list item  
  _Matches: CLAUDE.md_
- [311:004] Fixed interrupting Claude not taking effect until a timeout while an MCP server had not answered a resource read or a skill was still downloading  
  _Matches: MCP, skills_
- [311:006] Fixed Write and Edit stalling for up to 5 seconds after they ran, and reporting 0 lines changed, when changing thousands of lines in a file  
  _Matches: tools (named tool)_
- [311:007] Fixed subagents being unable to use MCP tools from servers that finish connecting after the subagent starts  
  _Matches: MCP, tools_
- [311:008] Fixed Claude seeing stale MEMORY.md and CLAUDE.md content right after automatic compaction when those files were edited earlier in the session  
  _Matches: CLAUDE.md_
- [311:010] Fixed `SubagentStop` hooks running about twice a minute for each running subagent instead of once when it finishes  
  _Matches: hooks_
- [311:011] Fixed the @ file picker ignoring `.ignore`/`.rgignore` negation rules that re-include git-ignored files  
  _Matches: rules_
- [311:014] Fixed the Bash tool description claiming the working directory always persists between calls  
  _Matches: tools_
- [311:015] Fixed the environment block naming a shell commands don't run in, such as fish when the Bash tool uses zsh  
  _Matches: tools_
- [311:016] Fixed `claude mcp add`, `claude mcp remove` and `/mcp` naming the current folder instead of the project entry in `~/.claude.json` that holds a local-scope server when run below a repository root  
  _Matches: MCP_
- [311:017] Fixed `claude mcp list` and `claude mcp get` showing the error code twice on failed-connection lines (for example `ENOENT: ENOENT: …`)  
  _Matches: MCP_
- [311:021] Fixed WebFetch and WebSearch hanging on a stalled response in Cowork cloud sessions; an unfinished request now fails after 300 seconds  
  _Matches: tools (named tool)_
- [311:027] Fixed the Write tool's file preview skipping rows and miscounting hidden lines when a line is wider than the terminal  
  _Matches: tools_
- [311:029] Fixed Cowork cloud sessions losing their connectors and most tools after a restart when a plugin or your settings named an `agent`; Cowork cloud sessions now ignore that setting  
  _Matches: plugins, tools_
- [311:036] Fixed a finished `/code-review`, or another skill that runs in a sub-agent, running a second time when a cloud or background session restarts  
  _Matches: skills_
- [311:038] Fixed `/ide` saying it had installed the JetBrains plugin when nothing was installed  
  _Matches: plugins_
- [311:041] Fixed `/mcp` showing a remote server as failed after "Clear authentication" when the server works without sign-in  
  _Matches: MCP_
- [311:042] Fixed `/mcp` showing "authenticated" for a remote server that Claude Code sends no credentials to  
  _Matches: MCP_
- [311:043] Fixed a `--plugin-dir` folder of plugins loading as one plugin when an empty `.mcp.json` was at its top  
  _Matches: plugins, MCP_
- [311:047] Fixed the /rewind warning that wrongly said manual and Bash edits are never affected by a code restore  
  _Matches: tools (named tool)_
- [311:050] Linux: Fixed sandboxed Bash commands failing with `bwrap: Can't create file` when a `--plugin-dir` folder was also an added directory and `permissions.blockReadsOutsideWorkingDirectories` was on  
  _Matches: plugins_
- [311:058] Improved the Artifact tool's choice between a page and a document: explainers and visual or interactive work become artifact pages; documents are for writing people keep editing or pass around  
  _Matches: tools_
- [311:061] Improved screen reader mode: deleting a rule in /permissions says "Deleted allow rule …" right away  
  _Matches: rules_
- [311:063] Improved Slack connector sends: Claude now checks a channel's topic for posting rules before messaging a channel you didn't name  
  _Matches: rules_
- [311:070] Changed startup warnings about permission rules in settings files to show once per user until the rule changes  
  _Matches: rules_
- [311:072] Changed `DISABLE_COMPACT` in settings files and in a mod's `$.env.set` so they can only turn compaction off, not back on  
  _Matches: mods_
- [311:074] Changed sessions that set `CLAUDE_CODE_SYNC_SKILLS` with feature-flag fetching off to reuse a claude.ai skills list up to 10 minutes old that another session on the machine fetched  
  _Matches: skills_
- [311:078] [VSCode] Added a "Running UserPromptSubmit hooks" spinner status and screen reader announcement for slow UserPromptSubmit hooks  
  _Matches: hooks_
- [311:079] [VSCode] Fixed custom skills and custom slash commands sent from the VS Code or JetBrains panel leaving out the open file or selected lines that ordinary messages include (anthropics/claude-code#102799)  
  _Matches: skills_
- [311:081] [VSCode] Fixed clicking an image in a tool result, or closing its preview, also opening the result's text in an editor tab  
  _Matches: tools_
- [311:088] [Claude Tag] Added a Skills view to Claude Tag analytics showing how often Claude runs each attached skill in Slack channels and which go unused, with Usage links in admin settings  
  _Matches: skills_

### 2.1.312

Published 2026-10-27 20:24 UTC. Source: [release v2.1.312](https://github.com/anthropics/claude-code/releases/tag/v2.1.312).

- [312:004] Fixed Claude overwriting a very large CLAUDE.md, rules file or @-included file in a subdirectory after seeing only its start; Write now asks Claude to read it all or edit in place  
  _Matches: rules, CLAUDE.md_
- [312:005] Fixed per-directory and `paths:` skills not being found after a Bash `cd` deeper into a git repository  
  _Matches: skills_
- [312:008] Fixed the Read tool sometimes failing on PDF pages with "pdftoppm failed: Could not write image" when the clean-up of old session files ran at the same time  
  _Matches: tools_
- [312:017] Improved WebFetch errors in cloud sessions: a host that does not resolve is now explained as possibly outside the allowed network domains, so Claude names the host to allow  
  _Matches: tools (named tool)_
- [312:022] Changed prompt and agent hooks to run at most 24 at a time per session, sub-agents included, plus at most 12 that have waited longer than their event's timeout; a `timeout` under 1 second now counts as 1 second  
  _Matches: hooks_
- [312:024] Changed OpenTelemetry `mcp_server.name` to report the real name of fixed-URL remote MCP servers declared by plugins from the official Anthropic marketplace, instead of `custom`  
  _Matches: plugins, MCP, marketplace_

### 2.1.314

Published 2026-10-30 01:06 UTC. Source: [release v2.1.314](https://github.com/anthropics/claude-code/releases/tag/v2.1.314).

- [314:001] Added `permissions.blockWritesOutsideWorkingDirectories`: Write, Edit and NotebookEdit refuse paths outside the working directories in every permission mode  
  _Matches: tools (named tool)_
- [314:009] Fixed repeated refused requests behind a gateway that doesn't accept tool search's `tool_reference` blocks: the request is sent again once without tool search, and the session remembers  
  _Matches: tools_
- [314:011] Fixed MCP servers that also work without sign-in showing "needs authentication" after their stored sign-in stopped working; they are now used signed out  
  _Matches: MCP_
- [314:012] Fixed `claude mcp logout` reporting success when the MCP sign-in was not removed, for example while the macOS keychain is locked over SSH  
  _Matches: MCP_
- [314:016] Fixed model switching being refused on machines with managed plugin settings when one of your own `--plugin-dir` or `--plugin-url` plugins had a broken manifest or failed to download  
  _Matches: plugins_
- [314:021] Fixed the last broken reply and its retry prompts staying in the conversation after Claude gave up on a tool call that could not be parsed  
  _Matches: tools_
- [314:022] Fixed a PreCompact hook with very large output making compaction fail or repeat; each hook's output is now cut at 10,000 characters  
  _Matches: hooks_
- [314:025] Fixed the /resume picker showing the text of CLAUDE.md or CLAUDE.local.md as a session's title when the session only ran slash commands  
  _Matches: CLAUDE.md_
- [314:031] Fixed shell and MCP calls that auto mode, a deny rule or a PreToolUse hook blocked, or that otherwise did not run, reading as if they ran in a collapsed tool group  
  _Matches: MCP, rules, hooks, tools_
- [314:033] Fixed hooks matching Bash not running on shell commands started by the Monitor tool; such hooks can block or ask, but not approve or rewrite those commands  
  _Matches: hooks, tools_
- [314:034] Fixed a settings file excluded with `--setting-sources` still supplying some settings, such as auto mode rules and saved permission consents  
  _Matches: rules_
- [314:045] Fixed WebFetch in Cowork cloud sessions silently dropping a PDF's text past 100,000 characters; it now says how much was unread and where to read on  
  _Matches: tools (named tool)_
- [314:062] Fixed the skill file watcher checking every removed skill kept in `~/.claude/skills/.trash`, which added file system load that grew with each removal  
  _Matches: skills_
- [314:066] Fixed `~/.claude/skills/.trash` and `~/.claude/plugins/.trash` growing without limit: each now holds about 1024 entries, whatever `cleanupPeriodDays` says  
  _Matches: plugins, skills_
- [314:067] Fixed the Bash edit diff listing a whole file as changed when a CRLF file under git's line-ending conversion was re-saved unchanged or had one line edited  
  _Matches: tools (named tool)_
- [314:069] Improved memory use in long headless and SDK turns that run many subagents: the parent session no longer keeps each subagent's tool results until the turn ends  
  _Matches: tools_
- [314:078] Improved session auto-titles: a session that starts with a skill or a prompt-based command such as `/security-review` now gets a title from it instead of staying untitled  
  _Matches: skills_
- [314:080] Improved `/context` speed in sessions with ten thousand or more MCP tools  
  _Matches: MCP, tools_
- [314:082] Updated the `/claude-api` skill: its Datadog setup for API tracing now sends the `dd-llmobs-enabled: true` header, as the Console does, and its `ant` install instructions drop the outdated macOS `xattr` step  
  _Matches: skills_
- [314:083] Updated the bundled dataviz skill to advise printing y-axis tick labels in full under 10,000, and horizontal ones in full under a million where they fit  
  _Matches: skills_
- [314:084] Updated the bundled dataviz skill to answer donut and pie chart requests with ranked bars or a segmented bar that prints its values  
  _Matches: skills_
- [314:085] Changed Claude's file tools to ask before editing the local copy of your organization's server-managed settings, as they do for your settings files  
  _Matches: tools_
- [314:087] Changed the Bash tool's shell to clear any inherited `which` alias or function and to stop passing exported `which`/`unsetenv` functions to commands, so `which` is the system command or zsh builtin  
  _Matches: tools_
- [314:089] Changed auto mode in Cowork cloud sessions: a hook's allow of an MCP tool call now counts as no answer, so the classifier or a permission prompt decides  
  _Matches: MCP, hooks, tools_
- [314:090] Changed hook `if` conditions such as `Monitor(tail *)` to match the Monitor tool's shell commands as `Bash(tail *)` matches Bash's  
  _Matches: hooks, tools_
- [314:091] Changed the `claude-api` skill to ask to read a Managed Agents workflow run's workflow before changing the agent to improve that run  
  _Matches: skills_
- [314:096] [VSCode] Fixed "Clear authentication" for MCP servers reporting success when the saved sign-in could not be removed  
  _Matches: MCP_
- [314:097] [VSCode] Fixed missing spinner and Stop button while a queued message's hooks run  
  _Matches: hooks_
- [314:102] [VSCode] Changed `CLAUDE_CODE_DISABLE_CFC_PROMPT` to also stop the extension adding the Claude in Chrome instructions to a session's messages; the browser tools stay available  
  _Matches: tools_
- [314:108] [Cloud sessions] Improved scheduled tasks: runs in Anthropic's cloud now load the plugins enabled on your claude.ai account  
  _Matches: plugins_
- [314:109] [Cloud sessions] Improved Test connection for GitHub Enterprise in admin settings to also connect the way cloud sessions do, and to warn you when that second test fails  
  _Matches: test_
- [314:118] [Claude Tag] Fixed Retry on plugin and skill pages in Claude Tag admin settings discarding unsaved access changes after a failed load; your edits now stay in place  
  _Matches: plugins, skills_

## Appendix A: versions with no release notes

- 2.1.297, 2.1.298 and 2.1.313: not published (see Coverage).

## Appendix B: near-miss entries not listed

These entries touch a requested topic but contain none of its keywords and name no built-in tool. Nery decides whether to add them.

- [296:038] Fixed `/code-review` ending on a raw JSON array in cloud sessions, the Agent SDK and IDE integrations; the findings now print as a numbered list  
  _Not listed: `/code-review` is a bundled command; the entry names no requested keyword._
- [296:050] Windows: Fixed `rm -rf /c/Users/<name>` in Git Bash not asking in bypass permissions mode  
  _Not listed: Bash permission behavior; the entry names no tool._
- [296:055] Improved `--debug` output to name unrecognized frontmatter fields in custom agent files, with a hint for likely typos  
  _Not listed: custom agent files, not skills or plugins._
- [299:030] Fixed rm prompts on shell `-c` scripts that don't run `rm`. An rm built at run time in a script Claude Code can't read no longer prompts unless `CLAUDE_CODE_STRICT_INLINE_SHELL_RM_PROMPT=1`  
  _Not listed: shell permission prompts; the entry names no tool._
- [299:112] Fixed a custom slash command's embedded shell line running twice when a newer message interrupted the command while its prompt was being checked  
  _Not listed: custom slash command; the entry names no requested keyword._
- [300:041] Fixed Claude polling a background command's output file or sleeping while it runs  
  _Not listed: background command behavior; the entry names no tool._
- [304:005] Added `/claude-api managed-agents-secure`, which compares a Managed Agents agent's settings with Anthropic's published security guide, without changing anything  
  _Not listed: `/claude-api` is a bundled skill; the entry does not say skill._
- [304:010] Fixed `rm -r` of a mounted drive or a folder at its top level (`/Volumes`, `/media`, WSL's `/mnt/c`) not getting the safety prompt that `rm -rf /Applications` gets  
  _Not listed: shell safety prompt; the entry names no tool._
- [307:001] Added `/claude-api api-version` to move Claude API code to API version `2026-10-21`  
  _Not listed: `/claude-api` is a bundled skill; the entry does not say skill._
- [310:005] Fixed file read permission prompts not showing where a symbolic link leads  
  _Not listed: read permission prompt; the entry names no tool._
- [311:056] Improved shell commands that reach their timeout: the result now shows the output so far and says the command is still running in the background  
  _Not listed: shell command behavior; the entry names no tool._
- [311:071] Changed `/code-review` to tell Claude to put the effort level first and use max only when asked  
  _Not listed: `/code-review` is a bundled command; the entry names no requested keyword._
- [312:007] Fixed a command with an invalid name stopping all commands from loading, which could leave `claude -p` with no output  
  _Not listed: command files; the entry names no requested keyword._
- [312:015] Fixed `/verify` showing a long description meant for Claude in `/help` and the `/` command menu instead of a short one  
  _Not listed: `/verify` is a bundled skill; the entry does not say skill._

## Verification

- Entries read, version by version, from the release bodies: 1130 across 17 versions. The CHANGELOG sections hold the same 1130 entries.
- Listed: 435 (390 by keyword and 45 by named tool). Near-miss, not listed: 14. Reviewed and outside the requested topics: 681.
- 435 + 14 + 681 = 1130.
