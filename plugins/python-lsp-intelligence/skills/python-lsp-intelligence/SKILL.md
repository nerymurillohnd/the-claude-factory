---
name: python-lsp-intelligence
description: Use before writing, editing, refactoring, renaming, moving or deleting Python code in .py or .pyi files, even for a one-line fix, and when ruff or basedpyright reports a finding, an import fails only in the editor, or the user asks where a function is used. Finds every caller through basedpyright before a change, since grep misses aliased and re-exported names, and checks the result with the project's own ruff and basedpyright configuration instead of default rules. Not for other languages, nor for Python questions that touch no project file.
---

# Python code intelligence

Work with the language server first and the toolchain second. This skill does not assume that anything checks your edits automatically: run the commands under "Checks" yourself after a change.

## Before you start: start the language server

Do these steps once per session, before you read or edit the first Python file of the task, and again after `/reload-plugins` or when every `LSP` call starts failing:

1. Binary: run `command -v basedpyright-langserver`. When it prints nothing, the language server is not installed: tell the user to install it as [toolchain.md](references/toolchain.md) says, and go to step 4.
2. Tool: when the `LSP` tool is not loaded, load it with `ToolSearch` and the query `select:LSP`. When that finds nothing, this session runs no language servers, as in cloud sessions and in the Claude app's chat and Cowork: go to step 4.
3. Start: call `documentSymbol` on a Python file of the task, or on another Python file of the project when the task creates the first one, alone in its message; Claude Code starts the server on that first call. Repeat it until the three-identical rule below holds. When every call errors, the server can't start here: go to step 4.
4. Without a language server: answer each `LSP` question in the table below with Grep and reading the files, report semantic evidence as unavailable and why, and run the checks under "Checks" all the same.

Then run `command -v ruff basedpyright`: the checks under "Checks" need both. Tell the user about each one missing, give its install command from [toolchain.md](references/toolchain.md), and report its check as not run.

### Three identical results

A language server can answer before it has indexed the project, and its first answers can be partial or wrong. Repeat every `LSP` operation you rely on, with the same arguments, until three consecutive results are identical, at most six calls. When no three match within six, record the result as unstable and confirm it with Grep and reading.

## LSP and Grep are complementary

LSP owns questions about code structure; Grep owns questions about text. Route each question to its owner, and use both before changing or deleting code.

| Question | Owner | Operation |
| :-- | :-- | :-- |
| Where is X defined? | LSP | `goToDefinition` |
| Who uses or imports X? | LSP | `findReferences` |
| Type or signature of X? | LSP | `hover` |
| What does this file contain? | LSP | `documentSymbol`, before reading the whole file |
| Where is X, file unknown? | LSP | `workspaceSymbol`, always with `query` |
| Who calls X, what does X call? | LSP | `incomingCalls` / `outgoingCalls` on the function's position; `prepareCallHierarchy` only confirms that the position names a function |
| Implementations of an interface | LSP | `goToImplementation` |
| Where does a word appear as text (docs, comments, strings, config, scripts)? | Grep | — |
| Is it safe to delete or rename? | Both | LSP for code references, Grep for the blind spots below |

Every operation takes `filePath` (absolute), `line` (1-based) and `character` (1-based, UTF-16 code units: an emoji before the symbol counts 2). Raw LSP data in logs is 0-based: add 1 to both.

## Trusting a result

When a result is empty, shows only the definition, or will justify an edit or deletion, check all five before believing it:

1. **Position**: `hover` at the same spot shows the intended symbol. "No hover information" means a wrong position or no server, never "no usages".
2. **Warm-up**: the three-identical rule under "Before you start" holds for this result.
3. **Scope**: only the session's working directory is indexed. Outside it, results are stable and incomplete: say so and use Grep plus reading.
4. **Freshness**: changes made outside Edit and Write (Bash, git, codegen, formatters) may never reach the index. Grep or Read those files instead of trusting counts.
5. **Blind spots**: Grep the name for the uses LSP cannot see (next section).

Only after all five does "no references" mean none. Never delete code on LSP evidence alone.

## Blind spots, every language

LSP sees static code references only. Grep the name in: strings and reflection (dynamic imports, `eval`, dispatch by name); entry points and config (package scripts, YAML, JSON, TOML, `.env`); framework injection (fixtures, decorators, registries, routes); shell scripts, CI, Makefiles, Dockerfiles; docs, comments, templates.

## Impact analysis (rename, signature change, deletion)

- Public API: a name is public API when code outside the repository can import or run it: the project is a published package (a `[project]` table in `pyproject.toml`, or a `setup.py`), and the name is importable from one of its packages without a leading underscore, listed in `__all__`, or an entry point in `[project.scripts]` or `[project.entry-points]`. Ask the user before renaming or deleting one, naming how outside code reaches it.

Copy this checklist into your working notes and tick each item:

- [ ] `findReferences` on the definition, with the five trust checks. The references are the must-change list.
- [ ] The language-specific steps in "Gotchas" below.
- [ ] Grep the blind spots. Textual mentions are listed as optional; any dynamic use blocks a deletion.
- [ ] After the change, run the checks in [toolchain.md](references/toolchain.md) and fix what they report.

## Gotchas

- **Aliases aren't followed.** After `from m import f as g`, `findReferences` on `f` lists the import line but not the calls to `g`. Run it on `g` too, and keep the alias unless the rename includes it.
- **PEP 723 scripts show false import errors in the server** (`reportMissingImports`, cascading `reportUnknown*`): it can't see the script's uv environment. Check such a script with `basedpyright --pythonpath "$(uv python find --script <file>)" <file>`.
- **`ruff format` and `ruff check --fix` rewrite in place.** Re-read a file after running them and before the next edit.
- **Diagnostics after each edit cover the edited file only.** A caller broken by a signature change surfaces when you run basedpyright on it; do that for every file `findReferences` listed.
- **pytest fixtures, entry points and `__all__` are strings to the server.** Grep `tests/`, `conftest.py`, `pyproject.toml` (`[project.scripts]`, `[project.entry-points]`) and `__all__` lists before calling a name unused.

## Checks

Run them yourself after a change, on every file you touched and every caller:

- `ruff check --fix <files>` then `ruff format <files>`; `ruff rule <CODE>` explains a code.
- `basedpyright <files>` from the project root, so it reads the project's `pyrightconfig.json` or `pyproject.toml`; add `--outputjson` for machine-readable output.
- The project's tests for the changed behavior.

Fix the cause of a finding. Never silence one with `# noqa`, `# type: ignore`, `cast()` or a relaxed rule; narrow untrusted data with a real check instead of casting it. When you can show a finding is a false positive, report it with the evidence and let the project owner decide.

Read [toolchain.md](references/toolchain.md) when configuring or installing ruff or basedpyright, wiring CI or an IDE, or raising strictness. Read [fixtures.md](references/fixtures.md) when a check passes code it should flag.
