# Primary sources and version assumptions

Tested with basedpyright 1.40.2 and Ruff 0.17.0 on 2026-10-12. These versions record what was tested; they are not a request to upgrade installed tools.

The links below are citations. Open them only when an installed tool behaves differently from this skill and network access is available; otherwise report the difference and the version you observed.

| Topic | Primary source | Use it to verify |
|---|---|---|
| Claude semantic client | [LSP tool behavior](https://code.claude.com/docs/en/tools-reference#lsp-tool-behavior) | Available operations and client limitations |
| Skill loading | [Claude skills](https://code.claude.com/docs/en/skills) | Discovery and supported instruction format |
| basedpyright CLI | [Command line](https://docs.basedpyright.com/latest/configuration/command-line/) | Statuses, JSON, warning failure, and explicit-file scope |
| basedpyright settings | [Config files](https://docs.basedpyright.com/latest/configuration/config-files/) | Rules, checking mode, and environment overrides |
| Interpreter default | [Better defaults](https://docs.basedpyright.com/latest/benefits-over-pyright/better-defaults/) | Conditional `.venv` discovery |
| Ruff scope/style | [Configuration](https://docs.astral.sh/ruff/configuration/) | Exclusions, force-exclude, cwd, and nearest-file config |
| Ruff fixes/status | [Linter](https://docs.astral.sh/ruff/linter/) | Fix safety and actual exit behavior |
| Tested releases | [basedpyright 1.40.2](https://github.com/DetachHead/basedpyright/releases/tag/v1.40.2), [Ruff 0.17.0](https://github.com/astral-sh/ruff/releases/tag/0.17.0) | Compatibility changes before changing assumptions |

Ruff 0.17.0 changes fallback Python versions and several rules/fix-display behaviors. A displayed unsafe suggestion is not evidence that an unsafe fix was applied. basedpyright's warnings/defaults differ from upstream Pyright; verify the installed checker rather than borrowing upstream severity assumptions.

The semantic control was tested on basedpyright 1.40.2. Alias behavior, client exposure, synchronization, and scope can change with versions or client configuration; retain the observed boundary and recheck when relying on a changed environment.
