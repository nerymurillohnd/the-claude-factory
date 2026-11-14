# Claude configuration architecture: proposal and migration plan

- **Date:** 2026-11-13
- **Branch:** `ccr-60dfcba3-fsbz16` at `6b4600f` (local equals `origin`)
- **Claude Code:** 2.1.323
- **Status:** proposal for the owner's approval; nothing has been migrated
- **Inputs:** `.claude/maintainer/audits/2026-11-13-claude-configuration-inventory-audit.md` (verified below; corrections in 1.6), every file under `.claude/` except the ADR bodies not cited, `package.json`, `scripts/`, `claude plugin list --json` and `claude plugin details` for the 21 loaded plugins, the instruction checker (`check_instructions.py --project . --no-user`, with `--match`), and the official pages and changelog listed in section 7.
- **Owner decisions taken while writing it:** neutralize `superpowers`, `cloudflare`, `feature-dev`, `svelte-development`, `tailwind-development` and `pdf-viewer` in this repository; the skill gate denies the edit.

## Summary

The repository already has the right parts: a short CLAUDE.md, path-scoped rules, five project skills, four project agents, maintainer scripts behind npm, and this marketplace's own engineering plugins. What it lacks is one home per kind of content and anything that enforces which skill governs which work.

- 264 lines load in every session, two thirds of them `WORKFLOW.md`, a stage catalog that four other files repeat.
- Four subjects (version levels, release dates, categories, evals) are written two to four times in files that load together.
- `.claude/references/` and `.claude/templates/` are orphaned and cite files that do not exist.
- Nothing enforces "load the governing skill first". Third-party plugins inject a competing process at session start.

The target:
- CLAUDE.md of about 100 lines with a task-to-skill routing table and no import.
- Path rules with one home per convention.
- One new lifecycle skill that absorbs `WORKFLOW.md`, the orphaned templates and the drafts' stage content.
- A two-hook skill gate.
- Permission rules for the actions only the owner authorizes.
- Six synced plugins turned off here.

Eight steps, each one short session.

## 1. Findings

### 1.1 What works (keep)

- **Two-scope split** is stated once and clearly (`.claude/CLAUDE.md:28-35`).
- **Path-scoped rules** exist for every area and quote their globs; the checker finds 0 errors (2 warnings, 5 info, analysed in 1.3 and 1.5).
- **Project skills are procedures with scripts outside them:** `plugin-versioning`, `plugin-releases`, `plugin-catalog-changes`, `plugin-icons` and `docs-maintenance` call `npm run release:*`, `check:consistency` and `check:install` (claude-dir rule, `.claude/rules/architecture/claude-dir.md:11`).
- **One entry point for maintainer work:** 28 npm scripts in `package.json`.
- **This marketplace's own plugins cover their domains:** `instruction-engineering`, `hook-engineering`, `plugin-engineering`, `project-maintainer`, `github-operations`, `skill-diagnostics` and the three LSP plugins. The three LSP plugins already lint and type-check every edited Python, shell and TypeScript file through blocking PostToolUse hooks (`claude plugin details`).
- **Records:**
  - ADRs and debt live in `.claude/maintainer/`, written by `project-maintainer:write-records`.
  - Handoffs are read at start by that plugin's SessionStart hook.
- **The `@synced: false` mechanism works:** `frontend-design@synced` and `forestal-mt@synced` show `enabled: false` in `claude plugin list --json`, set by `.claude/settings.json:69,72`.

### 1.2 What loads every session

| Source | Size | Evidence |
| :-- | --: | :-- |
| `.claude/CLAUDE.md` + `@WORKFLOW.md` import (`CLAUDE.md:77`) | 264 lines (89 + 175) | checker: "Loaded at launch: 1 files, 264 lines including imports" |
| Skill and agent listings of 21 plugins | ~10,300 tokens (sum of `claude plugin details` Always-on lines) | cloudflare ~2,078; github-operations ~1,171; skill-diagnostics ~909; superpowers ~848; instruction-engineering ~836; svelte ~821; tailwind ~560 |
| SessionStart injections | project-maintainer protocol; superpowers' whole `using-superpowers` SKILL.md (65 lines, wrapped in `<EXTREMELY_IMPORTANT>`) | `hooks/session-start` line 49 of superpowers 7.0.2 |

`WORKFLOW.md` is a 20-stage command catalog. Most tasks touch one or two stages, yet all of it loads every time. Imports never reduce context ([memory: imports](https://code.claude.com/docs/en/memory)).

### 1.3 Overlaps: one subject, several homes

Each row lists files that load together (checker `--match`) or that a task reads together.

| Subject | Homes today | Evidence |
| :-- | :-- | :-- |
| Version bump levels | `rules/plugins.md:50-57`, `rules/plugins/versioning.md:11-17`, `plugin-versioning` step 2, `refactor.md:351-355` | `plugins/<p>/.claude-plugin/plugin.json` loads `plugins.md`, `plugins/versioning.md`, `plugins/categories.md` and `hook-scripts.md` together |
| Release dates (UTC) | `CLAUDE.md:86-89`, `rules/plugins/versioning.md:19-22`, `plugin-releases` step 4, `docs-maintenance/references/governance.md:54` | checker near-duplicate `CLAUDE.md:89` / `versioning.md:22` (73%) |
| Category | `rules/plugins.md:59-61`, `rules/plugins/categories.md:13-18` | checker near-duplicate `plugins.md:61` / `categories.md:18` (64%) |
| Evals policy | `rules/plugins.md:79-84`, `rules/plugins/evals.md` (whole), `WORKFLOW.md:97-101`, `references/evals-ci.md`, `CLAUDE.md:65` | `.github/workflows/release.yml` loads `plugins.md`, `evals.md` and `github.md` |
| PRs inside `plugins/` | `CLAUDE.md:81-84`, `rules/plugins.md:74-77`, `CLAUDE.draft.md:45-49` | three wordings of one policy |
| Agent model and effort | `CLAUDE.md:51-54`, `rules/architecture/claude-dir.md:9` | same two sentences |
| Stage commands | `WORKFLOW.md`, `refactor.md` Part 1, `CLAUDE.draft.md:103-145`, each project skill, `cli-commands-guide` | inventory audit section 12 |
| CLI gotchas | `refactor.md` Part 1, `agents/testers/plugin-tester.md:27-44`, `tooling-tester.md:29-36`, `cli-commands-guide` | copied bullets, e.g. "`--plugin-dir` at a marketplace root loads nothing" |
| README rules | `agents/docs-maintainers/plugin-readme-writer.md:57-275`, `docs-maintenance/references/documents/plugin-readme.md` | two homes for one document's rules; `governance.md:36` says the agent "already knows" them |
| Plugin install test | `agents/testers/plugin-tester.md` (manual `CLAUDE_CONFIG_DIR` flow), `npm run check:install` (`scripts/release/check-install.sh`) | the script already isolates and checks the install |
| Mechanical doc consistency | `npm run check:consistency` (PC-01…PC-10), `docs-consistency-auditor` checklist lines 96-98, 101-102 | the agent re-checks what the script fails on |
| Skill authoring | `references/skill.md` + template, `skill-creator`, `superpowers:writing-skills`, `public-marketplace-dev` | four sources, no designated one |
| Planning process | `superpowers` (brainstorming, writing-plans, executing-plans…), `feature-dev`, built-in `Plan`/`Explore`, the owner's task flow in the claude.ai preferences | competing mandates (1.4) |

### 1.4 Conflicts

| # | Conflict | Evidence | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | Draft vs rule in force on where stage procedures live | `refactor.md:580` (Appendix F) sends them to `.claude/maintainer/blueprint.md`; `claude-dir.md:6` keeps them in `WORKFLOW.md` | Neither: a lifecycle skill (section 2). Changes `claude-dir.md:6` |
| C2 | Rule in force contradicts the repository | `rules/architecture/scripts.md:14` says release scripts target Python 3.12 and run "by path on the runner's `python3`"; `ruff.toml:7-9` targets 3.15, `release.yml:35-53` runs `uv run python`, ADR_2026-11-13_release-workflow-runs-python-through-uv | Fix the rule to the ADR |
| C3 | A rule in force points to a draft as its source | `scripts.md:22` "Look up a script in `.claude/architecture/refactor.md` before writing it" | Point to the backlog's new home (section 5, step 5) |
| C4 | CHANGELOG-only change: bump or not | `plugin-versioning` step 1: "`CHANGELOG.md` included: bump"; `rules/plugins.md:57` and `versioning.md:16`: documentation-only changes take no bump; `docs-maintenance` small-fix event: no bump | Decision D3 |
| C5 | "In CI, only the evals run" vs the planned validate CI | `CLAUDE.md:65`; handoff 2026-11-13-1047 item 2 plans `validate.yml` running `claude plugin validate` on plugins; `release.yml` waits on `Validate` | Reword: plugin behavior is tested locally; CI runs validation and evals (D6) |
| C6 | Third-party session mandate vs the owner's task flow | superpowers' SessionStart: "Invoke relevant or requested skills BEFORE any response… including clarifying questions" and "Before entering plan mode… invoke the brainstorming skill"; the owner's preferences require stating the approach and waiting for approval | Owner decided: neutralize here |
| C7 | Scope bleed | `rules/plugins.md` (plugin scope) loads for `.github/workflows/**` (maintainer CI) only because of its Evals section; `skill-lint.md` (`scripts/**/*.py`) loads for every release script | Narrow globs (step 2) |
| C8 | Memory location | `CLAUDE.md:58` keeps repository memory in `.claude/memory/`; `settings.json:78` sets `autoMemoryDirectory` to `~/Claude/repositories/the-claude-factory/.claude/memory`, which in this cloud session resolves to `/root/Claude/…/memory` (empty, outside the checkout `/home/user/the-claude-factory`) | D5 |
| C9 | Draft CLAUDE.md drops "unless the owner asks for one" for doc-only plugin PRs | `CLAUDE.draft.md:48` vs `rules/plugins.md:77` and `CLAUDE.md:84` | Keep the rule in force's wording |

### 1.5 Missing or broken

| # | Gap | Evidence |
| :-- | :-- | :-- |
| G1 | Nothing enforces which skill governs which file | `.claude/settings.json` registers no hook; the owner's 2026-11-13 memory records a skipped-skill failure (`.claude/memory/research-claude-code-with-the-project-skills.md:14`) |
| G2 | No end-to-end route from an idea to a shipped plugin, and no procedure for a new plugin | `WORKFLOW.md:29-32`: "No command"; no project skill covers scaffolding; `refactor.md:148-150` lists the scaffold scripts as Pending |
| G3 | Orphaned, stale templates | No file under `.claude/` except `claude-dir.md:12` and `refactor.md:301,329` names `.claude/references/` or `.claude/templates/`. They cite missing files: `references/skill.md:50` (`.claude/hooks/skill-frontmatter.py`), `:58` (`scripts/validators/skill-names-consistency.py`, `skill-size.py`); `references/plugin-manifest.md:19` (`.claude/skills/building-plugins/…`), `:38` (`scripts/categories.json`), `:47,61,68` (`npm run generate`, `generate:check`), `:63` (`scripts/schemas/` "is strict", the folder is empty); `references/evals-ci.md` (`.claude/skills/testing-plugins/…`); `references/README.md:38` calls `.github/VULNERABILITY_REPORT.yml` unused while `rules/architecture/github.md:13` and `lint:github` use it, and links a `security.md` that does not exist |
| G4 | Owner-only actions are guarded by prose only | Push, PR create/merge and workflow dispatch need the owner's explicit authorization (owner preferences; handoff "Context for the next session"); `settings.json:41-48` denies only force-push, repo delete and pip |
| G5 | Lockfile rule in prose only | `CLAUDE.md:47` "never edit `uv.lock` by hand"; no deny rule |
| G6 | No reviewer for plugin-scope rules | Safety, portability, prerequisites, surfaces and Windows (`rules/plugins.md:20-23, 63-72`) are checked by no script or agent; `check:consistency` and `validate:portable` cover mechanical parts only |
| G7 | Stale text in force | `plugin-releases/SKILL.md:12` names branch `claude/repo-refactor-redesign-feqwzk`; `refactor.md:3-4` header and Part 2 describe that branch |
| G8 | `enableAllProjectMcpServers: true` (`settings.json:5`) is a no-op | there is no `.mcp.json` |
| G9 | Project `enabledPlugins` never reach cloud sessions, so cloud work runs on the account's synced copies | Documented behavior: "A cloud session doesn't install the plugins a repository turns on under `enabledPlugins`, including ones from the marketplaces it lists under `extraKnownMarketplaces`" ([cloud-environments, What carries over](https://code.claude.com/docs/en/cloud-environments)). Here the synced `plugin-engineering` is 0.2.3 while the branch has 0.2.4 |
| G10 | skill-diagnostics gate always on | `userConfig.on_skill_write` options `gate`/`suggest`/`off`, default `gate`; no override anywhere (`pluginConfigs` null), and it can be overridden only in user or managed settings; the owner declined these audits (handoff item 12) |

### 1.6 Corrections to the inventory audit

- Section 10 says nothing about `mcp-server-dev@claude-plugins-official`: it loads (~504 tokens), and `claude plugin list --json` omits it.
- Section 11 misses two session hooks: the cloud launcher's Stop hook `~/.claude/stop-hook-git-check.sh`, which blocks on uncommitted, unpushed or unverified commits, and `prompt-writer`'s skill-scoped Stop agent hook.
- Section 13.6: the `.claude/hooks/**` glob of `hook-scripts.md` matches nothing today only because no project hook exists; it becomes live with step 3. It is not a defect to remove.
- The checker's `duplicate-line` between `rules/plugins/categories.md:3` and `rules/hook-scripts.md:4` compares two `paths` entries (`plugins/*/.claude-plugin/plugin.json`), not instructions: a false positive.
- Missed entirely: G3 (stale references) and C2, C3, C4, C5, C7.
- `claude plugin details github-operations` reports `Agents (0)`, but its four nested agents are registered in this session (`github-operations:pr-lifecycle:pr-tracker` and the others appear among the available agent types).

### 1.7 Published-plugin defects noticed (outside this task, reported now)

- **`tailwind-development` 0.3.3, as synced:** its MCP server fails with `CONNECTION_CLOSED`. `mcp/server.mjs` imports `@modelcontextprotocol/server` and `zod`, and the synced copy has no `node_modules`. The cause is not confirmed.
- **`svelte-development` 0.1.3:** its agents allow `mcp__plugin_svelte-development_svelte__*`, but this session exposes the server as `mcp__svelte__*`. Whether the agents get the tools is not verified.

Both are plugin-scope work and need their own task.

## 2. Target architecture

### 2.1 One home per kind of content

| Kind of content | Single home | Loads | Pointed to by |
| :-- | :-- | :-- | :-- |
| Project identity, surfaces, OS targets, roles | `.claude/CLAUDE.md` | always | root `README.md` (for people) |
| The two scopes | `.claude/CLAUDE.md` | always | first line of `rules/plugins.md` and `rules/architecture/claude-dir.md` |
| Owner-only actions and the PR policy (inside and outside `plugins/`) | `.claude/CLAUDE.md`, enforced by `permissions.ask` | always / on the tool call | `plugin-versioning` step 8, `plugin-releases` step 5 |
| Verification standard | `.claude/CLAUDE.md` (trimmed; the owner's preferences hold the general version) | always | — |
| Task routing (what work → which skill or agent) | `.claude/CLAUDE.md` routing table | always | skill descriptions (triggers), the gate map (paths) |
| Core maintainer commands and "only through `npm run`" | `.claude/CLAUDE.md` (≈10 lines); `package.json` is the truth | always | `rules/npm-and-uv.md` |
| Lifecycle order and every stage's commands | `skills/plugin-lifecycle/references/stages.md` | on demand | routing table |
| Plugin CLI facts and gotchas | `plugin-engineering:cli-commands-guide` (installed) | on demand | `plugin-lifecycle`, `plugin-tester` (preload) |
| Official plugin, skill, agent, hook and MCP docs | `plugin-engineering:public-marketplace-dev` (installed) | on demand | `plugin-lifecycle`, gate rows |
| Claude Code facts in general | `anthropic-skills:cc-docs-research` + Claude Code Docs MCP | on demand | routing table (replaces the memory file) |
| Plugin-scope conventions: design, safety, license, names, version invariants, surfaces, portability, testing policy | `rules/plugins.md` | path: `plugins/**`, `.claude-plugin/**`, root `README.md`, `CHANGELOG.md` | CLAUDE.md scopes |
| Categories | `rules/plugins/categories.md` | path | — |
| Evals policy | `rules/plugins/evals.md` | path: `plugins/*/evals/**`, `.github/workflows/**` | — |
| Icons policy | `rules/plugins/icons.md` | path | `plugin-icons` |
| npm and uv | `rules/npm-and-uv.md` (from the draft) | path: manifests, lockfiles, configs, `scripts/**` | CLAUDE.md one line |
| Script placement and blueprint rules | `rules/architecture/scripts.md` | path: `scripts/**` | — |
| skill-lint internals | `rules/skill-lint.md` | path: `scripts/validators/skill_lint/**`, `scripts/validators/skill-lint.py`, `scripts/testers/skill_lint/**` | — |
| Hook script conventions | `rules/hook-scripts.md` | path (live once `.claude/hooks/` exists) | — |
| Naming other skills from a skill | `rules/skill-references.md` (from the draft) | path: `.claude/skills/**`, `plugins/*/skills/**` | — |
| `.claude/` layout and agent model and effort policy | `rules/architecture/claude-dir.md` | path: `.claude/**` | — |
| `.github/` and `docs/` conventions | `rules/architecture/github.md`, `docs.md` | path | — |
| Procedures: versioning, releases, catalog changes, icons, documents | the five project skills | on demand | routing table, gate |
| Procedure: idea → new plugin → change → fix → release, end to end | `skills/plugin-lifecycle/` (new) | on demand | routing table, gate |
| Release dates (UTC, publish day) | `docs-maintenance` `references/documents/changelog.md` (Rules), applied by `plugin-releases` step 4 and `npm run release:changelog` | on demand | `docs-maintenance` governance and `marketplace-changelog.md` (pointers) |
| Version levels | `plugin-versioning` step 2 | on demand | `rules/plugins.md` (one pointer line) |
| Document templates | `docs-maintenance/assets/` + `references/documents/` | on demand | — |
| Non-document templates (manifest, skill, agent, evals workflow) | `plugin-lifecycle/assets/` + `references/` (moved from `.claude/templates/`, `.claude/references/`; **changes `claude-dir.md:12`**) | on demand | `plugin-lifecycle` |
| Records: ADRs, debt | `.claude/maintainer/decisions/`, `technical-debt/` via `project-maintainer:write-records` | on demand; mod guards on write | gate rows |
| Plans, specs, audits | `.claude/maintainer/plans/`, `specs/`, `audits/` | on demand | — |
| Native validator coverage (E1–E14, NV-*) | `.claude/maintainer/audits/2026-11-09-native-validator-coverage-audit.md` (from `refactor.md` Appendix A and its gotchas) | on demand | `tooling-tester` |
| Pending maintainer scripts | `.claude/maintainer/plans/<date>-maintainer-scripts-backlog.md` (from `refactor.md` script status) | on demand | `rules/architecture/scripts.md` |
| Handoffs | `.claude/session-handoff/` via `project-maintainer:write-handoff` | SessionStart hook | — |
| Repository memory | `.claude/memory/` + `MEMORY.md` | at start, through `autoMemoryDirectory` (D5) | CLAUDE.md memory lines |
| Enforcement | `.claude/settings.json` (hooks, `permissions`), `.claude/hooks/`, plugin hooks, CI | by event | section 4 |
| Tests of maintainer scripts and project hooks | `scripts/testers/` (`npm run test:scripts`) | — | `rules/architecture/scripts.md` |
| Tests of plugins | each plugin's own (`claude plugin test`, evals), `npm run check:install`, `plugin-tester` | — | `rules/plugins.md` testing policy |
| Saved workflows (Workflow tool) | none now; `.claude/workflows/` only when a fan-out repeats (first candidate: a catalog-wide semantic README audit for DEBT-001) | `/<name>` | — |

### 2.2 Target CLAUDE.md (about 100 lines, no import)

| Section | Source | Note |
| :-- | :-- | :-- |
| What it is, platforms | `CLAUDE.draft.md:3-15` | keep |
| Who works on it | `CLAUDE.draft.md:17-22` | keep |
| Scopes | `CLAUDE.md:28-35` | keep; the draft's per-scope lists (`CLAUDE.draft.md:30-43`) only where they settle a real ambiguity |
| Owner-only actions and pull requests | `CLAUDE.md:81-84` + `rules/plugins.md:74-77` + `CLAUDE.draft.md:45-49` | one home; keeps "unless the owner asks" (C9) |
| Routing table | new | ≈15 rows: plugin work → `plugin-lifecycle`; documents → `docs-maintenance`; instruction files → `instruction-engineering:claude-md-and-rules`; hooks → `hook-engineering:hook-development`; settings → `update-config`; PRs → `github-operations:auto-pr-lifecycle`; workflows → `github-operations:claude-github-actions`; GitHub files → `github-operations:github-files-setup`; cleanup → `github-operations:cleanup-and-debug`; ADRs and debt → `project-maintainer:write-records`; handoff → `project-maintainer:write-handoff`; skill audit → `npm run lint:skills`, then `skill-diagnostics:skills-best-practices` on request; Claude Code facts → `anthropic-skills:cc-docs-research` + `plugin-engineering:cli-commands-guide`; plugin review → `plugin-release-reviewer` |
| Verification | `CLAUDE.md:67-73` | keep 69, 70, 72, 73; fold the Commitment section (`CLAUDE.md:20-24`) into one line; drop 71 (checker no-op candidate) |
| Core commands | `CLAUDE.draft.md:105-122` | setup, check, lint, typecheck, validate, check:consistency, lint:skills, test:scripts; plus "run maintainer tasks only through `npm run`" |
| Repository memory | `CLAUDE.md:56-60` | keep |
| Cloud sessions | `CLAUDE.draft.md:147-151` | keep |
| Removed | `CLAUDE.md:41-47` (Tooling) → `rules/npm-and-uv.md`; `51-54` → `claude-dir.md`; `62-65` → routing + rules by path, `65` reworded (D6); `75-77` import → `plugin-lifecycle`; `86-89` → `plugin-releases`; `CLAUDE.draft.md:69-101` (stack table, repository map) → deleted as discoverable from `package.json` and the tree | always-loaded lines: 264 → ≈100 |

### 2.3 Target tree of `.claude/`

```text
.claude/
├── CLAUDE.md                    always · identity, scopes, owner-only actions, routing, verification, core commands, memory, cloud
├── settings.json                permissions (allow, ask, deny), enabledPlugins (six synced plugins off), hooks (skill gate)
├── hooks/
│   ├── skill-gate.sh            PreToolUse Edit|Write: denies an edit until the file's governing skill is loaded
│   ├── skill-record.sh          PostToolUse Skill + UserPromptExpansion: records the skills loaded in the session
│   └── skill-gate.tsv           the map: path glob → skill; agent type → skills it preloads
├── rules/                       all path-scoped
│   ├── plugins.md               plugins/**, .claude-plugin/**, README.md, CHANGELOG.md
│   ├── plugins/{categories,evals,icons}.md
│   ├── npm-and-uv.md            (from architecture/rules/)
│   ├── skill-references.md      (from architecture/rules/)
│   ├── hook-scripts.md
│   ├── skill-lint.md            (narrowed globs)
│   └── architecture/{claude-dir,docs,github,scripts}.md
├── skills/
│   ├── plugin-lifecycle/        NEW · SKILL.md (router) · references/{stages,new-plugin,plugin-manifest,skill,agent,evals-ci}.md · assets/*-template.md
│   ├── docs-maintenance/  plugin-versioning/  plugin-releases/  plugin-catalog-changes/  plugin-icons/
├── agents/
│   ├── auditors/{docs-consistency-auditor,plugin-release-reviewer}.md   (the second is new, Opus)
│   ├── docs-maintainers/plugin-readme-writer.md
│   └── testers/{plugin-tester,tooling-tester}.md
├── memory/                      MEMORY.md + one file per fact
├── maintainer/                  decisions/ technical-debt/ plans/ specs/ audits/
└── session-handoff/
Removed once migrated: WORKFLOW.md, architecture/, references/, templates/, rules/plugins/versioning.md
```

### 2.4 What happens to the drafts

| Draft | Verdict | Where each part goes |
| :-- | :-- | :-- |
| `architecture/CLAUDE.draft.md` | **Merge** into the new CLAUDE.md (2.2) | stack table and repository map deleted; Testing (`:51-67`) policy lines → `rules/plugins.md` Testing; mod procedures → `plugin-lifecycle` |
| `architecture/refactor.md` | **Split and retire** | blueprint rules 1-2, 5-6 → `rules/architecture/scripts.md`; rule 3 → CLAUDE.md core commands line; Part 1 commands → `plugin-lifecycle/references/stages.md`; `[E#]`/`[NV-#]` gotchas and Appendix A → the coverage audit; `[docs]`/`[skill]` gotchas dropped (`cli-commands-guide` holds them); script status → the backlog plan; Part 2 and Appendix F superseded by this proposal |
| `architecture/rules/npm-and-uv.md` | **Keep**, adopt | replaces `CLAUDE.md:41-47`; one pointer line stays in CLAUDE.md because commands run before a manifest is opened |
| `architecture/rules/plugins.md` | **Merge** its one extra line (in-plugin files and links) into the rule in force | — |
| `architecture/rules/skill-references.md` | **Keep**, adopt | — |

## 3. Installed versus to build

### 3.1 Installed (21 loaded plugins plus built-ins)

| Plugin · component | Verdict | How the project uses it |
| :-- | :-- | :-- |
| instruction-engineering · `claude-md-and-rules`, agent `reviewer` | **Use** | gate row for instruction files; the reviewer checks steps 2 and 5 |
| hook-engineering · `hook-development`, agent `hook-engineer` | **Use** | gate row for hook files; lint and probe scripts test step 3 |
| plugin-engineering · `public-marketplace-dev`, `cli-commands-guide` | **Use** | `plugin-lifecycle` loads them; `plugin-tester` preloads the guide |
| project-maintainer · `write-records`, `write-handoff`, SessionStart hook, mod guards | **Use** | gate rows for records and handoffs |
| github-operations · 4 skills, 2 commands, 4 nested agents | **Use** | routing rows; the agents only through `auto-pr-lifecycle` and `cleanup-and-debug` |
| skill-diagnostics · `skills-best-practices`, 6 agents, hooks | **Use on request**; set `on_skill_write` per D4 | deterministic `npm run lint:skills` first |
| prompt-writer | **Use on request** (user-invoked only) | — |
| bash- / python- / typescript6-lsp-intelligence | **Use** | their PostToolUse hooks are the post-edit linters |
| svelte-development, tailwind-development | **Neutralize here** (owner) | test them with `--plugin-dir` when they change |
| superpowers (15 skills, SessionStart) | **Neutralize here** (owner) | replaced by: the owner's task flow and plan mode (brainstorming, plans); `skill-lint.md:38` and the scripts rule (TDD); CLAUDE.md Verification (verification-before-completion); built-in `code-review` and github-operations (reviews); `public-marketplace-dev` + `lint:skills` (writing-skills) |
| feature-dev (command, 3 agents) | **Neutralize here** (owner) | built-in Explore and Plan, `code-review` |
| cloudflare (22 skills, MCP) | **Neutralize here** (owner) | not used in this repository |
| pdf-viewer | **Neutralize here** (owner) | not used |
| claude-code-setup | **Use on demand** | ~141 tokens |
| skill-creator | **Use** only for trigger evals and description tuning | authoring goes through `public-marketplace-dev` |
| cowork-plugin-management | **Not used**; left on (not in the owner's six) | revisit: ~259 tokens |
| playwright (MCP) | **Keep** | ~0 tokens |
| mcp-server-dev (official, project-enabled) | **Use** when a plugin ships an MCP server | — |
| Built-in Explore, Plan, general-purpose, claude-code-guide; `code-review`, `security-review`, `simplify`, `update-config` | **Use** | `update-config` is the gate row for `settings.json` |
| Built-in `init` | **Drop** | CLAUDE.md exists |

Always-on cost removed by the six neutralized plugins: 2,078 + 848 + 821 + 560 + 240 + 228 ≈ 4,775 tokens per session (`claude plugin details`, 2026-11-13).

### 3.2 To build

| # | Item | Kind | Trigger |
| :-- | :-- | :-- | :-- |
| B1 | `skill-gate.sh` + `skill-record.sh` + `skill-gate.tsv` | project hooks | every Edit or Write; every Skill call and typed `/skill` |
| B2 | `plugin-lifecycle` | project skill, invoked by Claude and the owner | any plugin idea, new plugin, change, fix, issue to fix, release, rename or removal, or "what's next for plugin X" |
| B3 | `plugin-release-reviewer` | project agent, Opus, read-only, adversarial | `plugin-releases` step 1; review of a PR that changes `plugins/` |
| B4 | `issue-triage` (later) | project skill, user-invoked (`disable-model-invocation: true`) | `/issue-triage`, or the scheduled task in `specs/issue-triage-task-prompt.md`; after handoff items 2 and 4 |
| B5 | Biome post-edit check (optional) | project hook, PostToolUse | Edit or Write of files `biome.jsonc` includes |
| — | `validate.yml` | CI, outside Claude Code | the owner's open decision (handoff item 2); this proposal only depends on it for C5 |

## 4. Enforcement

| Must never be skipped | Mechanism | Event, matcher | Effect | How it is tested |
| :-- | :-- | :-- | :-- | :-- |
| The governing skill is loaded before its files are edited | B1 | PreToolUse `Edit\|Write`, `onFailure: "block"`, `timeout` 5 | deny with "Load the `<skill>` skill with the Skill tool, then retry"; unmapped paths pass silently; unreadable input exits 2 | below |
| The skills loaded are known | B1 recorder | PostToolUse `Skill`; UserPromptExpansion (no matcher) | appends the skill name to `${TMPDIR:-/tmp}/claude-skill-gate/<session_id>`; never blocks | below |
| Push, PR create or merge, workflow dispatch, label apply, tag push only with the owner's authorization | `permissions.ask` | `Bash(git push*)`, `Bash(gh pr create*)`, `Bash(gh pr merge*)`, `Bash(gh workflow run*)`, `Bash(gh api *dispatches*)`, `Bash(claude plugin tag * --push*)`, `Bash(npm run labels:sync -- --apply*)`, and the GitHub MCP tools that create or merge PRs, push files or run workflows (both server names) | a prompt every time | in a session, `git push --dry-run` raises the prompt |
| Lockfiles change only through npm or uv | `permissions.deny` | `Edit(/uv.lock)`, `Edit(/package-lock.json)` | Edit and Write refused | an Edit of `uv.lock` is refused; `npm ci` and `uv sync --locked` still run |
| Lint and types on every edit | existing plugin hooks | PostToolUse (LSP plugins) | block on findings | already active |
| Record format | existing project-maintainer mod | `tool.call` / `tool.check` | deny or ask | already active (whether it loads is unverified) |
| Repository checks before merge | CI | `validate.yml` | required check | outside this proposal |

**Not enforced, with the reason:**
- the scope split and the verification standard need judgment;
- whether a `plugins/` change needs a PR is better done by CI on the diff later.

The gate is a barrier for Claude, not a security boundary: a Bash write bypasses it (hook-development, "Pick the mechanism").

**How B1 is tested (step 3):**
1. **Capture real input first.** A temporary `.claude/settings.local.json` hook writes stdin to the scratchpad for one PostToolUse `Skill` call and one PreToolUse `Edit`. This is needed because the Skill tool's `tool_input` schema is not documented.
2. **Unit tests.** `scripts/testers/hooks/test_skill_gate.py` runs the scripts with sample JSON on stdin and a temporary `TMPDIR`, through `npm run test:scripts`. Cases:
   - (a) mapped path, no record → one JSON object with `permissionDecision: "deny"` naming the skill;
   - (b) mapped path, skill recorded → exit 0, no output;
   - (c) unmapped path → exit 0, no output;
   - (d) not JSON → exit 2;
   - (e) no `tool_input.file_path` → exit 2;
   - (f) first match wins: `plugins/x/hooks/a.sh` → `hook-engineering:hook-development`, not the plugin row;
   - (g) a subagent whose `agent_type` preloads the skill → exit 0;
   - (h) the recorder on a PostToolUse `Skill` sample and on a UserPromptExpansion sample → the name is in the record;
   - (i) a path outside the project → exit 0;
   - (j) every skill in the map is named in the CLAUDE.md routing table.
3. **Static checks.**
   - `python3 <hook-engineering>/skills/hook-development/scripts/lint-hooks-config.py .claude/settings.json` exits 0 with no ERROR.
   - `npm run lint:shell` exits 0.
   - `probe-hook.py --on-failure block` on inputs (a), (b) and (d) predicts deny, silent and block.
4. **Live check.**
   - In a session started with `--debug-file`, ask for a one-word fix in a plugin README without naming a skill. The deny shows, Claude loads `docs-maintenance`, the retry succeeds, and `/hooks` lists both hooks as project hooks.
   - Revert the test edit.

## 5. Migration plan

**Progress (2026-11-13):**
- Step 1 done: `fddcae2`, `45023d4`.
- Step 2 done, with four refinements:
  - the release dates' single home is the changelog procedure, which already held the rule;
  - `scripts.md:22` keeps its pointer until step 5b creates the backlog plan;
  - `plugin-releases` keeps its `validate.yml` warning, minus the stale branch name, because the warning is still true;
  - D6 was applied in step 2, because removing the Evals section would have left `CLAUDE.md:65` pointing at nothing.
- Step 5a changed and done early. The owner's CLAUDE.md draft was promoted as `.claude/CLAUDE.md`, not a new file of about 100 lines composed as section 2.2 describes. ADR_2026-11-13_claude-configuration-architecture-on-the-owners-claude-md records it and supersedes the earlier architecture ADR.
  - The draft received the old Commitment, Repository memory and Verification sections, and seven fixes from an independent review.
  - `rules/npm-and-uv.md` was adopted.
  - The CLAUDE and plugins drafts were deleted.
  - `WORKFLOW.md` is now reached through a pointer until step 4.

Each step is one short session and ends with one commit per topic on the working branch. Nothing is pushed without the owner's authorization. Undo is `git revert <commit>` unless stated. Before each step, load the skill the gate or the routing table names for the files it touches.

| Step | Changes | Checks (command → expected) | Undo |
| :-- | :-- | :-- | :-- |
| **1. Decision record and settings hygiene** | ADR for this architecture (`project-maintainer:write-records`). `settings.json`: six `"<name>@synced": false`; remove `enableAllProjectMcpServers`; add the `ask` and `deny` rules of section 4 | `jq empty .claude/settings.json` → exit 0. New session: `claude plugin list --json \| jq -r '.[] \| select(.id \| test("^(superpowers\|cloudflare\|feature-dev\|svelte-development\|tailwind-development\|pdf-viewer)@synced$")) \| "\(.id) \(.enabled)"'` → six lines ending `false`. No `using-superpowers` text at session start. `git push --dry-run` → permission prompt. An Edit of `uv.lock` → refused | revert; the six plugins come back at the next session |
| **2. One home per rule (no new files)** | `rules/plugins.md`: drop Version bumps, Category, PRs, Evals and the `.github/workflows/**` path; add the draft's in-plugin-files line. Delete `rules/plugins/versioning.md`. CLAUDE.md: drop Dates and Models. `scripts.md:14` → uv run on 3.15, `:22` → backlog plan. `skill-lint.md` globs narrowed. `plugin-releases/SKILL.md:12` removed. `plugin-versioning` step 1 per D3. `governance.md:54` → pointer | Checker → 0 errors; no near-duplicate for dates or category. `--match`: `plugins/github-operations/.claude-plugin/plugin.json` → plugins.md, categories.md, hook-scripts.md (no versioning.md); `.github/workflows/release.yml` → github.md, evals.md (no plugins.md); `scripts/release/release-notes.py` → scripts.md (no skill-lint.md); `scripts/validators/skill_lint/cli.py` → skill-lint.md, scripts.md. `npm run lint:skills -- .claude/skills/plugin-releases` and `-- .claude/skills/plugin-versioning` → exit 0. `npm run validate:claude` → exit 0 | revert |
| **3. Skill gate** | B1 scripts and map, the hooks block in `settings.json`, the tests, `claude-dir.md` (hooks line). The map rows: plugin docs and root docs → `docs-maintenance`; `plugins/*/hooks/**`, `.claude/hooks/**` → `hook-engineering:hook-development`; icon sources → `plugin-icons`; `.claude/CLAUDE.md`, `.claude/rules/**` → `instruction-engineering:claude-md-and-rules`; `.claude/settings.json` → `update-config`; `.github/workflows/**` → `github-operations:claude-github-actions`; other `.github/` files → `github-operations:github-files-setup`; ADRs and debt → `project-maintainer:write-records`; handoffs → `project-maintainer:write-handoff`; `.claude/skills/**`, `.claude/agents/**` → `plugin-engineering:public-marketplace-dev`; `.claude-plugin/marketplace.json` and the rest of `plugins/*/**` → `plugin-engineering:public-marketplace-dev` until step 4 | Section 4 test list: `npm run test:scripts` → OK; lint-hooks-config → exit 0; `npm run lint:shell` → exit 0; probe predictions; the live check. Checker `--match .claude/hooks/skill-gate.sh` → hook-scripts.md (the glob is now live) | revert; for an emergency, `{"disableAllHooks": true}` in `.claude/settings.local.json` |
| **4. `plugin-lifecycle` skill** | Create the skill. `WORKFLOW.md` stages → `references/stages.md`, keeping each stage's **Docs** line. Move `.claude/references/*` and `.claude/templates/*` into it, fixing every G3 line. Add `references/new-plugin.md` (folder, manifest, components, the documents through `docs-maintenance` New plugin, icon through `plugin-icons`, catalog entry, 0.1.0 through `plugin-versioning`, `labels:sync`). Gate rows for `plugins/*/**` and `marketplace.json` → `plugin-lifecycle`. `claude-dir.md:12` updated | `npm run lint:skills -- .claude/skills/plugin-lifecycle` → exit 0. `npm run validate:claude` → exit 0. `grep -rn '\.claude/references\|\.claude/templates' .claude --exclude-dir=maintainer --exclude-dir=session-handoff` → nothing. Fresh session: "I have an idea for a plugin that …" → Claude loads `plugin-lifecycle` first (observed in the transcript) | revert (`WORKFLOW.md` still exists until 5a) |
| **5a. New CLAUDE.md** | CLAUDE.md per 2.2, with a keep, migrate and delete table for every original line. Remove `@WORKFLOW.md` and delete `WORKFLOW.md`. Adopt `rules/npm-and-uv.md`, `rules/skill-references.md` and the Testing policy in `rules/plugins.md`. Update `claude-dir.md:6` | Checker "Loaded at launch" ≤ 110 lines (from 264), 0 errors. `instruction-engineering:reviewer` given the old files and the table → no lost instruction. `grep -rn 'WORKFLOW\.md' . --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=maintainer --exclude-dir=session-handoff` → nothing. `npm run check` → the same result as before the step (pre-existing failures: DEBT-003, `lint:js`) | revert |
| **5b. Retire the drafts** | Split `refactor.md` per 2.4 into the coverage audit, the backlog plan and `scripts.md`. Delete `.claude/architecture/` and its `!.claude/architecture` entry in `biome.jsonc:52`; drop `!.claude/references` and `!.claude/templates` (`biome.jsonc:50-51`) | `npm run lint:js` → no new findings. `test -d .claude/architecture` → false. `tooling-tester` points to the audit file | revert |
| **6. Agents** | `plugin-readme-writer`: `skills: [docs-maintenance]`; move any rule of lines 57-275 that `plugin-readme.md` lacks into the procedure, then cut them. `plugin-tester`: run `npm run check:install -- --from local <plugin>`, drop the copied gotchas, preload `plugin-engineering:cli-commands-guide`. `docs-consistency-auditor`: run `check:consistency` first, audit only the semantic facts (DEBT-001). `tooling-tester`: point to the audit. Create `plugin-release-reviewer` (D8) and call it from `plugin-releases` step 1. Gate map: the agent-type rows | `npm run validate:claude` → exit 0. `npm run lint:skills -- .claude/skills/docs-maintenance` and `-- .claude/skills/plugin-releases` → exit 0. One run of each changed agent on one plugin, report shown raw. The gate lets `plugin-readme-writer` edit a README (test g, live) | revert |
| **7. Memory** | Apply D5. Delete `memory/research-claude-code-with-the-project-skills.md` (the routing row now holds it) and update `MEMORY.md` | Fresh cloud session: the memory path in the system prompt resolves inside the checkout, and `MEMORY.md` shows in `/memory` | revert; remove the setup-script line |
| **8. Optional, each on its own approval** | B5 Biome hook; B4 `issue-triage`; `validate.yml` (handoff item 2) | per item | per item |

## 6. Decisions for the owner

| # | Question | Recommendation and why |
| :-- | :-- | :-- |
| D1 | Approve this target architecture and start step 1? | **Yes.** Steps 1 and 2 change no structure and remove the duplicates and the competing session mandate at once |
| D2 | One `plugin-lifecycle` skill (router, new-plugin procedure and templates) or two skills (router + `new-plugin`)? | **One.** Fewer homes; the new-plugin procedure is one branch of the lifecycle, and its templates are only used there |
| D3 | Does a CHANGELOG-only change take a version bump? | **No.** It changes nothing users install; the rule in force and the small-fix event already say so. Fix `plugin-versioning` step 1 to match |
| D4 | Set `skill-diagnostics` `on_skill_write` from `gate` to `suggest` for this repository? | **Corrected 2026-11-13: no repository change; keep `gate`.** `pluginConfigs` is "Scope: User or managed", and "Claude Code ignores project and local entries" ([settings-reference: pluginConfigs](https://code.claude.com/docs/en/settings-reference#pluginconfigs)), so a repository cannot set it. If the reminders bother you, set `suggest` on your machine with `claude plugin configure skill-diagnostics@<marketplace>` (user scope, every project). The Stop reminder never blocks |
| D5 | How should repository memory work in cloud sessions, where `autoMemoryDirectory` (absolute or `~/` paths only) points outside the checkout? | **Keep the setting and add one line to the cloud setup script that links `~/Claude/repositories/the-claude-factory` to the checkout.** One mechanism in both places. It assumes your local checkout lives at that path, and that auto memory follows a directory link; both are unverified. Before step 7, settle a conflict: the installed build's settings schema says `autoMemoryDirectory` is "Ignored if set in projectSettings", while the memory docs say project settings honor it under workspace trust |
| D6 | Reword `CLAUDE.md:65` ("In CI, only the evals run") to "CI runs validation and the evals; plugin behavior is tested locally"? | **Yes.** It matches `release.yml` waiting on `Validate` and the planned `validate.yml` |
| D7 | Do you work on this repository from Claude Projects threads? | **Make maintainer changes in plain cloud sessions or the terminal; use Projects threads for coordination and research only** (recommended 2026-11-13). Project skills do not load in those threads, and project hooks run only in single-repository sessions ([skills: Choose where skills load](https://code.claude.com/docs/en/skills); [cloud-environments](https://code.claude.com/docs/en/cloud-environments)). The fix would be a private maintainer plugin, which this proposal does not recommend now |
| D8 | Build `plugin-release-reviewer` (Opus, read-only)? | **Yes.** It is the only gap between what scripts check and the plugin-scope rules on safety and portability, and every release is the last gate before users |

## 7. Risks and what could not be verified

**Risks:**
- The Skill tool's hook `tool_input` schema is not documented. The recorder reads `tool_input.skill` only after step 3 captures a real sample; the fallback, the transcript, is also an undocumented format.
- Whether a subagent's hook input carries the parent's `session_id` is not verified. Test (g) and the agent-type rows cover the project agents either way.
- After compaction the record persists while the skill text may not. Re-injection of invoked skills after compaction is not verified.
- The gate needs `jq` (`/usr/bin/jq` 1.7 here). On the owner's macOS it is not verified, and a missing `jq` blocks every edit by design (fail closed).
- Behavior of `permissions.ask` under bypass mode is not verified. The docs state that a hook `ask` forces a prompt even in auto mode.
- `@synced: false` is proven only for two plugins in this cloud session. On a local machine it applies only when signed in with the claude.ai account.
- The cloud launcher's Stop hook blocks on uncommitted changes. Each step therefore ends with local commits; pushes still wait for the owner.
- Step 5a rewrites an always-loaded file. The reviewer agent and the traceability table are the guard against a lost instruction.

**Not verified:**
- The owner's machine (`~/.claude`, local paths).
- ADR bodies beyond the six read: hook-scripts, release-workflow, npm-scripts, biome-markdown, cloud-dependencies, git-hooks.
- Plugin skills' bodies.
- The trigger behavior of any skill description.
- Whether the project-maintainer mod loads.
- Where `on_skill_write` persists.
- **Not documented:** `engines["claude-code"]`, and a project-relative `autoMemoryDirectory`.

**Release notes read:**
- Installed and project version: 2.1.323. It is also the latest: GitHub `v2.1.323`, 2026-11-12.
- Read: 2.1.318 (2026-11-04), 2.1.319 (2026-11-06), 2.1.321 (2026-11-09), 2.1.322 (2026-11-10) and 2.1.323 (2026-11-12). 2.1.320 was never released.
- None changes CLAUDE.md, imports, `.claude/rules` or `paths` loading.

**Changes that bear on this proposal:**
- **2.1.323:**
  - adds `engines["claude-code"]` and type-checks mod modules in `validate`;
  - deprecates a plugin's `agent` setting;
  - stops repository settings from disabling hooks in untrusted VS Code folders and self-hosted runners;
  - makes repository-only `enabledPlugins` report "not installed" instead of "not cached".
- **2.1.321:** nested `.claude/skills` inside `~/.claude/plugins` no longer load.
- **2.1.319:**
  - adds `permissions.denyInsteadOfPrompting`;
  - nested project skills load only from the start folder when the sandbox is on.

**Sources (read 2026-11-13):**
- [memory](https://code.claude.com/docs/en/memory)
- [hooks](https://code.claude.com/docs/en/hooks)
- [skills](https://code.claude.com/docs/en/skills)
- [sub-agents](https://code.claude.com/docs/en/sub-agents)
- [settings-reference](https://code.claude.com/docs/en/settings-reference)
- [settings](https://code.claude.com/docs/en/settings)
- [cloud-environments](https://code.claude.com/docs/en/cloud-environments)
- [plugins/loading](https://code.claude.com/docs/en/plugins/loading)
- [workflows](https://code.claude.com/docs/en/workflows)
- [changelog](https://code.claude.com/docs/en/changelog)

The Claude Code Docs MCP was up and agreed with the site pages.
