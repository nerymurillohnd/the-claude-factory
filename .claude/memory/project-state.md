# Project state

## Decisions

| Date | Decision | Why |
| :-- | :-- | :-- |
| 2026-10-11 | New repo `nerymurillohnd/the-claude-factory`; marketplace name `the-claude-factory` (permanent) | Fresh public flagship |
| 2026-10-11 | `claude-essentials` (Nery's older public marketplace) will be retired; migrate plugins from it **only when Nery asks** | Avoid carrying unreviewed work |
| 2026-10-11 | Explicit SemVer in `plugin.json` + Keep a Changelog per plugin and at root; marketplace versioned too | `claude-plugins-official` uses commit SHAs without changelogs; we want meaningful changelogs and bumps |
| 2026-10-11 | Tags `{name}--v{version}` / `marketplace--v{version}` created only by `release.yml` | Same format as `claude plugin tag`; dependency ranges resolve against tags |
| 2026-10-11 | MIT license; public content in English | Global audience |
| 2026-10-11 | No external PRs (GitHub: Collaborators only); users contribute via issue forms | Owners maintain everything |
| 2026-10-11 | Monorepo with relative sources `./plugins/<name>`; README catalog generated from `marketplace.json` | Single source of truth; plugin metadata visible before install |
| 2026-10-11 | Maintenance lives only in `.claude/` and `.github/scripts/`; `CLAUDE.md` moved to `.claude/CLAUDE.md` | Keep the public root a clean showcase |
| 2026-10-11 | Project memory committed in `.claude/memory/` | Auto memory is machine-local; this repo is worked on from Nery's Mac and cloud sessions |
| 2026-10-11 | Plugins must be generic: no Forestal MT references, no forced conversation language | Public audience |

## Status

- Marketplace `0.1.0` released (`marketplace--v0.1.0`). Catalog empty — no plugins yet.
- CI green: Validate (policy + script tests, `claude plugin validate`, markdownlint + actionlint) and Release.
- GitHub settings done: PRs Collaborators only, private vulnerability reporting, topics, 20 custom labels.

## Open items

- GitHub's default labels (`bug`, `enhancement`, `documentation`, `duplicate`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`, `accessibility`) still exist next to ours — Nery decides whether to delete them.
- First plugin: not chosen yet. Candidates mentioned in past work: `project-records`, `skills-engineering` (skill auditor + best practices), `live-docs-research`.

## Plugin ideas backlog

| Idea | Origin | Status |
| :-- | :-- | :-- |
| `project-records` — decision records, debt ledgers, session handoffs (handoffs gitignored) | Nery, earlier sessions | idea |
| `skills-engineering` — create/audit/improve skills grounded in live docs | Nery, earlier sessions | idea |
| `live-docs-research` — research from live official sources + changelog checks | Nery, earlier sessions | idea |
