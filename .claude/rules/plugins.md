---
paths:
  - "plugins/**"
  - ".claude-plugin/**"
  - "README.md"
  - "CHANGELOG.md"
---

# Plugin scope

Conventions for the plugins this marketplace distributes. The split between the maintainer scope and the plugin scope is set in `.claude/CLAUDE.md` (How work is done › Two scopes).

## Design

- Each plugin covers its purpose completely, end to end, so users find everything that goal needs in one place.
- A plugin earns its place by being more complete and more reliable for its purpose than the official and public alternatives.
- Each plugin is designed only from what it must do and solve for its users, never by copying another plugin.

## Safety

- Every action a plugin takes on a user's machine is treated as high risk, and the least invasive design wins.
- Any doubt about user safety goes to the owner before anything ships.

## License

- Every plugin is MIT-licensed and documented in its own README.

## Names

- `<plugin-name>` in `plugins/<plugin-name>/` is identical in:
  - `name` in the plugin's `.claude-plugin/plugin.json`
  - the `./plugins/<plugin-name>` path of its entry in `.claude-plugin/marketplace.json`
  - the prefix of every git tag and GitHub Release (`<plugin-name>--v…`)
  - the name in the root README catalog
- Record every rename in the `renames` map of `.claude-plugin/marketplace.json`, and leave no reference to the old name outside the CHANGELOGs and release notes, which record the rename.

## Versions

- Each plugin is versioned on its own. The source of truth is `version` in `plugins/<plugin-name>/.claude-plugin/plugin.json`; `marketplace.json` stores no version field.
- `CHANGELOG.md`:
  - has an empty `## [Unreleased]` section
  - has one `## [x.y.z]` heading per released version, and that set exactly matches the plugin's git tags
  - has compare and tag links that point to the right `<plugin-name>--v<x.y.z>` tags
- The plugin's `README.md` has exactly one version badge, on line 7: a shields.io dynamic badge reading `$.version` from that plugin's `plugin.json` on `main`.
- The version column of the root README catalog matches each plugin's `version`.
- The latest git tag of each plugin equals `version` in its `plugin.json` on `main`, and `plugin.json` at the tagged commit holds the same version.
- Every plugin tag commit is an ancestor of `main`.
- When a change under `plugins/<plugin>/` is ready, or a new plugin needs its first version, set the version with the `plugin-versioning` skill: it decides whether the change takes a bump and at which level. When a version is about to be merged or published, release it with the `plugin-releases` skill.

## Target surfaces

- Every plugin in this marketplace is built exclusively for Claude Code, for Claude, or for both.
- When a component does not work everywhere in Claude, the plugin's compatibility notes state where it works, for example only where Claude runs tasks on the user's computer.

## Portability and prerequisites

- Every plugin is self-contained and portable: it depends on no path, configuration, tool, software or version specific to the maintainer's machine, so any user can install and use it.
- Keep every file and relative link a plugin uses inside `plugins/<plugin>/`: Claude Code copies only that folder into the user's cache, so a link such as `../../docs/` breaks on users' machines. Use real files rather than symlinks that leave the plugin: Claude Code copies such a symlink's target when the marketplace comes from git, but skips it when the marketplace was added from a local path.
- Every tool, software, integration or dependency a plugin needs to run, and every specific or minimum version it requires, is declared as a prerequisite in the Prerequisites section of that plugin's README.
- Each plugin's README states its Windows support.

## Evals

- Add evals only to plugins the owner chooses; suggest them when a plugin would benefit, and say why. How cases are written and run is in `.claude/rules/plugins/evals.md`.
