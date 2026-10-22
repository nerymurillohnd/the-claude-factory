# Renaming or removing a plugin

Read from step 4 of `release-and-versioning`, only when a plugin is renamed or removed.

1. List every place that uses the old name: `grep -rn '<old>' . --exclude-dir=.git`. Change the live ones (directory, `plugin.json` `name` and `homepage`, skill names, the README commands and badges, the `marketplace.json` entry and `source`); leave dated history such as old changelog lines and specs.
2. Add `"renames": { "old": "new" }` to `.claude-plugin/marketplace.json`, or `"old": null` for a removal, and make `plugins` list the new name and no longer the old one. `check-repo.mjs` fails otherwise.
3. A rename changes the commands users type, so it is breaking: in `0.x` bump the new name by minor with `**Breaking:**` in its changelog, naming the old and new command. A removal has nothing to bump.
4. Add the root `CHANGELOG.md` line: under `### Removed` for a retirement or removal, as the file does today, and under `### Changed` for a plain rename. Run `node scripts/sync-labels.mjs --dry-run` and tell Nery if the `plugin: <name>` label needs to change; writing labels waits for his order.
5. The new name gets its own tag at release; the old tag and its GitHub Release stay as history.
