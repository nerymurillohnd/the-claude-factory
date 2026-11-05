# The Claude Factory

Public Claude Code plugin marketplace (`github.com/nerymurillohnd/the-claude-factory`) for users and developers who run projects and operations with Claude. It publishes plugins only, built for Claude Code and, where applicable, the Claude app. Development occurs in Nery’s local clone; distribution occurs from the remote repository. Users participate solely through issues.

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
- Never format these Markdown files with any tool: everything under `plugins/`, `.claude/skills/`, `.claude/memory/`, `.claude/session-handoff/`, `.claude/maintainer/`, `.claude/plans/`, `.claude/specs/` and `.claude/rules/`; `MEMORY.md` and the files it indexes; every `CLAUDE.md`. `biome.jsonc` excludes them.
- Every tool skips `node_modules/`, `.github/` and those files, and reads its scope from its own config (`biome.jsonc`, `ruff.toml`, `pyrightconfig.json`, `.editorconfig` for shfmt).
- Basedpyright skips dot folders: `.claude/skills/pyrightconfig.json` covers the skills' Python, and `scripts/basedpyright-maintainer.mjs` checks each PEP 723 script in its own environment.
- CI checks the plugins' structure only; the local gates cover the analysis and tests of plugin code.
- Husky runs `biome check --staged` and `npm test` before each commit and `npm run gates` before each push. The Claude Code hooks in `.claude/settings.json` check commits and `SKILL.md` writes. Fix what they report; never skip them.
- Navigate code with the LSP tool and the skill for its language: `python-lsp-intelligence:python-lsp-intelligence`, `typescript6-lsp-intelligence:ts-lifecycle`, `bash-lsp-intelligence:bash-lsp-intelligence`. They come from this marketplace's LSP plugins, which `.claude/settings.json` enables. Without the LSP tool, say so and use Grep and Read.

## Change Control

- Release tags (`<plugin>--v<version>`) are created unsigned by `release.yml`, as this project's exception to the global signing rule: signing in CI would put the signing key in a GitHub secret. Users' Claude Code resolves dependency version ranges against these tags by name, without verifying signatures. Every commit, and every tag created locally, is still SSH-signed.
