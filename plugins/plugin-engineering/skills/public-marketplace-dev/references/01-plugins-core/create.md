# Create a Claude Code plugin

Build a first Claude Code plugin from an empty directory, test it without a marketplace, and convert an existing `.claude/` setup.

## Contents

- [Overview](#overview)
- [Decide when to use a plugin](#decide-when-to-use-a-plugin)
- [Create your first plugin](#create-your-first-plugin)
  - [Share your plugin](#share-your-plugin)
  - [Plugin layout](#plugin-layout)
- [Develop without a marketplace](#develop-without-a-marketplace)
  - [Load a plugin for one session](#load-a-plugin-for-one-session)
    - [Load a plugin from a directory or `.zip`](#load-a-plugin-from-a-directory-or-zip)
    - [Load a folder of plugins](#load-a-folder-of-plugins)
    - [Load a plugin from a URL](#load-a-plugin-from-a-url)
    - [Load plugins from an environment variable](#load-plugins-from-an-environment-variable)
  - [Make a plugin load in every session](#make-a-plugin-load-in-every-session)
    - [Scaffold the plugin with `claude plugin init`](#scaffold-the-plugin-with-claude-plugin-init)
    - [Name the plugin's skills](#name-the-plugins-skills)
    - [Stop loading the plugin](#stop-loading-the-plugin)
- [Test and debug](#test-and-debug)
  - [A component path isn't found](#a-component-path-isnt-found)
  - [`--plugin-dir` at a marketplace root doesn't load the plugins under `plugins/`](#--plugin-dir-at-a-marketplace-root-doesnt-load-the-plugins-under-plugins)
  - [The plugin loads but its skills are missing](#the-plugin-loads-but-its-skills-are-missing)
  - [The `userConfig` dialog never appears](#the-userconfig-dialog-never-appears)
  - [Check that the plugin changes Claude's behavior](#check-that-the-plugin-changes-claudes-behavior)
- [Convert an existing `.claude/` setup](#convert-an-existing-claude-setup)
- [Documentation References](#documentation-references)

## Overview

A plugin is a directory of skills, agents, hooks, and MCP servers, plus a `plugin.json` file, called the manifest, that names the plugin. Claude Code loads the directory as one unit, so it can be shared with others, installed in several projects, or published to a marketplace.

This file is about writing plugins.

> **Note:** These cases are covered on other pages:
>
> * **Installing someone else's plugin**: read [Install plugins](https://code.claude.com/docs/en/plugins/install.md)
> * **Not sure a plugin is needed**: read [Decide whether you need a plugin](https://code.claude.com/docs/en/plugins/overview.md#decide-whether-you-need-a-plugin) on the overview
> * **The plugin's users are on claude.ai or in Cowork**: the same folder installs there with a different subset of components. Some components are Claude Code-only. Read [Plugin structure and testing](https://claude.com/docs/plugins/build) and the [component support table](https://claude.com/docs/plugins/platform-support#compare-component-support-by-app), which lists which components load on each surface

Start from the section that matches what already exists:

* **Nothing yet**: follow [Create your first plugin](#create-your-first-plugin), then [Develop without a marketplace](#develop-without-a-marketplace) and [Test and debug](#test-and-debug).
* **Files under `.claude/` already**: do the first-plugin walkthrough once to learn the layout, then follow [Convert an existing `.claude/` setup](#convert-an-existing-claude-setup).

## Decide when to use a plugin

Skills, agents, hooks, and MCP servers all work standalone in a project or home directory. Keep that standalone setup while it serves one project or one person. Make a plugin to share the setup with others, install it in several projects, or publish versioned releases.

When standalone skills, agents, hooks, and MCP config move into a plugin, their location and names change:

* **Where the files go**: under the plugin's own directory, called the plugin root, as `skills/`, `agents/`, `hooks/hooks.json`, and `.mcp.json`.
* **How they're named**: plugin skills and agents get the plugin name as a prefix, such as `/my-plugin:hello`, so two plugins can each provide a `hello` skill without colliding.

To move an existing setup into a plugin, read [Convert an existing `.claude/` setup](#convert-an-existing-claude-setup).

## Create your first plugin

This walkthrough creates a plugin whose only component is one skill, a greeting, and runs it with `--plugin-dir`, which loads a plugin for one session without installing it. A plugin can hold any mix of [components](https://code.claude.com/docs/en/plugins/components.md), such as skills, agents, hooks, and MCP servers, and none is required; one skill is the smallest example that shows the layout.

Claude Code must be [installed and signed in](https://code.claude.com/docs/en/quickstart.md#step-1-install-claude-code).

Open a terminal in the directory that will hold the plugin, such as `~/projects`, and run the commands in these steps from it. A plugin can live anywhere, because its path is passed to Claude Code when a session starts.

**1. Create the plugin directory**

Create the plugin directory, with a `.claude-plugin/` folder inside it to hold the manifest:

```bash theme={null}
mkdir -p my-first-plugin/.claude-plugin
```

**2. Write the manifest**

The [manifest](https://code.claude.com/docs/en/plugins/manifest-reference.md) is a JSON file named `plugin.json` that tells Claude Code the plugin's name and describes it. Save this one as `my-first-plugin/.claude-plugin/plugin.json`:

```json my-first-plugin/.claude-plugin/plugin.json theme={null}
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

The four fields do this:

* **`name`**: required. It identifies the plugin and becomes the prefix on every skill and agent the plugin provides. Don't put spaces in it.
* **`description`**: the text users see for the plugin in `/plugin`.
* **`version`**: optional. Setting it keeps users on that version until it changes; [Release a new version](https://code.claude.com/docs/en/plugins/host-marketplace.md#release-a-new-version) says when to set or omit it.
* **`author`**: who to credit. `name` is required inside it; `email` and `url` are optional.

Every other field is on the [manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference.md#fields).

Only `plugin.json` goes inside `.claude-plugin/`. The skill added next goes directly under `my-first-plugin/`, next to that folder.

**3. Add a skill**

This plugin's one component is a skill. Each skill is a directory under `skills/` that contains a `SKILL.md` file. Create the skill's directory:

```bash theme={null}
mkdir -p my-first-plugin/skills/hello
```

Then create `my-first-plugin/skills/hello/SKILL.md` with this content:

```markdown my-first-plugin/skills/hello/SKILL.md theme={null}
---
name: hello
description: Greet the user with a friendly message
disable-model-invocation: true
---

Greet the user warmly and ask how you can help them today.
```

The `disable-model-invocation: true` line means Claude doesn't run the skill on its own. Remove that line from a skill Claude should run on its own. The skill's command combines the plugin name and the skill's name, so this one runs as `/my-first-plugin:hello`. For the other frontmatter fields, read the [skill frontmatter reference](https://code.claude.com/docs/en/skills.md#frontmatter-reference).

**4. Validate the plugin**

Check the manifest and the skill's frontmatter before running anything:

```bash theme={null}
claude plugin validate ./my-first-plugin
```

The command prints the manifest path it checked and `✔ Validation passed`. If it prints `✘ Validation failed` instead, each line above that result line names the field to fix. Look up each message under [`claude plugin validate` reports errors](https://code.claude.com/docs/en/plugins/troubleshooting#claude-plugin-validate-reports-errors).

**5. Run Claude Code with the plugin**

Start a session with the plugin loaded:

```bash theme={null}
claude --plugin-dir ./my-first-plugin
```

Once Claude Code starts, run the skill:

```text theme={null}
/my-first-plugin:hello
```

Claude replies with a greeting.

The plugin loads only in sessions started with `--plugin-dir`. To keep working on it without the flag, or to test a `.zip` build, read [Develop without a marketplace](#develop-without-a-marketplace).

To scaffold and check a larger plugin with Claude's help, [install](https://code.claude.com/docs/en/plugins/install.md#install-a-plugin) Anthropic's `plugin-dev` plugin from the `claude-plugins-official` marketplace, which adds skills and agents for writing components such as skills, hooks, and MCP servers and for validating the finished plugin. Once it's installed, run `/plugin-dev:create-plugin` followed by a description of the plugin, and Claude walks through designing, creating, and validating it.

### Share your plugin

A plugin built with [Create your first plugin](#create-your-first-plugin) exists only on the local machine. The source page lists three ways to get it to other people; this copy keeps the one that applies here:

* **List it in your own marketplace**: users add the marketplace once and install the plugin by name, and they receive its updates. Read [Publish through your own marketplace](https://code.claude.com/docs/en/plugins/publish.md#publish-through-your-own-marketplace).

### Plugin layout

Each kind of [component](https://code.claude.com/docs/en/plugins/components.md), such as skills, agents, hooks, and MCP servers, goes in a fixed directory under the plugin root, which is the directory passed to `--plugin-dir`. Add only the directories the plugin uses. To click through a complete plugin directory and read what each file does, open the [plugin explorer](https://code.claude.com/docs/en/plugins/components.md#explore-the-plugin-directory).

The table lists the directories most plugins start with, and the [full layout](https://code.claude.com/docs/en/plugins/manifest-reference.md#standard-layout) lists the rest.

| Location | Contents |
| :- | :- |
| `.claude-plugin/plugin.json` | The manifest. When you load a plugin with `--plugin-dir` and it has no manifest, Claude Code names the plugin after its directory |
| `skills/` | One `<name>/SKILL.md` directory per skill |
| `commands/` | Flat Markdown files, the older form of skills. Use `skills/` for new plugins |
| `agents/` | One Markdown file per subagent |
| `hooks/hooks.json` | Hook configuration: a top-level `"hooks"` key whose value has the same shape as `hooks` in a settings file |
| `.mcp.json` | MCP server definitions |

> **Warning:** Only `plugin.json` goes inside `.claude-plugin/`. Components saved there don't load.
>
> The plugin root is the plugin's own directory, not `~/.claude/` itself. A `.mcp.json` saved at `~/.claude/.mcp.json` doesn't load.

## Develop without a marketplace

A [marketplace](https://code.claude.com/docs/en/plugins/overview.md#get-plugins-from-a-marketplace) is not needed to run a plugin under development. Load it directly from disk or a URL instead:

* [`--plugin-dir`](#load-a-plugin-from-a-directory-or-zip): loads a directory or `.zip` archive for one session.
* [`--plugin-url`](#load-a-plugin-from-a-url): fetches a `.zip` archive from a URL for one session.
* [`claude plugin init`](#scaffold-the-plugin-with-claude-plugin-init): scaffolds a plugin under `~/.claude/skills/` that loads across sessions.

If two plugins loaded in different ways share a name, read [Name conflicts](https://code.claude.com/docs/en/plugins/loading.md#name-conflicts) for which one Claude Code keeps.

### Load a plugin for one session

There are three ways to load a plugin for a single session: from a directory or `.zip` archive on disk with `--plugin-dir`, from a URL with `--plugin-url`, or from an environment variable when a flag can't be added. Each plugin loads for that session only, and nothing is written to settings for it. After editing the plugin's files during the session, run `/reload-plugins` to load the changes.

#### Load a plugin from a directory or `.zip`

When starting `claude` from the shell, pass `--plugin-dir` with the plugin's root directory or a `.zip` archive of it. Repeat the flag to load several plugins:

```bash theme={null}
claude --plugin-dir ./my-first-plugin --plugin-dir ./other-plugin.zip
```

#### Load a folder of plugins

To load several plugins from one place, pass a folder that holds them, such as `--plugin-dir ./plugins`. Loading a folder of plugins requires Claude Code v2.1.265 or later.

If the folder has no `.claude-plugin/` directory and no plugin components at its top level, Claude Code treats it as a folder of plugins. Each immediate subfolder that has a `.claude-plugin/plugin.json` manifest then loads as a separate plugin. Everything else in the folder is skipped without an error, including a subfolder that has no manifest. If a plugin in the folder doesn't load, check that its subfolder has a `.claude-plugin/plugin.json`.

A folder that keeps a `.claude-plugin/marketplace.json` beside its plugin folders also works. As long as that `.claude-plugin/` directory holds no `plugin.json`, the plugin folders still load. Nothing is installed or enabled from the marketplace file, because Claude Code doesn't read it. Loading plugins from such a folder requires Claude Code v2.1.281 or later.

In an interactive session, plugins can also be added to and removed from the folder after startup:

* An added subfolder loads as a new plugin once its manifest exists.
* When a subfolder is removed, its plugin unloads.

A message appears in the session for each of these changes. If loading or unloading a plugin mid-conversation would [invalidate the prompt cache](https://code.claude.com/docs/en/prompt-caching.md#enabling-or-disabling-a-plugin), the change is held instead, and the message says to run `/reload-plugins` to apply it.

#### Load a plugin from a URL

When starting `claude` from the shell, pass `--plugin-url` with the address of a `.zip` archive, such as a build artifact that CI publishes:

```bash theme={null}
claude --plugin-url https://example.com/my-first-plugin.zip
```

Claude Code downloads the archive at startup. To load several, repeat the flag or pass the URLs space-separated in one quoted argument.

Point the flag only at archives you control or trust.

If Claude Code can't fetch the archive, or the archive is invalid, it starts without the plugin and records a plugin load error, shown in the `/plugin` manager's **Errors** tab.

#### Load plugins from an environment variable

To load plugins in a session where the `--plugin-dir` flag can't be added, list their absolute paths in the [`CLAUDE_CODE_PLUGIN_DIRS`](https://code.claude.com/docs/en/env-vars#variables) environment variable instead. Claude Code loads each path as it loads a `--plugin-dir` path. These plugins load in addition to any passed with `--plugin-dir`. [Project and local settings can't set this variable](https://code.claude.com/docs/en/settings-reference.md#variables-claude-code-ignores-in-env). `CLAUDE_CODE_PLUGIN_DIRS` requires Claude Code v2.1.280 or later.

Managed settings can turn off `--plugin-dir` and `CLAUDE_CODE_PLUGIN_DIRS`. Read [Flags that load a plugin for one session](https://code.claude.com/docs/en/plugins/cli-reference.md#flags-that-load-a-plugin-for-one-session). To test a plugin together with a plugin it depends on, read [Test a plugin and its dependency locally](https://code.claude.com/docs/en/plugins/dependencies.md#test-a-plugin-and-its-dependency-locally).

### Make a plugin load in every session

The personal skills directory is `~/.claude/skills/`, and a folder there that contains a `.claude-plugin/plugin.json` is a skills-directory plugin. Unless an administrator has [blocked skills-directory plugins](https://code.claude.com/docs/en/plugins/loading.md#skills-directory-plugins-blocked-by-managed-settings), Claude Code loads each one when a session starts, with no flag and no install step. `claude plugin init` scaffolds one.

#### Scaffold the plugin with `claude plugin init`

`claude plugin init` writes a starter plugin under `~/.claude/skills/`. Scaffold one from the shell:

```bash theme={null}
claude plugin init my-tool
```

The command creates `~/.claude/skills/my-tool/` with a `.claude-plugin/plugin.json` and a root `SKILL.md`. It prints `✔ Created plugin "my-tool" at ~/.claude/skills/my-tool` followed by `It will auto-load next session as my-tool@skills-dir. Run /reload-plugins to load it now.`

Pass `--with skills` to have `claude plugin init` also scaffold a skill under `skills/`. The other `--with` values are on the [plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-init).

#### Name the plugin's skills

The root skill at `~/.claude/skills/my-tool/SKILL.md` is also a personal skill, so it is invoked as `/my-tool`, not `/my-tool:my-tool`. Skills added under `skills/` inside the plugin get the plugin-name prefix, such as `/my-tool:example`.

#### Stop loading the plugin

To stop loading a scaffolded plugin, delete its directory, or run `claude plugin disable my-tool@skills-dir` in the shell with the `my-tool@skills-dir` name that `claude plugin init` printed. In the ID `my-tool@skills-dir`, `skills-dir` stands where a marketplace name would, because the plugin loads from the skills directory rather than from a marketplace.

## Test and debug

When a change to a plugin doesn't show up, work through these checks in order. Each one shows what Claude Code did with the plugin:

1. In the shell, run `claude plugin validate <path>`. It checks the manifest and the frontmatter of every skill, agent, and command file, and exits `0` on `Validation passed`. Add `--strict` to fail on warnings too. Exit codes and directory handling are on the [plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-validate).
2. In the running session, run `/reload-plugins` to apply edits made on disk. It prints one `Reloaded:` line with counts. Then confirm a skill loaded by typing its `/plugin-name:skill` command, or by finding the plugin in the `/plugin` **Installed** tab.
3. In the same session, run `/plugin`. The **Installed** tab lists the plugin and, in the plugin's details, the components Claude Code found. The **Errors** tab lists what failed to load and why, such as a path in the manifest that doesn't exist.
4. Back in the shell, run `claude plugin list`. It prints session-only and skills-directory plugins in their own sections with `Status: ✔ loaded` or the load error. To include the plugin under development, pass `--plugin-dir` with its path before `plugin list`.
5. If the plugin is in a skills directory and `claude plugin list` doesn't print it, with no error there or in `/plugin`, read [Skills-directory plugins blocked by managed settings](https://code.claude.com/docs/en/plugins/loading.md#skills-directory-plugins-blocked-by-managed-settings).

To check an MCP server, run `/mcp` in the session to see the server's status. When the server is healthy, `/mcp` lists it as connected. If it isn't, read [MCP servers that don't start](https://code.claude.com/docs/en/plugins/troubleshooting.md#invalid-mcp-server-config-for-and-mcp-servers-that-dont-start).

To check a hook, trigger the event it matches. For example, have Claude edit a file to trigger a `PostToolUse` hook. Then read the [debug log](https://code.claude.com/docs/en/hooks.md#debug-hooks), which shows which hooks matched, their exit codes, and their output.

The next sections cover the failures most likely during development, and the [troubleshooting page](https://code.claude.com/docs/en/plugins/troubleshooting.md#build-a-plugin) has the full entry for each.

### A component path isn't found

The **Errors** tab of `/plugin` shows `<component> path not found: <path>`, for example `commands path not found`. A component path in the manifest, such as `commands`, `skills`, `agents`, or `hooks`, points at nothing. Fix the path or create the directory, then run `/reload-plugins` in the session. Read [`commands path not found`](https://code.claude.com/docs/en/plugins/troubleshooting#commands-path-not-found).

### `--plugin-dir` at a marketplace root doesn't load the plugins under `plugins/`

`--plugin-dir` takes the plugin's root directory, the one that contains `.claude-plugin/plugin.json` and the component directories such as `skills/`. If it points at a marketplace root instead, Claude Code doesn't read `marketplace.json`, so a plugin under `plugins/` doesn't load, and no error appears. Point the flag at one plugin's folder, or add the marketplace. Read [the troubleshooting entry](https://code.claude.com/docs/en/plugins/troubleshooting.md#plugin-dir-loads-a-plugin-with-no-components).

### The plugin loads but its skills are missing

Cause: the `skills/` directory is inside `.claude-plugin/`, or a `skills` entry in the manifest points at a file. Move `skills/` to the plugin root, point each `skills` entry at a directory that contains `SKILL.md`, and run `/reload-plugins` in the session. Read [Plugin loads but its skills are missing](https://code.claude.com/docs/en/plugins/troubleshooting.md#plugin-loads-but-its-skills-are-missing).

### The `userConfig` dialog never appears

The dialog for a plugin's [`userConfig`](https://code.claude.com/docs/en/plugins/components#user-configuration) options is part of installing through `/plugin` in a session. Loading with `--plugin-dir` doesn't show it, and neither does `claude plugin install` in the shell. With the plugin loaded, run `/plugin configure <plugin-name>` in the session to open it. Read [The `userConfig` dialog never appears](https://code.claude.com/docs/en/plugins/troubleshooting#the-userconfig-dialog-never-appears).

### Check that the plugin changes Claude's behavior

A plugin that loads without errors can still fail to steer Claude as intended. `claude plugin eval`, run in the shell, runs test cases with and without the plugin and scores the difference. Read [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals.md), starting with [Create your first eval suite](https://code.claude.com/docs/en/plugin-evals.md#create-your-first-eval-suite).

## Convert an existing `.claude/` setup

Skills, agents, or hooks under a project's `.claude/` directory can move into a plugin without being rewritten.

Run the commands in these steps from the project root, which is the directory that contains `.claude/`, because the `cp` paths are relative to it.

**1. Create the plugin structure**

Create the plugin directory and its `.claude-plugin/` folder alongside `.claude/`. The plugin can move anywhere afterwards.

```bash theme={null}
mkdir -p my-plugin/.claude-plugin
```

Create `my-plugin/.claude-plugin/plugin.json`:

```json my-plugin/.claude-plugin/plugin.json theme={null}
{
  "name": "my-plugin",
  "description": "Migrated from standalone configuration",
  "version": "1.0.0"
}
```

**2. Copy the existing files**

Copy each existing configuration directory to the plugin root, and skip the command for any directory that doesn't exist.

```bash theme={null}
cp -r .claude/commands my-plugin/
```

```bash theme={null}
cp -r .claude/agents my-plugin/
```

```bash theme={null}
cp -r .claude/skills my-plugin/
```

Run `ls -a my-plugin` to confirm that each copied directory appears next to `.claude-plugin`.

**3. Move the hooks**

If there are hooks in `.claude/settings.json` or `.claude/settings.local.json`, create a hooks directory:

```bash theme={null}
mkdir -p my-plugin/hooks
```

Create `my-plugin/hooks/hooks.json` and copy the `hooks` object from the settings file into it. The format is the same.

This example shows the shape with one hook that runs a linter on each file Claude writes or edits. Replace the example with the project's own `hooks` object.

```json my-plugin/hooks/hooks.json theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npm run lint:fix" }]
      }
    ]
  }
}
```

**4. Test the migrated plugin**

Load the plugin for a session:

```bash theme={null}
claude --plugin-dir ./my-plugin
```

Check each component under its new name:

* **Skills**: run `/my-plugin:deploy` for a skill that was `/deploy`.
* **Subagents**: have Claude use the `my-plugin:reviewer` agent for an agent that was `reviewer`.
* **Hooks**: trigger the event each hook matches.

If something is missing, work through [Test and debug](#test-and-debug).

While the originals are still under `.claude/`, they stay loaded alongside the plugin's copies:

* **Skills and agents**: the two sets don't collide, because the plugin's skills and agents carry the `my-plugin:` prefix. `/deploy` and `/my-plugin:deploy` both work, and Claude sees `reviewer` and `my-plugin:reviewer` as two subagents.
* **Hooks**: hooks have no prefix, so a hook that is in both the settings file and `hooks/hooks.json` runs twice each time its event fires.

After confirming the plugin works, delete the originals from `.claude/` and remove the `hooks` object from the settings file.

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/create
- https://code.claude.com/docs/en/plugins/install.md: install someone else's plugin, and install `plugin-dev`
- https://code.claude.com/docs/en/plugins/overview.md: decide whether a plugin is needed, and get plugins from a marketplace
- https://claude.com/docs/plugins/build: plugin structure and testing; the same folder installs on claude.ai and in Cowork
- https://claude.com/docs/plugins/platform-support: the component support table, which components load on each surface
- https://code.claude.com/docs/en/plugins/components.md: plugin components (agents, hooks, MCP servers, LSP servers, user configuration) and the plugin directory explorer
- https://code.claude.com/docs/en/plugins/components: user configuration (`userConfig`)
- https://code.claude.com/docs/en/quickstart.md: install and sign in to Claude Code
- https://code.claude.com/docs/en/plugins/manifest-reference.md: every `plugin.json` field, path rule, and the standard layout
- https://code.claude.com/docs/en/plugins/host-marketplace.md: release a new version, when to set or omit `version`
- https://code.claude.com/docs/en/skills.md: skill frontmatter reference, writing the skills a plugin provides
- https://code.claude.com/docs/en/plugins/troubleshooting: `claude plugin validate` errors, `commands path not found`, the `userConfig` dialog
- https://code.claude.com/docs/en/plugins/troubleshooting.md: build-a-plugin failures, MCP servers that don't start, `--plugin-dir` with no components, missing skills
- https://code.claude.com/docs/en/plugins/publish.md: version a plugin, publish through your own marketplace, submit for review
- https://code.claude.com/docs/en/plugins/loading.md: name conflicts and skills-directory plugins blocked by managed settings
- https://code.claude.com/docs/en/prompt-caching.md: enabling or disabling a plugin mid-conversation and the prompt cache
- https://code.claude.com/docs/en/env-vars: the `CLAUDE_CODE_PLUGIN_DIRS` environment variable
- https://code.claude.com/docs/en/settings-reference.md: variables Claude Code ignores in project and local `env`
- https://code.claude.com/docs/en/plugins/cli-reference.md: flags that load a plugin for one session, `plugin init`, `plugin validate`
- https://code.claude.com/docs/en/plugins/dependencies.md: test a plugin and its dependency locally
- https://code.claude.com/docs/en/hooks.md: debug hooks with the debug log
- https://code.claude.com/docs/en/plugin-evals.md: write eval cases and run them with `claude plugin eval`
- https://github.com/anthropics/claude-plugins-official/tree/main/plugins: Anthropic's plugins in the claude-plugins-official repository, complete worked examples such as `feature-dev` and `code-review`
