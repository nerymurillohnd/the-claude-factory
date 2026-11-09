# Troubleshoot a mod

> How to find out why a Claude Code mod does nothing: match the symptom or message to its cause, look up refusal messages, and read the debug log.

## Contents

- [Find out why a mod does nothing](#find-out-why-a-mod-does-nothing)
- [Check whether mods can load](#check-whether-mods-can-load)
- [The mod doesn't load](#the-mod-doesnt-load)
  - [Your version is too old](#your-version-is-too-old)
  - [The `mods active` line doesn't name the mod](#the-mods-active-line-doesnt-name-the-mod)
  - [A `claude -p` run prints `hooks module not loaded`](#a-claude--p-run-prints-hooks-module-not-loaded)
  - [Refusal messages](#refusal-messages)
  - [Messages from the built-in guard](#messages-from-the-built-in-guard)
  - [`validate` passes and lists no `hooks` line](#validate-passes-and-lists-no-hooks-line)
  - [`hooks module did not load`](#hooks-module-did-not-load)
  - [`options do not fit plugin.json userConfig`](#options-do-not-fit-pluginjson-userconfig)
  - [`code nested too deep to scan: more than 2000 scopes`](#code-nested-too-deep-to-scan-more-than-2000-scopes)
  - [`the engine ran out of stack linking the file and its imports`](#the-engine-ran-out-of-stack-linking-the-file-and-its-imports)
  - [`the parser stopped` or `the engine ran out of stack loading the file`](#the-parser-stopped-or-the-engine-ran-out-of-stack-loading-the-file)
  - [No mod loads in a directory you opened for the first time](#no-mod-loads-in-a-directory-you-opened-for-the-first-time)
  - [No installed plugin loads at all](#no-installed-plugin-loads-at-all)
  - [Claude Code stops asking to enable hot reloading](#claude-code-stops-asking-to-enable-hot-reloading)
- [A hook is skipped or a mod is unloaded](#a-hook-is-skipped-or-a-mod-is-unloaded)
  - [`hook skipped`](#hook-skipped)
  - [`no command.run hook answered it`](#no-commandrun-hook-answered-it)
  - [`it crashed the hooks worker`](#it-crashed-the-hooks-worker)
  - [`its session.start ran again in a fresh copy`](#its-sessionstart-ran-again-in-a-fresh-copy)
  - [`This mod's change didn't load` or `the earlier version is no longer running`](#this-mods-change-didnt-load-or-the-earlier-version-is-no-longer-running)
  - [`$.agent.register refused: the hooks module that made the call is no longer loaded`](#agentregister-refused-the-hooks-module-that-made-the-call-is-no-longer-loaded)
  - [`mods that run in the hooks worker are off for this session`](#mods-that-run-in-the-hooks-worker-are-off-for-this-session)
- [A tool call is denied](#a-tool-call-is-denied)
  - [`a hook changed this call's input after the model wrote it`](#a-hook-changed-this-calls-input-after-the-model-wrote-it)
  - [A message about the deny rules in your settings](#a-message-about-the-deny-rules-in-your-settings)
- [A toast appears after a turn is stopped](#a-toast-appears-after-a-turn-is-stopped)
  - [`Stopped: type a message to continue; a mod cannot resume work after Stop`](#stopped-type-a-message-to-continue-a-mod-cannot-resume-work-after-stop)
- [A drawing doesn't appear or respond](#a-drawing-doesnt-appear-or-respond)
  - [Another mod's band shows and yours doesn't](#another-mods-band-shows-and-yours-doesnt)
  - [A pane or band is empty or shows Claude Code's usual content](#a-pane-or-band-is-empty-or-shows-claude-codes-usual-content)
  - [A `ui.render` line says `refused`](#a-uirender-line-says-refused)
  - [`needs a key`, `is drawn twice`, or `key each once`](#needs-a-key-is-drawn-twice-or-key-each-once)
  - [A `ui.render` line says `threw while drawn`](#a-uirender-line-says-threw-while-drawn)
  - [`the module failed without a message`](#the-module-failed-without-a-message)
  - [`$.ui.open` runs and no pane appears](#uiopen-runs-and-no-pane-appears)
  - [A toast doesn't appear](#a-toast-doesnt-appear)
  - [The band shows `plugin panel hidden`](#the-band-shows-plugin-panel-hidden)
  - [Hotkeys do nothing](#hotkeys-do-nothing)
  - [A drawing works in the terminal and not in the Desktop app or VS Code](#a-drawing-works-in-the-terminal-and-not-in-the-desktop-app-or-vs-code)
- [An edit or a value is lost](#an-edit-or-a-value-is-lost)
  - [Your edits don't take effect](#your-edits-dont-take-effect)
  - [A value resets when the module reloads](#a-value-resets-when-the-module-reloads)
  - [A value resets after `/clear`, `/resume`, or `/branch`](#a-value-resets-after-clear-resume-or-branch)
  - [A key your `settings.read` hook returns doesn't take effect](#a-key-your-settingsread-hook-returns-doesnt-take-effect)
  - [`the answer for <key> is no value the key can hold`](#the-answer-for-key-is-no-value-the-key-can-hold)
  - [`settings.read: refused to the engine`](#settingsread-refused-to-the-engine)
- [Read the debug log](#read-the-debug-log)
- [Documentation References](#documentation-references)

When a mod's module or one of its hooks fails, Claude Code skips it and the session continues, so a broken mod can look like one that does nothing. Start by checking what Claude Code read from the mod and where it reports a problem, then find the matching symptom or message below.

## Find out why a mod does nothing

When a mod does nothing, check two things: what Claude Code reads from the mod's files, and the line it writes when it skips something. For the first, in the shell run [`claude plugin validate`](https://code.claude.com/docs/en/plugins/mods/create#check-what-claude-code-reads-from-your-mod) with the mod's directory, as in `claude plugin validate ./first-mod`. It catches a misspelled event, a bad manifest, and a module Claude Code cannot read, without starting a session.

When a module does not load, a hook is skipped, or another mod refuses the mod, Claude Code writes one line that names the mod. Where that line appears depends on the session:

* **A session that hot-reloads a plugin directory**: a dim line in the transcript. That is an interactive session started with `--plugin-dir`, or one where the user [enabled hot reloading](https://code.claude.com/docs/en/plugins/mods/create.md#ask-claude-for-a-mod) for mods Claude wrote.
* **Any other interactive session, such as one that runs a mod installed from a marketplace**: the [debug log](#read-the-debug-log) only. To get one, start the session with `claude --debug`.
* **A `claude -p` run with `--plugin-dir`**: stderr, in the default text output format. A refusal by another mod goes to the debug log only.

## Check whether mods can load

To check whether the setup lets mods load at all, without installing one, run `claude plugin test` in the shell from a directory that does not hold a mod. No session is needed. The message it prints gives the state:

| Message includes | What it means |
| :- | :- |
| `no hooks module to load` | Mods can load. The command found no mod to test in this directory. |
| `hooks modules are turned off here` | A setting is blocking your mods: `disableAllHooks` in your own settings, or your organization's policy |
| `hooks modules are turned off in this process: the rollout switch served off` | Anthropic has turned installed mods off remotely. |
| `hooks modules are turned off in this process: the rollout switch was saved off by an earlier session` | The command used a value an earlier session saved, which may be out of date. Start `claude` once to refresh it, then run the command again. |

An organization can also set `allowManagedModsOnly` to allow only its own mods, which this command does not report. In that case Claude Code refuses a mod the user installs, and [a message says why](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md#messages-from-the-built-in-guard).

## The mod doesn't load

Symptom: nothing the mod adds appears: no command, no drawing, and no change in behavior.

### Your version is too old

See [which version to use and how to check it](https://code.claude.com/docs/en/plugins/mods/overview.md#turn-mods-on-or-off).

### The `mods active` line doesn't name the mod

Symptom: nothing the mod adds appears, and the [`mods active` line](https://code.claude.com/docs/en/plugins/mods/overview#see-which-mods-a-session-loaded) in `/plugin` does not name it. Cause: the hooks module did not load. When Claude Code refused it, the debug log has a line that starts with `hooks module`, the mod's name, and `not loaded:`, as in `hooks module first-mod@inline not loaded: disableAllHooks in managed settings` for a mod loaded with `--plugin-dir`.

Read the reason after the colon. The [refusal messages](#refusal-messages) section lists each one. If the log has no such line, work through the other entries in this group.

Some settings stop a mod and leave the rest of its plugin working. [Turn mods on or off](https://code.claude.com/docs/en/plugins/mods/overview.md#turn-mods-on-or-off) names them.

### A `claude -p` run prints `hooks module not loaded`

The line starts with the mod's name and goes to stderr. Cause: the hooks module was refused. A non-interactive run has no transcript, so the message goes to stderr.

Read the reason after the colon. The [refusal messages](#refusal-messages) section lists each one.

### Refusal messages

Each of these follows `hooks module`, the mod's name, and `not loaded:` in the debug log.

| Message starts with | What it means |
| :- | :- |
| `hooks modules are turned off for installed plugins in this process: the rollout switch served off` | Anthropic has turned installed mods off remotely. |
| `hooks modules are turned off for installed plugins in this process: the rollout switch was saved off by an earlier session` | The session used a value an earlier session saved, which may be out of date. Start Claude Code again to refresh it. |
| `disableAllHooks in managed settings` | Your organization turned off hooks from installed plugins |
| `only managed plugins and built-in plugins run` | `allowManagedHooksOnly` is set, or `disableAllHooks` is set in a settings file other than managed settings |
| `installed plugins that are not managed load no hooks module in this mode (--bare)` | You started Claude Code with `--bare` |
| `another plugin of that name loads first` | Another enabled plugin has the same name as your mod and [holds the name](https://code.claude.com/docs/en/plugins/loading.md#hooks-when-two-enabled-plugins-share-a-name), so your hooks module doesn't load |

### Messages from the built-in guard

On a machine with managed settings, or in a session whose credential is a Team or Enterprise `/login`, the [built-in guard](https://code.claude.com/docs/en/plugins/mods/admin.md#know-what-happens-by-default) can refuse a mod or one of its answers. Each message names the option the organization's administrator sets to change the rule.

| Message contains | What it means | Where it appears |
| :- | :- | :- |
| `mods are limited to your organization's by policy (allowManagedModsOnly)` | Your organization allows only [its own mods](https://code.claude.com/docs/en/plugins/mods/admin.md#install-your-organizations-mods), so yours was refused | The debug log, and the transcript in a [session that hot-reloads a plugin directory](#find-out-why-a-mod-does-nothing) |
| `tried to lift a deny rule in your settings` | Your mod's [`tool.check`](https://code.claude.com/docs/en/plugins/mods/reference#tools) hook approved a call that a `deny` rule refuses. The call stays denied. | The transcript and the debug log, once for each mod in a session. In a `claude -p` run, the debug log only. |
| `the deny rules in your settings could not be checked for this call, so it is refused` | The guard failed while checking a call that a mod approved, so it refused the call | The reason Claude reads for the denied call |

### `validate` passes and lists no `hooks` line

Cause: `hooks/hooks.json` has no `modules` key, or the key is misspelled.

Fix: add `"modules": ["./register.js"]`.

### `hooks module did not load`

The line starts with the mod's name, then `hooks module did not load:` and a reason, which gives the file and line when the problem is in the mod's code. Cause: Claude Code could not load the module, for example because its top-level code threw.

Fix the error the reason names.

If the reason ends with `; the version loaded before is unloaded`, no version of the mod is running now. Once the error is fixed, run [`/reload-plugins`](https://code.claude.com/docs/en/plugins/cli-reference#reload-plugins) in the session to load the mod again. When the user installed the mod and did not write it, the user has to ask its author to fix the error.

### `options do not fit plugin.json userConfig`

The line starts with the mod's name, then `hooks module did not load: options do not fit plugin.json userConfig:` and a reason. Cause: an option fails validation against its [`userConfig`](https://code.claude.com/docs/en/plugins/components#user-configuration) field, such as a number above the field's `max`, or a required field has no value.

Fix: set or change the value. The end of the line names its `pluginConfigs` entry in `settings.json`.

### `code nested too deep to scan: more than 2000 scopes`

The line starts with the mod's name, then `hooks module did not load:`, the file, and `code nested too deep to scan: more than 2000 scopes`. Cause: a file in a hooks module cannot nest scopes, such as functions, blocks, and loops, more than [2,000 deep](https://code.claude.com/docs/en/plugins/mods/reference.md#limits). [`claude plugin validate`](https://code.claude.com/docs/en/plugins/mods/create#check-what-claude-code-reads-from-your-mod) reports the same reason.

Fix: rewrite the code so its scopes nest less deeply.

### `the engine ran out of stack linking the file and its imports`

Cause: code in the hooks module is nested too deeply, or its chain of imports is too long, for Claude Code to load it. The line starts with the mod's name and `hooks module did not load:`, then gives a file's name and this reason.

Fix: in that file and the files its imports reach, find the most deeply nested code and rewrite it to nest less, or shorten the chain of imports. When the user did not write the mod, the user has to ask its author to fix it.

### `the parser stopped` or `the engine ran out of stack loading the file`

Cause: code in one file of the hooks module is nested so deeply that Claude Code ran out of stack reading it. The line starts with the mod's name and `hooks module did not load:`, then gives that file's name and one of these reasons:

* `code nested too deep to scan (the parser stopped: <message>)`
* `the engine ran out of stack loading the file (code nested too deep): <message>`

The reason gives no line number and does not say what kind of code is nested, so look through the file for its most deeply nested part and rewrite that part to nest less. When the user installed the mod and did not write it, the user has to ask its author to do this.

### No mod loads in a directory you opened for the first time

Cause: the trust prompt for the directory has not been answered.

Fix: start an interactive session in that directory with `claude`, and accept the trust prompt it opens with.

### No installed plugin loads at all

Cause: Claude Code was started with `--safe-mode`.

Fix: start without the flag.

### Claude Code stops asking to enable hot reloading

Symptom: Claude writes a mod in an interactive session, nothing loads, and Claude Code does not ask again [whether to enable hot reloading](https://code.claude.com/docs/en/plugins/mods/create.md#ask-claude-for-a-mod). Cause: if the question ends three times without an answer picked, hot reloading stays off. For example, the question ends that way when [`askUserQuestionTimeout`](https://code.claude.com/docs/en/settings-reference#askuserquestiontimeout) is set and the time passes before the user answers. That setting applies here because Claude Code asks in the same [question dialog that `AskUserQuestion` uses](https://code.claude.com/docs/en/tools-reference#question-auto-continue-timeout). A question the user dismisses does not count toward the three.

Fix: to run the mod, [copy its directory out of the mods folder](https://code.claude.com/docs/en/plugins/mods/create.md#use-the-mod-in-other-sessions), then in the shell start a new session with `--plugin-dir`, as in `claude --plugin-dir ~/mods/git-branch`.

## A hook is skipped or a mod is unloaded

Symptom: the mod loaded, and then Claude Code skipped one of its hooks or unloaded it.

### `hook skipped`

The line names the mod and the event, then says `hook skipped:` and a reason, as in `first-mod: tool.call hook skipped: threw Error: boom`. Cause: a hook threw, exceeded its [time limit](https://code.claude.com/docs/en/plugins/mods/reference.md#limits), or returned a result of the wrong shape. The line appears once for each event and kind of failure until the mod reloads.

Fix the error. The debug log has a line for every occurrence.

### `no command.run hook answered it`

Symptom: running a command the mod added gives a reply that names the mod and the command, as in `first-mod registered /tally but no command.run hook answered it`, then says to add a hook. Claude Code prints that reply when the command reaches the end of the chain with no answer, which happens in two cases:

* **No hook answered the command**: the module has no `command.run` hook, the hook's [filter](https://code.claude.com/docs/en/plugins/mods/events.md#filter-which-events-a-hook-handles) names a different command, or the hook returned `next(e)`
* **Claude Code skipped the hook**: [`hook skipped`](#hook-skipped) lists the reasons. Passing `focus: false` to [`$.ui.open`](https://code.claude.com/docs/en/plugins/mods/interface#open-a-pane-at-the-right-time) is one way to get there.

If the module already has the hook the reply describes, look for a `hook skipped` line that names `command.run`, which gives the reason. A [test](https://code.claude.com/docs/en/plugins/mods/test.md) that runs the command fails with the same reason.

### `it crashed the hooks worker`

The line starts with the mod's name, as in `first-mod was unloaded: it crashed the hooks worker`. Cause: installed mods share one worker thread. The worker stopped responding or crashed, and Claude Code traced that to this mod and unloaded it. A hook that blocks the thread, such as a loop that never awaits, is one cause.

Fix the hook.

### `its session.start ran again in a fresh copy`

The line starts with the mod's name and names a `$.prompt.submit`, `$.command.run`, or `$.agent.spawn` call, as in `first-mod: its session.start ran again in a fresh copy; the $.prompt.submit call it had already made was not made again`. Claude Code loaded the mod's module again, for example after the hooks worker crashed and was replaced, and the fresh copy's [`session.start`](https://code.claude.com/docs/en/plugins/mods/reference#session) hook ran. The call the line names resolved with the result of its first run instead of running again, so the mod does not submit the prompt, run the command, or start the subagent twice. The rest of the hook ran as usual.

There is nothing to fix.

Before v2.1.292, the call ran a second time, so the prompt was submitted, the command run, or the subagent started twice.

### `This mod's change didn't load` or `the earlier version is no longer running`

Cause: a change to a [mod Claude wrote in this session](https://code.claude.com/docs/en/plugins/mods/create.md#ask-claude-for-a-mod) could not load. The transcript line starts with the mod's name and ends with the reason:

* `This mod's change didn't load, so the earlier version is still running: <reason>.`
* `This mod didn't load, and the earlier version is no longer running: <reason>.`

Claude does not see this line, so the user has to paste it into the next message when asking Claude for a fix.

### `$.agent.register refused: the hooks module that made the call is no longer loaded`

The line starts with the mod's name, as in `first-mod: $.agent.register refused: the hooks module that made the call is no longer loaded (it was reloaded or removed)`, and the agent is not registered. Cause: the mod was reloaded or unloaded before the call. A reload loads a fresh copy of the hooks module, and this call came from code still running in the old copy, such as a hook that had not returned yet.

If that hook does not catch the rejection, it fails and Claude Code [skips it](#hook-skipped). To register the agent from the copy that stays loaded, make the call in the mod's [`session.start`](https://code.claude.com/docs/en/plugins/mods/reference#session) hook, which runs again in each fresh copy after a reload.

### `mods that run in the hooks worker are off for this session`

The line reads `hooks: mods that run in the hooks worker are off for this session: it crashed 3 times`. Cause: the worker stopped three times and Claude Code could not trace the stops to one mod, so it unloaded every mod that is not built in, including mods the organization installs. This line reaches the transcript in every interactive session.

Fix: run `/reload-plugins` to load them again.

## A tool call is denied

Symptom: the mod loaded and its hooks run, and a tool call it touched is refused.

### `a hook changed this call's input after the model wrote it`

In auto mode, a denied tool call gives this reason. Cause: a hook changed the tool call's input after the [server-side classifier](https://code.claude.com/docs/en/permission-modes.md#server-side-classifier-review) reviewed it, so that review does not cover what would run. The hook can be a mod's [`tool.call`](https://code.claude.com/docs/en/plugins/mods/reference#tools) or [`turn.step`](https://code.claude.com/docs/en/plugins/mods/reference#turns) hook, or a [`PreToolUse`](https://code.claude.com/docs/en/hooks#pretooluse) settings hook. The message does not say which.

The message tells Claude to issue the call once more as recorded. If that call is denied too, the hook changes the input every time: turn off the mod or hook, or leave auto mode and have the user approve the call.

> [!NOTE]
>
> In [some interactive terminal sessions and VS Code sessions](https://code.claude.com/docs/en/hooks.md#pretooluse-updatedinput-in-auto-mode), the same denial gives the reason `a hook changed this call's input after auto mode reviewed it`. The repeated call there carries the mod's first change, and a `tool.call` hook still runs on it, but a further change is dropped. The mod needs no change unless Claude's reply says that [auto mode couldn't check the call](https://code.claude.com/docs/en/errors.md#hook-changed-input-after-review).

### A message about the deny rules in your settings

`tried to lift a deny rule in your settings` and `the deny rules in your settings could not be checked for this call, so it is refused` both come from the built-in guard.

Look them up in [Messages from the built-in guard](#messages-from-the-built-in-guard).

## A toast appears after a turn is stopped

### `Stopped: type a message to continue; a mod cannot resume work after Stop`

This toast means that after the user stopped the turn, for example with Esc, a mod tried to start work on its own and Claude Code did not let it. Nothing needs fixing. After the user's next message, mods can start work again and [some of that work comes back](https://code.claude.com/docs/en/plugins/mods/api.md#work-your-mod-started-before-the-interruption) on its own. If what was expected from the mod does not come back, ask for it again or run the mod's command again.

For the mod's author, see [Calls and background work after the user interrupts a turn](https://code.claude.com/docs/en/plugins/mods/api.md#calls-and-background-work-after-the-user-interrupts-a-turn).

## A drawing doesn't appear or respond

Symptom: the mod loaded, and its pane, band, toast, or controls do not behave as expected.

### Another mod's band shows and yours doesn't

There is one band above the prompt, and every mod shares it. Cause: a mod that runs [before this one](https://code.claude.com/docs/en/plugins/mods/events.md#the-order-mods-run-in) replaces the band when it returns a tree without the result of `next(e)` in it. To show both bands, change that mod's hook, or ask its author to:

* **Keep the bands after it**: put the result of `await next(e)` among the children of a `Box` in its tree, as in the Band above the prompt tab of [Pick where to draw](https://code.claude.com/docs/en/plugins/mods/interface.md#pick-where-to-draw)
* **Keep the tree valid**: do not give that `Box`, or any `Box` around it, a `width`, `height`, `minWidth`, `minHeight`, `position`, `top`, `left`, `right`, `bottom`, `display`, or `overflow` prop

To find that mod, [write a debug log](#read-the-debug-log) and search it for `answered ui.render without next()`. A line such as `other-mod (user) answered ui.render without next()` names a mod that returned its tree without calling `next(e)`. It does not name the [render site](https://code.claude.com/docs/en/plugins/mods/reference.md#render-sites), so a pane-only mod can appear too. A mod that calls `next(e)` and drops the result gets no line, so check the hooks that run before this mod's hook too.

A mod's band is also missing when the tree its own hook returned does not validate, and the other mods' bands stay. To find which mod and why, [write a debug log](#read-the-debug-log) and search it for [`ui.render hook skipped`](#a-pane-or-band-is-empty-or-shows-claude-codes-usual-content).

### A pane or band is empty or shows Claude Code's usual content

Cause: the [tree](https://code.claude.com/docs/en/plugins/mods/interface.md#build-a-tree-from-elements) the hook returned did not validate. A [`hook skipped`](#hook-skipped) line [in the transcript or the debug log](#find-out-why-a-mod-does-nothing) names the mod and the reason, as in this one for a `Box` in a pane:

```text theme={null}
first-mod: ui.render hook skipped: returned the wrong shape (a tree Pane refuses: Box prop "flexDirection" must be one of row, column, row-reverse, column-reverse)
```

Fix what the reason names. If the reason is cut short, [write a debug log](#read-the-debug-log) and search it for `a hook returned a tree that does not validate` to read the rest.

If the line instead says `refused:` right after the site's name, as in `ui.render (Pane) refused:`, see [A `ui.render` line says `refused`](#a-uirender-line-says-refused).

### A `ui.render` line says `refused`

`ui.render (<site>) refused:`, or `ui.render (<site>): the chain settled on a tree that does not validate` in the [debug log](#read-the-debug-log), means the [tree](https://code.claude.com/docs/en/plugins/mods/interface.md#build-a-tree-from-elements) at that site exceeds a [size limit](https://code.claude.com/docs/en/plugins/mods/reference.md#limits). Either line names the [render site](https://code.claude.com/docs/en/plugins/mods/reference.md#render-sites) and then the reason, and the reason names the limit.

Fix: change the mods that draw at that site so their [`ui.render`](https://code.claude.com/docs/en/plugins/mods/reference#interface) hooks return smaller trees, or ask their authors to. If the transcript line starts with `hooks`, more than one loaded mod has a `ui.render` hook for that site, so check each of those mods' trees. When several mods' bands above the prompt nest into a tree more than 32 levels deep, the line reads:

```text theme={null}
hooks: ui.render (AbovePrompt) refused: deeper than 32; nothing was drawn
```

Before v2.1.307, a `refused:` line for any site reported any tree that did not validate, and for `Pane` and `AbovePrompt` it ended `; the engine drew its own`. On those releases, fix what the reason names.

### `needs a key`, `is drawn twice`, or `key each once`

Cause: an element in the tree the `ui.render` hook returns has no valid [`key`](https://code.claude.com/docs/en/plugins/mods/interface#which-controls-need-a-key), or two elements share one. Match the message:

* **`<Input> needs a key` or `<Select> needs a key`**: the element has no `key` prop, or its `key` is empty or is not a string, as in `key: 3`. Give it a non-empty string as its `key`.
* **`<Button> needs a key`**: give the button a non-empty string as its `key`
* **`is drawn twice; each takes its own key`**: two elements of the kind the message names have the same `key`, as in `Input "size" is drawn twice; each takes its own key`. Give each element its own `key`.
* **`key each once` from `press` in a [test](https://code.claude.com/docs/en/plugins/mods/test.md#test-a-drawing)**: the drawing has more than one button with the key passed to `press`. Buttons with the same label and no `key` prop share that label as their key. Give each button its own `key`.

### A `ui.render` line says `threw while drawn`

The line names the [render site](https://code.claude.com/docs/en/plugins/mods/reference.md#render-sites), then says `threw while drawn:` and the error, as in `first-mod: ui.render (ToolUse) threw while drawn: <error>; the engine drew its own`. Cause: Claude Code hit that error while drawing the tree the [`ui.render`](https://code.claude.com/docs/en/plugins/mods/reference#interface) hook returned, or while drawing the site from the [`props` the hook passed to `next`](https://code.claude.com/docs/en/plugins/mods/interface#change-what-claude-code-already-draws). The ending `the engine drew its own` means the site shows Claude Code's usual content.

Fix: read the error and fix the value in the hook that caused it.

Before v2.1.289, this error in a transcript row ended the session with [`Claude Code exited after an unrecoverable interface error`](https://code.claude.com/docs/en/errors#exited-after-an-unrecoverable-interface-error).

### `the module failed without a message`

Cause: a [`Client`](https://code.claude.com/docs/en/plugins/mods/interface#when-a-client-fails) failed with an error that has no message, such as `throw new Error()`. The line in its place reads like `my-mod: Client client/spinner.js: the module failed without a message`.

Fix: find the throw in the `Client`'s code and give the error a message. The line then shows that message.

Before v2.1.289, the line showed `Error` as the reason instead.

### `$.ui.open` runs and no pane appears

Cause: the call did not come from something the user did, and the terminal is narrower than [the width that pane needs](https://code.claude.com/docs/en/plugins/mods/interface.md#when-a-pane-waits-for-a-wider-terminal).

Fix: open the pane from a command or a button, or check the call's `isPlaced` result. See [Open a pane at the right time](https://code.claude.com/docs/en/plugins/mods/interface.md#open-a-pane-at-the-right-time).

### A toast doesn't appear

Symptom: the mod calls [`$.ui.toast`](https://code.claude.com/docs/en/plugins/mods/api#show-something-without-starting-a-turn) in an interactive terminal session and no toast is visible. To confirm that the call ran, look in the [debug log](#read-the-debug-log) for a line with the mod's name and the toast's text, as in `$.ui.toast (first-mod): build finished`. Then check for causes such as these:

* **The line for the call is missing**: look for one that says why Claude Code refused the call, as in `first-mod: $.ui.toast dropped: timeoutMs is a whole number of ms, 1 to 60000`.
* **A pane is holding toasts**: this mod or another one passed [`holdToasts`](https://code.claude.com/docs/en/plugins/mods/interface#hold-toasts-behind-a-dialog) when it opened the pane that is showing. Close the pane to end the hold. If the pane belongs to this mod and is meant to stay open, remove `holdToasts` from its `$.ui.open` call and open the pane again.
* **The toast is under the prompt**: in the [classic renderer](https://code.claude.com/docs/en/fullscreen.md#enable-fullscreen-rendering), look at the right under the prompt. A toast there is one line that starts with the mod's name, rather than a box at the top right.
* **The mod raised a newer toast**: in the classic renderer, a newer toast from the same mod can take the place of one that is showing or waiting to show. The debug log has another line for the older toast, which ends with `gave way, cut short` when it was showing, or `gave way, unseen` when it never appeared. To show both messages, put them in one toast.
* **The toast ran out of time undrawn**: in fullscreen rendering, Claude Code draws at most three toasts at a time, so a toast can run out of time before it is drawn. The debug log has another line for that toast, which ends with `left the stack, never drawn`. When the mod raises several at once, put the messages in one toast.

Before v2.1.290, Claude Code dropped a toast raised within two seconds of the last one it showed for the mod, and the debug log line for the dropped toast said `within 2000ms of the last; dropped`.

### The band shows `plugin panel hidden`

Cause: the band is [collapsed](https://code.claude.com/docs/en/plugins/mods/interface.md#when-the-user-collapses-the-band). It collapses when the user presses Ctrl+X then Ctrl+A, or the keys bound in their place, and in [fullscreen rendering](https://code.claude.com/docs/en/fullscreen.md) when the user clicks the `[-]` on its first row. It stays collapsed until it is expanded or Claude Code starts again, and meanwhile no hotkey or `action` binding presses a button in it.

Fix: to expand the band, press the keys the row names, Ctrl+X then Ctrl+A by default, or in fullscreen rendering click the row.

### Hotkeys do nothing

Cause: the pane or band does not have keyboard focus, the button is in a collapsed band, or the drawing is in the VS Code extension, where buttons have no hotkeys. Apply the matching fix:

* **No keyboard focus**: press Ctrl+X then Tab or, in [fullscreen rendering](https://code.claude.com/docs/en/fullscreen.md), click the pane or band. To have the pane take focus when it opens, open it with `focus: true` from a command.
* **The button is in a collapsed band**: the band shows one dim row that starts with `▸ plugin panel hidden`. Press the keys the row names, Ctrl+X then Ctrl+A by default, to [expand it](#the-band-shows-plugin-panel-hidden).
* **In the VS Code extension**: click the button, or press Enter on it once it has focus

### A drawing works in the terminal and not in the Desktop app or VS Code

Cause: either that app does not draw the site or element, or the session is one where the VS Code extension draws nothing for mods. The mod's other hooks still run. Check for these causes:

* **The site or element is not drawn in that app**: look up the site in the [render sites](https://code.claude.com/docs/en/plugins/mods/reference.md#render-sites) table and the elements in the [elements](https://code.claude.com/docs/en/plugins/mods/reference.md#elements) table. For an element the app lacks, check `e.surface` in the hook and return a tree the app can draw.
* **The VS Code extension is older than 2.1.299**: the chat panel draws for mods from [extension version](https://code.claude.com/docs/en/vs-code.md#install-the-extension) 2.1.299. Check the version in VS Code's Extensions view and update the extension there.
* **The extension is older than 2.1.304 and the session does not fetch feature flags**: update the extension, or run `claude` in VS Code's integrated terminal instead. Sessions on Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry skip the fetch. For the others that skip it, such as a [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway) session, see [Features that need feature-flag fetching](https://code.claude.com/docs/en/env-vars.md#features-that-need-feature-flag-fetching).

## An edit or a value is lost

Symptom: the mod runs, and a change made to it or a value it kept is not there.

### Your edits don't take effect

Cause: the edits are being made to an installed plugin. Claude Code runs the cached copy for the installed version.

Fix: develop with `--plugin-dir` pointed at the working copy, as in `claude --plugin-dir ./first-mod`, which reloads on save.

### A value resets when the module reloads

Cause: module-level variables are re-initialized on each reload.

Fix: [keep the value in `$.state` or `$.store`](https://code.claude.com/docs/en/plugins/mods/interface#keep-state).

### A value resets after `/clear`, `/resume`, or `/branch`

Symptom: a value resets, or a saved value is replaced by its default. Cause: each of those commands resets `$.state` to its defaults, and `session.start` does not fire again.

Fix: [load the saved value again](https://code.claude.com/docs/en/plugins/mods/interface.md#load-a-saved-value-again-after-clear) in a `classic.SessionStart` hook.

### A key your `settings.read` hook returns doesn't take effect

When a hook returns permission rules or `env` on [Claude Code's own read](https://code.claude.com/docs/en/plugins/mods/events.md#settings-read-hook), the rules are not checked on tool calls and the `env` entries do not become environment variables. Use a [settings file](https://code.claude.com/docs/en/settings.md) for both, or [`$.env.set`](https://code.claude.com/docs/en/plugins/mods/api#reach-files-processes-and-the-network) for `env`.

For another key, check [which mods get `settings.read` and from which version](https://code.claude.com/docs/en/plugins/mods/events#settings-read-hook), then search the [debug log](#read-the-debug-log) for `settings.read` and look for one of these lines:

| Log line | Meaning and step |
| :- | :- |
| `settings.read hook skipped`, after your mod's name | Your hook failed. [Fix the error the line reports](#hook-skipped). |
| `settings.read bypassed by cc-plugin-sec-default`, on a line that names your mod ahead of it | The [built-in guard](https://code.claude.com/docs/en/plugins/mods/admin.md#know-what-happens-by-default) skipped your hook. Ask your organization's administrator to [install the mod as one of the organization's mods](https://code.claude.com/docs/en/plugins/mods/admin.md#install-your-organizations-mods). |
| `settings.read: the answer for <key> is no value the key can hold` | Claude Code refused the value a hook returned for that key. The hook may be yours or another mod's. Follow [the step for your case](#the-answer-for-key-is-no-value-the-key-can-hold). |
| `settings.read: the merge never settles for <key>` | The keys the line names keep the settings sources' values. Set them in a settings file. |
| `answered settings.read without next()`, after a mod's name | Your hook is affected if the named mod [runs before yours](https://code.claude.com/docs/en/plugins/mods/events.md#the-order-mods-run-in). Then your hook didn't run on that read. [Turn that mod off](https://code.claude.com/docs/en/plugins/mods/overview.md#turn-mods-on-or-off), or if your organization deployed it, ask its administrator to. |
| `settings.read: refused to the engine` | Your value didn't apply because Claude Code's own read was refused. [Find what refused it](#settingsread-refused-to-the-engine). |

If no line explains the key, check the mods that run before this mod for a `settings.read` hook that [changes the key](https://code.claude.com/docs/en/plugins/mods/events.md#settings-read-example). Turn that mod off, or ask the organization's administrator to. If no hook does, set the key in a settings file.

### `the answer for <key> is no value the key can hold`

This [debug log](#read-the-debug-log) line means Claude Code refused the value a [`settings.read`](https://code.claude.com/docs/en/plugins/mods/events#settings-read-hook) hook returned for the named key, and for that key alone:

```text theme={null}
settings.read: the answer for <key> is no value the key can hold; the settings' own value stands
```

Cause: the value returned for the named key did not fit that key's schema, for example by type or by range.

* **The mod's value does not fit the key's schema**: return one the key's [settings reference](https://code.claude.com/docs/en/settings-reference.md) entry allows.
* **The mod's value fits**: the value that does not fit came from another mod's `settings.read` hook. To find that mod, follow [the steps to turn off mods one at a time](#settingsread-refused-to-the-engine), and search each new log for this line instead of `refused to the engine`.

While the value does not fit, the key keeps the value merged from the settings sources before any hook answered. The line calls it the settings' own value.

### `settings.read: refused to the engine`

This line appears in the [debug log](#read-the-debug-log) when [Claude Code's own read](https://code.claude.com/docs/en/plugins/mods/events.md#settings-read-hook) is refused, and Claude Code drops every hook's value. When a `settings.read` hook refuses that read with [`{ deny: reason }`](https://code.claude.com/docs/en/plugins/mods/events#settings-read-returns), the line carries that hook's reason:

```text theme={null}
settings.read: refused to the engine (engine: $.settings.read: <reason>); the settings' own values stand
```

Search the mod's code for the reason in the parentheses:

* **The mod's code has it**: the mod's hook refused the read. Make it return `{ value }` when [`next.origin`](https://code.claude.com/docs/en/plugins/mods/events#settings-read-origin) shows Claude Code's own read.
* **The mod's code does not have it**: [turn off](https://code.claude.com/docs/en/plugins/mods/overview.md#turn-mods-on-or-off) the other mods one at a time. When the organization deployed a mod, ask its administrator to turn it off. After each:
  1. Start the session from the shell with `claude --debug-file ./settings-read-2.log`, followed by the flags it started with. Use a new path each time.
  2. Search that file for `refused to the engine`. If the line is there, turn off the next mod. If not, the last mod turned off refused the read, so keep it off.

If the line stays with no other mod left, set the keys the hook returns in a [settings file](https://code.claude.com/docs/en/settings.md). Its values hold while the read is refused.

## Read the debug log

The debug log has a line for every module Claude Code loads or refuses, every hook that fails, and every result it refuses, so it is where to look when the transcript shows nothing. To write one, in the shell start Claude Code with `--debug`, or with `--debug-file <path>` to choose where it goes:

```bash theme={null}
claude --debug-file ./mod-debug.log --plugin-dir ./first-mod
```

In another terminal, follow the file and filter for the mod's name:

```bash theme={null}
tail -f ./mod-debug.log | grep first-mod
```

A mod that loaded has a line that names it and lists the events it handles. A mod loaded with `--plugin-dir` appears under its name followed by `@inline`:

```text theme={null}
hooks module first-mod@inline loaded (worker, environment 2, tier user); events: session.start,tool.call,command.run,ui.render
```

To write custom lines in the log, call [`$.ui.log`](https://code.claude.com/docs/en/plugins/mods/api#show-something-without-starting-a-turn) with a second argument, as in `$.ui.log('message', { to: 'debug' })`. Without the second argument, `$.ui.log` adds a dim line to the transcript.

While a mod loaded with `--plugin-dir` is being edited, the transcript shows a line for each reload that names the mod and lists its hooks. If a save breaks the module, the line says `reload failed, the previous version stays loaded:` with the reason, and the last working version keeps running until Claude Code next reloads plugins, such as when `/reload-plugins` runs.

## Documentation References

- Source page: <https://code.claude.com/docs/en/plugins/mods/troubleshoot>
- <https://code.claude.com/docs/en/plugins/mods/create.md>: checking what Claude Code reads from a mod with `claude plugin validate`, asking Claude for a mod, hot reloading, using a mod in other sessions
- <https://code.claude.com/docs/en/plugins/mods/overview.md>: required versions, turning mods on or off, the `mods active` line in `/plugin`
- <https://code.claude.com/docs/en/plugins/loading.md>: what happens when two enabled plugins share a name
- <https://code.claude.com/docs/en/plugins/mods/admin.md>: the built-in guard and installing an organization's mods
- <https://code.claude.com/docs/en/plugins/mods/reference.md>: events (`tool.check`, `session.start`, `turn.step`, `ui.render`), limits, render sites and elements tables
- <https://code.claude.com/docs/en/plugins/cli-reference>: `/reload-plugins`
- <https://code.claude.com/docs/en/plugins/components>: `userConfig` fields
- <https://code.claude.com/docs/en/settings-reference.md>: `askUserQuestionTimeout` and the schema each settings key allows
- <https://code.claude.com/docs/en/tools-reference>: the question dialog's auto-continue timeout
- <https://code.claude.com/docs/en/plugins/mods/events.md>: hook filters, the order mods run in, the `settings.read` hook, what it can return, and `next.origin`
- <https://code.claude.com/docs/en/plugins/mods/interface.md>: opening panes, keys, element trees, `Client` failures, holding toasts, collapsing the band, keeping state, loading a saved value after `/clear`
- <https://code.claude.com/docs/en/plugins/mods/test.md>: tests that catch problems before they reach a session
- <https://code.claude.com/docs/en/permission-modes.md>: the auto mode server-side classifier
- <https://code.claude.com/docs/en/hooks.md>: the `PreToolUse` settings hook and its `updatedInput` in auto mode
- <https://code.claude.com/docs/en/errors.md>: the error when auto mode could not check a changed call, and the unrecoverable interface error exit
- <https://code.claude.com/docs/en/plugins/mods/api.md>: `$.ui.toast`, `$.ui.log`, `$.env.set`, work started before an interruption, calls after the user interrupts a turn
- <https://code.claude.com/docs/en/fullscreen.md>: classic and fullscreen rendering
- <https://code.claude.com/docs/en/vs-code.md>: installing the VS Code extension
- <https://code.claude.com/docs/en/claude-apps-gateway>: Claude apps gateway sessions
- <https://code.claude.com/docs/en/env-vars.md>: features that need feature-flag fetching
- <https://code.claude.com/docs/en/settings.md>: settings files
- <https://code.claude.com/docs/en/plugins/troubleshooting.md>: problems installing and loading a plugin that are not specific to mods
