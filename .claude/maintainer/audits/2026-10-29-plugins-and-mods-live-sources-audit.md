# Plugins and mods served from a public GitHub marketplace: live-sources audit

Date: 2026-10-29. Installed CLI at the time: Claude Code 2.1.314.

## 1. Scope

What the current official sources say about four subjects, read only as they apply to plugins and mods that a public GitHub marketplace serves to third parties:

1. Testing mods.
2. Testing plugins.
3. Mods: components, dependencies and manifests.
4. Plugins: components, dependencies and manifests.

Every finding passed one gate: it was checked against the GitHub releases of `anthropics/claude-code` from v2.1.295 to v2.1.314. A finding that a release changed carries that version. A finding no release in the range touches says so.

## 2. Sources and method

| Source | How it was read | Date of the content |
| :- | :- | :- |
| Release notes, `anthropics/claude-code` GitHub releases | GitHub MCP `list_releases`, full bodies | v2.1.295 (2026-10-08) to v2.1.314 (2026-10-30T01:06Z). v2.1.297, v2.1.298 and v2.1.313 have no release: 17 releases in the range |
| Official docs, code.claude.com | Context7 library `/websites/code_claude` (official site, High reputation), 30 single-topic queries | Live index at the date of this audit |
| `anthropics/claude-code` repository, `mods/` | GitHub MCP `get_file_contents`, `gh api` for one file header and its commit history | `mods/README.md` and `mods/tsconfig.json` at `b3f291d`; `mods/types/claude-code.d.ts` last changed 2026-10-13 |
| Web search | 4 searches, standard and extended | Third-party posts, used only to look for anything the official sources miss |
| Installed binary | `claude plugin --help`, `claude plugin test --help`, `claude plugin test`, `claude plugin validate`, `claude -p --plugin-dir` | 2.1.314 |

The Claude Code Docs MCP server was not used, as requested.

Precedence when sources differ: the installed binary, then the release notes, then the docs, then the GitHub repository, then third-party posts. Third-party posts confirm nothing on their own.

## 3. How a user receives a plugin from a public GitHub marketplace

These facts set the boundary between what reaches a user and what never leaves the maintainer.

**F3.1 Adding the marketplace.** A user runs `/plugin marketplace add owner/repo` and needs only `git`.
> "GitHub | `/plugin marketplace add your-org/your-marketplace` | `git`" (plugins/host-marketplace, Host your marketplace)

**F3.2 Copy to cache.** A plugin from a marketplace that was added by source is copied into the cache. Only the plugin's own directory is copied.
> "Every other marketplace plugin: Claude Code copies the plugin into `cache/<marketplace>/<plugin>/<version>/` at install and loads that copy. Files outside the plugin directory aren't copied" (plugins/loading, In-place and copied plugins)

Only "Relative-path plugins in a marketplace you added from a local path" load in place. That case covers the maintainer's own local clone, never a user of the GitHub marketplace.

**F3.3 What the copy holds.** The marketplace is a git clone (`marketplaces/<name>/` is "The clone or download of a marketplace added from GitHub", plugins/loading). So a user's copy holds exactly what is committed under `plugins/<plugin>/` at the fetched ref.
- Every committed file under that directory reaches the user: tests, eval suites, `tsconfig.json`, fixtures included. The docs list no exclusion rule for files inside the plugin directory.
- A git-ignored file never reaches the user, because a clone does not contain it.
- This conclusion is derived from the clone behavior; no docs page states it in one sentence.

**F3.4 Symlinks.** A symlink that stays inside the plugin is kept. A symlink into the rest of the marketplace is dereferenced. A symlink outside the marketplace is skipped.
> "Outside the marketplace: the symlink is skipped for security." (plugins/host-marketplace, Share files within a marketplace with symlinks)

**F3.5 Version and updates.** The manifest `version` comes first, then the marketplace entry's `version`. For a relative path inside a git-hosted marketplace with neither set, "The commit SHA of the installed directory" is used.
> "If you set `"version": "1.0.0"` and push new commits without changing it, users don't receive them." (plugins/host-marketplace, Release a new version)

> "Don't set `version` in both `plugin.json` and the marketplace entry. If you do, Claude Code uses the `plugin.json` value without warning" (same page)

**F3.6 Release tags.** Tags take the form `<plugin-name>--v<version>`, created with `claude plugin tag [path]`. The command validates the plugin, checks that `plugin.json` and the marketplace entry agree, requires a clean tree and refuses an existing tag (plugins/dependencies, Create a release tag). Version ranges in other plugins' `dependencies` resolve against these tags.

**F3.7 Node.js runtime dependencies.** When the plugin is copied, Claude Code installs the plugin's own npm dependencies into the copy. This happens only if the plugin root holds both `package.json` and a supported lockfile. Registry packages only, pinned exactly, `--ignore-scripts`, no `overrides`, frozen resolution, 60-second timeout (plugins/loading, Node.js package dependencies).

**Release-note corroboration, F3:**
- 2.1.295: "Fixed plugin marketplaces whose repository has large git submodules failing to add or refresh: only the submodules that hold plugin files are now fetched".
- 2.1.295: "Fixed `claude plugin marketplace add` reporting success for a marketplace whose name no plugin can be installed under; such an add is now refused".
- 2.1.296: "Windows: Fixed `claude plugin install` failing for GitHub `owner/repo` plugin sources on machines with no GitHub SSH key; the clone is now retried over HTTPS".
- 2.1.296: "Fixed `claude plugin marketplace add`, `marketplace update` and `plugin install` failing with an internal error for a marketplace named like `constructor`".
- 2.1.302: "Fixed plugin marketplaces re-cloning on every refresh, and newly installed git plugins showing version "unknown", when git defaults to the reftable ref format".
- No release in the range changes the copy rule, the version precedence, the tag convention or the npm install limits.

## 4. Plugins: manifest, components, dependencies

**F4.1 Manifest location.** The manifest goes at `.claude-plugin/plugin.json`; "Only `plugin.json` goes inside `.claude-plugin/`" (plugins/create). The manifest is optional: without one, the components are discovered from the layout (plugins/manifest-reference, Standard layout).

**F4.2 Fields.**
- `name` is required. `description`, `version` and `author` (`name` required inside it) are common.
- The full set in the official example: `displayName`, `homepage`, `repository`, `license`, `keywords`, `defaultEnabled`, `dependencies`, `metadata`, `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`, `experimental.themes`, `experimental.monitors`, `userConfig` (plugins/manifest-reference, Full example).
- Mods add `types` (§6).
- Eval suites use `experimental.evals` (§5).

**F4.3 Standard layout.**
- `skills/<name>/SKILL.md`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `output-styles/`, `workflows/`, `themes/`, `monitors/monitors.json`, `bin/` and `settings.json`.
- `bin/` goes on the Bash tool's PATH. "claude.ai and Cowork don't install a plugin that has this directory" (plugins/manifest-reference).

**F4.4 Path variables.**
- `${CLAUDE_PLUGIN_ROOT}` is the installed copy.
- `${CLAUDE_PLUGIN_DATA}` is `~/.claude/plugins/data/<id>/`, kept across updates.
- Which component resolves them inline and which gets them exported is tabulated on plugins/manifest-reference, Where each variable resolves.

**F4.5 Plugin-on-plugin dependencies.**
- `dependencies` in `plugin.json` takes bare names or `{ name, version, marketplace }`.
- A range resolves to "the highest git tag that satisfies this range".
- Cross-marketplace dependencies need `allowCrossMarketplaceDependenciesOn` in the root `marketplace.json`; "When it's declared in `plugin.json`, the install completes without the dependency and your plugin then fails to load" (plugins/dependencies).

**F4.6 Marketplace manifest.**
- `name`, `owner` (`owner.name` required) and `plugins` are required. Each entry needs `name` and `source`.
- Optional top-level keys: `description` (validate warns when missing), `metadata.pluginRoot` (v2.1.239+), `forceRemoveDeletedPlugins`, `allowCrossMarketplaceDependenciesOn` and `renames`.
- A relative `source` must start with `./` and must not contain `..` (plugins/marketplace-reference).

**F4.7 userConfig.** `sensitive: true` stores the value in secure storage. "`claude plugin install` never prompts for `userConfig` values"; the shell form takes `--config KEY=VALUE` (plugins/troubleshooting, plugins/cli-reference).

**Release-note corroboration, F4:**
- 2.1.295: "Added a warning to `claude plugin install`, `enable`, `disable` and `marketplace add` when the settings file they write to does not load".
- 2.1.295: "Fixed plugin options named `constructor` or `prototype` always reading as their default"; 2.1.296: "Fixed a plugin secret named `constructor` or `prototype` being deleted by the next save of that plugin's options".
- 2.1.296: "Added a note in `/plugin` on a plugin whose hooks are left out because another enabled plugin has the same name".
- 2.1.299: "Changed plugin hooks and workflow scripts to refuse values they hand back that nest deeper than 28,000 levels".
- 2.1.299: "Changed actions a plugin hook can block to be refused, not let through, when the hook cannot be handed them or cannot hand back its answer".
- 2.1.300: "Fixed plugin `WorktreeCreate` and `WorktreeRemove` hooks not running when Claude Code starts with `--worktree`".
- 2.1.302: "Fixed the PowerShell tool not finding commands in a plugin's `bin/` folder".
- 2.1.304: "Changed skill hooks: the skills of one source (a repo, your own folder, or a plugin) can register at most 1,024 hooks and 16,384 matcher characters per session".
- 2.1.305: "Changed plugins that Claude Desktop mounts by path to no longer keep their `allowed-tools` when your organization's managed settings set `allowManagedPermissionRulesOnly`".
- 2.1.310: "Added the Monitor tool and plugin monitors on Bedrock, Vertex, and Foundry, and when telemetry or nonessential traffic is disabled".
- 2.1.311: "Fixed a `--plugin-dir` folder of plugins loading as one plugin when an empty `.mcp.json` was at its top".
- 2.1.312: prompt and agent hooks "run at most 24 at a time per session".
- 2.1.314: "Changed hook `if` conditions such as `Monitor(tail *)` to match the Monitor tool's shell commands as `Bash(tail *)` matches Bash's".
- No release in the range changes the manifest fields, the standard layout or the dependency rules stated above.

## 5. Testing plugins

Every tool in this section runs on the maintainer's machine, before publication. None of them runs on a user's machine when the user installs or uses a plugin. Nothing in the docs says a user runs a plugin's validation, tests or evals.

**F5.1 `claude plugin validate <path>` is "the authoritative manifest check".**
- It checks the manifest and the frontmatter of every skill, agent and command.
- Exit codes: 0 passed, 1 failed (or warnings under `--strict`), 2 validator error.
- Its "Advice" on a README without an install line "doesn't change the verdict line or the exit code" and "requires Claude Code v2.1.295 or later" (plugins/cli-reference).
- The publish page warns that a clean local run doesn't guarantee a clean portal validation for Anthropic's directory.

**F5.2 Live loading during development.**
- `claude --plugin-dir <dir>` loads a plugin for one session; `/reload-plugins` applies edits.
- `/plugin` shows the Installed and Errors tabs; `claude plugin list` reports load status (plugins/create, Test and debug).
- A plugin that works from `--plugin-dir` but references `../shared` breaks after install (plugins/troubleshooting).

**F5.3 Eval suites, `claude plugin eval`.**
- They live under `evals/`, or under the directory in `experimental.evals`.
- `results/` "is written by each run; add to .gitignore".
- Runs are model calls billed to the runner's account.
- A non-interactive run needs `--trust-plugin`.
- `init` needs a terminal; CI uses `init --bare` (plugin-evals).
- The eval directory is always "below the plugin" (`claude plugin eval --help`, 2.1.314), so a committed suite reaches users' caches (F3.3); it never runs there.

**Release-note corroboration, F5:**
- 2.1.295: "Added advice to `claude plugin validate` when a plugin's README has no install line: it prints the line to paste and never changes the exit code, even with `--strict`".
- 2.1.299: "Added `--disallow-tools` and a `disallowed_tools` case field to `claude plugin eval`"; "Fixed `claude plugin eval` passing runs that the API refused: a run that ends on an API error now scores 0 without grading and makes the suite exit 1".
- 2.1.302: "Fixed `claude plugin` and other subcommands sometimes exiting before a queued settings or config write finished".

## 6. Mods: components, manifest, dependencies

**F6.1 Definition.** A mod is a plugin whose `hooks/hooks.json` has `modules`, an array with one path to the hooks module.
> "having it is what makes the plugin a mod" (plugins/mods/create)

**F6.2 Files** (plugins/mods/reference, Files):
- `.claude-plugin/plugin.json`: required. "Mods add no required fields."
- `hooks/hooks.json`: required. `modules`, plus optional settings hooks under `hooks`.
- The hooks module: required. It exports `register(on, options)` and is named `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.mts`, `.cts` or `.tsx`. An ES module.
- `types/index.d.ts`, unless the manifest's `types` names another path: required when the mod uses `$.state` or adds a namespace. "To leave `types` out of the manifest, you need v2.1.299 or later."
- `*.test.ts` and `*.test.tsx` files: optional, run by `claude plugin test`.

The reference table lists no `tsconfig.json` among a mod's files.

**F6.3 No build step.**
> "You don't need Node.js, a bundler, or a build step, because Claude Code loads `.js` and `.ts` files directly." (plugins/mods/create)

A user who installs a mod needs no TypeScript, no `tsc` and no `tsconfig.json`.

**F6.4 Imports.**
> "Import only from files inside the plugin directory, by relative path. The one bare import allowed is `claude-code`, for types and a few helpers." (plugins/mods/create)

**F6.5 `options`.** `register` receives the manifest's `userConfig` values, with defaults filled in. Values are stored under `pluginConfigs` keyed by the plugin id (plugins/mods/reference).

**F6.6 Dependencies.**
- A mod declares plugin dependencies through the same `dependencies` key (F4.5).
- The generated declarations add "one directory for each plugin your `plugin.json` lists under `dependencies`" (plugins/mods/create).
- Anthropic's `mods/README.md`: "A plugin outside this repository that depends on a mod's noun points its tsconfig `include` at that mod's `types/` folder for now".

**F6.7 Where mods run** (plugins/mods/overview):
- Mods are on by default. "In the terminal, use Claude Code v2.1.287 or later. The Desktop app includes its own copy of Claude Code, and mods work there from v2.1.286."
- Hooks run in the terminal, the Desktop Code tab (not WSL), VS Code, `claude -p`, the Agent SDK, Remote Control and cloud sessions.
- Drawing appears only in the terminal, Desktop and VS Code. VS Code needs extension 2.1.299+, or 2.1.304+ where feature flags aren't fetched.

**F6.8 Trust.**
> "A mod is code that runs with your permissions… Install mods only from authors and marketplaces you trust." (plugins/mods/overview)

Administrators can stop user-installed mods with `allowManagedModsOnly`, `allowManagedHooksOnly` or managed `disableAllHooks` (plugins/mods/admin).

**F6.9 `claude plugin validate` on a mod.**
- "It checks the manifest and runs the same static analysis on the hooks module's source that Claude Code runs when it loads a mod" (plugins/mods/create).
- It prints `hooks:` and `calls:` lines.
- A misspelled event fails with an error such as `"tool.calls" is not an event`.
- "Claude Code refuses to load a mod that uses the mods API in a way this command can't read" (plugins/mods/admin).
- This check runs the installed build's own engine, so it reflects that build without any declaration files.

**Release-note corroboration, F6:**
- 2.1.295: "Fixed plugins whose hooks module nests code thousands of levels deep failing to load or validate with a bare stack-overflow message"; "Improved `claude plugin validate` and plugin loading: when a hooks module is refused over a rebound top-level `var`, the error now names the line".
- 2.1.299: "Fixed `claude plugin validate` rejecting a mod's `$.state` references when `plugin.json` has no `types` key and the contract is at `./types/index.d.ts`". This is the version gate in F6.2.
- 2.1.299: "Added a note in `/plugin` and `claude plugin validate` naming a mod's hooks that are skipped where an organization manages Claude Code".
- 2.1.304: "Removed the notes from `claude plugin validate` that predicted where a mod's hooks would run" (see D3).
- 2.1.299: "Fixed mods loaded from source files being refused when a hook hands `$` to a function declaration imported from another file of the mod". The docs still list "a function you import from another of your files" among what fails validation (see D4).
- 2.1.299: "Changed the `turn.start` mod hook to also hear subagents' and teammates' turns".
- 2.1.299: "Fixed installed mods that kept running in an open session after being turned off remotely".
- 2.1.304: "Added `decider: "person"` to a mod's `tool.check` answer"; "Added `e.isReadOnly` to a mod's `tool.check` event"; "Added a transcript line when a plugin that runs first skips one of your mod's hooks".
- 2.1.304: "Changed mods' `settings.read` hooks to receive each settings layer".
- 2.1.309: "Improved the error when a hooks module is nested too deep to load: it now names the file".
- 2.1.311: "Changed `DISABLE_COMPACT` in settings files and in a mod's `$.env.set` so they can only turn compaction off".
- The mods API changed in almost every release of the range (2.1.295, 299, 300, 301, 304, 305, 309, 310, 311). A mod's behavior therefore depends on the user's build. The README's declared minimum version is what speaks to users (F6.7).

## 7. Testing mods

**F7.1 `claude plugin test [dir]`.**
- It "Runs every file under the mod directory ending in .test.ts or .test.tsx and exits with status 1 when a test fails. Needs no session, sign-in, or network" (plugins/cli-reference).
- The argument is "The mod's folder" (`claude plugin test --help`, 2.1.314).

**F7.2 Where tests live.**
- "save it anywhere in the plugin directory"; "Every test file needs at least one `test()`" (plugins/mods/test).
- The runner only discovers files under the mod's folder, so a mod's tests must sit inside the plugin directory. Under F3.3 they then reach users' caches as inert files: no user command runs them.
- Anthropic's own built-in mods keep them in `tests/` inside each mod, with shared helpers under `tests/fixtures/` (`mods/README.md`).

**F7.3 Test kit, `claude-code/testing`.**
- `test`, `describe`, `expect` and `tier` (`prepend`, `append`, `builtin`; default `user`).
- `mock.clock`, `mock.store`, `mock.env`, and `mock.session` (2.1.293+).
- `$.ui.mount` and `press`, and inline `plugins` for policy tests (plugins/mods/test).

**F7.4 What a mod test proves.** It runs the mod inside the installed binary: "A test gets the engine's own `$`… Each call on `$` is one the engine makes" (`mods/README.md`). Like F6.9, it reflects the maintainer's installed build only.

**F7.5 Whether mods can load at all.** Run `claude plugin test` from a directory without a mod: `no hooks module to load` means they can; other messages name the block (plugins/mods/troubleshoot).

**Release-note corroboration, F7:**
- 2.1.295: "Fixed `claude plugin test` passing a `session.append` hook that removes tool call, tool result or thinking blocks that a real session keeps".
- 2.1.299: "Changed `ui.render` trees in `claude plugin test`: each mod's Box or Text root now carries `part: { plugin }` naming the mod, so exact-tree assertions must include it".
- 2.1.299: "Changed `claude plugin test` to fail a call to a mod's served `$` method that has not answered within ten seconds"; "Fixed `claude plugin test` pausing a hook's time budget…".

## 8. A mod's type declarations: `.claude-plugin/types/`

**F8.1 What they are.**
> "When Claude Code loads a mod from `--plugin-dir` in an interactive session, or a mod Claude wrote for you, it writes TypeScript declaration files into the mod's `.claude-plugin/types/` directory… so your editor can autocomplete and type-check your hooks." (plugins/mods/create)

They are an authoring aid for the build the developer runs. The docs give them no role in loading, installing or running a mod. For the facts of the mods API they are the authority over the docs pages:
> "The events and methods can change between releases, so trust these files over any page, this one included, when they disagree." (plugins/mods/create, Get type definitions for your version)

**F8.2 Only development sessions write them.** 2.1.295: "Fixed generated type files being written into a `--plugin-dir` plugin's folder in `-p` and SDK sessions; they are now written only where a mod is being developed."

Checked on 2.1.314: `claude -p --plugin-dir`, `claude plugin test` and `claude plugin validate` wrote nothing into a fresh copy of `tool-ledger`.

**F8.3 They never reach users.**
- The folder Claude Code writes holds a `.gitignore` containing `*` (observed in every mod of this repository), so git never tracks it and a GitHub marketplace clone never contains it (F3.3).
- A user's installed copy loads from the cache, not `--plugin-dir`, so no user session writes them either.

**F8.4 The root `tsconfig.json` is generated too.**
> "If your mod has no `tsconfig.json` of its own, Claude Code adds one at the mod's root that extends the generated one, so your editor and `tsc -p ./first-mod` type-check the mod without more setup." (plugins/mods/create)

That root file is not git-ignored. Once committed, it reaches users (F3.3), where it extends a file they never have (F8.3). The docs give it no runtime role; it is a development file.

**F8.5 They are pinned to one build.** The declarations "describe the exact events, mods API methods, and elements in the Claude Code version you're running". The first line names that build (`// Written by Claude Code <version>.`).

**F8.6 The GitHub copy is older.**
- `mods/types/claude-code.d.ts` in `anthropics/claude-code` starts `// Written by Claude Code 2.1.277.`; its last commit is 2026-10-13.
- The docs: "The copy on GitHub can be older than the Claude Code version you have installed. When the two disagree, trust the copy Claude Code writes for your version" (plugins/mods/reference).

**F8.7 How Anthropic type-checks its own mods** (`mods/README.md`, `mods/tsconfig.json` at `b3f291d`):
- One repository-level `mods/tsconfig.json`, outside every mod. `include`: `types`, `*/types/**/*.d.ts`, `*/hooks`, `*/tests`.
- One shared `mods/types/` with the engine declarations.
- Each mod folder holds only `.claude-plugin/plugin.json`, `README.md`, `hooks/` and `tests/`, with no `tsconfig.json` of its own.
- "`tsc -p mods/tsconfig.json` typechecks every mod's hooks and tests against `types/` and each mod's own `types/` contract."

## 9. Discrepancies and unresolved points

**D1. Minimum version for mods.**
- The project owner recalled 2.1.295.
- The docs say v2.1.287 for the terminal and v2.1.286 for Desktop (F6.7). No release in the range contradicts this.
- Features newer than that floor carry their own minimum. Examples: an omitted `types` key needs 2.1.299, VS Code drawing needs 2.1.299 or 2.1.304, `mock.session` needs 2.1.293, `Input` `rows` needs 2.1.301.

**D2. `/plugin-types`.**
- `mods/README.md` and the GitHub declarations' header say the declarations are "Written by `/plugin-types`; regenerate with that command".
- No current docs page and no release note in the range mentions that command. The string `plugin-types` appears in the 2.1.314 binary, but whether a user-facing command exists was not confirmed.
- Treat it as unverified; do not build on it.
- Closed after the first pass: a GitHub code search of `anthropics/claude-code` finds `plugin-types` only in `mods/README.md`, and the repository's full `CHANGELOG.md` never mentions it. It is not a documented user command; never tell a user or a skill to run it.

**D7. The built-in `plugin-authoring` skill's declarations.**
- `building-mods` cites a `types/claude-code.d.ts` that `plugin-authoring` writes as it loads, as a source when no `--plugin-dir` session has written `.claude-plugin/types/`. The first pass did not cover it.
- The 2.1.314 binary holds the skill's loader with `var ve="${CLAUDE_SKILL_DIR}";var He="types/claude-code.d.ts"`: the skill writes that file into its own skill directory when it loads. The citation in `building-mods` stands. The file describes the installed build, like `.claude-plugin/types/`, and the same limits apply (F8.5).

**D3. Validate notes about where hooks run.** 2.1.299 added a note naming hooks skipped under organization management; 2.1.304 removed "the notes … that predicted where a mod's hooks would run". Whether the 2.1.304 removal includes the 2.1.299 note is not stated. Do not rely on either note.

**D4. Passing `$` to an imported function.**
- 2.1.299 fixed mods "loaded from source files being refused when a hook hands `$` to a function declaration imported from another file".
- The docs' static-analysis rules still say passing `$` to "a function you import from another of your files fails validation".
- Release notes outrank the docs, but the fix speaks of loading and the docs of validation. Treat imported helpers that take `$` as unsupported until a validate run on the installed build shows otherwise.

**D5. Third-party posts.**
- One claims `.claude-plugin/types/` is written "after a mod loads", with no qualifier.
- That is wrong since 2.1.295: only interactive `--plugin-dir` and Claude-written mods (F8.2). Ignore it.

**D6. Where tests and evals live versus the maintainer/plugin split.**
- The official tools require a mod's tests inside the plugin directory (F7.2) and default eval suites to `evals/` inside it (F5.3).
- Both therefore ship in the plugin's cache copy, as inert files, while running only on the maintainer's machine.
- Neither can move outside the plugin. `claude plugin eval --help` on 2.1.314: "`--eval-dir <dir>` Directory name (below the plugin) that holds the eval cases; results go to `<plugin>/<dir>/results/`". The manifest's `experimental.evals` names the same directory. Mod tests must sit under the folder `claude plugin test` is given (F7.2).
- So a committed eval suite or mod test always ships. What the maintainer controls is only what is committed: secrets and private data stay out of fixtures, and `results/` stays git-ignored (F5.3).

## 10. Conclusions to apply

1. Tests, evals, validation and type checks are maintainer tooling. A user never runs them. They are judged only by what they tell the maintainer on the maintainer's build (F5, F7).
2. A user's compatibility comes from the README's declared minimum Claude Code version (D1). It never comes from a test or a type check.
3. `.claude-plugin/types/` is a development artifact the engine writes for the developer's build, git-ignored, never shipped (F8.1–F8.3).
4. A mod's root `tsconfig.json` is a generated development file. Committed, it ships to users for nothing (F8.4). Anthropic keeps one repository-level tsconfig and no per-mod tsconfig (F8.7).
5. A type check against declarations only proves something against the build that wrote them (F8.5). `claude plugin validate` and `claude plugin test` already check a mod against the installed engine with no declaration files (F6.9, F7.4).
6. Mod tests must stay inside the mod's folder, and eval suites inside the plugin's folder; both are official constraints, and both ship as inert files when committed (F7.2, F5.3, D6).
7. Everything committed under `plugins/<plugin>/` ships to users; nothing git-ignored does (F3.3).
