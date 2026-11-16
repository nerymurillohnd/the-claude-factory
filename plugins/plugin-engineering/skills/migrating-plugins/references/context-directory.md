# A listing in Anthropic's directory

You act for the publisher of a plugin listed in Anthropic's directory. Each listing reads one folder of one GitHub repository, follows one tracked branch or tag, and belongs to the claude.ai organization that submitted it. Users add it from **Customize > Plugins** > **Discover** in Claude, so it lives on their account, and Claude Code loads it as `<name>@synced`.

You can edit the repository. The developer portal at https://claude.ai/directory/manage is the user's, and only an account that can submit opens it (on Pro, Max or Ultra the account itself; on Team and Enterprise an Owner, or on Enterprise a member with the **Directory** permission). For every portal stage, write the exact clicks for the user and mark the stage as waiting on them.

## Contents

- [Gotchas](#gotchas)
- [How the build changes the procedure](#how-the-build-changes-the-procedure)
- [Update](#update)
- [Turn off or uninstall](#turn-off-or-uninstall)
- [Retire: delist or withdraw](#retire-delist-or-withdraw)
- [Relabel](#relabel)
- [Rename](#rename)
- [Merge](#merge)
- [Split](#split)
- [Move to another repository, folder or organization](#move-to-another-repository-folder-or-organization)
- [Verify](#verify)

## Gotchas

- A version that passes every check isn't live until it is published. **Approved** isn't installable; only **Published** is. Until then the listing keeps serving the last published version, so users see no change and no error.
- After a version fails the security scan, later versions also wait until a reviewer clears the plugin.
- Every new version is scanned against all the directory's rules again, the name checks included: a `name` another organization uses blocks it, and a look-alike or a brand name holds it for a reviewer.
- A listing's repository and folder can't change after submission. A different one is a new submission, with its own review, and users of the old listing don't move to it on their own.
- A listing submitted through the earlier Claude Console form gets no new versions. Move it to the portal before any update: in the Console's **Plugin submissions**, select **Withdraw** and submit again from claude.ai, or, when there is no **Withdraw** button, email `directory@anthropic.com` to have it moved.
- The directory is separate from Anthropic's marketplaces: a listed plugin reaches Claude Code through account sync, never through a marketplace install. `claude-plugins-official` doesn't take submissions through the portal; a partner contact at Anthropic is the route to it.

**Read in full**:

- https://claude.com/docs/plugins/submit#after-you-submit-a-plugin
- https://claude.com/docs/directory/submission-status#plugin-bundle-statuses
- https://claude.com/docs/directory/publish#confirm-you-can-submit-to-the-directory
- https://claude.com/docs/directory/publish#move-an-earlier-submission-to-the-developer-portal
- https://code.claude.com/docs/en/plugins/publish#submit-to-anthropics-directory, with its subsection

## How the build changes the procedure

- **The tracked ref**: a branch releases on every push to it. A tag stays on its commit, so a release is a new tag that the user selects as the tracked tag (see [Update](#update), stage 3).
- **The publish setting**, shown in the **Auto-publish** row of the plugin's **Overview** tab: by default the user selects **Publish** and a reviewer publishes each version. When the setting lets later versions go live by themselves and **Publish new versions automatically** is on, a passing version goes live with no portal step, so the push is the moment the change reaches users.
- **Versioning**: when `plugin.json` sets `version`, raise it with every release, because installed copies use it to tell that an update exists.
- **Components**: the portal lists the plugin on each surface that supports what it contains. Claude can't install a plugin with a top-level `bin/`, so the portal lists it for Claude Code only (derived: the portal takes the surfaces from the component table); so are a plugin with only `skills/` and no `plugin.json`, and a mod. The plugin's **Settings** tab can change the surfaces it is listed on. On Claude, dependencies between plugins don't install: each plugin is added on its own.
- **What the scan holds or blocks**: compiled, packed or minified code, a non-image binary, a file over 256 KiB other than images and fonts, more than 512 files, package launchers, lockfile installs and scripts the validator can't follow are held for a reviewer, which delays the release. Everything the plugin runs, sends or fetches must be described in its README.
- **README and license**: every version needs a README of at least 40 words in the plugin folder, not counting code blocks, and a `LICENSE` file or `license` in `plugin.json`; without them the version is blocked and never reaches users.
- **Visibility**: the repository can be private while a version is scanned and reviewed, but publishing and relisting need it public, and the GitHub account connected in the submitting Claude organization must be able to push to it.

**Read in full**:

- https://claude.com/docs/plugins/submit#publish-a-passing-version
- https://claude.com/docs/plugins/submit#submit-from-a-private-repository
- https://claude.com/docs/plugins/submit#connect-your-github-account
- https://claude.com/docs/plugins/pre-submission-checklist#review-what-validation-and-the-scan-check, with all its subsections
- https://claude.com/docs/plugins/pre-submission-checklist#prepare-for-the-security-scan
- https://claude.com/docs/plugins/platform-support#compare-component-support-by-app
- https://claude.com/docs/connectors/building/after-publishing#listing-details

## Update

**When**: the plugin's files changed and listed users should receive them. Listed users receive a published version on their own, with nothing to run.

**Stages**:

1. **Release in the repository**: raise `version` if `plugin.json` sets it, check the change against [How the build changes the procedure](#how-the-build-changes-the-procedure), validate and commit. The portal runs more checks than the command, so a clean run doesn't guarantee a passing scan.
   - Done when: validation passes and the working tree is clean.

   ```bash
   claude plugin validate ./<plugin-folder> --strict
   git status --short
   ```

2. **Notes**, only when the version asks something of users or changes what they get. Send them before the push when users must act first, because with auto-publish the version can go live as soon as it passes; otherwise send them once it is published.
   - Done when: the user has the notes from `assets/migration-notes.md`, or has decided none are needed.
3. **Reach the tracked ref**, with the user's yes:
   - a tracked branch: push the release commit to it;
   - a tracked tag: push a new tag, then in the portal, the plugin's **Settings** tab > **Tracked branch or tag** > the new tag > **Save**. This can't be done while the plugin is with a reviewer, and it cancels a publish request still waiting.
   - Done when: the remote's tracked branch or tag points at the release commit.

   ```bash
   git rev-parse HEAD
   git ls-remote origin <tracked-branch-or-tag>
   ```

4. **Scan**: the directory scans the new commit on a schedule, on push when the GitHub webhook is set up, or when the user selects **Check for new commits** on the plugin's page.
   - Done when: the user reports that the **Versions** tab lists the commit with a result.
5. **Act on the status** the plugin's page shows:
   - **Scanning** or **In review**: wait; nothing is on the user's side.
   - **Needs changes**: fix the cause the page names, then run stages 1, 3 and 4 again. When the **Review** tab shows **Resubmit for review**, the submission was rejected and the directory stopped scanning it: read **Requested changes** there first, and after the push select **Resubmit for review** instead of **Check for new commits**.
   - **Approved**: whoever the card names publishes it; when that is the user, select **Publish**, or **Publish update** when a version is already live.
   - **Published** with a card about a newer version: act on what the card says about that version.
   - Done when: the user reports **Published** for this version.

**Read in full**:

- https://claude.com/docs/plugins/submit#update-a-published-plugin, with its subsection
- https://claude.com/docs/plugins/submit#fix-a-failed-version
- https://claude.com/docs/plugins/submit#publish-a-passing-version
- https://claude.com/docs/connectors/building/after-publishing#plugin-changes
- https://claude.com/docs/directory/submission-status#plugin-bundle-statuses

## Turn off or uninstall

Not the publisher's change here: each user turns a listed plugin off or removes it on their own account, as `references/context-claude-account.md` describes under "Turn off" and "Remove". To stop offering it to everyone, retire it.

## Retire: delist or withdraw

**When**: the plugin should no longer be offered, which is what users mean by deprecate. There is no deprecation state.

**Stages**:

1. **Agree the timing with the user**: once delisted, users who have the plugin stop getting updates and their copy may be removed.
   - Done when: the user confirmed the date.
2. **Announce** it with the retirement notes from `assets/migration-notes.md` before delisting. A last published version can carry the announcement inside the plugin too, such as in its description or a notice in its skills, because a published version still reaches every user who has it (derived from how updates are served).
   - Done when: the user says the notes went out, and the announcing version, if any, is **Published**.
3. **Take it out**, with the user's yes, from the plugin's page in the portal:
   - a live plugin: the menu in the page header, or the **Settings** tab > **Delist plugin**;
   - a submission in review that was never published: **Withdraw submission**, in the page header or on the **Settings** tab;
   - a draft: **Delete draft**.
   - Done when: the user reports the status **Delisted** or **Withdrawn**, or that the draft is gone. While a delist is pending, the menu shows **Delist requested**, and it can take time to reach every Claude app.
4. **Other contexts**: retire the plugin in every other context it lives in, such as the user's own marketplace (`references/context-own-marketplace.md`, "Retire a plugin") or an organization (`references/context-organization.md`, "Turn off for members, or retire"). Leave the repository public and in place: what making it private or deleting it does to copies users still have isn't documented.
   - Done when: each context in the plan has its retirement stage done or marked as waiting on its owner.

**Relist plugin** on the **Settings** tab is a request, not a switch: the directory may send it to a reviewer, and it can be declined. A withdrawn submission reopens when the same repository and path are submitted again, and it still counts toward the 10 submissions per 24 hours.

**Read in full**:

- https://claude.com/docs/plugins/submit#withdraw-or-delist-a-plugin
- https://claude.com/docs/connectors/building/after-publishing#delist-a-connector-or-plugin
- https://claude.com/docs/plugins/submit#submission-limits-and-duplicates

## Relabel

**When**: only the label users see must change. The listing's name and short description follow the live version's `plugin.json` and README.

**Stages**:

1. **Change the label**: set the new `displayName`, or edit `description` or the README. Keep `name`. Pick a label of the user's own, because a label that looks like another plugin, publisher or brand holds the version for a reviewer.
   - Done when: only the label files changed.

   ```bash
   git diff --stat
   ```

2. **Release it** with the stages of [Update](#update).
   - Done when: the version with the new label is **Published**.
3. **Check the listing**: a field an Anthropic reviewer edited during review keeps the reviewer's text. How to replace it isn't documented: when the listing still shows the old text, the user asks Anthropic from the plugin's menu > **Get help** or **Contact Anthropic**.
   - Done when: the user reports that the listing shows the new label.

**Read in full**:

- https://claude.com/docs/connectors/building/after-publishing#listing-details
- https://claude.com/docs/plugins/submit#submit-a-plugin, step 3 (**Check the listing details**)
- https://claude.com/docs/plugins/pre-submission-checklist#manifest-and-plugin-name

## Rename

**When**: `name` itself must change. Propose [Relabel](#relabel) first: it breaks nothing.

What a new `name` does to users who already have the listed plugin isn't documented, and the docs give the directory no `renames` map. Their synced copy loads under its `name`, so a per-machine `"<old>@synced": false` key stops applying to it (derived from how synced plugins are keyed).

**Stages**:

1. **Ask Anthropic before changing `name`**: the user writes from the plugin's menu > **Get help** or **Contact Anthropic**, or to `directory@anthropic.com`, with the listing's name, the organization and the new name.
   - Done when: the user has Anthropic's answer, and decides with it whether to rename, relabel instead, or submit a new plugin and retire this one.
2. **Release the new `name`**, only if the user chose it, with the stages of [Update](#update).
   - Done when: the version with the new name is **Published**.
3. **Notes**: write the rename notes from `assets/migration-notes.md`.
   - Done when: the user has the notes.

**Read in full**:

- https://claude.com/docs/plugins/pre-submission-checklist#manifest-and-plugin-name
- https://claude.com/docs/directory/submission-status#contact-anthropic-about-a-submission
- https://code.claude.com/docs/en/plugins/publish#rename-or-remove-a-plugin
- https://code.claude.com/docs/en/plugins/loading#plugins-synced-from-claudeai

## Merge

**When**: several listed plugins become one. The docs have no procedure for it; these stages are derived from the rules above (each folder is its own listing, a folder can't change, and accounts add each plugin on its own). Tell the user they are derived.

**Stages**:

1. **Choose the surviving listing**: the one whose folder will hold the merged plugin, keeping its `name`.
   - Done when: the user confirmed which listing survives.
2. **Release the merged plugin** in that folder with the stages of [Update](#update).
   - Done when: the merged version is **Published**.
3. **Announce** it to users of the other listings with the notes from `assets/migration-notes.md` ("In the directory or an organization"). Moving options or data between listings isn't documented, so the notes tell users to set the surviving plugin up as new.
   - Done when: the user says the notes went out.
4. **Retire each other listing** with the stages of [Retire: delist or withdraw](#retire-delist-or-withdraw), after the date the user set.
   - Done when: each other listing shows **Delisted**.

**Read in full**:

- https://claude.com/docs/plugins/submit#withdraw-or-delist-a-plugin
- https://claude.com/docs/plugins/submit#change-the-tracked-branch-or-tag

## Split

**When**: one listed plugin becomes several. The docs have no procedure for it; these stages are derived from the same rules. Tell the user they are derived.

**Stages**:

1. **Submit each new folder** as a new submission from the organization that owns the listing. Each one goes through validation, the scan and a reviewer before it goes live. An organization can create up to 10 submissions in 24 hours, drafts and withdrawn submissions included.
   - Done when: each new listing is **Published**.
2. **Announce** the new plugins with the notes from `assets/migration-notes.md` ("In the directory or an organization").
   - Done when: the user says the notes went out.
3. **Slim the original** to what it keeps, and release it with the stages of [Update](#update), only after stage 2, so users have the new plugins before the original loses anything.
   - Done when: the slimmed version is **Published**.

**Read in full**:

- https://claude.com/docs/plugins/submit#submit-a-plugin, with its subsections
- https://claude.com/docs/plugins/submit#submission-limits-and-duplicates
- https://claude.com/docs/plugins/platform-support#compare-component-support-by-app

## Move to another repository, folder or organization

**When**: the plugin's files move to another repository or folder, or another claude.ai organization should own the listing. A listing can't follow a move, so the move is a new submission and a retirement. What a listing does after its repository is renamed or transferred on GitHub isn't documented; ask Anthropic through **Get help** before doing either.

**Stages**:

1. **Submit from the new place**, from the organization that should own the listing long term: the first organization to submit a repository folder holds that listing. When the portal refuses with **Already submitted by another organization** and the user's organization owns the repository, the user writes to `directory@anthropic.com`.
   - Done when: the new listing is **Published**.
2. **Announce** the new listing with the notes from `assets/migration-notes.md` ("In the directory or an organization").
   - Done when: the user says the notes went out.
3. **Retire the old listing** with the stages of [Retire: delist or withdraw](#retire-delist-or-withdraw), after the date the user set.
   - Done when: the old listing shows **Delisted**.

**Read in full**:

- https://claude.com/docs/plugins/submit#change-the-tracked-branch-or-tag
- https://claude.com/docs/plugins/submit#submission-limits-and-duplicates
- https://claude.com/docs/directory/publish#confirm-you-can-submit-to-the-directory
- https://claude.com/docs/directory/publish#what-a-listing-gets-you

## Verify

1. The plugin's page in the portal shows the expected status for the expected version, and later its **Usage** tab > **Versions** shows accounts moving to it. The figures are computed once a day in UTC.
2. In Claude, **Customize > Plugins** > **Discover** shows the listing with the new label, or no longer shows it. On Team and Enterprise, an Owner can remove the directory as a source, so check from an account whose organization keeps it.
3. In Claude Code, signed in with a claude.ai account that has the plugin, after a new start the object whose `id` is `<name>@synced` shows the manifest's `version` (`unknown` when it sets none) and `enabled`, or no object has that `id`:

   ```bash
   claude plugin list --json
   ```

**Read in full**:

- https://claude.com/docs/connectors/building/after-publishing#track-published-plugin-usage
- https://code.claude.com/docs/en/plugins/cli-reference#plugin-list
- https://claude.com/docs/plugins/platform-support#compare-installation-sync-and-admin-controls
- https://code.claude.com/docs/en/plugins/publish#how-a-listed-plugin-reaches-claude-code-users
