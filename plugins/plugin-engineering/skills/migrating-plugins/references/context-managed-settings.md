# A plugin or marketplace that managed settings deliver

You act for the admin who deploys managed settings to a fleet: server-managed settings from the claude.ai admin console, an MDM profile or registry policy, a `managed-settings.json` file, or a Claude apps gateway policy. Managed `extraKnownMarketplaces` registers a marketplace on every machine that receives the settings, and managed `enabledPlugins` force-enables or blocks plugins there; both win over every other scope. You edit the managed settings only when the user is the admin. Otherwise write the exact settings change to send the admin, and mark the stage as waiting on them. Delivering changed managed settings reaches every machine, so it is in "Stop and confirm" in SKILL.md: show the exact change and wait for the user's yes. The marketplace itself is the publisher's: when the user maintains it, load `references/context-own-marketplace.md` as well.

## Contents

- [Gotchas](#gotchas)
- [How the delivery and the build change the procedure](#how-the-delivery-and-the-build-change-the-procedure)
- [Choose the fleet's update policy](#choose-the-fleets-update-policy)
- [Update](#update)
- [Turn off or block](#turn-off-or-block)
- [Stop installing it for the fleet](#stop-installing-it-for-the-fleet)
- [Retire a managed marketplace](#retire-a-managed-marketplace)
- [Relabel](#relabel)
- [Rename or merge](#rename-or-merge)
- [Split](#split)
- [Move to another marketplace](#move-to-another-marketplace)
- [Verify](#verify)

## Gotchas

- By default only one managed source applies on a machine: server-managed settings first, then MDM, then the managed settings file. If server-managed settings deliver even one unrelated policy key, the plugin keys in an MDM policy or a managed settings file on that machine are ignored, unless `managedSourcesBehavior` is `"merge"`. Edit the source that applies, or the change never lands.
- A `managed-settings.json` that isn't valid JSON stops Claude Code from starting on every machine that reads it. Validate the file before you deploy it.
- The plugin keys apply at session start. A change reaches a machine at its next session, and a running session keeps what it loaded.
- A plugin set to `true` in managed `enabledPlugins` loads whatever users set at their own scopes, and `/plugin` shows it at **Managed** scope with no enable, disable or uninstall. A plugin set to `false` there is blocked at every scope and hidden from its marketplace's catalog.
- Every plugin key applies to everyone who receives the settings. Per-group policy needs a separate delivery per group, and neither a server-managed group configuration nor a gateway policy merges with another one: each holds every setting and every marketplace its group needs.
- Claude Code can't rewrite managed settings. After a publisher's rename, the plugin loads under its new name, but the rename notice repeats on every machine until the admin changes the key.
- `forceRemoveDeletedPlugins` never uninstalls a plugin that only managed settings installed. Removing it from the fleet is the admin's stage.
- A managed `extraKnownMarketplaces` entry replaces a same-name entry from any other scope whole. From 2.1.321, when users had added that name from another source, their entry is hidden, the plugins the declared marketplace lists are reinstalled from it, their saved data is set aside for `cleanupPeriodDays`, and their options and secrets until `claude plugin restore-set-aside` brings them back **(changelog)**. Before declaring a name users already have, tell them, because the take-over reaches them at their next session.
- While `strictKnownMarketplaces` is set, a marketplace whose source isn't on it can't install or update plugins, and its installed plugins don't load. A marketplace the admin adds must be on the allowlist first.
- In an Anthropic-hosted cloud session, only server-managed settings reach the session; MDM policies and files stay on the user's machine. In `-p` and CI runs, plugins install in the background, so a plugin can be missing from the first turn unless `CLAUDE_CODE_SYNC_PLUGIN_INSTALL=1` is set.
- What members get in Claude, and what reaches Claude Code as `@synced`, comes from **Organization settings > Plugins & skills** on claude.ai, not from these keys. For that, load `references/context-organization.md`.

## How the delivery and the build change the procedure

- **Finding the source that applies**: on a machine that receives the settings, the `Setting sources` line of `/status` names it: `(remote)` for server-managed or a gateway, `(plist)` or `(HKLM)` for MDM, `(file)` or `(drop-ins)` for the file.
- **Managed settings file**: `managed-settings.json` and the drop-in folder `managed-settings.d/` live in `/Library/Application Support/ClaudeCode/` on macOS, `/etc/claude-code/` on Linux and WSL, and `C:\Program Files\ClaudeCode\` on Windows. Drop-ins merge after the main file in alphabetical order, and a later `extraKnownMarketplaces` entry with the same name replaces the earlier one whole, so edit the file that holds the entry.
- **Checking the delivered settings**: the stages read a managed settings file with `python3 -m json.tool`, which also fails on invalid JSON; the Linux path is shown, use the platform's. For server-managed settings, the admin reads the JSON at **Organization settings > Claude Code > Managed settings**; for MDM, the deployed profile or registry value.
- **A private git marketplace**: each user clones it with the git credentials stored on their machine. Users without access get nothing; a seed reaches them instead.
- **A seed (`CLAUDE_CODE_PLUGIN_SEED_DIR`)** for containers and CI: Claude Code never writes to it and forces `autoUpdate` off, and `claude plugin marketplace update` fails on it. Every change ships by rebuilding the seed into the image with `CLAUDE_CODE_PLUGIN_CACHE_DIR`, and the plugins in it still need `enabledPlugins` keys, in managed settings or the repository's `.claude/settings.json`.
- **A plugin from `claude-plugins-official`**: a managed `"<name>@claude-plugins-official": true` registers the marketplace by itself, and that marketplace auto-updates by default.
- **A `command` source**: Claude Code re-runs the command every session whatever the update policy, and `disableCommandPluginSources` blocks such plugins from installing, updating or loading. A changed command waits for each user to accept it; `references/context-own-marketplace.md` (How the build changes the procedure) covers it.
- **An entry with a `headersHelper`**: background auto-update skips it and lists it in the `/plugin` **Errors** tab, so each user updates that plugin by itself.

**Read in full**:

- https://code.claude.com/docs/en/plugins/org#which-managed-source-applies-on-a-machine
- https://code.claude.com/docs/en/plugins/org#troubleshoot-policy
- https://code.claude.com/docs/en/plugins/org#seed-containers-and-ci
- https://code.claude.com/docs/en/plugins/loading#when-a-command-source-re-runs
- https://code.claude.com/docs/en/plugins/host-marketplace#installs-and-updates-that-refuse-the-command-instead-of-asking

## Choose the fleet's update policy

Choose this once per marketplace, before the first release that must reach the fleet. The Update stages depend on it.

- **Per marketplace**: `"autoUpdate": true` on the managed `extraKnownMarketplaces` entry turns background updates on for everyone who receives it, and `false` turns them off. When the managed entry sets the field, a user's toggle in `/plugin` is refused with `Auto-update for '<name>' is set by`; when it leaves the field unset, each user's own toggle decides. With neither set, a third-party marketplace stays off, and its users get a release only when they update it themselves.
- **Whole fleet off**: `"env": {"DISABLE_AUTOUPDATER": "1"}` in managed settings turns plugin auto-update off for every marketplace and also stops Claude Code's own background updates. Add `"FORCE_AUTOUPDATE_PLUGINS": "1"` to the same block to keep plugin auto-update. Neither stops `command` sources.
- **Shipping Claude Code versions yourself**: `DISABLE_AUTOUPDATER` still lets users run `claude update` and `claude install`; `"DISABLE_UPDATES": "1"` blocks every Claude Code update path, and also turns plugin auto-update off unless `FORCE_AUTOUPDATE_PLUGINS` is set. Whether `DISABLE_UPDATES` also blocks a manual plugin update isn't documented: test it on one machine before relying on either outcome.
- **Release channels per group**: the publisher hosts one marketplace per channel (`references/context-own-marketplace.md`, Hold users on a version, and release channels). Each group then receives its own channel's managed `extraKnownMarketplaces` entry, through separate endpoint-managed settings, one gateway policy per group, or on Enterprise one server-managed configuration per group.

**Read in full**:

- https://code.claude.com/docs/en/plugins/org#set-update-policy
- https://code.claude.com/docs/en/plugins/loading#which-marketplaces-and-plugins-auto-update
- https://code.claude.com/docs/en/setup#disable-auto-updates
- https://code.claude.com/docs/en/env-vars
- https://code.claude.com/docs/en/plugins/host-marketplace#run-release-channels

## Update

**When**: the publisher released a version and the fleet should get it.

**Stages**:

1. **Set the update policy** the fleet should follow, from [Choose the fleet's update policy](#choose-the-fleets-update-policy).
   - Done when: the delivered managed settings carry the chosen policy:

     ```bash
     python3 -m json.tool /etc/claude-code/managed-settings.json
     ```

2. **The publisher releases**: a new computed version in the marketplace (`references/context-own-marketplace.md`, Update: release a new version). For a seeded fleet, rebuild the seed with the new version.
   - Done when: the publisher's release check passes, or the new image's seed holds the new version.
3. **The fleet picks it up**. With auto-update on, an interactive session refreshes the marketplace after its first message and a random delay of up to ten minutes; the new version loads at the next launch or after `/reload-plugins`. With it off, each user updates.
   - Done when: on a sample machine, after a new session, the plugin shows `"scope": "managed"` and the new `version`:

     ```bash
     claude plugin list --json
     ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/org#require-a-marketplace-and-its-plugins
- https://code.claude.com/docs/en/plugins/loading#when-auto-update-runs
- https://claude.com/docs/plugins/org-rollout#update-through-managed-settings

## Turn off or block

**When**: no machine that receives the settings may load the plugin, whatever users install. This also covers a plugin the publisher retired that some users installed themselves.

**Stages**:

1. **Block it**: set `"<plugin>@<marketplace>": false` in managed `enabledPlugins`. Users can't install it at any scope, and it disappears from the catalog in `/plugin`.
   - Done when: the delivered managed settings map the key to `false`:

     ```bash
     python3 -m json.tool /etc/claude-code/managed-settings.json
     ```

2. **Confirm on a sample machine** after a new session.
   - Done when: the plugin's entry shows `"enabled": false`, or it is absent:

     ```bash
     claude plugin list --json
     ```

To block a whole marketplace instead of one plugin, add its source to managed `blockedMarketplaces`: its installed plugins stop loading at session start and `/plugin` shows `Marketplace "<name>" is blocked by enterprise policy`.

**Read in full**:

- https://code.claude.com/docs/en/plugins/org#control-matrix
- https://code.claude.com/docs/en/plugins/org#blocklist-with-blockedmarketplaces
- https://code.claude.com/docs/en/settings-reference#enabledplugins

## Stop installing it for the fleet

**When**: the fleet should stop receiving the plugin, and users may still install it themselves.

**Stages**:

1. **Remove its key** from managed `enabledPlugins`.
   - Done when: no delivered managed settings name the key:

     ```bash
     python3 -m json.tool /etc/claude-code/managed-settings.json
     ```

2. **Check a sample machine** after a new session, and report what it shows.
   - What happens to the copy managed settings installed, once its key is gone, isn't documented. With no key at any scope, an installed plugin follows its `defaultEnabled`.
   - If the plugin must not load anywhere, use [Turn off or block](#turn-off-or-block) instead.
   - Done when: the output shows what happened to the plugin, and you reported it to the user:

     ```bash
     claude plugin list --json
     ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/org#require-a-marketplace-and-its-plugins
- https://code.claude.com/docs/en/settings-reference#enabledplugins

## Retire a managed marketplace

**When**: the fleet no longer uses a marketplace, usually after its publisher retired its plugins.

**Stages**:

1. **Handle each plugin first**: [Stop installing it for the fleet](#stop-installing-it-for-the-fleet), or [Turn off or block](#turn-off-or-block) when it must not load anywhere.
   - Done when: each of its plugins' stages passed.
2. **Remove the marketplace's managed `extraKnownMarketplaces` entry**, after checking that no other managed `enabledPlugins` key still names it.
   - Done when: no delivered managed settings name the marketplace:

     ```bash
     python3 -m json.tool /etc/claude-code/managed-settings.json
     ```

3. **Check a sample machine** after a new session, and report what it shows.
   - Whether machines unregister a marketplace whose managed entry is gone isn't documented.
   - If it must stop serving plugins everywhere, add its source to managed `blockedMarketplaces`.
   - Done when: the marketplace is absent or blocked, or you reported to the user that it stays registered:

     ```bash
     claude plugin marketplace list
     claude plugin list --json
     ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/org#require-a-marketplace-and-its-plugins
- https://code.claude.com/docs/en/plugins/org#blocklist-with-blockedmarketplaces
- https://code.claude.com/docs/en/plugins/host-marketplace#uninstall-removed-plugins-from-users-machines

## Relabel

A relabel changes only `displayName`, which no managed key names: nothing changes here. Follow `references/context-own-marketplace.md`.

## Rename or merge

**When**: the publisher renamed a plugin, or merged several into one, with a `renames` map, and managed `enabledPlugins` names an old key.

**Stages**:

1. **The publisher adds the `renames` entry** and ships it (`references/context-own-marketplace.md`, Relabel or rename a plugin, or Merge plugins).
   - Done when: the publisher's rename check passes in that reference.
2. **Replace each old key** in managed `enabledPlugins` with `"<new>@<marketplace>": true`, and remove the old keys.
   - Done when: the delivered managed settings name only the new key:

     ```bash
     python3 -m json.tool /etc/claude-code/managed-settings.json
     ```

3. **Confirm on a sample machine** after a new session.
   - Done when: the new id shows `"scope": "managed"` and no rename note remains on it:

     ```bash
     claude plugin list --json
     ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/host-marketplace#migrate-users-with-a-renames-map

## Split

**When**: the publisher split one plugin into several and the fleet should get the parts.

**Stages** (derived from the documented key rules):

1. **The publisher ships the new plugins** and decides what the old name becomes (`references/context-own-marketplace.md`, Split a plugin).
   - Done when: the publisher's split check passes in that reference.
2. **Add a managed `enabledPlugins` key for each part**, then remove the old key, or set it to `false` if it must stop loading where users installed it themselves.
   - Done when: the delivered managed settings name every part and not the old key as `true`:

     ```bash
     python3 -m json.tool /etc/claude-code/managed-settings.json
     ```

3. **Confirm on a sample machine** after a new session.
   - Done when: each part shows `"scope": "managed"`:

     ```bash
     claude plugin list --json
     ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/org#require-a-marketplace-and-its-plugins

## Move to another marketplace

**When**: the plugin moved to another marketplace, or the fleet should take it from another one.

**Stages**:

1. **Allow the new source** in managed `strictKnownMarketplaces`, when an allowlist is set.
   - Done when: no allowlist is set, or it holds an entry that matches the new marketplace's source exactly (`repo` or `url`, `ref` and `path`):

     ```bash
     python3 -m json.tool /etc/claude-code/managed-settings.json
     ```

2. **Switch the id in one delivery**: add the new marketplace's managed `extraKnownMarketplaces` entry, keyed by its own `name`, and replace `"<plugin>@<old>": true` with `"<plugin>@<new>": true` in managed `enabledPlugins`.
   - Never deliver both ids as `true`: two enabled plugins with the same name both show as enabled, but only one runs its hooks, and with both turned on by managed settings nothing says which.
   - Done when: the delivered managed settings name the new id and not the old one:

     ```bash
     python3 -m json.tool /etc/claude-code/managed-settings.json
     ```

3. **Confirm on a sample machine** after a new session.
   - What happens to the copy the old key installed isn't documented, as in [Stop installing it for the fleet](#stop-installing-it-for-the-fleet). The move notes from `assets/migration-notes.md` tell users to remove any old copy.
   - Done when: `<plugin>@<new>` shows `"scope": "managed"`:

     ```bash
     claude plugin list --json
     ```

4. **Remove the old marketplace's entry** when no other managed key names it, as [Retire a managed marketplace](#retire-a-managed-marketplace) does.
   - Done when: that section's stage 2 check passes for the old marketplace.

**Read in full**:

- https://code.claude.com/docs/en/plugins/org#restrict-what-users-can-install
- https://code.claude.com/docs/en/plugins/org#allowlist-with-strictknownmarketplaces
- https://code.claude.com/docs/en/settings-reference#extraknownmarketplaces
- https://code.claude.com/docs/en/plugins/loading#hooks-when-two-enabled-plugins-share-a-name

## Verify

On one machine that receives the settings, in a new session:

1. The user runs `/status`, and the `Setting sources` line names `Enterprise managed settings` with the source you changed.
2. Run these and show the raw output:

   ```bash
   claude plugin marketplace list
   claude plugin list --json
   ```

3. Each managed marketplace shows with its source; each managed plugin shows `"scope": "managed"` with the expected `version`; each blocked or removed plugin is absent or disabled.
4. For a CI or container fleet, run one job this way and read the `plugins` list of its `init` event; a seeded plugin's `path` is under the seed:

   ```bash
   claude -p "hello" --output-format stream-json --verbose
   ```

**Read in full**:

- https://code.claude.com/docs/en/plugins/org#confirm-the-rollout
- https://code.claude.com/docs/en/plugins/org#when-each-surface-applies-the-plugin-keys
- https://code.claude.com/docs/en/plugins/org#plan-for-what-managed-settings-cant-enforce
