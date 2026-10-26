# Troubleshooting a mod

Source: https://code.claude.com/docs/en/plugins/mods/troubleshoot, plus CHANGELOG items in `version-drift.md`. Scope here is mods installed from a public GitHub marketplace or loaded from a clone with `--plugin-dir`.

## Step 0: where does Claude Code report problems?

When a module does not load, a hook is skipped, or another mod refuses yours, Claude Code writes **one line naming the mod**. Where you read it depends on the session:

| Session | Where the line is |
| :- | :- |
| Interactive, started with `--plugin-dir` (or hot-reload enabled for mods Claude wrote) | dim line in the transcript |
| Any other interactive session, **including a mod installed from a marketplace** | debug log only: start with `claude --debug` or `claude --debug-file <path>` |
| `claude -p` with `--plugin-dir` | stderr (default text output). A refusal by *another* mod goes to the debug log only |

Then, in order:
1. `claude plugin validate --strict <clone>` (static: misspelled event, bad manifest, unreadable module).
2. `claude plugin test <clone>` (behavior; see `testing.md`).
3. Debug log: `claude --debug-file ./mod-debug.log --plugin-dir <clone>`; `grep <mod-name> ./mod-debug.log`. A loaded mod has a line like `hooks module first-mod@inline loaded (worker, environment 2, tier user); events: ...` (`@inline` for `--plugin-dir`; installed mods show their marketplace). **Unverified in `claude -p`**: in testing with 2.1.310 this line did not appear in `-p` debug logs; confirm in an interactive session.
4. Each `--plugin-dir` hot reload prints a transcript line naming the mod and its hooks; a broken save prints `reload failed, the previous version stays loaded: <reason>`.

## Can mods load here at all?

Run `claude plugin test` from a directory that holds **no** mod:

| Output includes | Meaning |
| :- | :- |
| `no hooks module to load` | mods can load |
| `hooks modules are turned off here` | `disableAllHooks` in your settings or org policy |
| `hooks modules are turned off in this process: the rollout switch served off` | Anthropic switched installed mods off remotely |
| `... the rollout switch was saved off by an earlier session` | stale saved value; start `claude` once to refresh, rerun |

`allowManagedModsOnly` (org setting) is not reported by this check; it shows as a refusal when a mod is installed (guard table below).

## Nothing the mod adds appears

- **Version too old**: mods need Claude Code ≥ 2.1.287.
- **`mods active` line in `/plugin` does not name the mod** → module not loaded. Look for `hooks module <name> not loaded: <reason>` in the debug log, e.g. `hooks module first-mod@inline not loaded: disableAllHooks in managed settings`.
- **`claude -p` prints `hooks module not loaded`** on stderr: same reasons.
- **`validate` lists no `hooks` line for the module, or fails**: `hooks/hooks.json` has no `modules` key or it is misspelled. Docs: validate passes with no `hooks` line. **[obs 2.1.310]** when the file has neither `hooks` nor `modules` (e.g. only a misspelled `module`), validate fails with `hooks.json must have \`hooks\` (the hook matchers) or \`modules\` (hooks modules), or both`; either way the fix is `"modules": ["./register.js"]`. (If the plugin was never meant to have a hooks module, it is not a mod and is out of scope.)
- **No mod loads in a directory opened for the first time**: trust prompt unanswered; start interactive `claude` there and accept.
- **`--plugin-dir` refused at startup**: managed `disableSideloadFlags` rejects `--plugin-dir` and `--plugin-url` (`/en/plugins/mods/reference`, settings table).
- **The Desktop app shows nothing**: it does not show `hooks module did not load`, so a mod its bundled CLI refuses fails silently there (anthropics/claude-code#102841, open). Reproduce in the terminal with `claude --debug-file <path>`.
- **No installed plugin loads at all**: started with `--safe-mode`.
- **Hot-reload question stopped appearing** (mods Claude wrote): ended three times unanswered (e.g. `askUserQuestionTimeout`); copy the mod out of the mods folder and use `--plugin-dir`.

### Refusal messages (after `hooks module <name> not loaded:`)

| Starts with | Meaning |
| :- | :- |
| `hooks modules are turned off for installed plugins in this process: the rollout switch served off` | remote kill switch for installed mods |
| `... the rollout switch was saved off by an earlier session` | stale value; restart Claude Code |
| `disableAllHooks in managed settings` | organization disabled hooks from installed plugins |
| `only managed plugins and built-in plugins run` | `allowManagedHooksOnly`, or `disableAllHooks` in a non-managed settings file |
| `installed plugins that are not managed load no hooks module in this mode (--bare)` | started with `--bare` |
| `another plugin of that name loads first` | another enabled plugin with the same name holds the hooks-module name (only one same-named plugin's module loads; /plugin Errors tab notes this from v2.1.296) |

### Built-in guard (`cc-plugin-sec-default`) on managed machines or Team/Enterprise logins

| Message contains | Meaning | Where |
| :- | :- | :- |
| `mods are limited to your organization's by policy (allowManagedModsOnly)` | only the org's own mods allowed; yours refused | debug log; transcript in hot-reload sessions |
| `tried to lift a deny rule in your settings` | `tool.check` hook approved a call a `deny` rule refuses; call stays denied | transcript + debug log once per mod; `-p`: debug log only |
| `the deny rules in your settings could not be checked for this call, so it is refused` | guard failed while checking an approved call | reason Claude reads for the denied call |

Remedy for org refusals is the administrator's (install as an org mod); a marketplace mod cannot be fixed from its side.

On Team organizations the guard has been reported to pass over user-tier `classic.Stop`, `classic.StopFailure` and `classic.SessionStart` hooks, silently for `Stop` (anthropics/claude-code#104236, open), and to keep user-tier `prompt.attachment` hooks from running since 2.1.299 (anthropics/claude-code#102653, open). A user on a Team login who reports such a hook doing nothing may be hitting these.

### Load errors (line starts with the mod name, then `hooks module did not load:`)

- **Generic reason with file/line**: top-level code threw; fix the named error. If the reason ends `; the version loaded before is unloaded`, no version is running; after fixing, `/reload-plugins`. For a mod you did not write, tell its author.
- **`options do not fit plugin.json userConfig: ...`**: an option fails its `userConfig` field (above `max`, required missing). Set or change it; the line names the `pluginConfigs` entry in `settings.json`.
- **`code nested too deep to scan: more than 2000 scopes`**: scopes (functions/blocks/loops) nest > 2000 deep; `validate` reports it too.
- **`the engine ran out of stack linking the file and its imports`**: code nested too deeply or import chain too long; shorten.
- **`the parser stopped` / `the engine ran out of stack loading the file`**: one file nested too deeply; no line number given, search the file's deepest part.

## A hook is skipped or the mod is unloaded

- **`<mod>: <event> hook skipped: <reason>`**: the hook threw, exceeded its time limit, or returned a wrong-shaped result. Shown once per event and failure kind until reload; the debug log has every occurrence. Fix the error.
- **`<mod> registered /tally but no command.run hook answered it`**: no `command.run` hook, the filter names another command, the hook returned `next(e)`, or Claude Code skipped the hook (see `hook skipped`; `focus: false` to `$.ui.open` is one route). A `claude plugin test` that runs the command fails with the same reason.
- **`<mod> was unloaded: it crashed the hooks worker`**: installed mods share one worker thread; a blocking hook (loop that never awaits) is a cause.
- **`hooks: mods that run in the hooks worker are off for this session: it crashed 3 times`**: all non-built-in mods unloaded; run `/reload-plugins`.
- **`its session.start ran again in a fresh copy; the $.prompt.submit call it had already made was not made again`**: informational (module reloaded, e.g. worker replaced). Nothing to fix. Before 2.1.292 the call ran twice.
- **`This mod's change didn't load...` / `...the earlier version is no longer running`**: for mods Claude wrote in-session; Claude does not see the line, so paste it.
- **`$.agent.register refused: the hooks module that made the call is no longer loaded`**: call came from a pre-reload copy. Register the agent in `session.start`, which reruns in each fresh copy; an uncaught rejection makes Claude Code skip the hook.

## A tool call is denied

- **`a hook changed this call's input after the model wrote it`** (auto mode): a `tool.call`/`turn.step` mod hook or a `PreToolUse` settings hook changed the input after the classifier reviewed it. Reissuing once as recorded; if denied again the hook changes it every time, so turn the mod off, leave auto mode, or approve manually.
- Guard messages: see the guard table above.

## Toast after a stop

`Stopped: type a message to continue; a mod cannot resume work after Stop`: expected; a mod tried to start work after Esc. Nothing to fix; work may come back after the next message.

## Drawing does not appear or respond

- **Another mod's band shows, yours does not**: one band above the prompt is shared. An earlier mod that returns a tree without the result of `next(e)` replaces yours. Search the debug log for `answered ui.render without next()`. Fix is in that mod: put `await next(e)`'s result among children of a `Box` with none of `width height minWidth minHeight position top left right bottom display overflow`. If any mod's tree does not validate, nothing shows: look for `ui.render (AbovePrompt) refused:` (transcript, `--plugin-dir`) or `does not validate` (debug log).
- **Pane/band empty or shows usual content**: tree did not validate. `ui.render (Pane) refused: <reason>; the engine drew its own` (transcript with `--plugin-dir`) or `a hook returned a tree that does not validate` (debug log). Common: unsupported prop, element the app lacks.
- **`<Input> needs a key` / `<Select> needs a key` / `<Button> needs a key`**: non-empty string `key` missing (e.g. `key: 3` is invalid). **`is drawn twice; each takes its own key`**: duplicate keys. In a test, **`key each once`** from `press`: several buttons share the key; unlabeled-key buttons use their label as key.
- **`threw while drawn`**: `<mod>: ui.render (<site>) threw while drawn: <error>; the engine drew its own`. Error occurred drawing your tree or the site with your `props` passed to `next`. Before 2.1.289 this in a transcript row ended the session (`Claude Code exited after an unrecoverable interface error`).
- **`the module failed without a message`**: a `Client` threw an error with no message (`throw new Error()`). Give it a message. Before 2.1.289 the line showed `Error`.
- **`$.ui.open` runs and no pane**: call did not come from a user action and the terminal is narrower than the pane needs. Open from a command/button or check `isPlaced`.
- **Toast missing** (debug log has `$.ui.toast (<mod>): <text>` if it ran): look for a refusal line (`$.ui.toast dropped: timeoutMs is a whole number of ms, 1 to 60000`); a pane holding toasts via `holdToasts`; toast under the prompt in the classic renderer (one line starting with the mod name); a newer toast from the same mod replacing it (`gave way, cut short` / `gave way, unseen`); fullscreen draws at most three toasts (`left the stack, never drawn`). Combine messages. Before 2.1.290 toasts within 2 s of the last were dropped (`within 2000ms of the last; dropped`).
- **`▸ plugin panel hidden`**: band collapsed (Ctrl+X then Ctrl+A, or `[-]` in fullscreen); expand with the same keys/click. No hotkey presses buttons in a collapsed band.
- **Hotkeys do nothing**: no focus (Ctrl+X then Tab, or click in fullscreen; `focus: true` when opening from a command), collapsed band, or VS Code extension (no button hotkeys; click or Enter).
- **Works in terminal, not in Desktop/VS Code**: site/element not drawn in that app (check `e.surface`, return a tree the app can draw); VS Code extension < 2.1.299 draws nothing for mods; extension < 2.1.304 and the session does not fetch feature flags (Bedrock, Google Agent Platform, Foundry skip the fetch): update the extension or run `claude` in the integrated terminal. In the VS Code chat panel `prompt.edit` never fires (anthropics/claude-code#99045, open; comment of 2026-10-18 on extension 2.1.301), so a mod driven by typed edits does nothing there.

## An edit or a value is lost

- **A copy synced from claude.ai does nothing**: an installed or `--plugin-dir` copy of the same name loads instead and the synced one is reported as not loaded; synced plugins also do not load in sessions without a claude.ai sign-in (`ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`, `apiKeyHelper`), without feature-flag fetching, in bare mode, under `--safe-mode`, or with a `--setting-sources` list that leaves out `user` (`/en/plugins/loading`, "Synced plugins" and "Name conflicts").
- **Edits to an installed plugin do nothing**: Claude Code runs the cached copy for the installed version. Develop with `claude --plugin-dir <clone>` (reloads on save). For marketplace updates and cache behavior see `github-marketplace.md`.
- **Value resets when the module reloads**: module-level variables reinitialize; keep values in `$.state` or `$.store`.
- **Value resets after `/clear`, `/resume`, `/branch`**: `$.state` resets to defaults and `session.start` does not fire again; reload the saved value in a `classic.SessionStart` hook.
- **`settings.read` hook key has no effect**: returned `env` entries do not become environment variables (use `$.env.set`), and returned `allow`/`ask`/`deny` rules are not checked on tool calls (use a settings file). For other keys grep the debug log for `settings.read`:
  - `settings.read hook skipped` → your hook failed; fix as for `hook skipped`.
  - `settings.read bypassed by cc-plugin-sec-default` → guard skipped the hook; needs the org to install it as an org mod.
  - `settings.read: the answer for <key> is no value the key can hold; the settings' own value stands` → value does not fit the key's schema (type/range); return a valid one.
  - `settings.read: the merge never settles for <key>` → set the key in a settings file.
  - `answered settings.read without next()` after a mod's name → that earlier mod blocks yours.
  - `settings.read: refused to the engine (engine: $.settings.read: <reason>); the settings' own values stand` → Claude Code's own read was refused, so no hook value applied. If `<reason>` text is in your code, return `{ value }` when `next.origin` shows Claude Code's own read; otherwise bisect by turning other mods off one at a time and rerunning with a fresh `--debug-file`.
