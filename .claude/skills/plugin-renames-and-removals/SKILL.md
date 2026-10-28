---
name: plugin-renames-and-removals
description: Use when a plugin of this marketplace is to be renamed, merged into another plugin, removed, retired or deprecated, before changing its name, its directory or its marketplace entry.
---

# Renaming or Removing a Plugin

## Scope

Follow this procedure only when a plugin is renamed or removed in `the-claude-factory`. It is complete on its own: it covers the change, the marketplace entry, the version, the changelogs, the checks, the PR and the release verification. Never rename or remove a plugin silently.

To change only the label users see in `/plugin`, set `displayName` in `plugin.json` and keep `name`: that is not a rename, and this procedure does not apply.

Claude Code has no deprecation state. Deprecating, withdrawing or retiring a plugin is a removal: remove the entry, map the name to `null` in `renames`, and decide on `forceRemoveDeletedPlugins` (`/en/plugins/host-marketplace`, "Work around what a marketplace can't do").

Run every command from the repository root. All paths are relative to it:
- Plugins live in `plugins/<plugin>/`; the manifest is `plugins/<plugin>/.claude-plugin/plugin.json`.
- Plugin changelog: `plugins/<plugin>/CHANGELOG.md`
- Root changelog: `CHANGELOG.md`
- Marketplace file: `.claude-plugin/marketplace.json` (top-level `renames` map)

## Why this matters

A rename or removal reaches users only through the `renames` map in `.claude-plugin/marketplace.json`. With that entry, Claude Code migrates existing installs instead of reporting the plugin as not found (`/en/plugins/host-marketplace`, "Migrate users with a renames map"). Without it, users of the old name are stranded.

After the push, a user who still has the old name enabled sees one of these results:
- **Rename or merge** (`"<old>": "<new>"`): the plugin loads under its new name, `claude plugin list` and `/plugin` show `Renamed to "<new>" in the "the-claude-factory" marketplace` once, and Claude Code rewrites the old key to the new one in `enabledPlugins` and `pluginConfigs` in the user, project and local settings scopes. Because this marketplace is a git repository, the plugin reports `Plugin "<new>" not cached at <path>` until the user runs `/plugin install <new>@the-claude-factory` once.
- **Removal** (`"<old>": null`): the old key is dropped from those scopes and the user sees `Removed from the "the-claude-factory" marketplace`.
- **Enabled in managed settings**: Claude Code cannot rewrite managed settings, so the notice recurs until an admin updates `enabledPlugins` there.

`renames` migrates only existing installs. A new install by the old name fails: `claude plugin install git-hygiene@the-claude-factory` printed `Plugin "git-hygiene" not found in marketplace "the-claude-factory"` on 2026-10-25, though `git-hygiene` maps to `github-operations`. Every README, doc and template that names the old plugin or its commands changes in the same PR.

## Rules

1. Register every rename or removal in the `renames` map. The map is append-only: add one entry per rename or removal, and never edit or delete an existing entry.
2. Leave dated history untouched: old changelog lines and specs keep the old name.
3. A rename changes the commands users type, so it is a breaking change. A removal has nothing to bump.
4. Version plugins only: never add a version or a tag to `.claude-plugin/marketplace.json`; `check-marketplace-unversioned.py` enforces it in step 10. Apply bumps with `.claude/skills/plugin-renames-and-removals/scripts/bump-version.py <plugin> <major|minor|patch>`, never by hand, then run `node scripts/generators/catalog.mjs`: the bump does not regenerate the README catalog.
5. Never promote a plugin to `1.0.0` without Nery's explicit authorization. In `0.x` a breaking change bumps the minor; from `1.0.0` on it bumps the major.
6. Never tag by hand. `release.yml` creates the tags (format `<plugin>--v<version>`) after Validate succeeds on `main`, and it tags every plugin whose `plugin.json` version has no tag yet, not only the one you changed.
7. Never delete or move the old tag or its GitHub Release; they stay as history. The new name gets its own tag at release.
8. Never merge a PR or push to `main` without listing what it publishes and confirming with Nery (step 12). Never run `gh workflow run release.yml` while Validate is failing.
9. Do not write GitHub labels until Nery orders it.
10. Push, open a PR or merge only when Nery authorizes it. Merge only with all CI checks green, all review comments resolved and a `github-operations:pr-tracker` report with no issues.
11. Never reuse a retired name: this repository's plugin scaffold refuses any name that is a key of `renames`, and for a rename `check-new-name.py <new>` refuses a retired, listed or malformed name in step 3.

## Scripts

This skill's scripts live in `.claude/skills/plugin-renames-and-removals/scripts/`. Each one is Python with its own shebang: run it by path from the repository root, never through `python3` or `node`. Each reads and writes only what its row says, and none uses the network.

| Script | Run at | What it does | Fails when |
| :-- | :-- | :-- | :-- |
| `check-new-name.py <new>` | Step 3, rename only, before `git mv` | Reads `.claude-plugin/marketplace.json` and checks whether `plugins/<new>` exists | `<new>` is not kebab-case, is already listed, is a key of `renames`, or `plugins/<new>` exists |
| `bump-version.py <plugin> <major\|minor\|patch>` | Step 5, rename and merge | Writes the new version to `plugin.json` and moves `[Unreleased]` of `CHANGELOG.md` into the dated section with its link references | `[Unreleased]` is missing or empty, the level is unknown, the plugin has no manifest or version, or the target is `marketplace`; on a failure it writes nothing |
| `plugin-labels.py` | Step 8.1 | Prints the `gh label create` command of each listed plugin's `plugin: <name>` label; it runs none of them and calls no GitHub API | `marketplace.json` cannot be read |
| `check-version-bump.py origin/main` | Step 10, after the step 9 commit | Reads the committed diff `origin/main...HEAD` and each changed plugin's version at `origin/main` | A plugin's files changed, other than its `README.md` alone, without the next version (exactly one patch, minor or major step above `origin/main`; a skipped version fails) or without a `CHANGELOG.md` section for it. A step from `0.x` to `1.0.0` passes with a `!` note that it needs Nery's authorization. A renamed plugin is compared with its old name's version: a `renames` entry added since `origin/main`, or a `plugin.json` git sees moved, marks the rename; its patch step fails, since a rename is breaking, and a move without its `renames` entry fails |
| `check-marketplace-unversioned.py` | Step 10 | Reads `.claude-plugin/marketplace.json` | It has a top-level `version`, a `metadata.version` or a `version` on any entry |
| `check-changelog-entry.py <plugin>` | Step 10, rename and merge | Reads the plugin's `plugin.json` and `CHANGELOG.md` | The section of the `plugin.json` version is missing or empty |
| `release-tag.py <plugin>` | Step 13.4, rename and merge | Prints `<plugin>--v<version>` from `plugin.json` | The plugin has no version |

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

- **Rename**: first run `.claude/skills/plugin-renames-and-removals/scripts/check-new-name.py <new>`; if it fails, choose another name with Nery. Then move the directory with `git mv plugins/<old> plugins/<new>`, then change the live uses: `name` and `homepage` in `plugin.json`, skill names, the README commands and badges, its test folder (`git mv scripts/testers/<old> scripts/testers/<new>`) and its mentions in `docs/`.
- **Merge**: move the components into `plugins/<target>/` and change `<target>` as the official docs page of each moved component type says, then delete `plugins/<old>/` as for a removal. `<target>` keeps its category, unless the merge moves a hooks module in or out of it or changes what it is for: then check it with `plugin-categories` (situations C and B) before step 4; this procedure keeps the bump and the changelog.
- **Removal**: delete `plugins/<old>/`, its `scripts/testers/<old>/` folder, and remove the live uses elsewhere (for example README and `docs/` mentions), so the marketplace generator no longer finds the plugin.

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

For a removal, skip this step: there is nothing to bump. For a merge, `<target>` gained components: write its notes under `## [Unreleased]` in `plugins/<target>/CHANGELOG.md` and bump it with `.claude/skills/plugin-renames-and-removals/scripts/bump-version.py <target> minor`, because it gained components (from `1.0.0` on, `major` when the merge breaks anything users of `<target>` rely on); in its changelog entry tell users of `<old>` which command replaces theirs. Claude Code moves each user's `pluginConfigs` entry of `<old>` to `<target>`: compare the `userConfig` keys of both plugins, and treat a key that `<target>` also declares with another meaning as a breaking change to resolve before the merge. **Unverified:** what Claude Code does when a user has both `<old>` and `<target>` installed. Then go to step 6.

1. Write the release notes first, under `## [Unreleased]` in `plugins/<new>/CHANGELOG.md`, following Keep a Changelog 2.0.0. Start the entry with `**Breaking:**` and name the old and the new command, in user language. Tell users to run `/plugin install <new>@the-claude-factory` once, because the plugin reports `Plugin "<new>" not cached` until they do, and that an organization that enables the plugin in managed settings must change `enabledPlugins` there. The bump script fails when `[Unreleased]` is empty.
2. Run `.claude/skills/plugin-renames-and-removals/scripts/bump-version.py <new> <minor|major>`: `minor` during `0.x`, `major` from `1.0.0` on. The script turns `[Unreleased]` into the dated section; step 6 regenerates the README catalog.
3. Read its output line (`<new>: <old version> → <new version>`).

### 6. Regenerate the catalog

Run `node scripts/generators/catalog.mjs` in every case: the bump does not regenerate it, and a removal drops the plugin from it.

### 7. Add the root changelog line

1. In `CHANGELOG.md` (root), use the structure: `## YYYY-MM-DD` headings, newest first; under each, change-type headings (`### Added`, `### Changed`, `### Fixed`, `### Removed`); under each, one line per event. Create the date heading and the change-type heading if they are missing.
2. Put the line under today's date:
   - Rename, under `### Changed`: `- **<new>** X.Y.Z — renamed from <old>; one-line summary.`
   - Removal, under `### Removed`: `- **<old>** retired: one-line reason.`
   - Merge, under `### Removed`: ``- **<old>** retired: its <what> is now the `<skill>` skill of **<target>**, and the marketplace renames existing installs. Type `/<target>:<skill>` where you typed `/<old>:<skill>`.`` The bump of `<target>` gets its own line under its change type.

### 8. Check the GitHub label and installed copies

1. Run `.claude/skills/plugin-renames-and-removals/scripts/plugin-labels.py`. A rename needs a `plugin: <new>` label, as a new plugin does; the `plugin: <old>` label stays, as the labels of retired plugins do. Tell Nery which `plugin: <new>` command it prints. Do not write labels until he orders it.
2. Removal: tell Nery that `.claude-plugin/marketplace.json` does not set `forceRemoveDeletedPlugins`. The `null` entry drops the old key from users' settings, but the docs do not say that it deletes the installed copy. With `"forceRemoveDeletedPlugins": true`, Claude Code uninstalls at each session start every plugin that is neither listed in `plugins` nor in `renames`, from the user, project and local scopes, and lists it under **Flagged** in `/plugin` as `Removed from marketplace`; plugins installed only by managed settings stay. A plugin that stays installed also keeps on the user's machine its data directory and the options and secrets saved for it, which an uninstall deletes (`/en/plugins/cli-reference`, "What an uninstall deletes and keeps"); say so when the plugin declares `userConfig` or writes to `${CLAUDE_PLUGIN_DATA}`. Setting the field is his decision, and it applies to every later removal too.

### 9. Commit

Commit as one signed commit (`git commit -S`): the directory change, the `renames` entry, the regenerated `plugins` list and catalog, the plugin changelog and bump (rename), and the root changelog line. The commit message says what changed and why.

### 10. Run the checks and show their raw output

Run them after the commit in step 9: `check-version-bump.py` reads committed changes only (`origin/main...HEAD`).

`<plugin>` below is `<new>` for a rename and `<target>` for a merge; a removal skips the steps that name it, since it leaves no plugin to check.

1. `git fetch origin main` and `S=.claude/skills/plugin-renames-and-removals/scripts`
2. `$S/check-version-bump.py origin/main`
3. `$S/check-marketplace-unversioned.py`
4. `$S/check-changelog-entry.py <plugin>`
5. `node scripts/generators/marketplace.mjs --check`
6. `node scripts/generators/catalog.mjs --check`
7. `claude plugin validate --strict plugins/<plugin>`, then `claude plugin validate --strict .` for the marketplace.
8. `git lfs ls-files --include='plugins/<plugin>/**'` prints nothing and exits 0 (`git lfs ls-files -- <path>` reads the path as a ref and fails): a git clone never downloads LFS content, so an LFS file reaches users as a pointer file (`/en/plugins/host-marketplace`, "Keep plugin files out of Git LFS").
9. `find plugins/<plugin> -type l` lists every symlink, and each must resolve inside `plugins/<plugin>/`: a link elsewhere in the repository is copied as its target's content, and a link outside it is skipped without a warning (`/en/plugins/host-marketplace`, "Share files within a marketplace with symlinks"). For a merge, check the moved components most closely: a link that resolved inside `plugins/<old>/` now points at a deleted directory.
10. Read the renamed or target plugin's `README.md`, `CHANGELOG.md` and `plugin.json` side by side and make them agree with the change: the components, commands, prerequisites and network calls the README states, the Compatibility rows, and the version each file shows. A script passing is not this check.

If any check fails before the push, fix the cause, amend the commit (`git commit -S --amend`) and run all the checks again. After the push, commit the fix as a new signed commit instead: never amend or force-push a pushed commit.

### 11. Push and open the PR

With Nery's authorization only: push the branch and open the PR, applying only the labels the repository already has; the one exception is the `plugin: <new>` label from step 8, once Nery orders it.

### 12. Before any merge or push to `main`

1. List what the merge publishes: the plugins whose `plugin.json` version differs from `origin/main` (`git diff --name-only origin/main...HEAD -- 'plugins/*/.claude-plugin/plugin.json'`, then compare the versions), the name that leaves `plugins`, and the versions on `origin/main` that still have no tag (`plugin.json` version against `git tag -l '<plugin>--v<version>'`). Users receive the rename or removal as soon as the merge lands.
2. Show Nery the lists and confirm each change is meant to ship.
3. If the PR is still open on a later day than the root changelog line, move the line to that day's section now, before the merge, never in a push after the merge.
4. Rename or merge: install `<new>` (or `<target>`) the way a user without a GitHub SSH key gets it, from the pushed PR branch over HTTPS, in a throwaway configuration that leaves Nery's settings and plugins untouched; make `B` with `mktemp -d` in the session scratchpad:
   ```bash
   iso() { local t="$1"; shift; env -u CLAUDE_CODE_PLUGIN_DIRS CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1 CLAUDE_CONFIG_DIR="$t/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="$t/plugins" claude "$@"; }
   B="$(mktemp -d)"
   iso "$B" plugin marketplace add nerymurillohnd/the-claude-factory#<branch>
   iso "$B" plugin install <new>@the-claude-factory
   iso "$B" plugin list --json
   iso "$B" plugin install <old>@the-claude-factory
   ```
   `plugin list --json` must show the new version, and the last command must fail with `not found in marketplace`. Delete `B` afterwards.
5. Merge only when Nery orders it.

### 13. Verify after the merge

1. Take the merge commit's SHA: `gh pr view <n> --json mergeCommit`.
2. Wait until `gh run list --workflow validate.yml --commit <sha>` shows the run completed.
3. Read the release run: `gh run list --workflow release.yml --commit <sha>`. It starts only from a Validate run that succeeded on a `push` to `main`. No run while Validate is still running is not a failure. A missing run after Validate succeeded is unexplained: read the trigger in `release.yml` before running anything.
4. Rename or merge: print the expected tag with `.claude/skills/plugin-renames-and-removals/scripts/release-tag.py <new>` (or `<target>`, whose bump in step 5 gets its own tag), then confirm it exists with `gh release view <new>--v<version>` (or `<target>--v<version>`) and matches the printed tag.
5. Confirm the old name's last tag and GitHub Release still exist: `gh release view <old>--v<last version>`. For a removal, no new tag is expected.
6. Confirm no other plugin was tagged by the same run unless intended: `gh run view <run-id> --log | grep -oE 'Released [a-z0-9-]+--v[0-9.]+'` lists every tag that run published.
7. Repeat step 12.4 with `#main` in place of `#<branch>`: for a rename or merge, `plugin list --json` shows the new version of `<new>` (or `<target>`); in every case, installing `<old>` fails, because `<old>` is no longer in `plugins`.
8. Report to Nery: what users receive, the new tag and release exist (rename or merge), the old ones are intact, and nothing unintended was tagged.

### 14. Recover from a failed Validate

1. If Validate failed on `main`, nothing is tagged, but users who update already receive the rename or removal: tell Nery at once.
2. Fix the cause first, in a new PR, with its own bump when a plugin version must change to reach users.
3. The next green push of `main` tags everything still untagged, so the fix's merge releases it without a manual run.
4. Run `gh workflow run release.yml` only when Validate passed and no release run exists, and only after Nery says so: it tags and publishes.
5. An instruction like "súbelo ya" with a failed Validate does not skip steps 1 to 4.
