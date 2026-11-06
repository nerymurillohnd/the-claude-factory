---
name: releases
description: Use for the initial release of a new plugin and for the release of an existing plugin that had changes, to check it, open the pull request, merge it and confirm what users receive.
---

# Releases

Release a plugin of `the-claude-factory`, first release or release of a changed plugin. The marketplace is hosted in a public GitHub repository and users add it as `nerymurillohnd/the-claude-factory`, so Claude Code clones the default branch, `main`. Users fetch `main` as soon as a merge lands and keep that version until they update again, so every check happens before the merge.

## Rules

1. Never tag by hand. `release.yml` tags every plugin whose version has no tag yet, after Validate succeeds on `main`.
2. Put the release in the plugin's pull request: version, changelog entries and regenerated catalog in one signed commit. Commit nothing for the release after the merge.
3. Push, open a pull request or merge only when Nery authorizes it.
4. Merge only with all CI checks green, all review comments resolved and a `github-operations:pr-lifecycle:pr-tracker` report with no issues.
5. Never merge or push to `main` before listing what it publishes and confirming with Nery that each plugin is meant to ship.
6. Never run `release.yml` by hand while Validate is failing.

## Steps

### 1. Confirm the plugin is ready

1. A new plugin holds `0.1.0` with its launch notes.
2. A changed plugin holds the next version above `origin/main` with a non-empty changelog section.
3. A removal has no version and no changelog: `plugins/<old>/` is gone and `renames` holds `"<old>"`.
4. Every Claude Code behavior the change relies on was checked against `claude --version`, the release notes and the current docs, in that order of trust. Note what could not be verified, such as a platform the change was not run on.
5. Stop and tell Nery when what applies is missing.

### 2. Commit

1. Commit once, signed (`git commit -S`): the version, the plugin changelog entry, the root changelog line and the regenerated catalog.
2. Write a message that says what changed and why.

### 3. Run the checks

Run them after the commit, and show Nery the raw output.

1. `git fetch origin main`.
2. Check each changed plugin: exactly one version step above `origin/main` (a new plugin has none), a non-empty changelog section for its version, and no version anywhere in `marketplace.json`.
3. Run `node scripts/generators/catalog.mjs --check` and `node scripts/generators/marketplace.mjs --check`.
4. Run `claude plugin validate --strict plugins/<plugin>` for each changed plugin, then `claude plugin validate --strict .`.
5. Run `claude plugin tag plugins/<plugin> --dry-run` for each changed plugin. It prints the tag `<plugin>--v<version>` and "would create tag" when `plugin.json` and its marketplace entry agree. It refuses a dirty working tree and an existing tag. Never run it without `--dry-run`: only `release.yml` creates tags.
6. Run `git lfs ls-files --include='plugins/<plugin>/**'`: it prints nothing, because LFS files reach users as pointer files.
7. Run `find plugins/<plugin> -type l`: each symlink resolves inside `plugins/<plugin>/`. A link to elsewhere in the repository is copied as its target's content, and one outside the repository is skipped, so only a link inside the plugin keeps working for users.
8. Read the plugin's `README.md`, `CHANGELOG.md` and `plugin.json` side by side and make them agree with the change: components, commands, prerequisites, network calls, Compatibility rows and versions. The README's minimum Claude Code version is the only compatibility users get, so it must cover every feature the change uses.
9. Run `npm run gates`: every gate passes, the local-only ones included.

A removal has no plugin to check: skip items 2 and 4's plugin run, and items 5 to 8. Keep items 3 and 9 and the marketplace run of item 4.

When a check fails before the push, fix the cause, amend the commit (`git commit -S --amend`) and run every check again. After the push, fix with a new signed commit; never amend or force-push.

### 4. Push and open the pull request

1. Push the branch and open the pull request, with Nery's authorization only.
2. Apply only labels the repository already has.
3. For a new plugin, apply its `plugin: <name>` label. When it does not exist yet, create it only on Nery's order, with `npm run labels:sync`, which creates or updates every label from `.github/labels.json` plus one `plugin: <name>` label per plugin.

### 5. Before the merge

1. List every plugin whose version on the branch differs from `origin/main`, and every name that leaves `plugins`.
2. List every version on `origin/main` that has no tag yet: users already have it, and a missing tag means an earlier release did not run.
3. Show Nery both lists, with what step 1 could not verify, and confirm each plugin is meant to ship.
4. Date each release with the UTC day of its tag, the day `release.yml` runs after the merge: set each plugin's `## [X.Y.Z] - YYYY-MM-DD` heading, and the root changelog line's `## YYYY-MM-DD` section, to today's UTC date. Never change the date of a section that already has a tag.
5. Install each published plugin from the pushed branch over HTTPS, in throwaway configurations that leave Nery's settings and plugins untouched. `B` holds the branch and `M` the current `main`; create both with `mktemp -d` in the session scratchpad. Keep `${1}` braced in `iso`: Claude Code replaces a bare dollar-digit placeholder in a skill body with an argument of the skill, so the bare form would point every install at the same folder.
   ```bash
   iso() { local t="${1}"; shift; env -u CLAUDE_CODE_PLUGIN_DIRS CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1 CLAUDE_CONFIG_DIR="$t/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="$t/plugins" claude "$@"; }
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
   For a removal, install `<old>` in `B` instead: it fails with `not found in marketplace`.
7. Fix any failure before the merge, then delete `B` and `M`.
8. Merge only when Nery orders it.

### 6. Verify after the merge

1. Take the merge commit's SHA: `gh pr view <n> --json mergeCommit`.
2. Wait until `gh run list --workflow validate.yml --commit <sha>` shows the run completed.
3. Read the release run: `gh run list --workflow release.yml --commit <sha>`. It starts only after Validate succeeds on a push to `main`. No run while Validate is still running is normal. No run after Validate succeeded is unexplained: read the trigger in `release.yml` before running anything.
4. Confirm the tag `<plugin>--v<version>` and its GitHub Release exist: `gh release view <plugin>--v<version>`. The tag takes `<version>` from `plugin.json`. The Release body is the plugin's changelog section for that version, then `---`, then `**Update:**` and a code block with `claude plugin update <plugin>@the-claude-factory`. Compare the body with that section in the merge commit's `CHANGELOG.md`: a mismatch means the section changed after the tag, and the body changes only on Nery's order. The Release is neither a draft nor a prerelease. A removal gets no new tag.
5. Confirm the plugin's `## [x.y.z]` headings in `CHANGELOG.md` and its `<plugin>--v*` tags (`git ls-remote --tags origin '<plugin>--v*'`) are the same set, and that the latest tag equals `version` in `plugin.json` on `main`. No validator checks tags.
6. Confirm the run tagged nothing unintended: `gh run view <run-id> --log | grep -oE 'Released [a-z0-9-]+--v[0-9.]+'`.
7. Repeat step 5.5 from `nerymurillohnd/the-claude-factory#main`: the version and components match, and `Always-on` equals the figure before the merge. For a removal, installing `<old>` fails.
8. Report to Nery: the version users receive, that the tag and release exist and match, and that nothing unintended was tagged.

### 7. Recover from a failed Validate

1. Tell Nery at once: nothing is tagged, but users who update already receive the merged version.
2. Fix the cause in a new pull request with its own version bump: a fix under the same version never reaches users who already updated.
3. Expect the next green push to `main` to tag everything still untagged, so the fix's merge releases it.
4. Run `gh workflow run release.yml` only when Validate passed, no release run exists and Nery says so.
5. Keep these steps when Nery says "súbelo ya" with a failed Validate.
