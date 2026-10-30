---
name: rename-a-plugin
description: Use when a published plugin of this marketplace must be renamed and keeping its name is not possible, so existing installs migrate through the renames map.
---

# Rename a plugin

Rename a published plugin of `the-claude-factory`, a marketplace hosted in a public GitHub repository whose plugins are relative-path entries (`./plugins/<plugin>`). Claude Code records each install under the plugin's name, so a rename reaches users only through the `renames` map in `.claude-plugin/marketplace.json`. Without that entry, users of the old name lose the plugin.

## Rules

1. Rename only when keeping the name is not possible. To change only the label users see, set `displayName` in `plugin.json`, keep `name`, and stop: that is not a rename.
2. Register every rename in the `renames` map. The map is append-only: add one entry per rename, and never edit or delete an existing one.
3. Ship a rename as a breaking change. The plugin's `name` namespaces its commands, agents and MCP tools, so the old ones and the permission rules that name them stop working, and each user reinstalls once.
4. Leave dated history untouched: old changelog lines and specs keep the old name.
5. Never reuse a retired name.
6. Never delete or move the old tag or its GitHub Release. They stay as history.
7. Write no GitHub label until Nery orders it.

## What users see after the push

- The plugin loads under its new name, and `claude plugin list` and `/plugin` show `Renamed to "<new>" in the "the-claude-factory" marketplace` once.
- Claude Code rewrites the old key to the new one in `enabledPlugins` and `pluginConfigs` of the user, project and local settings.
- The plugin reports `Plugin "<new>" not cached` until the user runs `/plugin install <new>@the-claude-factory` once.
- An organization that enables the plugin in managed settings sees the notice on every session until an administrator changes `enabledPlugins` there.
- A new install by the old name fails with `not found in marketplace`: `renames` migrates only existing installs.

## Steps

### 1. Confirm the rename is unavoidable

1. Ask what the rename must achieve.
2. When a different label is enough, apply rule 1 and stop.

### 2. Choose the new name

1. Use kebab-case: lowercase letters, digits and single hyphens.
2. Check that `<new>` is not an entry of `plugins` in `.claude-plugin/marketplace.json`, not a key of `renames` and not a directory under `plugins/`. Do it before the move in step 5: afterwards the directory exists and the check fails.
3. Agree the name with Nery.

### 3. Find every use of the old name

1. Run `grep -rn '<old>' . --exclude-dir=.git --exclude-dir=node_modules`.
2. Split the results into live uses, which change, and dated history, which stays.

### 4. Find what depends on the old plugin

1. Search `plugins/*/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` for a `dependencies` entry that names `<old>`.
2. Search `plugins/` for symlinks that point into `plugins/<old>/`.
3. Plan the change of each dependent in step 5.
4. Tell Nery that plugins outside this repository may depend on `<old>` and cannot be checked from here.

### 5. Change the live uses

1. Move the directory: `git mv plugins/<old> plugins/<new>`.
2. Change `name` and `homepage` in `plugin.json`, the skill names, the README commands and badges, and the mentions in `docs/`.
3. Move its test folder: `git mv scripts/testers/<old> scripts/testers/<new>`.
4. Change the `dependencies` entries and symlinks found in step 4.

### 6. Register the rename

1. Add `"<old>": "<new>"` to the top-level `renames` map in `.claude-plugin/marketplace.json`.
2. When the plugin was renamed before, add a second entry and leave the first: Claude Code follows the chain from the oldest name.
3. Regenerate the marketplace file, then run its check.
4. Run `claude plugin validate --strict .`: it fails with `renames.<name>: chain does not resolve` when a chain cycles or ends anywhere other than `null` or a listed plugin.
5. Regenerate the README catalog.

### 7. Write the release notes content

1. Start the entry in `plugins/<new>/CHANGELOG.md` with `**Breaking:**`, and name the old and the new command in user language.
2. Tell users to run `/plugin install <new>@the-claude-factory` once.
3. Tell organizations that enable the plugin in managed settings to change `enabledPlugins` there.
4. Write the root changelog line under `### Changed`: `- **<new>** X.Y.Z — **Breaking:** renamed from <old>; one-line summary.`

### 8. Prepare the label

1. A rename needs a `plugin: <new>` label, as a new plugin does. The `plugin: <old>` label stays.
2. Show Nery the command, and write nothing until he orders it: `gh label create "plugin: <new>" --repo nerymurillohnd/the-claude-factory --color EDEDED --description "Issues about the <new> plugin" --force`.

### 9. Verify once released

1. Install `<new>` from `nerymurillohnd/the-claude-factory#main` in a throwaway configuration: `plugin list --json` shows the new version.
2. Install `<old>` the same way: it fails with `not found in marketplace`.
3. Confirm the old name's last tag and GitHub Release still exist: `gh release view <old>--v<last version>`.
4. Report to Nery what users receive and that the old tag and release are intact.
