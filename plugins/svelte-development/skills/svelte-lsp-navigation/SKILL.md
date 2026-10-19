---
name: svelte-lsp-navigation
description: Answers where a Svelte project's component, prop, function or type is defined, used or called, and what a change would break, through the Svelte language server and the project check. Use in a Svelte project for "is X used", "which files break if", renames, types and checking the project for errors.
license: MIT
---

# Svelte LSP navigation

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

All of these rules hold for every later turn of the task, not only the turn that loaded this skill, whichever Svelte skill loaded first. Depart from one only for a reason you state to the user.

### Ground rules for every Svelte task

0. **Route before the first tool call.** An audit or review of project files goes to the `svelte-code-auditor` agent; creating or changing `.svelte`, `.svelte.ts`, `.svelte.js` or SvelteKit route files beyond a line or two goes to the `svelte-component-editor` agent (Agent tool, without a `name`). Work inline only for a question, code pasted in the chat, a change of one or two lines, when the user asks you to, or when you already are one of these agents. [Who does the work](#who-does-the-work) gives the detail.
1. **Version first.** In a project, find the installed `svelte` and `@sveltejs/kit` before writing (`npm ls`, else the `package.json` ranges and the lockfile). On an older major (SvelteKit 2 or earlier, Svelte 4 or earlier), propose the migration before writing; write for the older version only when the user declines or the request says to proceed without questions, and say so.
2. **Docs before code.** Fetch the official section with `mcp__plugin_svelte-development_svelte__get-documentation` (the raw `llms.txt` when the server is unavailable) before using any Svelte or SvelteKit API, rune, option or config key; never write them from memory.
3. **Symbols through the language server.** Where something of the project is defined, used or called goes to the LSP tool first when the language server answers; Grep only for strings, route files, CSS classes, configuration, or a symbol that lives only in `.ts`/`.js` files no `.svelte` file imports, labelled as text matches.
4. **Autofixer on all you write or review.** Run `mcp__plugin_svelte-development_svelte__svelte-autofixer` with the full code (the remote tool treats a file path as code) and `desired_svelte_version` (5, or 4 for Svelte 4 code), or the local `svelte-mcp` with the file path when the code must not leave the machine, on every component or module you wrote, until it reports no issues. In a review, run it on every component and module in scope and report what it finds; name any file you skipped and why. Before sending more than 20 files of the user's code to the remote server, ask, and offer the local `svelte-mcp`.
5. **Done means checked.** When you change code in a project, finish only when the project check reports no error in the files you changed; a review or a question reports the check result instead. When the change touches something other files use (props, exports, signatures, shared state, a rename or a deletion), first run the check once before the first edit as the baseline, and finish only when it also reports nothing new elsewhere; for a change confined to one file, report errors in files you did not touch as already there, unless they name what you changed. Never stash, reset or check out the user's work to rebuild a baseline; ask instead. The check: `npm run check`; without that script, `npx --no-install svelte-kit sync`, then `npx --no-install svelte-check --tsconfig ./tsconfig.json` in SvelteKit, or `npx --no-install svelte-check` without SvelteKit, never chained with `&&`.

### Rules of this skill

1. **LSP first for every symbol question** (ground rule 3). The first code-navigation call is an LSP call, never Grep or a whole-file Read; Glob may first locate a `.svelte` file by name when the question names a component but not its path. Two exceptions, both stated to the user: the language server does not answer (step 0 of the [procedure](#procedure-for-a-symbol-question)), or the symbol lives only in `.ts`/`.js` files that no `.svelte` file imports, so there is no `.svelte` position to start from; then Grep comes first and its results are text matches.
2. **Start every call from a `.svelte` file.** The plugin maps only `.svelte` to the Svelte server. A call on a `.ts`, `.js`, `.svelte.ts` or `.svelte.js` file returns `No LSP server available for file type: .ts`; that is configuration, not a crash. From a `.svelte` position the server still finds definitions and references inside those files. Never map `.ts` to the Svelte server to work around this: it returns empty results for TypeScript files and hides their symbols; to start from TypeScript files the user installs a TypeScript language server. When a task involves symbols that live in `.svelte.ts`, `.svelte.js`, `.ts` or `.js` files, tell the user that the results start from `.svelte` positions or come from the project check.
3. **Load the tool before calling it.** The LSP tool may be deferred; a call without its loaded schema fails with invalid parameters (observed: eight failed calls in a row). Load it with ToolSearch first.
4. **Warm up before giving up, when the server answers.** An error or an empty result is retried as the [procedure](#procedure-for-a-symbol-question) says, up to three attempts per question, before any fallback. A missing server is not retried.
5. **Say when you fall back.** Grep results are text matches: tell the user "LSP unavailable, using text search" and what that can miss. Never present them as semantic answers.
6. **Grep alongside, never instead,** except in the two cases of rule 1. Use Grep only for the [blind spots](#blind-spots), next to the LSP results.
7. **Diagnostics are not a project check.** Diagnostics are pushed once after an edit, only for open files, and cannot be requested again. "No diagnostics" proves nothing about the project: run the [project check](#project-check).
8. **Never hide a problem.** No `--compiler-warnings x:ignore` or `--ignore` to get a check passing; ignore only a verified false positive, with the reason.
9. **Prove a clean result when a tool stays silent, with the probe for that tool.** A silent language server and a silent project check have different causes:
   - **Language server** (no diagnostics after an edit, empty answers): `documentSymbol` on a non-empty `.svelte` file of the project must list its symbols; an error that names the server (`No LSP server available`, `Executable not found in $PATH`) means it is missing. If it fails, follow [troubleshooting.md](references/troubleshooting.md). Never probe with `command -v svelteserver` in Bash: a sandboxed Bash cannot follow a symlinked global install and prints nothing while the server works.
   - **Project check** (nothing reported after a change that must break): the cause is almost always in the project, not in svelte-check. In a SvelteKit project, run `npx --no-install svelte-kit sync` and check again, because missing generated types hide errors (a project on Svelte alone has no sync to run); read the last line, `COMPLETED <n> FILES …`, and confirm the edited file is inside the tsconfig `include` (SvelteKit 3 projects extend `$app/tsconfig`, SvelteKit 2 projects `./.svelte-kit/tsconfig.json`); confirm that `npm run check` really runs svelte-check (read the script in `package.json`); in a monorepo, run it from the app folder.
10. **No installs without consent.** Never install `svelte-language-server`, `sv` or any package; tell the user what is missing.

### Gotchas

- The server needs `svelteserver` on the user's PATH (`npm install -g svelte-language-server`, done by the user) and TypeScript in the project.
- The server's workspace is the directory Claude Code was started in. In a monorepo whose Svelte app lives in a subfolder, results that ignore the app's `tsconfig` or `vite.config` may come from a session started at the repository root (not tested on a monorepo); tell the user, and run the project check from the app folder.
- The plugin restarts a crashed server up to three times, and a request the server never answers fails after 60 seconds (Claude Code's default); after that, ask the user to run `/reload-plugins`.
- Cloud sessions do not start plugin language servers: use the project check there.
- The language server and svelte-check lag SvelteKit 3, so some results are wrong rather than missing. Issues to re-check in `sveltejs/language-tools` before citing them: moving, creating or deleting route files can crash the server (#3108); config reading from `vite.config` can be wrong (#3080); type arguments on `$props()` make destructured props `any` (#3124); TypeScript 7 crashes svelte-check without `--tsgo` (#3063). If results look wrong after such changes, ask the user to run `/reload-plugins` and confirm with the project check.

## Contents

- [Who does the work](#who-does-the-work)
- [Where things are](#where-things-are)
- [Calling the LSP tool](#calling-the-lsp-tool)
- [Procedure for a symbol question](#procedure-for-a-symbol-question)
- [Procedure for a change](#procedure-for-a-change)
- [Project check](#project-check)
- [Blind spots](#blind-spots)

## Who does the work

| Situation | Who | How |
|---|---|---|
| A question about where code is, what calls it, or what type it has | You | This skill, inline: answers are short and the main conversation needs them |
| The answer leads to editing `.svelte`, `.svelte.ts` or `.svelte.js` files beyond a line or two | `svelte-component-editor` agent | Agent tool, `subagent_type: "svelte-development:svelte-component-editor"`, with the edit set you found |
| The user wants a review or audit of the code, not a change | `svelte-code-auditor` agent | Agent tool, `subagent_type: "svelte-development:svelte-code-auditor"` |
| You already are one of these agents | You | Never delegate further |

Hand the agent the locations you found (file and line), so it does not repeat the search. Call it without a `name`: a named call can start an agent-team teammate instead of a subagent, and a teammate gets none of the agent's preloaded skills.

## Where things are

- [references/operations.md](references/operations.md): read when you need to see what an operation returns (real output on the bundled fixture), or a result does not match what you expected.
- [references/troubleshooting.md](references/troubleshooting.md): read when a call errors, returns nothing unexpectedly, or diagnostics never appear.
- `${CLAUDE_SKILL_DIR}/fixtures/kit3-app`: the SvelteKit 3 project behind the examples in operations.md; it is not meant to be installed in the user's project.
- The `svelte-best-practices` skill for the rules when fixing what diagnostics report; the `svelte-docs-and-autofixer` skill for the docs and the autofixer.

The sibling skills (`svelte-best-practices`, `svelte-docs-and-autofixer`) are named `svelte-development:<skill>`. When a step needs one that is not loaded yet, load it with the Skill tool:

```text
Skill
  skill: "svelte-development:svelte-best-practices"
```

## Calling the LSP tool

Load it when it is not in your tool list:

```text
ToolSearch
  query: "select:LSP"
```

Every call takes `operation`, `filePath`, `line` and `character`; positions are 1-based, as an editor shows them, on the first character of the symbol's name. `workspaceSymbol` also takes a non-empty `query`.

```text
LSP
  operation: "findReferences"
  filePath: "src/lib/components/CounterButton.svelte"
  line: 8
  character: 5
```

| Operation | Answers | Use before | Instead of |
|---|---|---|---|
| `documentSymbol` | The outline of one component: script symbols, props, markup elements, with lines | Working in a long component; getting an exact position | Reading the whole file |
| `workspaceSymbol` | Where a symbol is declared, by name (`query: "formatCount"`) | Finding related code | Glob or Grep for a name |
| `goToDefinition` | The declaration of a usage, through `#lib` imports and component tags | Changing code you did not write | Grep, then Read the matches |
| `findReferences` | Every usage in `.svelte` and `.ts` files, including props passed by parents | Renaming, changing a signature, deleting | Grep, which also matches comments and strings |
| `hover` | The inferred type, including `$props()` and rune-derived types | Writing code that depends on a type | Tracing types by hand |
| `prepareCallHierarchy` → `incomingCalls` / `outgoingCalls` | Callers per module with call positions; what a function calls | Deciding whether a function is dead | Grepping call sites |
| `goToImplementation` | Not observed from a `.svelte` position | — | `findReferences` on the interface member |

## Procedure for a symbol question

Choose the procedure first: a question about the code (where, who calls, what type, is it used) follows this one; a change to a symbol other files use follows the [procedure for a change](#procedure-for-a-change); a request to check the project for errors goes to the [project check](#project-check).

Run these in order and do not skip a step:

0. **Is the server there?** Once per session, before the first question: load the LSP tool if it is deferred (step 1) and call `documentSymbol` on a non-empty `.svelte` file of the project. Symbols mean the server answers. An empty result or a start-up error can be a server still starting: warm it up as step 4 says before deciding. An error that names the server (`No LSP server available`, `Executable not found in $PATH`) means there is no code intelligence in this session: skip steps 2 to 4, tell the user once that installing `svelte-language-server` (done by them) with `svelteserver` on the `PATH` of the shell they start `claude` from enables it, and go to step 5. Never probe with `command -v svelteserver` in Bash: a sandboxed Bash cannot follow a symlinked global install and prints nothing while the server works.
1. **Load** the LSP tool if it is deferred. If ToolSearch does not return it, go to step 5.
2. **Locate** the symbol: `documentSymbol` on the `.svelte` file that uses it, or `workspaceSymbol` with its name from any `.svelte` file. Take the exact line and character from the result.
3. **Ask** the question: `findReferences`, `goToDefinition`, `hover` or `incomingCalls` at that position.
4. **Warm up if it fails.** On an error or an empty result: `documentSymbol` on the file (opens it and confirms the position), `hover` at the position (confirms the symbol), then repeat step 3. Stop after three attempts on the same question.
5. **Fall back, and say so.** Only after step 0, 1 or 4 fails: tell the user the language server is not answering and why, if the error says. Then use the project check for diagnostics, Grep for locations (stating they are text matches), or the Svelte MCP docs tools for API questions.
6. **Add the blind spots.** Before answering "unused" or listing an edit set, Grep the bare name for the [blind spots](#blind-spots). Before saying a component is not used dynamically, run `documentSymbol` on each file that imports it: the server sees components held in variables, `<svelte:element>` and `{#await}` blocks.
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

Copy this checklist when a change touches a symbol other files use. Steps 4 to 6 make the project check prove the edit set by breaking it on purpose; use them for a rename, a signature change or a deletion in a project that has a project check, and skip them for a change no other file uses.

```
- [ ] 1 Locate     documentSymbol or workspaceSymbol(query) from a .svelte file, for the exact position
                   (no server: Grep the name, label the results as text matches, and let steps 4-6 prove them)
- [ ] 2 Impact     findReferences from a .svelte usage (and incomingCalls for functions)
- [ ] 3 Blind      Grep the bare name for the blind spots below
- [ ] 4 Baseline   run the project check before editing; note the errors already there
- [ ] 5 Break      change only the declaration; run the project check again
- [ ] 6 Compare    every new error must sit at a site from steps 2-3; an error elsewhere is a use the LSP missed,
                   a listed site with no error is one the check cannot see; both join the edit set
- [ ] 7 Edit       change every site in the edit set
- [ ] 8 Confirm    the project check is back to the baseline and the changed files show no diagnostics; run it once more
                   after fixing errors, because one error can hide another
```

**Done when**, for a rename, a signature change or a deletion, the project check ran at least at baseline, break and confirm, and the last run matches the baseline. There is no rename operation: a rename is steps 2 to 8, including the props passed to the component and destructured in `$props()`. [operations.md](references/operations.md), "Prove it", shows a worked example.

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

- `svelte-check` is the check in every Svelte project; `svelte-kit sync` exists only in a SvelteKit one, so never chain them with `&&`: in a project on Svelte alone the sync fails and the check would never run.
- In a SvelteKit project, without `svelte-kit sync` the generated `./$types` and `$app/types` are missing and the check reports false errors.
- `npx sv check` forwards to the same tool but downloads `sv` when the project does not depend on it: ask before running it.
- Inside Claude Code, svelte-check prints its machine format by default, because it detects the `CLAUDECODE` environment variable. Parse these lines; pass `--output human` only for the user:

  ```text
  ERROR "src/routes/+page.svelte" 13:26 "Type 'number' is not assignable to type 'string'."
  COMPLETED 177 FILES 1 ERRORS 0 WARNINGS 1 FILES_WITH_PROBLEMS
  ```

- Useful flags: `--threshold error`, `--fail-on-warnings`, `--compiler-warnings <code>:ignore|error`, `--diagnostic-sources "svelte,ts"`, `--tsgo` (TypeScript 7, experimental).

## Blind spots

Uses the server cannot see, because they live in strings, file names or configuration. Grep for them, alongside the LSP results, before a rename or delete:

- **Route files**: SvelteKit finds `+page.svelte`, `+layout.svelte`, `+server.ts` and hooks by file name, so nothing references them.
- **Paths in strings**: `import()` paths, `import.meta.glob` patterns, route paths in `href`, `goto()` and `resolve()`. In step 6 of the procedure for a change, the project check reports a literal `import()` of a missing file, but never a glob pattern or a route path.
- **Calls through an alias**: callers of `obj.fn()` when `fn` was stored in an object; follow the alias with `findReferences`.
- **Strings and attributes**: CSS class names (including Tailwind classes in `class` objects and arrays), `data-sveltekit-*` attributes.
- **Configuration and scripts**: `vite.config`, `package.json` scripts and `imports`, `svelte-check --ignore` lists, CI files.

Dynamic Svelte code is not a blind spot by default: a component held in a variable, `<svelte:element this={tag}>` and `{#await}` blocks are seen. Run `documentSymbol` and `findReferences` before concluding that the server cannot see it; [operations.md](references/operations.md) lists what is and is not seen.

Sources: the Claude Code LSP tool (its runtime schema and observed results), https://code.claude.com/docs/en/plugins/code-intelligence, https://code.claude.com/docs/en/plugins-reference (plugin agents are named `<plugin>:<agent>`), svelte-check `src/options.ts` (machine output when `CLAUDECODE=1`).
