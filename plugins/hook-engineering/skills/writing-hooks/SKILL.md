---
name: writing-hooks
description: Use for every request or task that creates, rewrites or wires a hook or hook script for Claude Code or Cowork, including the hooks entry in settings.json, even when the user never says hook. Load it before or with update-config when that settings change is a hook. That includes setting something up to run automatically, from now on, in every session or every time an event happens (when Claude edits a file, after it reads files, before a command runs, when a session starts or ends), to block, allow, log or check commands, tool calls, prompts or file changes, to make Claude always or never do something with a guarantee instead of a memory or an instruction, and to add hooks to a plugin, a skill, a subagent or user, project, local or managed settings. Writes hooks of every type (command, HTTP, MCP tool, prompt, agent) from the current docs, picks the event and location, and tests them with real inputs. Not for auditing or debugging an existing hook (hook-development), Git hooks, React hooks or webhooks.
---

# Write a Claude Code hook

This skill owns the order of work. For a specific part of it, use the session's skill or tool built for that part together with this skill, and continue with this skill's own steps when there is none:

- the hook's tests and evals: `plugin-engineering:test-and-evals`; plugin debugging: `plugin-engineering:troubleshoot-and-debug`;
- a mod's hooks module (JavaScript that Claude Code runs in its own process, listed under `modules` in `hooks/hooks.json`): the built-in `plugin-authoring` skill.

## Workflow

Copy this checklist into your task list. The work is not finished while any item is unchecked; tick each one only with its evidence.

- [ ] 1. Understand the request and the environment, and identify the kind of hook.
- [ ] 2. Clarify with the user, through `AskUserQuestion`, whatever is still open.
- [ ] 3. Read the official docs the hook depends on, and check the user's version.
- [ ] 4. Decide the event, the handler type, the mechanism and the location.
- [ ] 5. Choose the script conventions.
- [ ] 6. Build the script and its configuration.
- [ ] 7. Verify, correct in one pass, and report.

## Gotchas

- Pick the event from when and how often it fires, not from its name. A name that sounds right often fires at the wrong moment.
- Read whole sections, never matching lines. The rule that changes the design usually sits a few lines away from the match.
- Use only what the docs and the changelog state, plus the facts this skill marks as observed, which you tell the user are undocumented. Mark anything you could not verify instead of filling it in.
- When the changelog disagrees with a page, the changelog wins. Pages lag the releases.
- The docs' own example scripts start with `#!/bin/bash` and no strict mode. Take the shebang and opening lines from [references/script-conventions.md](references/script-conventions.md), never from an example.
- `Edit|Write` sees only the `Edit` and `Write` tools: files changed through `Bash`, `PowerShell` or `NotebookEdit` don't fire it. `FileChanged` fires for any change on disk, but it can't block, and its `systemMessage` and stderr reach only the user, never Claude. To tell Claude about a change, set `asyncRewake` on the handler and exit 2: its stderr reaches Claude as a system reminder.
- A command hook runs in exec form when `args` is set (even `"args": []`) and in shell form when it is not. Run a script (`.sh`, `.py` and the like) in shell form with its whole path in double quotes, as the templates in `assets/` write it: it runs on macOS, Linux and Windows through Git Bash. Use exec form only when `command` is a real executable, such as `"command": "node"` with the script in `args`: on Windows exec form can't start a `.sh`, `.py`, `.cmd` or `.bat` path, and `"command": "bash"` fails on a default Git for Windows install, which puts only its `cmd` folder on the PATH (from the installer's code, not the docs). The docs prefer exec form for path placeholders because it needs no quoting; the double quotes do that job in shell form.
- On Windows, `tool_input.file_path` arrives with backslashes even when the hook runs under Git Bash, so a pattern written with `/` never matches and a guard lets the call through. Normalize it before comparing (`"${FILE_PATH//\\//}"` in Bash, `.replace("\\", "/")` in Python, `.replaceAll("\\", "/")` in Node), then match a segment such as `/src/` instead of anchoring with `^`. Substituted paths such as `CLAUDE_PLUGIN_ROOT` arrive with `/` under Git Bash but keep `\` in exec form and under PowerShell.
- Not every event takes every handler type: `hooks#prompt-based-hooks` lists which events take `prompt` and `agent`, and `SessionStart` and `Setup` take only `command` and `mcp_tool`. Check the event takes the type before you write the handler.
- When several hooks match one event, they all run in parallel to the end: one hook's `deny` doesn't stop a sibling's side effects. For `PreToolUse` the most restrictive decision wins (`deny`, `defer`, `ask`, `allow`), and two hooks that both return `updatedInput` for the same tool are not merged.
- `onFailure` has no effect on `Stop`, `SubagentStop`, `TaskCompleted` and `TeammateIdle` hooks, or on `async` and `asyncRewake` hooks: a gate there must fail closed by itself.
- A hook's `allow` never overrides a deny rule from settings, and its `deny` holds in every permission mode, `bypassPermissions` included. To enforce a hard allow or deny, prefer a permission rule; the `if` filter is best effort.
- A `Stop` hook that blocks must read `stop_hook_active` and exit 0 when it is `true`: Claude Code overrides a `Stop` hook after it blocks eight times in a row.
- JSON output takes effect only when stdout starts with `{`. A shell profile that prints on start (Git Bash, or `BASH_ENV` pointing at `~/.bashrc`) silently turns the JSON into plain text, and a field placed at the wrong level, such as `permissionDecision` outside `hookSpecificOutput`, is ignored without an error. Build the JSON with an encoder (`jq`, Python `json`, `JSON.stringify`), never by concatenating strings.

## When a step fails

The goal of every step is the result it names (the full section, the version check, a verified script), not the command that was planned. When a command, a tool or a source fails, reach the same goal another way: another route this skill names, another command the tool supports, the other form of the same page (`.mdx` in the MCP, `.md` on the site). Repeat a failing command at most once, and only after a timeout. Report the route you used and why the first one failed; report a gap only after every route has failed, with what it leaves unverified.

## Step 1: Understand (what the hook must achieve, and where)

1. State the goal, what must happen when the hook succeeds and when it fails, and whether it must guarantee an outcome (a gate that blocks) or only act quickly (advise, log, add context).
2. Read the environment before asking anything. Each signal points at a location:
   - `.claude-plugin/plugin.json` at the root: a plugin;
   - an `agents/` folder or a subagent named in the request: a subagent hook;
   - `.mcp.json` or `mcpServers`, or MCP tools named in the request: a hook on MCP tools;
   - a skill named in the request: skill frontmatter;
   - "only for me", "don't commit it": local settings;
   - a project with `.claude/` and nothing above: project settings;
   - "every project", "on this machine": user settings;
   - "for the whole organization", "for every developer": managed settings;
   - `CLAUDE_CODE_REMOTE` set to `true`: a cloud session, which never reads the user's own `~/.claude/settings.json`.
3. List the hooks already registered that the new one could meet: the settings files in scope, the plugin's `hooks/hooks.json` and the enabled plugins. Design the new hook to coexist with them.
4. Note the platforms the hook must run on: a README, CI matrix or the request may name Windows.
5. Note the Claude Code version the hook will run on. A version the user states or the project pins (README, CI, devcontainer, setup scripts) wins over the local `claude --version`, and a hook shared by a team runs on the oldest version among them. Only when nothing states it, use the local one.

## Step 2: Clarify (what is still open)

1. Judge whether you can build without guessing: the goal, the kind of hook, the systems it touches and what must happen on failure are all clear from the request and step 1. If they are, the request is complete: go to step 3 without asking anything.
2. For an incomplete request, call the `AskUserQuestion` tool before you write any file. Ask one to four questions, as many as you need to be certain what the user wants.
3. Ask about the user's goal and context, and keep the technical choices (events, matchers, handler types, exit codes, forms) out of the questions: those are your job.
   - Not "Should this be a `PreToolUse` or a `PermissionRequest` hook?"
   - But "When Claude tries to run one of these commands, should it be stopped every time, or should you be asked?"
4. When `AskUserQuestion` is not available, as in a subagent or a non-interactive run, ask the same questions in your reply and stop there.
5. Build nothing until the answers remove the ambiguity; ask again if they don't.

## Step 3: Source (what the docs allow)

1. Read [references/reading-docs.md](references/reading-docs.md): it says how to find, download and read each section below and how to search the changelog.
2. Read these sections, in this order, and cite each one in the report. Each name below is a page and anchor under `https://code.claude.com/docs/en/`; page `hooks` unless another is named.
   1. Events, as a panorama before any choice:
      - `hooks-guide#how-hooks-work` gives one line per current event on when it fires; `hooks#hook-events` lists the same events as its `###` headings; `hooks#prompt-based-hooks` says which handler types each event takes.
      - `hooks-guide#what-you-can-automate` holds the documented recipes for common goals: when one matches, use it as the starting design and adapt it to the script conventions.
      - From these, list every event that could serve the goal, then read each candidate's `### <EventName>` section in full.
   2. Lifecycle: `hooks#hook-lifecycle`, including `hooks#how-a-hook-resolves`.
   3. Matcher: `hooks#matcher-patterns`, including `hooks#match-mcp-tools` for MCP actions.
   4. Input: `hooks#common-input-fields`, plus the input in the event's section.
   5. Output: `hooks#exit-code-output` and `hooks#exit-code-2-behavior-per-event`; `hooks#json-output` and `hooks#decision-control`; `hooks#http-response-handling` for an HTTP hook; for a hook that must guarantee an outcome, `hooks#block-the-action-when-a-hook-fails` and `hooks#timeouts`.
   6. Handler fields and how the handler runs: `hooks#hook-handler-fields` with `hooks#common-fields` and the chosen type's fields (`hooks#command-hook-fields` with `hooks#exec-form-and-shell-form`, `hooks#http-hook-fields`, `hooks#mcp-tool-hook-fields` or `hooks#prompt-and-agent-hook-fields`). When a model's judgment or background work may fit better: `hooks#agent-based-hooks` and `hooks#run-hooks-in-the-background`.
   7. Where the hook lives: `hooks#configuration`, `hooks#hook-locations`, `hooks#reference-scripts-by-path` and `hooks#hooks-in-skills-and-agents`; for a plugin, `plugins/components#hooks`; for a subagent, `sub-agents#define-hooks-for-subagents`.
   8. Only when step 1 noted Windows: `hooks#failed-hooks-on-windows-without-git-bash`, `hooks#powershell-started-no-program` and `hooks#windows-powershell-tool`.
   9. Only when the hook would observe or change Claude's own interface or in-process behavior: `plugins/mods/overview#compare-mods-settings-hooks-skills-and-mcp-servers` and `plugins/mods/overview#what-a-hook-can-do-with-an-event`.
   10. For a project, plugin or managed hook: `hooks#workspace-trust` and `hooks#security-best-practices`.
   11. How to confirm it fired: `hooks-guide#limitations-and-troubleshooting` and `hooks#debug-hooks`.
3. Check that the version from step 1 has every event and field the design relies on: a hook that relies on one the version lacks doesn't do what it promises there, and a gate fails open.
   1. Check only what the design uses: first the minimum the docs write beside a field or event, such as "Requires Claude Code v<version> or later"; then the changelog, for each event and field the docs give no minimum for.
   2. When the version lacks one, pick a mechanism that version has, or tell the user what an upgrade would add, and say which.

## Step 4: Decide (the optimal hook, not the first that works)

1. Compare the candidate events read in step 3 and every other mechanism that could do the job: each handler type (`command`, `http`, `mcp_tool`, `prompt`, `agent`), a mod, a permission rule.
2. Weigh them by when and how often each fires, what each can see and decide, and what each costs to run and maintain.
3. Pick the optimal one. A way that works can still carry more complexity than a newer event or field that does the job directly. Note the alternatives set aside, and why, for the report.
4. For a command hook, pick exec form or shell form as the gotcha on the two forms says.
5. Pick the location from step 1 and read its reference before writing its configuration; copy its template in step 6. Each reference gives the role to take, what the location changes (scope, lifetime, registration, trust, placeholders), its gotchas, its rules and its template:
   - [references/location-plugin.md](references/location-plugin.md): a plugin's `hooks/hooks.json` or the `hooks` key of `plugin.json`, for Claude Code and Cowork. Template: [assets/plugin-hooks.json](assets/plugin-hooks.json).
   - [references/location-user-settings.md](references/location-user-settings.md): `~/.claude/settings.json`, every project on one machine. Template: [assets/user-settings.json](assets/user-settings.json).
   - [references/location-project-settings.md](references/location-project-settings.md): `.claude/settings.json`, committed and shared with everyone who clones the repository. Template: [assets/project-settings.json](assets/project-settings.json).
   - [references/location-local-settings.md](references/location-local-settings.md): `.claude/settings.local.json`, one person in one project. Template: [assets/project-settings.json](assets/project-settings.json).
   - [references/location-managed-settings.md](references/location-managed-settings.md): managed policy settings, deployed by an organization's administrator. Template: [assets/project-settings.json](assets/project-settings.json).
   - [references/location-skill-frontmatter.md](references/location-skill-frontmatter.md): `hooks` in a skill's frontmatter, registered when the skill is invoked. Template: [assets/skill-frontmatter.md](assets/skill-frontmatter.md).
   - [references/location-subagent-frontmatter.md](references/location-subagent-frontmatter.md): `hooks` in a subagent's frontmatter, active only while it runs. Template: [assets/subagent-frontmatter.md](assets/subagent-frontmatter.md).
   - [references/location-subagent-events.md](references/location-subagent-events.md): `SubagentStart` and `SubagentStop` in settings or `hooks/hooks.json`, the only way to hook a plugin's own agents. Template: [assets/subagent-events-settings.json](assets/subagent-events-settings.json). Read the reference of the file those hooks go in too.

## Step 5: Choose the script conventions

1. Skip this step when the chosen handler runs no script (`http`, `mcp_tool`, `prompt`, `agent`).
2. Read [references/script-conventions.md](references/script-conventions.md), and pick the interpreter and opening lines for the chosen event and the hook's role (a gate, or a hook that only advises).

## Step 6: Build (how it is written)

1. If the handler runs a script, write it from what step 3 read, starting with the opening lines from step 5, and set its permissions as the script conventions say.
2. Merge the template's event entry into the location's existing file: add to its `hooks` object, and never replace the file or another event's entries. Replace every `<placeholder>`, keep each handler's fields to what step 3 confirmed, leave `matcher` out on events that don't support one, and set `timeout` only when the script's real run time or the event needs a value other than the docs' default.
3. For a handler that is not a command, put one of these objects in the template's inner `hooks` array instead of the command handler:
   - [assets/handler-http.json](assets/handler-http.json): an HTTP hook. Every header variable must be listed in `allowedEnvVars`, and `allowedHttpHookUrls` in any settings level can block the URL.
   - [assets/handler-mcp-tool.json](assets/handler-mcp-tool.json): an MCP tool hook. A plugin's own server is named `plugin:<plugin>:<server>`. `SessionStart` at launch and `Setup` skip it, because MCP servers are not connected yet.
   - [assets/handler-prompt.json](assets/handler-prompt.json): a prompt hook. Its `\$ARGUMENTS` placeholder is replaced with the hook input JSON.
   - [assets/handler-agent.json](assets/handler-agent.json): an agent hook, which the docs mark experimental.
   - [assets/node-exec-handler.json](assets/node-exec-handler.json): a command handler that runs a Node script in exec form, which works on every system because `node` is a real executable.

## Step 7: Verify and correct (one pass)

1. Write the expected outcome of each input before running anything:
   - one input that must trigger the hook's action (block, deny, context);
   - one input that must stay silent;
   - for a gate, one input it cannot read, which must block.
2. Check the configuration file: `jq -e .` for JSON, and `claude plugin validate <plugin-dir>` for a plugin, which warns about an unquoted placeholder in shell form.
3. Build each input from the event's documented fields and run the handler's exact `command` the way the hook will, from the directory the session starts in, with the placeholders it uses set:

   ```bash
   printf '%s' '<input-json>' | CLAUDE_PROJECT_DIR='<project-root>' CLAUDE_PLUGIN_ROOT='<plugin-dir>' sh -c '<command string>'; echo "exit=$?"
   ```

   For exec form, run `command` with its `args` directly. Check that JSON output parses (`jq -e .`) and that each field sits where `hooks#json-output` puts it.
4. Compare stdout, stderr and the exit code with the expected outcome. Collect every mismatch, in the script and in the configuration, find each cause in the docs, apply all fixes at once, check what else they touch, then rerun only the affected inputs.
5. Confirm in a live session that the hook fires, as `hooks#debug-hooks` describes: `/hooks` lists it under its event, and `claude --debug-file <path>` records a `Hooks:` line for its run. A skill's hooks appear in `/hooks` only after the skill is invoked. Where `/hooks` isn't available, as in a subagent or a `-p` run, use `claude -p --debug-file <path>` with a prompt that triggers the event, and remember that a `-p` run treats the folder as trusted except for a project subagent's frontmatter hooks.
6. Delete any folder of downloaded docs you created inside the working directory.
7. Report, with explicit evidence for each claim: the raw output, the file and line, or the docs section as a link with its anchor. Verify everything within reach instead of assuming it.
   - the kind of hook and the evidence for it;
   - the event, the handler type and why they were chosen, and the alternatives set aside;
   - the location and template used, and the hooks it coexists with;
   - the full content of every file written, and of every file whose write was blocked, so the user can apply it;
   - the docs sections read, and the changelog range checked against the user's version;
   - each input with its expected and actual outcome;
   - what changed in the correction pass and why;
   - what could not be verified, and every observed, undocumented fact relied on.
