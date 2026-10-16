# Semantic execution facet

Read for code comprehension, impact analysis and edits. Apply the SKILL.md rules through the readiness loop and operation matrix below. Use only operation names the tool actually exposes; never invent one.

## Establish the tool boundary

Inspect the authorized workspace root, target files, relevant language/server profile, executable/version, project association and exposed capabilities. Use explicit absolute source paths when the wrapper requires them. Do not use the skill/plugin installation path as the project root. Consult the installed wrapper schema and official server documentation for unsupported or uncertain behavior.

The Claude Code `LSP` tool takes `operation`, `filePath`, `line` and `character` on every call, with `line` and `character` **1-based** as shown in editors. `workspaceSymbol` also needs a non-empty `query`. `incomingCalls` and `outgoingCalls` take the function's position directly. Raw LSP, as used by other clients, is zero-based, with character offsets in the negotiated encoding, and its hierarchy calls consume a prepared item. Do not mix the two conventions.

The tool exposes `goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, `prepareCallHierarchy`, `incomingCalls` and `outgoingCalls`. It is read-only, and diagnostics are not a callable operation (SKILL.md, "Treat LSP results as evidence, not the whole picture"). A call returns an error when no language server can start for the file.

Use document symbols or a targeted file/text search to locate the actual occurrence when coordinates are unknown. Confirm the intended symbol, avoiding comments, string lookalikes and shadowed names; SKILL.md says how to tell apart symbols that share a name.

## Readiness and bounded retry loop

This loop is the only statement of the retry bounds. A bound applies to one operation: the same operation on the same file and position.

1. Submit the relevant supported operation. Record target, content state and availability/partial-result metadata where exposed.
2. Classify the response. A valid empty result, wrong project/position, unsupported method, unavailable dependency, request failure, indexing, stale cache and truncation need different remedies. Check project inclusion and symbol position before blaming cold start.
3. When initialization/indexing or another transient state is evidenced, await the available readiness/progress signal. If the wrapper exposes no signal and cold start remains plausible after scope checks, repeat the same read-only operation with brief waits, for at most **four total attempts** (initial call plus three retries), within a **30-second recovery budget**. Honor server retry guidance when available. These bounds are workflow defaults, not LSP guarantees.
4. Stop early when usable results arrive. For an unsupported capability or invalid scope, correct the cause or use a documented fallback instead of repeating an identical failing request. Narrow a truncated query or collect supported continuation/partial results; repeated truncation does not increase coverage.
5. After exhaustion, record incomplete semantic evidence and proceed with safe independent work or native tooling. Never convert four empty responses into a global absence claim. If a scoped negative conclusion matters, corroborate with project membership, relevant declarations/exports, consumer checks and textual/dynamic boundaries.

Do not restart servers, reinstall packages, change configuration or loop indefinitely merely to make a query succeed. A necessary environment repair is a separate scoped decision. Before retrying any mutating operation, establish whether it already applied; this retry loop is for observations, not repeated edits.

## Operation selection matrix

Use every applicable row needed to resolve the change, and say for each whether you used it, skipped it as not applicable, or could not run it, with a reason. Record the relevant rows, not a transcript of every operation.

| Capability | `LSP` tool operation, or fallback | Trigger and evidence sought | Boundary to check |
| --- | --- | --- | --- |
| Definition | `goToDefinition` | Locate ownership before changing an unfamiliar symbol | Import alias versus actual declaration; multiple targets; generated or external code |
| Type information | `hover` | Understand declared and inferred types, overloads and call contracts | Actual occurrence, compiler version, contextual typing; hover is not use coverage |
| References | `findReferences` | Before a rename, deletion or contract change; locate consumers | Never the full list; confirm with Grep as SKILL.md says before a deletion or signature change |
| Implementation | `goToImplementation` | Interfaces, abstract members and polymorphic dispatch | Structural matches and runtime dispatch may exceed static results |
| Document symbols | `documentSymbol` | File structure and exact positions | Outline completeness; not a substitute for references |
| Workspace symbols | `workspaceSymbol` with `query` | Find relevant symbols across a project | Query limits, indexing and duplicate names (tell them apart by their import lines); follow to definitions |
| Callers | `incomingCalls` | Callers affected by a change to a callable contract | Supported server scope; dynamic calls |
| Callees | `outgoingCalls` | Callees and dependencies used by the changed function | Dynamic calls and callbacks may be incomplete |
| Type hierarchy | Not exposed: `goToImplementation`, `findReferences` and reading the declarations | Inherited contracts, when relevant | Structural typing |
| Rename | Not exposed: `findReferences` plus a repository text search, then manual edits | Authorized symbol rename | Public, string-keyed and generated consumers |
| Code actions and organize imports | Not exposed: edit by hand, following the project's formatter and linter | Import repairs and other fixes | Side-effect imports |
| Diagnostics | Not callable (SKILL.md); the native checker is the second observer, and the only one when none arrive | Baseline and post-edit feedback | Current content, framework checker ownership, files outside the edit |

Selection examples: a renamed exported function usually needs ownership, references, type/signature, `findReferences` confirmed by Grep and diagnostics; call hierarchy adds caller/callee evidence when the behavior or calling contract warrants it. A tsconfig change emphasizes file membership, type/diagnostic changes and consumers rather than renaming. A literal-only edit may need text search, not a symbol operation.

## Apply and observe

Apply a rename or signature change by the rules under "Map impact and control edits" in SKILL.md; also validate target paths, current content, unexpected public API changes and generated ownership.

Search relevant dynamic imports, serialized keys, routes, templates, test mocks and configuration alongside semantic references. Respect the project's formatter and import conventions. Removing an import can drop a side effect: check semantics and tests first.

After edits, refresh positions and synchronize content through the actual integration. Observe expected type/reference/diagnostic changes. Published or empty diagnostics alone do not establish freshness. Compare the same file and project against the native checker; preserve intentional environment differences. Then continue with verification.md, linked from SKILL.md.

## Official foundations

- [LSP specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/): lifecycle, synchronization, capabilities, progress, edits and language operations; use matching supported protocol version.
- [Official Position source](https://raw.githubusercontent.com/microsoft/language-server-protocol/gh-pages/_specifications/lsp/3.17/types/position.md): position indexing and encoding.
- [Official machine-readable model](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/metaModel/metaModel.json): parameter/result relationships. Inspect per-feature version/proposed markers; a versioned URL is not evidence that every exposed feature is stable or installed.

The protocol does not promise a universal “hydration” operation or a fixed number of requests until indexing is complete. Server-specific readiness and wrapper schemas remain separate evidence.
