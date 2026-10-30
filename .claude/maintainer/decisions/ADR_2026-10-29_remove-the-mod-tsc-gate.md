---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Remove the mod-tsc gate

## Scope

The `mod-tsc:<plugin>` gates of `scripts/gates.mjs`, their `npm run typecheck` and `typecheck:ts` selectors, and the setup step and gate blocker added in commits `a72f7ed` and `b7593ce`. The `mod-test:<plugin>` (`claude plugin test`) and `claude-validate:<plugin>` gates are out of scope and stay.

## Context and problem statement

`mod-tsc` ran `tsc -p plugins/<mod>/tsconfig.json`. That tsconfig extends `.claude-plugin/types/tsconfig.json`, which Claude Code writes only when an interactive session loads the mod with `--plugin-dir`, pinned to the build that wrote it, and git-ignores. A new worktree had none, so the pre-push hook failed. Copying them from the main checkout (`a72f7ed`) spread declarations from an older build (2.1.310 against an installed 2.1.314). Should the pre-push gates type-check mods against these declarations at all?

## Decision drivers

- A gate must tell Nery something true about his installed build, and users' compatibility comes only from the README's declared minimum.
- `claude plugin validate` runs the engine's own static analysis of the hooks module, and `claude plugin test` runs the mod inside the installed binary; neither needs declarations.
- A push must not depend on an artifact only an interactive session can write.

## Considered options

- **Remove the gate**: chosen.
- **Move the type check to one maintainer tsconfig outside `plugins/`, non-blocking**: rejected, because it still depends on declarations from one build and adds no check that validate and test lack.
- **Keep the gate and copy the declarations into new worktrees**: rejected, because the copies come from whatever build last wrote them, so the gate checks stale declarations.

## Decision outcome

Chosen option: **Remove the gate**, because validate and test already check each mod against the installed engine, and the gate only added a stale-artifact failure.

### Consequences

- Good, because a fresh worktree pushes after `npm ci` and `npm run setup`.
- Good, because no check depends on a generated, build-pinned file.
- Bad, because no tool now reports a TypeScript type error in a mod's hooks or tests before the push unless validate or test trips on it; `tsc` against a fresh `--plugin-dir` session remains available as an editor aid.

## More information

Decided by Nery on 2026-10-29, after the live-sources audit `.claude/maintainer/audits/2026-10-29-plugins-and-mods-live-sources-audit.md` (F6.9, F7.4, F8.1 to F8.5). Implemented in commit `4a7e467`, which reverts `a72f7ed` and `b7593ce`. The "mods' `tsc`" row of ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure no longer applies.
