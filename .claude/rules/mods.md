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
| [Overview](https://code.claude.com/docs/en/plugins/mods/overview.md) | How a mod works, Where mods run, Turn mods on or off, See which mods a session loaded, Decide whether to trust a mod |
| [Create a mod](https://code.claude.com/docs/en/plugins/mods/create.md) | Write a mod yourself, Get type definitions for your version, Check what Claude Code reads from your mod, Test the mod |
| [Reference](https://code.claude.com/docs/en/plugins/mods/reference.md) | Files, The hook function, Events → Tools, Mods API methods, Render sites, Elements, Limits, Commands |
| [Events](https://code.claude.com/docs/en/plugins/mods/events.md) | Guard or change a tool call, Approve or refuse a tool call before the user is asked, Check whether a tool call is read-only, The order mods run in, Handle a hook that fails |
| [Test a mod](https://code.claude.com/docs/en/plugins/mods/test.md) | Stub what Claude Code would answer, Follow the test kit's rules, Look up what a stub returns, Test a drawing, Test a policy mod |
| [Troubleshoot a mod](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md) | Find out why a mod does nothing, Check whether mods can load, Refusal messages, Messages from the built-in guard, A hook is skipped or a mod is unloaded, A tool call is denied, Read the debug log |
| [API](https://code.claude.com/docs/en/plugins/mods/api.md), [Interface](https://code.claude.com/docs/en/plugins/mods/interface.md), [Admin](https://code.claude.com/docs/en/plugins/mods/admin.md) | `$` calls and background work, drawing and `$.state`, organization controls and the built-in guard |
| [Permissions](https://code.claude.com/docs/en/permissions.md) | Precedence among rules, hooks, and mods; Hook approvals in plan mode |
| [`CHANGELOG.md`](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md) | Fetch it raw with `curl`; the docs changelog page is too large for WebFetch. Expect missing version headings and contract changes with no entry |
| [Docs index](https://code.claude.com/docs/llms.txt) | Find a mod page not listed here |

## Authority

- **Trust** the declarations the engine writes into `.claude-plugin/types/claude-code/index.d.ts` over any docs page when they disagree: the docs say so (Create a mod → Get type definitions for your version). Check the `// Written by Claude Code` header first: a stale file describes another build.
- **Refresh** those declarations by loading the mod in an interactive session (`claude --plugin-dir plugins/<name>`, then `/exit`; `expect` can drive it). `claude -p` never writes them. The debug line `type root … wrote nothing` means they are current. Claude Code also adds a root `tsconfig.json` that extends the generated one when the mod has none.
- **Run** `tsc` on the tests as well as the hooks: it flags a removed field read as `verdict.x`, but not an extra field in an async hook's `return`.

## Load and diagnose

- **Run** `claude plugin validate <dir>` first: it catches a misspelled event, a bad manifest and an unreadable module without a session. A pass with no `hooks` line means `hooks/hooks.json` has no `modules` key.
- **Run** `claude plugin test` from a folder with no mod to learn whether mods can load at all: `no hooks module to load` means yes, and `hooks modules are turned off …` names the blocker. It does not report `allowManagedModsOnly`.
- **Look** for problems where the session reports them: a dim transcript line under `--plugin-dir`, the debug log only (`claude --debug`) for an installed mod, and stderr for `claude -p --plugin-dir`.
- **Read** `hooks module <name> not loaded: <reason>` in the debug log for a refused module: managed `disableAllHooks`, `allowManagedHooksOnly`, `--bare`, a plugin of the same name that loads first, or the remote rollout switch.
- **Read** `hooks module did not load: <reason>` for a module whose top-level code threw, whose options do not fit `userConfig`, or that nests more than 2,000 scopes. A reason ending `the version loaded before is unloaded` means nothing runs until `/reload-plugins`.
- **Accept** the folder trust prompt before you test: no mod loads in an untrusted folder, and `--safe-mode` loads no installed plugin.
- **Confirm** what loaded with `/plugin` (`N mod active · <names>`) or the debug line `hooks module <name>@inline loaded (…); events: …`.
- **Edit** the working copy through `--plugin-dir`, which reloads on save. Edits to an installed plugin never take effect, because Claude Code runs the cached copy. A broken save logs `reload failed, the previous version stays loaded:`.
- **Write** your own debug lines with `$.ui.log(text, { to: 'debug' })`; without the second argument the line goes to the transcript.

## Where mods run

- **Claim** surfaces from Overview → Where mods run: hooks run in the terminal, the Desktop Code tab, the VS Code extension, `claude -p`, the Agent SDK, Remote Control and cloud sessions that receive the plugin; they do not run in a Desktop WSL session. Drawing appears only in the terminal, the Desktop Code tab and the VS Code extension.
- **Remember** that `disableAllHooks` and `allowManagedModsOnly` stop the mod and keep the rest of the plugin (skills, commands, agents, MCP) loaded.

## `tool.check`

- **Answer** with `{ decision: 'allow' | 'ask' | 'deny', reason? }`, or return `await next(e)` to leave the decision alone. Never return `decider`: the engine removed it with no changelog entry.
- **Expect** an unknown field in a hook's answer to be ignored, not to skip the hook: a stray field fails only the tests that assert it.
- **Rely** on the declarations for who answers a hook's `ask`: the engine pins `plugin` on it, puts it to a person (dialog, host callback or `PermissionRequest` hook), lets no classifier's allow settle it, and turns it into a deny where nobody can be asked. State the minimum version that has this routing, because an older engine puts the `ask` to the mode's decider, and in auto mode the classifier can approve it.
- **Order** your reasoning: `tool.check` runs after the `PreToolUse` hooks and before the permission dialog, the auto mode classifier and any `PermissionRequest` hook.
- **Use** `e.agentId` to tell a subagent's call from the main loop's. Read `e.isReadOnly` as present only when `true`, and never approve on it alone.
- **Remember** precedence: without managed settings or a Team or Enterprise login, a mod's `allow` overrides deny rules and `PreToolUse` blocks; with them, the built-in guard keeps the deny (`tried to lift a deny rule in your settings`). In plan mode a mod cannot approve a write.
- **Avoid** rewriting a tool call's input in `tool.call` or `turn.step` in auto mode: the server-side classifier reviewed the original input, so the call is denied with `a hook changed this call's input after the model wrote it`.

## Failure and limits

- **Expect** a hook that throws, times out or returns the wrong shape to be skipped (`<name>: <event> hook skipped: <reason>`, once per event and kind until reload), leaving the verdict beneath it when it failed before `next`, and its result when it failed after.
- **Fail closed** with `.catch` on every blocking hook. At `tool.check`, return `{ decision: 'deny', reason }` from it without testing `next.called`; at `tool.call`, test `next.called` first. A `.catch` has 1 second, and one that fails leaves the hook skipped.
- **Know** that `.catch` runs only when the hook itself throws or times out: events raised beneath the hook's own `$` calls skip the hook without asking `.catch`.
- **Budget** 10 seconds of a hook's own time per event (time inside `next` and `$` calls does not count), 30 seconds for `$.process.run` by default, and 4 MiB per `$.fs.read`. Read Reference → Limits before relying on any other bound.
- **Await** inside every loop: installed mods share one worker thread, a hook that blocks it gets its mod unloaded (`it crashed the hooks worker`), and three untraced crashes turn off every non-built-in mod for the session.

## State and reload

- **Keep** values in `$.state` or `$.store`, never in module-level variables: a reload re-initializes the module.
- **Reload** saved values in a `classic.SessionStart` hook: `/clear`, `/resume` and `/branch` reset `$.state` and do not fire `session.start` again.
- **Register** commands, tools and agents in `session.start`, which runs again in each fresh copy after a reload; a `$.agent.register` call from code still running in the old copy is refused.
- **Expect** that after the user presses Stop, a mod cannot start work until the next message.

## Interface

- **Return** `await next(e)` inside a `Box` when you draw the shared band, and give that `Box` no size or position props, or you hide every mod after yours.
- **Check** `e.surface` against the Render sites and Elements tables, and fall back to a transcript line or a command reply where nothing draws.
- **Open** a pane from a command or a button, and read `isPlaced`: a pane opened without the user asking waits for a wide terminal.

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

## User docs for a plugin with a mod

- **Tell** users how to diagnose an installed mod: `/plugin` names the active mods, and only `claude --debug` shows why one was refused or skipped.
- **List** what turns the mod off while the rest of the plugin stays: `disableAllHooks`, `allowManagedModsOnly`, `allowManagedHooksOnly`, `--safe-mode`, `--bare`.
- **Disclose** that in organizations with managed settings or a Team or Enterprise login, the built-in guard can refuse the mod or keep a deny it tried to lift.
