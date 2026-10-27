---
name: building-mods
description: Use before creating, scaffolding or editing a plugin of this marketplace that is a mod or contains one, meaning its hooks/hooks.json lists modules, and before writing the README text about its mod. Not for testing or troubleshooting a mod.
---

# Building mods

A mod is a plugin whose `hooks/hooks.json` lists a hooks module under `modules`. It runs JavaScript inside Claude Code with the user's permissions and no sandbox, on machines we never see, and its API changes between releases, often with no changelog entry. This skill sets how a mod of this marketplace is built so that what users install is correct on the current build and honest about what it does.

## 1. Native first

Claude Code ships what a mod is written with. Use it before anything this skill adds:

| Need | Native tool |
| :-- | :-- |
| How to write a hooks module: events, `$`, elements, state, examples | The built-in skill `plugin-authoring`. Load it with the Skill tool before the first edit of a hooks module; its `SKILL.md`, `reference.md` and `examples/` are written for the installed build |
| The exact API of the installed build | Its declarations: `plugins/<mod>/.claude-plugin/types/claude-code/index.d.ts` once the mod has loaded, or, before that, the `types/claude-code.d.ts` that `plugin-authoring` writes as it loads. Grep them for the event or method at hand; they win over any page |
| What Claude Code reads from the mod, and what it refuses | `claude plugin validate --strict plugins/<mod>`; `--json` adds `gatingHooks` and `hasCatch` |
| The mod's tests | `claude plugin test plugins/<mod>`, which runs its `*.test.ts` and `*.test.tsx` against `claude-code/testing` |
| Type check | `tsc -p plugins/<mod> --noEmit` |
| Load it and reload on save | `claude --plugin-dir plugins/<mod>`, in an interactive session |
| Why it does nothing | `claude --debug-file <log>`, or `claude --debug=hooks` |
| Which mods a session loaded | `/plugin`: the dim line `N mod active · <names>`; **Installed** → **Built-in** lists Claude Code's own mods |
| Components and always-on cost | `claude plugin details <plugin>` |
| Re-read plugins after an edit or install | `/reload-plugins` |

## 2. What this marketplace overrides in `plugin-authoring`

`plugin-authoring` is written for a mod made in one session and shared on its own. A mod of this marketplace differs in three places:

- **Where it is written.** Skip its WHERE TO WRITE IT. A marketplace mod lives in `plugins/<name>/`, the only folder the scaffold, the checks and the catalog read. Never write in `~/.claude/dev-mods/`: loading `plugin-authoring` starts a watch there, and the first file written raises "Turn on the mods Claude writes in this session?".
- **How it is shared.** Skip its SHARING IT: no `gh repo create`, no `marketplace.json` beside the mod's `plugin.json`, no new repository. A mod reaches users only through this marketplace, by pull request, with a version bump.
- **A personal or throwaway mod** that Nery asks for, not meant for the marketplace, follows `plugin-authoring` as written.

## 3. Decide what to do

- **A new mod.** Create the plugin first with this repository's plugin scaffold, which sets its category; give it `mods` only when a mod is the plugin's purpose, as `plugin-categories` says. When a mod is added to or removed from an existing plugin, check its category with `plugin-categories` (situation C). Then add the files `plugin-authoring` describes: `hooks/hooks.json` with one path under `modules`, the hooks module, and `types/index.d.ts` when the mod keeps `$.state` values or adds a noun to `$`. Never use `claude plugin init`: it scaffolds a plugin of command hooks under `~/.claude/skills/`, not a mod (`claude plugin --help` on 2.1.310: "Scaffold a new plugin at ~/.claude/skills/<name>/"; `plugin-authoring`'s `reference.md`: "one of command hooks under `~/.claude/skills`").
- **An edit to a mod in `plugins/`.** Edits load, and the declarations are written, only in an interactive session started with `claude --plugin-dir plugins/<mod>` (`/en/plugins/mods/create` → "Change a mod with Claude"). In a session started without it, write the change, prove it with validate, test and `tsc`, and ask Nery for a `--plugin-dir` session before claiming it works live.
- **Edits ask for approval.** A folder loaded with `--plugin-dir` is a protected path: in `default` and `acceptEdits` modes each edit asks, and `permissions.allow` rules do not pre-approve it (`/en/permission-modes` → Protected paths). A sandboxed shell command cannot write there (2.1.299).
- **Types without an interactive session** (`claude -p`, an SDK host, a mod that has not loaded yet). Type-check against the `types/claude-code.d.ts` of `plugin-authoring`, with the `tsconfig.json` from that file's header kept outside `plugins/<mod>/`. `claude -p` never writes `.claude-plugin/types/` (2.1.295). Never commit `.claude-plugin/types/`; the engine git-ignores it. The mod's own `tsconfig.json` and `types/index.d.ts` are committed.
- **The mod's own contract.** `types/index.d.ts` declares each `$.state` value and any noun the mod adds to `$`. It is not the engine's `.claude-plugin/types/`. From 2.1.299 the manifest's `types` field can be left out when the contract sits at `./types/index.d.ts`.
- **The module's files.** Only `.ts`, `.tsx`, `.jsx`, `.js`, `.mjs`, `.cjs`, `.mts` and `.cts` load, each as an ES module: no `import()`, no `require`, and a bare import only of `claude-code`.
- **Where `$` may go.** Declare every function that receives `$`, and the module state they share, at the top level of the file: validate refuses `$` passed to a closure declared inside `register` (verified on v2.1.308). A top-level function declaration imported from another file of the mod loads from 2.1.299; the docs page still says it fails, so confirm with validate the first time you rely on it. Re-derivable caches (listings, snapshots) may live at the top level and redraw with `$.ui.invalidate`; the person's own choices stay in `$.state`.
- **A tool a build may not have.** Compare it through `String(e.tool)`: `Glob` and `Grep` are not registered on native macOS and Linux builds.
- **The plugin's name.** Distinctive and permanent. Validate refuses names that start with `claude-`, `anthropic-`, `anthropics-` or `cc-plugin-`. Only one plugin of a given name loads a hooks module (2.1.296+).
- **APIs for managed mods only.** A mod installed from this marketplace cannot use `$.prompt.media` or `$.session.identity` (2.1.299). Never call `next.to` either: a plugin copied from a GitHub source always runs among users' mods (`/en/plugins/mods/admin`), and a user mod that calls it does not load at all, although validate passes it (verified on v2.1.310).
- **The minimum Claude Code version.** It is the highest minimum among the features the mod uses. Mods themselves need 2.1.287 (Desktop 2.1.286). Others found so far:
  - 2.1.299: leaving out the manifest's `types`, `turn.start` with `e.agentId`, `Text` `weight` (`bold` is deprecated);
  - 2.1.301: `Input` `rows`, `$.env.set` answering `{ deny }`;
  - 2.1.304: `e.isReadOnly` on `tool.check`, `settings.read` receiving each settings layer;
  - 2.1.307: a hook's `ask` routed to a person;
  - 2.1.309: `turn.step` naming a model by alias.

  Look up any other feature in the changelog. State the minimum in Requirements and in the Claude Code badge.
- **When sources disagree**, trust in this order:
  1. the installed binary's output;
  2. the changelog, read raw from <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md> (expect missing version headings);
  3. the installed build's declarations;
  4. `plugin-authoring`'s `reference.md`;
  5. the docs pages;
  6. the declarations copy on GitHub;
  7. this skill.

  Correct this skill when it loses.

## 4. What this project verified

These hold on the builds named, and neither `plugin-authoring` nor the docs pages say them:

- **`tool.check`.** Answer `{ decision: 'allow' | 'ask' | 'deny', reason? }`, or `await next(e)` to leave the decision alone. Never return `decider`: changelog 2.1.304 announced `decider: "person"`, but 2.1.307 removed it with no entry, and the 2.1.310 declarations have no such field. A hook's `ask` goes to a person from 2.1.307: the engine pins `plugin` on it, no classifier's allow settles it, and it becomes a deny where nobody can be asked. State v2.1.307 as the minimum when the README promises that routing.
- **Guards fail closed.** A hook whose answer refuses something gets a `.catch` that refuses. At `tool.check`, return `{ decision: 'deny', reason }` without testing `next.called`. At `tool.call`, test `next.called` first and replay `next(e)` when it ran.
- **Subagents.** From 2.1.299 `agent.spawn` also runs when a finished subagent or a killed teammate is resumed, with `e.resume`. The docs page still says it does not. To gate subagents completely, also guard `SendMessage` in `tool.call` until a test proves `e.resume` covers that path.
- **Protected folders.** For a file in a protected folder such as `.claude/`, Claude Code shows its own prompt with the change and no hook reason, and a declined prompt tells the model only `User rejected update`. A guard's advice reaches Claude only through a deny. A session-wide approval in that prompt does not settle the hook's later asks (observed live).
- **A turn's cost.** Add each subagent's `turn.complete` `usage` to the main loop's: each loop reports only its own requests (observed live on v2.1.308).
- **Long lists.** Scroll them yourself (observed live on v2.1.308):
  - keep the engine's window pinned one row into a body exactly `bodyRows` tall, with a spacer row above and below;
  - turn each `ui.scroll` `by` into your own offset, answering `next({ ...e, offset: 1 })`;
  - let a `Client` with `flexGrow` measure the rows it really has and post them.

  A `Client` gets keys only after a click on it.
- **Module-level variables.** A reload re-initializes them, so keep values in `$.state` or `$.store`. The one exception is a counter of the turn in progress, when losing it to a reload mid-turn only shortens that turn's count; the README says so.
- **Updates can break a mod.** That is our risk to carry, not the user's: keep it out of user docs, and prove each release on the current build.

## 5. The README of a plugin with a mod

Put each of these in the template's own sections:

- **Where it runs**, from `/en/plugins/mods/overview` → Where mods run. Don't take surfaces from validate: it stopped predicting them in 2.1.304.
- **What turns it off.** `disableAllHooks` and an organization's `allowManagedModsOnly` stop the mod and keep the rest of the plugin (skills, commands, agents, MCP servers) loaded. `--safe-mode` and `--bare` start Claude Code without the plugin's mod, and `--safe-mode` without any customization.
- **Organizations.** With managed settings or a Team or Enterprise login, the built-in guard `cc-plugin-sec-default` loads ahead of user mods: it can refuse the mod or keep a deny the mod tried to lift. `allowManagedModsOnly` refuses any mod installed from a GitHub source, even one the organization enables. Validate names the hooks skipped under managed settings (2.1.299).
- **What it reaches.** Build the list from validate's `hooks:`, `calls:`, `env reads:` and `state` lines and from reading the module, because the lines are cut at about 1,000 characters (anthropics/claude-code#105020). Then:
  - name every file it reads, since a permission deny rule such as `Read(.env)` does not cover `$.fs`;
  - name every network call, since a WebFetch deny does not stop `$.http.fetch`;
  - say what it never does (writes, network, model calls);
  - tell users to run `claude plugin validate` themselves before installing.
- **The permission prompt.** Say that the mod cannot restyle it or change what it shows.
- **Diagnosis.** `/plugin` names the mods the session loaded, and only `claude --debug` shows why one was refused or a hook skipped.
- **Options.** Set them from the shell with `claude plugin install <plugin>@the-claude-factory --config <key>=<value>`, or in `/config`.
- **Tested with.** In the Claude Code row of the Compatibility table, "Tested with vX.Y.Z.", updated in every release, and the same version in that release's CHANGELOG entry. The docs say the README is where to state it (`/en/plugins/mods/create` → Share your mod).

## 6. Sources

| Page | Read when |
| :-- | :-- |
| `plugin-authoring` (built-in skill) | Before any hooks-module code: where things are, events, `$`, drawing, state, examples |
| [Overview](https://code.claude.com/docs/en/plugins/mods/overview.md) | How a mod works, where mods run, turning them off, which mods loaded, built-in mods, trust |
| [Create a mod](https://code.claude.com/docs/en/plugins/mods/create.md) | Files, what validate reads, changing a mod with Claude, type definitions, sharing |
| [Reference](https://code.claude.com/docs/en/plugins/mods/reference.md) | Files, the hook function, every event table, mods API methods, render sites, elements, limits, settings |
| [Events](https://code.claude.com/docs/en/plugins/mods/events.md) | Guarding or changing a tool call, `tool.check`, read-only calls, the order mods run in, failing hooks |
| [API](https://code.claude.com/docs/en/plugins/mods/api.md), [Interface](https://code.claude.com/docs/en/plugins/mods/interface.md), [Admin](https://code.claude.com/docs/en/plugins/mods/admin.md) | `$` calls and background work; drawing and `$.state`; organization controls and the built-in guard |
| [Permissions](https://code.claude.com/docs/en/permissions.md), [Permission modes](https://code.claude.com/docs/en/permission-modes.md) | Precedence among rules, hooks and mods; protected paths |
| [Plugins → Loading](https://code.claude.com/docs/en/plugins/loading.md) | Name conflicts, `--plugin-dir`, synced plugins |
| [Changelog, raw](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md) | Every change since the last release, and each feature's minimum version |
| [Docs index](https://code.claude.com/docs/llms.txt) | A mod page not listed here |
