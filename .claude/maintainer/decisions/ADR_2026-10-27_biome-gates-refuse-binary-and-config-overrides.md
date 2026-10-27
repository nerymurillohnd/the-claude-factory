---
status: accepted
date: 2026-10-27
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The Biome gates and the pre-commit hook refuse to run while `BIOME_BINARY` or `BIOME_CONFIG_PATH` is set

## Scope

- `scripts/gates.mjs`: every gate whose command is `biome`, which today means `biome-maintainer`, `biome-migrate` and `biome-plugins`.
- `.husky/pre-commit`.
- Out of scope: other tools' variables, and the editor, which resolves its own binary (`biome.lsp.bin`, then `node_modules`).

## Context and problem statement

Biome's environment-variables reference documents two variables:
- `BIOME_BINARY` "overrides the Biome binary used by the `@biomejs/biome` npm package";
- `BIOME_CONFIG_PATH` points Biome at another configuration.

Probes on 2026-10-27:
- With `BIOME_BINARY` pointing at a fake binary, both `node_modules/.bin/biome --version` and `npm exec -- biome --version` printed the fake version. That is the path `npm run` and the gates use.
- With `BIOME_CONFIG_PATH` pointing at a scratch configuration, `biome ci scripts/lib.mjs` reported an error that `biome.json` does not.

The gates inherit the environment, and the hook calls `biome` directly. So either variable silently replaces the pinned Biome (`package.json`, `package-lock.json`) or `biome.json`, and the gates report on something else. How should the gates treat them?

## Decision drivers

- The gates check with the exact pinned Biome and the repository's configuration, nothing else.
- `~/.claude/CLAUDE.md`: the receiving side validates what it needs and fails loudly when it is not there.
- A variable's value can be a private path: it is never printed.

## Considered options

- **Refuse to run, naming the variable**: chosen.
- **Drop both variables from the gates' environment, as `GIT_HOOK_VARIABLES` drops git's**: rejected, because it would silently overrule whoever set the variable, who would never learn that their override was ignored.

## Decision outcome

Chosen option: **refuse**.
- `runGates` fails a `biome` gate with "`<NAME>` is set; unset it, the gates run only the pinned Biome", before spawning it, whenever either name is present in the environment, even with an empty value.
- `.husky/pre-commit` does the same before `biome check --staged`.
- The names live in `BIOME_OVERRIDES`, exported from `scripts/gates.mjs`.

### Consequences

- Good, because a Biome run that passes the gates is always the pinned Biome on `biome.json`.
- Good, because the failure names the variable and never its value.
- Bad, because whoever wants to try another Biome build has to unset the variable before `npm run gates` or a commit, and run that build outside the gates.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| A Biome gate refuses each variable, without printing its value | `scripts/tests/gates.test.mjs`, "a Biome gate refuses to run while … is set", once per name | Passes, 2 cases. A gate whose command is not `biome` still runs with the variable set | Each commit (`npm test`) |
| The tests catch a regression | The check disabled in `scripts/gates.mjs` on purpose, then restored, with the hash compared | The two cases failed; restored, all 28 tests passed | When the check changes |
| The hook refuses each variable, set or empty, and passes when both are unset | The hook's loop run under `sh -e` with each case | Exit 1 for each set or empty variable, no value printed; exit 0 with both unset | When the hook changes |
| The hook is clean shell | `shfmt -d`, `shellcheck -s sh -x -a`, `sh -n` | All exit 0 | When the hook changes |

## More information

- Decided by Nery on 2026-10-27, as D9 (a) of `.claude/specs/2026-10-26-biome-config-corrections-and-strictness-design.md` (item 38).
