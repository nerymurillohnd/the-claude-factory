# Case format

Read this when you write, fix or review an eval case or grader for `claude plugin eval`. The snapshot version is in [sources.md](sources.md). Confirm any field you are unsure of with the live page.

## Contents

- Suite layout
- `prompt.md`
- `case.yaml`
- Graders: common keys
- What a grader looks at (`target` and `focus`)
- Grader types
- Scoring and the no-plugin baseline
- Ready-to-copy patterns

## Suite layout

```text
my-plugin/
├── .claude-plugin/plugin.json
├── skills/...
└── evals/                       # default eval directory
    ├── <case>/                  # a directory is a case when it holds prompt.md or case.yaml
    │   ├── prompt.md            # frontmatter: case fields; body: the prompt
    │   ├── case.yaml            # optional: context.* fields, or the whole case
    │   ├── graders/<name>.md    # one grader per file; the name is the file name
    │   ├── mocks/               # optional: this case's MCP mocks
    │   └── <fixtures, scripts, transcripts>
    ├── <group>/<case>/          # nest cases under a non-case directory to group them
    ├── mocks/<server>/<tool>.md # suite-wide MCP mocks
    └── results/<timestamp>/     # written by each run: add results/ to .gitignore
```

- A case with no grader fails to load, with an `invalid case.yaml` error that names `graders`.
- Another eval directory: set `"experimental": { "evals": "quality/evals" }` in `plugin.json`, or pass `--eval-dir quality/evals` to both `claude plugin eval` and `init`. The flag wins over the manifest. Use plain relative directory names only. An absolute path or `..` is an error as a flag; as a manifest value it prints a `Warning:` and the run falls back to `evals/`. With an array in the manifest, only the first entry is used.
- Case names, including `init` names, start with a letter or digit and use only letters, digits, `.`, `_` and `-`. Names Windows can't store, such as `con`, are refused.
- Each run starts in an empty working directory, and the run can't read the eval directory. Put what the task needs in the prompt, or seed it with `case.yaml` (see [fixtures-and-mocks.md](fixtures-and-mocks.md)). Don't use absolute paths or `~/` in prompts or graders.

## `prompt.md`

The body is sent exactly as written. `@path` mentions are not expanded, so to have Claude read a file, allow `Read` and seed the file. An unknown frontmatter key is an error.

| Field | Default | Notes |
| :-- | :-- | :-- |
| `schema_version` | `"1.1"`, set for you | Rarely written by hand |
| `name` | the directory name | `--case` globs match it, and the report keys on it |
| `description` | — | For humans: say what the case proves |
| `tags` | `[]` | `--tag` keeps a case when any of its tags match |
| `plugins` | the nearest enclosing plugin | Paths relative to the case directory, such as `["../.."]`, when auto-detection fails |
| `runs` | `3` | 1–50 per arm; `--runs` overrides it |
| `expected_outcome` | — | For humans |
| `model` | the child session's default | `--model` overrides it |
| `max_turns` | `10` | Up to 200. Hitting it is a run error |
| `timeout_seconds` | `300` | Up to 3600 |
| `allowed_tools` | `[]` | Read-only tools listed here are granted. Everything else needs `--allow-tools` (see [running-and-ci.md](running-and-ci.md)) |
| `append_system_prompt` | — | Appended to the child session's system prompt |
| `env` | `{}` | Keys must match `EVAL_[A-Z0-9_]*`; any other key fails the run |

The read-only set that `allowed_tools` can grant on its own is `Read`, `Glob`, `Grep`, `NotebookRead`, `Skill`, `AskUserQuestion`, `Agent`, `TodoWrite`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate` and `TaskStop`.

**`disallowed_tools`** (since v2.1.299) removes built-in tools from Claude in that case, even when they are granted, for example `Agent`. The run-wide flag is `--disallow-tools`. When this snapshot was taken, the docs page didn't list the field yet. Confirm where it goes with the live page before you rely on it. When you can't confirm it, use the run-wide `--disallow-tools` flag instead, because an unknown `prompt.md` key fails the case.

## `case.yaml`

`case.yaml` is an alternative or a companion to `prompt.md`. It requires `schema_version: "1.1"` and `name`.

- **Top level:** `description`, `tags`, `plugins`, `runs`, `expected_outcome`, `graders`.
- **Under `execution:`:** `model`, `max_turns`, `timeout_seconds`, `allowed_tools`, `append_system_prompt`, `env`, and `prompt` when there is no `prompt.md`.
- **Under `context:`:** `scaffold_script`, `history_file`, `add_dirs` (see [fixtures-and-mocks.md](fixtures-and-mocks.md)).
- **`graders:`** is a list, each entry with a `name` plus the same keys as a grader file. For `llm`, put the rubric in `criteria`.
- **When both files exist:** `prompt.md` frontmatter overrides the matching `case.yaml` fields, the `prompt.md` body is the prompt, and `graders/*.md` are added after the graders `case.yaml` lists.

## Graders: common keys

| Key | Default | Notes |
| :-- | :-- | :-- |
| `type` | required | `regex`, `tool_used`, `tool_order`, `file_exists`, `llm`, `baseline`. There are no custom-code graders |
| `weight` | `1` | Any positive number; the run score is the weighted fraction of graders that passed |
| `arm` | unset | `with-only` excludes the grader from the score in a two-arm run; `both` forces scoring in both arms |

## What a grader looks at (`target` and `focus`)

`regex` takes `target`; `llm` takes `focus`. Both accept the same values:

| Value | What it sees |
| :-- | :-- |
| `last_message` (default) | Claude's final reply |
| `trace` | The session as JSON, one message per line. A `regex` sees every line; an `llm` judge sees the first 12 and the last 12 messages. Quotes are escaped, so match `\"`, not `"` |
| `files` | The paths Claude created during the run, one per line. Not their contents, not scaffold files, not files Claude only edited |
| `{ source: file, path: <path> }` | One file's contents after the run. PNG, JPEG, GIF and WebP are shown to an `llm` judge as images. The judge refuses other binaries such as `.pptx` or PDF, so have the case render them to an image or text first |
| `mock_calls` | Each call to a mocked MCP tool, with its input and the mock's answer |

## Grader types

| Type | Options | Passes when |
| :-- | :-- | :-- |
| `regex` | `pattern`, `flags`, `match`, `target` | The JavaScript regex is found. `match: not_contains` requires its absence; `match: "count:N"` requires exactly N matches. Case-insensitive is `flags: i`; inline `(?i)` is not supported |
| `tool_used` | `tool`, `input_match`, `min` (1), `max` (unlimited) | The number of calls to `tool` whose JSON-encoded input matches `input_match` is between `min` and `max`. "Never called" needs `min: 0` and `max: 0` |
| `tool_order` | `before`, `after` | Both were called and the first matching `before` call precedes the first matching `after` call. Each is a tool name or `{ tool, input_match }` |
| `file_exists` | `path` (glob), `exists` | A file created during the run matches, or none does with `exists: false` |
| `llm` | `criteria` (the file body in `.md` form), `focus` | A judge votes PASS in at least 2 of 3 votes |
| `baseline` | `baseline_file`, `criteria` | A judge finds the run meets the criteria at least as well as the reference transcript at `baseline_file`, a `.jsonl` in the case directory |

- The default judge for `llm` and `baseline` comes from the CLI: run `claude plugin eval --help` to see it. Set it with `--judge-model`. Use a Sonnet-tier or larger judge that is not the agent's own model, because a small judge can mark a correct but differently formatted answer wrong.
- Write `llm` rubrics as concrete `PASS if …` / `FAIL if …` claims. Keep them for short outputs, and grade long files with `regex`, which reads the whole file the same way every time.
- **Tool names to match:**
  - Skill calls: `tool: Skill` with `input_match: '"skill"\s*:\s*"(?:[\w-]+:)?<skill-name>"'`. The skill name is its directory name, or its frontmatter `name`, and the pattern also matches the `plugin:skill` form.
  - Plugin MCP tools: `mcp__plugin_<plugin>_<server>__<tool>`. Any character outside `A-Za-z0-9_-` becomes `_`.
  - Plugin agents: `<plugin>:<agent>`. Subfolders add segments, as in `<plugin>:review:security`.
  - The subagent tool is `Agent`, formerly `Task`.

## Scoring and the no-plugin baseline

- **Scores.** A run's score is the weighted fraction of its graders that passed. A case's score is the mean of its with-arm runs. A case passes when its score is at least `--threshold`, `1.0` by default.
- **Arms.** When a plugin resolves, each case also runs with no plugin loaded. Δ is the with-arm score minus the without-arm score.
- **One arm only.** A case runs a single arm under `--ablation none`, when the case resumes a `history_file` and the target is a path (pass `--ablation with-without` to compare), or when no plugin was found for it.
- **Excluded graders.** In a two-arm run these are reported with `scored: false` and count in neither arm:
  - every `tool_used` grader whose `tool` is `Skill`;
  - every `regex` grader with `target: mock_calls` and every `llm` grader with `focus: mock_calls`, when each mocked server in the case is one the plugin declares;
  - every grader marked `arm: with-only`.

  If all of a case's graders are excluded, they are scored normally. `arm: both` forces a grader into the score. Under `--ablation none` nothing is excluded, so the absolute score differs between the modes.
- **Baseline agent errors are expected.** In the baseline arm, a call to a plugin agent fails with `Agent type '<plugin>:<agent>' not found`.

## Ready-to-copy patterns

The skill fired. A display-only indicator under two arms; pair it with an outcome grader, because as a case's only grader it is scored and inflates Δ.

```markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?my-skill"'
---
```

The skill must not fire. This counts in both arms; pair it with an outcome grader.

```markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?my-skill"'
min: 0
max: 0
arm: both
---
```

The produced file has a heading:

```markdown
---
type: regex
target:
  source: file
  path: report.md
pattern: '(^|\n)## Summary\s*(\n|$)'
---
```

The reply mentions refunds in any letter case:

```markdown
---
type: regex
pattern: refund
flags: i
---
```

A judged outcome:

```markdown
---
type: llm
---

PASS if the reply names the failing test and the line that throws.
FAIL if it only restates the error message or proposes a fix without naming the test.
```

A build or test inside the run: the prompt asks Claude to run the command and write its outcome to a file. Grade that file with `regex` on `{ source: file, path: … }`, and prove the command ran with a `tool_used` grader on `Bash` whose `input_match` names the command. This needs a `Bash(...)` grant.
