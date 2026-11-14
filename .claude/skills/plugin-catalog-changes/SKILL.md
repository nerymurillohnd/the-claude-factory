---
name: plugin-catalog-changes
description: Renames, removes, deprecates or merges plugins in this marketplace without breaking existing installs, through the marketplace's renames map. Use whenever a plugin should get a new name, be retired, withdrawn or deprecated, or be folded into another plugin, or when someone asks what users see after a plugin disappears from the catalog, even if they only say "kill this plugin" or "combine these two".
---

# Plugin catalog changes

Users install, enable and configure a plugin by `name@the-claude-factory`, and that name is the key in their `enabledPlugins` and `pluginConfigs` settings. Changing or dropping a name without telling Claude Code breaks every existing install, so every one of these changes goes through the `renames` map in `.claude-plugin/marketplace.json`.

## How Claude Code handles it (official)

From code.claude.com/docs/en/plugins/publish (Rename or remove a plugin) and host-marketplace (Rename or remove a plugin; Work around what a marketplace can't do):

- For a different label only, set `displayName` in `plugin.json` and keep `name`. That is not a rename.
- `renames` maps each former name to its current name, or to `null` when the plugin is gone. After the push, a user who still has the old name enabled sees:
  - renamed: the plugin loads under the new name, `Renamed to "<new>" in the "the-claude-factory" marketplace` shows once, and Claude Code rewrites the key in the user, project and local settings. From a git-hosted marketplace it reports `Plugin "<new>" not cached` until the user runs `/plugin install <new>@the-claude-factory` once.
  - `null`: the key is dropped and `Removed from the "the-claude-factory" marketplace` shows.
  - enabled in managed settings: the notice recurs until an admin updates `enabledPlugins` there.
- `renames` is append-only history: keep old entries after everyone migrated, and add a second entry for a second rename, because Claude Code follows the chain from the oldest name.
- With `"forceRemoveDeletedPlugins": true`, Claude Code uninstalls, at each session start, every installed plugin that is neither listed nor renamed, from the user, project and local scopes, and flags it in `/plugin` as `Removed from marketplace`. Plugins installed only by managed settings stay. Without it, a removed plugin stays installed and reports `Plugin "<name>" not found in marketplace`. This marketplace sets it to `true` in `.claude-plugin/marketplace.json` (owner's decision, 2026-11-13); confirm it is still there with `jq '.forceRemoveDeletedPlugins' .claude-plugin/marketplace.json` before a removal.
- A user who removes a plugin by hand runs `claude plugin uninstall <plugin> [--scope <scope>] [--keep-data] [--prune]`. Uninstalling from the last scope deletes the plugin's options, secrets and data unless `--keep-data` is passed, and `--prune` also removes dependencies nothing else needs. When a removed plugin stores options or data, say this in the removal's line in the root `CHANGELOG.md`.
- A user who runs `claude plugin marketplace remove the-claude-factory` from the last scope that declares it uninstalls every plugin installed from it, and Claude Code deletes their saved options, secrets and data where it can; `claude plugin marketplace update` refreshes the listings without that loss (code.claude.com/docs/en/plugins/cli-reference, plugin marketplace remove).
- There is no deprecation state. Deprecating a plugin means removing its entry, mapping its name to `null`, and letting `forceRemoveDeletedPlugins` uninstall it.
- `claude plugin validate .` rejects a chain that cycles or that ends anywhere but `null` or a listed name, with `renames.<name>: chain does not resolve`. Several former names may point to one plugin (checked on Claude Code 2.1.323).

## Steps for every case

1. Confirm the case with the owner: rename, removal (deprecation is a removal), or merge into another plugin.
2. Find every use of the old name and change the live ones; dated history such as changelog entries and specs keeps the old name:
   ```bash
   grep -rn '<old>' . --exclude-dir=.git --exclude-dir=node_modules
   ```
3. Find what depends on the old plugin, and change each dependent first, since a dependency on a missing plugin fails to install:
   - `dependencies` that name `<old>`, in each `plugin.json` and in each marketplace entry. This prints one `dependent: <plugin> needs <name> <range>` line per declared dependency; any line whose `<name>` is `<old>` is a dependent:
     ```bash
     npm run release:status
     ```
   - symlinks into `plugins/<old>/` (`find plugins -type l`)
   Tell the owner that plugins in other repositories may depend on `<old>` and can't be checked from here.
4. Make the change for the case (sections below).
5. Check the map, and show the raw output:
   - `claude plugin validate --strict .` exits 0
   - `npm run check:consistency` exits 0. Its `PC-02` finding is a `renames` key still listed in `plugins`, which the validator doesn't catch; `PC-01` and `PC-08` catch a name, source or catalog row left behind.
6. Never reuse a retired name, and never delete the old tags or GitHub Releases: they are the history users and dependents resolve against.

## Rename

1. Choose `<new>`: kebab-case, not in `plugins`, not a key of `renames`, and no `plugins/<new>/` folder yet.
2. `git mv plugins/<old> plugins/<new>`, then change `name` in `plugin.json`, the marketplace entry's `name` and `source` (`./plugins/<new>`), any URL in `plugin.json` that contains `<old>`, and every other live use step 2 of Steps for every case found.
3. Add `"<old>": "<new>"` to `renames`.
4. Bump the plugin as a breaking change through the `plugin-versioning` skill (Minor in `0.x`, Major after). Its changelog entry starts with `**Breaking:**`, maps each old command to the new one, and tells users to run `/plugin install <new>@the-claude-factory` once.
5. Update the documents with the `docs-maintenance` skill: every command and name in the plugin's `README.md`, its catalog row in the root `README.md`, and the rename's line in the root `CHANGELOG.md`.
6. With the owner's authorization, run `npm run labels:sync -- --apply` so the `plugin: <new>` label exists; the old label stays.

## Removal or deprecation

1. Remove the entry from `plugins` in `marketplace.json`. Whether `plugins/<old>/` is deleted too is the owner's call.
2. Add `"<old>": null` to `renames`.
3. Update the documents with the `docs-maintenance` skill: remove the plugin's row from the root `README.md` catalog and the plugin from `PRIVACY.md`, and record the removal in the root `CHANGELOG.md` under `### Removed`. The removed plugin gets no version bump and no new tag.

## Merge into another plugin

1. Move the components into `plugins/<target>/`, check every moved symlink, then remove `<old>`'s entry and folder.
2. Compare the `userConfig` keys of both plugins: Claude Code moves `<old>`'s saved options to `<target>`, so a key that means something else in `<target>` is a breaking change to resolve first.
3. Add `"<old>": "<target>"` to `renames`.
4. Bump `<target>` through the `plugin-versioning` skill (at least Minor). Its changelog maps each old command to the new one and tells users to run `/plugin install <target>@the-claude-factory` once.
5. Update the documents with the `docs-maintenance` skill: `<target>`'s `README.md` for the components it gained, `<old>`'s removal from the root `README.md` catalog and from `PRIVACY.md`, and the merge's line in the root `CHANGELOG.md`.
6. After the release, run After the release and confirm `claude plugin list --json` shows `<target>` (see Version notes).

## After the release

Check what users receive in throwaway configurations, so your own stays untouched:

```bash
T="$(mktemp -d)"
env CLAUDE_CONFIG_DIR="${T}/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="${T}/cache" claude plugin marketplace add "nerymurillohnd/the-claude-factory#main"
env CLAUDE_CONFIG_DIR="${T}/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="${T}/cache" claude plugin install <old>@the-claude-factory
rm -rf "${T}"
npm run check:install -- --from main <new-or-target>
```

- installing `<old>` fails with `not found in marketplace`
- after a rename or a merge, `check:install` exits 0 for `<new-or-target>` (the new name, or the merge target): `claude plugin list --json` shows it at its new version with no `errors`, and the installed copy validates
- the old name's last tag and GitHub Release still exist: `gh api repos/nerymurillohnd/the-claude-factory/releases/tags/<old>--v<last version>` in a terminal session; in a cloud session, where `gh` is kept for search, the MCP tool `github:get_release_by_tag` (`owner: nerymurillohnd`, `repo: the-claude-factory`, `tag: <old>--v<last version>`).

## Version notes

On Claude Code 2.1.319, after a merge `claude plugin list` left `<target>` out and `claude plugin update` failed until the user ran `/plugin install <target>@the-claude-factory`. Unverified on later versions.
