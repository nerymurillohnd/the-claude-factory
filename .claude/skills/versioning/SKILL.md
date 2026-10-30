---
name: versioning
description: Use for the initial versioning of a new plugin and for updating the version of an existing plugin that changed, with the release notes and changelog lines that go with it.
---

# Versioning

Set or change a plugin's version in `the-claude-factory`. Users receive a change only when the plugin's version string changes, so every shipped change needs a new version.

## Rules

1. Version plugins only. Never add a version or a tag to `.claude-plugin/marketplace.json`.
2. Use SemVer (`MAJOR.MINOR.PATCH`) and choose the level by user-facing impact.
3. Stay in `0.x` while a plugin is new. Never promote a plugin to `1.0.0` without Nery's explicit authorization.
4. Choose a new plugin's name to keep: kebab-case, never a key of `renames`. Changing it later is a rename, handled by `plugin-renames-and-removals`.
5. When another plugin declares a version range on the changed plugin in its `dependencies`, keep the new version inside that range or change the dependent plugin too.

## Steps

### 1. Identify the case

- New plugin: it starts at `0.1.0`, which the scaffold writes. Skip steps 2 and 4.
- Only documentation files (`README.md`, `LICENSE`, `NOTICE.txt`) or in-plugin maintainer files (a mod's tests, an eval suite) changed: no bump. Stop here.
- Only `.claude-plugin/marketplace.json` changed: no bump. Go to step 5.
- Anything else: a changed plugin. Continue.

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

1. Skip this step when `plugin.json` already holds a version above the one in `origin/main`.
2. Bump the version in `plugins/<plugin>/.claude-plugin/plugin.json` to the chosen level, and move `[Unreleased]` into a dated section of the changelog.
3. Confirm the new version is the one you chose.
4. Regenerate the README catalog, which shows the version.

### 5. Add the root changelog line

1. Add a line to `CHANGELOG.md` at the repository root for a version bump, a launch or a marketplace-level change.
2. Put it under today's `## YYYY-MM-DD` heading and the matching change type (`### Added`, `### Changed`, `### Fixed`, `### Removed`). Create either heading if it is missing.
3. Write the line in the shape of its case:
   - Launch or bump: `- **<plugin>** X.Y.Z — one-line summary.` A launch goes under `### Added`.
   - Breaking bump: `- **<plugin>** X.Y.Z — **Breaking:** one-line summary.`
   - Marketplace-level change: `- summary.`, with no plugin name or version.
4. Keep it a summary, never a copy of the plugin changelog.
