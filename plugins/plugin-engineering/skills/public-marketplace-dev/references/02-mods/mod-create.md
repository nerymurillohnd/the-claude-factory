# Create a mod

How a Claude Code mod is made: have Claude write one from a description, or write one by hand that counts tool calls and adds a command. Covers the reload and validate loop, type definitions, tests, and sharing.

## Contents

- [Ask Claude for a mod](#ask-claude-for-a-mod)
  - [Use the mod in other sessions](#use-the-mod-in-other-sessions)
  - [Sessions where a mod Claude writes can't load](#sessions-where-a-mod-claude-writes-cant-load)
- [Write a mod yourself](#write-a-mod-yourself)
  - [How the example mod works](#how-the-example-mod-works)
- [Keep working on a mod](#keep-working-on-a-mod)
  - [Change a mod with Claude](#change-a-mod-with-claude)
  - [Get type definitions for your version](#get-type-definitions-for-your-version)
  - [Check what Claude Code reads from your mod](#check-what-claude-code-reads-from-your-mod)
  - [Test the mod](#test-the-mod)
- [Share your mod](#share-your-mod)
- [Documentation References](#documentation-references)

A mod is a Claude Code [plugin](https://code.claude.com/docs/en/plugins/overview.md) with an entry file, called the hooks module: a JavaScript or TypeScript file whose functions Claude Code calls when events happen. A mod is made in one of two ways:

* **Claude writes it**: the user [describes what they want](#ask-claude-for-a-mod) in a Claude Code session.
* **It is written by hand**: [follow the tutorial](#write-a-mod-yourself) to learn how a mod's code works. No Node.js, bundler, or build step is needed, because Claude Code loads `.js` and `.ts` files directly.

If it isn't settled whether a mod is the right tool, read the [comparison on the overview](https://code.claude.com/docs/en/plugins/mods/overview.md#compare-mods-settings-hooks-skills-and-mcp-servers) first.

> [!NOTE]
>
> Use Claude Code v2.1.287 or later. To check, run `claude --version` in the shell. To see whether mods can load, see [Check whether mods can load](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md#check-whether-mods-can-load).

## Ask Claude for a mod

When the user describes a mod in an interactive Claude Code session, Claude writes it. Claude works from a built-in [skill](https://code.claude.com/docs/en/skills.md) named `plugin-authoring`, which tells it where to write the mod, which events and methods the running version has, and how the mod gets loaded. Claude can load the skill when the user asks for a mod, or the user can load it by running `/plugin-authoring` at the Claude Code prompt.

The mod runs once the user approves it, except in [sessions where a mod Claude writes can't load](#sessions-that-skip-the-approval).

**1. Describe the mod**

The user asks for the mod in their own words, for example `make a mod that shows the current git branch above the prompt`. Claude writes the mod in a directory of its own in the session's mods folder, which is `~/.claude/dev-mods/` followed by the session's ID. A mod's full path looks like `~/.claude/dev-mods/3f2a9c1e-5b7d-4e8a-9c21-6d0f4b8a7e13/git-branch/`.

> [!NOTE]
>
> In the `default` and `acceptEdits` [permission modes](https://code.claude.com/docs/en/permission-modes.md), Claude Code asks the user to approve each of the mod's files before Claude creates it, because the mods folder is a [protected path](https://code.claude.com/docs/en/permission-modes.md#protected-paths). The user approves each file as it comes up.

**2. Approve the mod**

When Claude saves the first file, Claude Code asks whether to enable hot reloading for the session. Hot reloading runs the mods Claude writes in this session and picks up each later change. Only the user can answer; no permission mode, rule or hook answers it.

In Claude Code 2.1.304 and later, the question reads "Turn on the mods Claude writes in this session?" and offers three answers (verified in the 2.1.319 binary; the 2.1.304 changelog records the change; the official page still shows the older label "Enable for this session"):

* **How does this work?**: explains hot reloading before the user picks.
* **Turn them on**: the mods in the session's mods folder load when the turn ends, and reload at the end of each turn that changes them. The answer lasts for the session, including after it is resumed. Claude is told what loaded.
* **Not now**: nothing loads for now. The files stay where Claude wrote them, and the mods load the next time that session starts. To keep a mod from ever loading, delete its directory.

**3. Check that the mod loaded**

Run `/plugin` at the Claude Code prompt and press Tab until the **Installed** tab is selected. It lists the mod, and the mod can be turned off there.

**4. Try the mod**

Use what was asked for. For the example prompt, the current branch name appears above the prompt box. If the mod doesn't do what was wanted, the user tells Claude what to change. The mod reloads at the end of each turn that changes its files, so the change can be tried as soon as Claude finishes.

If a transcript line that starts with the mod's name says the [change didn't load](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md#this-mods-change-didnt-load), the official page says the user must paste that line into their next message when asking Claude for a fix, because Claude doesn't see the line unless it is pasted. In Claude Code 2.1.319, the built-in `plugin-authoring` skill states instead that a failed hook of a mod Claude wrote comes back to Claude as a notice at its next turn. When no such notice arrives, ask the user to paste the line.

### Use the mod in other sessions

A mod Claude wrote loads only in the session that made it, and Claude Code deletes that session's mods folder once it's older than [`cleanupPeriodDays`](https://code.claude.com/docs/en/settings-reference#cleanupperioddays). To keep the mod, copy its directory out of the mods folder to another place, such as `~/mods/git-branch`. Then choose how to load it:

* **In a session started by hand**: in the shell, run `claude --plugin-dir ~/mods/git-branch`.
* **For other people**: [add it to a marketplace](#share-your-mod) so they can install it.

### Sessions where a mod Claude writes can't load

A mod Claude writes loads only after the user approves it, in a trusted workspace where mods are allowed to run. It doesn't load in these sessions:

* **Nobody is there to approve**: the session can't show a prompt, as in a `claude -p` run or [`dontAsk` mode](https://code.claude.com/docs/en/permission-modes).
* **The workspace isn't trusted**: the user hasn't accepted the trust prompt for the directory.
* **Mods are disabled**: the session started with `--safe-mode` or `--bare`, `disableAllHooks` is set, or the organization's [managed settings block it](https://code.claude.com/docs/en/plugins/mods/admin.md#choose-how-much-to-allow).

## Write a mod yourself

This tutorial builds a mod named `first-mod` that counts the tool calls Claude makes, shows the count beside the spinner while Claude works, and adds a `/tally` command that prints it. It then reads the type declarations Claude Code writes beside the mod and runs `claude plugin validate`. Together they show the events and methods the running version offers and what Claude Code reads from the code.

This recording shows the finished mod. The spinner counts tool calls, `/tally` prints the count, and an edit to the code takes effect while the session runs:

<video autoPlay muted loop playsInline controls src="https://mintcdn.com/claude-code/dgiVO_Od1X1faduV/images/mods-first-mod-light.mp4?fit=max&auto=format&n=dgiVO_Od1X1faduV&q=85&s=eb561134afa90375777408453ba51c77" aria-label="In a Claude Code session, the prompt 'list the files here and read the README' is typed and sent. The spinner reads 'Thinking · tool calls: 1' and the count rises as Claude works. The /tally command prints 'first-mod: Claude has made 3 tool calls since this mod loaded'. A line says first-mod reloaded and lists its four hooks. On the next prompt the spinner reads 'Thinking · tools used: 1'." />

The tutorial writes three files:

```text theme={null}
first-mod/
├── .claude-plugin/
│   └── plugin.json
└── hooks/
    ├── hooks.json
    └── register.js
```

* **`plugin.json`**: the plugin's [manifest](https://code.claude.com/docs/en/plugins/manifest-reference.md)
* **`hooks.json`**: [points to the code file](https://code.claude.com/docs/en/plugins/mods/reference.md#files)
* **`register.js`**: the code, called the hooks module

**1. Create the plugin directory**

Create the two directories that hold the files:

> [tab] Bash or Zsh
>
> ```bash theme={null}
> mkdir -p first-mod/.claude-plugin first-mod/hooks
> ```

> [tab] PowerShell
>
> ```powershell theme={null}
> New-Item -ItemType Directory -Force first-mod\.claude-plugin, first-mod\hooks
> ```

**2. Write the manifest**

A mod is a plugin, and a mod needs a [manifest](https://code.claude.com/docs/en/plugins/manifest-reference.md). This mod's manifest has no special fields. Save this as `first-mod/.claude-plugin/plugin.json`:

```json first-mod/.claude-plugin/plugin.json theme={null}
{
  "name": "first-mod",
  "version": "0.1.0",
  "description": "Counts Claude's tool calls, shows the count beside the spinner, and adds a /tally command",
  "author": { "name": "Your Name" }
}
```

**3. Tell Claude Code where the code is**

When Claude Code loads a plugin, it reads the plugin's `hooks/hooks.json`. The `modules` key in that file gives the path to the code, and having that key is what makes the plugin a mod. List one path, relative to `hooks.json`. Here it points to `register.js`, written in the next step.

Save this as `first-mod/hooks/hooks.json`:

```json first-mod/hooks/hooks.json theme={null}
{
  "description": "The first-mod hooks module",
  "modules": ["./register.js"]
}
```

**4. Write the code**

This file is the mod's code, called the hooks module. When the mod loads, Claude Code calls the `register` function the file exports and passes it a function named [`on`](https://code.claude.com/docs/en/plugins/mods/reference#the-hook-function). Each call to `on` registers an event handler, called a hook, for the event it names.

Save this as `first-mod/hooks/register.js`:

```javascript first-mod/hooks/register.js theme={null}
// The count, shared by the hooks below
let calls = 0

// Claude Code calls this once when the mod loads
export function register(on) {
  // Runs when the session starts, before your first prompt
  on('session.start', async ($, e, next) => {
    // Add the /tally command
    await $.command.register({
      name: 'tally',
      description: 'Show how many tool calls Claude has made',
    })
    // Let the session start as usual
    return next(e)
  })

  // Runs each time Claude is about to use a tool
  on('tool.call', async ($, e, next) => {
    calls += 1
    // Ask Claude Code to draw the interface again, so the new count shows
    $.ui.invalidate('ui.render')
    // Let the tool run as usual
    return next(e)
  })

  // Runs when you type /tally, and only then, because of the matcher
  on('command.run', { command: 'tally' }, async () => {
    // The text to print in the transcript
    return { text: 'Claude has made ' + calls + ' tool calls since this mod loaded' }
  })

  // Runs each time Claude Code draws the spinner
  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    // Keep Claude Code's spinner, with the count added after its word
    return next({ ...e, props: { ...e.props, suffix: ' · tool calls: ' + calls + '…' } })
  })
}
```

The file keeps a count in `calls` and registers four hooks:

* **[`session.start`](https://code.claude.com/docs/en/plugins/mods/reference#session)** runs when the session starts, before the first prompt, and again each time the mod reloads. It adds the `/tally` command to Claude Code.
* **[`tool.call`](https://code.claude.com/docs/en/plugins/mods/reference#tools)** runs each time Claude is about to use a tool. It adds one to `calls` and asks Claude Code to draw the interface again.
* **[`command.run`](https://code.claude.com/docs/en/plugins/mods/reference#commands-and-configuration)** runs when the user types `/tally`. It returns the text to print.
* **[`ui.render`](https://code.claude.com/docs/en/plugins/mods/reference#interface)** runs each time Claude Code draws the spinner. It adds the count after the spinner's word.

[How the example mod works](#how-the-example-mod-works) explains the three arguments each hook takes and what each one returns.

**5. Load the mod**

Start Claude Code with the `--plugin-dir` flag, which loads a plugin directory for one session without installing it:

```bash theme={null}
claude --plugin-dir ./first-mod
```

**6. Try the mod**

Ask Claude to do something that takes a few tool calls, such as `list the files here and read the README`. While Claude works, the spinner's word is followed by a count that rises, as in `Thinking · tool calls: 2…`. When Claude finishes, type `/tally` and press Enter. The transcript shows `first-mod: Claude has made 2 tool calls since this mod loaded`, with the actual count. Claude Code puts the plugin's name in front of the command's text.

To check the command without an interactive session, run it in non-interactive mode:

```bash theme={null}
claude -p "/tally" --plugin-dir ./first-mod
```

```text theme={null}
first-mod: Claude has made 0 tool calls since this mod loaded
```

If `/tally` isn't in the command list, the module didn't load. See [Find out why a mod does nothing](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md#find-out-why-a-mod-does-nothing).

**7. Change the code while the session runs**

Leave the session open. In `register.js`, change `' · tool calls: '` to `' · tools used: '` in the `ui.render` hook and save. The highlighted line (line 4 of the block) is the one that changes:

```javascript first-mod/hooks/register.js {4} theme={null}
  // Runs each time Claude Code draws the spinner
  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    // Keep Claude Code's spinner, with the count added after its word
    return next({ ...e, props: { ...e.props, suffix: ' · tools used: ' + calls + '…' } })
  })
```

A line in the transcript says `first-mod` reloaded and lists its hooks, and the next spinner uses the new text, as in `Thinking · tools used: 1…`.

### How the example mod works

In `first-mod`, the `session.start` and `tool.call` hooks observe and return `next(e)`; the `command.run` hook answers `/tally` itself without calling `next`, and its matcher `{ command: 'tally' }` limits it to that command; the `ui.render` hook rewrites, passing `next` a copy of `e` whose `suffix` holds the count. Each hot reload runs `register` again, so `calls` resets to `0`.

The built-in `plugin-authoring` skill covers this for the installed build: load it (`/plugin-authoring`) and grep the `claude-code.d.ts` it writes for `Register` and `EngineInterface`. If the skill is not available, read [How the example mod works on the official page](https://code.claude.com/docs/en/plugins/mods/create#how-the-example-mod-works).

## Keep working on a mod

Once a mod loads, have Claude change it, check the code against the type definitions for the running version, list the events and calls Claude Code finds in it, and test it.

### Change a mod with Claude

To change an existing mod, start the session with `--plugin-dir` pointed at the mod's directory, so that what Claude writes loads in the same session:

```bash theme={null}
claude --plugin-dir ./first-mod
```

Then ask for the change, for example `add a /tally-reset command to this mod that sets the tally back to zero`. Claude edits the hooks module, runs `claude plugin validate`, and fixes what it reports. A directory loaded with `--plugin-dir` is a [protected path](https://code.claude.com/docs/en/permission-modes.md#protected-paths), so in `default` and `acceptEdits` modes the user is asked to approve each of Claude's edits to the mod. The protected paths table gives the result for the other permission modes.

Files Claude saves during its turn reload when the turn ends, so `/tally-reset` can be tried as soon as Claude finishes.

### Get type definitions for your version

The built-in `plugin-authoring` skill covers this for the installed build: load it (`/plugin-authoring`) and read its WHERE THE TYPES ARE paragraph, then grep the `claude-code.d.ts` it writes for `tsconfig.json` (the header says what the engine lays in `.claude-plugin/types/` and the `tsconfig.json` it gives a mod with none). If the skill is not available, read [Get the types for your build on the official page](https://code.claude.com/docs/en/plugins/mods/create#get-the-types-for-your-build).

### Check what Claude Code reads from your mod

To see a mod the way Claude Code sees it, without running its code or starting a session, use `claude plugin validate`. It checks the manifest and runs the same static analysis on the hooks module's source that Claude Code runs when it loads a mod. Run it in the shell on the mod's directory:

```bash theme={null}
claude plugin validate ./first-mod
```

For `first-mod`, the output includes these lines.

```text theme={null}
  ❯ ./register.js hooks: session.start, tool.call, command.run{command=tally}, ui.render{component=Spinner}
  ❯ ./register.js calls: $.command.register, $.ui.invalidate

✔ Validation passed
```

Read the output this way:

* The `hooks:` line lists the events the module hooks, each with its filter in braces.
* The `calls:` line lists every mods API method the module calls.
* If the module reads or sets environment variables, look for `env reads:` and `env writes:` lines too, and `state reads:` and `state writes:` if it uses [`$.state`](https://code.claude.com/docs/en/plugins/mods/interface#keep-state).
* There is one line for each hook that can refuse an action, such as `gating hook without .catch: tool.call`, which says whether that hook has a [`.catch` handler](https://code.claude.com/docs/en/plugins/mods/events#handle-a-hook-that-fails).

If an event the mod is meant to handle is missing from the `hooks:` line, Claude Code won't call that hook either. The usual cause is a misspelled event name, which the command reports as an error such as `"tool.calls" is not an event`.

Follow these rules so that static analysis can find every hook and call:

* Write each mods API call in full: `$`, the namespace, then the method, as in `$.store.get('notes')`. `$` may be passed to a function declared at the top level of the same file; for a function named `loadNotes`, the `calls:` line then reads `$.store.get (via loadNotes)`. Passing `$` to a method, a function defined inside the hook, or a function imported from another of the mod's files fails validation. The `read` and `update` functions that [`$.state`](https://code.claude.com/docs/en/plugins/mods/interface#keep-state) uses are the imports that can take it. Don't assign `$` or one of its namespaces to a variable, destructure it, or index it with a computed name. `const ui = $.ui` fails with `$.ui is used as a value`.
* Write the event name in each `on` call as a string literal, such as `'tool.call'`. A variable, or a loop over a list of names, fails with `the event name passed to on() is not a string literal`.
* Inside `register`, don't declare a second variable or parameter named `on`. Validation fails with `"on" is declared again (shadowed)`.
* Import only from files inside the plugin directory, by relative path. The one bare import allowed is `claude-code`, for types and a few helpers.
* Use `import` declarations at the top of the file, as in `import { name } from './file.js'`. A dynamic `import()` fails with `a dynamic import(); a hooks module imports its own files with an import declaration`.
* Write every file as an ES module, with `import` and not `require`. The [reference](https://code.claude.com/docs/en/plugins/mods/reference.md#files) lists the file extensions Claude Code loads.

### Test the mod

Write automated tests for a mod and run them from the shell with `claude plugin test`, with no session, sign-in, or network. A test fires the events the hooks handle and checks what the hooks did.

This test fires two tool calls, runs `/tally`, and checks that the reply counts both. Save it as `first-mod/tests/first-mod.test.ts`:

```typescript first-mod/tests/first-mod.test.ts theme={null}
import { expect, test } from 'claude-code/testing'

test('/tally reports the tool calls the mod has seen', async ($, on) => {
  // Answer each tool call in Claude Code's place, so no tool runs
  on('tool.call', () => ({ result: 'ok' }))

  // Fire two tool calls, which the mod's tool.call hook counts
  await $.tool.call({ tool: 'Bash', command: 'ls' })
  await $.tool.call({ tool: 'Read', file_path: 'README.md' })

  // Run /tally and check the text its hook returns
  const answer = await $.command.run({ command: 'tally', args: '' })
  expect(answer.text).toBe('Claude has made 2 tool calls since this mod loaded')
})
```

Run the tests in the shell from the `first-mod` directory:

```bash theme={null}
claude plugin test
```

The output names each test and whether it passed, with timings that vary from run to run:

```text theme={null}
tests/first-mod.test.ts:
(pass) /tally reports the tool calls the mod has seen [22.87ms]

 1 pass
 0 fail
Ran 1 test across 1 file. [0.19s]
```

[Test a mod](https://code.claude.com/docs/en/plugins/mods/test.md) covers stubbing a model call or the store, and testing timers and drawings.

## Share your mod

A mod is a plugin, so its version lives in the manifest and people install and update it with the `/plugin` commands. How to share it depends on who it's for:

* **Anyone**: make the marketplace's repository public, or [submit the plugin to Anthropic's directory](https://code.claude.com/docs/en/plugins/publish.md#submit-to-anthropics-directory).

Before sharing, check the plugin's `name`: `claude plugin validate` fails a name that [looks like one of Anthropic's own](https://code.claude.com/docs/en/plugins/manifest-reference.md#name), such as one that starts with `claude-`. The events and methods can change between releases, so state in the README which Claude Code version the mod was tested with.

Keep developing against the directory with `--plugin-dir`, not against an installed copy. Claude Code caches an installed plugin by version, so edits don't reach the installed copy until the version is incremented and the plugin is installed again.

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/mods/create — the full official page, including sections this copy omits.
- https://code.claude.com/docs/en/plugins/overview.md — what a Claude Code plugin is.
- https://code.claude.com/docs/en/plugins/mods/overview.md — mods overview, comparing mods with settings hooks, skills, and MCP servers, and the source of built-in mods (complete plugins, each with its hooks module and tests).
- https://code.claude.com/docs/en/plugins/mods/troubleshoot.md — checking whether mods can load, changes that didn't load, why a mod does nothing, and the debug log.
- https://code.claude.com/docs/en/skills.md — skills, such as the built-in `plugin-authoring` skill.
- https://code.claude.com/docs/en/permission-modes.md — permission modes and protected paths.
- https://code.claude.com/docs/en/settings-reference — the `cleanupPeriodDays` setting.
- https://code.claude.com/docs/en/permission-modes — `dontAsk` mode.
- https://code.claude.com/docs/en/plugins/mods/admin.md — how an organization's managed settings choose how many mods to allow.
- https://code.claude.com/docs/en/plugins/manifest-reference.md — the plugin manifest, including the rules for `name`.
- https://code.claude.com/docs/en/plugins/mods/reference.md — mods reference: files, the hook function, events, mods API methods, and interface elements.
- https://code.claude.com/docs/en/plugins/mods/events.md — how a hook handles an event, matchers, and handling a hook that fails.
- https://code.claude.com/docs/en/plugins/mods/interface.md — drawing in the interface (panes, above the prompt, buttons, text fields) and keeping state with `$.state`.
- https://code.claude.com/docs/en/plugins/mods/test.md — testing a mod: stubbing what Claude Code would answer, and testing timers and drawings.
- https://code.claude.com/docs/en/plugins/publish.md — publishing plugins and submitting to Anthropic's directory.
- https://code.claude.com/docs/en/plugins/mods/api.md — the mods API: adding commands and tools, calling a model, and running work on a timer.
