# Audit brief: Cold executor

Skill: <absolute path>
Origin: <origin> · Surfaces it reaches: <list>
Claude Code release: <the user's version, from claude --version, or "unknown">
Profile: <each profile question with its answer>

## Inventory
Read every file below from its first line to its last.
<relative path> · <lines> · <executable: yes | no>

## Task
<one realistic task, and where it came from: the skill's evals when they exist, otherwise the user's request or the skill's main workflow>
Follow ${CLAUDE_PLUGIN_ROOT}/skills/skills-best-practices/references/executability-trace.md on this task, on every workflow and every variant that changes the output.

## Return
Return the report template in your agent file, filled exactly, and complete its self-check before returning.
