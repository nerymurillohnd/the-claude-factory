---
status: accepted
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# A schema's identity is its file location

## Scope

- In scope: every `*.schema.json` under `scripts/schemas/`, its `$id` and its `$ref`, and how a validator loads them.
- Out of scope: the `$schema` keyword of each schema, which keeps declaring draft 2020-12.

## Context and problem statement

The split schema folders (`hooks-schema/`, `marketplace-schema/`, `plugin-manifest-schema/`) each set `$id` to the file's path relative to its own folder. Two `$id` collided across folders (`plugin-manifest.schema.json`, `components/lsp-servers.schema.json`), so no validator could load the whole tree into one registry, and each folder's rules forbade a `$ref` outside it. A relative `$id` also resolves against the URI a file was loaded from, so a file-based tool would see a doubled path. How should a schema be identified so that folders can reference each other?

## Decision drivers

- One registry for the whole tree, with no collisions.
- Cross-folder references instead of copies.
- The same resolution in Python, Rust, editors and a raw GitHub URL.

## Considered options

- **No `$id` at all; identity is the file location and every `$ref` is relative to the file that holds it**: chosen.
- **`$id` relative to one common root**: rejected because each file still carries a second copy of its path to keep in sync, and the relative `$id` still resolves against the retrieval URI.
- **Absolute `$id` (a URL)**: rejected because it ties identity to a URL on `main` and needs a mapping for offline validation.

## Decision outcome

Chosen option: **no `$id`**, because nothing can drift from the location, collisions are impossible, and a relative `$ref` resolves the same way from disk, from an editor and from a raw URL.

- A validator keys its registry by each file's `file://` URI.
- Rules in `.claude/rules/schemas/` say: never declare `$id`; reach a sibling folder (`../hooks-schema/…`) instead of copying.

### Consequences

- Good, because measured: the self-check over the tree found every `$ref` resolving, no `$id` and nothing orphaned (42 files), and every real `plugin.json`, `hooks.json`, `.lsp.json`, `.mcp.json` and `marketplace.json` stayed valid.
- Bad, because moving a file means updating every `$ref` to it across all of `scripts/schemas/`.

## More information

- Decided by Nery in the session of 2026-10-24, on the proposal comparing the three identity options.
- Related: ADR_2026-10-24_one-schema-source-per-shape, ADR_2026-10-24_schemas-are-strict-on-every-known-shape, ADR_2026-10-24_schema-validators-use-jsonschema-rs.
