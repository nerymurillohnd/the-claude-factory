---
name: svelte-lsp-intelligence
description: Answers where a Svelte project's component, prop, function or type is defined, used or called, and what a change would break, through the Svelte language server and the project check. Use in a Svelte project for "is X used", "which files break if", renames, types and checking the project for errors.
license: MIT
---

# Svelte LSP intelligence

## Overview

The contract for questions about the project's own code. The plugin starts the Svelte language server (`svelteserver --stdio`) for `.svelte` files; it answers by symbol, not by text, so it sees through imports, re-exports, `#lib` aliases and TypeScript inside `<script lang="ts">`. Grep matches strings and also hits comments, so it is the fallback, not the first tool. The project check proves a change across every file.

## When to use it and when not

| Use it | Do not use it |
|---|---|
| Where a component, prop, function or type of the project is defined or used | For how a Svelte or SvelteKit API works: that is the `svelte-docs-and-autofixer` skill |
| Before renaming, changing a signature or deleting code | For writing Svelte code by the current rules: that is the `svelte-best-practices` skill |
| Reading an inferred type, or a long component's outline | For text that is not a symbol (route paths, CSS classes): Grep, per [blind spots](#blind-spots) |
| Proving the project has no type or Svelte errors after a change | |

## Governance rules

Depart from any rule that holds here, ground rule or rule of this skill, only for a reason you state to the user.

### Ground rules for every Svelte task

The ground rules (0 to 5) live in the `svelte-development:svelte-best-practices` skill. A question about the project's code needs only this skill's rules below. Before writing, changing or reviewing Svelte code, load that skill with the Skill tool unless it is already in your context; its ground rules then hold for this skill too, including rule 0 on who does the work.

### Rules of this skill

1. **LSP first for every symbol question.** The first code-navigation call is an LSP call, never Grep or a whole-file Read. Glob may first locate a `.svelte` file by name, and a Read limited to one line (`offset` and `limit`) may give the column of a symbol on a line an LSP result named. Two exceptions, both stated to the user: the language server does not answer (step 1 of the [procedure](#procedure-for-a-symbol-question)), or `workspaceSymbol` finds the symbol only in `.ts`/`.js` files and no `.svelte` file imports it, so there is no `.svelte` position to start from; then Grep comes next and its results are text matches.
2. **Start every call from a `.svelte` file.** The plugin maps only `.svelte` to the Svelte server. A call on a `.ts`, `.js`, `.svelte.ts` or `.svelte.js` file returns `No LSP server available for file type: .ts`; that is configuration, not a crash. From a `.svelte` position the server still finds definitions and references inside those files. Never map `.ts` to the Svelte server to work around this: it returns empty results for TypeScript files and hides their symbols; to start from TypeScript files the user installs a TypeScript language server. A TypeScript server sees `.svelte` callers only when the project's tsconfig lists `typescript-svelte-plugin` in `compilerOptions.plugins` and the package is installed in the project (observed with typescript-language-server 6.0.2: `findReferences` from a `.ts` file found 2 references without it, every `.svelte` caller with it); it sees saved files only. When a task involves symbols that live in `.svelte.ts`, `.svelte.js`, `.ts` or `.js` files, tell the user that the results start from `.svelte` positions or come from the project check, and that a TypeScript language server with `typescript-svelte-plugin` closes that gap (rule 11: the user installs both).
3. **Load the tool before calling it, and send the session's first call alone.** The LSP tool may be deferred; load it with ToolSearch first. The first LSP call of a session starts the server: send it by itself, not in parallel with other LSP calls, and run the next ones after it answers.
4. **Warm up before giving up, when the server answers.** An error or an empty result is retried as step 4 of the [procedure](#procedure-for-a-symbol-question) says, for at most three attempts of the question call in total, the first one included, before any fallback; the `documentSymbol` and `hover` calls before each retry do not count. A missing server is not retried.
5. **Say when you fall back.** Grep results are text matches: tell the user "LSP unavailable, using text search", why if the error says, and what text search can miss. Never present them as semantic answers.
6. **Grep alongside, never instead,** except in the two cases of rule 1. Use Grep only for the [blind spots](#blind-spots), next to the LSP results.
7. **Diagnostics are not a project check.** The server pushes diagnostics after an edit, only for open files, possibly on a later turn or not at all, and they cannot be requested again. "No diagnostics" right after an edit proves nothing about the edit or the project: run the [project check](#project-check). One Svelte or configuration error can also hide the file's other Svelte compiler diagnostics, while TypeScript and CSS diagnostics still appear ([troubleshooting.md](references/troubleshooting.md), "Diagnostics that hide others").
8. **Never hide a problem.** No `--compiler-warnings x:ignore` or `--ignore` to get a check passing; ignore only a verified false positive, with the reason.
9. **Prove a clean result when a tool stays silent, with the probe for that tool.** A silent language server and a silent project check have different causes:
   - **Language server** (no diagnostics after an edit, empty answers): `documentSymbol` on a non-empty `.svelte` file of the project must list its symbols. On that `.svelte` call, `No LSP server available` or `Executable not found in $PATH` means the server is missing. If it fails, follow [troubleshooting.md](references/troubleshooting.md). A server that answers can still be silent or wrong when the configuration fails to load, when it sets no `preprocess` and the file has a `lang` attribute (`lang="ts"` included), or when the project's `svelte` cannot be loaded; troubleshooting.md covers all three. Never probe with `command -v svelteserver` in Bash: it checks the Bash command's `PATH`, not the server Claude Code started, so neither result proves anything about the server.
   - **Project check** (nothing reported after a change that must break): the cause is almost always in the project, not in svelte-check. In a SvelteKit project, run `npx --no-install svelte-kit sync` and check again, because missing generated types hide errors (a project on Svelte alone has no sync to run); read the last line, `COMPLETED <n> FILES …`, and confirm the edited file is inside the tsconfig `include` (SvelteKit 3 projects extend `$app/tsconfig`, SvelteKit 2 projects `./.svelte-kit/tsconfig.json`); confirm that `npm run check` really runs svelte-check (read the script in `package.json`); in a monorepo, run it from the app folder.
10. **Changes outside Edit and Write may not reach the server.** Change files with Edit and Write when you can. Files changed by Bash, git, a code generator or a formatter, and changes to `vite.config`, `svelte.config` or a tsconfig, can leave the server's answers stale. For changed files, trust the project check and a Read of the file over LSP results; when the server's answers contradict what the files or the configuration say, ask the user to run `/reload-plugins`.
11. **No installs without consent.** Never install `svelte-language-server`, `svelte-check`, `sv` or any package; tell the user what is missing.

### Gotchas

- The server needs `svelteserver` on the user's PATH (`npm install -g svelte-language-server`, done by the user), version 0.18.5 or later, and Node 18 or later. Older servers fail without an error in two common cases: before 0.18.4 they do not read SvelteKit 3's configuration from `vite.config`, and before 0.18.5 they find no configuration when the project sits under a directory whose name starts with a dot, such as Claude Code's `.claude/worktrees/`. It runs its own TypeScript, a peer dependency npm installs with it (5.9 or 6, not 7), so the project needs no TypeScript of its own for the server.
- The server starts on the first LSP call or the first edit of a `.svelte` file, and its first answer can come late; that is what the warm-up is for.
- The server's workspace is the directory Claude Code was started in. In a monorepo whose Svelte app lives in a subfolder, results that ignore the app's `tsconfig` or `vite.config` may come from a session started at the repository root (not tested on a monorepo); tell the user, and run the project check from the app folder.
- The plugin restarts a crashed server up to three times, and a request the server never answers fails after 60 seconds (Claude Code's default). When requests keep timing out or the server stays down after its restarts, ask the user to run `/reload-plugins`.
- The language server and svelte-check lag SvelteKit 3, so some results are wrong rather than missing: after moving, creating or deleting route files, with the Svelte config in `vite.config`, with type arguments on `$props()`, and with TypeScript 7. The issues behind these, and how to check whether each is still open, are in the "Known open issues" section of [troubleshooting.md](references/troubleshooting.md). If results look wrong after such changes, ask the user to run `/reload-plugins` and confirm with the project check.

## Contents

- [Who does the work](#who-does-the-work)
- [Where things are](#where-things-are)
- [Calling the LSP tool](#calling-the-lsp-tool)
- [Procedure for a symbol question](#procedure-for-a-symbol-question)
- [Procedure for a change](#procedure-for-a-change)
- [Project check](#project-check)
- [Blind spots](#blind-spots)

## Who does the work

Answer questions about where code is, what calls it or what type it has yourself, with this skill: the answers are short and the main conversation needs them. An edit beyond one or two lines in total, or a review, goes to an agent by ground rule 0 of `svelte-best-practices`, whose "Who does the work" table is the single copy. When an answer leads to an edit, hand the `svelte-component-editor` agent the edit set you found (file and line); it runs the baseline, break and confirm steps of the [procedure for a change](#procedure-for-a-change) itself, so do not run them first.

## Where things are

- [references/operations.md](references/operations.md): read when you need to see what an operation returns (real output observed on a SvelteKit 3 test project), or a result does not match what you expected.
- [references/troubleshooting.md](references/troubleshooting.md): read when a call errors, returns nothing unexpectedly, or diagnostics never appear.
- [references/rename.md](references/rename.md): read before a rename or move that involves a prop with shorthand attributes, a store or a component file.
- The `svelte-best-practices` skill for the rules when fixing what diagnostics report; the `svelte-docs-and-autofixer` skill for the docs and the autofixer.

The sibling skills are `svelte-development:svelte-best-practices` and `svelte-development:svelte-docs-and-autofixer`.

## Calling the LSP tool

Load it when it is not in your tool list:

```text
ToolSearch
  query: "select:LSP"
```

Point at the symbol's name; its first character is the safest position.

```text
LSP
  operation: "findReferences"
  filePath: "src/lib/components/CounterButton.svelte"
  line: 8
  character: 5
```

| Operation | What to know about its result | Use before | Instead of |
|---|---|---|---|
| `documentSymbol` | A flat outline with a line per symbol, no column, that merges markup elements, CSS selectors and script symbols (the script ones under `script`); the server spends about 1 s on each call | Working in a long component; finding the line of a symbol | Reading the whole file |
| `workspaceSymbol` | The file and line where a name is declared, no column; often a `.ts` file, which is not a starting position. It searches only projects already loaded, so open a `.svelte` file of the project first (step 1 does), and returns at most 256 results per project | Finding which file declares a symbol | Glob or Grep for a name |
| `goToDefinition` | `file:line:column` of the declaration, through `#lib` imports; from a component tag, the component file at its first line, not a symbol | Changing code you did not write | Grep, then Read the matches |
| `findReferences` | `line:column` of every usage in `.svelte` and `.ts` files, including props passed by parents. On line 1, character 1 of a component, or on its `<script` tag, it lists where that component is used (imports and tags) instead | Renaming, changing a signature, deleting; finding where a component is used | Grep, which also matches comments and strings |
| `hover` | The inferred type on an identifier or a `{expression}`; on an element, attribute, directive or block keyword (`{#if}`, `bind:`), static documentation, not a type | Writing code that depends on a type | Tracing types by hand |
| `incomingCalls` / `outgoingCalls` | Callers per module with call positions; call directly, no `prepareCallHierarchy` first. A function's line includes its leading comment; calls from markup or top-level script show as the whole component | Deciding whether a function is dead | Grepping call sites |
| `goToImplementation` | The classes or methods that implement an interface or interface member, including ones in `.svelte.ts` modules. An empty result does not prove there are none: confirm with `findReferences` on the member | Changing an interface | `findReferences` alone |

## Procedure for a symbol question

Choose the procedure first: a question about the code (where, who calls, what type, is it used) follows this one; a change to a symbol other files use follows the [procedure for a change](#procedure-for-a-change); a request to check the project for errors goes to the [project check](#project-check).

Run these in order; step 1 runs once per session:

0. **Load** the LSP tool if it is deferred. If ToolSearch does not return it, go to step 5.
1. **Is the server there?** Once per session, before the first question (a subagent is its own session, so it runs this step too): call `documentSymbol` on a non-empty `.svelte` file of the project, alone (rule 3), up to three times. Symbols mean the server answers. An empty result or a start-up error on the first calls can be a server still starting. `No LSP server available` or `Executable not found in $PATH` on this `.svelte` call means there is no code intelligence in this session: tell the user once that installing `svelte-language-server` (done by them) with `svelteserver` on the `PATH` of the shell they start `claude` from enables it, and go to step 5.
2. **Locate** a `.svelte` position for the symbol. `documentSymbol` on a `.svelte` file that uses it gives the line; read that one line (Read with `offset` and `limit`) for the column. When you do not know which file uses it, `workspaceSymbol` with its name finds the declaring file; if that is a `.ts` file, find a `.svelte` file that imports it, or take rule 1's exception. For where a component is used, `findReferences` on line 1, character 1 of the component's own file lists every import and tag.
3. **Ask** the question: `findReferences`, `goToDefinition`, `hover` or `incomingCalls` at that position.
4. **Warm up if it fails.** On an error or an empty result: `documentSymbol` on the file (opens it and confirms the line), `hover` at the position (confirms the symbol), then repeat step 3; stop after three attempts of the question call in total (rule 4).
5. **Fall back, and say so** (rule 5). Only after step 0, 1 or 4 fails: use the project check for diagnostics and Grep for locations, stating they are text matches.
6. **Add the blind spots.** Before answering "unused" or listing an edit set, Grep the bare name for the [blind spots](#blind-spots). Before saying a component is not used dynamically, run `findReferences` on its import in each file that imports it, and on any variable that holds it; `documentSymbol` helps find those variables.
7. **Answer with this default structure**, so the user can tell semantic results from text matches; drop the lines that do not apply:

   ```markdown
   **`<symbol>`** (<kind>), declared at <file>:<line>

   | # | File:line | Use | Found by |
   |---|---|---|---|
   | 1 | src/routes/+page.svelte:13 | passes `label` | LSP findReferences |
   | 2 | src/lib/menu.ts:8 | route path in a string | Grep (text match) |

   Blind-spot search: `<pattern>` → <matches, or "none">
   Not covered: <what neither the language server nor Grep can see, or "nothing known">
   ```

## Procedure for a change

Copy this checklist when a change touches a symbol other files use. Steps 4 to 6 make the project check prove the edit set by breaking it on purpose; use them for a rename, a signature change or a deletion in a project that has a project check, and skip them for a change no other file uses. When the edit itself goes to the `svelte-component-editor` agent (ground rule 0), you run steps 1 to 3 and hand it the edit set; the agent runs steps 4 to 8.

```
- [ ] 1 Locate     a .svelte position for the symbol (step 2 of the question procedure)
                   (no server: Grep the name, label the results as text matches, and let steps 4-6 prove them)
- [ ] 2 Impact     findReferences from a .svelte usage (and incomingCalls for functions); when a TypeScript server
                   is active too, also from the declaring .ts file, and take the union
- [ ] 3 Blind      Grep the bare name for the blind spots below
- [ ] 4 Baseline   run the project check before editing; note the errors already there
- [ ] 5 Break      change only the declaration, meaning every site in the file that declares the symbol
                   (its type, default and destructuring); run the project check again
- [ ] 6 Compare    only sites outside the declaring file count: every new error must sit at a site from steps 2-3;
                   an error elsewhere is a use the LSP missed, a listed site with no error is one the check
                   cannot see; both join the edit set
- [ ] 7 Edit       change every site in the edit set
- [ ] 8 Confirm    the project check is back to the baseline (errors already there may remain, nothing new), and
                   the changed files show no new diagnostics; run it once more after fixing errors, because one
                   error can hide another
```

**Done when**, for a rename, a signature change or a deletion, the project check ran at least at baseline, break and confirm, and the last run matches the baseline. There is no rename operation: a rename is steps 2 to 8, including the props passed to the component and destructured in `$props()`. For shorthand attributes, a store or a component file move, read [rename.md](references/rename.md) first. [operations.md](references/operations.md), "Prove it", shows a worked example.

## Project check

Run it from the project root, choosing the first command that applies:

```sh
# 1. The project has a check script (look in package.json "scripts")
npm run check

# 2. No check script, SvelteKit project: generate its types, then run the svelte-check the project already has
npx --no-install svelte-kit sync
npx --no-install svelte-check --tsconfig ./tsconfig.json

# 3. No check script, Svelte without SvelteKit: there is no sync, svelte-check is the whole check
npx --no-install svelte-check
```

These are the commands of ground rule 5 in `svelte-best-practices`, repeated here because a question can run without that skill.

- `svelte-check` is the check in every Svelte project; `svelte-kit sync` exists only in a SvelteKit one, so never chain them with `&&`: in a project on Svelte alone the sync fails and the check would never run.
- In a SvelteKit project, without `svelte-kit sync` the generated `./$types` and `$app/types` are missing and the check reports false errors.
- When the project has no svelte-check, `--no-install` makes the command fail: tell the user and report the result as unchecked (rule 11).
- `npx sv check` forwards to the same tool but downloads `sv` when the project does not depend on it: ask before running it.
- Inside Claude Code, svelte-check prints its machine format by default, because it detects the `CLAUDECODE` environment variable. Each line starts with a timestamp in milliseconds; parse what follows it, and pass `--output human` only for the user. The counts depend on the project and its dependencies:

  ```text
  1760845342123 ERROR "src/routes/+page.svelte" 13:26 "Type 'number' is not assignable to type 'string'."
  1760845342130 COMPLETED 177 FILES 1 ERRORS 0 WARNINGS 1 FILES_WITH_PROBLEMS
  ```

- Useful flags: `--threshold error`, `--fail-on-warnings`, `--compiler-warnings <code>:ignore|error` (rule 8 limits `ignore`), `--diagnostic-sources "js,svelte"` (the values are `js`, which includes TypeScript, `svelte` and `css`; svelte-check drops any other value without a warning, so a wrong one hides those diagnostics), `--tsgo` (TypeScript 7 support; experimental, and it needs TypeScript 7 and TypeScript 6 both installed).

## Blind spots

Uses the server cannot see, because they live in strings, file names or configuration. Grep for them, alongside the LSP results, before a rename or delete:

- **Route files**: SvelteKit finds `+page.svelte`, `+layout.svelte`, `+server.ts` and hooks by file name, so nothing references them.
- **Paths in strings**: `import()` paths, `import.meta.glob` patterns, route paths in `href`, `goto()` and `resolve()`. In step 6 of the procedure for a change, the project check reports a literal `import()` of a missing file, but never a glob pattern or a route path.
- **Calls through an alias**: callers of `obj.fn()` when `fn` was stored in an object; follow the alias with `findReferences`.
- **Strings and attributes**: CSS class names (including Tailwind classes in `class` objects and arrays), `data-sveltekit-*` attributes. The server links no CSS: a class, id or custom property in `<style>` has no references or definition, so Grep connects it to `class=`, `class:` and class objects.
- **Configuration and scripts**: `vite.config`, `package.json` scripts and `imports`, `svelte-check --ignore` lists, CI files.

Dynamic Svelte code is not a blind spot by default: a component held in a variable, `<svelte:element this={tag}>` and `{#await}` blocks are seen through `findReferences` and `goToDefinition`. Run them before concluding that the server cannot see it; [operations.md](references/operations.md) lists what is and is not seen.

Sources: the Claude Code LSP tool (its runtime schema and observed results), https://code.claude.com/docs/en/plugins/code-intelligence, https://code.claude.com/docs/en/plugins-reference (plugin agents are named `<plugin>:<agent>`), svelte-check `src/options.ts` (machine output when `CLAUDECODE=1`) and README (`--tsgo`), and the svelte-language-server 0.18.5 source (`src/plugins/`, `PluginHost.ts`).
