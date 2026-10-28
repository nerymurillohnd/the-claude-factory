# Procedures and repeated workflows: recommend a skill, a hook or a script

Instruction files hold standing facts and conventions. Procedures (ordered steps for one kind of task) cost context in every session while being useful in a few, and they are where Claude most often skips or reorders steps. Detect them whenever you read instruction files, whatever the request was, and raise them unprompted.

## Signals

- Ordered steps or a checklist (five or more items, or "first… then… finally…") inside CLAUDE.md or a rule.
- Headings or phrases such as release, deploy, rollout, runbook, onboarding, setup, migration guide, incident, "how to add a new …", "steps", "checklist", "every time we …".
- A rule that only ever applies when doing one task type (cutting a release, adding an endpoint end to end, rotating a key).
- The user says Claude has to be reminded of the same sequence every session, or the same request recurs.
- Mechanical sequences that never vary (always format after edit, regenerate the client after changing the schema, run the same three commands before finishing).

## Decide what it should become

| What you found | Becomes | Why |
| :-- | :-- | :-- |
| Multi-step task that needs judgment (which tests to run, how to write release notes, how to scaffold an endpoint) | Skill in `.claude/skills/<name>/SKILL.md` | Only its name and description load until it is used; steps stay together |
| Task with side effects the user must start deliberately (release, deploy, data migration, sending messages) | Skill with `disable-model-invocation: true` | Runs only when the user types `/<name>` |
| Fixed mechanical step that must always follow an action | Hook (for example `PostToolUse` to format, a `Stop` hook to require the check) or a project script | Deterministic; the model does not need to remember it |
| Reference material needed sometimes (API conventions doc, style guide) | Skill, or a doc Claude is pointed to | Keeps always-on context small |
| One-off steps for the current task | The task prompt or a plan file | Not durable |

Keep behind a one-line pointer in CLAUDE.md only what Claude must know before the task starts ("Releases: run /release; never publish from a laptop").

## How to raise it

Raise it as a recommendation with a question, not a silent change, unless the user asked you to restructure:

```markdown
**Candidate for a skill:** CLAUDE.md lines 88–112 are a 15-step release runbook. They load in every
session but matter only when releasing, and steps 9–11 have side effects. Proposed: a `release` skill
(`disable-model-invocation: true`, description "Cut a release: version bump, changelog, tag and
promote"), with one pointer line left in CLAUDE.md. Want me to create it?
```

When creating it (asked or approved): move the steps verbatim first, then tighten; keep side-effecting steps behind explicit confirmation; check the skill's frontmatter against the current skills reference; remove the steps from the instruction file and leave the pointer; record the move in the traceability table.
