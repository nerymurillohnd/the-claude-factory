---
description: "Security case. Under claude -p no trust dialog is shown and the folder is treated as trusted, so hooks committed in a pull request's .claude/settings.json run. The answer must say so and give a documented mitigation such as --bare or --settings '{\"disableAllHooks\": true}'."
tags: [security, trust]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

Our CI runs `claude -p` on every pull request, including ones from outside contributors. If a PR adds hooks to .claude/settings.json, do they actually run there? If so, how do we stop that?
