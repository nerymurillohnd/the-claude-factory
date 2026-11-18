# Phase 2: Components

Decide what the skill does when a server or a skill it relies on is missing, which skills it may rely on, and where its configuration and state live.

## MCP tools

- Say what to do when the server isn't connected: tell the user what to connect and stop, or fall back to a stated alternative.

## Other skills

- The other skill must not set `disable-model-invocation: true`: neither the model nor another skill can load a skill that sets it.
- When the other skill may be missing, say what to do without it. A skill for third parties works on its own, with other skills as optional help.

## Configuration and state

Keep the config and any state where updates don't erase them:

- **Plugin skill**: the plugin's data folder, which `SKILL.md` reaches as `CLAUDE_PLUGIN_DATA` in a dollar sign and braces; Claude Code replaces it with the path. The plugin's install folder is replaced on every update.
- **Personal or project skill**: the skill's folder, or the project when the state belongs to it, kept out of version control if private.
- **claude.ai or the API**: don't rely on files from an earlier conversation; design the skill to work without saved state.

For a history the skill learns from, such as earlier reports, append to a log in the same place and say when the model reads it.
