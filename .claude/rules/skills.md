---
paths:
  - ".claude/skills/**"
  - "plugins/*/skills/**"
---

# Skills

This repository holds two kinds of skills, and they never mix:

- **Project skills,** in `.claude/skills/<skill>/`: maintainer procedures for this marketplace. They run only in this repository and never reach users.
- **Plugin skills,** in `plugins/<plugin>/skills/<skill>/`: part of a plugin, installed on users' machines and run in their projects.

## Which skill governs each task

Load the skill before starting the task.

- Plugin lifecycle, with the project skills:
  - versions and bumps: `plugin-versioning`
  - releases, tags and GitHub Releases: `plugin-releases`
  - renames, removals and merges: `plugin-catalog-changes`
  - READMEs, CHANGELOGs, licenses, notices and the policy documents: `docs-maintenance`
  - plugin directory icons: `plugin-icons`
- Maintenance, with the skills of this marketplace's own plugins:
  - ADRs and technical debt: `project-maintainer:write-records`
  - session handoffs: `project-maintainer:write-handoff`
  - CLAUDE.md and rules: `instruction-engineering:claude-md-and-rules`
  - hooks: `hook-engineering:hook-development`
  - the plugin CLI and the official plugin docs: `plugin-engineering:cli-commands-guide` and `plugin-engineering:public-marketplace-dev`
  - pull requests, workflows and GitHub files: `github-operations:auto-pr-lifecycle`, `github-operations:claude-github-actions` and `github-operations:github-files-setup`

## Project skills

- Write a project skill as a procedure that calls the maintainer scripts through `npm run`, with no scripts inside the skill folder. Put a new script in `scripts/`, as `.claude/rules/architecture/scripts.md` sets.

## Plugin skills

- Keep the scripts a plugin skill runs inside its skill folder, never in `scripts/`: users receive only `plugins/<plugin>/`, and the maintainer scripts never ship.

## Name other skills from a skill

Claude loads another skill through the Skill tool, which takes the skill's name with no leading slash; `/name` is what a user types.

- Name a project skill by its bare name in backticks: "write the entry with the `docs-maintenance` skill".
- Name a plugin skill with its plugin prefix: `project-maintainer:write-records`.
- Write `/name` only where the instruction tells the user what to type, such as `/plugin install …`.
- Never set `disable-model-invocation: true` on a skill that other skills load: Claude could no longer invoke it through the Skill tool.
- Cite the skill, never a file path inside another skill's folder: the skill knows which reference to open, and a path that leaves the skill's folder fails `npm run lint:skills` (CO-08).

## Check every skill

- After creating or changing a skill, run `npm run lint:skills -- <skill folder>`. Report each defect it finds to the owner, one question per rule id, and fix it or record it as debt only after the owner decides.
- Run the `skill-diagnostics:skills-best-practices` audit only when the owner asks for it: it starts several subagents.
