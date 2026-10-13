# Session log

Newest first. One entry per session: what changed, commits, what's next.

## 2026-10-13 — LSP intelligence plugins v2 (branch `feat/lsp-intelligence-v2`)

- Design from official sources only (Claude Code Docs, agentskills.io, Platform docs) with runtime probes: spec `.claude/specs/2026-10-13-lsp-intelligence-plugins-design.md` (on `main`, `c902e97`); plan executed inline from `.claude/plans/2026-10-13-lsp-intelligence-v2.md`.
- Each plugin = `.lsp.json` + one `PostToolUse`/`PostToolUseFailure` hook (`Edit|Write[|NotebookEdit]|Bash`, shell form) scoped to the changed files + a short LSP-first skill. Python hook in Python 3 stdlib with defaults in `hooks/defaults/`; Bash and both TypeScript hooks in Node; TypeScript 7.0.2 and 6.0.3 + typescript-language-server 6.0.2 pinned by `package.json`/lockfile and installed by Claude Code into the cache.
- Tools run natively (user config first, plugin defaults only when none exists: `shfmt -i 2 -ci -bn`, `shellcheck -o all -S style -x -a -P SCRIPTDIR`, the bundled ruff/basedpyright profiles, `tsc` defaults without a tsconfig); clean runs confirm with a `systemMessage`; findings go to stderr with exit 2.
- Removed: the unused `.github/scripts/quality-gate/` engine, `bin/`, `verify-fixtures.sh`, the six-reference skill layout. Versions: python/bash/typescript7 0.2.0, typescript6 0.1.0 (new). CI installs shellcheck, a checksum-pinned shfmt, ruff, basedpyright and the TS plugins' `node_modules` for the hook tests.
- Verified: 59 script tests + 19 Python hook tests, every gate green; copied install from the branch in an isolated config with `node_modules` auto-installed; headless sessions on the installed copies showed each hook's findings reaching Claude (basedpyright, SC2086/SC2250, TS2322 in the edited file and its caller) and the `systemMessage` on a clean edit; skill trigger rate 3/3 (python, ts7, ts6) and 2/3 (bash: a bare rename prompt greps first).
- Independent whole-branch review (fresh Opus reviewer) found three normal-path defects CI missed and five important ones; all fixed with tests first in `248d11a`: jsconfig and solution-style tsconfig handling, JavaScript without a config no longer blocks, the default basedpyright profile is bound to the file's project (root, `src/`, `.venv`) through a temporary config, the mtime walk skips unreadable folders, stops at 20,000 files and never walks the home directory, TS6's `initializationOptions` dropped (not substituted by Claude Code). CI uses uv (`setup-uv` pinned) instead of pip and mypy covers the test suites too.
- Incident: the spec commit `9b754cf` swept the staged plugin draft onto `main`; reverted in `606988a` (plugins restored byte-identical). Lesson recorded in learnings.
- Released: PR #7 squash-merged as `d86e3b1`; `release.yml` tagged `python-lsp-intelligence--v0.2.0`, `bash-lsp-intelligence--v0.2.0`, `typescript7-lsp-intelligence--v0.2.0` and `typescript6-lsp-intelligence--v0.1.0` (their versions were dated on the branch). Marketplace 0.1.0 → 0.2.0; the bump-version test no longer hardcodes the marketplace's next version.
- CI: the uv cache is keyed to `validate.yml` (`c36471d`), which removed setup-uv's "cache will never get invalidated" warning from every Python job; Nery committed the `tsconfig.base.json` rename (`f52cefa`); the merged feature branch is deleted on GitHub and locally. The installed python-lsp-intelligence 0.2.0 hook blocked a scratch script of this session on ruff and basedpyright findings (dogfooding works).
- Next: `/test-installed-plugin` for the four LSP plugins and a Claude app check; decide on the deferred minors (project-state open items).

## 2026-10-12 — Biome strictness, unwired tsconfig, tooling research

- Researched TypeScript 6/7, tsconfig bases, typescript-language-server and Biome with Context7, each fact probed with Nery's `tsc` 6.0.3, LSP 6.0.2 and Biome 2.5.15.
- Biome: Nery's rule set merged and migrated to 2.5.15, override globs fixed, `jsxEverywhere` off, `allowComments`/`globals` kept unset with proof; gates now `--error-on-warnings`; scripts got block statements and one justified suppression (`b3ada31`).
- `tsconfig.json` (root base) and `.github/scripts/tsconfig.json` added unwired and force-ignored by Biome.
- Verified: every `/verify` gate, `check-version-bump` and actionlint green before the commit.
- Next: Nery decides when to wire the TypeScript gate (package.json in `.github/scripts`, JSDoc for 132 errors); plugin-test-bench follow-ups in the entry below.

## 2026-10-12 — plugin-test-bench audits and fixes

- Three-agent audit (skill-creator, conformance, executability) of `test-install` and `review-evals`; plan `.claude/plans/2026-10-12-plugin-test-bench-fixes.md` executed inline: verdict rules, free load check, sign-in after the go-ahead, quoted grants, prompt before `--allowedTools` (`397be74`, `f15ea85`, `f493a73`).
- Final branch review plus two re-audit rounds with live docs and the changelog 2.1.291–2.1.296: Anthropic profiles could bill the load check, plugin cache variables, step-7 agreement, case pass threshold, results folder, scaffold flag (`db854d2` and the release-prep commit). Nery: fix only what users would realistically hit.
- Next: free installed run on the plugin itself (confirms init-before-login), port the fixes to `.claude/skills/test-installed-plugin`, `/release` plugin-test-bench 0.1.0 and the marketplace.

## 2026-10-12 — Unified Claude app, three releases, per-plugin evals

- Surface model moved to Claude Code + the Claude app (chat and Cowork one app); `check-repo.mjs` enforces the directory's portability rules; skill-diagnostics lost its scripts and `allowed-tools`; `/test-installed-plugin` added (squashed into PR #1).
- Released skill-diagnostics 0.1.0 (PR #1, `809cf90`) and 0.1.1 (PR #3, `b829490`, `@claude` review fixes), and session-handoff 0.1.0 (PR #5, `e1aa8dd`) after a plugin-reviewer and docs-auditor pass (hook path-glob bug, synced-copy claim, Claude app labels fixed repo-wide).
- `evals.yml` now evaluates only changed plugins that ship `evals/`, one matrix job each (PR #4, `5b61124`); evals are optional per plugin.
- Rule from Nery: PRs only for plugin changes; everything else by direct push or PR as Nery decides (`8c1e476`).
- Full CI eval of skill-diagnostics 0.1.1: 8/10; the audit skips the changelog check and sometimes the lens agents (regression from the refactor).
- Next: fix the skill-diagnostics regression (Stop prompt hook, local `--keep-temp` smoke test, 0.1.2); test session-handoff in Cowork and chat; `/release marketplace` 0.2.0 and `sync-labels.mjs`.

## 2026-10-11/12 — skill-diagnostics build (phases 0–9)

- Audited claude-essentials `skills-engineering`; rebuilt it as `skill-diagnostics` (audit-only skill, conformance + executability agents, `check_skill.py`, `PostToolUse` hook). Plan and audit live in claude.ai artifacts (see project-state).
- Evals pilot ($2.41), docs-auditor and plugin-reviewer reviews, isolated cached installs and installed self-audits; Nery tested synced zips in Cowork and Claude Code and reviewed PR #1 from another session. Every confirmed finding fixed.
- Design changes from testing: full-read auditors with only Read and a `check_skill.py --list` inventory (Glob is absent on macOS/Linux and caps at 100); coverage left to user settings; hook fires anywhere (`//**/SKILL.md`) and skips Claude Code-managed folders; synced-install docs.
- Course correction: the self-audit loop had grown `SKILL.md` 66%; refactored to moderate detail with `references/fallbacks.md`, recalibrated "decides output", updated `plugin-authoring.md`.
- Commits `caacfa4`…`HEAD` on `feat/skill-diagnostics`; CI green; Nery's local `main` holds a merge (not pushed).
- Verification gate (Nery's design): auditors report everything; the orchestrator verifies each finding against the files, live official docs and the last 15 days of official changes, sends disputes back, closes with a checklist. Two audits of `8afed00` from Nery's sessions fixed in `41c3c6e`, `4c62e1a`, `87ac3fe` (Files read line, dispute protocol, merge rule, provisional threshold, WebFetch pre-approval, `--list` `exists` flag, plugin-root expansion per the manifest docs).
- Evals rebuilt around Nery's five cases (natural trigger rate 7/7, hook-offer, hook-audit, full reads proven from the trace, live verification) and run by path on Linux/macOS/Windows in CI (`by_path.sh`); every checker rule has a test (meta-test).
- Smoke tests found the audit skipping step 5: fixed with a `Stop` hook in the skill frontmatter (`verification_gate.py`), proven in an installed run. Checker fixes: missing `name` is a note outside uploads; `${CLAUDE_SKILL_DIR}` in uploads is a warning.
- CI `evals.yml` authenticates with `CLAUDE_CODE_OAUTH_TOKEN`, runs on PR open/reopen/ready or by hand, shows skipped without the token, evaluates a copy outside `$HOME`. Fifth PR review fixed (`e4d3cc7`); `anthropics/skills` dropped as a verification source (`2c6def5`).
- Next: Nery tests the latest zip and the skill-creator → hook offer; re-run the eval pilot; decide the CI eval key and trigger; `/release` (marketplace 0.2.0, tag `skill-diagnostics--v0.1.0`).

## 2026-10-11 — Bootstrap and publication

- Researched current plugin/marketplace docs and how `claude-plugins-official` versions (commit SHAs, no changelogs) → chose explicit SemVer.
- Built the repo: marketplace manifest, showcase README with generated catalog, `docs/` guides, issue forms, community files, labels, zero-dependency scripts with 18 tests, Validate + Release workflows, maintainer rules/skills/agents/templates.
- Verified: all gates green locally and in CI; end-to-end install of a throwaway plugin from a local marketplace; independent docs audit (fixed the findings that held up).
- Created the public GitHub repo from Nery's browser, pushed `c441921`, Release published `marketplace--v0.1.0`; set PRs to Collaborators only, topics, labels.
- Moved `CLAUDE.md` to `.claude/CLAUDE.md` and created committed project memory in `.claude/memory/`.
- Settled the cross-surface standard (Claude Code + Cowork) and saved the verified component matrix in `.claude/rules/cross-surface-compatibility.md`.
- Added `metadata.surfaces` declaration with README badge, catalog "Works in" column and enforced checks (22 tests); made maintenance skills invocable on explicit request.
- Next: choose and build the first plugin with `/new-plugin`.
