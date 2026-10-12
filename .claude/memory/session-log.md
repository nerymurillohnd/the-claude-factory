# Session log

Newest first. One entry per session: what changed, commits, what's next.

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
