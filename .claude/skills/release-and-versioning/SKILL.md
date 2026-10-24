---
name: release-and-versioning
description: Use to choose a plugin's version bump, rename or remove a plugin, or confirm its tag and release after a merge.
---

# Release and versioning

A plugin reaches users only through a version: `plugin.json` holds it, the changelog tells its story, and `release.yml` turns it into a tag and a GitHub Release after the merge. The marketplace itself has no version and no tag. This skill covers choosing the bump, rolling the changelog, renaming or removing a plugin without surprising anyone, and confirming the release after the merge.

## Role

Act as the release manager who answers for what users receive. You choose the bump from what changed for the user, you let the scripts and workflows do the mechanical work, and you confirm the result with evidence instead of assuming the pipeline ran.

## Rules

- The plugin PR carries the release: the bump from `bump-version.mjs`, the notes under the new version, and the root `CHANGELOG.md` line. There is no separate release commit.
- Bump with `bump-version.mjs`, never by hand: it also rolls the changelog and regenerates the README catalog, and a hand edit leaves them out of step.
- A change limited to a plugin's `README.md` needs no bump; any other change inside the plugin does, a `CHANGELOG.md`-only edit included (`check-version-bump.mjs` treats only `README.md` as documentation).
- Stay in `0.x` while a plugin is new. Going to `1.0.0` is Nery's declaration that the interface is stable; never take that step yourself.
- Never tag by hand. `release.yml` tags after Validate succeeds on `main`.
- Never rename or remove a plugin silently: add the entry to `renames` in `marketplace.json` and note it in the root changelog.

## Gotchas

- `release.yml` tags every plugin in `marketplace.json` whose current version has no tag yet, not only the one you changed. A push of `main` can therefore publish a plugin that is not ready: list the untagged plugins (each `plugin.json` version against `git tag -l '<plugin>--v<version>'`) and ask Nery before any push of `main`.
- The release run starts only from a Validate run that succeeded on a `push` to `main`. If Validate failed, nothing is tagged; the next green push of `main` then tags everything still untagged, the earlier version included, so the fix's merge releases it without any manual run.
- `bump-version.mjs` fails when `[Unreleased]` is empty, and it refuses `marketplace`: the marketplace has no version, so a marketplace-level change is one line, `- summary.`, under today's date and its change type in the root `CHANGELOG.md`.
- The tag is `<plugin>--v<version>`. Print it with `node scripts/release-notes.mjs <plugin> --tag` instead of composing it, and the same script prints the notes the release will carry.
- In `0.x` a breaking change bumps the minor, not the major, and its changelog entry keeps `**Breaking:**`. From `1.0.0` on, breaking means major.
- The root `CHANGELOG.md` is a summary grouped by date, newest first, then by change type (`### Added`, `### Changed`, `### Fixed`, `### Removed`), one line per event in the format `.claude/CLAUDE.md` → Plugin Documentation and Changelogs → Root CHANGELOG.md gives it; a launch or a version bump reads `- **plugin-name** 1.2.0 — one-line summary.` Create the `## YYYY-MM-DD` heading and the change-type heading when they are missing, and put the line under today's date; if the PR is still open on a later day, move the line before Nery merges, never in a push after the merge.

## Hand-offs

| When | Invoke with the Skill tool |
| :-- | :-- |
| You finished step 3 and `plugin-consistency` has not run since the last edit | `plugin-consistency`: the bump rewrote `plugin.json`, the changelog and the README catalog |
| Step 4 is done and the PR is still open | Nothing if `plugin-consistency`, `plugin-development` or `github-workflow` invoked you: hand back. Loaded alone, `github-workflow`, which owns the push, the PR and the merge |
| The release is verified or recovered (steps 5 and 6) | `github-workflow`, which closes the fixed issues (its step 8) |

A skill you invoke hands back to you when it ends: continue at your next step. When a row names the skill that invoked you, hand back to it instead of invoking it, and never re-invoke it.

## Workflow

Tick each step as you finish it. Steps 1 to 4 happen in the plugin's PR; then `github-workflow` pushes and stops at ready to merge, and the merge is Nery's, never yours. Steps 5 and 6 come after the merge.

Progress:
- [ ] 1. **Level**: the bump the change deserves.
- [ ] 2. **Notes**: `[Unreleased]` complete, in user language.
- [ ] 3. **Bump**: the script, then the root changelog line.
- [ ] 4. **Renames**: `renames` for a rename or removal.
- [ ] 5. **Verify**: after the merge, the release run, the tag and the GitHub Release.
- [ ] 6. **Recover**: if Validate or the release failed.

## Step details

### 1. Level

Read the diff and pick the bump from what changes for the user:

| Bump | When |
| :-- | :-- |
| **major** | Breaking: a removed or renamed skill, agent or command; changed config keys; a new required dependency; a change to behavior users rely on |
| **minor** | A new component, option or capability, backwards compatible |
| **patch** | A bug fix, prompt wording fix, performance gain or internal refactor with the same behavior |

In `0.x`, apply the table with major read as minor. When one PR mixes levels, take the highest.

### 2. Notes

The release notes are the changelog section the bump creates, so write them first. Follow Keep a Changelog 2.0.0. Each plugin changelog tells that plugin's full story, so under `## [Unreleased]` record every user-visible change in detail, in user language (what changed for the user, not how), reference issues as `(#12)`, and lead a breaking entry with `**Breaking:**` inside its change type. The root `CHANGELOG.md` is only a summary, never a copy of a plugin changelog. Check it against the diff: every change appears and nothing that did not happen does.

### 3. Bump

Skip the script when the PR already carries this change's bump (`plugin.json` holds a version above `origin/main`'s). Otherwise run `node scripts/bump-version.mjs <plugin> <major|minor|patch>`. It rewrites `plugin.json`, turns `[Unreleased]` into the dated section with its link references, and regenerates the README catalog. Read its output line (`<plugin>: <old> → <new>`). Then add the root `CHANGELOG.md` line when the change is a version bump, a launch, a rename or a removal. Run `node scripts/check-version-bump.mjs origin/main`, `node scripts/check-repo.mjs` and `node scripts/generators/catalog.mjs --check`, and show their output. Commit the bump, the plugin and root changelog entries and the catalog as one signed commit, because the first two read committed changes only (`origin/main...HEAD`). If `plugin-consistency` has not run since your last edit and did not invoke you, invoke it now.

### 4. Renames

A rename or removal reaches users only through `renames`, which makes Claude Code migrate existing installs instead of reporting the plugin as not found (`/en/plugins/host-marketplace`, "Migrate users with a renames map"). Never do one silently.

When the change renames or removes a plugin, read [the rename procedure](references/renames.md) and follow it; otherwise skip this step.

### 5. Verify

Right after Nery's merge:

1. Take the merge commit's SHA (`gh pr view <n> --json mergeCommit`). Wait until `gh run list --workflow validate.yml --commit <sha>` shows it completed. Then `gh run list --workflow release.yml --commit <sha>` reads the release run that follows; no run yet while Validate is still running is not a failure, and once Validate has succeeded a missing run is unexplained, so read the trigger in `release.yml` before running anything.
2. `gh release view <plugin>--v<version>` confirms the tag and the GitHub Release exist. Compare the tag with the one `release-notes.mjs <plugin> --tag` prints.
3. Confirm that no other plugin was tagged by the same run unless you meant it: `gh release list --limit 5`.

### 6. Recover

If Validate failed, fix the cause first in a new PR. Run `gh workflow run release.yml` only when Validate passed and no release run exists, and only after Nery says so: it tags and publishes. An instruction like "súbelo ya" with a failed Validate does not skip this; fix the cause, since the next green push tags by itself. Once the release is verified, hand back to `github-workflow` (its step 8). A recovery PR starts a new `github-workflow` run at its step 4.
