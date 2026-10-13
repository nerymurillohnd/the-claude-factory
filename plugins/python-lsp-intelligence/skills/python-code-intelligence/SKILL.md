---
name: python-code-intelligence
description: "Navigate and repair Python with basedpyright and Ruff. Use for requests such as \"rename this Python function\", \"find all usages\", \"explain this inferred type\", \"fix reportMissingImports\", or \"fix this Ruff or Python type error\" while working on Python code."
---

# Python Code Intelligence

Repair findings introduced by this task in changed files and affected callers. Report pre-existing findings separately; repair them only when the requested work covers them. A required check remains failed while its findings remain. Code edits are authorized when requested or necessary for that work; environment, dependency and checking-policy changes require explicit task scope.

## Semantic tool use

Prefer LSP navigation: definitions and references follow symbol identity and types, whereas matching text can merge unrelated names or miss aliases. Read source bodies for behavior; use the available text/file search for registrations, dynamic names, or files outside server coverage.

Choose the operation for the question: `goToDefinition` and `hover` establish identity/type; `findReferences` finds consumers; `documentSymbol` outlines a file and `workspaceSymbol` locates named symbols. For implementation/call analysis, use exposed `goToImplementation`, `prepareCallHierarchy`, `incomingCalls`, and `outgoingCalls` capabilities.

Read the loaded tool definition before calling it. When it exposes `filePath`, `line`, and `character`, use an absolute authorized source path and its declared line/column indexing. If it declares 1-based positions, pass 1-based positions. Use its declared encoding; do not import assumptions from raw LSP or another client. Add a query or hierarchy item only when that schema accepts it. An explicit unsupported-method response calls for supported alternatives; other errors require checking the request or server state and do not prove that capability is absent. A stable short result still needs the language-specific checks below.

## Rename a definition and its aliases

1. Find the declaration, inspect its signature, and query references there.
2. With `from module import target as local`, query `local` too: the definition's reference set can omit calls through the alias.
3. For a public rename, update the definition and imported name, keeping `local(...)` unchanged unless the alias is also being renamed. Check `__all__`, re-exports, pytest/registry names, and declared entry-point strings for additional consumers.

```python
from module import target as local
result = local(1)
```

Renaming `target` to `calculate` changes the import to `from module import calculate as local`; replacing every matching word would change more than this request requires.

## Diagnose and repair

- For `reportMissingImports`, compare the selected interpreter, declared dependencies, import spelling, and search paths before editing code. PEP 723 requirements do not guarantee the editor selected that script's environment.
- For F401, inspect exports and module initialization before import removal. An autofix can remove the import that explained a resolution failure; read the original diagnostic first.
- For `reportAny` or unknown input types, validate the external value and narrow it to the public return/argument type. Check the project's minimum Python version before choosing annotation syntax or typing APIs: standard-library `TypeGuard` requires Python 3.10.

Read [repair.md](references/repair.md) for environment mismatches, warning status, and a version-qualified JSON boundary.

## Check the affected code

Run the declared Ruff lint/format checks and basedpyright under the intended interpreter/profile. Preserve each status before parsing output; use `--outputjson` for structured diagnostics and add `--warnings` only when the declared project/task checking policy treats warnings as failures. Verify actual input coverage: Ruff's `force-exclude` can skip a named file, and checking only the definition file can omit broken callers. Re-read formatter/fix changes, then test the behavior changed by the repair.

Use [sources.md](references/sources.md) when an option, rule, or installed-version difference needs confirmation.
