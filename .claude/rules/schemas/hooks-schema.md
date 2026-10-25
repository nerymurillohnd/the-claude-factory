---
paths:
  - "scripts/schemas/hooks-schema/**/*.schema.json"
---

# Hooks schema

`scripts/schemas/hooks-schema/` is the only source of truth for Claude Code hook configuration, JSON Schema draft 2020-12, 15 files. Edit the files directly; nothing generates them. No other folder holds a hooks schema: `plugin-manifest-schema` and `marketplace-schema` reference `hooks-config.schema.json`.

## Entry points
- `hooks.schema.json`: a plugin's `hooks/hooks.json`, with `$schema`, `description`, `hooks` and `modules`, at least one of `hooks` or `modules`.
- `hooks-config.schema.json`: a bare event map: settings.json, skill or agent frontmatter, the inline `hooks` of `plugin.json` and of a marketplace entry, and the value of `hooks` in `hooks.json`.

## Structure
- `hooks-config.schema.json` maps each event to `events/<family>.schema.json#/$defs/hookEvent_<Event>`, an array of `hookMatcherGroup_<Event>`. The event name is exact and case-sensitive.
- Each group's `hooks.items` points to one set in `handlers/handler-sets.schema.json`: `hookHandler`, `hookHandlerNoAgent`, `hookHandlerCommandHttpMcp` or `hookHandlerCommandMcp`. Add `hookHandlerWithoutIf` through `allOf` on every event that does not evaluate `if`.
- The five handlers are leaves with no `$ref`: `handlers/{command,http,mcp-tool,prompt,agent}.schema.json`.
- Consumers outside the folder: `plugin-manifest-schema/plugin-manifest.schema.json` (`properties.hooks`) and `marketplace-schema/plugin-entry.schema.json` (`properties.hooks`, inline map only). A change here changes their validation.

## Rules
- Declare `"$schema": "https://json-schema.org/draft/2020-12/schema"` and use `$defs`, never `definitions`.
- Never declare `$id`: a schema's identity is its location. Write every `$ref` relative to the file that holds it.
- Keep `additionalProperties: false` on every object except the `input` of `mcp_tool`, which holds the tool's own arguments. The CLI silently drops an unknown key; this schema must reject it.
- Allow on each event only the handler types its set lists, and forbid `if` everywhere except PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest and PermissionDenied.
- Accept `matcher` on every event. Where the event has no matcher support, the group's description says to omit it.
- Keep fields that exist only in the engine bundle out (command `rewakeMessage`, `rewakeSummary` and `cloud`; http `cloud`). Model every documented field, including `onFailure` (command and http) and `modules`.

## Changes
- **Verify first.** Read the hooks page, the changelog and the installed `claude --version`, and when they disagree the changelog wins. Cite the source in `x-source`, and set `x-verified` (`claudeCodeVersion`) in `hooks.schema.json` only after a full re-verification.
- **New event:**
  - add `hookEvent_<Event>` and `hookMatcherGroup_<Event>` to its family file;
  - add a bare `$ref` property to `hooks-config.schema.json`;
  - fill every `x-` annotation.
- **Changing an event's handler types:** change the group's `$ref`, the event's `x-handlerTypes` and the group description together.
- **New handler field:** edit only that handler's file, and keep its first `examples` entry a valid minimal handler.
- **Annotations must agree with the structure:**
  - `x-handlerTypes` with the set;
  - `x-ifEvaluated` with `hookHandlerWithoutIf`;
  - `x-matcherValues` with the matcher's description and `examples`.
- **Moved or renamed file:** update every `$ref` to it across all of `scripts/schemas/`. Leave no file or `$defs` entry that nothing references.

## Validation
- Load every `*.schema.json` under `scripts/schemas/` into one registry keyed by its `file://` URI, then check:
  - every file passes the 2020-12 metaschema;
  - no file declares `$id`;
  - every `$ref` resolves;
  - every file other than the four entry points (`hooks-schema/hooks.schema.json`, `plugin-manifest-schema/plugin-manifest.schema.json`, `plugin-manifest-schema/mcp/mcp.schema.json`, `marketplace-schema/marketplace.schema.json`), and every `$defs` entry, is referenced.
- Validate every `plugins/*/hooks/hooks.json` against `hooks.schema.json`.
