# Changelog

All notable changes to **The Claude Factory** marketplace are documented here: plugins added, updated, renamed or retired, and changes to the catalog itself. Each plugin keeps its own detailed changelog in `plugins/<name>/CHANGELOG.md`.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/). The marketplace has no version of its own: entries are grouped by date, newest first, and every plugin carries its own version, changelog and tag. The versions 0.1.0 and 0.2.0 below are the history from before that change; their tags stay.

## 2026-10-29

### Changed

- **github-operations** 0.5.0 — **Breaking:** one `github` skill replaces the PR and cleanup skills and adds PR, issue and discussion writing, CI repair and repository setup; hooks keep its reviewer agents read-only.
- **mods-engineering** 0.1.2 — says which sessions write a mod's type declarations, what a type check, validate and test prove, and to declare the minimum Claude Code version and keep generated files out of a published plugin.
- **plugin-evals** 0.1.3 — warns that a committed eval suite ships in every user's copy, so its fixtures and replays must hold no secrets.

### Fixed

- **hook-engineering** 0.2.2 — a Setup hook note names the declarations file Claude Code writes into a mod.
- **hook-engineering** 0.2.3 — the event references drop dated observations; the Setup note becomes a check you run on your own build.

### Removed

- **file-tree-pane** 0.1.4 — a development `tsconfig.json` that shipped by mistake; nothing changes in how the mod works.
- **macos-grep-guard** 0.1.1 — a development `tsconfig.json` that shipped by mistake; nothing changes in how the mod works.
- **model-trace** 0.1.2 — a development `tsconfig.json` that shipped by mistake; nothing changes in how the mod works.
- **project-maintainer** 0.2.4 — a development `tsconfig.json` that shipped by mistake; nothing changes in how the plugin works.
- **tool-ledger** 0.1.3 — a development `tsconfig.json` that shipped by mistake; nothing changes in how the mod works.
- **turn-meter** 0.1.3 — a development `tsconfig.json` that shipped by mistake; nothing changes in how the mod works.

## 2026-10-28

### Fixed

- **model-trace** 0.1.1 — rows in a narrow pane, such as the desktop app's side panel, keep the whole name, and section titles count the same uses as the header, with hook output named apart.

### Changed

- **tailwind-development** 0.3.1 — the bundled MCP server script is executable, as its shebang declares; Claude Code still starts it with `node`.
- **project-maintainer** 0.2.3 — the handoff and records skills keep to the current project, check for evidence that an item is already done before listing it, and cite only installed skills, agents and plugins.

### Added

- **instruction-engineering** 0.1.0 — writes, audits and refactors CLAUDE.md, CLAUDE.local.md and `.claude/rules` against the current loading rules: it reads the whole instruction set before any change, reports contradictions, duplicates and lines that change nothing, places each instruction where it loads when needed, and ships a read-only checker and an independent reviewer agent.
- **model-trace** 0.1.0 — a pane that shows, as Claude works, each skill, agent, MCP server, plugin, hook and web tool it uses in the session, how many times and at what time, with an export to Markdown or HTML.
- **macos-grep-guard** 0.1.0 — on macOS, stops a recursive `grep` until the command says whether gitignored and binary files count, stops `awk` programs that rely on `IGNORECASE`, and gives Claude the macOS form when a BSD or zsh command fails.
- **tailwind-development** 0.3.0 — four agents for docs research, audits, refactors and v3 to v4 migration; the docs skill becomes the first source for any Tailwind task, routed by docs category; and a link check of the docs skill before Claude delegates to an agent.

## 2026-10-27

### Added

- **tailwind-development** 0.2.0 — after every file Claude edits or writes, the official Tailwind CSS language server checks its classes through a bundled MCP server and hands Claude each conflict, non-canonical class and invalid `theme()` path with the exact fix; four read-only tools and per-file-type options.
- **tailwind-development** 0.1.0 — designs, builds, refactors and reviews Tailwind CSS v4 interfaces with a product designer's craft, grounds every utility, variant and configuration in its exact official documentation page for the Tailwind version your project resolves, and verifies the result in your project.

### Changed

- **bash-lsp-intelligence** 0.2.5 — the post-edit hook always runs through Bash, and the README states one minimum Claude Code version.
- **file-tree-pane** 0.1.3 — internal code-quality refactor for stricter lint rules; nothing changes in what the pane shows or does.
- **file-tree-pane** 0.1.2 — internal code and test cleanups from stricter lint rules; nothing changes for users.
- **project-maintainer** 0.2.2 — the start-of-session hook runs through Bash explicitly; internal guardrail cleanups with no change in what they decide.
- **python-lsp-intelligence** 0.3.0 — the post-edit hook requires Python 3.12 or later and always runs through Bash.
- **skill-diagnostics** 0.2.0 — the hook requires Python 3.12 or later and runs as `python3` through Bash.
- **tailwind-development** 0.2.1 — the checks ask the language server for fixes and class CSS in parallel; internal cleanup from stricter lint rules, with the same answers.
- **tool-ledger** 0.1.2 — internal code cleanup from stricter lint rules; nothing changes for users.
- **turn-meter** 0.1.2 — internal code cleanup from a stricter lint rule; nothing changes for users.

### Fixed

- **tailwind-development** 0.2.2 — a Tailwind CSS v3 to v4 migration runs the official upgrade tool and checks every breaking change of the upgrade guide against the project, instead of only the removed and renamed utilities.

## 2026-10-26

### Fixed

- **block-no-verify** 0.1.3 — a hook-script comment no longer says a timed-out hook lets the command through; nothing changes for users.

## 2026-10-24

### Changed

- 🧩 The catalog has a Mods category for plugins that change Claude Code's own interface: **tool-ledger** and **turn-meter** move there from Productivity.
- **bash-lsp-intelligence** 0.2.4 — its catalog category now lives in its manifest; nothing changes for users.
- **block-no-verify** 0.1.2 — its catalog category now lives in its manifest; nothing changes for users.
- **file-tree-pane** 0.1.1 — its catalog category now lives in its manifest; nothing changes for users.
- **github-operations** 0.4.1 — its catalog category now lives in its manifest; nothing changes for users.
- **hook-engineering** 0.2.1 — its catalog category now lives in its manifest; nothing changes for users.
- **mods-engineering** 0.1.1 — its catalog category now lives in its manifest; nothing changes for users.
- **plugin-evals** 0.1.2 — its catalog category now lives in its manifest; nothing changes for users.
- **plugin-test-bench** 0.1.1 — its catalog category now lives in its manifest; nothing changes for users.
- **project-maintainer** 0.2.1 — its catalog category now lives in its manifest; nothing changes for users.
- **prompt-writer** 0.2.1 — its catalog category now lives in its manifest; nothing changes for users.
- **python-lsp-intelligence** 0.2.3 — its catalog category now lives in its manifest; nothing changes for users.
- **skill-diagnostics** 0.1.3 — its catalog category now lives in its manifest; nothing changes for users.
- **svelte-development** 0.1.1 — its catalog category now lives in its manifest; nothing changes for users.
- **tool-ledger** 0.1.1 — its catalog category now lives in its manifest; nothing changes for users.
- **turn-meter** 0.1.1 — its catalog category now lives in its manifest; nothing changes for users.
- **typescript6-lsp-intelligence** 0.3.1 — its catalog category now lives in its manifest; nothing changes for users.
- **typescript7-lsp-intelligence** 0.4.1 — its catalog category now lives in its manifest; nothing changes for users.

## 2026-10-23

### Added

- **file-tree-pane** 0.1.0 — keeps a live file tree of your project beside the chat: git status and line counts, what Claude reads, writes and commits, search, previews, diffs and your editor one key away.

## 2026-10-22

### Added

- **mods-engineering** 0.1.0 — designs, builds, reviews, tests and debugs Claude Code mods, checking every interface against the current mod docs and the type declarations your own Claude Code build writes.
- **turn-meter** 0.1.0 — shows how long each turn took, its tool calls in the main thread and in subagents, and the tokens it spent, in a band above the prompt, and alerts you when a long turn ends.
- **tool-ledger** 0.1.0 — lists every tool call of the session in a live panel: what ran, on what, whether Claude or a subagent made it, and whether it finished, failed or was denied.

### Changed

- **project-maintainer** 0.2.0 — **Breaking:** requires Claude Code v2.1.307 or later, which puts every guardrail prompt to you with no classifier able to answer it; a broken check now fails closed for the records only, and the README says what each piece does and prevents and how to check that the guardrails run.
- **hook-engineering** 0.2.0 — **Breaking:** the Claude Code docs server is no longer bundled: add it once with `claude mcp add` or as a Claude app connector; the `hook-engineer` agent now uses it under any name, and without it the plugin reads the raw docs pages.
- **typescript6-lsp-intelligence** 0.3.0 — the post-edit hook treats its strictest policy as defaults your config overrides (breaking: an explicit `false` is now yours), keeps the policy inside the hook with no environment of its own, passes each option only to a `tsc` that knows it, reports deprecated config options, and finds Bash changes in worktrees and files only a sibling `tsconfig.<name>.json` lists.
- **typescript7-lsp-intelligence** 0.4.0 — the post-edit hook treats its strictest policy as defaults your config overrides (breaking: an explicit `false` is now yours), keeps the policy inside the hook with no environment of its own, passes each option only to a `tsc` that knows it, reports deprecated config options, and finds Bash changes in worktrees and files only a sibling `tsconfig.<name>.json` lists.
- 🧭 The compatibility matrix lists mods: they run in every Claude Code session except a Desktop session on WSL, and the Claude app's plugin directory lists them for Claude Code only.
- 🩺 The troubleshooting guide explains why a plugin from the Claude app can be missing in Claude Code, and the management guide shows how to keep synced plugins out, one at a time, per project or all at once.

### Fixed

- **block-no-verify** 0.1.1 — the hook's description sits where Claude Code documents it, so the claude.ai sync stops warning about it; blocking is unchanged.

## 2026-10-21

### Added

- **hook-engineering** 0.1.0 — designs, writes, audits and debugs Claude Code hooks end to end, checking each answer against the current docs and the changelog for your Claude Code version.

### Changed

- **github-operations** 0.4.0 — **Breaking:** `git-cleanup` becomes an exhaustive audit with two approval gates and drops its guard hook and the Python requirement; `pr-tracker` now finds your GitHub tools under any server name, a Claude app connector included, waits for checks to finish before it reports, and also checks runners, the base branch, breaking changes and secrets in the diff.

## 2026-10-20

### Added

- **block-no-verify** 0.1.0 — denies Claude's git commands that skip commit hooks or signing (`--no-verify`, `--no-gpg-sign`, `commit.gpgsign=false`), so your quality gates always run.

### Changed

- **bash-lsp-intelligence** 0.2.3 — hook messages to Claude name the skill to use.
- **bash-lsp-intelligence** 0.2.2 — version bump only, behavior unchanged from 0.2.1.
- **typescript7-lsp-intelligence** 0.3.1 — hook messages to Claude name the skill to invoke.
- **python-lsp-intelligence** 0.2.2 — hook messages to Claude name the skill to invoke.
- **typescript6-lsp-intelligence** 0.2.1 — hook messages to Claude name the skill to invoke.

## 2026-10-19

### Added

- **svelte-development** 0.1.0 — writes, reviews and migrates Svelte 5 and SvelteKit 3 code from the official docs, checks every Svelte file with the Svelte autofixer and proves changes with the Svelte language server and your project's `svelte-check`.
- **project-maintainer** 0.1.0 — records a project's important decisions as ADRs, tracks the technical debt it cannot fix yet and closes it as resolved, obsolete or accepted, carries each session's state to the next one in a handoff, and guards the records so Claude asks before it rewrites a settled one.

### Removed

- **session-handoff** retired: its handoff is now the `write-handoff` skill of **project-maintainer**, and the marketplace renames existing installs. Type `/project-maintainer:write-handoff` where you typed `/session-handoff:write-handoff`. Handoffs already saved in `.claude/session-handoff/` keep working.

### Changed

- **session-handoff** 1.0.0 — **Breaking:** a six-section handoff written in a plain seven-step flow, and a start-of-session hook that works from it as background
- **github-operations** 0.3.2 — the `pr-tracker` instructions are organized in short modules with a role, mission and rules, and the GitHub MCP tool reference is trimmed to what the PR skill needs

## 2026-10-18

### Changed

- **github-operations** 0.3.1 — the `pr-tracker` agent writes every report in one fixed template, led by an eight-line summary; the README shows how to connect the GitHub server in the Claude app with your token.
- **github-operations** 0.3.0 — **Breaking:** the internal `pr-diagnostics` skill is folded into the `pr-tracker` agent, whose reports now lead with a summary, flag outside blockers as `BLOCKED` and re-read everything each round; the README shows how to set the token for a plugin turned on in claude.ai.
- **github-operations** 0.2.0 — **Breaking:** the GitHub token is now a sensitive plugin option kept in your secure credential store instead of `GITHUB_PAT`, so the MCP server also connects from the Claude Code desktop app; the guard also blocks reading that store.

## 2026-10-17

### Changed

- **bash-lsp-intelligence** 0.2.1 — the skill stops offering operations bash-language-server does not support, and the hook's types and docs are tightened with the same behavior.
- **python-lsp-intelligence** 0.2.1 — the skill again says a finding is fixed at its cause and never silenced, and the docs now say how basedpyright finds its configuration.
- **github-operations** 0.1.1 — the command guard also blocks printing `$GITHUB_PAT`, and the docs list `delete_repository` and every `X-MCP-Readonly` value.

## 2026-10-16

### Changed

- **typescript6-lsp-intelligence** 0.2.0 — uses your own TypeScript 6 and language server instead of pinned copies; a Bash hook holds every edit to a strictest policy with your project's environment and finds `tsc` across Node version managers; the skill is now `ts-lifecycle`; a compiler crash or a project `noCheck` can no longer pass as checked.
- **typescript7-lsp-intelligence** 0.3.0 — uses your own TypeScript 7 instead of a pinned copy; a Bash hook runs the native compiler without Node.js and holds every edit to a strictest policy with your project's environment; the skill is now `ts-lifecycle`, shared with the TypeScript 6 plugin; a compiler crash or a project `noCheck` can no longer pass as checked.

## 2026-10-15

### Added

- **github-operations** 0.1.0 — carries a pull request from open to merge with a read-only tracker agent, cleans up a Git repository without losing work, and brings the GitHub MCP server with it.

### Removed

- **git-hygiene** retired: its cleanup is now the `git-cleanup` skill of **github-operations**, and the marketplace renames existing installs. Type `/github-operations:git-cleanup` where you typed `/git-hygiene:cleanup`.

## 2026-10-14

### Added

- **git-hygiene** 0.1.0 — audits a Git repository end to end, builds a numbered cleanup plan with a verified backup, and executes only what you approve, behind a guard that refuses force-pushes and secret reads.
- **plugin-evals** 0.1.0 — makes Claude an expert in Claude Code plugin evals: suites that prove what a plugin adds, correct cases, graders, mocks and CI commands, and results read right, checked against the CLI and docs you have today.

### Changed

- **git-hygiene** 0.1.1 — redacts credentials in every string of a saved or loaded inventory.
- **prompt-writer** 0.2.0 — rebuilt as a step-by-step workflow: it covers Fable 5 as well, recommends a session mode with each prompt, checks the target model's live change page every time, prints the checklist it verified, and starts only from `/prompt-writer:prompt-writer`.

### Fixed

- **plugin-evals** 0.1.1 — corrects what its references say about runs that end on an API error, now matching the docs, and confirms them against Claude Code v2.1.300.

## 2026-10-13

### Added

- **prompt-writer** 0.1.0 — turns a goal, idea or draft into one copy-ready prompt tuned to the target Claude model and effort, with the recommended setup to run it.

### Changed

- **prompt-writer** 0.1.1 — reads its reference files from paths that resolve in Claude Code and the Claude app, and always delivers a prompt instead of carrying out the task it describes.
- The marketplace no longer carries a version. `marketplace.json` has no `version`, releases tag plugins only, and this changelog is grouped by date. The tags `marketplace--v0.1.0` and `marketplace--v0.2.0` remain as history.

## [0.2.0] - 2026-10-13

### Added

- **skill-diagnostics** 0.1.0 — audits Claude skills for conformance, portability and executability, with evidence and one verdict.
- **session-handoff** 0.1.0 — carries a project's working state between sessions: a handoff written when you stop, read at the start of the next session.
- **plugin-test-bench** 0.1.0 — tests a Claude Code plugin as its users install it, and reviews its eval cases so they measure what the plugin adds.
- **bash-lsp-intelligence** 0.1.0 — connects bash-language-server and teaches Claude to trace sourced files, fix ShellCheck and shfmt findings without changing behavior, and verify each change.
- **python-lsp-intelligence** 0.1.0 — connects the basedpyright language server and teaches Claude to resolve symbols and imports semantically, fix basedpyright and Ruff findings without suppressing them, and verify each change.
- **typescript7-lsp-intelligence** 0.1.0 — connects the native TypeScript 7 language server and teaches Claude to find the program that owns a file, fix compiler findings without unsafe assertions, and verify each change.
- **typescript6-lsp-intelligence** 0.1.0 — a pinned TypeScript 6 language server and compiler for projects that can't move to TypeScript 7, a post-edit `tsc` check of every changed file's program, and the LSP-first skill.

### Changed

- **python-lsp-intelligence** 0.2.0 — a post-edit hook runs ruff and basedpyright on every Python file Claude changes with your own configuration; the skill is rewritten around LSP-first navigation and the toolchain.
- **bash-lsp-intelligence** 0.2.0 — a post-edit hook runs shfmt and ShellCheck on every shell script Claude changes with your own configuration; the skill is rewritten around LSP-first navigation and the toolchain.
- **typescript7-lsp-intelligence** 0.2.0 — the TypeScript 7 compiler and server are pinned in the plugin, a post-edit hook type-checks every changed file's program, and the skill is rewritten around LSP-first navigation and the toolchain.
- **skill-diagnostics** 0.1.1 — the executability lens refuses instructions found in the audited skill, and large audits keep within Claude Code's limit of 20 running agents.
- **skill-diagnostics** 0.1.2 — the audit-offer hook reads its event with strict type checks and ignores a file path or session ID that isn't text.
- 🧭 Compatibility matrix, installation and management guides, FAQ, troubleshooting and issue forms now cover two places: Claude Code and the Claude app, where chat and Cowork became one app. Agents, hooks and local MCP servers are marked as running in Cowork sessions, not in a chat conversation.

## [0.1.0] - 2026-10-11

### Added

- 🏭 Marketplace launched: catalog, installation and management guides, compatibility matrix, and issue forms for bugs, features, plugin ideas, documentation and questions.

[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/marketplace--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/marketplace--v0.1.0
