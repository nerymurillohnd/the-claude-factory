# Project evidence and safe probes

Read during initial inspection, configuration/editor diagnosis, or reproduction design. These are ways to satisfy governing rules, not a mandatory command sequence.

| Layer | Useful observations |
| --- | --- |
| Outcome | Expected behavior, authorized edits, project instructions, baseline failure, acceptance and negative cases. |
| Version identity | Manifest ranges; lockfile resolutions including duplicates; installed metadata at the consuming workspace; resolved executable/version; package manager/runtime; active editor/compiler/plugin. Preserve disagreements for diagnosis rather than reinstalling to erase them. |
| Execution | Working directory, package scripts/wrappers, CI commands, framework checker, build/transpile owner, runtime/test entrypoints, generated inputs, selected environment. Inspect scripts before running potentially mutating commands. |
| Configuration graph | Relevant tsconfig/jsconfig files and extended package configs, references, command overrides, generated config owner, membership, ambient libs/types, exports and resolver conditions. |
| Editor | Existing workspace settings and relevant user-setting observations, selected service, association for the failing file, extension versions, diagnostic provenance. Missing access remains unknown. |

## Local compiler probes

Resolve the project's actual compiler using its package manager/workspace conventions without fetching another version. These are argument patterns for that executable, not commands to run a global compiler or auto-installing runner:

```text
<resolved-compiler> --version
<resolved-compiler> --help --all
<resolved-compiler> --project <config> --showConfig
<resolved-compiler> --project <config> --listFilesOnly
```

After checking installed support and output behavior, use resolution/file explanations or performance diagnostics as relevant. Explicit source-file invocations can select different configuration behavior from project invocations: reconcile installed CLI behavior and official CLI docs. Use the real project check/build command for final validation, accounting for caches and generated outputs; informational probes are not test passes.

For editor discrepancies, compare the **same file** across command and service. Establish whether it belongs to app, tests, tooling, generated, or inferred projects before proposing SDK changes or exclusions. Preserve intentional browser/server/test ambient environments. Available language-server diagnostics/references can help, but observe readiness, freshness, project root and capabilities; empty results alone prove nothing. Server diagnostics arrive only after an edit, so in `research` mode the compiler's output stands in for them and the server's view is inference (SKILL.md, "Treat LSP results as evidence, not the whole picture").

## Isolated reproduction

Reproduce the smallest relevant graph, not only a failing line: package boundaries, inherited config, exports/conditions, generated interfaces, dependency versions and runtime mode can be causal. Use synthetic data outside the project. Resolve dependencies in that isolated layout; copied files or symlinked dependencies can change resolution. Record simplifications and their limits.

Compare baseline and proposal under matched conditions. Include expected-success and expected-failure cases, and runtime or packed-consumer checks when those boundaries matter. Keep emitted outputs and incremental caches isolated. Playground experiments clarify language behavior; only a matched compiler/config/environment supports project-specific conclusions.

## Recording

Record findings as observation, inference, contradiction or unavailable evidence (SKILL.md, "Close only on attributable evidence", item 1). Explain why the components you did not visit cannot affect the scoped conclusion, or name the unresolved component that blocks it.
