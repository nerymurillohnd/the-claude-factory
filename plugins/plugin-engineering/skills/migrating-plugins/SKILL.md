---
name: migrating-plugins
description: Plans, carries out and verifies changes to plugins and marketplaces that people already have installed, or resumes one already under way - renames, relabels, merges, splits, moves, updates that must reach users, retirements, deprecations, delistings, uninstalls and removals, on a machine, a Claude account (name@synced), a public, private, URL or local marketplace, Anthropic's directory, a claude.ai organization or managed settings. Use when the user wants to rename, merge, split, move, consolidate, retire, deprecate, delist, remove or uninstall a plugin or marketplace without breaking installs; when a new version doesn't reach users or update says it is already at the latest version; when a plugin won't go away; or when a change was started and must be finished. Use it even when the user only pastes a message such as not found in marketplace. Not for setting up a marketplace or releasing a new plugin (public-marketplace-dev) or for one that fails to load (plugin-testing-and-debugging).
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          if: Bash(claude plugin *)
          command: bash "${CLAUDE_PLUGIN_ROOT}/skills/migrating-plugins/scripts/ask-before-destructive.sh"
          onFailure: block
        - type: command
          if: Bash(claude plugins *)
          command: bash "${CLAUDE_PLUGIN_ROOT}/skills/migrating-plugins/scripts/ask-before-destructive.sh"
          onFailure: block
        - type: command
          if: Bash(rm *)
          command: bash "${CLAUDE_PLUGIN_ROOT}/skills/migrating-plugins/scripts/ask-before-destructive.sh"
          onFailure: block
        - type: command
          if: Bash(rmdir *)
          command: bash "${CLAUDE_PLUGIN_ROOT}/skills/migrating-plugins/scripts/ask-before-destructive.sh"
          onFailure: block
        - type: command
          if: Bash(unlink *)
          command: bash "${CLAUDE_PLUGIN_ROOT}/skills/migrating-plugins/scripts/ask-before-destructive.sh"
          onFailure: block
        - type: command
          if: Bash(git rm *)
          command: bash "${CLAUDE_PLUGIN_ROOT}/skills/migrating-plugins/scripts/ask-before-destructive.sh"
          onFailure: block
        - type: command
          if: Bash(find *)
          command: bash "${CLAUDE_PLUGIN_ROOT}/skills/migrating-plugins/scripts/ask-before-destructive.sh"
          onFailure: block
    - matcher: Edit|Write
      hooks:
        - type: command
          if: Edit(**/marketplace.json)
          command: bash "${CLAUDE_PLUGIN_ROOT}/skills/migrating-plugins/scripts/ask-before-destructive.sh"
          onFailure: block
        - type: command
          if: Write(**/marketplace.json)
          command: bash "${CLAUDE_PLUGIN_ROOT}/skills/migrating-plugins/scripts/ask-before-destructive.sh"
          onFailure: block
---

# Migrating Claude Code plugins: rename, update, merge, split, retire and remove

A change to a plugin reaches users through rules they never see: the computed version, the `renames` map, auto-update, scopes, account sync, directory review and organization availability. Those rules differ by context, and one plugin often lives in several contexts at once. This skill teaches the whole job: orient yourself, decide whether the requested change is the right one, learn each context from its official sections, then plan, run and verify the change from start to finish, or from wherever someone else left it.

The failures it exists to prevent: a rename that strands every install, a release that never reaches users, a removal that deletes users' options and data without warning, a context nobody remembered (a directory listing, an organization, managed settings), and a change reported as done after a check on one machine or one surface.

## Scope

- **This skill**: deciding, planning and carrying out updates, removals, retirements, renames, merges, splits and moves of plugins and marketplaces, and finding why a change didn't reach users.
- **`plugin-engineering:cli-commands-guide`**: every flag, message, JSON field and exit code of a command. Load it with this skill.
- **`plugin-engineering:plugin-testing-and-debugging`**: a plugin that fails to install, load or run for reasons other than an update, rename or removal.
- **Not covered**: creating a plugin from nothing and writing its components, except the target plugin of a merge or a split.

Facts come from the official docs at code.claude.com, claude.com/docs and support.claude.com. **(observed)** marks behavior seen on the Claude Code binary but not written in the docs, and **(changelog)** behavior only the changelog states. A version in the text is the one where a behavior started: compare it with the version that will run the change.

## Workflow

Copy this checklist into your task list. Tick each step only with its evidence.

- [ ] 1. Orient yourself: answer the orientation questions.
- [ ] 2. Decide whether the requested change is the right one.
- [ ] 3. Clarify with the user what is still open.
- [ ] 4. Learn the case from the official docs.
- [ ] 5. Plan every stage, and find where the work stands.
- [ ] 6. Run the stages from that point to the end.
- [ ] 7. Verify the result in every context and on every surface.
- [ ] 8. Report.

## Gotchas

These hold in every context. Each context reference adds its own.

- A plugin's `name` is its identity: the key in `enabledPlugins` and `pluginConfigs`, and the `name@marketplace` users type. Changing it breaks every install that isn't migrated. When only the label must change, change `displayName`.
- Users get a new copy only when the computed version changes, so pushing commits while `plugin.json` pins `version` releases nothing. How the version is computed, and the plugins that update by other rules (loaded in place, `command` sources, marketplaces from claude.ai), are in "How Claude Code decides there is an update" in `references/context-machine.md`.
- One plugin often lives in several contexts: a public marketplace that is also listed in Anthropic's directory, a repository that an organization syncs and that managed settings also enable. Each context reaches users by its own route, on its own schedule, and needs its own stage in the plan.
- A Claude account and a Claude Code machine are managed apart. A plugin added on the account reaches Claude Code only as `<name>@synced`, a `claude plugin` command never changes the account, and a plugin installed from the command line isn't added to the account.
- A running session keeps the version it loaded. `/reload-plugins` is a session command you can't run from Bash: after any update or removal, ask the user to run it in the open session, or to start a new one.
- The docs change every few days and this skill can fall behind. When a section you read disagrees with this skill, follow the section and tell the user which part of the skill is out of date. When a behavior isn't documented anywhere, say so; never fill the gap with a guess.

## Stop and confirm

These actions destroy a plugin, its data or a marketplace, or reach every user, so the decision is the user's. Before each one, say what it will do and wait for an explicit yes:

- `claude plugin uninstall` from the last scope, `claude plugin prune` without `--dry-run`, `claude plugin restore-set-aside --discard` **(observed)**, and `claude plugin marketplace remove`, because each deletes options, secrets or data;
- deleting a plugin's folder, its `.claude-plugin/` manifest, `marketplace.json`, or anything under `~/.claude/plugins/`, because Claude Code keeps installs, options and data there;
- `"forceRemoveDeletedPlugins": true`, a `null` rename, or removing an entry from `plugins`, because they change every user's machine at their next catalog refresh;
- in Claude and claude.ai: **Remove** on an account's plugin, or removing users from its **Share** list, which stops it loading for them; **Delist plugin**, **Withdraw submission** or **Delete draft** in the developer portal; and in Organization settings **Delete source**, **Remove from organization**, deleting a plugin from the Inventory tab, or availability set to **Not available**;
- pushing, tagging with `--push`, publishing in the developer portal, re-syncing an organization, or delivering changed managed settings, because from there the change reaches every user.

Urgency, a deadline or a general "just do it" doesn't stand in for that yes: these actions run on other people's machines and accounts, where you can't take them back. Name each action and its target, ask once, and wait. A yes covers the action it named, not the rest of the list.

While this skill is active, its `PreToolUse` hook backs this list up. It asks the user before the plugin CLI removals above (also through the `claude plugins` alias), before `rm`, `rmdir`, `unlink`, `git rm` or `find -delete` on plugin, marketplace or `~/.claude/plugins/` paths, and before a `marketplace.json` edit that touches `forceRemoveDeletedPlugins` or maps a plugin to `null`. It leaves every other command alone, pushes included. It can't see `/plugin`, claude.ai, the developer portal or `marketplace.json` edits made through `Bash`, and before Claude Code 2.1.295 a hook that fails to run lets the action through. Ask first anyway: the hook is a safety net, not the rule.

## When a step fails

The goal of every step is its result (an answer found, a section read in full, a stage done), not the command that was planned.

1. Keep the exact message and exit code.
2. Look the message up in `references/diagnose-changes.md`, then in `plugin-engineering:plugin-testing-and-debugging` if it isn't there.
3. Read the official section the entry links, then apply its fix once. Changing things and rerunning to see what happens hides the cause and leaves its other effects in place.
4. When a source or a tool fails (a download, `search_claude_code_docs` or `query_docs_filesystem_claude_code_docs`, a command), don't stop there: name the cause and reach the same result another way, the other form of the page, the other docs site, the docs MCP or the command's other form, in the order "When a route fails" in `references/reading-docs.md` gives. Repeat a failing command at most once, and only after a timeout. Report a gap only after every route has failed.
5. If nothing explains it, stop and report the command, the message, the exit code and what you checked.

## Step 1: Orient yourself

Answer each question in order, from what you can read before you change anything. Write the answers down: they become the first part of the plan and of the report.

**A. The project and the request**

1. **What is this project?** Read the README, `CLAUDE.md`, `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json`, and list the remotes:

   ```bash
   git remote -v
   ```

2. **Where does this session run, and on which version?** A cloud session sets `CLAUDE_CODE_REMOTE` to `true`. There, and in task work in Claude, commands change that session's environment, not the user's computer or account. For a fleet, the version that matters is the oldest one among its users.

   ```bash
   printenv CLAUDE_CODE_REMOTE
   claude --version
   ```

3. **What exactly is the user asking for?** Name the kind of change in the user's words, then match it to one kind:
   - **update**: users move to a newer version and the plugin keeps its name;
   - **turn off**: it stays installed with its options and data;
   - **uninstall or remove**: it leaves one machine or one account;
   - **retire** (also deprecate, sunset, shut down, delist): the publisher stops offering it to everyone; no context has a deprecation state;
   - **relabel**: only the name users see changes;
   - **rename**: the identity changes and every install has to migrate;
   - **merge** (also consolidate, fold into): several plugins become one; **split**: one becomes several;
   - **move**: to another marketplace, repository, host, folder or organization.
4. **Does the plugin exist?** If it doesn't, creating it is outside this skill, except as the target of a merge or a split.

**B. Where the plugin lives.** Check every signal: more than one usually applies, and each one that applies loads its reference. A directory listing, an organization that distributes the plugin, managed settings on other machines, and users who added the marketplace in Claude show in no file: only the user, an Owner or an admin knows them. Mark each of questions 7 to 10 that the files and this machine don't settle as unknown, and ask about it in Step 3.

5. **On a machine**: the list shows it as `name@marketplace` (a `claudeai-` marketplace included), `@inline`, `@skills-dir`, built-in or a mod. Load `references/context-machine.md`.

   ```bash
   claude plugin list --json
   ```

6. **On a Claude account**: it was added from **Customize > Plugins** in Claude, and Claude Code shows it as `<name>@synced`. Load `references/context-claude-account.md`. A `<plugin>@claudeai-<marketplace>` id is a machine install from a marketplace hosted on claude.ai (question 5); its source changes on the account or in the organization, so also load `references/context-claude-account.md` for the user's own uploads, or `references/context-organization.md` for the organization's library.
7. **In a marketplace the user maintains**: the user owns a `marketplace.json`. Note how it is hosted, from the remote and the add command users run: a public git repository, a private one, a `marketplace.json` URL or a local path. Note too whether users may have added it in Claude, which no file shows. Load `references/context-own-marketplace.md`.
8. **In Anthropic's directory**: it has a listing managed in the developer portal at claude.ai/directory/manage. The Claude Marketplace website (claude.com/marketplace) has no submission of its own: publishers submit to the directory. Load `references/context-directory.md`.
9. **In a claude.ai organization**: an Owner distributes it from **Organization settings > Plugins & skills**, from a synced repository, an upload, a member's published plugin or one of Anthropic's catalogs. Load `references/context-organization.md`.
10. **In managed settings**: managed `extraKnownMarketplaces` or `enabledPlugins` name it, and `/plugin` shows it at Managed scope. Load `references/context-managed-settings.md`.

**C. How the plugin is built and configured.** Each answer changes a stage, so read them from the files:

11. **Its components**: skills, agents, commands, hooks, a hooks module, MCP and LSP servers, a top-level `bin/`. They decide which surfaces load it, and what Claude refuses.
12. **Its source in the marketplace entry**: relative path, `github`, `url`, `git-subdir`, `archive`, `npm` or `command`. It decides how a release reaches users.
13. **How it is versioned**: `version` in `plugin.json`, in the entry, in both (a defect: `plugin.json` wins at install, and `claude plugin validate` only warns), or nowhere (the commit SHA). Also whether it has `<name>--v<version>` tags, whether other plugins depend on it with a version range, and whether it declares `engines`.
14. **Its options and data**: `userConfig` keys, and whether it keeps data under `~/.claude/plugins/data/<id>/`. They decide what a rename, merge or removal can lose.
15. **How this repository works**: its release process (tags, CHANGELOG, labels, CI), and any `renames` map or `forceRemoveDeletedPlugins` already there. Compare each practice with the docs you read in Step 4, and list every difference.

**D. The state of the change**

16. **What has already been done?** Step 5 checks it stage by stage. Note here what the user, the git history or the files already show.

## Step 2: Decide whether it is the right change

Match the request to the change that reaches the user's goal with the least loss. When a better one exists, propose it with the reason before going on.

- **Relabel before rename**: rename only when `name` itself must change (a conflict, a policy, a merge). For a new label, `displayName` breaks nothing.
- **Turn off before uninstall**: off keeps options and data and is reversible; uninstall from the last scope deletes them.
- **Retire instead of deleting the entry**: in a marketplace, a retirement maps the name to `null` so installs end cleanly; removing the entry alone leaves broken installs behind.
- **Merge, or bundle**: when users should get several plugins together but each stays useful alone, a plugin that depends on them installs them all without a merge. Only Claude Code supports dependencies between plugins, so a bundle doesn't help users in Claude. Merge when the plugins only make sense as one.
- **Split** a plugin whose users each need only part of it, so each installs what they need.
- **Update**: pick the versioning model the plugin already uses, unless it is broken; changing the model is a decision for the user.

## Step 3: Clarify

1. Judge whether you can plan without guessing: the goal, the audience, the contexts, and what may be lost are clear from the request and Step 1. A context marked unknown in Step 1, part B, is not clear. If everything is clear, go on without asking. Never ask what the files, a command or the docs can answer: find it first.
2. Otherwise, ask with `AskUserQuestion`, one to four questions, before changing anything. Where it isn't available, ask in your reply and stop.
3. Ask about the user's goal, not about mechanics: not "should I use a `null` rename?", but "should users who have the plugin keep its data after it is retired?".
4. Always ask about anything in "Stop and confirm", every context still unknown from Step 1, part B, the timing of a retirement, and who may lose data.

## Step 4: Learn the case

Learn each context from its current docs, because the rules change between releases.

1. Read `references/reading-docs.md` once: it shows how to find a page, download it and read whole sections.
2. In each loaded context reference, read its gotchas and the entry for this kind of change, then every official section it lists under **Read in full**, from top to bottom.
3. Follow the links inside those sections that touch the change, and read the troubleshooting entries they name: those messages are what users will see.
4. Look up what the reference doesn't cover: search both docs indexes (`llms.txt`), `search_claude_code_docs` (find it with ToolSearch, query `claude_code_docs`), and the help center, as `references/reading-docs.md` shows.
5. Check the changelog for every field and command the plan relies on, against the version from Step 1.
6. For each difference you listed in Step 1, question 15, apply the documented practice in what this change touches, and tell the user what you found and why. When correcting a practice would itself change what users receive (switching the versioning model, removing a duplicated `version`), present it and wait for the user's yes. Report differences the change doesn't touch without fixing them.

## Step 5: Plan, and find where the work stands

1. List the stages of this kind of change in every loaded context, in the order each context reference gives them.
2. Merge the contexts into one sequence by these rules, derived from the context references, so users keep working at every point:
   - notes that ask users to act before the change reaches them (announce a retirement, export data) come before the stage that ships it (push, tag, publish, sync, delivered managed settings); notes for what users do once it arrives (install the new name once, set options again) come after that stage, where each context reference puts them;
   - a stage that depends on another context's result comes after it: managed `enabledPlugins` keys change after the `renames` entry ships, and a new marketplace, listing or repository serves before the old one is retired;
   - cleanup (`forceRemoveDeletedPlugins`, deleting a source or an old marketplace) comes last, after the date the user set.
3. For each stage, write its owner (you, the user, an admin, Anthropic's review, each user) and its **Done when** check.
4. Run the checks in order. The first stage whose check fails is where the work stands; earlier stages that pass are done, even if someone else did them. Record the evidence for each.
5. Present the plan: the answers from Step 1, the decision from Step 2, each stage with its owner and status, the stages that need the user's yes, and what users will see.
6. Wait for the user's yes on the plan when it includes any action in "Stop and confirm".

## Step 6: Run the stages

1. Start at the first stage that isn't done.
2. Run one stage, then run its **Done when** check before the next. A stage isn't done until its check passes.
3. Stop before every action in "Stop and confirm" and ask.
4. For a stage someone else owns, write the exact message or steps to send them, and mark the stage as waiting on them.
5. For each notes stage, write the notes from `assets/migration-notes.md`. Notes are needed only when the change asks something of users or changes what they get; a change that only the user's own machine or account sees needs none.

## Step 7: Verify end to end

1. Run each context's **Verify** section, and show the raw output.
2. Check each surface the plugin is served on: what each one loads, and that nothing in the change makes Claude refuse the plugin there. The rules are in "How the build changes the procedure" in `references/context-claude-account.md`, and for a listing in the same section of `references/context-directory.md`.
3. Confirm that every stage's check passes, or is marked as waiting on its owner.

## Step 8: Report

- The answers from Step 1, and the decision from Step 2 with its reason.
- Each context: the stages already done before you started, the stages you ran, and the stages waiting on someone else, with the message for each.
- What differs from the documented practice, and what you changed or left.
- The official sections read, and the changelog range checked against the version in use.
- Each verification with its output.
- What couldn't be verified, and every **(observed)** or **(changelog)** fact the plan relied on.

Keep each claim's evidence visible: what you saw in a command's output or read in an official section during this task, what you inferred from it, and what you assumed. A stage you planned but didn't check is not done, and a command that ran is not proof it worked until its **Done when** check passes.

## References

- `references/reading-docs.md`: find, download and read official sections in full, follow their links, check the changelog, and the routes to try when one fails. Read it in Step 4, before the first docs read.
- `references/context-machine.md`: a plugin installed on a machine, by origin and surface.
- `references/context-claude-account.md`: a plugin on a Claude account, and its synced copy in Claude Code.
- `references/context-own-marketplace.md`: a marketplace the user maintains, with every kind of change and each way to host it.
- `references/context-directory.md`: a listing in Anthropic's directory.
- `references/context-organization.md`: a plugin a claude.ai organization distributes.
- `references/context-managed-settings.md`: a plugin or marketplace managed settings deliver to a fleet.
- `references/diagnose-changes.md`: messages and symptoms after a change, with cause, fix and the section to read.
- `assets/migration-notes.md`: the notes for users who have the plugin, with an example.
- `scripts/ask-before-destructive.sh`: the hook this skill registers. Don't run it by hand.
