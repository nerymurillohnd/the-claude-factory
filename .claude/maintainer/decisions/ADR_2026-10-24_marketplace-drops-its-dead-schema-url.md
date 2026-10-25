---
status: accepted
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The marketplace drops its dead `$schema` URL

## Scope

- In scope: the `$schema` key of `.claude-plugin/marketplace.json` and the `check-repo.mjs` check that required it.
- Out of scope: the schemas, which keep allowing `$schema` because the docs list it.

## Context and problem statement

`marketplace.json` carried `"$schema": "https://anthropic.com/claude-code/marketplace.schema.json"`, which returns 404, and `check-repo.mjs` failed the repository without it. The docs describe `$schema` as an optional URL "for editor autocomplete. Ignored at load time" (`/en/plugins/marketplace-reference#top-level-fields`), and none of their file examples need it. Keep it, point it elsewhere, or drop it?

## Decision drivers

- No requirement for a field Claude Code ignores.
- No public URL that leads nowhere.

## Considered options

- **Drop the key and the check**: chosen.
- **Point it at this repository's raw schema on `main`**: rejected for now; it would publish a URL tied to `main` for an editor convenience nobody asked for.
- **Keep it**: rejected because the URL gives no autocomplete and the check enforces a dead link.

## Decision outcome

Chosen option: **drop both**, because the field is optional, ignored at load time, and its URL was dead.

### Consequences

- Good, because measured: `check-repo.mjs`, `marketplace-json-schema.py` and `claude plugin validate --strict .` pass without the key.
- Bad, because editors lose nothing today, but would need a working URL to autocomplete `marketplace.json` later.

## More information

- Decided by Nery in the session of 2026-10-24.
