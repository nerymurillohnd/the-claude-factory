# A plugin installed on a machine

You act for the user on the computer where Claude Code runs: in the terminal, the desktop app, an IDE, a cloud session or the Agent SDK. You can change what this machine holds: its install records, its catalog copies, its cache and its settings at user, project and local scope, through `claude plugin` in Bash and through the steps you give the user for `/plugin`. You can't change the catalog the plugin comes from, the Claude account or managed settings, and you can't update or uninstall Claude Code's built-in plugins; those belong to the publisher, the account, the admin and Claude Code, and each has its own reference. Load this reference for every id `claude plugin list --json` shows except `<name>@synced`, which `references/context-claude-account.md` covers.

## Contents

- [Gotchas](#gotchas)
- [How the plugin's build and origin change the procedure](#how-the-plugins-build-and-origin-change-the-procedure)
- [Update](#update)
- [Turn auto-update on or off](#turn-auto-update-on-or-off)
- [Turn off](#turn-off)
- [Uninstall](#uninstall)
- [Remove a marketplace](#remove-a-marketplace)
- [Relabel](#relabel)
- [Finish a publisher's rename or merge](#finish-a-publishers-rename-or-merge)
- [Finish a publisher's split](#finish-a-publishers-split)
- [Finish a publisher's retirement](#finish-a-publishers-retirement)
- [Finish a publisher's move](#finish-a-publishers-move)
- [Verify](#verify)

## Gotchas

- `claude plugin marketplace update` refreshes catalogs and leaves every installed plugin at its version (documented without a name, **(observed)** with one), so a user who ran it still has the old plugin. Updating takes `claude plugin update` per plugin, or **Update marketplace** in `/plugin`. The docs also say `/plugin marketplace update <name>` in a session delivers changes; that conflict is the second gotcha of `references/context-own-marketplace.md`, so check it there before relying on either form.
- `claude plugin marketplace remove` uninstalls every plugin installed from that marketplace, with their options, secrets and data, once no scope declares it. Use it only to remove a marketplace, never to refresh one.
- `claude plugin uninstall` from the last scope deletes the plugin's options, secrets and `~/.claude/plugins/data/<id>/` unless `--keep-data` is passed. Turning a plugin off keeps all of it and can be undone, so offer that first.
- `install` and `uninstall` default to `user` scope, while `update`, `enable` and `disable` detect the scope. An uninstall without `--scope` fails for a plugin installed only at project or local scope, so always read the scope from `claude plugin list` and pass it.
- `-y` and `--accept-command` are ignored when Claude runs `claude plugin` through Bash. A plugin whose update shows a command to accept (a `command` source, or an entry with `headersHelper`) is updated by the user in their own terminal; give them the exact command.
- You can't type `/plugin` or `/reload-plugins` from Bash: the user types them in a session. After you change plugins from Bash, ask the user to run `/reload-plugins`, or to start a new session, before you check what the session loaded.
- Some plugins can't be changed from this machine: managed ones, synced ones the organization requires, and built-in plugins. Retrying the command changes nothing; route each to its owner, as [Origins this machine doesn't control](#origins-this-machine-doesnt-control) says.

## How the plugin's build and origin change the procedure

Read the subsections that match your answers to Step 1 of `SKILL.md` (where the plugin lives, its source, its versioning and its dependencies): each one changes a stage of the kinds of change below.

### How Claude Code decides there is an update

Claude Code computes a version for every installed plugin and compares it on each update. When it matches what `installed_plugins.json` records, nothing on disk changes, however many commits the author pushed.

For every source type except `command`, the computed version is the first of these that exists:

1. `version` in the plugin's `plugin.json`;
2. `version` in the plugin's marketplace entry;
3. a value from the source type:
   - `github`, `url`, `git-subdir`: the source's commit SHA, shortened to 12 characters (`git-subdir` also carries a hash of the subdirectory path);
   - `archive`: the SHA-256 digest, shortened to 12 characters;
   - a relative path in a git-hosted marketplace: the commit SHA of the installed directory;
   - a local directory with no git repository, and `npm`: `unknown`.

Three exceptions:

- A relative-path plugin in a marketplace added from a local path loads **in place**: it picks up its current files at every session start or `/reload-plugins`, whatever its version says, and never needs updating.
- A `command` source's version is a hash of what the command produced (`<manifest version>-<hash>` when the manifest sets one). The command re-runs at every install and update, and once per session in the background.
- A plugin from a marketplace hosted on claude.ai (a `claudeai-` name) has the version claude.ai records; the manifest's `version` isn't read.

**Read in full**:

- https://code.claude.com/docs/en/plugins/loading#versions-and-updates
- https://code.claude.com/docs/en/plugins/loading#how-claude-code-computes-the-version
- https://code.claude.com/docs/en/plugins/loading#in-place-and-copied-plugins
- https://code.claude.com/docs/en/plugins/loading#when-a-command-source-re-runs

### Sources that update differently

- **`command` source whose command changed**: when the publisher changes the command, the background run stops and the `/plugin` Errors tab shows the new command and the `claude plugin update` command to run; the user runs it in their own terminal and accepts the new command.
- **Entry with `headersHelper`**: auto-update and **Update marketplace** skip it, and the Errors tab lists it when an update is waiting. The user updates it by itself, from its view in `/plugin` or with `claude plugin update` in their own terminal.
- **Private git marketplace**: Claude Code turns off git's prompts, and background auto-update never prompts, so a credential that needs a prompt makes the update fail quietly and the plugin stays at the last synced state. The user stores a credential git can use without a prompt, then you [update](#update) from stage 2:
  - SSH: a key loaded in `ssh-agent`, and the host already in `known_hosts`;
  - HTTPS on GitHub, in the user's terminal:

    ```bash
    gh auth login
    gh auth setup-git
    ```

  - HTTPS on another host: a personal access token stored in the git credential helper.
- **`engines["claude-code"]` in `plugin.json`** (2.1.323+, **(changelog)**): the plugin isn't installed, updated or loaded outside that Claude Code version range, and install and update pick the newest version that fits. Compare the range with the Claude Code version you found in Step 1 of `SKILL.md`.

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#change-the-command-of-a-command-source
- https://code.claude.com/docs/en/plugins/host-marketplace#installs-and-updates-that-refuse-the-command-instead-of-asking
- https://code.claude.com/docs/en/plugins/host-marketplace#what-background-auto-update-does-with-credentials
- https://code.claude.com/docs/en/plugins/install#add-a-private-marketplace
- https://code.claude.com/docs/en/plugins/troubleshooting#ssh-authentication-failed-or-https-authentication-failed
- https://code.claude.com/docs/en/plugins/cli-reference#accept-a-displayed-install-command

### Plugins with dependencies

- **Install and update**: dependencies install at the same scope. A dependency without a version range moves to each new release on update; a range resolves against `<plugin>--v<version>` tags.
- **Disable**: refused while another enabled plugin needs it; the message prints a chained command that disables both in order.
- **Uninstall**: dependencies that were installed automatically stay until `claude plugin prune` removes them. `prune` never removes a plugin the user installed.

**Read in full**:

- https://code.claude.com/docs/en/plugins/install#plugins-with-dependencies
- https://code.claude.com/docs/en/plugins/cli-reference#plugin-prune

### Origins that change the procedure

- **Session-only (`<name>@inline`)**, from `--plugin-dir`, `--plugin-url`, `CLAUDE_CODE_PLUGIN_DIRS` or the Agent SDK's `plugins` option: it has no install record, so `update` and `uninstall` don't apply. To change it, edit its files and reload. To remove it, stop passing it; when a parent process passes it, set `"<name>@inline": false` in `enabledPlugins` in any settings file, and the marketplace or skills-directory copy of the same name loads instead.
- **Skills-directory (`<name>@skills-dir`)**: a folder with `.claude-plugin/plugin.json` under `~/.claude/skills/` or the project's `.claude/skills/`. Update it by editing the folder. Turn it off with `"<name>@skills-dir": false`, or remove the folder after the user's yes. Managed `strictPluginOnlyCustomization`, `strictKnownMarketplaces` or `blockedMarketplaces` can skip it with no error.
- **Mods**: a mod installs, updates, turns off and uninstalls as its plugin, with the same commands and scopes.
- **Anthropic's marketplaces** (`claude-plugins-official`, `claude-community` and topic marketplaces such as `anthropics/skills`): their plugins change like any marketplace plugin; the auto-update defaults differ, as [Turn auto-update on or off](#turn-auto-update-on-or-off) says. Claude Code adds `claude-plugins-official` the first time an interactive terminal session starts, unless a managed policy or `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL` blocks it, and `claude plugin` commands never add it. When it is missing, follow the troubleshooting entry below.
- **The deprecated `claude-code-plugins` marketplace** (in `anthropics/claude-code`): leave it installed; its plugins update from the official repository. `ralph-wiggum` is now `ralph-loop`, with commands that start with `/ralph-loop:`; if they're missing, install `ralph-loop@claude-plugins-official`. `claude-opus-4-5-migration` is retired: uninstall it. Skip any tutorial step that adds `anthropics/claude-code` as a marketplace.

**Read in full**:

- https://code.claude.com/docs/en/plugins/loading#find-where-a-plugin-came-from
- https://code.claude.com/docs/en/plugins/loading#keep-a-session-only-plugin-from-loading
- https://code.claude.com/docs/en/plugins/loading#skills-directory-plugins-blocked-by-managed-settings
- https://code.claude.com/docs/en/plugins/mods/overview#install-or-update-a-mod
- https://code.claude.com/docs/en/plugins/mods/overview#turn-mods-on-or-off
- https://code.claude.com/docs/en/plugins/anthropic-marketplaces#anthropics-marketplaces
- https://code.claude.com/docs/en/plugins/anthropic-marketplaces#deprecated-claude-code-plugins-marketplace
- https://code.claude.com/docs/en/plugins/troubleshooting#marketplace-claude-plugins-official-not-found

### Origins this machine doesn't control

- **Managed scope** (`"scope": "managed"`): the user can't turn it off or uninstall it, and only the admin can change it, as the Gotchas of `references/context-managed-settings.md` say. `claude plugin update --scope managed` still updates it on this machine.
- **Synced and required by the organization**: only the organization's admin can change it, as the Gotchas of `references/context-claude-account.md` say.
- **Built-in** (listed under **Built-in** in `/plugin` > Installed): can't be updated or uninstalled. The user can turn most of them off in `/plugin`; `cc-plugin-sec-default` only an admin can change.

**Read in full**:

- https://code.claude.com/docs/en/plugins/install#manage-installed-plugins
- https://code.claude.com/docs/en/plugins/loading#control-which-synced-plugins-load
- https://code.claude.com/docs/en/plugins/mods/overview#mods-built-into-claude-code

### Where Claude Code runs

In Claude (chat and Cowork, now one experience), plugins come from the account, as "How the build changes the procedure" in `references/context-claude-account.md` explains. In Claude Code, the place it runs decides which tools act on the machine. The terminal, the desktop app's local sessions and the VS Code extension read the same settings files on one computer, so a change at user scope in one of them applies to all three.

- **Terminal**: `claude plugin` from the shell, or `/plugin` in a session. In `claude -p`, `/plugin` doesn't run; `/reload-plugins` does (2.1.260+) when typed in the prompt, but it doesn't connect or disconnect plugin MCP servers there.
- **Desktop app, Code tab** (local or SSH session): **+** > **Plugins** > **Manage plugins** enables, disables or uninstalls. Plugins aren't available in WSL sessions, and plugins installed from the desktop app don't reach cloud sessions.
- **VS Code extension**: `/plugins` opens **Manage plugins**. A row's toggle turns it off and its trash icon uninstalls that row's scope; a dimmed icon marks a row this workspace can't uninstall. For a plugin the project's `.claude/settings.json` turns on, both ask first: the toggle offers **Disable for me** or **Disable for everyone**, which changes the shared file, and the trash icon offers **Disable for me** or **Uninstall for everyone**, which removes the project install with `--keep-data`. For the last install of a plugin with saved data, it asks whether to keep the data (**Keep** is the default). On the **Marketplaces** tab, the refresh icon updates a catalog and the trash icon removes a marketplace and its plugins.
- **JetBrains**: Claude Code runs in the IDE's terminal, so use the terminal's steps. The IDE plugin's **Enable automatic updates** setting updates the JetBrains plugin, not Claude Code plugins.
- **Cloud session** (Claude Code on the web): no `/plugin`, and neither user-scope plugins nor the plugins the repository's `.claude/settings.json` turns on load there. A plugin added from a suggestion card in the session is turned on for the claude.ai account; remove it there.
- **Agent SDK**: plugins load from the paths the app passes; update by changing the files. Apply a change in a running session with `reloadPlugins()` on the TypeScript `Query` object, or by sending `/reload-plugins` as a prompt from Python.

**Read in full**:

- https://code.claude.com/docs/en/plugins/install#choose-an-install-scope
- https://code.claude.com/docs/en/plugins/install#jetbrains-non-interactive-runs-and-the-agent-sdk
- https://code.claude.com/docs/en/plugins/cli-reference#sessions-without-an-interactive-terminal
- https://code.claude.com/docs/en/desktop#install-plugins
- https://code.claude.com/docs/en/vs-code#manage-plugins
- https://code.claude.com/docs/en/claude-code-on-the-web#plugin-suggestions-in-the-conversation
- https://code.claude.com/docs/en/agent-sdk/plugins#reload-plugins-in-a-running-session

## Update

**When**: the publisher released a version the user doesn't have yet. For a plugin that loads in place, nothing needs updating (see [How Claude Code decides there is an update](#how-claude-code-decides-there-is-an-update)); for a session-only or skills-directory plugin, [Origins that change the procedure](#origins-that-change-the-procedure).

**Stages**:

1. **Read the plugin's id, every scope it is installed at and its version.** Done when: you have the `id`, `scope` and `version` of each entry for the plugin.

   ```bash
   claude plugin list --json
   ```

2. **Refresh the catalog.** What `claude plugin update` prints when it can't reach the marketplace isn't documented, so prove the catalog is current before you trust its verdict. Done when: it prints `Successfully updated marketplace: <marketplace>`. Any other output, such as `Failed to clone marketplace repository:` followed by `SSH authentication failed` or `HTTPS authentication failed`, goes to `references/diagnose-changes.md` before stage 3; for a private git marketplace, see [Sources that update differently](#sources-that-update-differently).

   ```bash
   claude plugin marketplace update <marketplace>
   ```

3. **Update it at each scope.** Done when: each run prints that the plugin was updated, or `<name> is already at the latest version (<version>).`. After stage 2 succeeded, that line means the computed version didn't change: the publisher hasn't released one, and retrying changes nothing.

   ```bash
   claude plugin update <plugin>@<marketplace> --scope <scope>
   ```

   - Without `--scope`, it updates the most specific scope the plugin is installed at for the current project (2.1.281+); before that it used `user` and failed with `Plugin "<name>" is not installed at scope user`.
   - A bare name works (2.1.246+) when only one marketplace has a plugin of that name.
   - When the run shows a command to accept, stop and give the user the same command to run in their own terminal (see the gotchas).
   - When it stays on an old version and the plugin declares `engines`, check the range, as [Sources that update differently](#sources-that-update-differently) says.
   - To update every plugin from one marketplace at once, the user selects `/plugin` > **Marketplaces** > the marketplace > **Update marketplace**, the only one-step way. It reports any plugin it left, which you then update one by one.

4. **Load the new version.** Ask the user to run `/reload-plugins` in each open session, or to start a new one. Done when: the reload summary reports no `errors during load`, and the list shows the new version at every scope.

   ```bash
   claude plugin list --json
   ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/install#update-plugins-now
- https://code.claude.com/docs/en/plugins/cli-reference#plugin-update
- https://code.claude.com/docs/en/plugins/cli-reference#reload-plugins

## Turn auto-update on or off

**When**: the user wants a marketplace's plugins to update on their own, or to stop updating on their own.

How auto-update runs: in an interactive session, after the first message, Claude Code waits a random delay of up to ten minutes, refreshes every marketplace with auto-update on and updates its plugins on disk. The running session keeps what it loaded and shows `Plugin updated: <name> · Run /reload-plugins to apply`; the next launch loads the new version. After a copied plugin updates mid-session, `/reload-plugins` switches hooks, MCP and LSP servers to the new path, and monitors need a restart.

Whether a marketplace auto-updates is the first of these that is set:

1. `autoUpdate` on its `extraKnownMarketplaces` entry in a settings file;
2. `autoUpdate` in `known_marketplaces.json`, which the **Enable auto-update** toggle in `/plugin` > **Marketplaces** writes (and also writes to the settings entry when one declares the marketplace);
3. the default: on for `claude-plugins-official` and Anthropic's other official marketplaces except `knowledge-work-plugins` and `first-party-plugins`, and for marketplaces added from claude.ai; off for every other marketplace, including `claude-community`, third-party and local ones.

`DISABLE_UPDATES=1`, `DISABLE_AUTOUPDATER=1` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` turns the whole pass off and hides the toggle, unless `FORCE_AUTOUPDATE_PLUGINS=1` is also set.

**Stages**:

1. **Find who decides.** A managed entry that sets `autoUpdate` wins over the user's choice; route that to the admin, as "Choose the fleet's update policy" in `references/context-managed-settings.md` says. Done when: you know which settings file, if any, sets it, from this search; a managed entry shows itself when the toggle is refused.

   ```bash
   grep -s -n '"autoUpdate"' ~/.claude/settings.json .claude/settings.json .claude/settings.local.json ~/.claude/plugins/known_marketplaces.json
   ```

2. **Set it.** The user selects `/plugin` > **Marketplaces** > the marketplace > **Enable auto-update** or **Disable auto-update**. Done when: the settings entry that declares the marketplace, or `known_marketplaces.json` when none does, shows the new `autoUpdate`; run the same `grep` again.

**Read in full**:

- https://code.claude.com/docs/en/plugins/loading#when-auto-update-runs
- https://code.claude.com/docs/en/plugins/loading#which-marketplaces-and-plugins-auto-update
- https://code.claude.com/docs/en/plugins/install#keep-plugins-updated

## Turn off

**When**: the user wants the plugin out of their sessions and may want it back. It stays installed with its options and data. A plugin's skill goes away only with its plugin. When the user asks which plugins to turn off, `/plugin` > Installed shows a **Not used recently** header and a **Last used** line per plugin, and the `Always-on` line of the details shows the tokens a plugin adds to every session:

```bash
claude plugin details <name>
```

**Stages**:

1. **Read the scope the plugin is set at**, as in [Update](#update), stage 1. Done when: you have its `scope`.
2. **Turn it off.** Without `--scope`, `disable` acts on the most specific scope whose settings list the plugin. For a plugin the project's `.claude/settings.json` turns on, pass `--scope local` to turn it off for the user alone, which leaves the shared file unchanged. Done when: the command prints `Successfully disabled plugin: <name> (scope: <scope>)`, or `is already disabled`.

   ```bash
   claude plugin disable <plugin>@<marketplace> --scope <scope>
   ```

   - When another enabled plugin depends on it, the command refuses and prints a chained command that disables both in order; show it to the user before running it.
   - `--all` in place of a name turns off every enabled plugin; use it only when the user asks for exactly that.

3. **Apply it.** Ask the user to run `/reload-plugins`, or to start a new session. Done when: the plugin's entry shows `"enabled": false`.

   ```bash
   claude plugin list --json
   ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/install#manage-installed-plugins
- https://code.claude.com/docs/en/plugins/cli-reference#plugin-disable
- https://code.claude.com/docs/en/plugins/loading#find-where-a-plugin-is-enabled

## Uninstall

**When**: the user wants the plugin gone from this machine, or from one scope. Ask first whether they need its options or data, because an uninstall from the last scope deletes them.

**Stages**:

1. **Read every scope it is installed at and the size of its data.** Its data directory is `~/.claude/plugins/data/<id>/`, where `<id>` is the plugin's id with every character other than a letter, digit, `_` or `-` replaced by `-`. Done when: you have each scope and the `dataDirSize` (absent when there is no data).

   ```bash
   claude plugin list --json --data-size <plugin>@<marketplace>
   ```

2. **Save what the user wants to keep**: copy the data directory elsewhere, or plan `--keep-data`. Done when: the user confirmed what to keep, and the copy, if any, lists the files.

   ```bash
   ls -la <copy-path>
   ```

3. **Uninstall at each scope**, with the user's yes before the last one. Uninstalling at `project` scope changes the shared `.claude/settings.json`; to stop it for the user alone, [turn it off](#turn-off) at `local` scope instead, and commit a shared change only with the user's yes. Done when: each run prints `Successfully uninstalled plugin: <name> (scope: <scope>)`.

   ```bash
   claude plugin uninstall <plugin>@<marketplace> --scope <scope>
   ```

   - Add `--keep-data` to keep the data directory.
   - In `/plugin`, **Uninstall** on a plugin the project's `.claude/settings.json` turns on asks first: **Disable for me** (`y`) writes `false` in the user's `.claude/settings.local.json`, and **Uninstall for everyone** (`u`) removes it from the shared file.
   - When it fails, nothing was deleted. Look the message up under "Removals and uninstalls" in `references/diagnose-changes.md`.

4. **Remove the dependencies it installed**, with the user's yes. Done when: a dry run prints a line that starts `Nothing to prune`.

   ```bash
   claude plugin prune --dry-run
   ```

   When it lists dependencies and the user agrees, remove them:

   ```bash
   claude plugin prune -y
   ```

5. **Apply it.** Ask the user to run `/reload-plugins`, or to start a new session. Done when: the list has no entry for the plugin at the scopes you uninstalled.

   ```bash
   claude plugin list --json
   ```

What an uninstall from the last scope keeps:

- the data directory, with `--keep-data`, or when another installed plugin uses the same folder (an id that differs only in letter case);
- the options, secrets and data, when Claude Code can't read the install list back after the removal; the uninstall still succeeds and the message says how to delete them (`savedKept: "install_records_unreadable"` with `--json`);
- the cached files under `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, which get an `.orphaned_at` marker and are deleted by a background sweep 14 days later, so running sessions keep working. The sweep runs only while at least one install is recorded.

For a plugin the user no longer trusts, also delete its cache directory now and check that its data directory is gone, both after the user's yes, and remove its marketplace when the user doesn't trust the owner either.

**Read in full**:

- https://code.claude.com/docs/en/plugins/cli-reference#plugin-uninstall
- https://code.claude.com/docs/en/plugins/cli-reference#what-an-uninstall-deletes-and-keeps
- https://code.claude.com/docs/en/plugins/install#uninstall-a-plugin-the-project-enables
- https://code.claude.com/docs/en/plugins/loading#cleanup-of-previous-versions
- https://code.claude.com/docs/en/plugins/security#remove-a-plugin-you-no-longer-trust
- https://code.claude.com/docs/en/errors#plugin-was-not-uninstalled

## Remove a marketplace

**When**: the user wants a marketplace and every plugin from it gone from this machine. To refresh a catalog, use [Update](#update) instead.

**Stages**:

1. **Read the marketplace's name**, which is the name the list shows, not the source it was added from. Done when: you have the `name`.

   ```bash
   claude plugin marketplace list --json
   ```

2. **List the plugins it will uninstall**: every entry whose `id` ends in `@<name>`, with the size of its data. Show them to the user and get a yes that covers each one, and save any data they want first, as in [Uninstall](#uninstall), stage 2. Done when: the user approved the list.

   ```bash
   claude plugin list --json --data-size
   ```

3. **Remove it.** Without `--scope`, the declaration goes from every scope, and once no scope declares it Claude Code deletes its cache and uninstalls its plugins with their options, secrets and data where it can. Done when: it prints `Successfully removed marketplace: <name>`, and lists any plugins under `Also uninstalled N plugins from this marketplace:`.

   ```bash
   claude plugin marketplace remove <name>
   ```

4. **Apply it**, as in [Uninstall](#uninstall), stage 5. Done when: neither list shows the marketplace or an `@<name>` plugin.

   ```bash
   claude plugin marketplace list
   claude plugin list
   ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-remove
- https://code.claude.com/docs/en/plugins/install#manage-marketplaces

## Relabel

A new `displayName` arrives with the plugin's next update and changes nothing else on the machine: follow [Update](#update).

## Finish a publisher's rename or merge

**When**: the publisher's notes or `claude plugin list` say the plugin was renamed or merged into another (`Renamed to "<new>" in the "<marketplace>" marketplace`, or `not found in marketplace` for a plugin that used to work). Read the publisher's notes first: they name the new plugin and what to move.

What the docs say happens once the catalog refreshes and a session loads the old name: the plugin loads under its new name, the notice shows once, and Claude Code rewrites the old key to the new one in `enabledPlugins` and `pluginConfigs` at user, project and local scope. In a merge, several old names map to the same new one.

**Stages**:

1. **Refresh the catalog.** Third-party marketplaces don't auto-update by default, so the rename doesn't arrive until the catalog is refreshed. Done when: it prints `Successfully updated marketplace: <marketplace>`.

   ```bash
   claude plugin marketplace update <marketplace>
   ```

2. **Load the new name.** Ask the user to start a new session, or to run `/reload-plugins`, so a session loads the refreshed catalog.
   - For a git or URL marketplace, the new name reports `Plugin "<new>" not cached at <path>` until it is installed once. Install it at the scope the old one had:

     ```bash
     claude plugin install <new>@<marketplace> --scope <scope>
     ```

   - An install set to `false` keeps its old id **(observed)**. When the user wants the new plugin, [uninstall](#uninstall) the old id and install the new one as above.

   Done when: the list shows `<new>@<marketplace>` at the old scope, with no old id left unless the user chose to keep it.

   ```bash
   claude plugin list --json
   ```

3. **Check the options.** In a merge, only one `pluginConfigs` entry survives **(observed)**. For each option this lists as `not set`, ask the user to run `/plugin configure <new>@<marketplace>` in a session, which opens the options dialog and keeps secrets out of your context. Done when: every option the user needs shows `set`.

   ```bash
   claude plugin configure <new>@<marketplace>
   ```

4. **Move the data.** The data directory is named after the id, and the migration leaves the old one under `~/.claude/plugins/data/<old-id>/` **(observed)**, so the new plugin starts without it. Copy what the publisher's notes name. Done when: those files exist in the new directory, and the user decided whether to delete the old one.

   ```bash
   ls -la ~/.claude/plugins/data/<new-id>/
   ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#migrate-users-with-a-renames-map
- https://code.claude.com/docs/en/plugins/troubleshooting#plugin-not-cached-at
- https://code.claude.com/docs/en/plugins/troubleshooting#plugin-not-found-in-marketplace
- https://code.claude.com/docs/en/plugins/cli-reference#plugin-configure
- https://code.claude.com/docs/en/plugins/loading#enabled-in-project-settings-but-not-installed, for a renamed plugin the project's `.claude/settings.json` enables
- https://code.claude.com/docs/en/plugins/troubleshooting#plugin-is-enabled-in-project-settings-but-isnt-installed-here

## Finish a publisher's split

**When**: the publisher split the plugin into several, and the notes name the new parts.

**Stages**:

1. **Get the new parts.** When the original now depends on them, updating it installs them: follow [Update](#update), and the reload installs the dependencies it added. Otherwise install each new part the user wants, at the original's scope. Done when: the list shows each new part at that scope.

   ```bash
   claude plugin install <part>@<marketplace> --scope <scope>
   claude plugin list --json
   ```

2. **Set each part's options and move its data**, as in [Finish a publisher's rename or merge](#finish-a-publishers-rename-or-merge), stages 3 and 4. Done when: each part passes those two checks.
3. **Remove what the user no longer wants**: the original, when the notes retire it, through [Uninstall](#uninstall). Done when: the list shows exactly the plugins the user chose.

   ```bash
   claude plugin list --json
   ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/dependencies#bundle-plugins-for-a-team
- https://code.claude.com/docs/en/plugins/install#plugins-with-dependencies

## Finish a publisher's retirement

**When**: the publisher retired the plugin, and the notes give the date and what to save.

What happens on the machine depends on the catalog:

- with `"<name>": null` in `renames`: once the catalog refreshes, the old key is dropped from user, project and local scope, and the user sees `Removed from the "<marketplace>" marketplace`;
- with the entry removed and no `renames` entry: the plugin stays installed and reports `Plugin "<name>" not found in marketplace` when a session loads it;
- with `"forceRemoveDeletedPlugins": true`: each session start uninstalls it from user, project and local scope and lists it under **Flagged** in `/plugin` with `Removed from marketplace`. The removal deletes the data directory **(observed)**, so save the data before the next session start.

**Stages**:

1. **Save what the user needs** from `~/.claude/plugins/data/<id>/` before refreshing the catalog or starting a session. Done when: the copy lists the files, or the user said nothing needs saving.

   ```bash
   ls -la <copy-path>
   ```

2. **Install the replacement** the notes name, if the user wants it, as in [Finish a publisher's split](#finish-a-publishers-split), stage 1. Done when: the list shows it at the old plugin's scope.
3. **Uninstall the retired plugin** at each scope where it is still listed, through [Uninstall](#uninstall). Done when: the list has no entry for it.

   ```bash
   claude plugin list --json
   ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#migrate-users-with-a-renames-map
- https://code.claude.com/docs/en/plugins/host-marketplace#uninstall-removed-plugins-from-users-machines

## Finish a publisher's move

**When**: the plugin moved to another marketplace, or the marketplace moved to another host or source.

- **The marketplace keeps its name and changes source**: plugin ids, options and data don't change, so re-point the registration. Never remove and re-add it, because removal uninstalls its plugins with their data. Adding the new source alone is refused while the user's `extraKnownMarketplaces` entry lists the old one, with `Cannot add marketplace "<name>": its source doesn't match its extraKnownMarketplaces entry in user or managed settings`. When managed settings declare it, the admin changes it (`references/context-managed-settings.md`). Otherwise:
  1. Change the `source` of the marketplace's `extraKnownMarketplaces` entry in the settings file that declares it (`~/.claude/settings.json` for a marketplace the user added), with the user's yes when that file is the shared `.claude/settings.json`. Write the new source as the add command records it: `owner/repo` is `{"source": "github", "repo": "<owner>/<repo>"}`, and an `https://` clone URL is `{"source": "git", "url": "<url>"}`, even on GitHub. Done when: the entry shows the new source.

     ```bash
     grep -n -A4 '"<name>"' ~/.claude/settings.json
     ```

  2. Fetch it from the new source: add it again now, or ask the user to start a new session, after which Claude Code re-fetches it and shows `Plugins changed. Run /reload-plugins to activate.` Done when: the add prints `Successfully added marketplace: <name>` (or the new session showed that notice), the list shows the new source, and the plugins are still installed.

     ```bash
     claude plugin marketplace add <new-source>
     claude plugin marketplace list --json
     claude plugin list --json
     ```

  For a marketplace added from a local path, the add alone re-points it without the edit, printing `Marketplace '<name>' was already added from <old> and now points at <new>.` **(observed)**.

- **The plugin moved to another marketplace, or the marketplace changed its name**: the id changes, so treat it as a new plugin. Two enabled plugins with the same manifest name from different marketplaces both show as enabled but only one runs its hooks, so turn the old one off before installing the new one.

**Stages** for a new id:

1. **Add the new marketplace** from the source the notes give, unless the list already shows it. Done when: it prints `Successfully added marketplace: <new>`.

   ```bash
   claude plugin marketplace add <source>
   ```

2. **Turn off the old id**, through [Turn off](#turn-off). Done when: that section's stage 3 check passes for the old id.
3. **Install the new id** at the old one's scope. Done when: the list shows `<plugin>@<new>` enabled at that scope.

   ```bash
   claude plugin install <plugin>@<new> --scope <scope>
   claude plugin list --json
   ```

4. **Set its options and move its data**, as in [Finish a publisher's rename or merge](#finish-a-publishers-rename-or-merge), stages 3 and 4. Done when: it passes those two checks.
5. **Remove the old id**, through [Uninstall](#uninstall), and the old marketplace when nothing else installed comes from it, through [Remove a marketplace](#remove-a-marketplace). Done when: neither list shows the old id, nor the old marketplace if the user removed it.

   ```bash
   claude plugin list
   claude plugin marketplace list
   ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/loading#plugins-and-marketplaces-that-arent-on-disk-at-session-start
- https://code.claude.com/docs/en/plugins/troubleshooting#cannot-add-marketplace-source-doesnt-match
- https://code.claude.com/docs/en/plugins/loading#hooks-when-two-enabled-plugins-share-a-name
- https://code.claude.com/docs/en/plugins/install#add-a-marketplace

## Verify

1. After the user ran `/reload-plugins` or started a new session, show the raw output of both lists. Done when: each plugin the change touched shows the expected id, scope, version and `enabled` value, or is absent, and no entry the change touched carries `errors`.

   ```bash
   claude plugin list --json
   claude plugin marketplace list
   ```

2. Ask the user to open `/plugin` > **Errors**. Done when: it has no entry for the plugins the change touched, or each one left is explained in the report.
3. On each other surface the user runs on this computer (desktop app, VS Code), the plugin shows the same state, because they read the same settings files.
