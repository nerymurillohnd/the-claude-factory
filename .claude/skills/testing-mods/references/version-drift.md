# Where the docs and the binary disagree (read before quoting messages)

The docs lag releases by days; the CHANGELOG and the installed binary win. Evidence labels: **[obs 2.1.310]** observed by running the installed CLI during this skill's authoring; **[changelog X]** from the CHANGELOG entry for version X (raw: https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md); **[docs]** only from the docs pages; **[unverified]** could not be confirmed.

When a version-sensitive answer matters, re-check: run the command on the installed build, `grep` the CHANGELOG for the mod/test/validate entry, and compare. The mods types in the `anthropics/claude-code` repo (`mods/types/claude-code.d.ts`) were "written by Claude Code 2.1.277" and also lag.

## Known mismatches and recent behavior changes

| Topic | Docs say | Reality |
| :- | :- | :- |
| Missing/misspelled `modules` key | `validate` passes and lists no `hooks` line | **[obs 2.1.310]** if the file also lacks `hooks`, `validate` exits 1 with `hooks.json must have \`hooks\` (the hook matchers) or \`modules\` (hooks modules), or both`. With a valid `hooks` object and a misspelled `modules` key the docs behavior is **[unverified]**. |
| Mods-API stub returns a bare value | `returned neither { value } nor { deny }` | **[obs 2.1.310]** `returned something that is not a result object`; returning `undefined` gives `returned no result`. Match on `not a result object` / `no result` / `neither` when grepping. |
| Debug line `hooks module <name>@inline loaded (...)` | present in debug log | **[unverified in `-p`]** not seen in `claude -p --debug-file` runs with 2.1.310; confirm interactively. |
| Drawn trees in `$.ui.mount` tests | `{ type, props, children }` | **[obs 2.1.310]** + **[changelog 2.1.299]** trees carry `part: { plugin }` (e.g. `{"type":"Text","props":{},"children":["Thinking"],"part":{"plugin":"test"}}`). An exact `toEqual` on a whole tree fails without `part`; use `toMatchObject` or assert on fields. |
| `.catch` on gating hooks | reference lists a `re-entry` kind | **[changelog 2.1.301]** `.catch` runs only on throw/timeout; the `re-entry` kind may be stale **[unverified]**. |
| Served `$` methods in tests | not stated | **[changelog 2.1.299]** a served `$` method must answer within 10 s. |
| Failed `expect` / refused stub answer in a registered hook | partially described | **[changelog 2.1.292]** now fails the test. |
| `mock.session` / `$.session.append` | needs ≥ 2.1.293 [docs] | **[changelog 2.1.293]** added. **[changelog 2.1.295]** a `session.append` hook that dropped blocks no longer passes the test. |
| `validate --json` | | **[changelog 2.1.290]** `gatingHooks` with `hasCatch`. **[changelog 2.1.304]** removed notes predicting where hooks run. **[changelog 2.1.295]** README install-line advice added. |
| Hooks skipped where an org manages Claude Code | | **[changelog 2.1.299]** note added; **[changelog 2.1.304]** transcript line when an earlier plugin skips your mod's hook. |
| Load-error wording | | **[changelog 2.1.309]** nested-too-deep error names the file; **[changelog 2.1.295]** rebound top-level `var` error names the line. |
| Same-name plugins | | **[changelog 2.1.296]** /plugin Errors tab notes when another plugin of the same name holds the hooks-module name. |
| Toast rate limiting | dropped within 2 s | **[docs]** removed in 2.1.290. |
| `Claude Code exited after an unrecoverable interface error` on a bad `ui.render` | | **[docs]** fixed in 2.1.289 (becomes `threw while drawn`). |
| `claude plugin install <plugin> --marketplace <source>` | | **[docs]** shell form 2.1.292+, in-session form 2.1.275+. |
| Minimum versions | | Mods ≥ 2.1.287 (Desktop ≥ 2.1.286); VS Code extension ≥ 2.1.299 to draw, ≥ 2.1.304 without feature-flag fetch **[docs]**. |
| Generated type declarations | written when a mod loads | **[changelog 2.1.295]** written only where a mod is being developed: an interactive `--plugin-dir` session, never `-p` or the SDK. |
| `$.state` checks in `validate` | | **[changelog 2.1.299]** `validate` no longer rejects `$.state` references when `plugin.json` has no `types` key and the contract is at `./types/index.d.ts`. |
| Sandboxed shell and `--plugin-dir` | | **[changelog 2.1.299]** a sandboxed shell command can no longer write into a `--plugin-dir` folder. |
| `turn.start` | main loop only | **[changelog 2.1.299]** also raised for subagents' and teammates' turns; tell them apart by `e.agentId` (absent on the main loop). |
| `validate` passes a module the loader refuses | | **[issue #103915, open]** observed on 2.1.304 with `$` passed in a call with a spread argument. |
| `validate` footprint lines | | **[issue #105020, open]** `hooks:` and `calls:` lines cut at about 1,000 characters, text and `--json`. |
| `claude plugin test` on a pipe | | **[issue #103055, open]** can lose the tail of its output, summary included, and exit 0; `scripts/check-mod.sh` writes to a file and requires the summary. |
| VS Code chat panel | | **[issue #99045, open]** draws mods since extension 2.1.301 (comment, 2026-10-18), but `prompt.edit` never fires there. |

## Process to refresh this table

1. `claude --version`.
2. `grep -n -i -E 'mod|plugin (test|validate)|hooks module' CHANGELOG.md` in a shallow clone of `anthropics/claude-code`, newest entries first.
3. Reproduce any message you intend to quote with the smallest failing mod; record the build.
