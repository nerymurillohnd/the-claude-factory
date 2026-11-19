# Phase 1: Understand the user's intent

Whether a skill is the right feature, and how to understand what the user wants (Scenario A), propose a skill for a repeated process (Scenario B), or understand what to change in an existing skill (Scenario C), before you design anything.

## Gotchas

- Claude loads a skill only for work it can't do well alone, so a skill for a one-step task such as "read this PDF" may never load: write skills for specialized knowledge, unfamiliar APIs, domain workflows or uncommon formats.
- A session signed in with a claude.ai account already has Anthropic's synced skills, such as `pdf` and `xlsx`, and every session has the bundled ones, such as `/code-review` and `/loop`: check the listing for one that does the job before you write a skill.
- A failure you hit while doing a process once, such as a network error or a missing tool, isn't a rule of the process: check that it holds beyond this session before a skill you propose states it.

## Is a skill the right feature

Match the need to the feature that meets it, before you design anything:

| The need | The feature |
| :-- | :-- |
| A task that won't repeat | Do the task, with no skill |
| Something Claude already does well | No skill |
| A fact or "always do X" rule every session needs | CLAUDE.md |
| A rule for some files or folders | A rule in `.claude/rules/` with `paths` |
| A voice, length or format for every response | An output style |
| A rule that must hold every time | A hook or a permission rule |
| Work that needs its own context and tools | A subagent; a skill can give it knowledge |
| Access to an external system | An MCP server; a skill teaches how to use it |
| Knowledge or a procedure Claude needs for some tasks | A skill |

- When the need isn't a skill, tell the user which feature fits and why, and stop unless they still want a skill.
- When the request holds several needs, split it: each need gets its own feature or skill.

Example: "a skill so Claude never edits `.env`" is a hook. "A skill with our release checklist" is a skill. "A skill that formats code after each edit" is a hook that runs the formatter, plus a skill only if fixing what the formatter reports needs judgment.

## Scenario A: user request

1. Understand
   - Read the request together with the related work already done in the conversation or the project, and state the goal the skill must meet.
2. Ask
   - Ask the user only for context you lack. Decide the technical matters yourself, such as how to build it, what to name it and which fields it needs.
3. Challenge
   - Check the need against Is a skill the right feature, above.
   - Tell the user when part of the request doesn't apply, is deficient, or has a better way to reach the same goal, and propose it.
   - The decision is theirs.
   - Build only what serves the user's goal.
4. No one to ask
   - In a subagent, or a run with nobody to answer, state each assumption in your reply and go on.
5. Move on
   - Go to Phase 2 only when you can state the goal, what the skill is, what it must achieve or teach Claude, and why it should exist.

## Scenario B: repeated process

The process can be a task that will repeat across sessions, or a procedure you just performed that may serve the user again.

1. Pause
   - Stop the work in progress when you detect the process.
2. Explain
   - Check the process against Is a skill the right feature, above, and propose the feature it fits.
   - Tell the user what you detected, based on the work already done.
   - Explain what a skill is and why you propose one: what you saw, why it will repeat, and the work it saves.
3. Ask
   - Ask whether they want a skill for it.
4. Wait for approval
   - Wait for the user's answer before you do anything else.
5. Act on the answer
   - If the user says yes, or adds comments, continue with their comments and go to Phase 2.
   - If the user says no, end here and leave this skill.

## Scenario C: existing skill

The request can be the user's own, or the improvements and corrections an audit recommended.

1. Understand
   - Read the existing skill whole, first line to last, with every file it points to.
   - Unfold what the user asks to change, or what the audit recommended, and the goal of the change.
2. Verify the findings
   - When the request follows an audit, check each finding against the skill and the official sources, since a finding can be wrong.
   - Tell the user which findings you reject and why.
3. Ask, challenge and proceed
   - Follow steps 2 to 4 of Scenario A, changing only what serves the goal.
4. Move on
   - Go to Phase 2 only when you can state what changes, why, and what stays.
   - Keep the skill's name and folder unless the user asks otherwise.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Compare similar features](https://code.claude.com/docs/en/features-overview#compare-similar-features) when the need sits between a skill and another feature. It compares a skill with CLAUDE.md, rules, subagents, MCP, hooks and output styles, pair by pair.
- Read [How skill triggering works](https://agentskills.io/skill-creation/optimizing-descriptions#how-skill-triggering-works) when the task may be simple enough for Claude to do without the skill. It explains which tasks make an agent consult a skill.
- Read [Bundled skills](https://code.claude.com/docs/en/skills#bundled-skills) when the job may already ship with Claude Code. It lists the bundled skills.
- Read [Skills synced from claude.ai](https://code.claude.com/docs/en/skills#how-synced-skills-behave) when a synced skill may already do the job. It says which of Anthropic's skills always sync and in which sessions.
