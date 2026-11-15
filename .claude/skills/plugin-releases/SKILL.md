---
name: plugin-releases
description: Versions and releases a plugin of this marketplace end to end, from the semver bump and its changelog notes to the reviews and checks before the merge, the merge-day date, the tag and GitHub Release that CI creates, the checks after, and the backfill of a version that never got its tag. Use whenever a plugin under plugins/ changed and may need a version bump, a new plugin needs its first version, someone asks which semver level a change takes, a version is about to be merged or published, a tag or Release is missing or must be verified, or someone asks how users receive an update, even if they only say "bump it", "ship it" or "publish the new version".
---

# Plugin releases

Every plugin here is a relative-path entry (`./plugins/<plugin>`) in a git-hosted marketplace. Users receive a change only when the plugin's `version` string changes, and they receive whatever `main` holds the moment a merge lands. So the bump, the notes and every check happen before the merge; after it, CI tags the version and you confirm what users got.

## Gotchas

- **One version per release.** `release.yml` tags only each plugin's current `plugin.json` version. Never bump a plugin again while its previous version has no tag: that version can then only get its tag through a backfill (Backfill below).
- **The catalog row moves with the version.** `npm run check:consistency` (PC-08) fails as soon as `plugin.json` and the root `README.md` catalog cell disagree, so set both in the same change (Phase A), not at release time.
- **The date is the merge day, in UTC.** A release is dated the day its tag is created, and `release.yml` tags it minutes after the merge. On a pull request, `check:consistency -- --date-check` (PC-11, run by Validate) fails while an untagged current version is dated any other day. PC-11 is evaluated only when Validate runs, so a green run from an earlier UTC day proves nothing: re-run the pull request's Validate on merge day, right before merging.
- **`untagged:` is not the backfill list.** `npm run release:status` prints `untagged:` only for each plugin's current version on `main`, which the next merge's release tags on its own. A version that will never be tagged that way, an older heading with no tag, shows only as a PC-04 finding of `npm run check:consistency`: those are the versions to backfill.
- **A rename computes the next version from the old name.** `npm run release:status -- --next <new name>` finds nothing on `origin/main` and prints `0.1.0`; pass the old name, and treat the rename as breaking.
- **Cloud sessions never tag.** The cloud proxy refuses tag pushes and answers 403 to `POST …/git/refs` and `POST …/releases`. Only `release.yml` creates tags and Releases; a cloud session only dispatches it, with the owner's authorization.
- **The Claude review skips its own first pull request.** `claude-code-action` ends green without running when the workflow file differs from the default branch's copy, so a pull request that adds or changes `claude-code-review.yml` gets no Claude review until after it merges.
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
   - Only the plugin's `README.md`, `CHANGELOG.md`, `LICENSE`, `NOTICE.txt`, `tests/`, `*.test.ts(x)` or `evals/` changed: no bump. Stop.
   - Only `.claude-plugin/marketplace.json` changed: no plugin bump. A rename or removal goes through the `plugin-catalog-changes` skill.
   - Anything else in `plugins/<plugin>/` changed: bump. Continue.
2. **Choose the level** from the diff against `origin/main`; when a change mixes levels, take the highest.
   - Major: a removed or renamed skill, agent, command or plugin; changed configuration keys; a new mandatory dependency; changed behavior users rely on.
   - Minor: a new backward-compatible component, option or capability, or a higher `engines["claude-code"]` floor.
   - Patch: a bug fix, prompt wording, a performance improvement, a refactor with the same behavior, or a metadata change such as the category, the listing URLs or the icon.
   - In `0.x`, a breaking change bumps Minor. Moving from `0.x` to `1.0.0` needs the owner's authorization, because it promises users a stable interface.
3. **Check dependents.** `npm run release:status` prints `dependent: <plugin> needs <name> <range>` for each declared dependency (`any` for a bare name). Keep the new version inside every range that names this plugin, or change the dependent in the same pull request.
4. **Set the minimum Claude Code version** when the change relies on a Claude Code feature: `engines["claude-code"]` in `plugin.json`, as `">=<lowest version that has the feature>"`. Outside the range the plugin is not installed, updated or loaded (changelog, 2.1.323; not yet in the manifest reference). Make the README's minimum Claude Code version say the same, and note it under `### Changed`.
5. **Write the notes** with the `docs-maintenance` skill under `## [Unreleased]` in `plugins/<plugin>/CHANGELOG.md`: one entry per user-visible change, under Added, Changed, Deprecated, Removed, Fixed or Security, with `**Breaking:**` where it breaks something. Update the README with the same skill when the change alters what it describes. For a new plugin, run that skill's "New plugin" event instead.
6. **Set the version.** After `git fetch origin main`, set `version` in `plugins/<plugin>/.claude-plugin/plugin.json` to what `npm run release:status -- --next <plugin> --level <major|minor|patch>` prints. Then set the plugin's version cell in the root `README.md` catalog to the same value.
7. **Check it**, and show the raw output:
   - `npm run release:status` exits 0 and lists `changed: <plugin> <old> -> <new>`; it exits 1 on a version that isn't semver, which the validator accepts.
   - `claude plugin validate --strict plugins/<plugin>` and `claude plugin validate --strict .` exit 0. A plugin that DEBT-003 holds back fails here today; report it instead of fixing it in this change.
   - For a mod (`tests/*.test.ts(x)`), `claude plugin test plugins/<plugin>` exits 0; for hook tests, `npm run test:plugins` exits 0.
   - `npm run check:consistency -- --offline` exits 0.
   - `npm run check:install -- --from local <plugin>` exits 0 and prints the new version. It runs in a throwaway configuration, because this checkout and an installed `the-claude-factory` can't both be added under the same marketplace name.
   - With the owner's approval of the spend, a local smoke eval: `claude plugin eval plugins/<plugin> --case <case> --runs 1 --ablation none --no-publish`, as `.claude/rules/plugins/evals.md` sets.

## Phase B: Before the merge, on merge day

1. **Review the diff yourself** before you ask to push: run `/code-review` on the branch with the `code-review` skill. For changed scripts and hooks, also launch the `pr-review-toolkit:silent-failure-hunter` and `pr-review-toolkit:pr-test-analyzer` agents when the `pr-review-toolkit` plugin (marketplace `claude-plugins-official`) is installed; when it isn't, say so instead of skipping the step silently. Fix what the reviews find, or report it to the owner when it needs a decision.
2. **Date the release** with the `docs-maintenance` skill, for every plugin `npm run release:status` lists as changed or untagged:
   - `npm run release:changelog -- <plugin>` turns `## [Unreleased]` into `## [X.Y.Z] - <today in UTC>`, adds an empty `## [Unreleased]` above it and writes the compare and release links. It exits 1 and changes nothing when `## [Unreleased]` is empty: stop and ask the owner what the version changes.
   - Write the release line in the root `CHANGELOG.md`.
   - For a version already dated on an earlier day, `npm run release:changelog -- <plugin> --redate` moves its heading to today in UTC and leaves its notes as they are; change the root `CHANGELOG.md` line's date to match. PC-11 fails the pull request until both say the merge day.
3. **Check what `release.yml` will publish**, on a committed tree:
   - `npm run release:notes -- <plugin>` for every plugin builds the Release body `release.yml` will publish; it exits 1 when a version has no dated section with notes, and a failure there would stop the release loop at that plugin. Until merge day, Validate runs it with `--pending`, which lets the `[Unreleased]` notes stand for a version not dated yet; on `main` it runs without it.
   - `claude plugin tag plugins/<plugin> --dry-run` prints `<plugin>--v<version>`; it exits 1 while any file under the plugin is uncommitted.
   - `find plugins/<plugin> -type l` lists no link out of the plugin.
4. **List for the owner** what will ship: `git fetch origin main && npm run release:status`. `changed:` lines are the new versions, and `untagged:` lines are current versions on `main` that this merge's release will also tag. The PC-04 findings of `npm run check:consistency` are versions that need a backfill (Backfill below) before Validate's `Checks` can pass.
5. **Ask the owner to authorize the push**, then drive the pull request with `github-operations:auto-pr-lifecycle`. On the pull request:
   - Validate's `Checks` job must pass. Its `Debt` job reports the checks DEBT items hold back and never blocks.
   - `claude-code-review.yml` posts Claude's review on every push, as inline comments and one summary per push, when the owner has enabled it; `auto-pr-lifecycle` answers and resolves its findings.
   - `evals.yml` runs the suite of each changed plugin that has one, when the owner has enabled it, at the pass bar `.claude/rules/plugins/evals.md` sets.
   - `npm run check:install -- --from <pull request branch> <plugin>` installs what users will get from the branch.

## Phase C: Merge and release

1. **Merge** only with the owner's authorization, Validate's `Checks` green on a run from today in UTC, and every review resolved.
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

## The owner's one-time setup

The Claude workflows stay inert until the owner sets these in the repository's GitHub settings; tell the owner when one is missing, never ask for a value:

- an environment named `claude`, holding the secrets `ANTHROPIC_API_KEY` (for `claude-code-review.yml`) and `CLAUDE_CODE_OAUTH_TOKEN` (for `claude.yml` and `evals.yml`, created with `claude setup-token`);
- the repository variables `CLAUDE_CODE_REVIEW` and `CLAUDE_EVALS`, each set to `enabled`.
