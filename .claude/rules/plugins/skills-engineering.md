---
paths:
  - "plugins/skills-engineering/**"
---
# skills-engineering

## Sync points

- Add, rename or remove a reviewer in one change across `agents/<area>-reviewer.md`, `references/<area>.md`, the Reviewers list and step 6 of `SKILL.md`, its `argument-hint`, the README's components table and Usage section, and `plugin.json` where its description is affected.
- When a reference's sections are renumbered, update every section number its agent's checklist cites.
- When what a reviewer receives changes, update its Receives entry and the step 3 command in `SKILL.md`, and `.claude/maintainer/skills-engineering/mechanical-check-sources.md`.
- Change `assets/audit-report.md` only in a way every agent's REPORT section still matches.
- When the plugin starts relying on a newer Claude Code feature, raise `engines["claude-code"]` in `plugin.json` and record why in the CHANGELOG.

## Invariants

- Each audit rule has one owner: a rule two references would judge stays in one and leaves the other.
- No agent or reference names another reviewer or what another covers.
- Each agent reads only its reference and `assets/audit-report.md`, by `${CLAUDE_PLUGIN_ROOT}` paths.
- Plugin files never name the maintainer validators, their rule ids or any repository path.
- Model a new agent or reference on the existing ones: same frontmatter fields, section order and checklist groups.

## Release gate

- Don't release until the mechanical-check scripts exist under `skills/auditing-skills/scripts/`.
- Keep the skill-lint findings CO-08, CO-10, CO-12, PO-03, FM-03 and SC-03 on this plugin in suspense: report them, never fix them or record them as debt.
