---
paths:
  - "plugins/**"
  - ".claude/hooks/**"
  - ".github/workflows/**"
---

# Testing

How plugins and hooks are tested, and which checks run locally and which in CI. Tests of the maintainer scripts follow `.claude/rules/architecture/scripts.md`.

## Plugins

- **Working copy:** develop against the plugin's folder with `--plugin-dir`, never an installed copy, and apply each edit with `/reload-plugins`.
- **Load before behavior:** pass `claude plugin validate --strict`, then confirm that every component loaded: `claude --plugin-dir plugins/<plugin> plugin details <plugin>` lists them, and in a session the Installed and Errors tabs of `/plugin` show them.
- **Every surface:** test in Claude Code with `--plugin-dir`. For a plugin that declares Claude, ask the owner to test it in Claude by uploading it to their own account.
- **What users receive:** install it in an isolated throwaway configuration (`npm run check:install`) before any release.
- **Evals:** only on plugins the owner chose; `.claude/rules/plugins/evals.md` sets how they are written and run.

## Command hooks

- Put the tests of a plugin's command hooks in `plugins/<plugin>/tests/`, so they ship with the plugin and depend on no maintainer tool.
- Run each hook as Claude Code does: start its script as a subprocess, write its input JSON to stdin, and check the exit code, stdout and stderr.
- Write the tests with the standard library only, such as Python's `unittest` or Node's `node:test`.
- Try a hook by hand by piping a sample input into it and printing the exit code: `echo '<input JSON>' | ./<script>; echo $?`.

## Mods

- **Every mod has tests:** `.test.ts` or `.test.tsx` files in `plugins/<plugin>/tests/`, run with `claude plugin test plugins/<plugin>`, with no session, sign-in or network, and a stub for every `$` call the mod makes.
- **Validate first:** `claude plugin validate` shows what Claude Code reads from the hooks module and type-checks a TypeScript one; read it before opening a session.
- **Debug from the skip line:** read the line Claude Code writes when it skips a hook or refuses a mod, in the transcript with `--plugin-dir`, or in `claude --debug` for an installed copy.
- **Guards fail closed:** every hook at a gating site handles its own failure with `.catch`.
- **Current CLI:** run mod tests on Claude Code v2.1.299 or later.

## Local and CI

Define each check once, as an npm script or a `claude plugin` command, and call that same definition locally and in CI.

| When | Run |
| :-- | :-- |
| Locally, before each commit: fast, only what changed | `npm run lint` and `npm run typecheck`; `npm run test:scripts` when `scripts/` changed; `claude plugin validate --strict plugins/<plugin>` for each changed plugin, plus `claude plugin test plugins/<plugin>` for a mod; `npm run check:consistency -- --offline`; an eval smoke run only with the owner's approval |
| In CI, on each pull request: everything, on the whole repository | `npm run check`; `npm run check:install` for each changed plugin; the full eval suite of each changed plugin that has evals |

- Run a CI-only check locally only to reproduce a CI failure.
- Until a pull-request workflow exists, run the CI-only checks locally before a merge, as the `plugin-releases` skill does.
- Merge only when CI passes: CI is the gate.
- Let maintainer tools check plugin files, but never make a plugin depend on them.
