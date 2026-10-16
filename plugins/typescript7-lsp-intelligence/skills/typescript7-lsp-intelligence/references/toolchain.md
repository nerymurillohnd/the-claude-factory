# TypeScript toolchain: tsc

## Contents

- Which compiler runs
- TypeScript 7 and TypeScript 6
- Where configuration lives
- A strict profile
- No tsconfig.json
- Frequent errors
- Repair external values without assertions
- Check one program or the whole repository
- When the editor and tsc disagree
- CI
- IDE

## Which compiler runs

The plugin ships no TypeScript: it uses yours. The project's `node_modules/.bin/tsc` is what its `package.json` scripts and CI run, so it comes first; a global `tsc` serves only a project without one. Check which one you are about to run before trusting its result:

```bash
node_modules/.bin/tsc --version || tsc --version
```

Run it from the folder that holds the program's `tsconfig.json`; in a monorepo with hoisted dependencies, walk up the folders to the first `node_modules/.bin/tsc` instead.

The language server is `tsc --lsp --stdio`, the TypeScript 7 `tsc` on the `PATH` Claude Code started with. The `typescript` package also ships a native binary per platform, `node_modules/@typescript/typescript-<os>-<arch>/lib/tsc`, which runs without Node.js. When the project's and the global compiler disagree, say which one produced each result; never mix their outputs.

## TypeScript 7 and TypeScript 6

Tell the generation by its interface, not its version number. TypeScript 7 (the native compiler) serves the language server as `tsc --lsp --stdio` and ships no `lib/tsserver.js`. TypeScript 6 ships `lib/tsserver.js`, which wrappers such as typescript-language-server drive; such a wrapper cannot run TypeScript 7. A project pinned to TypeScript 6 is served by the sibling plugin `typescript6-lsp-intelligence`; enable one of the two, never both, since one server handles each file extension. When the project's `tsc --version` reports 6.x while this plugin is active, tell the user the sibling plugin fits that project, and label every result with the compiler that produced it.

## Where configuration lives

- The nearest `tsconfig.json` above a file is the program that owns it. `extends` chains inherit options; a config with neither `files` nor `include` still defines a program (defaults include the source files beside it).
- A solution-style root (`references`, `files: []`) owns nothing itself: follow its `references` to the program that lists the file.
- `tsc --showConfig -p <tsconfig>` prints the resolved options; `tsc --listFilesOnly -p <tsconfig>` prints the program's files. Neither type-checks.
- `jsconfig.json` projects are JavaScript programs with `allowJs` implied; `checkJs` or a `// @ts-check` comment is still what turns type checking on.

## A strict profile

There is no `--strictest` flag. The strict check in SKILL.md holds code to this profile, the same one the plugin's post-edit hook applies (the hook also sets `target` and `module`; the skill keeps the project's):

```json
{
  "compilerOptions": {
    "strict": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitOverride": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "allowUnusedLabels": false,
    "allowUnreachableCode": false,
    "allowJs": true,
    "checkJs": true,
    "skipLibCheck": true,
    "noEmit": true
  }
}
```

`strict` already turns on `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `noImplicitThis`, `useUnknownInCatchVariables`, `alwaysStrict` and `strictBuiltinIteratorReturn`; the command names each one anyway. Keep the project's `target`, `module`, `moduleResolution`, `jsx` and `lib`: strictness never replaces them.

Command-line options override the config while its `paths`, module resolution and `types` still apply. `--strict` alone does not override an explicit `"strictNullChecks": false`, so the command names every option. `--checkJs true` also brings the program's JavaScript files into the check.

## No tsconfig.json

Without a `tsconfig.json` above the file, `tsc <file>` checks it alone with the compiler's defaults: not strict, no JSX, default `lib`. Propose a `tsconfig.json` to the user (the profile above plus `target` and `module`) and create it only if they agree. Meanwhile, run the strict check's options on the file instead of `-p <tsconfig.json>`: `tsc <options> --target es2022 --module nodenext <file>`, adding `--jsx preserve` for `.tsx` or `.jsx`. Do not invent a config in a temporary folder.

## Frequent errors

Read the error's own text; these are the ones whose fix is easy to get wrong.

| Code | Meaning | Fix |
| :-- | :-- | :-- |
| TS2322 / TS2345 | A value's type does not match the declared or expected type | Decide which side is wrong and fix that one |
| TS2683 | `this` implicitly has type `any` (`noImplicitThis`) | Use an arrow function, or declare `this` as the first parameter |
| TS2307 | Cannot find module | Fix the import path, or install the package with the project's package manager |
| TS18003 | No inputs were found in the config file | Fix `include` or `files`; the config is broken, not the code |

Never make an error disappear with `@ts-ignore`, `any`, `as unknown as T`, a non-null `!`, or a looser option. The only exception is a verified false positive: put `// @ts-expect-error <reason>` on the line above and tell the user.

## Repair external values without assertions

Start from `unknown`, validate the shape, then use the narrowed value (`JSON.parse(text)` assigned to `const decoded: unknown`, then `typeof` and `in` checks that throw on a wrong shape). Invalid JSON keeps its parsing exception.

## Check one program or the whole repository

Use the strict check from SKILL.md; these two commands inspect a program and do not give a verdict:

```bash
tsc --noEmit --listFiles -p path/to/tsconfig.json | grep '^/'   # the files the program read
tsc --noEmit --pretty false -p path/to/tsconfig.json             # file(line,col): error TSnnnn: message, with the project's own options only
```

- One `-p` run checks one program. A repository with several `tsconfig.json` files needs one run per program that includes a changed file or a caller.
- `tsc` exits 0 when clean, non-zero with errors; a non-zero exit with no `error TS` line is a tool failure, not a clean result.
- `--noEmit` only stops output files; `--incremental` still writes `tsbuildinfo`.

## When the editor and tsc disagree

Take the same file through four steps; the command line is the reference.

1. **Same compiler?** Compare `node_modules/.bin/tsc --version` with the editor's TypeScript (VS Code: **TypeScript: Select TypeScript Version**).
2. **Same program?** `tsc --listFilesOnly -p <tsconfig.json>` must list the file, and `--showConfig` must show the options the editor assumes.
3. **Same options?** The editor uses the project's config; the strict check adds the strict profile, so it can report errors the editor does not.
4. **Stale editor?** Restart the language server; tell the user which side produced each result.

## CI

```bash
node_modules/.bin/tsc --noEmit -p tsconfig.json
```

This CI command applies the project's own policy, not the strict check; add the strict check's options only if the user wants CI held to that profile. In CI, install dependencies first and run the project's own TypeScript, pinned in `package.json`, so CI and the editor agree.

## IDE

VS Code: **TypeScript: Select TypeScript Version** → **Use Workspace Version** makes the editor use the project's compiler. The editor's diagnostics come from its own server; the command line is the reference when they disagree.
