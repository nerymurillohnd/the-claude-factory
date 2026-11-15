# Merge the configuration branch and retire WORKFLOW.md Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One branch, `ccr-7fcd6ef3-rku7l1`, that holds both sessions' work, with `CLAUDE.md` as the single place that says which skill governs each job and `WORKFLOW.md` gone.

**Architecture:** Merge `origin/ccr-60dfcba3-fsbz16` into `ccr-7fcd6ef3-rku7l1` with a merge commit (no rebase, no force push). Take the other branch's `CLAUDE.md` and rules as the base, because they already carry the owner's "How to run this project" design. Then carry this branch's decisions into them: Biome lints all Markdown and skips only the formatting of instruction Markdown, and frontmatter values hold no colon or quotes. Move the few facts only `WORKFLOW.md` holds to their owners, then delete it.

**Tech Stack:** git, Markdown instruction files, Biome 2.6.6, the maintainer npm scripts, Claude Code 2.1.325.

**Spec:** the owner's decisions in this session (2026-11-14): `CLAUDE.md` defines once, under "How to run this project", which skill to load for each job; `WORKFLOW.md` is retired; the merge resolutions below are the ones the owner approved. Background: `origin/ccr-60dfcba3-fsbz16:.claude/session-handoff/2026-11-14-0750.md`.

## Global Constraints

- Never rebase, force push or rewrite either branch's history; merge only.
- Push, open a pull request, merge to `main` or dispatch a workflow only with the owner's explicit authorization in that turn. A stop hook never counts.
- Write files under `.claude/` with the Edit or Write tool, never through Bash. Delete `.claude/WORKFLOW.md` with `git rm`, which the owner approved in this plan.
- Biome lints every file and formats every file except the Markdown Claude reads as instructions (ADR_2026-11-14_biome-lints-all-markdown-and-skips-only-formatting-instructions). Never exclude a folder from Biome in `files.includes` to skip formatting.
- In frontmatter, a colon goes only after a field name, no value holds a colon or quotes; only a `<plugin>:<skill>` item of `skills` keeps its colon (ADR_2026-11-14_frontmatter-lint-forbids-colons-and-quotes-in-values).
- Instruction lines state the rule with no dates; dates and evidence go to memory and records.
- Load `instruction-engineering:claude-md-and-rules` before editing `CLAUDE.md` or a rule, and `project-maintainer:write-records` before writing an ADR.

## Review Focus

- After the merge, the other branch's PreToolUse guard and ask rules (`.claude/settings.json`) may prompt the owner on every edit to `.claude/CLAUDE.md`, `biome.jsonc` or `package.json`: expect prompts and wait for each answer; never route around them.
- A rule that still says "never lint" or "exclusions under `files.includes`" contradicts the Biome ADR: `grep` must find none after Task 2.
- A file, skill or rule that still names `WORKFLOW.md` or `@WORKFLOW.md` after Task 3 is a broken pointer: `grep` must find none outside records, handoffs and plans.
- The other branch's `plugin_consistency` changes and this branch's `frontmatter_lint` must both pass `npm run test:scripts` in the merged tree.
- A fact only `WORKFLOW.md` held and no task relocates is lost on deletion: Task 3's inventory must list every line with its new home or the reason it needs none.

---

### Task 1: Merge and resolve the four textual conflicts

**Files:**
- Modify: `.claude/CLAUDE.md`, `.claude/memory/MEMORY.md`, `.claude/rules/architecture/claude-dir.md`, `.claude/WORKFLOW.md` (conflicted)

**Interfaces:**
- Produces: a merge commit on `ccr-7fcd6ef3-rku7l1` whose `.claude/CLAUDE.md` and rules are the other branch's, plus this branch's memory line.

- [ ] **Step 1: Fetch and check both branches are clean**

Run: `git fetch origin && git status --porcelain && git log --oneline -1 origin/ccr-60dfcba3-fsbz16`
Expected: no output from `status`; HEAD of the other branch is `2409033`, or a newer commit to read first.

- [ ] **Step 2: Merge without committing**

Run: `git merge --no-commit --no-ff origin/ccr-60dfcba3-fsbz16`
Expected: conflicts in exactly `.claude/CLAUDE.md`, `.claude/WORKFLOW.md`, `.claude/memory/MEMORY.md`, `.claude/rules/architecture/claude-dir.md`.

- [ ] **Step 3: Resolve `.claude/CLAUDE.md`**

Keep the other branch's side, the `### GitHub and CI` heading. Drop this branch's Tooling block: its lines live in the other branch's `.claude/rules/npm-and-uv.md`, and its Biome line moves to `.claude/rules/code-quality/markdown.md` in Task 2.

- [ ] **Step 4: Resolve `.claude/memory/MEMORY.md`**

Keep both index lines, this branch's `frontmatter-values-without-colons-or-quotes.md` line first, then `rule-paths-bare-names-match-every-folder.md`.

- [ ] **Step 5: Resolve `.claude/rules/architecture/claude-dir.md`**

Keep the other branch's side. This branch's two unique lines are carried elsewhere: the Biome override line goes to `markdown.md` (Task 2), and "run `npm run lint:skills` after changing a skill" is already in the other branch's `.claude/rules/skills.md`.

- [ ] **Step 6: Resolve `.claude/WORKFLOW.md`**

Keep the other branch's side, which drops the `labels:sync` line. Task 3 deletes the file after its facts are relocated.

- [ ] **Step 7: Check no marker is left, then commit the merge**

Run: `git diff --check && ! grep -rn '^<<<<<<<\|^>>>>>>>' .claude`
Expected: no output.

```bash
git add .claude/CLAUDE.md .claude/memory/MEMORY.md .claude/rules/architecture/claude-dir.md .claude/WORKFLOW.md
git commit -m "Merge ccr-60dfcba3-fsbz16 into ccr-7fcd6ef3-rku7l1"
```

The message body says which side each conflict kept and why, as Steps 3 to 6 do.

### Task 2: Carry the Biome and frontmatter decisions into the merged rules

**Files:**
- Modify: `.claude/rules/code-quality/markdown.md:8-10`, `.claude/CLAUDE.md:23` (the Stack line)

**Interfaces:**
- Consumes: the merged tree from Task 1.

- [ ] **Step 1: Confirm the contradictions are present**

Run: `grep -n -E 'Never format or lint|exclusions under .files.includes.' .claude/rules/code-quality/markdown.md; grep -n 'Markdown written for people' .claude/CLAUDE.md`
Expected: three hits.

- [ ] **Step 2: Rewrite the two Markdown rule lines**

In `markdown.md`, replace "Never format or lint the Markdown Claude reads as instructions …" with "Never format the Markdown Claude reads as instructions (…same list…); Biome still lints it." Replace the `files.includes` line with "Add each new `.claude/` folder of instruction Markdown as a `*.md` pattern to the first `overrides` entry of `biome.jsonc`; never exclude a folder in `files.includes`." Add the line "Run `npm run lint:frontmatter -- <file>` after each edit of a skill's, agent's or command's frontmatter."

- [ ] **Step 3: Rewrite the Stack line of `CLAUDE.md`**

"**Formatting and linting:** Biome for TypeScript, JavaScript, JSON, YAML and Markdown, formatting all but the Markdown Claude reads as instructions; ruff for Python; shfmt and ShellCheck for shell."

- [ ] **Step 4: Verify**

Run: `grep -rn -E 'Never format or lint|exclusions under .files.includes.|Markdown written for people' .claude/CLAUDE.md .claude/rules`
Expected: no output.
Run the instruction checker: `python3 <instruction-engineering skill dir>/scripts/check_instructions.py --project . --no-user`
Expected: `0 error(s)`.

- [ ] **Step 5: Commit**

```bash
git add .claude/rules/code-quality/markdown.md .claude/CLAUDE.md
git commit -m "docs(rules): carry the Biome lint and frontmatter decisions into the merged rules"
```

### Task 3: Relocate WORKFLOW.md's own facts and delete it

**Files:**
- Modify: `.claude/skills/plugin-releases/SKILL.md` (step 1), `.claude/skills/plugin-catalog-changes/SKILL.md` ("How Claude Code handles it"), `.claude/CLAUDE.md` ("How to run this project" › Plugins)
- Delete: `.claude/WORKFLOW.md`

**Interfaces:**
- Consumes: the merged tree from Tasks 1 and 2.

- [ ] **Step 1: Inventory every WORKFLOW.md line against its home**

For each command line, `grep` the merged `.claude/skills`, `.claude/rules`, `.claude/CLAUDE.md` and `package.json`, and write a table in the commit body: line, home found, or relocation. Known results, re-check each:
  - `npm run release:notes` has no home: Step 2.
  - `claude plugin marketplace remove` has no home: Step 3.
  - Stage 10 eval lines: `.claude/rules/plugins/evals.md` holds the smoke form and the billing note, but loads only with eval files: Step 4.
  - `claude plugin init` writes only to `~/.claude/skills/`: already in `.claude/rules/plugins.md:16`.
  - "Report each `lint:skills` defect to the owner": already in `.claude/rules/skills.md`.
  - "outside `validate`/`lint` while DEBT-003/DEBT-005 is open": already in those entries of `pending-debt.md`.
  - Every `claude plugin …` command and flag: owned by `plugin-engineering:cli-commands-guide`, which `CLAUDE.md` names.
  - Every `npm run …` line: `package.json`, which `npm run` lists.

- [ ] **Step 2: Add `release:notes` to `plugin-releases` step 1**

New bullet: "`npm run release:notes -- <plugin>` prints the GitHub Release body `release.yml` will publish, and `-- --tag` the tag name; run both for every plugin whose version has no tag, and stop on a failure, because `release.yml` stops at the first one."

- [ ] **Step 3: Add `marketplace remove` to `plugin-catalog-changes`**

New bullet under "How Claude Code handles it (official)": "`claude plugin marketplace remove <name>` uninstalls every plugin from that marketplace and deletes their options, secrets and data." Check the wording against `claude plugin marketplace remove --help` first.

- [ ] **Step 4: Add the evals line to `CLAUDE.md`**

Under "How to run this project" › Plugins: "For a plugin's evals, load and use `plugin-evals:plugin-evals`, and follow `.claude/rules/plugins/evals.md`: every case bills the owner."

- [ ] **Step 5: Delete WORKFLOW.md and check no pointer is left**

Run: `git rm .claude/WORKFLOW.md && git grep -n 'WORKFLOW\.md' -- . ':!.claude/session-handoff' ':!.claude/maintainer/plans' ':!.claude/maintainer/decisions' ':!CHANGELOG.md'`
Expected: no output from `git grep`.

- [ ] **Step 6: Lint the two skills**

Run: `npm run lint:skills -- .claude/skills/plugin-releases` and `npm run lint:skills -- .claude/skills/plugin-catalog-changes`
Expected: no new finding compared with the same command on the merge commit; report any finding to the owner, one question per rule id.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/plugin-releases/SKILL.md .claude/skills/plugin-catalog-changes/SKILL.md .claude/CLAUDE.md
git commit -m "docs(claude): retire WORKFLOW.md after moving its own facts to their skills"
```

### Task 4: Record the retirement

**Files:**
- Create: `.claude/maintainer/decisions/ADR_2026-11-14_claude-md-names-the-skill-for-each-job-and-workflow-md-retires.md`

- [ ] **Step 1: Search for an existing record**

Run: `grep -ril -E 'WORKFLOW|How to run this project' .claude/maintainer/decisions/`
Expected: no ADR on this decision; if one exists, supersede it instead.

- [ ] **Step 2: Write the ADR with `project-maintainer:write-records`**

Status `accepted`, decision-maker "Nery (project owner)". Context: `WORKFLOW.md` was created (ed180b8), removed into a CLAUDE.md Workflow section (30eb294), re-created by #104 (ced195b), retired and restored unreferenced on the other branch (ff28e21, f9153a2). Chosen: `CLAUDE.md` names the skill for each job once; skills own their commands; `WORKFLOW.md` is deleted. Rejected: keeping a command catalog beside the skills, because it duplicates them and drifts.

- [ ] **Step 3: Commit**

```bash
git add .claude/maintainer/decisions/ADR_2026-11-14_claude-md-names-the-skill-for-each-job-and-workflow-md-retires.md
git commit -m "docs(records): record that CLAUDE.md names each job's skill and WORKFLOW.md retires"
```

### Task 5: Verify the merged branch

- [ ] **Step 1: Run every maintainer check**

Run, one at a time, and keep the raw output for the owner:
`npm run test:scripts`, `npm run lint:python`, `npm run typecheck:python`, `npm run validate:claude`, `npm run check:consistency -- --offline`, `npm run lint:frontmatter`, `npx biome check --error-on-warnings --max-diagnostics=none --reporter=summary .`, and the instruction checker.
Expected:
- tests OK;
- ruff and basedpyright with 0 errors;
- `√ Validation passed`;
- `check:consistency` exit 0;
- `lint:frontmatter` with the 16 DEBT-005 findings and no new one;
- Biome with only the DEBT-006 findings, and any new one from the other branch's files listed;
- the checker with `0 error(s)`.

- [ ] **Step 2: Report and ask**

Show the owner the outputs, the commits since `a494ce0`, and the other branch's open items this branch now resolves:
- 9: the `release.yml` fix;
- 27: DEBT-006;
- 7: `autoMemoryDirectory`, decided there.

Then ask for authorization to push `ccr-7fcd6ef3-rku7l1` and to open one pull request to `main` with `github-operations:auto-pr-lifecycle`.

## Out of scope

These stay open and are listed for the owner:
- The other branch's open items 2, 3, 4, 6, 7, 8, 14 and 15.
- The labels fixes (1) to (5).
- The `biome.jsonc` citations of three ADRs deleted in ced195b, now at lines 392, 420 and 421.
- Spec section 6 "reuse first".
- DEBT-003, DEBT-005 and DEBT-006.
