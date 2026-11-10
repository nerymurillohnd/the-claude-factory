# Claude Code Plugin Marketplace — Lifecycle Map and Maintainer Blueprint

> Status: draft for review, 2026-11-09.  
> Repository: `nerymurillohnd/the-claude-factory` at `9caaea8` (inventory and audit of 2026-11-09).  
> Terminology and commands: Claude Code official docs (code.claude.com), checked 2026-11-09.  
> Command reference: https://code.claude.com/docs/en/plugins/cli-reference  
> CLI behavior verified on Claude Code 2.1.322 (`claude plugin --help` and tests E1–E14).  
> Structure: Phase → Stage → What the stage includes → Commands → Gotchas → Scripts.  
> Gotcha sources: [docs] official reference · [skill] cli-commands-guide (checked on 2.1.321) · [E#] local test on 2.1.322 · [NV-#] native-validation-coverage audit.  
> Conventions: `claude plugin …` runs from a shell (alias `claude plugins`); `/plugin …` runs inside an interactive session (aliases `/plugins`, `/marketplace`).  
> Exit codes: `0` success, `1` failure; `validate` adds `2` for an unexpected error.

## Blueprint rules

1. **One source of truth.** Every maintainer script exists once, under `scripts/<subfolder>/`. Skills, Claude Code hooks, Git hooks, gates and CI only call it; none holds its own copy.
2. **The command governs; the script adds.** A script covers only what no plugin command does or finishes. Where a command covers a check, the script does not repeat it.
3. **Entry points stay where their tool looks for them**, as thin callers of `scripts/`: `.github/workflows/*.yml`, `.husky/pre-commit` and `pre-push`, hook registrations in `.claude/settings.json` (commands point to `${CLAUDE_PROJECT_DIR}/scripts/...`).
4. **Maintainer files inside plugins stay inside plugins**, because the CLI finds them only there: mod tests (`plugins/<p>/tests/*.test.ts(x)`) and eval suites (`plugins/<p>/evals/**`).
5. **Plugin runtime files stay inside their plugin** (hook handlers, skill scripts, MCP/LSP servers): they ship with the install and cannot depend on `scripts/`.
6. **No scripts under `.claude/skills/` or `.claude/hooks/`.** Project skills describe procedures and call `scripts/`.

**Script status:** **Keep** stays where it is · **Move** relocates (from → to) · **New** to be built · **Retire** to be removed (Appendix B).  
**Callers:** `gate` = `scripts/gates.mjs` (local pre-push and/or CI group) · `CI` = a workflow · `commit` = commit-time hook · `CC hook` = Claude Code hook registration · `skill` = a project skill · `manual` = run by hand.

---

# Part 1 — Lifecycle map

## Phase A — Marketplace Setup (one time)

### 1. Planning & Design
- Scope and audience: plugins built for third parties and their machines
- Naming convention for marketplace and plugins (kebab-case, no names reserved by Anthropic)
- Versioning policy: explicit bumps vs. omitting `version` so users track commits (rules: stages 12–14)
- Catalog policy: never rename (use `displayName`), `renames`, `forceRemoveDeletedPlugins`
- Cross-surface compatibility: Claude Code, claude.ai, Cowork (a top-level `bin/` blocks install on claude.ai and Cowork). `docs/compatibility.md` is the only source of the component × surface matrix; every plugin README's Compatibility cells copy it. In user docs and READMEs the two surfaces are named **Claude Code** and **Claude**
- Validation strategy: native CLI checks plus scripts for what the CLI doesn't catch (Appendix A)
- Maintainer installs only as a third party: add the marketplace, install each plugin; nothing is scaffolded or installed into the maintainer's global config

**Commands**
- `claude --version` — confirm the installed version before relying on version-gated flags
- `claude plugin --help` / `claude plugin <subcommand> --help` — list the subcommands and full options your version has

**Gotchas**
- The docs' flag tables list common options, not every option; `--help` on the installed binary is authoritative [docs]
- `/plugin help` printed nothing on 2.1.319 and 2.1.321; use `claude plugin --help` [skill]

**Scripts**
- None. Planning has no executable step.

### 2. Marketplace Scaffolding
- Repository and folder structure (one directory per plugin)
- `.claude-plugin/marketplace.json`: `name`, `owner`, `plugins` (required), `description`, `$schema`
- Optional fields: `metadata.pluginRoot`, `renames`, `forceRemoveDeletedPlugins`, `allowCrossMarketplaceDependenciesOn`
- Root README, LICENSE, SECURITY

**Commands**
- No scaffold command for a marketplace: `marketplace.json` is written by hand
- `claude plugin validate .` — run from the marketplace root once the file exists (see stage 8)

**Gotchas**
- `validate` accepts a top-level `version`, a `metadata.version`, `owner.email: "bad"`, and a `renames` key that is still a listed plugin; only a name with spaces failed [E9]

**Scripts**
- `scripts/check-repo.mjs` — **Keep** · Callers: gate, CI · Gap: fixed marketplace name and description, no top-level `version` (native passes both, E9). **Absorbs** the `metadata.version` rule from `check-marketplace-unversioned.py`, which nothing runs today (E13)
- `scripts/validators/marketplace-json-schema.py` — **Keep** · Callers: gate, CI, commit · Gap: duplicate keys (NV-B6). **Extend:** `owner.email` format (caught by nothing, E13)

### 3. Repository Governance
- **Branch protection**
  - Rulesets and protected branches
  - Required status checks before merge
- **GitHub Actions (CI)**
  - Validation workflow: run `claude plugin validate` on every PR and push
  - Linting: JSON/YAML, Markdown, shell scripts, and code in hooks/MCP servers
  - Consistency checks: `plugin.json` vs. marketplace entry version, CHANGELOG entry present
  - Scripts for native coverage gaps (Appendix A), including duplicate JSON keys
  - Security: secret scanning, dependency review, Dependabot for Actions and dependencies
  - Workflow hardening: least-privilege `permissions`, pinned action versions
- **Community templates**
  - Issue forms (`.github/ISSUE_TEMPLATE/`): bug report, feature request, plugin request, `config.yml`
  - Pull request template (`.github/PULL_REQUEST_TEMPLATE.md`) with a validation checklist
  - CODEOWNERS
  - CONTRIBUTING, CODE_OF_CONDUCT, SECURITY policy
  - Labels (source `.github/labels.json`; synced by `scripts/sync-labels.mjs`, see Scripts):
    - `type:` bug, enhancement, plugin-idea, documentation, question, security, dependencies
    - `status:` triage, needs-info, confirmed, in-progress, released, duplicate, wontfix, upstream
    - `priority:` high, medium, low
    - `area:` marketplace, ci
    - `plugin: <name>`: one per catalog entry, generated from `marketplace.json`
    - Apply only labels that already exist in the repository
- **Maintainer environment**
  - Session context for the maintainer (branch, sync state, tool versions)
  - Project records, written with the `project-maintainer` plugin:
    - Decisions: ADRs in `.claude/maintainer/decisions/` (`ADR_<YYYY-MM-DD>_<slug>.md`)
    - Technical debt: `.claude/maintainer/technical-debt/` (`pending-debt.md`, `closed-debt.md`, IDs `DEBT-NNN`)
    - Session handoffs: `.claude/session-handoff/` (`YYYY-MM-DD-HHMM.md`), read at the next session start
  - Commit-time and push-time gates

**Commands (used inside CI jobs)**
- `claude plugin validate <path> --strict --json` — warnings fail the run; machine-readable report
- `claude plugin validate <plugin-dir> --strict --profile directory` — adds portability checks (see stage 8)
- `claude plugin test [directory]` — tests for mods; no session, sign-in, or network needed
- `claude plugin tag <plugin-dir> --dry-run` — version-agreement check without creating a tag (see stage 14)
- `claude plugin eval [target]` — eval suite (see stage 10)

**Gotchas**
- Scripts must read the exit code or `--json`, not the symbols: without a TTY, ✔ ⚠ ✘ become √ ‼ × [skill]
- `test` needs no sign-in, so it fits CI; `eval` calls the model with real credentials and bills usage [docs]
- `details` token projections can change with sign-in state: an unsigned `claude` produced different counts, so do not gate on them in unauthenticated CI or commit hooks [E14]

**Scripts**
- `scripts/gates.mjs` — **Keep** · Callers: `.husky/pre-push`, CI, commit · The one runner of every gate (local and CI). **New gates** (View 2 of the audit):
  - `claude-validate-profile:<p>`: `validate --strict --profile directory` per plugin (22 of 22 pass today, E2)
  - `claude-validate:project`: `validate .claude --strict` for the repository's own skills, agents and commands (E1)
  - `mod-hooks-catch:<p>`: parse `validate --json` → fail on `gatingHooks[].hasCatch: false` (fails today on `project-maintainer` and `turn-meter`, E2; decision pending)
  - `mod-test:<p>`: move from group `local` to CI (the command needs no sign-in)
  - Fold in the missing-summary guard from `check-mod.sh` until anthropics/claude-code#103055 is confirmed closed (E11)
- `scripts/basedpyright-maintainer.mjs` — **Keep** · Callers: gate, CI · Type-checks maintainer Python per interpreter group. No command equivalent
- `scripts/lib.mjs`, `scripts/components.mjs` — **Keep** · Libraries used by gates, generators and checks. `components.mjs` counts mods' hook modules, which `details` shows as `Hooks (0)`
- `scripts/sync-labels.mjs` — **Keep** · Caller: manual · GitHub labels from `.github/labels.json`. No plugin command touches GitHub
- `scripts/validators/skill-references.py` — **Keep** · Callers: gate, CI, commit · Every path and skill name cited in `.claude/skills/**` and `.claude/CLAUDE.md` exists. Required after every move in this blueprint
- `scripts/session/checkout.sh` — **Move** from `.claude/hooks/checkout.sh` · Caller: CC hook (SessionStart) · Branch, ahead/behind, tool versions. No command reports git state. *Subfolder `session/` is new: decision pending*
- `.claude/hooks/validators-gate.sh` — **Retire** · Its CC hook registration on `git commit` calls `scripts/gates.mjs --only <validator gates>` directly, excluding `skill-size` until E14 is fixed
- `.husky/pre-commit` — **Keep** (entry point) · Biome on staged files, then `npm test`
- `.husky/pre-push` — **Keep** (entry point) · `npm run gates`
- `.github/workflows/validate.yml` — **Keep** (entry point) · Add the new gates above to its groups
- `.github/workflows/claude.yml`, `claude-code-review.yml` — **Keep** (entry points) · Not plugin commands; the review workflow is a recorded no-op with its fix deferred
- `scripts/testers/run_unittest.py`, `gates.test.mjs`, `scripts.test.mjs`, `reserved-name.test.mjs`, `schemas/test_schemas.py`, `checkers/*`, `validators/*` — **Keep** · Callers: `npm test`, gate `unittest-maintainer`, `node-tests` · Test the maintainer tooling itself

---

## Phase B — Plugin Development (per plugin)

### 4. Plugin Scaffolding
- Plugin directory with `.claude-plugin/plugin.json` (only the manifest goes inside `.claude-plugin/`)
- Metadata: `name`, `description`, `version`, author, keywords, `userConfig`
- Create only the component directories the plugin uses

**Commands**
- None for this repository. `claude plugin init` does not apply: it writes only to `~/.claude/skills/<name>/` (no target-folder option) and the result loads in every maintainer session as `<name>@skills-dir` [docs, E4]

**Gotchas**
- `init` produces a skills-directory layout (root `SKILL.md`, `skills: ["./"]`) with no README, CHANGELOG, LICENSE, icon or category [E4]; `scaffold-plugin.py` replaces it here

**Scripts**
- `scripts/checkers/check-plugin-name.py` — **Move** from `.claude/skills/building-plugins/scripts/` · Callers: skill, manual · Gap: refuses a retired name (a `renames` key) and a similar name (≤ 2 edits, reordered words, word subsets). Native fails only reserved and duplicate names
- `scripts/generators/scaffold-plugin.py` — **Move** from `.claude/skills/building-plugins/scripts/` · Callers: skill, manual · Gap: creates `plugins/<name>/` (impossible with `init`, E4) with `plugin.json`, `CHANGELOG.md` at 0.1.0, `LICENSE`, `README.md` from the template, category checked against `categories.json` and `renames`
- `scripts/validators/plugin-required-files.py` — **Keep** · Callers: gate, CI, commit · Gap: `CHANGELOG.md`, a `LICENSE` *file* (native accepts the `license` field), regular files with no broken or escaping symlinks. README and license presence are also covered by `--profile directory`

### 5. Component Authoring
- Skills: `skills/<name>/SKILL.md` (preferred over the older `commands/`)
- Agents: `agents/*.md`
- Hooks: `hooks/hooks.json` plus the scripts it calls
- MCP / LSP servers: `.mcp.json`, `.lsp.json`
- Other components: monitors, workflows, output styles, themes, `bin/`, `settings.json`
- Portable paths: `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`
- No root `CLAUDE.md` (not loaded; the validator warns); context-loading instructions go in a skill
- Plugin icon: `./.claude-plugin/icon.png` from an SVG source

**Commands**
- `claude --plugin-dir <path>` — load the plugin being edited for one session
- `/reload-plugins` — apply on-disk edits without restarting
- `/reload-plugins --force` — apply a reload that adds/removes a plugin MCP server or the `LSP` tool
- `claude --plugin-dir <path> plugin details <name>` — component inventory and projected token cost

**Gotchas**
- A reload that changes plugin MCP servers or the `LSP` tool is not applied without `--force`, because it invalidates the prompt cache [docs]
- In sessions without an interactive terminal, `/reload-plugins` doesn't connect or disconnect plugin MCP servers; that waits for the next session [docs]
- Skill frontmatter is not checked as strict YAML: `description: Use this: when …` passes `validate` [E1]
- `.lsp.json` is not validated: an unknown key or a missing `command` loads silently and `details` still lists the server [E6]
- Mod hooks modules (JavaScript) are outside `validate`; check gating handlers for error handling (`.catch`) yourself [E2]

**Scripts**
- `scripts/validators/skill-frontmatter.py` — **Move** from `.claude/hooks/skill-frontmatter.py` · Callers: CC hook (PreToolUse/PostToolUse on `SKILL.md`), gate, CI · Gap: strict YAML 1.2 frontmatter (native accepts `description: Use this: when …` and `description: [unclosed`, E1, NV-A2); blocks the write before the file is saved, which no command can do
- `scripts/validators/skill-names-consistency.py` — **Keep** · Callers: gate, CI, commit · Gap: flat, unquoted `name` equal to its folder for every `SKILL.md`, plugins and `.claude/skills` (native checks nothing here, NV-B5a)
- `scripts/validators/skill-argument-placeholders.py` — **Keep** · Callers: gate, CI, commit · Gap: no bare `$N` in a skill or command body that Claude Code would replace (NV-B5b)
- `scripts/validators/skill-size.py` — **Keep** · Callers: gate (local only) · Gap: fails at 500 lines or 5,000 body tokens against `skill-size-baseline.json`; `details` only reports. **Fix required:** its result depends on `claude` being signed in (E14); stays out of CI and the commit hook until fixed
- `scripts/validators/mcp-json-schema.py` — **Keep** · Callers: gate, CI, commit · Gap: unknown keys (lost silently at load) and duplicate keys (NV-B1, NV-B6)
- `scripts/validators/lsp-json-schema.py` — **Keep** · Callers: gate, CI, commit · Gap: every file-based `.lsp.json` (unknown keys, missing `command`, duplicate keys); native validates only inline `lspServers` (NV-B2, E6)
- `scripts/validators/hooks-json-schema.py` — **New** · Callers: gate, CI, commit · Gap: unknown keys in a handler or at top level (native passes, E7; today only `test_schemas.py` catches them, as a test) and duplicate keys (caught by nothing, E12). Reads `scripts/schemas/`
- `scripts/generators/plugin-icons.mjs` — **Keep** · Caller: manual · Renders `scripts/generators/plugin-icons/<plugin>.svg` to `icon.png`. No command equivalent
- `scripts/validators/plugin-icons.py` — **Keep** · Callers: gate, CI, commit · Gap: square PNG, 512–2048 px, under 2 MB, fixed path, SVG source present. Native only warns on a missing icon or icon path (E3, NV-B5e)
- `scripts/checkers/fetch-github-mod.sh` — **Move** from `.claude/skills/testing-mods/scripts/` · Caller: manual · Gap: prints the source tree of another marketplace's plugin for comparison without installing it (the CLI path writes settings and cache, E10)

### 6. Dependencies & Relevance
- Plugin and cross-marketplace dependencies
- `relevance` block so Claude Code suggests the plugin when a session matches

**Commands**
- `/reload-plugins` — installs missing dependencies and reports `(+ N dependencies: <names>) resolved`
- `claude plugin prune [--scope]` (alias `autoremove`) — remove auto-installed dependencies no plugin needs
- `claude plugin validate <marketplace-dir>` — checks the `relevance` block

**Gotchas**
- `prune` never removes a plugin the user installed directly, only auto-installed dependencies [docs]

**Scripts**
- None. The commands cover this stage.

### 7. Marketplace Registration
- Entry in `plugins[]`: `name`, `source`, `description`
- `version` in one place only: `plugins/<plugin>/.claude-plugin/plugin.json`; the entry and `marketplace.json` carry none

**Commands**
- No registration command: the entry is edited in `marketplace.json`
- `claude plugin validate .` — flags duplicate names, `..` paths, and version mismatches

**Gotchas**
- An entry named `alpha` whose `source` points to `./plugins/beta` passes; check name/source agreement yourself [E9]
- An entry without `description`, or with an empty one, passes; so does an unknown entry `category` [E9]

**Scripts**
- `scripts/generators/marketplace.mjs` — **Keep** · Callers: manual (`npm run generate`), gate and CI (`--check`) · Gap: builds `plugins[]` (name, source, description, category) from each `plugin.json`, so entries never drift; `--check` fails a missing or empty `description` and an unknown `metadata.category` (E13)
- `scripts/validators/plugin-names-consistency.py` — **Keep** · Callers: gate, CI, commit · Gap: name agrees across entry (name, source, `renames`), folder, `plugin.json` (`name`, `homepage`) and README (badge, install/update/uninstall commands) (NV-B4, NV-B5c, E9)

### 8. Validation
- `claude plugin validate` after every edit (locally and in CI)
- Fix errors and warnings: names, paths, mismatched versions, unknown fields

**Commands**
- `claude plugin validate <path>` — a directory validates `marketplace.json` if present, otherwise `plugin.json`
- `claude plugin validate <path> --strict` — warnings become errors
- `claude plugin validate <path> --json` — one JSON report, same exit codes
- `claude plugin validate <plugin-dir> --profile directory` — portability profile
- `/plugin validate <path>` — same report inline in a session

**Gotchas**
- A marketplace run doesn't open each plugin's components; validate each plugin directory too [skill]
- `validate` doesn't follow symlinks in the directory you name [skill]
- `--profile directory` caught `.DS_Store` and a missing `icon` path (warnings), but passed Windows-hostile names (`nul.txt`, `a:b.md`), case-colliding names (`Notes.md`/`notes.md`), a symlink, large files and file counts [E3]
- For mods, `--profile directory` returns `incomplete: true`: none of its checks apply to the hooks module [E2]
- In `hooks.json`, a wrong `type`, a missing `command`, an unquoted `${CLAUDE_PLUGIN_ROOT}` and a misspelled top-level `hooks` fail; an unknown key inside a handler (`timeot`) or at top level passes [E7]
- Duplicate JSON keys (e.g. `PostToolUse` twice) pass: the later value silently wins [E12]
- In `plugin.json`, non-SemVer `version: "1.0"`, invalid emails, non-SPDX `license`, duplicate `keywords`, unknown `metadata.category` and empty `displayName` all pass [E8]
- Full coverage table: Appendix A

**Scripts**
- `scripts/validators/plugin-json-schema.py` — **Keep** · Callers: gate, CI, commit · Gap: duplicate keys (NV-B6), non-SemVer `version` (E13). **Extend:** `author.email` format and unique `keywords` (caught by nothing, E13)
- `scripts/check-repo.mjs` — **Keep** · Callers: gate, CI · Gap: Windows-invalid names, trailing dot or space, case collisions, symlinks, files over 256 KiB, more than 512 files (E3); maintainer files that would ship (`tsconfig.json`, extra `.claude-plugin/*`, eval results); `plugin.json` required fields, `license` = MIT, `repository` (E8)
- Commit-time `claude plugin validate --strict` on changed plugins — **New** (gate selector in the commit hook) · Catches manifest and component errors one step before pre-push

### 9. Local Testing
- Develop against the directory with `--plugin-dir`, not an installed copy
- Real install from the local marketplace
- Test in Claude Code, the desktop app, and VS Code
- Deterministic tests of plugin hook scripts, skill scripts and MCP servers

**Commands**
- `claude --plugin-dir <path>` / `claude --plugin-url <url>` — session-only load (repeatable; `.zip` supported)
- `claude --plugin-dir <path> plugin list` — shows the plugin as `<name>@inline`
- `claude plugin marketplace add <local-path>` — add the local marketplace
- `claude plugin install <plugin>@<marketplace> --scope user|project|local` (alias `i`)
- `claude plugin install <plugin> --marketplace <source>` — add the marketplace and install in one step
- `claude plugin install <plugin>@<marketplace> --config <key=value>` — set `userConfig` at install
- `claude plugin configure <plugin>@<marketplace>` — show or set `userConfig`
- `claude plugin enable|disable <plugin> [--scope]`
- `claude plugin list [--json]`
- `/plugin` (Discover tab), `/plugin manage` (Installed tab), `/reload-plugins`
- `claude plugin test [directory]` — mods only

**Gotchas**
- `--plugin-dir` and `--plugin-url` go before the subcommand: `claude --plugin-dir <p> plugin details <name>` [skill]
- `--plugin-dir` at a marketplace root loads nothing and shows no error; point it at the plugin directory [skill]
- A `--plugin-dir` plugin silently replaces a same-named installed plugin for that session, while `list` still shows the installed row as enabled [skill]
- `/plugin install <path|url|owner/repo>` installs nothing and reports `Marketplace not found`; add the marketplace first or use `--marketplace` [docs]
- `/plugin install <plugin>` only opens the details pane; nothing installs until a scope is chosen [skill]
- `configure` accepts only `name@marketplace`, never a bare name [docs]
- `enable` on an enabled plugin, or `disable` on a disabled one, exits `1`; with `--json`, `alreadyInGoalState: true` [skill]
- `/plugin` doesn't run in `claude -p`; use `claude plugin` from the shell [docs]
- `-y` and `--accept-command` have no effect inside a session (Bash tool, hook); run those from your own terminal [skill]
- `claude plugin test` runs only mods' `*.test.ts(x)`; no command fires a command hook without a session (NV-A8)

**Scripts**
- `plugins/<p>/tests/*.test.ts(x)` — **Keep in plugin** (rule 4) · Callers: gate `mod-test:<p>` (move to CI, see stage 3) · Fully covered by `claude plugin test`
- `scripts/testers/<plugin>/by_path.sh` (block-no-verify, hook-engineering, project-maintainer, python-lsp-intelligence, skill-diagnostics) — **Keep** · Callers: gate `by-path:<plugin>`, CI · Gap: runs a command hook by path as Claude Code would, with a payload on stdin
- `scripts/testers/<plugin>/*.test.mjs` and `test_*.py` (bash-lsp-intelligence, github-operations, hook-engineering, instruction-engineering, python-lsp-intelligence, skill-diagnostics, tailwind-development, typescript6-lsp-intelligence) — **Keep** · Callers: `npm test`, gates · Gap: deterministic tests of plugin hook scripts, skill scripts, an MCP server and agent frontmatter
- `scripts/testers/tailwind-development/fixtures/stub-language-server.mjs`, `scripts/testers/svelte-development/kit3-app/**` — **Keep** (fixtures, not run as tests)

### 10. Evaluation
- Trigger evals: does the skill or agent fire when it should
- Behavior and output-quality evals

**Commands**
- `claude plugin eval init [name]` — run from the plugin root; interactive interview that writes the suite
- `claude plugin eval .` — run every case, with and without the plugin, and report the difference
- `claude plugin eval . --case <case-name> --runs 1 --ablation none` — fast single-case iteration

**Gotchas**
- Put the target before `--tag`, `--allow-tools` and `--json`; each takes the following words as its value [skill]
- Evals call the model with your credentials and bill your plan or API account [docs]
- A case without a grader fails to load [docs]

**Scripts**
- `plugins/<p>/evals/**` (including `fixture.sh` scaffolds) — **Keep in plugin** (rule 4) · Caller: `claude plugin eval` only · Fully covered by the command; never run today
- `scripts/testers/changed-eval-plugins.sh` — **Move** from `.claude/skills/testing-plugins/scripts/` · Caller: the new eval workflow · Gap: selects plugins with evals that changed between BASE and HEAD; `eval` doesn't select by diff
- `.github/workflows/evals.yml` — **New** (entry point; from the template in `.claude/skills/testing-plugins/assets/evals-ci.yml`) · Runs `claude plugin eval` on the plugins `changed-eval-plugins.sh` selects. Needs a credential secret and a usage budget: *decision pending*

### 11. Documentation
- Plugin README: purpose, installation, tested Claude Code version
- Usage and configuration examples
- Root README catalog and maintainer reference pages
- `docs/`: reference documentation for users and third parties: `installation.md`, `managing-plugins.md`, `troubleshooting.md`, `faq.md`, `compatibility.md` (see stage 1), `github-mcp-tools.md` (GitHub Operations' MCP tools) and `assets/`
- README rules:
  - A README describes what exists now; old names, merges, removed features and migration steps go in the CHANGELOG and the release notes
  - Each kind has its rule and template: root `README.md` → `.claude/rules/maintainer/root-readme.md` and `.claude/templates/root-readme-template.md`; `plugins/<plugin>/README.md` → `.claude/rules/plugins/plugin-readme.md` and `.claude/templates/plugin-readme-template.md`; a maintainer README outside `plugins/` only has to stay accurate
  - User READMEs: English, second person, present tense; never mention the repository's maintenance, `.claude/`, scripts, CI or release mechanics; every command, flag, UI path and minimum version checked against the sources first
  - One fact, one value: the marketplace is `nerymurillohnd/the-claude-factory` (`@the-claude-factory`)
  - A plugin's README changes in the same change as its components, prerequisites, surfaces, configuration or minimum Claude Code version
  - Version shown in READMEs: one badge per plugin README, on line 7, a shields.io dynamic badge reading `$.version` from that plugin's `plugin.json` on `main`; the root catalog's version column is generated by `npm run generate`

**Commands**
- `claude plugin validate <path>` — prints an `Advice` block when the README has no install-from-marketplace line

**Gotchas**
- `Advice` never changes the verdict or exit code, even with `--strict`; CI will not fail on it [docs]
- `--profile directory` checks only that a README exists and has 40 words (NV-A7)

**Scripts**
- `scripts/check-repo.mjs` — **Keep** · Callers: gate, CI · Gap: README sections, template placeholders, Compatibility cells against `docs/compatibility.md`, the Platforms line
- `scripts/generators/catalog.mjs` — **Keep** · Callers: manual (`npm run generate`), gate and CI (`--check`) · Gap: builds the root README catalog from marketplace and manifests (NV-C)
- `scripts/validators/readme-catalog-consistency.py` — **Keep** · Callers: gate, CI, commit · Gap: one catalog row per plugin under its category, categories match, `mods` holds only mods
- `scripts/checkers/markdown-urls.py` — **Keep** · Caller: manual · Gap: live check of every http(s) URL and fragment in tracked Markdown
- `scripts/checkers/reference-pages.py` — **Keep** · Caller: manual · Gap: offline layout (`## Contents`, `## Documentation References`), relative links and anchors

---

## Phase C — Release Cycle (per version)

### 12. CHANGELOG Update
- One entry per version: Added / Changed / Fixed / Removed / Deprecated
- Flag breaking changes
- `CHANGELOG.md`: an empty `## [Unreleased]`, one `## [x.y.z]` heading per released version and no other, compare and tag links to `<plugin>--v<x.y.z>`; a breaking entry starts with `**Breaking:**`

**Commands**
- No CLI command

**Scripts**
- `scripts/release/bump-version.py` — **Keep** · Callers: manual (`npm run version:bump`), skill · Gap: turns `[Unreleased]` into the dated section (America/Tegucigalpa) with its links. No command writes a CHANGELOG
- `scripts/validators/plugin-versions-consistency.py` — **Keep** · Callers: gate, CI, commit · Gap: CHANGELOG sections, order and links agree with `plugin.json`; root CHANGELOG lines, README badge, catalog version

### 13. Versioning / Bumping
- Choose the SemVer bump: major / minor / patch
- Keep `plugin.json` and the marketplace entry in sync
- Format: SemVer `MAJOR.MINOR.PATCH`, in the one place stage 7 sets
- Major: a breaking change, such as a removed or renamed skill, agent or command, a renamed plugin, changed configuration keys, a new mandatory dependency, or changed behavior users rely on
- Minor: a new backward-compatible component, option or capability. In `0.x`, breaking changes also bump minor, with the `**Breaking:**` entry of stage 12; `1.0.0` needs Nery's explicit authorization
- Patch: a backward-compatible bug fix, prompt wording, performance, or an internal refactor that keeps observable behavior
- No bump: a change limited to the plugin's documentation files or its in-plugin maintainer files (tests, the eval suite)
- Each bump is exactly one step above `origin/main`; a change that mixes levels takes the highest

**Commands**
- No bump command: edit `version` by hand
- `claude plugin validate .` — reports `Entry declares version "<a>" but <path>/plugin.json says "<b>"`

**Gotchas**
- `validate` accepts non-SemVer versions such as `"1.0"`; enforce SemVer with a script [E8]

**Scripts**
- `scripts/release/bump-version.py` — **Keep** (see stage 12) · Gap: writes the new version in `plugin.json`. Doesn't regenerate the catalog: run `catalog.mjs` after it
- `scripts/release/check-version-bump.py` — **Keep** · Callers: gate `version-bump`, CI · Gap: every plugin changed since `<base>` went up exactly one SemVer step and has its CHANGELOG section, with exemptions. `tag --dry-run` only checks entry/manifest agreement (NV-A12)

### 14. Tagging
- `claude plugin tag` → `<plugin>--v<version>`
- Pre-checks: validation, matching version, clean working tree, tag not already present
- `--dry-run` before creating
- **GitHub Actions:** release workflow triggered after validation (re-validate, create the GitHub Release, attach notes from the CHANGELOG)
- Every released version has its tag and a GitHub Release with the same name, never draft or prerelease; the latest tag equals the `version` on `main`, `plugin.json` at the tagged commit holds it, and the tag commit is an ancestor of `main`. `release.yml` creates the tags unsigned; every commit and every local tag is SSH-signed

**Commands**
- `claude plugin tag [path] --dry-run` — show the plan without creating anything
- `claude plugin tag [path]` — create the annotated tag
- `claude plugin tag [path] --push` — create and push (requires authorization)
- `/plugin tag [path] [--push] [--dry-run] [--force]` — session form; accepts only these flags

**Gotchas**
- Needs a git repository, a `version` in `plugin.json` or the entry, a clean working tree and a new tag [skill]
- `--dry-run` produced the same tag names as `release-notes.py --tag` on 22 of 22 plugins [E5]
- `release.yml` creates the tag through `gh release create`, so `claude plugin tag` cannot replace that step as written

**Scripts**
- `scripts/release/release-notes.py` — **Keep** · Caller: `.github/workflows/release.yml` · Gap: the release body (CHANGELOG section plus the update command). Its `--tag` mode duplicates `tag --dry-run` (E5): *reduce or keep, decision pending*
- `.github/workflows/release.yml` — **Keep** (entry point) · Optional **New** step: `claude plugin tag <p> --dry-run` before `gh release create` (low value: `plugin-versions-consistency.py` already covers the version pair)

### 15. Publishing / Distribution
- Push and merge (with authorization)
- Public repository or submission to Anthropic's directory
- Installation instructions for users

**Commands (to document for users)**
- `claude plugin marketplace add <owner/repo>`
- `claude plugin install <plugin>@<marketplace>`
- `claude plugin install <plugin> --marketplace <source>` — one step

**Gotchas**
- Without a TTY, an install that shows a marketplace-declared command is refused unless `-y` or `--accept-command <sha256>` is passed [skill]

**Scripts**
- `scripts/release/check-published-install.sh` — **New** · Caller: a post-release CI job · Gap: in an isolated `CLAUDE_CONFIG_DIR`, `marketplace add` the GitHub repository, `install` the released plugin, read `installPath` from `list --json`, then `validate --strict` and `test` (mods) on what users actually receive (E10). Each step is a command; the script only orchestrates and isolates

### 16. Update Delivery
- `claude plugin update` on the user side
- Auto-update (off by default for third-party marketplaces)
- Announce new versions to users

**Commands (user side)**
- `claude plugin marketplace update [name]` — refresh listings
- `claude plugin update <plugin> [--scope]` — install the new version
- `/reload-plugins` — load it into a running session
- Auto-update toggle: `/plugin` → Marketplaces tab

**Gotchas**
- No command updates every plugin at once; `marketplace update` refreshes listings but leaves installed plugins at their versions [skill]
- Before v2.1.281, `update` without `--scope` assumed `user` and failed for project- or local-scope installs [skill]
- Users on a pinned `version` receive nothing until the version string changes [docs]

**Scripts**
- None. User-side commands; the release body from `release-notes.py` (stage 14) carries the update command.

---

## Phase D — Operations (ongoing)

### 17. Monitoring & Measurement
- Plugin cost and usage
- Issues and user feedback (triaged through the issue forms and labels)

**Commands**
- `claude plugin details <name>` — projected token cost per plugin
- `claude plugin list --json --data-size [plugin]` — size of each plugin's saved data
- `/plugin stats` — Stats tab, where `/skill-doctor` is available

**Gotchas**
- `details` requires the plugin to be loaded: installed, in a skills directory, or passed with `--plugin-dir`/`--plugin-url` in the same command [docs]
- Token projections can change with sign-in state; compare only figures taken under the same auth [E14]
- `--available` and `--data-size` have no effect without `--json` [docs]

**Scripts**
- `scripts/validators/skill-size.py` — **Keep** (see stage 5) · Gap: turns the `details` token figure into a limit with a baseline ratchet; `details` reports and never fails

### 18. Maintenance
- Update components for Claude Code changes
- Dependencies and security patches (Dependabot PRs)
- Re-run evals after relevant changes
- Keep CI workflows and templates current

**Commands**
- `claude --version`, `claude plugin <subcommand> --help` — detect CLI changes
- `claude plugin validate <path> --strict` and `claude plugin eval .` — regression checks
- `HOME=<tmp> claude plugin init <name> --with skills agents hooks mcp lsp` — reference only, in an isolated `HOME`: after a CLI upgrade, compare the official scaffold with the repository templates; delete the temp folder afterwards

**Gotchas**
- Re-test the native coverage gaps (Appendix A) after each CLI upgrade; a gap closed upstream can make a script redundant (rule 2)
- Never run `init` without an isolated `HOME`: the scaffold would load in every maintainer session [docs]

**Scripts**
- `scripts/testers/schemas/test_schemas.py` — **Keep** · Caller: `npm test` · Re-run after CLI upgrades: its recorded cases document which gaps still exist
- `scripts/sync-labels.mjs` — **Keep** (see stage 3) · Run after adding a plugin (one `plugin: <name>` label each)

### 19. Catalog Changes
- Renaming via the `renames` map
- Removing via `renames: null` and `forceRemoveDeletedPlugins`
- Deprecation: advance notice and a transition period

**Commands**
- `claude plugin validate .` — after editing `renames` or entries
- `claude plugin uninstall <plugin> [--scope] [--keep-data] [--prune]` (aliases `remove`, `rm`) — user side
- `claude plugin marketplace remove <name>` — uninstalls every plugin from that marketplace

**Gotchas**
- `validate` accepts a `renames` key that is still a listed plugin; check this yourself [E9]
- `uninstall` from the last scope deletes options, secrets and data unless `--keep-data` is passed [docs]
- `marketplace remove` uninstalls every plugin from that marketplace and deletes their options, secrets and data; use `marketplace update` to refresh [docs]
- `uninstall --json` can't be combined with `--prune` [docs]

**Scripts**
- `scripts/validators/plugin-names-consistency.py` — **Keep** (see stage 7) · Gap: a `renames` key that is still listed (only check that catches it, E13)
- `scripts/checkers/check-plugin-name.py` — **Keep** after its move (see stage 4) · Gap: a retired name cannot be reused
- `scripts/generators/marketplace.mjs`, `catalog.mjs` — **Keep** · Regenerate entries and catalog after the change

### 20. Troubleshooting
- Marketplace and plugin validation errors
- Plugins that fail to load, or install but don't work
- Component issues: hooks not firing, MCP servers not starting, skills not invoked
- Distribution issues: `Plugin "<name>" not found in marketplace`, users not receiving updates
- Every fix re-enters the cycle: 8 → 9 → 12 → 13 → 14 → 16

**Commands**
- `claude plugin validate <path> --json`
- `claude plugin list --json` — includes `installPath` of each plugin
- `claude plugin marketplace list --json` — includes `installLocation` of each marketplace
- `/plugin list --enabled|--disabled`
- `claude plugin details <name>`
- `claude plugin restore-set-aside <name@marketplace> [--discard]` — recover options and secrets set aside when a managed marketplace replaced a plugin's source
- `/plugin` (Errors tab) and the `/reload-plugins` summary (`N errors during load`)
- Error lookup: https://code.claude.com/docs/en/plugins/troubleshooting

**Gotchas**
- A clean `list --json` does not prove a component is valid: a defective `.lsp.json` shows no `errors` or `notes` [E6]
- `restore-set-aside --discard` deletes the set-aside options and secrets permanently [skill]
- A synced plugin (`<name>@synced`) appears only in sessions signed in with the claude.ai account [skill]

**Scripts**
- None. The commands cover diagnosis; fixes re-enter stages 8 → 16 with their scripts.

---

# Part 2 — Target structure

```text
.
├── .claude/
│   ├── settings.json            # CC hook registrations → ${CLAUDE_PROJECT_DIR}/scripts/... (no .claude/hooks/ scripts)
│   ├── skills/                  # project skills: procedures only, no scripts/ folders
│   └── CLAUDE.md
├── .husky/
│   ├── pre-commit               # entry point → biome --staged, npm test
│   └── pre-push                 # entry point → npm run gates
├── .github/
│   ├── workflows/
│   │   ├── validate.yml         # gates:ci groups (+ profile, project validate, mod-test, hooks-catch)
│   │   ├── release.yml          # release-notes.py, gh release create
│   │   ├── evals.yml            # NEW · changed-eval-plugins.sh → claude plugin eval
│   │   ├── claude.yml
│   │   └── claude-code-review.yml
│   ├── ISSUE_TEMPLATE/  pull_request_template.md  labels.json  CODEOWNERS  dependabot.yml
├── plugins/<p>/
│   ├── tests/*.test.ts(x)       # mods only — stays (claude plugin test)
│   └── evals/**                 # stays (claude plugin eval)
└── scripts/
    ├── gates.mjs  check-repo.mjs  basedpyright-maintainer.mjs  sync-labels.mjs
    ├── lib.mjs  components.mjs
    ├── session/                 # NEW subfolder (pending) · checkout.sh
    ├── validators/              # plugin-json-schema, marketplace-json-schema, mcp-json-schema,
    │                            # lsp-json-schema, hooks-json-schema (NEW), plugin-names-consistency,
    │                            # plugin-versions-consistency, plugin-required-files, plugin-icons,
    │                            # readme-catalog-consistency, skill-names-consistency,
    │                            # skill-argument-placeholders, skill-references, skill-size,
    │                            # skill-frontmatter (MOVED)
    ├── checkers/                # markdown-urls, reference-pages, check-plugin-name (MOVED), fetch-github-mod (MOVED)
    ├── generators/              # marketplace, catalog, plugin-icons (+ plugin-icons/*.svg), scaffold-plugin (MOVED)
    ├── release/                 # bump-version, check-version-bump, release-notes, check-published-install (NEW)
    ├── schemas/                 # one schema per shape
    └── testers/                 # maintainer tests, per-plugin testers, changed-eval-plugins (MOVED), fixtures
```

---

# Appendix A — Native validator coverage (`validate --strict`, CLI 2.1.322)

| File | Caught by the CLI | Not caught by the CLI | Script that covers it |
|:--|:--|:--|:--|
| Skill frontmatter | Parse errors (NV-A2) | Non-strict YAML [E1] | `skill-frontmatter.py` |
| `hooks/hooks.json` | Wrong `type`, missing `command`, unquoted `${CLAUDE_PLUGIN_ROOT}`, misspelled `hooks` [E7] | Unknown keys [E7]; duplicate keys [E12] | `hooks-json-schema.py` (New) |
| `.mcp.json` | Missing `command`, types, unknown `type`, undeclared `user_config`, `http://` (NV-B1) | Unknown keys, duplicate keys | `mcp-json-schema.py` |
| `.lsp.json` | Inline `lspServers` only (NV-B2) | Every file-based `.lsp.json` [E6] | `lsp-json-schema.py`, `check-repo.mjs` |
| Mod hooks module | — | All checks (`incomplete: true`) [E2] | `gates.mjs` `mod-hooks-catch` (New); `claude plugin test` |
| `plugin.json` | Empty `description` (warning), empty `author.name` (error) [E8] | Non-SemVer `version`, invalid `author.email`, non-SPDX `license`, foreign `repository`, duplicate `keywords`, unknown `metadata.category`, empty `displayName` [E8] | `plugin-json-schema.py` (+ extensions), `check-repo.mjs`, `marketplace.mjs --check`, `catalog.mjs --check` |
| `marketplace.json` | Name with spaces [E9] | Top-level or `metadata` version, missing/empty entry `description`, invalid `owner.email`, unknown entry `category`, mismatched entry `name`/`source`, `renames` key still listed [E9] | `check-repo.mjs` (+ `metadata.version`), `marketplace-json-schema.py` (+ `owner.email`), `marketplace.mjs --check`, `plugin-names-consistency.py`, `readme-catalog-consistency.py` |
| Directory (`--profile directory`) | `.DS_Store`, missing `icon` path (warnings) [E3] | Windows-reserved or invalid names, case collisions, symlinks, size or file-count limits [E3] | `check-repo.mjs`, `plugin-icons.py` |

# Appendix B — Retired scripts and why

| Script (current path) | Reason | Replaced by |
|:--|:--|:--|
| `.claude/skills/building-plugins/scripts/check-required-files.py` | Duplicate; validator caught every case it caught | `scripts/validators/plugin-required-files.py` |
| `.claude/skills/building-plugins/scripts/check-manifest-schema.py` | Duplicate, second schema engine | `scripts/validators/plugin-json-schema.py` |
| `.claude/skills/building-plugins/scripts/check-mcp-schema.py` | Duplicate | `scripts/validators/mcp-json-schema.py` |
| `.claude/skills/building-plugins/scripts/check-lsp-schema.py` | Duplicate | `scripts/validators/lsp-json-schema.py` |
| `.claude/skills/building-plugins/scripts/check-skill-names.py` | Duplicate and weaker: missed unparsable frontmatter and a duplicate key | `scripts/validators/skill-names-consistency.py` |
| `.claude/skills/building-plugins/scripts/check-readme-placeholders.py` | Weaker: passed a placeholder `check-repo` caught | `scripts/check-repo.mjs` |
| `.claude/skills/plugin-categories/scripts/check-catalog-categories.py` | Duplicate | `scripts/validators/readme-catalog-consistency.py` |
| `.claude/skills/testing-mods/scripts/check-mod.sh` | Both steps already run as gates; its summary-line guard folds into `gates.mjs` | `gates.mjs` `claude-validate:<p>` and `mod-test:<p>` |
| `.claude/hooks/validators-gate.sh` | Orchestrator duplicating `gates.mjs`; ran `skill-size.py` despite E14 | CC hook calling `gates.mjs --only` |
| `scripts/release/check-changelog-entry.py` | Orphan (no caller); every case it caught, `plugin-versions-consistency.py` caught too | `scripts/validators/plugin-versions-consistency.py` |
| `scripts/release/check-marketplace-unversioned.py` | Orphan; its only unique rule (`metadata.version`) folds into `check-repo.mjs` | `scripts/check-repo.mjs` |
| `release-notes.py --tag` mode *(reduce, pending)* | Duplicates `claude plugin tag --dry-run` (E5) | `claude plugin tag --dry-run`, or keep |

# Appendix C — Open gaps and pending decisions

| Item | Status |
|:--|:--|
| Duplicate keys in `hooks.json` (E12) | Covered by `hooks-json-schema.py` (New) |
| `author.email`, duplicate `keywords`, `owner.email` (E13) | Covered by schema extensions (New) |
| Gating mod hooks without `.catch` in `project-maintainer` and `turn-meter` (E2) | Decide whether this is a defect before adding the gate (it fails today) |
| `skill-size.py` depends on sign-in state (E14) | Fix before it returns to the commit hook or CI |
| Runtime effect of a bad `.lsp.json` | Untested in a session |
| Eval workflow: credentials and budget | Decision pending |
| `scripts/session/` subfolder for `checkout.sh` | Decision pending |
| anthropics/claude-code#103055 (output loss in `test`) | Not reproduced on 2.1.322 (E11); keep the guard until upstream confirms |
| `gates.mjs --only` accepts the validator selectors this blueprint uses | Unverified: confirm in the implementation plan |
| Validators can be scoped to one plugin when a skill calls them | Unverified: confirm in the implementation plan |

# Appendix D — Records this blueprint changes

| Record | Effect |
|:--|:--|
| `ADR_2026-10-25_skill-checks-are-separate-from-gates` | Superseded: one copy per check in `scripts/`; skills and gates both call it |
| `ADR_2026-10-25_skill-scripts-are-stdlib-python` | Superseded: no skill scripts remain |
| `ADR_2026-11-01_release-scripts-live-in-scripts-release` | Precedent; consistent with this blueprint |
| `ADR_2026-10-21_maintainer-scripts-at-root` | Consistent; extended to hooks and skill scripts |
| `plugin-scaffold-belongs-to-building-plugins`, `category-rules-live-in-plugin-categories-skill`, `procedures-live-in-project-skills`, `building-plugins-is-this-repositorys-procedure`, `testing-plugins-owns-live-mcp-checks`, `building-mods-skill-holds-mod-authoring`, `rebuilt-skills-do-not-run-check-repo` | To review (not yet read): likely affected by the skills refactor |

# Appendix E — Project skills catalog (PROPOSAL, reference only)

> **Status: not implementable.** Do not build, scaffold or run any skill in this appendix unless Nery requests it explicitly.  
> **Prerequisite:** Parts 1–2 of this blueprint implemented and proven (scripts relocated, retirements done, gates and CI green).  
> **Purpose:** record the intended skill layer so the refactor leaves room for it. Final names, scope and consolidation are decided after the new structure is proven.

## Principles

- **The blueprint says what, where and when; each skill says how** for its stages.
- **Skills hold procedures only.** They call `scripts/` through `${CLAUDE_PROJECT_DIR}` and pre-approve those exact commands with `allowed-tools: Bash(${CLAUDE_PROJECT_DIR}/scripts/... *)`. No `scripts/` folder inside any skill (rule 6).
- **Hooks enforce, skills orchestrate.** Anything that must hold every time stays in a hook or gate; a skill adds judgment and multi-step flow.
- **Side effects are user-invoked.** Skills that write, tag, push or change the catalog set `disable-model-invocation: true`.
- **Consolidate stages** where one procedure naturally spans them, to keep the skill count small.
- **Avoid names of bundled skills** (`doctor`, `code-review`, `debug`, `loop`, `run`, `simplify`), except `verify`, which intentionally replaces the bundled one at the repository root.

## Proposed skills

| Skill | Stages | Invocation | Orchestrates (scripts and commands) |
|:--|:--|:--|:--|
| `verify` | 8, 9, (10) | Claude-invocable; runs before each commit (Claude Code ≥ 2.1.286, `includeGitInstructions` on) | `gates.mjs --only` on changed plugins; `by_path` testers of those plugins; `claude plugin details`; optional single-case `claude plugin eval` |
| `scaffold-plugin` | 4, 5 (setup), 6, 7 | User only | `check-plugin-name.py` → `scaffold-plugin.py` → `plugin-icons.mjs` → `marketplace.mjs` → `claude plugin validate --strict [--profile directory]` → `sync-labels.mjs` |
| `docs-sync` | 11 | User only | `catalog.mjs` → `readme-catalog-consistency.py` → `check-repo.mjs` → `reference-pages.py` → `markdown-urls.py` |
| `release-plugin` | 12, 13, 14, 15 | User only; push and release need explicit authorization | `bump-version.py` → `catalog.mjs` → `check-version-bump.py` → `plugin-versions-consistency.py` → `claude plugin tag --dry-run` → `release-notes.py`; post-release `check-published-install.sh` |
| `catalog-change` | 19 | User only | `renames` / `forceRemoveDeletedPlugins` edit → `check-plugin-name.py` → `plugin-names-consistency.py` → `marketplace.mjs` → `catalog.mjs` → release flow |
| `audit-repo` | 3, 17, 18 | Claude-invocable (read-only) | `gates.mjs` full run; Appendix A gap re-test after a CLI upgrade; `HOME=<tmp> claude plugin init` scaffold comparison; `skill-size.py` report; `skill-references.py` |
| `troubleshoot-plugin` | 20 | Claude-invocable (read-only) | `claude plugin validate --json`, `list --json`, `marketplace list --json`, `details`; troubleshooting page lookup; hands the fix back to `verify` / `release-plugin` |

## Stages without a skill

| Stage | Why |
|:--|:--|
| 1 Planning & Design | Decisions, recorded as ADRs; no executable procedure |
| 2 Marketplace Scaffolding | One time, already done |
| 16 Update Delivery | User side; the release body carries the update command |

## Open questions (decide after the refactor is proven)

- Merge `docs-sync` into `release-plugin` and `scaffold-plugin`, since both already regenerate the catalog?
- Split `catalog-change` into `rename-plugin` and `retire-plugin`, or keep one?
- Is a project `verify` running before every commit acceptable in time and usage, or should it be user-invoked (which removes the automatic pre-commit run)?
- Does `audit-repo` absorb `troubleshoot-plugin`?

# Appendix F — Where this blueprint lives once adopted

> Decided in the implementation plan. `CLAUDE.md` loads every session and the official guidance keeps it under 200 lines; this blueprint is over 500 without appendices.

| Content | Location | Loads |
|:--|:--|:--|
| The six blueprint rules and a pointer to the full map | `.claude/CLAUDE.md` | Every session (a few lines) |
| File-bound rules (e.g. `scripts/validators/**`, `plugins/*/hooks/**`, `.github/workflows/**`) | `.claude/rules/` with `paths` frontmatter | Only when Claude works with matching files |
| Stage procedures not bound to a path (release, catalog changes, troubleshooting) | The full map as a reference document (e.g. `.claude/maintainer/blueprint.md`), later the skills of Appendix E | When a task or skill needs it |
