---
name: new-plugin
description: Creates a new plugin in The Claude Factory end to end — design brief, scaffold from templates, components, sales-quality README, changelog, validation and a local install test. Use when Nery asks to create, build, add or start a plugin for the marketplace.
argument-hint: "[plugin-name] [category]"
disable-model-invocation: true
---

# Create a plugin

Arguments: `$ARGUMENTS` (optional name and category).

## 1. Design brief (confirm with Nery before building)

Agree on, in Spanish:

- **Problem and outcome** — the recurring friction it removes; who it's for.
- **Name** — kebab-case, permanent, no `claude-`/`anthropic-` prefix. **Display name** and an emoji.
- **Category** — an `id` from `.github/scripts/categories.json`.
- **Components** — skills, agents, hooks, MCP, LSP, output styles, monitors, scripts. Justify each.
- **Surfaces** — Claude Code, Cowork, Claude chat; consequences (e.g. `bin/` blocks Cowork).
- **Requirements** — CLIs, accounts, API keys (`userConfig`), minimum Claude Code version.

Research current official docs for every component type used (Claude Code Docs MCP). Note version-gated features.

## 2. Scaffold

```bash
node .github/scripts/new-plugin.mjs --name <name> --category <id> \
  --description "<one sentence, outcome-first>" --display-name "<Display Name>" --emoji <emoji> \
  --min-claude-code <x.y.z>
```

This creates `plugins/<name>/` (manifest, README, CHANGELOG, LICENSE), registers the entry and regenerates the catalog.

## 3. Build components

Follow `.claude/rules/plugin-authoring.md`. Add `keywords` to `plugin.json`. Keep `version` at `0.1.0` for the first release.

## 4. Write the README

- Resolve every `{{…}}` and `<!-- TODO -->` in `plugins/<name>/README.md`; delete rows/sections that don't apply (keep all required sections).
- Follow `.claude/rules/user-docs-style.md`: outcome-first TL;DR, real usage examples, accurate Compatibility table.
- Fill `CHANGELOG.md` `0.1.0` → `### Added` with what ships.

## 5. Register everywhere

- `node .github/scripts/catalog.mjs`
- Root `CHANGELOG.md` → `[Unreleased]` → `### Added`: `- **<name>** 0.1.0 — <summary>.`
- After push: `node .github/scripts/sync-labels.mjs` to create `plugin: <name>`.

## 6. Prove it works

1. Run the `verify` skill — every gate ✔.
2. Local install loop in an isolated config:

   ```bash
   export CLAUDE_CONFIG_DIR="$(mktemp -d)"
   claude plugin marketplace add ./
   claude plugin install <name>@the-claude-factory
   claude plugin details <name>
   ```

3. Exercise each component in a session (`claude --plugin-dir plugins/<name>` is fine for iteration).
4. Delegate an independent review to the `plugin-reviewer` agent; fix every confirmed finding.

## 7. Hand off

Summarize for Nery: what was built, evidence (raw gate output), surfaces tested, and the release step (`/release marketplace minor` when publishing).
