---
paths:
  - "scripts/schemas/marketplace-schema/**/*.schema.json"
---

# Marketplace schema

`scripts/schemas/marketplace-schema/` is the source of truth for `.claude-plugin/marketplace.json` and for what only a marketplace entry has (`source`, `category`, `tags`, `strict`, `relevance`, `headers`, `headersHelper`), JSON Schema draft 2020-12, 13 files. Edit the files directly; nothing generates them.

## Entry points
- `marketplace.schema.json`: the whole catalog, also one served from a URL.
- `plugin-entry.schema.json`: one element of `plugins[]`.
- `sources/plugin-source.schema.json`: one plugin `source` value.

## Structure
- `marketplace.schema.json` holds the envelope and points `plugins[].items` to `plugin-entry.schema.json`.
- `plugin-entry.schema.json` delegates to:
  - `sources/plugin-source.schema.json`, a `oneOf` of 8 forms: relative-path and bare-name as strings, and github, url, git-subdir, npm, archive and command selected by their `source` const;
  - `relevance.schema.json`;
  - `../hooks-schema/hooks-config.schema.json` for `hooks`;
  - `../plugin-manifest-schema/plugin-manifest.schema.json#/properties/<field>` for every other field an entry shares with `plugin.json`, `name` and `version` included, and `../plugin-manifest-schema/components/channel.schema.json` for `channels[]`.
- `common.schema.json` is a container referenced by fragment: `pluginName`, the name rule of `marketplace.schema.json`.

## Rules
- Declare `"$schema": "https://json-schema.org/draft/2020-12/schema"` and use `$defs`, never `definitions`.
- Never declare `$id`: a schema's identity is its location. Write every `$ref` relative to the file that holds it.
- Never copy into this folder a field or shape another folder defines: reference it. A copy of a `plugin.json` field or of a hooks definition here is a defect.
- Keep `additionalProperties: false` on every object with a known shape, also where the CLI accepts extras with no message (`owner`, source objects, `relevance.signals.manifestDeps` items): a typo there passes `claude plugin validate` silently. Leave open only the free-form `metadata`. Record what the CLI does in `x-cli-unknown-keys`.
- Accept `hooks` in an entry only as an inline event map: a path or an array passes `claude plugin validate` but never runs.
- Keep the cross-field rules where they live:
  - **In `marketplace.schema.json`:** a bare-name source needs `metadata.pluginRoot`, through `if`/`else`.
  - **In `plugin-entry.schema.json`:** `headersHelper` requires `"strict": false` (`allOf[0]`), and `headers` or `headersHelper` require an archive source (`allOf[1]`).
- Plugin entry `name` is `plugin.json`'s `name`: kebab-case and not reserved for Anthropic. Change that rule in `plugin-manifest-schema`.
- Marketplace `name`:
  - Reject `..`, `npm`, `pip`, `uv`, `cargo`, `github` and `gh`, and names that impersonate an official marketplace.
  - Accept the exact names in `x-reserved-official-names`: `claude plugin validate` 2.1.310 passes them, and only adding the marketplace refuses them.
- Mark a field the CLI accepts but the docs omit with `x-undocumented: true` and an `x-note`, and keep it.

## Changes
- **Verify first.** Read the marketplace reference, the manifest reference, the changelog and the installed `claude --version`, and run `claude plugin validate --strict` on a fixture. When the docs and the changelog disagree, the changelog wins. Cite the source in `x-doc`, and set `x-verified` (`claude_code_version`) in `marketplace.schema.json` only after a full re-verification.
- **New entry field:** when `plugin.json` has the same field, `$ref` it from `../plugin-manifest-schema/`; otherwise add it to `plugin-entry.schema.json` `properties`, and when it has its own structure, create a whole-file schema and `$ref` it by path.
- **New source form:** add `sources/<form>.schema.json` with a `source` const and add it to the `oneOf` of `sources/plugin-source.schema.json`.
- **Definition two files of this folder need:** move it to `common.schema.json` `$defs`.
- **Moved or renamed file:** update every `$ref` to it across all of `scripts/schemas/`. Leave no file or `$defs` entry that nothing references.

## Validation
- Load every `*.schema.json` under `scripts/schemas/` into one registry keyed by its `file://` URI, then check:
  - every file passes the 2020-12 metaschema;
  - no file declares `$id`;
  - every `$ref` resolves;
  - every file other than the five entry points (`hooks-schema/hooks.schema.json`, `plugin-manifest-schema/plugin-manifest.schema.json`, `marketplace-schema/marketplace.schema.json`, `lsp.schema.json`, `mcp.schema.json`), and every `$defs` entry, is referenced.
- Validate `.claude-plugin/marketplace.json` against `marketplace.schema.json`.
