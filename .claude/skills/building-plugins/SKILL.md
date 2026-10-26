---
name: building-plugins
description: Use whenever creating, adding, writing or fixing a plugin, its MCP servers, userConfig, MCP tool names and MCP hooks included, and before answering a question about MCP in plugins. Do not use for testing plugins, writing evals, CI, or a mod's hooks module.
---

# Create plugins for public GitHub marketplaces

A plugin published from a public GitHub repo is installed by people whose machines, git setup and Claude Code versions you'll never see, and nothing reviews it between your push and their install. Most broken plugins in this setting come from a handful of facts that differ from local development: users get a cached copy keyed by version, they clone with whatever git credentials they have, a plugin's `name` is its permanent identity, and the repo's default branch is the release. This skill carries those facts and the order of work that respects them.

Scope: creating a plugin of this repository and writing its manifest and components, its MCP servers included, and the hooks, agents and skills that reach their tools. Testing, evals, CI and diagnosing users' install or update errors are out of scope, and so are versioning, releasing, renaming and removing a plugin: `.claude/rules/workflow.md` names the stage for each.

## In this repository

This is the plugin-building procedure of this repository, a multi-plugin marketplace (`plugins/<name>/`, one `.claude-plugin/marketplace.json` at the root). `.claude/CLAUDE.md` and `.claude/rules/` win when they say something different, and the official docs and release notes win over all of them. The references keep the general facts that hold for any public plugin, because they explain why this repository works the way it does.

## Other skills

`.claude/rules/workflow.md` names the skill for each stage. These are the ones a plugin build meets, and when:

| Situation | Load | When |
| :-- | :-- | :-- |
| The plugin is a mod or contains one | `building-mods`, for the hooks module, what the README says about the mod, and the `mods` category | Together with this skill, from step 1 |
| A new component type changes what `docs/compatibility.md` must say | `maintaining-user-docs` | Before step 4, so the README copies the updated cells |
| The plugin is ready to ship | `release-and-versioning`, for the version, the changelog notes, the root changelog line, the pull request and the release | After step 5 (step 6) |
| The plugin has an MCP server, or a hook that matches or calls MCP tools, and Nery says it is ready | `testing-plugins`, for the live MCP checks this skill never runs | After step 5 |
| Evals are requested, or an install, load or marketplace error needs diagnosing | `testing-plugins` | After step 5, only when asked |
| The plugin is to be renamed, merged, removed or retired | `plugin-renames-and-removals` | Instead of this skill |

## Ground truth before you rely on a behavior

Claude Code ships releases every day or two and the docs lag behind them. The references here were checked on 2026-10-25 against the docs and Claude Code v2.1.310.

1. Run `claude --version`. If it's newer than 2.1.310, search the changelog (`CHANGELOG.md` in `anthropics/claude-code`) for `plugin` and `marketplace` entries after 2.1.310 before relying on a field, flag or limit here. When the changelog and the docs disagree, the changelog wins; say which one you used.
2. For a field or limit you're about to depend on, read the current page through the Claude Code Docs MCP tools first; read the raw page at `https://code.claude.com/docs/en/<page>.md` too when a heading is missing or exact wording decides, and say which text you used. The two copies can differ; `references/sources.md` says how and maps each topic to its page.
3. Run `claude plugin <subcommand> --help` for exact flags. The installed CLI is the authority.
4. Mark anything you couldn't verify as unverified and say what it affects.

## Defaults for a public plugin

These hold for what the plugin ships unless the repo's own rules say otherwise, and each has a reason:

- **Build for strangers.** Never depend on the author's machine, paths, accounts or installed tools. A required tool is a README prerequisite with how to install it, not an assumption.
- **Portable scripts.** Every executable the plugin ships starts with `#!/usr/bin/env <interpreter>` (no version), is committed executable (`100755`), and is called by path through the plugin-root variable (`CLAUDE_PLUGIN_ROOT` in dollar-brace form; `references/manifest-and-components.md` shows the exact quoting). Use the tools the user already has on `PATH`. Don't add version checks, feature probes or hand-written fallback paths: when a command fails, report it clearly and stop. Fallbacks hide breakage the user needs to see.
- **The plugin never maintains itself.** It doesn't edit its own files or update itself against docs. Keeping it current is the maintainer's work and lives in the repo, outside the plugin directory.
- **Disclose every network call and every hook** in the README. Hooks run with the user's full permissions outside the sandbox, and Claude Code's trust warning sends users to the plugin's homepage to decide whether to trust it.
- **Never push, tag, publish, open a PR or merge without the user's explicit go-ahead** for that action. A push to the default branch is a release.

## Scripts

This skill's scripts live in `.claude/skills/building-plugins/scripts/`, and the table names them by file; elsewhere in this skill, `scripts/` alone is the repository's own folder. They are maintainer tooling: they run on the maintainer's machine against this repository and never ship in a plugin, so the portable-scripts default above is not theirs. Each one is Python with its own shebang: run it by path from the repository root, never through `python3` or `node`. Each exits 0 when it passes, 1 when a check fails and 2 on wrong arguments.

The `check-*` scripts take the plugin's name. Their "Run when" column selects which of them step 5 runs; step 2 also runs two of them right after the scaffold. A check whose condition does not hold would read nothing that changed, so skipping it loses nothing. A schema check also exits 1 when uv is missing or cannot fetch `check-jsonschema`: report that and stop, never skip the check.

| Script | Run when | What it does | Fails when |
| :-- | :-- | :-- | :-- |
| `scaffold-plugin.py --name <name> --category <id> --description "<one sentence>" [--display-name "<label>"] [--claude-code-only]` | Step 2, for a new plugin | Writes `plugins/<name>/` from this skill's `assets/`: `.claude-plugin/plugin.json`, `CHANGELOG.md` at `0.1.0`, `LICENSE` and `README.md` with the plugin, repository and marketplace names filled in. It reads `marketplace.json` and `scripts/categories.json`, and never registers the plugin or touches the root README | The name is not kebab-case, passes as Anthropic's, is listed in `marketplace.json`, is a key of `renames`, or `plugins/<name>` exists; the category is not in `scripts/categories.json`. It then writes nothing, and a write that fails midway removes `plugins/<name>/`. It does not check the 64-character limit on names |
| `check-required-files.py <plugin>` | Right after `scaffold-plugin.py`, and whenever one of the four required files is added, moved, renamed, deleted or replaced by a symlink. Not for an edit inside them, nor for any other file | Checks that `plugins/<plugin>/` holds `.claude-plugin/plugin.json`, `README.md`, `CHANGELOG.md` and `LICENSE` as regular files inside the repository | A file is missing, a broken symlink, not a regular file or a symlink that leaves the repository |
| `check-manifest-schema.py <plugin>` | Right after `scaffold-plugin.py`, and whenever `plugin.json` changes, its inline `hooks`, `mcpServers` and `lspServers` included. Not when `plugin.json` is untouched | Validates `plugin.json` against `scripts/schemas/plugin-manifest-schema/plugin-manifest.schema.json`. It runs `check-jsonschema` through `uv run --with`, so it needs uv, and the network the first time | The manifest is missing, leaves the repository, repeats a key, or has an unknown, missing, empty or mistyped field |
| `check-mcp-schema.py <plugin>` | When the plugin has `.mcp.json` or `mcpServers` names a `.json` file, and that file or the `mcpServers` field changed. Not for a plugin with no MCP file | Validates `.mcp.json` and each `.json` file `mcpServers` names against `scripts/schemas/plugin-manifest-schema/mcp/mcp.schema.json`, the same way | A named file leaves the plugin or does not exist, a file repeats a key, or a server breaks the schema |
| `check-lsp-schema.py <plugin>` | When the plugin has `.lsp.json` or `lspServers` names a `.json` file, and that file or the `lspServers` field changed. Not for a plugin with no LSP file | Validates `.lsp.json` and each `.json` file `lspServers` names against `scripts/schemas/plugin-manifest-schema/components/lsp-servers.schema.json`, the same way | A named file leaves the plugin or does not exist, a file repeats a key, or a server breaks the schema |
| `check-skill-names.py <plugin>` | When a skill is added, renamed or moved, a `SKILL.md` frontmatter changes, or `skills` in `plugin.json` changes. Not for an edit to a skill's body or its other files | Checks that each skill under `skills/`, and under each directory `skills` in `plugin.json` names, has one `name:` line equal to its directory name, kebab-case and at most 64 characters | A `SKILL.md` has no frontmatter, no `name` or two, or a `name` that is not its directory name written alone and plain |

## Workflow

Copy this checklist and tick steps as you go. Steps 1 and 2 are for a new plugin; steps 3–6 repeat for each later change.

- [ ] 1. **Settle the plugin's identity** — name, category, description, display name and surfaces. Ask Nery for any the request does not give, because the name is permanent and the rest is what users see first:
  - **Name**: the identity users type and their settings store, and the prefix of every skill and agent. Kebab-case, at most 64 characters, and clear of the reserved-name rules in `references/repo-layouts.md` → Names. The scaffold refuses a name that breaks a rule it checks, but not one that is too long.
  - **Category**: one `id` of `scripts/categories.json`, chosen by the plugin's purpose; `mods` only for a mod (`.claude/CLAUDE.md` → Plugin Categories).
  - **Description**: one sentence on what it does for the user.
  - **Display name**: the label users read; without one, the scaffold capitalizes each word of the name.
  - **Surfaces**: both Claude Code and the Claude app, or Claude Code only (`--claude-code-only`) when a component the plugin needs loads only in Claude Code, as `docs/compatibility.md` states per component type.

  This repository is a multi-plugin marketplace (`plugins/<name>/`) named `the-claude-factory`; `references/repo-layouts.md` explains the general rules behind that layout and the names.
- [ ] 2. **Create the plugin** — run `node scripts/generators/marketplace.mjs --check` (a repository tool). If it fails, the existing plugins and `marketplace.json` are out of step: stop and report it, and scaffold nothing. Then run `scaffold-plugin.py`, then `check-required-files.py` and `check-manifest-schema.py` on the new plugin, so a broken scaffold shows before you write components. Then run `npm run generate`, the repository's maintenance step: `marketplace.mjs` registers the plugin in `marketplace.json`, then `catalog.mjs` updates the root README catalog. If it fails, delete `plugins/<name>/` and run `node scripts/generators/marketplace.mjs` so `marketplace.json` drops the entry it may have written, fix the cause, and scaffold again. `references/templates.md` says what each asset in `assets/` becomes and how to fill and change it.
- [ ] 3. **Write the components** — read `references/manifest-and-components.md`, then the official page for each component type you write (skills, agents, hooks, MCP, LSP). For an MCP server, its `userConfig`, or an agent, skill or permission rule that names MCP tools, read `references/mcp-servers.md` and work through its order; for a hook that matches MCP tools or calls one, a server's connection state, authentication or timeouts, also read `references/mcp-hooks-and-lifecycle.md`. A plugin that is a mod or contains one also loads `building-mods`, which owns the hooks module, its README items and the `mods` category (`.claude/rules/workflow.md`).
- [ ] 4. **Make it public-ready** — install line, LICENSE, no secrets, disclosures, surfaces it supports. Read `references/public-readiness.md`, and fill the README the scaffold wrote from `assets/README-template.md`, in the style of `references/readme-style.md`: resolve every `<!-- TODO -->` comment, and take each Compatibility cell from `docs/compatibility.md`. When the plugin bundles or derives from third-party material, write `NOTICE.txt` from `assets/NOTICE-template.txt`, as `references/templates.md` says.
- [ ] 5. **Validate** — run each of this skill's checks whose "Run when" condition the change meets, in the Scripts table's order, fixing each failure before the next. A new plugin meets every condition its files can: all the checks, except `check-mcp-schema.py` without an MCP file, `check-lsp-schema.py` without an LSP file and `check-skill-names.py` without a skill. When the category, the surfaces, the minimum Claude Code version or the description changed, run `npm run generate` again. Then `claude plugin validate --strict` on the plugin directory and `claude plugin validate .` at the marketplace root; fix every error. Read `references/validation-messages.md` for what each message means and what validation won't catch.
- [ ] 6. **Hand over to the release stage** — this skill never bumps, tags or pushes. When the plugin is ready to ship, the release stage of `.claude/rules/workflow.md` takes its version, changelog, PR and publication; `references/versioning-and-release.md` explains how users receive a version.

## Facts that cause most broken releases

Keep these in view even when you don't open a reference:

- **Version decides delivery.** Users stay on their cached copy until the `version` in `plugin.json` changes, however many commits you push. Every plugin of this repository sets it, and never in the marketplace entry.
- **The marketplace name comes from `marketplace.json`, not the repo name.** Users install `<entry-name>@<marketplace-name>`. Keep each entry's `name` identical to its `plugin.json` `name`.
- **Names are forever.** Renaming a published plugin breaks every install unless the marketplace's `renames` map migrates it. Change `displayName` for a new label.
- **Only manifests go in `.claude-plugin/`** — `plugin.json`, plus `marketplace.json` at the marketplace root. Components live at the plugin root, and every manifest path starts with `./` and stays inside the plugin, because users get a copy of the plugin directory and nothing outside it.
- **Users may have no GitHub SSH key.** Tell them in the README to set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`, because installs from `/plugin` inside a session and plugin updates don't fall back to HTTPS on their own.
- **Auto-update is off** for third-party marketplaces. Most users get your fix only when they run `claude plugin update`, so ship fixes as new versions and say how to update in the README.
- **A top-level `bin/` stops claude.ai and Cowork from installing the plugin.** Put executables under the plugin's own `scripts/` unless the plugin is Claude Code-only on purpose.
- **Git LFS files arrive as pointer files**, and symlinks that leave the marketplace are skipped. Commit real files.
- **A plugin's MCP tools are scoped.** They are named `mcp__plugin_<plugin>_<server>__<tool>`, and a matcher, `tools` entry or permission rule on the bare server key never matches.

## What to hand back

The files written or changed, the raw output of each check and `claude plugin validate` run, the checks you skipped and the condition that did not hold, decisions the user still has to make (name, category, surfaces), and anything unverified.
