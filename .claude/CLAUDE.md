# The Claude Factory Guidelines

This file defines the guidelines for Claude Code (claude.ai/code) when working in this repository.

## What this project is

- A public plugin marketplace for Claude Code and Claude, hosted on GitHub at `nerymurillohnd/the-claude-factory`, a personal account, not an organization.
- It designs, builds, tests, releases and maintains plugins and mods for third parties, who install them on their own machines and use them in their own projects and operations.

## Who works on it

- Nery is the owner and author: he sets the direction and makes every final decision. Claude carries out the execution: the engineering, integration and wiring, commands, commits, testing, releases, distribution and maintenance.
- GitHub Copilot takes part only at Nery's request, inside a pull request.
- Users contribute only by reporting issues; they never open pull requests or take part in triage, fixes or releases.
- No one else reviews a plugin before users install it, so every push, release and issue reply is the last gate before public exposure.

## Surfaces and platforms

- The two surfaces are named **Claude Code** and **Claude**, and no other surface name is used.
  - **Claude** is the unified chat and Cowork experience.
  - **Claude Code** is a separate product.
- The repository and its plugins are built for macOS and Linux.

## Responsibility and verification

- Everything this project publishes reaches third parties: their machines, their projects and their operations with Claude. It can help them, or it can damage, break, block or complicate their work. The consequences are real, for those users and for the owner, as author and as a person.
- The owner and Claude share that responsibility, in every session and every change.
- Every decision, implementation and published change rests on validation and evidence: the current official documentation and its latest applicable changes, with the argument that ties them to the decision.
- Sources rank in this order: the installed build first, then the release notes, then the documentation, which lags the releases.
- Assuming, taking something for granted, acting on what is believed to be true, or fixing things by trial and error is a serious defect, and is not allowed.
- Nothing is published until it is confirmed to be actionable, executable, not deprecated, aligned with current best practices and the official documentation, and built on the best current Claude features available for its purpose.
- Work counts as done only when its checks are shown with their raw output.
- Problems are reported as soon as they are found, including defects in work already published.

## Project scopes

- The project has two scopes, which are never mixed:
  - **Maintainer scope:** the development, creation, publishing and upkeep of the project itself: everything outside `plugins/`. It serves only the owner and Claude, runs only in their environment, and may rely on the owner's tools, accounts and setup.
  - **Plugin scope:** what each plugin distributes to its users: one self-contained directory per plugin under `plugins/<plugin>/`, mods included. It runs on users' machines and in their projects.
- A rule, tool or file of one scope does not apply to, or become a requirement of, the other.
- Each scope is checked where it belongs:
  - **Maintainer scope:** the tools, scripts, configuration and workflows that maintain the project are checked in CI and locally.
  - **Plugin scope:** each plugin's code and behavior are checked locally, with the plugin's own testing methods, in isolated environments that do not depend on the maintainer's tools or versions. In CI, only the evals run, as the Evals section of `.claude/rules/plugins.md` states.

## Plugin scope

- Before designing, creating or changing a plugin, or a workflow that runs its evals, read `.claude/rules/plugins.md`. It holds the plugin-scope conventions: design, safety, license and version, target surfaces, Windows support, portability and prerequisites, pull requests inside `plugins/`, and evals. It also loads on its own when a file under `plugins/` or `.github/workflows/` is read or edited.

## Maintainer scope

### Maintainer tooling

- `package.json` is the single entry point: run every maintainer command through its npm script (`npm run <script>`; `npm run` alone lists them). A new maintainer script, Python included, gets its npm script before it is run.
- Node 26 (`.nvmrc`) and npm 12, which `devEngines` in `package.json` enforces. Install with `npm ci`.
- Python is 3.15, set in `.python-version` and installed with `uv python install`.
- npm scripts run maintainer Python as `uv run python scripts/<file>.py`, never bare `python3` (each machine's OS Python) or `.venv/bin/python`: only `uv run` and `uv sync` create `.venv` and keep `uv.lock` current.
- Add a package a maintainer script imports with `uv add --dev <package>`, which updates `pyproject.toml` and `uv.lock` together; commit both, and never edit `uv.lock` by hand.
- ruff, basedpyright, zizmor and check-jsonschema are uv tools pinned in the `tools:install` npm script and called bare, not project dependencies. Biome and TypeScript are pinned dev dependencies in `package.json`.

### Commands

- How to run this project in each lifecycle stage, its Claude Code commands and npm scripts: @WORKFLOW.md

### Models and effort

- Executors and simple auditors run on Sonnet.
- Adversarial reviewers, orchestrators, and reviewers of critical, complex or broad work run on Opus.
- Effort is set per task, following the official best practices and recommendations for the model.

### Repository memory

- Feedback, facts, lessons and learnings about this repository are saved in `.claude/memory/`, one file each, and indexed in `.claude/memory/MEMORY.md`.
- Dated facts, evidence and notes go to memory; instructions and conventions state only the rule, with no dates.
- The repository is public, so memory holds only project information that is safe to publish, never personal, client or business data, or credentials.

## Changes and releases

### Pull requests

- A pull request is opened only at the owner's request. When a change needs one under these rules, Claude asks the owner for permission before opening it.
- Changes outside `plugins/` need no pull request, unless the owner asks for one.

### Dates

- Release dates are written in UTC, as `YYYY-MM-DD`.
- A release is dated when it is published: the UTC day its tag and GitHub Release are created, never the day the bump is prepared.
