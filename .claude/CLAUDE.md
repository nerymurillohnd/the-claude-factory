# The Claude Factory

Public Claude Code plugin marketplace (`github.com/nerymurillohnd/the-claude-factory`) for users and developers who run projects and operations with Claude. It publishes plugins only, built for Claude Code and, where applicable, the Claude app. Development occurs in Nery’s local clone; distribution occurs from the remote repository. Users participate solely through issues.

## Purpose

Publish plugins that automate and optimize everyday workflows.

- Design, build, and document every plugin solely from its own goals: what it must do, execute, and solve for its users. Never treat another plugin’s implementation as a reference, pattern, justification, or constraint.

## Responsibility

This marketplace is public. Published plugins execute on other people’s machines, inside their projects and operations. Nery is the sole owner and author and remains personally accountable for any harm a plugin causes a user, however minor.

- Nery and Claude Code are the only parties responsible for this marketplace and the only parties who work on it. There are no external collaborators.
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
- `scripts/`: Maintainer scripts that build, check, and release this repository.
- `plugins/`: The plugins that are developed, published, and maintained in this repository.
- `docs/`: Reference documentation and repository information intended for users and third parties.
- `.claude-plugin/marketplace.json`: The marketplace manifest.

## Commands

Run Biome and `tsc` only through `npm run`, which uses the versions `package-lock.json` pins; never by bare name. Ruff, Basedpyright, shfmt, ShellCheck and actionlint may run directly to check one file, but `npm run gates` is the verdict: it holds each tool's scope and flags, as CI and Husky run them.

- Use `npm install`, with the `.nvmrc` Node selected, to install the maintainer tools.
- Use `npm run format` to format Markdown, JSON, YAML, JavaScript and TypeScript with Biome, Python with Ruff and shell scripts with shfmt.
- Use `npm run lint` to lint with Biome, Ruff, ShellCheck and actionlint.
- Use `npm run fix` to apply the formatters' and linters' safe fixes.
- Use `npm run typecheck` to type-check TypeScript with `tsc` (strictest settings, `--noEmit`) and Python with Basedpyright.
- Use `npm test` to run the maintainer tests (`node --test` and unittest), and `npm run test:plugins` for the plugins' tests.
- Use `npm run validate` to run the validators in `scripts/validators/`.
- Use `npm run generate` to rebuild `marketplace.json` and the README catalog, and `npm run generate:check` to confirm they are current.
- Use `npm run gates` to run every gate, as the pre-push hook does.
- Use `claude plugin validate` and `claude plugin test` to check a mod's hooks module; no gate type-checks it against `.claude-plugin/types/`.
- `format` and `fix` also write in `plugins/`.
- Husky runs `biome check --staged` and `npm test` before each commit and `npm run gates` before each push. The Claude Code hooks in `.claude/settings.json` check commits and `SKILL.md` writes. Fix what they report; never skip them.

## Change Control

- Release tags are created unsigned by `release.yml`, as this project's exception to the global signing rule: signing in CI would put the signing key in a GitHub secret. Users' Claude Code resolves dependency version ranges against these tags by name, without verifying signatures. Every commit, and every tag created locally, is still SSH-signed.

## How To Work in this Project


### Required existence
- Every plugin directory under `plugins/` must contain:
  - `.claude-plugin/plugin.json`
  - `CHANGELOG.md`
  - `README.md`
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

### README content requirements
- Every `README.md` in the repository must be written in English and addressed to end users. It must not mention maintainer tasks, internal processes, or reminders.
- Every plugin `README.md` must declare:
  - prerequisites (when Python is required, it must be stated as Python 3.12 or later)
  - how to install the prerequisites
  - how to add and remove the marketplace
  - how to install, update, and uninstall the plugin
  - the platform support policy (Linux and macOS primary; Windows only via Git Bash)
  - every external program invoked by the plugin’s hooks or scripts, each accompanied by a command that verifies its presence

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

- All Markdown files under `.claude/`
- All Markdown files under `plugins/` (`plugins/**/*.md`)
- Every `CLAUDE.md` file in the repository
