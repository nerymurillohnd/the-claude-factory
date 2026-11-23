---
name: plugin-releases
description: Versions and releases a plugin of this marketplace end to end, from the semver bump and its changelog notes to the reviews and checks before the merge, the changelog date, the tag and GitHub Release that CI creates, the checks after, and the backfill of a version that never got its tag. Use whenever a plugin under plugins/ changed and may need a version bump, a new plugin needs its first version, someone asks which semver level a change takes, a version is about to be merged or published, a tag or Release is missing or must be verified, or someone asks how users receive an update, even if they only say "bump it", "ship it" or "publish the new version".
---

# Plugin releases

Every plugin here is a relative-path entry (`./plugins/<plugin>`) in a git-hosted marketplace. Users receive a change only when the plugin's `version` string changes, and they receive whatever `main` holds the moment a merge lands. So the bump, the notes and every check happen before the merge; after it, CI tags the version and you confirm what users got.

## Gotchas

- **One version per release.** `release.yml` tags only each plugin's current `plugin.json` version. Never bump a plugin again while its previous version has no tag: that version can then only get its tag through a backfill (Backfill below).
- **The catalog row moves with the version.** `npm run check:consistency` (PC-08) fails as soon as `plugin.json` and the root `README.md` catalog cell disagree, so set both in the same change (Phase A), not at release time.
- **The changelog date is the day the version was prepared, in UTC; never re-date it.** `release:changelog` writes it before the merge, and the GitHub Release records the day the version was published. No check compares the two, so a merge on a later day changes nothing.
- **`untagged:` is not the backfill list.** `npm run release:status` prints `untagged:` only for each plugin's current version on `main`, which the next merge's release tags on its own. A version that will never be tagged that way, an older heading with no tag, shows only as a PC-04 finding of `npm run check:consistency`: those are the versions to backfill.
- **A rename computes the next version from the old name.** `npm run release:status -- --next <new name>` finds nothing on `origin/main` and prints `0.1.0`; pass the old name, and treat the rename as breaking.
- **Cloud sessions never tag.** The cloud proxy refuses tag pushes and answers 403 to `POST …/git/refs` and `POST …/releases`. Only `release.yml` creates tags and Releases; a cloud session only dispatches it, with the owner's authorization.
- **Auto-fix stays off.** Claude's Auto-fix for pull requests pushes fixes without asking, which this project doesn't allow; CI failures and review findings go through `github-operations:auto-pr-lifecycle`, which asks before every push.

## How Claude Code reads the version (official)

From code.claude.com/docs/en/plugins/host-marketplace (Release a new version), plugins/loading (How Claude Code computes the version) and plugins/manifest-reference (`version`):

- The version comes from `version` in `plugin.json` first, then from the marketplace entry; with neither, a relative-path plugin in a git-hosted marketplace uses the commit SHA.
- With `version` set, commits pushed without changing it don't reach users: `claude plugin update` prints `<name> is already at the latest version (<version>)`. A merge without a bump still changes what a new install receives under the old number.
- Set `version` only in `plugin.json`. If the marketplace entry also sets one, `plugin.json` wins silently and `claude plugin validate` reports `Entry declares version "<a>" but <path>/plugin.json says "<b>"`.
- Ranges in other plugins' `dependencies` resolve against tags named `<plugin>--v<version>`, held by the marketplace repository.

## Project conventions

These go beyond the docs and stay unless the owner changes them:

- Versions are semver. Changelogs follow Keep a Changelog, written with the `docs-maintenance` skill.
- Every released version gets a tag and a GitHub Release with the same name, never a draft or prerelease. The Release body is that version's changelog section, then `claude plugin update <plugin>@the-claude-factory`.
- A plugin's `## [x.y.z]` changelog headings are exactly its tags, and `## [Unreleased]` is empty on `main`.
- Tags made by `release.yml` are unsigned, because signing in CI would put the key in a GitHub secret.
- Never move, delete or reuse a tag. A fix ships as a new version.

## Phase A: Version, on the branch, with the change

1. **Identify the case.**
   - A new plugin: its first version is `0.1.0`. Go to step 4.
   - Only the plugin's `README.md`, `CHANGELOG.md`, `LICENSE`, `NOTICE.txt`, `tests/`, `*.test.ts(x)` or `evals/` changed: no bump. Stop. A README change that raises a Node.js or Python minimum is the exception: bump, and continue.
   - Only `.claude-plugin/marketplace.json` changed: no plugin bump. A rename or removal goes through the `plugin-catalog-changes` skill.
   - Anything else in `plugins/<plugin>/` changed: bump. Continue.
2. **Choose the level** from the diff against `origin/main`; when a change mixes levels, take the highest.
   - Major: a removed or renamed skill, agent, command or plugin; changed configuration keys; a new mandatory dependency; changed behavior users rely on; a higher Node.js or Python minimum in the plugin's README Prerequisites, because it drops users whose runtime meets the old one.
   - Minor: a new backward-compatible component, option or capability, or a higher `engines["claude-code"]` floor.
   - Patch: a bug fix, prompt wording, a performance improvement, a refactor with the same behavior, or a metadata change such as the category, the listing URLs or the icon.
   - In `0.x`, a breaking change bumps Minor. Moving from `0.x` to `1.0.0` needs the owner's authorization, because it promises users a stable interface.
3. **Check dependents.** `npm run release:status` prints `dependent: <plugin> needs <name> <range>` for each declared dependency (`any` for a bare name). Keep the new version inside every range that names this plugin, or change the dependent in the same pull request.
4. **Set the minimum Claude Code version** when the change relies on a Claude Code feature: `engines["claude-code"]` in `plugin.json`, as `">=<lowest version that has the feature>"`. Outside the range the plugin is not installed, updated or loaded (changelog, 2.1.323; not yet in the manifest reference). Make the README's minimum Claude Code version say the same, and note it under `### Changed`.
5. **Write the notes** with the `docs-maintenance` skill under `## [Unreleased]` in `plugins/<plugin>/CHANGELOG.md`: one entry per user-visible change, under Added, Changed, Deprecated, Removed, Fixed or Security, with `**Breaking:**` where it breaks something. Update the README with the same skill when the change alters what it describes. For a new plugin, run that skill's "New plugin" event instead.
6. **Set the version.** After `git fetch origin main`, set `version` in `plugins/<plugin>/.claude-plugin/plugin.json` to what `npm run release:status -- --next <plugin> --level <major|minor|patch>` prints. Then set the plugin's version cell in the root `README.md` catalog to the same value.
7. **Check it**, and show the raw output:
   - `npm run release:status` exits 0 and lists `changed: <plugin> <old> -> <new>`; it exits 1 on a version that isn't semver, which the validator accepts.
   - `claude plugin validate --strict plugins/<plugin>` and `claude plugin validate --strict .` exit 0.
   - For a mod (`tests/*.test.ts(x)`), `claude plugin test plugins/<plugin>` exits 0; for plugin tests (`tests/test_*.py`, `tests/*.test.mjs`), `npm run test:plugins` exits 0.
   - When the plugin's Python or Node.js code changed, its tests also pass on the floor runtimes users may have, Python 3.12 and Node.js 24, since `npm run test:plugins` runs on the `python3` and `node` first on `PATH`, the maintainers' Python 3.15 and Node.js 26. Keep both runtimes in the session's scratchpad and delete them right after: Python 3.12 through `UV_PYTHON_DOWNLOADS=automatic UV_PYTHON_INSTALL_DIR=<scratchpad>/py UV_CACHE_DIR=<scratchpad>/uvcache uv run --isolated --no-project --python 3.12 …`, lifting the machine's `UV_PYTHON_DOWNLOADS=manual` only for those commands, and Node.js 24 from the official nodejs.org tarball, checked against its `SHASUMS256.txt`. With both runtimes' `bin` first on `PATH`, run the `test:plugins` script's own command from `package.json` with `bash`, not through `npm run`, and it exits 0: the root `package.json` `devEngines` requires Node 26 and npm 12, so npm rejects the tarball's Node 24 and its npm with `EBADDEVENGINES`. `.claude/rules/plugins/testing.md` holds the full procedure.
   - `npm run check:consistency -- --offline` exits 0.
   - `npm run check:install -- --from local <plugin>` exits 0 and prints the new version. It runs in a throwaway configuration, because this checkout and an installed `the-claude-factory` can't both be added under the same marketplace name.
   - With the owner's approval of the spend, a local smoke eval: `claude plugin eval plugins/<plugin> --case <case> --runs 1 --ablation none --no-publish`.

## Phase B: Before the merge

1. **Review the diff yourself** before you ask to push: run `/code-review` on the branch with the `code-review` skill. For changed scripts and hooks, also launch the `pr-review-toolkit:silent-failure-hunter` and `pr-review-toolkit:pr-test-analyzer` agents when the `pr-review-toolkit` plugin (marketplace `claude-plugins-official`) is installed; when it isn't, say so instead of skipping the step silently. Fix what the reviews find, or report it to the owner when it needs a decision.
2. **Date the release before you push**, with the `docs-maintenance` skill, for every plugin `npm run release:status` lists as changed. Validate checks a pull request as `main` will be after the merge, so a version still under `## [Unreleased]` fails it (PC-05 and the release notes):
   - `npm run release:changelog -- <plugin>` turns `## [Unreleased]` into `## [X.Y.Z] - <today in UTC>`, adds an empty `## [Unreleased]` above it and writes the compare and release links. It exits 1 and changes nothing when `## [Unreleased]` is empty: stop and ask the owner what the version changes.
   - Write the release line in the root `CHANGELOG.md`, with the same date.
   - A version already dated keeps its date.
3. **Check what `release.yml` will publish**, on a committed tree:
   - `npm run release:notes -- <plugin>` for every plugin builds the Release body `release.yml` will publish; it exits 1 when a version has no dated section with notes, and a failure there would stop the release loop at that plugin. Validate runs it the same way on pull requests and on `main`.
   - `claude plugin tag plugins/<plugin> --dry-run` prints `<plugin>--v<version>`; it exits 1 while any file under the plugin is uncommitted.
   - `find plugins/<plugin> -type l` lists no link out of the plugin.
4. **List for the owner** what will ship: `git fetch origin main && npm run release:status`. `changed:` lines are the new versions, and `untagged:` lines are current versions on `main` that this merge's release will also tag. The PC-04 findings of `npm run check:consistency` are versions that need a backfill (Backfill below) before Validate's `Checks` can pass.
5. **Ask the owner to authorize the push**, then drive the pull request with `github-operations:auto-pr-lifecycle`. On the pull request:
   - Validate's `Checks` job must pass. Its `Debt` job reports the checks DEBT items hold back and never blocks.
   - `npm run check:install -- --from <pull request branch> <plugin>` installs what users will get from the branch.

## Phase C: Merge and release

1. **Merge** only with the owner's authorization, Validate's `Checks` green on the pull request's latest push, and every review resolved.
2. **The release runs on its own.** The push to `main` runs Validate; when `Checks` passes, its `Release` job calls `release.yml`, which tags and publishes each plugin whose current version has no tag, at the merged commit. A plugin whose tag exists is skipped.
3. **If the `Release` job fails or is cancelled**, tell the owner at once: users who update already have the merged version. `release.yml` keeps one release running and one waiting, so a third merge in quick succession cancels the waiting one; the next release then tags that version at its later commit. Fix a failure's cause in a new commit on `main` through a pull request, then, with the owner's authorization, dispatch `release.yml` on `main` (Backfill below, without `backfill_target`). Never move or reuse a tag.

## Phase D: Verify, and show the raw output

- `git ls-remote --tags origin '<plugin>--v*'` lists exactly the changelog's `## [x.y.z]` versions.
- The tag's commit is an ancestor of `main`: `git merge-base --is-ancestor <tag commit> origin/main`.
- The GitHub Release exists with the tag's name and is neither a draft nor a prerelease: the GitHub MCP tool `get_release_by_tag` (`owner: nerymurillohnd`, `repo: the-claude-factory`, `tag: <plugin>--v<version>`).
- `npm run release:status` prints no `untagged:` line.
- `npm run check:install -- --from main <plugin>` installs the new version.

## Backfill a version that never got its tag

`release.yml` also runs through `workflow_dispatch`, with two inputs: `plugin`, to release only that plugin, and `backfill_target`, a commit on `main` where the plugin's `plugin.json` held the version to release. The tag goes on that commit and the Release body comes from the dispatched branch's changelog, so the version's section must exist and be dated there. Every tag lands on a commit `main` has: the script refuses a target that isn't on `origin/main`, whichever branch was dispatched.

1. Find the last commit on `main` where `plugin.json` held the version: `git log --format=%h origin/main -- plugins/<plugin>/.claude-plugin/plugin.json`, then `git show <commit>:plugins/<plugin>/.claude-plugin/plugin.json`.
2. With the owner's authorization, dispatch it from a cloud session with the GitHub MCP tool `actions_run_trigger` (`method: run_workflow`, `owner: nerymurillohnd`, `repo: the-claude-factory`, `workflow_id: release.yml`, `ref: <branch>`, `inputs: {"plugin": "<plugin>", "backfill_target": "<commit>"}`). The run uses the `release.yml` of the branch it is dispatched on.
3. Verify as in Phase D. A dispatch with an unknown plugin exits 2, and one whose commit isn't on `main` exits 1; neither creates anything.

## Withdraw a version

Claude Code can't take a published version back: users who updated keep it until a newer one reaches them. Release the fix as a new version through this skill, then mark the withdrawn version `[YANKED]` in the plugin's `CHANGELOG.md` with the `docs-maintenance` skill, with the evidence that it was withdrawn. Never delete its section, its tag or its GitHub Release.

## What users run

From code.claude.com/docs/en/plugins/publish (Ship updates to users) and host-marketplace (Turn on auto-update). The release notes and the README give users these:

- `claude plugin update <plugin>@the-claude-factory [--scope <scope>]` installs the new version.
- `claude plugin marketplace update the-claude-factory` refreshes the listings only; installed plugins keep their versions.
- `/reload-plugins` loads the new version into a running session.
- Auto-update is off by default for this marketplace; each user turns it on under **Marketplaces** in `/plugin`.
