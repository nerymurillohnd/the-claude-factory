# Marketplace changelog

How to create and keep the root `CHANGELOG.md` of an unversioned marketplace from `assets/marketplace-changelog-template.md`.

## Produces

`CHANGELOG.md` at the repository root: one line per plugin added, updated, renamed or retired, and per change to the catalog itself, grouped by date, newest first.

## When

- At the release of every new plugin and plugin version (the `plugin-releases` skill), and with every rename, merge or removal (the `plugin-catalog-changes` skill).
- With every marketplace-level change users notice (a catalog, category or documentation change).

## Sources

Read 2026-11-10:

- Keep a Changelog 2.0.0: the six change types, `YYYY-MM-DD` dates, newest first, `**Breaking:**`.
- Claude Code docs `plugins/marketplace-reference`: `marketplace.json` accepts an optional `version` (or `metadata.version`); a plugin's `plugin.json` `version` takes precedence over its entry's. This repository sets neither (see Rules), so the changelog groups by date.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{marketplaceDisplayName}}` | Marketplace display name | The root README hero |
| `{{date}}` | The date heading, `YYYY-MM-DD` | A launch or a version: the date of the plugin's changelog section. A rename, merge or removal: the UTC day it merges into `main` |
| `{{pluginName}}`, `{{pluginVersion}}` | The plugin and its new version | Its `plugin.json` |
| `{{summary}}` | One-line summary of the change, for users | The plugin's changelog section |

## Procedure

1. Find or create the `## {{date}}` heading, keeping dates newest first.
2. Find or create the change type heading under it.
3. Add one line in the shape of its case:
   - Launch or bump: `- **<plugin>** X.Y.Z — summary.` A launch goes under `### Added`.
   - Breaking bump: `- **<plugin>** X.Y.Z — **Breaking:** summary.`
   - Rename, under `### Changed`: `- **<old>** is now **<new>** X.Y.Z — **Breaking:** summary.`
   - Merge, under `### Changed`: `- **<old>** is merged into **<target>** X.Y.Z — **Breaking:** summary.`
   - Removal, under `### Removed`: `- **<plugin>** — summary.`, with no version; say whether uninstalling deletes its saved options and data.
   - Marketplace-level change: `- summary.`, with no plugin name or version.
4. Run the checks.

## Rules

Official (Keep a Changelog):

- Only the six change types; dates `YYYY-MM-DD`; newest first.

This repository:

- The marketplace carries no version: headings are dates, never `## [X.Y.Z]`. The `## [0.1.0]` and `## [0.2.0]` sections at the end of the file predate that rule; keep them as they are. No `marketplace--v*` tag exists for them, so their two link references don't resolve.
- A line is a summary, never a copy of the plugin's changelog.
- The date is the plugin changelog's date: the UTC release day (see `changelog.md` → Rules).

## Checks

- The line's version equals the plugin's `plugin.json` `version`.
- A launch's or version's date equals the date of that version's section in the plugin's `CHANGELOG.md`; a rename's, merge's or removal's date is the UTC day it merges.

## Never

- Never add a version heading for the marketplace.
- Never add `version` to `marketplace.json`.
