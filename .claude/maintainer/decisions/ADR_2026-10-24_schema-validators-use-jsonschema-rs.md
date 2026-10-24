---
status: accepted
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Schema validators use jsonschema-rs

## Scope

- In scope: the JSON Schema library of `scripts/validators/lsp-json-schema.py`, `mcp-json-schema.py`, `plugin-json-schema.py` and `marketplace-json-schema.py`, and how they resolve `$ref` across `scripts/schemas/`.
- Out of scope: the schemas themselves, `scripts/tests/run_pytest.py` and its tests, the gates and CI.

## Context and problem statement

The four validators check plugin files against `scripts/schemas/`, whose files reference each other with relative `$ref` and declare no `$id`. They used `jsonschema` with `referencing` and `rfc3986-validator`, five packages with `attrs` and `rpds-py`, and their messages for an `anyOf` failure only said "is not valid under any of the given schemas". Which library should validate them?

## Decision drivers

- Verdicts must not change: the schemas are the contract.
- Few dependencies, typed for basedpyright in all mode.
- Messages that name the real cause inside an `anyOf` or `oneOf`.
- Validation must never reach the network.

## Considered options

- **jsonschema-rs with an explicit registry and `offline=True`**: chosen.
- **`jsonschema` + `referencing` + `rfc3986-validator`**: rejected because it needs five packages for what one does, and its `anyOf` messages hide the cause.
- **jsonschema-rs resolving `$ref` by itself from the entry schema's `base_uri`, without a registry**: rejected because that needs retrieval on, and then a `$ref` to `https://` would be fetched. With `offline=True` it cannot read `file://` either.

## Decision outcome

Chosen option: **jsonschema-rs, a `Registry` of every `scripts/schemas/` file keyed by its file URI, and `validator_for(..., base_uri=..., registry=..., validate_formats=True, offline=True)`**, because it keeps the verdicts, needs one package with no runtime dependencies, ships type stubs, checks `format: uri` itself, and exposes the branches of an `anyOf`/`oneOf` failure.

- A failure inside `anyOf` or `oneOf` is reported from the branch closest to passing (fewest errors, then the deepest), and within it the deepest error.
- The four scripts declare `dependencies = ["jsonschema-rs"]` and keep the uv shebang (ADR_2026-10-24_maintainer-python-shebang-follows-its-dependencies).

### Consequences

- Good, because measured: 107 instances (the 74 cases of `scripts/tests/schemas/cases.json` and 33 real repository files) gave 0 verdict differences against `jsonschema`.
- Good, because measured: 27 probes on throwaway copies gave the same exit code and the same file and JSON path as the previous scripts; the inline hook with an invented `onFailre` key now reports `Additional properties are not allowed ('onFailre' was unexpected)` instead of "is not valid under any of the given schemas".
- Good, because measured: a remote `$ref` added to a schema fails with "Default retriever does not fetch resources"; nothing is fetched.
- Good, because ruff and basedpyright in all mode pass against `uv python find --script`.
- Bad, because jsonschema-rs is pre-1.0 (0.60.1): its API can change between releases, and the dependency is not pinned.
- Bad, because `pattern` runs on its Rust regex engine, not Python's `re`; parity holds for today's schemas and must be rechecked when a schema adds a pattern.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Verdicts equal `jsonschema` on the recorded cases and real files | The parity run of the session of 2026-10-24 | 107/107 equal | When a schema adds a `pattern` or jsonschema-rs changes minor version |

## More information

- Decided by Nery in the session of 2026-10-24, from the plan "move the four schema validators to jsonschema-rs".
