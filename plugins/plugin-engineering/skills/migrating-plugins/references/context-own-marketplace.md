# A marketplace the user maintains

You act as the publisher. You can edit the catalog (`.claude-plugin/marketplace.json`), each plugin's files and `.claude-plugin/plugin.json`, and the repository; you commit, tag and push only with the user's yes. You can't change users' machines, accounts or managed settings: a change reaches users when their copy of the catalog refreshes, and the rest is what they do from your notes. Read the gotchas and the two "How … changes the procedure" sections, then the section for the kind of change, then Verify.

## Contents

- [Gotchas](#gotchas)
- [How the build changes the procedure](#how-the-build-changes-the-procedure)
- [How the hosting changes the procedure](#how-the-hosting-changes-the-procedure)
- [Ship a catalog change](#ship-a-catalog-change)
- [Update: release a new version](#update-release-a-new-version)
- [Turn off or uninstall](#turn-off-or-uninstall)
- [Retire a plugin](#retire-a-plugin)
- [Relabel or rename a plugin](#relabel-or-rename-a-plugin)
- [Merge plugins](#merge-plugins)
- [Split a plugin](#split-a-plugin)
- [Move a plugin or a marketplace](#move-a-plugin-or-a-marketplace)
- [Verify](#verify)

## Gotchas

- Auto-update is off by default for every third-party marketplace, and no `marketplace.json` field turns it on. Users get your change only when they update, when they turn auto-update on, or when an admin sets it in managed settings.
- The docs state two ways what a catalog refresh delivers. Shell `claude plugin marketplace update` with no name "leaves your installed plugins at their current versions" (https://code.claude.com/docs/en/plugins/install#update-plugins-now), and it does the same with a name **(observed)**. But https://code.claude.com/docs/en/plugins/host-marketplace#turn-on-auto-update says users "receive your changes when they run `/plugin marketplace update <name>` in a session". Before writing the update notes, download both pages again and read both sections in full. If they still differ, tell the user about the conflict and test the in-session form on one machine. Until a test settles it, the notes give the update route from `assets/migration-notes.md`, which doesn't rely on either form.
- Removing an entry from `plugins` without a `renames` mapping leaves the plugin installed on users' machines, reporting `Plugin "<name>" not found in marketplace`. Map the old name in `renames`, to the new name or to `null`, in the same commit.
- A retirement takes effect as soon as a user's catalog has it: the key leaves their user, project and local settings and they see `Removed from the "<marketplace>" marketplace`. The plugin stops loading and its data stays until they uninstall it **(observed)**. Anything users must still do with the plugin has to happen before the push.
- `"forceRemoveDeletedPlugins": true` makes each session start uninstall every installed plugin from this marketplace that is neither listed nor renamed, from user, project and local scopes, and list it under **Flagged** as `Removed from marketplace`. Plugins that only managed settings installed stay. A `null` entry counts as removed, and the uninstall deletes the data directory with no way to keep it **(observed)**. The field covers every plugin missing from `plugins`, not only the one you retire.
- `renames` is append-only history: add a key for each rename, keep the old ones, and validate after every edit. From 2.1.323 one malformed entry no longer makes Claude Code ignore every other rename **(changelog)**, so on older versions one bad key breaks them all.
- A rename moves only settings keys: Claude Code rewrites the key in `enabledPlugins` and `pluginConfigs` in user, project and local settings (2.1.193+, **changelog**), and can't rewrite managed settings. Nothing else moves **(observed)**: disabled installs keep the old id, data directories stay under the old id, and a merge keeps only one `pluginConfigs` entry. `claude plugin list` shows no install of the new name until it is installed: git and URL marketplaces report `Plugin "<name>" not cached at <path>` until the user runs `/plugin install <new>@<marketplace>` once, which is what the notes give. That a later session start installs it on its own is **(observed)** only.
- A `renames` map migrates installs of this marketplace only. The same plugin in Anthropic's directory, an organization or managed settings needs its own stage, and so do users who added the marketplace in Claude: what a `renames` map does there isn't documented (see "Rename, merge or split" in `references/context-claude-account.md`).
- Changing `name` in `marketplace.json` doesn't rename the marketplace for users who already added it: `claude plugin marketplace update` keeps the name they registered, and `<plugin>@<new-name>` doesn't resolve for them **(observed)**. Plugin ids include the marketplace name, so a marketplace rename is a new marketplace.
- A push reaches every user at their next refresh. Rehearse every catalog change with [Verify](#verify) before the push: the rehearsal needs only the local commits.

## How the build changes the procedure

Read "How Claude Code decides there is an update" in `references/context-machine.md` first: it owns the order in which the version is computed. What each entry source changes for the publisher:

- **Relative path in a git-hosted marketplace**: the marketplace repository is the release. Bump `version` where the plugin keeps it, or commit to the plugin's folder when it tracks commits. Tags go on the marketplace repository.
- **Relative path in a marketplace added from a local path**: it loads in place, so every saved edit reaches users at their next session or `/reload-plugins`, whatever `version` says. There is no release step.
- **`github`, `url`, `git-subdir`**: the plugin's own repository is the release, and its tags go there. The catalog changes only when the entry pins `ref` or `sha`, which you then move.
- **`archive`**: publish the new zip, and put its digest in `sha256` with every new zip. An entry with `headersHelper` needs each user to accept the command again whenever the command or the archive URL changes.
- **`npm`**: set `version`, or the computed version is `unknown`.
- **`command`**: the version is a hash of what the command produced, and the entry's `version` is ignored. Changing the command or its `mode` stops it for every user until each one accepts the new command.
- **Components**: when the plugin also reaches Claude accounts (a marketplace added in Claude, the directory, an organization), what Claude loads and refuses (a top-level `bin/`, the file and size limits) is in "How the build changes the procedure" in `references/context-claude-account.md`; Update stage 2 checks it.
- **Dependents**: other plugins that declare this one with a version range resolve against `<name>--v<version>` tags, so each release needs its tag.

**Read in full**:

- https://code.claude.com/docs/en/plugins/loading#how-claude-code-computes-the-version
- https://code.claude.com/docs/en/plugins/loading#in-place-and-copied-plugins
- https://code.claude.com/docs/en/plugins/marketplace-reference#plugin-sources
- https://code.claude.com/docs/en/plugins/host-marketplace#change-the-command-of-a-command-source
- https://code.claude.com/docs/en/plugins/host-marketplace#authenticate-archive-downloads, with all its subsections
- https://code.claude.com/docs/en/plugins/dependencies#release-a-plugin-that-others-depend-on
- https://claude.com/docs/plugins/platform-support#compare-component-support-by-app

## How the hosting changes the procedure

Find the host from the add command users run and the repository's remote.

### Hosted in a public git repository

- **The add command**: `owner/repo` for GitHub, or the full URL for any other git host, because the shorthand always means github.com. The marketplace's name comes from `name` in `marketplace.json`, not from the repository name.
- **Releases** reach users through `claude plugin update`, **Update marketplace** in `/plugin`, or auto-update. Users who added `#<ref>` stay on that ref.
- **Files in Git LFS** arrive as pointer files, because the clone never downloads LFS content.
- **Users who added it in Claude** (**Customize > Plugins** > **Add marketplace**): Claude accepts GitHub and GitHub Enterprise repositories and public GitLab and Bitbucket repositories, up to 25 marketplaces per account, 500 plugins per marketplace and a 512 MB repository archive. They get updates with **Check for updates**, or with **Sync automatically** on. A move to a host Claude doesn't accept cuts them off.

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#host-your-marketplace
- https://code.claude.com/docs/en/plugins/host-marketplace#keep-plugin-files-out-of-git-lfs
- https://claude.com/docs/plugins/platform-support#compare-installation-sync-and-admin-controls
- https://claude.com/docs/cowork/guide/plugins#use-a-git-repository-as-a-marketplace
- https://claude.com/docs/cowork/guide/plugins#limits

### Hosted in a private git repository

Claude Code clones with git on each user's machine, with prompts turned off, using credentials the machine already stores. Neither Claude Code nor `marketplace.json` carries a token.

- **What users need**: SSH with a key loaded in `ssh-agent` and the host in `known_hosts`, or HTTPS with a credential the helper already stores (on GitHub, the first two commands in the block below store it). `GITHUB_TOKEN` in the environment alone doesn't authenticate.
- **Auto-update**: the background check never prompts. When the credential helper would have to prompt, the update fails quietly and users stay on their last checkout. `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` keeps the checkout without a re-clone.
- **A release that reaches only some users** is usually this: their credentials can't answer in the background. The notes give those users these steps, in their shell: on GitHub over HTTPS, store a credential, then update the plugin. Over SSH, they load the key in `ssh-agent` instead of the first two lines.

  ```bash
  gh auth login
  gh auth setup-git
  claude plugin update <plugin>@<marketplace>
  ```

- **Users without access to the host** can install only entries whose sources they can reach, such as `archive` sources or public repositories.
- **The organization route**: a Team or Enterprise organization can distribute the repository from claude.ai instead, where users' git credentials aren't involved (see `references/context-organization.md`).

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#grant-access-to-a-private-marketplace
- https://code.claude.com/docs/en/plugins/host-marketplace#what-background-auto-update-does-with-credentials
- https://code.claude.com/docs/en/plugins/host-marketplace#serve-users-who-have-no-git-host-account
- https://code.claude.com/docs/en/plugins/install#add-a-private-marketplace
- https://code.claude.com/docs/en/plugins/install#auto-update-from-a-private-marketplace

### Hosted as a `marketplace.json` URL

Claude Code downloads only the file, so every entry needs a source it can fetch on its own.

- **Relative-path entries** fail at install with `its marketplace entry path does not stay inside the marketplace directory`. Use `github` or `archive` sources, or host the marketplace in git.
- **Download limits**: 5 MiB and 10 seconds for `marketplace.json`; 256 MiB, 120 seconds and five redirects for an `archive` zip, plus extraction limits.
- **Authenticated downloads**: `headers` on the marketplace's `url` source work on any version; `headersHelper` there, and `headers` or `headersHelper` on an entry, need 2.1.238+. An entry with `headersHelper` must set `"strict": false`.
- **An entry's `headersHelper`** runs only when a user installs or updates that one plugin by itself and accepts the command. Auto-update, **Update marketplace**, bulk installs, suggestions and installs as a dependency never run it; they list the plugin in the `/plugin` Errors tab. A release that changes the command or the archive URL is refused until each user updates the plugin by itself and accepts again; a change in the query string alone doesn't count, except in the VS Code extension or with `--accept-command`.
- **A marketplace `url` source's `headersHelper`** lives in users' settings, not in your catalog. From user, `--settings` or managed settings it runs without asking, including in background refreshes; from a project's settings only after the user trusts that folder.
- A redirect to another origin drops every header.

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#avoid-relative-path-entries-in-a-url-hosted-marketplace
- https://code.claude.com/docs/en/plugins/host-marketplace#stay-within-the-download-limits-for-hosted-files
- https://code.claude.com/docs/en/plugins/host-marketplace#authenticate-archive-downloads, with all its subsections
- https://code.claude.com/docs/en/plugins/marketplace-reference#archive-plugin-source
- https://code.claude.com/docs/en/plugins/troubleshooting#plugins-with-relative-paths-fail-in-url-based-marketplaces

### Hosted on a local path or shared directory

Users add the folder's path, and relative-path plugins load in place from it.

- **Releases**: saved edits reach users at their next session start or `/reload-plugins`, with no update step and no version bump. A half-finished edit reaches everyone at once, so edit a copy, and make the swap into the live folder the push stage of [Ship a catalog change](#ship-a-catalog-change).
- **Plugins with remote sources** in the same catalog are copied and versioned as usual.
- **Symlinks**: only links that resolve inside the plugin's own directory are kept.
- **Renames and retirements** work as in any marketplace. The `not cached` message is documented for git and URL marketplaces only.
- **An inline catalog** (a `settings` source in `extraKnownMarketplaces`) lives in the settings file itself: change it there.

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#edit-plugins-in-place-on-a-shared-directory
- https://code.claude.com/docs/en/plugins/host-marketplace#share-files-within-a-marketplace-with-symlinks
- https://code.claude.com/docs/en/plugins/create-marketplace#remove-the-marketplace-to-start-over

## Ship a catalog change

Every kind of change below ends with these stages. Run them from the marketplace root.

1. **Commit** everything the change touched.
   - Done when: the working tree is clean and the last commit is the change.

   ```bash
   git status --short
   git log -1 --oneline
   ```

2. **Rehearse** the change with [Verify](#verify): part A for a release or a split, part B for a rename, merge or retirement.
   - Done when: that part's checks pass.
3. **Push** with the user's yes. For a marketplace on a local path, swap the edited copy into the live folder instead.
   - Done when: the branch has nothing ahead of the remote (the first line shows no `[ahead`).

   ```bash
   git fetch -q origin && git status -sb | head -1
   ```

## Update: release a new version

**When**: the plugin's files changed and users should receive them. Keep the versioning model the plugin already uses; changing it is the user's decision. `<plugin-dir>` below is the entry's relative path, or a checkout of the plugin's own repository for a `github`, `url` or `git-subdir` source.

**Stages**:

1. **Version**: bump `version` where the plugin keeps it, in `plugin.json` or in the marketplace entry, never in both. A plugin that tracks commits keeps `version` out of both. For a plugin that sets it in both, present the fix and wait for the user's yes (SKILL.md, Step 4).
   - Done when: one command prints the new version and the other prints `null`, or both print `null` for a plugin that tracks commits.

   ```bash
   jq -r .version <plugin-dir>/.claude-plugin/plugin.json
   jq -r '.plugins[] | select(.name == "<plugin>") | .version' .claude-plugin/marketplace.json
   ```

2. **Compatibility**: check the plugin against every surface it reaches (see Components under [How the build changes the procedure](#how-the-build-changes-the-procedure)), and its `engines["claude-code"]` against the oldest version among users (2.1.323+, **changelog**).
   - Done when: for a plugin that reaches Claude accounts, the first command prints nothing and the counts stay within the limits that section of `references/context-claude-account.md` gives; and `engines` is `null` or admits the oldest version.

   ```bash
   ls -d <plugin-dir>/bin 2>/dev/null
   find <plugin-dir> -type f -not -path '*/.git/*' | wc -l
   du -sm <plugin-dir>
   jq '.engines' <plugin-dir>/.claude-plugin/plugin.json
   ```

3. **Validate** the marketplace root and the plugin.
   - Done when: both print `Validation passed` and neither prints `Entry declares version`, which is only a warning but means `plugin.json` silently wins. Report other warnings to the user.

   ```bash
   claude plugin validate .
   claude plugin validate <plugin-dir>
   ```

4. **Commit and rehearse**: stages 1 and 2 of [Ship a catalog change](#ship-a-catalog-change).
   - Done when: both checks pass.
5. **Tag**, when other plugins depend on a version range. `claude plugin tag` validates the plugin, checks the version against the entry and needs a clean tree under the plugin, so it runs after the commit.
   - Done when: the dry run shows the tag you expect, and the last command prints it.

   ```bash
   claude plugin tag <plugin-dir> --dry-run
   claude plugin tag <plugin-dir>
   git tag -l '<plugin>--v<version>'
   ```

6. **Push** the commit as stage 3 of [Ship a catalog change](#ship-a-catalog-change), and the tag, if stage 5 made one.
   - Done when: the push check passes and the remote lists the tag.

   ```bash
   git push origin refs/tags/<plugin>--v<version>
   git ls-remote --tags origin '<plugin>--v<version>'
   ```

7. **Notes**, when the release asks something of users: the update notes from `assets/migration-notes.md`.
   - Done when: the user has the notes.

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#keep-users-up-to-date
- https://code.claude.com/docs/en/plugins/publish#ship-updates-renames-and-removals
- https://code.claude.com/docs/en/plugins/dependencies#release-a-plugin-that-others-depend-on

### Hold users on a version, and release channels

One marketplace serves one version of each plugin at a time.

- **Pin an entry**: `ref` (branch or tag) or `sha` (commit) on a `github`, `url` or `git-subdir` source.
- **Pin the catalog**: users who add `owner/repo#stable` get that ref. A marketplace `ref` can be a full commit SHA (2.1.325+, **(changelog)**); older versions can't load a marketplace pinned that way.
- **Release channels**: two marketplaces with different `name` values, such as `stable-tools` and `latest-tools`, whose entries point at different refs. Give the refs different versions, or omit `version`, or users on a moving ref stay on their cached copy.

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#hold-users-on-one-version
- https://code.claude.com/docs/en/plugins/host-marketplace#run-release-channels

## Turn off or uninstall

A publisher can't turn a plugin off or uninstall it on users' machines: each user does that (see "Turn off" and "Uninstall" in `references/context-machine.md`). To stop offering it to everyone, retire it.

## Retire a plugin

**When**: the plugin should no longer be offered, which is what users mean by deprecate. There is no deprecation state.

**Stages**:

1. **Agree the timing with the user**: the date it stops working, what users must do with it first (export data, move to a replacement), and whether to uninstall it from machines after that date.
   - Done when: the user confirmed the date and the cleanup decision.
2. **A last release**, if the user wants one: it carries the announcement inside the plugin (in its description, a notice in its skills, a way to export its data), because a release still reaches users and the retirement doesn't. Run it with the stages of [Update](#update-release-a-new-version).
   - Done when: the update's stages pass, or the user declined.
3. **Announce** it with the retirement notes from `assets/migration-notes.md`, before the change ships.
   - Done when: the user says the notes went out.
4. **Remove the entry and map the name to `null`** in the same commit. The plugin's folder can stay; delete it only with the user's yes.

   ```json
   "renames": { "legacy-linter": null }
   ```

   - Done when: the name is gone from the list, the `null` mapping is there, and validation passes.

   ```bash
   jq '[.plugins[].name], .renames' .claude-plugin/marketplace.json
   claude plugin validate .
   ```

5. **Ship** it: [Ship a catalog change](#ship-a-catalog-change), with Verify part B.
   - Done when: its push check passes.
6. **Clean up, after the date, if the user chose it**: set `"forceRemoveDeletedPlugins": true` at the top level, then ship it. Check first that `plugins` lists every plugin that must stay installed.
   - Done when: the field is `true`, the list holds every plugin that stays, and the push check passes after the date the user set.

   ```bash
   jq '.forceRemoveDeletedPlugins, [.plugins[].name]' .claude-plugin/marketplace.json
   ```

To retire a whole marketplace, retire every plugin this way, then have the notes tell users to remove the marketplace, which uninstalls what is left with its data.

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#rename-or-remove-a-plugin
- https://code.claude.com/docs/en/plugins/host-marketplace#uninstall-removed-plugins-from-users-machines
- https://code.claude.com/docs/en/plugins/host-marketplace#work-around-what-a-marketplace-cant-do
- https://code.claude.com/docs/en/plugins/manifest-reference#defaultenabled, for why a last release can't turn the plugin off for users who already have it
- https://code.claude.com/docs/en/plugins/troubleshooting#plugin-not-found-in-marketplace

## Relabel or rename a plugin

**When**: relabel when only the label users see must change; rename only when `name` itself must change.

**Relabel**: change `displayName` in `plugin.json` and release it with the stages of [Update](#update-release-a-new-version). Nothing migrates.

**Rename stages**:

1. **New name in the files**: the entry's `name`, `name` in `plugin.json`, and the folder if you rename it, with the entry's `source` changed to the new folder. `claude plugin validate` passes with a `source` that still points at the old folder, and the break shows only at install **(observed)**.
   - Done when: the first command lists the new name and not the old one, the second prints the new name, and the last finds the manifest folder at the path the third prints.

   ```bash
   jq -r '.plugins[].name' .claude-plugin/marketplace.json
   jq -r .name <plugin-dir>/.claude-plugin/plugin.json
   jq -r '.plugins[] | select(.name == "<new>") | .source' .claude-plugin/marketplace.json
   ls -d <that-path>/.claude-plugin
   ```

2. **The `renames` entry**, in the same commit as stage 1, or in the next commit if stage 1 already shipped without it:

   ```json
   "renames": { "formatter": "code-formatter" }
   ```

   For a second rename, add `"code-formatter": "fmt-pro"` and keep the first: Claude Code follows the chain from the oldest name.
   - Done when: the map shows the new mapping and every older one.

   ```bash
   jq .renames .claude-plugin/marketplace.json
   ```

3. **Validate**.
   - Done when: it passes. A chain that cycles or ends anywhere other than `null` or a name in `plugins` fails with `renames.<old>: chain does not resolve`.

   ```bash
   claude plugin validate .
   ```

4. **Dependents and references**: change the old name in other plugins' `dependencies`, and in docs, hooks or scripts that call `/<old>:<skill>`.
   - Done when: the only matches left are the `renames` key and history such as a changelog. The pattern skips longer names that contain the old one.

   ```bash
   git grep -nE '(^|[^[:alnum:]_-])<old>([^[:alnum:]_-]|$)'
   ```

5. **Ship** it: [Ship a catalog change](#ship-a-catalog-change), with Verify part B.
   - Done when: its push check passes.
6. **Tag the new name**, when other plugins depend on it with a version range: ranges resolve against `<name>--v<version>` tags, and the renamed plugin has none yet (derived). Run stages 5 and 6 of [Update](#update-release-a-new-version).
   - Done when: those stages' checks pass, or no plugin depends on it with a range.
7. **Notes**: the rename notes from `assets/migration-notes.md`.
   - Done when: the user has the notes.

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#migrate-users-with-a-renames-map
- https://code.claude.com/docs/en/plugins/publish#rename-or-remove-a-plugin
- https://code.claude.com/docs/en/plugins/marketplace-reference#top-level-fields
- https://code.claude.com/docs/en/plugins/troubleshooting#plugin-not-cached-at

## Merge plugins

**When**: the plugins only make sense as one. When each stays useful alone and users should simply get them together, publish a bundle plugin whose `dependencies` lists them instead.

The docs have no merge procedure; these stages are derived from the rename rules. A `renames` map with several old names pointing at one new name passes `claude plugin validate` and migrates every old name **(observed)**.

**Stages**:

1. **The merged plugin**: build it under a new name, or keep one of the old names and merge the other into it.
   - Done when: the merged plugin validates on its own.

   ```bash
   claude plugin validate <merged-plugin-dir>
   ```

2. **Option keys that don't collide**: only one old `pluginConfigs` entry survives the merge, so give the merged plugin distinct `userConfig` keys. Read the old keys before stage 4 removes the old folders.
   - Done when: every old key has a counterpart in the merged plugin's keys, and the notes list the options users must set again.

   ```bash
   jq -r '.userConfig // {} | keys[]' <old-plugin-dir>/.claude-plugin/plugin.json
   jq -r '.userConfig // {} | keys[]' <merged-plugin-dir>/.claude-plugin/plugin.json
   ```

3. **Data**: neither old data directory moves. Tell users where the old data is, or have the merged plugin read the old paths once.
   - Done when: the notes or the plugin cover each old data directory.
4. **The catalog**: remove every old entry and map each old name to the merged one:

   ```json
   "renames": { "lint-helper": "code-quality", "format-helper": "code-quality" }
   ```

   - Done when: only the merged name is listed, every old name maps to it, and validation passes.

   ```bash
   jq '[.plugins[].name], .renames' .claude-plugin/marketplace.json
   claude plugin validate .
   ```

5. **Names and dependents**: commands become `/<merged>:<skill>`, and plugins that depend on an old name need a release that names the merged one. How `renames` applies to `dependencies` isn't documented, so don't rely on it.
   - Done when: the only matches left are the `renames` keys and history.

   ```bash
   git grep -nE '(^|[^[:alnum:]_-])(<old-1>|<old-2>)([^[:alnum:]_-]|$)'
   ```

6. **Ship** it: [Ship a catalog change](#ship-a-catalog-change), with Verify part B.
   - Done when: its push check passes.
7. **Notes**: the merge notes from `assets/migration-notes.md`.
   - Done when: the user has the notes.

**Read in full**: the sections under "Relabel or rename a plugin", and:

- https://code.claude.com/docs/en/plugins/dependencies#bundle-plugins-for-a-team
- https://code.claude.com/docs/en/plugins/dependencies#how-dependencies-behave-for-your-users
- https://code.claude.com/docs/en/plugins/manifest-reference#where-values-are-stored
- https://code.claude.com/docs/en/settings-reference#pluginconfigs, for which settings files hold the options a rename or merge rewrites; sensitive options live in the credential store, not in `pluginConfigs`

## Split a plugin

**When**: users use only part of a large plugin, and each part stands alone.

`renames` maps one old name to one target, so a split can't migrate users to both parts.

**Stages**:

1. **Keep the original name** for the part most users need, so its installs keep working.
   - Done when: the list still shows the original name.

   ```bash
   jq -r '.plugins[].name' .claude-plugin/marketplace.json
   ```

2. **The new plugin** as its own entry, with the moved parts taken out of the original.
   - Done when: validation passes with both entries.

   ```bash
   claude plugin validate .
   ```

3. **Carry existing users over**, if the user wants it: list the new plugin in the original's `dependencies`, and release the original with the stages of [Update](#update-release-a-new-version). Its next update installs the new dependency. Leave it out when users should choose the new part themselves.
   - Done when: the original lists the new plugin and its version moved, or the user chose to let users install it themselves.

   ```bash
   jq '.dependencies, .version' <original-plugin-dir>/.claude-plugin/plugin.json
   ```

4. **Ship** it: [Ship a catalog change](#ship-a-catalog-change), with Verify part A.
   - Done when: its push check passes.
5. **Notes**: the split notes from `assets/migration-notes.md`.
   - Done when: the user has the notes.

**Read in full**:

- https://code.claude.com/docs/en/plugins/measure
- https://code.claude.com/docs/en/plugins/dependencies#bundle-plugins-for-a-team
- https://code.claude.com/docs/en/plugins/dependencies#declare-dependencies
- https://code.claude.com/docs/en/plugins/manifest-reference#defaultenabled, for whether a new part starts on

## Move a plugin or a marketplace

These procedures are derived from the documented rules: a plugin's id is `<plugin>@<marketplace>`, and `renames` works only inside one marketplace.

**A plugin to another marketplace** (its id changes from `<plugin>@<old>` to `<plugin>@<new>`):

1. **Publish it in the new marketplace**, with the stages of [Update](#update-release-a-new-version) there.
   - Done when: Verify part C installs it from the new marketplace.
2. **Notes**: the move notes from `assets/migration-notes.md` (install from the new marketplace, then uninstall from the old one).
   - Done when: the user says the notes went out.
3. **Retire it in the old marketplace** with a `null` rename, once users have moved, following [Retire a plugin](#retire-a-plugin) from its stage 4.
   - Done when: those stages' checks pass.

**A marketplace to a new name**:

1. **Publish the new name as a new marketplace** at its own address, and keep the old one serving. Changing `name` in place leaves existing users on the old name (see Gotchas).
   - Done when: Verify part C installs each plugin from the new marketplace.
2. **Notes**: the move notes for every plugin, with the step to add the new marketplace first.
   - Done when: the user says the notes went out.
3. **Retire the old marketplace** once users have moved, as the end of [Retire a plugin](#retire-a-plugin) describes for a whole marketplace.
   - Done when: those stages' checks pass.

**A marketplace whose name Claude Code refuses** (reserved, or impersonating an official marketplace): here a rename in place is the documented fix, unlike the case above.

1. **Rename it** in `marketplace.json`, then ship it with [Ship a catalog change](#ship-a-catalog-change).
   - Done when: validation passes with no name error, and the push check passes.

   ```bash
   claude plugin validate .
   ```

2. **Notes**: users refresh the marketplace under the name they registered, instead of removing it. The notes give this command:

   ```bash
   claude plugin marketplace update <registered-name>
   ```

   - Done when: the user says the notes went out.

**A marketplace to another repository, host or folder, under the same name**:

1. **Publish it at the new address**.
   - Done when: the new address serves the last commit (for a folder, the folder holds the catalog).

   ```bash
   git ls-remote <new-url> HEAD
   ```

2. **Check whether the old address still serves it**: GitHub redirects a renamed or transferred repository (GitHub's behavior; the Claude docs don't cover it), and other hosts may not.
   - Done when: you know whether the old address answers with the new commit, and users needn't act while it does.

   ```bash
   git ls-remote <old-url> HEAD
   ```

3. **Choose how users re-point it**, without removing it: removing and re-adding the marketplace uninstalls its plugins with their data, so it is the last resort.
   - First, users change `source` in the `extraKnownMarketplaces` entry of the settings file that declares the marketplace (`~/.claude/settings.json` for one they added; managed settings are the admin's). Without that edit, an add from the new source is refused with `Cannot add marketplace "<name>": its source doesn't match its extraKnownMarketplaces entry in user or managed settings`.
   - Write the edited `source` as the same type and fields as the `<new-source>` users will add, or the add is still refused: two sources match only when the type and every field match, and a `ref` the add doesn't pass counts as different.
     - `<owner>/<repo>` is `{"source": "github", "repo": "<owner>/<repo>"}`.
     - An `https://github.com/` URL or any other git URL is `{"source": "git", "url": "<url>"}`: Claude Code records a GitHub URL as a `git` source.
   - Then either start a new session, after which Claude Code re-fetches the marketplace from the new source and shows `Plugins changed. Run /reload-plugins to activate.`, or run `claude plugin marketplace add <new-source>`, which applies it at once and keeps the installed plugins.
   - For a marketplace added from a local path only, the add re-points it even without the edit, printing `was already added from <old> and now points at <new>` **(observed)**.
   - Rehearse the route in a throwaway home (set up `<T>` as in [Verify](#verify)), with the new source written that way.
   - Done when: the add prints `Successfully added marketplace` or the re-point line, and the lists show the new source and the plugin still enabled.

   ```bash
   HOME="<T>/home" claude plugin marketplace add <old-source>
   HOME="<T>/home" claude plugin install <plugin>@<marketplace>
   jq --argjson s '<new-source-object>' '.extraKnownMarketplaces["<marketplace>"].source = $s' "<T>/home/.claude/settings.json" > "<T>/settings.json"
   mv "<T>/settings.json" "<T>/home/.claude/settings.json"
   HOME="<T>/home" claude plugin marketplace add <new-source>
   HOME="<T>/home" claude plugin marketplace list
   HOME="<T>/home" claude plugin list
   ```

4. **Notes**: the notes for a marketplace moved under the same name, from `assets/migration-notes.md`. Keep the old address serving until users have moved.
   - Done when: the user says the notes went out.

**Read in full**:

- https://code.claude.com/docs/en/plugins/marketplace-reference#reserved-names
- https://code.claude.com/docs/en/plugins/marketplace-reference#marketplace-sources
- https://code.claude.com/docs/en/plugins/install#manage-marketplaces
- https://code.claude.com/docs/en/plugins/loading#plugins-and-marketplaces-that-arent-on-disk-at-session-start
- https://code.claude.com/docs/en/plugins/troubleshooting#marketplace-is-already-added-from-a-different-source
- https://code.claude.com/docs/en/plugins/troubleshooting#cannot-add-marketplace-source-doesnt-match
- https://code.claude.com/docs/en/errors#claude-code-refuses-the-marketplace-name

## Verify

Rehearse the change as a user would see it, in a throwaway home, so the user's own setup is untouched. The procedure is derived and **(observed)** to work:

- Each Bash call starts a new shell, so set `HOME` on every `claude` command and write the folder the first block prints in place of `<T>`.
- Parts A and B install from a clone of the repository's own commits, so they work after the commit and before the push. `<after>` is the commit with the change. `<before>` is the commit users have now: before the push, the upstream head; for a rename, merge or retirement already under way, the newest commit whose catalog still lists the old name. The commands to find it follow the setup.
- The clone is added from a folder, so its relative-path plugins load in place: parts A and B check the catalog and the versions, not the cache. `not cached` never shows there.
- An entry with a `github`, `url` or `git-subdir` source installs from that remote, so part A sees a release of such a plugin only once its own repository has it; before that, rely on stage 3 of the update.

Set up the throwaway folder from the marketplace root. For a marketplace that isn't a git repository, use `cp -R` of the live folder instead of the clone, and in step 2 of each part copy the edited files over `<T>/mkt` instead of the checkout.

```bash
T="$(mktemp -d)" && git clone -q . "$T/mkt" && echo "$T"
```

Find `<before>`: the upstream head for a change not yet pushed, or the newest commit that still lists `<old>`.

```bash
git rev-parse @{upstream}
for c in $(git log --format=%H -- .claude-plugin/marketplace.json); do git show "$c:.claude-plugin/marketplace.json" | jq -e --arg n '<old>' 'any(.plugins[]; .name == $n)' >/dev/null && { echo "$c"; break; }; done
```

**Part A: a release or a split.**

1. Install the plugin as it was before the change.
   - Done when: the list shows the old version.

   ```bash
   git -C <T>/mkt checkout -q <before>
   HOME="<T>/home" claude plugin marketplace add <T>/mkt
   HOME="<T>/home" claude plugin install <plugin>@<marketplace>
   HOME="<T>/home" claude plugin list --json
   ```

2. Move the clone to the change and update the plugin.
   - Done when: the update prints `updated from <old> to <new>`, with `(+ 1 dependency: <new-plugin>)` for a split that carries users over, and the list shows the new version. `is already at the latest version` means the computed version didn't change.

   ```bash
   git -C <T>/mkt checkout -q <after>
   HOME="<T>/home" claude plugin marketplace update <marketplace>
   HOME="<T>/home" claude plugin update <plugin>@<marketplace>
   HOME="<T>/home" claude plugin list --json
   ```

**Part B: a rename, merge or retirement.**

1. Install every old name as it was before the change.
   - Done when: the list shows each old name enabled.

   ```bash
   git -C <T>/mkt checkout -q <before>
   HOME="<T>/home" claude plugin marketplace add <T>/mkt
   HOME="<T>/home" claude plugin install <old>@<marketplace>
   HOME="<T>/home" claude plugin list
   ```

2. Move the clone to the change, refresh the catalog, and list twice: the first list migrates the keys and still shows the old state, and the second shows the result **(observed)**. Don't wait for the `Renamed to` notice: it didn't print in `claude plugin list` in the rehearsal **(observed)**, so the settings are the proof.
   - Done when: the second list shows no old name enabled (a retired plugin shows as disabled), and `enabledPlugins` holds `<new>@<marketplace>` and no old key (no key at all for a retirement).

   ```bash
   git -C <T>/mkt checkout -q <after>
   HOME="<T>/home" claude plugin marketplace update <marketplace>
   HOME="<T>/home" claude plugin list
   HOME="<T>/home" claude plugin list
   jq .enabledPlugins "<T>/home/.claude/settings.json"
   ```

3. For a rename or a merge, install the new name once, as the notes tell git and URL users to.
   - Done when: the list shows `<new>@<marketplace>` enabled at the expected version.

   ```bash
   HOME="<T>/home" claude plugin install <new>@<marketplace>
   HOME="<T>/home" claude plugin list --json
   ```

**Part C: after the push, a fresh install from the real source.**

1. Add the marketplace with the command users run, and install.
   - Done when: the list shows the new version, or for a retired plugin the install fails with `not found in marketplace`. When the add fails for lack of credentials on a private repository (git reads its global configuration from `HOME`), report it and rely on parts A and B.

   ```bash
   HOME="<T>/fresh" claude plugin marketplace add <marketplace-source>
   HOME="<T>/fresh" claude plugin install <plugin>@<marketplace>
   HOME="<T>/fresh" claude plugin list --json
   ```

When the last part is done, delete the throwaway folder: it holds only copies, so deleting it needs no confirmation.

```bash
rm -rf <T>
```
