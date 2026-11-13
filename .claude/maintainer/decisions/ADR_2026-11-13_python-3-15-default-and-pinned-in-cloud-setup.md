---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: ADR_2026-11-12_maintainer-scripts-run-through-uv-run
superseded-by: none
---

# Run maintainer Python through uv run, and make Python 3.15 the default python3, pinned twice, in cloud sessions

## Scope

The npm scripts in the root `package.json` that run `scripts/*.py`, `pyproject.toml`, `uv.lock`, `.python-version`, `scripts/pyrightconfig.json`, and the Python step of the `the-claude-factory` cloud environment's setup script. Maintainer scope. Plugin scripts, which run on each user's own `python3`, are out of scope.

## Context and problem statement

ADR_2026-11-12_maintainer-scripts-run-through-uv-run set the uv project model: npm scripts run `uv run python scripts/<file>.py`, uv keeps `.venv` and `uv.lock` current, and the four maintainer tools stay pinned uv tools. It rejected `uv python install --default` and left bare `python3` on each machine's OS Python, and it described the setup script's Python step as `uv python install` from `.python-version`.

The stored setup script no longer matches that record. Read through the environment tools on 2026-11-13, it installs uv from `https://astral.sh/uv/0.13.7/install.sh`, runs `uv python install 3.15 --default --preview-features python-install-default`, then `uv python pin 3.15` inside the clone. In this session `python3` resolves to `/root/.local/bin/python3`, Python 3.15.2.

The owner calls `python3`, ruff and basedpyright bare from any directory, with or without a project environment, and stated on 2026-11-13 that without the pin the Python version diverged in earlier cloud sessions. `git log --all -- .python-version` shows the file was first committed in a3e35ec on 2026-11-12, so before that commit the setup script's pin was the only one.

## Decision drivers

- Bare `python3`, ruff and basedpyright work in any directory, as on the owner's machine.
- Cloud sessions use the same Python as the project, without divergence.
- Keep uv's project workflow for the maintainer scripts: `uv run` and one `uv.lock`.

## Considered options

- **uv project model for the scripts, plus Python 3.15 installed as the default `python3` and pinned both in `.python-version` and by the setup script**: chosen.
- **The earlier record as written: `uv python install` from `.python-version`, without `--default`, and `python3` left on the OS Python**: rejected because the owner calls `python3` bare and expects 3.15 there.
- **Drop the setup script's `uv python pin 3.15`, since `.python-version` is tracked**: rejected by the owner, because the version diverged without it.
- **Standalone scripts with PEP 723 inline metadata and one lock per script**: rejected, as in the earlier record, in favor of one project environment and one lockfile.
- **Run scripts through `.venv/bin/python`**: rejected, as in the earlier record, because it bypasses uv's sync.

## Decision outcome

Chosen option: **the uv project model, with Python 3.15 as the default `python3` and pinned in two places**, because it keeps uv's documented workflow for the scripts while giving every session the same bare `python3` the owner uses.

### Consequences

- Good, because `python3`, `.venv` and `uv run` all resolve to Python 3.15 in a cloud session.
- Good, because the tools stay global uv tools: `uv tool install` inside the project left `pyproject.toml` and `uv.lock` unchanged and put nothing in `.venv/bin` (checked on 2026-11-13).
- Bad, because `--default` is a uv preview feature (`--preview-features python-install-default`); a new uv release can change it, which is why `UV_VERSION` stays fixed at 0.13.7.
- Bad, because the version lives in two places, `.python-version` and the setup script, and they must change together.
- Neutral, because `uv run` updates `uv.lock` when `pyproject.toml` changes; `npm run setup` uses `uv sync --locked`, which refuses an outdated lock instead.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| `python3` is Python 3.15 in a cloud session | `command -v python3; python3 --version` | `/root/.local/bin/python3`, Python 3.15.2 (2026-11-13) | First fresh session after the setup script change |
| The setup script's pin leaves the tracked file unchanged | Run the setup script from the checkout's parent, then `git status --porcelain` | Clean (2026-11-13) | When `.python-version` changes |
| The npm scripts run with no existing `.venv` | Delete `.venv`, run `npm run setup`, then `npm run typecheck` | 0 errors (2026-11-13) | When a script is added |

## More information

- The owner stated the reasons on 2026-11-13: bare tool and `python3` calls from any directory, and the divergence seen without the pin.
- Sources: uv docs at docs.astral.sh/uv, "Running commands in projects" and "Locking and syncing", read through Context7 on 2026-11-13.
- The setup script is stored on the cloud environment, not in the repository. ADR_2026-11-13_cloud-dependencies-through-setup-script-and-npm-run-setup records how it installs the repository's dependencies.
