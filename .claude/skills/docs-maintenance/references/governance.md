# Governance

The rules you follow on every documentation task, whatever the event. Read this file in full before you launch the first subagent of a task.

## What stays with you

These are not documents and no subagent touches them:

- `plugins/<plugin>/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`: versions, names, descriptions, catalog entries. Change them yourself, before you launch the subagents that read them.
- The decisions: which version a release gets, which change type and whether it is breaking, what changed for the user and why.
- The owner's values in the subagents table of `SKILL.md`. Ask the owner for any that are missing; never invent one and never let a subagent guess it.
- Commits, pull requests and releases, under the rules in `.claude/CLAUDE.md`.

## Running subagents in parallel

- Never run two subagents on the same file at the same time. Every file has one owner, so this only happens if you launch the same subagent twice for one file.
- Subagents start in the background. Wait for their completion notices instead of doing their work in the meantime.

## How to brief a subagent

The subagent starts with no context, so the prompt is its whole picture of the task. Write it like a work order:

- **Scenario**: the event in one line, and whether to create, update, release, audit or fix.
- **Target**: the plugin directory and the file, or "repository root".
- **What changed and why**: in the user's terms, with the paths of the files that changed.
- **Decisions**: version, change types, breaking or not, release date.
- **Owner values**: every value the subagents table of `SKILL.md` lists for this subagent, exactly as the owner gave it.
- **Scope**: "report only" or "fix" for an audit; any file it must leave alone that it might be tempted to touch.

Example:

```text
Scenario: a released plugin changed; record the changes under Unreleased.
Target: plugins/turn-meter/CHANGELOG.md
What changed: the status line now shows tokens per minute (new, from skills/turn-meter/SKILL.md and
scripts/rate.sh); the `--compact` option was removed from the /turn-meter command.
Decisions: the first change is Added; the removal is Removed and breaking: users who pass --compact
get an error and must drop the flag.
Owner values: none needed.
```

Leave out what the subagent already knows: its template, its rules, how to format its document.

## Check what came back

For every subagent, before you rely on its result:

1. **Read its final message.** Act on each part:
   - **Missing values**: ask the owner, then launch the subagent again with them.
   - **Changes other files need**: send each one to that file's owner, or make it yourself when it is `plugin.json` or `marketplace.json`.
   - **Findings** (audit): take them to the owner before any fix.
2. **Check what it touched.** `git status --short` must show only the files the subagent owns, plus its memory under `.claude/agent-memory/`. If it changed anything else, restore that file with `git checkout -- <file>` and tell the owner.
3. **Check for leftovers** in each file it wrote: `grep -n '{{' <file>` and `grep -n '<!--' <file>` should find nothing, except where the subagent's own rules keep them.
4. **Validate the plugin** when the subagent wrote one of its documents: `claude plugin validate plugins/<plugin> --strict --profile directory`.
5. **Read the diff.** Make sure it says what the change is, and that it states nothing the plugin's files or the owner did not give.

When a result is wrong, launch the subagent again with what is wrong and what to do. Do not fix the document yourself.

## When something gets in the way

- **No subagents in this session**, as in a cloud thread of a Claude Project or in Claude chat: leave the documents as they are, and tell the owner which documents the change needs and why.
- **A subagent stops without finishing** (turn limit or error): resume it with SendMessage and its agent ID, or launch it again with the same brief.
- **A subagent reports that an official source contradicts its template**: do not work around it. Bring the conflict to the owner; a template changes only with the owner's decision.
- **The owner asks you to edit a document directly**: say once that its subagent keeps it consistent with the template, and recommend launching it. Do what the owner decides.

## Conventions that bind every document

They are in `.claude/CLAUDE.md`. The ones that shape briefs most often:

- Release dates are UTC, `YYYY-MM-DD`, the day the tag and GitHub Release are created.
- The two surfaces are named **Claude Code** and **Claude**, and no other surface name is used.
- Prerequisites, tools and minimum versions a plugin needs go in its README's Prerequisites section.
- Plugin changes that touch components, dependencies or configuration go through a pull request, and only at the owner's request. A change limited to a plugin's documentation needs none.
- The repository is public: no personal, client or business data in any document or memory.
