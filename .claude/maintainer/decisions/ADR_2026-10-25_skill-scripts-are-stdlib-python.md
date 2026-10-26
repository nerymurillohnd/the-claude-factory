---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Skill scripts are stdlib Python, with a tool through uv only where stdlib cannot do the job

## Scope

The scripts of this repository's project skills, first the five checks of `building-plugins` (`check-required-files.py`, `check-manifest-schema.py`, `check-mcp-schema.py`, `check-lsp-schema.py`, `check-skill-names.py`). Out of scope: the validators of `scripts/validators/`, which keep their PEP 723 inline metadata.

## Context and problem statement

The repository's validators run on Python 3.15 through uv, with `jsonschema-rs` and `pyyaml` from inline metadata. Moving their checks into `building-plugins` raised how the skill's own scripts should run. A first draft of the skill-name check rebuilt PyYAML's scalar rules by hand. How should a skill script check what stdlib cannot?

## Decision drivers

- Nery's instruction: Python scripts, pure stdlib, with `#!/usr/bin/env python3`.
- Do not complicate: if the same result can be had with what exists, do it that way; reach for more only when it is impossible otherwise.
- One source for the JSON schemas.

## Considered options

- **Stdlib, plus `uv run --with` for the one thing stdlib cannot do**: chosen. The skill-name check reads the frontmatter's `name:` line and compares it with the directory name; the three schema checks find and decode the files with stdlib and validate through `uv run --with check-jsonschema`, reading `scripts/schemas/`.
- **Rebuild YAML or JSON Schema rules in stdlib**: rejected because it is complex and error-prone where a plain comparison or an existing tool gives the same result.
- **Copy the schemas into the skill**: rejected because it makes a second copy to keep equal.

## Decision outcome

Chosen option: **Stdlib, plus `uv run --with` where stdlib cannot do the job**, because it follows Nery's instruction and keeps the scripts simple.

### Consequences

- Good, because four of the five checks need nothing but `python3`, and the schema checks catch what `claude plugin validate --strict` missed in a test on 2026-10-25 (an unknown `.mcp.json` field, a non-SemVer version, a broken `.lsp.json`).
- Bad, because the schema checks need uv on `PATH`, and the network the first time uv fetches `check-jsonschema`; without uv they exit 1 and the skill reports it instead of skipping.

## More information

Nery's words on 2026-10-25: "py scripts, stdlib puros. Con shebang #/usr/bin/env python3"; for the schemas, "puede leer, usar jq, o el mismo script invocar alguna tool que requiera via uv run --with"; and "no compliques… Expandamos a algo más cuando con lo que tenemos, si se puede hacer, sea imposible." Commits `4565c0d` and `86ad136`.
