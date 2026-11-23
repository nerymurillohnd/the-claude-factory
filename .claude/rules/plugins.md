---
paths:
  - "plugins/**"
  - ".claude-plugin/**"
  - "/README.md"
  - "/CHANGELOG.md"
---

# Plugins

## Design

- Add a plugin only when it is more complete and more reliable than the official and public alternatives.
- Design each plugin from what its users need, never by copying another plugin.
- Create a new plugin's folder in `plugins/<plugin>/` yourself: `claude plugin init` scaffolds only in `~/.claude/skills/<name>/`.
- Choose the least invasive design for every action a plugin takes on a user's machine, and take any safety doubt to the owner before it ships.
- License every plugin under MIT.
- Build every plugin for both surfaces, Claude Code and Claude, with no branches by surface: a plugin installed from a marketplace in Claude, or created there, reaches Claude and Claude Code unless the user turns off `syncClaudeAiPlugins`, and one installed with `claude plugin install` stays on that machine.
- State a surface difference in a plugin only where a documented limit applies, with its source.
- Keep a plugin's executables in `scripts/`, never in a top-level `bin/`: Claude doesn't install a plugin that has one.

## Portability

- Keep every file and link a plugin uses inside `plugins/<plugin>/`, as real files, never symlinks out of it: users receive only that folder.
- Depend on nothing specific to the maintainer's machine.
- Declare every tool, dependency and minimum version a plugin needs in its README Prerequisites, and state its Windows support there.
- State Node.js 24 or later and Python 3.12 or later there for each runtime a plugin uses, or a tool's own minimum when it is higher: a tool that needs Node 22 still gets Node.js 24.

## Names and versions

- Use the plugin's folder name, unchanged, as its `plugin.json` `name`, its marketplace entry and its tag prefix (`<plugin>--v…`).
- Record every rename in the `renames` map of `.claude-plugin/marketplace.json`.
- Keep a plugin's version only in its `plugin.json`, never in `marketplace.json`.
- Run `npm run check:consistency` after changing a name, version, changelog, README or catalog row, and fix every finding.

## Testing

- Develop against the plugin's folder with `claude --plugin-dir plugins/<plugin>`, never an installed copy, and run `/reload-plugins` after each edit.
- Run `claude plugin validate --strict plugins/<plugin>`, then `claude --plugin-dir plugins/<plugin> plugin details <plugin>` to confirm every component loaded.
- Run `npm run check:install -- --from local <plugin>` before any release to test what users receive.
- Add evals only to plugins the owner chooses.
