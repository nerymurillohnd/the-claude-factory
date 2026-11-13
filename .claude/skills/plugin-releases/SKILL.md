---
name: plugin-releases
description: Releases a plugin version of this marketplace, with the checks before the merge, the changelog date, the tag and GitHub Release, and the checks after. Use whenever a plugin's new version is about to be merged or published, a release or tag needs to be created or verified, a version on main has no tag, or someone asks how users receive an update, even if they only say "ship it" or "publish the new version".
---

# Plugin releases

Plugins here are relative-path entries, so users receive whatever version is on `main` the moment a merge lands. Every check happens before the merge; after it, the work is tagging and confirming what users got.

## Before you start

Status checked on 2026-11-13: `release.yml` waits for a `Validate` workflow that doesn't exist yet, so a merge tags and releases nothing on its own; only `workflow_dispatch` runs it. Check `.github/workflows/` before step 5, and stop there if `validate.yml` is still missing. Once it exists, delete this section.

## Facts (official, unless marked)

From code.claude.com/docs/en/plugins/publish (Release a new version, Tag a release), dependencies (Create a release tag) and cli-reference (`plugin tag`):

- A release reaches users when the changed `version` is pushed to the branch the marketplace serves. Users get it with `claude plugin update <plugin>@the-claude-factory` or with auto-update, which is off by default.
- The docs require a tag only when other plugins declare a version range on this one, because ranges resolve against tags. The tag is `<plugin-name>--v<version>`, matching `version` in that commit's `plugin.json`; in a relative-path marketplace the marketplace repository holds it.
- `claude plugin tag [path]` creates an annotated tag after it validates the plugin, checks that `plugin.json` and the marketplace entry agree, requires a clean working tree under the plugin directory and refuses an existing tag. `--dry-run` prints the plan; `--push` sends the tag to `--remote` (default `origin`).
- Cloud sessions can't create tags or Releases: the cloud proxy refuses tag pushes and answers 403 to `POST /repos/{owner}/{repo}/git/refs` and `POST /repos/{owner}/{repo}/releases`, with the session credential and with the owner's personal token, and the GitHub MCP servers have no tool for either (tested 2026-11-13). GitHub Actions can: `.github/workflows/release.yml`, which runs after `Validate` succeeds on `main` or through `workflow_dispatch`. A cloud session starts that dispatch with `gh api repos/nerymurillohnd/the-claude-factory/actions/workflows/release.yml/dispatches -f ref=main`, or with the MCP tool `github:actions_run_trigger` (`method: run_workflow`, `owner: nerymurillohnd`, `repo: the-claude-factory`, `workflow_id: release.yml`, `ref: main`).

## Project conventions

These go beyond the docs and stay unless the owner changes them:
- Every released version gets a tag and a GitHub Release with the same name, never a draft or prerelease. The Release body is that version's changelog section, then `claude plugin update <plugin>@the-claude-factory`.
- A plugin's `## [x.y.z]` changelog headings are exactly its tags, and its latest tag equals `version` in `plugin.json` on `main`.
- Tags made by `release.yml` are unsigned, because signing in CI would put the key in a GitHub secret; commits stay signed.
- Never move, delete or reuse a tag. A fix ships as a new version, never under one already released.

## Steps

1. **Check each released plugin before the merge**, and show the raw output:
   - `claude plugin validate --strict plugins/<plugin>` and `claude plugin validate --strict .`
   - `claude plugin validate --profile directory --strict plugins/<plugin>`, and for a mod (`tests/*.test.ts(x)`) `claude plugin test plugins/<plugin>`
   - `npm run check:consistency`: names, `renames`, changelog tags, README and catalog agree
   - `claude plugin tag plugins/<plugin> --dry-run`, on a committed tree: it exits 1 while any file under the plugin is uncommitted
   - `find plugins/<plugin> -type l`: every link resolves inside the plugin, since a link outside it doesn't reach users
   - `README.md`, `CHANGELOG.md` and `plugin.json` agree. Take the components from `claude --plugin-dir plugins/<plugin> plugin details <plugin>` and the version and minimum Claude Code version from `jq '{version, engines}' plugins/<plugin>/.claude-plugin/plugin.json`, and compare them with the README's components, Prerequisites and minimum Claude Code version, and with the `## [Unreleased]` notes.
2. **List for the owner** and confirm each one is meant to ship. From the repository root:
   ```bash
   git fetch origin main && npm run release:status
   ```
   `changed: <plugin> <old> -> <new>` lines are the plugins whose version on the branch differs from `origin/main` (`new` for a plugin not there yet); `untagged: <plugin>--v<version>` lines are versions on `origin/main` with no tag yet, which means an earlier release didn't run. It prints nothing when there is nothing to report.
3. **Install what users will get**, in a throwaway configuration so the owner's own setup stays untouched. Run it once with `<ref>` set to the pull request's branch as pushed to GitHub, then once with `<ref>` set to `main`:
   ```bash
   npm run check:install -- --from <ref> <plugin>
   ```
   It prints `claude plugin list --json`, with the installed version and any `errors`, and `claude plugin details`, with the components and the `Always-on` cost, then validates the installed copy and runs a mod's tests; it exits 1 on the first failure. Report the branch's version and `Always-on` figure against `main`'s. A plugin new in this release is not on `main` yet, so its `main` install fails with `not found in marketplace`.
4. **Write the release into the documents** with the `docs-maintenance` skill, dated with today's UTC date, the day `release.yml` will tag it:
   - the plugin's `CHANGELOG.md`: `npm run release:changelog -- <plugin>` turns `## [Unreleased]` into `## [X.Y.Z] - YYYY-MM-DD`, with the version from `plugin.json` and today's UTC date (`--date YYYY-MM-DD` sets another), adds an empty `## [Unreleased]` above it and points `[Unreleased]` at a compare from the new tag and links the version to its release page. It exits 1 and changes nothing when `## [Unreleased]` is empty: stop and ask the owner what the version changes.
   - the plugin's `README.md`, where it depends on the version, such as the minimum Claude Code version
   - the release line in the root `CHANGELOG.md`, and the catalog row of the root `README.md` when it shows the version.

   If the merge happens on a later UTC day, change the date in both changelogs to that day before merging.
5. **Merge** only with the owner's authorization, every check green and every review resolved. Stop here if `release.yml` can't run (see Before you start).
6. **Release.** `Validate` on `main` starts `release.yml`, which tags each plugin whose version has no tag yet and creates its GitHub Release. Start it by hand with `workflow_dispatch` only when `Validate` passed, no release run exists for the merge, and the owner says so.


   **If the workflow can't run**, and only outside a cloud session with the owner's authorization: from a clean checkout of the released commit on `main`, `claude plugin tag plugins/<plugin> --push` creates and pushes the annotated tag (in a session: `/plugin tag plugins/<plugin> --push`). `release.yml` skips any version whose tag already exists, so a tag made by hand also needs its GitHub Release created by hand.
7. **Verify**, and show the raw output:
   - `git ls-remote --tags origin '<plugin>--v*'` lists exactly the changelog's `## [x.y.z]` versions
   - the latest tag equals `version` in `plugin.json` on `main`, and `plugin.json` at the tagged commit holds it
   - the tag's commit is an ancestor of `main` (`git merge-base --is-ancestor <tag> origin/main`)
   - the GitHub Release has the tag's name and is neither a draft nor a prerelease: `gh api repos/nerymurillohnd/the-claude-factory/releases/tags/<plugin>--v<version>` in a terminal session; in a cloud session, where `gh` is kept for search, the MCP tool `github:get_release_by_tag` (`owner: nerymurillohnd`, `repo: the-claude-factory`, `tag: <plugin>--v<version>`)
   - step 3 from `main` (`npm run check:install -- --from main <plugin>`) now installs the new version.
8. **If `Validate` fails after the merge**, tell the owner at once: users who update already have the merged version. The fix goes in a new pull request with its own version bump.

## Withdraw a version

Claude Code can't take a published version back: users who updated keep it until a newer one reaches them. To withdraw one, release the fix as a new version through this skill, then mark the withdrawn version `[YANKED]` in the plugin's `CHANGELOG.md` with the `docs-maintenance` skill, with the evidence that it was withdrawn. Never delete its section, its tag or its GitHub Release.

## What users run

From code.claude.com/docs/en/plugins/publish (Ship updates to users) and host-marketplace (Turn on auto-update). The release notes and the README give users these:
- `claude plugin update <plugin>@the-claude-factory [--scope <scope>]` installs the new version. Version note: before Claude Code 2.1.281, `update` without `--scope` assumed `user` and failed for project- or local-scope installs.
- `claude plugin marketplace update the-claude-factory` refreshes the listings only; installed plugins keep their versions.
- `/reload-plugins` loads the new version into a running session.
- Auto-update is off by default for this marketplace; each user turns it on under **Marketplaces** in `/plugin`.
