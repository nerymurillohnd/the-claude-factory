# Versioning, releases, renames and updates

Checked 2026-10-25 against `/en/plugins/loading` (Versions and updates), `/en/plugins/host-marketplace`, `/en/plugins/publish`, `/en/plugins/dependencies`, `/en/plugins/cli-reference` (`plugin tag`), Claude Code v2.1.310.

## Contents
- How users receive a release
- Choose: bump or omit `version`
- Release checklist
- Tags
- Holding users on a version, release channels
- Rename or remove a published plugin
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

## Choose: bump or omit `version`

| | Bump `version` each release | Omit `version` everywhere |
| :-- | :-- | :-- |
| Users update when | You change the string | Any commit changes the plugin's directory (relative path) or the source repo (github/url) |
| Good for | Curated releases, changelogs, SemVer, dependency ranges | Fast-moving plugins where every merged commit should ship |
| Risk | Forgetting the bump ships nothing to existing users | Every commit is a release; a broken commit reaches users who update |
| `validate --strict` | Passes | Missing `version` is a warning, which `--strict` turns into a failure → validate that plugin without `--strict` |

Never set `version` in both `plugin.json` and the entry: `plugin.json` wins silently and `validate` reports `Entry declares version "<a>" but <path>/plugin.json says "<b>"`. In a multi-plugin marketplace, keep versions in each `plugin.json` and none in `marketplace.json`.

The value isn't checked against SemVer; SemVer is a convention you choose. Staying in `0.x` signals no stability promise yet. This repository takes the first column: every plugin sets `version` in `plugin.json`, follows SemVer, and bumps it in its release.

## Release checklist

1. Decide the bump from the user-facing change (or confirm the plugin is unversioned on purpose).
2. Update `version` in `plugin.json` and the plugin's `CHANGELOG.md` before the change reaches the default branch, so it never holds changed files under an old version. In this repository the release stage of `.claude/rules/workflow.md` decides how: the bump goes in the change's pull request, as its own signed commit.
3. `claude plugin validate --strict` on the plugin directory (no `--strict` if it omits `version` on purpose) and `claude plugin validate .` at the marketplace root; raw output in the hand-back.
4. List what the push publishes — each plugin and its new version — and get the user's explicit go-ahead before pushing or merging to the default branch.
5. In release notes or the README, tell users how to update (`claude plugin update <plugin>@<marketplace>`) and that auto-update is opt-in.

## Tags

Tags don't deliver anything. In general they are needed only when other plugins declare a version range on yours, because ranges resolve against tags named `<plugin>--v<version>`. In this repository `release.yml` creates that tag for every new version after the merge, so never create one by hand. `claude plugin tag [path]` checks that `plugin.json` and any marketplace entry agree, then creates that annotated tag; `--dry-run` previews, `--push` pushes (needs the user's approval). It refuses a dirty tree, an existing tag, or a missing `version`. For a relative-path plugin, the tag lives in the marketplace repo on a commit whose `plugin.json` holds that version. A GitHub Release is for people, not for Claude Code.

## Holding users on a version, release channels

- An entry with a `github`/`url`/`git-subdir` source can pin `ref` (branch/tag) and `sha` (40-char commit). With `sha`, users get exactly that commit even if the ref later moves or is deleted.
- Users can add `owner/repo#stable` to follow a branch or tag of the catalog.
- For stable and early-access tracks, host two marketplaces with **different `name` values** whose entries point at different refs, and give each ref a different `version` (or none). Claude Code has no channel concept, and one marketplace serves one version of each plugin.

## Rename or remove a published plugin

Users' `enabledPlugins` and `pluginConfigs` are keyed by `<name>@<marketplace>`, so a changed `name` breaks every install with `Plugin "<name>" not found in marketplace`. Avoid renames; change `displayName` instead.

When it's unavoidable, add a top-level `renames` map to `marketplace.json`:

```json
{
  "renames": {
    "formatter": "code-formatter",
    "legacy-linter": null
  }
}
```

- Old → new migrates users: the plugin loads under the new name and Claude Code rewrites the old keys in user/project/local settings. `null` drops a removed plugin. Managed settings can't be rewritten, so the notice repeats there until an admin edits them.
- Users who added the marketplace from git see `Plugin "<name>" not cached at <path>` until they run `/plugin install <new>@<marketplace>` once. Say so in the release notes.
- Treat `renames` as append-only history; on a second rename add a new entry instead of editing the old one. `validate` rejects cycles and chains that don't end in `null` or a listed name (`renames.<name>: chain does not resolve`).
- Don't reuse a name that appears as a key in `renames` (our advice, not a documented rule: the chain is followed from the old name, so reusing it is ambiguous).
- `"forceRemoveDeletedPlugins": true` uninstalls plugins that are neither listed nor renamed from users' machines at session start (managed-settings installs stay). Without it, a removed plugin stays installed and errors.

## What a marketplace cannot do

No field turns on auto-update, installs or enables a plugin for users, shows different entries to different users, marks a plugin deprecated (remove it, map it to `null`, optionally force-remove), or carries git credentials. Separate audiences need separate marketplaces; fleet-wide enablement is a managed-settings job (`/en/plugins/org`).
