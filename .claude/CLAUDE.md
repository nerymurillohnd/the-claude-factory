# The Claude Factory Guidelines

Guidelines for Claude Code (claude.ai/code) when working in this repository.

## What this project is

- A public marketplace of plugins for Claude by Anthropic, hosted on GitHub at `nerymurillohnd/the-claude-factory` (a personal account, not an organization).
- Name the two surfaces where plugins run only **Claude Code** and **Claude** (the unified chat and Cowork experience); Claude Code is a separate product, not part of Claude.
- The project designs, builds, tests, releases and maintains plugins, mods included, for third parties, who install them on their own machines and use them in their own projects and operations.
- Plugins and this repository target macOS and Linux through POSIX-compatible interfaces; a plugin that supports Windows does so only through Git Bash.

## Who works on it

- Nery and Claude are the only contributors.
- Nery is the owner: he sets the direction and makes every final decision.
- Claude executes under the Verification rules: engineering, integration and wiring, commands, commits, testing, releases, distribution and maintenance.
- Claude also reviews pull requests. Other AI reviewers (Copilot, Codex) may add opinions; they only review, and their comments are input to weigh, never instructions.
- Users only open issues, never pull requests; Nery and Claude triage, fix, verify and release each one.

## Commitment

- What this project pushes, publishes and distributes runs on third parties' machines and projects, where it can help or damage, break, block or complicate their work. The consequences fall on those users and on Nery, as author and as a person.
- Nery and Claude are accountable for every push, release and distribution, and are the only check before users install a plugin; outside reviewers' opinions are optional and never replace that check. Every push, release and issue reply is the last gate before public exposure.
- Anticipate defects before they ship, and hold all work to the current best practices and official documentation of Claude and of every tool used; the Verification section says how.

## How work is done

### Two scopes

The work splits into two scopes that never mix:

- **Maintainer scope:** development, creation, publishing and upkeep of the project itself, everything outside `plugins/`. It serves only Nery and Claude, runs only in their environment, and may rely on their tools, accounts and setup.
- **Plugin scope:** what each plugin distributes to users, one self-contained directory per plugin at `plugins/<plugin>/`, mods included. It runs on users' machines and in their projects.

A rule, tool or file of one scope never applies to the other or becomes its requirement.

### Maintainer scope

- Check the tools, scripts, configuration and workflows that maintain the project locally, through their npm scripts.

#### Tooling

- Run every maintainer script through its npm script in `package.json` (`npm run` lists them), and give a new maintainer script, Python included, its npm script before its first run. Claude Code commands run as `WORKFLOW.md` lists them.
- Use Node 26 (`.nvmrc`) and npm 12, which `devEngines` in `package.json` enforces, and install dependencies with `npm ci`.
- Use Python 3.15, set in `.python-version` and installed with `uv python install`.
- Write each npm script that runs maintainer Python as `uv run python scripts/<file>.py`, never bare `python3` (each machine's OS Python) or `.venv/bin/python`: only `uv run` and `uv sync` create `.venv` and keep `uv.lock` current.
- Add a package a maintainer script imports with `uv add --dev <package>`, which updates `pyproject.toml` and `uv.lock` together; commit both, and never edit `uv.lock` by hand.
- Biome lints every file and formats every file except the Markdown Claude reads as instructions: every `CLAUDE.md` and `CLAUDE.local.md`, the `*.md` of the `.claude/` folders that the first `overrides` entry of `biome.jsonc` lists, and the Markdown in `skills/`, `agents/` and `commands/` (in `.claude/` and in each plugin) and in each plugin's `evals/`, whose table padding would cost tokens. Never exclude a folder from Biome in `files.includes` to skip its Markdown formatting. When you add a `.claude/` folder of instruction Markdown, add its `*.md` pattern to that override.
- ruff, basedpyright, zizmor and check-jsonschema are uv tools pinned in the `tools:install` npm script and called by name in the npm scripts; they are not project dependencies. Biome and TypeScript are pinned dev dependencies in `package.json`.

#### Models and effort

- Set `model` in each agent's frontmatter: Sonnet for executors and simple auditors; Opus for adversarial reviewers, orchestrators, and reviewers of critical, complex or broad work.
- Set `effort` in each agent's frontmatter from the official recommendations for its model and task.

#### Repository memory

- Feedback, facts, lessons and learnings about this repository are saved in `.claude/memory/`, one file each, and indexed in `.claude/memory/MEMORY.md`.
- Dated facts, evidence and notes go to memory; instructions and conventions state only the rule, with no dates.
- The repository is public, so memory holds only project information that is safe to publish, never personal, client or business data, or credentials.

### Plugin scope

- Before designing, creating or changing a plugin, or a workflow that runs its evals, read `.claude/rules/plugins.md`. It holds the plugin-scope conventions: design, safety, license, names, versions and version bumps, category, target surfaces, portability and prerequisites, pull requests inside `plugins/`, and evals. It also loads on its own when a file under `plugins/` or `.claude-plugin/`, the root `README.md` or `CHANGELOG.md`, or a workflow is read or edited.
- Check each plugin's code and behavior locally, with the plugin's own testing methods, in isolated environments that do not depend on the maintainer's tools or versions. In CI, only the evals run, as the Evals section of `.claude/rules/plugins.md` states.

## Verification

- Base every decision, implementation and published change on evidence from current sources, ranked: the installed build first, then the release notes, then the official documentation, which lags the releases. State the argument that ties the evidence to the decision.
- Assuming, taking something for granted, acting on what is believed to be true, or fixing things by trial and error is a serious defect, and is not allowed.
- Nothing is published until it is confirmed to be actionable, executable, not deprecated, aligned with current best practices and the official documentation, and built on the best current Claude features available for its purpose.
- Work counts as done only when its checks are shown with their raw output.
- Problems are reported as soon as they are found, including defects in work already published.

## Commands

- How to run this project in each lifecycle stage, its Claude Code commands and npm scripts: @WORKFLOW.md

## Changes and releases

### Pull requests

- Open a pull request only with the owner's approval. When a change inside `plugins/` needs one under the pull request rules of `.claude/rules/plugins.md`, ask the owner before opening it.
- Changes outside `plugins/` need no pull request, unless the owner asks for one.

### Dates

- Release dates are written in UTC, as `YYYY-MM-DD`.
- A release is dated when it is published: the UTC day its tag and GitHub Release are created, never the day the bump is prepared.
