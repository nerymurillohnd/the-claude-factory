# Skill checklist

The single list of what a finished skill must meet. Every audit report maps its findings onto these items, and every item has exactly one owner: one of the three validation scripts, one of the four reviewers, the cold executor, or the evals. An owner of `evals` means no static audit can show the item; the audit report marks it "not assessed by this audit" and names the evaluation in [evaluation.md](evaluation.md) that would.

Strength labels and source tags are defined in [evidence-and-verdict.md](evidence-and-verdict.md). The area file named in each section holds the rule in full.

## Contents

- [How to read an item](#how-to-read-an-item)
- [Frontmatter and description](#frontmatter-and-description)
- [Body and structure](#body-and-structure)
- [Scripts](#scripts)
- [Claude Code features](#claude-code-features)
- [Testing](#testing)
- [Security](#security)
- [Surfaces](#surfaces)
- [Executability](#executability)
- [Owners at a glance](#owners-at-a-glance)

## How to read an item

`ID` · the condition the skill must meet · sources · strength · owner.

Owners: `check-metadata`, `check-structure`, `check-runtime` (the scripts), `description-reviewer`, `instructions-reviewer`, `scripts-runtime-reviewer`, `security-reviewer`, `cold-executor`, `evals`. A script may also report a lead on an item a reviewer owns; the reviewer confirms or rejects it.

## Frontmatter and description

Area files: [frontmatter.md](frontmatter.md), [description.md](description.md).

- `FM-1` · `name` and `description` meet the limits of every surface the skill targets · \[AS\]\[PL\]\[CC\] · `req` · check-metadata
- `FM-2` · Only the six standard fields when the skill also ships to claude.ai or the API · \[CC\] · `req` · check-metadata
- `FM-3` · The description says what and when, includes the users' key terms, is specific, and puts the main use case first · \[PL\]\[AS\]\[CC\] · `rec` · description-reviewer
- `FM-4` · The frontmatter starts on line 1 and parses · \[CC\]\[AS\] · `req` · check-metadata
- `FM-5` · No strict-YAML trap in a plain value; `metadata` is a map · \[SD\]\[CC\] · `spec` · check-metadata
- `FM-6` · No combination of fields that disables the skill · \[CC\] · `req` · check-metadata
- `FM-7` · The description doesn't summarize the procedure and covers every capability the body offers · \[SD\] · `default` · description-reviewer
- `FM-8` · Who may invoke the skill fits what it does · \[CC\] · `rec` · description-reviewer

## Body and structure

Area files: [body-and-structure.md](body-and-structure.md), [workflows.md](workflows.md).

- `BS-1` · `SKILL.md` is under 500 lines and every reference file is linked directly from `SKILL.md`, one level deep · \[PL\]\[AS\]\[CC\] · `rec` · check-structure
- `BS-2` · Each file Claude reads is linked with a relative Markdown link and the condition for reading it · \[PL\]\[AS\]\[CC\] · `rec` · instructions-reviewer
- `BS-3` · No `${CLAUDE_SKILL_DIR}` inside a Markdown link · \[CP\] · `default` · check-structure
- `BS-4` · In a plugin skill, `${CLAUDE_SKILL_DIR}` names the skill's own folder and the path after it is relative to the skill · \[CC\] · `req` · check-runtime
- `BS-5` · Only what the agent lacks; one default per choice with an escape hatch; a Gotchas section · \[AS\] · `rec` · instructions-reviewer
- `BS-6` · One term per concept; no time-sensitive text outside an "Old patterns" section · \[PL\] · `rec` · instructions-reviewer
- `BS-7` · Concrete examples and output templates where the output has a required form · \[PL\]\[AS\] · `rec` · instructions-reviewer
- `BS-8` · Workflows have clear steps, a checklist when steps depend on each other or have validation gates, a validation loop for quality-critical work, and a completion condition · \[PL\]\[AS\]\[SD\] · `rec` · instructions-reviewer
- `BS-9` · Forward slashes only; reference files over 100 lines open with a table of contents whose entries match headings · \[PL\] · `rec` · check-structure
- `BS-10` · Rules that must always hold are hooks, not prose · \[CC\] · `rec` · instructions-reviewer
- `BS-11` · Every local link and pointer resolves, and no file in the skill is unused (`evals/` exempt) · \[SD\] · `req` · check-structure
- `BS-12` · A skill with side effects states what it authorizes; a forked or preloaded skill states its input and single output and never asks · \[SD\] · `rec` · instructions-reviewer
- `BS-13` · The blocks of `SKILL.md` follow the recommended order, and no rule first appears after the step it governs · \[CC\]\[AS\]\[PL\] · `default` · instructions-reviewer

## Scripts

Area file: [scripts.md](scripts.md).

- `SC-1` · Scripts handle errors themselves, with specific messages; no unexplained constants · \[PL\] · `rec` · scripts-runtime-reviewer
- `SC-2` · No interactive prompts; `--help`; structured stdout and diagnostics on stderr; bounded output; idempotent, with `--dry-run` for destructive operations · \[AS\] · `rec` · scripts-runtime-reviewer
- `SC-3` · Required packages and interpreters are listed and available on the target surfaces · \[PL\] · `req` · scripts-runtime-reviewer
- `SC-4` · Whether to run or read each script is explicit · \[PL\] · `rec` · scripts-runtime-reviewer
- `SC-5` · Critical operations have a validation or verification step · \[PL\] · `rec` · scripts-runtime-reviewer
- `SC-6` · A script whose output Claude needs exits 0 and reports problems inside its output · \[CC\]\[SD\] · `req` · scripts-runtime-reviewer
- `SC-7` · Scripts are called through `${CLAUDE_SKILL_DIR}` in Claude Code, or through their interpreter with a relative path for uploads and the API · \[CC\]\[CP\]\[SD\] · `req` · check-runtime
- `SC-8` · Scripts are called with their interpreter as a prefix; a skill that runs one directly says so and pre-approves that exact form · \[CC\]\[CP\] · `default` · check-runtime
- `SC-9` · Every script has a `#!/usr/bin/env <interpreter>` line and the executable bit · \[SD\] · `default` · check-structure

## Claude Code features

Area file: [claude-code-features.md](claude-code-features.md).

- `CF-1` · Every `arguments` name is used as `$name`; a literal `$` before a digit, `ARGUMENTS` or a declared argument name is escaped with one backslash · \[CC\]\[SD\] · `req` · check-runtime
- `CF-2` · `allowed-tools` names exact commands · \[SD\] · `rec` · scripts-runtime-reviewer
- `CF-3` · Every `Bash()` pattern in `allowed-tools` matches the whole command line the body runs, interpreter prefix included · \[CP\] · `req` · check-runtime
- `CF-4` · No argument placeholder inside a `!` command · \[SD\] · `observed` · check-runtime
- `CF-5` · A fork has an explicit task; on Explore or Plan it states every rule it needs · \[CC\] · `req` · scripts-runtime-reviewer
- `CF-6` · Hook commands in the frontmatter use the plugin or project root, are quoted or in exec form, and don't rely on `onFailure` on `Stop`-type events · \[CC\] · `req` · check-runtime
- `CF-7` · Every command that uses `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_PLUGIN_DATA}` is written in `SKILL.md`, not in a file it links to · \[CC\]\[SD\] · `req` · scripts-runtime-reviewer
- `CF-8` · A skill that runs other agents fits the way it runs them to the official comparison, and no pre-approved command depends on running after a subagent's result · \[CC\]\[SD\] · `req` · scripts-runtime-reviewer

## Testing

Area file: [evaluation.md](evaluation.md).

- `TE-1` · At least three evaluations, with a no-skill baseline · \[PL\]\[AS\] · `rec` · evals
- `TE-2` · A trigger eval with should and should-not queries and a train/validation split · \[AS\] · `rec` · evals
- `TE-3` · Tested with every model the skill will run on · \[PL\] · `rec` · evals
- `TE-4` · Tested on real usage in a fresh session; feedback incorporated · \[PL\]\[CC\] · `rec` · evals

## Security

Area file: [security.md](security.md).

- `SE-1` · Every bundled file is free of network calls, file access and operations outside the stated purpose · \[PL\] · `req` · security-reviewer
- `SE-2` · Content fetched from external URLs is treated as untrusted · \[PL\] · `req` · security-reviewer
- `SE-3` · No reads of credentials or history, no data sent out, and no action the description doesn't announce · \[SD\] · `req` · security-reviewer
- `SE-4` · No over-broad pre-approval in `allowed-tools` and no shell injection through a `!` command · \[SD\] · `rec` · security-reviewer

## Surfaces

Area file: [surfaces.md](surfaces.md).

- `SU-1` · Nothing an instruction depends on is skipped by a surface the skill reaches; a plugin skill says what it does without its agents and hooks in chat · \[CC\]\[CP\] · `req` · description-reviewer
- `SU-2` · A plugin skill that reaches chat keeps every file it reads or runs inside its own folder and names references by paths relative to `SKILL.md` · \[CP\] · `req` · check-structure

## Executability

Method file: [executability-trace.md](executability-trace.md).

- `EX-1` · A model can follow every workflow and every variant that changes the output from trigger to completion without guessing · \[SD\] · `req` · cold-executor

## Owners at a glance

| Owner | Items |
| --- | --- |
| check-metadata | FM-1, FM-2, FM-4, FM-5, FM-6 |
| check-structure | BS-1, BS-3, BS-9, BS-11, SC-9, SU-2 |
| check-runtime | BS-4, SC-7, SC-8, CF-1, CF-3, CF-4, CF-6 |
| description-reviewer | FM-3, FM-7, FM-8, SU-1 |
| instructions-reviewer | BS-2, BS-5, BS-6, BS-7, BS-8, BS-10, BS-12, BS-13 |
| scripts-runtime-reviewer | SC-1, SC-2, SC-3, SC-4, SC-5, SC-6, CF-2, CF-5, CF-7, CF-8 |
| security-reviewer | SE-1, SE-2, SE-3, SE-4 |
| cold-executor | EX-1 |
| evals | TE-1, TE-2, TE-3, TE-4 |
