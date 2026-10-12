# Real prompts against the installed copy

Read when the user wants to watch the plugin answer real requests, or when it has no eval suite.

These runs isolate the configuration, not the home folder: unlike an eval run, they can see the user's files and environment.

1. Put in `<target>` whatever the prompts need, such as a small sample project or file. Never copy the user's real project.
2. Take the realistic requests from the plugin's README usage examples. Run each one twice, as the slash command (`/<name>:<skill> …`) and as a natural request that doesn't name the skill. Say the number of runs first and wait for the go-ahead.
3. Run each prompt:

   ```bash
   cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude -p --output-format json \
     --permission-mode dontAsk --allowedTools <grants> "<prompt>"
   ```

   - `--permission-mode dontAsk` denies anything that would prompt, instead of leaving the run to a default mode. In auto mode, a bare `Bash` grant is dropped (docs: <https://code.claude.com/docs/en/headless>).
   - For a natural request to reach a skill, `Skill` must be among the grants.
4. Report for each prompt: the `result` text, every entry in `permission_denials`, `total_cost_usd`, and which of the plugin's components ran (skill, agents, hooks). Re-run with `--output-format stream-json --verbose` when you need the tool calls to tell.

To watch an interactive session instead, the user opens a separate terminal and runs `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude`. An interactive session can't run inside this conversation's `!` prefix. Wait until they say they are done before cleaning up.
