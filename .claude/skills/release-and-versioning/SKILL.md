---
name: release-and-versioning
description: Use to choose a plugin's version bump or confirm its tag and release after a merge.
---

# Versioning and Releases

## Scope

Follow this procedure whenever a plugin changes in `the-claude-factory`, to decide whether it needs a version bump and to carry the change through release. For a plugin rename, removal or merge into another plugin, follow the `plugin-renames-and-removals` skill instead; it is a complete procedure on its own.

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
- The `<plugin>--v<version>` tag does not deliver the plugin. Plugin dependency ranges resolve against it, and for a relative-path plugin the tag lives in the marketplace repository, on a commit whose `plugin.json` holds that version (`/en/plugins/dependencies`, "Release a plugin that others depend on"). The GitHub Release carries the notes for people.
- Claude Code does not check the value against SemVer; SemVer is this project's convention (`/en/plugins/manifest-reference`, "version").

## Rules

1. Version plugins only. Never add a version or a tag to `.claude-plugin/marketplace.json`.
2. Use SemVer (`MAJOR.MINOR.PATCH`) and choose the bump by user-facing impact.
3. Apply every bump with `node scripts/bump-version.mjs <plugin> <major|minor|patch>`, never by hand. The script also turns `[Unreleased]` into the dated section with its link references and regenerates the README catalog; a hand edit leaves them out of step.
4. A `0.x` version makes no interface-stability promise; `1.0.0` does. Stay in `0.x` while a plugin is new. Never promote a plugin to `1.0.0` without Nery's explicit authorization.
5. Never tag by hand. `release.yml` creates the tags (format `<plugin>--v<version>`) on the commit Validate checked, after Validate succeeds on `main`, and it tags every plugin whose `plugin.json` version has no tag yet, not only the one you changed.
6. Never push or merge to `main` without first listing the untagged plugins and confirming with Nery that each is meant to ship (step 8).
7. Never run `gh workflow run release.yml` while the Validate workflow is failing.
8. The plugin PR carries the release: the bump, the changelog entries and the regenerated catalog go in that PR as one signed commit, beside the PR's other commits. Nothing is committed for the release after the merge.
9. Push, open a PR or merge only when Nery authorizes it. Merge only with all CI checks green, all review comments resolved and a `github-operations:pr-tracker` report with no issues.

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

### 2. Write the plugin release notes

1. Write them before the bump: they become the changelog section the bump creates. The bump script fails when `[Unreleased]` is empty.
2. Put them under `## [Unreleased]` in `plugins/<plugin>/CHANGELOG.md`, following Keep a Changelog 2.0.0 (change types `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`).
3. Record every user-visible change in detail, in user language (what changes for the user, not how). Reference issues as `(#12)`.
4. Start a breaking entry with `**Breaking:**`, inside its change type.
5. Check the notes against the diff: every change appears and nothing that did not happen does.

### 3. Apply the bump

1. If `plugin.json` already holds a version above the one in `origin/main` (the PR already carries this change's bump), skip this step.
2. Otherwise run `node scripts/bump-version.mjs <plugin> <major|minor|patch>`. It refuses `marketplace`: the marketplace has no version.
3. Read its output line (`<plugin>: <old> → <new>`) and confirm the new version is the one you intended.

### 4. Add the root changelog line

1. Add a line in `CHANGELOG.md` (root) when the change is a version bump, a launch or a marketplace-level change.
2. The root changelog is a summary, never a copy of a plugin changelog. Its structure: `## YYYY-MM-DD` headings, newest first; under each, change-type headings (`### Added`, `### Changed`, `### Fixed`, `### Removed`); under each, one line per event. Create the date heading and the change-type heading if they are missing.
3. Put the line under today's date and the matching change type:
   - Version bump or launch: `- **<plugin>** X.Y.Z — one-line summary.`
   - Marketplace-level change: `- summary.` (no plugin name, no version)

### 5. Commit

1. Commit as one signed commit (`git commit -S`): the bump, the plugin changelog entry, the root changelog line and the regenerated catalog. The catalog is regenerated by the bump script; when step 3 was skipped or only the marketplace changed, run `node scripts/generators/catalog.mjs`.
2. The commit message says what changed and why.

### 6. Run the checks and show their raw output

The first two checks read committed changes only (`origin/main...HEAD`), so run them after the commit in step 5.

1. `git fetch origin main`
2. `node scripts/check-version-bump.mjs origin/main`
3. `node scripts/check-repo.mjs`
4. `node scripts/generators/catalog.mjs --check`
5. If `plugin-consistency` has not run since your last edit and did not invoke you, invoke it now.

If any check fails before the push, fix the cause, amend the commit (`git commit -S --amend`) and run all the checks again. After the push, commit the fix as a new signed commit instead: never amend or force-push a pushed commit.

### 7. Push and open the PR

With Nery's authorization only: push the branch and open the PR (`github-workflow` step 5), applying only the labels the repository already has.

### 8. Before any merge or push to `main`

1. List the untagged plugins: for each plugin, compare the version in `plugin.json` with `git tag -l '<plugin>--v<version>'`. A plugin with no matching tag is untagged.
2. Show Nery the list and confirm each untagged plugin is meant to ship. A plugin that is not ready would be published by the next green push of `main`.
3. If the PR is still open on a later day than the root changelog line, move the line to that day's section now, before the merge, never in a push after the merge.
4. Confirm the PR's Evals run passed for every changed plugin that ships evals.
5. Install each bumped plugin the way users will get it: from the pushed PR branch, through GitHub, in a throwaway configuration that leaves Nery's settings and plugins untouched. Run in the scratchpad or a `mktemp -d` folder `T`:
   ```bash
   iso() { env -u CLAUDE_CODE_PLUGIN_DIRS CLAUDE_CONFIG_DIR="$T/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="$T/plugins" claude "$@"; }
   iso plugin marketplace add nerymurillohnd/the-claude-factory#<branch>
   iso plugin install <plugin>@the-claude-factory
   iso plugin list --json
   iso plugin details <plugin>
   ```
   `plugin list` must show the new version and an `installPath` under `cache/the-claude-factory/<plugin>/<version>/`, and `plugin details` the components the plugin ships. A failure here would reach users: fix it before the merge. Delete `T` afterwards.
6. Merge only when Nery orders it.

### 9. Verify the release after the merge

1. Take the merge commit's SHA: `gh pr view <n> --json mergeCommit`.
2. Wait until `gh run list --workflow validate.yml --commit <sha>` shows the run completed.
3. Read the release run: `gh run list --workflow release.yml --commit <sha>`. The release run starts only from a Validate run that succeeded on a `push` to `main`. No run while Validate is still running is not a failure. A missing run after Validate succeeded is unexplained: read the trigger in `release.yml` before running anything.
4. Print the expected tag with `node scripts/release-notes.mjs <plugin> --tag` (never compose it by hand; the same script prints the notes the release will carry).
5. Confirm the tag and the GitHub Release exist: `gh release view <plugin>--v<version>`, and that the tag matches step 4.
6. Confirm no other plugin was tagged by the same run unless intended: `gh run view <run-id> --log | grep -oE 'Released [a-z0-9-]+--v[0-9.]+'` lists every tag that run published.
7. Repeat the isolated install of step 8.5 from `nerymurillohnd/the-claude-factory#main` and confirm `plugin list` shows the new version: that is what users receive.
8. Report to Nery: the version users receive, the tag and the release exist and match, and nothing unintended was tagged.

### 10. Recover from a failed Validate

1. If Validate failed on `main`, nothing is tagged, but users who update already receive the merged version: tell Nery at once.
2. Fix the cause first, in a new PR, with its own bump, because a fix under the same version never reaches the users who already updated.
3. The next green push of `main` tags everything still untagged, the earlier version included, so the fix's merge releases it without a manual run.
4. Run `gh workflow run release.yml` only when Validate passed and no release run exists, and only after Nery says so: it tags and publishes.
5. An instruction like "súbelo ya" with a failed Validate does not skip steps 1 to 4.

## Hand-offs

| When | Invoke with the Skill tool |
| :-- | :-- |
| The change renames, removes or merges a plugin | `plugin-renames-and-removals`, instead of this skill |
| Step 6 is done and the PR is still open | Nothing if `plugin-consistency`, `plugin-development` or `github-workflow` invoked you: hand back. Loaded alone, `github-workflow`, which owns the push, the PR and the merge (steps 7 and 8 here) |
| The release is verified or recovered (steps 9 and 10) | `github-workflow`, which closes the fixed issues (its step 8) |

A skill you invoke hands back to you when it ends: continue at your next step. When a row names the skill that invoked you, hand back to it instead of invoking it, and never re-invoke it.
