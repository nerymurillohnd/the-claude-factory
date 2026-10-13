# Shell source map

External links are citations and optional lookups requiring network access. Offline, use the installed tool definition/help and local configuration; do not make web access a prerequisite for ordinary work.

Use the installed server's capabilities and tagged implementation for server-specific behavior. Select version-matching help/manuals when dialect, optional rules or formatting results change; review release notes for the change being investigated. The source map does not pin tools or promise a fixed capability set.

| Question | Primary source |
|---|---|
| What operations and tool schema are actually available? | [Claude LSP behavior](https://code.claude.com/docs/en/tools-reference#lsp-tool-behavior), plus the loaded tool definition |
| How does server discovery/navigation work? | [bash-language-server](https://github.com/bash-lsp/bash-language-server), [releases](https://github.com/bash-lsp/bash-language-server/releases); inspect the installed version's tag |
| Which dialects and formatting options are supported? | [shfmt manual](https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd), [releases](https://github.com/mvdan/sh/releases) |
| Which rc keys, flags and statuses apply? | [ShellCheck manual](https://github.com/koalaman/shellcheck/blob/master/shellcheck.1.md), [releases](https://github.com/koalaman/shellcheck/releases) |
| What does a particular SC code mean? | [ShellCheck wiki](https://www.shellcheck.net/wiki/) |
| What happens at runtime? | [Bash manual](https://www.gnu.org/software/bash/manual/bash.html) |
