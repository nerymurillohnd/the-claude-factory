# Real requests against the installed copy

Read when the user agreed to real requests in step 7, after step 8 signed in.

These runs isolate the configuration, not the home folder: unlike an eval run, they can see the user's files and environment.

1. Put in `<target>` whatever the requests need, such as a small sample project or file. Never copy the user's real project.
2. Take the requests from the plugin's README usage examples. If it has none, propose one to three realistic requests from the skills' descriptions and confirm them with the user. Run each request twice: as the slash command (`/<name>:<skill> …`) and as a natural request that doesn't name the skill.
3. Run each request, with the prompt right after `-p`, because `--allowedTools` takes several values and would read a prompt placed after it as a tool:

   ```bash
   cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude -p "<request>" --output-format json \
     --permission-mode dontAsk --allowedTools "<grant>,<grant>"
   ```

   - `<grant>,<grant>` is one quoted, comma-separated list, such as `"Skill,Read,Edit,Bash(npm test *),WebFetch(domain:example.com)"`.
   - `Skill` must be among the grants for a natural request to reach a skill.
   - `--permission-mode dontAsk` denies anything that would prompt, instead of leaving the run to a default mode. In auto mode, a bare `Bash` grant is dropped (docs: <https://code.claude.com/docs/en/headless>).
4. Report for each request: the `result` text, every entry in `permission_denials`, `total_cost_usd`, and which of the plugin's components ran (skill, agents, hooks). Re-run with `--output-format stream-json --verbose` when you need the tool calls to tell.

To watch an interactive session instead, the user runs `cd <target> && CLAUDE_CONFIG_DIR=<cfg> claude` in a separate terminal. Wait until they say they are done before cleaning up.
