# Plugin changelog

How to create and keep a plugin's `CHANGELOG.md` from `assets/CHANGELOG-template.md`.

## Produces

`plugins/<plugin>/CHANGELOG.md`: every released version of the plugin, newest first, in Keep a Changelog 2.0.0 form.

## When

- When the plugin is created, with "Initial release." under `## [Unreleased]`.
- In every change that needs a version bump, under `## [Unreleased]` until the release dates it (step 4).

## Sources

Read 2026-11-10:

- Keep a Changelog 2.0.0 (`https://keepachangelog.com/en/2.0.0/`): an `Unreleased` section at the top; one `## [X.Y.Z] - YYYY-MM-DD` section per release, newest first; the six types `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`; breaking changes marked `**Breaking:**`; yanked releases as `## [X.Y.Z] - YYYY-MM-DD [YANKED]`; link references at the bottom.
- Semantic Versioning 2.0.0.
- Claude Code docs `plugins/cli-reference` → `claude plugin tag`: release tags are `<name>--v<version>`.

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{displayName}}` | Plugin display name | `plugin.json` `displayName` |
| `{{repositoryUrl}}` | Repository URL, no trailing slash | `plugin.json` `repository` |
| `{{name}}` | Plugin name, the tag prefix | `plugin.json` `name` |

## What belongs

Record a change when it matters to users: a skill, agent, command, hook, MCP or LSP server, permission, installation, compatibility, security or breaking change.

Leave out formatting-only work, internal refactors with no observable effect, plans, test-only work, lockfile churn with no effect, and unconfirmed versions or dates. Write the result for the user, not the implementation activity, one bullet per coherent change, under exactly one type. Keep only the type headings that have entries, in the order Added, Changed, Deprecated, Removed, Fixed, Security.

## Procedure

1. New plugin: copy the template to `plugins/<plugin>/CHANGELOG.md`, delete its instruction comment, and fill the values. "Initial release." stays under `## [Unreleased]`, with no dated version, until the release dates it (step 4).
2. Each later change: write the notes under `## [Unreleased]`, under the type each change belongs to, in user language: what changes for the user, not how.
3. A breaking change starts its line with `**Breaking:**`, under `### Changed` or `### Removed`, and says what changed, who is affected and the action they must take. A security fix is stated without details that help an attacker.
4. At release, when the `plugin-releases` skill calls for it: rename `## [Unreleased]` to `## [X.Y.Z] - YYYY-MM-DD`, with the version from `plugin.json` and the UTC date the release gives, and add a new empty `## [Unreleased]` above it. Run `npm run release:changelog -- <plugin>` (`--date YYYY-MM-DD` when the release day is not today in UTC): it does this step and step 5, and exits 1 without changing the file when `## [Unreleased]` is empty. If `## [Unreleased]` is empty, stop and ask the owner what the version changes.
5. Update the link references at the bottom: `[Unreleased]` becomes `{{repositoryUrl}}/compare/<name>--v<newest>...HEAD`; each version compares its tag with the previous one; the oldest version links to `{{repositoryUrl}}/releases/tag/<name>--v<oldest>`. Before the first release, `[Unreleased]` links to `{{repositoryUrl}}/commits/main/plugins/<name>`, as the template has it.
6. Run the checks.

## Rules

Official (Keep a Changelog):

- Only the six change types, each as `### Type`.
- Dates `YYYY-MM-DD`.
- Newest version first; `Unreleased` always at the top.

Keep a Changelog sets no time zone. The choice:

- Date each release in UTC, on the day its tag and GitHub Release are created, never the day the bump is prepared. The release runs in CI, whose clock is UTC, and the readers are everywhere: in America/Tegucigalpa (UTC−6), anything after 18:00 is already the next day in UTC.

This repository:

- `## [Unreleased]` is empty on `main`.
- The set of version headings equals the set of `<name>--v<x.y.z>` tags: no missing, no extra.
- Compare and tag links point at the `<name>--v<x.y.z>` tags.
- Bump levels follow the `plugin-versioning` skill; during `0.x` a breaking change takes a minor bump.
- Write plain English in short sentences, for users, many of whom aren't native speakers: say what changes for them, not how it was built. When a change alters nothing in how the plugin works, say "Nothing changes in how the plugin works".
- A `### Security` entry leads with the CVE identifier when there is one, tells users to update to this version, and gives no detail that helps an attacker.
- A `### Deprecated` entry names the feature, its replacement and the release that removes it, when they are known.
- A rename's `**Breaking:**` entry tells users to run `/plugin install <new>@the-claude-factory` once: the marketplace's `renames` map migrates existing installs, and the plugin reports "not cached" until that install.

## Checks

- Every changed plugin has a new version and a non-empty section for it: `npm run release:status` lists every plugin whose version differs from `origin/main` as a `changed:` line; read each one's section.
- `npm run check:consistency` exits 0: every dated version has its tag except the one being released (`PC-04`), and `## [Unreleased]` is empty on `main` (`PC-05`).
- `claude plugin tag plugins/<plugin> --dry-run`, after the changelog is committed: it exits 1 while any file under the plugin is uncommitted, and when the tag already exists.
- `grep -n '{{' plugins/<plugin>/CHANGELOG.md` returns nothing.

## Never

- Never rewrite a released section, except to mark it `[YANKED]`, and only with evidence that the version was withdrawn; keep it in the history.
- Never invent a version, date, compare link, issue or pull request number.
- Never copy the git log into the changelog.
