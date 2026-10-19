# LSP operations on Svelte files: observed behaviour and worked examples

> Observed in a clean session with only this plugin loaded, on an installed copy of `fixtures/kit3-app`. Every result below is the tool's real output, shortened. Paths are relative to the fixture root.

## Contents

- [Call shape](#call-shape)
- [What the server answers](#what-the-server-answers)
- [Find a symbol](#find-a-symbol)
- [Go to a definition](#go-to-a-definition)
- [Find references before a change](#find-references-before-a-change)
- [Read a type with hover](#read-a-type-with-hover)
- [Trace callers and callees](#trace-callers-and-callees)
- [Read diagnostics](#read-diagnostics)
- [What the server sees in dynamic code](#what-the-server-sees-in-dynamic-code)
- [Prove it: break something on purpose](#prove-it-break-something-on-purpose)
- [Fetch before relying on this when](#fetch-before-relying-on-this-when)
- [Official sources](#official-sources)

## Call shape

Every operation takes `operation`, `filePath`, `line` and `character`, all 1-based. `workspaceSymbol` also takes `query`, which must not be empty. Point at the first character of the symbol's name. Load the tool with ToolSearch (`query: "select:LSP"`) when it is deferred.

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

`documentSymbol` lists one `.svelte` file's outline, script and markup:

```text
LSP documentSymbol  src/lib/components/CounterButton.svelte 1 1
→ script (Field) L1; Snippet, Counter, formatCount (Variable) L2-4; Props (Interface) L6;
  counter, label, children (Property) L7-9; counter, label, children (Variable) L12; button (Field) L15
```

`workspaceSymbol` searches the project by name, from any `.svelte` file:

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
  10:30 (stored in an object); format.ts 2:17; index.ts 1:10; +page.svelte 4:12, 14:16
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
LSP findReferences  src/routes/+page.svelte 17 49   (reset in counter.reset())
→ 3 references across 3 files: counter.svelte.ts 12:3; resettable.ts 3:3; +page.svelte 17:46
```

There is no rename operation: this list is the edit set, after checking it against the uses the server cannot see: route files, paths in strings, calls through an alias, CSS class names, and configuration or scripts.

## Read a type with hover

```text
LSP hover  src/lib/components/CounterButton.svelte 12 9   (counter in the $props() destructuring)
→ let counter: Counter
```

## Trace callers and callees

```text
LSP prepareCallHierarchy  src/lib/components/CounterButton.svelte 16 14   (formatCount call)
→ formatCount (Function) - src/lib/format.ts:1
LSP incomingCalls         src/lib/components/CounterButton.svelte 16 14
→ 2 incoming calls: CounterButton.svelte (Module) [calls at 16:13]; +page.svelte (Module) [calls at 14:16]
LSP outgoingCalls         src/lib/components/CounterButton.svelte 16 14
→ No outgoing calls found (this function calls nothing)
```

## Read diagnostics

After each edit to a `.svelte` file, Claude Code reports the server's new diagnostics under the edit (`Found N new diagnostic issues in M files`). The fixture's deliberate error, as the project check reports it in Claude Code:

```text
ERROR "src/routes/+page.svelte" 13:26 "Type 'number' is not assignable to type 'string'."
COMPLETED 177 FILES 1 ERRORS 0 WARNINGS 1 FILES_WITH_PROBLEMS
```

That check ran in a copy of the fixture outside the plugin, with the `.example` suffix dropped from its three config files and dependencies installed (see the fixture README), through `npm run check`.

## What the server sees in dynamic code

Dynamic Svelte code is not a blind spot by default. Observed on this plugin's fixture:

| Code | Seen | How |
|---|---|---|
| A component held in a variable: `let Active = $state(CounterButton)`, then `<Active />` | Yes | `findReferences` on the import lists the assignment; references of `Active` include its tag |
| `<svelte:element this={tag}>` | Yes | `findReferences` on `tag` includes the `this={tag}` use |
| `{#await lazy then mod}` and `<mod.default />` | Yes | `goToDefinition` on `mod` reaches the await block |
| A function stored in an object: `{ format: formatCount }` | The alias site, yes | `findReferences` on `formatCount` lists the object property |
| A call through that alias: `handlers.format(...)` | Not as a call of the original | `incomingCalls` lists only direct callers; check the alias's own references |
| The path string of `import("#lib/components/X.svelte")` | No | A string, not a reference. The project check still reports a literal `import()` of a file that does not exist |
| `import.meta.glob("./*.svelte")` patterns | No | A string pattern; the project check does not report it either, so only Grep finds it |

`documentSymbol` lists every one of these constructs in a component. Run it before concluding that the server cannot see dynamic code.

## Prove it: break something on purpose

A clean result proves nothing until a deliberate break has shown that the tool can see the change. Two ways, both with known results (the fixture README's "Mutations" table):

**In the user's project, during a rename**: rename only the declaration, run the project check, and compare its error sites with the `findReferences` list. On the fixture, renaming `label` inside `CounterButton.svelte` makes the check report exactly the three `findReferences` sites above:

```text
LSP findReferences  src/lib/components/CounterButton.svelte 8 5   (label in Props)
→ CounterButton.svelte 8:5, 12:18; Dynamic.svelte 14:19, 17:26; +page.svelte 13:26

project check after renaming the declaration only
→ ERROR "src/lib/components/Dynamic.svelte" 14:19, 17:26; ERROR "src/routes/+page.svelte" 13:26
```

An error site that is not in the `findReferences` list is a use the language server missed; a `findReferences` site with no error is a use the check cannot see (a string, a pattern). Both go into the edit set.

**When the language server stays silent** (no diagnostics after an edit, empty answers), probe it directly: `documentSymbol` on a non-empty `.svelte` file must list its symbols, as in [Find a symbol](#find-a-symbol). Do not use `command -v svelteserver` in Bash for this: a sandboxed Bash cannot follow a symlinked global install. A script cannot call the LSP tool, so only these calls prove the server.

**When the project check stays silent** (it reports nothing after a change that must break): the cause is almost always in the project, not in svelte-check. Run `npx --no-install svelte-kit sync` and check again (missing generated types hide errors); read the last line, `COMPLETED <n> FILES …`, and confirm the edited file is inside the tsconfig `include` (SvelteKit 3 projects extend `$app/tsconfig`); confirm that `npm run check` really runs svelte-check (read the script in `package.json`); in a monorepo, run it from the app folder.

## Fetch before relying on this when

- The project uses svelte-language-server or svelte-check newer than the versions above: check the language-tools releases for changed behaviour.
- A result contradicts what Grep shows: Grep also matches comments and strings, and the language server can lag SvelteKit 3; confirm with the project check before trusting either.

## Official sources

- Claude Code code intelligence: https://code.claude.com/docs/en/plugins/code-intelligence
- svelte-check flags: `curl -sS https://raw.githubusercontent.com/sveltejs/language-tools/master/packages/svelte-check/README.md`
- `sv check`: `mcp__plugin_svelte-development_svelte__get-documentation` with `section: ["cli/sv-check"]`, or `curl -sS https://svelte.dev/docs/cli/sv-check/llms.txt`
- Language tools releases: https://github.com/sveltejs/language-tools/releases
