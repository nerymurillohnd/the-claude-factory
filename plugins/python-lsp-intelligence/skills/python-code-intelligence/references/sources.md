# Python source map

External links are citations and optional lookups requiring network access. Offline, use the installed tool definition/help and local configuration; do not make web access a prerequisite for ordinary work.

Read the installed tool's help/configuration and select matching documentation or tagged source when an option, severity or behavior differs. Check release notes when adopting a changed feature or investigating a regression. These links locate authoritative material; they do not pin a release or label a version as permanently current.

| Question | Primary source |
|---|---|
| What semantic operations can the client expose? | [Claude LSP behavior](https://code.claude.com/docs/en/tools-reference#lsp-tool-behavior); the loaded tool definition supplies the actual schema |
| How does skill discovery work? | [Claude skills](https://code.claude.com/docs/en/skills) |
| How do JSON output, warning failure and file targets work? | [basedpyright CLI](https://docs.basedpyright.com/latest/configuration/command-line/) |
| Which interpreter/rules apply? | [basedpyright configuration](https://docs.basedpyright.com/latest/configuration/config-files/) |
| Which exclusions and fixes apply? | [Ruff configuration](https://docs.astral.sh/ruff/configuration/), [linter](https://docs.astral.sh/ruff/linter/) |
| Which typing APIs are available on the target Python? | [Python typing](https://docs.python.org/3/library/typing.html#typing.TypeGuard); choose the target-version documentation |
| What changed in the installed release? | [basedpyright releases](https://github.com/DetachHead/basedpyright/releases), [Ruff releases](https://github.com/astral-sh/ruff/releases) |
