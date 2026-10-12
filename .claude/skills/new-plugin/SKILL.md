---
name: new-plugin
description: Creates a new plugin in The Claude Factory end to end — design brief, scaffold, components, sales-quality README, changelog, validation and install tests on Claude Code and Cowork. Use only when Nery explicitly asks to create, build or start a plugin.
argument-hint: "[plugin-name] [category]"
---

# Create a plugin

Arguments: `$ARGUMENTS` (optional name and category).

## 1. Design brief (confirm with Nery before building)

Agree on, in Spanish:

- **Problem and outcome** — the recurring friction it removes; who it's for.
- **Name** — kebab-case, permanent, no `claude-`/`anthropic-` prefix. **Display name** and an emoji.
- **Category** — an `id` from `.github/scripts/categories.json`.
- **Components** — skills, agents, hooks, MCP, LSP, output styles, monitors, scripts. Justify each.
- **Surfaces** — default Claude Code + Cowork. Check every component against `.claude/rules/cross-surface-compatibility.md`; if any part forces Claude Code-only, say why and get Nery's OK.
- **Requirements** — CLIs, accounts, API keys (`userConfig`), minimum Claude Code version.

Research current official docs for every component type used (Claude Code Docs MCP). Note version-gated features.

## 2. Scaffold

```bash
node .github/scripts/new-plugin.mjs --name <name> --category <id> \
  --description "<one sentence, outcome-first>" --display-name "<Display Name>" --emoji <emoji> \
  --min-claude-code <x.y.z> [--claude-code-only]
```

Add `--claude-code-only` only when the brief approved it; the default declares Claude Code + Cowork.

This creates `plugins/<name>/` (manifest, README, CHANGELOG, LICENSE), registers the entry and regenerates the catalog.

## 3. Build components

Follow `.claude/rules/plugin-authoring.md`. Add `keywords` to `plugin.json`. Keep `version` at `0.1.0` for the first release.

## 4. Write the README

- Resolve every `{{…}}` and `<!-- TODO -->` in `plugins/<name>/README.md`; delete rows/sections that don't apply (keep all required sections).
- Compatibility table: keep exactly one row per component type the plugin ships.
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

3. Exercise each component in Claude Code (`claude --plugin-dir plugins/<name>`) and in Cowork (add the marketplace or upload a zip, run a task), unless the plugin is declared Claude Code-only.
4. Delegate an independent review to the `plugin-reviewer` agent; fix every confirmed finding.

## 7. Hand off

Summarize for Nery: what was built, evidence (raw gate output), surfaces tested, and the release step (`/release marketplace minor` when publishing).
