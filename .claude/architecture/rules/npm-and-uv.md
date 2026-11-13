---
paths:
  - "package.json"
  - "package-lock.json"
  - ".nvmrc"
  - "pyproject.toml"
  - "uv.lock"
  - ".python-version"
  - "scripts/**"
  - "biome.jsonc"
  - "ruff.toml"
  - "pyrightconfig.json"
  - "tsconfig*.json"
---

# npm and uv

npm and uv serve only the maintainer tooling; no plugin needs them and users never install them.

## npm
- Run every maintainer task, Python ones included, through its npm script in `package.json` (`npm run` lists them). Add a new maintainer script's npm script before its first run.
- Use the Node and npm versions that `.nvmrc` and `devEngines` in `package.json` set; `devEngines` fails the install on any other version.
- Install the JavaScript dev dependencies with `npm ci`; `package.json` pins them to exact versions.

## uv
- Install the Python version in `.python-version` with `uv python install`.
- Write each npm script that runs maintainer Python as `uv run python scripts/<file>.py`, not bare `python3` (the machine's OS Python) or `.venv/bin/python`: only `uv run` and `uv sync` create `.venv` and keep `uv.lock` current.
- Add a package that a maintainer script imports with `uv add --dev <package>`, which updates `pyproject.toml` and `uv.lock` together. Commit both, and never edit `uv.lock` by hand.
- Call ruff, basedpyright, zizmor and check-jsonschema by name: they are uv tools pinned in the `tools:install` npm script, not project dependencies. Change a tool's version there.
