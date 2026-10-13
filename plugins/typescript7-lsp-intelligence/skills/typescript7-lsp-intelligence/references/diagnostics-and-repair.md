# Diagnose the program and repair its contract

## Compiler generation and configuration

Tell the generation by its interface, not its version number. The legacy generation ships `lib/tsserver.js`, which wrappers such as typescript-language-server drive. The native generation ships a compiler that serves `tsc --lsp --stdio` and no `tsserver.js`, so it is not a drop-in target for those wrappers. Use the interface the chosen client actually supports and verify its runtime capabilities; a native LSP does not imply every legacy API is compatible, and a preview package is not the same as the stable one.

Inspect the explicitly intended compiler and policy first. TSConfig/JSConfig, inherited settings, references, module resolution, paths, libraries, and ambient declarations change diagnostics and inferred types. LSP launch configuration alone does not make them independent of the project.

Use `--showConfig -p /absolute/config` to inspect the resolved program configuration and `--listFilesOnly -p /absolute/config` to establish membership; SKILL.md shows how to find the config that owns a file. Preserve their statuses. Then run actual compilation with `--noEmit` under the same context. Do not infer that a missing explicit `include` or `files` means there is no program: defaults can include source files. A solution-style references-only root may require checking its referenced programs; inspect the structure rather than indiscriminately compiling every configuration in the repository.

`allowJs` and `checkJs` answer different questions. Listed JS source with checking off has membership evidence, not JavaScript type-check evidence. Verify effective options and file directives without weakening or silently enabling policy. If broader checking is requested, apply that scoped configuration change only on an explicit request.

There is no `tsc --strictest` flag. A declared strictest profile is a set of options or an explicit preset such as `@tsconfig/strictest`. Inspect the resolved options: a preset can include `skipLibCheck: true`. The supplied controls explicitly use false and add stricter options. They are test profiles, not a universal project configuration. Do not substitute targets, module modes, runtime types, or libraries without considering the project's runtime.

## Findings and corrections

| Finding | Inspect first | Defensible correction |
|---|---|---|
| TS2304 / TS2307 | Declaration/import identity, program coverage, paths, exports, module mode | Repair the demonstrated name/resolution defect; distinguish missing packages from wrong context |
| TS2322 / TS2345 | Intended value and caller/callee contract | Correct construction or validate/narrow the value |
| TS7006 | Real parameter contract and affected calls | Add an accurate type or improve contextual typing |
| Optional/undefined diagnostics | Presence and branch conditions | Check absence and preserve rejection/fallback semantics |
| Declaration/library mismatch | Tool/runtime versions and effective ambient types | Establish compatibility rather than hide it with `skipLibCheck` |
| No matching TS lines from a failed command | Status, stderr, setup, and coverage | Report incomplete analysis and its cause |

For untrusted JSON, treat the boundary as `unknown`, validate its shape and required members, and return the intended type. For example:

```typescript
export function readLabel(text: string): string {
  const decoded: unknown = JSON.parse(text);
  if (
    typeof decoded !== "object" ||
    decoded === null ||
    !("label" in decoded)
  ) {
    throw new Error("Expected an object with a label");
  }
  if (typeof decoded.label !== "string") {
    throw new Error("Expected a string label");
  }
  return decoded.label;
}
```

This preserves parsing exceptions, rejects missing/non-string labels, and accepts empty strings. Test those paths under the intended contract. An `as` assertion, non-null assertion, `any`, ignored diagnostic, or permissive default is not runtime validation. This example compiles under the control profile with both compiler generations; a different runtime/schema requires its own checks.

Malformed configurations, missing executables, internal errors, and timeouts are tool failures or incomplete analysis. Do not change unrelated code or suppress diagnostics to convert those outcomes into a pass.
