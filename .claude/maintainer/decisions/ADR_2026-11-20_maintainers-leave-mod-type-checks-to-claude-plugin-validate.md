---
status: accepted
date: 2026-11-20
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Maintainers leave mod type checks to claude plugin validate

## Scope

The `.ts` and `.tsx` files of every mod under `plugins/`: the maintainer checks (`.claude/CLAUDE.md`, the Git pre-commit gate, Validate) and how findings on them are treated. Out of scope: the `typescript6-lsp-intelligence` plugin's post-edit hook, which ships to third-party users and stays as it is.

## Context and problem statement

Mod files are type-checked by `claude plugin validate`, which compiles a hooks module against the mod API Claude Code generates for its version; Validate runs it with `--strict` on every plugin, and DEBT-003's closure made `validate:portable` and `validate:hooks-catch` blocking too. `.claude/CLAUDE.md` also told maintainers to run `npx tsc -p plugins/<mod> --noEmit` through a `tsconfig.json` that exists only after an interactive `--plugin-dir` session, and the 2026-11-19 handoff kept open whether the 41 mod `.ts`/`.tsx` files should be type-checked anywhere else. Meanwhile the `typescript6-lsp-intelligence` post-edit hook checks each edited mod file alone against the root `tsconfig.json`, which has no mod types, and reports errors (TS2307 `claude-code`, TS1295, TS7006, TS17004) that the mod's own check does not.

Should maintainers type-check mod files with `tsc` on top of `claude plugin validate`?

## Decision drivers

- Claude Code already type-checks mods, against the API version that will load them.
- A second `tsc` check needs a tsconfig the repository does not have outside an interactive session.
- The `typescript6-lsp-intelligence` hook is built for third-party projects; changing it to suit this repository's mods would change it for its users.

## Considered options

- **Leave mod type checks to `claude plugin validate`**: chosen.
- **Type-check mods with `tsc` in the pre-commit gate or CI**: rejected because Claude Code already does it, and a separate config would duplicate and drift from the one Claude Code writes.
- **Change the `typescript6-lsp-intelligence` hook to skip mod files**: rejected because the hook is for third parties, and its noise on mod files here is the only cost.

## Decision outcome

Chosen option: **Leave mod type checks to `claude plugin validate`**, because Claude Code checks mods against the API that runs them, and no maintainer `tsc` run adds a check it lacks.

### Consequences

- Good, because one check, the one Claude Code runs, decides whether a mod's types are right.
- Bad, because the `typescript6-lsp-intelligence` post-edit hook still reports errors after each edit of a mod file in this repository; they are not findings of the mod's own check.

## More information

Nery made the decision on 2026-11-20 in the session that closed DEBT-003. `.claude/CLAUDE.md` dropped the mod `tsc` command in commit 4cabe48. Related records: DEBT-003.
