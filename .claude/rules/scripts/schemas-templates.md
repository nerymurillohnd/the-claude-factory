---
paths:
  - "scripts/schemas/**"
  - ".claude-plugin/marketplace.json"
  - "plugins/*/.claude-plugin/plugin.json"
  - "plugins/*/.mcp.json"
  - "plugins/*/.lsp.json"
  - "plugins/*/hooks/hooks.json"
---

# JSON Schemas

- A field its schema in `scripts/schemas/` lacks fails `npm run validate` and the commit; add it to the schema from the official docs instead of dropping it.
- Define each shape once in its folder and `$ref` it from the others; a copy is a defect (ADR_2026-10-24_one-schema-source-per-shape).
- Keep `additionalProperties: false` on every known-shape object, because `claude plugin validate` lets unknown keys through (ADR_2026-10-24_schemas-are-strict-on-every-known-shape).
- Record a valid and an invalid case in `scripts/tests/schemas/cases.json` for each schema change.
- No validator covers `hooks.json`; only `scripts/tests/run_pytest.py scripts/tests/schemas` checks it.
- After a change, run `npm run validate` and `scripts/tests/run_pytest.py scripts/tests/schemas`.
