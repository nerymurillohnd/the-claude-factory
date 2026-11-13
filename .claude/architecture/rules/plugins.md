---
paths:
  - "plugins/**"
  - ".claude-plugin/**"
  - "README.md"
  - "CHANGELOG.md"
  - ".github/workflows/**"
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

### Version bumps

A breaking-change entry in the changelog begins with `**Breaking:**`.

- **Major** (`x.0.0`): any breaking change, such as removing or renaming a skill, agent, command or the plugin itself; changing configuration keys; adding a mandatory dependency; or changing behavior existing users rely on.
- **Minor** (`x.y.0`): new backward-compatible components, options or capabilities. In the `0.x` series, breaking changes also bump Minor.
- **Patch** (`x.y.z`): backward-compatible bug fixes, prompt wording improvements, performance improvements, and internal refactors that preserve observable behavior.
- **No bump**: only for changes confined to a plugin's documentation files or its in-plugin maintainer files (for example tests or the eval suite).

## Category

- Each plugin sets `metadata.category` in its `.claude-plugin/plugin.json`, chosen by its purpose; its entry in `.claude-plugin/marketplace.json` and its row in the root README catalog carry the same category.

## Target surfaces

- Every plugin in this marketplace is built exclusively for Claude Code, for Claude, or for both.
- When a component does not work everywhere in Claude, the plugin's compatibility notes state where it works, for example only where Claude runs tasks on the user's computer.

## Portability and prerequisites

- Every plugin is self-contained and portable: it depends on no path, configuration, tool, software or version specific to the maintainer's machine, so any user can install and use it.
- Keep every file, link and symlink a plugin uses inside `plugins/<plugin>/`: Claude Code copies only that folder into the user's cache, so anything outside it, such as `../../docs/`, is missing on users' machines.
- Every tool, software, integration or dependency a plugin needs to run, and every specific or minimum version it requires, is declared as a prerequisite in the Prerequisites section of that plugin's README.
- Each plugin's README states its Windows support.

## Pull requests inside `plugins/`

- A change that creates or edits a plugin's components, dependencies or configuration always goes through a pull request. Skill, agent and command files are components, even though they are Markdown.
- A change limited to a plugin's general documentation, which alters neither the plugin's behavior nor what users have installed on their machines, needs no pull request, unless the owner asks for one.

## Evals

- Whether a plugin has evals is the owner's decision. Claude may suggest adding them to a plugin, and says when and why.
- When the owner decides a plugin gets evals, Claude discusses every eval case with the owner before writing it, and never creates cases on its own.
- A plugin with evals runs a reduced smoke suite locally, through the official testing modes.
- In CI, the full eval suite of a plugin runs the first time, and afterwards only when a plugin that has evals changes in a way that needs a pull request. Every other run skips the eval workflow.
