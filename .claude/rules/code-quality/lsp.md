---
paths:
  - "**/*.py"
  - "**/*.sh"
  - "**/*.{js,cjs,mjs,ts,cts,mts,tsx}"
---

# LSP, diagnostics and navigation

- Answer questions about code structure with the LSP tool, and questions about text with Grep.
- Use `goToDefinition` for a definition, `findReferences` for callers and imports, `hover` for a type or signature, and `documentSymbol` before reading a whole file.
- Use `workspaceSymbol`, always with a `query`, when you don't know the file.
- Before trusting an empty result, `hover` the same position: "No hover information" means a wrong position or no server, never "no usages".
- Before a rename or deletion, Grep the name where LSP can't see it: strings, config, scripts, CI, docs and dynamic dispatch.
- Never delete code on LSP evidence alone.
- After a change made outside Edit and Write, such as a formatter, git or a Bash command, Grep or read the files: the index may not see it.
- Treat no diagnostics after an edit as unknown, not clean: run the language's checks before reporting done.
