---
status: superseded
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: ADR_2026-11-12_maintainer-tools-as-pinned-uv-tools
superseded-by: ADR_2026-11-13_python-3-15-default-and-pinned-in-cloud-setup
---

# Run maintainer Python scripts through uv run, and keep the maintainer tools as pinned uv tools

## Scope

The npm scripts in the root `package.json` that run `scripts/*.py`, `pyproject.toml`, `uv.lock`, `.python-version`, `scripts/pyrightconfig.json`, and the Python step of the cloud environment's setup script. Maintainer scope. Plugin scripts are out of scope.

## Context and problem statement

ADR_2026-11-12_maintainer-tools-as-pinned-uv-tools had npm scripts run maintainer scripts with `.venv/bin/python`. That path assumes a `.venv` already exists, but nothing created one: the cloud setup script installed Python 3.15 and never synced the project, so a fresh session could not run `labels:sync` or `lint:github`. The setup script also installed Python as `uv python install 3.15`, which only links `python3.15`, so bare `python3` stayed on the image's OS Python. uv's docs set the project model: `uv run` runs commands in the project environment, creates `.venv` when it is missing, and keeps `uv.lock` current ("Running commands in projects"; "Structure and files", read on 2026-11-12).

## Decision drivers

- Follow uv's documented project workflow, not a hand-built path to the environment.
- A fresh clone or session runs every maintainer script with no manual step.
- One source for the Python version (`.python-version`) and one for the dependencies (`pyproject.toml` and `uv.lock`).
- Call the maintainer tools by their bare names, as the owner does.

## Considered options

- **uv project model: npm scripts run `uv run python scripts/<file>.py`; uv creates `.venv` and keeps `uv.lock` current; `uv.lock` stays in git; the setup script installs Python with `uv python install` from `.python-version`; ruff 0.17.4, basedpyright 1.40.2, zizmor 1.32.0 and check-jsonschema 0.39.0 stay pinned uv tools in `tools:install`, called bare**: chosen.
- **Standalone scripts with PEP 723 inline metadata, one `<script>.py.lock` per script (`uv lock --script`) and a `#!/usr/bin/env -S uv run --script` shebang**: rejected by the owner in favor of one project environment and one lockfile for every maintainer script.
- **Keep `.venv/bin/python`**: rejected because it bypasses uv's sync, so the environment has to exist beforehand.
- **Make `python3` the uv Python with `uv python install --default`**: rejected because uv's docs call `--default` experimental, and `uv run` picks the project's interpreter without it.

## Decision outcome

Chosen option: **the uv project model with `uv run`**, because it is uv's documented workflow, recreates the environment from the lockfile on demand, and keeps the Python version and the dependencies each in one file.

### Consequences

- Good, because after deleting `.venv` and `uv.lock`, `npm run labels:sync` and `npm run lint:github` exited 0, uv recreated a `uv.lock` identical to the committed one, `uv lock --check` passed, and `basedpyright -p scripts` reported 0 errors (2026-11-12, commit e29f167).
- Good, because Dependabot's `uv` entry keeps reading the one `uv.lock`, under ADR_2026-11-12_dependabot-cooldown-and-groups.
- Bad, because `uv run` updates `uv.lock` when `pyproject.toml` changes. A run with `--locked` refuses an outdated lock instead; CI should use it once it exists.
- Bad, because Dependabot doesn't read `tools:install`, so the four tool versions are still bumped by hand.
- Neutral, because bare `python3` keeps pointing at each machine's OS Python, which no maintainer command uses.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The npm scripts run with no existing `.venv` | Delete `.venv` and `uv.lock`, then `npm run labels:sync` and `npm run lint:github` | Both exit 0; `uv.lock` identical to git | When a script is added |
| The setup script installs the Python in `.python-version` | `uv python install` from the clone, in a fresh cloud session | Passed in this session; pending in a fresh session | First fresh session on the environment |

## More information

- This record also replaces the "Python tools run with `uv run --locked`" clause of ADR_2026-11-12_npm-scripts-are-the-single-entry-point, which ADR_2026-11-12_maintainer-tools-as-pinned-uv-tools had already replaced. That record's decision, npm scripts as the single entry point, still holds.
- Sources: uv docs at docs.astral.sh/uv, "Running commands in projects", "Structure and files", "Locking and syncing", "Python versions" and "Running scripts", read on 2026-11-12 with uv 0.13.7 installed.
- The setup script is stored on the cloud environment, not in the repository. Its Python step became `(cd "${REPO}" && uv python install)`, with uv pinned by `uv self update 0.13.7`.
- The owner decided this in this session, on 2026-11-12.
