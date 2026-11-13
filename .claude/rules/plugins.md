---
paths:
  - "plugins/**"
  - ".claude-plugin/**"
  - "/README.md"
  - "/CHANGELOG.md"
---

# Plugin scope

Conventions for the plugins this marketplace distributes. `.claude/CLAUDE.md` (Work areas) sets the split between the maintainer area and the plugin area.

## Design

- Design each plugin to cover its purpose completely, end to end, so users find everything that goal needs in one place.
- Add a plugin only when it is more complete and more reliable for its purpose than the official and public alternatives.
- Design each plugin only from what it must do and solve for its users, never by copying another plugin.

## Safety

- Treat every action a plugin takes on a user's machine as high risk, and choose the least invasive design.
- Take any doubt about user safety to the owner before anything ships.

## License

- License every plugin under MIT, and document it in the plugin's own README.

## Names

- Use `<plugin-name>` from `plugins/<plugin-name>/`, unchanged, in:
  - `name` in the plugin's `.claude-plugin/plugin.json`
  - the `./plugins/<plugin-name>` path of its entry in `.claude-plugin/marketplace.json`
  - the prefix of every git tag and GitHub Release (`<plugin-name>--v…`)
  - the name in the root README catalog
- Record every rename in the `renames` map of `.claude-plugin/marketplace.json`, and leave no reference to the old name outside the CHANGELOGs and release notes, which record the rename.

## Versions

- Version each plugin on its own. Keep its version only in `version` of `plugins/<plugin-name>/.claude-plugin/plugin.json`; `marketplace.json` stores no version field.
- Keep the plugin's `CHANGELOG.md` with:
  - an empty `## [Unreleased]` section
  - one `## [x.y.z]` heading per released version, the same set as the plugin's git tags
  - compare and tag links that point to the right `<plugin-name>--v<x.y.z>` tags
- Keep exactly one version badge in the plugin's `README.md`, on line 7: a shields.io dynamic badge reading `$.version` from that plugin's `plugin.json` on `main`.
- Keep the version column of the root README catalog equal to each plugin's `version`.
- Keep each plugin's latest git tag equal to `version` in its `plugin.json` on `main`, with the same version in `plugin.json` at the tagged commit, and keep every plugin tag commit an ancestor of `main`.
- When a change under `plugins/<plugin>/` is ready, or a new plugin needs its first version, set the version with the `plugin-versioning` skill: it decides whether the change takes a bump and at which level. When a version is about to be merged or published, release it with the `plugin-releases` skill.

## Target surfaces

- Build every plugin for Claude Code, for Claude, or for both, and for nothing else.
- When a component does not work everywhere in Claude, state where it works in the plugin's compatibility notes, for example only where Claude runs tasks on the user's computer.

## Portability and prerequisites

- Make every plugin self-contained and portable: it depends on no path, configuration, tool, software or version specific to the maintainer's machine, so any user can install and use it.
- Keep every file and relative link a plugin uses inside `plugins/<plugin>/`: Claude Code copies only that folder into the user's cache, so a link such as `../../docs/` breaks on users' machines. Use real files rather than symlinks that leave the plugin: Claude Code copies such a symlink's target when the marketplace comes from git, but skips it when the marketplace was added from a local path.
- Declare every tool, software, integration or dependency a plugin needs to run, and every specific or minimum version it requires, in the Prerequisites section of that plugin's README.
- State each plugin's Windows support in its README.

## Evals

- Add evals only to plugins the owner chooses; suggest them when a plugin would benefit, and say why. How cases are written and run is in `.claude/rules/plugins/evals.md`.
