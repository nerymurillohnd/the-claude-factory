# Description lens

What the description reviewer checks: how the skill is found and invoked, and whether every surface it reaches loads what it depends on.

## Items

Each line names the checklist item from [checklist.md](checklist.md), then the area file and heading that hold the rule, then the rule's bold lead-in. Read the rule there; it is not repeated here.

- `FM-3` · [description.md#writing-the-description](description.md#writing-the-description) · **What and when.**
- `FM-3` · [description.md#writing-the-description](description.md#writing-the-description) · **Key terms.**
- `FM-3` · [description.md#writing-the-description](description.md#writing-the-description) · **User intent, not mechanics.**
- `FM-3` · [description.md#writing-the-description](description.md#writing-the-description) · **Be pushy about scope.**
- `FM-3` · [description.md#writing-the-description](description.md#writing-the-description) · **Concise.**
- `FM-3` · [description.md#writing-the-description](description.md#writing-the-description) · **Point of view.**
- `FM-3` · [description.md#writing-the-description](description.md#writing-the-description) · **Too broad or too narrow.**
- `FM-3` · [description.md#writing-the-description](description.md#writing-the-description) · **Tell sibling skills apart by the kind of request**
- `FM-3` · [description.md#writing-the-description](description.md#writing-the-description) · **Avoid vague descriptions**
- `FM-7` · [description.md#writing-the-description](description.md#writing-the-description) · **Don't summarize the procedure.**
- `FM-7` · [description.md#writing-the-description](description.md#writing-the-description) · **Cover every capability the body offers.**
- `FM-8` · [claude-code-features.md#invocation-control](claude-code-features.md#invocation-control) · **Two kinds of content** and **Which setting to use.**
- `SU-1` · [surfaces.md#origins-and-the-surfaces-they-reach](surfaces.md#origins-and-the-surfaces-they-reach)
- `SU-1` · [surfaces.md#repository-skills-in-cloud-sessions](surfaces.md#repository-skills-in-cloud-sessions)
- `SU-1` · [surfaces.md#plugin-components-by-surface](surfaces.md#plugin-components-by-surface) · **State what the skill does without its agents and hooks.**
- `SU-1` · [surfaces.md#how-the-body-behaves-by-surface](surfaces.md#how-the-body-behaves-by-surface) · **Depending on a skipped feature is a defect.**

## Method

1. Read the area file each pointer names, including one your contract doesn't list, at the step that uses it.
2. Read every file in the inventory first: the description must cover what the whole skill offers, not only `SKILL.md`.
3. Triggering: list what the body offers, then compare that list with the description, capability by capability. A capability missing from the description, and a phrase that describes the procedure or the mechanics instead of the user's intent, are findings.
4. Boundary: read the description as a user with a near-miss request would. Check that it marks where the skill ends by the kind of request, without naming other skills.
5. Order: check that the main use case comes first, where a cut listing still shows it.
6. Invocation: decide whether the skill is reference content or task content, and whether it has side effects; check that who may invoke it fits that.
7. Surfaces: for each surface the brief lists, walk the body's instructions and mark each one that depends on something that surface skips (agents and hooks in chat, `!` lines in synced skills, Claude Code-only features in chat and the API).
