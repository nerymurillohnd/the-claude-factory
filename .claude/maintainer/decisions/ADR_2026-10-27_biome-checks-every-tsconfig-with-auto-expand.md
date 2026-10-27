---
status: accepted
date: 2026-10-27
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Biome checks every tsconfig file, formatted with `expand: "auto"`

## Scope

`biome.json` (`files.includes` and `overrides`) and the seven tracked tsconfig files:
- `tsconfig.base.json`, `scripts/tsconfig.json` and `scripts/tsconfig.plugins.json`;
- the mods' `plugins/file-tree-pane/tsconfig.json`, `plugins/project-maintainer/tsconfig.json`, `plugins/tool-ledger/tsconfig.json` and `plugins/turn-meter/tsconfig.json`.

The engine-generated `plugins/<mod>/.claude-plugin/types/tsconfig.json` is out of scope, since git ignores it.

## Context and problem statement

Since commit `b3ada31`, `biome.json` force-ignored `**/tsconfig.json` and `**/tsconfig.base.json`, and no reason was recorded (DEBT-034). A malformed tsconfig passed Biome.

The Biome 2.6.3 configuration reference reserves `!!` for build output and nested projects, and asks for a regular exclusion for files that give types or other project information.

Removing the exclusion alone would reformat five files under the JSON-wide `json.formatter.expand: "always"`: `scripts/tsconfig.json` and the four mods' tsconfig files. A plugin file changed that way needs a pull request, a version bump and a changelog entry (`check-version-bump.mjs` exempts only `README.md`). How should Biome check the tsconfig files without touching the plugins?

## Decision drivers

- Every tracked tsconfig is checked, with nothing left out.
- No plugin file changes only to satisfy formatting.
- `expand: "always"` exists so the scripts' `JSON.stringify(…, 2)` output stays formatted (`809cf90`). No repository script writes a tsconfig.

## Considered options

- **Include all seven, with an override that sets `json.formatter.expand: "auto"` for `**/tsconfig.json` and `**/tsconfig.*.json`**: chosen.
- **Exclude the plugin tsconfig files with a regular `!plugins/*/tsconfig.json`**: rejected, because four files would stay unchecked.
- **Include all seven under `expand: "always"`**: rejected, because it needs four plugin pull requests and releases for a formatting-only change.

## Decision outcome

Chosen option: **include all seven with the `expand: "auto"` override**, because it is the only option that checks every tsconfig without changing a plugin file. The `expand: "always"` reason does not reach tsconfig files, since no script writes one.

### Consequences

- Good, because a malformed or badly formatted tsconfig now fails `biome ci`, the pre-commit hook and the gates.
- Good, because Biome parses `tsconfig.json` and `tsconfig.*.json` as JSONC, the well-known-files behavior, so comments and trailing commas stay legal in them.
- Good, because the override replaces a force-ignore with no recorded reason, and this record holds the reason.
- Bad, because tsconfig files follow a different expansion rule from other JSON, which a reader of `biome.json` has to notice.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Biome processes all seven tsconfig files | `biome ci . --verbose`, its "Files processed" list before and after | 163 → 170 files. Added: the six tsconfig files that were excluded, plus `.claude/settings.json` (a separate decision of the same commit); `scripts/tsconfig.plugins.json` was already in. Nothing removed. | On any change to `files.includes` |
| No plugin file changes | `git diff --stat` | Only `biome.json` and `scripts/tsconfig.json` changed | Once |
| The configuration passes | `biome ci .` and `npm run lint:js` | 170 files, no fixes, 4 infos; `biome-maintainer` and `biome-plugins` passed | Each commit |
| The reformatted tsconfig still works | `tsc -p scripts/tsconfig.json --noEmit` and `tsc -p scripts/tsconfig.plugins.json --noEmit` | Both exit 0 | Each commit |

## More information

- Decided by Nery on 2026-10-27, as D1 (c) of `.claude/specs/2026-10-26-biome-config-corrections-and-strictness-design.md` (items 1 and 21).
- Closes DEBT-034 as resolved.
