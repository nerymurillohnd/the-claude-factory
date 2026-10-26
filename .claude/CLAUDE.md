# The Claude Factory

Public Claude Code plugin marketplace (`github.com/nerymurillohnd/the-claude-factory`) for users and developers who run projects and operations with Claude. It publishes plugins only, built for Claude Code and, where applicable, the Claude app. Development occurs in Nery’s local clone; distribution occurs from the remote repository. Users participate solely through issues.

This project follows the guidelines in `~/.claude/CLAUDE.md` and the global cross-project lessons in `~/.claude/LESSONS.md`.

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

## Maintainer and Plugin Scopes

This repository holds two scopes. They are never mixed: a rule written for one scope does not apply to the other, and nothing from the maintainer's environment leaks into what a plugin ships or needs.

| | Maintainer scope | Plugin scope |
| --- | --- | --- |
| **What it is** | Everything outside `plugins/`: `scripts/`, the root `package.json`, `.claude/`, `docs/`, the root `CHANGELOG.md`, `.claude-plugin/marketplace.json` | One self-contained directory per plugin under `plugins/<plugin>/` |
| **Who it serves** | Nery and Claude Code | Third parties whose setups are unknown |
| **Environment** | The tools, versions and binaries on Nery's machine | Only what the plugin's `README.md` declares as prerequisites |
| **Versioning** | None | Semantic Versioning per plugin |

Rules that keep the scopes apart:

- Before acting, identify the scope of every file the task touches. A task that touches both is handled as two parts, each under its own rules.
- `scripts/` (maintainer) and any scripts inside `plugins/<plugin>/` (plugin) are different things. A script inside a plugin follows the plugin rules: portable, declared prerequisites, shebang and executable bit.
- Maintainer tools may be run over plugin files to check them. That never makes them a dependency of the plugin, and a plugin never assumes them.
- Never copy a maintainer-side path, tool or version into a plugin, and never apply a plugin-side constraint (versioning, portability limits) to a maintainer file unless a rule below says so.

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

- Default target platforms are Linux and macOS with POSIX-compatible interfaces.
- Windows support is optional and, when provided, must be limited to Git Bash only, and only when the plugin's README declares Windows support.
- Run plugin Python with the user's `python3` from `PATH`; never rely on the maintainer's uv, PEP 723 execution or the maintainer's Python version.
- Write plugin Python for any `python3` a user may have; declare a minimum in the README only when a feature requires it.
- Type-check plugin Python with Basedpyright in its default `recommended` mode.
- Test plugin scripts with their own tests under `scripts/tests/<plugin>/`; keep maintainer-only test dependencies out of plugin runtimes.

## Plugin Categories

Categories: `development`, `productivity`, `automation`, `mods`, `testing`, `security`, `documentation`, `data`, `design`, `devops`, `integrations`, `language-support`, `learning`.

- `scripts/categories.json` is the only place a category is defined: its `id`, the title and description the README catalog shows, and the catalog order. Add or change a category there first.
- Give every plugin exactly one category, chosen by its purpose, in `metadata.category` of its `plugin.json`. The `building-plugins` skill's scaffold sets it for a new plugin.
- Put a plugin in `mods` only when it is a mod: its `hooks/hooks.json` lists one hooks module under `modules`. A mod whose purpose is another goes in that category.
- After setting or changing a category, run `npm run generate`: it writes the category into `marketplace.json` and the README catalog. Never edit the category in either file by hand.

---

## Plugin Documentation and Changelogs

### Required files

- Every plugin directory holds `.claude-plugin/plugin.json`, `README.md`, `CHANGELOG.md` and `LICENSE`. `scripts/validators/plugin-required-files.py` fails when one is missing, is not a regular file, is a broken symlink or resolves outside the repository.
- `plugin.json` is the only source of the plugin's name, version, description and category.
- Third-party material goes in `NOTICE.txt`, which opens with the plugin's own copyright and license and names, for each source, the files derived from it.

### Templates

- Create every one of those files with the `building-plugins` skill's scaffold, from that skill's assets, never from another plugin's files. `.claude/templates/plugin/` holds the older templates, frozen until DEBT-011 closes: never edit them or create a plugin from them.
- Keep every section the template defines. The README needs these sections, which `scripts/check-repo.mjs` checks: Why use it, What's inside, Requirements, Installation, Usage, Updating, Uninstalling, Compatibility, Changelog, License.
- Resolve every `<!-- TODO -->` and `<!-- TEMPLATE -->` comment before the plugin ships; `check-repo.mjs` fails while one is left.
- When a template changes, bring every plugin README built from it in line in the same change.

### README

- Requirements also states each version constraint, and the prerequisites of any single feature.
- Compatibility has one row per component type the plugin ships, and each cell says exactly what `docs/compatibility.md` says for that type.
- Never write a version number in the README, except, for a plugin with a mod, the Claude Code version it was tested with, in Compatibility (the `building-mods` skill). The badges show values that live in other files:
  - **Version**: a dynamic shields.io badge that reads `$.version` from this plugin's `plugin.json` on `main`, so a bump shows once it is merged. `plugin-versions-consistency.py` fails on a hardcoded version.
  - **Works in**: `Claude Code · Claude app` or `Claude Code only`, matching `metadata.surfaces` in `plugin.json`.
  - **Category**: the title in `scripts/categories.json` of the plugin's `metadata.category`.
  - **Claude Code**: the minimum Claude Code version, the same one Requirements states.
  - **License**: links to the plugin's `LICENSE`.
- When the surfaces, the category or the minimum Claude Code version change, update the badge, the README text that states it and the README catalog (`npm run generate`) in the same change.

### Plugin CHANGELOG.md

- `plugin-versions-consistency.py` checks that the newest section is the `plugin.json` version, that sections run newest first, and the link references.

### Root CHANGELOG.md

- The `X.Y.Z` of a plugin line is a version that plugin's changelog has; `plugin-versions-consistency.py` fails otherwise.

---

## Documentation and Maintenance

- `.claude/rules/workflow.md`: the workflow rules, which name the skill each stage loads.
- `.claude/maintainer/decisions/`: ADRs for important decisions.
- `.claude/maintainer/technical-debt/`: pending and closed debt.
- `.claude/memory/`: project memory (facts, feedback). Git-ignored.
- `.claude/session-handoff/`: session handoffs. Git-ignored.
- `.claude/skills/`: project skills, the procedures for work on this repository.
- `.claude/specs/`: specs, written before plans.
- `.claude/plans/`: implementation plans.
- `.claude/templates/`: the older plugin and root README templates, frozen until DEBT-011 closes.
- `docs/`: the user guides, covering installation, managing plugins, compatibility, FAQ, troubleshooting and tool references.
- `plugins/`: the plugins, one self-contained directory per plugin.
- `scripts/`: maintenance scripts, tests and schemas.
- `CHANGELOG.md`: the concise project-level changelog.
- `.claude-plugin/marketplace.json`: the marketplace catalog, regenerated from `plugins/` with `node scripts/generators/marketplace.mjs`. It is never versioned or tagged.
- Keep these git-ignored in `.gitignore` and never commit them: eval results (`eval-results/` and `**/evals/results/`), `.claude/session-handoff/`, `.claude/memory/` and `.claude/settings.local.json`.

---

## Change Control

- Every change inside a plugin's directory, its components, dependencies and a `README.md`-only change included, goes through a pull request. A `README.md`-only change does not require a version bump (see the `release-and-versioning` skill).
- Every change outside `plugins/` does not require a pull request.
- Pushes, to any branch and including tags, are made only with Nery's explicit authorization.
- Release tags (`<plugin>--v<version>`) are created unsigned by `release.yml`, under the exemption `~/.claude/CLAUDE.md` gives public plugin marketplaces: users never fetch a tag, and signing in CI would put the signing key in a GitHub secret. Every commit, and every tag created locally, is still SSH-signed.
- Every item that takes labels, issues included, uses only the labels already established in the repository. The one label created is `plugin: <name>`, for a new or renamed plugin, on Nery's order; the labels of retired plugins stay.
