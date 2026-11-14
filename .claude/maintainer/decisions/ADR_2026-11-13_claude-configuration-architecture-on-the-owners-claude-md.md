---
status: superseded
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: ADR_2026-11-13_claude-configuration-architecture
superseded-by: ADR_2026-11-14_claude-md-names-the-skill-for-each-job-and-workflow-md-retires
---

# The Claude configuration architecture, with the owner's CLAUDE.md draft as the project CLAUDE.md

## Scope

How this repository organizes Claude's own configuration in the maintainer scope:
- `.claude/CLAUDE.md` and `.claude/WORKFLOW.md`;
- `.claude/rules/`, `.claude/skills/`, `.claude/agents/`;
- `.claude/references/`, `.claude/templates/` and `.claude/architecture/`;
- `.claude/settings.json` (plugins, permissions and hooks).

Out of scope: the content of each plugin under `plugins/`, CI workflows, and the owner's user-level settings.

## Context and problem statement

ADR_2026-11-13_claude-configuration-architecture accepted the target architecture of `.claude/maintainer/plans/2026-11-13-claude-architecture-proposal.md`. Its CLAUDE.md part composed a new file of about 100 lines from the old CLAUDE.md and the owner's draft (`.claude/architecture/CLAUDE.draft.md`), and dropped the draft's stack table and repository map as discoverable.

The owner then stated that the draft is the replacement being built for CLAUDE.md, not one input among others. The owner chose to:
- add the old file's Commitment, Repository memory and Verification sections to the draft;
- promote it as `.claude/CLAUDE.md`;
- delete the old file and the drafts that had reached their place.

An independent review of the promoted file (the `instruction-engineering:reviewer` agent) found that the promotion lost or broke these things, and the owner approved the seven fixes:
- the planning-time pointer to `.claude/rules/plugins.md`;
- the path to the stage commands in `.claude/WORKFLOW.md`;
- parts of the pull request policy;
- three stale cross-references;
- a false line saying the full eval suite runs in CI;
- the reason not to run `./<file>.py`.

## Decision drivers

- The owner's draft is the intended CLAUDE.md, and the owner decides its content.
- No instruction of the old CLAUDE.md is lost without the owner deciding so.
- Every other decision of the earlier architecture still holds.

## Considered options

- **Promote the owner's draft as CLAUDE.md, with the three sections and the seven review fixes, and keep the rest of the earlier architecture**: chosen.
- **Compose a new CLAUDE.md of about 100 lines, as the earlier ADR set**: rejected by the owner. The draft is the owner's design for the file, stack table and repository map included.

## Decision outcome

Chosen option: **the owner's draft becomes `.claude/CLAUDE.md`**, because it is the file the owner designed to replace the old one. The three added sections and the fixes keep every instruction the owner did not decide to drop.

### What is now in place

- **The file itself:** `.claude/CLAUDE.md` is the draft plus three sections copied verbatim from the old file (Commitment, Repository memory, Verification), plus the review fixes:
  - the pointer to `.claude/rules/plugins.md`, under Scopes;
  - a line under Main commands that points to `.claude/WORKFLOW.md`, which is no longer imported;
  - the pull request policy: owner approval, "unless the owner asks for one" for documentation-only plugin changes, and skill, agent and command files counted as components;
  - the CI line: in CI, plugins get only `claude plugin validate` and their evals.
- **Rule adopted from the drafts:** `.claude/rules/npm-and-uv.md`, adopted unchanged and then extended:
  - it also loads for `.claude/hooks/**`;
  - it now says never to run `./<file>.py`.
- **Rules fixed:**
  - `hook-scripts.md` points Python hooks to `npm-and-uv.md`;
  - `plugins.md` names the "Scopes" heading;
  - `claude-dir.md` says CLAUDE.md points to WORKFLOW.md without importing it, and takes WORKFLOW.md's rule that every `lint:skills` defect goes to the owner before it is fixed or recorded as debt.
- **Drafts deleted:** `.claude/architecture/CLAUDE.draft.md`, `.claude/architecture/rules/npm-and-uv.md` and `.claude/architecture/rules/plugins.md`. The last one was already absorbed into `.claude/rules/plugins.md` by migration step 2.

### What carries over unchanged from ADR_2026-11-13_claude-configuration-architecture

- One home per kind of content, and path rules for area conventions.
- The `plugin-lifecycle` skill, which takes over WORKFLOW.md's stage catalog and the orphaned templates; one skill, not two.
- The `plugin-release-reviewer` agent (Opus, read-only).
- The skill gate hooks.
- The `permissions.ask` and `permissions.deny` rules.
- Six synced plugins turned off in this repository.
- Maintainer changes in plain cloud sessions or the terminal, not in Claude Projects threads.
- D3 (CHANGELOG-only changes take no bump), D4 (no repository change for `skill-diagnostics`), D5 (memory, step 7) and D6 (the CI line).

### Consequences

- Good, because the owner's own design is in force, and the old file's instructions survive or were dropped by the owner's choice.
- Good, because the always-loaded instructions shrink from 256 to about 180 lines, since WORKFLOW.md is no longer imported.
- Bad, because the CLAUDE.md target of about 100 lines is abandoned: the stack table, the repository map, the Testing section and the command tables stay always-on.
- Bad, because the stage commands are reachable only through a pointer until the `plugin-lifecycle` skill exists.

## More information

- **Decided:** by the owner on 2026-11-13: promote the draft with the three sections, delete the old file and the drafts that reached their place, then apply the seven fixes of the independent review.
- **Supersedes:** ADR_2026-11-13_claude-configuration-architecture.
- **Left open, as the review reported:**
  - the old CLAUDE.md lines 7, 8, 14, 16, 17, 32 and 35 survive only in part (account type, the surface-naming instruction, "only contributors", the full list of Claude's duties, AI reviewers "only review", "may rely on their tools, accounts and setup", "never applies to the other");
  - the old plugin-testing clause "with the plugin's own testing methods, in isolated environments that do not depend on the maintainer's tools or versions" is gone, and it bears on where tests of plugin hooks live;
  - `npm-and-uv.md` says no plugin needs npm, while `tailwind-development` ships npm runtime dependencies;
  - the routing table of the proposal is not written yet.
