# LSP operations on Svelte files: observed behaviour and worked examples

> Observed in a clean session with only this plugin loaded, on the maintainer's SvelteKit 3 test project, which is not installed with the plugin. Every result below is the tool's real output, shortened. Paths are relative to that project's root.

## Contents

- [Call shape](#call-shape)
- [What the server answers](#what-the-server-answers)
- [Find a symbol](#find-a-symbol)
- [Go to a definition](#go-to-a-definition)
- [Find references before a change](#find-references-before-a-change)
- [Find implementations](#find-implementations)
- [Read a type with hover](#read-a-type-with-hover)
- [Trace callers and callees](#trace-callers-and-callees)
- [Read the project check output](#read-the-project-check-output)
- [What the server sees in dynamic code](#what-the-server-sees-in-dynamic-code)
- [Prove it: break something on purpose](#prove-it-break-something-on-purpose)
- [Fetch before relying on this when](#fetch-before-relying-on-this-when)
- [Official sources](#official-sources)

## Call shape

Every operation takes `operation`, `filePath`, `line` and `character`, all 1-based. Point at the symbol's name; its first character is the safest position.

```text
LSP
  operation: "findReferences"
  filePath: "src/lib/components/CounterButton.svelte"
  line: 4
  character: 12
```

The examples below write each call on one line as `LSP <operation>  <filePath> <line> <character>`, then the result after `→`.

## What the server answers

| Start position | Result | Meaning |
|---|---|---|
| A symbol in a `.svelte` file | Answers for symbols defined anywhere: `.svelte`, `.ts`, `.svelte.ts`, `#lib` imports | Always start from a `.svelte` file |
| Any position in a `.ts`, `.js` or `.svelte.ts` file | `No LSP server available for file type: .ts` | The plugin maps only `.svelte`; this is configuration, not a crash |
| The same file types mapped to `svelteserver` (tested) | Empty results ("No references found", "No symbols found") | The Svelte server gives code intelligence for Svelte documents only; mapping `.ts` to it hides symbols instead of finding them |
| The first `findReferences` of a session | The full set (8 references across 5 files), identical on repeat | No cold-index under-reporting was observed on this project size |
| `prepareCallHierarchy`, `incomingCalls`, `outgoingCalls` from a `.svelte` call site | Supported; callers are reported per module with call positions | Use them for dead-code and impact questions |

To navigate from inside TypeScript files as well, the user needs a TypeScript language server installed separately (for example a TypeScript LSP plugin); it then handles `.ts`/`.js` while this plugin handles `.svelte`.

## Find a symbol

`documentSymbol` lists one `.svelte` file's outline, script and markup, with lines but no columns; read the line for the column. The server holds every `documentSymbol` request for 1 s before answering (svelte-language-server 0.18.5, `PluginHost.ts`; 1085 ms measured with a direct LSP client, not through the LSP tool, against 2 to 41 ms for the other operations):

```text
LSP documentSymbol  src/lib/components/CounterButton.svelte 1 1
→ script (Field) L1; Snippet, Counter, formatCount (Variable) L2-4; Props (Interface) L6;
  counter, label, children (Property) L7-9; counter, label, children (Variable) L12; button (Field) L15
```

`workspaceSymbol` searches the project by name, from any `.svelte` file. It finds the declaring file, here a `.ts` file, which is not a starting position: start from a `.svelte` file that uses the symbol.

```text
LSP workspaceSymbol  src/routes/+page.svelte 1 1  query=formatCount
→ src/lib/format.ts: formatCount() (Function) - Line 2
```

## Go to a definition

Through a `#lib` import into a TypeScript module:

```text
LSP goToDefinition  src/routes/+page.svelte 14 16   (formatCount)
→ Defined in src/lib/format.ts:2:17
```

From a component tag to the component:

```text
LSP goToDefinition  src/routes/+page.svelte 13 2   (CounterButton)
→ Defined in src/lib/components/CounterButton.svelte:1:2
```

## Find references before a change

Start from a usage or the import in a `.svelte` file; the result includes the definition and every usage in `.svelte` and `.ts` files:

```text
LSP findReferences  src/lib/components/CounterButton.svelte 4 12   (formatCount import)
→ 8 references across 5 files: CounterButton.svelte 4:12, 16:13; Dynamic.svelte 4:12,
  10:30 (stored in an object); format.ts 2:17; index.ts 2:10; +page.svelte 4:12, 14:16
```

A prop: references on the `Props` member include the destructuring and every parent that passes it.

```text
LSP findReferences  src/lib/components/CounterButton.svelte 8 5   (label in Props)
→ 5 references across 3 files: CounterButton.svelte 8:5, 12:18; Dynamic.svelte 14:19
  (through a component held in a variable), 17:26 (through a lazily imported module);
  +page.svelte 13:26
```

A method called on an instance: references from the call site include the implementation in a
`.svelte.ts` module and the interface member it implements, so this also answers "who implements it".

```text
LSP findReferences  src/routes/+page.svelte 17 46   (reset in counter.reset())
→ 3 references across 3 files: counter.svelte.ts 12:3; resettable.ts 3:3; +page.svelte 17:46
```

Where a component is used: on line 1, character 1 of the component's own file (or on its `<script` tag), `findReferences` returns the component's imports and tags instead of a symbol's references:

```text
LSP findReferences  src/lib/components/CounterButton.svelte 1 1
→ 4 references across 2 files: Dynamic.svelte 2:10, 7:23; +page.svelte 2:10, 13:2
```

There is no rename operation: this list is the edit set, after checking it against the uses the server cannot see: route files, paths in strings, calls through an alias, CSS class names, and configuration or scripts.

## Find implementations

`goToImplementation` from a `.svelte` position reaches the classes and methods that implement an interface, including those in `.svelte.ts` modules. Observed with an added component that types a prop as `Resettable` (`let { item }: { item: Resettable } = $props();`, then `item.reset()` in markup):

```text
LSP goToImplementation  <component> 2 17   (Resettable in the import)
→ Defined in src/lib/counter.svelte.ts:4:14   (class Counter implements Resettable)
LSP goToImplementation  <component> 6 33   (reset in item.reset())
→ Defined in src/lib/counter.svelte.ts:12:3   (Counter.reset)
```

The server drops implementations that sit in generated code or do not map back to a source file, so an empty answer is not proof: confirm with `findReferences` on the interface member.

## Read a type with hover

```text
LSP hover  src/lib/components/CounterButton.svelte 12 9   (counter in the $props() destructuring)
→ let counter: Counter
LSP hover  src/routes/+page.svelte 17 2   (the <button> tag)
→ The button element represents a button labeled by its contents. … [MDN Reference]
```

On an HTML element, attribute, directive or block keyword the HTML or Svelte part of the server answers first with static documentation; on a component tag or its props, and on an identifier or an expression, the answer is the TypeScript type.

## Trace callers and callees

`incomingCalls` and `outgoingCalls` work without a `prepareCallHierarchy` call first. A call-hierarchy item's line includes the function's leading comment, so `formatCount` shows line 1, its JSDoc, while `goToDefinition` gives line 2.

```text
LSP prepareCallHierarchy  src/lib/components/CounterButton.svelte 16 13   (formatCount call)
→ formatCount (Function) - src/lib/format.ts:1
LSP incomingCalls         src/lib/components/CounterButton.svelte 16 13
→ 2 incoming calls: CounterButton.svelte (Module) [calls at 16:13]; +page.svelte (Module) [calls at 14:16]
LSP outgoingCalls         src/lib/components/CounterButton.svelte 16 13
→ No outgoing calls found (this function calls nothing)
```

## Read the project check output

After each edit to a `.svelte` file, Claude Code reports the server's new diagnostics under the edit (`Found N new diagnostic issues in M files`). The project check reports the whole project; the test project's deliberate error, as it prints in Claude Code (the file count includes dependencies and depends on the environment):

```text
1760845342123 ERROR "src/routes/+page.svelte" 13:26 "Type 'number' is not assignable to type 'string'."
1760845342130 COMPLETED 177 FILES 1 ERRORS 0 WARNINGS 1 FILES_WITH_PROBLEMS
```

That check ran with the test project's dependencies installed, through `npm run check`.

## What the server sees in dynamic code

Dynamic Svelte code is not a blind spot by default. Observed on the test project:

| Code | Seen | How |
|---|---|---|
| A component held in a variable: `let Active = $state(CounterButton)`, then `<Active />` | Yes | `findReferences` on the import lists the assignment; references of `Active` include its tag |
| `<svelte:element this={tag}>` | Yes | `findReferences` on `tag` includes the `this={tag}` use |
| `{#await lazy then mod}` and `<mod.default />` | Yes | `goToDefinition` on `mod` reaches the await block |
| A function stored in an object: `{ format: formatCount }` | The alias site, yes | `findReferences` on `formatCount` lists the object property |
| A call through that alias: `handlers.format(...)` | Not as a call of the original | `incomingCalls` lists only direct callers; check the alias's own references |
| The path string of `import("#lib/components/X.svelte")` | No | A string, not a reference. The project check still reports a literal `import()` of a file that does not exist |
| `import.meta.glob("./*.svelte")` patterns | No | A string pattern; the project check does not report it either, so only Grep finds it |

Run the operation the table names, on the variable or import that holds the component, before concluding that the server cannot see dynamic code; `documentSymbol` helps find those variables.

## Prove it: break something on purpose

During a change, a clean result proves nothing until a deliberate break has shown that the tool can see the change. The break is for changes only; a read-only review uses the two probes below, which break nothing. On the test project the break gave these results:

**In the user's project, during a rename**: rename only the declaration, run the project check, and compare its error sites with the `findReferences` list. The declaration is every site in the file that declares the symbol. On the test project, renaming `label` inside `CounterButton.svelte` makes the check report exactly the three `findReferences` sites outside that file:

```text
LSP findReferences  src/lib/components/CounterButton.svelte 8 5   (label in Props)
→ CounterButton.svelte 8:5, 12:18; Dynamic.svelte 14:19, 17:26; +page.svelte 13:26

project check after renaming the declaration only
→ ERROR "src/lib/components/Dynamic.svelte" 14:19, 17:26; ERROR "src/routes/+page.svelte" 13:26
```

An error site that is not in the `findReferences` list is a use the language server missed; a `findReferences` site outside the declaring file with no error is a use the check cannot see (a string, a pattern). Both go into the edit set.

**When the language server stays silent** (no diagnostics after an edit, empty answers), probe it directly: `documentSymbol` on a non-empty `.svelte` file must list its symbols, as in [Find a symbol](#find-a-symbol). Do not use `command -v svelteserver` in Bash for this: it checks the Bash command's `PATH`, not the server Claude Code started, and a missing server already shows as `Executable not found in $PATH` on the LSP call. A script cannot call the LSP tool, so only these calls prove the server.

**When the project check stays silent** (it reports nothing after a change that must break): follow rule 9 of the skill, which lists the causes to check in order.

## Fetch before relying on this when

- The language server or svelte-check behaves differently from what this file describes: read the language-tools releases newer than the svelte-check the project has (`npm ls svelte-check`) for changed behaviour.
- A result contradicts what Grep shows: Grep also matches comments and strings, and the language server can lag SvelteKit 3; confirm with the project check before trusting either.

## Official sources

- Claude Code code intelligence: https://code.claude.com/docs/en/plugins/code-intelligence
- svelte-check flags: `curl -sS https://raw.githubusercontent.com/sveltejs/language-tools/master/packages/svelte-check/README.md`
- `sv check`: `mcp__plugin_svelte-development_svelte__get-documentation` with `section: ["cli/sv-check"]`, or `curl -sS https://svelte.dev/docs/cli/sv-check/llms.txt`
- Language tools releases: https://github.com/sveltejs/language-tools/releases
