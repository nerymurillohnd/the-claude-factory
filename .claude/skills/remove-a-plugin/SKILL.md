---
name: remove-a-plugin
description: Use to remove, retire or deprecate a plugin of this marketplace, or to merge it into another plugin, so existing installs migrate through the renames map.
---

# Remove a plugin

Remove a plugin from `the-claude-factory`, or merge it into another plugin. The marketplace is hosted in a public GitHub repository and its plugins are relative-path entries (`./plugins/<plugin>`). Claude Code has no deprecation state, so deprecating, withdrawing and retiring are all a removal. Users learn about it only through the `renames` map in `.claude-plugin/marketplace.json`.

Two cases, named below:
- **Removal**: `<old>` is retired and nothing replaces it.
- **Merge**: `<old>` is retired and its components move into the existing plugin `<target>`.

## Rules

1. Register every removal in the `renames` map. The map is append-only: add one entry per removal, and never edit or delete an existing one.
2. Never remove a plugin while another plugin depends on it or links to it. Change the dependent first.
3. Leave dated history untouched: old changelog lines and specs keep the old name.
4. Never reuse a retired name.
5. Never delete or move the old tag or its GitHub Release. They stay as history.
6. Setting `forceRemoveDeletedPlugins` is Nery's decision.

## What users see after the push

- Removal (`"<old>": null`): Claude Code drops the old key from `enabledPlugins` and `pluginConfigs` and shows `Removed from the "the-claude-factory" marketplace`.
- Merge (`"<old>": "<target>"`): Claude Code rewrites the old key to `<target>` and shows the rename notice once. Each user runs `/plugin install <target>@the-claude-factory` once if `<target>` is not cached.
- An organization that enables the plugin in managed settings sees the notice on every session until an administrator changes `enabledPlugins` there.
- A new install by the old name fails with `not found in marketplace`.

## Steps

### 1. Identify the case

Decide removal or merge, and keep using `<old>` and `<target>` below.

### 2. Find every use of the old name

1. Run `grep -rn '<old>' . --exclude-dir=.git --exclude-dir=node_modules`.
2. Split the results into live uses, which change, and dated history, which stays.

### 3. Find what depends on the old plugin

1. Search `plugins/*/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` for a `dependencies` entry that names `<old>`.
2. Search `plugins/` for symlinks that point into `plugins/<old>/`.
3. Stop and change each dependent first (rule 2).
4. Tell Nery that plugins outside this repository may depend on `<old>` and cannot be checked from here.

### 4. Change the live uses

1. Removal: delete `plugins/<old>/` and `scripts/testers/<old>/`, then remove the live uses elsewhere, such as README and `docs/` mentions, so the marketplace generator no longer finds the plugin.
2. Merge: move the components into `plugins/<target>/` and change `<target>` as the official docs page of each moved component type says, then delete `plugins/<old>/` as for a removal.
3. Merge: check every moved symlink. One that resolved inside `plugins/<old>/` now points at a deleted directory.
4. Merge: keep `<target>`'s category, unless the merge moves a hooks module in or out of it or changes what it is for. In that case, settle its category with Nery first.

### 5. Check the merge for configuration clashes

1. Compare the `userConfig` keys of `<old>` and `<target>`: Claude Code moves each user's `pluginConfigs` entry of `<old>` to `<target>`.
2. Treat a key that `<target>` also declares with another meaning as a breaking change, and resolve it before the merge.
3. Tell Nery that what Claude Code does when a user has both plugins installed is unverified.

### 6. Register the removal

1. Add the entry to the top-level `renames` map: `"<old>": null` for a removal, `"<old>": "<target>"` for a merge.
2. Regenerate the marketplace file, then run its check.
3. Run `claude plugin validate --strict .`: it fails with `renames.<name>: chain does not resolve` when a chain cycles or ends anywhere other than `null` or a listed plugin.
4. Regenerate the README catalog, which drops the plugin.

### 7. Write the release notes content

1. Removal: `<old>` has no version to bump and no changelog to write.
2. Merge: write the notes of `<target>` in `plugins/<target>/CHANGELOG.md`, and tell users of `<old>` which command replaces theirs.
3. Write the root changelog line under `### Removed`:
   - Removal: `- **<old>** retired: one-line reason.`
   - Merge: `` - **<old>** retired: its <what> is now the `<skill>` skill of **<target>**, and the marketplace renames existing installs. Type `/<target>:<skill>` where you typed `/<old>:<skill>`. ``

### 8. Tell Nery about installed copies

1. State that `.claude-plugin/marketplace.json` does not set `forceRemoveDeletedPlugins`.
2. Explain that the `null` entry drops the old key from users' settings, and that the docs do not say it deletes the installed copy.
3. Explain that with `"forceRemoveDeletedPlugins": true`, Claude Code uninstalls at each session start every plugin that is neither listed in `plugins` nor in `renames`, from the user, project and local scopes. It lists the plugin under **Flagged** in `/plugin` as `Removed from marketplace`, and plugins installed only by managed settings stay.
4. Add that a plugin which stays installed keeps its data directory and the options and secrets saved for it, which an uninstall deletes. Say so when the plugin declares `userConfig` or writes to `${CLAUDE_PLUGIN_DATA}`.
5. Remind him that the field applies to every later removal too.

### 9. Verify once released

1. Install from `nerymurillohnd/the-claude-factory#main` in a throwaway configuration: installing `<old>` fails with `not found in marketplace`.
2. Merge: `plugin list --json` shows the new version of `<target>`.
3. Confirm the old name's last tag and GitHub Release still exist: `gh release view <old>--v<last version>`.
4. Removal: confirm no new tag was created for it.
5. Report to Nery what users receive and that the old tag and release are intact.
