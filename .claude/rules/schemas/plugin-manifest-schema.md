---
paths:
  - "scripts/schemas/plugin-manifest-schema/**/*.schema.json"
  - "scripts/schemas/lsp.schema.json"
  - "scripts/schemas/mcp.schema.json"
---

# Plugin manifest schema

`scripts/schemas/plugin-manifest-schema/` is the source of truth for `.claude-plugin/plugin.json` and for every plugin component shape other than hooks: LSP servers, MCP servers, userConfig, channels and monitors. JSON Schema draft 2020-12, 12 files. Edit the files directly; nothing generates them.

## Entry points
- `plugin-manifest.schema.json`: a plugin's `.claude-plugin/plugin.json`.
- `scripts/schemas/lsp.schema.json`: a plugin's `.lsp.json`; it points to `components/lsp-servers.schema.json`.
- `scripts/schemas/mcp.schema.json`: a `.mcp.json`, wrapped in `mcpServers` or bare; it points to `mcp/mcp-servers.schema.json`.

## Structure
- `plugin-manifest.schema.json` holds the 42 root fields, only `name` required, and delegates:
  - `hooks` to `../hooks-schema/hooks-config.schema.json`;
  - `mcpServers` to `mcp/mcp-servers.schema.json`, which checks server names and sends each value to `mcp/server.schema.json`;
  - `lspServers` to `components/lsp-servers.schema.json`;
  - `userConfig` to `components/user-config.schema.json#/$defs/userConfigOption`;
  - `channels` to `components/channel.schema.json`;
  - `monitors` and `experimental.monitors` to `components/monitor.schema.json`.
- `mcp/server.schema.json` restricts `type` and applies one transport through `allOf` + `if`/`then`: `stdio` or no `type` → `stdio.schema.json`; `http` or `streamable-http` → `http.schema.json`; `sse` → `sse.schema.json`; `ws` → `ws.schema.json`. A `url` without `type` makes `type` required, so the error names the fix.
- `mcp/fields.schema.json` is a container: fields two or more transports share (`alwaysLoad`, `bareElicitationCapability`, `oauth`, `discoveryCache`, `toolPermissions`, `toolPolicies`), referenced by fragment.
- `marketplace-schema/plugin-entry.schema.json` points to `#/properties/<field>` of `plugin-manifest.schema.json` for every field an entry shares with `plugin.json` except `hooks`. Changing one of those properties changes how both files validate, and moving or renaming one breaks the entry's pointer.

## Rules
- Declare `"$schema": "https://json-schema.org/draft/2020-12/schema"` and use `$defs`, never `definitions`.
- Never declare `$id`: a schema's identity is its location. Write every `$ref` relative to the file that holds it, and reach into a sibling folder (`../hooks-schema/…`) instead of copying a definition.
- Keep `additionalProperties: false` at the root and on every object with a known shape, also where the CLI ignores unknown keys (`author`, dependency objects, `commands` object entries, `settings`, `binaries` entries, MCP transports and `oauth`). Leave open only free-form maps: `metadata` and `settings.subagentStatusLine`.
- Record what the CLI does with an unknown key in `x-cli-unknown-keys` (`rejects`, `warns`, `ignores`), measured with `claude plugin validate --strict`.
- Keep `name` (kebab-case, not reserved for Anthropic: a `claude-`, `anthropic-`, `anthropics-` or `cc-plugin-` prefix, exactly `claude`, `anthropic`, `anthropics`, `claude-code` or `claude-mods`, or `official` beside claude or anthropic) and `version` (full SemVer) stricter than Claude Code; each carries `x-policy` with the reason. A whole-word match elsewhere (`mcp-for-claude`) is only a CLI warning and passes.
- Reject `..` in every path field with `^\./(?!(?:.*/)?\.\.(?:/|$))`; `skills` also accepts `.`.
- Reject the MCP server names Claude Code skips (`workspace`, `claude-in-chrome`, `computer-use`, `Claude Preview`, `Claude Browser`) and the JavaScript object member names the engine refuses (`constructor`, `prototype`, `__proto__` and the four `__define*__`/`__lookup*__`).
- Accept an empty `url` on a remote MCP server: it marks a placeholder that shows as `not configured`.
- `userConfigOption` with `options` must be `type: string`, may not set `multiple` or `sensitive` to `true`, and needs a `default` or `required: true`.
- Accept the listing keys (`privacyPolicyUrl`, `supportUrl`, `icon`, `screenshots`, `classification`, `privacy_policy`, `privacyPolicy`, `support`, `bugs`, `termsOfServiceUrl`, `terms_of_service`, `documentationUrl`, `docs`) with any value: the CLI tolerates them without checking type.
- Leave to `claude plugin validate` what JSON Schema cannot express: path existence, unique monitor names, `options` default membership, and `channels[].server` matching an `mcpServers` key.
- Mark a field the manifest reference omits with `x-docs-status`: `documented-once`, `changelog-only`, `cli-tolerated` or `cli-only`.

## Changes
- **Verify first.** Read the manifest reference, the components page, the MCP page, the changelog and the installed `claude --version`, and run `claude plugin validate --strict` on a fixture. When the docs and the changelog disagree, the changelog wins. Cite the source in `x-source`, and set `x-verified` (`claudeCodeVersion`) only after a full re-verification.
- **New manifest field:** add it to `properties` of `plugin-manifest.schema.json`; when it has its own structure, create a whole-file schema under `components/` and `$ref` it by path.
- **New MCP transport:** add `mcp/<transport>.schema.json`, its value to the `type` enum and one `if`/`then` in `mcp/server.schema.json`.
- **Field two transports need:** move it to `mcp/fields.schema.json` `$defs`.
- **New hook event or handler field:** change `../hooks-schema/`, never this folder.
- **Moved or renamed file:** update every `$ref` to it across all of `scripts/schemas/`. Leave no file or `$defs` entry that nothing references.

## Validation
- Load every `*.schema.json` under `scripts/schemas/` into one registry keyed by its `file://` URI, then check:
  - every file passes the 2020-12 metaschema;
  - no file declares `$id`;
  - every `$ref` resolves;
  - every file other than the five entry points (`hooks-schema/hooks.schema.json`, `plugin-manifest-schema/plugin-manifest.schema.json`, `marketplace-schema/marketplace.schema.json`, `lsp.schema.json`, `mcp.schema.json`), and every `$defs` entry, is referenced.
- Validate every `plugins/*/.claude-plugin/plugin.json` against `plugin-manifest.schema.json`, every `plugins/*/.lsp.json` against `lsp.schema.json` and every `plugins/*/.mcp.json` against `mcp.schema.json`.
