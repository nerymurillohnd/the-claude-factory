# Claude configuration inventory

Everything a Claude Code session in this repository reads or can call: instructions, rules, drafts, skills, agents, plugins, hooks, references, templates, records and settings. Each item has one line on what it is and does. This is an inventory, not a proposal: it records what exists, where it overlaps, and the defects found while mapping it.

- **Date:** 2026-11-13
- **Repository state:** branch `ccr-60dfcba3-fsbz16` at `a5e611a`, pushed; `main` at `fee7ff1`
- **Claude Code:** 2.1.323 (the latest release on 2026-11-13), in a claude.ai cloud session
- **Collected with:** the files themselves, `claude plugin list --json`, `claude plugin details <plugin>@synced`, and the instruction-engineering checker (`check_instructions.py --project . --no-user`)

## 1. What loads when

| When | What |
| :-- | :-- |
| Every session, at start | `.claude/CLAUDE.md` and, through its `@WORKFLOW.md` import, `.claude/WORKFLOW.md` (265 lines together); the owner's claude.ai user preferences; the name and description of every skill and agent available (about 9,800 tokens from the 20 loaded plugins alone, per `claude plugin details`); the output of every `SessionStart` hook |
| When a matching file is read or edited | Each rule under `.claude/rules/` whose `paths` match |
| When invoked | A skill's body and references; an agent's whole definition, in its own context |
| Never, by themselves | Everything under `.claude/architecture/`, `.claude/references/`, `.claude/templates/`, `.claude/maintainer/` and `.claude/session-handoff/`, until a file, skill or hook points Claude at them |

## 2. Instruction files

| File | Lines | What it holds |
| :-- | --: | :-- |
| `.claude/CLAUDE.md` | 89 | Project instructions in force: what the project is, the two scopes, tooling (Node, npm, uv, Python), models and effort for agents, repository memory, plugin-scope pointer, verification, pull requests, dates. Imports `WORKFLOW.md` |
| `.claude/WORKFLOW.md` | 175 | The commands of each of the 20 lifecycle stages (phases A to D): Claude Code commands and npm scripts, with the skill that writes each stage's documents. Loaded every session through the import |
| `.claude/settings.json` | 95 | Project settings: skill-listing budget, claude.ai skill and plugin sync on, four experimental env flags, permission allow list, denied MCP servers (claude.ai Gmail and Google Calendar), workflows on, `enabledPlugins` for 9 `@the-claude-factory` plugins plus `mcp-server-dev@claude-plugins-official`, `autoMemoryDirectory`, two extra marketplaces. Registers no hooks |
| `.claude/memory/MEMORY.md` | 4 | Repository memory index, created 2026-11-13; one entry |
| `.claude/memory/research-claude-code-with-the-project-skills.md` | — | Memory: load cc-docs-research and cli-commands-guide before Claude Code answers; say "not documented", not "not possible". Duplicates the owner's user preferences |

## 3. Rules in force (`.claude/rules/`)

| Rule | Loads with | What it sets |
| :-- | :-- | :-- |
| `architecture/claude-dir.md` | `.claude/**` | Where each kind of `.claude/` file goes: instructions in `CLAUDE.md`, stage commands in `WORKFLOW.md`, rules, agents by group, skills without scripts, templates, records, drafts in `architecture/` until approved |
| `architecture/docs.md` | `docs/**` | Where user guides and images go; `compatibility.md` as the single source of surface support |
| `architecture/github.md` | `.github/**` | Workflows, issue and PR templates, labels, Dependabot, zizmor exceptions; when to run `lint:github`, `lint:workflows`, `labels:sync` |
| `architecture/scripts.md` | `scripts/**` | Script folders by role (validators, checkers, generators, release, schemas, testers, typings); run lint, typecheck and tests after each change |
| `hook-scripts.md` | plugin hooks, `plugin.json`, `.claude/hooks/**`, `.claude/settings.json`, `.claude/agents/**` | Hook script language, shebang, mode 100755, Bash flags, Python on the standard library, exec versus shell form |
| `plugins.md` | `plugins/**`, `.claude-plugin/**`, root `README.md` and `CHANGELOG.md`, `.github/workflows/**` | Plugin scope: design, safety, license, names, versions, version bumps, category, surfaces, portability, pull requests inside `plugins/`, evals |
| `plugins/versioning.md` | `plugins/**`, `CHANGELOG.md` | Semver levels, UTC release dates; load `plugin-versioning` and `plugin-releases` |
| `plugins/categories.md` | `plugin.json`, plugin READMEs, `marketplace.json`, root `README.md` | One purpose-based category per plugin, the 13-category list (with `monitoring`, without `mods`); load `plugin-versioning` and `docs-maintenance` |
| `plugins/evals.md` | `plugins/*/evals/**`, `.github/workflows/**` | Evals only on owner-chosen plugins; cases on Sonnet 5.5, judge Opus 5.5, effort by tag; smoke locally, full suite in CI on changed plugins |
| `plugins/icons.md` | icon sources, renderer, `icon.png`, `listing.py` | Change icons only through the SVG source and `icons:render`; owner approval; load `plugin-icons` |
| `skill-lint.md` | `scripts/**/*.py`, `scripts/**/*.pyi` | How skill-lint is run, edited and tested, rule family by module |

## 4. Drafts (`.claude/architecture/`)

| File | Lines | What it is |
| :-- | --: | :-- |
| `CLAUDE.draft.md` | 151 | The replacement for `CLAUDE.md`: what it is, goal, platforms, roles, scopes, pull requests, testing (plugins and mods), stack, repository map, main commands, cloud sessions |
| `refactor.md` | 580 | The lifecycle map and maintainer blueprint: six blueprint rules (one source of truth first), the 20 stages with commands, gotchas and script status, target structure, native validator coverage (Appendix A), and where the blueprint lives once adopted (Appendix F) |
| `rules/npm-and-uv.md` | 31 | Draft rule for npm and uv, loaded with the manifests and `scripts/**`; replaces the Tooling section of `CLAUDE.md` |
| `rules/plugins.md` | 85 | Draft of `rules/plugins.md`; differs from the one in force by one line (keep every file and link a plugin uses inside its folder) |
| `rules/skill-references.md` | 15 | Draft rule on naming other skills from a skill (bare name for project skills, prefix for plugin skills, no paths into another skill) |

## 5. Project skills (`.claude/skills/`)

| Skill | What it does |
| :-- | :-- |
| `docs-maintenance` | Writes, updates and audits every repository document from its template and procedure: plugin README, CHANGELOG, LICENSE, NOTICE; root README, CHANGELOG and policy files. Holds 11 templates and 21 procedures, and seven events (new plugin, audit, small fix and others) |
| `plugin-versioning` | Chooses a plugin's semver level, sets the version, writes the changelog notes, runs the checks |
| `plugin-releases` | Releases a version: checks before the merge, changelog date, tag and GitHub Release, checks after |
| `plugin-catalog-changes` | Renames, removes, deprecates or merges plugins through the marketplace's `renames` map |
| `plugin-icons` | Designs, renders, reviews and checks plugin directory icons on the shared frame |

## 6. Project agents (`.claude/agents/`)

| Agent | Model, effort | What it does |
| :-- | :-- | :-- |
| `auditors/docs-consistency-auditor` | Sonnet 5.5, high | Read-only check that READMEs, CHANGELOGs, manifests and the catalog state the same facts after a change |
| `docs-maintainers/plugin-readme-writer` | Sonnet 5.5, high | Writes a plugin README in full for the first time, for the `docs-maintenance` skill |
| `testers/plugin-tester` | Sonnet 5.5, medium | Tests plugins as users receive them: loads, installs in an isolated config, runs mod tests |
| `testers/tooling-tester` | Sonnet 5.5, medium | Runs the maintainer test suite and checks, and re-tests validator gaps after a CLI upgrade |

## 7. References and templates

| File | What it is |
| :-- | :-- |
| `.claude/references/README.md` | Index: one fill procedure per template; points document templates to `docs-maintenance` and records, handoffs and GitHub files to their plugins |
| `.claude/references/agent.md` + `templates/agent-template.md` | How to create a plugin subagent |
| `.claude/references/skill.md` + `templates/skill-template.md` | How to create a plugin skill's `SKILL.md` |
| `.claude/references/plugin-manifest.md` + `templates/plugin-template.md` | How to create a plugin's `plugin.json` |
| `.claude/references/evals-ci.md` + `templates/evals-ci-template.md` | How to create `.github/workflows/evals.yml` |

## 8. Records and session state

| Location | Contents |
| :-- | :-- |
| `.claude/maintainer/decisions/` | 30 ADRs, written with `project-maintainer:write-records` |
| `.claude/maintainer/technical-debt/` | `pending-debt.md` and `closed-debt.md` (DEBT-001 and DEBT-003 open) |
| `.claude/maintainer/plans/` | 3 implementation plans (skill-lint, its review fixes, release and consistency scripts) |
| `.claude/maintainer/specs/` | 3 specs (github-operations, issue-triage task prompt, skill-lint) |
| `.claude/maintainer/audits/` | This file and the 2026-11-10 github-files-setup audit |
| `.claude/session-handoff/` | 3 handoffs; the latest is read at session start by the project-maintainer hook |

## 9. Maintainer scripts and npm entry points

`package.json` holds the single entry point (28 npm scripts). Scripts on disk: `scripts/validators/` (skill-lint, plugin-consistency PC-01 to PC-10, gating-hooks-catch), `scripts/release/` (release-status, release-changelog, release-notes, check-install), `scripts/generators/` (plugin-icons renderer and 22 SVG sources), `scripts/testers/` (unittest suites), `scripts/typings/` (ruamel stubs), root `sync-labels.py` and `check-github-files.py`. `checkers/` and `schemas/` are empty.

## 10. Plugins loaded in this session

All arrive through claude.ai sync (`@synced`), not through the project's `enabledPlugins`. Always-on is the per-session cost `claude plugin details` reports.

| Plugin | Source | Components | Always-on | What it adds |
| :-- | :-- | :-- | --: | :-- |
| `plugin-engineering` 0.2.3 | This marketplace | 2 skills | ~536 | `public-marketplace-dev` (official docs for public marketplace plugins, mods included) and `cli-commands-guide` (every plugin command) |
| `instruction-engineering` 0.1.3 | This marketplace | 1 skill, 1 agent | ~836 | Writing, auditing and placing CLAUDE.md and rules; checker script; independent reviewer |
| `hook-engineering` 0.2.5 | This marketplace | 1 skill, 1 agent | ~208 | Designing, auditing and debugging hooks |
| `skill-diagnostics` 0.4.0 | This marketplace | 1 skill, 6 agents, 5 hooks | ~909 | Multi-agent skill audit; hooks gate every skill write until an audit is recorded |
| `project-maintainer` 0.2.6 | This marketplace | 2 skills, 1 hook, a mod | ~176 | ADRs, technical debt, session handoffs; SessionStart hook injects the handoff protocol; its mod notes commits that may need a record |
| `github-operations` 0.8.0 | This marketplace | 6 skills | ~1,171 | PR lifecycle, GitHub Actions audits, repository files, cleanup |
| `prompt-writer` 0.2.5 | This marketplace | 1 skill | ~165 | Prompt engineering |
| `bash-lsp-intelligence` 0.2.8 | This marketplace | 1 skill, 2 hooks, LSP | ~154 | Shell intelligence; post-edit shfmt and ShellCheck |
| `python-lsp-intelligence` 0.3.3 | This marketplace | 1 skill, 2 hooks, LSP | ~146 | Python intelligence; post-edit ruff and basedpyright |
| `typescript6-lsp-intelligence` 0.3.5 | This marketplace | 1 skill, 2 hooks, LSP | ~216 | TypeScript intelligence; post-edit tsc |
| `svelte-development` 0.1.3 | This marketplace | 3 skills, 2 agents, MCP, LSP | ~821 | Svelte and SvelteKit |
| `tailwind-development` 0.3.3 | This marketplace | 2 skills, 4 agents, 1 hook, MCP | ~560 | Tailwind CSS v4; its MCP server fails to connect ("Connection closed") |
| `superpowers` 7.0.2 | Other | 15 skills, 1 hook | ~848 | General process skills (brainstorming, plans, TDD, debugging, reviews); SessionStart hook injects a rule to invoke a skill before any response |
| `feature-dev` 1.0.1 | Other | 1 skill, 3 agents | ~240 | Guided feature development: explorer, architect, reviewer agents |
| `claude-code-setup` 1.0.0 | Other | 1 skill | ~141 | Recommends hooks, agents, skills, plugins and MCP servers for a codebase |
| `skill-creator` | Other | 1 skill | ~114 | Creates and evaluates skills, optimizes descriptions |
| `cloudflare` 1.0.4 | Other | 22 skills, MCP | ~2,078 | Cloudflare products; MCP needs OAuth in cloud sessions |
| `cowork-plugin-management` 0.2.2 | Other | 2 skills | ~259 | Creating and customizing Cowork plugins |
| `pdf-viewer` 0.2.0 | Other | 5 skills, MCP | ~228 | PDF viewing and annotation |
| `playwright` | Other | MCP | ~0 | Browser automation |

Also available without a plugin: the owner's claude.ai skills (`anthropic-skills:*`, among them `cc-docs-research`, `docs`, `deep-research`), Claude Code's built-in skills (`code-review`, `simplify`, `init`, `security-review`, artifact skills and others) and built-in agents (`Explore`, `Plan`, `general-purpose`, `claude-code-guide`, `statusline-setup`, `web-fetch`).

### Plugins of this marketplace that this session does not have

| Plugin | Why |
| :-- | :-- |
| `plugin-evals` | Enabled in `settings.json` as `@the-claude-factory`, but that marketplace install is not in this cloud session, and the claude.ai sync does not carry it |
| `plugin-test-bench` | Not enabled in `settings.json` and not synced |
| `mods-engineering` | Not enabled in `settings.json` and not synced |
| The other 7 `@the-claude-factory` entries of `enabledPlugins` | Not installed here; their `@synced` copies load instead, at the versions on the claude.ai account (`plugin-engineering` 0.2.3, while the branch has 0.2.4) |

## 11. Hooks that act on this session

| Hook | From | Effect |
| :-- | :-- | :-- |
| SessionStart | `project-maintainer` | Injects the session start protocol: read the latest handoff, list pending items, flag records newer than it |
| SessionStart | `superpowers` | Injects "using-superpowers": invoke a skill before any response, including clarifying questions |
| SessionStart, PostToolUse, Stop, SubagentStop, PermissionRequest | `skill-diagnostics` | After a skill file changes, the Stop hook keeps asking for an audit until one is recorded (`on_skill_write` defaults to `gate`) |
| PostToolUse, PostToolUseFailure | `python-lsp-intelligence`, `bash-lsp-intelligence`, `typescript6-lsp-intelligence` | Lint, format and type-check each edited file; block the turn on findings |
| PostToolUse | `tailwind-development` | Checks edited Tailwind files |
| Mod hook on commits | `project-maintainer` (its hooks module) | After a commit with "revert" or a dependency manifest, asks whether it needs a record |

`.claude/settings.json` registers no project hook; `.claude/hooks/` does not exist.

## 12. Overlaps and competition

| Subject | Who covers it |
| :-- | :-- |
| Lifecycle stage commands | `WORKFLOW.md` (in force, owner per `claude-dir.md`), `refactor.md` Part 1 (draft), `CLAUDE.draft.md` Main commands, the commands inside each project skill, `cli-commands-guide` |
| Releasing, renaming and versioning plugins | Project skills `plugin-versioning`, `plugin-releases`, `plugin-catalog-changes`; `plugin-engineering:public-marketplace-dev` (host-marketplace, publish) |
| Testing plugins | Agent `plugin-tester`; plugin `plugin-test-bench` (not loaded); `CLAUDE.draft.md` Testing; `CLAUDE.md` line 65; `WORKFLOW.md` stage 9; `public-marketplace-dev` (create, build, mod-test, mod-troubleshoot) |
| Evals | `rules/plugins/evals.md`, `rules/plugins.md` Evals, `WORKFLOW.md` stage 10, references and template `evals-ci`, plugin `plugin-evals` (not loaded), `public-marketplace-dev` (plugin-evals) |
| Creating skills | `references/skill.md` + template, `skill-creator`, `superpowers:writing-skills`, `public-marketplace-dev` (skills, platform best practices) |
| Auditing skills | `skill-diagnostics` (gate), `npm run lint:skills` (skill-lint) |
| Documentation consistency | `npm run check:consistency`, agent `docs-consistency-auditor`, `docs-maintenance` audit event |
| Planning and process | `superpowers` (brainstorming, writing-plans, executing-plans, subagent-driven development), `feature-dev`, built-in `Plan` agent, the owner's task-flow preferences |
| Instruction files | `instruction-engineering`, `claude-dir.md`, `CLAUDE.md` |
| Version bump levels | `rules/plugins.md` Version bumps, `rules/plugins/versioning.md`, `plugin-versioning` skill |
| Category | `rules/plugins.md` Category, `rules/plugins/categories.md` |
| Release dates | `CLAUDE.md` Dates, `rules/plugins/versioning.md`, `plugin-releases`, `docs-maintenance/references/governance.md` |

## 13. Defects found while mapping

1. **Duplicated rules that load together.** The checker reports near-duplicates between `.claude/CLAUDE.md:89` and `rules/plugins/versioning.md:22` (dates) and between `rules/plugins.md:61` and `rules/plugins/categories.md:18` (category); `rules/plugins.md` also repeats Version bumps and Evals.
2. **A draft that contradicts a rule in force.** `refactor.md` Appendix F sends stage procedures to `.claude/maintainer/blueprint.md`; `claude-dir.md` keeps stage commands in `WORKFLOW.md`.
3. **The draft's Main commands copy `WORKFLOW.md`** and the npm scripts in `package.json`.
4. **`autoMemoryDirectory` points outside the checkout** (`~/Claude/repositories/the-claude-factory/.claude/memory`), while `CLAUDE.md` keeps repository memory in `.claude/memory/`; in a cloud session the configured folder is empty.
5. **Project `enabledPlugins` never reach cloud sessions:** the `@the-claude-factory` installs are absent; only claude.ai-synced copies load, at the account's versions.
6. **A glob that never matches:** `hook-scripts.md` lists `.claude/hooks/**`, which does not exist.
7. **Two always-on instruction sources pull in different directions:** the `superpowers` SessionStart hook mandates a skill before every response and brainstorming before any creative work, beside the project's own task flow and skills.
8. **The `skill-diagnostics` gate fires after every skill edit,** while the owner has declined those audits; nothing records that choice in its configuration.
9. **The memory file duplicates the owner's user preferences** (CURRENT SOURCES), which already load every session.
10. **`refactor.md` is stale in places:** its header and Part 2 describe the `claude/repo-refactor-redesign-feqwzk` branch and plans built before 2026-11-13.

## 14. Not covered here

- The owner's own machine: its `~/.claude/` settings, user rules and locally installed plugins differ from this cloud session's.
- The content of each plugin's skills beyond their names and costs.
- Whether each skill's description triggers when it should; no trigger evals were run.
