# Primary sources and version assumptions

Tested with bash-language-server 5.8.1, shfmt 3.14.1, and ShellCheck 0.11.0 on 2026-10-12. These versions record what was tested; they are not a request to upgrade tools.

The links below are citations. Open them only when an installed tool behaves differently from this skill and network access is available; otherwise report the difference and the version you observed.

| Topic | Primary source | Verify |
|---|---|---|
| Claude semantic client | [LSP behavior](https://code.claude.com/docs/en/tools-reference#lsp-tool-behavior) | Operations exposed to the model |
| Server behavior | [bash-language-server](https://github.com/bash-lsp/bash-language-server/tree/server-5.8.1) | Scope, discovery, configuration, and actual capabilities |
| Formatter | [shfmt manual](https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd) | Dialects, EditorConfig, write/diff behavior |
| ShellCheck options | [Manual](https://github.com/koalaman/shellcheck/blob/v0.11.0/shellcheck.1.md) | Configuration lookup, flags, and exit behavior |
| Rule explanations | [ShellCheck wiki](https://www.shellcheck.net/wiki/) | The specific SC code and exceptions |
| Sourced paths | [SC1090](https://www.shellcheck.net/wiki/SC1090) | Dynamic path and source metadata limitations |
| Runtime shell semantics | [Bash manual](https://www.gnu.org/software/bash/manual/bash.html) | Splitting, traps, sourcing, arrays, and statuses |
| Tested releases | [ShellCheck 0.11.0](https://github.com/koalaman/shellcheck/releases/tag/v0.11.0), [shfmt 3.14.1](https://github.com/mvdan/sh/releases/tag/v3.14.1) | Changed rule defaults and formatter fixes |

shfmt has gained Zsh support, but ShellCheck's supported dialects are a separate boundary. The skill focuses on Bash/POSIX work and does not infer that every `.sh` is one of those dialects. A changed tool can change results without a source edit.

On bash-language-server 5.8.1, same-named functions in unrelated scripts came back in one reference list, and call hierarchy was unsupported. The skill handles both by the server's response, not by version: it checks identity through source relationships and falls back when an operation is unsupported.
