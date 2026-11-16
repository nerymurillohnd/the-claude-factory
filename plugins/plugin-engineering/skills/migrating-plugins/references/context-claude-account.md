# A plugin on a Claude account

You act for the user whose Claude account has the plugin, or who made it there. The account's plugins are managed in Claude, at **Customize > Plugins** (https://claude.ai/customize/plugins), and Claude Code only receives a synced copy, `<name>@synced`, with no marketplace and no install record. **Customize > Plugins** is the user's to operate: write the exact clicks for every stage there, and mark it as waiting on the user. You can edit the plugin's files when the user has them, and run `claude plugin` commands, which change only the machine they run on. Load this reference when `claude plugin list` shows `<name>@synced`, or when the user works in Claude. A `<plugin>@claudeai-<marketplace>` id is different: it is a machine install from a marketplace hosted on claude.ai, with an install record, so update and uninstall it on the machine with `references/context-machine.md`; its source (the user's uploads, or the organization's library) changes on the account or in `references/context-organization.md`.

Who can change the plugin depends on where it came from:

- **The directory or a marketplace added in Claude**: the publisher. Their changes arrive through the source; see `references/context-directory.md` or `references/context-own-marketplace.md` when the user is that publisher.
- **Uploaded, or made with Create with Claude or Create a plugin**: the user is the publisher, and the account holds the plugin.
- **Added from a plugin suggestion card** in a cloud session: turned on for the account, where it stays after the session ends. The card's **Manage** opens its page on claude.ai, where it is removed.
- **Shared with you** by a teammate: the teammate. It stays in the list for as long as they share it.
- **Turned on by the organization** (installed by default or required): an Owner; see `references/context-organization.md`.

## Contents

- [Gotchas](#gotchas)
- [How the build changes the procedure](#how-the-build-changes-the-procedure)
- [Update](#update)
- [Turn off](#turn-off)
- [Remove](#remove)
- [Retire](#retire)
- [Relabel](#relabel)
- [Rename, merge or split](#rename-merge-or-split)
- [Move](#move)
- [Verify](#verify)

## Gotchas

- **Remove** deletes the plugin from the account. A plugin made with Create with Claude lives only on the account, so Remove destroys it; get its files first.
- `claude plugin uninstall` never applies to a synced plugin, because the plugin has no install record on the machine. To take it off every machine, turn it off or remove it in Claude.
- A plugin marked **This plugin is required by your organization** can't be turned off or removed by the user, in Claude or in Claude Code. Only an Owner changes it; see the gotchas of `references/context-organization.md`.
- Terminal sessions sync once, in the background, each time Claude Code starts (2.1.273+), so a change made on the account during a session applies at the next start. When the sync lands in an open session, it shows `Plugins changed. Run /reload-plugins to activate.`
- Claude loads the account's plugins into a task when the task starts. If the plugin changes during task work that runs in the cloud, keep working; if nothing has changed after a few messages, start a new conversation.
- Nothing syncs, removals included, in terminal sessions that use `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` or `apiKeyHelper` instead of the claude.ai sign-in, that set `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, that run in bare mode or with `--safe-mode`, or whose `--setting-sources` list leaves out `user`. A sign-in made on an older Claude Code covers plugins only after it renews; `/login` renews it now, and sync starts at the next start.
- A synced plugin loses to any enabled plugin of the same name from another origin, and Claude Code reports the synced copy as not loaded. When the user also installed the plugin from a marketplace, the account's changes never show in Claude Code until that copy is disabled or uninstalled.
- Sync only downloads. A file edited under `~/.claude/plugins/synced/` never reaches the account, and whether a later sync overwrites it isn't documented for plugins (for synced skills, it does). Make every change on the account.
- `syncClaudeAiPlugins: false`, in user or managed settings, stops every synced plugin on a machine and moves the ones already synced to `~/.claude/plugins/.trash/` at the next start. It is not a way to turn off one plugin.

## How the build changes the procedure

Plugins run in two modalities, and each loads a different part of the same plugin, so a change can work in one and not the other:

- **Claude** (chat and Cowork) reads the plugin from the account. Where chat and Cowork are one experience, everything Cowork did is available from any conversation, and a Cowork task runs as a session built on Claude Code, which downloads the account's plugins into the session's own environment. The docs' component table still has separate Chat and Cowork columns, and which one a conversation follows isn't documented. Derived: expect the Cowork column when Claude works through a task, and check each component that matters in a conversation that runs one. Where the account isn't one experience yet (the message box still shows separate Chat and Cowork options), chat follows the Chat column and Cowork tasks the Cowork column.
- **Claude Code** loads every component of the synced copy in terminal sessions.

What each component does under the docs' Chat column, under their Cowork column, and in Claude Code:

- **Skills** load under both columns and in Claude Code.
- **Commands**: the Chat column loads them as skills that Claude applies when they fit; the Cowork column runs them as `/plugin-name:command`; Claude Code loads them.
- **Agents and hooks**: the Chat column ignores them; the Cowork column and Claude Code load them.
- **A remote MCP server** (`http` or `sse` with a fixed URL) works in Claude only after the user adds or connects it from the plugin's **Connectors** tab, because installing never connects it. A connector marked **Not added** needs an Owner to add it on Team and Enterprise plans. Claude Code loads it.
- **A local MCP server** (marked **Runs in each session**): the Chat column ignores it; the Cowork column runs it only while the task runs on the user's computer with Claude Desktop open; Claude Code loads it.
- **An MCP server that references `${user_config.*}`**: the Chat column ignores it when the URL holds the reference; the Cowork column ignores it when a referenced option has no default, because it never prompts for values; Claude Code prompts for them.
- **A top-level `bin/`** makes Claude refuse to install the whole plugin; Claude Code loads it. What an update that adds one does to a copy already on the account isn't documented, so keep `bin/` out of any release that reaches Claude accounts.
- **LSP servers, output styles, themes and `settings`** load only in Claude Code.

Other parts of the build that change a stage:

- **Size**: Claude takes a plugin of up to 5,000 files and 200 MB, and **Upload plugin** a file of up to 200 MB. Check that an update stays within both.
- **Version**: `claude plugin list` shows a synced plugin's manifest `version`, or `unknown` when it declares none; with no `version`, prove an update by its contents.
- **Dependencies**: Claude installs none, because dependencies between plugins are a Claude Code-only feature. For the synced copy in Claude Code, a dependency that names a marketplace is met only by that plugin installed from its marketplace, or by a plugin of the same name turned on in the same account. When a plugin with dependencies reaches users through Claude, tell them to turn the dependencies on there too.

**Read in full**:

- https://claude.com/docs/plugins/platform-support#compare-component-support-by-app
- https://claude.com/docs/plugins/platform-support#compare-installation-sync-and-admin-controls
- https://claude.com/docs/plugins/overview#bundled-connectors
- https://code.claude.com/docs/en/plugins/loading#plugins-synced-from-claudeai
- https://code.claude.com/docs/en/plugins/install#add-a-marketplace-from-claudeai
- https://code.claude.com/docs/en/plugins/dependencies#dependencies-when-your-plugin-loads-from-claudeai
- https://claude.com/docs/plugins/build#add-claude-code-only-components
- https://support.claude.com/en/articles/16761823

## Update

**When**: the plugin's source released a new version, or the user changed a plugin they made.

**Stages**:

1. **Get the new version onto the account**, by origin:
   - from the directory: nothing to run; updates arrive from the source on their own, with nothing to accept;
   - from a marketplace added in Claude: select **Check for updates** on the marketplace to pull now, or turn on **Sync automatically** for one added from github.com;
   - uploaded or made in Claude: edit it in place, in the plugin's editor or in the conversation that made it. Users it is shared with get the edits wherever they use Claude. Whether uploading it again replaces it or adds a second plugin isn't documented: when the user uploads instead, check the list and handle a duplicate as in [Rename, merge or split](#rename-merge-or-split);
   - published to the organization's library: follow `references/context-organization.md`.
   - Done when: the plugin's page in **Customize > Plugins** shows the new contents in its tabs.
2. **Keep local edits**: if the user edited the plugin's files on their computer, Claude warns before the update overwrites them; save those files first.
   - Done when: the user has kept the edits, or has said there are none.
3. **Claude Code**: the next start syncs the new version. In an open session, the `Plugins changed` message appears; ask the user to type `/reload-plugins` there to load the change in that session.
   - Done when: the list shows `<name>@synced` with the new `version`, or with its new contents when it declares none.

   ```bash
   claude plugin list --json
   ```

**Read in full**:

- https://claude.com/docs/plugins/overview#manage-installed-plugins
- https://claude.com/docs/cowork/guide/plugins#update-and-remove-plugins
- https://claude.com/docs/plugins/share#what-the-people-you-share-with-get
- https://code.claude.com/docs/en/plugins/loading#sync-timing-in-terminal-sessions

## Turn off

**When**: the user wants to stop using the plugin and keep it, with its connectors, on the account.

**Stages**:

1. **On the account**: open the plugin in **Customize > Plugins** and turn off its toggle (**Disable plugin**). Turning it on again brings it back. A plugin installed by default can be turned off this way; a required one can't.
   - Done when: the toggle shows off.
2. **Claude Code**: the next start removes the synced copy.
   - Done when: after a new start, the list no longer shows `<name>@synced`.

   ```bash
   claude plugin list --json
   ```

**Only on one machine**, keeping it on the account: disable the synced copy there. This saves `"<name>@synced": false` in user `enabledPlugins`; to keep it out of one project on every machine, put the same key in that project's committed `.claude/settings.json`.

```bash
claude plugin disable <name>@synced
```

- Done when: the list shows `<name>@synced` as disabled.

  ```bash
  claude plugin list --json
  ```

**Read in full**:

- https://claude.com/docs/plugins/overview#manage-installed-plugins
- https://code.claude.com/docs/en/plugins/loading#control-which-synced-plugins-load
- https://code.claude.com/docs/en/plugins/install#manage-plugins-synced-from-claudeai

## Remove

**When**: the plugin should leave the account for good (uninstall). To stop using it and keep it, turn it off instead.

**Stages**:

1. **Keep what Remove destroys**: for a plugin made with Create with Claude, the user asks Claude, in the conversation that made it, for the plugin "as a plugin folder", and downloads the zip; for an uploaded plugin, check that the user still has its file. For a plugin the user shares, tell those users first: a shared plugin stays in their list only while it is shared, and what Remove does to their copy isn't documented.
   - Done when: the user has the zip and has told those users, or has said neither is needed.
2. **Remove**, after the user's explicit yes: open the plugin in **Customize > Plugins**, open its menu and select **Remove**.
   - Done when: the plugin is gone from **Customize > Plugins**.
3. **Claude Code**: the next start removes the synced copy.
   - Done when: after a new start, the list has no `<name>@synced`.

   ```bash
   claude plugin list --json
   ```

**Read in full**:

- https://claude.com/docs/plugins/overview#manage-installed-plugins
- https://claude.com/docs/plugins/create-with-claude#use-disable-or-remove-your-plugin
- https://claude.com/docs/plugins/create-with-claude#submit-a-plugin-you-created-with-claude

## Retire

**When**: the user made the plugin and wants nobody to get it anymore. For a plugin from the directory or a marketplace, the publisher retires it in that context, and what the account's copy does then is written there.

**Stages**:

1. **Tell the users who have it**, with notes from `assets/migration-notes.md`, before they lose it.
   - Done when: the user has sent the notes.
2. **Stop sharing**, after the user's explicit yes: open the plugin, select **Share**, and remove each user from the list. The plugin stops loading for them. A copy a user added from the plugin file is a separate plugin on their account, out of the user's reach: the notes ask them to remove it.
   - Done when: the share list is empty.
3. **Published to the organization's library**: retire it there, with "Turn off for members, or retire" in `references/context-organization.md`.
   - Done when: that section's checks pass.
4. **The user's own copy**: turn it off, or remove it with the stages of [Remove](#remove).
   - Done when: the stage's own check passes.

**Read in full**:

- https://claude.com/docs/plugins/share#stop-sharing-a-plugin
- https://claude.com/docs/plugins/share#choose-how-to-distribute-a-plugin

## Relabel

**When**: only the label users see must change.

1. **Change `displayName`** in the plugin's manifest and leave `name` as it is. For a plugin the user made, release it as in [Update](#update); from a marketplace or the directory, the change arrives as an update from the source.
   - Done when: **Customize > Plugins** shows the new label, and the list in Claude Code still shows `<name>@synced` under the old `name`.

   ```bash
   claude plugin list --json
   ```

**Read in full**:

- https://claude.com/docs/plugins/build#write-the-manifest

## Rename, merge or split

**When**: the plugin's `name` must change, several plugins become one, or one becomes several.

What a publisher's `renames` map does to an account's copy isn't documented; it is a rule of marketplace installs on a machine. For a plugin from the directory or a marketplace, test on one account after the publisher's release: when the old plugin stops updating or disappears, install the new one from **Customize > Plugins** and remove the old one with the user's yes.

**Stages, for plugins the user made** (derived from the documented install, share and remove steps):

1. **Build the new plugins** and add them to the account by upload or in Claude. For a merge, carry over every skill, command and connector of the old plugins; for a split, give each new plugin the parts its users need.
   - Done when: each new plugin passes the checks in [Verify](#verify).
2. **Share each new plugin** with the users of the old one. A shared plugin arrives turned off, so the notes from `assets/migration-notes.md` tell them to turn it on and to reconnect its connectors with their own account.
   - Done when: the share lists match the old plugin's, and the user has sent the notes.
3. **Retire the old plugin** with stages 2 to 4 of [Retire](#retire), once users have the new one.
   - Done when: the old plugin is gone from **Customize > Plugins**, or is off.
4. **Claude Code**: at the next start, the old synced copy leaves and the new ones arrive.
   - Done when: the list shows each new `<name>@synced` and none of the old.

   ```bash
   claude plugin list --json
   ```

**Read in full**:

- https://claude.com/docs/plugins/overview#find-and-add-a-plugin
- https://claude.com/docs/plugins/share#what-the-people-you-share-with-get

## Move

**When**: the plugin must reach another organization, or move from the account to a marketplace or the directory.

- **To another organization**: a plugin is attached to the account for the organization it was added in, and a plugin file added in another organization becomes a separate plugin there. Derived: the user switches to the other organization and adds the plugin file with **Add > Upload plugin**. Retire the old one only if it should leave the first organization.
- **To a marketplace or the directory**: get the plugin's files as in [Remove](#remove), stage 1, push them to a Git repository, and follow `references/context-own-marketplace.md` or `references/context-directory.md`. Then retire the account's copy once users have the new source.
- **A marketplace added in Claude that moves host**: Claude accepts only some hosts; check the new one against the bullet for users who added it in Claude, under "Hosted in a public git repository" in `references/context-own-marketplace.md`. Then the user adds the marketplace again from its new address (derived).

**Read in full**:

- https://claude.com/docs/plugins/share#choose-how-to-distribute-a-plugin
- https://claude.com/docs/plugins/create-with-claude#submit-a-plugin-you-created-with-claude
- https://claude.com/docs/plugins/platform-support#compare-installation-sync-and-admin-controls

## Verify

1. In **Customize > Plugins**, the plugin shows the expected state (on, off or gone), label and contents.
2. In Claude, open a conversation and ask Claude which skills it has from plugins. When the plugin has agents or hooks, run a task in Claude and check that they load. Connect each bundled connector from the **Connectors** tab and check it shows **Connected**.
3. In Claude Code, after a new start, `<name>@synced` is listed as expected, or isn't listed.

   ```bash
   claude plugin list --json
   ```

4. In the same list, no enabled plugin of the same name comes from another origin; if one does, it loads instead of the synced copy.

**Read in full**:

- https://claude.com/docs/plugins/build#test-the-plugin-on-each-surface
- https://code.claude.com/docs/en/plugins/loading#name-conflicts
