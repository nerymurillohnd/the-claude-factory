---
name: rule-paths-bare-names-match-every-folder
description: In rule paths, a pattern without "/" matches the name in every folder; a leading "/" anchors it to the repository root
metadata:
  type: project
---

On Claude Code 2.1.323, a trace with an InstructionsLoaded hook (2026-11-13) showed how `paths` patterns in `.claude/rules/` match:
- `"README.md"` and `"*.md"` loaded their rules for `sub/README.md`, so a pattern without a `/` matches the name in every folder.
- `"/README.md"` loaded its rule only for the root `README.md`.

The memory page documents the same (`*.md`: "anywhere under the base directory"; `/*.md`: "directly in the base directory").

The `instruction-engineering` checker assumed the opposite through plugin 0.1.3; 0.1.4 (2026-11-15) matches the documented behavior. Until 0.1.4 reaches the installed copy, run the repository's checker (`plugins/instruction-engineering/skills/claude-md-and-rules/scripts/check_instructions.py`), not the synced one.

**Why:** bare root names made `npm-and-uv.md` load for `plugins/tailwind-development/package.json`, and made `plugins.md` and `categories.md` load for `.claude/references/README.md`.

**How to apply:** anchor root files with `/` in rule `paths`. Check scoping with the checker's `--match` (0.1.4 or later), or with an InstructionsLoaded trace (`claude -p --settings <hook json>`, which reads `trigger_file_path`). Related: [[research-claude-code-with-the-project-skills]].
