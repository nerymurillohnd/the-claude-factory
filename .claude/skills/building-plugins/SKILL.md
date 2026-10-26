---
name: building-plugins
description: Use whenever creating, adding, writing or fixing a plugin. Do not user for testing plugins, writing evals, CI, or mods.
---

# Create plugins for public GitHub marketplaces

A plugin published from a public GitHub repo is installed by people whose machines, git setup and Claude Code versions you'll never see, and nothing reviews it between your push and their install. Most broken plugins in this setting come from a handful of facts that differ from local development: users get a cached copy keyed by version, they clone with whatever git credentials they have, a plugin's `name` is its permanent identity, and the repo's default branch is the release. This skill carries those facts and the order of work that respects them.

Scope: designing, writing and publishing the plugin. Testing, evals, CI and diagnosing users' install or update errors are out of scope; leave them to the repo's own procedures or to whatever the user uses for that.

## Precedence

If the repository has its own project instructions for plugin work (a `CLAUDE.md`, `.claude/rules/`, or project skills such as `plugin-development` or `release-and-versioning`), follow them and use this skill only for what they leave out. Project rules know the repo's scripts and decisions; this skill is the general case.

## Ground truth before you rely on a behavior

Claude Code ships releases every day or two and the docs lag behind them. The references here were checked on 2026-10-25 against the docs and Claude Code v2.1.310.

1. Run `claude --version`. If it's newer than 2.1.310, search the changelog (`CHANGELOG.md` in `anthropics/claude-code`) for `plugin` and `marketplace` entries after 2.1.310 before relying on a field, flag or limit here. When the changelog and the docs disagree, the changelog wins; say which one you used.
2. For a field or limit you're about to depend on, read the current page through the Claude Code Docs MCP tools, or the raw page at `https://code.claude.com/docs/en/<page>.md`. The two copies can differ; `references/sources.md` says how and maps each topic to its page.
3. Run `claude plugin <subcommand> --help` for exact flags. The installed CLI is the authority.
4. Mark anything you couldn't verify as unverified and say what it affects.

## Defaults for a public plugin

These hold unless the user or the repo's own rules say otherwise, and each has a reason:

- **Build for strangers.** Never depend on the author's machine, paths, accounts or installed tools. A required tool is a README prerequisite with how to install it, not an assumption.
- **Portable scripts.** Every executable starts with `#!/usr/bin/env <interpreter>` (no version), is committed executable (`100755`), and is called by path through the plugin-root variable (`CLAUDE_PLUGIN_ROOT` in dollar-brace form; `references/manifest-and-components.md` shows the exact quoting). Use the tools the user already has on `PATH`. Don't add version checks, feature probes or hand-written fallback paths: when a command fails, report it clearly and stop. Fallbacks hide breakage the user needs to see.
- **The plugin never maintains itself.** It doesn't edit its own files or update itself against docs. Keeping it current is the maintainer's work and lives in the repo, outside the plugin directory.
- **Disclose every network call and every hook** in the README. Hooks run with the user's full permissions outside the sandbox, and Claude Code's trust warning sends users to the plugin's homepage to decide whether to trust it.
- **Never push, tag, publish, open a PR or merge without the user's explicit go-ahead** for that action. A push to the default branch is a release.

## Workflow

Copy this checklist and tick steps as you go. Steps 3–6 repeat for each later change.

- [ ] 1. **Pick the repo layout** — single-plugin repo or multi-plugin marketplace. Read `references/repo-layouts.md`.
- [ ] 2. **Choose permanent names** — plugin `name` and marketplace `name`. Both are identities users type and their settings store; check them against the reserved-name rules in `references/repo-layouts.md` before writing anything else.
- [ ] 3. **Write the plugin** — manifest and components. Read `references/manifest-and-components.md`, then the official page for each component type you write (skills, agents, hooks, MCP, LSP).
- [ ] 4. **Make it public-ready** — README with install line, LICENSE, no secrets, disclosures, surfaces it supports. Read `references/public-readiness.md`; start the README from `assets/README-template.md`.
- [ ] 5. **Decide versioning** — bump or omit `version`, changelog, tag only if needed; for a rename or removal, the `renames` map. Read `references/versioning-and-release.md` before the first release and before every later one.
- [ ] 6. **Validate** — `claude plugin validate --strict` on each plugin directory (without `--strict` for a plugin that omits `version` on purpose) and `claude plugin validate .` at the marketplace root; fix every error. Read `references/validation-messages.md` for what each message means and what validation won't catch.
- [ ] 7. **Publish with approval** — list exactly what the push publishes (which plugins, which versions), get a yes, then push.

## Facts that cause most broken releases

Keep these in view even when you don't open a reference:

- **Version decides delivery.** If `plugin.json` sets `version`, users stay on their cached copy until that string changes, however many commits you push. Either bump it on every release or omit it everywhere so the commit SHA becomes the version. Never set it in both `plugin.json` and the marketplace entry.
- **The marketplace name comes from `marketplace.json`, not the repo name.** Users install `<entry-name>@<marketplace-name>`. Keep each entry's `name` identical to its `plugin.json` `name`.
- **Names are forever.** Renaming a published plugin breaks every install unless the marketplace's `renames` map migrates it. Change `displayName` for a new label.
- **Only manifests go in `.claude-plugin/`** — `plugin.json`, plus `marketplace.json` in a single-plugin repo. Components live at the plugin root, and every manifest path starts with `./` and stays inside the plugin, because users get a copy of the plugin directory and nothing outside it.
- **Users may have no GitHub SSH key.** Tell them in the README to set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`, because installs from `/plugin` inside a session and plugin updates don't fall back to HTTPS on their own.
- **Auto-update is off** for third-party marketplaces. Most users get your fix only when they run `claude plugin update`, so ship fixes as new versions and say how to update in the README.
- **A top-level `bin/` stops claude.ai and Cowork from installing the plugin.** Put executables under `scripts/` unless the plugin is Claude Code-only on purpose.
- **Git LFS files arrive as pointer files**, and symlinks that leave the marketplace are skipped. Commit real files.

## What to hand back

The files written or changed, the raw output of each `claude plugin validate` run, what the next push would publish (plugin names and versions), decisions the user still has to make (name, license, versioning style), and anything unverified.
