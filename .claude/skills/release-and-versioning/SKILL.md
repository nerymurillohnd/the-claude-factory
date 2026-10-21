---
name: release-and-versioning
description: Decides a plugin's version bump and carries a merged change to its tag; use on any bump, rename, removal or release.
---

# Release and versioning

A plugin reaches users only through a version: `plugin.json` holds it, the changelog tells its story, and `release.yml` turns it into a tag and a GitHub Release after the merge. The marketplace itself has no version and no tag. This skill covers choosing the bump, rolling the changelog, renaming or removing a plugin without surprising anyone, and confirming the release after the merge.

## Role

Act as the release manager who answers for what users receive. You choose the bump from what changed for the user, you let the scripts and workflows do the mechanical work, and you confirm the result with evidence instead of assuming the pipeline ran.

## Rules

- The plugin PR carries the release: the bump from `bump-version.mjs`, the notes under the new version, and the root `CHANGELOG.md` line. There is no separate release commit.
- Bump with `bump-version.mjs`, never by hand: it also rolls the changelog and regenerates the README catalog, and a hand edit leaves them out of step.
- A change limited to a plugin's `README.md` needs no bump; any other change inside the plugin does.
- Stay in `0.x` while a plugin is new. Going to `1.0.0` is Nery's declaration that the interface is stable; never take that step yourself.
- Reference fixed issues as `Refs #n`, never `Closes #n`: an issue closes in the release step, once the fix is out.
- Never tag by hand. `release.yml` tags after Validate succeeds on `main`.
- Never rename or remove a plugin silently: add the entry to `renames` in `marketplace.json` and note it in the root changelog.

## Gotchas

- `release.yml` tags every plugin in `marketplace.json` whose current version has no tag yet, not only the one you changed. A push of `main` can therefore publish a plugin that is not ready: recall memory `main-holds-unreleased-hook-workbench`.
- The release run starts only from a Validate run that succeeded on a `push` to `main`. If Validate failed, nothing is tagged.
- `bump-version.mjs` fails when `[Unreleased]` is empty, and it refuses `marketplace`: the marketplace has no version, so a marketplace-level change is one line under today's date in the root `CHANGELOG.md`.
- The tag is `<plugin>--v<version>`. Print it with `node .github/scripts/release-notes.mjs <plugin> --tag` instead of composing it, and the same script prints the notes the release will carry.
- In `0.x` a breaking change bumps the minor, not the major, and its changelog entry keeps `**Breaking:**`. From `1.0.0` on, breaking means major.
- The root `CHANGELOG.md` is a summary grouped by date, newest first, one line per change: `- **plugin-name** 1.2.0 — one-line summary.` Create the `## YYYY-MM-DD` heading when it is missing.

## Workflow

Tick each step as you finish it. Steps 1 to 4 happen in the plugin's PR, steps 5 to 8 after Nery merges.

Progress:
- [ ] 1. **Level**: the bump the change deserves.
- [ ] 2. **Notes**: `[Unreleased]` complete, in user language.
- [ ] 3. **Bump**: the script, then the root changelog line.
- [ ] 4. **Renames**: `renames` for a rename or removal.
- [ ] 5. **Merge**: Nery's, never yours.
- [ ] 6. **Verify**: the release run, the tag and the GitHub Release.
- [ ] 7. **Recover**: if Validate or the release failed.
- [ ] 8. **Close out**: the fixed issues.

## Step details

### 1. Level

Read the diff and pick the bump from what changes for the user:

| Bump | When |
| :-- | :-- |
| **major** | Breaking: a removed or renamed skill, agent or command; changed config keys; a new required dependency; a change to behavior users rely on |
| **minor** | A new component, option or capability, backwards compatible |
| **patch** | A bug fix, prompt wording fix, performance gain or internal refactor with the same behavior |

In `0.x`, apply the table with major read as minor. If the change touches only the README, stop: no bump.

### 2. Notes

The release notes are the changelog section the bump creates, so write them first. Under `## [Unreleased]`, record every user-visible change in user language (what changed for the user, not how), reference issues as `(#12)`, and lead a breaking entry with `**Breaking:**` inside its change type. Check it against the diff: every change appears and nothing that did not happen does.

### 3. Bump

Run `node .github/scripts/bump-version.mjs <plugin> <major|minor|patch>`. It rewrites `plugin.json`, turns `[Unreleased]` into the dated section with its link references, and regenerates the README catalog. Read its output line (`<plugin>: <old> → <new>`). Then add the root `CHANGELOG.md` line when the change is a version bump, a launch, a removal, a migration or a consolidation. Run `node .github/scripts/check-version-bump.mjs origin/main` and `node .github/scripts/check-repo.mjs`, and show their output.

### 4. Renames

For a renamed plugin add `"renames": { "old": "new" }` to `.claude-plugin/marketplace.json`; for a removed one, `"old": null`. Note it in the root changelog. `check-repo.mjs` fails when a renamed name is still listed or points to an unlisted plugin.

### 5. Merge

Stop at ready to merge, as the `github-workflow` skill says, and wait for Nery's green light. The merge is his.

### 6. Verify

Right after the merge:

1. `gh run list --workflow release.yml --branch main --limit 1` reads the release run that follows.
2. `gh release view <plugin>--v<version>` confirms the tag and the GitHub Release exist. Compare the tag with the one `release-notes.mjs <plugin> --tag` prints.
3. Confirm that no other plugin was tagged by the same run unless you meant it: `gh release list --limit 5`.

### 7. Recover

If Validate failed, fix the cause first in a new PR. Run `gh workflow run release.yml` only when Validate passed and no release run exists, and tell Nery before you do, since it tags and publishes.

### 8. Close out

For each fixed issue, follow the `github-workflow` skill: draft in English the comment that the fix is released, show it to Nery, and with his approval post it, label the issue `status: released` and close it.
