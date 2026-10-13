---
name: bash-lsp-intelligence
description: Navigates Bash and POSIX shell scripts through bash-language-server, tells same-named functions apart by what each script sources, repairs ShellCheck and shfmt findings without changing behavior, and verifies each change. Use when navigating, editing, refactoring or diagnosing shell scripts, including sourced files and extensionless executables, investigating ShellCheck or shfmt findings, or verifying shell behavior. Not for converting scripts to other shell dialects.
---

# Bash and POSIX Shell Code Intelligence

Understand the real shell dialect and source relationships, preserve execution semantics, and verify the changed behavior. Fix the actionable diagnostics before beginning unrelated changes: those are the findings in the code the task changes, including any the change introduces. Report pre-existing findings in code the task does not touch; fix them only when the user asks.

**Authorized** means what the request covers explicitly or necessarily implies, such as editing the scripts it asks to change and running read-only checks. Executing scripts beyond a syntax check, installing tools, converting a script's dialect, and changing ShellCheck, shfmt or EditorConfig policy always need an explicit request.

## Choose the right tool

**Claude must prefer the LSP over Grep, Glob, and Bash for code navigation and semantic relationships.** Shell definitions, references, outlines, and documentation are useful, but shell navigation is not a static type checker. Source reading resolves implementation details and sourcing scope. Text search supplements semantic discovery for strings and files outside coverage.

The user installs `bash-language-server` separately, and Claude Code doesn't start plugin language servers in cloud sessions. If the `LSP` tool is missing or returns an error because the server can't start, don't retry: say so once, and navigate with source reading and text search.

| Operation | Purpose | Use before |
|---|---|---|
| `goToDefinition` | Identify a function or variable definition | Modifying unfamiliar code |
| `findReferences` | Discover candidate uses | Refactoring or renaming |
| `goToImplementation` | Implementation relationships | Polymorphic work |
| `hover` | Inspect available documentation/declaration information | Understanding APIs or checking position |
| `documentSymbol` | Obtain a script outline | Exploring a long script |
| `workspaceSymbol` | Search named symbols | Locating related source |
| `prepareCallHierarchy` | Callable hierarchy item | Call analysis |
| `incomingCalls` | Callers from a hierarchy item | Impact analysis |
| `outgoingCalls` | Callees from a hierarchy item | Dependency tracing |

Not every server answers every operation. When one returns an error or says the method is unsupported, use the fallback in [operations.md](references/operations.md) instead of retrying it.

For the Claude `LSP` tool, provide the common parameters for every operation:

- `filePath`: the absolute source path.
- `line`: a 1-based line number.
- `character`: a 1-based UTF-16 column at the symbol name.

Supply additional fields only when the actual tool schema exposes them. Raw protocol positions are 0-based. Read [operations.md](references/operations.md) for capability checks, workspace symbol search, and supported alternatives.

## Resolve identity, not just names

Use `documentSymbol` when the function name or position is unknown, then definitions/references for the specific relationship. Confirm the declaration; hover may be absent for shell functions even when references work.

Reference results can be overinclusive: bash-language-server can return unrelated same-named functions together. For an empty or short result, verify path, dialect, loaded workspace, file discovery, and synchronization, then retry at most twice after the initial request. Report material scope limitations once.

To rename or delete a function:

1. Find the definition and its references semantically.
2. Trace the direct and transitive `source`/`.` relationships and decide which definition each caller reaches; exclude a candidate only after establishing it belongs to another definition.
3. Search for indirect consumers: command dispatch, aliases, traps, `eval`, generated commands, CI and Makefiles, and source paths that depend on cwd or variables. Include extensionless executables and relevant hidden directories.
4. List confirmed edits and unresolved cases separately, then edit only the confirmed ones.
5. Verify with the checks in "Verify changed behavior". The rename is done when they pass, no confirmed caller still uses the old name, and the unresolved cases are reported.

Read [shell-navigation.md](references/shell-navigation.md) before a rename or deletion, or when counts look incomplete.

## Diagnose the correct language and context

A shebang or explicit shell declaration determines intent; a `.sh` suffix does not turn Zsh into Bash. ShellCheck's unsupported-dialect message is a tool boundary, not proof that valid Zsh code is defective. Preserve language and behavior unless conversion is authorized.

Inspect SC codes, severity, location, source resolution, and effective configuration before changing a script. An unresolved sourced file can produce later unassigned-variable findings; verify the source chain before adding assignments or suppressions. Analyzer lookup paths do not change the script's runtime cwd.

Repair quoting, splitting, globbing, arrays, exit-status handling, and redirection with the intended behavior in mind. Do not quote an intentional glob into a literal filename or convert an intentional multi-argument value into one argument. Reread any formatted source before constructing another edit.

Read [diagnostics-and-repair.md](references/diagnostics-and-repair.md) for practical repair decisions. Do not run an arbitrary script merely to obtain static diagnostics, install a tool automatically, or change checker configuration solely to hide a finding.

## Verify changed behavior

Use the project's declared tools, dialect, and checking policy; when it declares none, use the default in [verification.md](references/verification.md) and say that no policy was declared. Formatting, parsing, linting, and runtime tests establish different things. Preserve each process status, stdout, and stderr; a successful final command does not cancel an earlier failure. A successful ShellCheck invocation does not establish that an omitted or unfollowed file was analyzed.

For scripts that write, delete, deploy, or contact services, test with existing test doubles or in a temporary directory rather than running production operations. After each fix, rerun the same checks; [verification.md](references/verification.md) sets when to stop. Report the actual checks performed, source scope, observed behavior, and remaining uncertainty.

## Control tests

Run the control tests only when the user asks to test tool coverage, or when a check passes code it should flag. They are not a step of ordinary coding tasks. Read [controls.md](references/controls.md) first, then run the bundled runner by path:

```bash
"${CLAUDE_SKILL_DIR}/scripts/verify-fixtures.sh"
"${CLAUDE_SKILL_DIR}/scripts/verify-fixtures.sh" --tool shellcheck=/absolute/path/to/shellcheck --tool shfmt=/absolute/path/to/shfmt
```

The first form uses `shellcheck` and `shfmt` from `PATH`; add one `--tool name=/absolute/path` pair for each executable the task declares. The runner needs `bash` and `jq` 1.6 or later, installs nothing, and never executes the controls.

- **Exit 0**: the JSON report printed. `allExpectedOutcomesMatched` is the overall result; each entry in `results` carries its own `expectedOutcomeMatched`.
- **Exit 2**: setup failed and no report printed; stderr names the failed step and what to do next.

## Reference map

- [operations.md](references/operations.md): capability checks, workspace symbol search, and fallbacks.
- [shell-navigation.md](references/shell-navigation.md): sourcing identity, traps, and discovery.
- [diagnostics-and-repair.md](references/diagnostics-and-repair.md): SC findings, quoting, and context.
- [verification.md](references/verification.md): the default check policy, statuses, and the repeat-after-fix loop.
- [controls.md](references/controls.md): the control tests and their expected results.
- [sources.md](references/sources.md): read when an installed tool behaves differently from this skill, before revising an assumption.
