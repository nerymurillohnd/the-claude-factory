# Notes for users who have the plugin

Use this in Step 6 when the change asks something of users or changes what they get: a name, a command, an option, their data, or where the plugin comes from. Turning a plugin off or uninstalling it on the user's own machine, a relabel, and a directory or organization update that users receive with nothing to do need no notes. Keep only the parts that apply, and give the notes to the user to send.

## Gotchas

- A note users must act on is useless once the change reaches them. A retired plugin stops loading as soon as their catalog has the change, and a delisted one may be removed, so send that note first and let the user set the date (see "Retire a plugin" in `references/context-own-marketplace.md`).
- Users run the commands exactly as the note writes them. Write the real plugin, marketplace and scope names, and say where each one runs: `claude plugin …` in the shell, `/plugin …` and `/reload-plugins` inside a Claude Code session.
- One change reaches users by a different route in each context. Write one section per audience the change reaches: users of the marketplace in Claude Code, users who have the plugin on a Claude account, and admins who deliver it through managed settings.

## What every note says

1. What changes for the reader.
2. What they must do, in order, and by when.
3. What they will see, with the exact messages.

Write it for the user who has the plugin, not for the maintainer.

## What each kind of change adds

- **Update**: how the release reaches them, by where they got it:
  - a marketplace without auto-update (the default for every third-party marketplace): `claude plugin update <plugin>@<marketplace>` in the shell, **Update now** on the plugin in `/plugin` > Installed, or **Update marketplace** in `/plugin` > Marketplaces for all its plugins, then `/reload-plugins` in an open session; and that `claude plugin marketplace update` in the shell alone leaves installed plugins at their version. Don't name `/plugin marketplace update <name>` as the route until the conflict in the second gotcha of `references/context-own-marketplace.md` is settled;
  - how to get later releases on their own: `/plugin` > Marketplaces > the marketplace > **Enable auto-update**;
  - a marketplace added from a local path: nothing to run, the next session or `/reload-plugins` loads it;
  - a private repository: what users whose credentials can't answer in the background must do (see "Hosted in a private git repository" in `references/context-own-marketplace.md`);
  - a marketplace added in Claude: it arrives on its own, and **Check for updates** in **Customize > Plugins** pulls it now;
  - a raised `engines["claude-code"]` (2.1.323+, **changelog**): the Claude Code versions it needs, and that older versions keep the newest release that fits;
  - a new remote MCP server: connect it from the plugin's **Connectors** tab in **Customize > Plugins**, because installing never connects it; on Team and Enterprise an Owner adds it first;
  - when an earlier release didn't arrive: why, and that this one fixes it.
- **Rename or merge**:
  - the new name and the new `/<new-plugin>:<skill>` command names;
  - what proves the migration: `claude plugin list` shows `<new>@<marketplace>`. The docs say `Renamed to "<new>" in the "<marketplace>" marketplace` shows once, but it didn't print in `claude plugin list` in a rehearsal **(observed)**, so mention it as something they may see, not as the check;
  - `/plugin install <new>@<marketplace>` once in a session, while Claude Code reports `Plugin "<new>" not cached at <path>` (git and URL marketplaces);
  - that disabled installs aren't migrated **(observed)**: uninstall the old id and install the new one if they want it;
  - the options to set again with `/plugin configure <new>@<marketplace>`; after a merge only one old plugin's options survive **(observed)**;
  - where the old data stays: `~/.claude/plugins/data/<old-id>/` **(observed)**;
  - that Claude Code rewrites the key in a project's `.claude/settings.json`, so one collaborator commits that change, and every collaborator then runs `claude plugin install <new>@<marketplace> --scope project` once per clone, because committing the key doesn't download the plugin (https://code.claude.com/docs/en/plugins/install#choose-an-install-scope). Until they do, `/plugin` > Errors shows `Plugin "<new>" is enabled in project settings but isn't installed here`, or `not cached at <path>` before 2.1.323 (changelog 2.1.323). Before writing this, read https://code.claude.com/docs/en/plugins/loading#enabled-in-project-settings-but-not-installed in full;
  - for users who have it on a Claude account from the directory or a marketplace: install the new one from **Customize > Plugins** once the old one stops updating, then remove the old one (see "Rename, merge or split" in `references/context-claude-account.md`);
  - for a directory listing: a machine where they set `"<old>@synced": false` needs `"<new>@synced": false` instead (see "Rename" in `references/context-directory.md`);
  - for admins: the managed `enabledPlugins` key to change, and that the rename notice repeats until they do.
- **Retirement**:
  - the date, and what to do before it: save data from `~/.claude/plugins/data/<id>/`, move to the replacement;
  - that once their catalog has the change, the plugin stops loading and they see `Removed from the "<marketplace>" marketplace`;
  - whether a later session start uninstalls it for them (`forceRemoveDeletedPlugins`), deleting its options, secrets and data **(observed)**; otherwise, to uninstall it themselves, with `--keep-data` to keep the data folder;
  - for a whole marketplace: `claude plugin marketplace remove <name>` after its plugins are retired, which uninstalls what is left with its options, secrets and data;
  - in the directory: after delisting, no more updates, and their copy may be removed;
  - in an organization: once it is **Not available**, it stops loading for members who installed it;
  - for admins: `forceRemoveDeletedPlugins` leaves plugins that only managed settings installed, so they set the key to `false` in managed `enabledPlugins` (see "Turn off or block" in `references/context-managed-settings.md`).
- **A `command` source whose command or `mode` changed**: run the `claude plugin update` command that the `/plugin` Errors tab shows, in a terminal, and accept the new command; until then the plugin's once-per-session run stops.
- **Any release of a plugin whose entry sets `headersHelper`**: update that one plugin by itself and accept the command it shows: from its own view in `/plugin`, with `claude plugin update <plugin>@<marketplace>` in the shell, or from **Manage plugins** in the VS Code extension. Auto-update and **Update marketplace** skip it and list it in the Errors tab.
- **Split**:
  - the new plugin's name;
  - whether an update installs it, when the original now depends on it (the next auto-update, or `claude plugin update <original>@<marketplace>` then `/reload-plugins`), or they install it themselves;
  - for users who have the original on a Claude account, from any source: turn the new plugin on there too, or install it from its marketplace, because Claude installs no dependencies.
- **Move to another marketplace** (a renamed marketplace is one too):
  - add the new marketplace, turn `<plugin>@<old>` off, install `<plugin>@<new>`, then uninstall `<plugin>@<old>`, with `--keep-data` to keep the old data folder and copy it across, because data lives under the plugin's id;
  - why the old one goes off first: when two enabled plugins share a manifest name, only one runs its hooks;
  - the options to set again;
  - for admins: enable `<plugin>@<new>` in managed `enabledPlugins` and remove the old key.
- **Marketplace moved to a new address under the same name**:
  - whether users must do anything (see "Move a plugin or a marketplace" in `references/context-own-marketplace.md`);
  - when they must, the route in stage 3 of that procedure: change `source` in the `extraKnownMarketplaces` entry that declares the marketplace (`~/.claude/settings.json` for one they added), then start a new session, or run `claude plugin marketplace add <new-source>` to apply it at once; plugin ids, options and data stay;
  - the exact `source` object to write, in the type the new address parses as: `{"source": "github", "repo": "<owner>/<repo>"}` for `owner/repo`, `{"source": "git", "url": "<url>"}` for a git URL. An entry of another type still refuses the add with `Cannot add marketplace "<name>": its source doesn't match its extraKnownMarketplaces entry in user or managed settings`;
  - for a marketplace added from a local path only: `claude plugin marketplace add <new-path>` re-points it without the edit **(observed)**;
  - not to remove and re-add the marketplace, because `claude plugin marketplace remove` uninstalls every plugin from it with its options, secrets and data;
  - for a private repository: confirm they can reach the new one before they switch.
- **In the directory or an organization**:
  - an update, when users must act on it (a server to connect, an option to set): when the version goes live (after it is published, or after the next sync), and that Claude Code loads it at its next start, or after `/reload-plugins` when it shows `Plugins changed. Run /reload-plugins to activate.`;
  - a rename, merge, split or move: the new plugin to add from **Customize > Plugins** > **Discover** (a new listing, or an organization plugin set to **Available to install**), then the old one to remove, and to set the new one up as a new plugin, because moving options or data between plugins there isn't documented; an organization plugin set to **Installed by default** or **Required** arrives on its own.
- **A plugin shared from the user's Claude account**:
  - a rename, merge or split: the new plugin is under **Shared with you** on the **Your plugins** tab of **Customize > Plugins**, turned off until they turn it on, and they connect its connectors with their own account;
  - a retirement or a move: the date sharing stops, after which the plugin stops loading for them; where to get it instead, if anywhere; and that a copy they added from the plugin file is their own, so they remove it themselves.

## Example: a merge

Input: `lint-helper` and `format-helper` merge into `code-quality` in the `acme-tools` marketplace on GitHub. Both old plugins had an option named `level`, now `lint_level` and `format_level`. Neither kept data.

Output:

```markdown
## lint-helper and format-helper are now code-quality

**What changes:** both plugins are now one plugin, `code-quality`. Its skills are `/code-quality:lint` and `/code-quality:format`, which replace `/lint-helper:run` and `/format-helper:run`.

**What to do:**
1. Update the marketplace in your shell: `claude plugin marketplace update acme-tools`.
2. In a Claude Code session, run `/plugin install code-quality@acme-tools` once. Until you do, Claude Code reports `Plugin "code-quality" not cached at <path>`.
3. In a session, run `/plugin configure code-quality@acme-tools` and set your options again: the old `level` option is now `lint_level` and `format_level`.
4. Update scripts or docs that call the old skill names. If a project's `.claude/settings.json` enabled either plugin, Claude Code rewrites it to `code-quality@acme-tools`: commit that change.

**What you'll see:** after step 2, `claude plugin list` shows `code-quality@acme-tools`. Claude Code may also show `Renamed to "code-quality" in the "acme-tools" marketplace` once. If you had either plugin disabled, it isn't migrated: uninstall it and install `code-quality` if you want it.

**Admins:** change `lint-helper@acme-tools` and `format-helper@acme-tools` to `code-quality@acme-tools` in managed `enabledPlugins`; until then the notice repeats.
```
