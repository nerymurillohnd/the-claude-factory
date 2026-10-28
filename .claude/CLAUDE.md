# The Claude Factory

Public Claude Code plugin marketplace (`github.com/nerymurillohnd/the-claude-factory`) for users and developers who run projects and operations with Claude. It publishes plugins only, built for Claude Code and, where applicable, the Claude app. Development occurs in Nery’s local clone; distribution occurs from the remote repository. Users participate solely through issues.

This project follows the guidelines in `~/.claude/CLAUDE.md` and the global cross-project lessons in `@~/.claude/LESSONS.md`.

## Purpose

Publish plugins that automate and optimize everyday workflows.

- Every plugin is self-contained. Design, build, and document it solely from its own goals: what it must do, execute, and solve for its users. Never treat another plugin’s implementation as a reference, pattern, justification, or constraint.
- Plugins target third parties whose environments are unknown. Each plugin operates exclusively from the declarations in its README, never from software or configuration present on Nery’s machine.

## Responsibility

This marketplace is public. Published plugins execute on other people’s machines, inside their projects and operations. Nery is the sole owner and author and remains personally accountable for any harm a plugin causes a user, however minor.

- Nery and Claude Code are the only parties responsible for this marketplace and the only parties who work on it. There are no external collaborators.
- Users contribute only by opening issues. Triaging, confirming, fixing, verifying, and releasing every fix is the exclusive work of Nery and Claude Code; the reporter has no further obligation.
- No third-party review occurs before users install a plugin. Every push, release, and issue reply is the final gate before public exposure.

## Operating Standard

This standard applies to every session on this repository, including the current one:

- Ship nothing that has not been verified against current Claude Code official documentation and the latest release notes. Out-of-date knowledge or negligence that reaches a user constitutes the failure this project exists to prevent.
- Treat every action a plugin performs on a user’s machine (files, commands, network, hooks, permissions, data) as high-risk. Prefer the least invasive design and require the README to state exactly what the plugin does on the host.
- When safety for users cannot be determined with certainty, state the uncertainty and obtain Nery’s explicit approval before shipping. Never publish on a guess.
- Report problems immediately upon discovery, including one’s own errors and defects in already-published work.
- Improve the working system, not only the delivered artifacts. When a session reveals a gap in this file, a rule, a gate, or a skill, propose the corrective change in the same session.
- Automate recurring work (validation, review, releases, drift detection, issue handling) through CI, evals, hooks, agents, and scheduled tasks. Where no automation yet exists, propose its construction.

## Current Claude Code features, capabilities, and guidance enforcement

Claude Code, the Claude app, the Claude models and every tool the gates run change faster than training data, recall or project docs. Before any plan, plugin component or scaffold, and before any answer about how they behave, read the current official documentation and release notes.

- When docs and release notes differ, the release notes win: docs lag releases.
- When components depend on each other, research each side. For example, a plugin hook needs the hooks reference, the plugins reference and the Claude app platform-support page.

## Workflow

This section is the contract of the work on this project: the scope every file belongs to, where the working files live, and each stage with the skill that owns it and its key jobs. The procedure of each stage lives in its skill; never copy it here. Depending on the context, resume the work from the stage it belongs to, and apply its skill to what is already built. The scope and working-file rules apply to every stage.

1. Maintainer and Plugin Scopes
2. Working Files
3. Management, Maintenance and Quality Gates
4. Marketplace Plugins

### Maintainer and Plugin Scopes

This repository holds two scopes. They are never mixed: a rule written for one scope does not apply to the other, and nothing from the maintainer's environment leaks into what a plugin ships or needs. Maintainer tools may check plugin files; that never makes them a plugin dependency. Before acting, identify the scope of every file the task touches; a task that touches both is handled as two parts, each under its own rules.

- **Maintainer scope**: everything outside `plugins/`. Its environment is the tools, versions and binaries on Nery's machine.
- **Plugin scope**: one self-contained directory per plugin under `plugins/<plugin>/`. Its environment is only what the plugin's `README.md` declares as prerequisites.

Pull requests and version bumps (this is the only place that sets them):

- **A plugin's documentation alone** (`README.md`, `LICENSE`, `NOTICE.txt`): commit it signed straight to `main`, with no pull request, version bump or `CHANGELOG.md` entry, because it changes nothing the plugin does. GitHub shows it on push; installed copies keep the old text until the plugin's next version.
- **Every other file inside a plugin's directory** (its manifest, components, scripts, dependencies, `CHANGELOG.md`): a pull request and a version bump, through `release-and-versioning`.
- **Everything outside `plugins/`**: no pull request.

#### Maintainer Tooling

- Python: format and lint with Ruff, type-check with Basedpyright, test with unittest or pytest.
- Markdown, JSON, YAML, JavaScript and TypeScript: format and lint with Biome.
- Never format these Markdown files, with Biome or any other tool: every Markdown file under `plugins/`, `.claude/skills/`, `.claude/memory/`, `.claude/session-handoff/`, `.claude/maintainer/`, `.claude/plans/`, `.claude/specs/` and `.claude/rules/`; `MEMORY.md` and the files it indexes; and every `CLAUDE.md`. `biome.jsonc` excludes them whenever Markdown is in its `files.includes`.
- Every tool covers the whole repository except `node_modules/`, `.github/` and the files above (the CI gates leave out `plugins/`, which the local gates cover); run at the root, each reads that scope from its own config (`biome.jsonc`, `ruff.toml`, `pyrightconfig.json`, `.editorconfig` for shfmt). Basedpyright always skips dot folders, so `.claude/skills/pyrightconfig.json` covers the skills' Python, and `scripts/basedpyright-maintainer.mjs` checks each PEP 723 script against its own environment.
- JavaScript and TypeScript: type-check with `tsc` under the strictest settings and `--noEmit`.
- Shell scripts: format with `shfmt` and lint with ShellCheck.
- Navigate and explore code with the LSP tool, in every file of the repository, plugin files included, and follow the skill for its language: Python with `python-lsp-intelligence:python-lsp-intelligence`; JavaScript and TypeScript with `typescript6-lsp-intelligence:ts-lifecycle`; shell scripts with `bash-lsp-intelligence:bash-lsp-intelligence`.
- Tests of plugin scripts live in `scripts/testers/<plugin>/`, which is maintainer scope: their test dependencies never enter a plugin's runtime.
- The root `package.json` serves repository-level development tooling only, never plugin runtimes; it stays `"private": true`. Its devDependencies are the npm tools (Biome, TypeScript, Husky) and the `@types/*` packages, each pinned to an exact version.
- A plugin's own `package.json` and `package-lock.json` hold only that plugin's runtime dependencies, pinned exactly; Claude Code installs them for users when it caches the plugin. `npm run setup` installs them in the clone, which `tsc-plugins` and the plugin's node tests need.
- Every maintenance command is an `npm run` script (`test`, `typecheck`, `lint`, `format`, `fix`, `check:*`, `generate`, `validate`, `gates`, `setup`): run the tools through them, so local runs, the git hooks and CI use the pinned versions. In this repository that overrides running a tool by its bare name from PATH; the global installs serve the editor. `format` and `fix` also write in `plugins/`: a plugin file they change goes through a pull request.
- Husky's git hooks run `biome check --staged` and `npm test` before each commit and `npm run gates` before each push; fix what they report, never skip them.
- Run `npm ci` in every fresh clone and new worktree, with the `.nvmrc` Node selected.

#### Plugin Tooling

- Target Linux and macOS with POSIX-compatible interfaces. Windows is supported only through Git Bash, and only when the plugin's README declares it.
- Write plugin Python for `python3` 3.12 or later, and state that minimum in the README of every plugin that runs Python. Ruff (`per-file-target-version` in `ruff.toml`) and Basedpyright (the `plugins` execution environment in `pyrightconfig.json`) check it against 3.12; Basedpyright runs in `all` mode, as `pyrightconfig.json` sets for the whole repository.

### Working Files

- `.claude/specs/`: specs, written before plans.
- `.claude/plans/`: implementation plans.
- Keep these git-ignored in `.gitignore` and never commit them: eval results (`eval-results/` and `**/evals/results/`), `.claude/plans/`, `.claude/session-handoff/`, `.claude/memory/` and `.claude/settings.local.json`.

### Management, Maintenance and Quality Gates

1. Decision records
   - When: Nery makes an important decision.
   - Skill: `project-maintainer:write-records`.
   - Key jobs: write the ADR.
2. Pending and resolved tasks
   - When: an idea, task or conflict resolution cannot be carried out, or a logged item is withdrawn, completed or closed.
   - Skill: `project-maintainer:write-records`.
   - Key jobs: log the pending item; record its closure.
3. User documentation
   - When: the marketplace's own user documentation is written, updated or checked.
   - Skill: `maintaining-user-docs`.
   - Key jobs: keep the docs true to the current Claude Code release and the marketplace.
4. Issue handling and resolution
   - Skill: none yet; ask Nery.
   - Key jobs: label each issue only with the labels the repository already has.
5. Local quality gates
   - Skill: none yet; ask Nery.
   - Key jobs: check each changed file with the tooling of its scope (Maintainer and Plugin Scopes).
6. Remote quality gates
   - Skill: none yet; ask Nery.

### Marketplace Plugins

1. Plugin design and planning
   - Skill: none yet; ask Nery.
   - Key jobs: write the spec, then the plan, where Working Files says.
2. Plugin creation
   - When: a plugin is created, scaffolded, written or fixed.
   - Skills: `building-plugins`; also `building-mods` when the plugin is a mod or contains one.
   - Key jobs:
     - Settle the identity with Nery: name, category (with `plugin-categories`), description, display name and surfaces.
     - Create the plugin and register it in the marketplace.
     - Write the components from the current official docs.
     - Make it public-ready: README, host disclosures, `LICENSE`, `CHANGELOG.md`, third-party notice when it applies.
     - Validate it.
3. Plugin categories
   - When: a new plugin needs its category, a plugin's category changes, a plugin gains or loses a mod, or `scripts/categories.json` changes.
   - Skill: `plugin-categories`.
   - Key jobs:
     - Give every plugin one category, chosen by its purpose.
     - Keep `scripts/categories.json` the only definition, and `metadata.category` the only place a plugin's category is set.
     - Regenerate the marketplace and the catalog after every change.
4. Plugin testing and evaluation
   - When: evals are requested, a ready plugin has MCP servers or MCP hooks, a mod is tested, or an install, load or marketplace error needs diagnosing.
   - Skills: `testing-plugins`; `testing-mods` for a mod's own tests and troubleshooting.
   - Key jobs:
     - Build and run eval suites, only when asked.
     - Run the live MCP checks once Nery says the plugin is ready.
     - Run a mod's own tests.
     - Diagnose install, load and marketplace errors.
5. Versioning and releases
   - When: a new plugin is published, or an existing plugin has changed.
   - Skill: `release-and-versioning`.
   - Key jobs:
     - Choose the version and write the release notes.
     - Check the release before the merge.
     - Confirm what users receive after the merge.
6. Plugin renames and removals
   - When: a plugin is to be renamed, merged into another, removed, retired or deprecated.
   - Skill: `plugin-renames-and-removals`.
   - Key jobs: migrate existing installs through the marketplace's `renames` map, and ship a rename as a breaking change.

## Change Control

- Release tags (`<plugin>--v<version>`) are created unsigned by `release.yml`, under the exemption `~/.claude/CLAUDE.md` gives public plugin marketplaces: users never fetch a tag, and signing in CI would put the signing key in a GitHub secret. Every commit, and every tag created locally, is still SSH-signed.
