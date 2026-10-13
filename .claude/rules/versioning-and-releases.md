---
paths:
  - "**/CHANGELOG.md"
  - "**/plugin.json"
  - ".claude-plugin/**"
  - ".github/workflows/release.yml"
---

# Versioning and releases

## Plugin versions (SemVer)

| Bump | When |
| :-- | :-- |
| **major** | Breaking: removed/renamed skill, agent or command; changed config keys; new required dependency; behavior users rely on changes |
| **minor** | New component, option or capability, backwards compatible |
| **patch** | Bug fix, prompt wording fix, performance, internal refactor with same behavior |

- Users only receive changes when `version` changes. Any change to shipped plugin files needs a bump (CI: `check-version-bump.mjs`). README-only edits don't.
- `0.x` while a plugin is new; `1.0.0` once its interface is stable.

## Marketplace

- The marketplace has no version: `.claude-plugin/marketplace.json` carries no `version`, and `check-repo.mjs` fails when it does.
- Plugins carry the versions. Each plugin version has its own tag and its own changelog.
- Root `CHANGELOG.md` is grouped by date, newest first. The versions 0.1.0 and 0.2.0 in it are history.
- Never create a marketplace tag. The tags `marketplace--v0.1.0` and `marketplace--v0.2.0` stay as history.

## Changelogs (Keep a Changelog 2.0.0)

- Write entries under `## [Unreleased]` as you work, grouped: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
- User-facing language: what changed for the user, not implementation detail. Reference issues as `(#12)`.
- Mark breaking entries with a leading `**Breaking:**` inside their change type (they force a major bump).
- Release with `node .github/scripts/bump-version.mjs <plugin> <level>`; it dates the section and fixes link references. Never edit versions by hand.
- Root `CHANGELOG.md` gets one line per plugin release under the date heading of the release day: `- **plugin-name** 1.2.0 — one-line summary.`
- Create the `## YYYY-MM-DD` heading when it is missing, with `### Added`, `### Changed` and so on below it.

## Tags and GitHub Releases

- `release.yml` creates `{name}--v{version}` tags (same format as `claude plugin tag`) and a GitHub Release with the changelog section after Validate passes on `main`. Never create these tags by hand.

## Renames and removals

- Never rename silently. Add `"renames": { "old": "new" }` (or `"old": null` for removal) to `marketplace.json` and note it in the root changelog.
