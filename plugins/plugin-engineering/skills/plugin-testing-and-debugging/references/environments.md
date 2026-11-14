# Where the session runs: terminal, cloud session or project thread

Read this file before testing or debugging a plugin when the session may not be the user's own terminal: `CLAUDE_CODE_REMOTE` is `true`, the work happens in a fresh clone, the user is at claude.ai/code, the desktop or mobile app, or the task came from a project. What loads, which commands exist and where the fix goes all change with the environment. Sources: "Use Claude Code on the web" (https://code.claude.com/docs/en/claude-code-on-the-web), "Cloud environments", section "What carries over from your setup" (https://code.claude.com/docs/en/cloud-environments), "Claude Projects" (https://code.claude.com/docs/en/claude-projects), "Skills", section "Use skills in Cowork and cloud sessions" (https://code.claude.com/docs/en/skills), and the changelog to 2.1.325.

## Contents

- 1. Find where you are
- 2. Cloud session: what loads
- 3. Project cloud thread: what loads
- 4. Testing in a cloud session or thread
- 5. Debugging in a cloud session or thread
- 6. Where each fix goes
- 7. Claude on the web, desktop and mobile
- 8. Agent SDK

## 1. Find where you are

1. `echo "$CLAUDE_CODE_REMOTE"`: Claude Code sets it to `true` in a cloud session, and a project's cloud threads are cloud sessions. Empty means a session on a machine: the user's terminal, IDE or desktop app, or a thread running on the user's computer through Remote Control, which uses what is installed there.
2. A cloud session started from a project carries the project's goal or instructions in its context and loads only the root `CLAUDE.md` files and rules of the project's repositories. A cloud session outside a project starts from a fresh clone of its repository and loads that repository's committed `.claude/` configuration.
3. Everything Claude runs with Bash in a cloud session, including `claude plugin ...`, acts on the session's own VM and its own `~/.claude`, never on the user's machine. A `claude plugin install` there changes nothing the user will see in their terminal, and the user's own installs are not there to inspect.
4. The person uses Claude in a browser, the desktop app or the mobile app, not Claude Code: plugins come from their claude.ai account, not from a machine. Use section 7.
5. The plugin is loaded by an application built on the Agent SDK: use section 8.

Tell the user which environment you found before giving fixes, because the same symptom has different causes in each.

## 2. Cloud session: what loads

A cloud session runs on an Anthropic-managed VM from a fresh clone. Anything committed to the repository is there; anything configured only on the user's machine is not.

Loaded:
- the repository's `CLAUDE.md`, `.claude/rules/`, `.claude/skills/`, `.claude/agents/` and `.claude/commands/`;
- hooks and permission rules in the repository's `.claude/settings.json`, and its `.mcp.json` servers, in a session with one repository;
- skills and plugins enabled for the user's claude.ai account (plugins load as `<name>@synced`);
- the organization's server-managed settings, fetched at session start.

Not loaded:
- plugins the repository turns on under `enabledPlugins` in `.claude/settings.json`, and marketplaces it lists under `extraKnownMarketplaces`;
- anything under the user's `~/.claude/` on their machine: personal skills, agents, commands, plugins enabled only in user settings, `CLAUDE.md`;
- MCP servers added with `claude mcp add` at local or user scope;
- managed settings deployed to the user's device through MDM or managed settings files.

Commands:
- `/plugin` is a terminal-interface command and is not available. `/reload-plugins` runs when typed into the session itself (from v2.1.260 without an interactive terminal), but not through a relayed message.
- Claude may show a plugin suggestion card with an Add button. Add turns the plugin on for the user's claude.ai account, where it stays after the session ends; it loads as a synced plugin.

## 3. Project cloud thread: what loads

A project thread is a cloud session that loads even less from the repositories: their root `CLAUDE.md`, `.claude/CLAUDE.md` and `.claude/rules/` (path-specific rules excepted), and nothing else.

Not loaded in a thread, with where the thing goes instead:
- skills under `.claude/skills/`: enable the skill for the claude.ai account;
- agents and commands under `.claude/`: run the thread on the user's computer through Remote Control (Claude Code v2.1.280 or later there);
- MCP servers in `.mcp.json`: use the connectors on the claude.ai account;
- plugins enabled in `.claude/settings.json`: add the plugin in **Project settings > Plugins**; it loads into each new thread;
- permission rules: approve tool calls inside the thread, or run the thread on the user's computer;
- hooks in the repository's `.claude/settings.json`: not run; run the thread on the user's computer to use them. This is about the repository's settings, not about a plugin added in **Project settings > Plugins**: that plugin loads into each new thread, and the docs do not say its hooks are skipped, so test it there before ruling it out;
- `env`: set environment variables in the project's cloud environment;
- command-line tools: install them in the environment's setup script.

Changes in **Project settings** (plugins, repositories, instructions, environment) reach new threads, not threads already running. A plugin added there while a thread runs is not in that thread.

## 4. Testing in a cloud session or thread

- `claude plugin validate <dir> [--strict]` reads files only, so it works the same here and is the first check.
- A plugin under development in the repository is not loaded by the session itself (repository `enabledPlugins` are skipped, and threads skip `.claude/skills/` too). Test its static side here, and test its behavior where it will run: on the user's machine with `--plugin-dir` or an install, or, for a team that works in cloud sessions, through the claude.ai account or **Project settings > Plugins**.
- `claude plugin eval` runs model calls with whatever credential the session's environment provides; check that one exists before planning a run, agree the cost with the user, and keep in mind that every run is isolated from the session's own plugins anyway.
- Marketplace sources and package downloads go through the environment's network access; a host outside its allowed domains fails to clone or download. Check the environment's network setting before reading a clone failure as a credential problem.

## 5. Debugging in a cloud session or thread

Start from "is it supposed to load here at all?" before the terminal causes in `messages.md` and `loading.md`:

1. A plugin the repository enables in `.claude/settings.json` is missing: expected in every cloud session. Turn it on for the claude.ai account (it then loads as `@synced` in cloud sessions and the user's terminal), or, for a project, add it in **Project settings > Plugins**.
2. A repository skill, agent, command, hook or `.mcp.json` server is missing in a project thread: expected; use the replacements in section 3.
3. A plugin added in **Project settings** is missing in a thread: the thread started before the change; start a new thread.
4. A plugin turned on for the claude.ai account is missing in a cloud session: start a new session; on 2.1.323 and later Claude can also say why plugins are missing when the account has very many turned on.
5. The user's local installs, settings or scopes cannot explain a cloud symptom and cannot be read from here; ask the user to run the terminal checks on their machine when the problem is there.

## 6. Where each fix goes

- For the user's terminal: the settings files and `claude plugin` commands in `loading.md` and `messages.md`, run by the user on their machine.
- For every cloud session of a repository: commit it (skills, agents, commands, hooks, permission rules, `.mcp.json`), or turn the plugin or skill on for the claude.ai account.
- For a project's threads: **Project settings > Plugins**, the claude.ai account's skills and connectors, the project's cloud environment (variables, network, setup script), or a thread run on the user's computer.

## 7. Claude on the web, desktop and mobile

Sources: "Plugin structure and testing" (https://claude.com/docs/plugins/build), "Plugin feature support across platforms" (https://claude.com/docs/plugins/platform-support), "Install plugins" (https://claude.com/docs/cowork/guide/plugins), and the help center articles "Claude Cowork and chat are one Claude" (support.claude.com 16761823), "Use plugins in Claude" (13837440) and "Manage plugins, skills, and connectors from one Plugins page" (17740565), read 2026-11-14.

### Which experience the account has

- Since the announcement of 2026-09-16 ("Claude Cowork and chat are now one Claude", https://claude.com/blog/cowork-is-now-claude), chat and Cowork are merging into one Claude. It rolls out gradually to Pro, Max and Ultra on web, desktop and mobile; on Team and Enterprise it is available where "Chat and Cowork unified" is turned on.
- On Pro, Max and Ultra, if the message box still shows separate "Chat" and "Cowork" options, the account does not have the merged experience yet. Once it does, it cannot switch back.
- The claude.com/docs component tables still use separate Chat and Cowork columns, while the help center documents the merge. When they disagree, tell the user both, ask which experience the account shows, and rely on what the session shows.

### Install and requirements

- Add plugins from the sidebar's **Plugins** page in a browser or the desktop app, not with `/plugin`. That page was **Customize > Plugins**: the rename rolls out to Free, Pro, Max, Ultra and Team from 2026-10-29, generally available 2026-11-09, and reaches Enterprise on 2026-11-30.
- From there: browse, add a marketplace from a Git repository, or upload a plugin file.
- On Team and Enterprise, an owner must turn on "Cloud code execution and file creation" in Organization settings, because plugins require it. From 2026-11-30, if Skills are turned off for a Team or Enterprise organization, plugins are also blocked in the desktop app.
- Plugins are saved to the account and sync to Claude Code (v2.1.273 or later) once at each start, as `<name>@synced` (see `loading.md`, "Plugins synced from claude.ai"). They do not sync when Claude Code is signed in with an API key or runs on a cloud provider such as Amazon Bedrock.

### What loads

- Skills and commands load everywhere. In chat a command loads as a skill that Claude applies when it fits; in Cowork it runs as `/plugin-name:command`.
- Documented: agents and hooks load in Cowork and Claude Code, and chat ignores them; in chat they appear grayed out.
- Observed in a Claude session, 2026-11-13, on a merged account: a conversation doing task work ran as a cloud session built on Claude Code, where account plugins loaded as `<name>@synced`; plugin hooks fired and plugin agents were available. On an account not yet merged, expect the documented chat behavior.
- A remote MCP server with a fixed URL is listed on the plugin's **Connectors** tab and works once it is added or connected there. A local MCP server, one the app starts as a command, loads only in Claude Code and in Cowork sessions that run on the person's computer.
- An MCP server whose URL references `${user_config.*}` is ignored in chat; in Cowork it is ignored when a referenced option has no default, because Cowork does not prompt for values. Only Claude Code prompts for them.
- In Cowork, connectors reach external services through Anthropic's cloud, not the local network, so a custom connector must be reachable over the public internet.
- LSP servers, output styles, themes and `settings` load only in Claude Code.
- A top-level `bin/` directory makes chat and Cowork refuse to install the whole plugin.
- Any binary a hook or skill calls must exist in the environment that runs it. Observed in a Claude session, 2026-11-13: a plugin hook reported "basedpyright is not installed" until the binary was installed. In a Claude Code cloud environment, install such binaries with its setup script ("Cloud environments", https://code.claude.com/docs/en/cloud-environments).
- Before debugging something present on one surface and missing on another, check this list: a component a surface skips by design is the surface working as designed.

### How to test there

1. Zip the plugin folder, with the folder as the single top-level entry or its contents at the root.
2. Upload it from **Plugins** (formerly **Customize > Plugins**) with **Add > Upload plugin**. `plugin.json must be at .claude-plugin/plugin.json at the zip root (or inside a single top-level directory)` means the manifest is nested more than one folder deep, or the archive has other files beside the plugin folder.
3. Open a conversation and ask Claude which skills it has from plugins.
4. Connect each bundled connector from the plugin's **Connectors** tab.
5. If the plugin has agents, start a Cowork task to confirm they load (observed: on a merged account, a task in any conversation).
6. For a team, push the folder to a Git repository set up as a marketplace and have each tester add it, so everyone installs the same copy.

### When it goes wrong

- Installing never adds or connects a connector. A plugin that bundles an MCP server installs, but the server stays off until it is connected from the plugin's **Connectors** tab (also confirmed by the user's testing, 2026-11-13). Removing the plugin does not disconnect it; disconnect it separately.
- A marketplace added by the person: GitHub repositories, including GitHub Enterprise, and public repositories on GitLab and Bitbucket. An organization can limit which ones are allowed, and Claude then refuses the repository. **Check for updates** pulls changes, or **Sync automatically** keeps them current.
- On Team and Enterprise, an Owner can instead sync a private or internal github.com repository from Organization settings through the Claude GitHub App, installing the app on the repository when it is not listed ("Organization sync", https://claude.com/docs/plugins/org-sync).
- Limits: 200 MB uncompressed and 5,000 files per plugin (also the largest file **Upload plugin** accepts: 200 MB); a 512 MB marketplace repository archive; 500 plugins per marketplace; 25 marketplaces a person adds, per organization.
- On Enterprise with skill scanning on, a plugin with malicious content is blocked and a risky one shows a caution banner. On Team and Enterprise, if the organization has security scanning on, a plugin published to the organization is not listed for others until it passes, which usually takes a few minutes.
- On Team and Enterprise, a plugin the organization requires cannot be turned off or removed in Claude, nor disabled in Claude Code.
- Cowork warns before an update overwrites plugin files edited by hand.

## 8. Agent SDK

Sources: "Plugins in the SDK" (https://code.claude.com/docs/en/agent-sdk/plugins) and the changelog, 2.1.323.

- Load plugins with the `plugins` option, each entry `{ type: "local", path }`; `"local"` is the only type the SDK accepts.
- Relative paths resolve against the `cwd` option. The SDK does not expand `~`.
- The path is the plugin root: the parent of `skills/`, `agents/`, `hooks/`, `commands/` or `.claude-plugin/`.
- The SDK does not install marketplace plugins. Download the plugin and give its local path, or point at a CLI install under `~/.claude/plugins/`.
- Verify through the `system` message with subtype `init`: `plugins` (each `name` and `path`), `skills` (namespaced, such as `my-plugin:greet`) and `slash_commands`.
- A path that does not exist is skipped and the session continues, so the init message's `plugins` list is the only proof that each plugin loaded.
- A plugin missing from `plugins`: read the init message's `plugin_errors` first, then check the path, the `plugin.json` syntax, the folder's read permissions and that the folder exists. From v2.1.323, load errors of plugins enabled by managed settings also appear in `init.plugin_errors` in SDK and Desktop sessions, instead of only in the debug log.
- Skills not working: invoke them as `/plugin-name:skill-name`, confirm they appear in `skills`, and confirm each has `skills/<name>/SKILL.md`.
- Apply edits to a plugin's skills, commands, agents or hooks without a new session: call `reloadPlugins()` on the TypeScript `Query` object, or send `/reload-plugins` as a prompt in Python, which has no equivalent method.
- Add a folder to a running session: TypeScript `reloadPlugins({ addPlugins: [{ type: "local", path }] })` with an absolute path, on TypeScript Agent SDK v0.3.301 or later. Confirm the path appears in the result's `plugins`.
