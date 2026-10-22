---
paths:
  - "plugins/*/.claude-plugin/plugin.json"
  - "plugins/*/hooks/hooks.json"
  - "**/register.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
  - "plugins/*/hooks/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx}"
  - "plugins/*/types/index.d.ts"
  - "plugins/**/*.test.{ts,tsx}"
  - "plugins/*/tests/**"
  - "plugins/*/tsconfig.json"
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
| [Reference](https://code.claude.com/docs/en/plugins/mods/reference.md) | Files, The hook function, Events (every table), Mods API methods, Render sites, Elements, Limits, Settings and environment variables, Commands |
| [Events](https://code.claude.com/docs/en/plugins/mods/events.md) | Guard or change a tool call, Approve or refuse a tool call before the user is asked, Check whether a tool call is read-only, The order mods run in, Handle a hook that fails |
| [Test a mod](https://code.claude.com/docs/en/plugins/mods/test.md) | Stub what Claude Code would answer, Follow the test kit's rules, Look up what a stub returns, Test a drawing, Test a policy mod |
| [Troubleshoot a mod](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md) | Find out why a mod does nothing, Check whether mods can load, Refusal messages, Messages from the built-in guard, A hook is skipped or a mod is unloaded, A tool call is denied, Read the debug log |
| [API](https://code.claude.com/docs/en/plugins/mods/api.md), [Interface](https://code.claude.com/docs/en/plugins/mods/interface.md), [Admin](https://code.claude.com/docs/en/plugins/mods/admin.md) | `$` calls and background work, drawing and `$.state`, organization controls and the built-in guard |
| [Permissions](https://code.claude.com/docs/en/permissions.md) | Precedence among rules, hooks, and mods; Hook approvals in plan mode |
| [Plugins → Loading](https://code.claude.com/docs/en/plugins/loading.md) | Plugins synced from claude.ai, the load order by manifest name, Hooks when two enabled plugins share a name, Keep a session-only plugin from loading |
| [Declarations on GitHub](https://github.com/anthropics/claude-code/blob/main/mods/types/claude-code.d.ts), [built-in guard source](https://github.com/anthropics/claude-code/tree/main/mods/sec-default) | A method or element not on the pages. The GitHub copy can be older than the installed build |
| [`CHANGELOG.md`](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md) | Fetch it raw with `curl`; the docs changelog page is too large for WebFetch. Expect missing version headings and contract changes with no entry |
| [Docs index](https://code.claude.com/docs/llms.txt) | Find a mod page not listed here |

## Authority

- **Trust** the declarations the engine writes into `.claude-plugin/types/claude-code/index.d.ts` over any docs page and over the GitHub copy when they disagree: the docs say so (Create a mod → Get type definitions for your version; Reference, opening note). Check the `// Written by Claude Code` header first: a stale file describes another build.
- **Expect** the Reference page to lag: it says it covers an older build. For example, it lists a `re-entry` kind for `next.error`, while the installed declarations allow only `throw` and `timeout`.
- **Refresh** those declarations by loading the mod in an interactive session (`claude --plugin-dir plugins/<name>`, then `/exit`; `expect` can drive it). `claude -p` never writes them. The debug line `type root … wrote nothing` means they are current. Claude Code also adds a root `tsconfig.json` that extends the generated one when the mod has none.
- **Run** `tsc` on the tests as well as the hooks: it flags a removed field read as `verdict.x`, but not an extra field in an async hook's `return`.

## Files and the hook function

- **Declare** exactly one module path in `hooks/hooks.json` → `modules` (`"modules": ["./register.ts"]`); classic settings hooks can sit beside it under `hooks`. The module is an ES module that exports `register(on, options)`.
- **Read** `options` as the plugin's `userConfig` values with defaults filled in, and treat a missing value as its default.
- **Declare** `$.state` values and any namespace the mod adds in `types/index.d.ts`, named by `types` in the manifest. It is not the engine's `.claude-plugin/types/`.
- **Treat** `e` as deeply frozen: change an event by passing a copy to `next`, as in `next({ ...e, text })`.
- **Write** `turn.step` and `process.spawn` hooks as async generators; every other hook is an async function.
- **Read** `next.budget.remainingMs` before slow work, and `next.origin` to know who fired the event (`{ plugin: 'engine', tier: 'core' }` for Claude Code).
- **Treat** every `$` call as fallible: each mods API method is also an event, and a mod that runs before yours can answer it with `{ deny }` or a `{ value }` of its own.

## Load and diagnose

- **Run** `claude plugin validate <dir>` first (`--strict` fails on warnings, `--json` prints a machine report): it catches a misspelled event, a bad manifest and an unreadable module without a session. A pass with no `hooks` line means `hooks/hooks.json` has no `modules` key.
- **Run** `claude plugin test` from a folder with no mod to learn whether mods can load at all: `no hooks module to load` means yes, and `hooks modules are turned off …` names the blocker. It does not report `allowManagedModsOnly`.
- **Look** for problems where the session reports them: a dim transcript line under `--plugin-dir`, the debug log only (`claude --debug`) for an installed mod, and stderr for `claude -p --plugin-dir`.
- **Read** `hooks module <name> not loaded: <reason>` in the debug log for a refused module: managed `disableAllHooks`, `allowManagedHooksOnly`, `--bare`, a plugin of the same name that loads first, or the remote rollout switch.
- **Read** `hooks module did not load: <reason>` for a module whose top-level code threw, whose options do not fit `userConfig`, or that nests more than 2,000 scopes. A reason ending `the version loaded before is unloaded` means nothing runs until `/reload-plugins`.
- **Accept** the folder trust prompt before you test: no mod loads in an untrusted folder, and `--safe-mode` loads no installed plugin. Managed `disableSideloadFlags` rejects `--plugin-dir` at startup.
- **Confirm** what loaded with `/plugin` (`N mod active · <names>`) or the debug line `hooks module <name>@inline loaded (…); events: …`.
- **Edit** the working copy through `--plugin-dir`, which reloads on save. Edits to an installed plugin never take effect, because Claude Code runs the cached copy. A broken save logs `reload failed, the previous version stays loaded:`. Set `CLAUDE_CODE_PLUGIN_DIR_WATCH=1` for a long `-p` session to reload too, and `CLAUDE_CODE_PLUGIN_DIRS` where you cannot pass the flag.
- **Set** test values for `userConfig` under `pluginConfigs` keyed `<name>@inline` for a `--plugin-dir` mod, or the plugin id for an installed one; project settings are not read for them.
- **Write** your own debug lines with `$.ui.log(text, { to: 'debug' })`; without the second argument the line goes to the transcript.

## Where mods run

- **Claim** surfaces from Overview → Where mods run: hooks run in every session that loads the plugin, whatever the model provider: the terminal (JetBrains included), the Desktop Code tab, the VS Code extension, `claude -p`, the Agent SDK, Remote Control and cloud sessions that receive the plugin; they do not run in a Desktop WSL session. Drawing appears only in the terminal, the Desktop Code tab and the VS Code extension.
- **Remember** that `disableAllHooks` and `allowManagedModsOnly` stop the mod and keep the rest of the plugin (skills, commands, agents, MCP) loaded.
- **Expect** the built-in guard `sec-default@builtin` (`cc-plugin-sec-default`) ahead of user mods on machines with managed settings or a Team or Enterprise login.

## Copies of the same plugin

- **Know** which copy runs (Plugins → Loading → the load order, Hooks when two enabled plugins share a name): copies compare by manifest name, a `--plugin-dir` copy beats an installed one, and an installed one beats the `<name>@synced` copy from claude.ai, which is reported as not loaded. Only one copy per name loads a hooks module; `/plugin` → **Errors** says `Its hooks module does not load` for the other.
- **Test** a mod you also have installed or synced with `--plugin-dir`, and confirm `overrides installed version` and `shadowed by local copy` in the debug log. Set `"enabledPlugins": {"<name>@inline": false}` to stop a session-only copy from shadowing.
- **Expect** a synced copy to load its hooks in the terminal only in sessions signed in with the claude.ai account: none load under `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` or `apiKeyHelper`, without feature-flag fetching (`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`), in bare mode, under `--safe-mode`, or with `--setting-sources` that leaves out `user`. A synced change arrives at the next start, or after `/reload-plugins` when the session says `Plugins changed`.

## Events to handle with care

- **Answer** `tool.check` with `{ decision: 'allow' | 'ask' | 'deny', reason? }`, or return `await next(e)` to leave the decision alone. Never return `decider`: the engine removed it with no changelog entry.
- **Expect** an unknown field in a hook's answer to be ignored, not to skip the hook: a stray field fails only the tests that assert it.
- **Rely** on the declarations for who answers a hook's `ask`: the engine pins `plugin` on it, puts it to a person (dialog, host callback or `PermissionRequest` hook), lets no classifier's allow settle it, and turns it into a deny where nobody can be asked. State the minimum version that has this routing, because an older engine puts the `ask` to the mode's decider, and in auto mode the classifier can approve it.
- **Promise** no reason in the dialog for a file in a protected folder such as `.claude/`: there Claude Code shows its own prompt with the change and no hook reason (observed live), even though the declarations say the dialog shows it. A declined prompt tells the model only `User rejected update`, so a guard's advice reaches Claude only through a deny. A session-wide approval the person picks in that prompt does not settle the hook's later asks (observed live: the next guarded edit asked again).
- **Order** your reasoning: `tool.check` runs after the `tool.call` and `PreToolUse` hooks and before the permission dialog, the auto mode classifier and any `PermissionRequest` hook.
- **Use** `e.agentId` to tell a subagent's or in-process teammate's call from the main loop's, and `e.ceiling` to see a connector tool your organization set to `ask`. Read `e.isReadOnly` as present only when `true`, and never approve on it alone.
- **Remember** precedence: without managed settings or a Team or Enterprise login, a mod's `allow` overrides deny rules and `PreToolUse` blocks; with them, the built-in guard keeps the deny (`tried to lift a deny rule in your settings`) unless `allowModsToOverrideDenyRules` is set. In plan mode a mod cannot approve a write.
- **Avoid** rewriting a tool call's input in `tool.call` or `turn.step` in auto mode: the server-side classifier reviewed the original input, so the call is denied with `a hook changed this call's input after the model wrote it`.
- **Guard** `SendMessage` in `tool.call` too when you gate subagents: `agent.spawn` does not run again when Claude resumes a subagent.
- **Change** only `text` and `frontmatter` in a `skill.prompt` hook; changing any other field fails the hook.
- **Filter** a telemetry hook with `{ to: 'collector' }`, or the mod fails `claude plugin validate`.

## Failure and limits

- **Expect** a hook that throws, times out or returns the wrong shape to be skipped (`<name>: <event> hook skipped: <reason>`, once per event and kind until reload), leaving the verdict beneath it when it failed before `next`, and its result when it failed after.
- **Fail closed** with `.catch` on every blocking hook. At `tool.check`, return `{ decision: 'deny', reason }` from it without testing `next.called`; at `tool.call`, test `next.called` first. `next.error.kind` is `throw` (also a refused result or a worker that ended) or `timeout`. A `.catch` has 1 second, and one that fails leaves the hook skipped.
- **Know** that `.catch` runs only when the hook itself throws or times out: events raised beneath the hook's own `$` calls skip the hook without asking `.catch`.
- **Budget** 10 seconds of a hook's own time per event (50 ms for `prompt.edit`; time inside `next` and `$` calls other than `$.clock.sleep` does not count), 30 seconds for `$.process.run` by default, 4 MiB per `$.fs.read` or `$.fs.write`, and 4,096 characters for a `drop` or `deny` reason. Name commands, tools, subagent types and panes with letters, digits, `_` and `-`, up to 64 characters. Read Reference → Limits before relying on any other bound.
- **Await** inside every loop: installed mods share one worker thread, a hook that blocks it gets its mod unloaded (`it crashed the hooks worker`), and three untraced crashes turn off every non-built-in mod for the session.

## State, files and reload

- **Keep** values in `$.state` or `$.store`, never in module-level variables: a reload re-initializes the module.
- **Use** `$.store` (shared by every session on the machine, 4 MiB of JSON) for data several sessions change: `$.fs.write` is not atomic and another process can read a half-written file.
- **Reload** saved values in a `classic.SessionStart` hook: `/clear`, `/resume` and `/branch` reset `$.state` and do not fire `session.start` again.
- **Register** commands, tools and agents in `session.start`, which runs again in each fresh copy after a reload; a `$.agent.register` call from code still running in the old copy is refused.
- **Expect** that after the user presses Stop, a mod cannot start work until the next message.
- **Know** that `$.prompt.submit({ text })` reaches Claude after a sentence naming your mod as the sender; only `asUser: true` sends it as the user's words. `$.mcp.connect` reaches only servers your own manifest lists.

## Interface

- **Return** `await next(e)` inside a `Box` when you draw the shared band, and give that `Box` no size or position props, or you hide every mod after yours.
- **Check** `e.surface` against the Render sites and Elements tables, and fall back to a transcript line or a command reply where nothing draws. The VS Code extension ignores some props (`Button` `hotkey`, `Code` colors and more).
- **Use** `weight` instead of the deprecated `bold`, and a `borderStyle` from the documented list: any other name draws no border.
- **Open** a pane from a command or a button, and read `isPlaced`: a pane opened without the user asking waits for a wide terminal.

## Tests (`claude plugin test`)

- **Name** test files `*.test.ts` or `*.test.tsx` anywhere in the plugin; each needs at least one `test()`. The command exits 1 when a test fails.
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
- **List** what the mod reaches, from the `hooks:` and `calls:` lines of `claude plugin validate`, with what each call touches and what the mod never does (writes, network, model calls): a mod runs with the user's permissions and no sandbox (Overview → Decide whether to trust a mod), and tell users to run `claude plugin validate` themselves before installing.
- **Remember** that a mod cannot restyle or change what a permission prompt shows.
- **Show** how to set the mod's options from the shell (`claude plugin install … --config <key>=<value>`) or in `/config`.
