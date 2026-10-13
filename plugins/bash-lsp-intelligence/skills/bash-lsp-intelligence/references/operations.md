# Shell semantic operations

Use the client's actual request schema. The Claude common parameters are an absolute `filePath` and 1-based UTF-16 `line`/`character`; raw LSP uses a URI and 0-based position. A missing hover does not prove that a function is unserved; confirm it with its declaration and other supported operations.

## Capability checks

Read the `LSP` tool's input schema to learn which operations and fields it accepts; use only those. Then call the operation. Claude Code returns an error result for every LSP call on a file whose language server it can't start. Treat an error, or a result saying the method is unsupported, as "not supported" and use the fallback for that operation; an empty result is different and needs the checks in SKILL.md. Do not promise interface implementations or inferred types: shell has neither.

| Operation not supported | Fallback |
|---|---|
| `prepareCallHierarchy`, `incomingCalls`, `outgoingCalls` | `findReferences` for callers; `goToDefinition` on each call in the function body for callees |
| `goToImplementation` | `goToDefinition` and the source relationships |
| `workspaceSymbol` | Text search for the name to find candidate files, then `documentSymbol` on each |
| `hover` | The declaration from `goToDefinition` |

## Workspace symbol search

Pass the symbol name as `workspaceSymbol`'s `query` parameter (Claude Code 2.1.162 and later). If the schema has no `query` field or the search returns nothing, use the text-search fallback above. When only a filename is known, request its outline before guessing a function or reading an entire long script. For ambiguous names, resolve each declaration before treating results as one symbol.

## Rename and imports

Shell has sourced files and command resolution, not a generic organize-imports transformation. Reordering `source` statements can change variables, options, registrations, and side effects. Do not apply a language-inappropriate import action.

A server rename action can mix names if its reference model is broad. Preview the proposed edits and correlate definitions/source chains before applying an exposed, authorized action. If the client does not expose rename, make explicit scoped edits after semantic discovery.

Use text search for trap command strings, CI commands, Makefiles, launch configurations, and extensionless scripts after checking semantic coverage. Respect authorized paths and secret-bearing file boundaries. Report the relevant limitation once; ordinary read/search steps do not need repeated fallback narration.
