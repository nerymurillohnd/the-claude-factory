---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# YAML checks compose ruamel.yaml nodes and report FILE:LINE:COLUMN

## Scope

- `plugins/github-operations/skills/github/scripts/check-forms.py`, the only script this decision changes now.
- The rule for any later script in this repository that reads YAML to check rules a schema misses.
- Out of scope now: `scripts/validators/skill-names-consistency.py` and the full removal of PyYAML from the repository, logged as DEBT-041.

## Context and problem statement

`check-forms.py` validated GitHub issue and discussion forms with check-jsonschema's built-in schemas and read the YAML a second time with a PyYAML `SafeLoader` subclass to find what the schemas miss, chiefly an unquoted `Yes`, `No` or `On` that GitHub reads as a boolean (YAML 1.1). check-jsonschema already installs ruamel.yaml, so the script's uv environment held two YAML parsers, and its findings carried no position. Which YAML reader should such a check use, and how should it report?

## Decision drivers

- One YAML engine per environment: PyYAML next to check-jsonschema's ruamel.yaml is redundant (Nery).
- Every finding at its source position, in the `file:line:column: message` form compilers and linters use, which a GitHub Actions problem matcher can read once a workflow registers it (`::add-matcher::`).
- The structural check (the official SchemaStore schema) and the complementary rules run as two decoupled phases.
- Basedpyright in `all` mode with no suppression.

## Considered options

- **ruamel.yaml `compose()` in YAML 1.1 mode, rules checked on the node tree**: chosen.
- **PyYAML `SafeLoader` subclass with a bool constructor (the 0.5.0 draft)**: rejected; a second YAML engine, and positions only for booleans.
- **ruamel.yaml with a custom bool constructor**: rejected; it gives the text and position of booleans only, while nodes give them for every rule.
- **python-frontmatter with pydantic**: rejected; forms are whole YAML files, not frontmatter, python-frontmatter depends on PyYAML, and pydantic would copy the schema SchemaStore maintains and sees `Yes` only after it became `True`.

## Decision outcome

Chosen option: **ruamel.yaml `compose()` in YAML 1.1 mode**, because one engine gives every node its resolved tag (`bool` or `str`), its text as written and its `start_mark`, so booleans, duplicate ids and labels, the reserved `None` option and invalid keys all report as `FILE:LINE:COLUMN: message` with no constructor or subclass.

- PEP 723 metadata: `ruamel.yaml>=0.18.10` (check-jsonschema 0.36.0's own minimum, declared, not inherited) and `check-jsonschema>=0.36.0` (the first release with `vendor.github-discussion`; 0.34.0 added the issue form and config schemas); shebang `#!/usr/bin/env -S uv run --script`.
- ruamel.yaml declares no types on nodes and errors: the script reads each attribute through a typed `attrgetter` binding and narrows the value with a real check.
- check-jsonschema's own errors are passed on unchanged; they carry a JSON path, not a line.

### Consequences

- Good, because the environment holds one YAML parser and every complementary finding has a position.
- Bad, because ruamel.yaml's untyped API needs typed getters, about a dozen lines that PyYAML's bundled stubs would not.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| ruamel 1.1 resolves `Yes`, `no`, `true`, `On` as `bool` and keeps the text and position | prototype runs on ruamel.yaml 0.19.1 | pass, 2026-10-29 | a ruamel.yaml major release |
| check-jsonschema below 0.36.0 lacks `vendor.github-discussion` | `--help` of 0.29.0 to 0.38.0 | 0.34.0 adds issue forms and config, 0.36.0 adds discussions | never |
| Findings read `FILE:LINE:COLUMN` | `scripts/testers/github-operations/test_scripts.py` `CheckForms` | pass, 2026-10-29 | each change to the script |
| Type check clean without suppression | `basedpyright-plugins:` gate | pass, 2026-10-29 | each change to the script |
