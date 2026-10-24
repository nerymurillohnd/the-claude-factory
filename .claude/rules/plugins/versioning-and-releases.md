# Versioning and Releases Rules

## General

- Version only plugins; never add a version or a tag to `.claude-plugin/marketplace.json`.
- Use SemVer (`MAJOR.MINOR.PATCH`); choose the bump by user-facing impact.
- Apply bumps with `node scripts/bump-version.mjs <plugin> <major|minor|patch>`, never by hand.

## Versioning

- Use `major` for breaking changes: removing or renaming skills, agents, or commands; changing configuration keys; introducing mandatory dependencies; or breaking behavior users rely on.
- Use `minor` to add backward-compatible components, options, or capabilities.
- Use `patch` for backward-compatible bug fixes, prompt wording improvements, performance improvements, or internal refactors.
- Choose the highest applicable bump per affected plugin when a PR mixes change levels.
- Skip the bump only when a plugin's changes are limited to that plugin's `README.md`; require a bump for every other plugin change, including changelog-only changes.
- During `0.x`, use `minor` for breaking changes and prefix their changelog entries with `**Breaking:**`.
- Never promote a plugin to `1.0.0` without Nery's explicit authorization; that release declares interface stability.
- From `1.0.0` onward, use `major` for breaking changes.

## Releases

- Write the release notes under `## [Unreleased]` in the plugin's `CHANGELOG.md`, in terms of what changes for users, following Keep a Changelog 2.0.0.
- Add the root `CHANGELOG.md` line under today's date: `- **<plugin>** X.Y.Z — summary.` If the PR is still open on a later day, move the line to that day's section before the merge.
- Commit the bump, the plugin and root changelog entries, and the catalog regenerated with `node scripts/generators/catalog.mjs` as one signed commit.
- Never push `main` without first listing the untagged plugins (`plugin.json` version against `git tag -l '<plugin>--v<version>'`) and confirming each is meant to ship.
- Never run `gh workflow run release.yml` while the Validate workflow is failing; fix the cause first.
