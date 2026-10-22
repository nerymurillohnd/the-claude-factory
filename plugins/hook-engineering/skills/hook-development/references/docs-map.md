# Official docs map

Use this map to find the official section behind a fact and open it. The references condense the official pages; this map lists every official heading they draw on, so you can open the exact section and read it in full. Look a heading up by name; the tables are for lookup, not for reading end to end.

Use it before citing, checking or re-verifying any fact about prompt, agent or background hooks, hook security, PowerShell hooks or hook debugging: it says where each fact lives in the official source and how to fetch it.

> Precedence: the changelog and the user's own debug log win over the docs for released behavior; the docs win over this map; this map wins over memory. When the docs and the changelog disagree for the user's version, report both and say which version each applies to. The full order is in `sources.md` → Which source wins.

## Contents

- How to open a section
- Retrieve a section's exact text
- Read the changelog for a version range
- Hooks reference
- Hooks guide
- Other official pages
- How to use the tables below
- Hooks reference: prompt and agent hooks
- Hooks reference: events that accept prompt and agent hooks
- Hooks reference: background hooks
- Hooks reference: security, PowerShell, debugging
- Hooks reference: supporting sections
- Hooks guide: prompt, agent and troubleshooting sections
- Other pages
- Out of scope: where to point

## How to open a section

- **The Claude Code docs server** (preferred): the official Claude Code docs MCP server (<https://code.claude.com/docs/mcp>), which the user adds; this plugin doesn't bundle it. Added in Claude Code under the name the plugin's README gives, its tools are `mcp__claude-code-docs__<tool>`. Added as a Claude app connector, they reach Claude Code as `mcp__claude_ai_<connector name>__<tool>`; when both point at that URL, Claude Code connects the one added in Claude Code and hides the connector. Find the tools with ToolSearch, query `claude_code_docs`, which matches them under any server name, and load them if they are deferred. If none is connected, tell the user once that `claude mcp add --transport http --scope user claude-code-docs https://code.claude.com/docs/mcp` adds it, and use the raw page below. Its filesystem tool serves each page as a file. Find the heading, then read from it:
  `rg -n '^#+ PreToolUse decision control$' /en/hooks.mdx`, then `sed -n '<line>,<line+80>p' /en/hooks.mdx`. Search a topic across pages with `rg -n -i '<words>' /en/`.
  Configuration example: `rg -n '^#+ Matcher patterns$' /en/hooks.mdx`, then `sed -n '<line>,<line+80>p' /en/hooks.mdx`.
- **Raw page**: when a heading from this map is missing in the server's copy, or a decision rests on the exact text, fetch the page's raw Markdown as below. When the two differ, the raw page wins: on 2026-10-20 the server's `/en/hooks-guide.mdx` lacked `## Limitations and troubleshooting`, which the raw <https://code.claude.com/docs/en/hooks-guide.md> has.
- **WebFetch** (last resort): it returns a model's summary, not the source. Use it only to locate a section, never to quote a field, default or version, and mark anything that rests on it `unverified against live docs`.
- **Search**: if a heading is missing from both the server's copy and the raw page, the page moved. Search the docs for the heading text and use what you find. Never edit this plugin's files; say in your answer that the map is out of date so the user can report it.

Each line gives the heading's URL and the heading as written in the page source (`#` level + title). Anchors follow the site's rule (lowercase, punctuation and spaces become `-`, backticks dropped), checked against the anchors the docs pages link to themselves. The page source wins over this map, and the changelog wins over the page (see the precedence rule in sources.md).

Leading `/` in a heading: an anchor keeps it URL-encoded as `%2F` (the rule the configuration entries were built with); the docs search returns the same anchors with a plain `/`. Both spellings appear below; copy anchors from this map, never rebuild them by hand.

## Retrieve a section's exact text

Order: the docs server to search and read (item 2), the raw page whenever a decision rests on the wording or the server lacks a heading (item 1), WebFetch last (item 3). Prefer raw Markdown over summaries. Each page serves raw Markdown at its URL plus `.md`, such as <https://code.claude.com/docs/en/hooks.md>.

1. **Shell (exact text; use it whenever a decision rests on the wording or the server lacks a heading):** fetch the page once and cut the section by its exact header. The section ends at the next header of the same or a higher level:

   ```bash
   curl -sS https://code.claude.com/docs/en/hooks.md |
     awk -v h='### Response schema' '
       $0 == h { p = 1; n = index(h, " ") - 1; print; next }
       p && /^#+ / { m = index($0, " ") - 1; if (m <= n) exit }
       p'
   ```

2. **Claude Code Docs MCP (main session, when connected):** read `/en/hooks.mdx` with the filesystem tool, for example `rg -n -F '### Response schema' /en/hooks.mdx` and then `sed -n '<line>,<line+60>p' /en/hooks.mdx`. Its index can be incomplete: if a header from this map is missing there, fetch the raw page (item 1); if it is missing there too, use the search tool, whose `Link` field gives the live anchor.
3. **WebFetch (last resort):** it returns a model's summary, not the source. Use it only to locate a section, never to quote a field, default or version. Mark anything that rests on it `unverified against live docs`.

If none of the three reaches the docs, say so and mark every version-sensitive claim `unverified against live docs`.

## Read the changelog for a version range

The docs describe the latest release and often lag it by a release; fixes and behavior changes often appear only in the changelog.

| Source | URL | Use |
| :-- | :-- | :-- |
| Raw changelog (newest first, `## <version>` headers) | <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md> | Primary. Updated with each release |
| Docs changelog page | <https://code.claude.com/docs/en/changelog> | Cross-check; can trail the raw file by a release |


List the hook entries of every release newer than a version with the changelog script in `SKILL.md`: pass the skill's baseline, or the user's version (what `claude --version` prints) to list the changes the user's build lacks; the docs may already describe them. Its search terms include `hook`, every event name except a bare `Stop`, `asyncRewake`, `ARGUMENTS`, `continueOnBlock`, `stop_hook_active`, `disableAllHooks` (through `Hook`) and `trust`. A bare `Stop` would mostly match the Stop button and stopped turns. A changelog entry about `Stop` that says neither `hook` nor `stop_hook_active` is not listed: search the changelog for `Stop` by hand when the question involves that event.

Read each matching line in its release, then apply the precedence rule above.

## Hooks reference

Page: <https://code.claude.com/docs/en/hooks> · MCP path: `/en/hooks.mdx`

- [Hook lifecycle](https://code.claude.com/docs/en/hooks#hook-lifecycle) — `## Hook lifecycle`
  - [How a hook resolves](https://code.claude.com/docs/en/hooks#how-a-hook-resolves) — `### How a hook resolves`
- [Configuration](https://code.claude.com/docs/en/hooks#configuration) — `## Configuration`
  - [Hook locations](https://code.claude.com/docs/en/hooks#hook-locations) — `### Hook locations`
  - [Matcher patterns](https://code.claude.com/docs/en/hooks#matcher-patterns) — `### Matcher patterns`
    - [Match MCP tools](https://code.claude.com/docs/en/hooks#match-mcp-tools) — `#### Match MCP tools`
  - [Hook handler fields](https://code.claude.com/docs/en/hooks#hook-handler-fields) — `### Hook handler fields`
    - [Common fields](https://code.claude.com/docs/en/hooks#common-fields) — `#### Common fields` (the `timeout` row lists the default timeouts per hook type and event)
      - [How if patterns match Bash commands](https://code.claude.com/docs/en/hooks#bash-if-matching) — `<h4 id="bash-if-matching">` How if patterns match Bash commands
    - [Command hook fields](https://code.claude.com/docs/en/hooks#command-hook-fields) — `#### Command hook fields`
      - [Exec form and shell form](https://code.claude.com/docs/en/hooks#exec-form-and-shell-form) — `##### Exec form and shell form`
    - [HTTP hook fields](https://code.claude.com/docs/en/hooks#http-hook-fields) — `#### HTTP hook fields`
    - [MCP tool hook fields](https://code.claude.com/docs/en/hooks#mcp-tool-hook-fields) — `#### MCP tool hook fields`
      - [How the tool's result is read](https://code.claude.com/docs/en/hooks#how-the-tools-result-is-read) — `##### How the tool's result is read`
      - [When the server is still connecting](https://code.claude.com/docs/en/hooks#when-the-server-is-still-connecting) — `##### When the server is still connecting`
      - [Events that fire before MCP servers are available](https://code.claude.com/docs/en/hooks#events-that-fire-before-mcp-servers-are-available) — `##### Events that fire before MCP servers are available`
    - [Prompt and agent hook fields](https://code.claude.com/docs/en/hooks#prompt-and-agent-hook-fields) — `#### Prompt and agent hook fields`
  - [Reference scripts by path](https://code.claude.com/docs/en/hooks#reference-scripts-by-path) — `### Reference scripts by path`
  - [Hooks in skills and agents](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents) — `### Hooks in skills and agents`
  - [The /hooks menu](https://code.claude.com/docs/en/hooks#the-%2Fhooks-menu) — ### The `/hooks` menu
  - [Disable or remove hooks](https://code.claude.com/docs/en/hooks#disable-or-remove-hooks) — `### Disable or remove hooks`
- [Hook input and output](https://code.claude.com/docs/en/hooks#hook-input-and-output) — `## Hook input and output`
  - [Common input fields](https://code.claude.com/docs/en/hooks#common-input-fields) — `### Common input fields`
  - [Exit code output](https://code.claude.com/docs/en/hooks#exit-code-output) — `### Exit code output`
    - [Exit code 0](https://code.claude.com/docs/en/hooks#exit-code-0) — `#### Exit code 0`
    - [Exit code 2](https://code.claude.com/docs/en/hooks#exit-code-2) — `#### Exit code 2`
    - [Other exit codes](https://code.claude.com/docs/en/hooks#other-exit-codes) — `#### Other exit codes`
    - [Timeouts](https://code.claude.com/docs/en/hooks#timeouts) — `#### Timeouts`
    - [Hooks that start a background process](https://code.claude.com/docs/en/hooks#hooks-that-start-a-background-process) — `#### Hooks that start a background process`
    - [Block the action when a hook fails](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails) — `#### Block the action when a hook fails`
    - [Failed hooks on Windows without Git Bash](https://code.claude.com/docs/en/hooks#failed-hooks-on-windows-without-git-bash) — `#### Failed hooks on Windows without Git Bash`
    - [Exit code 2 behavior per event](https://code.claude.com/docs/en/hooks#exit-code-2-behavior-per-event) — `#### Exit code 2 behavior per event`
  - [HTTP response handling](https://code.claude.com/docs/en/hooks#http-response-handling) — `### HTTP response handling`
  - [JSON output](https://code.claude.com/docs/en/hooks#json-output) — `### JSON output`
    - [Emit terminal notifications](https://code.claude.com/docs/en/hooks#emit-terminal-notifications) — `#### Emit terminal notifications`
    - [Add context for Claude](https://code.claude.com/docs/en/hooks#add-context-for-claude) — `#### Add context for Claude`
    - [Decision control](https://code.claude.com/docs/en/hooks#decision-control) — `#### Decision control`
- [Hook events](https://code.claude.com/docs/en/hooks#hook-events) — `## Hook events`
  - [SessionStart](https://code.claude.com/docs/en/hooks#sessionstart) — `### SessionStart`
    - [SessionStart input](https://code.claude.com/docs/en/hooks#sessionstart-input) — `#### SessionStart input`
    - [SessionStart decision control](https://code.claude.com/docs/en/hooks#sessionstart-decision-control) — `#### SessionStart decision control`
    - [Reload skills that a hook installs](https://code.claude.com/docs/en/hooks#reload-skills-that-a-hook-installs) — `#### Reload skills that a hook installs`
    - [Persist environment variables](https://code.claude.com/docs/en/hooks#persist-environment-variables) — `#### Persist environment variables`
      - [Persisted variables in PowerShell commands](https://code.claude.com/docs/en/hooks#persisted-variables-in-powershell-commands) — `##### Persisted variables in PowerShell commands`
  - [Setup](https://code.claude.com/docs/en/hooks#setup) — `### Setup`
    - [Setup input](https://code.claude.com/docs/en/hooks#setup-input) — `#### Setup input`
    - [Setup decision control](https://code.claude.com/docs/en/hooks#setup-decision-control) — `#### Setup decision control`
  - [InstructionsLoaded](https://code.claude.com/docs/en/hooks#instructionsloaded) — `### InstructionsLoaded`
    - [InstructionsLoaded input](https://code.claude.com/docs/en/hooks#instructionsloaded-input) — `#### InstructionsLoaded input`
    - [InstructionsLoaded decision control](https://code.claude.com/docs/en/hooks#instructionsloaded-decision-control) — `#### InstructionsLoaded decision control`
  - [UserPromptSubmit](https://code.claude.com/docs/en/hooks#userpromptsubmit) — `### UserPromptSubmit`
    - [UserPromptSubmit input](https://code.claude.com/docs/en/hooks#userpromptsubmit-input) — `#### UserPromptSubmit input`
    - [UserPromptSubmit decision control](https://code.claude.com/docs/en/hooks#userpromptsubmit-decision-control) — `#### UserPromptSubmit decision control`
    - [What a blocked prompt leaves behind](https://code.claude.com/docs/en/hooks#what-a-blocked-prompt-leaves-behind) — `#### What a blocked prompt leaves behind`
  - [UserPromptExpansion](https://code.claude.com/docs/en/hooks#userpromptexpansion) — `### UserPromptExpansion`
    - [UserPromptExpansion input](https://code.claude.com/docs/en/hooks#userpromptexpansion-input) — `#### UserPromptExpansion input`
    - [UserPromptExpansion decision control](https://code.claude.com/docs/en/hooks#userpromptexpansion-decision-control) — `#### UserPromptExpansion decision control`
  - [MessageDisplay](https://code.claude.com/docs/en/hooks#messagedisplay) — `### MessageDisplay`
    - [MessageDisplay input](https://code.claude.com/docs/en/hooks#messagedisplay-input) — `#### MessageDisplay input`
    - [MessageDisplay output](https://code.claude.com/docs/en/hooks#messagedisplay-output) — `#### MessageDisplay output`
  - [PreToolUse](https://code.claude.com/docs/en/hooks#pretooluse) — `### PreToolUse`
    - [PreToolUse input](https://code.claude.com/docs/en/hooks#pretooluse-input) — `#### PreToolUse input`
      - [Bash](https://code.claude.com/docs/en/hooks#bash) — `##### Bash`
      - [PowerShell](https://code.claude.com/docs/en/hooks#powershell) — `##### PowerShell`
      - [Write](https://code.claude.com/docs/en/hooks#write) — `##### Write`
      - [Edit](https://code.claude.com/docs/en/hooks#edit) — `##### Edit`
      - [Read](https://code.claude.com/docs/en/hooks#read) — `##### Read`
      - [Glob](https://code.claude.com/docs/en/hooks#glob) — `##### Glob`
      - [Grep](https://code.claude.com/docs/en/hooks#grep) — `##### Grep`
      - [WebFetch](https://code.claude.com/docs/en/hooks#webfetch) — `##### WebFetch`
      - [WebSearch](https://code.claude.com/docs/en/hooks#websearch) — `##### WebSearch`
      - [Agent](https://code.claude.com/docs/en/hooks#agent) — `##### Agent`
      - [AskUserQuestion](https://code.claude.com/docs/en/hooks#askuserquestion) — `##### AskUserQuestion`
      - [ExitPlanMode](https://code.claude.com/docs/en/hooks#exitplanmode) — `##### ExitPlanMode`
    - [PreToolUse decision control](https://code.claude.com/docs/en/hooks#pretooluse-decision-control) — `#### PreToolUse decision control`
    - [Tools that require user interaction](https://code.claude.com/docs/en/hooks#allow-with-updatedinput) — `<h4 id="allow-with-updatedinput">` Tools that require user interaction
    - [Defer a tool call for later](https://code.claude.com/docs/en/hooks#defer-a-tool-call-for-later) — `#### Defer a tool call for later`
  - [PermissionRequest](https://code.claude.com/docs/en/hooks#permissionrequest) — `### PermissionRequest`
    - [PermissionRequest input](https://code.claude.com/docs/en/hooks#permissionrequest-input) — `#### PermissionRequest input`
    - [PermissionRequest decision control](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control) — `#### PermissionRequest decision control`
    - [Permission update entries](https://code.claude.com/docs/en/hooks#permission-update-entries) — `#### Permission update entries`
  - [PostToolUse](https://code.claude.com/docs/en/hooks#posttooluse) — `### PostToolUse`
    - [PostToolUse input](https://code.claude.com/docs/en/hooks#posttooluse-input) — `#### PostToolUse input`
    - [PostToolUse decision control](https://code.claude.com/docs/en/hooks#posttooluse-decision-control) — `#### PostToolUse decision control`
    - [Annotate a result for the auto mode classifier](https://code.claude.com/docs/en/hooks#annotate-a-result-for-the-auto-mode-classifier) — `#### Annotate a result for the auto mode classifier`
  - [PostToolUseFailure](https://code.claude.com/docs/en/hooks#posttoolusefailure) — `### PostToolUseFailure`
    - [PostToolUseFailure input](https://code.claude.com/docs/en/hooks#posttoolusefailure-input) — `#### PostToolUseFailure input`
    - [PostToolUseFailure decision control](https://code.claude.com/docs/en/hooks#posttoolusefailure-decision-control) — `#### PostToolUseFailure decision control`
  - [PostToolBatch](https://code.claude.com/docs/en/hooks#posttoolbatch) — `### PostToolBatch`
    - [PostToolBatch input](https://code.claude.com/docs/en/hooks#posttoolbatch-input) — `#### PostToolBatch input`
    - [PostToolBatch decision control](https://code.claude.com/docs/en/hooks#posttoolbatch-decision-control) — `#### PostToolBatch decision control`
  - [PermissionDenied](https://code.claude.com/docs/en/hooks#permissiondenied) — `### PermissionDenied`
    - [PermissionDenied input](https://code.claude.com/docs/en/hooks#permissiondenied-input) — `#### PermissionDenied input`
    - [PermissionDenied decision control](https://code.claude.com/docs/en/hooks#permissiondenied-decision-control) — `#### PermissionDenied decision control`
  - [Notification](https://code.claude.com/docs/en/hooks#notification) — `### Notification`
    - [Notification input](https://code.claude.com/docs/en/hooks#notification-input) — `#### Notification input`
  - [SubagentStart](https://code.claude.com/docs/en/hooks#subagentstart) — `### SubagentStart`
    - [SubagentStart input](https://code.claude.com/docs/en/hooks#subagentstart-input) — `#### SubagentStart input`
  - [SubagentStop](https://code.claude.com/docs/en/hooks#subagentstop) — `### SubagentStop`
    - [SubagentStop input](https://code.claude.com/docs/en/hooks#subagentstop-input) — `#### SubagentStop input`
  - [TaskCreated](https://code.claude.com/docs/en/hooks#taskcreated) — `### TaskCreated`
    - [TaskCreated input](https://code.claude.com/docs/en/hooks#taskcreated-input) — `#### TaskCreated input`
    - [TaskCreated decision control](https://code.claude.com/docs/en/hooks#taskcreated-decision-control) — `#### TaskCreated decision control`
  - [TaskCompleted](https://code.claude.com/docs/en/hooks#taskcompleted) — `### TaskCompleted`
    - [TaskCompleted input](https://code.claude.com/docs/en/hooks#taskcompleted-input) — `#### TaskCompleted input`
    - [TaskCompleted decision control](https://code.claude.com/docs/en/hooks#taskcompleted-decision-control) — `#### TaskCompleted decision control`
  - [Stop](https://code.claude.com/docs/en/hooks#stop) — `### Stop`
    - [Stop input](https://code.claude.com/docs/en/hooks#stop-input) — `#### Stop input`
    - [Stop decision control](https://code.claude.com/docs/en/hooks#stop-decision-control) — `#### Stop decision control`
  - [StopFailure](https://code.claude.com/docs/en/hooks#stopfailure) — `### StopFailure`
    - [StopFailure input](https://code.claude.com/docs/en/hooks#stopfailure-input) — `#### StopFailure input`
  - [TeammateIdle](https://code.claude.com/docs/en/hooks#teammateidle) — `### TeammateIdle`
    - [TeammateIdle input](https://code.claude.com/docs/en/hooks#teammateidle-input) — `#### TeammateIdle input`
    - [TeammateIdle decision control](https://code.claude.com/docs/en/hooks#teammateidle-decision-control) — `#### TeammateIdle decision control`
  - [ConfigChange](https://code.claude.com/docs/en/hooks#configchange) — `### ConfigChange`
    - [ConfigChange input](https://code.claude.com/docs/en/hooks#configchange-input) — `#### ConfigChange input`
    - [ConfigChange decision control](https://code.claude.com/docs/en/hooks#configchange-decision-control) — `#### ConfigChange decision control`
  - [CwdChanged](https://code.claude.com/docs/en/hooks#cwdchanged) — `### CwdChanged`
    - [CwdChanged input](https://code.claude.com/docs/en/hooks#cwdchanged-input) — `#### CwdChanged input`
    - [CwdChanged output](https://code.claude.com/docs/en/hooks#cwdchanged-output) — `#### CwdChanged output`
  - [DirectoryAdded](https://code.claude.com/docs/en/hooks#directoryadded) — `### DirectoryAdded`
    - [DirectoryAdded input](https://code.claude.com/docs/en/hooks#directoryadded-input) — `#### DirectoryAdded input`
  - [FileChanged](https://code.claude.com/docs/en/hooks#filechanged) — `### FileChanged`
    - [FileChanged input](https://code.claude.com/docs/en/hooks#filechanged-input) — `#### FileChanged input`
    - [FileChanged output](https://code.claude.com/docs/en/hooks#filechanged-output) — `#### FileChanged output`
  - [WorktreeCreate](https://code.claude.com/docs/en/hooks#worktreecreate) — `### WorktreeCreate`
    - [WorktreeCreate input](https://code.claude.com/docs/en/hooks#worktreecreate-input) — `#### WorktreeCreate input`
    - [WorktreeCreate output](https://code.claude.com/docs/en/hooks#worktreecreate-output) — `#### WorktreeCreate output`
  - [WorktreeRemove](https://code.claude.com/docs/en/hooks#worktreeremove) — `### WorktreeRemove`
    - [WorktreeRemove input](https://code.claude.com/docs/en/hooks#worktreeremove-input) — `#### WorktreeRemove input`
  - [PreCompact](https://code.claude.com/docs/en/hooks#precompact) — `### PreCompact`
    - [PreCompact input](https://code.claude.com/docs/en/hooks#precompact-input) — `#### PreCompact input`
  - [PostCompact](https://code.claude.com/docs/en/hooks#postcompact) — `### PostCompact`
    - [PostCompact input](https://code.claude.com/docs/en/hooks#postcompact-input) — `#### PostCompact input`
  - [PreModelSwitch](https://code.claude.com/docs/en/hooks#premodelswitch) — `### PreModelSwitch`
    - [PreModelSwitch input](https://code.claude.com/docs/en/hooks#premodelswitch-input) — `#### PreModelSwitch input`
    - [PreModelSwitch decision control](https://code.claude.com/docs/en/hooks#premodelswitch-decision-control) — `#### PreModelSwitch decision control`
    - [PreModelSwitch timeouts and other exit codes](https://code.claude.com/docs/en/hooks#premodelswitch-timeouts-and-other-exit-codes) — `#### PreModelSwitch timeouts and other exit codes`
  - [PostModelSwitch](https://code.claude.com/docs/en/hooks#postmodelswitch) — `### PostModelSwitch`
    - [PostModelSwitch input](https://code.claude.com/docs/en/hooks#postmodelswitch-input) — `#### PostModelSwitch input`
    - [PostModelSwitch decision control](https://code.claude.com/docs/en/hooks#postmodelswitch-decision-control) — `#### PostModelSwitch decision control`
  - [SessionEnd](https://code.claude.com/docs/en/hooks#sessionend) — `### SessionEnd`
    - [SessionEnd input](https://code.claude.com/docs/en/hooks#sessionend-input) — `#### SessionEnd input`
  - [Elicitation](https://code.claude.com/docs/en/hooks#elicitation) — `### Elicitation`
    - [Elicitation input](https://code.claude.com/docs/en/hooks#elicitation-input) — `#### Elicitation input`
    - [Elicitation output](https://code.claude.com/docs/en/hooks#elicitation-output) — `#### Elicitation output`
    - [Other ways to decline an elicitation](https://code.claude.com/docs/en/hooks#other-ways-to-decline-an-elicitation) — `#### Other ways to decline an elicitation`
    - [Answer a form request from a script](https://code.claude.com/docs/en/hooks#answer-a-form-request-from-a-script) — `#### Answer a form request from a script`
  - [ElicitationResult](https://code.claude.com/docs/en/hooks#elicitationresult) — `### ElicitationResult`
    - [ElicitationResult input](https://code.claude.com/docs/en/hooks#elicitationresult-input) — `#### ElicitationResult input`
    - [ElicitationResult output](https://code.claude.com/docs/en/hooks#elicitationresult-output) — `#### ElicitationResult output`
- [Run hooks in the background](https://code.claude.com/docs/en/hooks#run-hooks-in-the-background) — `## Run hooks in the background`
  - [How async hooks execute](https://code.claude.com/docs/en/hooks#how-async-hooks-execute) — `### How async hooks execute`
  - [Limitations](https://code.claude.com/docs/en/hooks#limitations) — `### Limitations`
- [Debug hooks](https://code.claude.com/docs/en/hooks#debug-hooks) — `## Debug hooks`

## Hooks guide

Page: <https://code.claude.com/docs/en/hooks-guide> · MCP path: `/en/hooks-guide.mdx`. Worked examples, configuration and troubleshooting. The site links `#limitations-and-troubleshooting`; that heading is in the raw page but not in the docs server's copy, so on the server search for `### Limitations` there.

- [How hooks work](https://code.claude.com/docs/en/hooks-guide#how-hooks-work) — `## How hooks work`
  - [Filter hooks with matchers](https://code.claude.com/docs/en/hooks-guide#filter-hooks-with-matchers) — `### Filter hooks with matchers`
    - [Filter by tool name and arguments with the if field](https://code.claude.com/docs/en/hooks-guide#filter-by-tool-name-and-arguments-with-the-if-field) — #### Filter by tool name and arguments with the `if` field
  - [Configure hook location](https://code.claude.com/docs/en/hooks-guide#configure-hook-location) — `### Configure hook location`
  - [Hooks and permission modes](https://code.claude.com/docs/en/hooks-guide#hooks-and-permission-modes) — `### Hooks and permission modes`
  - [Hook not firing](https://code.claude.com/docs/en/hooks-guide#hook-not-firing) — `### Hook not firing`
  - [/hooks shows no hooks configured](https://code.claude.com/docs/en/hooks-guide#%2Fhooks-shows-no-hooks-configured) — ### `/hooks` shows no hooks configured
  - [Combine results from multiple hooks](https://code.claude.com/docs/en/hooks-guide#combine-results-from-multiple-hooks) — `### Combine results from multiple hooks`
  - [Read input and return output](https://code.claude.com/docs/en/hooks-guide#read-input-and-return-output) — `### Read input and return output`
    - [Hook input](https://code.claude.com/docs/en/hooks-guide#hook-input) — `#### Hook input`
    - [Hook output](https://code.claude.com/docs/en/hooks-guide#hook-output) — `#### Hook output`
    - [Structured JSON output](https://code.claude.com/docs/en/hooks-guide#structured-json-output) — `#### Structured JSON output`
- [Limitations and troubleshooting](https://code.claude.com/docs/en/hooks-guide#limitations-and-troubleshooting) — `## Limitations and troubleshooting`
  - [Limitations](https://code.claude.com/docs/en/hooks-guide#limitations) — `### Limitations`
  - [Hooks and permission modes](https://code.claude.com/docs/en/hooks-guide#hooks-and-permission-modes) — `### Hooks and permission modes`
  - [Hook not firing](https://code.claude.com/docs/en/hooks-guide#hook-not-firing) — `### Hook not firing`
  - [Hook error in output](https://code.claude.com/docs/en/hooks-guide#hook-error-in-output) — `### Hook error in output`
  - [Stop hook hits the block cap](https://code.claude.com/docs/en/hooks-guide#stop-hook-hits-the-block-cap) — `### Stop hook hits the block cap`
  - [Hook JSON has no effect](https://code.claude.com/docs/en/hooks-guide#hook-json-has-no-effect) — `### Hook JSON has no effect`
    - [Shell profile output before the JSON](https://code.claude.com/docs/en/hooks-guide#shell-profile-output-before-the-json) — `#### Shell profile output before the JSON`
    - [Fields at the wrong level](https://code.claude.com/docs/en/hooks-guide#fields-at-the-wrong-level) — `#### Fields at the wrong level`
  - [Check what a hook did](https://code.claude.com/docs/en/hooks-guide#check-what-a-hook-did) — `### Check what a hook did`

## Other official pages

| Page | MCP path | Open when |
| :-- | :-- | :-- |
| <https://code.claude.com/docs/en/changelog> | `/en/changelog.mdx` | The installed version is newer than the one in sources.md; search entries for `hook` |
| <https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md> | — | The docs changelog doesn't list the installed version yet |
| <https://code.claude.com/docs/en/permissions> | `/en/permissions.mdx` | What a hook `allow` can't override: deny and ask rules, actions no mode auto-approves |
| <https://code.claude.com/docs/en/tools-reference> | `/en/tools-reference.mdx` | A tool's input fields for `updatedInput`, or its output shape for `updatedToolOutput` |
| <https://code.claude.com/docs/en/headless> | `/en/headless.mdx` | `defer`, `initialUserMessage` and other `-p` behavior |
| <https://code.claude.com/docs/en/env-vars> | `/en/env-vars.mdx` | Variables that change hook behavior, such as `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` or `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` |
| <https://code.claude.com/docs/en/debug-your-config> | `/en/debug-your-config.mdx` | A hook never fires, or settings precedence is unclear |
| <https://code.claude.com/docs/en/plugins/components#hooks> | `/en/plugins/components.mdx` | A plugin's `hooks/hooks.json`, when plugin hooks fire, quoting and environment |
| <https://code.claude.com/docs/en/plugins/loading#hooks-when-two-enabled-plugins-share-a-name> | `/en/plugins/loading.mdx` | A plugin's hooks are left out because another plugin has the same name |
| <https://code.claude.com/docs/en/plugins/manifest-reference#environment-variables> | `/en/plugins/manifest-reference.mdx` | `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` and option variables |
| <https://code.claude.com/docs/en/settings> | `/en/settings.mdx` | Settings Warning and Settings Error for malformed hook entries |
| <https://code.claude.com/docs/en/settings-reference#allowmanagedhooksonly> | `/en/settings-reference.mdx` | `allowManagedHooksOnly`, `disableAllHooks`, HTTP hook allowlists |
| <https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder> | `/en/permissions.mdx` | Hooks that don't run in an untrusted folder |
| <https://code.claude.com/docs/en/permissions> | `/en/permissions.mdx` | Permission rule syntax used by `if` |
| <https://code.claude.com/docs/en/sub-agents#define-hooks-for-subagents> | `/en/sub-agents.mdx` | Hooks in subagent frontmatter, and SubagentStart/SubagentStop matchers |
| <https://code.claude.com/docs/en/skills> | `/en/skills.mdx` | Hooks in skill frontmatter |
| <https://code.claude.com/docs/en/tools-reference> | `/en/tools-reference.mdx` | Tool names to match, including Bash and PowerShell |
| <https://code.claude.com/docs/en/plugins/mods/overview> | `/en/plugins/mods/overview.mdx` | What a mod is next to a settings hook, what turns mods off, which mods a session loaded |
| <https://code.claude.com/docs/en/plugins/mods/events#where-settings-hooks-run-in-the-order> | `/en/plugins/mods/events.mdx` | Where settings hooks run in the mods chain; `classic.<Event>` |
| <https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods> | `/en/permissions.mdx` | A mod's approval against deny and ask rules and `PreToolUse` hooks |
| <https://code.claude.com/docs/en/plugins/mods/admin> | `/en/plugins/mods/admin.mdx` | `allowManagedModsOnly` and other organization controls on mods |
| <https://code.claude.com/docs/en/plugins/mods/create> | `/en/plugins/mods/create.mdx` | Writing a mod; Claude Code's built-in `plugin-authoring` skill covers it |

## How to use the tables below

- Each row gives the **header exactly as it appears in the source**, with its Markdown level, and the **URL with its anchor**. Cite the URL; search the source for the header.
- **Verified by** says how the anchor was confirmed on 2026-10-20 (Claude Code 2.1.305):
  - `link`: an official docs page links to that exact anchor.
  - `search`: the official docs search returns that exact URL for the section.
  - `slug`: derived from the header by the same rule as the verified anchors around it. Confirm it the first time you cite it.
- Anchors keep some punctuation: `/hooks` in a header becomes `%2F` in one page's link and stays `/` in another's search result. Copy anchors from this map; never rebuild them by hand.
- When a header in this map is no longer found in the source, the section was renamed or removed. Say so, search the page for the topic, cite what you find, and flag the map entry as stale in your report.

## Hooks reference: prompt and agent hooks

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `## Prompt-based hooks` | <https://code.claude.com/docs/en/hooks#prompt-based-hooks> | Which events take which hook types | link |
| `### How prompt-based hooks work` | <https://code.claude.com/docs/en/hooks#how-prompt-based-hooks-work> | Single model call; default model | search |
| `### Prompt hook configuration` | <https://code.claude.com/docs/en/hooks#prompt-hook-configuration> | `prompt`, `$ARGUMENTS`, `model`, `timeout`, `continueOnBlock` | link |
| `### Response schema` | <https://code.claude.com/docs/en/hooks#response-schema> | `ok`, `reason`, `impossible`; what `ok: false` does per event | link |
| `### Check multiple conditions before stopping` | <https://code.claude.com/docs/en/hooks#check-multiple-conditions-before-stopping> | Multi-condition Stop example | search |
| `## Agent-based hooks` | <https://code.claude.com/docs/en/hooks#agent-based-hooks> | Experimental status; events | link |
| `### How agent hooks work` | <https://code.claude.com/docs/en/hooks#how-agent-hooks-work> | Up to 50 turns; example tools; block handling | search |
| `### Agent hook configuration` | <https://code.claude.com/docs/en/hooks#agent-hook-configuration> | 60 s default; no `continueOnBlock`, no `impossible` | link |
| `#### Prompt and agent hook fields` | <https://code.claude.com/docs/en/hooks#prompt-and-agent-hook-fields> | `\$` escaping in `prompt` | link |
| `#### Common fields` | <https://code.claude.com/docs/en/hooks#common-fields> | `if`, `timeout` defaults, `statusMessage`, `once` | link |
| `### Hook handler fields` | <https://code.claude.com/docs/en/hooks#hook-handler-fields> | Parallel runs; 12-at-once limit; duplicate handlers | link |
| `### Hooks in skills and agents` | <https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents> | Lifetime of frontmatter hooks; `Stop` → `SubagentStop` | link |

## Hooks reference: events that accept prompt and agent hooks

Each event has an overview section and an input section. The input section lists the fields a prompt can point at through `$ARGUMENTS`.

| Event | Overview header · URL | Input header · URL | Verified by |
| :-- | :-- | :-- | :-- |
| PreToolUse | `### PreToolUse` · <https://code.claude.com/docs/en/hooks#pretooluse> | `#### PreToolUse input` · <https://code.claude.com/docs/en/hooks#pretooluse-input> | link · link |
| PostToolUse | `### PostToolUse` · <https://code.claude.com/docs/en/hooks#posttooluse> | `#### PostToolUse input` · <https://code.claude.com/docs/en/hooks#posttooluse-input> | link · slug |
| PostToolUseFailure | `### PostToolUseFailure` · <https://code.claude.com/docs/en/hooks#posttoolusefailure> | `#### PostToolUseFailure input` · <https://code.claude.com/docs/en/hooks#posttoolusefailure-input> | link · slug |
| PostToolBatch | `### PostToolBatch` · <https://code.claude.com/docs/en/hooks#posttoolbatch> | `#### PostToolBatch input` · <https://code.claude.com/docs/en/hooks#posttoolbatch-input> | link · slug |
| PermissionDenied | `### PermissionDenied` · <https://code.claude.com/docs/en/hooks#permissiondenied> | `#### PermissionDenied input` · <https://code.claude.com/docs/en/hooks#permissiondenied-input> | link · slug |
| PermissionRequest (prompt only) | `### PermissionRequest` · <https://code.claude.com/docs/en/hooks#permissionrequest> | `#### PermissionRequest input` · <https://code.claude.com/docs/en/hooks#permissionrequest-input> | link · link |
| UserPromptSubmit | `### UserPromptSubmit` · <https://code.claude.com/docs/en/hooks#userpromptsubmit> | `#### UserPromptSubmit input` · <https://code.claude.com/docs/en/hooks#userpromptsubmit-input> | link · slug |
| UserPromptExpansion | `### UserPromptExpansion` · <https://code.claude.com/docs/en/hooks#userpromptexpansion> | `#### UserPromptExpansion input` · <https://code.claude.com/docs/en/hooks#userpromptexpansion-input> | link · slug |
| Stop | `### Stop` · <https://code.claude.com/docs/en/hooks#stop> | `#### Stop input` · <https://code.claude.com/docs/en/hooks#stop-input> | link · link |
| SubagentStop | `### SubagentStop` · <https://code.claude.com/docs/en/hooks#subagentstop> | `#### SubagentStop input` · <https://code.claude.com/docs/en/hooks#subagentstop-input> | link · slug |
| TaskCreated | `### TaskCreated` · <https://code.claude.com/docs/en/hooks#taskcreated> | `#### TaskCreated input` · <https://code.claude.com/docs/en/hooks#taskcreated-input> | link · slug |
| TaskCompleted | `### TaskCompleted` · <https://code.claude.com/docs/en/hooks#taskcompleted> | `#### TaskCompleted input` · <https://code.claude.com/docs/en/hooks#taskcompleted-input> | link · slug |
| TeammateIdle | `### TeammateIdle` · <https://code.claude.com/docs/en/hooks#teammateidle> | `#### TeammateIdle input` · <https://code.claude.com/docs/en/hooks#teammateidle-input> | link · slug |
| Fields every event sends | `### Common input fields` · <https://code.claude.com/docs/en/hooks#common-input-fields> | — | link |
| All events, one per section | `## Hook events` · <https://code.claude.com/docs/en/hooks#hook-events> | — | link |

## Hooks reference: background hooks

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `## Run hooks in the background` | <https://code.claude.com/docs/en/hooks#run-hooks-in-the-background> | Async hooks cannot block or decide | link |
| `### Configure an async hook` | <https://code.claude.com/docs/en/hooks#configure-an-async-hook> | `async` is command-only; `timeout` not enforced; `-p` teardown | search |
| `### How async hooks execute` | <https://code.claude.com/docs/en/hooks#how-async-hooks-execute> | Delivered fields; stdout rules; dropped fields; verbose notices | link |
| `### Run tests after file changes` | <https://code.claude.com/docs/en/hooks#run-tests-after-file-changes> | Worked example | search |
| `### Limitations` | <https://code.claude.com/docs/en/hooks#limitations> | Next-turn delivery; `asyncRewake` exit 2 wakes Claude | search |
| `#### Command hook fields` | <https://code.claude.com/docs/en/hooks#command-hook-fields> | `async`, `asyncRewake`, `shell` field definitions | link |
| `#### Hooks that start a background process` | <https://code.claude.com/docs/en/hooks#hooks-that-start-a-background-process> | A synchronous hook that leaves a process running | link |

## Hooks reference: security, PowerShell, debugging

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `## Security considerations` | <https://code.claude.com/docs/en/hooks#security-considerations> | Section entry point | link |
| `### Disclaimer` | <https://code.claude.com/docs/en/hooks#disclaimer> | Full-user-permission warning | search |
| `### Workspace trust` | <https://code.claude.com/docs/en/hooks#workspace-trust> | Interactive vs `-p`/SDK trust; mitigations | link |
| `### Security best practices` | <https://code.claude.com/docs/en/hooks#security-best-practices> | Validate, quote, traversal, absolute paths, sensitive files | search |
| `## Windows PowerShell tool` | <https://code.claude.com/docs/en/hooks#windows-powershell-tool> | `shell: "powershell"`; placeholder rewriting; bare `$CLAUDE_PROJECT_DIR` | link |
| `## Debug hooks` | <https://code.claude.com/docs/en/hooks#debug-hooks> | Debug log paths; `Hooks:` lines; verbose level | link |

## Hooks reference: supporting sections

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `##### Exec form and shell form` | <https://code.claude.com/docs/en/hooks#exec-form-and-shell-form> | `args` vs shell; quoting placeholders | link |
| `### Reference scripts by path` | <https://code.claude.com/docs/en/hooks#reference-scripts-by-path> | `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`; worktrees and `cwd` | link |
| ``### The `/hooks` menu`` | <https://code.claude.com/docs/en/hooks#the-%2Fhooks-menu> | Read-only list with sources | link |
| `### Disable or remove hooks` | <https://code.claude.com/docs/en/hooks#disable-or-remove-hooks> | `disableAllHooks` precedence; `--settings` override | link |
| `<h4 id="bash-if-matching">` (rendered "How `if` patterns match Bash commands") | <https://code.claude.com/docs/en/hooks#bash-if-matching> | `if` is best-effort | link |

## Hooks guide: prompt, agent and troubleshooting sections

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `## Prompt-based hooks` | <https://code.claude.com/docs/en/hooks-guide#prompt-based-hooks> | Guide view of prompt hooks | link |
| `## Agent-based hooks` | <https://code.claude.com/docs/en/hooks-guide#agent-based-hooks> | When to pick agent over prompt | link |
| `## Limitations and troubleshooting` | <https://code.claude.com/docs/en/hooks-guide#limitations-and-troubleshooting> | Entry point for symptoms | link (header text not confirmed) |
| `### Limitations` | <https://code.claude.com/docs/en/hooks-guide#limitations> | Timeouts by type; Stop vs StopFailure | link |
| `### Hooks and permission modes` | <https://code.claude.com/docs/en/hooks-guide#hooks-and-permission-modes> | A hook's deny holds in every mode | search |
| `### Hook not firing` | <https://code.claude.com/docs/en/hooks-guide#hook-not-firing> | First checks | search |
| `### Hook error in output` | <https://code.claude.com/docs/en/hooks-guide#hook-error-in-output> | Piping sample JSON; parse vs validation errors | search |
| ``### `/hooks` shows no hooks configured`` | <https://code.claude.com/docs/en/hooks-guide#/hooks-shows-no-hooks-configured> | Reload, JSON validity, `allowManagedHooksOnly` | search |
| `### Stop hook hits the block cap` | <https://code.claude.com/docs/en/hooks-guide#stop-hook-hits-the-block-cap> | 8-block cap; `stop_hook_active`; `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` | link |
| `### Hook JSON has no effect` | <https://code.claude.com/docs/en/hooks-guide#hook-json-has-no-effect> | Output not starting with `{`; misplaced fields | link |
| `#### Shell profile output before the JSON` | <https://code.claude.com/docs/en/hooks-guide#shell-profile-output-before-the-json> | Profile `echo` breaking JSON | link |
| `#### Fields at the wrong level` | <https://code.claude.com/docs/en/hooks-guide#fields-at-the-wrong-level> | `unrecognized keys` log line | link |
| `### Check what a hook did` | <https://code.claude.com/docs/en/hooks-guide#check-what-a-hook-did> | Transcript view; `/debug` mid-session | link |

## Other pages

| Header in source | URL | Settles | Verified by |
| :-- | :-- | :-- | :-- |
| `## Project allow rules and workspace trust` | <https://code.claude.com/docs/en/permissions#project-allow-rules-and-workspace-trust> | What the trust dialog covers | link |
| `### What runs before you trust a folder` | <https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder> | Per-content trust table; `-p` mitigations; `hasTrustDialogAccepted` | link |
| `### Precedence among rules, hooks, and mods` | <https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods> | Hook allow vs deny/ask rules | link |
| `#### Hooks in subagent frontmatter` | <https://code.claude.com/docs/en/sub-agents#hooks-in-subagent-frontmatter> | Project subagent hooks need folder trust; never under `-p` | link |
| `<h3 id="supported-frontmatter-fields">` (rendered "Frontmatter reference") | <https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields> | Plugin subagents ignore `hooks` | link |
| `#### Preload skills into subagents` | <https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents> | `skills` frontmatter | link |
| `### Start faster with bare mode` | <https://code.claude.com/docs/en/headless#start-faster-with-bare-mode> | What `--bare` skips | link |
| `## Check hooks` | <https://code.claude.com/docs/en/debug-your-config#check-hooks> | `/hooks` first, then the debug log | search |
| `<h3 id="hook-needs-quotes-around-a-path-with-a-space">` (rendered "Hook needs quotes around a path with a space") | <https://code.claude.com/docs/en/errors#hook-needs-quotes-around-a-path-with-a-space> | `asyncRewake` shell-form path with a space | search |

## Out of scope: where to point

Link these in a **Not covered** line; do not assess them.

| Topic | Header in source | URL |
| :-- | :-- | :-- |
| Permission rules | `## Permission rule syntax` | <https://code.claude.com/docs/en/permissions#permission-rule-syntax> |
| Writing a mod | `## Ask Claude for a mod` | <https://code.claude.com/docs/en/plugins/mods/create#ask-claude-for-a-mod> |

