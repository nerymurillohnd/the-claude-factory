---
paths:
  - "plugins/*/tests/**"
  - "plugins/*/hooks/**"
  - "plugins/*/.claude-plugin/plugin.json"
  - ".claude/hooks/**"
  - ".github/workflows/**"
---

# Testing

## Command hooks

- Put a plugin's hook tests in `plugins/<plugin>/tests/`, using only the standard library: Python `unittest` in `test_*.py`, or Node's `node:test` in `*.test.mjs`.
- Run each hook as Claude Code does: start it as a subprocess, write its input JSON to stdin, and check the exit code, stdout and stderr.
- Run the tests with `python3 -m unittest discover -s plugins/<plugin>/tests -p 'test_*.py'` or `node --test plugins/<plugin>/tests/*.test.mjs`.
- Run one hook by hand with `echo '<input JSON>' | ./<script>; echo $?` to see its output and exit code.

## Mods

- Write tests for every mod in `plugins/<plugin>/tests/*.test.ts` or `*.test.tsx`, with a stub for every `$` call and no session, sign-in or network.
- Run `claude plugin test plugins/<plugin>` on Claude Code v2.1.299 or later to run them.
- Run `claude plugin validate plugins/<plugin>` before opening a session to see what Claude Code reads from the hooks module.
- Read the skip line in the transcript with `--plugin-dir`, or in `claude --debug` for an installed copy, when Claude Code skips a hook or refuses a mod.
- Give every hook at a gating site its own `.catch`, and run `npm run validate:hooks-catch` to confirm it.

## Local and CI

| When | Run |
| :-- | :-- |
| Locally, before each commit | `npm run lint` and `npm run typecheck`; `npm run test:scripts` when `scripts/` changed; for each changed plugin, `claude plugin validate --strict plugins/<plugin>` and its mod and hook tests; `npm run check:consistency -- --offline` |
| Before each merge: in the pull-request workflow, or locally while there is none | `npm run check`; `npm run check:install` for each changed plugin; evals as `.claude/rules/plugins/evals.md` sets |

- Run a merge-only check locally only when no pull-request workflow exists, or to reproduce a CI failure.
- Merge only when the merge checks pass.
