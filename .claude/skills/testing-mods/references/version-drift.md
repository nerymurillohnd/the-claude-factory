# Where the docs and the binary disagree (read before quoting messages)

The docs lag releases; the installed binary and the CHANGELOG win.

Before you quote a message or rely on version-sensitive behavior:

1. Run `claude --version`.
2. Read the CHANGELOG's mod, `plugin test` and `plugin validate` entries since the build that matters (raw: https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md).
3. Reproduce the message with the smallest failing mod on the installed build, and quote that output.
4. Never take facts from `mods/types/claude-code.d.ts` in the `anthropics/claude-code` repository: it lags the build; use the declarations the installed build writes.

## Measured traps

- **A `hooks.json` with neither `hooks` nor `modules`.** Expect `validate` to exit 1 with `hooks.json must have \`hooks\` (the hook matchers) or \`modules\` (hooks modules), or both`, not to pass. Reproduce the case of a valid `hooks` object with a misspelled `modules` key before you describe it.
- **A mods-API stub that returns a bare value.** Match the error on `not a result object`, `no result` or `neither`: the wording differs from the docs' `returned neither { value } nor { deny }`, and `undefined` gives `returned no result`.
- **The `hooks module <name>@inline loaded (...)` debug line.** Confirm it in an interactive session: it may not appear in a `claude -p --debug-file` run.
- **Drawn trees in `$.ui.mount` tests.** Assert with `toMatchObject` or on single fields, never an exact `toEqual` on a whole tree: each root carries `part: { plugin }`.
- **`.catch` on a gating hook.** Expect it to run only on a throw or a timeout; never rely on the reference's `re-entry` kind.
- **A served `$` method in a test.** Answer within ten seconds, or the call fails as it would in a session.
- **A failed `expect` or a refused stub answer in a registered hook.** Expect it to fail the test.
- **A `session.append` hook that drops blocks.** Expect the test to fail when it removes tool calls, tool results or thinking blocks a real session keeps.
- **`validate` notes on where hooks run.** Never rely on them: take organization effects from `/en/plugins/mods/admin`. Use `validate --json`'s `gatingHooks` and `hasCatch` for the gating hooks.
- **A hook an earlier plugin skipped.** Recognize the transcript line `<mod>: its <event> hook was skipped. "<plugin>" runs first and sent the event on past it.`
- **`next.to` in a mod a user installs.** Never call it: `validate` passes it, but the loader refuses the module with `hooks module not loaded; next.to is available to managed plugins (prependPlugins / appendPlugins) only, and this plugin is user (policy/scan)`.
- **Load errors.** Read the file named in a nested-too-deep error, and the line named in a rebound top-level `var` error.
- **Two plugins with the same name.** Check the `/plugin` Errors tab: only one of them loads a hooks module.
- **Generated type declarations.** Load the mod in an interactive `--plugin-dir` session to get them: `-p` and SDK sessions never write them.
- **`$.state` without a `types` key.** Keep the contract at `./types/index.d.ts`; `validate` then accepts the references.
- **A sandboxed shell command.** Never expect it to write into a `--plugin-dir` folder.
- **`turn.start`.** Tell the main loop from subagents' and teammates' turns by `e.agentId`, absent on the main loop.

## Open upstream issues

Check each issue's state before you rely on its workaround.

- **#103915:** `validate` can pass a module the loader refuses when `$` is passed in a call with a spread argument; pass `$` directly.
- **#105020:** `validate` cuts the `hooks:` and `calls:` lines at about 1,000 characters, in text and `--json`; read the module for the full list.
- **#103055:** `claude plugin test` on a pipe can lose the tail of its output, summary included, and exit 0; run `scripts/check-mod.sh`, which writes to a file and requires the summary.
- **#99045:** the VS Code chat panel draws mods, but `prompt.edit` never fires there; don't rely on it in VS Code.
