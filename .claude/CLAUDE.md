# The Claude Factory

Public Claude Code plugin marketplace (`github.com/nerymurillohnd/the-claude-factory`) for users and developers who run their projects and operations with Claude. It ships plugins only, built for Claude Code and, where they apply, for the Claude app. It is built in Nery's local clone and served to users from the remote repository. Users contribute through issues.

This project also follows the guidelines and way of working in `~/.claude/CLAUDE.md` and the global cross-project lessons in `~/.claude/LESSONS.md`.

The order of work, stage by stage, is a map whose steps each name the skill or rule that governs it: @WORKFLOW.md

---

## Responsibility

- Nery and Claude Code are the only two parties responsible for this marketplace, and the only ones who work on it. There are no outside collaborators, and pull requests from users are not accepted.
- Users take part only through issues. Triaging, confirming, fixing, verifying and releasing the fix for every issue is Nery's and Claude Code's work, never the reporter's.
- No third-party team reviews our work before users install it, so every push, release and issue reply is the last check before the public: verify it before it goes out.
- Automate recurring work (validation, review, releases, drift checks, issue handling) with CI, evals, hooks, agents and scheduled tasks. Where none exists yet, propose building it.

---

## Current Claude Code features, capabilities, and guidance enforcement

Claude Code, the Claude app, the Claude models and every tool the gates run change faster than training data, recall or project docs. Before any plan, plugin component or scaffold, and before any answer about how they behave, read the current official documentation and release notes.

- When docs and release notes differ, the release notes win: docs lag releases.
- When components depend on each other, research each side. For example, a plugin hook needs the hooks reference, the plugins reference and the Claude app platform-support page.

---

## Purpose and release gate

- Goal: publish plugins that automate and optimize everyday workflows.
- One plugin covers its whole domain: knowledge, enforcement, tooling, review and proof that it works.
- Every plugin stands on its own. Design, build and document it from its own goals: what it must do, run and solve for its users. Never use how another plugin was built as a reference, pattern, justification or constraint for a new one.
- Plugins are for third parties whose setups are unknown. Every plugin works from what its README declares, never from what is installed on Nery's machine.
- A plugin is not released unless it carries `README.md`, `LICENSE` and `CHANGELOG.md` and passes the checks in Plugin Tooling.

---

## Maintainer and Plugin Scopes

This repository holds two scopes. They are never mixed: a rule written for one scope does not apply to the other, and nothing from the maintainer's environment leaks into what a plugin ships or needs.

| | Maintainer scope | Plugin scope |
| --- | --- | --- |
| **What it is** | Everything outside `plugins/`: `scripts/`, the root `package.json`, `.claude/`, `docs/`, the root `CHANGELOG.md`, `.claude-plugin/marketplace.json` | One self-contained directory per plugin under `plugins/<plugin>/` |
| **Who it serves** | Nery and Claude Code | Third parties whose setups are unknown |
| **Environment** | The tools, versions and binaries on Nery's machine | Only what the plugin's `README.md` declares as prerequisites |
| **Changes** | Pull request required only for `scripts/`; otherwise none | Pull request always |
| **Versioning** | None | Semantic Versioning per plugin |

Rules that keep the scopes apart:

- Before acting, identify the scope of every file the task touches. A task that touches both is handled as two parts, each under its own rules.
- `scripts/` (maintainer) and any scripts inside `plugins/<plugin>/` (plugin) are different things. A script inside a plugin follows the plugin rules: portable, declared prerequisites, shebang and executable bit.
- Maintainer tools may be run over plugin files to check them. That never makes them a dependency of the plugin, and a plugin never assumes them.
- Never copy a maintainer-side path, tool or version into a plugin, and never apply a plugin-side constraint (versioning, portability limits, PR requirement) to a maintainer file unless a rule below says so.

### Maintainer Tooling

- Use the tools, versions, and binaries available on the maintainer's machine.
- Python: format and lint with Ruff, type-check and diagnose with Basedpyright, test with unittest or pytest.
- Markdown, JSON, JavaScript and TypeScript: format and lint with Biome.
- Never format these Markdown files, with Biome or any other tool: every `SKILL.md`; `.claude/memory/`, `MEMORY.md` and the files it indexes; every `CLAUDE.md`; `.claude/session-handoff/`; the ADRs in `.claude/maintainer/decisions/`; the ledgers in `.claude/maintainer/technical-debt/`; `.claude/plans/`; `.claude/specs/`; `.claude/rules/`; and `.claude/templates/`. `biome.json` excludes them whenever Markdown is in its `files.includes`.
- JavaScript and TypeScript: type-check with `tsc` under the strictest settings and `--noEmit`; inspect the effective configuration with `--showConfig`.
- Shell scripts: format with `shfmt` and lint with ShellCheck.
- The root `package.json` is the manifest for repository-level JavaScript and TypeScript development tooling, not for plugin runtimes. Do not mix the two.
- Set `"private": true` in the root `package.json` to prevent accidental NPM publication.
- Retain the root NPM manifest only while repository-level tooling requires it.
- Run `npm ci` in every fresh clone and new worktree, with the `.nvmrc` Node selected.
- Existing gates that still use Mypy must be refactored to Basedpyright as they are discovered.

### Plugin Tooling

- Plugins must be self-contained and portable. They are intended for third parties and must not contain hard-coded paths or assumptions about any maintainer's machine.
- Default target platforms are Linux and macOS with POSIX-compatible interfaces.
- Windows support is optional and, when provided, must be limited to Git Bash only.
- Plugins must not depend on the maintainer's runtime tools or environment. All required tools, version constraints, binaries, and software dependencies must be declared as installation prerequisites in each plugin's `README.md`, including any feature-specific requirements.
- A plugin that needs Node packages ships its own `package.json` and a lockfile Claude Code reads in `plugins/<name>/`: a text `bun.lock`, or an npm `package-lock.json` or `npm-shrinkwrap.json` with `lockfileVersion` 2 or 3. Never `bun.lockb`, `yarn.lock` or `pnpm-lock.yaml`: Claude Code skips the install with them. It never relies on the root `package.json`, and its `README.md` declares npm or Bun as a prerequisite.
- Every plugin is validated with `claude plugin validate --strict`.
- Mod plugins are additionally tested with `claude plugin test`.
- Every plugin that ships hooks, skills, agents or scripts carries evals as its proof that it works. A plugin without such components is covered by validation alone.
- CI runs evals only for plugins that contain evals, and only when those plugins have changed; otherwise the evals are skipped.
- Executable plugin scripts (especially Claude Code hooks) must include their interpreter's shebang (`#!/usr/bin/env python3`, `#!/usr/bin/env bash`, or `#!/usr/bin/env node`), be marked executable with `chmod +x`, and have their executable permissions preserved in Git.

---

## Plugin Categories

Categories: `development`, `productivity`, `automation`, `mods`, `testing`, `security`, `documentation`, `data`, `design`, `devops`, `integrations`, `language-support`, `learning`.

- `scripts/categories.json` is the only place a category is defined: its `id`, the title and description the README catalog shows, and the catalog order. Add or change a category there first.
- Give every plugin exactly one category, chosen by its purpose, in `metadata.category` of its `plugin.json`. `node scripts/new-plugin.mjs --category <id>` sets it for a new plugin.
- Put a plugin in `mods` only when it is a mod: its `hooks/hooks.json` lists one hooks module under `modules`. A mod whose purpose is another goes in that category.
- After setting or changing a category, run `npm run generate`: it writes the category into `marketplace.json` and the README catalog. Never edit the category in either file by hand.

---

## Plugin Documentation and Changelogs

### Required files

Every plugin directory holds these files. `scripts/validators/plugin-required-files.py` fails when one of the first four is missing, is not a regular file, is a broken symlink or resolves outside the repository.

- `.claude-plugin/plugin.json`: the manifest, the only source of the plugin's name, version, description and category.
- `README.md`: the user guide.
- `CHANGELOG.md`: the plugin's full history.
- `LICENSE`.
- `NOTICE.txt`, only when the plugin bundles, derives from or wires in third-party material: the plugin's copyright and license, then each third-party source with its repository, version or commit, license and the files derived from it.

### Templates

- Create every one of those files from its template in `.claude/templates/plugin/`, never from another plugin's files. `node scripts/new-plugin.mjs` renders them for a new plugin.
- Keep every section the template defines. The README needs these sections, which `scripts/check-repo.mjs` checks: Why use it, What's inside, Requirements, Installation, Usage, Updating, Uninstalling, Compatibility, Changelog, License.
- Resolve every `<!-- TODO -->` and `<!-- TEMPLATE -->` comment before the plugin ships; `check-repo.mjs` fails while one is left.
- When a template changes, bring every plugin README built from it in line in the same change.

### README

- Requirements lists every installation prerequisite, as Plugin Tooling requires.
- Compatibility has one row per component type the plugin ships, and each cell says exactly what `docs/compatibility.md` says for that type.
- Never write a version number in the README. The badges show values that live in other files:
  - **Version**: a dynamic shields.io badge that reads `$.version` from this plugin's `plugin.json` on `main`, so a bump shows once it is merged. `plugin-versions-consistency.py` fails on a hardcoded version.
  - **Works in**: `Claude Code · Claude app` or `Claude Code only`, matching `metadata.surfaces` in `plugin.json`.
  - **Category**: the title in `scripts/categories.json` of the plugin's `metadata.category`.
  - **Claude Code**: the minimum Claude Code version, the same one Requirements states.
  - **License**: links to the plugin's `LICENSE`.
- When the surfaces, the category or the minimum Claude Code version change, update the badge, the README text that states it and the README catalog (`npm run generate`) in the same change.

### Plugin CHANGELOG.md

- It is the plugin's detailed history, written for its users: what changes for them, not how the code changed. It follows Keep a Changelog 2.0.0, with the change types `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed` and `Security`.
- Record every change under `## [Unreleased]`, referencing issues as `(#12)`. A breaking change leads its entry with `**Breaking:**`.
- `bump-version.mjs` turns `[Unreleased]` into the dated `## [X.Y.Z] - YYYY-MM-DD` section and writes its link references; it refuses an empty `[Unreleased]`.
- A change limited to the README gets no entry, because any entry requires a bump.
- `plugin-versions-consistency.py` checks that the newest section is the `plugin.json` version, that sections run newest first, and the link references.

### Root CHANGELOG.md

- It is a concise synthesis of the marketplace, never a copy of a plugin changelog. It has one line for each of these events:
  - a plugin is created;
  - a plugin gets a version bump, a patch included;
  - a plugin is renamed or removed;
  - the marketplace itself changes, for example the catalog gains a category.
- Group the lines under `## YYYY-MM-DD`, newest first, then under the Keep a Changelog change type: `### Added`, `### Changed`, `### Fixed`, `### Removed`. Use the date the change lands on `main`. If the PR is still open on a later day, move the line to that day's section before the merge.
- Write each line in the format of its event:
  - New plugin, under `### Added`: `- **<plugin>** X.Y.Z — summary.`
  - Version bump, under the change type of the change: `- **<plugin>** X.Y.Z — summary.`
  - Rename, under `### Changed`: `- **<plugin>** X.Y.Z — renamed from <old>; summary.` The `renames` map in `marketplace.json` gets `"<old>": "<plugin>"`.
  - Removal, under `### Removed`: `- **<old>** retired: reason.` The `renames` map gets `"<old>": null`.
  - Merge into another plugin, under `### Removed`: `- **<old>** retired: its <what> is now the `<skill>` skill of **<target>**, and the marketplace renames existing installs. Type `/<target>:<skill>` where you typed `/<old>:<skill>`.` The `renames` map gets `"<old>": "<target>"`.
  - Marketplace change: `- summary.`, with no plugin name or version.
- The `X.Y.Z` of a plugin line is a version that plugin's changelog has; `plugin-versions-consistency.py` fails otherwise.

---

## Versioning and Releases

Versioning applies **only to plugins**. The marketplace catalog (`.claude-plugin/marketplace.json`) is never versioned or tagged.

- Use Semantic Versioning (`MAJOR.MINOR.PATCH`). Choose the bump according to user-facing impact.
- Apply version bumps exclusively with:
  ```bash
  node scripts/bump-version.mjs <plugin> <major|minor|patch>
  ```
  Never edit version numbers by hand.
- **major** — breaking changes: removing or renaming skills, agents, or commands; changing configuration keys; introducing mandatory dependencies; or breaking behavior users rely on.
- **minor** — backward-compatible additions of components, options, or capabilities.
- **patch** — backward-compatible bug fixes, prompt wording improvements, performance improvements, or internal refactors.
- When a single PR contains mixed change levels for a plugin, apply the highest applicable bump.
- Skip the version bump **only** when a plugin's changes are limited to its `README.md`. Every other plugin change (including changelog-only changes) requires a bump.
- During the `0.x` series, treat breaking changes as `minor` and prefix the corresponding changelog entries with `**Breaking:**`.
- Never promote a plugin to `1.0.0` without Nery's explicit authorization. Reaching `1.0.0` declares interface stability.
- From `1.0.0` onward, use `major` for breaking changes.
- Write the plugin changelog entry and the root changelog line as described in Plugin Documentation and Changelogs.
- Commit the version bump, the plugin and root changelog entries, and the catalog regenerated with `node scripts/generators/catalog.mjs` as a single signed commit.
- Never push to `main` without first listing the untagged plugins (`plugin.json` version versus `git tag -l '<plugin>--v<version>'`) and confirming each is intended to ship.
- Never run `gh workflow run release.yml` while the Validate workflow is failing; resolve the failure first.

---

## Documentation and Maintenance

- `.claude/WORKFLOW.md`: the stage map, imported above.
- `.claude/maintainer/decisions/`: ADRs for important decisions.
- `.claude/maintainer/technical-debt/`: pending and closed debt.
- `.claude/memory/`: project memory (facts, feedback). Git-ignored.
- `.claude/session-handoff/`: session handoffs. Git-ignored.
- `.claude/skills/`: project skills, the procedures for work on this repository.
- `.claude/specs/`: specs, written before plans.
- `.claude/plans/`: implementation plans.
- `.claude/templates/`: templates for plugin files, the root README and the plugin review brief.
- `docs/`: the user guides, covering installation, managing plugins, compatibility, FAQ, troubleshooting and tool references.
- `plugins/`: the plugins, one self-contained directory per plugin.
- `scripts/`: maintenance scripts, tests and schemas.
- `CHANGELOG.md`: the concise project-level changelog.
- `.claude-plugin/marketplace.json`: the marketplace catalog, regenerated from `plugins/` with `node scripts/generators/marketplace.mjs`. It is never versioned or tagged.
- Keep these git-ignored in `.gitignore` and never commit them: eval results (`eval-results/` and `**/evals/results/`), `.claude/session-handoff/`, `.claude/memory/` and `.claude/settings.local.json`.

---

## Change Control

- Changes to plugin components or dependencies **require a pull request**.
- Any change inside a plugin's directory, including a `README.md`-only change, goes through a pull request. A `README.md`-only change does not require a version bump (see Versioning and Releases).
- Changes to `scripts/` **require a pull request**: they decide what is published and nobody reviews them afterwards.
- Changes to documentation and maintainer files outside plugins and `scripts/` **do not require a pull request**.
- Pull requests are opened only with Nery's explicit authorization.
- Pushes, to any branch and including tags, are made only with Nery's explicit authorization. This holds for changes that need no pull request.
- Every pull request, issue and any other item that takes labels uses only the labels already established in the repository. The one label created is `plugin: <name>`, for a new or renamed plugin, on Nery's order; the labels of retired plugins stay.
