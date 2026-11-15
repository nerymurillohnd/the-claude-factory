---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# CLAUDE.md states each stack area's basics and points to the rule that holds its guidelines

## Scope

The `## Stack` section of `.claude/CLAUDE.md` and the rules it points to in `.claude/rules/`:
- `npm-and-uv.md`
- `linting.md` (new)
- `plugins.md`
- `architecture/github.md`
- `testing.md` (new, takes the former `## Testing` section of `CLAUDE.md`)
- `skills.md` (new, adopts the draft `.claude/architecture/rules/skill-references.md`)

Out of scope: the other `CLAUDE.md` sections (Repository map, Main commands, Cloud sessions) and the plugins' own files.

## Context and problem statement

The Stack section described "two stacks that never mix". It mixed tools with how to use them, and the Testing section kept every testing guideline always loaded. The owner found that this framing confused maintenance work with plugin work, and that path-scoped rules only load once Claude touches a matching file. Without a pointer, Claude may never learn that a rule exists for the task at hand.

How should `CLAUDE.md` and the rules share the stack knowledge so that Claude always knows what applies, without the guidelines sitting in every session?

## Decision drivers

- Claude knows which rule governs a task before it opens the files that would load that rule.
- `CLAUDE.md` keeps the basics; the how lives in one rule per topic, which loads with its files.
- The maintainer/plugin split stays in one place: Scopes, in `CLAUDE.md`.
- Pointers follow the official guidance and the `instruction-engineering` skill: name the task that should make Claude read the rule ("Before X, read Y"), not a bare "See Y".

## Considered options

- **Stack by area (Maintenance, Plugins, CI/CD and GitHub, Testing, Skills), each area ending with a "Before <task>, read <rule>" pointer, and the guidelines moved into one rule per topic**: chosen.
- **Keep the two-stacks framing and the always-loaded Testing section**: rejected because it restates the Scopes rule and keeps every testing guideline in every session.
- **Bare "See <rule>" pointers**: rejected because a pointer without a trigger gives Claude no moment to follow it.

## Decision outcome

Chosen option: **Stack by area with a trigger pointer per area**, because Claude learns at launch which rule covers each kind of work, and the rule's content loads only when the work starts.

What changed:
- `CLAUDE.md`:
  - Stack has five areas, each ending with its pointer.
  - The plugins.md pointer moved from Scopes to Stack › Plugins.
  - The `## Testing` section moved to `testing.md`.
- New rules:
  - `testing.md`: plugins, command hooks, mods, and local versus CI.
  - `linting.md`: the file type → formatter, linter and type checker → npm script map, and the finding policy.
  - `skills.md`: project skills versus plugin skills, naming other skills, and the checks. It took the `lint:skills` line from `claude-dir.md` and the "no scripts in a project skill" line.
- Changed rules:
  - `npm-and-uv.md`:
    - Node 26 LTS and npm 12;
    - `.nvmrc` kept equal to the machine's Node;
    - npm 12 installed globally;
    - the user-wide uv tools, and the Python tools not to use;
    - a correction: the root manifests serve only the maintainer, while a plugin declares its own runtime dependencies.
  - `plugins.md`: rewritten as imperatives.
  - `hook-scripts.md` and `scripts.md`: lint lines and the hook piping test moved to `linting.md` and `testing.md`.
- Root files in `paths` are anchored with a leading `/`, and `claude-dir.md` states both conventions: anchoring and the pointer from `CLAUDE.md`.

### Consequences

- Good, because each area of work names its rule at launch, and the guidelines load only with their files.
- Good, because the root globs no longer load a rule for a same-named file in another folder. Two cases this fixes:
  - `plugins/tailwind-development/package.json` loaded `npm-and-uv.md`;
  - `.claude/references/README.md` loaded `plugins.md` and `categories.md`.
- Bad, because `CLAUDE.md` grows from 180 to about 190 lines: the Skills list and the pointers outweigh the removed Testing section.
- Bad, because the `instruction-engineering` checker (plugin 0.1.3) predates the documented glob semantics: it reports every `/`-anchored pattern as matching nothing.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| A pattern without `/` matches the name in every folder; a leading `/` anchors it to the root | InstructionsLoaded hook trace with `claude -p` on Claude Code 2.1.323: `sub/README.md` loaded the `"README.md"` and `"*.md"` rules, not `"/README.md"`; the root `README.md` loaded all three | passed, 2026-11-13 | After a Claude Code release that mentions rule `paths` |
| Each rule loads for its files and not for others | InstructionsLoaded trace in this repository:<br>- `plugins/tailwind-development/package.json` loads `plugins.md` and `testing.md`, not `npm-and-uv.md`<br>- `.nvmrc` loads `npm-and-uv.md`<br>- `biome.jsonc` loads `linting.md`<br>- a project skill loads `skills.md` and `claude-dir.md`<br>- `.claude/references/README.md` loads only `claude-dir.md`<br>- root `CHANGELOG.md` and `README.md` load `plugins.md` and `categories.md` | passed, 2026-11-13 | When a rule's `paths` change |
| `.claude` validates | `npm run validate:claude` | passed, 2026-11-13 | Each change under `.claude/` |

## More information

- Decided by the owner on 2026-11-13: CLAUDE.md keeps the basics, and each area points to its rule to reinforce what path scoping already does.
- Sources:
  - [How Claude remembers your project: Path-specific rules](https://code.claude.com/docs/en/memory#path-specific-rules) documents `*.md` as "`.md` files anywhere under the base directory" and `/*.md` as "directly in the base directory";
  - [Best practices: Keep CLAUDE.md short](https://code.claude.com/docs/en/best-practices#keep-claude-md-short).
- Related:
  - ADR_2026-11-13_claude-configuration-architecture-on-the-owners-claude-md, whose CLAUDE.md this changes;
  - ADR_2026-11-13_plugin-command-hook-tests-ship-in-the-plugin;
  - ADR_2026-11-13_checks-run-fast-locally-and-in-full-in-ci.
