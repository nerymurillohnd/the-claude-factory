# TypeScript quality gate: tsc

The gate's hooks ship in the `ts-lsp` plugin, next to the language server. This file is the
only guidance for them: read it when writing TypeScript or JavaScript code or when the gate reports findings or blocks a stop.

Every TypeScript/JavaScript project Claude changes is type-checked as a whole by the `ts-lsp` plugin's hook before Claude (or a subagent) stops. After each edit, the per-file feedback comes from the TypeScript language server's diagnostics instead, so fix those as they appear rather than waiting for the stop:

```bash
tsc --noEmit -p <each tsconfig*.json of the project> --listFiles
```

- The project is the nearest directory above the file holding any `tsconfig*.json`, and **every program that directory declares is checked**, not only `tsconfig.json`: a file often belongs to a sibling program (`tsconfig.scripts.json`, `tsconfig.tests.json`). The project's own `node_modules/.bin/tsc` is used when present, else the global `tsc`. There is no `cd`: tsc runs where the gate is invoked, with `-p` naming each tsconfig by its full path, and `--noEmit` so the check writes nothing.
- A `tsconfig*.json` with no `include` anywhere in its `extends` chain and no `files` of its own exists only to be extended and is skipped; `tsc --showConfig` decides, so an inherited `include` counts. Plain `tsconfig.json` is always a program.
- Each program's tsconfig decides strictness and scope. `--noEmit` only keeps the check from writing output.
- tsc checks the **whole program**. An error can be in a file you did not edit, e.g. a caller broken by a changed signature, in any program that reaches it. Those errors are yours to fix too.
- A changed file that **no program read** is reported, not passed over: add it to the `include` or `files` of a tsconfig in its project. Generated output (`dist`, `build`, `out`, `coverage`, `.astro`, `.next`, `.svelte-kit`, `.wrangler`, `.output`) is exempt.
- Files with no `tsconfig*.json` above them, and files under `node_modules`, are not checked.
- A config error counts as a finding, including `TS18003` from an `include` that matches nothing: fix the config.
- Only `.ts .tsx .mts .cts .js .jsx .mjs .cjs` trigger the check. `.astro` and `.svelte` files are not covered.

## When the hook reports errors

1. Read each error as `file(line,col): error TSxxxx: message` and fix its root cause.
2. Save with Edit, then check the project yourself before stopping: `ts-gate <file>` (see "Checking on demand"). The LSP diagnostics cover the edited file only; callers elsewhere surface in `tsc`.
3. A stop blocked by the hook lists every project that still fails. Fix them all, then stop again: the hook re-checks at every stop.

Never make the gate pass by weakening it: no `@ts-ignore`, `@ts-nocheck` or `@ts-expect-error`, no `any`, no `as unknown as T` or non-null `!` just to silence an error, and no loosening of `tsconfig.json` (`strict`, `skipLibCheck`, `exclude`, ...). A suppression or loosened config hides the defect from every later check and from the user, so the gate would report green on broken code.
The one exception is an error you verified is a false positive. Put `// @ts-expect-error <reason>` on the line above, and tell the user.

## Frequent errors

| Code | Meaning | Fix |
|---|---|---|
| TS2322 / TS2345 | A value's type does not match the declared or expected type | Decide which side is wrong and fix that one |
| TS2339 | The property does not exist on the type | Narrow the type first, or fix the type definition |
| TS18047 / TS18048 / TS2532 | The value may be `null` or `undefined` | Narrow with a check before use |
| TS7006 / TS7031 | Implicit `any` parameter | Annotate the parameter |
| TS2307 | Cannot find module | Fix the import path, or install the package with the project's package manager |
| TS6133 | Declared but never used | Remove it, or use it |

## Checking on demand

```bash
ts-gate <file>...
```

`ts-gate` comes from `ts-lsp`'s `bin/`, on the Bash tool's `PATH` while the plugin is enabled. Exit 0 means clean. Exit 2 prints the errors per project.
