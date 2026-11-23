---
paths:
  - "plugins/*/tests/**"
  - "plugins/*/hooks/**"
  - "plugins/*/.claude-plugin/plugin.json"
---

# Plugin and mod testing

## Command hooks

- Put a plugin's hook tests in `plugins/<plugin>/tests/`, using only the standard library: Python `unittest` in `test_*.py`, or Node's `node:test` in `*.test.mjs`.
- Run each hook as Claude Code does: start it as a subprocess, write its input JSON to stdin, and check the exit code, stdout and stderr.
- Run the tests with `python3 -m unittest discover -s plugins/<plugin>/tests -p 'test_*.py'` or `node --test plugins/<plugin>/tests/*.test.mjs`: they run on the `python3` and `node` first on `PATH`, the machine's Python 3.15 and Node 26 at the top of the supported range, until the floor runtimes go first on `PATH` (see "Before a release").
- Run plugin code and its tests with bare `python3` and `node`, never `uv run` or `.venv/bin/python`: plugins run on the user's interpreter, and `npm-and-uv.md`'s `uv run` rule covers maintainer Python only.
- Never let a hook test skip itself because a machine holds a tool the hook always searches (the CI runner's `/usr/local/bin` holds `node`): give the hook an environment-variable seam that the tests set, and check that `Checks` and `Floors` report 0 skipped tests for the changed plugin.
- Run one hook by hand with `echo '<input JSON>' | ./<script>; echo $?` to see its output and exit code.

## Mods

- Write tests for every mod in `plugins/<plugin>/tests/*.test.ts` or `*.test.tsx`, with a stub for every `$` call and no session, sign-in or network.
- Require Claude Code v2.1.299 or later for `claude plugin test`.
- Run `claude plugin validate plugins/<plugin>` before opening a session to see what Claude Code reads from the hooks module.
- Read the skip line in the transcript with `--plugin-dir`, or in `claude --debug` for an installed copy, when Claude Code skips a hook or refuses a mod.
- Give every hook at a gating site its own `.catch`, and run `npm run validate:hooks-catch` to confirm it.

## Before a commit

- Run `npm run validate:mods` for the mods' tests and `npm run test:plugins` for every plugin's `tests/test_*.py` and `tests/*.test.mjs` before each commit.

## Before a release

Validate's `Floors` job runs every plugin's tests on Python 3.12 and Node.js 24 on each pull request. Before releasing a plugin whose Python or Node code changed, or to reproduce a `Floors` failure, run its tests on those floors locally, from the session scratchpad, and delete the runtimes right after the run:

- Get Python 3.12 with `UV_PYTHON_DOWNLOADS=automatic UV_PYTHON_INSTALL_DIR=<scratchpad>/py UV_CACHE_DIR=<scratchpad>/uvcache uv run --isolated --no-project --python 3.12 python3 -V`; lift `UV_PYTHON_DOWNLOADS=manual` only for that command, which links nothing into `~/.local/bin`.
- Download `node-v24.<x>-<os>-<arch>.tar.xz` and `SHASUMS256.txt` from the newest `v24` folder under `https://nodejs.org/dist/` into `<scratchpad>`, check it with `shasum -a 256 -c --ignore-missing SHASUMS256.txt`, then `tar -xJf` it.
- Run `PATH="$(echo <scratchpad>/py/cpython-3.12-*/bin):<scratchpad>/node-v24.<x>-<os>-<arch>/bin:$PATH" bash scripts/checks/plugins.sh tests`, not `npm run test:plugins`: the tarball's Node 24 and its npm fall outside the root `devEngines`.
- Delete `<scratchpad>/py`, `<scratchpad>/uvcache` and the Node folder and tarball.
