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

## Marketplace version

| Bump | When |
| :-- | :-- |
| **major** | Plugin removed or renamed (`renames` entry added) |
| **minor** | Plugin added, or a plugin releases a major/minor |
| **patch** | Plugin releases a patch, or catalog/root-doc metadata changes |

## Changelogs (Keep a Changelog 2.0.0)

- Write entries under `## [Unreleased]` as you work, grouped: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
- User-facing language: what changed for the user, not implementation detail. Reference issues as `(#12)`.
- Mark breaking entries with a leading `**Breaking:**` inside their change type (they force a major bump).
- Release with `node .github/scripts/bump-version.mjs <plugin|marketplace> <level>`; it dates the section and fixes link references. Never edit versions by hand.
- Root `CHANGELOG.md` gets one line per plugin release: `- **plugin-name** 1.2.0 — one-line summary.`

## Tags and GitHub Releases

- `release.yml` creates `{name}--v{version}` tags (same format as `claude plugin tag`) and a GitHub Release with the changelog section after Validate passes on `main`. Never create these tags by hand.
- Marketplace tags: `marketplace--v{version}`.

## Renames and removals

- Never rename silently. Add `"renames": { "old": "new" }` (or `"old": null` for removal) to `marketplace.json`, bump the marketplace **major**, note it in the root changelog.
