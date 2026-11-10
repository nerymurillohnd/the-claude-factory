# Plugin changelog

How to create and keep a plugin's `CHANGELOG.md` from `.claude/templates/CHANGELOG-template.md`.

## Produces

`plugins/<plugin>/CHANGELOG.md`: every released version of the plugin, newest first, in Keep a Changelog 2.0.0 form.

## When

- When the plugin is created, with its first version.
- In every change that needs a version bump, under `## [Unreleased]` until the bump dates it.

## Sources

Read 2026-11-10:

- Keep a Changelog 2.0.0 (`https://keepachangelog.com/en/2.0.0/`): an `Unreleased` section at the top; one `## [X.Y.Z] - YYYY-MM-DD` section per release, newest first; the six types `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`; breaking changes marked `**Breaking:**`; yanked releases as `## [X.Y.Z] - YYYY-MM-DD [YANKED]`; link references at the bottom.
- Semantic Versioning 2.0.0.
- Former procedures consolidated and corrected: `codex-essentials-legacy` `doc-keeper` → `references/changelog-maintenance.md` (it cites Keep a Changelog 1.1.0; corrected here to 2.0.0) and `claude-essentials-deprecated` `templates/CHANGELOG-reusable-template.md`.
- Claude Code docs `plugins/cli-reference` → `claude plugin tag`: release tags are `<name>--v<version>`.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{displayName}}` | Plugin display name | `plugin.json` `displayName` |
| `{{version}}` | First version | `plugin.json` `version` (`0.1.0` for a new plugin) |
| `{{date}}` | Release date, `YYYY-MM-DD` | The UTC day the version is released, meaning the day its tag and GitHub Release are created (see Rules) |
| `{{repositoryUrl}}` | Repository URL, no trailing slash | `plugin.json` `repository` |
| `{{name}}` | Plugin name, the tag prefix | `plugin.json` `name` |

## What belongs

Record a change when it matters to users: a skill, agent, command, hook, MCP or LSP server, permission, installation, compatibility, security or breaking change.

Leave out formatting-only work, internal refactors with no observable effect, plans, test-only work, lockfile churn with no effect, and unconfirmed versions or dates. Write the result for the user, not the implementation activity, one bullet per coherent change, under exactly one type. Keep only the type headings that have entries, in the order Added, Changed, Deprecated, Removed, Fixed, Security.

## Procedure

1. New plugin: copy the template to `plugins/<plugin>/CHANGELOG.md`, delete its instruction comment, and fill the values; the first section keeps `### Added` with "Initial release."
2. Each later change: write the notes under `## [Unreleased]`, under the type each change belongs to, in user language: what changes for the user, not how.
3. A breaking change starts its line with `**Breaking:**`, under `### Changed` or `### Removed`, and says what changed, who is affected and the action they must take. A security fix is stated without details that help an attacker.
4. At release, run `npm run version:bump`: it raises the version and turns `[Unreleased]` into `## [X.Y.Z] - YYYY-MM-DD`, leaving an empty `## [Unreleased]`.
5. Update the link references at the bottom: `[Unreleased]` compares the newest tag with `HEAD`; each version compares its tag with the previous one; the oldest version links to `releases/tag/`.
6. Run the checks.

## Rules

Official (Keep a Changelog):

- Only the six change types, each as `### Type`.
- Dates `YYYY-MM-DD`.
- Newest version first; `Unreleased` always at the top.

Keep a Changelog sets no time zone. The choice:

- Date each release in UTC, on the day it is released. The release runs in CI, whose clock is UTC, and the readers are everywhere. A local date written when the bump is prepared can differ from the day the tag and Release appear: in America/Tegucigalpa (UTC−6), anything after 18:00 is already the next day in UTC.
- `scripts/release/bump-version.py` dates in America/Tegucigalpa when the bump is prepared, and `scaffold-plugin.py` dates in UTC. That inconsistency is left for the refactor, where the date should be set in UTC at release time.

This repository:

- `## [Unreleased]` is empty on `main`.
- The set of version headings equals the set of `<name>--v<x.y.z>` tags: no missing, no extra.
- Compare and tag links point at the `<name>--v<x.y.z>` tags.
- Bump levels follow `.claude/CLAUDE.md` → Version bump policy; during `0.x` a breaking change takes a minor bump.

## Checks

- `python3 scripts/release/check-version-bump.py`: every changed plugin has a new version and its entry.
- `claude plugin tag plugins/<plugin> --dry-run`: the tag does not exist yet and the tree is clean.
- `grep -n '{{' plugins/<plugin>/CHANGELOG.md` returns nothing.

## Never

- Never rewrite a released section, except to mark it `[YANKED]`, and only with evidence that the version was withdrawn; keep it in the history.
- Never invent a version, date, compare link, issue or pull request number.
- Never copy the git log into the changelog.
