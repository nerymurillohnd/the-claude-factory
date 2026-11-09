# Settings files and precedence

> Covers how to change Claude Code settings, pick the scope a key belongs in, verify the change, and determine which value Claude Code uses when a key is set in several places.

## Contents

- [Settings files and who they affect](#settings-files-and-who-they-affect)
  - [Compare the scope of each settings file](#compare-the-scope-of-each-settings-file)
  - [Find or create your settings files](#find-or-create-your-settings-files)
  - [Share settings with your team](#share-settings-with-your-team)
  - [Keep personal settings out of a repository](#keep-personal-settings-out-of-a-repository)
    - [Where Claude Code keeps the local file in a git repository](#where-claude-code-keeps-the-local-file-in-a-git-repository)
  - [Check what your organization enforces](#check-what-your-organization-enforces)
- [Change a setting](#change-a-setting)
  - [Edit a settings file](#edit-a-settings-file)
  - [Change a setting for one session](#change-a-setting-for-one-session)
  - [When edits take effect](#when-edits-take-effect)
  - [Confirm what loaded](#confirm-what-loaded)
  - [Fix a broken settings file](#fix-a-broken-settings-file)
- [Settings precedence](#settings-precedence)
  - [Lists merge instead of overriding](#lists-merge-instead-of-overriding)
  - [Precedence examples](#precedence-examples)
    - [Team settings override personal settings](#team-settings-override-personal-settings)
    - [The command line overrides your files for one session](#the-command-line-overrides-your-files-for-one-session)
  - [Troubleshoot a setting that doesn't apply](#troubleshoot-a-setting-that-doesnt-apply)
    - [A value you set is ignored](#a-value-you-set-is-ignored)
    - [A change you made in Claude Code is lost in new sessions](#a-change-you-made-in-claude-code-is-lost-in-new-sessions)
    - [A committed key doesn't reach teammates](#a-committed-key-doesnt-reach-teammates)
- [Settings in cloud sessions](#settings-in-cloud-sessions)
- [Documentation References](#documentation-references)

Settings are the JSON keys that change how Claude Code behaves: which model it starts with, what it can run without asking, which files it can't read, how it looks in the terminal, and what an organization enforces.

> **Tip:** To look up a specific key, read [All settings](https://code.claude.com/docs/en/settings-reference.md), which lists every key with the file it is set in, its default, and an example.

Claude Code reads settings from JSON settings files such as `~/.claude/settings.json`. It looks for them in a few locations, and [the file it reads a setting from decides who the setting applies to](#settings-files-and-who-they-affect). This file covers which settings file to put a setting in, how to change a setting and confirm it applied, and which value Claude Code uses when the same key is set in more than one file. [Configure permissions](https://code.claude.com/docs/en/permissions.md) covers what Claude Code can run without asking and how to write `allow`, `ask`, and `deny` rules.

> **Note:** This file covers Claude Code running on the user's machine: the terminal, the [VS Code](https://code.claude.com/docs/en/vs-code.md) and [JetBrains](https://code.claude.com/docs/en/jetbrains.md) extensions, and the [desktop app](https://code.claude.com/docs/en/desktop.md), which all read the same settings files. A [cloud session](https://code.claude.com/docs/en/claude-code-on-the-web.md) runs on a different machine and reads only some of them; see [Settings in cloud sessions](#settings-in-cloud-sessions).

## Settings files and who they affect

Claude Code reads settings from four files, and an organization can also deliver managed settings from the claude.ai console. Each source has a scope: the set of people and projects a setting saved in it applies to, whether that is one user, everyone in a project, or everyone in an organization.

| Scope | File | Who it affects | Use it for |
| :- | :- | :- | :- |
| User | `~/.claude/settings.json` | You, in every project on this machine | Personal preferences: theme, editor mode, default model, your own permission rules |
| Shared project | `.claude/settings.json` | Everyone working in the folder that contains it. In a git repository, commit it so teammates get it | Team permissions, hooks, plugins, and the environment variables the project needs |
| Project local | `.claude/settings.local.json` | You, in this one project only. Claude Code keeps it out of git when it creates the file; if you create it by hand, add it to `.gitignore` yourself | Personal overrides for one project, and testing before you share |
| Managed | `managed-settings.json` and other [managed sources](https://code.claude.com/docs/en/managed-settings.md#delivery-mechanisms) | Everyone your organization deploys it to; [Settings precedence](#settings-precedence) says what can override it | Security policy and compliance requirements |

In the File column, `~/.claude` is the `.claude` folder in the home directory, and a bare `.claude` is the `.claude` folder inside the project.

### Compare the scope of each settings file

Consider a user with three projects on one machine, `website/`, `api/`, and `acme-app/`, a teammate with their own clone of `acme-app/`, and a [cloud session](#settings-in-cloud-sessions) started on `acme-app/`.

The original page shows an interactive graphic of which of those folders a setting applies in when Claude Code starts from them; clicking a settings file shows the folders it reaches. Its labels are: Settings file; Your machine; A teammate’s machine; A cloud session. What each file reaches:

* **`~/.claude/settings.json`**: every project on the user's machine, and nothing on the teammate's machine or in the cloud session
* **`acme-app/.claude/settings.json`**: the user's `acme-app/`. It reaches the teammate's clone and the cloud session only if the file is committed to version control; until then, it is a file on the user's disk like any other and nobody else has it
* **`acme-app/.claude/settings.local.json`**: the user's `acme-app/` only. Claude Code adds it to the global git excludes the first time it writes the file, so it stays out of commits; if the file is created by hand, [add it to `.gitignore` manually](#keep-personal-settings-out-of-a-repository)
* **Managed settings**, whether a `managed-settings.json` file, an MDM policy, or [server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md) from the claude.ai console: every project on every machine the organization deploys it to, or that a user signs in to with the organization account. Only server-managed settings reach the cloud session

### Find or create your settings files

Installing Claude Code doesn't create any settings file. A settings file that already exists on a machine or in a project came from one of these sources:

* **Managed**: the organization deploys it. Users don't create or edit it.
* **Shared project**: a project that already uses Claude Code may have one committed. If not, create it at `.claude/settings.json` in the project folder.
* **User** and **Project local**: create them manually, or let Claude Code create them. Claude Code writes `~/.claude/settings.json` the first time the user changes an option in the `/config` menu that it stores in user settings, such as the theme, and `.claude/settings.local.json` the first time the user gives a standing approval on a permission prompt, such as "Yes, and don't ask again" for a Bash command. A few `/config` options, including **Show tips**, save to `.claude/settings.local.json` instead of the user file.

> **Note:** On Windows, `~/.claude` means `%USERPROFILE%\.claude`. To keep the home-directory files somewhere else, set [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars); Claude Code then stores settings, session history, and plugins there instead.

Claude Code also keeps a fifth file, [`~/.claude.json`](https://code.claude.com/docs/en/claude-directory#ce-claude-json), that it writes for itself; it needs no manual editing. It holds account details, [MCP server](https://code.claude.com/docs/en/mcp.md) configurations, per-project state such as trust decisions, and the [global config keys](https://code.claude.com/docs/en/settings-reference.md#global-config-settings) that `/config` writes.

### Share settings with your team

Commit `.claude/settings.json` so everyone who clones the repository gets the same permissions, hooks, and plugins. Each teammate can still override it in their own `.claude/settings.local.json`, so personal exceptions don't need a commit. For a complete team file, see [a team's shared settings](https://code.claude.com/docs/en/settings-example.md#a-teams-shared-settings).

Some committed settings wait until each teammate [trusts the folder](https://code.claude.com/docs/en/permissions.md#project-allow-rules-and-workspace-trust), and a few keys never take effect from a repository file; [Troubleshoot a setting that doesn't apply](#troubleshoot-a-setting-that-doesnt-apply) covers both.

### Keep personal settings out of a repository

To change a setting for one user in one project without changing it for teammates, save it in `.claude/settings.local.json` inside the project. Claude Code applies that file over the committed `.claude/settings.json`. For example, if the team's file sets `"model": "claude-sonnet-5"` and the user wants Opus, put `"model": "claude-opus-5-5"` in the local file and only that user's sessions change.

Claude Code also writes to this file, keeps it out of commits, and applies its allow rules without the trust step:

* **Claude Code writes it too.** When Claude asks permission to run a Bash command and the user chooses "Yes, and don't ask again", Claude Code saves that [permission approval](https://code.claude.com/docs/en/permissions.md#permission-system) here as an `allow` rule.
* **No manual gitignore is needed, unless the file was created by hand.** The first time Claude Code writes the file in a git repository that doesn't already ignore it, it adds `**/.claude/settings.local.json` to the global git excludes file, so the file stays out of commits in every repository. That excludes file is `core.excludesFile` when the global git config sets it to an absolute or `~`-prefixed path; otherwise it is `$XDG_CONFIG_HOME/git/ignore`, or `~/.config/git/ignore` when `XDG_CONFIG_HOME` is unset. If the file was created by hand and Claude Code hasn't written to it yet, add it to `.gitignore` manually.
* **Its allow rules don't wait for trust while the file stays untracked.** Because the file belongs to the user and not the repository, Claude Code applies its `allow` rules without the [workspace trust](https://code.claude.com/docs/en/permissions.md#project-allow-rules-and-workspace-trust) step it requires for the committed file. If git tracks the file, the trust step applies to it too; see [When your local settings file needs trust](https://code.claude.com/docs/en/permissions.md#when-your-local-settings-file-needs-trust).

#### Where Claude Code keeps the local file in a git repository

When Claude asks permission to run a Bash command and the user chooses "Yes, and don't ask again", Claude Code saves that approval as an `allow` rule in `.claude/settings.local.json`. When Claude Code starts in a subdirectory of a git repository, it reads and writes that file at the repository root and applies the approval across the whole repository. In a [worktree](https://code.claude.com/docs/en/worktrees.md), it uses the file at the main checkout's root.

Two rules qualify the root location:

* **When the file stays with `.claude/settings.json` instead**: outside a git repository, when the repository root is the home directory, on Windows, or when the repository root or its `.git` or `.claude` entry isn't owned by the current user.
* **Paths in the file don't anchor at the repository root**: a permission rule that starts with `/` or a relative sandbox path [anchors at the session's primary working directory](https://code.claude.com/docs/en/permissions.md#read-and-edit) instead.

Claude Code reads the shared `.claude/settings.json` from the session's [primary working directory](https://code.claude.com/docs/en/permissions.md#working-directories), so to use a file committed at the repository root, start Claude Code there. After the session [moves with `/cd`](https://code.claude.com/docs/en/permissions#move-the-session-to-another-directory), Claude Code reads both project files from the new directory instead, placing the local file by the same rules. Reading them from the new directory requires Claude Code v2.1.246 or later. For a worktree session started from the desktop app, see [What worktrees share with the main checkout](https://code.claude.com/docs/en/worktrees.md#what-worktrees-share-with-the-main-checkout).

### Check what your organization enforces

When an organization manages Claude Code, some settings are decided by the organization and nothing in the user's own files changes them. To see which, run `/status`: the `Setting sources` line names the managed source that applies. Managed settings apply wherever Claude Code runs on the machine; [What a developer can change](https://code.claude.com/docs/en/managed-settings.md#what-a-developer-can-change) covers local admin rights and tools other than Claude Code.

## Change a setting

Change a setting from the `/config` menu, by editing a settings file, or for one session from the command line.

### Edit a settings file

Open the settings file for the target scope in an editor and add or change a key. Settings files are strict JSON: a `//` comment or a trailing comma is a syntax error, and Claude Code reports the file as a [Settings Error](#fix-a-broken-settings-file) at the next start. For example, to let Claude Code run the lint and test commands without asking and stop it reading `.env` files, add this to `~/.claude/settings.json`:

```json ~/.claude/settings.json theme={null}
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

Each entry under `permissions` is a rule that names a tool and what it may do; [Configure permissions](https://code.claude.com/docs/en/permissions.md) explains the syntax. The `$schema` line points to the [published JSON schema](https://json.schemastore.org/claude-code-settings.json) for Claude Code settings, which provides autocomplete and inline validation in VS Code, Cursor, and any other editor that supports JSON schema. The schema can lag behind the newest CLI releases, so a validation warning on a recently documented key doesn't mean the configuration is invalid.

After saving, run `/status` inside Claude Code to confirm the file loaded; [Confirm what loaded](#confirm-what-loaded) says what the `Setting sources` line shows and how a broken file is reported.

For a complete personal file, team file, and organization file, each shown with a comment on every key it sets, see the [example settings files](https://code.claude.com/docs/en/settings-example.md).

### Change a setting for one session

To try a value without saving it, set it when starting Claude Code. The value applies to that session and the settings files stay as they were. There are three ways:

* **`--settings`**: pass a key as JSON, inline or as a path to a file. Claude Code applies it above the user, project, and local files and below managed settings. It can set any key the user settings file can set; it can't set `Managed` or `Global config` keys.
* **A flag for that key**: some keys have their own flag, such as `--model` for `model` and `--effort` for `effortLevel` and `modelSettings`.
* **An environment variable**: export the key's paired variable before running `claude`, such as `ANTHROPIC_MODEL` for `model`.

Each key's entry on the [settings reference](https://code.claude.com/docs/en/settings-reference.md) lists its per-session overrides and which one takes precedence; check the entry for the key being changed.

### When edits take effect

Claude Code watches the settings files and reloads them when they change, so it applies most edits to the running session without a restart, including edits to `permissions`, `hooks`, and credential helpers such as `apiKeyHelper`. Claude Code also loads a settings file created mid-session if its folder existed when the session started. For the project's `.claude/` folder, it loads the file even when the folder is created in the same session.

The reload covers user, project, local, and managed settings. Claude Code runs the [`ConfigChange` hook](https://code.claude.com/docs/en/hooks#configchange) for each settings-file change it detects, but not for managed settings that arrive from MDM or the claude.ai console. Managed settings that arrive through MDM or from the claude.ai console reach a running session on a schedule rather than on save; the [delivery table](https://code.claude.com/docs/en/managed-settings.md#choose-a-delivery-mechanism) gives the schedule per source.

### Confirm what loaded

Run `/status` inside Claude Code to see which settings sources are active. The **Status** tab includes a `Setting sources` line that lists each settings file Claude Code loaded for the current session, such as `User settings` or `Project local settings`. When [managed settings](https://code.claude.com/docs/en/admin-setup.md#decide-how-settings-reach-devices) are in effect, the managed settings entry shows in parentheses how they reached the machine.

The line confirms which files Claude Code read; it doesn't show which file supplied each key. To list entries Claude Code rejected, run [`claude doctor`](https://code.claude.com/docs/en/debug-your-config); for a model that project or managed settings set, the startup header names the file that set it. `/status` and `/config` open the same dialog on different tabs, and the **Config** tab isn't a view of the `settings.json` contents.

### Fix a broken settings file

When JSON is mistyped or a key is set to a value Claude Code doesn't accept, Claude Code reports it at the start of an interactive session. What it shows depends on how much of the file is affected:

* **Settings Error**: a user, project, or local file has invalid JSON or a value the schema rejects. At the start of an interactive session Claude Code shows a dialog that offers to fix the file with Claude's help, exit, or continue without the broken settings.
* **Settings Warning**: only individual entries fail, such as a malformed permission rule or an unknown hook event name. Claude Code skips those values and keeps the rest of the file in effect.
* **Configuration error**: [`~/.claude.json`](https://code.claude.com/docs/en/claude-directory#ce-claude-json) can't be parsed. A `claude -p` run exits, and the file is unchanged. See [Configuration error in \~/.claude.json](https://code.claude.com/docs/en/errors.md#configuration-error-in-claude-json) to restore an earlier copy. Claude Code copies the broken file to `~/.claude/backups/.claude.json.corrupted.<timestamp>`, and in an interactive session asks whether to exit and fix it or reset to the default configuration. When the file is blank and there's no backup to restore, Claude Code starts with default settings.

After continuing, run `/status` to see the affected files and `claude doctor` for the details of each error.

A `-p` run shows no dialog. Unless [a managed settings document can't be parsed](https://code.claude.com/docs/en/errors.md#managed-settings-document-could-not-be-parsed), Claude Code skips a broken user, project, or local file or its broken values and continues with the rest. After a `-p` run that ignores a setting, run `claude doctor` from the terminal to see what it dropped.

## Settings precedence

When the same key appears in more than one place, Claude Code uses the value from the highest level that sets it. A key at a higher level overrides the same key anywhere below it.

The original page shows this as a stack diagram: "Settings precedence, highest first: managed settings, command line, project local, shared project, user. A key set at a higher level overrides the same key set lower down."

In order, highest precedence first:

1. **Managed settings**: settings the organization deploys, by a `managed-settings.json` file, an MDM policy, or [server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md) from the claude.ai console. Nothing in the user's own settings files or `--settings` overrides a managed key, and a flag such as `--model` picks only from the models the organization allows. A managed [`model`](https://code.claude.com/docs/en/settings-reference#model) is a starting default, not a lock; the locks are [`availableModels`](https://code.claude.com/docs/en/settings-reference#availablemodels) and [`deniedModels`](https://code.claude.com/docs/en/settings-reference#deniedmodels). When the organization delivers more than one managed source, the rules for [precedence within the managed tier](https://code.claude.com/docs/en/managed-settings.md#precedence-within-the-managed-tier) say what Claude Code reads from each.
2. **Command line**: JSON passed with `--settings <file-or-json>` when starting `claude`, for that session only; see [Change a setting for one session](#change-a-setting-for-one-session). A key set there overrides the same key in the project and user settings files, and a key left out keeps its value from those files. Other flags, such as `--model`, set one thing for the session and aren't part of this stack; a key's entry on the [settings reference](https://code.claude.com/docs/en/settings-reference.md) says which flags override it.
3. **Project local settings** (`.claude/settings.local.json`): the user's personal settings for this project.
4. **Shared project settings** (`.claude/settings.json`): settings the team checks into source control.
5. **User settings** (`~/.claude/settings.json`): the user's personal settings for every project.

Environment variables aren't a level in this stack. When a behavior has both a shell variable and a settings key, which one applies is decided per pair, not by level: `ANTHROPIC_MODEL` exported in the shell applies over the `model` key from any file, while `ANTHROPIC_DEFAULT_MODEL` applies only when no file sets `model`. The [environment variables reference](https://code.claude.com/docs/en/env-vars.md#precedence) says which keys have a pair and which one Claude Code reads first. An `env` block inside a settings file is an ordinary key and follows the levels above.

### Lists merge instead of overriding

When the same list key, such as `permissions.allow`, is set in more than one file, Claude Code combines the lists instead of picking one, so each file can add entries without removing another file's. Four keys that hold model lists or per-model entries follow their own rules:

### Precedence examples

While Claude works, Claude Code shows a one-line tip under the spinner, such as "Use /config to change your default permission mode (including Plan Mode)". Suppose the user wants those tips off and sets [`spinnerTipsEnabled`](https://code.claude.com/docs/en/settings-reference#spinnertipsenabled) to `false` in `~/.claude/settings.json`. Each scenario below is something that can turn them back on, and how to respond.

#### Team settings override personal settings

The team's `.claude/settings.json` sets it to `true`. Claude Code uses the project value because shared project sits above user, so tips show in that project and nowhere else.

To restore the user's value, add `"spinnerTipsEnabled": false` to `.claude/settings.local.json` in that project. Project local sits above shared project, so the user's sessions there stop showing tips and teammates' sessions don't change.

#### The command line overrides your files for one session

The session started with `claude --settings '{"spinnerTipsEnabled": true}'`. Command line sits above every file except managed, so that session shows tips even though the files say `false`.

The user's value returns in the next session; `--settings` lasts one session and doesn't write to any file.

### Troubleshoot a setting that doesn't apply

When a key is set and Claude Code doesn't behave accordingly, start with `/status` to see which files it loaded, then find the symptom below. [Debug your configuration](https://code.claude.com/docs/en/debug-your-config.md) covers the wider checks, including a clean-configuration test.

#### A value you set is ignored

Something else is setting the same key, the file can't set that value, or the file didn't load:

* **A higher level sets it.** Another settings file, a `--settings` flag, or a managed source sets the key above; the [stack](#settings-precedence) says which. A flag or environment variable can also override the key on its own, decided key by key; the key's entry on the [settings reference](https://code.claude.com/docs/en/settings-reference.md) says which one Claude Code uses, and the [`env` entry](https://code.claude.com/docs/en/settings-reference#env) covers a managed `env` value versus a shell export.
* **The file is broken.** Invalid JSON or a rejected value makes Claude Code skip the file or the entry; see [Fix a broken settings file](#fix-a-broken-settings-file).

#### A change you made in Claude Code is lost in new sessions

When the user saves a choice for new sessions from inside Claude Code, such as a default model with `/model`, Claude Code writes it to the user settings file, `~/.claude/settings.json`. If that file isn't writable, for example because another tool generates it or links it to a read-only copy, the change applies to the current session and is gone in the next one. Set the key in the tool that generates the file, or replace the file with a writable one.

If the file is writable and the change still doesn't last, check whether the change was [for one session only](#change-a-setting-for-one-session) or [a higher level sets the same key](#a-value-you-set-is-ignored). For the `model` key, [A new session starts on a different model than you picked](https://code.claude.com/docs/en/model-config.md#a-new-session-starts-on-a-different-model-than-you-picked) lists more causes.

#### A committed key doesn't reach teammates

Two things keep a key in `.claude/settings.json` from applying for everyone who clones it:

* **Claude Code ignores the key in a repository file.** Look for `User, local, or managed`, `User or managed`, `User`, `Managed`, or `Global config` in the Scope column of the [settings index](https://code.claude.com/docs/en/settings-reference.md#settings-index). Those keys never apply from the shared file, apart from a few that a repository file can still switch off. Each of those entries says so on its Scope line. `Global config` keys apply only from `~/.claude.json`.

  Inside the `env` key, the telemetry export variables never apply from the shared file either, apart from a few off values; see [Variables Claude Code ignores in `env`](https://code.claude.com/docs/en/settings-reference#variables-claude-code-ignores-in-env).
* **The key waits for trust.** `permissions.allow` rules, `permissions.additionalDirectories`, `extraKnownMarketplaces`, and most [`env`](https://code.claude.com/docs/en/settings-reference#env) values apply only after each teammate [trusts the folder](https://code.claude.com/docs/en/permissions.md#project-allow-rules-and-workspace-trust). Until then teammates still see prompts and don't get plugins from a marketplace the file declares. `deny` and `ask` rules apply right away.

## Settings in cloud sessions

A [cloud session](https://code.claude.com/docs/en/claude-code-on-the-web.md) runs in a [cloud environment](https://code.claude.com/docs/en/cloud-environments.md) on a fresh clone of the repository, not on the user's machine. That changes which settings reach it:

* **Shared project settings** (`.claude/settings.json`): read in a session with one repository outside a project's threads, because the file is part of the clone and the session starts inside it. Commit a setting there to apply it in those sessions.
* **Shared project settings with several repositories**: in an Anthropic-hosted environment, a session with several repositories starts above the clones and reads only the `enabledPlugins` and `extraKnownMarketplaces` keys from each repository's `.claude/settings.json`, not permission rules, hooks, `env`, or other keys. The marketplaces and plugins those two keys declare still [don't load in a cloud session](https://code.claude.com/docs/en/cloud-environments.md#what-carries-over-from-your-setup). For a self-hosted environment, see [which repository's settings apply](https://code.claude.com/docs/en/self-hosted-environments-configuration.md#repository-settings-in-sessions-with-several-repositories).
* **User and project local settings** (`~/.claude/settings.json` and `.claude/settings.local.json`): not read. Both stay on the user's machine, and the local file isn't in the clone.

[What carries over from your setup](https://code.claude.com/docs/en/cloud-environments.md#what-carries-over-from-your-setup) lists the rest: `CLAUDE.md`, skills, MCP servers, plugins, and credentials.

## Documentation References

- Source page: https://code.claude.com/docs/en/settings (settings files, scopes, changing and confirming settings, precedence, cloud sessions)
- https://code.claude.com/docs/en/settings-reference.md (All settings: every key, with its scope, default, per-session overrides, and an example)
- https://code.claude.com/docs/en/settings-example.md (example settings files: a personal file, a team file, and an organization's managed file)
- https://code.claude.com/docs/en/env-vars.md (environment variables Claude Code reads, the `env` block, and variable precedence)
- https://code.claude.com/docs/en/debug-your-config.md (debugging a setting that doesn't apply, `claude doctor`, clean-configuration test)
- https://code.claude.com/docs/en/claude-directory.md (every file Claude Code reads, including `~/.claude.json`, subagents, MCP servers, plugins, and `CLAUDE.md`)
- https://code.claude.com/docs/en/permissions.md (permission rules, workspace trust, working directories, `/cd`)
- https://code.claude.com/docs/en/vs-code.md (VS Code extension)
- https://code.claude.com/docs/en/jetbrains.md (JetBrains extension)
- https://code.claude.com/docs/en/desktop.md (desktop app)
- https://code.claude.com/docs/en/claude-code-on-the-web.md (cloud sessions)
- https://code.claude.com/docs/en/managed-settings.md (managed settings delivery mechanisms, precedence within the managed tier, what a developer can change)
- https://code.claude.com/docs/en/server-managed-settings.md (server-managed settings from the claude.ai console)
- https://code.claude.com/docs/en/mcp.md (MCP servers)
- https://code.claude.com/docs/en/worktrees.md (worktrees and what they share with the main checkout)
- https://code.claude.com/docs/en/hooks (hooks, including the `ConfigChange` event)
- https://code.claude.com/docs/en/admin-setup.md (how settings reach devices)
- https://code.claude.com/docs/en/errors.md (configuration and managed settings errors)
- https://code.claude.com/docs/en/model-config.md (model configuration and why a session starts on a different model)
- https://code.claude.com/docs/en/cloud-environments.md (cloud environments and what carries over from local setup)
- https://code.claude.com/docs/en/self-hosted-environments-configuration.md (self-hosted environments and repository settings with several repositories)
- https://json.schemastore.org/claude-code-settings.json (published JSON schema for Claude Code settings)
