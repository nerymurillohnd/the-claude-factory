---
name: troubleshoot-and-debug
description: Use when a Claude Code plugin or marketplace won't add, install, enable, update, load or run, when the user pastes a plugin error, an Errors tab entry or a failing claude plugin command, or when the wrong copy, scope or version of a plugin loaded, a change did nothing, or a plugin's skill, agent, hook, MCP or LSP server or mod is missing or misbehaves, on the terminal, the desktop app, cloud sessions, project threads, Claude, Cowork or the Agent SDK. Finds the loading stage and the documented cause from the exact message or the state on disk and in settings, sweeps every place the same cause reaches, applies the fix in one pass and verifies it once. Not for testing a working plugin or writing evals, which test-and-evals covers.
---

# Troubleshoot and debug Claude Code plugins

You are the user's plugin debugger. Two jobs, one discipline:

- Troubleshoot: the user has a message. Find the stage that produces it, the cause the docs give for it, and the fix.
- Debug: there is no message, or the wrong copy, scope or version loaded, or a change did nothing. Read the loading rules and the state on disk and in settings until one rule explains what happened.

These files were checked against Claude Code 2.1.330 and its docs. When `claude --version` is newer, read the changelog entries after it for the message or rule in question; the installed `--help` wins for flags.

Load `plugin-engineering:cli-commands-guide` too if it isn't loaded yet: it gives each command's exact flags, output, JSON fields and exit codes.

## Gotchas

- `--plugin-dir` loads a plugin in place, and an install from a git-hosted marketplace loads a copy without anything outside the plugin's folder: "works with `--plugin-dir`, breaks after install" is almost always a path that reaches outside the plugin.
- A manifest `version` keeps users on the cached copy however many commits follow: `claude plugin update` then prints `<name> is already at the latest version`.
- Nothing on disk or in settings reaches a running session until `/reload-plugins` (with `--force` when it asks) or a new session.
- `enabledPlugins` merges key by key; a higher source wins, so a project `true` overrides the user's `false`. To turn a project-enabled plugin off for one person, set it `false` in `.claude/settings.local.json`.
- A `--plugin-dir` plugin with the same name replaces an installed one in silence; only the debug log records it.
- Many causes appear only in the debug log, which `claude --debug` writes to `~/.claude/debug/<session-id>.txt` without printing anything to the terminal.
- In a cloud session the repository's `extraKnownMarketplaces` are not added and nothing from the user's own `~/.claude/` is there; plugins turned on for the user's claude.ai account arrive as `<name>@synced`.
- A message that names a hooks module (`hooks module not loaded`, `hooks module did not load`) means the plugin is a mod.

## Pick the job

First check where the session runs (`echo "$CLAUDE_CODE_REMOTE"`, the desktop app, a project thread, an SDK application). When it isn't the user's own terminal, read [Where the session runs](references/environments.md) before anything else: it says what is supposed to load there and where each fix goes.

1. The user has an exact message, an Errors tab entry or a failing command: troubleshoot. Read [Plugin messages by stage](references/messages.md) and search it for the message text.
2. No message, or the wrong copy, scope or version, or a change that did nothing: debug. Read [How plugins load](references/loading.md) and go to the section the symptom names.
3. The plugin loaded, but an agent, hook, MCP or LSP server or mod misbehaves, or a message names a hooks module: read [Components that load but misbehave](references/components.md).

## Diagnose: one cause, every place it reaches, one verification

Work from evidence, not from attempts: changing something and running again to see what happens hides the cause and leaves its other effects in place. Copy this checklist into your reply and tick each step.

```text
Progress:
- [ ] 1. Capture the facts
- [ ] 2. Read the state before changing anything
- [ ] 3. Place it: stage and origin
- [ ] 4. Name the cause from the reference
- [ ] 5. Sweep for the cause's other effects
- [ ] 6. Apply every fix in one pass
- [ ] 7. Apply the change to the session
- [ ] 8. Verify once
```

1. Facts: the exact message, the command or action that produced it, the surface (terminal, desktop, VS Code, cloud, `-p`, CI, SDK), the folder the session started in, and `claude --version`.
2. State: run `claude plugin list --json` and read the plugin's `id`, `scope`, `enabled`, `installPath`, `readFromFolder`, `errors`, `notes` and `projectEnabled`; then `claude plugin details <name>`, `claude plugin marketplace list`, the `/plugin` Errors tab, and `claude plugin validate <plugin-dir>` for the user's own plugin. These read and change nothing.
3. Place it: which stage did the plugin reach (declared in settings, fetched to disk, loaded in the session), and which origin is it (`@<marketplace>`, `@inline`, `@skills-dir`, `@synced`)?
4. Cause: name it from the reference entry that matches, quoting the message or the rule. When two causes fit, use the state from step 2 to rule one out before going on.
5. Sweep: look for the same cause in the marketplace's other plugins, the other scopes, the installed copy and the `--plugin-dir` copy, the other people who clone the repository, and CI. One cause often explains several symptoms the user reported separately.
6. Fix: apply every fix the causes need, in one pass. Say which files change and why, and leave the user's committed files alone when a personal file fixes it.
7. Session: run `/reload-plugins`, with `--force` when it asks, or start a new session.
8. Verify: check once, with what the reference entry says shows the fix worked, such as the Errors tab entry gone, `Installed plugin:` or `✓ Installed <plugin>.`, `Reloaded:` with no errors line, or the component listed by `claude plugin details`. Run the check yourself when you can.

When a fix needs something only the user can do (a terminal they own, an administrator, a credential), say exactly what to run or ask for, and what they will see when it worked.

## Report

```markdown
## Diagnosis
For each problem: symptom → stage and origin → cause, quoting the message or rule and naming the reference section.

## Fixes
Numbered, in the order to apply them, each with the exact file or command and why.

## Also affected
What else the same causes reach, or "nothing else" with the reason.

## Verify
The commands to run once all fixes are in, and what each prints when it worked.
```

## Reference files

- [Plugin messages by stage](references/messages.md): every documented message, from where `/plugin` runs through install, hooks, servers, building, hosting and organization policy.
- [How plugins load](references/loading.md): stages, origins, files on disk, copies, versions, which setting wins, name conflicts, reloads and the debug log.
- [Components that load but misbehave](references/components.md): plugin agents' fields and tools, hooks, MCP and LSP naming, and mods.
- [Where the session runs](references/environments.md): cloud sessions, project threads, Claude and Cowork, and the Agent SDK.
