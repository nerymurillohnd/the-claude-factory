# Testing a mod with `claude plugin test`

Source: https://code.claude.com/docs/en/plugins/mods/test (check `version-drift.md` for known mismatches with newer builds).

Tests run from the shell, with no session, sign-in or network: `claude plugin test [dir]`. Exit status 1 on any failure. Files are `*.test.ts` (or `.tsx`) anywhere in the plugin directory and import from `claude-code/testing`. A test file may import the mod's own files and sibling `.ts` helpers.

```typescript
import { expect, test } from 'claude-code/testing'

test('/tally counts tool calls', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' })) // stub: answers in Claude Code's place
  await $.tool.call({ tool: 'Bash', command: 'ls' }) // fires the event through the mod's hooks
  const answer = await $.command.run({ command: 'tally', args: '' })
  expect(answer.text).toBe('Claude has made 1 tool calls since this mod loaded')
})
```

- `$` in a test **acts as Claude Code**; it is not the mods API a hook receives. Its methods fire the event of the same name and resolve to the result: `$.tool.call`, `$.command.run`, `$.prompt.submit`, `$.session.start`, `$.turn.complete`, `$.turn.step`, `$.session.receive`, `$.classic.<Event>` (settings-hook events such as `Stop`, `SessionStart`). A test cannot fire a mods-API call such as `ui.close` directly; trigger it through the mod (press the button).
- `on(name, fn)` registers a **stub** (a hook answering in Claude Code's place). Name a mods-API stub without `$.`: stub `store.get` answers the mod's `$.store.get`.
- Each test starts with the module freshly loaded, no hook called, module variables at initial values, `$.state` at defaults (as after `/clear`).
- Default test timeout is 5000 ms (`timeoutMs`); a served `$` method must answer within 10 s (changelog 2.1.299).
- `$.tool.check` in a test runs only the mod's `tool.check` hooks: no `PreToolUse` hook, no classifier. No test plays a person's yes; a `classic.PermissionRequest` stub answers an `ask` (the declarations for the installed build, `EngineToolCall`).

## Kit rules (the errors new authors hit first)

1. **Register every stub before the first call on `$`.** Late `on()` throws `on("ui.render") after the test first called $`.
2. **`session.start` does not run by itself.** If a hook depends on it, stub `session.start` (`() => ({ cwd: '/work' })`) and any calls the hook makes (e.g. `command.register` → `() => ({ value: undefined })`), then `await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })`. A missing stub makes the call reject with `no implementation for command.register` and the kit silently skips the hook; the skip is listed under `the engine reported:` only if a later check fails.
3. **A hook that returns `next(e)` needs a stub** to answer, e.g. for `ui.render`: `on('ui.render', () => ({ type: 'Text', props: {}, children: ['drawn by Claude Code'] }))`. Otherwise mounting fails with `no implementation for ui.render`.
4. **`turn.step` stub is an async generator**; read the stream to the end:

   ```typescript
   on('turn.step', async function* ($, e) {
     yield { kind: 'text', index: 0, text: 'ok' }
     return { turnId: e.turnId, index: e.index, answer: 'ok', toolUses: [], stopReason: 'end_turn', usage: null }
   })
   const stream = $.turn.step({ turnId: 't', index: 0, model: 'claude-test', messageCount: 1 })
   let step = await stream.next()
   while (step.done !== true) step = await stream.next()
   const result = step.value
   ```
5. **Tool calls**: `await $.tool.call({ tool: 'Bash', command: 'ls' })` (tool name and args as fields) plus a `tool.call` stub returning `{ result }`.

## Stub result shapes

Mods-API calls → `{ value }` (or `{ deny: 'reason' }` to make the call reject in the mod; a stub that _throws_ is skipped instead). Claude Code's events → the event's own result. A bare value or `undefined` from a mods-API stub fails the test (message wording differs by build, see `version-drift.md`). A failed test prints a block headed `the engine reported:`; errors worth recognizing there: `no implementation for <name>` (mod made a call nobody stubbed) and the bare-value error above.

| Mod calls / passes on                                                                                         | Stub                                                                                                                                                                  |
| :------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `$.command.register`, `$.tool.register`, `$.ui.toast`, `$.ui.log`, `$.ui.status`, `$.ui.close`, `$.store.set` | `() => ({ value: undefined })` (text is `e.text` for toast/log)                                                                                                       |
| `$.store.get`                                                                                                 | `($, e) => ({ value: saved.get(e.key) })`                                                                                                                             |
| `$.fs.read`                                                                                                   | `($, e) => ({ value: e.path.endsWith('notes.md') ? '# Notes' : '' })` (`e.path` is absolute; use `endsWith`)                                                          |
| `$.ui.open`                                                                                                   | `() => ({ value: { isPlaced: true } })`                                                                                                                               |
| `$.ui.ask`                                                                                                    | a `tool.call` stub (arrives as `AskUserQuestion`): `($, e) => ({ result: { answers: { [e.questions[0].question]: 'Run it' } } })`; check `e.tool` first               |
| `$.model.complete`                                                                                            | `() => ({ value: { isAnswered: true, text: '...', usage } })` where `usage` = `{ input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens }` |
| `$.process.run`                                                                                               | `($, e) => ({ value: { exitCode: 0, stdout: '...', stderr: '' } })` (`e.argv`, `e.init.cwd/timeoutMs`)                                                                |
| any call that should fail                                                                                     | `() => ({ deny: 'the reason' })`                                                                                                                                      |
| `session.start`                                                                                               | `() => ({ cwd: '/work' })`                                                                                                                                            |
| `turn.start`                                                                                                  | `($, e) => ({ turnId: e.turnId })`                                                                                                                                    |
| `tool.call`                                                                                                   | `() => ({ result: '...' })`                                                                                                                                           |
| `turn.complete`                                                                                               | `() => ({ text: '' })`; fire with `$.turn.complete({ turnId, answer, durationMs, isAborted: false, usage: null })`                                                    |
| `prompt.submit`                                                                                               | `($, e) => ({ text: e.text })`                                                                                                                                        |
| `prompt.fill`                                                                                                 | `() => ({ isFilled: true })`; `$.prompt.read` → `() => ({ value: { text: '...', cursor: 0 } })`                                                                       |
| `$.ui.copy`                                                                                                   | `() => ({ value: { isCopied: true } })`                                                                                                                               |
| `$.ui.notify`                                                                                                 | `() => ({ value: { isSent: true, channel: 'terminal_bell' } })`                                                                                                       |
| `$.session.messages`                                                                                          | `() => ({ value: [{ role: 'assistant', text: '...', toolUses: [] }] })`                                                                                               |
| `$.session.id`, `$.agent.list`                                                                                | `() => ({ value: 'abc123' })`, `() => ({ value: [] })`                                                                                                                |
| `session.send`                                                                                                | `() => ({ isDelivered: true })` (`e.to` is a string)                                                                                                                  |
| `session.receive`                                                                                             | `($, e) => ({ text: e.text })`; fire with `$.session.receive({ origin: { kind: 'peer-send-message' }, text })`                                                        |
| `ui.render`                                                                                                   | `() => ({ type: 'Text', props: {}, children: ['...'] })`                                                                                                              |

The kit answers `$.ui.invalidate`, `$.state` and `$.session.append` itself. Everything else the mod calls needs a stub.

`expect` has `toBe`, `toEqual`, `toMatch`, `toMatchObject`, `toContain`, `toBeDefined`, `toBeUndefined`, `toThrow`, each with `.not`. A failed `expect` inside a plain-function hook or stub fails the test, the hook is skipped, and the output names it (`in the test's store.set hook`).

## Mocks

- `mock.clock(on)` / `mock.clock(on, { now: 5000 })` → clock starting at 0: `await clock.advance(ms)`, `await clock.set(ms)`, `clock.now()`, `await clock.settle()`, `await clock.sleep(ms)` (inside a stub: answers only after the test advances that far). Without it `$.clock.now()` fails with `no implementation for clock.now`.
- `mock.store(on, { count: 7 })` answers `$.store` from initial entries but returns nothing; to assert what the mod saved, write the two `store.get`/`store.set` stubs yourself with a `Map`.
- `mock.env(on, { CI: 'true' })` answers `$.env.get`.
- `mock.session(on)` → `appended()` lists rows added with `$.session.append`, oldest first. Needs Claude Code ≥ 2.1.293.

## Drawing tests

`const ui = await $.ui.mount({ plugin, surface, component, requestId, viewport: { columns: 100, rows: 30 }, props })` draws a render site through the mod's `ui.render` hook. `surface` is `terminal`, `desktop`, `vscode` or `mobile`; loop over surfaces to cover several apps. `props` must be what Claude Code passes for that site (render-sites table and the types for the installed build).

| Handle method                            | Effect                                                                                      |
| :--------------------------------------- | :------------------------------------------------------------------------------------------ |
| `press({ key })`                         | press the `Button` with that key                                                            |
| `input({ key, text })`                   | type into the `Input` and press Enter (`kind: 'change'` to not submit)                      |
| `select({ key, value })`                 | pick an option in the `Select`                                                              |
| `find({ key })` / `find({ type, text })` | first matching element `{ type, props, children }` or `undefined` (`text` string or RegExp) |
| `unmount()`                              | remove the drawing                                                                          |

Methods resolve after the handler finishes, so assert on the next line. A drawing test checks the returned tree and its validity for that app, not how the app paints it. Elements the tests address need a non-empty string `key` (see "needs a key" in troubleshooting).

After `/clear` behavior: skip `session.start`, stub `classic.SessionStart` (`() => ({})`), fire `await $.classic.SessionStart({ source: 'clear' })`, then mount and assert the restored value.

## Policy mods

`tier('prepend' | 'append' | 'builtin')` once at the top of the file loads the mod under test in that tier (default `user`). `test('name', { plugins: [{ name, register(on) {...}, tier? }] }, async ($, on) => {...})` supplies inline second mods. Mods load at the first call on `$`; a refusal throws there with `<mod>: refused by <policy-mod>: <reason>`.

## Checking that a check can fail

A green run proves little. Make a check fail on purpose (flip an expected string, remove a stub, drop a `key`) and confirm it fails for the right reason, in particular for third-party mods whose own tests you are relying on. Break a copy, or record `shasum -a 256` of the file before the change and check it after you restore it, so the break never ships.

## Settings for a live test session

- **Option values:** set a `--plugin-dir` mod's `userConfig` values under `pluginConfigs` keyed `<name>@inline`, and an installed mod's under its plugin id, in user or managed settings (`/en/plugins/mods/reference`, settings table). Project settings are not read for them.
- **Turn a session-only copy off:** `"enabledPlugins": {"<name>@inline": false}` in any settings file keeps a `--plugin-dir` copy from shadowing the installed one (`/en/plugins/loading`, "Keep a session-only plugin from loading").
- **Reload in a long `claude -p` run:** `CLAUDE_CODE_PLUGIN_DIR_WATCH=1` reloads `--plugin-dir` mods on save in a non-interactive session; interactive `--plugin-dir` sessions reload on save already (`/en/plugins/mods/reference`).
- **Your own debug lines:** `$.ui.log(text, { to: 'debug' })` writes to the debug log; without the second argument the line goes to the transcript.
- **Live evidence:** capture with `--debug-file <path>` and grep for `hooks module <name>@inline loaded`, `<name>: <event> hook skipped` and, for a `tool.check` guard, `tool.check settled in` (observed on 2.1.308, not in the docs). Do not prove behavior by scraping the terminal: the UI draws with escape sequences, and a pattern in your own prompt matches its echo. A person's answer to a dialog comes only from a person.
