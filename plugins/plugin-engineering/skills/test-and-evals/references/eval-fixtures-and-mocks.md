# Eval fixtures and mocks

How a case seeds its workspace or conversation, and how it stands in for the plugin's MCP servers.

## Contents

- [Gotchas](#gotchas)
- [Seed the workspace or the conversation](#seed-the-workspace-or-the-conversation)
- [Mock MCP servers](#mock-mcp-servers)
- [Mock files](#mock-files)
- [Patterns in expect](#patterns-in-expect)
- [Agent mocks and replays](#agent-mocks-and-replays)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- A `scaffold_script` runs only with `--scaffold`, as the user and outside the agent's sandbox. Ask the user before you pass `--scaffold`, and name the flag in the question.
- Real MCP servers never start in a run unless `--allow-real-servers` or `--mocks off` asks for them, and then they run as the user, outside the OS sandbox. A server with no mock shows in the `mocked:` progress line as `plugin_<plugin>_<server>[not started: no mock]`, and its tools are unavailable.
- A mock's `<server>` folder takes the server's name as the plugin's MCP configuration spells it.
- A call that breaks a mock's `expect:` aborts the run with score 0, reported as `aborted` with the server, the tool and the reason.
- An `expect:` pattern outside the documented dialect, such as a group, an alternation or a lookaround, keeps the case from loading; it scores 0 and the error names the pattern. List the allowed literals instead.
- Keep secrets, credentials and private data out of prompts, fixtures, transcripts, mocks and `mocks/.replay/`: the eval directory sits inside the plugin, and every install of the plugin copies it to the user's machine.

## Seed the workspace or the conversation

All three live in `case.yaml`, under `context:`:

- `scaffold_script`: a Bash script in the case directory. It gets the user's `PATH`, a `HOME` set to the run's temporary home, `TMPDIR` and fixed values such as `TERM=dumb`, and nothing else, not even the case's `EVAL_*` variables. A non-zero exit or more than 120 seconds scores that run 0 with `scaffold failed`. Project configuration it writes, such as a `.claude/` folder or a `CLAUDE.md`, is not loaded. `--no-scaffold` skips it explicitly.
- `history_file`: a `.jsonl` transcript in the case directory; the prompt becomes the next user turn. With a path target such a case runs the with-arm only.
- `add_dirs`: directories inside the case directory, added read-only.

`file_exists` and `target: files` don't see files the scaffold created: grade their contents with `{ source: file, path: <path> }`, or an edit with `tool_used` on `Edit`.

## Mock MCP servers

- Put one file per tool at `evals/mocks/<server>/<tool>.md` for the whole suite, or in a case's own `mocks/<server>/`. A case's file replaces the suite's file of the same name, file by file.
- Each server is replaced by a substitute registered under its name. Mocked tools need no `--allow-tools`; tools with no mock are unavailable.
- `--mocks record`, the default, answers from the mocks, starts no real server and saves agent-mock answers. `--mocks off` ignores `mocks/`, starts every real server and gates their tools by `--allow-tools`.
- `--allow-real-servers`, with `--mocks record`, also starts the real servers that have no mock.
- A real server's tools need the server started and a grant such as `--allow-tools "mcp__plugin_<plugin>_<server>__*"`.

## Mock files

The body is the tool's result. It can use `{{input.<field>}}`, and `{{file:fixtures/{input.<field>}.json}}` to answer from a fixture file. Frontmatter keys:

| Key | Values |
| :-- | :-- |
| `type` | `fixed` (default), or `agent` for a judge model that plays the server from the body's instructions |
| `expect` | dotted input paths mapped to a type name (`string`, `number`, `boolean`, `array`, `object`), a `/regex/`, a literal, or a list of literals |
| `error` | `true` to answer as a tool error; `fixed` only, default `false` |
| `abort_when` | prose listing the only conditions under which the agent mock may abort the run; `agent` only |

Two more files can sit in a server's folder:

- `_server.md`: one `type: agent` mock that answers every tool its `tools:` list names. A `<tool>.md` for the same tool wins, and `expect:` there is a load error unless `tools:` lists a single tool.
- `_tools.json`: a saved `tools/list` response, so the mocked tools carry the server's real descriptions and schemas.

## Patterns in expect

The dialect accepts literals, `.`, escapes such as `\d`, classes such as `[a-z]`, the quantifiers `*`, `+`, `?` and `{m,n}` on one character, escape or class, an optional `^` and `$`, and the flags `i` and `s`. Each pattern has a maximum length of value it checks, and a longer value counts as a violation: quantifiers lower that length, and a leading `^` raises it.

## Agent mocks and replays

- An agent mock sees the earlier calls of the run as history.
- A run may make up to 4 × `max_turns` agent-mock calls (40 at the default), replayed calls included. A `mock budget` progress line tracks them; past the budget the run aborts with score 0 and `mock call budget exceeded`.
- After a run with no error and no abort, its agent-mock answers are saved under the results folder's `mock-recordings/`, with an `ADOPT.txt` that names the `mocks/.replay/<server>/` folder to copy them to. Copied recordings answer identical calls with no model call; commit `mocks/.replay/`.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Set up fixtures and mocks](https://code.claude.com/docs/en/plugin-evals#set-up-fixtures-and-mocks) when a case needs files, a git repository, an earlier conversation or an MCP stand-in. It gives worked examples of each.
- Read [Mock files](https://code.claude.com/docs/en/plugin-evals#mock-files) when a mock key or the `expect` dialect is in question. It gives every key and the dialect's limits.

## Exit

The case's context and mocks are written, and each mocked server matches a server the plugin declares. Return to the step in `SKILL.md` that sent you here.
