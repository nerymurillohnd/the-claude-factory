# The Claude Factory

Public Claude Code plugin marketplace (`github.com/nerymurillohnd/the-claude-factory`) for users and developers who run projects and operations with Claude. It publishes plugins only, built for Claude Code and, where applicable, the Claude app. Development occurs in Nery’s local clone; distribution occurs from the remote repository. Users participate solely through issues.

## Purpose

Publish plugins that automate and optimize everyday workflows.

- Design, build, and document every plugin solely from its own goals: what it must do, execute, and solve for its users. Never treat another plugin’s implementation as a reference, pattern, justification, or constraint.

## Responsibility

This marketplace is public. Published plugins execute on other people’s machines, inside their projects and operations. Nery is the sole owner and author and remains personally accountable for any harm a plugin causes a user, however minor.

- Nery and Claude Code are the only parties responsible for this marketplace and the only parties who work on it. There are no external collaborators. GitHub Copilot acts only at Nery's explicit request in a pull request (reviews, and the commits Nery asks for) and never works on its own; treat its reviews and commits as Nery-directed work.
- Users contribute only by opening issues. Triaging, confirming, fixing, verifying, and releasing every fix is the exclusive work of Nery and Claude Code; the reporter has no further obligation.
- No third-party review occurs before users install a plugin. Every push, release, and issue reply is the final gate before public exposure.

## Operating Standard

This standard applies to every session on this repository, including the current one:

- Ship nothing that has not been verified against current Claude Code official documentation and the latest release notes. Out-of-date knowledge or negligence that reaches a user constitutes the failure this project exists to prevent.
- Treat every action a plugin performs on a user’s machine (files, commands, network, hooks, permissions, data) as high-risk. Prefer the least invasive design.
- When safety for users cannot be determined with certainty, state the uncertainty and obtain Nery’s explicit approval before shipping. Never publish on a guess.
- Report problems immediately upon discovery, including one’s own errors and defects in already-published work.
- Improve the working system, not only the delivered artifacts. When a session reveals a gap in this file, a rule, a gate, or a skill, propose the corrective change in the same session.
- Automate recurring work (validation, review, releases, drift detection, issue handling) through CI, evals, hooks, agents, and scheduled tasks. Where no automation yet exists, propose its construction.

## Current Claude Code features, capabilities, and guidance enforcement

Claude Code, the Claude app, the Claude models and every tool the gates run change faster than training data, recall or project docs. Before any plan, plugin component or scaffold, and before any answer about how they behave, read the current official documentation and release notes.

- When sources differ, trust them in this order: the installed binary (`--help`, `claude plugin validate`, `claude plugin test`), then the release notes, then the docs, which lag releases. When a release note and a doc describe different stages (loading versus validation), confirm on the installed build before relying on either.
- When components depend on each other, research each side. For example, a plugin hook needs the hooks reference, the plugins reference and the Claude app platform-support page.

## Maintainer and Plugin Scopes

This repository holds two scopes. They are never mixed: a rule written for one scope does not apply to the other, and nothing from the maintainer's environment becomes something a plugin needs to run. Maintainer tools may check plugin files; that never makes them a plugin dependency. Before acting, identify the scope of every file the task touches; a task that touches both is handled as two parts, each under its own rules.

- **Maintainer scope**: everything outside `plugins/`. Its environment is the tools, versions and binaries on Nery's machine.
- **Plugin scope**: one self-contained directory per plugin under `plugins/<plugin>/`. Its environment is only what the plugin's `README.md` declares as prerequisites; users' compatibility comes only from the README's declared minimum Claude Code version.
- **Maintainer files inside a plugin**: a mod's `*.test.ts(x)` (in the mod's `tests/`, importing only the mod's files and `claude-code/testing`) and a plugin's eval suite stay in the plugin's directory, because `claude plugin test` and `claude plugin eval` only find them there. They are maintainer tooling, run only on Nery's build, and ship to users as inert files. Everything committed under `plugins/<plugin>/` reaches every user's cache; nothing git-ignored does, so commit no other maintainer-only file there.

## Repository Layout

- `.claude/specs/`: Specification documents. Specs are written before implementation plans.
- `.claude/plans/`: Implementation plans derived from approved specs. The folder is created with the first plan.
- `.claude/maintainer/`: Decision records and technical-debt tracking.
- `.claude/rules/`: Path-scoped rules; each one loads when Claude reads or edits a file its `paths` cover.
- `.claude/templates/`: The README templates: `root-readme-template.md` for the root `README.md` and `plugin-readme-template.md` for each `plugins/<plugin>/README.md`.
- `scripts/`: Maintainer scripts that build, check, and release this repository.
- `plugins/`: The plugins that are developed, published, and maintained in this repository.
- `docs/`: Reference documentation and repository information intended for users and third parties.
- `.claude-plugin/marketplace.json`: The marketplace manifest.

## Commands

- Run Biome and `tsc` only through `npm run`, which uses the versions `package-lock.json` pins; never by bare name.
- Ruff, Basedpyright, shfmt, ShellCheck and actionlint may run directly to check one file, but `npm run gates` is the verdict: it holds each tool's scope and flags, as CI and Husky run them.
- Use `claude plugin validate` and `claude plugin test` to check a mod's hooks module; no gate type-checks it against `.claude-plugin/types/`.
- `format` and `fix` also write in `plugins/`.
- Fix what the Husky hooks and the Claude Code hooks in `.claude/settings.json` report; never skip them.

The repository's scripts, in the order of the project's phases, with what triggers each one.

### Phase 0: Environment and session

| Script | What it does | Triggered by |
| :-- | :-- | :-- |
| `.claude/hooks/checkout.sh` | Reports the branch, ahead/behind against `main` and the tool versions | SessionStart hook |
| `npm install` → `prepare` (Husky) | Installs the pinned maintainer tools and the git hooks | Manual |

### Phase 1: Creating a plugin (skill `building-plugins`)

| Script | What it does |
| :-- | :-- |
| `.claude/skills/building-plugins/scripts/check-plugin-name.py` | The name is free and unlike every name the marketplace uses |
| `.claude/skills/building-plugins/scripts/scaffold-plugin.py` | Creates `plugins/<name>/` from the templates |
| `.claude/skills/building-plugins/scripts/check-required-files.py` | The manifest, README, changelog and license exist |
| `.claude/skills/building-plugins/scripts/check-manifest-schema.py`, `check-mcp-schema.py`, `check-lsp-schema.py` | The plugin's manifest, MCP and LSP files conform to the repository schemas |
| `.claude/skills/building-plugins/scripts/check-skill-names.py` | Every skill is named after its directory |
| `.claude/skills/building-plugins/scripts/check-readme-placeholders.py` | No README template placeholder is left |
| `.claude/skills/plugin-categories/scripts/check-catalog-categories.py` | The README catalog lists each plugin once, under its category |

### Phase 2: Development and editing

| Script | What it does | Triggered by |
| :-- | :-- | :-- |
| `.claude/hooks/skill-frontmatter.py` | Checks `SKILL.md` frontmatter as strict YAML | PreToolUse and PostToolUse hooks on `SKILL.md` edits |
| `npm run format` / `npm run fix` | Biome, Ruff and shfmt | Manual |
| `npm run lint` / `npm run typecheck` → `scripts/gates.mjs` | Biome, Ruff, ShellCheck, actionlint, `tsc` and Basedpyright | Manual |
| `scripts/basedpyright-maintainer.mjs` | Type-checks the maintainer Python, each file against the interpreter that runs it | `scripts/gates.mjs` |
| `.claude/skills/testing-mods/scripts/check-mod.sh`, `fetch-github-mod.sh` | Runs `claude plugin validate --strict` and `claude plugin test` on a mod; clones an outside mod for comparison | Skill `testing-mods` |

### Phase 3: Tests

| Script | What it does | Triggered by |
| :-- | :-- | :-- |
| `npm test` → `scripts/testers/*.test.mjs` and `scripts/testers/run_unittest.py` | Tests of the maintainer tooling (scripts, gates, schemas, validators) | Husky pre-commit |
| `npm run test:plugins` → `scripts/testers/<plugin>/*` (`by_path.sh`, `test_*.py`, `*.test.mjs`) and `mod-test` | Each plugin's behavior | Local only |
| `.claude/skills/testing-plugins/scripts/changed-eval-plugins.sh` | Selects the plugins that get the full eval suite in CI | Nothing calls it yet |

### Phase 4: Structure and consistency checks

| Script | What it does | Triggered by |
| :-- | :-- | :-- |
| `scripts/validators/*.py` (13) | Schemas (plugin, marketplace, MCP, LSP), names, versions, required files, icons, catalog, skills, skill and command argument placeholders, `SKILL.md` references, plugin skill sizes (`skill-size.py`, through `claude plugin details`, so the gates run it in the claude group) | `npm run validate`, `scripts/gates.mjs`, the commit hook |
| `scripts/check-repo.mjs` (with `scripts/components.mjs`) | Repository policies that neither `claude plugin validate` nor the validators cover | `scripts/gates.mjs` |
| `scripts/checkers/markdown-urls.py` | Every http(s) URL in the Markdown files answers | Manual only (`npm run check:links`) |
| `scripts/checkers/reference-pages.py [--links-only] DIR...` | Every Markdown page under DIR has its `## Contents` and `## Documentation References` layout, and its relative links and anchors resolve | Manual only (`npm run check:references`) |

### Phase 5: Versioning

| Script | What it does | Triggered by |
| :-- | :-- | :-- |
| `scripts/release/bump-version.py` | Raises a plugin's version and turns `[Unreleased]` into the dated section | Manual (`npm run version:bump`) |
| `scripts/release/check-version-bump.py` | Every plugin whose files changed has a new version and its entry | `scripts/gates.mjs` (local and CI) |
| `scripts/release/check-changelog-entry.py` | The plugin's `CHANGELOG.md` has a non-empty section for its current version | Nothing calls it |
| `scripts/release/check-marketplace-unversioned.py` | `marketplace.json` carries no version | Nothing calls it |

### Phase 6: Catalog and icon generation

| Script | What it does | Triggered by |
| :-- | :-- | :-- |
| `scripts/generators/marketplace.mjs`, `scripts/generators/catalog.mjs` | Rebuild `marketplace.json` and the README catalog | `npm run generate` |
| `npm run generate:check` | Confirms both are current | `scripts/gates.mjs` |
| `scripts/generators/plugin-icons.mjs [plugin...]` | Renders `scripts/generators/plugin-icons/<plugin>.svg` into the plugin's `.claude-plugin/icon.png`; needs Playwright's Chromium, ImageMagick and the JetBrains Mono font | Manual only, after an SVG source changes |

### Phase 7: Commit and push

| Script | What it does | Triggered by |
| :-- | :-- | :-- |
| `.claude/hooks/validators-gate.sh` | Runs the validators and blocks the commit when one fails | PreToolUse hook on `git commit` |
| `.husky/pre-commit` | `biome check --staged` and `npm test` | Git |
| `.husky/pre-push` → `scripts/gates.mjs` | Every gate, the local-only ones (branch, status, signatures) included | Git |

### Phase 8: CI and release

| Script | What it does | Triggered by |
| :-- | :-- | :-- |
| `.github/workflows/validate.yml` → `scripts/gates.mjs --ci` | The same gates without the local-only ones, in one job per group (policy, python, claude, lint) | Push to `main` and pull requests |
| `.github/workflows/release.yml` → `scripts/release/release-notes.py` | Creates the `<plugin>--vX.Y.Z` tag and its GitHub Release with the notes | Validate green on `main` |

### Phase 9: Repository upkeep

| Script | What it does | Triggered by |
| :-- | :-- | :-- |
| `scripts/sync-labels.mjs` | Creates and updates the labels from `.github/labels.json`, plus one `plugin: <name>` label per plugin | Manual only (`npm run labels:sync`) |

Shared support, never run on its own: `scripts/lib.mjs`, `scripts/components.mjs`, `scripts/schemas/**`, `scripts/biome-plugins/main-module.grit`, `scripts/tsconfig*.json` and `scripts/pyrightconfig.maintainer.json`.

## Change Control

- Release tags are created unsigned by `release.yml`, as this project's exception to the global signing rule: signing in CI would put the signing key in a GitHub secret. Users' Claude Code resolves dependency version ranges against these tags by name, without verifying signatures. Every commit, and every tag created locally, is still SSH-signed.

## How To Work in this Project


### Required existence
- Every plugin directory under `plugins/` must contain:
  - `.claude-plugin/plugin.json`
  - `.claude-plugin/icon.png`, the directory listing icon, declared as `"icon": "./.claude-plugin/icon.png"` in `plugin.json`
  - `CHANGELOG.md`
  - `README.md`
- Every plugin icon is rendered from its own SVG source, `scripts/generators/plugin-icons/<plugin>.svg`, drawn on the shared frame of the existing sources, with no Claude, Anthropic or third-party logo. Edit the SVG and re-render; never edit the PNG.
- Every plugin must have a corresponding entry in `.claude-plugin/marketplace.json`.
- The marketplace must contain `.claude-plugin/marketplace.json`.
- The repository root must contain a generated catalog section in `README.md`.
- For every released version of every plugin there must exist:
  - a git tag named exactly `<plugin-name>--v<x.y.z>`
  - a corresponding GitHub Release with the identical name
- No draft or prerelease GitHub Releases are allowed for plugin tags.

### Name consistency
- The plugin identifier used in `plugins/<plugin-name>/` must be identical to:
  - the `name` field inside that plugin’s `.claude-plugin/plugin.json`
  - the path referenced by the corresponding entry in `.claude-plugin/marketplace.json` (`./plugins/<plugin-name>`)
  - the prefix of every git tag and GitHub Release for that plugin (`<plugin-name>--v…`)
  - the plugin name shown in the root README catalog
- Any rename must be recorded in the `renames` map of `.claude-plugin/marketplace.json` and must not leave dangling references under the old name.

### Version consistency
- The single source of truth for a plugin’s current version is the `version` field in `plugins/<plugin-name>/.claude-plugin/plugin.json`.
- `CHANGELOG.md` must:
  - contain a `## [Unreleased]` section that is empty
  - list every released version as a `## [x.y.z]` heading
  - have a set of version headings that exactly matches the set of git tags for that plugin (no missing, no extra)
  - use compare and tag links that point to the correct `<plugin-name>--v<x.y.z>` tags
- The version badge in each plugin’s `README.md` (exactly one, on line 7) must be a shields.io dynamic badge that reads `$.version` from that same plugin’s `plugin.json` on `main`.
- The marketplace (`marketplace.json`) must not store a version field; version is derived solely from each plugin’s `plugin.json`.
- The version column in the root README catalog must match the `version` in every plugin’s `plugin.json` (catalog is generated by `npm run generate` and enforced by the `generate:check` gate).
- The latest git tag of each plugin must equal the `version` currently present in that plugin’s `plugin.json` on `main`, and the `plugin.json` file at the tagged commit must contain the same version.
- Every plugin tag commit must be an ancestor of `main`.

#### Version bump policy
- **Major** (`x.0.0`): Required for any breaking change. Examples include:
  - removal or rename of a skill, agent, or command
  - rename of the plugin itself
  - change to configuration keys
  - introduction of a new mandatory dependency
  - any behavioral change that existing users rely on
- **Minor** (`x.y.0`): Required for new components, options, or capabilities that remain backward-compatible. During the `0.x` series, a Minor bump is also used for breaking changes. Any breaking-change entry in the changelog must begin with `**Breaking:**`.
- **Patch** (`x.y.z`): Required for backward-compatible bug fixes, prompt wording improvements, performance improvements, or internal refactors that preserve observable behavior.
- **No bump**: Allowed only for changes limited to a plugin’s documentation files or its in-plugin maintainer files (for example, tests or the eval suite).

### Category
- Every plugin must declare a category chosen according to its purpose, in `metadata.category` of its `.claude-plugin/plugin.json`.
- `npm run generate` copies the category into both:
  - the corresponding entry in `.claude-plugin/marketplace.json`
  - the root README catalog

### Portability and platform support
- Every plugin must be self-contained and portable. It must not depend on any machine-specific path, configuration, or environment belonging to the maintainer. Plugins are built to be installed and used by any user.
- Plugins target only Linux and macOS with POSIX-compatible interfaces. Windows is supported exclusively through Git Bash.

### Runtime and script conventions
- Every plugin that ships scripts run by command hooks must:
  - use the shebang `#!/usr/bin/env bash`, `#!/usr/bin/env python3`, or `#!/usr/bin/env node`
  - have those scripts marked executable (`chmod +x`)
- A mod's hooks module (`.ts` or `.tsx`, loaded by Claude Code) takes no shebang and no executable bit.
- Shell scripts may use only tools that ship with both macOS and Linux, unless the plugin README explicitly declares additional requirements.
- Node scripts may use only Node.js built-in modules (`node:`), unless the plugin ships its own dependencies.
- Python scripts that use the `python3` shebang may use only the Python standard library.

### README files
- A README describes what exists now: what the marketplace or the plugin is, what it contains and how to use it. Old names, merges, removed features and the steps to migrate from an earlier version go in the CHANGELOG and the release notes, never in a README.
- Each kind of README has its own rule, which loads when you edit it, and its own template:

  | File | Reader | Rule | Template |
  | :-- | :-- | :-- | :-- |
  | `README.md` at the root | Marketplace users | `.claude/rules/maintainer/root-readme.md` | `.claude/templates/root-readme-template.md` |
  | `plugins/<plugin>/README.md` | The plugin's users | `.claude/rules/plugins/plugin-readme.md` | `.claude/templates/plugin-readme-template.md` |
  | Any other README inside `plugins/<plugin>/`, such as in `tests/` or `evals/` | Users, who find it in their plugin cache | None | None |
  | Any README outside `plugins/`, such as under `scripts/testers/` | Maintainers | None | None |

- Write every user README in English, for users. Never mention this repository's maintenance, `.claude/`, scripts, CI internals or release mechanics; a user's own `.claude/settings.json` may be mentioned.
- Write user READMEs in the second person, active voice, present tense and short sentences. Use GitHub alerts (`> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`), never two back to back without text between; **bold** for UI labels exactly as the app shows them (`/plugin` → **Installed** → **Update now**) and _italics_ for emphasis or terms; relative links inside the repository and absolute `https://` links outside it.
- Check every command, flag, UI path and minimum version against the sources, in the order "Current Claude Code features, capabilities, and guidance enforcement" sets, before you write it.
- Give one fact one value everywhere: `docs/compatibility.md` is the only source of the component × surface matrix, and the marketplace is `nerymurillohnd/the-claude-factory` with the suffix `@the-claude-factory`.
- Update a plugin's README in the same change as its components, prerequisites, surfaces, configuration or minimum Claude Code version. When `docs/compatibility.md` changes, every plugin README's Compatibility cells follow it.
- A maintainer README outside `plugins/` only has to stay accurate.

### Evals
- Not every plugin is required to contain evals. The decision to include evals for a given plugin rests solely with the maintainer.
- When a plugin does contain evals:
  - A reduced smoke suite must be runnable locally.
  - The full eval suite runs in CI.
  - After a plugin has been published, CI must execute evals only for plugins that both contain evals and have been modified in the current change set. All other plugins are skipped.

### Pull request requirements
- Changes outside the `plugins/` directory do not require a pull request unless explicitly requested by the maintainer.
- Inside the `plugins/` directory:
  - Documentation-only changes (for example, updates limited to `README.md` or similar non-behavioral files) do not require a pull request.
  - Any change to components, scripts, configuration, or dependencies that alters the runtime behavior of a plugin always requires a pull request.
- Apply only labels that already exist in the repository.

## Formatting Exclusions

Biome must not format the following Markdown files. `biome.jsonc` excludes them:

- All Markdown files under `.claude/`. `biome.jsonc` lists each `.claude/` folder by name, so add a new folder there when you create it; `.claude/scheduled-tasks/` is excluded whole, from formatting and linting
- All Markdown files under `plugins/` (`plugins/**/*.md`)
- Every `CLAUDE.md` file in the repository
