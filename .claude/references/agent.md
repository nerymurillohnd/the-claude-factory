# Agent

How to create a plugin subagent from `.claude/templates/agent-template.md`.

## Produces

`plugins/<plugin>/agents/<agent>.md`: a subagent Claude delegates to, named `<plugin>:<agent>` once installed.

## When

- When a plugin gains a subagent, and when its job, tools or model change.

## Sources

Read 2026-11-10, Claude Code docs `sub-agents`:

- Required: `name` ("Names can't contain `:`, which is reserved for plugin-scoped identifiers") and `description` ("When Claude should delegate to this subagent").
- `tools`: comma-separated or a YAML list; omitted, the subagent inherits every tool available to subagents; to preload skills, use `skills`, not `Skill` in `tools`.
- `model`: `sonnet`, `opus`, `haiku`, `fable`, a full model ID, or `inherit`; omitted, Claude Code uses the subagent model order.
- `color`: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink` or `cyan`.
- "For security reasons, plugin subagents don't support the `hooks`, `mcpServers`, or `permissionMode` frontmatter fields"; `initialPrompt` is also ignored for plugin subagents.
- Other optional fields: `disallowedTools`, `maxTurns`, `autoCompactWindow`, `skills`, `memory`, `background`, `omitClaudeMd`, `effort`, `isolation`, `experimental`.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{agentName}}` | Kebab-case name, no colon | The file name |
| `{{agentDescription}}` | When Claude should delegate to it | The agent's job |
| `{{agentTools}}` | Tools it may use | The least set its job needs |
| `{{agentModel}}` | Model alias, full ID or `inherit` | The job's needs |
| `{{agentColor}}` | Display color | One of the eight colors |
| `{{agentRole}}`, `{{agentResponsibility}}`, `{{agentInstructions}}` | The system prompt | The agent's job |

## Procedure

1. Copy the template to `plugins/<plugin>/agents/<agent>.md`.
2. Fill the frontmatter; delete `tools` or `model` to inherit; delete the instruction comment.
3. Write the system prompt: role, bounded responsibility, procedure, what it reports.
4. Give it the fewest tools its job needs; a read-only reviewer gets no write tools.
5. Run the checks.

## Rules

Official:

- `name` and `description` are required; `name` has no colon.
- `hooks`, `mcpServers`, `permissionMode` and `initialPrompt` do nothing in a plugin agent.

This repository:

- A colon goes only after a field name. No value holds a colon or is wrapped in quotes: reword the sentence instead, so `description` stays one plain line that strict YAML parsers read.
- Every agent sets `color`.
- Agents load only where Claude can run tasks (`docs/compatibility.md`); the plugin README says so.

## Checks

- `claude plugin validate --strict plugins/<plugin>`.
- `claude plugin details plugins/<plugin>`: the agent is listed.

## Never

- Never rely on an ignored field for a safety guarantee.
- Never grant tools the job does not need.
