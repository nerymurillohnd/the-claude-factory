# Sources and how to re-verify them

Every reference file in this skill was checked on **2026-10-25** against Claude Code **v2.1.310** (the newest `CHANGELOG.md` entry that day). Re-verify anything you're about to rely on when the installed CLI is newer.

## Where to read the current truth

| Source                 | How to reach it                                                                                               | Notes                                                                                                                                                                                                                                                                |
| :--------------------- | :------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Installed CLI          | `claude --version`, `claude plugin <cmd> --help`                                                              | Authority for flags                                                                                                                                                                                                                                                  |
| Release notes          | `CHANGELOG.md` in `github.com/anthropics/claude-code`                                                         | Ahead of the docs; wins when they disagree                                                                                                                                                                                                                           |
| Claude Code docs       | Claude Code Docs MCP (`/en/<page>.mdx`) or `https://code.claude.com/docs/en/<page>.md`                        | On 2026-10-25 the two copies differed: the MCP copy was the newer text but was missing whole sections of some pages (e.g. `/en/plugins/troubleshooting` → "Build a plugin", "Host a marketplace"). When a heading is missing or wording decides something, read both |
| claude.com plugin docs | `https://claude.com/docs/plugins/<page>`                                                                      | claude.ai/Cowork behavior, directory submission                                                                                                                                                                                                                      |
| Real marketplaces      | `anthropics/claude-plugins-official`, `anthropics/claude-plugins-community`, `anthropics/claude-code/plugins` | Working layouts to compare against                                                                                                                                                                                                                                   |

## Pages by topic

| Topic                                                            | Page                                                                                                   |
| :--------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------- |
| Build a first plugin, convert a `.claude/` setup                 | `/en/plugins/create`                                                                                   |
| Components and plugin explorer                                   | `/en/plugins/components`                                                                               |
| `plugin.json` fields, path rules, env vars, `userConfig`         | `/en/plugins/manifest-reference`                                                                       |
| Loading, cache, versions, auto-update, Node deps                 | `/en/plugins/loading`                                                                                  |
| `marketplace.json`, sources, reserved names, validation messages | `/en/plugins/marketplace-reference`                                                                    |
| Build a marketplace                                              | `/en/plugins/create-marketplace`                                                                       |
| Host, private access, releases, renames, channels                | `/en/plugins/host-marketplace`                                                                         |
| Publish routes, release prep, directory                          | `/en/plugins/publish`                                                                                  |
| User-side install commands                                       | `/en/plugins/install`                                                                                  |
| Plugin dependencies, release tags                                | `/en/plugins/dependencies`                                                                             |
| CLI: `plugin validate`, `tag`, `init`, `marketplace add`         | `/en/plugins/cli-reference`                                                                            |
| Security model, trust tiers                                      | `/en/plugins/security`                                                                                 |
| Validation and build error messages                              | `/en/plugins/troubleshooting` ("Build a plugin", "Host a marketplace"), `/en/errors`                   |
| Suggest plugins by project, cost and usage, CLI hints            | `/en/plugins/relevance`, `/en/plugins/measure`, `/en/plugins/cli-hints`                                |
| Org rollout, managed settings                                    | `/en/plugins/org`                                                                                      |
| LSP                                                              | `/en/plugins/code-intelligence`                                                                        |
| Mods                                                             | `/en/plugins/mods/overview`, `create`, `api`, `events`, `interface`, `reference`                       |
| Skills, agents, hooks, MCP                                       | `/en/skills`, `/en/sub-agents`, `/en/hooks`, `/en/hooks-guide`, `/en/mcp`                              |
| MCP timeouts, plugin MCP servers that don't start                | `/en/env-vars`, `/en/plugins/troubleshooting` ("Invalid MCP server config")                            |
| What loads where (chat, Cowork, Code)                            | claude.com `/docs/plugins/platform-support`                                                            |
| Folder structure for every app                                   | claude.com `/docs/plugins/build`                                                                       |
| Directory rules and submission                                   | claude.com `/docs/plugins/pre-submission-checklist`, `/docs/plugins/submit`, `/docs/directory/publish` |

## Version notes used in this skill

From `CHANGELOG.md` and the docs:

| Version           | Change                                                                                                    |
| :---------------- | :-------------------------------------------------------------------------------------------------------- |
| 2.1.222           | `metadata` field in `plugin.json` and entries                                                             |
| 2.1.224 / 2.1.229 | `archive` / `command` plugin sources                                                                      |
| 2.1.238 / 2.1.239 | Entry `headers`/`headersHelper` / `metadata.pluginRoot`                                                   |
| 2.1.259           | `claude plugin validate --json`                                                                           |
| 2.1.265           | `--plugin-dir` accepts a folder of plugins                                                                |
| 2.1.271           | `userConfig` `options` (older versions can't load such plugins)                                           |
| 2.1.275           | `/plugin install <p> --marketplace <src>` in a session; `npm`/`pip`/`github`/… reserved marketplace names |
| 2.1.280           | `CLAUDE_CODE_PLUGIN_DIRS`; other spellings of reserved names refused                                      |
| 2.1.281           | `validate` checks `.mcp.json`; directory-listing fields no longer "unknown"                               |
| 2.1.287           | Mods                                                                                                      |
| 2.1.288           | Shell `claude plugin install` falls back to HTTPS without an SSH key                                      |
| 2.1.289           | `validate` on a dir with both manifests checks both                                                       |
| 2.1.290           | A marketplace named after another GitHub marketplace's `<owner>-<repo>` download folder is refused        |
| 2.1.292           | `claude plugin install <p> --marketplace <src>`                                                           |
| 2.1.295           | `validate` prints a README install line when missing; only plugin-holding submodules are fetched          |
| 2.1.296           | JS member names refused as marketplace names; shell install falls back to HTTPS on Windows                |
