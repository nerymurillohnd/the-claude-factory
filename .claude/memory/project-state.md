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
| 2026-10-11 | Plugins target Claude Code **and** the Claude app (was "Cowork"; renamed 2026-10-12); Claude Code-only only when unavoidable and declared in the README | Reach both audiences with one package |
| 2026-10-11 | Surfaces declared in `plugin.json` `metadata.surfaces`; README badge, catalog column and `check-repo.mjs` derive from it | One source of truth, enforced |
| 2026-10-12 | Two surfaces, Claude Code and the Claude app: `metadata.surfaces` `["claude-code","claude-app"]` (value `cowork` retired); Compatibility tables have two columns; agents, hooks and local MCP are ⚠️ "Cowork sessions only", with a note that a conversation runs as chat when it can't run Cowork | Chat and Cowork became one Claude app (support 16761823, 2026-09-16); support 13837440: hooks and sub-agents don't run in chat; official plugin docs still split them |
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
| 2026-10-12 | User docs and the plugin README template explain `<plugin>@synced` (installed from the Claude app): update/uninstall in the app, v2.1.273+ and claude.ai sign-in, a same-named Claude Code install wins | Users installing from the app saw only terminal instructions |
| 2026-10-12 | Auditors report every finding (severity classifies, never filters: high = decides output on a normal path); the orchestrator verifies every finding as a last gate against the files, live official docs and the Claude Code changelog (the user's release, the five before it and every newer one; only Claude Code, decided 2026-10-12), sends false or partly false findings back to the lens once, closes with a checklist of every agent stage; provisional only when a finding stays unverified live or the changelog can't be read | Nery: a real auditor finds everything and proves each finding with current official sources |
| 2026-10-12 | The audit's official sources are `code.claude.com`, `claude.com`, `platform.claude.com`, `support.claude.com`, `agentskills.io` and the Claude Code changelog; the `anthropics/skills` commit history was dropped (GitHub refuses automated fetches); verdict provisional only when a finding stays unverified live or the changelog could not be read | GitHub often refuses automated fetches |
| 2026-10-12 | Plugin skills ship no `allowed-tools`: each user's permission settings decide what asks first; denied reads or fetches are reported, never worked around | Nery: every user has their own configuration and settings |
| 2026-10-12 | Agent Teams not used by plugins: experimental, off by default, Claude Code CLI only (docs: agent-teams, glossary) | Plugins must work the same in Cowork |
| 2026-10-12 | skill-diagnostics evals follow Nery's five cases: natural trigger, hook-driven audit with full inventory and evidence briefs, full reads by both agents, live verification, scripts by path on macOS/Linux/Windows Git Bash (CI `by_path.sh`, not an eval); local = smoke test per the docs, CI = full eval | Measure that the plugin does what it promises, with raw evidence |
| 2026-10-12 | Rules that must hold every time go in hooks; the audit's `Stop` verification gate was removed in the 2026-10-12 rewrite, to be re-measured with installed audits and restored (a prompt hook on `Stop` at minimum) if the changelog check gets skipped; skills dirs validated with `claude plugin validate`; triggering measured as a rate | Claude Code skills docs: Skill not triggering, Claude stops following a skill |
| 2026-10-12 | skill-diagnostics auditors read every file end to end: Claude lists the inventory with its own tools, auditors get only Read (+ WebFetch), no search tools; a mod was considered and rejected (Claude Code-only, high-trust) | A real audit reads everything; works the same in Claude Code and Cowork |
| 2026-10-12 | skill-diagnostics ships no checker or helper scripts (`check_skill.py`, `changelog.py` removed): the conformance lens states what to check, and Claude checks it by reading, with the session's tools, or with a script it writes for the user's machine | Nery: Claude does this natively and knows what the user's machine has; we don't |
| 2026-10-12 | One ruff config: Nery's strict `ruff.toml` at the root (`ALL`, 100 cols, no `target-version`); `.github/scripts/ruff.toml` removed; CI ruff 0.17.0; every script has a shebang and `100755` | Nery's standard for all of Nery's repos |
| 2026-10-12 | Biome 2.5.15 for JS/JSON: Nery's `biome.json` (from claude-essentials) at the root plus `json.formatter.expand: "always"`; shell style in `.editorconfig` `[[shell]]` (shfmt `-i 2 -s -bn -ci -sr`); CI actionlint runs shellcheck with `SHELLCHECK_OPTS=-o all -S style -x -a -P SCRIPTDIR` | Nery's standards for all of Nery's repos; the same shellcheck rules in CI (workflow blocks) and in `/verify` (scripts) |
| 2026-10-12 | Maintenance scripts stay in Node, not Bash | JSON-heavy; Bash would need `jq`, macOS ships Bash 3.2 and BSD tools, Windows needs Git Bash |
| 2026-10-12 | Evals are optional per plugin (Nery decides which plugins get a suite); CI runs only plugins with `evals/` whose `plugin.json` changed in the PR, one matrix job each (`eval-targets.mjs`); no required eval check on `main` | With many plugins, re-running unchanged suites wastes time, Actions minutes and Nery's plan |
| 2026-10-12 | A PR is required only for changes to a plugin itself (`plugins/<name>/`: `plugin.json`, README, `SKILL.md`, components); everything else (docs, local skills, `.claude/`, `CLAUDE.md`, tooling) goes by direct push or PR as Nery decides; never default to a PR for those | Nery: forcing a PR to delete a `.gitkeep` is absurd |
| 2026-10-12 | session-handoff ships no evals; its `write-handoff` skill is model-invocable (no `disable-model-invocation`) | Nery; the Claude app documents slash commands for plugin commands only, so a manual-only skill may not be startable in Cowork |
| 2026-10-12 | `plugin-test-bench`: skills `test-install` and `review-evals`, Claude Code only (`metadata.surfaces: ["claude-code"]`), minimum Claude Code 2.1.293, ships no evals | It drives the `claude` CLI and git in a terminal; Nery decides evals per plugin |
| 2026-10-12 | Audits of our skills run in-session: one skill-creator agent plus the conformance and executability lenses as hand-built agents from skill-diagnostics' references, then the orchestrator's live verification and changelog read; fix only findings a user would realistically hit | Nery: not a `--plugin-dir` terminal session; stay objective, don't chase a clean report with remote edge cases |

## Status

- Released on `main` (tags by `release.yml`): `skill-diagnostics` 0.1.0 (PR #1) and 0.1.1 (PR #3, `@claude` review fixes), `session-handoff` 0.1.0 (PR #5). Marketplace still `0.1.0`: the 0.2.0 bump for the two added plugins is pending (`/release marketplace`).
- CI: Validate, Release, `claude-code-review.yml` (review on every PR) and `claude.yml` (`@claude` mentions, from PR #2); `evals.yml` runs one matrix job per changed plugin with `evals/` (PR #4; verified on PR #5: nothing selected, eval job skipped).
- GitHub settings done: PRs Collaborators only, private vulnerability reporting, topics, 20 custom labels. `main` has no branch protection.

## Open items

- **plugin-test-bench, before release:** the free installed run on itself (plan Task 6) is not done; it must confirm that `claude -p` with no credentials emits `system/init` before the login error (undocumented; the verdict rule depends on it). The maintainer skill `.claude/skills/test-installed-plugin` still carries the defects fixed in the plugin (verdict rule, free load check with profiles, sign-in after the go-ahead, quoted grants, prompt before `--allowedTools`).
- **skill-diagnostics regression (in 0.1.0 and 0.1.1):** the full CI eval of 0.1.1 (run 38297567893, 8/10 cases, score 0.94, Δ +0.67, ~$5.87 list-price estimate) showed natural-request never reading the Claude Code changelog (0/3) and skipping both lens agents in 2/3 runs; hook-audit skipped the agents in 1/3. Plan: restore a `Stop` gate (a prompt hook, no script), run a local `--keep-temp` smoke test of natural-request to read why agents are skipped, release 0.1.2. CI keeps no traces.
- **session-handoff, untested on the Claude app:** what `${CLAUDE_PROJECT_DIR}` is in a Cowork session (cloud or local), whether a handoff persists in the user's folder and the hook fires there, how a chat conversation renders the placeholder; also `/test-installed-plugin session-handoff`. The runtime minimum Claude Code version is undocumented (v2.1.292 is the install command's floor).
- skill-diagnostics follow-ups: `/test-installed-plugin skill-diagnostics`, a re-audit of the `audit` skill, the skill-creator → hook offer step; design item: lens agents read their method from the plugin cache (read prompts), and moving it into the agent body needs its own design and re-audit.
- `evals.yml` shows the skipped matrix job as `Plugin evals (${{ matrix.plugin }})`: cosmetic, give it a fixed name.
- `sync-labels.mjs` not yet run for the two plugins (`plugin: <name>` labels).
- Submitting skill-diagnostics to Anthropic's directory: its hook runs a Python file from a plugin in a repository subfolder, which the portal holds for a reviewer ("Scripts the validator couldn't follow", claude.com pre-submission checklist). `check-repo.mjs` enforces the checklist's file rules (names, system files, symlinks, 256 KiB, 512 files).
- GitHub's default labels (`bug`, `enhancement`, `documentation`, `duplicate`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`, `accessibility`) still exist next to ours — Nery decides whether to delete them.
- Evals cost basis: two full CI runs of skill-diagnostics, ~$6.70 (28 min) and ~$5.87 (20 min) list-price estimates on Nery's plan; cap `max_cost_usd` 10 in `evals-config.json`.

## Plugin ideas backlog

| Idea | Origin | Status |
| :-- | :-- | :-- |
| `project-records` — decision records, debt ledgers, session handoffs (handoffs gitignored) | Nery, earlier sessions | idea |
| `skill-diagnostics` — audit skills: conformance + executability (was `skills-engineering`) | Nery, earlier sessions | released 0.1.1 |
| `session-handoff` — end-of-session handoff file + start-of-session reader | Nery, 2026-10-12 | released 0.1.0 |
| `plugin-test-bench` — copied-install test of a plugin + eval-case review | Nery, 2026-10-12 | in review (draft PR) |
| `live-docs-research` — research from live official sources + changelog checks | Nery, earlier sessions | idea |
