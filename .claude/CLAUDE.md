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

This repository holds two scopes. They are never mixed: a rule written for one scope does not apply to the other, and nothing from the maintainer's environment leaks into what a plugin ships or needs. Maintainer tools may check plugin files; that never makes them a plugin dependency. Before acting, identify the scope of every file the task touches; a task that touches both is handled as two parts, each under its own rules.

| | Maintainer scope | Plugin scope |
| --- | --- | --- |
| **What it is** | Everything outside `plugins/` | One self-contained directory per plugin under `plugins/<plugin>/` |
| **Environment** | The tools, versions and binaries on Nery's machine | Only what the plugin's `README.md` declares as prerequisites |

### Maintainer Tooling

- Python: format and lint with Ruff, type-check with Basedpyright, test with unittest or pytest.
- Markdown, JSON, JavaScript and TypeScript: format and lint with Biome. A plugin's Markdown joins when the plugin next changes, as `building-plugins` step 5 says.
- Never format these Markdown files, with Biome or any other tool: every `SKILL.md`; `.claude/memory/`, `MEMORY.md` and the files it indexes; every `CLAUDE.md`; `.claude/session-handoff/`; the ADRs in `.claude/maintainer/decisions/`; the ledgers in `.claude/maintainer/technical-debt/`; `.claude/plans/`; `.claude/specs/`; and `.claude/rules/`. `biome.json` excludes them whenever Markdown is in its `files.includes`.
- JavaScript and TypeScript: type-check with `tsc` under the strictest settings and `--noEmit`.
- Shell scripts: format with `shfmt` and lint with ShellCheck.
- The root `package.json` serves repository-level development tooling only, never plugin runtimes; it stays `"private": true` and exists only while that tooling needs it.
- Run `npm ci` in every fresh clone and new worktree, with the `.nvmrc` Node selected.

### Plugin Tooling

- Target Linux and macOS with POSIX-compatible interfaces. Windows is supported only through Git Bash, and only when the plugin's README declares it.
- Write plugin Python for any `python3` a user may have; declare a minimum in the README only when a feature requires it. Type-check it with Basedpyright in its default `recommended` mode.
- Test plugin scripts under `scripts/tests/<plugin>/`; keep maintainer-only test dependencies out of plugin runtimes.

---

## Documentation and Maintenance

- `.claude/specs/`: specs, written before plans.
- `.claude/plans/`: implementation plans.
- Keep these git-ignored in `.gitignore` and never commit them: eval results (`eval-results/` and `**/evals/results/`), `.claude/session-handoff/`, `.claude/memory/` and `.claude/settings.local.json`.

---

## Change Control

- Every change inside a plugin's directory, its components, dependencies and a `README.md`-only change included, goes through a pull request. Every change outside `plugins/` does not require one.
- Release tags (`<plugin>--v<version>`) are created unsigned by `release.yml`, under the exemption `~/.claude/CLAUDE.md` gives public plugin marketplaces: users never fetch a tag, and signing in CI would put the signing key in a GitHub secret. Every commit, and every tag created locally, is still SSH-signed.
