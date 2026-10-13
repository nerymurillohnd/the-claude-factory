# Bash (bash-language-server)

Server: `bash-language-server start` from the `bash-lsp` plugin, for `.sh`, `.bash`, `.command`.
Binary installed with `npm install -g bash-language-server` (nvm-managed Node). Behaviour below verified
2026-09-29 with bash-language-server 5.8.1 on a fixture project.

## Observed behaviour

| Situation | What the server returns | Meaning |
|---|---|---|
| First `findReferences` of a session | Definition only | Warm-up; the repeat returned the full set |
| Two files each define a function with the same name | `findReferences` on **either** lists both definitions and every call | Matching is by **name**, not by what a script sources (upstream lists scope-based references as "to be implemented"): results over-report. Using the list as a rename set would also rename the unrelated function |
| Call in a script without an extension (`bin/backup`) | Missing from `findReferences`; `documentSymbol` there says `No LSP server available for file type:` | Extensionless scripts are never indexed. Grep them |
| Call in a hidden directory (`.claude/hooks/stop.sh`) | Missing until that file is opened by a query; with the `bash-lsp` plugin's `GLOB_PATTERN`, `.claude/` and `.github/` are indexed | The server's default discovery skips hidden paths; other hidden directories stay invisible. Grep them |
| `goToDefinition` on a call in a script that `source`s a library | Jumps to the library definition | Works when the `source` path is resolvable |
| `prepareCallHierarchy` | `Unhandled method textDocument/prepareCallHierarchy` | Unsupported; use `findReferences` |

## Before renaming or deleting a Bash function

1. Take the LSP list, then drop every hit that belongs to a same-named function in a file the caller does not `source`.
2. Grep the bare name across the whole tree, including files without an extension.

## Bash blind spots (static references LSP never reports)

Verified: each case below returned only the definition.

- **`trap <fn> EXIT`** handlers
- **Calls through a variable**: `action="fn"; "$action"`
- **Hook commands in JSON** (`settings.json`: `"command": "bash -c 'source lib.sh && fn'"`)

Also treat as blind spots (by the same mechanism): `eval`, `xargs`/`bash -c`/`sh -c` command strings,
CI YAML, `package.json` scripts, Makefiles, cron and launchd entries.
