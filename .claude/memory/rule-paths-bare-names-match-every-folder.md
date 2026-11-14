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

The `instruction-engineering` checker (plugin 0.1.3) still assumes the opposite. It reports `/`-anchored patterns as `glob-no-match` and `glob-leading-slash`, and its references say `*.md` is root-only.

**Why:** bare root names made `npm-and-uv.md` load for `plugins/tailwind-development/package.json`, and made `plugins.md` and `categories.md` load for `.claude/references/README.md`.

**How to apply:** anchor root files with `/` in rule `paths`. Check scoping with an InstructionsLoaded trace (`claude -p --settings <hook json>`, which reads `trigger_file_path`), not with the checker's `--match` for anchored patterns. Related: [[research-claude-code-with-the-project-skills]].
