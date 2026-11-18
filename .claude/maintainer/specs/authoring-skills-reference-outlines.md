# authoring-skills: reference outlines

The planned contents of each reference file, for the owner's approval before writing. Every section teaches a decision: when to use something, when not to, why, and how, with one correct and one incorrect example where seeing them changes the result. Requirement numbers point to `authoring-skills-requirements.md`.

## Contents

- Shared shape of every reference
- skill-types.md
- name-and-description.md
- structure.md
- components.md
- scripts-and-hooks.md
- writing-instructions.md
- task-mechanisms.md
- environment.md
- intent.md
- sources.md
- validation.md
- Coverage of the owner's list (O14)

## Shared shape of every reference

- A one-line statement of what the file teaches, then a table of contents when over 100 lines.
- Sections in the order the model needs them while working.
- Each section: the decision, the criterion with its reason, then how to apply it, then a short correct and incorrect pair only where it changes the result.
- Facts state their surface and version where they depend on one, and the source page to check when in doubt.
- No restatement of SKILL.md, of another reference, or of what the model already knows.

## skill-types.md

Read before choosing the location, fields, name and layout (phase 3). Requirements 2, 3.

1. Identify the type: location (enterprise, personal, project, nested, additional directory, plugin `skills/`, plugin root, skill folder as plugin, command file) and surfaces (Claude Code local or cloud, Cowork, claude.ai, Claude API, Managed Agents, other clients); one skill can be several.
2. What each location loads and where it doesn't (cloud, Cowork, project threads), precedence, reserved names and refused characters.
3. Frontmatter fields: the full Claude Code set, what each does, its valid values, and the decision for each (when to set it, when to leave it out); the six portable fields and the upload rejections.
4. Invocation: the default, `disable-model-invocation`, `user-invocable`; which to choose for side effects, background knowledge, preloading and scheduled tasks.
5. Skills run by subagents: `context: fork` (needs a task, no history, background tool set, `agent`, `background`) versus preloading through a subagent's `skills` (reference beside the task, 32-name limit, no `disable-model-invocation`), and what changes in the body for each.
6. Arguments and substitutions: `$ARGUMENTS`, indexed and named placeholders, escaping, the `CLAUDE_` variables and where each resolves.
7. Body features by surface: injected commands, `@` references and substitutions in Claude Code, synced skills, claude.ai and the API.
8. Layout per type, including the command file and the plugin-root `SKILL.md`, with a correct and incorrect example per type.

## name-and-description.md

Read before writing the name and the description (phase 3 for the name, phase 4 for the description). Requirement 4.

1. Choosing the name: the rules per surface, then the guidance (gerund, noun phrase, action form; consistency with sibling skills; what to avoid), proposed to the requester.
2. What the description is for: the only text the model sees before choosing; what it must carry (what it does, when to use it, the users' words, requests that never name the domain, the boundary with near-misses and sibling skills).
3. Point of view and phrasing: third-person capabilities plus "Use when"; no workflow summary.
4. Length by surface: 1,024 characters for uploads and the spec (rejected above it); the Claude Code listing cut at 1,536 by default, configurable, and the listing budget; no defect in a long description under the limit that applies.
5. `when_to_use`: when it helps, and why it fails outside Claude Code.
6. Angle brackets and placeholders.
7. Testing triggering: realistic should-trigger and near-miss queries, runs, threshold, train and validation split, no keywords copied from failures.
8. Correct and incorrect examples: vague, missing triggers, mechanics instead of intent, overlapping a sibling.

## structure.md

Read before planning the files (phase 4). Requirement 5.

1. The basic structure: `SKILL.md` alone is enough; when a skill grows into supporting files.
2. What goes where: `references/` (documentation the model reads), `scripts/` (code it runs), `assets/` (files used in the output: templates, data, images); root-level guides in capitals (`FORMS.md`, `REFERENCE.md`) and when a root file beats a `references/` file; descriptive file names; organizing by domain or variant.
3. Progressive disclosure as a design decision: what every run needs stays in the body; split by access pattern, not by size; when bundling large material is free and when it isn't (uploads).
4. Building the reference block in `SKILL.md`: one pointer per line at the step that needs it, a Markdown link, the verb by use (read, run, fill in, copy), the condition, what the file holds; correct and incorrect pointers, including links buried in paragraphs, generic "see references/", nested chains and `@` references.
5. Inside a reference: one level deep, a table of contents above 100 lines, forward slashes and paths from the skill root, link spelling that matches file names exactly.
6. Size budgets: the body under 500 lines and 5,000 tokens; what persists after compaction; what to move out first.
7. Files that don't belong in a skill folder, such as a README.

## components.md

Read before adding a reference, asset, `allowed-tools` entry, subagent preload, or another skill or MCP tool (phase 3). Requirements 6, 11.

1. Is a skill the right feature: skill versus CLAUDE.md, rule, hook, subagent, MCP server, output style; the criteria and what to tell the requester when it isn't a skill.
2. The component inventory and the question each one answers: references, scripts, assets, hooks, `allowed-tools`, `disallowed-tools`, MCP tools, other skills, subagents, setup configuration, memory in plugin data.
3. Tool permissions: when `allowed-tools` earns its place, the narrowest rule, and why it grants and never restricts.
4. MCP tools: fully qualified names, stating the dependency, what to do when the server isn't connected.
5. Composing with other skills: invoking by the exact name, `disable-model-invocation` on the target, stacking limits, plugin dependencies.
6. Setup and memory: a config file the model fills by asking once; persistent state in plugin data, never next to the code.
7. Security and least surprise: credentials, network, writes outside stated paths, external URLs.

## scripts-and-hooks.md

Read before writing a script, a hook, an injected shell command, or a shell command that uses a path variable (phase 5). Requirement 7.

1. When a script earns its place (deterministic, repeated, fragile) and when instructions are better; run versus read.
2. Where a script lives and what breaks: in the skill folder (travels everywhere), at the plugin level (shared, lost when the skill travels alone), in `bin/` (on PATH), in the user's project (project variable), outside the plugin (not copied to the cache, symlink rules); with a correct and incorrect example for each.
3. Reaching the script: the path variables, where they resolve, quoting, and the matching `allowed-tools` rule.
4. The interface the model meets: no prompts, `--help`, error messages, exit codes, structured stdout and stderr, idempotency, dry run, bounded output.
5. Dependencies and portability: pinned one-off commands, inline dependencies, what each surface provides, POSIX shells, Windows through Git Bash.
6. Injected commands: when to inject, the inline and fenced forms, failure aborting the invocation, `|| true`, permissions, synced and other surfaces.
7. Hooks in a skill: on-demand hooks, lifetime, `once`, the locks and limits, plugin `hooks/hooks.json` versus frontmatter hooks.

## writing-instructions.md

Read before designing the body (phase 4). Requirements 1, 9.

1. What earns a line: the test, what the model lacks, starting from real expertise; correct and incorrect pairs.
2. Reference content versus task content, and how each is written.
3. Freedom matched to fragility; defaults, not menus; procedures over declarations.
4. Matching the form to the failure: a discipline skipped under pressure, output in the wrong shape, a missing element, behavior that depends on a condition.
5. Register: imperative, one action per line with its condition and fallback, the reason only where it decides an unnamed case, no narration, no emphasis by capitals, positive instructions over prohibition lists.
6. Examples and snippets: when an example earns its place, input and output pairs, the rule line that says what to imitate, commands with pinned versions and explained placeholders, inline versus file; correct and incorrect.
7. Anti-patterns, each with a correct and incorrect pair: general knowledge, catch-all phrases, menus, time-sensitive wording, one term for two concepts, duplicated facts, rules after the step they govern, standing guidance written as a single step.
8. Writing from the model's seat: the walk through the description, body and files, and what to rewrite.

## task-mechanisms.md

Read when the task of the skill you write has ordered steps, a step whose failure later steps depend on, a fixed output format, or destructive actions (phase 4). Requirement 8.

1. Recognize the task: reference, workflow, output-producing, destructive or remote; most skills mix parts.
2. Workflows: when a marked sequence earns its place, when goals and criteria are better, gates and decision points, splitting large variants into files.
3. Checklists: progress checklist versus final verification checklist; when each is needed and when it is noise; how to build each so it fails when the work is wrong.
4. Validation loops: when, which validator (script, reference document, self-check with stated criteria), the fix branch, the gate and the exit.
5. Plan, validate, execute: for batch, destructive and high-stakes work.
6. Output templates: when, strict or flexible, inline or in `assets/`, placeholders that say what goes there.
7. Gotchas: what qualifies, where they go, growing them from corrections.
8. Task tracking and planning: what to rely on and what not to require.
9. How the mechanisms fit together, and the smallest set the task needs.

## environment.md

Read when you have no shell, you are outside Claude Code, or the skill you write targets another surface (phase 1). Requirements 2, O6.

1. Recognizing the surface and session you are in, and what it lets you save, run and test.
2. Your session versus the target session: what a check here proves and what stays unverified.
3. Inventorying existing skills, instructions, hooks, subagents and MCP servers safely, without reading setting values or credentials.
4. Working where no one can answer.

## intent.md

Read when the request is vague, covers several skills, or must be extracted from a conversation (phase 2). Requirements O8, 1.

1. Disentangling a request: what is asked, what lies behind it, what it implies.
2. Extracting a skill from a conversation or from project artifacts.
3. Use cases and success criteria the model can check.
4. Context questions versus design questions, with examples; when to ask and when to proceed.
5. Requests that hold several skills, and requests that aren't a skill.

## sources.md

Read before looking up any platform fact (phase 3). Requirements 12, O10, O15.

1. The official sources and what each one settles: Agent Skills, Claude Platform, Claude Code Docs, Anthropic's guide, Claude Academy, the changelog.
2. How to read them: full pages, the Markdown versions, the installed version and its release notes.
3. Settling disagreements by surface, with the known disagreements.
4. Recording facts and marking those from the changelog or the binary.

## validation.md

Read before running any check (phase 6). Requirement 10.

1. Mechanical checks: `claude plugin validate`, `skills-ref validate`, upload rules, links and paths.
2. The reread from the model's seat, and what to look for.
3. Behavior checks: use cases in a fresh session, with and without the skill, the models its users run.
4. Trigger checks: queries, runs, threshold.
5. Evals: skill-creator's format versus `claude plugin eval`, assertions that discriminate, reading transcripts.
6. Reporting what was verified and what wasn't.

## Coverage of the owner's list (O14)

- Every frontmatter field by type: skill-types.md 3, 4, 5.
- Name guidance: name-and-description.md 1.
- Description guidance: name-and-description.md 2-8.
- Embedding examples, command snippets, references and templates: writing-instructions.md 6; structure.md 4; task-mechanisms.md 6.
- Basic structure and what goes in `references/`, `scripts/`, `assets/`: structure.md 1, 2.
- Uppercase documents at the skill root: structure.md 2.
- Anti-patterns with correct and incorrect examples: writing-instructions.md 7; structure.md 4.
- When to use checklists, validation loops, workflows, scripts: task-mechanisms.md 2-5; scripts-and-hooks.md 1.
- Script placement in the skill, a subfolder, or outside it in a plugin: scripts-and-hooks.md 2.
- How a subagent skill differs: skill-types.md 5.
- Prioritizing progressive disclosure: structure.md 3, 6.
- How the reference block in `SKILL.md` is built: structure.md 4.
