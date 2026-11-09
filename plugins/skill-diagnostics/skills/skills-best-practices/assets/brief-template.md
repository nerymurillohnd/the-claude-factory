# Audit brief: <agent name>

Skill: <absolute path>
Origin: <origin> · Surfaces it reaches: <list>
Claude Code release: <the user's version, from claude --version, or "unknown">
Profile: <each profile question with its answer>

## Inventory
Read every file below from its first line to its last.
<relative path> · <lines> · <executable: yes | no>

## In scope
Apply every item of ${CLAUDE_PLUGIN_ROOT}/skills/skills-best-practices/references/<lens file> to every file in the inventory.
Items you own: <checklist item IDs>

## Out of scope: don't report these
- Items owned by the other agents: <their lens files>
- Proved by the scripts:
  <check ID> · <item ID> · <pass | fail> · <file:line when it failed>

## Leads from the scripts
Confirm each one as a finding or reject it with the reason.
<check ID> · <item ID> · <file:line> · <what the script flagged>

## Return
Fill ${CLAUDE_PLUGIN_ROOT}/skills/skills-best-practices/assets/<report template> exactly, and complete its self-check before returning.

---

# Audit brief: Cold executor

Skill: <absolute path>
Origin: <origin> · Surfaces it reaches: <list>
Claude Code release: <the user's version, from claude --version, or "unknown">
Profile: <each profile question with its answer>

## Inventory
Read every file below from its first line to its last.
<relative path> · <lines> · <executable: yes | no>

## Task
<one realistic task, and where it came from: the skill's evals when they exist>
Follow ${CLAUDE_PLUGIN_ROOT}/skills/skills-best-practices/references/executability-trace.md on this task, on every workflow and every variant that changes the output.

## Return
Fill ${CLAUDE_PLUGIN_ROOT}/skills/skills-best-practices/assets/executor-report.md exactly, and complete its self-check before returning.
