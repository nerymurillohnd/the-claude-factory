# Phase 2: Placements

Decide the surfaces the skill must run on, the subagent that runs it and how, and who invokes it, and the layout of a single skill at a plugin root.

## A skill that leaves Claude Code

claude.ai, the Skills API and other Agent Skills clients run the skill without Claude Code's processing. Write it for the strictest surface it must run on, and tell the requester each Claude Code feature that leaves out.

Before relying on what a surface provides, consult https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.

## A skill run by a subagent

Choose by who writes the task:

- **The skill is the task** (`context: fork`). The body becomes the prompt of a new subagent that sees none of the conversation.

  A body of guidelines with no task returns nothing useful: fork only a skill that is a complete task.
- **The skill is knowledge for a subagent's task** (the subagent's `skills` field). The full body loads into the subagent at startup, beside the task it was given.
  - A teammate in an agent team doesn't get its definition's `skills`, and while agent teams are on, a subagent Claude names launches as a teammate: put a skill such an agent needs in the project or user settings, which teammates load.
- **A subagent may load it on its own**, as the main session does, when its tools include the Skill tool. Write such a skill to work without the main conversation's context.

## A skill only its users invoke, or only the model

- **Only its users** (`disable-model-invocation: true`): use it for actions with side effects or timing the user must control, such as deploying, sending or publishing. Its description no longer reaches the model, so neither the model nor another skill can load it, and a subagent can't preload it.
- **Only the model** (`user-invocable: false`): use it for background knowledge that isn't an action, such as how a legacy system behaves. It leaves the menu; the model still loads it from the description.

Choose by consequence: if the model running the skill unasked could change something the user didn't approve, require the user to invoke it.

## Layouts

Single skill at a plugin root, for a plugin with no `skills/` folder. Its `name` field sets the command's last segment:

```text
my-plugin/
├── .claude-plugin/plugin.json
├── SKILL.md            name: review  →  /my-plugin:review
└── references/checklist.md
```
