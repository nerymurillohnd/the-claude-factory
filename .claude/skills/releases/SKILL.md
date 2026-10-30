---
name: releases
description: Use for the initial release of a new plugin and for the release of an existing plugin that had changes, to check it, open the pull request, merge it and confirm what users receive.
---

# Releases

Release a plugin of `the-claude-factory`, first release or release of a changed plugin. Users fetch `main` as soon as a merge lands and keep that version until they update again, so every check happens before the merge.

## Rules

1. Never tag by hand. `release.yml` tags every plugin whose version has no tag yet, after Validate succeeds on `main`.
2. Put the release in the plugin's pull request: version, changelog entries and regenerated catalog in one signed commit. Commit nothing for the release after the merge.
3. Push, open a pull request or merge only when Nery authorizes it.
4. Merge only with all CI checks green, all review comments resolved and a `github-operations:pr-tracker` report with no issues.
5. Never merge or push to `main` before listing what it publishes and confirming with Nery that each plugin is meant to ship.
6. Never run `release.yml` by hand while Validate is failing.

## Steps

### 1. Confirm the plugin is ready

1. A new plugin holds `0.1.0` with its launch notes.
2. A changed plugin holds the next version above `origin/main` with a non-empty changelog section.
3. Stop and tell Nery when either is missing.

### 2. Commit

1. Commit once, signed (`git commit -S`): the version, the plugin changelog entry, the root changelog line and the regenerated catalog.
2. Write a message that says what changed and why.

### 3. Run the checks

Run them after the commit, and show Nery the raw output.

1. `git fetch origin main`.
2. Check each changed plugin: exactly one version step above `origin/main` (a new plugin has none), a non-empty changelog section for its version, and no version anywhere in `marketplace.json`.
3. Run `node scripts/generators/catalog.mjs --check` and `node scripts/generators/marketplace.mjs --check`.
4. Run `claude plugin validate --strict plugins/<plugin>` for each changed plugin, then `claude plugin validate --strict .`.
5. Run `git lfs ls-files --include='plugins/<plugin>/**'`: it prints nothing, because LFS files reach users as pointer files.
6. Run `find plugins/<plugin> -type l`: each symlink resolves inside `plugins/<plugin>/`.
7. Read the plugin's `README.md`, `CHANGELOG.md` and `plugin.json` side by side and make them agree with the change: components, commands, prerequisites, network calls, Compatibility rows and versions.

When a check fails before the push, fix the cause, amend the commit (`git commit -S --amend`) and run every check again. After the push, fix with a new signed commit; never amend or force-push.

### 4. Push and open the pull request

1. Push the branch and open the pull request, with Nery's authorization only.
2. Apply only labels the repository already has.
3. For a new plugin, apply its `plugin: <name>` label, which this step may create only on Nery's order. Preview it with `node scripts/sync-labels.mjs --dry-run`.

### 5. Before the merge

1. List every plugin whose version on the branch differs from `origin/main`.
2. List every version on `origin/main` that has no tag yet: users already have it, and a missing tag means an earlier release did not run.
3. Show Nery both lists and confirm each plugin is meant to ship.
4. Move the root changelog line to the merge day's section when the pull request outlives its date.
5. Install each published plugin from the pushed branch over HTTPS, in throwaway configurations that leave Nery's settings and plugins untouched. `B` holds the branch and `M` the current `main`; create both with `mktemp -d` in the session scratchpad.
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
6. Check the output: `plugin list --json` shows the new version, `plugin details` lists the components, and the `Always-on` figure in `B` against `M` is reported to Nery with the component that grew. A new plugin has no figure in `M`: report its own.
7. Fix any failure before the merge, then delete `B` and `M`.
8. Merge only when Nery orders it.

### 6. Verify after the merge

1. Take the merge commit's SHA: `gh pr view <n> --json mergeCommit`.
2. Wait until `gh run list --workflow validate.yml --commit <sha>` shows the run completed.
3. Read the release run: `gh run list --workflow release.yml --commit <sha>`. It starts only after Validate succeeds on a push to `main`. No run while Validate is still running is normal. No run after Validate succeeded is unexplained: read the trigger in `release.yml` before running anything.
4. Confirm the tag `<plugin>--v<version>` and its GitHub Release exist: `gh release view <plugin>--v<version>`.
5. Confirm the run tagged nothing unintended: `gh run view <run-id> --log | grep -oE 'Released [a-z0-9-]+--v[0-9.]+'`.
6. Repeat step 5.5 from `nerymurillohnd/the-claude-factory#main`: the version and components match, and `Always-on` equals the figure before the merge.
7. Report to Nery: the version users receive, that the tag and release exist and match, and that nothing unintended was tagged.

### 7. Recover from a failed Validate

1. Tell Nery at once: nothing is tagged, but users who update already receive the merged version.
2. Fix the cause in a new pull request with its own version bump: a fix under the same version never reaches users who already updated.
3. Expect the next green push to `main` to tag everything still untagged, so the fix's merge releases it.
4. Run `gh workflow run release.yml` only when Validate passed, no release run exists and Nery says so.
5. Keep these steps when Nery says "súbelo ya" with a failed Validate.
