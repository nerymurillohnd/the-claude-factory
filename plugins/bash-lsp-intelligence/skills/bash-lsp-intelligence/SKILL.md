---
name: bash-lsp-intelligence
description: Use before writing, editing, refactoring or renaming code in a shell script (.sh, .bash, a hook or CI script, a file with a bash or sh shebang), even for a one-line change, and when ShellCheck reports a finding such as SC2086, a script fails under set -euo pipefail, or a function is defined in more than one sourced file. Traces source chains through bash-language-server before trusting a same-named function, and formats and checks the result with the project's own shfmt and ShellCheck configuration. Not for PowerShell or other languages.
---

# Bash and POSIX shell code intelligence

Work with the language server first and the toolchain second. This skill does not assume a post-edit hook is installed; run the checks yourself when the task calls for it.

## Before you start: start the language server

Do these steps once per session, before you read or edit the first shell file of the task, and again after `/reload-plugins` or when every `LSP` call starts failing:

1. Binary: run `command -v bash-language-server`. When it prints nothing, the language server is not installed: offer its install as "Missing tools" below says, and go to step 4.
2. Tool: when the `LSP` tool is not loaded, load it with `ToolSearch` and the query `select:LSP`. When that finds nothing, this session runs no language servers, as in cloud sessions and in the Claude app's chat and Cowork: go to step 4.
3. Start: call `documentSymbol` on a shell script of the task, or on another `.sh` file of the project when the task creates the first one, alone in its message; Claude Code starts the server on that first call. Repeat it until the three-identical rule below holds. When every call errors, the server can't start here: go to step 4.
4. Without a language server: answer each `LSP` question in the table below with Grep and reading the files, report semantic evidence as unavailable and why, and run the checks under "Checks" all the same.

Then run `command -v shfmt shellcheck`: the checks under "Checks" need both. Offer each one missing as "Missing tools" says, and report its check as not run until it is there.

### Missing tools

Never install a tool yourself: it changes the user's machine. Give the user the install command from [toolchain.md](references/toolchain.md) for their system, and tell them to run it at this session's prompt, typed after a `!`, as in `! <install command>`: Claude Code runs it in the session's shell and adds its output to the conversation, so you see whether it worked. The VS Code extension has no `!` prefix, and a command that waits for a password, such as `sudo apt install`, may not get one there; in both cases they run it in a terminal. Once it has run, repeat the `command -v` check. For a newly installed language server, ask the user to run `/reload-plugins`, then repeat steps 2 and 3. If every call still fails, say that Claude Code starts the server from the `PATH` of the shell it was launched from, so the user may need to restart Claude Code, after putting the install folder on that `PATH`.

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
| Who calls X, what does X call? | LSP, then reading | `findReferences` for the callers; read the body of X for what it calls |
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

- Public API: a function or script is public API when code outside the repository can call it: a script installed or documented as a command (put on `PATH` through `bin/`, a package's `bin` entry or an install step in the README), or a library file other projects `source`. Ask the user before renaming or deleting one, naming how outside code reaches it.

Copy this checklist into your working notes and tick each item:

- [ ] `findReferences` on the definition, with the five trust checks. The references are the must-change list.
- [ ] The language-specific steps in "Gotchas" below.
- [ ] Grep the blind spots. Textual mentions are listed as optional; any dynamic use blocks a deletion.
- [ ] After the change, run the [Checks](#checks) below and fix what they report.

## Gotchas

- **Functions match by name.** Two unrelated same-named functions share one `findReferences` list, so it over-reports and is never a rename set. Before renaming, drop every hit whose file the caller does not `source`, directly or transitively.
- **Extensionless scripts are never indexed** (`bin/tool`), nor are files in hidden folders the server's glob doesn't cover. Grep them.
- **No call hierarchy and no implementation lookup.** bash-language-server declares neither `callHierarchyProvider` nor `implementationProvider`, so `prepareCallHierarchy` and `goToImplementation` fail: use `findReferences` and read the bodies.
- **`trap fn EXIT`, `"$action"` dispatch, `eval`, `bash -c` strings and hook commands in JSON** are static text to the server: Grep the bare name across the tree before any deletion.
- **A `.sh` suffix does not make zsh code Bash.** Check the shebang; ShellCheck rejects zsh (SC1071), so a zsh file is never clean by ShellCheck.
- **`shfmt -w` rewrites in place.** Re-read a file after running it and before the next edit.

## Checks

Run them yourself after a change, on every script you touched and every script that sources it:

- `shfmt -w <files>`, then `shellcheck <files>`; `https://www.shellcheck.net/wiki/SC<code>` explains a code. The project's `.editorconfig`, `.shellcheckrc` and `SHELLCHECK_OPTS` set the rules. Where the project has no `.editorconfig`, run `shfmt -i 2 -ci -bn -w <files>`; where it has no ShellCheck configuration, run `shellcheck -o all -S style -x -a -P SCRIPTDIR <files>`. These are the post-edit hook's defaults, so your result matches the hook's.
- `bash -n <file>` for syntax, one script per invocation.
- Exercise the changed launch path, arguments, exit status and traps in a controlled context; never run a deploy or delete script to lint it.

Read [toolchain.md](references/toolchain.md) when configuring or installing shfmt or ShellCheck, wiring CI or an IDE, or when a finding needs the project's intended style. Read [fixtures.md](references/fixtures.md) when a check passes code it should flag; it runs the files in `references/fixtures/`.
