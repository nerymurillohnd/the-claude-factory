# Semantic operations and import actions

Use the actual client schema rather than sending raw protocol shapes to a similarly named tool. The common Claude parameters are `filePath`, `line`, and `character`; the path is absolute and the position is 1-based UTF-16. Raw protocol requests use `textDocument.uri` and a 0-based `position` instead. Diagnostic JSON ranges also begin at zero.

## Capability checks

Read the `LSP` tool's input schema to learn which operations and fields it accepts; use only those. Then call the operation. Claude Code returns an error result for every LSP call on a file whose language server it can't start. Treat an error, or a result saying the method is unsupported, as "not supported for this file" and use the fallback evidence below. An empty result is different: run the checks in SKILL.md before relying on it.

For a file outline, use `documentSymbol`; do not guess a target function when only the filename is known. For `workspaceSymbol`, pass the symbol name as its `query` parameter (Claude Code 2.1.162 and later); if the schema has no `query` field or the search returns nothing, search the name as text and request `documentSymbol` on the candidate files. Hover or the declaration verifies identity; an absent hover is inconclusive, because some symbols do not supply hover text.

`prepareCallHierarchy` supplies a hierarchy item for raw `incomingCalls`/`outgoingCalls` requests. Follow the client's declared operation-specific shape; it may manage that item internally. Do not manufacture an interface implementation or a call graph from textual matches. If a method is unsupported, use available definitions/references and read the relevant callable body.

## Imports

Inspect the actual import target with `goToDefinition` and its type/signature with `hover`. Package names, distribution names, and imported module names can differ. A missing type stub and a missing runtime module are distinct problems.

Organize-imports, rename edits, and completion are code actions that require separate client support. An advertised server action is not proof that Claude can invoke it. If the action is exposed and authorized, preview its edit scope, apply it, reread the source, and verify behavior. Otherwise edit explicitly or use the available formatter/linter within the task scope.

Removing an apparently unused import can remove module initialization, registration, exports, or typing behavior. F401 is useful evidence; it is not permission to erase an unresolved dependency. Before automatic removal, inspect how the import participates in runtime and public API behavior.

## Fallback evidence

Text search supplements semantic navigation for dynamic names, configurations, and excluded source formats. Respect file-access boundaries and avoid reading secret-bearing files. Use safe templates or variable-name metadata for configuration references. State the coverage limitation when it changes the recommendation; do not narrate every ordinary lookup.
