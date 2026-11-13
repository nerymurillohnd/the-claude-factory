---
paths:
  - "/package.json"
  - "/package-lock.json"
  - "/.npmrc"
  - "/.nvmrc"
  - "/pyproject.toml"
  - "/uv.lock"
  - "/.python-version"
  - "scripts/**"
  - ".claude/hooks/**"
---

# Maintainer runtimes, package managers and tools

- Never add a plugin's runtime dependency to the root `package.json` or `pyproject.toml`; declare it in the plugin's folder and its README Prerequisites.
- Move `.nvmrc` or the machine's Node, whichever is older, to the newest Node 26 LTS release only with the owner's approval; `release.yml` reads `.nvmrc`, so the change also moves CI.
- Install npm 12 with `npm install -g npm@12` only with the owner's approval; Node 26 ships npm 11, which `devEngines` rejects.
- Add an npm script for each new maintainer script before its first run.
- Never run a script as `./<file>.py`: its shebang picks the machine's OS Python, not the `.venv` one.
- Install with `npm ci`, or `npm run setup` for the whole checkout; never with `npm install`, which can rewrite `package-lock.json`.
- Add or change a dev dependency with `npm install -D <package>@<version>`, and commit `package.json` and `package-lock.json` together.
- Add a package to `allowScripts` with `npm approve-scripts <package>` only when it needs its install script to work.
- Install the Python version in `.python-version` with `uv python install`.
- Write each npm script that runs maintainer Python as `uv run python scripts/<file>.py`, never bare `python3` or `.venv/bin/python`.
- Add a package a maintainer script imports with `uv add --dev <package>`, and commit `pyproject.toml` and `uv.lock` together.
- Run `uv sync --locked` before `npm run typecheck:python`: basedpyright reads `.venv` directly.
- Pin ruff, basedpyright, zizmor and check-jsonschema in the `tools:install` npm script, then run `npm run tools:install`; install them with `uv tool install`, never `uv add --dev`.
