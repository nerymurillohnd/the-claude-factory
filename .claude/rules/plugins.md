---
paths:
  - "plugins/**"
  - ".claude-plugin/**"
  - "/README.md"
  - "/CHANGELOG.md"
---

# Plugins

## Design

- Design each plugin to solve its purpose end to end, so users find everything that goal needs in one place.
- Add a plugin only when it is more complete and more reliable than the official and public alternatives.
- Design each plugin from what its users need, never by copying another plugin.
- Create a new plugin's folder in `plugins/<plugin>/` yourself: `claude plugin init` scaffolds only in `~/.claude/skills/<name>/`.
- Choose the least invasive design for every action a plugin takes on a user's machine, and take any safety doubt to the owner before it ships.
- License every plugin under MIT.
- Build every plugin for Claude Code, for Claude, or for both, and state in its compatibility notes where a component does not work.

## Portability

- Keep every file and link a plugin uses inside `plugins/<plugin>/`, as real files, never symlinks out of it: users receive only that folder.
- Depend on nothing specific to the maintainer's machine.
- Declare every tool, dependency and minimum version a plugin needs in its README Prerequisites, and state its Windows support there.

## Names and versions

- Use the plugin's folder name, unchanged, as its `plugin.json` `name`, its marketplace entry and its tag prefix (`<plugin>--v…`).
- Record every rename in the `renames` map of `.claude-plugin/marketplace.json`.
- Keep a plugin's version only in its `plugin.json`, never in `marketplace.json`.
- Run `npm run check:consistency` after changing a name, version, changelog, README or catalog row, and fix every finding.

## Testing

- Develop against the plugin's folder with `claude --plugin-dir plugins/<plugin>`, never an installed copy, and run `/reload-plugins` after each edit.
- Run `claude plugin validate --strict plugins/<plugin>`, then `claude --plugin-dir plugins/<plugin> plugin details <plugin>` to confirm every component loaded.
- Test each surface the plugin declares: Claude Code with `--plugin-dir`, and Claude by asking the owner to upload it to their account.
- Run `npm run check:install -- --from local <plugin>` before any release to test what users receive.
- Add evals only to plugins the owner chooses, as `.claude/rules/plugins/evals.md` sets.
