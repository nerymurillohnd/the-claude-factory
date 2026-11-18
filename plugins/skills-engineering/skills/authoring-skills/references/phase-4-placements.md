# Phase 4: Placements

How to write the skill for the placements phase 2 chose: a skill that leaves Claude Code, a skill a subagent runs and a skill only its users invoke, and how to package an upload.

## A skill that leaves Claude Code

Write each part for the strictest surface the skill must run on:

- **Body**: no argument placeholders, `CLAUDE_` variables, injected commands or at-mentions. They reach the model as literal text there. Refer to bundled files by paths relative to the skill root.
- **Scripts**: the Claude API runs them with no network and no package installs, and claude.ai's access depends on its settings. Write scripts that use only the standard library or packages the surface already provides, and state each one the skill needs.

## A skill run by a subagent

- **A forked skill** (`context: fork`):
  - Open with the task.
  - Carry every input through the arguments or the body.
  - Give the steps.
  - End with what to return to the main conversation.
- **A skill a subagent preloads** (its `skills` field):
  - Write it as reference content the subagent applies to whatever it was asked.
  - Never refer to "the user's request" or to the conversation that spawned it.
- **A skill a subagent loads on its own:**
  - A subagent runs in the background by default, and there it keeps the Skill and ToolSearch tools and every MCP tool, but only a fixed set of built-in tools. Name each tool the skill relies on, and what to do when one is missing.

A skill run by a subagent can't ask the user anything: Claude Code removes the question tool from every subagent. Give it the default to take, and what to report instead of asking.

## A skill only its users invoke

- **Only its users** (`disable-model-invocation: true`):
  - Write the body as the procedure the command runs.

## Upload layout

Upload, with the skill folder at the root of the archive:

```text
invoice-export.zip
└── invoice-export/
    ├── SKILL.md        six portable fields only
    └── scripts/to_csv.py
```

The six portable fields are the ones phase-3-frontmatter.md lists as accepted by every surface.
