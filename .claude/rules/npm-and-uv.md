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
---

# Maintainer runtimes, package managers and tools

- Never add a plugin's runtime dependency to the root `package.json` or `pyproject.toml`; declare it in the plugin's folder and its README Prerequisites.
- Move `.nvmrc` or the machine's Node, whichever is older, to the newest Node 26 LTS release only with the owner's approval; `release.yml` reads `.nvmrc`, so the change also moves CI.
- Install npm 12 with `npm install -g npm@12` only with the owner's approval; Node 26 ships npm 11, which `devEngines` rejects.
- Add an npm script for each new maintainer script before its first run.
- Give each npm script one command or one pipeline (`lint:shellcheck`). Make a script that runs several only a chain of other npm scripts by name (`npm run lint:ruff && npm run lint:ruff-format`), and put a loop in a file under `scripts/`, as `scripts/checks/plugins.sh` holds the loops over plugins.
- Add or change a dev dependency with `npm install -D <package>@<version>`, and commit `package.json` and `package-lock.json` together.
- Add a package to `allowScripts` with `npm approve-scripts <package>` only when it needs its install script to work.
- Install the Python version in `.python-version` with `uv python install`.
- Write each npm script that runs maintainer Python as `uv run python -m scripts.<folder>.<module>`, never by file path, bare `python3` or `.venv/bin/python`: npm runs it from the repository root, where `scripts` imports as a package. Plugin code is the exception: `scripts/checks/plugins.sh` runs it with bare `python3` and `node`, the user's interpreter.
- Add a package a maintainer script imports with `uv add --dev <package>`, and commit `pyproject.toml` and `uv.lock` together.
- Run `uv sync --locked` before `npm run typecheck:python`: basedpyright reads `.venv` directly.
- Pin ruff, basedpyright, zizmor and check-jsonschema with `uv tool install <tool>==<version>`, never `uv add --dev`, then run `npm run tools:install`.
