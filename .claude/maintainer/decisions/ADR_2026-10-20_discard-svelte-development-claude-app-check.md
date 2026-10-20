---
status: accepted
date: 2026-10-20
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The Claude app check of svelte-development 0.1.0 is discarded

## Scope

The Claude app check that `.claude/CLAUDE.md` ("Done") requires before a plugin is released, applied to `plugins/svelte-development` 0.1.0.

Out of scope: any other plugin. The rule itself is unchanged: it still applies to every plugin that is not declared Claude Code-only.

## Context and problem statement

`svelte-development` 0.1.0 was merged on 2026-10-19 (PR #22) before the Claude app check ran. Nery reported on 2026-10-20 that the plugin "works great" after installing it and working from the forestal-mt rebuild repository, which is Claude Code. The check itself never ran.

The plugin declares `metadata.surfaces` `["claude-code", "claude-app"]`, and its README says the skills and the Svelte docs server work in the Claude app, the agents only in Cowork sessions, and that the remote MCP server is connected on the plugin's Connectors tab.

Question: run the check, or drop it?

## Decision drivers

- The plugin works well in the use Nery makes of it.
- The check needs a Cowork session and a chat conversation set up for this plugin.
- `.claude/CLAUDE.md` makes the check a condition of "Done" for plugins that are not Claude Code-only.

## Considered options

- **Discard the check**: chosen.
- **Nery runs the check in the Claude app**: rejected for now; it would keep the item open until he tests Cowork and chat.
- **Declare the plugin Claude Code-only**: rejected because it changes `metadata.surfaces`, the README and the version, and the plugin is meant to work in the app.

## Decision outcome

Chosen option: **discard the check**, because Nery reported the plugin works well and chose to drop it (2026-10-20).

### Consequences

- Good, because the open item and its follow-up work end.
- Bad, because the README's claims about the Claude app stay unverified: `${CLAUDE_PLUGIN_ROOT}` in skill bodies in the app, the Connectors-tab flow for a remote server without authentication, and whether a Cowork session on a local folder can run the project check.
- Bad, because it is an exception to the "Done" rule in `.claude/CLAUDE.md`; the rule is not changed.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| A user in the Claude app hits a failure the check would have found | A user installs the plugin in the app | A broken skill or connector for that user | A user report or issue reopens the check | Nery Samuel Murillo |

## More information

The decision was made in the conversation of 2026-10-20. See also ADR_2026-10-20_svelte-agents-bash-limited-by-instructions, decided at the same time for the same plugin.
