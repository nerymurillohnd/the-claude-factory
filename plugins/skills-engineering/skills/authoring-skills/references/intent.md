# Intent

How to find out what the requester actually needs before designing anything: disentangling the request, extracting a skill from work already done, writing use cases, and asking only the questions the requester alone can answer.

## Contents

- Disentangle the request
- Extract from work already done
- Use cases and success criteria
- What to ask and what to decide
- Requests that aren't one skill

## Disentangle the request

A request for a skill states a solution. Find the problem behind it:

1. **What is asked**: the literal request. "Make a skill for our release notes."
2. **What lies behind it**: what goes wrong today without the skill. "The model writes release notes in a different format each time and forgets the breaking-changes section."
3. **What it implies**: who will use it, on which surfaces, with what inputs, and what must not change. "The whole team, in Claude Code; input is the merged PRs since the last tag; the format is fixed by the website."
4. **What success looks like**: the result the requester would accept, stated so it can be checked.

Sort everything you know into stated, implied, assumed and missing. Carry the assumptions into the plan, where the requester sees them. Ask only about what is missing and would change what you build.

## Extract from work already done

The best source is a task already done well with the model in this conversation, or the project's own material. Extract:

- **The steps that worked**, in the order they worked.
- **The corrections**: each place the user steered the model. Each is a rule or gotcha the skill must carry.
- **The formats**: the inputs as they arrived and the outputs the user accepted.
- **The context supplied**: names, conventions, paths, accounts, facts the model couldn't have known.
- **What the model did well unaided**: leave it out of the skill.

From project material (runbooks, style guides, review comments, incident reports, past fixes), take the decisions and the reasons, not the prose.

Show the requester what you extracted and confirm it before designing.

## Use cases and success criteria

Write two or three use cases before any design. They define the skill's scope and become the scenarios you test it with.

```text
Use case: Release notes for a minor version
Trigger: "write the release notes for 2.4"
Steps: list merged PRs since v2.3.0, group by label, write the notes from the template
Result: RELEASE_NOTES.md with Features, Fixes and Breaking changes; every PR listed once
```

For each, state a result the model can check: a file that exists, a section present, a count that matches, a command that passes. "Good release notes" can't be checked; "every merged PR appears exactly once" can.

Add a use case for the request the skill must not handle, when a near-miss is likely.

## What to ask and what to decide

Ask the requester for context: what only they know. Decide the design yourself: that is your expertise, and asking hands your work back to them.

Ask:

- Who will use the skill, and on which surfaces?
- What goes wrong today, or what do you redo every time?
- Can you show an example of a good result, or of the input it starts from?
- What must stay under your control: approvals, things never to touch?
- Which tools, systems or accounts does the work involve?

Don't ask:

- Should the skill use a checklist? Should it have a script?
- What should the description say? What should the name be? (Propose them.)
- Which frontmatter fields do you want?
- Should I write it now?

Ask only what changes what you build, in one round, at most three questions, each with your recommended answer and why. When the conversation or the project already answers a question, use that answer and say so instead of asking.

## Requests that aren't one skill

- **Several skills in one request**: split by trigger and by task. If two parts would load on different requests, or one is reference and the other a procedure with side effects, propose them as separate skills, with the boundary between their descriptions.
- **Not a skill**: a rule that must hold every time is a hook; a fact every session needs belongs in CLAUDE.md; access to an external system is an MCP server. Say which feature fits and why, and stop unless the requester still wants a skill for part of it.
- **A one-off task**: if the work won't repeat, do the task instead of writing a skill for it, and say so.
