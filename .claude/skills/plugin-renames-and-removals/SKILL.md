---
name: plugin-renames-and-removals
description: Use when a plugin of this marketplace is to be renamed or removed, before changing its name, its directory or its marketplace entry.
---

# Renaming or Removing a Plugin

## Scope

Follow this procedure only when a plugin is renamed or removed in `the-claude-factory`. It is complete on its own: it covers the change, the marketplace entry, the version, the changelogs, the checks, the PR and the release verification. Never rename or remove a plugin silently.

To change only the label users see in `/plugin`, set `displayName` in `plugin.json` and keep `name`: that is not a rename, and this procedure does not apply.

Run every command from the repository root. All paths are relative to it:
- Plugins live in `plugins/<plugin>/`; the manifest is `plugins/<plugin>/.claude-plugin/plugin.json`.
- Plugin changelog: `plugins/<plugin>/CHANGELOG.md`
- Root changelog: `CHANGELOG.md`
- Marketplace file: `.claude-plugin/marketplace.json` (top-level `renames` map)

## Why this matters

A rename or removal reaches users only through the `renames` map in `.claude-plugin/marketplace.json`. With that entry, Claude Code migrates existing installs instead of reporting the plugin as not found (`/en/plugins/host-marketplace`, "Migrate users with a renames map"). Without it, users of the old name are stranded.

## Rules

1. Register every rename or removal in the `renames` map. The map is append-only: add one entry per rename or removal, and never edit or delete an existing entry.
2. Leave dated history untouched: old changelog lines and specs keep the old name.
3. A rename changes the commands users type, so it is a breaking change. A removal has nothing to bump.
4. Version plugins only: never add a version or a tag to `.claude-plugin/marketplace.json`. Apply bumps with `node scripts/bump-version.mjs <plugin> <major|minor|patch>`, never by hand.
5. Never promote a plugin to `1.0.0` without Nery's explicit authorization. In `0.x` a breaking change bumps the minor; from `1.0.0` on it bumps the major.
6. Never tag by hand. `release.yml` creates the tags (format `<plugin>--v<version>`) after Validate succeeds on `main`, and it tags every plugin whose `plugin.json` version has no tag yet, not only the one you changed.
7. Never delete or move the old tag or its GitHub Release; they stay as history. The new name gets its own tag at release.
8. Never push or merge to `main` without first listing the untagged plugins and confirming with Nery (step 12). Never run `gh workflow run release.yml` while Validate is failing.
9. Do not write GitHub labels until Nery orders it.
10. Push, open a PR or merge only when Nery authorizes it. Merge only with all CI checks green and all review comments resolved.
11. Never reuse a retired name: `node scripts/new-plugin.mjs` refuses any name that is a key of `renames`.

## Procedure

### 1. Fix the case

Decide which one applies and keep using these names below:
- **Rename**: `<old>` becomes `<new>`.
- **Removal**: `<old>` is retired and nothing replaces it.
- **Merge**: `<old>` is retired and its components move into the existing plugin `<target>`, as `git-hygiene` moved into `github-operations` and `session-handoff` into `project-maintainer`.

### 2. Find every use of the old name

Run: `grep -rn '<old>' . --exclude-dir=.git --exclude-dir=node_modules`

Split the results into live uses (to change) and dated history (to leave): old changelog lines and specs.

### 3. Change the live uses

- **Rename**: move the directory with `git mv plugins/<old> plugins/<new>`, then change the live uses: `name` and `homepage` in `plugin.json`, skill names, the README commands and badges, the plugin's key in `scripts/evals-config.json`, its test folder (`git mv scripts/tests/<old> scripts/tests/<new>`) and its mentions in `docs/`.
- **Merge**: move the components into `plugins/<target>/` and change `<target>` as the `plugin-development` skill says, then delete `plugins/<old>/` as for a removal.
- **Removal**: delete `plugins/<old>/`, its `scripts/evals-config.json` entry and its `scripts/tests/<old>/` folder, and remove the live uses elsewhere (for example README and `docs/` mentions), so the marketplace generator no longer finds the plugin.

### 4. Register the change in the marketplace

1. Add the entry to the top-level `renames` map in `.claude-plugin/marketplace.json`:
   - Rename: `"<old>": "<new>"`
   - Removal: `"<old>": null`
   - Merge: `"<old>": "<target>"`
   - A plugin renamed again gets a second entry; never edit the first, because Claude Code follows the chain from the oldest name.
2. Run `node scripts/generators/marketplace.mjs`. It rebuilds `plugins` from `plugins/`, so the list shows the new name and no longer the old one.
3. Run `node scripts/generators/marketplace.mjs --check`. It fails while `plugins` does not match `plugins/`; if it fails, fix the cause and repeat.
4. Run `claude plugin validate --strict .`. It fails with `renames.<name>: chain does not resolve` when a chain cycles or ends anywhere other than `null` or a name in `plugins`.

### 5. Version the plugin (rename and merge)

For a removal, skip this step: there is nothing to bump. For a merge, `<target>` gained components: bump it as the `release-and-versioning` skill says, and in its changelog entry tell users of `<old>` which command replaces theirs. Then go to step 6.

1. Write the release notes first, under `## [Unreleased]` in `plugins/<new>/CHANGELOG.md`, following Keep a Changelog 2.0.0. Start the entry with `**Breaking:**` and name the old and the new command, in user language. Tell users to run `/plugin install <new>@the-claude-factory` once: a marketplace added from a git repository reports `Plugin "<new>" not cached` until they do. The bump script fails when `[Unreleased]` is empty.
2. Run `node scripts/bump-version.mjs <new> <minor|major>`: `minor` during `0.x`, `major` from `1.0.0` on. The script turns `[Unreleased]` into the dated section and regenerates the README catalog.
3. Read its output line (`<new>: <old version> → <new version>`).

### 6. Regenerate the catalog

Run `node scripts/generators/catalog.mjs`. A removal needs it explicitly; for a rename the bump already did it and running it again changes nothing.

### 7. Add the root changelog line

1. In `CHANGELOG.md` (root), use the structure: `## YYYY-MM-DD` headings, newest first; under each, change-type headings (`### Added`, `### Changed`, `### Fixed`, `### Removed`); under each, one line per event. Create the date heading and the change-type heading if they are missing.
2. Put the line under today's date:
   - Rename, under `### Changed`: `- **<new>** X.Y.Z — renamed from <old>; one-line summary.`
   - Removal, under `### Removed`: `- **<old>** retired: one-line reason.`
   - Merge, under `### Removed`: `- **<old>** retired: its <what> is now the `<skill>` skill of **<target>**, and the marketplace renames existing installs. Type `/<target>:<skill>` where you typed `/<old>:<skill>`.` The bump of `<target>` gets its own line under its change type.

### 8. Check the GitHub label and installed copies

1. Run `node scripts/sync-labels.mjs --dry-run`. A rename needs a `plugin: <new>` label, as a new plugin does; the `plugin: <old>` label stays, as the labels of retired plugins do. Tell Nery what the dry run shows. Do not write labels until he orders it.
2. Removal: tell Nery that `.claude-plugin/marketplace.json` does not set `forceRemoveDeletedPlugins`, so the removed plugin stays installed on users' machines and reports `Plugin "<old>" not found in marketplace` when a session loads it. Setting it uninstalls every removed plugin at session start; that is his decision.

### 9. Commit

Commit as one signed commit (`git commit -S`): the directory change, the `renames` entry, the regenerated `plugins` list and catalog, the plugin changelog and bump (rename), and the root changelog line. The commit message says what changed and why.

### 10. Run the checks and show their raw output

The version-bump and repo checks read committed changes only (`origin/main...HEAD`), so run them after the commit.

1. `git fetch origin main`
2. `node scripts/check-version-bump.mjs origin/main`
3. `node scripts/check-repo.mjs`
4. `node scripts/generators/marketplace.mjs --check`
5. `node scripts/generators/catalog.mjs --check`
6. `claude plugin validate --strict .`
7. If `plugin-consistency` has not run since your last edit and did not invoke you, invoke it now.

If any check fails, fix the cause, amend the commit (`git commit -S --amend`) and run all the checks again.

### 11. Push and open the PR

With Nery's authorization only: push the branch and open the PR, applying only the labels the repository already has; the one exception is the `plugin: <new>` label from step 8, once Nery orders it.

### 12. Before any merge or push to `main`

1. List the untagged plugins: for each plugin, compare the version in `plugin.json` with `git tag -l '<plugin>--v<version>'`. A plugin with no matching tag is untagged.
2. Show Nery the list and confirm each is meant to ship; the next green push of `main` publishes every one of them.
3. If the PR is still open on a later day than the root changelog line, move the line to that day's section now, before the merge, never in a push after the merge.
4. Merge only when Nery orders it.

### 13. Verify after the merge

1. Take the merge commit's SHA: `gh pr view <n> --json mergeCommit`.
2. Wait until `gh run list --workflow validate.yml --commit <sha>` shows the run completed.
3. Read the release run: `gh run list --workflow release.yml --commit <sha>`. It starts only from a Validate run that succeeded on a `push` to `main`. No run while Validate is still running is not a failure. A missing run after Validate succeeded is unexplained: read the trigger in `release.yml` before running anything.
4. Rename: print the expected tag with `node scripts/release-notes.mjs <new> --tag`, then confirm it exists with `gh release view <new>--v<version>`.
5. Confirm the old tag and its GitHub Release still exist unchanged: `gh release list --limit 10`. For a removal, no new tag is expected.
6. Confirm no other plugin was tagged by the same run unless intended.
7. Report to Nery: the tag and release exist (rename), the old ones are intact, nothing unintended was tagged.

### 14. Recover from a failed Validate

1. If Validate failed on `main`, nothing is tagged.
2. Fix the cause first, in a new PR.
3. The next green push of `main` tags everything still untagged, so the fix's merge releases it without a manual run.
4. Run `gh workflow run release.yml` only when Validate passed and no release run exists, and only after Nery says so: it tags and publishes.
5. An instruction like "súbelo ya" with a failed Validate does not skip steps 1 to 4.
