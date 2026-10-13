# TypeScript repair decisions

## Configuration and generation

TSConfig/JSConfig, inherited options, ambient declarations, module resolution and loaded projects determine the analyzed program. Configuration inspection and membership listing precede interpreting a discrepancy; neither is a type check. A references-only solution config can require checking the referenced programs rather than treating the root as every source file.

Inspect `allowJs`, `checkJs` and file-level directives for JS coverage. Admission to the program is different from enabling ordinary JS type diagnostics; syntax/resolution findings can still exist when checkJs is off. A successful check of an old file cannot refute a current diagnostic in a moved file absent from that program.

Native TypeScript uses its LSP interface; a legacy wrapper depends on `tsserver`. Verify the executable resolved by the configured command before inferring generation support. Compiler/API packages, experimental builds and stable binaries are different compatibility questions; use matching source/package metadata for an integration change.

There is no `tsc --strictest` flag. Inspect the options of a supplied strict profile or preset, including `skipLibCheck`; a preset name does not prove library checking is enabled. Keep the runtime's target, module mode and types when selecting an authorized profile. `--noEmit` suppresses program output, but incremental/build metadata is a separate concern.

## Types and runtime input

For assignment/argument mismatches, inspect the intended contract and affected callers. For optional values, narrow in the branch where absence matters. For an external value, start from `unknown` and validate required members rather than assert the desired type.

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

Invalid JSON retains its parsing exception; missing/non-string labels or wrong top-level values are rejected, and empty strings remain valid. This `in`-operator narrowing requires a compiler that supports unlisted-property narrowing (TypeScript 4.9 or later). Adapt to the actual schema and target compiler, then test acceptance/rejection paths.

## Import actions and checking output

Organize imports, rename and other edits require an action actually exposed by the client. Preview the edit scope and reread the result. A removed import can remove module initialization or registration; a type-only import can differ from a runtime import. Check aliases, package exports and conditional/module resolution before changing import paths.

Use the declared formatter/linter independently from compilation. Biome `format`, `lint` and combined `check` have different scope; write/fix options modify source. Capture each checker status and full output before filtering diagnostics. A failed process with no matching `error TS` lines remains unsuccessful analysis; parsed lines alone do not prove completion.
