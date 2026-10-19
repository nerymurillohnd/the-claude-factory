# kit3-app fixture

A minimal SvelteKit 3 project used by the `svelte-lsp-intelligence` skill examples. It is not installed or built inside the plugin; it exists so the Svelte language server and the project check have known symbols to work on. The examples ran on a copy installed outside the plugin, as below.

| Symbol | File | Use it to try |
| --- | --- | --- |
| `Counter` class | `src/lib/counter.svelte.ts` | `goToDefinition`, `findReferences` |
| `Resettable` interface | `src/lib/resettable.ts` | `findReferences` on `reset()`, which lists the implementation in `Counter` (`goToImplementation` was not observed from a `.svelte` position) |
| `formatCount` function | `src/lib/format.ts` | `prepareCallHierarchy`, `incomingCalls` (two callers) |
| `CounterButton` props | `src/lib/components/CounterButton.svelte` | `hover`, `documentSymbol` |
| Dynamic usages | `src/lib/components/Dynamic.svelte` | A component held in `$state`, a lazy `import()`, `import.meta.glob`, `svelte:element` and a function stored in an object: `documentSymbol`, `findReferences` |
| Deliberate error | `src/routes/+page.svelte` | `label={42}` where `label` is a `string`: a diagnostic after edits and in the project check |

The project configuration files carry an `.example` suffix (`package.json.example`, `tsconfig.json.example`, `vite.config.ts.example`) so that tools which detect them by name, such as dependency scanners and editors, ignore the fixture inside the plugin. To run it for real, copy the folder somewhere outside the plugin, drop the suffix, install and check:

```sh
for f in package.json tsconfig.json vite.config.ts; do mv "$f.example" "$f"; done
npm install
npm run check
```

## Mutations

Deliberate breakage with known results. They are the expected results of the examples in `references/operations.md`; re-check them when the fixture's pinned versions change.

| Step | Change | The project check must report | What it proves |
| --- | --- | --- | --- |
| Baseline | none | `src/routes/+page.svelte` 13:26 | The check runs and sees the deliberate `label={42}` error |
| Mutation 1 | Rename the `label` prop to `caption` inside `CounterButton.svelte` only | `Dynamic.svelte` 14:19 and 17:26, `+page.svelte` 13:26 | Every parent that passes the old prop fails, at the same sites `findReferences` lists for `label` |
| Mutation 2 | Rename `CounterButton.svelte` to `Button.svelte` | `Dynamic.svelte` 2:29 and 8:23, `+page.svelte` 2:29 | Static imports and the literal dynamic `import()` fail; `import.meta.glob("./*.svelte")` (`Dynamic.svelte` 9) changes what it loads with no diagnostic, so only Grep finds it. The baseline error disappears while the module is missing: one error can hide another |
| Restored | Undo both | `+page.svelte` 13:26 | The check is back to the baseline |
