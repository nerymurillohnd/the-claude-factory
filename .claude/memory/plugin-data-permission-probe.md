---
name: plugin-data-permission-probe
description: Evidence behind the plugin-data and permission-probe gotchas in .claude/rules/gotchas.md (Claude Code 2.1.330)
metadata:
  node_type: memory
  type: project
  originSessionId: b427f49e-84fa-4a87-88aa-e4f8c53336e5
  modified: 2026-11-23T10:31:38.826Z
---

On 2026-11-23, Claude Code 2.1.330, a probe plugin (skill runs a script that writes to `${CLAUDE_PLUGIN_DATA}/checks/run1/out.json`, an agent whose own body names that path reads it) ran in `claude -p` Manual mode with zero permission denials, also with `--setting-sources project,local` and with `blockReadsOutsideWorkingDirectories: true`. The negative control, a file in `~/Claude/`, was denied only under the block. The first run was a false pass because user settings add the home folder to `additionalDirectories`.

A second probe the same day: `${CLAUDE_SESSION_ID}` in the skill's command became the real session id, while the agent's body kept it literal and its Read failed. A plugin `SessionEnd` command hook ran when `claude -p` exited, had `CLAUDE_PLUGIN_DATA` in its environment and the same `session_id` in its input, and deleted `checks/<session_id>`.

Unverified: whether the auto-mode first-read prompt skips the plugin data folder; whether `${CLAUDE_PLUGIN_DATA}` is substituted for an `@synced` plugin (the skills docs say a synced skill's body in a terminal session leaves `${CLAUDE_PROJECT_DIR}` and `${CLAUDE_SESSION_ID}` literal).

**Why:** the rules hold the gotchas; this file holds the evidence and the recheck point.
**How to apply:** rerun the probe after a Claude Code release that changes plugin variables, protected paths or read permissions. See [[research-claude-code-with-the-project-skills]].
