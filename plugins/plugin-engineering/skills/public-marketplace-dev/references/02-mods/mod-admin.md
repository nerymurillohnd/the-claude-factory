# Manage mods for your organization

How an organization controls Claude Code mods with managed settings: stop user-installed mods, allow only its own, review what a mod can do, and enforce policy with its own mod. Read it to know which controls an administrator can apply to a mod this marketplace publishes, and what a published mod can and cannot do on a managed machine.

## Contents

- [Stop user-installed mods from loading](#stop-user-installed-mods-from-loading)
- [Know what happens by default](#know-what-happens-by-default)
  - [Know which controls still apply](#know-which-controls-still-apply)
  - [Know which hooks of a user's mod don't run](#know-which-hooks-of-a-users-mod-dont-run)
- [Decide whether to leave mods on](#decide-whether-to-leave-mods-on)
  - [Review what a mod can do](#review-what-a-mod-can-do)
- [Choose how much to allow](#choose-how-much-to-allow)
  - [Set options on the built-in guard](#set-options-on-the-built-in-guard)
- [Documentation References](#documentation-references)

A [mod](https://code.claude.com/docs/en/plugins/mods/overview.md) is a plugin that runs code inside Claude Code with the permissions of the user who installed it. Mods aren't sandboxed. Through [managed settings](https://code.claude.com/docs/en/managed-settings.md), an administrator decides whether mods run on users' machines, which ones, and in what order. An administrator can also install a mod of the organization's own that watches or refuses what other mods do.

## Stop user-installed mods from loading

To keep every mod users bring from running its hooks, set the `allowManagedModsOnly` option on the [built-in guard](#know-what-happens-by-default), a policy mod that Claude Code loads ahead of every mod a user installs. Put the option in managed settings under `pluginConfigs`, keyed by `cc-plugin-sec-default@builtin`:

```json managed-settings.json theme={null}
{
  "pluginConfigs": {
    "cc-plugin-sec-default@builtin": {
      "options": {
        "allowManagedModsOnly": true
      }
    }
  }
}
```

With the option set in managed settings:

* **No mod a user brings runs its hooks**: this covers a mod in a plugin the user installed, a mod loaded with `--plugin-dir`, and a mod [Claude wrote during a session](https://code.claude.com/docs/en/plugins/mods/create.md#ask-claude-for-a-mod).
* **The organization's mods still run**: a mod that [counts as the organization's](#install-your-organizations-mods) isn't checked. Every other mod counts as a user's and is refused. That includes a mod in a plugin enabled from a GitHub or other remote marketplace, and one the organization turns on for its members on claude.ai. If no mod counts as the organization's, no installed mod runs its hooks.
* **Users can't undo it**: the guard reads the option from managed settings only, so the same entry in a user, project, or local settings file, or in a file passed with `--settings`, changes nothing.
* **A file or MDM policy covers every provider**: when the option is delivered as a file or through MDM, it works the same way on Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry. For delivery from the claude.ai admin console, see [Platform availability](https://code.claude.com/docs/en/server-managed-settings.md#platform-availability).
* **Users' other customizations keep working**: their [hooks in settings files](https://code.claude.com/docs/en/hooks.md) and in plugins' `hooks/hooks.json`, status lines, and `/goal` aren't affected.
* **Built-in mods keep running**: mods built into Claude Code, such as `AGENTS.md` support, each have [their own switch](https://code.claude.com/docs/en/plugins/mods/overview.md#mods-built-into-claude-code).

## Know what happens by default

With no mod settings from the organization, users get the following:

* **Mods are on.** A user can install a plugin that contains a mod from any marketplace the organization's plugin settings allow, or load one from a directory with `--plugin-dir`.
* **A built-in guard runs first.** Claude Code loads a built-in mod named `sec-default@builtin` ahead of every mod a user installs. Users can't turn it off. `/plugin` and the debug log list it as `cc-plugin-sec-default`. The guard loads when either of these is true:

  * The machine has managed settings
  * The session runs on [`/login` credentials](https://code.claude.com/docs/en/authentication#authentication-precedence) for a Team or Enterprise plan

  A user who authenticates with an API key, or through Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry, gets the guard only on a machine that has managed settings. A session that runs on a long-lived [`CLAUDE_CODE_OAUTH_TOKEN`](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token) doesn't count as that login either, even when a Team or Enterprise login is stored on the machine.
* **The guard protects what the organization manages.** A user's mod can't change what managed hooks receive or decide, the system prompt, the managed `CLAUDE.md` and other managed instructions, what any mod reads as settings, or the tools and descriptions of managed MCP servers.
* **Outside what the organization manages, a user's mod acts as that user.** The mod keeps that user's permissions: it can still read and write files, start processes, and make network requests. It can also rewrite tool calls and prompts, deny a tool call, and draw in the interface.
* **Permission rules and `PreToolUse` hooks take precedence over a user's mod.** With the guard loaded, by default a user's mod can't approve a call that a `deny` rule refuses or an `ask` rule prompts for, whichever settings file holds the rule. The mod can't approve a call that any `PreToolUse` hook blocked, either.

  Permission rules and `PreToolUse` hooks apply to Claude's tool calls, not to a mod's [`$.fs` and `$.process` calls](https://code.claude.com/docs/en/plugins/mods/api#reach-files-processes-and-the-network). With `Read(.env)` denied, a mod can still read that file with `$.fs.read` or start a program that does. To limit a mod's own `$.fs` and `$.process` calls, [keep the mod from loading](#stop-user-installed-mods-from-loading) or handle them in a [policy mod](https://code.claude.com/docs/en/plugins/mods/admin#enforce-a-policy-with-a-mod-of-your-own).
* **A user's mod can still skip some prompts.** In [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode), a call the mod approves runs without a classifier check, unless the guard is loaded and the session runs with [`--permission-prompt-tool`](https://code.claude.com/docs/en/cli-reference#cli-flags) or an Agent SDK [`canUseTool` callback](https://code.claude.com/docs/en/agent-sdk/user-input#handle-tool-approval-requests). In that case the classifier checks the call first. For the prompts a mod's approval doesn't skip, see [Extend permissions with hooks](https://code.claude.com/docs/en/permissions.md#precedence-among-rules-hooks-and-mods).

The guard's source is public in the [`mods/sec-default` directory of the Claude Code repository](https://github.com/anthropics/claude-code/tree/main/mods/sec-default).

### Know which controls still apply

Mods don't replace existing controls:

* **Settings hooks keep working.** Command, HTTP, prompt, and agent hooks in settings files and in plugins' `hooks/hooks.json` run as before, alongside mods.
* **Deny rules take precedence where the guard loads.** A user's mod can't approve a call that a `deny` rule refuses, unless [`allowModsToOverrideDenyRules`](#set-options-on-the-built-in-guard) is set.
* **Managed hooks run first.** A `PreToolUse` hook in managed settings runs before any mod's [`tool.call`](https://code.claude.com/docs/en/plugins/mods/reference#tools) hook, and when that managed hook blocks a tool call, no mod's `tool.call` hook runs for that call. If the call goes ahead and a mod rewrites it, the managed hooks run again on the rewritten call, so they can still block it.

  `PreToolUse` hooks from other settings files and from plugins run after the last mod. If a mod answers the tool call itself, the tool never runs and neither do those hooks. See [The order mods run in](https://code.claude.com/docs/en/plugins/mods/events.md#the-order-mods-run-in).
* **Network policy covers `$.http.fetch`.**

  * **The organization's policy doesn't allow WebFetch**: Claude Code also refuses every mod's `$.http.fetch` request. See [WebFetch availability](https://code.claude.com/docs/en/tools-reference.md#webfetch-availability).
  * **The WebFetch tool is turned off with [`CLAUDE_CODE_DISABLE_WEB_FETCH`](https://code.claude.com/docs/en/env-vars#variables) or a `WebFetch` [deny rule](https://code.claude.com/docs/en/permissions.md#tool-specific-permission-rules), in managed settings or any other settings file**: mods can still make `$.http.fetch` requests.

  * **[`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`](https://code.claude.com/docs/en/env-vars) is set**: a mod that the organization or its users install can still make these requests. The variable stops only the [mods built into Claude Code](https://code.claude.com/docs/en/plugins/mods/overview.md#mods-built-into-claude-code), plus any `$.http.fetch` request that carries the session's Anthropic credentials. Before v2.1.288, the variable stopped every mod's `$.http.fetch` request.

  None of these covers a program the mod starts with `$.process.run`, which reaches the network with the user's own access.
* **Plugin controls cover mods.** A mod is a plugin, so the [settings that restrict what users can install](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install), such as `strictKnownMarketplaces`, decide whether it can be installed at all.
* **Mods can't change the permission prompt.** A mod can restyle much of Claude Code's interface, but not the permission prompt, so it can't change what a prompt shows. A mod can still approve or deny a tool call before the prompt appears, as [Know what happens by default](#know-what-happens-by-default) describes.
* **Trust prompts come first.** In an interactive session in a directory the user hasn't trusted yet, no mod loads until the user answers the trust prompt.
* **`--safe-mode` turns installed mods off, the organization's included.** To check whether a mod caused a problem, start a session with `claude --safe-mode`.

None of these controls sandboxes a mod. An allowed mod runs as the user, with the user's access to files, processes, and the network.

### Know which hooks of a user's mod don't run

Where the [built-in guard](#know-what-happens-by-default) loads, a hook that a user's mod registers on one of these events never runs, and `/plugin` tells that user so in a note. In the [`session.append`](https://code.claude.com/docs/en/plugins/mods/reference#session) rows, `door` is the kind of stored row the hook is filtered to.

| Hook on | What the event is |
| :- | :- |
| [`classic.<Event>`](https://code.claude.com/docs/en/plugins/mods/events#hook-the-settings-hook-events), such as `classic.Stop` | A [settings hook event](https://code.claude.com/docs/en/hooks.md#hook-events) |
| [`prompt.compose`](https://code.claude.com/docs/en/plugins/mods/reference#prompts-and-what-claude-reads) | The system prompt's list of sections |
| `prompt.section` | One section of the system prompt |
| `prompt.context` | The context sent with a conversation's first message |
| `prompt.attachment` | A message Claude Code adds for Claude, such as a reminder |
| `skill.prompt` | A skill's text as it's expanded for Claude |
| `attribution.text` | Commit or pull request attribution text |
| [`session.compact`](https://code.claude.com/docs/en/plugins/mods/reference#session) | A compaction of the conversation |
| `settings.read` | A read of settings, such as a mod's `$.settings.read` call |
| `session.append{door=attachment}` | The stored row for a message Claude Code adds for Claude |
| `session.append{door=hook-context}` | The stored row for context from a settings hook |
| `session.append{door=compaction}` | The stored rows for a compaction's summary and boundary |

The guard also passes over a user's hooks in some other cases, such as the descriptions of the organization's tools, on [`tool.describe`](https://code.claude.com/docs/en/plugins/mods/reference#tools), and the stored row for a skill's text. `/plugin` shows no note for those. If a hook on another event does nothing, see [Find out why a mod does nothing](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md#find-out-why-a-mod-does-nothing).

The note appears in the plugin's details and in the **Errors** tab of `/plugin`. It requires Claude Code v2.1.299 or later. It names each hook from the table as the mod registered it, as in this example:

```text theme={null}
Its hooks on classic.Stop, prompt.section do not run here: where an organization manages Claude Code, these events pass over the plugins you install
Only a plugin that counts as your organization's own runs hooks on these events. An administrator sets that up in managed settings
```

A `session.append` hook with no `door` filter still runs and gets no note, but the stored rows in the table don't reach it.

## Decide whether to leave mods on

A mod can do more than the other parts of a plugin because it runs inside Claude Code. It sees every prompt and tool call, can change them, and can allow or deny a tool call before a permission prompt appears.

What a user can load as a mod depends on the organization's existing plugin controls:

| Your plugin controls today | What a user can load as a mod |
| :- | :- |
| None | A mod from any marketplace, from any directory with `--plugin-dir`, or that Claude writes during a session |
| A marketplace allowlist | A mod from the marketplaces you allow, or from any directory with `--plugin-dir`. A mod Claude writes during a session loads only when the allowlist [includes `skills-dir`](https://code.claude.com/docs/en/plugins/org#keep-skills-directory-plugins-loading). |
| A marketplace allowlist and `disableSideloadFlags` | A mod from the marketplaces you allow |

[Manage plugins for your organization](https://code.claude.com/docs/en/plugins/org.md) lists the ways a plugin loads and the setting that controls each.

### Review what a mod can do

To see what a mod is able to do without running it, run `claude plugin validate` in the shell on the plugin's directory:

```bash theme={null}
claude plugin validate ./some-mod
```

The `hooks:` and `calls:` lines in the output describe the mod's code:

```text theme={null}
  ❯ ./register.js hooks: session.start, tool.call, ui.render{component=Pane}
  ❯ ./register.js calls: $.fs.read, $.http.fetch, $.store.set, $.ui.open
```

The `hooks:` line lists the events the mod receives. The `calls:` line lists the mods API methods its code calls. The [mods API](https://code.claude.com/docs/en/plugins/mods/api.md), written `$` in a mod's code, is how a mod reaches files, processes, and the network. Claude Code refuses to load a mod that uses the mods API in a way this command can't read.

In the `calls:` line, look for these:

| Call | What it means |
| :- | :- |
| `$.fs.read`, `$.fs.write` | Reads or writes files anywhere the user can |
| `$.process.run`, `$.process.spawn` | Starts programs as the user |
| `$.http.fetch` | Makes network requests |
| `$.env.get`, `$.settings.read` | Reads environment variables and settings, which can hold API keys. An `env reads:` line in the output names each variable. |
| `$.env.set` | Sets an environment variable for Claude Code and for every command and MCP server it starts afterward, which can change what those programs run. An `env writes:` line names each variable. |
| `$.mcp.call` | Calls a tool on a connected MCP server, under the session's permission rules |
| `$.model.complete` | Uses the user's plan or API key for model calls |
| `$.prompt.submit` | Submits a prompt, and can send it as the user's own words |
| `$.session.send` | Sends a message that another session's, subagent's, or [teammate's](https://code.claude.com/docs/en/agent-teams.md) Claude reads |

In the `hooks:` line, these entries matter:

* [`tool.call`](https://code.claude.com/docs/en/plugins/mods/reference#tools) and [`prompt.submit`](https://code.claude.com/docs/en/plugins/mods/reference#prompts-and-what-claude-reads): the mod sees every tool call and every prompt, and can change them.
* [`session.append`](https://code.claude.com/docs/en/plugins/mods/reference#session): the mod can rewrite each row of the conversation before it's stored, apart from [the rows the guard passes over](#hooks-the-guard-passes-over).
* [`ui.render{component=AskUserQuestion}`](https://code.claude.com/docs/en/plugins/mods/interface#change-what-claude-code-already-draws): the mod can redraw the dialog Claude uses to ask the user a question.
* `tool.check`: the mod can approve or deny a tool call before a permission prompt appears. [Know what happens by default](#know-what-happens-by-default) lists which rules and hooks take precedence over its answer.

## Choose how much to allow

Mod policies range from no installed mods at all to any mod a user chooses, with the organization's own mod checking the others, and each policy is a few managed settings. Find the wanted policy in the first column and set what the second column names. [Deploy managed settings](https://code.claude.com/docs/en/managed-settings.md) covers where managed settings live.

| What you want | Settings |
| :- | :- |
| No installed mod runs, with settings hooks untouched | Set [`allowManagedModsOnly`](#set-options-on-the-built-in-guard) and deploy no mods of your own |
| No installed mods and no hooks at all, your managed hooks included | Set `disableAllHooks` to `true` |
| Only your organization's mods | Set the guard's [`allowManagedModsOnly` option](#stop-user-installed-mods-from-loading), and [install your mods](#install-your-organizations-mods) so that they count as yours |
| Any mod from marketplaces you approve | Keep your [marketplace restrictions](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install), and set `disableSideloadFlags` to `true` |
| Any mod, with your own mod checking the others | [Install your mod](#install-your-organizations-mods), and list it with `sec-default@builtin` in `prependPlugins` |

What each setting does:

* **`allowManagedModsOnly`**: an option on the built-in guard. Claude Code refuses users' own mods, so none of their hooks run. Users' settings hooks, status lines, and `/goal` keep working. [Stop user-installed mods from loading](#stop-user-installed-mods-from-loading) lists what it covers.
* **`allowManagedHooksOnly`**: a wider setting. Only [the organization's mods](#install-your-organizations-mods) and the mods built into Claude Code load. A mod a user installed themselves doesn't. The setting also blocks hooks in users' own settings files. Read [What runs under `allowManagedHooksOnly`](https://code.claude.com/docs/en/settings-reference#what-runs-under-allowmanagedhooksonly) before setting it.
* **`disableAllHooks`**: the widest setting. In managed settings, it stops the mods in every installed plugin, the organization's included, and turns off every hook in settings files, so a `PreToolUse` hook in managed settings no longer blocks anything. Custom status lines and `/goal` stop working too. Read [`disableAllHooks`](https://code.claude.com/docs/en/settings-reference#disableallhooks) before setting it.
* **`disableSideloadFlags`**: rejects `--plugin-dir` and `--plugin-url` at startup, and keeps mods Claude writes during a session from loading. The setting also rejects `--agents` and `--mcp-config`. Read [`disableSideloadFlags`](https://code.claude.com/docs/en/settings-reference#disablesideloadflags) before setting it.

Mods built into Claude Code, such as `AGENTS.md` support, aren't affected by these settings. Each has [its own switch](https://code.claude.com/docs/en/plugins/mods/overview.md#mods-built-into-claude-code).

A user whose mod was refused or didn't load finds the reason in their debug log. [Refusal messages](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md#refusal-messages) lists the lines for `allowManagedHooksOnly` and `disableAllHooks`, and [Messages from the built-in guard](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md#messages-from-the-built-in-guard) has the line for `allowManagedModsOnly`.

### Set options on the built-in guard

The built-in guard takes options. Set them in managed settings under `pluginConfigs`, keyed by `cc-plugin-sec-default@builtin`, as the example in [Stop user-installed mods from loading](#stop-user-installed-mods-from-loading) does.

The table gives what users get with each option unset and with it set to `true`:

| Option | Unset | `true` |
| :- | :- | :- |
| `allowManagedModsOnly` | Users' own mods run | Only [your organization's mods](#install-your-organizations-mods), and mods built into Claude Code, run their hooks. Claude Code refuses every other mod, including one a user installed or named with `--plugin-dir`. |
| `allowModsToOverrideDenyRules` | Deny rules take precedence over users' mods | A user's mod that approves tool calls can approve a call that a `deny` rule refuses |

These rules decide whether an option takes effect:

* **The id has one form here**: Claude Code reads the options only under `cc-plugin-sec-default@builtin`. `prependPlugins` accepts `sec-default@builtin` as well; `pluginConfigs` doesn't.
* **Only managed settings count**: the same entry in a user, project, or local settings file, or in a file passed with `--settings`, neither sets an option nor loosens one.
* **The guard has to load**: if `prependPlugins` is set, [name the guard in the list](#install-your-organizations-mods). Where the guard doesn't load, neither option applies.
* **The guard fails closed**: if the guard can't read managed settings, it refuses every user's mod at load. If it can't check the deny rules for a call that a user's mod approved, it refuses the call.

The [messages from the built-in guard](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md#messages-from-the-built-in-guard) are what users see when either option applies.

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/mods/admin — the full official page, including the sections this copy omits (installing the organization's mods, enforcing a policy with a mod of the organization's own).
- https://code.claude.com/docs/en/plugins/mods/overview.md — what a mod is, how it compares to hooks, skills, and MCP servers, and the switches for built-in mods.
- https://code.claude.com/docs/en/managed-settings.md — where managed settings live and how to deploy them.
- https://code.claude.com/docs/en/plugins/mods/create.md — creating a mod, including asking Claude for one.
- https://code.claude.com/docs/en/server-managed-settings.md — server-managed settings and their platform availability.
- https://code.claude.com/docs/en/hooks.md — settings hooks and the hook events.
- https://code.claude.com/docs/en/authentication — authentication precedence and long-lived tokens.
- https://code.claude.com/docs/en/plugins/mods/api — the mods API (`$`), including files, processes, and the network.
- https://code.claude.com/docs/en/permission-modes.md — permission modes, including auto mode.
- https://code.claude.com/docs/en/cli-reference — CLI flags such as `--permission-prompt-tool`.
- https://code.claude.com/docs/en/agent-sdk/user-input — handling tool approval requests with `canUseTool`.
- https://code.claude.com/docs/en/permissions.md — permission rules and precedence among rules, hooks, and mods.
- https://github.com/anthropics/claude-code/tree/main/mods/sec-default — the built-in guard's public source.
- https://code.claude.com/docs/en/plugins/mods/reference — mods reference: events such as `tool.call`, `session.append`, prompts, and the settings and environment variables table.
- https://code.claude.com/docs/en/plugins/mods/events.md — mod events, settings hook events, and the order mods run in (`prependPlugins`, `appendPlugins`).
- https://code.claude.com/docs/en/tools-reference.md — WebFetch availability.
- https://code.claude.com/docs/en/env-vars — environment variables such as `CLAUDE_CODE_DISABLE_WEB_FETCH` and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`.
- https://code.claude.com/docs/en/plugins/org.md — managing plugins for an organization, install restrictions, and keeping skills-directory plugins loading.
- https://code.claude.com/docs/en/plugins/mods/troubleshoot.md — why a mod does nothing, refusal messages, and messages from the built-in guard.
- https://code.claude.com/docs/en/agent-teams.md — agent teams and teammates.
- https://code.claude.com/docs/en/plugins/mods/interface — changing what Claude Code already draws.
- https://code.claude.com/docs/en/settings-reference — `allowManagedHooksOnly`, `disableAllHooks`, and `disableSideloadFlags`.
- https://code.claude.com/docs/en/plugins/security.md — what any plugin can do on a user's machine, and how to review one before it's installed.
- https://code.claude.com/docs/en/plugins/mods/reference.md — settings and environment variables named on this page, in one table.
