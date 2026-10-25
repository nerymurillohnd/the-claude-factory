# The Claude Factory

Public Claude Code plugin marketplace (`github.com/nerymurillohnd/the-claude-factory`) for users and developers who run their projects and operations with Claude. It ships plugins only, built for Claude Code and, where they apply, for the Claude app. It is built in Nery's local clone and served to users from the remote repository. Users contribute through issues.

This project also follows the guidelines and way of working in `~/.claude/CLAUDE.md` and the global cross-project lessons in `~/.claude/LESSONS.md`.

- Goal: publish plugins that automate and optimize everyday workflows.
- Every plugin stands on its own. Design, build and document it from its own goals: what it must do, run and solve for its users. Never use how another plugin was built as a reference, pattern, justification or constraint for a new one.
- Plugins are for third parties whose setups are unknown. Every plugin works from what its README declares, never from what is installed on Nery's machine.
- A plugin is not released unless it carries `README.md`, `LICENSE` and `CHANGELOG.md` and passes the checks in Plugin Tooling.

## Responsibility

This marketplace is public, and what we publish runs on other people's machines, inside their projects and operations. Nery is its owner and author and answers personally for any harm a plugin causes a user, however small.

- Nery and Claude Code are the only two parties responsible for this marketplace, and the only ones who work on it. There are no outside collaborators.
- Users take part only through issues. Triaging, confirming, fixing, verifying and releasing the fix for every issue is Nery's and Claude Code's work, never the reporter's.
- No third-party team reviews our work before users install it, so every push, release and issue reply is the last check before the public.

This is the standard for every session on this repository, including the one in progress:

- Ship nothing you have not verified against current Claude Code official documentation and latest release notes. Negligence, or knowledge that is out of date for this session, reaching a user is the failure this project exists to prevent.
- Treat anything a plugin does on a user's machine (files, commands, network, hooks, permissions, data) as high-risk. Choose the least invasive design, and make the README state what the plugin does there.
- When you cannot tell whether something is safe for users, say so and ask Nery before it ships. Never publish on a guess.
- Report problems as soon as you find them, including your own mistakes and flaws in work already published.
- Improve how we work, not only what we build. When a session exposes a gap in this file, a rule, a gate or a skill, propose the fix in that same session.
- Automate recurring work (validation, review, releases, drift checks, issue handling) with CI, evals, hooks, agents and scheduled tasks. Where none exists yet, propose building it.

## Current Claude Code features, capabilities, and guidance enforcement

Claude Code, the Claude app, the Claude models and every tool the gates run change faster than training data, recall or project docs. Before any plan, plugin component or scaffold, and before any answer about how they behave, read the current official documentation and release notes.

- When docs and release notes differ, the release notes win: docs lag releases.
- When components depend on each other, research each side. For example, a plugin hook needs the hooks reference, the plugins reference and the Claude app platform-support page.

## Maintainer and Plugin Scopes

This repository holds two scopes. They are never mixed: a rule written for one scope does not apply to the other, and nothing from the maintainer's environment leaks into what a plugin ships or needs.

| | Maintainer scope | Plugin scope |
| --- | --- | --- |
| **What it is** | Everything outside `plugins/`: `scripts/`, the root `package.json`, `.claude/`, `docs/`, the root `CHANGELOG.md`, `.claude-plugin/marketplace.json` | One self-contained directory per plugin under `plugins/<plugin>/` |
| **Who it serves** | Nery and Claude Code | Third parties whose setups are unknown |
| **Environment** | The tools, versions and binaries on Nery's machine | Only what the plugin's `README.md` declares as prerequisites |
| **Versioning** | None | Semantic Versioning per plugin |

Rules that keep the scopes apart:

- Before acting, identify the scope of every file the task touches. A task that touches both is handled as two parts, each under its own rules.
- `scripts/` (maintainer) and any scripts inside `plugins/<plugin>/` (plugin) are different things. A script inside a plugin follows the plugin rules: portable, declared prerequisites, shebang and executable bit.
- Maintainer tools may be run over plugin files to check them. That never makes them a dependency of the plugin, and a plugin never assumes them.
- Never copy a maintainer-side path, tool or version into a plugin, and never apply a plugin-side constraint (versioning, portability limits) to a maintainer file unless a rule below says so.

### Maintainer Tooling

- Use the tools, versions, and binaries available on the maintainer's machine.
- Python: format and lint with Ruff, type-check and diagnose with Basedpyright, test with unittest or pytest.
- Markdown, JSON, JavaScript and TypeScript: format and lint with Biome.
- Never format these Markdown files, with Biome or any other tool: every `SKILL.md`; `.claude/memory/`, `MEMORY.md` and the files it indexes; every `CLAUDE.md`; `.claude/session-handoff/`; the ADRs in `.claude/maintainer/decisions/`; the ledgers in `.claude/maintainer/technical-debt/`; `.claude/plans/`; `.claude/specs/`; `.claude/rules/`; and `.claude/templates/`. `biome.json` excludes them whenever Markdown is in its `files.includes`.
- JavaScript and TypeScript: type-check with `tsc` under the strictest settings and `--noEmit`; inspect the effective configuration with `--showConfig`.
- Shell scripts: format with `shfmt` and lint with ShellCheck.
- The root `package.json` is the manifest for repository-level JavaScript and TypeScript development tooling, not for plugin runtimes. Do not mix the two.
- Set `"private": true` in the root `package.json` to prevent accidental NPM publication.
- Retain the root NPM manifest only while repository-level tooling requires it.
- Run `npm ci` in every fresh clone and new worktree, with the `.nvmrc` Node selected.
- Existing gates that still use Mypy must be refactored to Basedpyright as they are discovered.

### Plugin Tooling

- Plugins must be self-contained and portable. They are intended for third parties and must not contain hard-coded paths or assumptions about any maintainer's machine.
- Default target platforms are Linux and macOS with POSIX-compatible interfaces.
- Windows support is optional and, when provided, must be limited to Git Bash only.
- Plugins must not depend on the maintainer's runtime tools or environment. All required tools, version constraints, binaries, and software dependencies must be declared as installation prerequisites in each plugin's `README.md`, including any feature-specific requirements.
- A plugin that needs Node packages ships its own `package.json` and a lockfile Claude Code reads in `plugins/<name>/`: a text `bun.lock`, or an npm `package-lock.json` or `npm-shrinkwrap.json` with `lockfileVersion` 2 or 3. Never `bun.lockb`, `yarn.lock` or `pnpm-lock.yaml`: Claude Code skips the install with them. It never relies on the root `package.json`, and its `README.md` declares npm or Bun as a prerequisite.
- Every plugin is validated with `claude plugin validate --strict`.
- Mod plugins are additionally tested with `claude plugin test`.
- CI runs evals only for plugins that contain evals, and only when those plugins have changed; otherwise the evals are skipped.
- Executable plugin scripts (especially Claude Code hooks) must include their interpreter's shebang (`#!/usr/bin/env python3`, `#!/usr/bin/env bash`, or `#!/usr/bin/env node`), be marked executable with `chmod +x`, and have their executable permissions preserved in Git.

## Plugin Categories

Categories: `development`, `productivity`, `automation`, `mods`, `testing`, `security`, `documentation`, `data`, `design`, `devops`, `integrations`, `language-support`, `learning`.

- `scripts/categories.json` is the only place a category is defined: its `id`, the title and description the README catalog shows, and the catalog order. Add or change a category there first.
- Give every plugin exactly one category, chosen by its purpose, in `metadata.category` of its `plugin.json`. `node scripts/new-plugin.mjs --category <id>` sets it for a new plugin.
- Put a plugin in `mods` only when it is a mod: its `hooks/hooks.json` lists one hooks module under `modules`. A mod whose purpose is another goes in that category.
- After setting or changing a category, run `npm run generate`: it writes the category into `marketplace.json` and the README catalog. Never edit the category in either file by hand.

## Mods

How to write a mod in `plugins/<name>/`. Mods change between releases, often without a changelog entry: when a line disagrees with the mod docs or with the declarations the engine writes for the installed build, those win and this block gets fixed. Testing and troubleshooting a mod follow the `testing-mods` skill.

### Sources

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

### Files and the hook function

- **Build** a marketplace mod in `plugins/<name>/` and run it with `claude --plugin-dir`, not in the session mods folder the plugin-authoring skill names: the project's scaffold, gates and catalog read only `plugins/`.
- **Declare** these at the top level of `register.ts(x)`: every function that receives `$`, and the module state they share. `claude plugin validate` refuses a `$` passed to a closure declared inside `register` (verified on v2.1.308). Re-derivable caches (listings, git snapshots) may live there too and redraw with `$.ui.invalidate('ui.render')`; the person's own choices stay in `$.state`.
- **Declare** exactly one module path in `hooks/hooks.json` → `modules` (`"modules": ["./register.ts"]`); classic settings hooks can sit beside it under `hooks`. The module is an ES module that exports `register(on, options)`.
- **Read** `options` as the plugin's `userConfig` values with defaults filled in, and treat a missing value as its default.
- **Declare** `$.state` values and any namespace the mod adds in `types/index.d.ts`, named by `types` in the manifest. It is not the engine's `.claude-plugin/types/`.
- **Treat** `e` as deeply frozen: change an event by passing a copy to `next`, as in `next({ ...e, text })`.
- **Write** `turn.step` and `process.spawn` hooks as async generators; every other hook is an async function.
- **Read** `next.budget.remainingMs` before slow work, and `next.origin` to know who fired the event (`{ plugin: 'engine', tier: 'core' }` for Claude Code).
- **Treat** every `$` call as fallible: each mods API method is also an event, and a mod that runs before yours can answer it with `{ deny }` or a `{ value }` of its own.

### Where mods run

- **Claim** surfaces from Overview → Where mods run: hooks run in every session that loads the plugin, whatever the model provider: the terminal (JetBrains included), the Desktop Code tab, the VS Code extension, `claude -p`, the Agent SDK, Remote Control and cloud sessions that receive the plugin; they do not run in a Desktop WSL session. Drawing appears only in the terminal, the Desktop Code tab and the VS Code extension.
- **Remember** that `disableAllHooks` and `allowManagedModsOnly` stop the mod and keep the rest of the plugin (skills, commands, agents, MCP) loaded.
- **Expect** the built-in guard `sec-default@builtin` (`cc-plugin-sec-default`) ahead of user mods on machines with managed settings or a Team or Enterprise login.

### Events to handle with care

- **Answer** `tool.check` with `{ decision: 'allow' | 'ask' | 'deny', reason? }`, or return `await next(e)` to leave the decision alone. Never return `decider`: the declarations for the installed build have no such field, although changelog 2.1.304 announced `decider: "person"`.
- **Expect** an unknown field in a hook's answer to be ignored, not to skip the hook: a stray field fails only the tests that assert it.
- **Rely** on the declarations for who answers a hook's `ask`: the engine pins `plugin` on it, puts it to a person (dialog, host callback or `PermissionRequest` hook), lets no classifier's allow settle it, and turns it into a deny where nobody can be asked. State the minimum version that has this routing, because an older engine puts the `ask` to the mode's decider, and in auto mode the classifier can approve it.
- **Promise** no reason in the dialog for a file in a protected folder such as `.claude/`: there Claude Code shows its own prompt with the change and no hook reason (observed live), even though the declarations say the dialog shows it. A declined prompt tells the model only `User rejected update`, so a guard's advice reaches Claude only through a deny. A session-wide approval the person picks in that prompt does not settle the hook's later asks (observed live: the next guarded edit asked again).
- **Order** your reasoning: `tool.check` runs after the `tool.call` and `PreToolUse` hooks and before the permission dialog, the auto mode classifier and any `PermissionRequest` hook.
- **Use** `e.agentId` to tell a subagent's or in-process teammate's call from the main loop's, and `e.ceiling` to see a connector tool your organization set to `ask`. Read `e.isReadOnly` as present only when `true`, and never approve on it alone.
- **Add** each subagent's `turn.complete` `usage` to the main turn's to get what a turn cost: each loop reports only its own requests, so the sum counts every token once (observed live on v2.1.308: main loop plus one Explore subagent equaled the run's `modelUsage` exactly).
- **Remember** precedence: without managed settings or a Team or Enterprise login, a mod's `allow` overrides deny rules and `PreToolUse` blocks; with them, the built-in guard keeps the deny (`tried to lift a deny rule in your settings`) unless `allowModsToOverrideDenyRules` is set. In plan mode a mod cannot approve a write.
- **Avoid** rewriting a tool call's input in `tool.call` or `turn.step` in auto mode: the server-side classifier reviewed the original input, so the call is denied with `a hook changed this call's input after the model wrote it`.
- **Guard** `SendMessage` in `tool.call` too when you gate subagents: `agent.spawn` does not run again when Claude resumes a subagent.
- **Change** only `text` and `frontmatter` in a `skill.prompt` hook; changing any other field fails the hook.
- **Filter** a telemetry hook with `{ to: 'collector' }`, or the mod fails `claude plugin validate`.

### Failure and limits

- **Expect** a hook that throws, times out or returns the wrong shape to be skipped (`<name>: <event> hook skipped: <reason>`, once per event and kind until reload), leaving the verdict beneath it when it failed before `next`, and its result when it failed after.
- **Fail closed** with `.catch` on every blocking hook. At `tool.check`, return `{ decision: 'deny', reason }` from it without testing `next.called`; at `tool.call`, test `next.called` first. `next.error.kind` is `throw` (also a refused result or a worker that ended) or `timeout`. A `.catch` has 1 second, and one that fails leaves the hook skipped.
- **Know** that `.catch` runs only when the hook itself throws or times out: events raised beneath the hook's own `$` calls skip the hook without asking `.catch`.
- **Budget** 10 seconds of a hook's own time per event (50 ms for `prompt.edit`; time inside `next` and `$` calls other than `$.clock.sleep` does not count), 30 seconds for `$.process.run` by default, 4 MiB per `$.fs.read` or `$.fs.write`, and 4,096 characters for a `drop` or `deny` reason. Name commands, tools, subagent types and panes with letters, digits, `_` and `-`, up to 64 characters. Read Reference → Limits before relying on any other bound.
- **Await** inside every loop: installed mods share one worker thread, a hook that blocks it gets its mod unloaded (`it crashed the hooks worker`), and three untraced crashes turn off every non-built-in mod for the session.

### State, files and reload

- **Keep** values in `$.state` or `$.store`, never in module-level variables: a reload re-initializes the module. Counters of the turn in progress are the exception, when losing them to a reload in the middle of a turn only shortens that turn's count; say so in the README.
- **Use** `$.store` (shared by every session on the machine, 4 MiB of JSON) for data several sessions change: `$.fs.write` is not atomic and another process can read a half-written file.
- **Reload** saved values in a `classic.SessionStart` hook: `/clear`, `/resume` and `/branch` reset `$.state` and do not fire `session.start` again.
- **Register** commands, tools and agents in `session.start`, which runs again in each fresh copy after a reload; a `$.agent.register` call from code still running in the old copy is refused.
- **Expect** that after the user presses Stop, a mod cannot start work until the next message.
- **Know** that `$.prompt.submit({ text })` reaches Claude after a sentence naming your mod as the sender; only `asUser: true` sends it as the user's words. `$.mcp.connect` reaches only servers your own manifest lists.

### Interface

- **Return** `await next(e)` inside a `Box` when you draw the shared band, and give that `Box` no size or position props, or you hide every mod after yours.
- **Check** `e.surface` against the Render sites and Elements tables, and fall back to a transcript line or a command reply where nothing draws. The VS Code extension ignores some props (`Button` `hotkey`, `Code` colors and more).
- **Use** `weight` instead of the deprecated `bold`, and a `borderStyle` from the documented list: any other name draws no border.
- **Open** a pane from a command or a button, and read `isPlaced`: a pane opened without the user asking waits for a wide terminal.
- **Scroll** a long list yourself (observed live on v2.1.308): keep the engine's window pinned one row into a body exactly `bodyRows` tall, with a spacer row above and below, and turn each `ui.scroll` `by` into your own offset, answering `next({ ...e, offset: 1 })`. With a tree that fits, the engine raises no `ui.scroll` for a wheel-up at offset 0; with spacer rows sized to a header you counted, any header that draws taller than counted hides the last rows. Let a `Client` with `flexGrow` measure the rows it really has and post them.
- **Expect** a `Client` to get keys only after a click on it; Ctrl+X Tab focuses the pane, where only `Button` hotkeys answer. A plugin's own `$.ui.scroll({ to: 'start' })` skips its own `ui.scroll` hook (re-entry): pin with `{ to: { key } }` on a keyed `Box`.

### Maintenance

- **Expect** a Claude Code update to break a mod: the mods API is in early access and changes between releases, often with no changelog entry. This is our risk to carry, not the user's: keep it out of user docs.
- **Version** each mod with semver like any plugin, and record in each release's CHANGELOG entry the Claude Code version it was validated and tested on.
- **Prove** each release on the current build: `npm run gates` runs `claude plugin validate --strict`, `claude plugin test` and the mod's `tsc` for every mod, after the declarations are refreshed to `claude --version`.

### User docs for a plugin with a mod

- **Tell** users how to diagnose an installed mod: `/plugin` names the active mods, and only `claude --debug` shows why one was refused or skipped.
- **List** what turns the mod off while the rest of the plugin stays: `disableAllHooks`, `allowManagedModsOnly`, `allowManagedHooksOnly`, `--safe-mode`, `--bare`.
- **Disclose** that in organizations with managed settings or a Team or Enterprise login, the built-in guard can refuse the mod or keep a deny it tried to lift.
- **List** what the mod reaches, from the `hooks:` and `calls:` lines of `claude plugin validate`, with what each call touches and what the mod never does (writes, network, model calls): a mod runs with the user's permissions and no sandbox (Overview → Decide whether to trust a mod), and tell users to run `claude plugin validate` themselves before installing.
- **Remember** that a mod cannot restyle or change what a permission prompt shows.
- **Show** how to set the mod's options from the shell (`claude plugin install … --config <key>=<value>`) or in `/config`.

---

## Plugin Documentation and Changelogs

### Required files

Every plugin directory holds these files. `scripts/validators/plugin-required-files.py` fails when one of the first four is missing, is not a regular file, is a broken symlink or resolves outside the repository.

- `.claude-plugin/plugin.json`: the manifest, the only source of the plugin's name, version, description and category.
- `README.md`: the user guide.
- `CHANGELOG.md`: the plugin's full history.
- `LICENSE`.
- `NOTICE.txt`, only when the plugin bundles, derives from or wires in third-party material: the plugin's copyright and license, then each third-party source with its repository, version or commit, license and the files derived from it.

### Templates

- Create every one of those files from its template in `.claude/templates/plugin/`, never from another plugin's files. `node scripts/new-plugin.mjs` renders them for a new plugin.
- Keep every section the template defines. The README needs these sections, which `scripts/check-repo.mjs` checks: Why use it, What's inside, Requirements, Installation, Usage, Updating, Uninstalling, Compatibility, Changelog, License.
- Resolve every `<!-- TODO -->` and `<!-- TEMPLATE -->` comment before the plugin ships; `check-repo.mjs` fails while one is left.
- When a template changes, bring every plugin README built from it in line in the same change.

### README

- Requirements lists every installation prerequisite, as Plugin Tooling requires.
- Compatibility has one row per component type the plugin ships, and each cell says exactly what `docs/compatibility.md` says for that type.
- Never write a version number in the README. The badges show values that live in other files:
  - **Version**: a dynamic shields.io badge that reads `$.version` from this plugin's `plugin.json` on `main`, so a bump shows once it is merged. `plugin-versions-consistency.py` fails on a hardcoded version.
  - **Works in**: `Claude Code · Claude app` or `Claude Code only`, matching `metadata.surfaces` in `plugin.json`.
  - **Category**: the title in `scripts/categories.json` of the plugin's `metadata.category`.
  - **Claude Code**: the minimum Claude Code version, the same one Requirements states.
  - **License**: links to the plugin's `LICENSE`.
- When the surfaces, the category or the minimum Claude Code version change, update the badge, the README text that states it and the README catalog (`npm run generate`) in the same change.

### Plugin CHANGELOG.md

- It is the plugin's detailed history, written for its users: what changes for them, not how the code changed. It follows Keep a Changelog 2.0.0, with the change types `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed` and `Security`.
- Record every change under `## [Unreleased]`, referencing issues as `(#12)`. A breaking change leads its entry with `**Breaking:**`.
- `bump-version.mjs` turns `[Unreleased]` into the dated `## [X.Y.Z] - YYYY-MM-DD` section and writes its link references; it refuses an empty `[Unreleased]`.
- A change limited to the README gets no entry, because any entry requires a bump.
- `plugin-versions-consistency.py` checks that the newest section is the `plugin.json` version, that sections run newest first, and the link references.

### Root CHANGELOG.md

- It is a concise synthesis of the marketplace, never a copy of a plugin changelog. It has one line for each of these events:
  - a plugin is created;
  - a plugin gets a version bump, a patch included;
  - a plugin is renamed or removed;
  - the marketplace itself changes, for example the catalog gains a category.
- Group the lines under `## YYYY-MM-DD`, newest first, then under the Keep a Changelog change type: `### Added`, `### Changed`, `### Fixed`, `### Removed`. Use the date the change lands on `main`.
- Write each line in the format of its event:
  - New plugin, under `### Added`: `- **<plugin>** X.Y.Z — summary.`
  - Version bump, under the change type of the change: `- **<plugin>** X.Y.Z — summary.`
  - Rename, under `### Changed`: `- **<plugin>** X.Y.Z — renamed from <old>; summary.` The `renames` map in `marketplace.json` gets `"<old>": "<plugin>"`.
  - Removal, under `### Removed`: `- **<old>** retired: reason.` The `renames` map gets `"<old>": null`.
  - Merge into another plugin, under `### Removed`: `- **<old>** retired: its <what> is now the `<skill>` skill of **<target>**, and the marketplace renames existing installs. Type `/<target>:<skill>` where you typed `/<old>:<skill>`.` The `renames` map gets `"<old>": "<target>"`.
  - Marketplace change: `- summary.`, with no plugin name or version.
- The `X.Y.Z` of a plugin line is a version that plugin's changelog has; `plugin-versions-consistency.py` fails otherwise.

---

## Documentation and Maintenance

- `.claude/rules/workflow.md`: the workflow rules, which name the skill each stage loads.
- `.claude/maintainer/decisions/`: ADRs for important decisions.
- `.claude/maintainer/technical-debt/`: pending and closed debt.
- `.claude/memory/`: project memory (facts, feedback). Git-ignored.
- `.claude/session-handoff/`: session handoffs. Git-ignored.
- `.claude/skills/`: project skills, the procedures for work on this repository.
- `.claude/specs/`: specs, written before plans.
- `.claude/plans/`: implementation plans.
- `.claude/templates/`: templates for plugin files and the plugin review brief.
- `docs/`: the user guides, covering installation, managing plugins, compatibility, FAQ, troubleshooting and tool references.
- `plugins/`: the plugins, one self-contained directory per plugin.
- `scripts/`: maintenance scripts, tests and schemas.
- `CHANGELOG.md`: the concise project-level changelog.
- `.claude-plugin/marketplace.json`: the marketplace catalog, regenerated from `plugins/` with `node scripts/generators/marketplace.mjs`. It is never versioned or tagged.
- Keep these git-ignored in `.gitignore` and never commit them: eval results (`eval-results/` and `**/evals/results/`), `.claude/session-handoff/`, `.claude/memory/` and `.claude/settings.local.json`.

---

## Change Control

- Every change inside a plugin's directory, its components, dependencies and a `README.md`-only change included, goes through a pull request. A `README.md`-only change does not require a version bump (see the `release-and-versioning` skill).
- Every change outside `plugins/` does not require a pull request.
- Pushes, to any branch and including tags, are made only with Nery's explicit authorization.
- Release tags (`<plugin>--v<version>`) are created unsigned by `release.yml`, under the exemption `~/.claude/CLAUDE.md` gives public plugin marketplaces: users never fetch a tag, and signing in CI would put the signing key in a GitHub secret. Every commit, and every tag created locally, is still SSH-signed.
- Every item that takes labels, issues included, uses only the labels already established in the repository. The one label created is `plugin: <name>`, for a new or renamed plugin, on Nery's order; the labels of retired plugins stay.
