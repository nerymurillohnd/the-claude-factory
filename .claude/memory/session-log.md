# Session log

Newest first. One entry per session: what changed, commits, what's next.

## 2026-10-15 — agent-files-diagnostics rebuilt on dynamic workflows and run end to end

- Morning: `prompt-audit` on the four agents (six repetition findings, patch applied by an agent and verified: 4 files, 7 insertions, 11 deletions), a skill-creator review of `SKILL.md` (13,000 tokens, inverted disclosure, entry point at the end), and the `--keep-temp` question answered from disk: 152 of 153 kept eval folders have mode 500 with `sealed/` at 000, undocumented anywhere.
- Nery's decision: delete the plugin or complete it; then the specification "Evidence-Based Instruction and Memory Audit Plugin" on dynamic workflows, scope limited to the Markdown that Claude Code and Codex load. Research: docs MCP (plugin `workflows/`, plans, limits, failure semantics, journal) plus a $0.03 probe proving `agentType` keeps `tools`, `omitClaudeMd`, `model` and `effort`.
- Build: the `aca` package from `feat/agent-context-audit` ported into `skills/agent-context-audit/scripts/` without its workers, pipeline, hook and settings/MCP domain; new `store`, `stages`, `cli`, `coverage` (journal and transcript readers); domains A–E, four per-source fields, two unit identities; four agents to the spec's eleven sections; two workflow scripts with embedded schemas; `SKILL.md` rewritten as the coordinator's procedure; tests rewritten around a fake workflow journal (88 tests); README, CHANGELOG, spec; Biome skips workflow scripts; `pyrightconfig.json` execution environments.
- Real run on a fixture with eight planted defects, headless with `--plugin-dir` and an isolated home: `complete-with-findings`, 14 findings (10 medium, 4 low), every planted defect found, 15 of 15 sources read completely with proof, 13 of 14 findings verified independently, 14 of 14 inspected by the coordinator, files and git unchanged, 6 minutes, $1.67. Fixes after the run: `finalize --checked-json`, the audited home in the report's metadata, two definition clarifications.
- Gates: ruff, ruff format, mypy 3.9 strict, unittest on 3.9 and 3.14, every `by_path.sh`, Node script tests (47), `check-repo`, `catalog --check`, `validate-claude.sh` (13), `check-version-bump`, Biome, shellcheck, shfmt, markdownlint: all green.
- Next: commit and push; `plugin-reviewer`; `/test-installed-plugin`; an interactive run on a real repository; `sync-labels.mjs`; draft PR; delete `feat/agent-context-audit` and its draft PR when Nery confirms.

## 2026-10-14 — agent-files-diagnostics migrated; markdownlint scoped to human docs

- Branch `feat/agent-files-diagnostics` created from `main` (`6e2f202`) in a worktree, because the main checkout holds `feat/agent-context-audit` with 21 staged files that must not be touched.
- `agent-files-diagnostics` 0.1.0 migrated from `~/NSM/Claude` (where two review rounds, 33 items, had been applied the same day): `plugin.json` aligned with the repo, LICENSE, README (Claude Code only, minimum 2.1.271), CHANGELOG, marketplace entry (`testing`), catalog regenerated (11 plugins). The skill is user-invoked only (`disable-model-invocation: true`). The five instruction files got one H1 each (they had 23, 12, 8, 8, 8).
- Prettier reviewed against `forestal-mt` and `forestal-mt-store` and rejected: it would rewrite 124 files, 70 of them instruction files, and realign the catalog block `catalog.mjs` writes. markdownlint stays, now limited to human-read Markdown with explicit Prettier-like spacing (`MD004`, `MD007`, `MD049`, `MD050`, `MD060` compact); agent-consumed Markdown is excluded from every linter and formatter (41 files linted, 0 issues).
- Gates run: markdownlint, Biome, `check-repo`, `catalog --check`, `validate-claude.sh`, `check-version-bump`, all green. Not run: script tests and the Python gates (no code changed).
- Commits: `feat(agent-files-diagnostics)` (plugin, marketplace, catalog), `chore(lint)` (markdownlint scope and rule), `docs(memory)` (this wrap-up); pushed to `origin/feat/agent-files-diagnostics`, no PR yet.
- Next: Nery decides on the `/skill-diagnostics:audit` offer, the `DEVELOPMENT.md` move and the fate of `agent-context-audit`; then `plugin-reviewer`, an isolated install test with one real audit, `sync-labels.mjs`, and the draft PR.

## 2026-10-14 — drift fixes applied and plugin-evals 0.1.1

- `/release` check: every plugin's `plugin.json` version was already tagged, with no changes since; memory corrected (prompt-writer 0.2.0 released in PR #12, stale remote branches gone) in `6d37893`.
- Drift items 1–4 pushed to `main` in `b034d5e`: Claude Code 2.1.300 (its changelog was published after the check; nothing in it touches our plugins), mypy 1.20.2, uv 0.13.1, `claude-code-action` v1.0.250 by SHA, and both maintainer agents list the docs MCP by server pattern under both names. Full `/verify` green, actionlint clean, Validate on `main` green.
- `plugin-evals` 0.1.1 (PR #14, squash `95388e5`): references no longer claim the docs grade API-error runs; results row aligned with the page; snapshot re-checked on 2.1.300. 13 checks passed, eval job skipped (no `evals/`), Claude review "No issues found"; `release.yml` tagged `plugin-evals--v0.1.1`.
- `sync-labels.mjs` had not run since git-hygiene and plugin-evals were added: synced, 30 labels.
- Nery installed git-hygiene, plugin-evals and prompt-writer from the marketplace on the Mac; the synced copies now report "not loaded", as documented.
- Next: Nery adds the marketplace in the Claude app and removes the uploaded zips; the skill-diagnostics `Stop` gate (0.1.3); Claude app tests of git-hygiene and plugin-evals.

## 2026-10-14 — docs drift check

- `/docs-drift-check` against Claude Code 2.1.299 (changelog; npm 2.1.300 not yet documented), plugin docs, platform-support, the Cowork plugins guide, support 13837440, the Claude app release notes and the Claude Desktop changelog (v2.37337.1, 2026-10-13), and the latest tool and action releases.
- Found: Claude Code pin 2.1.296 behind; maintainer agents name an MCP server that doesn't exist on the Mac (2.1.299 exact-server `tools:`); mypy capped at 1.20.x by the 3.9 floor; uv and `claude-code-action` patch releases; one stale note in plugin-evals' sources; an Install/Add wording split between official pages. User docs, version gates and the compatibility matrix matched.
- Report only; no repo files changed besides memory.
- Next: Nery decides which drift fixes to apply (pin bump, agent `tools:`, mypy 1.20.2, plugin-evals note in a patch release).

## 2026-10-13 — prompt-writer comprehensibility audit and user-only invocation

- Three-reviewer comprehensibility audit (Red, Blue, Green; `Plan`, sonnet, high) of the `prompt-writer` skill: 34 consolidated findings; after re-reading the full scaffold and the design spec, 11 confirmed (5 narrowed) and 23 retired with evidence.
- Fixed in `SKILL.md`, `agentic-patterns.md`, README and CHANGELOG: the skill never runs the prompt, even when asked in the same message; out-of-list models keep the model-independent references; one prompt by default, split only for an unseen result or a fixed chain; paste the body only; a system prompt gets no contract header; live docs win, drift reported in the design notes; unattended runs name the visible actions they may take.
- Nery: the skill is user-invoked only (`disable-model-invocation: true`), verified headless (natural request: 0 Skill calls; slash command: skill loaded from the branch). Version call: 0.x breaking change → minor, next 0.2.0.
- Commit `89fff81` on `fix/prompt-writer-references` (signed, local), with the earlier uncommitted reference work, `lessons.md`, `formats-and-variables.md` and the spec; full `/verify` green (73 script tests, every gate ✔).
- Next: push and PR, Claude app test of the user-only skill, `/release prompt-writer minor`, Nery's yes/no on the `0.x` versioning rule line.

## 2026-10-13 — prompt-writer plugin and the marketplace without a version

- Built `prompt-writer` 0.1.0 from `prompt-writer.skill` on `feat/prompt-writer` (PR #8, merged `1aceba8`; `release.yml` tagged `prompt-writer--v0.1.0`). Personal references made generic (the user, they/their, no default conversation language). The executability audit of another copy and the plugin-reviewer findings were applied; `lessons.md` and personal rules of that copy stay out.
- Nery: the marketplace does not change version. Removed `version` from `marketplace.json`; `check-repo.mjs` now fails on it; `bump-version.mjs`, `release-notes.mjs` and `release.yml` handle plugins only; root `CHANGELOG.md` grouped by date; rules, CLAUDE.md, release and new-plugin skills and the PR template updated. Existing marketplace tags and releases kept as history.
- Fixed skill-diagnostics memory: 0.1.2 is released; its regression is still open (no Stop gate, no eval re-run).
- Next: `/test-installed-plugin prompt-writer` and a Claude app check (Cowork and chat); skill-diagnostics Stop gate; the TypeScript gate stays unwired (the typescript6 hook reports its 132 known `tsc` errors on every `.github/scripts` edit).

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
