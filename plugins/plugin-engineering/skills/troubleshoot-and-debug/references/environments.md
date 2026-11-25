# Where the session runs

What loads in a cloud session, a project's cloud thread, Claude on the web, desktop and mobile, Cowork and the Agent SDK, and where each fix goes when the session is not the user's own terminal.

## Contents

- [Gotchas](#gotchas)
- [Cloud sessions](#cloud-sessions)
- [Project cloud threads](#project-cloud-threads)
- [Claude and Cowork](#claude-and-cowork)
- [The Agent SDK](#the-agent-sdk)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- A cloud session's `claude plugin` commands act on the session's VM, not on the user's machine: a fix that must reach the user's machine goes to them as a command to run.
- A repository's `extraKnownMarketplaces` are never added in cloud sessions or project threads; plugins turned on for the user's claude.ai account reach both.
- Claude's chat ignores a plugin's agents and hooks; any program a hook calls must be installed where the hook runs.
- In the Agent SDK, a missing plugin path is skipped without an error: read `plugin_errors`.

## Cloud sessions

`CLAUDE_CODE_REMOTE` is `true` in a cloud session, which starts on a fresh VM.

- Carried over: the repository's `CLAUDE.md`, `.claude/rules/`, `.claude/skills/`, `.claude/agents/` and `.claude/commands/`; in a one-repository session, `.claude/settings.json` hooks and permissions and `.mcp.json`; and the organization's server-managed settings, except in Claude Tag sessions.
- Not carried over: marketplaces the repository declares in `extraKnownMarketplaces`, because adding them needs the workspace trust dialog, which an Anthropic-hosted session doesn't show; the user's `~/.claude/` files, plugins only the user's settings enable, MCP servers added with `claude mcp add` at local or user scope, managed files on a machine, transport variables such as `NODE_EXTRA_CA_CERTS` in the repository's `env`, and interactive sign-ins such as AWS SSO. A multi-repository session reads only `enabledPlugins` and `extraKnownMarketplaces` from each repository, and still adds none of its marketplaces.
- Plugins synced from claude.ai appear as `<name>@synced`, never override a same-named installed plugin, and their `SessionStart` hooks run in new cloud sessions. Cloud sessions retry plugins that failed to download, and show a notice when a marketplace can't be fetched because its repository isn't one of the session's.
- A plugin suggestion card's **Add** turns the plugin on for the claude.ai account; deny `SearchPlugins` and `SuggestPluginInstall` in `permissions` to stop the cards.
- Fix a cloud problem in what carries over: the repository's `.claude/` files, the environment's setup script for binaries a hook or server needs, or the plugin on the claude.ai account.

## Project cloud threads

- A thread loads the repositories' root `CLAUDE.md`, `.claude/CLAUDE.md` and `.claude/rules/` (rules with `paths` don't load at the start), and the skills, agents and commands under `.claude/`, except in a thread started before October 1, 2026, a repository whose name starts with a dot, or a self-hosted thread. It never loads `.mcp.json`, permission rules, hooks or `env`.
- Plugins reach a thread when the user enables them for their claude.ai account at `claude.ai/customize/plugins`. A change to project settings reaches new threads, not running ones.
- A thread runs on the user's own computer only through Remote Control.

## Claude and Cowork

| Component | Chat (web, desktop, mobile) | Cowork | Claude Code |
| :-- | :-- | :-- | :-- |
| Skills, commands | load; commands as skills | load; commands as `/<plugin>:<command>` | load |
| Agents, hooks | ignored | run | run |
| Remote MCP server with a fixed URL | on the Connectors tab | on the Connectors tab | loads |
| Local MCP server, `.mcpb` | not available | only Cowork on the user's computer | loads |
| `${user_config.*}` in MCP | ignored | ignored without a default | substituted |
| LSP servers, output styles, themes, `settings` | not available | not available | load |
| A top-level `bin/` | the plugin can't be installed | the plugin can't be installed | on the Bash tool's `PATH` |

- Users add plugins in Claude under **Customize** > **Plugins** (the help center calls the page **Plugins**); installing never adds or signs in to a connector, and removing a plugin doesn't disconnect it.
- Limits: 25 self-added marketplaces per account per organization, from GitHub or GitHub Enterprise, public GitLab or Bitbucket; 5,000 files and 200 MB per plugin and per uploaded file.
- An upload fails with `plugin.json must be at .claude-plugin/plugin.json at the zip root (or inside a single top-level directory)` when the zip's layout is wrong.
- On an organization plan, Cowork and Skills must both be enabled before plugin marketplaces work, and turning Skills off stops the sync to Claude Code and removes plugins already synced there. Required plugins can't be removed, and Cowork warns before an update overwrites files the user edited.
- Claude's plugins sync to Claude Code once per start, one way; never with an API key or a cloud provider.

## The Agent SDK

- Plugins load only from `plugins: [{ type: "local", path }]`: the path is the plugin root, relative to `cwd`, with no `~` expansion. The SDK doesn't install marketplace plugins; point it at an installed copy under `~/.claude/plugins/` instead.
- Check the `system` `init` message: `plugins`, `skills` and `slash_commands` list what loaded, and `plugin_errors` what didn't, with a `path` for `--plugin-dir` failures and the load errors of managed-enabled plugins.
- Reload with `reloadPlugins()` in TypeScript, which also takes `addPlugins` with absolute paths, or by sending `/reload-plugins` as a prompt in Python.
- In `-p` and the SDK, plugins from managed settings with their own git repository are fetched in the background, so a short run can exit before they load.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [What carries over from your setup](https://code.claude.com/docs/en/cloud-environments#what-carries-over-from-your-setup) when a cloud session lacks a plugin or file. It gives each item that does and doesn't carry over.
- Read [What threads pick up from your repositories](https://code.claude.com/docs/en/claude-projects#what-threads-pick-up-from-your-repositories) when a project thread lacks a skill or plugin. It gives what threads load and the cases that skip it.
- Read [Platform support](https://claude.com/docs/plugins/platform-support) when the plugin runs in Claude or Cowork. It gives each component's support and the limits.
- Read [Plugins in the Agent SDK](https://code.claude.com/docs/en/agent-sdk/plugins) when an application embeds the plugin. It gives the `plugins` option, the `init` fields and reloads.

## Exit

The surface's rule explains what loaded there, and the fix goes where that surface reads it. Return to step 4 of the diagnosis in `SKILL.md`.
