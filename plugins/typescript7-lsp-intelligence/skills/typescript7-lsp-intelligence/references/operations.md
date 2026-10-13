# Semantic requests and import actions

Use the client's actual schema. Claude's common fields are `filePath`, `line`, and `character`, with an absolute path and a 1-based UTF-16 position. Raw protocol requests instead use a document URI and a 0-based position. An emoji before a symbol contributes two UTF-16 code units. Do not shift already converted coordinates again.

Use `documentSymbol` to locate a declaration when only a file is known. For `workspaceSymbol`, pass the symbol name as its `query` parameter (Claude Code 2.1.162 and later); if the schema has no `query` field or the search returns nothing, search the name as text and request `documentSymbol` on the candidate files. Confirm identity with a declaration or hover; lack of hover alone does not prove a wrong position.

Raw call hierarchy is a two-step interface: preparation produces an item used for incoming/outgoing calls. The client may manage that item internally. Follow the exposed operation shape. References, implementation links, and calls describe different relationships; a reference need not be an invocation, and an interface declaration need not be a concrete callable implementation.

## Capability checks

Read the `LSP` tool's input schema to learn which operations and fields it accepts; use only those. Claude Code returns an error result for every LSP call on a file whose language server it can't start. Treat an error, or a result saying the method is unsupported, as "not supported": use definitions, references and source inspection instead of retrying. An empty result is different and needs the checks in SKILL.md.

The `LSP` tool has no diagnostics operation. LSP diagnostics reach Claude only as the type errors and warnings Claude Code reports automatically after each edit of a file the server handles; to see a file's current findings without editing it, run the compiler.

## Imports and edits

For an import, inspect the resolved declaration and hover type/signature. Resolve aliases, re-export barrels, path mappings, package exports, conditional imports, and module mode before changing paths. A type-only import and a runtime import can have different emission and initialization consequences.

Organize imports, rename, completion, and formatting require separate client support. A server feature does not guarantee the model can invoke it. If an authorized action is exposed, preview its scope, apply it, reread source, and verify imports and affected callers. Otherwise make explicit edits or use the declared tool without claiming an unavailable LSP action ran.

Removing an apparently unused import can remove initialization or registration. A namespace or side-effect import deserves contract review before removal. Import organization is not proof of compiler correctness or runtime behavior.
