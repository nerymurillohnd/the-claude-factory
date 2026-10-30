# Getting and exercising a mod that comes from a public GitHub marketplace

Only what is needed to obtain, locate and exercise a mod. Sources: https://code.claude.com/docs/en/plugins/install, /plugins/marketplace-reference, /plugins/loading (fetched in this skill's authoring session, Claude Code 2.1.310). Generic plugin install problems (skills, agents, MCP, non-mod plugins) are out of scope.

## Marketplace and plugin identity

- Marketplace file: `.claude-plugin/marketplace.json` at the marketplace root (the directory that contains `.claude-plugin/`). Required top-level: `name`, `owner`, `plugins`. A plugin id is `<plugin>@<marketplace>`.
- Entry `source` says where the plugin comes from. In scope here: relative path (`"./plugins/x"`, resolved from the marketplace root, not from `.claude-plugin/`; bare names resolve under `metadata.pluginRoot`, v2.1.239+), `github` (`repo`, `ref`, `sha`), `url` (git URL on github.com; `ref`, `sha`), `git-subdir` (`url`, `path`, `ref`, `sha`). `npm`, `archive`, `command` sources are out of scope. `sha` wins over `ref` when both are set.
- A relative-path source only resolves when Claude Code has the marketplace's files, which is the case for `github`/`git` marketplaces and not for a bare hosted `marketplace.json` URL.
- `strict` (default `true`): with a `plugin.json` present, entry `hooks` matchers _replace_ the manifest's per event; with `strict: false` any entry component field makes the plugin fail with `has conflicting manifests`. Entry-level `hooks` written as a file path or array passes `validate` but never runs (`not yet supported in a marketplace entry`); file-based hooks, including a mod's `hooks/hooks.json` with `modules`, belong in the plugin's own files.
- Marketplace/plugin names are limited to letters, digits, `.`, `_`, `-`; reserved names include `inline` (used for `--plugin-dir` plugins, which is why a clone shows as `<name>@inline`).

## Adding and installing (shell forms)

```bash
claude plugin marketplace add owner/repo            # GitHub shorthand; owner/repo#ref pins a branch or tag (documented); owner/repo@ref also worked on 2.1.310
claude plugin marketplace list
claude plugin marketplace update <marketplace>      # refreshes the listing; installed plugins stay at their versions (/en/plugins/install, "Keep plugins updated")
claude plugin marketplace remove <marketplace>      # also uninstalls its plugins and deletes their saved data
claude plugin install <plugin>@<marketplace> [--scope user|project|local]
claude plugin install <plugin> --marketplace owner/repo   # add + install in one step, v2.1.292+
claude plugin update <plugin>@<marketplace>
claude plugin list [--json]                         # shows Version, Scope, Status and load errors
```

In a session: `/plugin marketplace add`, `/plugin install <plugin>@<marketplace>` (opens details to review and pick scope), `/plugin` (Installed tab; Errors tab), `/reload-plugins`. Installing or updating does not change the running session: run `/reload-plugins` (or restart). `/reload-plugins` also re-loads a mod whose load failed with `the version loaded before is unloaded`. `claude -p` cannot run `/plugin`; install from the shell first, installed plugins do load.

Third-party marketplaces have **auto-update off by default** (on for most of Anthropic's official ones, such as `claude-plugins-official`, but off for `knowledge-work-plugins` and `first-party-plugins`; on for marketplaces added from claude.ai), so an installed mod can lag the repo. Users toggle it in `/plugin` → Marketplaces.

## What runs after install: the cache

- An installed plugin from a non-local source is **copied** to `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` and that copy is what runs. Editing the repo or the cache copy by hand does not change behavior reliably.
- The version Claude Code computes is: manifest `version`, else the marketplace entry's `version`, else the commit SHA. If the maintainer pins a `version` and does not bump it, users stay on the cached copy even though the repo changed. When `plugin.json` and the entry both set `version`, `plugin.json` wins (`validate` warns).
- To test the _repo state_ (not the cached install), clone it and use `claude --plugin-dir <clone>`; it hot-reloads on save and reports problems in the transcript.
- Reproducing what a user has: `claude plugin list --json` for the installed version, then compare with the clone's `version`/HEAD SHA.

## Inspect before installing

`claude plugin validate <clone>` on the plugin directory lists the hooks the mod registers, the `$.` calls it makes, and the env and state it reads, without loading it. Run `claude plugin validate <marketplace-root>` to validate `marketplace.json` itself; entry problems are reported by index (`plugins[2].source`, or `plugins[2] plugin.json →` for the plugin's own files). `validate` does not catch source fetch errors; those show only after install (`claude plugin list`). Directory-submission checks (README, LICENSE, icon) are informational unless `--profile directory`; `--strict` turns warnings into failures; `--json` gives machine-readable output including `gatingHooks` (`hasCatch`).

## Policy that blocks marketplace mods (user cannot override)

`disableAllHooks`, `allowManagedHooksOnly`, `allowManagedModsOnly`, and org `strictKnownMarketplaces`/`blockedMarketplaces` lists can stop a GitHub marketplace from being added or its mods from loading. Messages are in `troubleshooting.md`. Say plainly that the fix belongs to the administrator.
