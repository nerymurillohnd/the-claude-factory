---
paths:
  - "scripts/schemas/marketplace-schema/*.schema.json"
  - "scripts/schemas/marketplace-schema/components/*.schema.json"
  - "scripts/schemas/marketplace-schema/sources/*.schema.json"
  - "scripts/schemas/hooks-schema/hooks-config.schema.json"
---

# Marketplace schema

`scripts/schemas/marketplace-schema/` is the source of truth for `.claude-plugin/marketplace.json`, JSON Schema draft 2020-12, 22 files. Edit the files directly; nothing generates them.

## Entry points
- `marketplace.schema.json`: the whole catalog, also one served from a URL.
- `plugin-entry.schema.json`: one element of `plugins[]`.
- `sources/plugin-source.schema.json`: one plugin `source` value.

## Structure
- `marketplace.schema.json` holds the envelope and points `plugins[].items` to `plugin-entry.schema.json`.
- `plugin-entry.schema.json` delegates to:
  - `common.schema.json` (`pluginName`, `person`, `relPath`, `relJsonPath`, `skillPath`, `agentPath`);
  - `sources/plugin-source.schema.json`, a `oneOf` of 8 forms: relative-path and bare-name as strings, and github, url, git-subdir, npm, archive and command selected by their `source` const;
  - `dependency`, `relevance`, `channel` and `user-config`;
  - `components/` (`commands`, `hooks`, `mcp-servers`, `lsp-servers`, `monitors`, `experimental`).
- Two kinds of file:
  - **Whole-file schemas** are referenced by path.
  - **Containers** (`common.schema.json`) are referenced by fragment (`common.schema.json#/$defs/pluginName`).

## Rules
- Declare `"$schema": "https://json-schema.org/draft/2020-12/schema"` and use `$defs`, never `definitions`.
- Set every `$id` to the file's path relative to `marketplace-schema/`. Write every `$ref` relative to the file that holds it. Never point a `$ref` outside the folder.
- Keep strictness mixed, as it stands.
  - `additionalProperties: false` where the CLI warns or errors on an unknown key: the root, `metadata`, plugin entries, `relevance`, `experimental`, userConfig options, LSP servers, monitors, channels.
  - `true` where the CLI accepts extras with no message: `owner`, `author`, source objects, dependency objects, hook handlers, MCP server configs.
  - Never tighten the `true` ones.
- Keep the cross-field rules where they live:
  - **In `marketplace.schema.json`:** a bare-name source needs `metadata.pluginRoot`, through `if`/`else`.
  - **In `plugin-entry.schema.json`:** `headersHelper` requires `"strict": false` (`allOf[0]`), and `headers` or `headersHelper` require an archive source (`allOf[1]`).
- Plugin entry `name`:
  - Reject the names `claude plugin validate` errors on as Anthropic's own: a `claude-`, `anthropic-`, `anthropics-` or `cc-plugin-` prefix; exactly `claude`, `anthropic`, `anthropics`, `claude-code` or `claude-mods`; or `official` beside claude or anthropic.
  - Accept a whole-word match elsewhere (`mcp-for-claude`), which is only a warning.
- Marketplace `name`:
  - Reject `..`, `npm`, `pip`, `uv`, `cargo`, `github` and `gh`, and names that impersonate an official marketplace.
  - Accept the exact names in `x-reserved-official-names`: `claude plugin validate` 2.1.310 passes them, and only adding the marketplace refuses them.
- Mark a field the CLI accepts but the docs omit with `x-undocumented: true` and an `x-note`, and keep it.
- `components/hooks.schema.json` is deliberately looser than `scripts/schemas/hooks-schema/`. It accepts any handler, and its `propertyNames` enum must list exactly the events of `hooks-schema/hooks-config.schema.json`.

## Changes
- **Verify first.** Read the marketplace reference, the manifest reference, the changelog and the installed `claude --version`, and run `claude plugin validate --strict` on a fixture. When the docs and the changelog disagree, the changelog wins. Cite the source in `x-doc`, and set `x-verified` (`claude_code_version`) in `marketplace.schema.json` only after a full re-verification.
- **New entry field:** add it to `plugin-entry.schema.json` `properties`; when it has its own structure, create a whole-file schema and `$ref` it by path.
- **New source form:** add `sources/<form>.schema.json` with a `source` const and add it to the `oneOf` of `sources/plugin-source.schema.json`.
- **New hook event:** add it to the enum of `components/hooks.schema.json` and to `scripts/schemas/hooks-schema/`.
- **Definition two files need:** move it to `common.schema.json` `$defs`.
- **Moved or renamed file:** update its `$id` and every `$ref` to it. Leave no file or `$defs` entry that nothing references.

## Validation
- Load all 22 files into one registry keyed by `$id`, then check:
  - every file passes the 2020-12 metaschema;
  - each `$id` equals its path;
  - every `$ref` resolves;
  - every file and every `$defs` entry is referenced;
  - the hook event enum equals `hooks-schema/hooks-config.schema.json`.
- Validate `.claude-plugin/marketplace.json` against `marketplace.schema.json`.
