# Project Conventions

Conventions that apply to the whole project. Each section groups the conventions on one subject; add a convention to the section it belongs to, or open a new section when none fits.

## The project

### Audience and distribution

- The marketplace is public and hosted in a public GitHub repository owned by a personal account, not an organization.
- Everything the marketplace distributes is built for third parties, to install on their own machines and in their own working environments, where they use Claude and Claude Code for their operations and projects.

### Ownership and contributions

- The project is developed and maintained by its owner, Nery, and Claude.
- Users contribute only by reporting issues; they do not open pull requests.
- Triaging, fixing, verifying, releasing and keeping the project current are the work of the owner and Claude alone.

### Target surfaces

- The two surfaces are named **Claude Code** and **Claude**, and no other surface name is used.
  - **Claude** is the unified chat and Cowork experience.
  - **Claude Code** is a separate product.

### Platform support

- The repository and its plugins are built for macOS and Linux.

## Responsibility and verification

- Everything this project publishes reaches third parties: their machines, their projects and their operations with Claude. It can help them, or it can damage, break, block or complicate their work. The consequences are real, for those users and for the owner, as author and as a person.
- The owner and Claude share that responsibility, in every session and every change.
- Every decision, implementation and published change rests on validation and evidence: the current official documentation and its latest applicable changes, with the argument that ties them to the decision.
- Assuming, taking something for granted, acting on what is believed to be true, or fixing things by trial and error is a serious defect, and is not allowed.
- Nothing is published until it is confirmed to be actionable, executable, not deprecated, aligned with current best practices and the official documentation, and built on the best current Claude features available for its purpose.

## Project scopes

- The project has two scopes, which are never mixed:
  - **Maintainer scope:** the development, creation, publishing and upkeep of the project itself.
  - **Plugin scope:** what each plugin distributes to its users.
- A rule, tool or file of one scope does not apply to, or become a requirement of, the other.
- Each scope is checked where it belongs:
  - **Maintainer scope:** the tools, scripts, configuration and workflows that maintain the project are checked in CI and locally.
  - **Plugin scope:** each plugin's code and behavior are checked locally, with the plugin's own testing methods, in isolated environments that do not depend on the maintainer's tools or versions. In CI, only the evals run, as the Evals section of `.claude/rules/plugins.md` states.

## Plugin scope

- Before designing, creating or changing a plugin, or a workflow that runs its evals, read `.claude/rules/plugins.md`. It holds the plugin-scope conventions: target surfaces, Windows support, portability and prerequisites, pull requests inside `plugins/`, and evals. It also loads on its own when a file under `plugins/` or `.github/workflows/` is read or edited.

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

### Project memory

- The project's memories, such as feedback, facts, learnings, lessons and future work, are stored in `.claude/memory/`, the auto memory directory that `autoMemoryDirectory` sets in `.claude/settings.json`.
- Claude Code's auto memory manages that directory: one file per memory, indexed in `MEMORY.md`.
- Dated facts, evidence and notes go to memory; instructions and conventions state only the rule, with no dates.
- The repository is public, so memory holds only project information that is safe to publish, never personal, client or business data, or credentials.

## Changes and releases

### Pull requests

- A pull request is opened only at the owner's request. When a change needs one under these rules, Claude asks the owner for permission before opening it.
- Changes outside `plugins/` need no pull request, unless the owner asks for one.

### Dates

- Release dates are written in UTC, as `YYYY-MM-DD`.
- A release is dated when it is published: the UTC day its tag and GitHub Release are created, never the day the bump is prepared.
