# Phase 2: Hooks

Decide whether the skill needs a hook, which event it uses and where the hook lives. This file covers:

- hook or skill
- how hooks work
- where a hook lives
- hooks in a skill
- paths and scripts

## Hook or skill

A rule that must hold every time belongs in a hook: a hook runs, and a skill is only advice. A check that must hold on every event once the skill is active belongs in the skill's own hooks. A check that must hold whether or not the skill was invoked belongs in the plugin's hooks or in settings.

## How hooks work

A hook runs at a point in a session. When an event fires and its matcher matches, Claude Code passes JSON about the event to the handler, which can inspect it, act and return a decision.

- Events come in three cadences: per session (`SessionStart`, `SessionEnd`), per turn (`UserPromptSubmit`, `Stop`) and on every tool call (`PreToolUse`, `PostToolUse`). There are more, for subagents, permissions, compaction, file changes and other points.
- A matcher filters the event: the tool name for tool events (`Bash`, `Edit|Write`, `mcp__.*`), how the session started for `SessionStart`, the agent type for subagent events. An omitted matcher or `*` matches all.
- A handler is a command, an HTTP endpoint, an MCP tool, a prompt or an agent. A command hook receives the event's JSON on standard input and answers with its exit code and JSON on standard output.
- The `if` field narrows a hook to one permission rule, such as `Bash(git *)`. The hooks that match an event run in parallel.

Read [Hook lifecycle](https://code.claude.com/docs/en/hooks#hook-lifecycle) when you choose the event.

Read [Hook events](https://code.claude.com/docs/en/hooks#hook-events) when you need an event's input and the decisions it can return.

Read [Matcher patterns](https://code.claude.com/docs/en/hooks#matcher-patterns) when the hook must fire only on some tools or sources.

Read [Hook handler fields](https://code.claude.com/docs/en/hooks#hook-handler-fields) when you choose the handler type and its fields.

## Where a hook lives

- Settings file (`~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`) or managed settings: user, project or organization scope.
- A plugin's `hooks/hooks.json`: while the plugin is enabled. Shareable with the plugin.
- A skill's frontmatter: from the moment the skill is invoked until the end of the session. Shareable with the skill.
- A subagent's frontmatter: only while that subagent runs.

Cloud sessions don't read the user's local `~/.claude/settings.json`.

## Hooks in a skill

- The hook registers when the skill is invoked and keeps running for the rest of the session, on later turns too. `once: true` removes it after its first successful run, and only skill frontmatter honors it.
- Under the managed setting `strictPluginOnlyCustomization`, a skill keeps its frontmatter hooks only if it is a plugin skill, a bundled skill or a skill in the managed settings directory. To keep them, ship the skill in a plugin.
- Each source of skills may register at most 1,024 hooks and 16,384 characters of matchers. Declare few hooks and short matchers.
- A check that must hold inside a subagent goes in that subagent's own `hooks` frontmatter. A plugin's subagent ignores `hooks`, so a plugin puts such a check in its own hooks file, which applies to the whole session.

Read [Hooks in skills and agents](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents) when the hook lives in frontmatter.

## Paths and scripts

- A hook reaches its script with a path variable: `${CLAUDE_PROJECT_DIR}` for the project, `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` for a plugin. `${CLAUDE_SKILL_DIR}` is not among the variables the hooks documentation lists, so don't rely on it in a hook.
- Prefer the exec form, a `command` plus its `args`, for any hook that names a path variable. In the shell form, wrap each variable in double quotes.
- Naming the interpreter as the command, with the script in `args`, passes the path as one argument and spares the script a shebang. A script called by its own path needs a shebang through `/usr/bin/env` and mode 755. Without them the call fails, and a failing hook doesn't block the action.

```yaml
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: python3
          args: ["${CLAUDE_PLUGIN_ROOT}/scripts/check_output.py"]
```

Read [Reference scripts by path](https://code.claude.com/docs/en/hooks#reference-scripts-by-path) when the hook calls a script.

Read [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide) when you need worked examples and troubleshooting.
