---
paths:
  - "**/register.{js,ts}"
  - "plugins/*/hooks/*.ts"
  - "plugins/*/hooks/*.js"
  - "plugins/*/tsconfig.json"
  - "plugins/**/*.test.ts"
  - "plugins/*/tests/**"
  - "plugins/*/.claude-plugin/types/**"
  - "**/graders/**"
---

# Mods

Lessons verified on 2026-10-22 against the live mod docs and the installed engine. Mods change between releases, often without a changelog entry: re-read the sources below before you rely on any line here, and when a line disagrees with them, the sources win and this file gets fixed.

## Sources

| Page | Read when |
| :-- | :-- |
| [Mods reference](https://code.claude.com/docs/en/plugins/mods/reference.md) | Files, The hook function, Events → Tools (`tool.check` fields), Mods API methods, Limits, Commands |
| [React to events](https://code.claude.com/docs/en/plugins/mods/events.md) | Guard or change a tool call, Approve or refuse a tool call before the user is asked, Check whether a tool call is read-only, The order mods run in, Handle a hook that fails |
| [Test a mod](https://code.claude.com/docs/en/plugins/mods/test.md) | Stub what Claude Code would answer, Follow the test kit's rules, Look up what a stub returns |
| [Create a mod](https://code.claude.com/docs/en/plugins/mods/create.md) | Get type definitions for your version, Check what Claude Code reads from your mod, Test the mod |
| [Troubleshoot a mod](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md) | Read the debug log, `hook skipped`, A tool call is denied |
| [Use the mods API](https://code.claude.com/docs/en/plugins/mods/api.md), [Interface](https://code.claude.com/docs/en/plugins/mods/interface.md), [Admin](https://code.claude.com/docs/en/plugins/mods/admin.md), [Overview](https://code.claude.com/docs/en/plugins/mods/overview.md) | `$` calls, drawing, organization controls, where mods run |
| [Permissions](https://code.claude.com/docs/en/permissions.md) | Precedence among rules, hooks, and mods; Hook approvals in plan mode |
| [`CHANGELOG.md`](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md) | Fetch it raw with `curl`; the docs changelog page is too large for WebFetch. Expect missing version headings and contract changes with no entry |
| [Docs index](https://code.claude.com/docs/llms.txt) | Find a mod page not listed here |

## Authority

- **Trust** the declarations the engine writes into `.claude-plugin/types/claude-code/index.d.ts` over any docs page when they disagree: the docs say so (Create a mod → Get type definitions for your version). Check the `// Written by Claude Code` header first: a stale file describes another build.
- **Refresh** those declarations with an interactive session (`claude --plugin-dir plugins/<name>`, then `/exit`; `expect` can drive it unattended). `claude -p` never writes them. The debug line `type root … wrote nothing` means they are current.
- **Run** `tsc` on the tests as well as the hooks: it flags a removed field read as `verdict.x`, but not an extra field in an async hook's `return`.

## `tool.check`

- **Answer** with `{ decision: 'allow' | 'ask' | 'deny', reason? }`, or return `await next(e)` to leave the decision alone. Never return `decider`: the engine removed it with no changelog entry.
- **Expect** an unknown field in a hook's answer to be ignored, not to skip the hook: a stray field fails only the tests that assert it.
- **Rely** on the declarations for who answers a hook's `ask`: the engine pins `plugin` on it, puts it to a person (dialog, host callback or `PermissionRequest` hook), lets no classifier's allow settle it, and turns it into a deny where nobody can be asked. State the minimum version that has this routing, because an older engine puts the `ask` to the mode's decider, and in auto mode the classifier can approve it.
- **Order** your reasoning: `tool.check` runs after the `PreToolUse` hooks and before the permission dialog, the auto mode classifier and any `PermissionRequest` hook.
- **Use** `e.agentId` to tell a subagent's call from the main loop's. Read `e.isReadOnly` as present only when `true`, and never approve on it alone.
- **Remember** precedence: without managed settings or a Team or Enterprise login, a mod's `allow` overrides deny rules and `PreToolUse` blocks; in plan mode a mod cannot approve a write.

## Failure

- **Expect** a hook that throws, times out or returns the wrong shape to be skipped (`hook skipped` in the debug log), leaving the verdict beneath it when it failed before `next`, and its result when it failed after.
- **Fail closed** with `.catch` on every blocking hook. At `tool.check`, return `{ decision: 'deny', reason }` from it without testing `next.called`; at `tool.call`, test `next.called` first.
- **Know** that `.catch` runs only when the hook itself throws or times out: events raised beneath the hook's own `$` calls skip the hook without asking `.catch`.

## Tests (`claude plugin test`)

- **Name** test files `*.test.ts` anywhere in the plugin; each needs at least one `test()`.
- **Register** every stub before the test's first call on `$`, and fire `session.start` yourself when a hook depends on it.
- **Stub** every `$` call the mod makes: a mods API stub returns `{ value }` or `{ deny }` (a stub that throws is skipped, not a refusal); an event stub returns that event's own result. The kit itself answers only `$.ui.invalidate`, `$.state` and `$.session.append`.
- **Read** the `the engine reported:` block of a failed test: `no implementation for <name>` is a missing stub, `returned neither { value } nor { deny }` a bare value.
- **Know** that `$.tool.check` runs the `tool.check` hooks only, with no `PreToolUse` hook and no classifier, and that no test plays a person's yes: per the declarations, a `classic.PermissionRequest` stub answers an `ask`.
- **Keep** each served `$` call under 10 seconds and each test under 5 seconds unless it sets `timeoutMs`.
- **Prove** a test catches a failure: break the rule on purpose once, confirm the failure, restore the file and check it with a hash.

## Live evidence

- **Capture** a live run with `--debug-file <path>` and grep it for `hooks module <plugin>@inline loaded`, `tool.check settled in`, `executePermissionRequestHooks called for tool` and `Slow permission decision`. A long wait means a dialog waited for a person.
- **Check** that `overrides installed version` and `shadowed by local copy` appear, so `--plugin-dir` tests the local copy.
- **Run** a control beside the guarded case: in auto mode an unguarded `.claude/` edit shows `Allowed by auto mode classifier`, which separates the guard's dialog from the protected-folder prompt.
- **Avoid** proving behavior by scraping the terminal: the UI draws text with escape sequences and no spaces, and a pattern in your own prompt matches its echo. A person's answer to a dialog comes only from a person.
