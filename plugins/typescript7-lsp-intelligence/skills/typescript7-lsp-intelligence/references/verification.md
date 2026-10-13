# Independent verification and completion evidence

The default compiler is the project's own `tsc`, run through its package manager with `--noEmit -p <tsconfig>`. A compiler the user or the project declares (a script, CI step or documented command) replaces it; when the task names a separate compiler or profile, use that and compare program coverage when relevant. Do not install a tool or rewrite project configuration merely to obtain fewer diagnostics.

| Evidence | Establishes | Does not establish |
|---|---|---|
| Diagnostics after an edit | Findings for the edited documents in the server's loaded program | Repository-wide absence of defects |
| `--showConfig` | Resolved options and selected program context | Type correctness |
| `--listFilesOnly` | Program membership | JavaScript checking or type correctness |
| `--noEmit` compilation | Compiler result under that policy and source scope | Lint, formatting, tests, or runtime behavior |
| Formatter | Source conforms to the selected format policy | Semantic or behavioral correctness |
| Linter | Enabled lint findings for selected files | Complete static types or application behavior |
| Behavior tests | Observed intended/rejection paths | Untested paths or external consumers |

Biome can supply a separately declared TS/JS lint/format tool. Its `format`, `lint`, and combined `check` commands have different scope. `--write` changes files; unsafe fixes need contract review and an explicit request. Check effective configuration and exclusions, reread resulting source, and use the compiler for type diagnostics. Biome does not replace `tsc`.

Capture each command's status, stdout, and stderr before interpreting output. A pipeline's final status or a regex finding zero `error TS` lines cannot erase a compiler failure. Where a structured format is unavailable, preserve complete text rather than claiming a compiler JSON format that the actual binary does not support.

## Repeat after a fix

After each fix, rerun the same checks on the same programs. Stop when they report no actionable diagnostics, or after three rounds that leave the same findings; then report what remains with its evidence.

## Report

Report the concrete change or diagnosis, the compiler/version/policy used, checked files/programs, independent lint/format/test results, and remaining scope limits. Successful compilation cannot prove an omitted moved file is healthy or that unchecked JS was type-checked.
