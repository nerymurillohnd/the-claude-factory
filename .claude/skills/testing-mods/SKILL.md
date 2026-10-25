---
name: testing-mods
description: Use whenever testing or troubleshooting a mods plugin or a plugin that contains Claude Code mods. Do NOT use for plugins without a hooks module (skills, agents, commands, MCP-only), for private or non-GitHub marketplaces, or for writing a new mod from scratch.
---

# Test and troubleshoot GitHub-marketplace mods

A **mod** is a Claude Code plugin whose `hooks/hooks.json` has a `"modules": [...]` key pointing at a hooks module (`export function register(on, options)`). When a mod's module or hook fails, Claude Code skips it and the session continues, so a broken mod looks like a mod that does nothing. This skill finds out which it is, and how to prove a mod works, for mods obtained from a **public GitHub marketplace**.

## Scope gate (do this first, say the result in one line)

Proceed only if all three hold. Otherwise say in one or two lines which one failed and that this skill does not cover it, and stop applying this skill: no `claude plugin test`/stub/mod advice for it. The user's actual problem still deserves an answer, so keep helping with your ordinary tools and the official docs, clearly labeled as outside this skill. If the request rests on a wrong premise (for example, `claude plugin test` only runs a mod's tests, so on an ordinary plugin it just reports `no hooks module to load`), say so.

1. **Mod, not plain plugin**: the plugin's `hooks/hooks.json` has a `modules` key. If it has none and the user says it should be a mod, that is the missing/misspelled `modules` case in `references/troubleshooting.md`. If the plugin is simply not a mod (skills/agents/commands/MCP only), it is out of scope.
2. **GitHub**: the marketplace (or the plugin's own `source`) lives on github.com.
3. **Public**: it clones without credentials. Private repos, other git hosts, `npm`/`archive`/`command`/`url`-file sources, and local-only marketplaces are out of scope.

## This marketplace's mods and third-party mods

This marketplace's own mods are every plugin under `plugins/` whose `hooks/hooks.json` lists `modules`. We are their authors: their source is `plugins/<mod>/` in this repository, and a defect is fixed there and shipped through a pull request, only on Nery's order. Clone a mod and leave it untouched only to check the copy that is published, to reproduce a problem a user reports, or for a mod that someone else maintains.

Mods can only run on Claude Code v2.1.287 or later (Desktop 2.1.286), so confirm with `claude --version` when behavior is "nothing loads", but do not build version checks into scripts.

## Source authority (docs lag the binary)

The official docs trail releases by days. When sources disagree, trust in this order: the installed binary's actual output, then the CHANGELOG (`https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md`), then the declarations Claude Code writes for the installed build into the mod's `.claude-plugin/types/`, then the docs pages, then the declarations copy on GitHub (`/en/plugins/mods/reference`: trust the copy written for your version over the GitHub one). Anything version-sensitive you state must say where you saw it; mark what you could not verify. `references/version-drift.md` lists the mismatches already found; read it before quoting an error message verbatim.

## Workflow

1. **Get the source.** For a mod of this marketplace, work in `plugins/<mod>/` on a branch. To check its published copy, reproduce a user's report, or test a third-party mod, run `scripts/fetch-github-mod.sh <owner/repo> <plugin-name> <dest>`: it clones the marketplace, resolves the plugin entry's `source`, and prints the plugin directory. Work only in that disposable clone, never in `~/.claude/plugins/cache/` (installed copies are cached; edits there are not the source of truth and may be overwritten).
2. **Look before you run.** Treat a third-party clone as untrusted code. Read `hooks/hooks.json`, the module file(s) and any `*.test.ts` first. `claude plugin validate` is static; `claude plugin test` *executes* the mod's JavaScript and its test files.
3. **Static check.** `claude plugin validate <dir>` (add `--json` for `gatingHooks`/`hasCatch`). It lists the module's `hooks:` and `calls:` lines, env and state reads, so it also tells you what the mod would do before anyone installs it, and it catches a misspelled event and a bad manifest.
   - A line such as `❯ ./register.tsx hooks: session.start, …` must appear for the module. If it does not (or validate errors that hooks.json needs `hooks` or `modules`), the `modules` key is missing or misspelled.
   - A pass does not prove the module loads: `validate` has passed a module the engine then refused (anthropics/claude-code#103915, `$` passed in a call with a spread argument). Only `claude plugin test` or a real session proves it loads.
   - The `hooks:` and `calls:` lines are cut at about 1,000 characters, in text and `--json` (anthropics/claude-code#105020): do not read them as a complete inventory for a large mod; read the module.
   - The "plugin directory checks" block (README, LICENSE, icon) is informational and does not change the result; the verdict is the final `Validation passed` / failure line and the exit code.
4. **Type check.** Type-check the hooks and the tests against the declarations Claude Code writes for the installed build (`/en/plugins/mods/create`, "Get type definitions for your version").
   - Refresh them first: load the mod in an interactive session, `env -u CLAUDE_CODE_PLUGIN_DIRS claude --plugin-dir <dir>`, then `/exit` (`expect` can drive it). `claude -p` and SDK sessions never write them (changelog 2.1.295).
   - The first line of `.claude-plugin/types/claude-code/index.d.ts` names the build that wrote it (`// Written by Claude Code <version>.`); it must match `claude --version`. A debug line `type root … wrote nothing` (observed on 2.1.308, not in the docs) means they were already current.
   - Then run `tsc -p <dir> --noEmit`. Claude Code adds a root `tsconfig.json` that extends the generated one when the mod has none. `tsc` flags a field the engine removed and the mod still reads, but not an extra field in an async hook's `return`.
5. **Dynamic check.** `scripts/check-mod.sh <dir>` runs validate then test, prints both outputs, and fails when either fails or when the test output lacks its summary line. If the mod ships no tests, write one following `references/testing.md` (stubs, `$.ui.mount`, mock clock/store). For a mod of this marketplace, make the fix and its test in `plugins/<mod>/`. Never push or open a PR upstream for a third-party mod unless the user explicitly authorizes it.
6. **Live session: confirm which copy runs.** Start it with `env -u CLAUDE_CODE_PLUGIN_DIRS claude --debug-file <log> --plugin-dir <dir>`, because `CLAUDE_CODE_PLUGIN_DIRS` loads other plugins as `--plugin-dir` does.
   - A `--plugin-dir` copy replaces an installed plugin of the same name silently: `claude plugin list` still shows the installed row as enabled, and only the debug log records `Plugin "<name>" from --plugin-dir overrides installed version` (`/en/plugins/loading`, "Name conflicts"). Grep for it, and for `hooks module <name>@inline loaded`.
   - A copy that managed settings lock is not loaded (`--plugin-dir copy of "<name>" ignored: plugin is locked by managed settings`), and only one copy per name loads a hooks module: `/plugin` → **Errors** says `Its hooks module does not load` for the other (v2.1.296+).
   - A report that the installed copy won over `--plugin-dir` (anthropics/claude-code#72369, v2.1.195) was closed without a reproduction, so treat the debug line, not the flag, as the proof.
7. **The copy a user gets.** Install the published mod as a user without a GitHub SSH key would, in a throwaway configuration that leaves your own settings and plugins untouched, and check the cached copy itself; make `T` with `mktemp -d` in the session scratchpad:
   ```bash
   iso() { env -u CLAUDE_CODE_PLUGIN_DIRS CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1 CLAUDE_CONFIG_DIR="$T/config" CLAUDE_CODE_PLUGIN_CACHE_DIR="$T/plugins" claude "$@"; }
   iso plugin marketplace add <owner/repo>#<branch-or-main>
   iso plugin install <plugin>@<marketplace>
   P="$(iso plugin list --json | jq -r '.[] | select(.id == "<plugin>@<marketplace>") | .installPath')"
   scripts/check-mod.sh "$P"
   ```
   `installPath` ends in `cache/<marketplace>/<plugin>/<version>/`, the copy Claude Code runs; validate and test pass on it without a session. The throwaway configuration has no sign-in, so a live session of an installed mod runs in your normal configuration with `claude --debug-file <log>`: an installed mod reports load failures only in the debug log (`/en/plugins/mods/troubleshoot`), and no command lists the modules a session loaded (anthropics/claude-code#104298). Delete `T` afterwards.
8. **Troubleshoot an installed mod.** Match the symptom or message in `references/troubleshooting.md`, from the debug log of a `claude --debug-file <path>` session, yours or the user's. To iterate on a fix, load the source with `--plugin-dir`, which hot-reloads; see `references/github-marketplace.md` for cache, version pinning and `/reload-plugins` behavior.
9. **Report.** For each claim give the evidence (command + raw output excerpt). Separate: what passed, what failed and why, what is unverified, and what only the maintainer can change.

## Rules that save the most time

- `claude plugin test` needs at least one `test()` per `*.test.ts`, every stub registered **before** the first call on `$`, and a `{ value }` or `{ deny }` result from mods-API stubs (events return their own result shape). Details and the stub table: `references/testing.md`.
- A mod that passes `validate` and `test` can still do nothing in a real session because of policy (managed settings, `allowManagedModsOnly`, `--bare`, `--safe-mode`, untrusted directory, a same-named plugin holding the hooks-module name). Tests do not exercise those, so check the refusal list in `references/troubleshooting.md`.
- To check whether mods can load at all on this machine without installing anything, run `claude plugin test` from a directory that holds no mod: `no hooks module to load` means they can.
- Tests check the tree a `ui.render` hook returns, not how an app paints it; a new layout still needs a look in a real session.
- Do not edit a third-party mod to make it pass. Report the defect and the minimal fix to its maintainer. A mod of this marketplace is fixed at its source, `plugins/<mod>/`, never in a clone or in the cache.
