---
name: versioning
description: Use for the initial versioning of a new plugin and for updating the version of an existing plugin that changed, with the release notes and changelog lines that go with it.
---

# Versioning

Set or change a plugin's version in `the-claude-factory`, a marketplace hosted in a public GitHub repository. Each plugin is a relative-path entry (`./plugins/<plugin>`), and users add the marketplace as `nerymurillohnd/the-claude-factory`, so Claude Code clones the repository and reads each plugin's version from its `plugin.json`. Users receive a change only when that version string changes: if it stays, `claude plugin update` reports the plugin at its latest version and users keep the old copy.

## Rules

1. Version plugins only. Never add a version or a tag to `.claude-plugin/marketplace.json`: when both files set one, Claude Code uses the `plugin.json` value without warning.
2. Use SemVer (`MAJOR.MINOR.PATCH`) and choose the level by user-facing impact.
3. Stay in `0.x` while a plugin is new. Never promote a plugin to `1.0.0` without Nery's explicit authorization.
4. Choose a new plugin's name to keep: kebab-case, never a key of `renames`. Changing it later is a rename, not a version change.
5. Look for dependents of the changed plugin with `jq -c 'select(.dependencies) | {name, dependencies}' plugins/*/.claude-plugin/plugin.json` and `jq -c '.plugins[] | select(.dependencies) | {name, dependencies}' .claude-plugin/marketplace.json`. When an entry names the changed plugin with a version range, keep the new version inside that range, or change the dependent plugin too.

## Steps

### 1. Identify the case

- New plugin: it starts at `0.1.0`, which the scaffold writes. Skip steps 2 and 4.
- Only documentation files at the plugin's root (`README.md`, `LICENSE`, `NOTICE.txt`) or maintainer files changed: no bump. Stop here. Maintainer files are anything under `tests/`, files named `*.test.ts` or `*.test.tsx`, and the eval directory, which is `evals/` unless `experimental.evals` in the manifest names another.
- Any other file changed, `CHANGELOG.md` included: the plugin needs a bump. Continue.
- Only `.claude-plugin/marketplace.json` changed: no bump. Go to step 6.

### 2. Choose the level

Read the diff against `origin/main`. When one pull request mixes levels, take the highest.

| Level | When |
| :-- | :-- |
| major | A breaking change: a removed or renamed skill, agent or command, a renamed plugin, changed configuration keys, a new mandatory dependency, or a change to behavior users rely on |
| minor | A new component, option or capability, backward compatible |
| patch | A backward-compatible bug fix, prompt wording improvement, performance improvement or internal refactor with the same behavior |

- During `0.x`, a breaking change bumps minor, and its changelog entry starts with `**Breaking:**`.
- From `1.0.0`, a breaking change bumps major.

### 3. Write the release notes

1. Open `plugins/<plugin>/CHANGELOG.md`.
2. Write the notes under `## [Unreleased]`. For a new plugin, write them under `## [0.1.0]` → `### Added`.
3. Use the Keep a Changelog types: `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`.
4. Record every user-visible change in user language: what changes for the user, not how.
5. Reference issues as `(#12)`.
6. Start a breaking entry with `**Breaking:**`, inside its type.
7. Compare the notes with the diff: every change appears and nothing that did not happen does.

### 4. Apply the version

1. Skip this step when `plugin.json` already holds a version above the one in `origin/main` (`git show origin/main:plugins/<plugin>/.claude-plugin/plugin.json`).
2. Stop when `## [Unreleased]` is missing or empty: write the notes first.
3. Compute the new version from the current one. Drop any pre-release or build suffix, then raise by the level: major gives `X+1.0.0`, minor gives `X.Y+1.0`, patch gives `X.Y.Z+1`.
4. Set `version` in `plugins/<plugin>/.claude-plugin/plugin.json` to it and keep the file's two-space JSON layout.
5. In `CHANGELOG.md`, leave an empty `## [Unreleased]` heading and put the notes under `## [X.Y.Z] - YYYY-MM-DD`, with the UTC date.
6. Update the link references at the bottom of the changelog:
   - `[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/<plugin>--v<X.Y.Z>...HEAD`
   - `[X.Y.Z]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/<plugin>--v<X.Y.Z>`
7. Replace the old `[Unreleased]:` line with the two lines above, or append them when it is missing.
8. Leave one blank line, never more, between sections.
9. Confirm the new version is the one you chose.
10. Regenerate the README catalog, which shows the version.

### 5. Check the version

1. Compare `plugin.json` with the version at `origin/main`: it is exactly one step above, patch `X.Y.Z+1`, minor `X.Y+1.0` or major `X+1.0.0`. A version that is not higher, or that skips a step, fails. A new plugin has no base: skip this item.
2. For a renamed plugin, compare with the old name's version at `origin/main`. A rename is breaking, so a patch step fails: use minor during `0.x` and major after.
3. A step from `0.x` to `1.0.0` needs Nery's authorization (rule 3).
4. `CHANGELOG.md` has a non-empty `## [X.Y.Z]` section for the current version.
5. `.claude-plugin/marketplace.json` holds no `version`: not at the top level, not under `metadata`, and not on any entry of `plugins`.

### 6. Add the root changelog line

1. Add a line to `CHANGELOG.md` at the repository root for a version bump, a launch or a marketplace-level change.
2. Put it under the `## YYYY-MM-DD` heading of the date the changelog section uses (UTC), and under the matching change type (`### Added`, `### Changed`, `### Fixed`, `### Removed`). Create either heading if it is missing.
3. Write the line in the shape of its case:
   - Launch or bump: `- **<plugin>** X.Y.Z — one-line summary.` A launch goes under `### Added`.
   - Breaking bump: `- **<plugin>** X.Y.Z — **Breaking:** one-line summary.`
   - Marketplace-level change: `- summary.`, with no plugin name or version.
4. Keep it a summary, never a copy of the plugin changelog.
