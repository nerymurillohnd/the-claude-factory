# How users receive a version

Checked 2026-10-25 against `/en/plugins/loading` (Versions and updates), `/en/plugins/host-marketplace`, `/en/plugins/publish`, `/en/plugins/dependencies`, `/en/plugins/cli-reference` (`plugin tag`), Claude Code v2.1.310.

This is background for building a plugin: what a version does on the user's machine, so the plugin you write ships the way you expect. Choosing the bump, writing the release notes, the pull request, the tag and the release are the release stage of `.claude/rules/workflow.md`; renaming, merging or removing a plugin is its renames stage. This skill does none of them.

## Contents
- How users receive a release
- Version in this repository
- Tags
- Holding users on a version, release channels
- Renames and removals
- What a marketplace cannot do

## How users receive a release

For a GitHub marketplace, the repo's default branch (or the `#ref` a user added) **is** the release: whatever it holds is what the next install or update fetches. There's no separate publish step and no review.

Claude Code computes a version for each installed plugin and replaces the cached copy only when that version changes:

1. `version` in the plugin's `plugin.json`, if set
2. else `version` in the marketplace entry, if set
3. else from the source: `github`/`url`/`git-subdir` → the source commit SHA (12 chars); a relative path inside a git-hosted marketplace → the commit SHA of the installed directory; `archive` → its SHA-256 (12 chars); a `git-subdir` version also carries a hash of the subdirectory path

Consequences:

- `version` set and not bumped → `claude plugin update` prints `<name> is already at the latest version (<v>).` and users keep the old copy. Meanwhile **new** installs fetch the current files under the same version string, so two different copies can carry one version (inferred from how the cache works; not stated in the docs).
- A marketplace a user added from a **local path** loads relative-path plugins in place, ignoring `version`. So a missed bump is invisible on your own machine when you added your marketplace from its local checkout; check the version by reading `plugin.json`, not by what loads locally.
- Background auto-update is **off** for third-party marketplaces; users turn it on per marketplace under `/plugin` → Marketplaces → Enable auto-update, or an admin sets `autoUpdate` in managed settings. `marketplace.json` has no field for it. Without it, users get changes only via `claude plugin update <plugin>@<marketplace>` or `/plugin marketplace update <name>`.
- A plugin updated mid-session keeps running the old path for hooks, MCP and LSP until `/reload-plugins`; monitors need a restart. Old version directories are removed 14 days later.
- Claude Code doesn't report usage to the author (`/en/plugins/measure`). Issues are the only signal, so check everything before the push.

## Version in this repository

Every plugin sets `version` in `plugin.json`, follows SemVer, and gets a new version in its release; no marketplace entry carries one. Claude Code itself does not check the value against SemVer, and an unversioned plugin would ship every commit as a release, which this repository does not do. `validate --strict` fails on a missing `version`, so it always runs with `--strict` here.

## Tags

Tags don't deliver anything. Plugin dependency ranges resolve against tags named `<plugin>--v<version>`, and a GitHub Release is for people, not for Claude Code. In this repository `release.yml` creates that tag and the release for every new version after the merge, so never create one by hand.

## Holding users on a version, release channels

- An entry with a `github`/`url`/`git-subdir` source can pin `ref` (branch/tag) and `sha` (40-char commit). With `sha`, users get exactly that commit even if the ref later moves or is deleted.
- Users can add `owner/repo#stable` to follow a branch or tag of the catalog.
- Claude Code has no channel concept, and one marketplace serves one version of each plugin: stable and early-access tracks need two marketplaces with different `name` values whose entries point at different refs.

## Renames and removals

Users' `enabledPlugins` and `pluginConfigs` are keyed by `<name>@<marketplace>`, so a changed `name` breaks every install with `Plugin "<name>" not found in marketplace` unless the marketplace's `renames` map migrates it. That is why a plugin's name is permanent and a new label goes in `displayName`. Renaming, merging or removing a published plugin is the renames stage of `.claude/rules/workflow.md`.

## What a marketplace cannot do

No field turns on auto-update, installs or enables a plugin for users, shows different entries to different users, marks a plugin deprecated (remove it, map it to `null`, optionally force-remove), or carries git credentials. Separate audiences need separate marketplaces; fleet-wide enablement is a managed-settings job (`/en/plugins/org`).
