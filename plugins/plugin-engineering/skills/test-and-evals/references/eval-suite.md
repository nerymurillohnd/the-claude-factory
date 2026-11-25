# Eval suites: layout, cases and graders

The files, fields and graders of a plugin eval suite, and how the arms are scored.

## Contents

- [Gotchas](#gotchas)
- [Layout](#layout)
- [prompt.md](#promptmd)
- [case.yaml](#caseyaml)
- [Graders](#graders)
- [What a grader looks at](#what-a-grader-looks-at)
- [Arms and what counts in the score](#arms-and-what-counts-in-the-score)
- [Graders that give a stable signal](#graders-that-give-a-stable-signal)
- [Another eval directory](#another-eval-directory)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- An unknown key in `prompt.md` frontmatter is an error, and a case with no grader fails to load with an `invalid case.yaml` error that names `graders`.
- Regex graders are JavaScript: put case-insensitivity in `flags: i`; inline `(?i)` isn't supported.
- `target: files` lists the paths Claude created, not their contents, and leaves out files a scaffold created or Claude only edited. Grade contents with `{ source: file, path: <path> }`, or an edit with `tool_used` on `Edit`.
- A "never called" check needs both `min: 0` and `max: 0`: `max: 0` alone can never pass.
- In a two-arm run a `tool_used` grader on `Skill` is left out of the score. A case whose only grader it is gets scored on it in both arms instead, so a skill that fires on every prompt looks like a gain. Give every case a grader on the result.
- `disallowed_tools` exists as a case field (changelog), but the docs don't say whether it goes in `prompt.md` or under `execution:` in `case.yaml`. Use `--disallow-tools` on the command instead, which `--help` documents.
- skill-creator's `evals/evals.json` is another format: neither tool reads the other's case files.

## Layout

- The eval directory is `evals/` under the plugin root, unless `experimental.evals` or `--eval-dir` says otherwise (last section).
- A directory is a case when it holds `prompt.md` or `case.yaml`. Everything inside a case directory belongs to that case. Group cases by nesting them under a directory that is not a case.
- Each run starts in an empty working directory, so a case that needs files seeds them through `context.scaffold_script` or `context.add_dirs` in `case.yaml`.
- Each run writes `<eval dir>/results/<timestamp>/`: add `results/` to `.gitignore`.

```text
evals/
├── <case>/
│   ├── prompt.md            # the prompt, with optional frontmatter
│   ├── case.yaml            # optional: setup, history, or the whole case
│   ├── graders/<name>.md    # one grader per file; the name is the file name
│   └── mocks/               # optional: this case's own mocks
├── mocks/<server>/          # suite-wide mocks: <tool>.md, _server.md, _tools.json, fixtures/
├── mocks/.replay/<server>/  # adopted agent-mock recordings
└── results/<timestamp>/     # aggregate-result.json, report.html, mock-recordings/
```

## prompt.md

The body is the prompt, sent exactly as written; `@path` mentions are not expanded. Frontmatter fields:

| Field | Default and rule |
| :-- | :-- |
| `schema_version` | `"1.1"`, set for you |
| `name` | the directory name; `--case` globs match it and the report keys on it |
| `description`, `expected_outcome` | for people; not used at run time |
| `tags` | `[]`; a case runs when any of its tags matches `--tag` |
| `plugins` | the nearest enclosing plugin; paths relative to the case directory; when detection misses, list the path up to the plugin, two parent-folder steps for a case directly under `evals/` |
| `runs` | 3, from 1 to 50; `--runs` overrides |
| `model` | the child session's default; `--model` overrides |
| `max_turns` | 10, up to 200; reaching it is a run error and usually lowers the score |
| `timeout_seconds` | 300, up to 3600 |
| `allowed_tools` | `[]`; grants only `Read`, `Glob`, `Grep`, `NotebookRead`, `Skill`, `AskUserQuestion`, `Agent`, `TodoWrite` and the task tools; any other tool needs `--allow-tools` on the command |
| `append_system_prompt` | appended to the child's system prompt |
| `env` | `{}`; keys must match `EVAL_[A-Z0-9_]*`, any other key fails the run |

Besides `EVAL_*`, a run receives `PATH`, locale, proxy and certificate settings, provider-selection and auth variables, and most `ANTHROPIC_*` and `CLAUDE_CODE_*` variables. To pass the plugin anything else, such as a toolchain setting, export it as an `EVAL_*` variable.

## case.yaml

- Requires `schema_version: "1.1"` and `name`.
- Top level: `description`, `tags`, `plugins`, `runs`, `expected_outcome`, `graders`.
- Under `execution:`: `model`, `max_turns`, `timeout_seconds`, `allowed_tools`, `append_system_prompt`, `env`, and `prompt`, which holds the whole case in `case.yaml`.
- Only in `case.yaml`: `context.scaffold_script`, `context.history_file`, `context.add_dirs`, `execution.prompt` and a `graders:` list. Each list entry takes `name` plus the grader file's keys, with an `llm` rubric in `criteria`.
- With both files, `prompt.md` frontmatter overrides the matching `case.yaml` fields, the `prompt.md` body is the prompt, and `graders/*.md` are added after the `case.yaml` graders.

## Graders

Every grader takes `type` (required), `weight` (default `1`, any positive number) and `arm` (unset, `with-only` or `both`). In a `.md` grader file the keys are frontmatter, and for `llm` the body is the criteria. There are no custom-code graders.

| Type | Keys | Passes when | Cost |
| :-- | :-- | :-- | :-- |
| `regex` | `pattern`, `flags`, `match`, `target` | the pattern matches; `match: not_contains` inverts it, `match: "count:N"` needs exactly N matches | free |
| `tool_used` | `tool`, `input_match`, `min` (1), `max` (unlimited) | the number of calls to `tool` whose JSON-encoded input matches `input_match` is within `min` and `max` | free |
| `tool_order` | `before`, `after` | both were called and the first `before` match precedes the first `after` match; each is a tool name or `{ tool, input_match }` | free |
| `file_exists` | `path` (glob), `exists` | a file created during the run matches, or none does with `exists: false` | free |
| `llm` | `criteria`, `focus` | the judge votes PASS in at least 2 of 3 calls | 3 judge calls per run |
| `baseline` | `baseline_file`, `criteria` | the judge finds the run at least as good as the reference `.jsonl` transcript in the case directory | 3 judge calls per run |

The documented check that a skill fired:

```yaml
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?your-skill-name"'
```

The skill's name is its directory under `skills/`; the optional prefix also matches `plugin-name:skill-name`.

The judge is "the model Claude Code uses for background tasks" on the page, and `haiku` in `claude plugin eval --help`. Pin it with `--judge-model` (`sonnet` or a full model ID) wherever the score must be comparable.

## What a grader looks at

`regex` takes `target` and `llm` takes `focus`, with the same values:

- `last_message` (default): the final response text.
- `trace`: the session as JSON, one message per line. `regex` sees every message, `llm` the first 12 and the last 12. Quotes and newlines are JSON-escaped, so match `\"`.
- `files`: the paths Claude created, one per line.
- `{ source: file, path: <path> }`: one file's contents after the run. An `llm` judge sees PNG, JPEG, GIF and WebP as images and refuses other binary files, such as `.pptx` or PDF.
- `mock_calls`: each call to a mocked MCP tool, with its input and the mock's answer.

## Arms and what counts in the score

- A run's score is the share of graders passed, weighted when weights are set; a case's score is the mean of its runs. A case passes when its with-arm score is at least `--threshold` (default `1.0`).
- With a plugin under test, every case runs with and without it (two arms), and Δ is the with-arm score minus the without-arm score.
- A case runs the with-arm only under `--ablation none`, when it resumes a `context.history_file` and the target is a path (a `single-arm (no Δ)` notice; `--ablation with-without` forces two arms), or when no plugin was found for it.
- In a two-arm run, these graders are left out of the score (`scored: false`) and shown in the with-arm as a `plugin-fired indicator`: every `tool_used` grader on `Skill`, every `regex` grader with `target: mock_calls` and `llm` grader with `focus: mock_calls` when each mocked server in the case is one the plugin declares, and every grader with `arm: with-only`. When every grader of a case is left out, they all count instead.
- `arm: both` counts a grader in both arms. A "must not invoke the skill" check is `tool: Skill`, the skill's `input_match`, `min: 0`, `max: 0`, `arm: both`.
- Under `--ablation none` nothing is left out, so absolute scores differ between the two modes.
- In the baseline arm, dispatching one of the plugin's agents fails with `Agent type '<plugin>:<agent-name>' not found`, which is expected. With the plugin, a case that lists `Agent` in `allowed_tools` can dispatch `<plugin>:<agent>`.

## Graders that give a stable signal

- Grade long output with `regex` over the file's contents; keep `llm` for short outputs, with concrete PASS and FAIL conditions.
- Give every case one grader on the result and one on the steps (`tool_used` or `tool_order`).
- To check a build or test inside a run, have the prompt ask Claude to run it and write the outcome to a file, grade the file, and add a `tool_used` grader whose `input_match` names the command.
- When the `tool_used: Skill` indicator passes but Δ is negative, suspect the judge: rerun with `--judge-model sonnet` and tighten the rubric.

## Another eval directory

- Set `"experimental": { "evals": "quality/evals" }` in `plugin.json`, or pass `--eval-dir quality/evals` to both `eval` and `eval init`; the flag wins. Cases, results and `init` output all move with it.
- The value is a plain relative directory name. An absolute path or `..` is an error as a flag, and a `Warning:` line with a fall-back to `evals/` as a manifest value.
- The manifest accepts a path or an array of paths, and only the array's first entry is used (manifest reference).

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Eval suite reference](https://code.claude.com/docs/en/plugin-evals#eval-suite-reference) when a field, grader key or default is not here or may have changed. It gives every key with its type and limit.
- Read [Write and refine cases](https://code.claude.com/docs/en/plugin-evals#write-and-refine-cases) when you write a case by hand. It gives the walkthrough and the skill-fired grader.
- Read [Score against the no-plugin baseline](https://code.claude.com/docs/en/plugin-evals#compare-against-a-no-plugin-baseline) when a score or Δ looks wrong. It gives which graders each arm counts.
- Read [Use a different eval directory](https://code.claude.com/docs/en/plugin-evals#use-a-different-eval-directory) when the suite lives outside `evals/`. It gives the manifest and flag rules.

## Exit

The cases and graders you need are written or reviewed against this file. Return to the step in `SKILL.md` that sent you here.
