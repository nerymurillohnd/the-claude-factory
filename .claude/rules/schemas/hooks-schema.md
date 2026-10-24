---
paths:
  - "scripts/schemas/hooks-schema/*.schema.json"
  - "scripts/schemas/hooks-schema/events/*.schema.json"
  - "scripts/schemas/hooks-schema/handlers/*.schema.json"
  - "scripts/schemas/marketplace-schema/components/hooks.schema.json"
---

# Hooks schema

`scripts/schemas/hooks-schema/` is the source of truth for Claude Code hook configuration, JSON Schema draft 2020-12, 16 files. Edit the files directly; nothing generates them.

## Entry points
- `hooks.schema.json`: a plugin's `hooks/hooks.json`, with `$schema`, `description`, `hooks` and `modules`, at least one of `hooks` or `modules`.
- `plugin-manifest.schema.json`: the `hooks` field of `.claude-plugin/plugin.json`: a `./*.json` path, an inline event map, or an array of both.
- `hooks-config.schema.json`: a bare event map (settings.json, skill or agent frontmatter, the value of `hooks`).

## Structure
- `hooks-config.schema.json` maps each event to `events/<family>.schema.json#/$defs/hookEvent_<Event>`, an array of `hookMatcherGroup_<Event>`. The event name is exact and case-sensitive.
- Each group's `hooks.items` points to one set in `handlers/handler-sets.schema.json`: `hookHandler`, `hookHandlerNoAgent`, `hookHandlerCommandHttpMcp` or `hookHandlerCommandMcp`. Add `hookHandlerWithoutIf` through `allOf` on every event that does not evaluate `if`.
- The five handlers are leaves with no `$ref`: `handlers/{command,http,mcp-tool,prompt,agent}.schema.json`.

## Rules
- Declare `"$schema": "https://json-schema.org/draft/2020-12/schema"` and use `$defs`, never `definitions`.
- Set every `$id` to the file's path relative to `hooks-schema/`. Write every `$ref` relative to the file that holds it. Never point a `$ref` outside the folder.
- Keep `additionalProperties: false` on every object. The CLI silently drops an unknown key; this schema must reject it.
- Allow on each event only the handler types its set lists, and forbid `if` everywhere except PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest and PermissionDenied.
- Accept `matcher` on every event. Where the event has no matcher support, the group's description says to omit it.
- Keep fields that exist only in the engine bundle out (command `rewakeMessage`, `rewakeSummary` and `cloud`; http `cloud`). Model every documented field, including `onFailure` (command and http) and `modules`.

## Changes
- **Verify first.** Read the hooks page, the changelog and the installed `claude --version`, and when they disagree the changelog wins. Cite the source in `x-source`, and set `x-verified` (`claudeCodeVersion`) in `hooks.schema.json` only after a full re-verification.
- **New event:**
  - add `hookEvent_<Event>` and `hookMatcherGroup_<Event>` to its family file;
  - add a bare `$ref` property to `hooks-config.schema.json`;
  - add the event to the `propertyNames` enum of `scripts/schemas/marketplace-schema/components/hooks.schema.json`;
  - fill every `x-` annotation.
- **Changing an event's handler types:** change the group's `$ref`, the event's `x-handlerTypes` and the group description together.
- **New handler field:** edit only that handler's file, and keep its first `examples` entry a valid minimal handler.
- **Annotations must agree with the structure:**
  - `x-handlerTypes` with the set;
  - `x-ifEvaluated` with `hookHandlerWithoutIf`;
  - `x-matcherValues` with the matcher's description and `examples`.
- **Moved or renamed file:** update its `$id` and every `$ref` to it.

## Validation
- Load all 16 files into one registry keyed by `$id`, then check that every file passes the 2020-12 metaschema, that each `$id` equals its path and that every `$ref` resolves.
- Validate every `plugins/*/hooks/hooks.json` against `hooks.schema.json`.
- Confirm that the event list equals the `propertyNames` enum of `marketplace-schema/components/hooks.schema.json`.
