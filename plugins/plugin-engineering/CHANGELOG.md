# Changelog

All notable changes to **Plugin Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-11-25

### Added

- `test-and-evals`: tests a plugin right after it is created and after every change, before the work is reported as done. It runs the checks that cost nothing first: strict validation, what the validator never reads, loading from the folder, each component, mod tests, an install from a git-hosted source into a throwaway configuration, and the directory and policy review before publishing. It then builds an eval suite only after you say yes to it and its cost, with Claude proposing and writing the cases, and covers suites, graders, fixtures, mocks, CI gates and reading the results, all checked against Claude Code 2.1.330.
- `troubleshoot-and-debug`: diagnoses a plugin or marketplace that won't add, install, enable, update, load or run, or whose wrong copy, scope or version loaded. It matches the exact message to its stage and documented cause, or reads the loading rules and the state on disk, checks every place the same cause reaches, fixes it in one pass and verifies it once. It covers cloud sessions, project threads, Claude, Cowork, the Agent SDK and mods.
- A `PostToolUse` hook that runs `claude plugin validate --strict` on a plugin after Claude edits or writes a file inside it, or on a marketplace after Claude edits its `.claude-plugin/` folder, and shows Claude every error and warning, in full, so it fixes them. When the edited file is code in a plugin with mod tests, it also runs `claude plugin test` and shows every failed test. It stays silent for files outside a plugin, reads only the edited file's path and the plugin's file names, writes nothing and makes no network call. It needs Bash 3.2 or later, `awk` and `find`.

### Removed

- **Breaking:** `plugin-testing-and-debugging` and its eval case templates. Use `/plugin-engineering:test-and-evals` to test a plugin or write its evals, and `/plugin-engineering:troubleshoot-and-debug` to fix one that won't install, load or run. Claude now writes eval cases with `claude plugin eval init` instead of copying fixed templates.

### Changed

- **Breaking:** the Plugin Evals plugin is merged into this one, and `test-and-evals` replaces its `plugin-evals` skill. If you had `plugin-evals@the-claude-factory` installed, Claude Code moves it to `plugin-engineering@the-claude-factory`; run `/plugin install plugin-engineering@the-claude-factory` once.
- `cli-commands-guide` and `public-marketplace-dev` now load `test-and-evals` and `troubleshoot-and-debug` where they loaded `plugin-testing-and-debugging`.
- Four command and message examples in `public-marketplace-dev`'s MCP and skills references now say they are plain text. Nothing changes in how the plugin works.

## [0.4.0] - 2026-11-18

### Changed

- `plugin-testing-and-debugging` now explains why a plugin's agent lacks a tool or ignores a field: the frontmatter fields a plugin agent ignores, the built-in tools a background subagent drops without an error, the "zero tools" refusal, how an MCP entry in `tools` must spell the server's name, and the default branch that `isolation: worktree` starts from.
- **Breaking:** `public-marketplace-dev` now runs only when you call it with `/plugin-engineering:public-marketplace-dev`. Claude no longer loads it on its own, and it costs no context until you call it. Its description now says what it is for: setting up a new public marketplace on GitHub from scratch, once, with every folder it will need. Other plugin work no longer goes through it: `cli-commands-guide` and `plugin-testing-and-debugging` cover it.
- `cli-commands-guide` now says when it applies at the start of its description: all work on plugins, their components, dependencies and marketplaces, on every surface and distribution method. Before the first step of a task, it has Claude review the available skills and load each specialized one alongside it. When the task is setting up a new marketplace, it asks you to run `/plugin-engineering:public-marketplace-dev`.
- `plugin-testing-and-debugging` now runs every time a plugin is created, and after every change to a plugin, its components or its dependencies, before the work is reported as done. These runs are the checks that cost nothing: an eval that spends your usage still starts only after you approve it. It loads `cli-commands-guide` for the exact commands if it isn't loaded yet.

## [0.3.1] - 2026-11-15

### Removed

- The eval gate script `gate_eval_result.py` and the CI template `ci-evals.sh`. The skill now teaches the CI command the official docs give, which fails the job on its own exit code.

### Changed

- `plugin-testing-and-debugging` now has Claude run every eval check that costs nothing before any run that spends your usage: validating the plugin, running each fixture by hand, testing each grader against a trace, checking the skill's own commands and templates, and loading every suite with `--max-cost-usd 0`, which on Claude Code 2.1.325 stopped before the first run (observed; the docs don't describe it).
- It also warns that real MCP servers start only with `--allow-real-servers` or `--mocks off`, and that granting Bash or PowerShell needs the OS sandbox (`bubblewrap` and `socat` on Linux), or every run is refused.
- The testing and CLI skills now teach evals as the official docs state them: every exit code and its causes, which graders a two-arm run leaves unscored, how the arms are decided per case, the judge default, and the `plugins` field, which defaults to the enclosing plugin. Facts that come only from `--help` or from an observed run are labeled as such.
- The README lists git 2.31 or later for evals, `bubblewrap` and `socat` for suites that grant Bash on Linux, and the Claude Code docs MCP server as a recommended prerequisite.

### Fixed

- The skill no longer shows the wrong text when you call it with arguments: one sentence used a placeholder that Claude Code replaced with your first argument.
- Two gotchas about quoting the plugin root no longer show the plugin's own install path where they mean the placeholder's name.

## [0.3.0] - 2026-11-15

### Added

- `plugin-testing-and-debugging`, a new skill that tests, troubleshoots and debugs Claude Code plugins with the official CLI. It finds the stage and the documented cause behind a plugin error, or behind a plugin that doesn't install, load or run, and checks every place the same cause reaches. It runs a check before you publish, and writes, runs and gates plugin evals, with eval case templates and a script that fails a CI job when the plugin stops helping. It also says what loads in cloud sessions, project threads, Claude on the web, desktop and mobile, and the Agent SDK.
- Links to this README, the issue forms and the marketplace's privacy policy, which Anthropic's plugin directory shows on the plugin's page. Claude Code ignores these fields when it loads the plugin, so nothing changes in how it works.

## [0.2.3] - 2026-11-09

### Added

- `cli-commands-guide` covers `claude plugin restore-set-aside`, new in Claude Code 2.1.321, which gives a plugin back the options and secrets set aside when a marketplace your organization declares replaces the plugin's source, or deletes them with `--discard`.
- Every section of the `cli-commands-guide` references links its section of the official docs, so Claude can check a fact against the live page. The skill also names the official pages for manifest fields, components, `marketplace.json`, dependencies, evals, loading and error messages.

### Changed

- `cli-commands-guide` now loads for any work on Claude Code plugins, mods or marketplaces, with or without a repository, and not only when Claude runs a plugin command.
- `public-marketplace-dev` now loads `cli-commands-guide` at the start of every task it handles, not only before Claude runs, writes or explains a plugin command.
- `cli-commands-guide` is checked against Claude Code 2.1.321. It covers the 2.1.321 managed-marketplace rules, the `Git clone timed out after 120s` and seed-managed marketplace messages and their environment variables, the variables that turn auto-update off, the dependencies an install adds, where the Context cost estimates show, and a pointer to the official troubleshooting page for any command error.

## [0.2.2] - 2026-11-09

### Changed

- `public-marketplace-dev` now tells Claude to declare `options` on a `userConfig` field that a plugin hook reads as one of a few fixed values, instead of leaving it free text.
- `cli-commands-guide` now says that `--plugin-dir` and `--plugin-url` must come before the subcommand, as in `claude --plugin-dir <path> plugin details <name>`, with the `unknown option` error the other order gives, and that `plugin details` has no `--json` and lists skills, agents and commands in one rounded table.

## [0.2.1] - 2026-11-09

### Changed

- `public-marketplace-dev` now loads the `cli-commands-guide` skill before Claude runs, writes or explains a plugin command, including the `claude plugin validate --strict` run after a change, so its exact flags, gotchas and exit codes apply. Answers that use no plugin command don't load it.

## [0.2.0] - 2026-11-08

### Added

- `public-marketplace-dev` skill: the official Claude Code, Claude plugin, Claude Platform and Help Center pages, pruned to what a public GitHub marketplace and the people who install its plugins need and rewritten for Claude, so Claude designs, builds, validates, releases and maintains plugins and marketplaces from the documented behavior instead of memory. It holds 65 references in seven areas (plugins and marketplaces, mods, feature references such as hooks, skills, subagents and MCP servers, settings, CLI and diagnostics, the Agent SDK, and other surfaces), 29 images of the official pages and 3 example manifests.
- Before relying on a version-sensitive fact, Claude checks the Claude Code release notes published after the references were checked (Claude Code 2.1.319) and the live page, and tells you what differs. After it changes plugin or marketplace files, it runs `claude plugin validate --strict` and fixes what the validator reports.

### Changed

- **Breaking:** the `plugin-commands` skill is now `cli-commands-guide`, so its name says what it covers next to the new skill. If you call it by name, use `/plugin-engineering:cli-commands-guide`; its content is unchanged.

## [0.1.0] - 2026-11-07

### Added

- `plugin-commands` skill: the complete Claude Code plugin CLI reference, so Claude runs the right `claude plugin` and `claude plugin marketplace` command, `/plugin` form, `/reload-plugins` or `--plugin-dir`/`--plugin-url` flag, with exact flags, defaults, aliases, messages, `--json` fields, exit codes, scopes and minimum versions, checked against Claude Code 2.1.319.
- Gotchas Claude keeps in view, such as `/plugin install` with a path installing nothing, `marketplace remove` uninstalling that marketplace's plugins, and reloads that change MCP tools needing `--force`.
- Before relying on a version-gated flag, Claude checks `--help` on your Claude Code version and the live docs, and tells you what differs.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/plugin-engineering--v0.5.0...HEAD
[0.5.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.5.0
[0.4.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.4.0
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.3.0
[0.2.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.2.3
[0.2.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.2.2
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.1.0
