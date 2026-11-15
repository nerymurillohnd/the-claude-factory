---
paths:
  - "scripts/validators/skill-lint.py"
  - "scripts/validators/skill_lint/**"
  - "scripts/testers/skill_lint/**"
---

# skill-lint

- Check a rule against `.claude/maintainer/specs/skill-lint-spec.md` before changing it, and update the spec in the same commit.
- Keep `scripts/validators/skill-lint.py` a shim that only puts `scripts/` on the import path and runs `validators.skill_lint.cli`.
- Keep the discovery globs `plugins/*/skills/*/SKILL.md` and `.claude/skills/*/SKILL.md`, and `PRUNED_DIRS` equal to the spec's Discovery section.
- Raise `GitError` for any git failure other than a missing git or a folder outside a repository.
- Build every `Finding` from its module's `SOURCES` map.
- Read only files inside the skill folder, and never write to a skill.
- Read parsed Markdown from `skill.markdown`, never call `parse_markdown` in a rule module, and build one `Resolver` per check.
- Build test skills in a `tempfile.TemporaryDirectory` with the helpers in `scripts/testers/skill_lint/helpers.py`; never commit fixture skills.
- Split a module past about 250 lines by responsibility.
