---
name: docs-drift-check
description: Checks The Claude Factory against current Claude Code and Claude app releases — changelog, plugin docs, platform support, pinned versions — and lists every outdated doc, rule, template or script. Use only when Nery explicitly asks for a drift or freshness check.
context: fork
agent: general-purpose
---

# Docs drift check

Goal: find everything in this repository that no longer matches official sources. Report with evidence; don't edit unless asked.

## 1. Gather current facts (live sources only)

- Claude Code changelog: `/en/changelog` in the Claude Code Docs MCP (or <https://code.claude.com/docs/en/changelog>). Note releases since the version pinned in `.github/workflows/validate.yml` (`CLAUDE_CODE_VERSION`).
- Plugin docs: `/en/plugins/*` — install, marketplace-reference, manifest-reference, publish, host-marketplace, troubleshooting.
- Cross-surface support: <https://claude.com/docs/plugins/platform-support> and <https://claude.com/docs/cowork/guide/plugins>.
- Latest versions: `npm view @anthropic-ai/claude-code version`, `npm view markdownlint-cli2 version`, latest tags of `actions/checkout`, `actions/setup-node`, `rhysd/actionlint`.

## 2. Compare against the repo

| Area | Files |
| :-- | :-- |
| Commands, flags, UI paths, min versions | `README.md`, `docs/*.md`, `.claude/templates/plugin/README.md` |
| Compatibility matrix | `.claude/rules/cross-surface-compatibility.md`, `README.md`, `docs/compatibility.md` |
| Manifest / marketplace fields, reserved names | `.github/scripts/lib.mjs`, `check-repo.mjs`, templates |
| Pinned versions | `.github/workflows/*.yml`, `.claude/CLAUDE.md`, `verify` skill |
| New capabilities worth adopting | e.g. new manifest fields, `relevance`, evals, new component types |

## 3. Report

- Table: file · line · what it says · what's current · source URL · severity (wrong / outdated / opportunity).
- Proposed edits grouped by file, plus required version bumps (docs-only README edits need none).
