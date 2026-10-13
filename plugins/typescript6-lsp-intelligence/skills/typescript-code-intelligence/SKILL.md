---
name: typescript-code-intelligence
description: "Navigate and repair TypeScript/JavaScript. Use for \"rename this function\", \"find all usages\", \"find interface implementations\", \"explain this type\", \"fix error TS2322\", or \"why does this JS file have no type diagnostics?\" in TS/JS code."
---

# TypeScript and JavaScript Code Intelligence

Repair findings introduced by this task in changed files and affected callers. Report pre-existing findings separately; repair them only when the requested work covers them. A required check remains failed while its findings remain. Code edits are authorized when requested or necessary for that work; environment, dependency and checking-policy changes require explicit task scope.

## Semantic tool use

Prefer LSP navigation: definitions and references follow symbol identity and types, whereas matching text can merge unrelated names or miss aliases. Read source bodies for behavior; use the available text/file search for registrations, dynamic names, or files outside server coverage.

Choose the operation for the question: `goToDefinition` and `hover` establish identity/type; `findReferences` finds consumers; `documentSymbol` outlines a file and `workspaceSymbol` locates named symbols. For implementation/call analysis, use exposed `goToImplementation`, `prepareCallHierarchy`, `incomingCalls`, and `outgoingCalls` capabilities.

Read the loaded tool definition before calling it. When it exposes `filePath`, `line`, and `character`, use an absolute authorized source path and its declared line/column indexing. If it declares 1-based positions, pass 1-based positions. Use its declared encoding; do not import assumptions from raw LSP or another client. Add a query or hierarchy item only when that schema accepts it. An explicit unsupported-method response calls for supported alternatives; other errors require checking the request or server state and do not prove that capability is absent. A stable short result still needs the language-specific checks below.

## Establish consumers before a rename or deletion

1. Identify the declaration and query references, checking local aliases and re-export barrels.
2. If a public export has only a definition result, establish which configured projects are loaded. Load a representative file from another implicated package and query that context; repeatedly querying the first project can leave the same gap.
3. Inspect package exports, declaration entry points and framework consumers. A plain TS/JS server cannot establish template usage it does not serve; use a framework-aware client or inspect that boundary explicitly.

## Match diagnostics to the program

`allowJs` admits JavaScript to the program. `checkJs` or a file's `@ts-check` enables its ordinary JavaScript type diagnostics; a listed JS file with checking off has not passed that checking. Some syntax/module diagnostics can still occur without checkJs. A tsconfig can select files by defaults without an explicit `files` or `include`.

With the declared compiler and the intended configuration, inspect configuration, confirm source membership, then compile:

```text
tsc --showConfig -p /absolute/tsconfig.json
tsc --listFilesOnly -p /absolute/tsconfig.json
tsc --noEmit --pretty false -p /absolute/tsconfig.json
```

Keep each status and complete output. The first two commands do not type-check. When a moved file is absent from the compiler's program, that compiler's success cannot dismiss a current diagnostic in the moved file. For an explicitly supplied compiler/profile, use that tool and context rather than silently substituting project-local settings.

## Use the server interface for the selected generation

Native TypeScript 7 exposes LSP through `tsc --lsp --stdio`. A legacy typescript-language-server integration expects `tsserver`; pointing it at a native package without that interface is not a compatible substitution. Check which executable/version the configured command actually resolves to.

Repair external values by runtime validation and narrowing from `unknown`; keep return/rejection contracts and inspect affected callers. Read [repair.md](references/repair.md) for strict profiles, JSON boundaries, import actions and checking scope. Use the declared formatter/linter separately from compiler diagnostics, then test the changed behavior.

Use [sources.md](references/sources.md) when generation compatibility or an installed option needs confirmation.
