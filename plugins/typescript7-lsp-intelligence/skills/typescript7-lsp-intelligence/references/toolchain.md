# TypeScript toolchain: tsc

## Contents

- The compiler this plugin pins
- TypeScript 7 and TypeScript 6
- Where configuration lives
- A strict profile
- No tsconfig.json
- Frequent errors
- Repair external values without assertions
- Check one program or the whole repository
- CI
- IDE

## The compiler this plugin pins

The plugin ships TypeScript 7.0.2 under its own `node_modules` and starts the language server from it, so it never depends on, or changes, the `tsc` on your `PATH` or in your project:

```bash
node "${CLAUDE_PLUGIN_ROOT}/node_modules/typescript/bin/tsc" --version
```

Your project's own `node_modules/.bin/tsc` is what its `package.json` scripts and CI run. When the two disagree, say which one produced each result; never mix their outputs.

## TypeScript 7 and TypeScript 6

Tell the generation by its interface, not its version number. TypeScript 7 (the native compiler) serves the language server as `tsc --lsp --stdio` and ships no `lib/tsserver.js`. TypeScript 6 ships `lib/tsserver.js`, which wrappers such as typescript-language-server drive; such a wrapper cannot run TypeScript 7. A project pinned to TypeScript 6 is served by the sibling plugin `typescript6-lsp-intelligence`; enable one of the two, never both, since one server handles each file extension.

## Where configuration lives

- The nearest `tsconfig.json` above a file is the program that owns it. `extends` chains inherit options; a config with neither `files` nor `include` still defines a program (defaults include the source files beside it).
- A solution-style root (`references`, `files: []`) owns nothing itself: follow its `references` to the program that lists the file.
- `tsc --showConfig -p <tsconfig>` prints the resolved options; `tsc --listFilesOnly -p <tsconfig>` prints the program's files. Neither type-checks.
- `jsconfig.json` projects are JavaScript programs with `allowJs` implied; `checkJs` or a `// @ts-check` comment is still what turns type checking on.

## A strict profile

There is no `--strictest` flag. A strict project sets these explicitly:

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
    "noEmit": true,
    "skipLibCheck": false
  }
}
```

`strict` already turns on `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `noImplicitThis`, `useUnknownInCatchVariables` and `alwaysStrict`. `noImplicitThis` is the one people forget they rely on: a plain `function () { return this.width }` returned from a method has no instance `this`, and TS2683 says so; keep it on and use an arrow function or an explicit `this` parameter. `@tsconfig/strictest` sets `skipLibCheck: true`; read a preset before relying on it. Keep the project's `target`, `module`, `moduleResolution`, `jsx` and `lib`: strictness never replaces them.

## No tsconfig.json

Without a `tsconfig.json` above the file, `tsc --noEmit <file>` checks it alone with the compiler's defaults: not strict, no JSX, default `lib`. Add a `tsconfig.json` to get the project's real policy; do not invent one in a temporary folder.

## Frequent errors

| Code | Meaning | Fix |
| :-- | :-- | :-- |
| TS2322 / TS2345 | A value's type does not match the declared or expected type | Decide which side is wrong and fix that one |
| TS2339 | The property does not exist on the type | Narrow the type first, or fix the type definition |
| TS18047 / TS18048 / TS2532 | The value may be `null` or `undefined` | Narrow with a check before use |
| TS7006 / TS7031 | Implicit `any` parameter | Annotate the parameter |
| TS2683 | `this` implicitly has type `any` (`noImplicitThis`) | Use an arrow function, or declare `this` as the first parameter |
| TS2307 | Cannot find module | Fix the import path, or install the package with the project's package manager |
| TS6133 | Declared but never used | Remove it, or use it |
| TS18003 | No inputs were found in the config file | Fix `include` or `files`; the config is broken, not the code |

Never make an error disappear with `@ts-ignore`, `@ts-expect-error`, `any`, `as unknown as T`, a non-null `!`, or a looser option. A verified false positive gets `// @ts-expect-error <reason>` on the line above, and the user is told.

## Repair external values without assertions

Start from `unknown`, validate the shape, then use the narrowed value:

```typescript
export function readLabel(text: string): string {
  const decoded: unknown = JSON.parse(text)
  if (typeof decoded !== 'object' || decoded === null || !('label' in decoded)) {
    throw new Error('Expected an object with a label')
  }
  if (typeof decoded.label !== 'string') {
    throw new Error('Expected a string label')
  }
  return decoded.label
}
```

Invalid JSON keeps its parsing exception; missing or non-string labels are rejected; empty strings stay valid. The `in` narrowing needs TypeScript 4.9 or later.

## Check one program or the whole repository

```bash
tsc --noEmit -p path/to/tsconfig.json
tsc --noEmit --listFiles -p path/to/tsconfig.json | grep '^/'   # the files the program read
tsc --noEmit --pretty false -p path/to/tsconfig.json             # file(line,col): error TSnnnn: message
```

- One `-p` run checks one program. A repository with several `tsconfig.json` files needs one run per program that includes a changed file or a caller.
- `tsc` exits 0 when clean, non-zero with errors; a non-zero exit with no `error TS` line is a tool failure, not a clean result.
- `--noEmit` only stops output files; `--incremental` still writes `tsbuildinfo`.

## CI

```bash
npx tsc --noEmit -p tsconfig.json
```

Run the project's own TypeScript there, pinned in `package.json`, so CI and the editor agree.

## IDE

VS Code: **TypeScript: Select TypeScript Version** → **Use Workspace Version** makes the editor use the project's compiler. The editor's diagnostics come from its own server; the command line is the reference when they disagree.
