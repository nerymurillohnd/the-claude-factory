# Phase 2: Skills for subagents

Whether a subagent runs the skill as its task or preloads it as knowledge, what a subagent can't do, and how to write the body of a subagent the skill ships.

## Contents

- [Gotchas](#gotchas)
- [The skill is the task](#the-skill-is-the-task)
- [The skill is knowledge for a subagent](#the-skill-is-knowledge-for-a-subagent)
- [Write the body of a subagent](#write-the-body-of-a-subagent)
- [Subagents in a plugin](#subagents-in-a-plugin)
- [Official sources](#official-sources)

## Gotchas

- A subagent in the background, the default, keeps every MCP tool but only a fixed set of built-in tools. Name each tool the skill relies on, and say what to do when one is missing.
- The built-in Explore and Plan agents start without CLAUDE.md and git status: the skill must carry everything the task needs.
- A teammate in an agent team doesn't get its definition's `skills`. It loads skills from the project and user scopes, so a skill a teammate needs lives there.
- A subagent shipped in a plugin ignores `permissionMode`, `hooks`, `mcpServers` and `initialPrompt`.

## The skill is the task

`context: fork` runs the skill in a new subagent of the type named in `agent`, `general-purpose` by default, with the skill's content as its prompt.

- Fork only a skill that is a complete task: open with the task, carry every input in the arguments or the body, give the steps, and end with what to return. Guidelines with no task return nothing useful.
- Set `background: false` to wait for the result and keep the full tool set, when the steps need a tool outside the background set.
- Fork the conversation instead, a different feature, when the task depends on the conversation's history.

## The skill is knowledge for a subagent

A subagent's `skills` field injects the full content of each listed skill into its context at startup, beside the task it was given.

- Write the skill as reference content the subagent applies to whatever it was asked, with no mention of "the user's request" or of the conversation that spawned it.
- Leave out `disable-model-invocation: true`: a skill with it can't be preloaded.
- Write a skill a subagent may load on its own, with the Skill tool, to work without the main conversation's context.

## Write the body of a subagent

Write the body as a prompt in natural language with a clear hierarchy, not as a Markdown document. Open every subagent with the same three parts, in this order, before anything else: its role, its expertise and its goal.

1. Role: a paragraph, "You are a [role], with expert knowledge of [the domains and sources it works from]. You specialize in [its focus].", then the seat it works from and what counts as a failure from there.
2. Expertise: `Your expertise:`, followed by a bullet per area, each as "Area: what it covers".
3. Goal: a `GOAL:` section with the purpose the subagent must reach, what it must determine or produce, and for whom.
4. Mark each later section with an uppercase label on its own line, followed by a colon, and choose the sections the work needs, such as `GOTCHAS:`, `WORKFLOW:`, `RULES:`, `REPORT:` and `VERIFICATION CHECKLIST:`.
5. Number the steps of `WORKFLOW:`, and bullet the facts and rules that have no order.
6. Point to each file the subagent reads by its full path. In a plugin, build it on `${CLAUDE_PLUGIN_ROOT}`, which Claude Code replaces in an agent's body, such as `${CLAUDE_PLUGIN_ROOT}/skills/[skill]/references/[file].md`: a subagent opens files with the Read tool, and a relative link resolves from no known folder.

```markdown
<!-- Weak: no role or expertise, and a Markdown document with headings, bold and a relative link -->
## Your task
**Review** the skill against [the checklist](checklist.md).

<!-- Strong -->
You are a senior reviewer of Claude skills, with expert knowledge of the Agent Skills specification and Anthropic's best practices for writing skills. You specialize in checklists: whether a skill meets each point it must meet. Review from the seat of a Claude that loads the skill with no prior context: every point it would fail is a defect.

Your expertise:

- Checklists: what each point requires, and the evidence that shows it met.
- Evidence: a quoted line for every finding, and an exact fix for every failure.

GOAL:

Determine whether the skill meets every point of its checklist, and report each failure with its evidence.

WORKFLOW:

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/reviewing/references/checklist.md` in full.
2. Check the skill against each point, in order.
```

## Subagents in a plugin

- Put agent files in `agents/`. The agent's name is `<plugin>:<name>`.
- Use the supported frontmatter: `name`, `description`, `model`, `effort`, `maxTurns`, `autoCompactWindow`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `omitClaudeMd`, `isolation` and `color`.
- Put hooks and MCP servers in the plugin's own hooks and MCP files.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Run skills in a subagent](https://code.claude.com/docs/en/skills#run-skills-in-a-subagent) when the skill uses `context: fork`. It covers when Claude Code waits for the result, the background tool set, and the `agent` options.
- Read [Preload skills into subagents](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents) when a subagent carries the skill. It covers the `skills` field, its limit of 32 names, and which skills can't be preloaded.
- Read [Available tools](https://code.claude.com/docs/en/sub-agents#available-tools) when the skill depends on a tool inside a subagent. It lists what a subagent keeps and what it loses.
- Read [Write subagent files](https://code.claude.com/docs/en/sub-agents#write-subagent-files) when the skill ships a subagent. It shows the file format, the frontmatter and the body.
- Read [Environment variables](https://code.claude.com/docs/en/plugins/manifest-reference#environment-variables) when a plugin agent's body names a path. It tables where each path variable is replaced, agent content included.
- Read [Frontmatter fields in plugin agents](https://code.claude.com/docs/en/plugins/components#frontmatter-fields-in-plugin-agents) when a plugin ships the subagent. It lists the fields a plugin agent honors and ignores.
- Read [Subagent orchestration](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#subagent-orchestration) when the skill delegates work to subagents. It says when current models delegate and how to steer it.
