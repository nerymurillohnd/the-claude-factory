---
paths:
  - "plugins/*/tests/**"
  - "plugins/*/hooks/**"
  - "plugins/*/.claude-plugin/plugin.json"
  - ".claude/hooks/**"
  - ".github/workflows/**"
---

# Testing

How plugins and hooks are tested, and which checks run locally and which in CI. Tests of the maintainer scripts follow `.claude/rules/architecture/scripts.md`; evals follow `.claude/rules/plugins/evals.md`.

## Plugins

- **Working copy:** develop against the plugin's folder with `--plugin-dir`, never an installed copy, and apply each edit with `/reload-plugins`.
- **Load before behavior:** pass `claude plugin validate --strict`, then confirm that every component loaded: `claude --plugin-dir plugins/<plugin> plugin details <plugin>` lists them, and in a session the Installed and Errors tabs of `/plugin` show them.
- **Every surface:** for each surface the plugin declares, test it there: in Claude Code with `--plugin-dir`; in Claude, ask the owner to upload it to their own account and test it.
- **What users receive:** install it in an isolated throwaway configuration (`npm run check:install`) before any release.

## Command hooks

- Put the tests of a plugin's command hooks in `plugins/<plugin>/tests/`, so they ship with the plugin and depend on no maintainer tool.
- Run each hook as Claude Code does: start its script as a subprocess, write its input JSON to stdin, and check the exit code, stdout and stderr.
- Write the tests with the standard library only: Python `unittest` in `test_*.py` files, or Node's `node:test` in `*.test.mjs` files, never `*.test.ts` or `*.test.tsx`, which `claude plugin test` runs as mod tests.
- Run them with `python3 -m unittest discover -s plugins/<plugin>/tests -p 'test_*.py'` or `node --test plugins/<plugin>/tests/*.test.mjs`.
- Try a hook by hand by piping a sample input into it and printing the exit code: `echo '<input JSON>' | ./<script>; echo $?`.

## Mods

- Write tests for every mod: `.test.ts` or `.test.tsx` files in `plugins/<plugin>/tests/`, run with `claude plugin test plugins/<plugin>`, with no session, sign-in or network, and a stub for every `$` call the mod makes.
- Validate first: `claude plugin validate` shows what Claude Code reads from the hooks module and type-checks a TypeScript one; read it before opening a session.
- Debug from the skip line: read the line Claude Code writes when it skips a hook or refuses a mod, in the transcript with `--plugin-dir`, or in `claude --debug` for an installed copy.
- Handle the failure of every hook at a gating site with its own `.catch`, so the guard fails closed; `npm run validate:hooks-catch` checks it.
- Run mod tests on Claude Code v2.1.299 or later.

## Local and CI

Define each check once, as an npm script or a `claude plugin` command, and call that same definition locally and in CI, except where CI's npm cannot run it (`release.yml` calls `uv run` directly).

| When | Run |
| :-- | :-- |
| Locally, before each commit | `npm run lint` and `npm run typecheck`; `npm run test:scripts` when `scripts/` changed; for each changed plugin, `claude plugin validate --strict plugins/<plugin>`, its mod tests and its hook tests; `npm run check:consistency -- --offline`; evals only as `evals.md` sets |
| CI-only: the pull-request workflow, or locally before a merge when there is none | `npm run check`; `npm run check:install` for each changed plugin; evals as `evals.md` sets |

- Run the CI-only checks before a merge: in the pull-request workflow when `.github/workflows/` has one, otherwise locally, as the `plugin-releases` skill does. Apart from that, run a CI-only check locally only to reproduce a CI failure.
- Merge only when the CI-only checks pass.
- Let maintainer tools check plugin files, but never make a plugin depend on them.
