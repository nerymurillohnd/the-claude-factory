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

- `0.x` while a plugin is new; `1.0.0` only when Nery declares its interface stable.
- In `0.x`, a breaking change bumps the minor (`0.y.z` → `0.(y+1).0`) and its changelog entry keeps `**Breaking:**`. From `1.0.0` on, breaking means major.

## Changelogs (Keep a Changelog 2.0.0)

- Write entries under `## [Unreleased]` as you work.
- User-facing language: what changed for the user, not implementation detail. Reference issues as `(#12)`.
- Mark breaking entries with a leading `**Breaking:**` inside their change type (they force a major bump, or a minor bump in `0.x`).
- Release only with `node .github/scripts/bump-version.mjs <plugin> <level>`; never edit versions by hand.
- Root `CHANGELOG.md` is grouped by date, newest first, with one line per plugin launch, version bump or substantial change under that day's heading: `- **plugin-name** 1.2.0 — one-line summary.`
- Create the `## YYYY-MM-DD` heading when it is missing, with `### Added`, `### Changed` and so on below it.

## Renames and removals

- Never rename silently. Add `"renames": { "old": "new" }` (or `"old": null` for removal) to `marketplace.json` and note it in the root changelog.
