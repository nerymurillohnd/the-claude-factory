# Mods and hooks

Read when a session loads mods and a hook behaves as if it were skipped or overruled, when a policy or flag turns hooks or mods off, or when deciding between a mod and a settings hook. This file covers how mods interact with hooks; writing a mod is Claude Code's built-in `plugin-authoring` skill and the type declarations of the user's build. Before you state a section's facts as current, fetch its `Docs:` section with the method in `docs-map.md`.

## Contents

- A mod next to a settings hook
- Where settings hooks run in the mods chain
- Mods and hook decisions
- What turns mods off, compared with hooks
- Evidence
- Versions

## A mod next to a settings hook

Docs: <https://code.claude.com/docs/en/plugins/mods/overview#compare-mods-settings-hooks-skills-and-mcp-servers> · <https://code.claude.com/docs/en/plugins/mods/create#ask-claude-for-a-mod>

- A mod is a plugin whose `hooks/hooks.json` has a `modules` key naming one JavaScript or TypeScript module; its handlers are functions Claude Code calls in its own process. A settings hook is a shell command, HTTP request, prompt or agent that Claude Code runs on a lifecycle event. One plugin can carry both.
- Pick a settings hook to block, allow or log an event with a script you already have. Pick a mod for a pane, a band above the prompt, a custom command, or to rewrite an event. Mods aren't sandboxed: a mod runs with the user's permissions (<https://code.claude.com/docs/en/plugins/mods/overview#decide-whether-to-trust-a-mod>).
- For a request to write a mod, point to the `plugin-authoring` skill (`/plugin-authoring`) and the types the user's build generates; don't write one from this skill.

## Where settings hooks run in the mods chain

Docs: <https://code.claude.com/docs/en/plugins/mods/events#where-settings-hooks-run-in-the-order> · <https://code.claude.com/docs/en/plugins/mods/events#hook-the-settings-hook-events>

- `PreToolUse` hooks from managed settings run before the first mod's `tool.call` hook. When a managed hook blocks the call, no mod's `tool.call` hook runs for that call.
- `PreToolUse` hooks from every other settings file and from plugins' `hooks/hooks.json` run after the last mod calls `next`, as part of Claude Code's own behavior. A mod that answers `tool.call` without calling `next` keeps them from running, and a mod that calls `next` sees their decision in the result it returns.
- Every settings hook event is also a mod event named `classic.` plus the event name (`classic.Stop`, `classic.PostToolUse`), whose input is the JSON a settings hook receives on stdin. A mod on one of them sits in the same chain as the settings hooks of that event.

## Mods and hook decisions

Docs: <https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods> · <https://code.claude.com/docs/en/plugins/mods/events#approve-or-refuse-a-tool-call-before-the-user-is-asked>

- A mod that handles `tool.check` gives its answer after the `PreToolUse` hooks have run.
- With managed settings on the machine, or a Team or Enterprise `/login` as the session's credential, a call a `PreToolUse` hook blocked stays blocked, whichever settings file the hook comes from, and a call a deny rule refuses stays refused, by default.
- With neither, the mod can approve a call that a deny rule refuses or a `PreToolUse` hook blocked. A session that runs on an API key or a long-lived `CLAUDE_CODE_OAUTH_TOKEN` isn't using that login, even when that login is stored.
- Auto mode: a call the mod approves runs without a classifier check, except where the mod can't bypass the permission prompt tool or Agent SDK permission callback. Plan mode: the mod can't approve a call that isn't read-only. `dontAsk` mode: the mod can approve a call that nothing but the mode would deny.
- For a tool that requires user interaction, such as `AskUserQuestion`, a mod's `tool.check` approval doesn't skip the prompt (v2.1.292+).
- So a hook relied on for enforcement can be overruled by a mod the user installed. Say so in an audit whenever the session loads mods and has neither managed settings nor a Team or Enterprise login.

## What turns mods off, compared with hooks

Docs: <https://code.claude.com/docs/en/plugins/mods/overview#turn-mods-on-or-off> · <https://code.claude.com/docs/en/plugins/mods/admin#choose-how-much-to-allow> · <https://code.claude.com/docs/en/plugins/mods/troubleshoot#no-mod-loads-in-a-directory-you-opened-for-the-first-time>

| Switch | Mods | Settings hooks |
| :-- | :-- | :-- |
| `"disableAllHooks": true` in `~/.claude/settings.json` | Every mod the user installed stops | Stop too, with the custom status line; what the organization manages keeps running |
| `disableAllHooks` in managed settings | Stops the mods in every installed plugin, the organization's included | Every hook in settings files turns off |
| `allowManagedHooksOnly` (managed) | Only the organization's mods and mods built into Claude Code load | Hooks in users' own settings files are blocked too |
| `allowManagedModsOnly` (option on the built-in guard, managed `pluginConfigs`) | Users' own mods are refused | Users' settings hooks keep working |
| `--safe-mode` | Every installed mod, for one session | Other customizations are disabled too |
| An untrusted folder in an interactive session | No mod loads until the trust prompt is answered | Hooks wait for the same dialog (`security-and-trust.md`) |

`disableAllHooks` and `allowManagedModsOnly` stop a mod and leave the rest of its plugin in place: its skills, commands, agents and MCP servers load. The settings and flags that stop installed mods, such as `disableAllHooks`, `--bare` and `--safe-mode`, don't stop the mods built into Claude Code.

## Evidence

Docs: <https://code.claude.com/docs/en/plugins/mods/overview#see-which-mods-a-session-loaded> · <https://code.claude.com/docs/en/plugins/mods/overview#list-what-a-mod-does-before-you-install-one>

- In a terminal session, `/plugin` shows a dim line under the tabs with the count and names of the mods the session loaded, such as `1 mod active · first-mod`. Built-in mods are left out of that line.
- `claude plugin validate <mod dir>` lists the events a mod handles (`hooks:`) and what it asks Claude Code to do (`calls:`), without running it. A `tool.call`, `tool.check` or `classic.*` entry there is a mod that can change what a hook runs or decides.
- Then reproduce with `claude --debug` as `debugging.md` says, and compare a run with the mod disabled in `/plugin`.

## Versions

Docs: <https://code.claude.com/docs/en/plugins/mods/overview#turn-mods-on-or-off>

Mods are on by default from v2.1.287 in the terminal and v2.1.286 in the Desktop app; `sources.md` → Version gates records a docs inconsistency on that minimum.
