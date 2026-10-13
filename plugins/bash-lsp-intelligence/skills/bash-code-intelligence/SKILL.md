---
name: bash-code-intelligence
description: "Navigate and repair Bash/POSIX scripts with bash-language-server, ShellCheck and shfmt. Use for \"rename this shell function\", \"find all callers\", \"fix SC2086\", \"why is this sourced variable undefined?\", or \"format this script\"."
---

# Bash and POSIX Shell Code Intelligence

Repair findings introduced by this task in changed files and affected callers. Report pre-existing findings separately; repair them only when the requested work covers them. A required check remains failed while its findings remain. Code edits are authorized when requested or necessary for that work; environment, dependency and checking-policy changes require explicit task scope.

## Semantic tool use

Prefer LSP navigation: definitions and references follow symbol identity and types, whereas matching text can merge unrelated names or miss aliases. Read source bodies for behavior; use the available text/file search for registrations, dynamic names, or files outside server coverage.

Choose the operation for the question: `goToDefinition` and `hover` establish identity/type; `findReferences` finds consumers; `documentSymbol` outlines a file and `workspaceSymbol` locates named symbols. For implementation/call analysis, use exposed `goToImplementation`, `prepareCallHierarchy`, `incomingCalls`, and `outgoingCalls` capabilities.

Read the loaded tool definition before calling it. When it exposes `filePath`, `line`, and `character`, use an absolute authorized source path and its declared line/column indexing. If it declares 1-based positions, pass 1-based positions. Use its declared encoding; do not import assumptions from raw LSP or another client. Add a query or hierarchy item only when that schema accepts it. An explicit unsupported-method response calls for supported alternatives; other errors require checking the request or server state and do not prove that capability is absent. A stable short result still needs the language-specific checks below.

## Rename only the function reached by the caller

bash-language-server can return unrelated same-named definitions and calls together. Treat those locations as candidates, then:

1. Inspect each definition and the caller's direct/transitive `source` or `.` chain.
2. Establish which definition exists in that shell at the call. A parent-sourced library can supply functions to another sourced file, but a separately executed child does not normally inherit unexported functions.
3. Change only the confirmed definition/consumers. Check trap strings, variable dispatch and extensionless launchers separately. A repeated count does not resolve identity.

If call hierarchy or implementation lookup is unsupported, use references, definitions on real calls, and source relationships. An absent shell-function hover does not invalidate a working definition/reference result.

## Diagnose the actual dialect and source context

Check the shebang, shell declaration and real callers. A `.sh` suffix does not make Zsh code Bash. ShellCheck's unsupported-dialect result calls for a supported checker, not automatic conversion.

For SC1090/SC1091 followed by SC2154, establish source resolution before inventing a variable assignment. `source-path=SCRIPTDIR` affects analyzer lookup; `source ./lib.sh` still uses runtime cwd. Include `.inc` libraries and extensionless consumers when relevant: server file discovery and the client's extension/language routing are separate settings.

For SC2086, decide whether one value or multiple arguments are intended. `"${directory}"/*.csv` preserves a glob; `"${directory}/*.csv"` passes a literal. Use an array for distinct arguments rather than quoting a whole argument list into one value.

Read [repair.md](references/repair.md) for sourced libraries, strict ShellCheck settings and status handling.

## Check the changed scripts

Use shfmt for format, ShellCheck for enabled lint rules, and the selected shell's syntax-only mode for parsing. Invoke `bash -n` separately for each Bash script; later filename arguments are not additional scripts to parse. Preserve formatter/analyzer statuses separately: a final successful command can hide an earlier failure. Test the affected launch directory, arguments, exit and trap behavior in a controlled context.

Use [sources.md](references/sources.md) to resolve dialect, rule or capability differences in the installed tools.
