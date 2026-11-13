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

claude/rules/npm-and-uv.md:
```
# npm and uv (maintainer scope)

npm and uv run only the maintainer tooling. No plugin needs them, and users never install them.

## npm
- Every maintainer task runs through its npm script in `package.json` (`npm run` lists them), Python ones included. Give a new maintainer script, Python included, its npm script before its first run.
- Use Node 26 (`.nvmrc`) and npm 12. `devEngines` in `package.json` enforces both and fails on any other version.
- Install the JavaScript dev dependencies (Biome, TypeScript) with `npm ci`. They are pinned to exact versions in `package.json`.

## uv
- **Python:** use Python 3.15, set in `.python-version` and installed with `uv python install`.
- **Environment:** write each npm script that runs maintainer Python as `uv run python scripts/<file>.py`. Never use bare `python3`, which is each machine's OS Python, or `.venv/bin/python`: only `uv run` and `uv sync` create `.venv` and keep `uv.lock` current.
- **Dependencies:** add a package that a maintainer script imports with `uv add --dev <package>`, which updates `pyproject.toml` and `uv.lock` together. Commit both, and never edit `uv.lock` by hand.
- **Tools:** ruff, basedpyright, zizmor and check-jsonschema are uv tools pinned to exact versions in the `tools:install` npm script and called by name in the npm scripts. They are not project dependencies.
```
