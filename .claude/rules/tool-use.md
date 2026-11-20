# Tools for files and code

- Read a file in full with Read before you change or judge it; past one Read page (2,000 lines or 25,000 tokens), keep reading with `offset` and `limit` until you have read all of it.
- Search shows matching lines, not files: Read in full every file you will edit, quote or base a decision on before you act on it.
- Search contents with the Grep tool and file names with the Glob tool when the session has them; otherwise, as on macOS and Linux where Claude Code leaves them out, use `rg` or `grep -rn` (`-C` for context) and `find` through Bash, and `awk` to pick fields or columns from their output.
- Use the LSP tool for code structure (definitions, references, symbols, callers), and confirm with Grep before renaming or deleting.
- Create files with Write and change them with Edit; never write files with `cat >`, `echo >`, heredocs, `sed -i` or inline scripts.
- Use Bash to run programs (tests, linters, builds, git), one short command per purpose: long, compound or unparseable commands, and redirects outside the project, prompt for approval.
- Put scratch files in the session's scratchpad, not in `/tmp`.
