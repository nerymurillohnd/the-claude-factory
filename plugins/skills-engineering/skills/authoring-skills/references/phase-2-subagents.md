# Phase 2: Subagents

Decide whether a subagent runs the skill or reads it, and what that changes. This file covers:

- a skill that is the subagent's task
- a skill that is knowledge for a subagent
- what a subagent can't do
- subagents in a plugin

## The skill is the task

`context: fork` runs the skill in a new subagent of the type named in `agent` (`general-purpose` by default), with the skill's content as its prompt. The subagent sees none of the conversation, so the skill must stand on its own: open with the task, carry every input through the arguments or the body, give the steps, and end with what to return.

- Fork only a skill that is a complete task. Guidelines with no task return nothing useful.
- A fork runs in the background by default, with the narrower tool set of background subagents. Set `background: false` to wait for the result and keep the full tool set when the steps depend on a tool outside that set.
- The built-in Explore and Plan agents start without CLAUDE.md and git status, so put everything the task needs in the skill.
- Forking the conversation is a different feature: use it when the task depends on the conversation's history.

Read [Run skills in a subagent](https://code.claude.com/docs/en/skills#run-skills-in-a-subagent) when the skill uses `context: fork`.

## The skill is knowledge for a subagent

A subagent's `skills` field injects the full content of each listed skill into its context at startup, beside the task it was given.

- Write the skill as reference content the subagent applies to whatever it was asked. Never refer to "the user's request" or to the conversation that spawned it.
- A skill with `disable-model-invocation: true` can't be preloaded.
- A subagent can also load a skill on its own with the Skill tool, as the main session does. Write such a skill to work without the main conversation's context.
- A teammate in an agent team doesn't get its definition's `skills`. It loads skills from the project and user scopes, so put a skill a teammate needs there.

Read [Preload skills into subagents](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents) when a subagent should carry the skill.

## What a subagent can't do

- Ask the user: `AskUserQuestion` is removed from every subagent. Give the skill the default to take, and what to report instead of asking.
- Use every built-in tool. A background subagent keeps every MCP tool but only a fixed set of built-in tools. Name each tool the skill relies on, and say what to do when one is missing.
- Spawn without limit: subagents have a depth limit.

Read [Available tools](https://code.claude.com/docs/en/sub-agents#available-tools) when the skill depends on a specific tool inside a subagent.

## Subagents in a plugin

- Agent files live in `agents/`. The agent's name is `<plugin>:<name>`.
- Supported frontmatter: `name`, `description`, `model`, `effort`, `maxTurns`, `autoCompactWindow`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `omitClaudeMd`, `isolation` and `color`.
- Ignored frontmatter: `permissionMode`, `hooks`, `mcpServers` and `initialPrompt`. Put hooks and MCP servers in the plugin's own hooks and MCP files.

Read [Frontmatter fields in plugin agents](https://code.claude.com/docs/en/plugins/components#frontmatter-fields-in-plugin-agents) when a plugin ships a subagent.
