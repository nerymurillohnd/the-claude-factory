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
| 2026-10-12 | Our own skills stay at moderate detail: fix first the findings that change a verdict, findings or produced files; rare cases may be left to the model's judgment (the audit still reports them) | Agent Skills "moderate detail" practice; the self-audit loop had bloated `SKILL.md` 66% |
| 2026-10-12 | skill-diagnostics `SKILL.md` keeps only the fragile core (~880 words); rare paths live in `references/fallbacks.md` | Progressive disclosure |
| 2026-10-12 | User docs and the plugin README template explain `<plugin>@synced` (installed from the Claude app/Cowork): update/uninstall in the app, v2.1.273+ and claude.ai sign-in, a same-named Claude Code install wins | Users installing from the app saw only terminal instructions |
| 2026-10-12 | Auditors report every finding (severity classifies, never filters: high = decides output on a normal path); the orchestrator verifies every finding as a last gate against the files, live official docs and the Claude Code changelog (the user's release, the five before it and every newer one; only Claude Code, decided 2026-10-12), sends false or partly false findings back to the lens once, closes with a checklist of every agent stage; provisional only when a finding stays unverified live or the changelog can't be read | Nery: a real auditor finds everything and proves each finding with current official sources |
| 2026-10-12 | The audit pre-approves WebFetch for its official sources (`code.claude.com`, `claude.com`, `platform.claude.com`, `support.claude.com`, `agentskills.io`); the `anthropics/skills` commit history was dropped as a source on 2026-10-12 (GitHub refuses automated fetches; the Claude Code changelog page already comes from the official `anthropics/claude-code` repo); verdict provisional only when a finding stays unverified live or no change source could be checked | Verification without prompts; GitHub often refuses automated fetches |
| 2026-10-12 | Agent Teams not used by plugins: experimental, off by default, Claude Code CLI only (docs: agent-teams, glossary) | Plugins must work the same in Cowork |
| 2026-10-12 | skill-diagnostics evals follow Nery's five cases: natural trigger, hook-driven audit with full inventory and evidence briefs, full reads by both agents, live verification, scripts by path on macOS/Linux/Windows Git Bash (CI `by_path.sh`, not an eval); local = smoke test per the docs, CI = full eval | Measure that the plugin does what it promises, with raw evidence |
| 2026-10-12 | Rules that must hold every time go in hooks; the audit's `Stop` verification gate was removed in the 2026-10-12 rewrite, to be re-measured with installed audits and restored (a prompt hook on `Stop` at minimum) if the changelog check gets skipped; skills dirs validated with `claude plugin validate`; triggering measured as a rate | Claude Code skills docs: Skill not triggering, Claude stops following a skill |
| 2026-10-12 | skill-diagnostics auditors read every file end to end: inventory from `check_skill.py --list`, auditors get only Read (+ WebFetch), no search tools; a mod was considered and rejected (Claude Code-only, high-trust) | A real audit reads everything; works the same in Claude Code and Cowork |
| 2026-10-12 | One ruff config: Nery's strict `ruff.toml` at the root (`ALL`, 100 cols, no `target-version`); `.github/scripts/ruff.toml` removed; CI ruff 0.17.0; every script has a shebang and `100755` | Nery's standard for all his repos |
| 2026-10-12 | Biome 2.5.15 for JS/JSON: Nery's `biome.json` (from claude-essentials) at the root plus `json.formatter.expand: "always"`; shell style in `.editorconfig` `[[shell]]` (shfmt `-i 2 -s -bn -ci -sr`); CI actionlint runs shellcheck with `SHELLCHECK_OPTS=-o all -S style -x -a -P SCRIPTDIR` | Nery's standards for all his repos; the same shellcheck rules in CI (workflow blocks) and in `/verify` (scripts) |
| 2026-10-12 | Maintenance scripts stay in Node, not Bash | JSON-heavy; Bash would need `jq`, macOS ships Bash 3.2 and BSD tools, Windows needs Git Bash |

## Status

- Marketplace `0.1.0` released (`marketplace--v0.1.0`). Catalog on `main` empty; `skill-diagnostics` 0.1.0 lives on `feat/skill-diagnostics` (draft PR #1), merged only into Nery's local `main` (not pushed).
- CI green: Validate (policy + script tests, `claude plugin validate`, markdownlint + actionlint) and Release.
- GitHub settings done: PRs Collaborators only, private vulnerability reporting, topics, 20 custom labels.

## Open items

- GitHub's default labels (`bug`, `enhancement`, `documentation`, `duplicate`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`, `accessibility`) still exist next to ours — Nery decides whether to delete them.
- `skill-diagnostics` eval pilot done (phase 7): hook-suggests Δ+1.00, portability-traps Δ+1.00, parallel-lenses Δ+0.50; cross-file-gaps and clean-skill-passes are guardrails, create-does-not-trigger the negative. Pilot cost per full single run ≈ $1.37 → CI cap `--max-cost-usd 5.50` (3 runs × 1.25).
- `skill-diagnostics` 0.1.0 is built through phase 9 on branch `feat/skill-diagnostics` (draft PR #1): docs-auditor and plugin-reviewer findings fixed, isolated cached install verified, hook verified for a SKILL.md outside cwd, Nery tested synced copies in Claude Code (macOS) and Cowork; the PR review findings are fixed; the 2026-10-12 slimming refactor passed an installed audit (pass with warnings, 0 denials); after the verification gate and two audits from Nery's sessions, 4 installed runs of `87ac3fe` gave pass with warnings, 0 high, 0 denials; the remaining findings are wording nits (lens IDs in disputes, one term for skill folder), left by the moderate-detail rule. Test zips are stamped `0.1.0-test.<sha>`. Pending: Nery's test of the latest zip, the skill-creator → hook offer step, re-running the eval pilot after the refactor, then phase 10 (CI evals + `/release`; re-date the 0.1.0 CHANGELOG entry and run `sync-labels.mjs` at release). Build in progress: plan and phases in Nery's "Plan: skill-diagnostics" doc (claude.ai artifact 3d3dfddc-5aad-4e92-8ad1-ac636b8db2fe); audit of the source plugin in artifact 268a085a-e5fb-4f8f-998a-863888641ff0.
- Evals in CI authenticate with Nery's `CLAUDE_CODE_OAUTH_TOKEN` secret (decided 2026-10-12, no API key); they run when a PR changing a `plugin.json` is opened, reopened or marked ready for review, or by hand once `evals.yml` is on `main`. First CI run (2026-10-12, `4c8d872`, run 38246672629): the token works with `claude plugin eval`; 9 of 10 cases passed, mean Δ +0.72, ~$6.70 list-price estimate, 28 min; natural-request scored 0.9 only because its Verification grader expected one line and the report nested it (grader fixed). Re-run on the fix: convert the PR to draft and mark it ready again (re-running a job reuses the old commit).

## Plugin ideas backlog

| Idea | Origin | Status |
| :-- | :-- | :-- |
| `project-records` — decision records, debt ledgers, session handoffs (handoffs gitignored) | Nery, earlier sessions | idea |
| `skill-diagnostics` — audit skills: conformance + executability (was `skills-engineering`) | Nery, earlier sessions | building |
| `live-docs-research` — research from live official sources + changelog checks | Nery, earlier sessions | idea |
