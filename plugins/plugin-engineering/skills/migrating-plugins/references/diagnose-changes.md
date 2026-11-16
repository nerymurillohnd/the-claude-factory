# Diagnose updates, renames and removals that didn't land

Match the exact message, or the symptom when there is no message. Read the entry's official section in full before you apply its fix, because the section names variants this entry can't. Run each diagnostic once; when the fix doesn't hold, go back to the section instead of trying something else. A fix that is in SKILL.md's "Stop and confirm" list is marked **(confirm first)**: say what it will do and wait for the user's yes. For failures unrelated to an update, rename or removal, load `plugin-engineering:plugin-testing-and-debugging`.

A heading that starts with a code span quotes the message Claude Code or claude.ai shows, word for word, with `<placeholders>` for the parts that vary; the words after it say when it appears, and a note in parentheses says when the quote is only the start. A message the docs show as bold interface text is quoted in bold. Any other heading is a symptom.

## Contents

- [Checks to run first](#checks-to-run-first)
- [Updates](#updates)
- [Renames, merges and moves](#renames-merges-and-moves)
- [Removals and uninstalls](#removals-and-uninstalls)
- [Synced, managed and session-only plugins](#synced-managed-and-session-only-plugins)
- [Anthropic's directory](#anthropics-directory)
- [claude.ai organizations](#claudeai-organizations)

## Checks to run first

Run these in the user's shell, and keep the raw output:

```bash
claude --version
claude plugin list --json
claude plugin marketplace list
claude plugin details <name>
```

- From `claude plugin list --json`, note each object's `id` (`name@marketplace`, `name@inline`, `name@skills-dir`, `name@synced`), `scope`, `version`, `enabled`, `errors` and `notes`.
- From `claude plugin details`, note the source. For a plugin that isn't loaded, it exits `1` with a message that starts `Plugin "<name>" not found.`
- Most entries below are decided by one of those fields.

## Updates

**`<name> is already at the latest version (<version>).`**

- Cause: the computed version is unchanged. Usually `plugin.json` pins `version` and the author pushed commits without changing it. A relative-path plugin in a marketplace added from a local path isn't controlled by `version`: it loads its current files at every session start, so it has nothing to update.
- Fix (user): first refresh the catalog alone, because the version is compared against the machine's copy of the catalog (derived). Only when it prints `Successfully updated marketplace: <name>` has the publisher released nothing new: tell the user so. Any other output, such as `SSH authentication failed` or `HTTPS authentication failed` for a private git marketplace, is the problem to look up first.

  ```bash
  claude plugin marketplace update <marketplace>
  ```

- Fix (publisher): bump `version` where the plugin keeps it, or remove it from both `plugin.json` and the entry to track commits.
- Read in full: https://code.claude.com/docs/en/plugins/loading#versions-and-updates

**Auto-update never brings new versions**

- Cause: one of these:
  - auto-update is off for the marketplace, which is the default for every marketplace except Anthropic's official ones and those added from claude.ai;
  - `DISABLE_UPDATES`, `DISABLE_AUTOUPDATER` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set, which turns the whole pass off and hides the toggle;
  - the entry sets a `headersHelper`, which auto-update skips;
  - the computed version didn't change.
- Auto-update runs after a random delay of up to ten minutes after the first message of an interactive session, not at startup. A `command` source doesn't use auto-update: it reruns once per session on its own.
- Fix: the user opens **Marketplaces** in `/plugin`, selects the marketplace and selects **Enable auto-update**. Where one of those variables must stay set, set `FORCE_AUTOUPDATE_PLUGINS=1` too. Update a `headersHelper` plugin by itself:

  ```bash
  claude plugin update <plugin>@<marketplace>
  ```

- Read in full: https://code.claude.com/docs/en/plugins/loading#which-marketplaces-and-plugins-auto-update

**The installed plugin stays at the old version after `claude plugin marketplace update`**

- Cause: that shell command refreshes the marketplace's catalog and leaves installed plugins at their current versions. The docs say so for the form without a name; the form with a name does the same **(observed)**.
- Fix: update the plugin, or have the user open **Marketplaces** in `/plugin`, select the marketplace and choose **Update marketplace**, which also updates its installed plugins except `command`-source and `headersHelper` ones:

  ```bash
  claude plugin update <plugin>@<marketplace>
  ```

- Read in full: https://code.claude.com/docs/en/plugins/install#update-plugins-now

**`Plugin updated: <name> · Run /reload-plugins to apply`, but the session still uses the old version**

- Cause: a running session keeps the versions it loaded.
- Fix: ask the user to run `/reload-plugins` in the session, or to start a new one. When the reload warns that it would invalidate the prompt cache and ends `Run /reload-plugins --force to apply.`, the user reruns it with `--force` only if they accept that cost. Monitors need a session restart.
- Read in full: https://code.claude.com/docs/en/plugins/loading#when-auto-update-runs

**`Plugin "<name>" is not installed at scope user` on update**

- Cause: from 2.1.281, `claude plugin update` without `--scope` picks the most specific scope the plugin is installed at; older versions use `user`.
- Fix: pass the scope that `claude plugin list` shows, or update Claude Code:

  ```bash
  claude plugin update <plugin>@<marketplace> --scope <scope>
  ```

- Read in full: https://code.claude.com/docs/en/plugins/cli-reference#which-scope-the-command-updates

**`Auto-update for '<name>' is set by`** (the start of the error when the user toggles auto-update)

- Cause: a managed `extraKnownMarketplaces` entry sets `autoUpdate` for that marketplace.
- Fix: the admin changes the managed entry. The user can still update by hand with `claude plugin update`.
- Read in full: https://code.claude.com/docs/en/plugins/org#turn-auto-update-on-or-off-per-marketplace

**A plugin with `engines` doesn't install, update or load** **(changelog)**

- Cause (2.1.323+): the plugin's `engines["claude-code"]` range excludes the running Claude Code version. Install and update pick the newest version whose range fits.
- Fix: update Claude Code, or tell the publisher the range excludes the version in use. The field isn't in the docs yet: read the changelog entry.
- Read in full: the 2.1.323 entry for `engines["claude-code"]` in https://code.claude.com/docs/en/changelog, searched as "Check the changelog" in `references/reading-docs.md` shows

**An entry in the `/plugin` Errors tab shows a command and a `claude plugin update` command to run**

- Cause: one of these:
  - the publisher changed a `command` source's `command` or `mode`; once the user's catalog copy has the change, the once-per-session run stops until the user accepts the new command;
  - the entry sets a `headersHelper`, and background auto-update, or a session start for a plugin whose archive was never downloaded, reached it. Bulk installs, plugin suggestions and dependency installs refuse it the same way.
- Fix: the user runs the `claude plugin update` command the entry shows in their own terminal and accepts the command Claude Code shows. `-y` is ignored and `--accept-command` has no effect inside a Claude Code session, so Claude can't accept it for them.
- Read in full: https://code.claude.com/docs/en/plugins/host-marketplace#change-the-command-of-a-command-source and https://code.claude.com/docs/en/plugins/host-marketplace#installs-and-updates-that-refuse-the-command-instead-of-asking

**`Version: unknown` in `claude plugin list`**

- First check the source. `unknown` is the normal version for a plugin from a local directory with no git repository, from `npm`, and for a session-only, skills-directory or synced plugin whose manifest declares no `version`.
- Cause, for a git-sourced plugin (its own repository, or inside a git-hosted marketplace): Claude Code couldn't read the commit it uses as the version. An `unknown` version also hides whether an update arrived, so fix it before judging a release.
- Fix: run these in order, in the shell. `claude update` brings Claude Code to 2.1.302 or later, which clones in a format it can read the commit from; the marketplace update refreshes the commit for plugins inside the marketplace repository; the plugin update rewrites the recorded version.

  ```bash
  claude update
  claude plugin marketplace update <marketplace>
  claude plugin update <plugin>@<marketplace>
  claude plugin list
  ```

- It worked when `Version:` shows a 12-character commit ID.
- `claude plugin update` changes one scope's block per run. For a block still `unknown`, rerun it with that block's `Scope:` value:

  ```bash
  claude plugin update <plugin>@<marketplace> --scope <scope>
  ```

- Still `unknown` after that: stop and report it, as the section's "Get more help" link says.
- Read in full: https://code.claude.com/docs/en/plugins/troubleshooting#a-plugin-installed-from-a-git-repository-shows-version-unknown

**Marketplace updates fail every session while offline**

- Cause: when the background check can't reach the marketplace's git host, Claude Code tries to clone it again, and offline that fails too.
- Fix: set `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` to keep the existing checkout. For a fully offline fleet, seed the plugins directory with `CLAUDE_CODE_PLUGIN_SEED_DIR` instead.
- Read in full: https://code.claude.com/docs/en/plugins/troubleshooting#marketplace-updates-keep-failing-offline

**`SSH authentication failed` or `HTTPS authentication failed`** (after `Failed to clone marketplace repository:`, on an add or an update)

- Cause: one of these:
  - the repository itself: a misspelled `owner/repo`, a repository that doesn't exist, or a private one the user can't see ends in the same message;
  - credentials: Claude Code turns off git's prompts and askpass programs, including `GIT_ASKPASS`, and runs SSH in batch mode, so only credentials git gets without a prompt work. When git needed a prompt, the error includes `fatal: Cannot prompt because user interactivity has been disabled`, `terminal prompts disabled` or `fatal: unable to get password from user`.
- Fix:
  1. Confirm the repository exists and the user can reach it:

     ```bash
     git ls-remote <url>
     ```

  2. Check the credential for the protocol in use; it must succeed without a prompt. For SSH, the key must work without a passphrase prompt (for example, loaded in `ssh-agent`) and the host must already be in `known_hosts`:

     ```bash
     ssh -T git@<host>
     ```

     For HTTPS, with `GIT_ASKPASS` unset:

     ```bash
     env -u GIT_ASKPASS git -c core.askPass= ls-remote <url>
     ```

  3. When the HTTPS check fails on GitHub, the user stores a credential in their own terminal, because `gh auth login` asks them to sign in. For another host, the user stores a personal access token in their git credential helper.

     ```bash
     gh auth login
     gh auth setup-git
     ```

  4. Run the add or update again. It worked when it prints `Successfully added marketplace: <name>` or `Successfully updated marketplace: <name>`:

     ```bash
     claude plugin marketplace update <marketplace>
     ```

- For GitHub `owner/repo` sources, `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` makes Claude Code skip SSH.
- Read in full: https://code.claude.com/docs/en/plugins/troubleshooting#ssh-authentication-failed-or-https-authentication-failed

**A plugin from a private git marketplace stays at an old version**

- Cause: the background check for new commits uses the user's git credential helpers and never prompts. With a helper that would have to prompt, the update fails quietly and the existing checkout stays in place, so the plugins keep working from the last synced state. A `GITHUB_TOKEN` or other provider token in the environment authenticates only through a credential helper that reads it, such as the `gh` CLI's.
- Fix: refresh the catalog from the shell. When it fails with an authentication message, follow `SSH authentication failed` or `HTTPS authentication failed` above, then update the plugin:

  ```bash
  claude plugin marketplace update <marketplace>
  claude plugin update <plugin>@<marketplace>
  ```

- Read in full: https://code.claude.com/docs/en/plugins/host-marketplace#what-background-auto-update-does-with-credentials

## Renames, merges and moves

**`Plugin "<name>" not found in marketplace "<marketplace>"`, or `Plugin "<name>" not found in marketplace` for a plugin that used to work**

- Cause: one of these:
  - on install, the name isn't in the machine's copy of the catalog. A hint that starts `Your local copy may be out of date` or `The marketplace couldn't be refreshed` means the copy may be stale; with no hint, the name is the likeliest problem;
  - when a session loads an installed plugin, the publisher renamed or removed its entry without a `renames` entry. `claude plugin list` shows it as `× failed to load` **(observed)**.
- Fix (user): refresh the catalog, then install again. If the plugin is still missing, it was renamed or removed upstream: install the replacement the publisher names, or uninstall the old id.

  ```bash
  claude plugin marketplace update <marketplace>
  ```

- Fix (publisher): add `"<old>": "<new>"`, or `"<old>": null` for a removed plugin, to `renames` and push **(confirm first)**.
- Read in full: https://code.claude.com/docs/en/plugins/troubleshooting#plugin-not-found-in-marketplace and https://code.claude.com/docs/en/plugins/host-marketplace#migrate-users-with-a-renames-map

**`Plugin "<name>" not cached at <path>` after a rename**

- Cause: in a marketplace the user added from a git repository or a URL, the renamed plugin has no cached copy under its new name.
- Fix: install the new name once, then ask the user to run `/reload-plugins` in the session. The docs give `/plugin install <new>@<marketplace>` in a session; from the shell, add `--scope project` when the project's settings enable the plugin:

  ```bash
  claude plugin install <new>@<marketplace>
  ```

- Read in full: https://code.claude.com/docs/en/plugins/troubleshooting#plugin-not-cached-at

**After a rename, `claude plugin list` shows no install of the new name**

- Cause: the migration dropped the old install record and moved the settings key **(observed)**. The new name isn't installed until the user installs it; a later session start may install it on its own **(observed)**.
- Fix: install the new name at the scope the old one had, as the `not cached` entry above gives:

  ```bash
  claude plugin install <new>@<marketplace> --scope <scope>
  ```

**A disabled plugin still shows its old name after a rename** **(observed)**

- Cause: the migration skips installs set to `false`.
- Fix: uninstall the old id, adding `--keep-data` to keep its data **(confirm first)**, then install the new name if the user wants it:

  ```bash
  claude plugin uninstall <old>@<marketplace> --scope <scope>
  claude plugin install <new>@<marketplace> --scope <scope>
  ```

**`Renamed to "<new>" in the "<marketplace>" marketplace` keeps appearing**

- Cause: managed settings still enable the old key, and Claude Code can't rewrite managed settings.
- Fix: the admin changes managed `enabledPlugins` to the new key.
- Read in full: https://code.claude.com/docs/en/plugins/host-marketplace#migrate-users-with-a-renames-map

**Options or data are missing after a rename or merge**

- Cause: the migration rewrites the `enabledPlugins` and `pluginConfigs` keys, but data directories stay under the old id **(observed)**. In a merge, only one `pluginConfigs` entry survives **(observed)**. Sensitive options live in the system's credential store, and whether they move isn't documented.
- Fix:
  1. List which options are set; without flags the command prints no values:

     ```bash
     claude plugin configure <new>@<marketplace>
     ```

  2. Have the user set the missing ones in a session, with `/plugin configure <new>@<marketplace>` or **Configure options** in the plugin's details. Sensitive values are the user's to type. For non-sensitive values only, the shell form saves a JSON object from stdin:

     ```bash
     claude plugin configure <new>@<marketplace> --values-stdin < values.json
     ```

  3. After the shell form prints `Configuration saved. Restart Claude Code to apply it.`, start a new session.
  4. Copy or reread data from `~/.claude/plugins/data/<old-id>/`.

- Read in full: https://code.claude.com/docs/en/plugins/cli-reference#plugin-configure and https://code.claude.com/docs/en/plugins/manifest-reference#user-configuration

**`renames.<name>: chain does not resolve`** (from `claude plugin validate`)

- Cause: the chain cycles, or ends anywhere other than a name in `plugins` or `null`.
- Fix: point the last link at a current entry or at `null`, then validate again. From 2.1.323, one malformed entry no longer makes Claude Code ignore the marketplace's other renames **(changelog)**; on older versions, one bad entry voids them all.

  ```bash
  claude plugin validate .
  ```

- Read in full: https://code.claude.com/docs/en/plugins/marketplace-reference#validation-messages

**The marketplace was renamed, but users still see the old name** **(observed)**

- Cause: Claude Code keeps the name each user registered, and plugin ids include it.
- Fix: follow "A marketplace to a new name" under "Move a plugin or a marketplace" in `references/context-own-marketplace.md`.

**`Cannot add marketplace "<name>": its source doesn't match its extraKnownMarketplaces entry in user or managed settings`**

- Cause: the `name` in the fetched `marketplace.json` already has an `extraKnownMarketplaces` entry in user or managed settings with a different source, so Claude Code registers nothing. Two sources match only with the same type and the same value in every field: an entry with a `ref` the add didn't pass differs, and a `github` entry differs from an `https://github.com/` URL, which Claude Code records as a `git` source. A marketplace moved to a new address under the same name hits this.
- Fix, by what the user wants:
  - the declared source: Claude Code registers marketplaces declared in settings on its own, so read `claude plugin marketplace list` from Checks to run first (the docs give `/plugin marketplace list` in a session). When the name is missing, add it with the source typed the way the entry writes it.
  - the new source: edit or remove the entry in the user's settings file, then add the marketplace again. A new session also re-fetches a declared marketplace whose source changed. When managed settings declare it, the admin changes it.

  ```bash
  claude plugin marketplace add <source>
  ```

- Read in full: https://code.claude.com/docs/en/plugins/troubleshooting#cannot-add-marketplace-source-doesnt-match

## Removals and uninstalls

**`Failed to uninstall plugin "<id>":`, and the command exits `1`**

- Cause: when nothing follows about a settings file, the plugin isn't installed at the scope given; without `--scope`, uninstall acts on `user`. When the line continues with `"<plugin>" was not uninstalled:`, use the next two entries.
- Fix: rerun with the scope `claude plugin list` shows. When that is the plugin's last scope, the uninstall deletes its options and data **(confirm first)**:

  ```bash
  claude plugin uninstall <plugin>@<marketplace> --scope <scope>
  ```

- Read in full: https://code.claude.com/docs/en/plugins/cli-reference#plugin-uninstall

**`"<plugin>" was not uninstalled: it is still switched on in <file>`, or `"<plugin>" was not uninstalled: <file> is there and could not be read`** (`failureCode: "settings_still_on"`)

- Cause: after removing the `enabledPlugins` entry, Claude Code read the scope's settings back, and the file still enables the plugin, couldn't be saved, couldn't be read, or is on a network path. The plugin stays installed and nothing it saved is deleted.
- Fix: follow the last sentence of the message: repair the file it names, or remove the plugin's entry from `enabledPlugins` there, then uninstall again.
- Read in full: https://code.claude.com/docs/en/errors#plugin-was-not-uninstalled

**`Plugin "<plugin>" was not uninstalled: installed_plugins.json holds a record under "<id>" that this version of Claude Code cannot read`**

- Cause: a record in `installed_plugins.json` doesn't parse for this version, most likely because another, perhaps newer, version of Claude Code wrote it. The same text can follow `was not installed:` or `was not updated:`, and `claude plugin list` prints it as a `Note:`.
- Fix, in order:
  1. Update Claude Code, then uninstall again:

     ```bash
     claude update
     ```

  2. If it can't be updated, uninstall the plugin with the version of Claude Code that wrote the record.
  3. If neither helps, delete the record from `installed_plugins.json` by hand **(confirm first)**, then ask the user to restart Claude Code or run `/reload-plugins`.
- Read in full: https://code.claude.com/docs/en/plugins/troubleshooting#installed-plugins-json-holds-a-record-this-version-cannot-read

**Uninstall reports success on Windows, but the plugin is still listed**

- Cause: `installed_plugins.json` held two records for the project folder with different spellings of its path, and one uninstall removes one of them. The remaining row's `projectPath` in `claude plugin list --json` shows the other spelling.
- Fix: run the same uninstall again, from the same folder, with the same `--scope`:

  ```bash
  claude plugin uninstall <plugin>@<marketplace> --scope <scope>
  ```

- The second run removes the other record from 2.1.295. On older versions it fails with `Plugin "<name>" is not installed in project scope`: update Claude Code, then run the uninstall again:

  ```bash
  claude update
  ```

- Read in full: https://code.claude.com/docs/en/plugins/troubleshooting#a-plugin-stays-installed-after-plugin-uninstall-on-windows

**`Disabled in ~/.claude/settings.json but still loads`**

- Cause: a `true` in a higher-precedence source overrides the user setting. The rest of the message names it: `project`, `project, gitignored` (`.claude/settings.local.json`), `cli flag` (`--settings`) or `managed`. When `claude plugin list` instead marks the plugin `required by your org`, no settings file is involved: see `Plugin "<name>@synced" is required by your organization` below.
- Fix: for a project-enabled plugin, set its id to `false` in `.claude/settings.local.json`. For `cli flag`, take the plugin out of the `--settings` value. For `managed`, ask the admin.
- Read in full: https://code.claude.com/docs/en/plugins/troubleshooting#a-plugin-you-disabled-still-loads

**An uninstalled or disabled plugin's skills or hooks still run**

- Cause: the running session loaded them before the change.
- Fix: ask the user to run `/reload-plugins`, or to start a new session.
- Read in full: https://code.claude.com/docs/en/plugins/loading#check-which-stage-a-plugin-reached

**`Removed from the "<marketplace>" marketplace`**

- Cause: the publisher mapped the plugin's name to `null` in `renames`, so Claude Code dropped its key from the user, project and local settings.
- Fix: nothing to repair. Install the replacement the publisher names, if any, and uninstall the old id when its data is no longer needed.
- Read in full: https://code.claude.com/docs/en/plugins/host-marketplace#migrate-users-with-a-renames-map

**`Removed from marketplace` under the Flagged heading in `/plugin`**

- Cause: the publisher removed it from the catalog with `"forceRemoveDeletedPlugins": true`, so a session start uninstalled it from the user, project and local scopes.
- Fix: nothing to repair. Install the replacement the publisher names, if any.
- Read in full: https://code.claude.com/docs/en/plugins/host-marketplace#uninstall-removed-plugins-from-users-machines

**A removed plugin stays installed for users** (publisher view)

- Cause: one of these:
  - the entry was removed without `forceRemoveDeletedPlugins`, so the plugin stays installed and reports `Plugin "<name>" not found in marketplace` when a session loads it;
  - only managed settings installed it, and the removal leaves those in place;
  - no session has started since the user's catalog copy changed: the removal runs at session start, and `claude plugin list` alone didn't trigger it **(observed)**.
- Fix: set `"forceRemoveDeletedPlugins": true` once users no longer need the plugin's data, because that uninstall deletes the data directory **(observed)** **(confirm first)**. For managed installs, the admin follows "Turn off or block" in `references/context-managed-settings.md`.
- Read in full: https://code.claude.com/docs/en/plugins/host-marketplace#uninstall-removed-plugins-from-users-machines

**Auto-installed dependencies remain after uninstall**

- Cause: uninstall leaves auto-installed dependencies until a prune.
- Fix: preview the prune, show the user the list, then remove them **(confirm first)**:

  ```bash
  claude plugin prune --dry-run
  claude plugin prune -y
  ```

- Read in full: https://code.claude.com/docs/en/plugins/cli-reference#plugin-prune

**Old version directories remain in `~/.claude/plugins/cache/`**

- Cause: an update or uninstall writes an `.orphaned_at` marker, and a background cleanup removes the directory 14 days later, only while `installed_plugins.json` records at least one install. A session that loaded the old version keeps running from it meanwhile.
- Fix: wait. Delete the directory by hand only after no session uses it **(confirm first)**.
- Read in full: https://code.claude.com/docs/en/plugins/loading#cleanup-of-previous-versions

**Removing a marketplace uninstalled more than expected**

- Cause: removing a marketplace from the last scope that declares it uninstalls every plugin installed from it and deletes their options, secrets and data where it can. Reinstalling doesn't bring the deleted data back.
- Fix: add the marketplace back, reinstall the plugins the user wants, and set their options again.
- Read in full: https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-remove

## Synced, managed and session-only plugins

**`Plugin "<name>@synced" is required by your organization and can't be disabled here. Contact your admin to change it.`**

- Cause: the claude.ai organization marks the synced plugin as required. Claude Code saves nothing and the plugin stays enabled.
- Fix: an admin of the organization changes the plugin's **Default access**, or its **Group access…**, from **Required** in **Organization settings > Plugins & skills**.
- Read in full: https://code.claude.com/docs/en/errors#plugin-is-required-by-your-organization

**A synced plugin turned off in Claude is still in the terminal**

- Cause: one of the sync rules in the Gotchas of `references/context-claude-account.md`: the change was made during the session and applies at the next start; this session is one where nothing syncs, removals included; or a same-named plugin from another origin is loading instead of the synced copy.
- Fix: restart Claude Code in a session signed in with the claude.ai account. To stop it on this machine now, disable it. If it comes back after a restart, check in **Customize > Plugins** in Claude (https://claude.ai/customize/plugins) that it is really off.

  ```bash
  claude plugin disable <name>@synced
  ```

- Read in full: https://code.claude.com/docs/en/plugins/loading#plugins-synced-from-claudeai

**`Plugins changed. Run /reload-plugins to activate.`**

- Cause: the background account sync added, updated or removed a synced plugin, or a declared marketplace's source changed in settings and Claude Code fetched it again.
- Fix: ask the user to run `/reload-plugins`, or to start a new session.
- Read in full: https://code.claude.com/docs/en/plugins/loading#sync-timing-in-terminal-sessions

**A plugin at Managed scope can't be disabled or uninstalled**

- Cause: the organization installed it through managed settings, and `/plugin` offers no enable, disable or uninstall for it.
- Fix: the admin sets its key to `false` in managed `enabledPlugins` to block it, or removes the key and checks a machine, as "Turn off or block" and "Stop installing it for the fleet" in `references/context-managed-settings.md` describe. What removing the key does to the installed copy isn't documented.
- Read in full: https://code.claude.com/docs/en/plugins/install#manage-installed-plugins

**A `--plugin-dir` copy keeps loading**

- Cause: something passes `--plugin-dir` or `--plugin-url` at launch, or sets `CLAUDE_CODE_PLUGIN_DIRS`.
- Fix: stop passing the flag or setting the variable. When a parent process passes it, set `"<name>@inline": false` under `enabledPlugins` in any settings file; the marketplace or skills-directory copy then loads instead.
- Read in full: https://code.claude.com/docs/en/plugins/loading#keep-a-session-only-plugin-from-loading

## Anthropic's directory

**A pushed release doesn't reach users who installed the plugin from the directory**

- Cause: the new version isn't published, or the directory never sees it. The listing keeps serving the last published version meanwhile.
- When the listing was submitted through the earlier Claude Console form, it gets no new versions until it is moved to the developer portal.
- Otherwise, read the status in the developer portal (claude.ai/directory/manage):
  - **Scanning**: Anthropic is scanning it;
  - **Needs changes**: the newest version didn't pass, or the scanner couldn't fetch or accept it;
  - **In review**: a reviewer holds it;
  - **Approved**: it passed but isn't live; the card says who publishes it;
  - **Published**, with a card about a newer version that is scanning, waiting with a reviewer or not passing;
  - **Not live yet**: the directory team has to list it.
- After a failed security scan, later versions also wait for a reviewer. A listing that follows a tag releases only when the tracked tag changes.
- Fix, by case:
  - Console submission: move it to the developer portal as the publish page describes (**Withdraw** **(confirm first)** and submit again, or write to `directory@anthropic.com`).
  - **Needs changes**, rejected (the submission says the version was not approved and its **Review** tab shows **Resubmit for review**): push the fix **(confirm first)**, then select **Resubmit for review**.
  - **Needs changes**, not rejected: push the fix **(confirm first)**, then select **Check for new commits**.
  - **Approved**, when the card names the user: select **Publish** **(confirm first)**.
  - Tag-tracked listing: on the plugin's **Settings** tab, set **Tracked branch or tag** to the new tag and select **Save**.
  - **Scanning**, **In review** or **Not live yet**: wait for Anthropic.
- Read in full: https://claude.com/docs/directory/submission-status#plugin-bundle-statuses, https://claude.com/docs/plugins/submit#update-a-published-plugin, https://claude.com/docs/plugins/submit#fix-a-failed-version and https://claude.com/docs/directory/publish#move-an-earlier-submission-to-the-developer-portal

**Publishing needs a public repository** (on the plugin's page in the developer portal)

- Cause: the repository is private. The directory scans private repositories, but publishing and relisting need a public one.
- Fix: with the user's approval, make the repository public on GitHub, then select **Check for new commits** on the plugin's page.
- Read in full: https://claude.com/docs/plugins/submit#submit-from-a-private-repository

**GitHub isn’t connected for this Claude organization**, or **The connected GitHub account can’t push to this repository** (in the developer portal)

- Cause: creating, submitting, publishing, relisting and turning on auto-publish check that the GitHub account connected in that Claude organization can push to the repository. A connection made in another organization doesn't count.
- Fix: select **Connect GitHub** in the message, or ask a repository admin to give the account write access, then try again.
- Read in full: https://claude.com/docs/plugins/submit#connect-your-github-account

**Already submitted by another organization** (when selecting **Submit for review**)

- Cause: another organization holds the submission for that repository and folder, or an earlier Claude Console submission does.
- Fix: when the user's organization owns the repository, write to `directory@anthropic.com`. For a Console submission, move it as the publish page describes.
- Read in full: https://claude.com/docs/plugins/submit#submission-limits-and-duplicates

**A new version is blocked or held with Name is taken, Name may be confused with an existing listing, Name matches a known brand or Publisher name may be confused with another** (titles in the validation report)

- Cause: each scan runs the directory's name checks again, so a changed `name`, `displayName` or `author.name` can block or hold a version.
- Fix: keep the published `name`, and change `displayName` or `author.name` to something of the user's own; for a held version, the user can wait for the reviewer.
- Read in full: https://claude.com/docs/plugins/pre-submission-checklist#manifest-and-plugin-name

## claude.ai organizations

**A release doesn't reach members**

- Cause: organization sync reads the default branch only, when an Owner selects **Re-sync** or, with **Sync automatically** on, when someone pushes to the default branch. Tags aren't read, and nothing syncs on a schedule.
- Fix: merge to the default branch, then select **Re-sync** in the marketplace's row menu under **Organization settings > Plugins & skills > Marketplaces** **(confirm first)**. On **You synced recently**, wait the seconds it gives and select **Re-sync** again.
- Read in full: https://claude.com/docs/plugins/org-rollout#update-through-organization-settings

**`Plugin contains a top-level bin/ directory`** (the start of the error)

- Cause: claude.ai rejects a plugin with a top-level `bin/`, by marketplace sync or by upload. On sync, the rest of the marketplace still syncs.
- Fix: move the executables to another folder, such as `scripts/`, reference them through the `CLAUDE_PLUGIN_ROOT` variable, then push and re-sync **(confirm first)**.
- Read in full: https://claude.com/docs/plugins/org-sync#keep-executables-out-of-the-top-level-bin-directory

**A plugin set to Not available still reaches some members**

- Cause: on Enterprise, a group's own **Group access…** setting replaces the organization-wide **Default access** for its members, and a member in several groups gets the most permissive one.
- Fix: set every group that has its own setting for the plugin to **Not available** too **(confirm first)**.
- Read in full: https://claude.com/docs/plugins/admin#limit-to-user-groups-on-enterprise
