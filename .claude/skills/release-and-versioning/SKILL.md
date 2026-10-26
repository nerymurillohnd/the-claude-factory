---
name: release-and-versioning
description: Use when a plugin of this marketplace is published for the first time or changed, to choose its version bump, write its release notes, check it before the merge and confirm what users receive after it.
---

# Versioning and Releases

## Scope

Follow this procedure whenever a plugin is published for the first time or changes in `the-claude-factory`, to decide whether it needs a version bump and to carry the change through release. Renaming, removing or merging a plugin is outside this procedure.

Run every command from the repository root. All paths are relative to it:
- Plugin manifest (holds the version): `plugins/<plugin>/.claude-plugin/plugin.json`
- Plugin changelog: `plugins/<plugin>/CHANGELOG.md`
- Plugin README: `plugins/<plugin>/README.md`
- Root changelog: `CHANGELOG.md`
- Marketplace file: `.claude-plugin/marketplace.json`

## Why this matters

This marketplace is a GitHub repository, and each plugin is a relative-path entry inside it (`./plugins/<plugin>`). Users add it as `nerymurillohnd/the-claude-factory`, which clones the repository's default branch, `main`. For that setup (`/en/plugins/loading`, "How Claude Code computes the version"; `/en/plugins/host-marketplace`, "Release a new version"):

- The `version` in `plugin.json` is the version Claude Code computes for the plugin, and it names the cached copy (`cache/the-claude-factory/<plugin>/<version>/`). Users get a new copy only when that string changes and they update: `claude plugin update <plugin>@the-claude-factory`, the `/plugin` update, or auto-update, which is off by default for this marketplace.
- A change merged without a bump never reaches existing installs, while a new install gets it under the same version: two different copies carry one version.
- The release happens at the merge: what `main` holds is what the next update fetches. The PR's CI is the last gate before users; Validate on `main` and the release run come after users can already fetch the change.
- Auto-update is off by default, so most users get a version only when they ask for it, and keep it until they update again. A defect stays on their machines, and its fix reaches them only as a new version.
- Claude Code reports no usage and no errors back to the author (`/en/plugins/measure`, "Check whether a plugin is used"). Issues are the only signal, so every check happens before the merge.
- A plugin in our own marketplace shows users no context cost before they install it (`/en/plugins/measure`, "Cost shown to users before install"). Its always-on tokens are added to every session of every user who enables it, so this procedure measures them.
- The `<plugin>--v<version>` tag does not deliver the plugin. Plugin dependency ranges resolve against it, and for a relative-path plugin the tag lives in the marketplace repository, on a commit whose `plugin.json` holds that version (`/en/plugins/dependencies`, "Release a plugin that others depend on"). The GitHub Release carries the notes for people.
- Claude Code does not check the value against SemVer; SemVer is this project's convention (`/en/plugins/manifest-reference`, "version").

## Rules

1. Version plugins only. Never add a version or a tag to `.claude-plugin/marketplace.json`; `check-marketplace-unversioned.py` enforces it in step 6.
2. Use SemVer (`MAJOR.MINOR.PATCH`) and choose the bump by user-facing impact.
3. Apply every bump with `.claude/skills/release-and-versioning/scripts/bump-version.py <plugin> <major|minor|patch>`, never by hand. The script also turns `[Unreleased]` into the dated section with its link references; a hand edit leaves them out of step. It does not regenerate the README catalog, which shows the version: run `node scripts/generators/catalog.mjs` right after it.
4. A `0.x` version makes no interface-stability promise; `1.0.0` does. Stay in `0.x` while a plugin is new. Never promote a plugin to `1.0.0` without Nery's explicit authorization.
5. Never tag by hand. `release.yml` creates the tags (format `<plugin>--v<version>`) on the commit Validate checked, after Validate succeeds on `main`, and it tags every plugin whose `plugin.json` version has no tag yet, not only the one you changed. The tags are unsigned (ADR_2026-10-25_release-tags-are-created-unsigned-by-ci).
6. Never merge a PR or push to `main` without listing what it publishes and confirming with Nery that each plugin is meant to ship (step 8).
7. Never run `gh workflow run release.yml` while the Validate workflow is failing.
8. The plugin PR carries the release: the bump, the changelog entries and the regenerated catalog go in that PR as one signed commit, beside the PR's other commits. Nothing is committed for the release after the merge.
9. Push, open a PR or merge only when Nery authorizes it. Merge only with all CI checks green, all review comments resolved and a `github-operations:pr-tracker` report with no issues.
10. A published plugin's `name` is permanent. Choose a new plugin's name to keep: kebab-case, and never a key of `renames`. Changing it later is a rename, outside this procedure.
11. When another plugin of this marketplace declares a version range on the changed plugin in its `dependencies`, the new version must still satisfy that range, or the dependent plugin gets its own change. Today no plugin declares `dependencies`: check with `jq '.dependencies // empty' plugins/*/.claude-plugin/plugin.json`.

## Scripts

This skill's scripts live in `.claude/skills/release-and-versioning/scripts/`. Each one is Python with its own shebang: run it by path from the repository root, never through `python3` or `node`. Each reads and writes only what its row says, and none uses the network.

| Script | Run at | What it does | Fails when |
| :-- | :-- | :-- | :-- |
| `bump-version.py <plugin> <major\|minor\|patch>` | Step 3, once per changed plugin | Writes the new version to `plugin.json` and moves `[Unreleased]` of `CHANGELOG.md` into the dated section with its link references | `[Unreleased]` is missing or empty, the level is unknown, the plugin has no manifest or version, or the target is `marketplace`; on a failure it writes nothing |
| `check-version-bump.py origin/main` | Step 6, after the step 5 commit | Reads the committed diff `origin/main...HEAD` and each changed plugin's version at `origin/main` | A plugin's files changed, other than its `README.md` alone, without the next version (exactly one patch, minor or major step above `origin/main`; a skipped version fails) or without a `CHANGELOG.md` section for it. A step from `0.x` to `1.0.0` passes with a `!` note that it needs Nery's authorization (rule 4) |
| `check-marketplace-unversioned.py` | Step 6 | Reads `.claude-plugin/marketplace.json` | It has a top-level `version`, a `metadata.version` or a `version` on any entry |
| `check-changelog-entry.py <plugin>` | Step 6, for each changed plugin | Reads the plugin's `plugin.json` and `CHANGELOG.md` | The section of the `plugin.json` version is missing or empty |
| `release-notes.py <plugin> [--tag]` | Step 9 | Prints the tag `<plugin>--v<version>` with `--tag`, otherwise the notes `release.yml` publishes | The version or its changelog section is missing |

## Procedure

### 1. Choose the bump level

Read the diff (`git diff origin/main...HEAD`) and choose the level by what changes for the user. When one PR mixes levels, take the highest for each affected plugin.

| Bump | When |
| :-- | :-- |
| **major** | Breaking: a removed or renamed skill, agent or command; changed configuration keys; a new mandatory dependency; a change to behavior users rely on |
| **minor** | A new component, option or capability, backward compatible |
| **patch** | A backward-compatible bug fix, prompt wording improvement, performance improvement or internal refactor with the same behavior |

- During `0.x`, a breaking change bumps **minor**, not major, and its changelog entry starts with `**Breaking:**`.
- From `1.0.0` on, a breaking change bumps **major**.
- If a plugin's changes are limited to its own `README.md`, it needs no bump: skip steps 2 and 3 for that plugin. Every other change requires a bump, a `CHANGELOG.md`-only change included.
- If the PR changes only `.claude-plugin/marketplace.json` (no plugin), no bump applies: skip steps 2 and 3 and write the marketplace line in step 4.
- A new plugin starts at the `0.1.0` that this repository's plugin scaffold writes, with its notes under `## [0.1.0]` → `### Added`: skip step 3 and write the launch line in step 4.

### 2. Write the plugin release notes

1. Write them before the bump: they become the changelog section the bump creates. The bump script fails when `[Unreleased]` is empty.
2. Put them under `## [Unreleased]` in `plugins/<plugin>/CHANGELOG.md`, following Keep a Changelog 2.0.0 (change types `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`).
3. Record every user-visible change in detail, in user language (what changes for the user, not how). Reference issues as `(#12)`.
4. Start a breaking entry with `**Breaking:**`, inside its change type.
5. Check the notes against the diff: every change appears and nothing that did not happen does.

### 3. Apply the bump

1. If `plugin.json` already holds a version above the one in `origin/main` (the PR already carries this change's bump), skip this step.
2. Otherwise run `.claude/skills/release-and-versioning/scripts/bump-version.py <plugin> <major|minor|patch>`. It refuses `marketplace`: the marketplace has no version.
3. Read its output line (`<plugin>: <old> → <new>`) and confirm the new version is the one you intended.
4. Run `node scripts/generators/catalog.mjs`, so the README catalog shows the new version.

### 4. Add the root changelog line

1. Add a line in `CHANGELOG.md` (root) when the change is a version bump, a launch or a marketplace-level change.
2. The root changelog is a summary, never a copy of a plugin changelog. Its structure: `## YYYY-MM-DD` headings, newest first; under each, change-type headings (`### Added`, `### Changed`, `### Fixed`, `### Removed`); under each, one line per event. Create the date heading and the change-type heading if they are missing.
3. Put the line under today's date and the matching change type:
   - Version bump or launch: `- **<plugin>** X.Y.Z — one-line summary.` A launch goes under `### Added`; a bump under the change type of its change.
   - Marketplace-level change: `- summary.` (no plugin name, no version)

### 5. Commit

1. Commit as one signed commit (`git commit -S`): the bump, the plugin changelog entry, the root changelog line and the regenerated catalog. Step 3.4 regenerated the catalog; when step 3 was skipped or only the marketplace changed, run `node scripts/generators/catalog.mjs`.
2. The commit message says what changed and why.

### 6. Run the checks and show their raw output

Run them after the commit in step 5: `check-version-bump.py` reads committed changes only (`origin/main...HEAD`).

1. `git fetch origin main` and `S=.claude/skills/release-and-versioning/scripts`
2. `$S/check-version-bump.py origin/main`
3. `$S/check-marketplace-unversioned.py`
4. `$S/check-changelog-entry.py <plugin>` for each changed plugin.
5. `node scripts/generators/catalog.mjs --check`, and `node scripts/generators/marketplace.mjs --check`, which fails while `marketplace.json` does not list a new plugin as `plugins/` holds it.
6. `claude plugin validate --strict plugins/<plugin>` for each changed plugin, then `claude plugin validate --strict .` for the marketplace.
7. `git lfs ls-files -- plugins/<plugin>` prints nothing: a git clone never downloads LFS content, so an LFS file reaches users as a pointer file (`/en/plugins/host-marketplace`, "Keep plugin files out of Git LFS").
8. `find plugins/<plugin> -type l` lists every symlink, and each must resolve inside `plugins/<plugin>/`: a link elsewhere in the repository is copied as its target's content, and a link outside it is skipped without a warning (`/en/plugins/host-marketplace`, "Share files within a marketplace with symlinks").
9. Read the changed plugin's `README.md`, `CHANGELOG.md` and `plugin.json` side by side and make them agree with the change: the components, commands, prerequisites and network calls the README states, the Compatibility rows, and the version each file shows. A script passing is not this check.

If any check fails before the push, fix the cause, amend the commit (`git commit -S --amend`) and run all the checks again. After the push, commit the fix as a new signed commit instead: never amend or force-push a pushed commit.

### 7. Push and open the PR

With Nery's authorization only: push the branch and open the PR, applying only the labels the repository already has. A new plugin's PR also takes its `plugin: <name>` label, the one label this step may create, and only on Nery's order: `node scripts/sync-labels.mjs --dry-run` shows it, and the run without `--dry-run` creates it.

### 8. Before any merge or push to `main`

1. List what the merge publishes: every plugin whose `plugin.json` version on the branch differs from `origin/main` (`git diff --name-only origin/main...HEAD -- 'plugins/*/.claude-plugin/plugin.json'`, then compare the versions). Users receive each one as soon as the merge lands.
2. List the versions on `origin/main` that have no tag yet (`plugin.json` version against `git tag -l '<plugin>--v<version>'`): users already have them, and a missing tag means an earlier release run did not happen. Show Nery both lists and confirm each plugin is meant to ship.
3. If the PR is still open on a later day than the root changelog line, move the line to that day's section now, before the merge, never in a push after the merge.
4. For every changed plugin that ships evals, confirm its suite passed on the PR's head. No CI runs it, so the run is a local `claude plugin eval` on Nery's yes, because it spends usage.
5. Install each published plugin the way a user without a GitHub SSH key gets it: from the pushed PR branch, cloned over HTTPS from GitHub, in throwaway configurations that leave Nery's settings and plugins untouched. `B` holds the branch and `M` the current `main`, for comparison; make both with `mktemp -d` in the session scratchpad.
   ```bash
   iso() { local t="$1"; shift; env -u CLAUDE_CODE_PLUGIN_DIRS CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1 CLAUDE_CONFIG_DIR="$t/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="$t/plugins" claude "$@"; }
   B="$(mktemp -d)"; M="$(mktemp -d)"
   iso "$B" plugin marketplace add nerymurillohnd/the-claude-factory#<branch>
   iso "$B" plugin install <plugin>@the-claude-factory
   iso "$B" plugin list --json
   iso "$B" plugin details <plugin>
   iso "$M" plugin marketplace add nerymurillohnd/the-claude-factory#main
   iso "$M" plugin install <plugin>@the-claude-factory
   iso "$M" plugin details <plugin>
   ```
   - `plugin list --json` shows the new version, with an `installPath` under `cache/the-claude-factory/<plugin>/<version>/`.
   - `plugin details` lists the components the plugin ships.
   - The `Always-on` figure of `plugin details` in `B` against `M`: report any increase to Nery, with the component that grew. A new plugin has no figure in `M`; report its figure.
   - A failure here would reach users: fix it before the merge. Delete `B` and `M` afterwards.
   - **Unverified:** a branch name with `/` after `#`. If the add fails on one, report it to Nery instead of renaming the branch.
6. Merge only when Nery orders it.

### 9. Verify the release after the merge

1. Take the merge commit's SHA: `gh pr view <n> --json mergeCommit`.
2. Wait until `gh run list --workflow validate.yml --commit <sha>` shows the run completed.
3. Read the release run: `gh run list --workflow release.yml --commit <sha>`. The release run starts only from a Validate run that succeeded on a `push` to `main`. No run while Validate is still running is not a failure. A missing run after Validate succeeded is unexplained: read the trigger in `release.yml` before running anything.
4. Print the expected tag with `.claude/skills/release-and-versioning/scripts/release-notes.py <plugin> --tag` (never compose it by hand). Without `--tag` it prints the notes the release carries, the same text `release.yml` builds with `scripts/release-notes.mjs`.
5. Confirm the tag and the GitHub Release exist: `gh release view <plugin>--v<version>`, and that the tag matches step 4.
6. Confirm no other plugin was tagged by the same run unless intended: `gh run view <run-id> --log | grep -oE 'Released [a-z0-9-]+--v[0-9.]+'` lists every tag that run published.
7. Repeat the branch half of step 8.5 from `nerymurillohnd/the-claude-factory#main`: `plugin list` must show the new version and `plugin details` the same components and `Always-on` figure as before the merge. That is what users receive.
8. Report to Nery: the version users receive, the tag and the release exist and match, and nothing unintended was tagged.

### 10. Recover from a failed Validate

1. If Validate failed on `main`, nothing is tagged, but users who update already receive the merged version and keep it until they update again: tell Nery at once.
2. Fix the cause first, in a new PR, with its own bump, because a fix under the same version never reaches the users who already updated.
3. The next green push of `main` tags everything still untagged, the earlier version included, so the fix's merge releases it without a manual run.
4. Run `gh workflow run release.yml` only when Validate passed and no release run exists, and only after Nery says so: it tags and publishes.
5. An instruction like "súbelo ya" with a failed Validate does not skip steps 1 to 4.
