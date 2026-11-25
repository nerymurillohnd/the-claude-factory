# Audit brief: <agent name>

Skill: <absolute path>
Origin: <origin> · Surfaces it reaches: <list>
Claude Code release: <the user's version, from claude --version, or "unknown">
Profile: <each profile question with its answer>

## Inventory
Read every file below from its first line to its last.
<relative path> · <lines> · <executable: yes | no>

## Evals
The skill's evals, from check-evals: read every file of each when an item you own judges evals.
<evals/evals.json, or "none"> · <the absolute path of each plugin eval case folder that names the skill, or "none">

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
