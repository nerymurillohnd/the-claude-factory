# Hooks on subagent events

Read this in step 5 when the main session must act when a subagent starts or stops: `SubagentStart` and `SubagentStop` in a settings file or a plugin's `hooks/hooks.json`.

## Role

You write hooks in the main session that wrap a subagent's run from outside it: set up before it starts, clean up after it stops.

## Knowledge

- Matcher: the agent's type name. For a project or user subagent it is the frontmatter `name`; for a plugin subagent it is the scoped name `<plugin>:<agent>`.
- A scoped name contains a colon, so it is evaluated as an unanchored regular expression: `my-plugin:db-agent` also matches `my-plugin:db-agent-v2`.
- This is the only way to hook a plugin's own agents, because plugin agents ignore frontmatter hooks.
- Location rules (scope, trust, placeholders) are those of the file the hooks live in: read that file's reference too.
- Docs: `#### Project-level hooks for subagent events` in `sub-agents`, and `### SubagentStart` and `### SubagentStop` in `hooks`.

## Gotchas

- `SubagentStop` is a stop event: exit 2 or `decision: "block"` sends the subagent back to work, and `onFailure` has no effect on it.
- A `SubagentStop` group with no matcher fires for every subagent: a cleanup hook without one runs when any other subagent stops.

## Rules

- Write a project or user agent's plain name as it is: letters, digits, `_` and `-` make an exact match. Anchor a plugin agent's scoped name: `^<plugin>:<agent>$`.
- Match `SubagentStop` to the same agent as `SubagentStart` when the two hooks pair up, such as opening and closing a resource.

## Structure

- File: `hooks/hooks.json` in a plugin, or the settings file of the chosen scope.
- Template: `assets/subagent-events-settings.json`. In a plugin, write each `command` the way `assets/plugin-hooks.json` does, through the plugin root placeholder instead of the project one, and keep that file's `"hooks"` wrapper.
