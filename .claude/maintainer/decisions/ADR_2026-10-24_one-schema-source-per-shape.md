---
status: accepted
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# One schema source per shape

## Scope

- In scope: where each shape of `scripts/schemas/` is defined: hooks, the plugin manifest and its components (LSP, MCP, userConfig, channel, monitor), the marketplace, and the `.lsp.json` and `.mcp.json` entry points.
- Out of scope: what the shapes accept, which their own rules and ADR_2026-10-24_schemas-are-strict-on-every-known-shape govern.

## Context and problem statement

Hooks lived in three versions (`hooks-schema/`, a copy in `plugin-manifest-schema/hooks/`, and a looser `marketplace-schema/components/hooks.schema.json`), and the component shapes in two. They had drifted: the manifest copy was still at Claude Code 2.1.281, without `onFailure`, `modules` or `requestTimeout`. Four monoliths at the folder root repeated them again, two with broken `$ref`. Where should each shape live?

## Decision drivers

- A change to a shape lands in one file.
- The marketplace entry accepts exactly what `plugin.json` accepts, except where the docs say otherwise.

## Considered options

- **One folder owns each shape and the others reference it**: chosen.
- **Self-contained folders kept in sync by a drift check**: rejected because the copies had already drifted while a check was documented.

## Decision outcome

Chosen option: **one source per shape**:

- `hooks-schema/` owns hooks; the manifest and a marketplace entry reference `hooks-config.schema.json`. A marketplace entry accepts only the inline map, the one form that runs there.
- `plugin-manifest-schema/` owns `plugin.json` and the component shapes; a marketplace entry references `plugin-manifest.schema.json#/properties/<field>` for every field it shares with `plugin.json`.
- `marketplace-schema/` keeps only what an entry alone has: `source`, `category`, `tags`, `strict`, `relevance`, `headers`, `headersHelper`.
- `plugin.schema.json` and `marketplace.schema.json` at the root are deleted; `lsp.schema.json` and `mcp.schema.json` are thin entry points into the manifest's components.

### Consequences

- Good, because the surviving copies absorbed the 2.1.310 fixes (`requestTimeout`, the engine-only MCP fields, reserved names, `..` rejected in paths, the `options` pattern, `homepage`), and the tree went from 75 files to 42.
- Good, because measured: 26 before-and-after probes behaved as intended and 73 of the 74 recorded cases matched; the 74th (an empty `mcpServers`) is accepted by `claude plugin validate --strict` 2.1.310.
- Bad, because a change to a manifest property also changes how a marketplace entry validates; the rules say so.

## More information

- Decided by Nery in the session of 2026-10-24 ("Aplicar siguiendo tus recomendaciones presentadas").
- Related: ADR_2026-10-24_schema-identity-is-its-file-location.
