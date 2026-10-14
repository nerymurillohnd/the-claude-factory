# prompt-writer: interpretation contract and deliverable kinds

Date: 2026-10-13. Status: approved for planning. Plugin: `plugins/prompt-writer` (skill `prompt-writer`).

## Product intent

From Nery's brief (2026-10-13), for any third-party user, Nery included as one more user who installs it:

- Claude acts as a strategic partner and an expert prompt engineer who closes the gap between what the user means and what they manage to ask.
- First, understand: help untangle a brief, incomplete or messy idea (what they work on, the goal, the expected result), conversationally, asking only what clarifies intent and context, never technical decisions, and stop asking once there is enough.
- Then guide with judgment: identify approaches, explain the differences that matter, recommend one with reasons, and help detect ambiguities and alternatives.
- Design the prompt at the length the task needs: neither huge by default nor two lines when more is needed.
- For multi-step work, say so, deliver the first prompt only, and ask for its result before adjusting and continuing.
- Works in the Claude desktop app and the terminal, invoked by asking naturally, without restating these expectations each time.
- The skill is a method, not a recipe: the purpose of the prompt comes first.

## Problem

Nery's tests of prompt-writer 0.1.1 show two failures that do not depend on the prompt requested:

1. **It does the task instead of writing the prompt.** In three tests Claude delivered the output the prompt should cause (it "auto-executed" the request).
2. **It misreads which deliverable the user wants.** In the git-hygiene test it switched three times between a skill's `SKILL.md`, a prompt that builds the tool and a prompt that runs the task, and never asked which one. The same session also showed: the output frontmatter clashing with a container's own frontmatter, `{{VAR}}` used where Claude Code fills `$ARGUMENTS`, requirements dropped or added without notice, and no pattern for prompts that build something.

What the skill did add, measured against the session without it: its live research caught the obsolete `git merge-tree` form and that slash commands are now skills.

## Root causes (evidence)

| Cause | Evidence |
| :-- | :-- |
| The request reaches Claude as a fresh order after the skill body | `SKILL.md` has no `$ARGUMENTS`; Claude Code then appends "ARGUMENTS: <value>" (<https://code.claude.com/docs/en/skills#available-string-substitutions>). `.claude/rules/plugin-authoring.md` requires `$ARGUMENTS` |
| The "never do the task" rule is not at the top | `SKILL.md` opens with a persona section; the scope rule follows it. `plugin-authoring.md`: the most important instructions sit near the top |
| Research can slide into doing the task | Step 3 allows tools; "investigate the repository" is the audit itself |
| No check of the reply's shape | The self-review checks prompt quality, never whether the reply is a prompt |
| Classification covers the operation only | Classify lists new/refine/audit/migrate; nothing names the deliverable kind or what runs it; `SKILL.md` Scope presumes the container-text reading |
| Questions are not ordered by impact | Clarify caps the count but not the order |
| No requirement traceability | The checklist never compares the prompt with the user's requirements |
| Variables are fixed to `{{VARIABLE_NAME}}` | `SKILL.md` Structure and checklist |

## Requirements

Design principle (Nery, 2026-10-13): writing a prompt is interpretation and reasoning, not a procedure. The skill explains its purpose and lets Claude judge; it adds no validators, templates or mandatory blocks. A first redesign with an interpretation template, numbered-requirement checks and a build-prompt procedure was rejected as over-engineering; its re-audit found five new contradictions, all caused by that mechanics.

- **R1** The skill opens by stating its purpose: it never carries out the request; it writes, improves, audits, refines or migrates a prompt that the user runs in a different session. A request that reads like an order is what the prompt must get done there.
- **R2** No argument block: Nery chose a plain skill (purpose, steps, references) over `$ARGUMENTS` framing, overriding the `plugin-authoring.md` rule for this skill; the purpose statement at the top carries the framing.
- **R3** The prompt can be a task prompt, the text of something Claude loads, or a prompt that has Claude build one; when the request could mean more than one, Claude asks which first.
- **R4** Tools serve reading the references, verifying current facts and reading material the user points to; the only write is saving the prompt on request.
- **R5** The self-review keeps everything the user asked for and names additions in the design notes.
- **R6** A short reference, `formats-and-variables.md`, holds only what Claude cannot know by itself: that container formats change (with their official pages) and the variable syntax per filler.
- **R7** The description names the three kinds and separates "write a prompt or instructions" from "do the work now".
- **R8** No literal `$ARGUMENTS`, `$N` or `$name` text in `SKILL.md` outside the request block: Claude Code substitutes them (<https://code.claude.com/docs/en/skills>, "To include a literal `$` before a digit, `ARGUMENTS`, or a declared argument name… escape it with a backslash"). Syntax examples live in the reference.

## Evidence that it works

Pending Nery's decision: the method (headless test sessions, an eval suite, or both) and the test cases. Nothing is run or committed for testing until he approves both.

## Merged from the 0.2.0 build (zip, 2026-10-13)

The zip, built from 0.1.0 in another session, lacked the 0.1.1 fixes and the purpose statement. Taken from it: follow-up as an operation and the close-the-loop line, the triggering description, scaling steps to the request, the target-model table with `target_model` values and the closest-model rule, overwriting a saved prompt on revision, `references/lessons.md` (without Nery-specific preferences), and three verified facts (Fable 5.1 rejects sampling parameters, the Mythos 5.1 ID, start with Opus 5.5). Not taken: relative reference links, reading references after alignment, `{{VARIABLE_NAME}}` only, `surface: claude-ai`, "read only the target model's file", and the unsupported Opus 5.5 claims.

## Coherence pass (2026-10-13)

- Each rule lives in one file: emphasis, positive framing and `reasoning_extraction` stay in `prompting-principles.md` (read every time); `SKILL.md` "Rules that always apply" keeps only what the references do not say.
- The Claude Code format pages live only in `formats-and-variables.md`; `sources.md` lists the Anthropic platform pages.
- `lessons.md` gained three lessons extracted from this design session (reasoning over procedure, no invented taxonomies, precise limits), and the `SKILL.md` example is the real git-cleanup case, following the agentskills.io advice to build skills from real material.

## Out of scope

- Claude Haiku models: not part of this plugin (Nery, 2026-10-13). A request for a Haiku prompt gets the existing answer: the guidance covers four models, proceed with the general principles only?
- The deferred audit findings C2, C3, C4, C6 and C7 (duplication and portability): C4 is partly absorbed by trimming the persona; the rest stays deferred.
- Hooks that enforce the contract: skill hooks stay registered for the rest of the session (<https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents>), so a Stop gate would judge every later turn; `once: true` would drop it after the first question turn.

## Decisions

| Decision | Why |
| :-- | :-- |
| Purpose and reason stated, no procedure | "Claude is already very smart. Only add context Claude doesn't already have" (Skill authoring best practices); context and motivation help Claude "better understand your goals" (Prompting best practices) |
| Variables and formats in a reference, not `SKILL.md` | R8 forbids the literal placeholders in `SKILL.md` |
| Minor bump (0.2.0) | New capabilities (three kinds, variables per filler), backwards compatible |
