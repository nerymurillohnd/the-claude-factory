# A plugin a claude.ai organization distributes

You act for the Owner of a Team or Enterprise organization, or for the member who published the plugin. The organization distributes plugins from **Organization settings > Plugins & skills**: from a repository synced as a marketplace, an uploaded plugin, a member's plugin published to the organization's library, or one of Anthropic's catalogs. Members, the users here, get them on their Claude accounts, and in Claude Code as synced plugins (see `references/context-claude-account.md`).

You can edit the synced repository. The organization's settings are the Owner's: write the exact clicks for every settings stage, and mark it as waiting on the Owner when the Owner isn't the user.

## Contents

- [Gotchas](#gotchas)
- [How the build changes the procedure](#how-the-build-changes-the-procedure)
- [Pilot with a few members](#pilot-with-a-few-members)
- [Update](#update)
- [Turn off for members, or retire](#turn-off-for-members-or-retire)
- [Relabel](#relabel)
- [Rename or merge](#rename-or-merge)
- [Split](#split)
- [Move to another repository](#move-to-another-repository)
- [Verify](#verify)

## Gotchas

- Organization sync reads the repository's default branch only, when an Owner selects **Re-sync** or on each push with **Sync automatically** on. Nothing syncs on a schedule, and tags aren't read, so a tag releases nothing.
- **Delete source** permanently deletes every plugin of that marketplace for every member. To pause or withdraw one plugin, set its availability to **Not available**.
- A plugin new to a synced marketplace starts with the marketplace's **Default access** at its first sync. When that is **Installed by default** or **Required**, a renamed, merged, split or moved plugin reaches every member at that sync, before any pilot.
- Group settings exist only on Enterprise. A group's own **Group access…** setting replaces the organization-wide availability for that group's members, whether it is stricter or looser. A member in several groups gets the most permissive setting.
- A member can't turn off or remove a plugin that is **Required** for them, in Claude or in Claude Code.
- Turning off **Skills** in the Policy tab turns off every plugin and skill for every member, and the sync into Claude Code. To stop only the sync into Claude Code, an admin sets `syncClaudeAiPlugins` to `false` in managed settings instead.
- When managed settings also install the plugin, Claude Code loads the managed copy and reports the synced copy as not loaded. Plan that route with `references/context-managed-settings.md` as well.
- What organization sync does with a `renames` map, and how members' installs carry over to a new name or a new marketplace, isn't documented. Run the old and the new plugin side by side and switch availability, as the stages below do.

## How the build changes the procedure

- **The synced repository** is a marketplace. On github.com and gitlab.com it must be private or internal, so an organization can't sync a public marketplace on those hosts.
- **Plugin sources**: each must be `github`, `url`, `git-subdir` or a relative path starting with `./`. A bare name under `metadata.pluginRoot` is rejected. A source outside the repository must be public on github.com, gitlab.com or bitbucket.org, or private only under the org-sync section's conditions (same github.com owner, the organization's GitHub Enterprise host, or the same GitLab host). To keep a plugin private, keep its folder in the synced repository.
- **A top-level `bin/`** makes Claude reject that plugin, with `Plugin contains a top-level bin/ directory`; the rest of the marketplace still syncs.
- **Uploaded plugins** can be rolled back from **Version history**. Synced plugins also list their versions there, but can't be reverted: a synced plugin rolls back only through the repository.
- **A member's published plugin** is frozen at the version submitted; later edits reach the organization only when the member publishes again.
- **Versioning**: whether organization sync reads `version` isn't documented; the item's **Version history** records each version and how it arrived, such as a GitHub push. Keep the plugin's versioning model, because Claude Code machines that add the same repository as a marketplace compare it.

**Read in full**:

- https://claude.com/docs/plugins/org-sync#plugin-sources-that-organization-sync-accepts
- https://claude.com/docs/plugins/org-sync#keep-executables-out-of-the-top-level-bin-directory
- https://claude.com/docs/plugins/admin#open-an-items-page
- https://claude.com/docs/plugins/org-rollout#if-a-developer-has-the-plugin-from-both-routes
- https://code.claude.com/docs/en/plugins/host-marketplace#distribute-through-organization-settings

## Pilot with a few members

Pilot a change that replaces a plugin members already have. Pick one route when you plan:

- **Group pilot**, on Enterprise when the new plugin's marketplace has **Default access** set to **Not available**: right after the sync, set the pilot group's **Group access…** for the new plugin, and **Not available** for the old one in that group.
- **Shared pilot**, in every other case: before members can get the new plugin from the organization, upload it to the user's own account from **Customize > Plugins** > **Add** > **Upload plugin**, and share it with the pilot members (**Share** on the plugin's page). This needs **User-created skills** and **Skill sharing** on in the Policy tab. On Enterprise, with **Share with groups** on, share it with a group.
- End a shared pilot by removing every member from **Share** before the organization's copy reaches them, so members don't get two plugins with one name. What happens when they do isn't documented.

**Read in full**:

- https://claude.com/docs/plugins/admin#limit-to-user-groups-on-enterprise
- https://claude.com/docs/plugins/share#share-a-plugin-with-specific-people

## Update

**When**: the plugin changed and members should receive it.

**Stages, for a synced repository**:

1. **Release in the repository**: run the version, compatibility, validate and commit stages of **Update: release a new version** in `references/context-own-marketplace.md`, then push or merge the release to the default branch with the user's yes.
   - Done when: the remote's default branch has the release commit (both commands print the same SHA, from the release commit):

     ```bash
     git rev-parse HEAD
     git ls-remote origin HEAD
     ```

2. **Sync**, with the user's yes: skip it when **Sync automatically** is on. Otherwise the Owner opens the Marketplaces tab, opens the menu on the marketplace's row and selects **Re-sync**. On **You synced recently**, wait the seconds it gives and select **Re-sync** again.
   - Done when: the marketplace's page shows **Last synced** after the release, with no failure, and the plugin's **Version history** lists the new version.

Members then get the new version on their account, and Claude Code at its next start (see the gotchas of `references/context-claude-account.md`).

**Stages, for an uploaded plugin**:

1. **Upload**: open the plugin's menu and select **Upload new version**.
   - Done when: its **Version history** marks the new version **Current**.
2. **Roll back**, when the user asks: in **Version history**, open the earlier version's menu and select **Revert to this version**; **Make this the current version** on a newer one goes forward again.
   - Done when: **Current** is on the chosen version.

**Stages, for a member's published plugin**:

1. **Publish again**: the member selects **Publish to org** on the plugin's page.
   - Done when: the plugin's page shows it published, or waiting for review.
2. **Review**, under **Requires review**: a reviewer other than the member approves the request in the Requests tab and sets its availability.
   - Done when: the plugin's page shows it published.

**Read in full**:

- https://claude.com/docs/plugins/org-rollout#update-through-organization-settings
- https://claude.com/docs/plugins/admin#manage-synced-marketplaces
- https://claude.com/docs/plugins/admin#roll-back-to-an-earlier-version
- https://claude.com/docs/plugins/admin#review-plugins-that-members-publish
- https://claude.com/docs/plugins/share#publish-a-plugin-to-your-organization

## Turn off for members, or retire

**When**: pause a broken plugin, or stop offering it, which is what users mean by deprecate. There is no deprecation state. The same stages turn off a plugin from one of Anthropic's catalogs, except the last.

**Stages**:

1. **Agree the timing** with the user. When members must act first (finish work, move to a replacement), send them the notes from `assets/migration-notes.md` before the change.
   - Done when: the user confirmed the date and, where needed, that the notes went out.
2. **Availability**, with the user's yes: in the Inventory tab, open the plugin's menu > **Default access** > **Not available**. Members stop seeing it and Claude stops loading it, including for members who installed it. Claude Code removes the synced copy at its next start.
   - Done when: the Inventory tab shows **Not available** for the plugin.
3. **Groups**, on Enterprise, with the same yes: set every group that has its own **Group access…** for the plugin to **Not available** too.
   - Done when: no group grants the plugin.
4. **Remove it for good**, only when the user chose that:
   1. For a synced repository, remove the plugin's entry in the repository (with its repository stages from **Retire a plugin** in `references/context-own-marketplace.md` when machines also add the repository as a marketplace) and sync as in **Update**.
   2. When the plugin is still in the Inventory tab, delete it from its menu there, with the user's yes. Whether a sync removes a plugin dropped from the repository isn't documented.
   - Done when: the plugin is no longer in the Inventory tab after the sync.

**A whole catalog of Anthropic's**, such as the directory, with the user's yes: in the Marketplaces tab, open the catalog row's menu > **Remove from organization**, then **Remove** in **Remove source**. Members no longer see its plugins; what happens to plugins they already installed from it isn't documented, so check with one member. **Add** > **Add marketplace** > **Browse Anthropic sources** adds it back.

- Done when: the catalog's row is gone from the Marketplaces tab.

**Read in full**:

- https://claude.com/docs/plugins/admin#set-availability
- https://claude.com/docs/plugins/admin#limit-to-user-groups-on-enterprise
- https://claude.com/docs/plugins/admin#open-an-items-page
- https://claude.com/docs/plugins/admin#remove-one-of-anthropics-sources
- https://claude.com/docs/plugins/admin#turn-plugins-and-skills-off-for-everyone

## Relabel

**When**: only the name members see changes.

**Stages**:

1. **Change `displayName`** in `plugin.json`, keep `name`, and release it as in **Update**.
   - Done when: the plugin's **Version history** lists the new version.
2. **Check the label**: which name Claude shows for an organization's plugin isn't documented. Check it in one member's **Customize > Plugins**.
   - Done when: the member sees the new label, or the user knows Claude still shows `name`.

**Read in full**:

- https://claude.com/docs/plugins/build#write-the-manifest

## Rename or merge

**When**: the plugin's `name` must change, or several plugins become one.

**Stages, for a synced repository**:

1. **Agree the timing and the availability** with the user: the date, which plugins are replaced, the availability and groups the new plugin gets (normally those of the old ones), and the pilot route from [Pilot with a few members](#pilot-with-a-few-members). When members must act (install the new plugin when it is **Available to install**, set its options again), send them the notes from `assets/migration-notes.md` before stage 5.
   - Done when: the user confirmed them.
2. **Shared pilot**, when that is the route.
   - Done when: the pilot members confirm the new plugin works.
3. **Add the new plugin** to the repository next to the old ones, and sync as in **Update**.
   - Done when: the new plugin is in the Inventory tab.
4. **Group pilot**, when that is the route.
   - Done when: the pilot members confirm the new plugin works.
5. **Switch availability**, with the user's yes: set the new plugin, and each group, to the agreed values, then set the old plugins to **Not available**, in the same sitting.
   - Done when: the Inventory tab shows the new plugin at the agreed availability and the old ones at **Not available**.
6. **Remove the old plugins**, after the date agreed:
   1. Remove their entries from the repository. When machines also add the repository as a marketplace, put the `renames` entries in the same commit, as **Relabel or rename a plugin** or **Merge plugins** in `references/context-own-marketplace.md` says.
   2. Sync as in **Update**, then delete from the Inventory tab, with the user's yes, any old plugin still listed.
   - Done when: the old plugins are no longer in the Inventory tab.

For an uploaded plugin or a member's published one, the same order applies: upload or publish the new plugin, switch availability, then delete the old one with the user's yes.

**Read in full**:

- https://claude.com/docs/plugins/admin#set-availability
- https://claude.com/docs/plugins/admin#add-your-own-plugins
- https://claude.com/docs/plugins/admin#manage-synced-marketplaces

## Split

**When**: part of the plugin becomes a plugin of its own.

**Stages**:

1. **Add the new plugin** to the synced repository, remove what moved out of the original, release both as in **Update**, and sync. The repository work follows **Split a plugin** in `references/context-own-marketplace.md`.
   - Done when: both plugins are in the Inventory tab with the new versions.
2. **Set the new plugin's availability**: it starts with the marketplace's **Default access**; set it, and each group on Enterprise, to what the user chose.
   - Done when: both plugins show the intended availability in the Inventory tab.

**Read in full**:

- https://claude.com/docs/plugins/admin#manage-synced-marketplaces
- https://claude.com/docs/plugins/admin#set-availability

## Move to another repository

**When**: the plugins move to a new repository, host or Git provider.

**Stages**:

1. **Check the new repository** against [How the build changes the procedure](#how-the-build-changes-the-procedure). For GitLab, an Owner first adds a GitLab configuration for the host in **Organization settings > Git providers**.
   - Done when: the repository is private or internal, and every source is an accepted type.
2. **Sync the new repository** as a new marketplace, with **Default access** at **Not available** so nothing reaches members yet. With **Add** > **Sync from GitHub**, choose it in the dialog. With **Add** > **Sync from GitLab**, the docs don't show that choice, so set **Default access** on the marketplace's page right after it is added.
   - Done when: the new marketplace's page shows **Last synced** with no failure, and its plugins are in the Inventory tab at **Not available**.
3. **Pilot**, by the route [Pilot with a few members](#pilot-with-a-few-members) picks.
   - Done when: the pilot members confirm the plugins work.
4. **Switch availability**, with the user's yes: give each new plugin, and each group, the availability its old copy had, then set the old copies to **Not available**, in the same sitting.
   - Done when: the Inventory tab shows each new plugin at the old availability and each old copy at **Not available**.
5. **Remove the old marketplace**, with the user's yes: **Delete source** on the old marketplace, from the Marketplaces tab. It deletes every plugin in that marketplace for every member, so check first that each one has a new copy.
   - Done when: the old marketplace is gone from the Marketplaces tab.

**Read in full**:

- https://claude.com/docs/plugins/org-sync#sync-a-marketplace-from-githubcom
- https://claude.com/docs/plugins/org-sync#sync-a-gitlab-hosted-marketplace
- https://claude.com/docs/plugins/admin#manage-synced-marketplaces
- https://claude.com/docs/plugins/admin#roll-back-to-an-earlier-version, for what **Delete source** deletes

## Verify

1. The Inventory tab shows the intended availability for each plugin and each group.
2. The Marketplaces tab shows **Last synced** after the change, with no failure.
3. One member sees the expected state in **Customize > Plugins**.
4. On that member's machine, after a new start, `<name>@synced` (or the plugin under a `claudeai-` marketplace, when the member added the organization's library) shows with the expected `version`, or is gone:

   ```bash
   claude plugin list --json
   ```
