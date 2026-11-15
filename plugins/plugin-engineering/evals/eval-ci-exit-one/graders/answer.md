---
type: llm
focus: last_message
---

PASS if the reply names at least two of these causes and gives a corrected step that fixes them: the default `--threshold` is 1.0, so cases scoring about 0.9 make the command exit 1; the target placed after `--tag` (and `--json`) is read as their value, so the target must come first; under `--json` or in CI an untrusted plugin directory is refused with exit 1 unless `--trust-plugin` is passed.
FAIL if the reply names none or only one of those causes, blames the model or flaky runs alone, or gives a step that still puts the target after `--tag`.
Formatting, headings and wording do not decide the verdict.
