---
name: new-plugin
description: Creates a new plugin in The Claude Factory end to end — design brief, scaffold, components, sales-quality README, changelog, validation and install tests on Claude Code and the Claude app. Use only when Nery explicitly asks to create, build or start a plugin.
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
- **Surfaces** — default Claude Code + the Claude app. Check every component against the [compatibility matrix](${CLAUDE_PROJECT_DIR}/docs/compatibility.md); if any part forces Claude Code-only, say why and get Nery's OK.
- **Requirements** — CLIs, accounts, API keys (`userConfig`), minimum Claude Code version.

Research current official docs for every component type used (Claude Code Docs MCP). Note version-gated features.

## 2. Scaffold

```bash
node .github/scripts/new-plugin.mjs --name <name> --category <id> \
  --description "<one sentence, outcome-first>" --display-name "<Display Name>" --emoji <emoji> \
  --min-claude-code <x.y.z> [--claude-code-only]
```

Add `--claude-code-only` only when the brief approved it; the default declares Claude Code + the Claude app.

This creates `plugins/<name>/` (manifest, README, CHANGELOG, LICENSE), registers the entry and regenerates the catalog.

## 3. Build components

Follow the [plugin authoring rules](${CLAUDE_PROJECT_DIR}/.claude/rules/stages/plugin-authoring.md). Add `keywords` to `plugin.json`. Keep `version` at `0.1.0` for the first release.

## 4. Write the README

- Resolve every `{{…}}` and `<!-- TODO -->` in `plugins/<name>/README.md`; delete rows/sections that don't apply (keep all required sections).
- Compatibility table: keep exactly one row per component type the plugin ships.
- Follow the [user docs style](${CLAUDE_PROJECT_DIR}/.claude/rules/stages/user-docs-style.md): outcome-first TL;DR, real usage examples, accurate Compatibility table.
- Fill `CHANGELOG.md` `0.1.0` → `### Added` with what ships.

## 5. Register everywhere

- `node .github/scripts/catalog.mjs`
- Root `CHANGELOG.md` → today's `## YYYY-MM-DD` heading → `### Added`: `- **<name>** 0.1.0 — <summary>.` Create the heading when it is missing; move the line under the merge day if the PR merges later.
- After push: `node .github/scripts/sync-labels.mjs` to create `plugin: <name>`.

## 6. Prove it works

1. Run the gates in [Before Every Push](${CLAUDE_PROJECT_DIR}/.claude/rules/QUALITY_GATE.md#before-every-push) — every gate passes.
2. Exercise each component in Claude Code while building (`claude --plugin-dir plugins/<name>`).
3. Run `/test-installed-plugin <name>` once, in full (this request authorizes it), and test in the Claude app (a Cowork session and a chat conversation), unless the plugin is declared Claude Code-only.
4. Delegate an independent review to the `plugin-reviewer` agent; fix every confirmed finding.

## 7. Hand off

Summarize for Nery: what was built, evidence (raw gate output), surfaces tested, and the release step (merge the PR; `release.yml` tags the plugin; the marketplace has no version to bump).
