# Where the session runs: terminal, cloud session or project thread

Read this file before testing or debugging a plugin when the session may not be the user's own terminal: `CLAUDE_CODE_REMOTE` is `true`, the work happens in a fresh clone, the user is at claude.ai/code, the desktop or mobile app, or the task came from a project. What loads, which commands exist and where the fix goes all change with the environment. Sources: "Use Claude Code on the web" (https://code.claude.com/docs/en/claude-code-on-the-web), "Cloud environments", section "What carries over from your setup" (https://code.claude.com/docs/en/cloud-environments), "Claude Projects" (https://code.claude.com/docs/en/claude-projects), "Skills", section "Use skills in Cowork and cloud sessions" (https://code.claude.com/docs/en/skills), and the changelog to 2.1.325.

## Contents

- 1. Find where you are
- 2. Cloud session: what loads
- 3. Project cloud thread: what loads
- 4. Testing in a cloud session or thread
- 5. Debugging in a cloud session or thread
- 6. Where each fix goes

## 1. Find where you are

1. `echo "$CLAUDE_CODE_REMOTE"`: Claude Code sets it to `true` in a cloud session, and a project's cloud threads are cloud sessions. Empty means a session on a machine: the user's terminal, IDE or desktop app, or a thread running on the user's computer through Remote Control, which uses what is installed there.
2. A cloud session started from a project carries the project's goal or instructions in its context and loads only the root `CLAUDE.md` files and rules of the project's repositories. A cloud session outside a project starts from a fresh clone of its repository and loads that repository's committed `.claude/` configuration.
3. Everything Claude runs with Bash in a cloud session, including `claude plugin ...`, acts on the session's own VM and its own `~/.claude`, never on the user's machine. A `claude plugin install` there changes nothing the user will see in their terminal, and the user's own installs are not there to inspect.

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
