# Session log

Newest first. One entry per session: what changed, commits, what's next.

## 2026-10-11/12 — skill-diagnostics build (phases 0–9)

- Audited claude-essentials `skills-engineering`; rebuilt it as `skill-diagnostics` (audit-only skill, conformance + executability agents, `check_skill.py`, `PostToolUse` hook). Plan and audit live in claude.ai artifacts (see project-state).
- Evals pilot ($2.41), docs-auditor and plugin-reviewer reviews, isolated cached installs and installed self-audits; Nery tested synced zips in Cowork and Claude Code and reviewed PR #1 from another session. Every confirmed finding fixed.
- Design changes from testing: full-read auditors with only Read and a `check_skill.py --list` inventory (Glob is absent on macOS/Linux and caps at 100); coverage left to user settings; hook fires anywhere (`//**/SKILL.md`) and skips Claude Code-managed folders; synced-install docs.
- Course correction: the self-audit loop had grown `SKILL.md` 66%; refactored to moderate detail with `references/fallbacks.md`, recalibrated "decides output", updated `plugin-authoring.md`.
- Commits `caacfa4`…`HEAD` on `feat/skill-diagnostics`; CI green; Nery's local `main` holds a merge (not pushed).
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
