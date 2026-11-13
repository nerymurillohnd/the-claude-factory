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

The root `package.json`, `pyproject.toml` and their lockfiles serve only the maintainer tooling; users never install them. Never add a plugin's runtime dependency to them: a plugin declares its own in its folder and in its README Prerequisites, as `.claude/rules/plugins.md` sets.

## Node and npm

- Run maintainer work on Node 26 LTS and npm 12. `.nvmrc` holds the exact Node version, and `devEngines` in `package.json` the accepted Node and npm ranges; `devEngines` fails the install on any version outside them.
- Keep `.nvmrc` equal to the Node version on the machine. When `node --version` and `.nvmrc` differ, tell the owner, and on approval move the older one to the newest Node 26 LTS release: install it on the machine, or edit `.nvmrc`. `release.yml` reads `.nvmrc`, so the edit also moves CI.
- When `npm --version` is below 12, ask the owner, then install npm 12 globally with `npm install -g npm@12`: Node 26 ships npm 11, which `devEngines` rejects.
- Run every maintainer task, Python ones included, through its npm script in `package.json` (`npm run` lists them). Add a new maintainer script's npm script before its first run. Never run a script as `./<file>.py`: its `#!/usr/bin/env python3` line picks the machine's OS Python instead of the `.venv` one `uv run` uses.
- Install with `npm ci`, or `npm run setup` for the whole checkout; it never rewrites `package-lock.json`. Use `npm install -D <package>@<version>` only to add or change a dev dependency, and commit `package.json` and `package-lock.json` together; `.npmrc` saves the exact version.
- npm skips a dependency's install scripts unless `allowScripts` in `package.json` lists it. Add a package there with `npm approve-scripts <package>` only when it needs its install script to work.

## Python and uv

- Run maintainer Python on the version in `.python-version`, installed with `uv python install`, and with a uv release that `required-version` in `pyproject.toml` accepts.
- Write each npm script that runs maintainer Python as `uv run python scripts/<file>.py`, not bare `python3` (the machine's OS Python) or `.venv/bin/python`: only `uv run` and `uv sync` create `.venv` and keep `uv.lock` current.
- Add a package that a maintainer script imports with `uv add --dev <package>`, which updates `pyproject.toml` and `uv.lock` together. Commit both, and never edit `uv.lock` by hand.
- Run `uv sync --locked` (part of `npm run setup`) before `npm run typecheck:python`: basedpyright reads `.venv` directly through `scripts/pyrightconfig.json`, not through `uv run`, and reports unresolved imports without it.

## Tools

- Call ruff, basedpyright, zizmor and check-jsonschema by name: they are uv tools, installed user-wide and pinned in the `tools:install` npm script, not project dependencies. Change a tool's version there and run `npm run tools:install`. Install a tool with `uv tool install`, never `uv add --dev`, which makes it a project dependency in `.venv`.
- Get Biome and `tsc` from the npm dev dependencies in `package.json`; the npm scripts run them from `node_modules/.bin`.
- Expect shfmt, ShellCheck and actionlint as standalone binaries on the `PATH`; this repository does not pin their versions.
- Test maintainer Python with `unittest` and manage its environment with uv, not pytest or poetry, even when the machine has them.
