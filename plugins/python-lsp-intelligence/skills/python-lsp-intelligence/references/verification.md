# Python verification evidence

Choose checks for the actual source and declared policy. The checker's executable version, cwd/project selection, interpreter, configuration, exclusions, and source snapshot all affect the conclusion. Do not assume the nearest generic packaging file defines the correct analysis root.

## Relevant independent checks

When CLI verification is needed and the tools are available, keep statuses separate:

```text
ruff check --output-format json <affected files>
ruff format --check <affected files>
basedpyright --outputjson <affected files>
```

These are independent check invocations, not a compound shell expression. Preserve stdout, stderr, and each process status before parsing JSON. A nonzero tool exit cannot be erased by a successful parser. Exit 0 also requires checking whether files were actually analyzed and whether output still contains warnings.

The project's configuration decides whether basedpyright warnings fail the run (`failOnWarnings`). Add `--warnings` only when the user asks for warnings to fail; it makes them fail even when the configuration says otherwise. Report warnings either way.

Formatting or autofix is part of authorized code edits. Re-read changed source and verify final lint/type behavior. If automatic import removal would destroy evidence or initialization behavior, retain F401 as a finding while investigating; `--unfixable F401` controls the fix, not rule detection.

## Repeat after a fix

After each fix, rerun the same checks on the same scope. Stop when they report no actionable diagnostics, or after three rounds that leave the same findings; then report what remains with its evidence.

## Scope

Ruff checks explicitly named files unless forced exclusion applies. A message that no Python files were found is not coverage of those targets. Global settings can still affect a temporary-directory run unless a specific test configuration is selected.

Explicit filenames restrict basedpyright's diagnostic targets. A passing definition file does not establish that callers remain valid. For a signature/export change, also run the declared affected-program checks or examine/check known consumers under their intended configurations. Project `.venv` discovery is a useful default in basedpyright, not a universal interpreter guarantee.

## Behavior and reporting

A type correction can still change serialization, exception handling, side effects, or API behavior: run the tests that cover the changed path.

Report each evidence layer: files linted, format checked or changed, type scope/interpreter, tests executed, and unresolved diagnostics. An unavailable tool is an explicit verification limit. Do not label an unexecuted, excluded, stale, or configuration-invalid check a pass.
