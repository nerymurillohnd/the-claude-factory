---
paths:
  - "plugins/skills-engineering/**"
---
# skills-engineering

## Sync points

- Add, rename or remove a reviewer in one change across `agents/<area>-reviewer.md`, `references/<area>.md`, its entry and Files line in the Reviewers list of `SKILL.md`, its `argument-hint`, its Receives entry in `MECHANICAL-CHECKS.md`, and `plugin.json` where its description is affected.
- When a reference's sections are renumbered, update every section number its agent's checklist cites.
- When what a reviewer receives changes, update its Receives entry and the command's entry in `MECHANICAL-CHECKS.md`, the reviewer's Files line in `SKILL.md` when a script is added, and `.claude/maintainer/skills-engineering/mechanical-check-sources.md`.
- Change `assets/audit-report.md` only in a way every agent's REPORT section still matches.
- When the plugin starts relying on a newer Claude Code feature, raise `engines["claude-code"]` in `plugin.json` and record why in the CHANGELOG.

## Invariants

- Each audit rule has one owner: a rule two references would judge stays in one and leaves the other.
- No agent or reference names another reviewer or what another covers.
- Each agent reads only its reference and `assets/audit-report.md`, by `${CLAUDE_PLUGIN_ROOT}` paths.
- `references/` holds the reviewers' references and the lookups they are given; `MECHANICAL-CHECKS.md`, at the skill root, is the main session's playbook, which no reviewer reads.
- Plugin files never name the maintainer validators, their rule ids or any repository path.

## Release gate

- Don't release until the mechanical-check scripts exist under `skills/auditing-skills/scripts/`.
