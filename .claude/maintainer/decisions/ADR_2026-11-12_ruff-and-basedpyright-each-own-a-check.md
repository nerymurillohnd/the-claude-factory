---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Give each Python check one owner: basedpyright or Ruff

## Scope

The `ignore` list in `ruff.toml` and the `report*` settings in `pyrightconfig.json`.

## Context and problem statement

Ruff runs with `select = ["ALL"]` and basedpyright with `typeCheckingMode: "all"`, so both reported some of the same problems. A test on the same file showed Ruff F401 and basedpyright `reportUnusedImport` on the same line. The restored `ruff.toml` also missed duplicates (ISC002, F811, F822, N804, N805, SLF001, PLE0604), ignored rules basedpyright does not fully cover (UP035 misses `typing.Callable` and the `collections.abc` moves), and named the wrong counterparts (ANN401 maps to `reportExplicitAny`, RUF013 to `reportArgumentType`).

## Decision drivers

- No diagnostic reported twice.
- No check left without an owner.
- The owner is the tool with the wider or type-aware coverage.

## Considered options

- **basedpyright owns the type-aware checks and Ruff ignores its copies; Ruff owns the lint checks both report and basedpyright turns its copies off**: chosen.
- **Leave both tools fully on**: rejected because duplicate diagnostics and duplicate suppressions.

## Decision outcome

Chosen option: **one owner per check**, because each problem is then reported once, by the tool that covers it best.

| Check | Owner | Turned off in the other tool |
| --- | --- | --- |
| Parameter annotations, `Any`, implicit Optional, index types, `__all__`, redefinitions, `self`/`cls` names, private access, implicit string concatenation | basedpyright | Ruff ignores ANN001-003, ANN401, RUF013, RUF016, PLE0604, PLE0605, F822, F811, N804, N805, SLF001, ISC001, ISC002, ISC004 |
| Unused imports, variables, expressions and parameters; undefined names; escape sequences; assert-always-true; call defaults; ignore comments; wildcard imports; deprecated typing spellings | Ruff | basedpyright sets the matching `report*` rules to `none` and `deprecateTypingAliases` to `false` |
| Formatter conflicts (W191, E111, E114, E117, D206, D300, Q000-Q004, COM812, COM819) | Ruff formatter | Ruff's linter ignores them, per Ruff's "Conflicting lint rules" list |

### Consequences

- Good, because `npm run lint:python` passes with one report per problem.
- Bad, because the checks basedpyright gave up now depend on Ruff running in CI and in the editor.
- Bad, because `select = ["ALL"]` turns on every rule a new Ruff minor stabilizes; `required-version = ">=0.17.4,<0.18"` makes each minor upgrade a deliberate review.

## More information

- Sources: `astral-sh/ruff` docs at tag 0.17.4 (`docs/linter.md`, `docs/formatter.md`, CHANGELOG); `DetachHead/basedpyright` docs at tag v1.40.2 (`docs/configuration/config-files.md`); paired fixtures run through both tools.
- Unverified: whether basedpyright shows per-overload docstrings on hover, the reason the old config gave for ignoring D418.
- Commits: 3211a2d, 7fc7def.
