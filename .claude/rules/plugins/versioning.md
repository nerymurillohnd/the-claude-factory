---
paths:
  - "plugins/**"
  - "CHANGELOG.md"
---

# Plugin versions

Each plugin carries its own semver version in `plugins/<plugin>/.claude-plugin/plugin.json`; users receive a change only when that version changes.

## Choose the level

- Bump Major for a breaking change.
- Bump Minor for a new backward-compatible feature, and for a breaking change while the plugin is in `0.x`.
- Bump Patch for a backward-compatible fix.
- Leave the version unchanged when only documentation, tests or evals changed.
- Start the changelog entry of a breaking change with `**Breaking:**`.

## Date a release

- Write release dates in UTC as `YYYY-MM-DD`.
- Date a release the UTC day its tag and GitHub Release are created, not the day the bump is prepared.

## Use the skills

- When a change under `plugins/<plugin>/` is ready, or a new plugin needs its first version, load the `plugin-versioning` skill: it picks the level, sets the version and writes the changelog notes.
- When a version is about to be merged or published, load the `plugin-releases` skill: it dates the changelog and creates the tag and the GitHub Release.
