---
name: plugin-releases
description: Releases a plugin version of this marketplace, with the checks before the merge, the changelog date, the tag and GitHub Release, and the checks after. Use whenever a plugin's new version is about to be merged or published, a release or tag needs to be created or verified, a version on main has no tag, or someone asks how users receive an update, even if they only say "ship it" or "publish the new version".
---

# Plugin releases

Plugins here are relative-path entries, so users receive whatever version is on `main` the moment a merge lands. Every check happens before the merge; after it, the work is tagging and confirming what users got.

## Facts (official, unless marked)

From code.claude.com/docs/en/plugins/publish (Release a new version, Tag a release), dependencies (Create a release tag) and cli-reference (`plugin tag`):

- A release reaches users when the changed `version` is pushed to the branch the marketplace serves. Users get it with `claude plugin update <plugin>@the-claude-factory` or with auto-update, which is off by default.
- The docs require a tag only when other plugins declare a version range on this one, because ranges resolve against tags. The tag is `<plugin-name>--v<version>`, matching `version` in that commit's `plugin.json`; in a relative-path marketplace the marketplace repository holds it.
- `claude plugin tag [path]` creates an annotated tag after it validates the plugin, checks that `plugin.json` and the marketplace entry agree, requires a clean working tree under the plugin directory and refuses an existing tag. `--dry-run` prints the plan; `--push` sends the tag to `--remote` (default `origin`).
- Cloud sessions can't create tags or Releases (tested 2026-11-13): the cloud proxy refuses tag pushes and answered 403 to `POST /repos/{owner}/{repo}/git/refs` and `POST /repos/{owner}/{repo}/releases`, with the session credential and with the owner's personal token, and the GitHub MCP servers have no tool for either. GitHub Actions can: `.github/workflows/release.yml`, which runs after `Validate` succeeds on `main` or through `workflow_dispatch`. A cloud session can start that dispatch (`gh api repos/nerymurillohnd/the-claude-factory/actions/workflows/release.yml/dispatches -f ref=main`, or the GitHub MCP tool `actions_run_trigger` with `method: run_workflow`).

## Project conventions

These go beyond the docs and stay unless the owner changes them:
- Every released version gets a tag and a GitHub Release with the same name, never a draft or prerelease. The Release body is that version's changelog section, then `claude plugin update <plugin>@the-claude-factory`.
- A plugin's `## [x.y.z]` changelog headings are exactly its tags, and its latest tag equals `version` in `plugin.json` on `main`.
- Tags made by `release.yml` are unsigned, because signing in CI would put the key in a GitHub secret; commits stay signed.
- Never move, delete or reuse a tag. A fix ships as a new version, never under one already released.

## Steps

1. **Check each released plugin before the merge**, and show the raw output:
   - `claude plugin validate --strict plugins/<plugin>` and `claude plugin validate --strict .`
   - `claude plugin tag plugins/<plugin> --dry-run`
   - `find plugins/<plugin> -type l`: every link resolves inside the plugin, since a link outside it doesn't reach users
   - `README.md`, `CHANGELOG.md` and `plugin.json` agree on components, prerequisites, the minimum Claude Code version (`engines`) and the version.
2. **List for the owner** and confirm each one is meant to ship: every plugin whose version on the branch differs from `origin/main`, and every version on `origin/main` that has no tag yet (an earlier release didn't run).
3. **Install what users will get**, from the branch and from `main`, in throwaway configurations so the owner's own setup stays untouched:
   ```bash
   T="$(mktemp -d)"
   env CLAUDE_CONFIG_DIR="${T}/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="${T}/cache" \
     claude plugin marketplace add "nerymurillohnd/the-claude-factory#<branch>"
   env CLAUDE_CONFIG_DIR="${T}/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="${T}/cache" \
     claude plugin install <plugin>@the-claude-factory
   env CLAUDE_CONFIG_DIR="${T}/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="${T}/cache" \
     claude plugin list --json
   env CLAUDE_CONFIG_DIR="${T}/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="${T}/cache" \
     claude plugin details <plugin>
   ```
   `claude plugin list --json` shows the installed version; `claude plugin details` shows the components and the `Always-on` cost. Repeat with `#main` in a second folder, report the new version and the `Always-on` figure against `main`, then delete both folders.
4. **Date the release** with today's UTC date, the day `release.yml` will tag it. Run the `docs-maintenance` event "A plugin gets a new version": `changelog-writer` turns `## [Unreleased]` into `## [X.Y.Z] - YYYY-MM-DD` with its compare and tag links, then `plugin-readme-writer`, then the root `CHANGELOG.md` and the catalog row.
5. **Merge** only with the owner's authorization, every check green and every review resolved.
6. **Release.** `Validate` on `main` starts `release.yml`, which tags each plugin whose version has no tag yet and creates its GitHub Release. Start it by hand with `workflow_dispatch` only when `Validate` passed, no release run exists for the merge, and the owner says so.

   Outside a cloud session, the documented command also tags: `claude plugin tag plugins/<plugin>` creates the annotated tag and `claude plugin tag plugins/<plugin> --push` also pushes it, run from a clean checkout of the released commit on `main` and only with the owner's authorization. In a session the same command is `/plugin tag plugins/<plugin> [--dry-run] [--push] [--force]`. `release.yml` skips any version whose tag already exists, so a tag made by hand gets no GitHub Release unless one is also created by hand; prefer the workflow.
7. **Verify**, and show the raw output:
   - `git ls-remote --tags origin '<plugin>--v*'` lists exactly the changelog's `## [x.y.z]` versions
   - the latest tag equals `version` in `plugin.json` on `main`, and `plugin.json` at the tagged commit holds it
   - the tag's commit is an ancestor of `main` (`git merge-base --is-ancestor <tag> origin/main`)
   - the GitHub Release has the tag's name and is neither a draft nor a prerelease (`gh api repos/nerymurillohnd/the-claude-factory/releases/tags/<plugin>--v<version>`)
   - step 3 from `#main` now installs the new version.
8. **If `Validate` fails after the merge**, tell the owner at once: users who update already have the merged version. The fix goes in a new pull request with its own version bump.

## What users run

From code.claude.com/docs/en/plugins/publish (Ship updates to users) and host-marketplace (Turn on auto-update). The release notes and the README give users these:
- `claude plugin update <plugin>@the-claude-factory [--scope <scope>]` installs the new version. Before Claude Code 2.1.281, `update` without `--scope` assumed `user` and failed for project- or local-scope installs.
- `claude plugin marketplace update the-claude-factory` refreshes the listings only; installed plugins keep their versions.
- `/reload-plugins` loads the new version into a running session.
- Auto-update is off by default for this marketplace; each user turns it on under **Marketplaces** in `/plugin`.

## What can block a release on this branch

`release.yml` here waits for a `Validate` workflow and calls `scripts/release/release-notes.py`; neither exists on the redesign branch. Until both are rebuilt, a merge of this branch releases nothing automatically. Say so before any merge.
