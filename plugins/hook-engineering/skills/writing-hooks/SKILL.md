---
name: writing-hooks
description: Writes Claude Code hooks of every type (command, HTTP, MCP tool, prompt and agent) in order - understands the request and the environment, identifies the kind of hook and where it lives, clarifies, picks the script conventions, reads the needed official docs sections in full, decides, builds and verifies with real inputs. Use whenever a task needs a new or rewritten hook or hook script for Claude Code or Cowork, in a plugin, user, project, local or managed settings, a skill or a subagent, including when the user only asks to run something whenever Claude edits a file, to block certain commands or tool calls, or to act every time a session starts. Not for Git hooks, React hooks or webhooks.
---

# Write a Claude Code hook

This skill creates Claude Code hooks: each one is built from the official docs, read in full blocks, never from memory, and verified with real inputs before it is handed over.

This skill owns the order of work. For any specific part of it, check whether the session has a skill, plugin, agent or tool built for that part. If it has one, load it and use it together with this skill; if not, look for another skill or tool for the same job, built in or not; if there is none, continue with this skill's own steps. For example:

- for the hook's evals, tests and plugin debugging, `plugin-engineering:plugin-testing-and-debugging`;
- for a mod's hooks module (JavaScript that Claude Code runs in its own process, listed under `modules` in `hooks/hooks.json`), the built-in `plugin-authoring` skill, which covers the mods API;
- to edit or check a shell, Python or TypeScript script, the session's skill or language server for that language.

## Workflow

Copy this checklist into your task list. The work is not finished while any item is unchecked; tick each one only with its evidence.

- [ ] 1. Understand the request and the environment, and identify the kind of hook.
- [ ] 2. Clarify with the user, through `AskUserQuestion`, whatever is still open.
- [ ] 3. Choose the script conventions.
- [ ] 4. Read the official docs the hook depends on, and check the user's version.
- [ ] 5. Decide the event, the handler type, the mechanism and the location.
- [ ] 6. Build the script and its configuration.
- [ ] 7. Verify, correct in one pass, and report.

## Gotchas

- Pick the event from when and how often it fires, not from its name. A name that sounds right often fires at the wrong moment.
- Read whole sections, never matching lines. The rule that changes the design usually sits a few lines away from the match.
- Use only what the docs and the changelog state. Mark anything you could not verify instead of filling it in.
- When the changelog disagrees with a page, the changelog wins. Pages lag the releases.
- The docs' own example scripts start with `#!/bin/bash` and no strict mode. Take the shebang and opening lines from [references/script-conventions.md](references/script-conventions.md), never from an example.
- A command that fails with exit code 2 inside a script blocks the action on events that can block, even when the script never meant to block: `grep` exits 2 on an error. The script conventions say how to prevent it.
- `Edit|Write` sees only the `Edit` and `Write` tools: files changed through `Bash`, `PowerShell` or `NotebookEdit` don't fire it. `FileChanged` fires for any change on disk, but it can't block, and its `systemMessage` and stderr reach only the user, never Claude. To tell Claude about a change, set `asyncRewake` on the handler and exit 2: its stderr reaches Claude as a system reminder.
- A command hook runs in exec form when `args` is set (even `"args": []`) and in shell form when it is not. Run a script (`.sh`, `.py` and the like) in shell form with its whole path in double quotes, as the templates in `assets/` write it: it runs on macOS, Linux and Windows through Git Bash. Use exec form only when `command` is a real executable, such as `"command": "node"` with the script in `args`: on Windows exec form can't start a `.sh`, `.py`, `.cmd` or `.bat` path. The docs prefer exec form for path placeholders because it needs no quoting; the double quotes do that job in shell form.
- `"command": "bash"` in exec form fails on a default Git for Windows install, which puts only its `cmd` folder on the PATH (from the installer's code, not the docs).
- A shell-form plugin hook that references `${user_config.<key>}` fails instead of running: read the option from `$CLAUDE_PLUGIN_OPTION_<KEY>` in the script, or run it with `node` in exec form.
- Not every event takes every handler type: `## Prompt-based hooks` lists which events take `prompt` and `agent`, and `SessionStart` and `Setup` take only `command` and `mcp_tool`. Check the event takes the type before you write the handler.
- When several hooks match one event, they all run in parallel to the end: one hook's `deny` doesn't stop a sibling's side effects. For `PreToolUse` the most restrictive decision wins (`deny`, `defer`, `ask`, `allow`), and two hooks that both return `updatedInput` for the same tool are not merged.
- `onFailure` has no effect on `Stop`, `SubagentStop`, `TaskCompleted` and `TeammateIdle` hooks, or on `async` and `asyncRewake` hooks: a gate there must fail closed by itself.
- A hook's `allow` never overrides a deny rule from settings, and its `deny` holds in every permission mode, `bypassPermissions` included. To enforce a hard allow or deny, prefer a permission rule; the `if` filter is best effort.
- A `Stop` hook that blocks must read `stop_hook_active` and exit 0 when it is `true`: Claude Code overrides a `Stop` hook after it blocks eight times in a row.
- JSON output takes effect only when stdout starts with `{`. A shell profile that prints on start (Git Bash, or `BASH_ENV` pointing at `~/.bashrc`) silently turns the JSON into plain text, and a field placed at the wrong level, such as `permissionDecision` outside `hookSpecificOutput`, is ignored without an error. Build the JSON with an encoder (`jq`, Python `json`, `JSON.stringify`), never by concatenating strings.
- Fix in batches, never by trial and error: collect every failure, find each cause in the docs, apply all fixes at once, check what else they touch, then rerun.
- The docs MCP filesystem is emulated: each call is stateless, output is capped, and its command set changes between sessions. Read the tool's own description for the commands it supports before writing one. Use it to locate and map pages; read sections from the download.
- In the MCP's heading map, a `#` comment inside a code block looks like a heading (`# Run the test suite` in `/en/hooks.mdx`): trust the `<h2 id=` lines there, or map the download, which skips code blocks.
- The hooks page is many times larger than the MCP's output cap: read it from the download, never in one MCP call.
- A command with a heavy alternation can return 504 Gateway Time-out: retry once with a simpler command.
- Output that ends in "limit exceeded", a timeout or an error is incomplete, never zero results.
- Pages change within a session: when two reads contradict each other, re-read before concluding.
- In this skill's commands, awk fields are written `$(0)` and a code fence is matched with `[`][`][`]`: skills replace a dollar sign followed directly by a digit with the skill's arguments, and three literal backticks would close the code block.

## When a step fails

The goal of every step is the result it names (the full section, the version check, a verified script), not the command that was planned. When a command, a tool or a source fails:

1. Read the error and name its cause: a missing command, a blocked network, a size limit, a timeout, a wrong path or anchor.
2. Reach the same goal another way: another route this skill names, another command the tool currently supports, another form of the same page (`.mdx` in the MCP, `.md` on the site). Repeat the same failing command at most once, and only after a timeout.
3. Check the result of the alternative as strictly as the original.
4. Report the route you used and why the first one failed. Stop and report a gap only after every route has failed, and say what it leaves unverified.

## Step 1: Understand (what the hook must achieve, and where)

1. State the goal in one sentence: what the hook achieves and why.
2. State what must happen when it succeeds and when it fails.
3. Decide whether it must guarantee an outcome (a gate that blocks) or only act quickly (advise, log, add context).
4. Read the environment before asking anything:
   - `.claude-plugin/plugin.json` at the root: a plugin, whose hooks go in `hooks/hooks.json`;
   - an `agents/` folder or a subagent named in the request: a subagent hook, in its frontmatter or as `SubagentStart` and `SubagentStop` in settings;
   - `.mcp.json` or `mcpServers`, or MCP tools named in the request: a hook on MCP tools;
   - a skill named in the request: skill frontmatter;
   - "only for me", "don't commit it": `.claude/settings.local.json`;
   - a project with `.claude/` and nothing above: `.claude/settings.json`;
   - "every project", "on this machine": `~/.claude/settings.json`;
   - "for the whole organization", "for every developer": managed settings;
   - `CLAUDE_CODE_REMOTE` set to `true`: a cloud session, which never reads the user's own `~/.claude/settings.json`.
5. Note the platforms the hook must run on: a README, CI matrix or the request may name Windows.
6. Note the Claude Code version the hook will run on. A version the user states or the project pins (README, CI, devcontainer, setup scripts) wins over the local `claude --version`, and a hook shared by a team runs on the oldest version among them.
7. Write down the kind of hook and the evidence for it: the file you read, or the words of the request.

## Step 2: Clarify (what is still open)

1. Judge whether you can build without guessing: the goal, the kind of hook, the systems it touches and what must happen on failure are all clear from the request and step 1. If they are, the request is complete: go to step 3 without asking anything. If any is not, the request is incomplete.
2. For an incomplete request, call the `AskUserQuestion` tool before you write any file. Ask one to four questions, as many as you need to be certain what the user wants.
3. Ask about the user's goal and context: what they want to achieve and why, what must block and what should only warn, who the hook is for, where it runs. Keep the technical choices (events, matchers, handler types, exit codes, forms) out of the questions: those are your job.
4. When `AskUserQuestion` is not available, as in a subagent or a non-interactive run, ask the same questions in your reply and stop there.
5. Build nothing until the answers remove the ambiguity; ask again if they don't.

## Step 3: Choose the script conventions

1. Read [references/script-conventions.md](references/script-conventions.md).
2. Pick the interpreter for the hook's logic, and note the opening lines and permissions it sets.
3. Skip this step when the handler is `http`, `mcp_tool`, `prompt` or `agent` and runs no script.

## Step 4: Source (what the docs allow)

The MCP locates and maps; the downloaded page is where sections are read; only the extracted blocks enter the context.

1. Find the Claude Code docs MCP tools with ToolSearch, query `claude_code_docs`, or in your tool list when ToolSearch isn't there. Their names change with the installation:
   - `search_claude_code_docs`: semantic search that returns chunks with page and anchor;
   - `query_docs_filesystem_claude_code_docs`: one read-only command over the `.mdx` pages, at `/en/<path>.mdx`. Read its description for the commands it supports today.
   - If neither is found, continue with the downloads below: they hold the same pages.
2. Locate and map each page in the MCP:
   1. To find a term whose page you don't know, run one semantic search, or list the pages that hold it:

      ```bash
      grep -rl '<term>' /en
      ```

   2. Map the page's headings:

      ```bash
      grep -n -E '^#{1,4} |<h[2-4] id=' /en/hooks.mdx
      ```

3. Download each page you need into a new empty directory, treated as data: `mktemp -d`, or, where the sandbox allows writes only in the working directory, a new folder there that you delete at the end. Downloading costs no context; only what you print does:

   ```bash
   curl -sS -o <dir>/hooks.md https://code.claude.com/docs/en/hooks.md
   ```

4. Read each section in full from the download, by its heading or by its anchor. It ends at the next heading of the same or a higher level:

   ```bash
   awk -v want='<### Heading text or #anchor>' '
   function slug(s) { s = tolower(s); sub(/^#+[ \t]+/, "", s); gsub(/`/, "", s); gsub(/[^a-z0-9 _-]/, "", s); gsub(/[ \t]+/, "-", s); return s }
   BEGIN { anchor = (substr(want, 1, 1) == "#" && want !~ /^#+ /) ? substr(want, 2) : "" }
   /^[[:space:]]*[`][`][`]/ { if (on) print; f = !f; next }
   !f && /^#+ / { lvl = index($(0), " ") - 1; if (on && lvl <= L) exit; if ((anchor != "" && slug($(0)) == anchor) || (anchor == "" && $(0) == want)) { on = 1; L = lvl } }
   on' <dir>/hooks.md
   ```

   - To save turns, extract several sections in one command: run the command once per heading, joined with `;`, and print a line with the heading before each block.
   - To find which section holds a term, list its lines in the download, then extract the heading above the hit:

     ```bash
     grep -n '<term>' <dir>/hooks.md
     ```

   - Empty output means the heading or anchor did not match. Map the download, skipping code fences, and check the spelling:

     ```bash
     awk '/^[[:space:]]*[`][`][`]/{f=!f; next} !f && /^#+ /{print NR": "$(0)}' <dir>/hooks.md
     ```

   - An explicit anchor that differs from its heading is found in the `.mdx` with `grep -n 'id="<anchor>"' /en/hooks.mdx`; then extract the heading below it by name.
   - The `.md` and the `.mdx` number their lines differently: find sections by name, never by a line number taken from the other form.
   - If the download is not possible, read the block in the MCP with `sed -n '<start>,<end>p' /en/hooks.mdx`, taking both lines from the MCP map, and truncate long lines with `cut -c1-200`.
5. List the links inside each extracted section, then read every linked section that touches the hook, with the same command:

   ```bash
   <extract command from step 4.4> | grep -oE 'https://code\.claude\.com/docs/en/[a-z0-9/-]+\.md(#[a-z0-9-]+)?|\]\(#[a-z0-9-]+\)' | sort -u
   ```

   - A link that is only `#anchor` points to the same page.
   - A link to another page: download that page and repeat steps 4.4 and 4.5 on it.
   - Stop when the last two reads added no new fact.
6. Read these sections, in this order, and cite each one in the report by its link. Page `hooks` unless another page is named.
   1. Events, as a panorama before any choice:
      - [How hooks work](https://code.claude.com/docs/en/hooks-guide#how-hooks-work) gives one line per current event on when it fires; [Hook events](https://code.claude.com/docs/en/hooks#hook-events) lists the same events as its `###` headings, and [Prompt-based hooks](https://code.claude.com/docs/en/hooks#prompt-based-hooks) says which handler types each event takes.
      - [What you can automate](https://code.claude.com/docs/en/hooks-guide#what-you-can-automate) holds the documented recipes for common goals: when one matches, use it as the starting design and adapt it to the script conventions.
      - From these, list every event that could serve the goal, then read each candidate's `### <EventName>` section in full before step 5 compares them.
   2. Lifecycle: [Hook lifecycle](https://code.claude.com/docs/en/hooks#hook-lifecycle), including [How a hook resolves](https://code.claude.com/docs/en/hooks#how-a-hook-resolves).
   3. Matcher: [Matcher patterns](https://code.claude.com/docs/en/hooks#matcher-patterns), including [Match MCP tools](https://code.claude.com/docs/en/hooks#match-mcp-tools) for MCP actions.
   4. Input: [Common input fields](https://code.claude.com/docs/en/hooks#common-input-fields), plus the input in the event's section.
   5. Output:
      - [Exit code output](https://code.claude.com/docs/en/hooks#exit-code-output), including [Exit code 2 behavior per event](https://code.claude.com/docs/en/hooks#exit-code-2-behavior-per-event);
      - [JSON output](https://code.claude.com/docs/en/hooks#json-output), including [Decision control](https://code.claude.com/docs/en/hooks#decision-control);
      - [HTTP response handling](https://code.claude.com/docs/en/hooks#http-response-handling) for an HTTP hook;
      - for a hook that must guarantee an outcome, [Block the action when a hook fails](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails) and [Timeouts](https://code.claude.com/docs/en/hooks#timeouts).
   6. Handler fields and how the handler runs: [Hook handler fields](https://code.claude.com/docs/en/hooks#hook-handler-fields), with [Common fields](https://code.claude.com/docs/en/hooks#common-fields) and the chosen type's fields: [Command hook fields](https://code.claude.com/docs/en/hooks#command-hook-fields) with [Exec form and shell form](https://code.claude.com/docs/en/hooks#exec-form-and-shell-form), [HTTP hook fields](https://code.claude.com/docs/en/hooks#http-hook-fields), [MCP tool hook fields](https://code.claude.com/docs/en/hooks#mcp-tool-hook-fields) or [Prompt and agent hook fields](https://code.claude.com/docs/en/hooks#prompt-and-agent-hook-fields). Which events take which types, and when a model's judgment or background work fits better: [Prompt-based hooks](https://code.claude.com/docs/en/hooks#prompt-based-hooks), [Agent-based hooks](https://code.claude.com/docs/en/hooks#agent-based-hooks), [Run hooks in the background](https://code.claude.com/docs/en/hooks#run-hooks-in-the-background).
   7. Where the hook lives: [Configuration](https://code.claude.com/docs/en/hooks#configuration), [Hook locations](https://code.claude.com/docs/en/hooks#hook-locations), [Reference scripts by path](https://code.claude.com/docs/en/hooks#reference-scripts-by-path) and [Hooks in skills and agents](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents); for a plugin, [Hooks](https://code.claude.com/docs/en/plugins/components#hooks) in `plugins/components`; for a subagent, [Define hooks for subagents](https://code.claude.com/docs/en/sub-agents#define-hooks-for-subagents). Then the location reference listed under "Where the hook lives" below.
   8. The operating system: [Failed hooks on Windows without Git Bash](https://code.claude.com/docs/en/hooks#failed-hooks-on-windows-without-git-bash), [PowerShell started no program](https://code.claude.com/docs/en/hooks#powershell-started-no-program) and [Windows PowerShell tool](https://code.claude.com/docs/en/hooks#windows-powershell-tool).
   9. Whether a mod solves it better: [Compare mods, settings hooks, skills, and MCP servers](https://code.claude.com/docs/en/plugins/mods/overview#compare-mods-settings-hooks-skills-and-mcp-servers) and [What a hook can do with an event](https://code.claude.com/docs/en/plugins/mods/overview#what-a-hook-can-do-with-an-event).
   10. Security: [Workspace trust](https://code.claude.com/docs/en/hooks#workspace-trust) and [Security best practices](https://code.claude.com/docs/en/hooks#security-best-practices).
   11. How to confirm it fired: [Limitations and troubleshooting](https://code.claude.com/docs/en/hooks-guide#limitations-and-troubleshooting) and [Debug hooks](https://code.claude.com/docs/en/hooks#debug-hooks).
7. Check that the user's version, the one step 1 noted, has every event and field the design relies on. A hook that relies on one the version lacks doesn't do what it promises there, and a gate fails open. Check only what the design uses:
    - First the minimum the docs write beside a field or event, such as "Requires Claude Code v<version> or later".
    - Then the changelog, for each event and field the docs give no minimum for, with the commands below.
    - When the version lacks one, pick a mechanism that version has, or tell the user what an upgrade would add, and say which.
    - Only when nothing states the user's version, get the local one:

    ```bash
    claude --version
    ```

    Then download the site changelog and list each hit with its version, newest first; each hit belongs to the nearest version line above it:

    ```bash
    curl -sS -o <dir>/changelog.md https://code.claude.com/docs/en/changelog.md
    grep -n -E '<term>|^\*\*[0-9]+\.[0-9]+\.[0-9]+\*\*$' <dir>/changelog.md | grep -B1 '<term>'
    ```

    - If the download is not possible, use the MCP changelog, where each hit belongs to the nearest `<Update label=` line above it:

      ```bash
      grep -n -E '<term>|<Update label=' /en/changelog.mdx | grep -B1 '<term>'
      ```

    - Read each hit's whole entry, from its version line to the next.
    - If no hit has a version line above it, the page no longer writes versions as `**X.Y.Z**`: map its headings with the map command of step 4.4, change the version pattern to match, and run the search again.
    - If neither has a hit, say the version check could not be done for that term.

## Step 5: Decide (the optimal hook, not the first that works)

1. Compare the candidate events read in step 4.6.1, and every other mechanism that could do the job: each handler type (`command`, `http`, `mcp_tool`, `prompt`, `agent`), a mod, a permission rule.
2. Weigh them by when and how often each fires, what each can see and decide, and what each costs to run and maintain.
3. Pick the optimal one. A way that works can still carry more complexity than a newer event or field that does the job directly.
4. For a command hook, pick exec form or shell form from what the command needs and the platforms noted in step 1, as the gotcha on exec form and shell form says: shell form for a script, exec form for a real executable.
5. Pick the location from step 1, and read its reference under "Where the hook lives".
6. Write down the alternatives set aside, and why.

## Step 6: Build (how it is written)

1. Write the script from what step 4 read, starting with the opening lines from step 3.
2. Write the configuration from the location's template (its reference names it). Copy the asset, replace every `<placeholder>`, keep each handler's fields to what step 4 confirmed, and leave `matcher` out on events that don't support one.
3. For a handler that is not a command, put one of these objects in the template's inner `hooks` array instead of the command handler:
   - [assets/handler-http.json](assets/handler-http.json): an HTTP hook. Every header variable must be listed in `allowedEnvVars`, and `allowedHttpHookUrls` in any settings level can block the URL.
   - [assets/handler-mcp-tool.json](assets/handler-mcp-tool.json): an MCP tool hook. A plugin's own server is named `plugin:<plugin>:<server>`. `SessionStart` at launch and `Setup` skip it, because MCP servers are not connected yet.
   - [assets/handler-prompt.json](assets/handler-prompt.json): a prompt hook. `$ARGUMENTS` is replaced with the hook input JSON.
   - [assets/handler-agent.json](assets/handler-agent.json): an agent hook, which the docs mark experimental.
   - [assets/node-exec-handler.json](assets/node-exec-handler.json): a command handler that runs a Node script in exec form, which works on every system because `node` is a real executable.
4. Set the script's permissions as the script conventions say.

## Step 7: Verify and correct (one pass)

1. Write the expected outcome of each input before running anything:
   - one input that must trigger the hook's action (block, deny, context);
   - one input that must stay silent;
   - for a gate, one input it cannot read, which must block.
2. Build each input from the event's documented fields and run the script with it:

   ```bash
   printf '%s' '<input-json>' | ./<script>; echo "exit=$?"
   ```

3. Compare stdout, stderr and the exit code with the expected outcome. Check that JSON output parses (`jq -e .`) and that each field sits where `### JSON output` puts it. Collect every mismatch, find each cause in the docs, apply all fixes at once, check what else they touch, then rerun only the affected inputs.
4. Check the configuration file itself: `jq -e .` for JSON, and `claude plugin validate <plugin-dir>` for a plugin, which warns about an unquoted placeholder in shell form.
5. Confirm in a live session that the hook fires, with the method `## Debug hooks` describes: `/hooks` lists it under its event, and `claude --debug-file <path>` records a `Hooks:` line for its run. A skill's hooks appear in `/hooks` only after the skill is invoked.
6. Report, with explicit evidence for each claim: the raw output, the file and line, or the docs section. Verify everything within reach instead of assuming it.
   - the kind of hook and the evidence for it;
   - the event, the handler type and why they were chosen, and the alternatives set aside;
   - the location and template used;
   - the full content of every file written, and of every file whose write was blocked, so the user can apply it;
   - the docs sections read, each by its link with its anchor, and the changelog range checked against the user's version;
   - each input with its expected and actual outcome;
   - what changed in the correction pass and why;
   - what could not be verified.

## Where the hook lives

Read the one reference for the hook's location in step 5, before writing its configuration, and copy its template in step 6. Each reference gives the role to take, what that location changes (scope, lifetime, registration, trust, placeholders), its gotchas, its rules and its template.

- [references/location-plugin.md](references/location-plugin.md): a plugin's `hooks/hooks.json` or the `hooks` key of `plugin.json`, for Claude Code and Cowork. Template: [assets/plugin-hooks.json](assets/plugin-hooks.json).
- [references/location-user-settings.md](references/location-user-settings.md): `~/.claude/settings.json`, every project on one machine. Template: [assets/user-settings.json](assets/user-settings.json).
- [references/location-project-settings.md](references/location-project-settings.md): `.claude/settings.json`, committed and shared with everyone who clones the repository. Template: [assets/project-settings.json](assets/project-settings.json).
- [references/location-local-settings.md](references/location-local-settings.md): `.claude/settings.local.json`, one person in one project. Template: [assets/project-settings.json](assets/project-settings.json).
- [references/location-managed-settings.md](references/location-managed-settings.md): managed policy settings, deployed by an organization's administrator. Template: [assets/project-settings.json](assets/project-settings.json).
- [references/location-skill-frontmatter.md](references/location-skill-frontmatter.md): `hooks` in a skill's frontmatter, registered when the skill is invoked. Template: [assets/skill-frontmatter.md](assets/skill-frontmatter.md).
- [references/location-subagent-frontmatter.md](references/location-subagent-frontmatter.md): `hooks` in a subagent's frontmatter, active only while it runs. Template: [assets/subagent-frontmatter.md](assets/subagent-frontmatter.md).
- [references/location-subagent-events.md](references/location-subagent-events.md): `SubagentStart` and `SubagentStop` in settings or `hooks/hooks.json`, the only way to hook a plugin's own agents. Template: [assets/subagent-events-settings.json](assets/subagent-events-settings.json).
