# Gotchas

## Probing Claude Code behavior

- A permission probe passes falsely on the owner's machine: the owner's user settings add the home folder as a working directory, so every read under it runs without a prompt. Run each probe with `claude -p … --setting-sources project,local`, beside a negative control that must be denied.
- A read outside the working directories runs without a prompt in Manual mode while `permissions.blockReadsOutsideWorkingDirectories` is off. To prove a plugin can read a path, also run the probe with `--settings '{"permissions":{"blockReadsOutsideWorkingDirectories":true}}'`, where only Claude Code's own files stay readable.
- `claude -p` in Manual mode denies the skill invocation itself. Pass `--allowedTools 'Skill(<plugin>:<skill>)' 'Agent(<plugin>:<agent>)'` for the components the probe launches.

## Plugin paths and permissions

- A skill's `allowed-tools` grant holds only for the turn that invokes the skill, and clears on the next user message. Run the commands it pre-approves in that turn; in later turns they ask.
- `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` are substituted in skill and agent text, not exported to the Bash tool. Pass a path to a script as an argument written in that text, and resolve the plugin's own files from `Path(__file__)`.
- `${CLAUDE_SESSION_ID}` is substituted in a plugin skill's text but stays literal in an agent's. Pass a session-specific path to a subagent in its prompt.
- `${CLAUDE_PLUGIN_DATA}` is one folder per install source: `~/.claude/plugins/data/<plugin>-<marketplace>/`, `<plugin>-inline` under `--plugin-dir`, `<plugin>-synced` for a plugin synced from Claude. Data written by a `--plugin-dir` test is not what the installed copy reads, so always reach the folder through the variable.
- Claude and its subagents can read files under `${CLAUDE_PLUGIN_DATA}` even when reads outside the working directories are blocked. A script run through Bash writes there without a prompt: Claude Code checks only the targets of `>`, `>>` and `tee` against protected paths, not the files a program writes.
- Never make a plugin depend on the session scratchpad. It exists only with a claude.ai login on the Anthropic API and with `enableArtifact` on, and no skill or agent variable names it; only hooks receive it, as `scratchpad_dir`.
