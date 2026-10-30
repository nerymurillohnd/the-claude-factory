# Fixtures and mocks

Read this when a case needs files, a git repository, an earlier conversation or MCP tools.

## Contents

- Seeding the workspace and the conversation
- Mocking MCP servers
- Mock file reference
- `expect` patterns
- Agent mocks, replay and the call budget
- Running against real servers

## Seeding the workspace and the conversation

Each run starts in an empty workspace. Add a `case.yaml` next to `prompt.md`:

```yaml
schema_version: "1.1"
name: changelog-from-diff
tags: [smoke]
context:
  scaffold_script: fixture.sh   # Bash script in the case directory
  add_dirs: [resources]         # case-directory folders Claude may read, read-only
  # history_file: earlier.jsonl # a transcript to resume; the prompt becomes the next user turn
```

### `scaffold_script`

The script runs **only with `--scaffold`**, as the user and outside the agent's sandbox, so pass that flag only for suites you or your organization wrote. `--no-scaffold` skips it explicitly.

- **Environment.** It starts in the empty workspace with a small fixed environment: your `PATH`, `HOME` set to the run's temporary home, `TMPDIR`, and constants such as `TERM=dumb`. The case's `EVAL_*` variables don't reach it, and nothing else from your shell does.
- **Failure.** A non-zero exit, or more than 120 seconds, scores that run 0 with `scaffold failed`.
- **What it may write.** Use it for files and git state only. Any `.claude/`, `CLAUDE.md` or `.mcp.json` it writes is never loaded, and files it creates are invisible to `files` and `file_exists`.
- **Test it for free first.** Run the script in a temporary folder and check the fixture before you pay for runs.

### `history_file`

A `.jsonl` transcript in the case directory. When the target is a path, the case runs one arm by default, and stderr prints a `single-arm (no Δ)` notice. Pass `--ablation with-without` to compare the resumed turn with and without the plugin.

### `add_dirs`

Grants read access only. Nothing in those folders is loaded as configuration.

## Mocking MCP servers

A run never starts the plugin's real MCP servers unless you opt in.

- **Substitute servers.** Claude Code registers a substitute under each server's own name: the key in the plugin's `.mcp.json` or `mcpServers`.
- **Mocked tools.** A tool with a mock file answers from that file and needs no `--allow-tools` grant, so don't add it to `allowed_tools` either.
- **Unmocked tools.** A tool with no mock file isn't available. A server with no mocks at all appears in the progress line as `plugin_<plugin>_<server>[not started: no mock]`.
- **Where mocks go.** Suite-wide mocks live in `evals/mocks/<server>/<tool>.md`. A case's own `mocks/` directory overrides them file by file. Use the bare tool name, not the `mcp__…` form.

Example: `evals/mocks/tracker/create_issue.md` guards the input and echoes the title:

```markdown
---
expect:
  title: string
  priority: [low, medium, high]
---

Created issue #4821: {{input.title}}
```

A call that violates `expect:` aborts the run with score 0. The JSON records it under `aborted`, with the server, tool and reason, and `error` stays `null`. Use `expect:` to assert what the plugin asked the server to do. To grade the calls themselves, point a `regex` at `target: mock_calls` or an `llm` at `focus: mock_calls`. In a two-arm run those graders are excluded from the score when every mocked server belongs to the plugin.

## Mock file reference

| Key | Default | Purpose |
| :-- | :-- | :-- |
| `type` | `fixed` | `fixed` returns the body. `agent` treats the body as instructions for a model that plays the server and sees earlier calls |
| `expect` | — | A map from dotted input paths to a type (`string`, `number`, `boolean`, `array`, `object`), a `/regex/`, a literal, or a list of allowed literals |
| `error` | `false` | `fixed` only: return the body as a tool error |
| `abort_when` | — | `agent` only: prose listing the only conditions under which the agent may abort the run |

- **Substitutions in the body.** `{{input.<field>}}` inserts a field of the call. `{{file:fixtures/{input.<field>}.json}}` inserts a file from `fixtures/` next to the mock.
- **`_server.md`.** One `type: agent` mock that answers several tools, listed in its `tools:` key. A `<tool>.md` for the same tool takes precedence. An `expect:` here is a load error unless `tools:` names a single tool, so put guards on the individual `<tool>.md`.
- **`_tools.json`.** A saved `tools/list` response from the real server, so mocked tools carry their real descriptions and input schemas.
- **Stubs.** A stub body still reading `TODO: replace with the canned result this tool should return` blocks the run until you fill it.

## `expect` patterns

A `/regex/` value uses a small dialect that is checked when the suite loads:

- **Allowed:** literal characters, `.`, escapes such as `\d`, and classes such as `[a-z]`.
- **Quantifiers:** `*`, `+`, `?` and `{m,n}`, each on a single character, escape or class.
- **Anchors:** an optional `^` at the start and `$` at the end.
- **Flags:** `i` and `s` only.
- **Not allowed:** groups, alternation, backreferences and lookaround. These stop the case from loading and score it 0. For several exact values, use a list of literals.
- **Length cap.** Values are checked only up to a maximum length, and a longer value counts as a violation. Anchor with `^` and keep quantifiers few.

## Agent mocks, replay and the call budget

- **Answers vary.** A `type: agent` mock answers through the judge model, so its output varies between runs and changes when you change `--judge-model`.
- **Recordings.** After a run that completes without an error or an abort, the agent-mock answers are saved under `results/<timestamp>/mock-recordings/`. `ADOPT.txt` there says which `.replay/<server>/` directory to copy each one into.
- **Replay.** Later runs answer an identical call from `mocks/.replay/<server>/` with no model call. Commit `mocks/.replay/` so CI is repeatable. Committed recordings ship in every user's copy of the plugin: check them for secrets and private data first.
- **Call budget.** All agent-mock calls in a run share one budget of 4 × `max_turns`, which is 40 at the default. Replayed calls count too. A call past the budget aborts the run with score 0 and `mock call budget exceeded`. Raise `max_turns` for flows that call a lot.

## Running against real servers

Either flag starts real processes, as you and outside the sandbox. Their tools also need a grant, such as `--allow-tools "mcp__plugin_my-plugin_github__*"`.

- `--allow-real-servers`: with `--mocks record` (the default), start the real server for each server that has no mock, and keep answering mocked tools from their files.
- `--mocks off`: ignore `mocks/` and start every server the plugin declares.

When the plugin's hooks or real servers can change the files the graders read, treat the scores as advisory unless you run them in an isolated container or CI runner.
