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
| 2026-10-11 | Plugins target Claude Code **and** Cowork; Claude Code-only only when unavoidable and declared in the README | Reach both audiences with one package |
| 2026-10-11 | Surfaces declared in `plugin.json` `metadata.surfaces`; README badge, catalog column and `check-repo.mjs` derive from it | One source of truth, enforced |
| 2026-10-11 | Maintenance skills invocable by Claude on Nery's explicit request (no `disable-model-invocation`) | Nery works mostly from the Claude app, whose menus don't show repo skills |
| 2026-10-11 | Plugins must be generic: no Forestal MT references, no forced conversation language | Public audience |
| 2026-10-11 | First plugin: `skill-diagnostics` (skill `audit`, agents `conformance-auditor` + `executability-auditor`), rebuilt from claude-essentials `skills-engineering` | Audit found it duplicated `skill-creator`; the executability audit and the checker are the unique value |
| 2026-10-11 | `skill-diagnostics` only audits; creating skills is left to `skill-creator` (scope guard in description and body) | Avoid competing with Anthropic's own tooling and mis-triggering |
| 2026-10-11 | One audit skill, two lens agents in parallel, one merged report and verdict; a PostToolUse hook on `SKILL.md` writes suggests the audit (`userConfig.on_skill_write`: suggest/run/off) | One entry point, no reviewer/auditor ambiguity |
| 2026-10-11 | All plugin content 100% original; facts cited by link | Clean MIT; no unlicensed third-party examples |
| 2026-10-11 | Scripts: `#!/usr/bin/env` shebang, `100755`, called by path; runtimes declared in README Requirements, no per-OS fallbacks | Simplicity; requirements are what READMEs are for |
| 2026-10-11 | Evals: Sonnet runs, Opus judges; only differentiating cases; uncapped local pilot, capped full run in CI (`.claude/rules/evals.md`) | Objective, cost-controlled evidence |
| 2026-10-11 | Keep a Changelog 2.0.0 (published 2026-06-07) | Current version of the format |
| 2026-10-12 | Plugins never limit their own file coverage (no git-ignored or similar exclusions); the user's settings and hooks set the limits, and blocked files are reported, never worked around | Users choose their own coverage; a plugin must not decide it for them |
| 2026-10-12 | Executability findings are high only when they change a verdict, findings or produced files; layout and rare cases are left to the model's judgment, and skills are never asked to cover every edge case | Agent Skills "moderate detail" practice; the self-audit loop had bloated `SKILL.md` 66% |
| 2026-10-12 | skill-diagnostics `SKILL.md` keeps only the fragile core (~880 words); rare paths live in `references/fallbacks.md` | Progressive disclosure |
| 2026-10-12 | User docs and the plugin README template explain `<plugin>@synced` (installed from the Claude app/Cowork): update/uninstall in the app, v2.1.273+ and claude.ai sign-in, a same-named Claude Code install wins | Users installing from the app saw only terminal instructions |
| 2026-10-12 | Auditors report every finding (severity classifies, never filters: high = decides output on a normal path); the orchestrator verifies every finding as a last gate against the files, live official docs and the last 15 days of official changes (Claude Code changelog, Claude apps release notes, Agent Skills, Anthropic repos), sends false/partial/off-focus findings back to the lens, closes with a checklist of every agent stage; offline → provisional verdict | Nery: a real auditor finds everything and proves each finding with current official sources |
| 2026-10-12 | skill-diagnostics auditors read every file end to end: inventory from `check_skill.py --list`, auditors get only Read (+ WebFetch), no search tools; a mod was considered and rejected (Claude Code-only, high-trust) | A real audit reads everything; works the same in Claude Code and Cowork |

## Status

- Marketplace `0.1.0` released (`marketplace--v0.1.0`). Catalog on `main` empty; `skill-diagnostics` 0.1.0 lives on `feat/skill-diagnostics` (draft PR #1), merged only into Nery's local `main` (not pushed).
- CI green: Validate (policy + script tests, `claude plugin validate`, markdownlint + actionlint) and Release.
- GitHub settings done: PRs Collaborators only, private vulnerability reporting, topics, 20 custom labels.

## Open items

- GitHub's default labels (`bug`, `enhancement`, `documentation`, `duplicate`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`, `accessibility`) still exist next to ours — Nery decides whether to delete them.
- `skill-diagnostics` eval pilot done (phase 7): hook-suggests Δ+1.00, portability-traps Δ+1.00, parallel-lenses Δ+0.50; cross-file-gaps and clean-skill-passes are guardrails, create-does-not-trigger the negative. Pilot cost per full single run ≈ $1.37 → CI cap `--max-cost-usd 5.50` (3 runs × 1.25).
- `skill-diagnostics` 0.1.0 is built through phase 9 on branch `feat/skill-diagnostics` (draft PR #1): docs-auditor and plugin-reviewer findings fixed, isolated cached install verified, hook verified for a SKILL.md outside cwd, Nery tested synced copies in Claude Code (macOS) and Cowork; the PR review findings are fixed; the 2026-10-12 slimming refactor passed an installed audit (pass with warnings, 0 denials). Test zips are stamped `0.1.0-test.<sha>`. Pending: Nery's test of the latest zip, the skill-creator → hook offer step, re-running the eval pilot after the refactor, then phase 10 (CI evals + `/release`; re-date the 0.1.0 CHANGELOG entry and run `sync-labels.mjs` at release). Build in progress: plan and phases in Nery's "Plan: skill-diagnostics" doc (claude.ai artifact 3d3dfddc-5aad-4e92-8ad1-ac636b8db2fe); audit of the source plugin in artifact 268a085a-e5fb-4f8f-998a-863888641ff0.
- Evals in CI need Nery's decision: `ANTHROPIC_API_KEY` secret (billed to the API console) and trigger (recommended: plugin version change + manual).

## Plugin ideas backlog

| Idea | Origin | Status |
| :-- | :-- | :-- |
| `project-records` — decision records, debt ledgers, session handoffs (handoffs gitignored) | Nery, earlier sessions | idea |
| `skill-diagnostics` — audit skills: conformance + executability (was `skills-engineering`) | Nery, earlier sessions | building |
| `live-docs-research` — research from live official sources + changelog checks | Nery, earlier sessions | idea |
