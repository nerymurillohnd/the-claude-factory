---
paths:
  - ".claude/**"
---

# Claude's project setup

- Put project settings in `settings.json`, and the scripts of its hooks in `hooks/`.
- Put a convention for one area or file type in `rules/<topic>.md` with a quoted `paths` list; anchor a root file with a leading `/`, because a pattern without `/` matches that name in every folder.
- Keep every rule file at 50 lines or fewer, frontmatter included; split a longer one by topic into its own rules.
- Point to each rule from the `CLAUDE.md` workstream it belongs to.
- Put a subagent in `agents/auditors/`, `agents/docs-maintainers/` or `agents/testers/`, and set its `model` (Sonnet for executors and simple auditors, Opus for adversarial, critical or broad reviews) and `effort`.
- Put a project skill in `skills/<skill>/`.
- Put a document template and its fill procedure in the `docs-maintenance` skill, and any other template in `templates/` with its procedure in `references/`.
- Record decisions and technical debt in `maintainer/` with the `project-maintainer:write-records` skill.
- Put specs in `maintainer/specs/`, plans in `maintainer/plans/<YYYY-MM-DD>-<topic>.md` and audit reports in `maintainer/audits/<YYYY-MM-DD>-<topic>-audit.md`.
- Write session handoffs with the `project-maintainer:write-handoff` skill.
- Put a redesign draft in `architecture/` at the path it will replace, move it there once the owner approves it, and delete `architecture/` when it is empty.
- Save each repository fact, lesson or piece of feedback in its own file in `memory/`, and add it to `memory/MEMORY.md`.
- Put dates and evidence in memory, never in instructions.
- Never save personal, client or business data, or credentials, in memory: the repository is public.
- Wait for the owner's answer when a write here asks for permission; never write here through Bash instead.
