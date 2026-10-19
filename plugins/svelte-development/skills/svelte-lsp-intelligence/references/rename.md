# Renames and moves: cases that change the edit set

> Read from the svelte-language-server 0.18.5 source (`RenameProvider.ts`, `server.ts`), not observed through the LSP tool, which has no rename operation. The procedure for a change in SKILL.md still decides the edit set; this file lists what a rename must also handle by hand.

## Props

- **Shorthand attributes.** `<Child {x} />` passes a prop named `x`. Renaming the prop to `y` makes it `<Child y={x} />`, unless the local variable is renamed too; `bind:x` becomes `bind:y={x}` the same way. The server applies the same expansion to `{x}`, `bind:x` and `let:x` (`RenameProvider.ts`, "shorthands: let:xx, bind:xx, {xx}").
- **`export { x as y }` props** are not supported by the server's rename (`RenameProvider.ts:49`, a TODO). Treat them as Grep territory and edit them with the project check as the judge. `$props()` destructuring has no such case.

## Stores

`store` and `$store` are one symbol: the server renames both spellings together, whichever one the rename starts from (`RenameProvider.ts`, `enhanceRenamesInCaseOf$Store`). Edit both by hand the same way, and Grep `\$name` for uses the references missed.

## Files with a syntax error

The server builds no generated code for a `.svelte` file with a syntax error and refuses to rename in it (`RenameProvider.ts:168`). Other operations are probably affected too (inferred, not observed). Run the project check on that file and fix the syntax before concluding that a symbol has no references.

## Moving or renaming a component file

The server can update imports for a moved file only through its custom request `$/getEditsForFileRename` (`server.ts:650`), which the LSP tool cannot send. Move a file only when the task asks for it; an agent whose Bash is limited to checks reports the move as an open point instead. Do it by hand:

1. `findReferences` at line 1, character 1 of the component, for its imports and tags.
2. Grep the file path and the bare file name: dynamic `import()`, `import.meta.glob` patterns, configuration, tests.
3. Move the file (`git mv` in a git repository, `mv` otherwise), then update every import. A move is a change outside Edit and Write: rule 10 applies, so trust the project check and a Read over the server afterwards.
4. In a SvelteKit project run `npx --no-install svelte-kit sync`, then the project check.
