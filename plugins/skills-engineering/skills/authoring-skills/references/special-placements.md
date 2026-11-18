# Special placements

What changes in the writing when a skill leaves Claude Code, runs in a subagent, or is invoked only by its users or only by the model. A skill can be several of these at once; apply every section that fits.

## A skill that leaves Claude Code

claude.ai, the Skills API and other Agent Skills clients run the skill without Claude Code's processing. Write it for the strictest surface it must run on:

- **Frontmatter**: only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Any other field makes the upload fail.
- **Body**: no argument placeholders, `CLAUDE_` variables, injected commands or at-mentions. They reach the model as literal text there. Refer to bundled files by paths relative to the skill root.
- **Scripts**: the Claude API runs them with no network and no package installs, and claude.ai's access depends on its settings. Write scripts that use only the standard library or packages the surface already provides, and state each one the skill needs.
- **Copies**: an upload doesn't sync back. A skill built in Claude Code reaches claude.ai or the API only when someone uploads it, and each copy is kept separately.

Before relying on what a surface provides, consult https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.

## A skill run by a subagent

Choose by who writes the task:

- **The skill is the task** (`context: fork`). The body becomes the prompt of a new subagent that sees none of the conversation.
  - Open with the task.
  - Carry every input through the arguments or the body.
  - Give the steps.
  - End with what to return to the main conversation.

  A body of guidelines with no task returns nothing useful: fork only a skill that is a complete task.
- **The skill is knowledge for a subagent's task** (the subagent's `skills` field). The full body loads into the subagent at startup, beside the task it was given.
  - Write it as reference content the subagent applies to whatever it was asked.
  - Never refer to "the user's request" or to the conversation that spawned it.
- **A subagent may load it on its own**, as the main session does, when its tools include the Skill tool. Write such a skill to work without the main conversation's context.
  - A subagent runs in the background by default, and there it keeps the Skill and ToolSearch tools and every MCP tool, but only a fixed set of built-in tools. Name each tool the skill relies on, and what to do when one is missing.

A skill run by a subagent can't ask the user anything: Claude Code removes the question tool from every subagent. Give it the default to take, and what to report instead of asking.

## A skill only its users invoke, or only the model

- **Only its users** (`disable-model-invocation: true`): use it for actions with side effects or timing the user must control, such as deploying, sending or publishing. Its description no longer reaches the model, so neither the model nor another skill can load it, and a subagent can't preload it.
  - Write the description for the person choosing it from the menu.
  - Write the body as the procedure the command runs.
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

Upload, with the skill folder at the root of the archive:

```text
invoice-export.zip
└── invoice-export/
    ├── SKILL.md        six portable fields only
    └── scripts/to_csv.py
```
