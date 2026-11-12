# Project Conventions

Conventions that apply to the whole project. Each section groups the conventions on one subject; add a convention to the section it belongs to, or open a new section when none fits.

## Dates

- Release dates are written in UTC, as `YYYY-MM-DD`.
- A release is dated when it is published: the UTC day its tag and GitHub Release are created, never the day the bump is prepared.

## Platform support

- The repository and its plugins are built for macOS and Linux.
- Windows is supported only when a plugin, current or future, is meant to run there, and then only through Git Bash.

## Portability and prerequisites

- Every plugin created and published here runs on its own on a user's machine. It never depends on the tools, software, configuration or versions installed on the owner's terminal or machine.
- Code is always written to be portable.
- Every tool, software, integration or dependency a plugin needs to run, and every specific or minimum version it requires, is declared as a prerequisite in the Prerequisites section of that plugin's README.

## Target surfaces

- Every plugin in this marketplace is built exclusively for Claude Code, for Claude, or for both.
- The two surfaces are named **Claude Code** and **Claude**, and no other surface name is used.
  - **Claude** is the unified chat and Cowork experience.
  - **Claude Code** is a separate product.
- When a component does not work everywhere in Claude, the plugin's compatibility notes state where it works, for example only where Claude runs tasks on the user's computer.

## Audience and distribution

- The marketplace is public and hosted in a public GitHub repository owned by a personal account, not an organization.
- Everything the marketplace distributes is built for third parties, to install on their own machines and in their own working environments, where they use Claude and Claude Code for their operations and projects.

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
  - **Plugin scope:** each plugin's code and behavior are checked locally, with the plugin's own testing methods, in isolated environments that do not depend on the maintainer's tools or versions. In CI, only the evals run, as the Evals section states.

## Maintainer tooling

- `package.json` is the single entry point: run every maintainer command through its npm script (`npm run <script>`; `npm run` alone lists them). A new maintainer script, Python included, gets its npm script before it is run.
- Node 26 (`.nvmrc`) and npm 12, which `devEngines` in `package.json` enforces. Install with `npm ci`; its `prepare` script points Git at the tracked `.githooks/`.
- Python is 3.15, set in `.python-version` and installed with `uv python install`.
- npm scripts run maintainer Python as `uv run python scripts/<file>.py`, never bare `python3` (each machine's OS Python) or `.venv/bin/python`: only `uv run` and `uv sync` create `.venv` and keep `uv.lock` current.
- Add a package a maintainer script imports with `uv add --dev <package>`, which updates `pyproject.toml` and `uv.lock` together; commit both, and never edit `uv.lock` by hand.
- ruff, basedpyright, zizmor and check-jsonschema are uv tools pinned in the `tools:install` npm script and called bare, not project dependencies. Biome and TypeScript are pinned dev dependencies in `package.json`.

## Pull requests

- A pull request is opened only at the owner's request. When a change needs one under these rules, Claude asks the owner for permission before opening it.
- Changes outside `plugins/` need no pull request, unless the owner asks for one.
- Inside `plugins/`:
  - A change that creates or edits a plugin's components, dependencies or configuration always goes through a pull request. Skill, agent and command files are components, even though they are Markdown.
  - A change limited to a plugin's general documentation, which alters neither the plugin's behavior nor what users have installed on their machines, needs no pull request, unless the owner asks for one.

## Evals

- Whether a plugin has evals is the owner's decision. Claude may suggest adding them to a plugin, and says when and why.
- When the owner decides a plugin gets evals, Claude discusses every eval case with the owner before writing it, and never creates cases on its own.
- A plugin with evals runs a reduced smoke suite locally, through the official testing modes.
- In CI, the full eval suite of a plugin runs the first time, and afterwards only when a plugin that has evals changes in a way that needs a pull request. Every other run skips the eval workflow.

## Models and effort

- Executors and simple auditors run on Sonnet.
- Adversarial reviewers, orchestrators, and reviewers of critical, complex or broad work run on Opus.
- Effort is set per task, following the official best practices and recommendations for the model.

## Project memory

- The project's memories, such as feedback, facts, learnings, lessons and future work, are stored in `.claude/memory/`, the auto memory directory that `autoMemoryDirectory` sets in `.claude/settings.json`.
- Claude Code's auto memory manages that directory: one file per memory, indexed in `MEMORY.md`.
- Dated facts, evidence and notes go to memory; instructions and conventions state only the rule, with no dates.
- The repository is public, so memory holds only project information that is safe to publish, never personal, client or business data, or credentials.

## Ownership and contributions

- The project is developed and maintained by its owner, Nery, and Claude.
- Users contribute only by reporting issues; they do not open pull requests.
- Triaging, fixing, verifying, releasing and keeping the project current are the work of the owner and Claude alone.
