---
name: python-lsp-intelligence
description: Navigates Python by symbol through basedpyright, resolves imports and aliases before a rename or deletion, and checks code with ruff and basedpyright using the project's own configuration. Use when editing, refactoring or diagnosing Python, fixing a ruff or basedpyright finding, finding every usage of a function, or explaining why an import fails only in the editor.
---

# Python code intelligence

Work with the language server first and the toolchain second. Nothing here mentions how the project is checked automatically; run every check yourself when the task calls for it.

## LSP and Grep are complementary

LSP owns questions about code structure; Grep owns questions about text. Route each question to its owner, and use both before changing or deleting code.

| Question | Owner | Operation |
| :-- | :-- | :-- |
| Where is X defined? | LSP | `goToDefinition` |
| Who uses or imports X? | LSP | `findReferences` |
| Type or signature of X? | LSP | `hover` |
| What does this file contain? | LSP | `documentSymbol`, before reading the whole file |
| Where is X, file unknown? | LSP | `workspaceSymbol`, always with `query` |
| Who calls X, what does X call? | LSP | `prepareCallHierarchy`, then `incomingCalls` / `outgoingCalls` |
| Implementations of an interface | LSP | `goToImplementation` |
| Where does a word appear as text (docs, comments, strings, config, scripts)? | Grep | — |
| Is it safe to delete or rename? | Both | LSP for code references, Grep for the blind spots below |

Every operation takes `filePath` (absolute), `line` (1-based) and `character` (1-based, UTF-16 code units: an emoji before the symbol counts 2). Raw LSP data in logs is 0-based: add 1 to both.

## Trusting a result

When a result is empty, shows only the definition, or will justify an edit or deletion, check all five before believing it:

1. **Position**: `hover` at the same spot shows the intended symbol. "No hover information" means a wrong position or no server, never "no usages".
2. **Warm-up**: a session's first workspace-wide query can be partial. Repeat until two consecutive results match (at most three).
3. **Scope**: only the session's working directory is indexed. Outside it, results are stable and incomplete: say so and use Grep plus reading.
4. **Freshness**: changes made outside Edit and Write (Bash, git, codegen, formatters) may never reach the index. Grep or Read those files instead of trusting counts.
5. **Blind spots**: Grep the name for the uses LSP cannot see (next section).

Only after all five does "no references" mean none. Never delete code on LSP evidence alone.

## Blind spots, every language

LSP sees static code references only. Grep the name in: strings and reflection (dynamic imports, `eval`, dispatch by name); entry points and config (package scripts, YAML, JSON, TOML, `.env`); framework injection (fixtures, decorators, registries, routes); shell scripts, CI, Makefiles, Dockerfiles; docs, comments, templates.

## Impact analysis (rename, signature change, deletion)

Copy this checklist into your working notes and tick each item:

- [ ] `findReferences` on the definition, with the five trust checks. The references are the must-change list.
- [ ] The language-specific steps in "Gotchas" below.
- [ ] Grep the blind spots. Textual mentions are listed as optional; any dynamic use blocks a deletion.
- [ ] After the change, run the checks in [toolchain.md](references/toolchain.md) and fix what they report.

## Gotchas (verified on fixtures)

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

Read [toolchain.md](references/toolchain.md) when configuring or installing ruff or basedpyright, wiring CI or an IDE, or raising strictness. Read [fixtures.md](references/fixtures.md) when a check passes code it should flag.
