# plugin.json and components

Checked 2026-10-25 against `/en/plugins/create`, `/en/plugins/components`, `/en/plugins/manifest-reference`, `/en/skills`, and claude.com `/docs/plugins/platform-support` (Claude Code v2.1.310). Before writing a component, read its own official page (table at the end); this file holds only what goes wrong in plugins.

## Contents
- Layout rules
- plugin.json for a public plugin
- Paths and path variables
- Components: what to know per type
- What loads on which surface
- Pages to read per component

## Layout rules

- Only manifests go in `.claude-plugin/`: `plugin.json`, and in a single-plugin repo also `marketplace.json`. A component saved there doesn't load.
- Component directories sit at the plugin root: `skills/<name>/SKILL.md`, `commands/*.md` (older form; use skills), `agents/*.md`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `output-styles/`, `themes/`, `monitors/monitors.json`, `bin/`, `settings.json`.
- A `CLAUDE.md` at the plugin root is not loaded (`validate` warns). Put instructions in a skill; put rules that must always hold in a hook.
- A `SKILL.md` at the plugin root loads as one skill only when there is no `skills/` directory and no `skills` key; give it a `name`, or a marketplace install names it after its cache directory.

## plugin.json for a public plugin

```json
{
  "name": "deploy-helper",
  "displayName": "Deploy Helper",
  "version": "0.1.0",
  "description": "What it does for the user, in one sentence.",
  "author": { "name": "Your Name", "url": "https://github.com/you" },
  "homepage": "https://github.com/you/deploy-helper#readme",
  "repository": "https://github.com/you/deploy-helper",
  "license": "MIT",
  "keywords": ["deploy", "ci"]
}
```

- `name` is the only required field. See `repo-layouts.md` → Names.
- `homepage` must parse as a URL or the plugin **fails to load**. `repository` isn't validated.
- `version`: either set it and bump it on every release, or omit it (and keep it out of the marketplace entry) so the git commit SHA is the version. See `versioning-and-release.md`. `validate --strict` fails on a missing `version`, so run it without `--strict` if you omit it on purpose.
- `license` (SPDX) or a `LICENSE` file; Anthropic's directory requires one of them.
- `metadata` (v2.1.222+) is free-form and ignored by Claude Code. Directory-listing fields `icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl`, `termsOfServiceUrl` are read only by Anthropic's directory; before v2.1.281 `validate` flagged them as unknown, so a `--strict` run on an older CLI fails.
- `defaultEnabled: false` makes an install leave the plugin off. Once a user's `enabledPlugins` entry exists, later changes to `defaultEnabled` don't affect them.
- `dependencies`: other plugins that must be enabled; bare names resolve in the same marketplace. Cross-marketplace dependencies install only if the marketplace lists the other in `allowCrossMarketplaceDependenciesOn`. Version ranges resolve against `<name>--v<version>` git tags (`/en/plugins/dependencies`).
- `userConfig`: values Claude Code asks the user for. Keys are identifiers; each option needs `type`, `title`, `description`; unknown option keys fail validation. `"sensitive": true` masks input and stores it in the platform's secure credential store (keychain on macOS, a protected credentials file elsewhere) instead of `settings.json`. `options` (fixed choices) makes the plugin unloadable before v2.1.271. `claude plugin install` from the shell never prompts; users pass `--config KEY=VALUE`, pipe JSON to `claude plugin configure --values-stdin`, or run `/plugin configure <plugin>@<marketplace>` in a session.
- `settings` / root `settings.json`: only `agent` and `subagentStatusLine` take effect.
- Component keys: `skills` adds to the default `skills/` scan; `commands`, `agents`, `outputStyles`, `workflows`, `experimental.themes`, `experimental.monitors` **replace** their default folder; `hooks`, `mcpServers`, `lspServers` merge with their default file. Don't list `hooks/hooks.json` in `hooks` — it loads automatically.

## Paths and path variables

- Every component path starts with `./`, uses forward slashes, and resolves inside the plugin. `..`, symlinks that leave the plugin (except within one marketplace), and backslashes on macOS/Linux are rejected with `path escapes plugin directory`.
- An installed plugin is a **copy** in `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. Files outside the plugin directory aren't copied, so a script reading `../shared` finds nothing for users even though it works in your checkout.
- `${CLAUDE_PLUGIN_ROOT}`: the installed version's directory. It changes on every update — never write state there.
- `${CLAUDE_PLUGIN_DATA}`: `~/.claude/plugins/data/<id>/`, survives updates; for `node_modules`, venvs, caches. Deleted on the last uninstall unless `--keep-data`.
- `${CLAUDE_PROJECT_DIR}`: the user's project root.
- Where they resolve: hook `command`/`args`, MCP stdio `command`/`args`/`env`, MCP remote `url`/`headers`/`headersHelper`, LSP fields, monitor `command`, and the Markdown body of skills, commands and agents. Hook, LSP and MCP stdio processes also get all three in their environment. The changelog added `CLAUDE_PROJECT_DIR` for MCP stdio servers, and `/en/mcp` says so; the variables table in `/en/plugins/manifest-reference` still lists only the other two for them, and the changelog wins.
- They are **not** in the environment of commands Claude runs with the Bash tool. In a skill, write the reference in `SKILL.md` itself; Claude Code substitutes it when the skill loads. Substitution is documented only for the skill's Markdown content and its `allowed-tools`, so don't rely on it in files under `references/` (unverified either way; keep commands that use the variables in `SKILL.md`).
- `${CLAUDE_SKILL_DIR}` is the skill's own directory (inside the plugin), useful for scripts bundled next to `SKILL.md`.
- Quoting: in a shell-form hook (`command` without `args`) wrap the path in double quotes, `"\"${CLAUDE_PLUGIN_ROOT}\"/scripts/x.sh"`; `validate` warns when it's unquoted. Exec form (`args`) needs no quoting.
- `${user_config.KEY}` is rejected in shell-form hook commands, monitor commands and MCP `headersHelper`. Use exec-form `args` or read `CLAUDE_PLUGIN_OPTION_<KEY>` from the hook environment.

## Components: what to know per type

**Skills.** Command name is `/<plugin>:<directory>` (frontmatter `name` replaces the last segment). Claude picks a skill by its `description`, so write it as the situations a user is in. Use `disable-model-invocation: true` only for skills that should run solely on explicit command.

**Agents.** Named `<plugin>:<name>`; subfolders add segments (`agents/review/security.md` → `my-plugin:review:security`). Supported frontmatter: `name`, `description`, `model`, `effort`, `maxTurns`, `autoCompactWindow`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `omitClaudeMd`, `isolation` (`"worktree"` only), `color`, `experimental.cacheTtl`. **Ignored in plugin agents:** `permissionMode`, `hooks`, `mcpServers`, `initialPrompt` — declare hooks and servers at plugin level. Unparseable frontmatter still loads with every field ignored; `validate` finds it.

**Hooks.** `hooks/hooks.json` with a top-level `"hooks"` key, same shape as settings. Plugin hooks register when the plugin loads and fire on every matching event from then on, not only when the plugin's skills run — narrow the `matcher`. A hook on the plugin's own MCP tool must match `mcp__plugin_<plugin>_<server>__<tool>`. Hooks have no prefix, so the same hook in user settings and the plugin runs twice. Read `/en/hooks` for events, exit codes and JSON output before writing one.

**MCP servers.** `.mcp.json` at the root (the `mcpServers` wrapper is optional). Server shows as `plugin:<plugin>:<server>`; tools as `mcp__plugin_<plugin>_<server>__<tool>`. Never put secrets in it — every user receives the file; use `userConfig` with `sensitive: true` and `${user_config.KEY}`. A remote `https://` server also reaches claude.ai and Cowork users as a connector; a local stdio server runs only in Claude Code and local Cowork. Start a local server by running a file in the plugin (`node ${CLAUDE_PLUGIN_ROOT}/server.js`), not through `npx`/`uvx` launchers that fetch code at runtime. Before writing one, read `mcp-servers.md`.

**LSP servers.** `.lsp.json` or `lspServers`. See `/en/plugins/code-intelligence`; the language server binary is a user prerequisite to document.

**Executables (`bin/`).** On the Bash tool's `PATH` while enabled, after the user's own entries (can't shadow system commands). A top-level `bin/` makes claude.ai and Cowork refuse the whole plugin; use `scripts/` and call by path unless the plugin is Claude Code-only by design.

**Node dependencies.** Claude Code installs them into the cached copy only when the plugin root has `package.json` plus a supported lockfile: text `bun.lock` (lockfileVersion ≤ 2), `npm-shrinkwrap.json` or `package-lock.json` (lockfileVersion 2 or 3). `bun.lockb`, `yarn.lock`, `pnpm-lock.yaml` get no install. Registry packages pinned exactly, no lifecycle scripts, 60 s timeout, no `overrides`. Anything else (Python deps, native builds) installs from a `SessionStart` hook into `${CLAUDE_PLUGIN_DATA}`. `package.json` plus a lockfile in the plugin root is held for review if you submit to Anthropic's directory.

**Monitors.** Background shell commands with full user permissions; not started under `-p`; never receive `${user_config.*}`.

**Mods.** A plugin whose `hooks/hooks.json` lists a JavaScript module under `modules` (v2.1.287+). Read `/en/plugins/mods/overview`, `create`, `api`, `events`, `interface` and `reference` before writing one. Mods publish through a marketplace exactly like other plugins.

## What loads on which surface

The same folder installs in Claude Code, claude.ai chat and Cowork, each loading a subset (claude.com `/docs/plugins/platform-support`):

| Component | Chat | Cowork | Claude Code |
| :-- | :-- | :-- | :-- |
| Skills | Loads | Loads | Loads |
| Commands | As a skill | Loads | Loads |
| Agents, hooks | Ignored | Loads | Loads |
| Remote MCP (`http`/`sse` fixed URL) | Connectors tab | Connectors tab | Loads |
| Local MCP (stdio, `.mcpb`) | Ignored | Local sessions only | Loads |
| MCP with `${user_config.*}` | Ignored if in URL | Ignored if no default | Loads, prompts |
| Top-level `bin/` | **Refuses plugin** | **Refuses plugin** | Loads |
| LSP, output styles, themes, `settings` | Ignored | Ignored | Loads |

If the plugin is Claude Code-only, say so in the README so app users aren't surprised.

## Pages to read per component

| Writing | Read first (Claude Code Docs MCP path, or `https://code.claude.com/docs/en/<page>.md`) |
| :-- | :-- |
| Any component, layout | `/en/plugins/components`, `/en/plugins/manifest-reference` |
| Skills | `/en/skills` |
| Agents | `/en/sub-agents` |
| Hooks | `/en/hooks`, `/en/hooks-guide` |
| MCP servers | `/en/mcp`, then `mcp-servers.md` and `mcp-hooks-and-lifecycle.md` in this skill |
| LSP | `/en/plugins/code-intelligence` |
| Output styles | `/en/output-styles` |
| Mods | `/en/plugins/mods/*` |
| Dependencies, loading, cache | `/en/plugins/dependencies`, `/en/plugins/loading` |
