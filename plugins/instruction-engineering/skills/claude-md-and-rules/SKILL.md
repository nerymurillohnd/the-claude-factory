---
name: claude-md-and-rules
description: Required before creating or changing any Claude Code instruction file (CLAUDE.md, CLAUDE.local.md, ~/.claude/CLAUDE.md, .claude/rules/**/*.md), even a one-line addition, because every change must be checked against the whole instruction set first. Also use it to review, audit, debug, reorganize or refactor these files; whenever the user wants a behavior persisted ("remember this", "make sure this doesn't happen again", "Claude keeps doing X", "make it stop"), including before configuring a hook for it, to find why the written instruction failed; when a rule is ignored or not loading; or when they mention project or global instructions or memory files. Finds contradictions, semantic duplicates, ambiguity, no-op and misplaced lines and procedures that should be skills; decides CLAUDE.md vs always-on or path-scoped rules vs skill vs hook; includes a read-only checker. Not for writing skills, hooks, settings, READMEs or one-off prompts, except to recommend them.
compatibility: Claude Code or Cowork. The checker needs python3 3.12+; git is optional.
---

# Instruction files

Claude Code instruction files are context, not configuration. Every file that loads is concatenated into the conversation; nothing overrides anything, conflicts are resolved arbitrarily, and nothing in prose is enforced. The work is to keep the fewest, truest, most concrete lines in the place that loads exactly when they are needed, to cut what Claude would do anyway, and to move what must never bend into hooks, permission rules or settings.

Loader details (what loads when, glob bases, size limits, AGENTS.md interplay) change between releases and differ from most blog posts and generators. They are in [references/loading-semantics.md](references/loading-semantics.md), checked against the docs and changelog through Claude Code v2.1.312 on 2026-10-28. Read it before stating how loading works; when `claude --version` is newer, check the changelog for `CLAUDE.md`, `rules` and `paths` entries after v2.1.312. Never answer loader questions from memory.

## Standing behavior: read, understand, act, surface

This applies to every request, from "add one line" to a full audit, and it is what the user relies on this skill for. They should never have to ask for it.

1. **Read the effective set first.** Every file that loads alongside the one in question (user scope, ancestors, root, CLAUDE.local.md, always-on and relevant scoped rules, nested files, imports, AGENTS.md), plus the repository facts the instructions talk about. Run the checker.
2. **Understand it as one document.** Compare across files by subject: contradictions, semantic duplicates, diverging details, ambiguity, scope mismatches, stale facts, procedures, fought-over lines, lines that change nothing because Claude already behaves that way, and instructions that sit at the wrong level (personal rules in a project, a project rule repeating a user-level rule, team rules copied across repositories that a shared linked rules directory or a plugin would serve better).
3. **Do what was asked**, in the right place and without creating a duplicate or contradiction.
4. **Surface what you found**, even outside the request, in a short "Noticed while doing this" section: each item with its evidence and a recommendation. Offer the fix; do not apply changes the user did not ask for. The user has the last word, especially on deletions.
5. **Route every finding through its reference before you write it.** This summary is not enough to recommend a fix: the references carry the caveats a correct recommendation depends on (which procedures must be user-invoked only, why a rule with `paths` linked from outside the working directory never loads, why a deny rule would also block new migrations, which lines Claude Code already makes redundant). Open the reference for each kind of finding the first time it appears, even when the finding itself seems obvious (list under "How to use these references").

Scale the depth: a one-line addition gets a focused read of the subjects it touches and a short noticed list (with an offer of a full audit when the set looks unhealthy); a review or audit gets the full cross-file analysis.

## Core facts to hold in every task

- **Load timing**: CLAUDE.md and CLAUDE.local.md in the working directory and above, `~/.claude/CLAUDE.md`, unscoped rules in the `.claude/rules/` of the launch directory and of every directory above it, and in `~/.claude/rules/`, and all their `@imports` load at launch. Subdirectory CLAUDE.md files, rules in a subdirectory's own `.claude/rules/`, and rules with `paths` load on demand when Claude reads, writes or edits a matching file. Most subagents receive the same files. Explore and Plan start with none of them, managed policy files and project rules included; agents with `omitClaudeMd` keep only the managed policy files. In all three, a subdirectory's CLAUDE.md and matching scoped rules still load when they touch files there. Rules with `paths` also load on a single-file Bash read (`cat`, `head`, `tail`, `sed -n`, `grep`).
- **Rules frontmatter**: `paths` is the only field read. Other keys (`globs`, `alwaysApply`, `description`, `priority`) are ignored silently. Invalid YAML makes the rule load in every session; an unquoted glob starting with `*`, `{` or `[` is a common cause, so quote globs. Folder names do not scope rules. `.md` backups inside `.claude/rules/` load too.
- **Glob base**: project rule patterns are relative to the directory holding the rule's `.claude` folder; user rule patterns to the session's working directory. `*.md` is root-only; use `**` to recurse.
- **Size**: under 200 lines per CLAUDE.md is guidance, not truncation; on-demand files (and their imports) are cut at 40,000 characters on a 200K window (150,000 on current 1M-window models); a CLAUDE.md over 4 MiB is skipped. Imports never save context.
- **Placement by applicability**: conventions for one area or file type belong in a rule with `paths`, however short, so they load with the files they govern; what is needed in most tasks or before files are chosen stays in CLAUDE.md.
- **Enforcement**: a zero-exception rule belongs in a hook (a `command` hook blocks with exit 2) or a `permissions.deny` rule; prose only informs, and emphasis does not enforce.

## Route the request

| Situation | Read and follow |
| :-- | :-- |
| Any write or edit, including "add this to CLAUDE.md" or "remember X" | [references/writing-guide.md](references/writing-guide.md): the pre-write protocol at the top, then the writing rules |
| Deciding where something belongs; what Claude would do anyway | [references/placement.md](references/placement.md) |
| Review or audit of CLAUDE.md and/or rules | [references/audit-and-refactor.md](references/audit-and-refactor.md), [references/cross-file-analysis.md](references/cross-file-analysis.md) and [references/rules-architecture.md](references/rules-architecture.md) (where each instruction belongs, always-on versus `paths`) |
| Saturated CLAUDE.md, refactor, CLAUDE.md vs rules, organizing rules, always-on vs `paths`, sharing rules across projects (user-level rules, symlinked shared rules, plugins) | [references/rules-architecture.md](references/rules-architecture.md) |
| "Claude keeps doing X", "make sure this doesn't happen again", persisting a correction | [references/escalation.md](references/escalation.md) |
| Steps, runbooks, checklists or repeated workflows in instruction files | [references/procedures-to-skills.md](references/procedures-to-skills.md) |
| Layout (bullets, numbered steps, tables, prose), imports versus pointers, pointers between rules, brace globs | [references/format-and-links.md](references/format-and-links.md) |
| How or when something loads; debugging a rule that doesn't apply | [references/loading-semantics.md](references/loading-semantics.md) |

Most real requests touch several rows; read each that applies.

### How to use these references

- Read a reference in full (each is under 200 lines) the first time its situation applies, and before you write the part of the answer that depends on it. Do not read it in fragments or rely on its title.
- Do not read every reference up front. Start with the rows the request names, then re-route as evidence appears: a contradiction or duplicate found while writing sends you to cross-file-analysis.md; a numbered procedure to procedures-to-skills.md; a fought-over or zero-exception rule to escalation.md; a loader question (frontmatter, globs, timing, size) to loading-semantics.md; a saturated file or a CLAUDE.md-versus-rules decision to rules-architecture.md.
- Keep going after the first finding. The analysis is complete when every file in the comparison set has been read and every kind of problem you report has gone through its reference.
- The checker ends its report with the references its findings need ("Read before reporting"); read those before you write about the findings.
- Before sending the reply, check each kind of finding in it against this list and read any reference you have not read in this session; then revise the finding with what it says (the references hold the fix patterns, the caveats and what to ask the user):
  - contradiction, duplicate, ambiguity, scope mismatch, no-op line → cross-file-analysis.md and placement.md;
  - procedure, checklist, repeated workflow → procedures-to-skills.md;
  - repeated misbehavior, emphasis, enforcement → escalation.md;
  - what stays in CLAUDE.md, rules organization, always-on vs `paths`, sharing across repositories → rules-architecture.md;
  - imports, pointers between files, tables and list formats, brace globs → format-and-links.md;
  - frontmatter, globs, load timing, size → loading-semantics.md.
- For a large set or a substantial refactor, a fresh-context review by the `instruction-engineering:reviewer` agent (when available) checks your result without inheriting your reasoning.

## Workflow

### 1. Identify the operation and the scope

Operation: write, edit, review or audit (read-only until approved), debug, reorganize, refactor, persist a correction. Scope: user (`~/.claude/` or `$CLAUDE_CONFIG_DIR`; affects every repository; get explicit approval and keep a copy before changing it), project (shared through git), local (CLAUDE.local.md), subtree, file type. If the deliverable is truly ambiguous (report vs edited files, which scope), ask once; otherwise proceed and state the interpretation.

### 2. Gather the effective set and the ground truth

Run the checker for a deterministic inventory and findings (read-only; python3 3.12+):

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check_instructions.py" --project <repo root>
```

`${CLAUDE_SKILL_DIR}` is the directory that contains this SKILL.md. `--match <file> ...` lists which scoped rules would load for given files (positive and negative scope tests); `--json` gives structured output; `--no-user` skips `~/.claude`; `--user-dir <dir>` points at another configuration directory. Errors are loader facts; warnings and the heuristic findings (near-duplicates, conflicting choices, procedures, scope candidates, generic lines, layout trees, style lines a formatter config already enforces, prohibitions without an alternative) are leads to confirm by reading. The checker cannot judge meaning: the cross-file analysis is yours.

### 3. Decide placement before wording

Apply the admission test in placement.md, starting with the counterfactual (would Claude act differently without this line?). Open the classification rubric in rules-architecture.md when the home is not obvious from placement.md, or when the change is structural. A procedure goes to a skill, a zero-exception rule to a hook or deny rule (proposed), personal content to CLAUDE.local.md or user scope, and no-op content nowhere.

### 4. Write, reorganize or refactor

Follow the pre-write protocol and writing rules in writing-guide.md. For structural work, present the target structure, the keep / migrate / delete table and the always-loaded footprint before and after (rules-architecture.md section 5); apply directly only when the user asked for the change itself. Every rule file gets a quoted `paths` list or a deliberate decision to stay always-on, and each glob is checked with `--match` against a file that should load it and one that should not.

Files under `.claude/` (all rules) are protected paths. In default and `acceptEdits` modes each write prompts (the prompt offers to allow the folder for the session); in auto mode the classifier decides; in `dontAsk` the write is denied; allow rules do not pre-approve it. Group rule writes so the user can approve the folder once. When a write is denied, do not route around it (no shell redirection, no copies elsewhere): deliver the target structure plus every new or changed file's complete content, ready to apply, and say that nothing under `.claude/` changed.

### 5. Verify and report

- Re-run the checker on the final set after any change; explain any remaining error. Re-read each changed file in full.
- Give the session checks the tools here cannot run: `/context` after a fresh launch, a `Loaded` line or an InstructionsLoaded hook for scoped rules, `claude --debug` for parse errors, optionally `/doctor prompt-audit` (v2.1.283+).
- Report: what changed and why; what was kept, moved, merged or removed (traceability); checker result before and after; what was verified and how, and what was not; recommended mechanism changes not applied (skills, hooks, deny rules, settings); and "Noticed while doing this".
- Never claim an instruction "will be followed" or "is loaded" without evidence; say what would show it.

## Boundaries

- Do not change settings, hooks, permissions, skills or source code as a side effect. Recommend them with the reason and an exact sketch; create them only when asked or approved.
- Do not delete instructions the user did not ask to remove; recommend it with the reason.
- Do not put secrets, credentials or customer data in any instruction file, including CLAUDE.local.md.
- Do not adopt a generator's score, line cap or invented frontmatter as a requirement; the official loader behavior and the user's tasks decide.
- When a request is weaker than an alternative (a stack mandate in user scope, an IMPORTANT line for a rule that keeps being broken, a duplicate of a rule that already exists), say so in one sentence, recommend the stronger option, then do what was asked unless it would add a contradiction or duplicate or leak private content into a shared file.
