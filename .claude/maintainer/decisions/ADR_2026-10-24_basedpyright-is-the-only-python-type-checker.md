---
status: superseded
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: ADR_2026-10-27_basedpyright-checks-everything-in-all-mode
---

# Basedpyright is the only Python type checker; Mypy is not used

## Scope

- In scope: the type checking of maintainer Python (`scripts/`) and plugin Python (`plugins/`), the `mypy-scripts` and `mypy-plugins` gates of `scripts/gates.mjs`, the Python post-edit commands in `.claude/CLAUDE.md` → Quality gates, and `.claude/rules/maintainer-tooling.md` and `.claude/rules/plugin-tooling.md`.
- Out of scope: Ruff, which stays the linter and formatter, and JavaScript and TypeScript, which `tsc` checks.

## Context and problem statement

Python was checked by both `mypy --strict` and Basedpyright. Running two checkers costs a tool, a gate and a second dialect of diagnostics. Does Mypy add defects that the rest of the stack misses?

## Decision drivers

- Rigor: an unvalidated value must not pass silently.
- One authority for diagnostics, in the CLI gate, with the editor and hooks as views of it.
- No tool without a concrete requirement.

## Considered options

- **Basedpyright alone, with Ruff `ALL`**: chosen.
- **Basedpyright and Mypy**: rejected because Mypy's extra diagnostics were policy checks or inference limitations, not defects the stack misses (measured below).

## Decision outcome

Chosen option: **Basedpyright alone**, because it was the stricter checker on the case that matters (data with no type) and its measured gaps are closed by Ruff or are not defects.

- Maintainer code: `typeCheckingMode = "all"` and `failOnWarnings = true`, scoped to maintainer paths.
- Plugin code: the default `recommended` mode.
- A second checker needs an ADR that classifies each diagnostic it adds as an implementation defect, a policy check or an inference limitation, and justifies it only by documented defects.
- Existing code and gates migrate when a task touches them, as `.claude/CLAUDE.md` → Migration says; until then the Mypy gates keep running and must pass.

### Consequences

- Good, because one checker gives one set of diagnostics and one configuration per scope.
- Bad, because a private function whose body is only `...` passes Basedpyright, which treats such a body as a placeholder (`checker.ts`, v1.40.2, `isSuiteEmpty`); `.claude/rules/maintainer-tooling.md` forbids placeholder bodies outside stubs, protocols, overloads and abstract methods, and tests catch it at run time.

## Pros and cons of the options

### Basedpyright alone

Measured on 2026-10-24 with Basedpyright 1.40.2, Mypy 2.4.0 and Python 3.15.0:

- Good, because a JSON value annotated without validation (`data: dict[str, str] = json.loads(...)`) fails Basedpyright (`reportAny`) and passes Mypy.
- Neutral, because a public function whose body is a docstring plus `...` is caught by Ruff `PIE790`, and the body that remains then fails Basedpyright `reportReturnType`.
- Bad, because the private `def _f() -> int: ...` passes Ruff and Basedpyright.

### Basedpyright and Mypy

- Good, because Mypy flags the private `...` body (`empty-body`).
- Neutral, because Mypy's `func-returns-value` (using a `None` result) is a policy check; pyright does not special-case `None` by design (basedpyright docs, "mypy comparison").
- Bad, because Mypy's error on a literal kept in a tuple is a false positive: pyright keeps the literal and the assignment is valid.

## More information

- Decided by Nery in the session of 2026-10-24.
- Related: ADR_2026-10-21_gates-run-installed-tools (Basedpyright and Ruff still run as installed, by bare name).
