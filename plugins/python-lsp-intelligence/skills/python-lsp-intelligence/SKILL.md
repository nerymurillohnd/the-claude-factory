---
name: python-lsp-intelligence
description: Navigates Python code through the basedpyright language server, repairs basedpyright and Ruff findings without suppressing them, and verifies each change with separate lint, format, type and test evidence. Use when navigating, editing, refactoring or diagnosing Python code, resolving imports or annotations, investigating incomplete LSP answers, or verifying a Python change. Not for other languages.
---

# Python Code Intelligence

Use semantic evidence to understand code, preserve its contract when changing it, and verify the specific behavior affected. Fix the actionable diagnostics before beginning unrelated changes: those are the findings in the code the task changes, including any the change introduces. Report pre-existing findings in code the task does not touch; fix them only when the user asks.

**Authorized** means what the request covers explicitly or necessarily implies, such as editing the code it asks to change and running read-only checks. Creating, synchronizing or substituting environments, installing or changing dependencies, and changing checker or linter policy always need an explicit request.

## Choose the right tool

**Claude must prefer the LSP over Grep, Glob, and Bash for code navigation and semantic relationships.** Confirm the available tool and server capabilities before making a request. Use source reading for implementation details and text search for strings, metadata, dynamic uses, or files the server cannot serve. Use command-line tools for explicit verification, not as substitutes for semantic navigation.

| Operation | Purpose | Use before |
|---|---|---|
| `goToDefinition` | Identify the defining symbol | Modifying unfamiliar code |
| `findReferences` | Discover static uses | Refactoring or renaming |
| `goToImplementation` | Find supported implementation relationships | Changing polymorphic behavior |
| `hover` | Inspect inferred types, signatures, and documentation | Understanding an API or validating a position |
| `documentSymbol` | Obtain a file outline | Exploring a large file |
| `workspaceSymbol` | Search named symbols | Locating a symbol with unknown file |
| `prepareCallHierarchy` | Identify the callable hierarchy item | Tracing call relationships |
| `incomingCalls` | Discover callers | Impact analysis |
| `outgoingCalls` | Discover callees | Dependency tracing |

For the Claude `LSP` tool, provide these common parameters for every operation:

- `filePath`: the absolute source-file path within the workspace.
- `line`: a 1-based line number.
- `character`: a 1-based UTF-16 column; an emoji before the symbol contributes two code units.

Point at the symbol name. Supply additional fields only when the actual tool schema exposes them; do not add raw-protocol fields to the Claude request. Raw LSP protocol positions and diagnostic ranges are 0-based; convert once when reporting or calling the Claude tool. A server capability is not automatically an operation exposed by the client. Read [operations.md](references/operations.md) for positions, capability checks, and imports.

## Navigate with bounded, scoped evidence

1. Locate the symbol semantically, confirm its identity with `hover` or its declaration, then ask the operation that answers the task.
2. Before relying on an empty or unexpectedly small result, verify the file, symbol position, workspace, synchronization, and supported operation. If a cold index is plausible, load a relevant file semantically and retry at most twice after the initial request. Stable results do not establish complete coverage.
3. For a rename or deletion, inspect imports, aliases, public exports, entry points, pytest fixtures, and dynamic consumers. With `from module import target as local`, references to `target` can omit calls through `local`; query the alias as well. Preserve the alias unless the requested change includes it.
4. Search the relevant non-code registrations and dynamic uses after semantic discovery. Inspect candidate hits by identity; do not replace every matching word. Report unresolved external consumers or dynamic names rather than asserting universal absence.

Read [python-navigation.md](references/python-navigation.md) for aliases, decorators, pytest, source scope, and safe change boundaries. If semantic tooling is unavailable or unsupported, report the material limit once and use the available source/search tools; do not invent a tool or install a server merely to complete a lookup.

## Diagnose before changing behavior

Collect the diagnostic's tool, file, position, rule, message, source version, and applicable configuration. An error, warning, empty response, unavailable analysis, and a passed check are different evidence. Investigate disagreements between LSP and CLI using the same source snapshot, interpreter, rules, and scope; neither source of evidence wins merely because it returned fewer findings.

For an import error, establish the intended environment and declaration before adding a dependency or editing the import. A PEP 723 script may be analyzed under a different interpreter than the one supplying its declared packages. Explain that mismatch; do not create, synchronize, or substitute environments unless authorized.

For unknown or `Any` data, validate the external boundary and narrow from `object` to the required type. Keep runtime rejection paths, public return types, and caller assumptions intact. An annotation alone does not validate a value. Do not use unchecked casts, suppression comments, invented defaults, or weaker configuration solely to hide a finding.

Read [diagnostics-and-repair.md](references/diagnostics-and-repair.md) for F401, type rules, input validation, and error classification. Re-read source that any formatter or code action changed before constructing the next edit.

## Verify the actual change

Use the declared checking policy and the tools already available. Confirm which files were analyzed and preserve each process's status and full diagnostics; the last command in a sequence or a successful JSON filter does not establish that preceding checks passed. A warning can exist with exit 0 under some configurations. Ruff can exclude an explicitly named file when `force-exclude` is enabled.

Check affected callers when changing exports, annotations, or signatures: file-scoped type checking is not whole-program coverage.

Read [verification.md](references/verification.md) when selecting checks, interpreting statuses, or repeating checks after a fix.

Report the concrete change or diagnosis, verification performed, scope, and remaining uncertainty. Correct authorized code defects without waiting for another approval; report a missing environment, incompatible API contract, or policy decision at its actual boundary.

## Control tests

Run the control tests only when the user asks to test tool coverage, or when a check passes code it should flag. They are not a step of ordinary coding tasks. Read [controls.md](references/controls.md) first, then run the bundled runner by path:

```bash
"${CLAUDE_SKILL_DIR}/scripts/verify-fixtures.sh"
"${CLAUDE_SKILL_DIR}/scripts/verify-fixtures.sh" --tool basedpyright=/absolute/path/to/basedpyright --tool ruff=/absolute/path/to/ruff
```

The first form uses `basedpyright` and `ruff` from `PATH`; add one `--tool name=/absolute/path` pair for each executable the task declares. The runner needs `bash` and `jq` 1.6 or later, installs nothing, and never executes the controls.

- **Exit 0**: the JSON report printed. `allExpectedOutcomesMatched` is the overall result; each entry in `results` carries its own `expectedOutcomeMatched`.
- **Exit 2**: setup failed (missing tool, bad argument, unreadable manifest) and no control ran; stderr names the cause.

## Reference map

- [operations.md](references/operations.md): Claude requests, capability checks, raw-protocol differences, and import actions.
- [python-navigation.md](references/python-navigation.md): Python-specific identity and consumer coverage.
- [diagnostics-and-repair.md](references/diagnostics-and-repair.md): repair decisions and input boundaries.
- [verification.md](references/verification.md): independent checks, the repeat-after-fix loop, and completion evidence.
- [controls.md](references/controls.md): the control tests and their expected results.
- [sources.md](references/sources.md): read when an installed tool behaves differently from this skill, before revising an assumption.
