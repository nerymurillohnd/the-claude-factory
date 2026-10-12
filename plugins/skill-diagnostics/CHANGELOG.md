# Changelog

All notable changes to **Skill Diagnostics** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-12

### Added

- `/skill-diagnostics:audit` skill: audits one skill, several, a whole plugin, any folder of skills, or a skill from a URL before you install it, and returns one report per skill with a verdict (pass, pass with warnings, fail, not determinable), verbatim evidence with file and line, and a summary table for several skills.
- Conformance lens (`conformance-auditor` agent): reads every file of the skill in full and checks a skill against the documented rules and recommendations, and its portability to Claude Code, Cowork, claude.ai uploads and the Skills API, always all four; the skill's origin (synced, plugin, personal, project, web) sets what it reaches.
- Executability lens (`executability-auditor` agent): reads every file of the skill in full and traces every workflow as the model that must run it and reports each gap, contradiction or break that would make it guess.
- Structure checker (`check_skill.py`, Python 3.9+): name and description limits per surface, YAML quoting, unknown fields and values, argument placeholders, body size, load-time commands, reserved names, links, references and script setup; `--list` prints the skill's full file inventory for the lenses, following symlinked folders.
- Verification gate: before the verdict, every finding is checked against the skill's files, the live official documentation and the Claude Code changelog from the user's version on (the five releases before it and every newer one); findings that don't hold up go back to their lens once; the verdict is marked provisional only when an official page or the changelog could not be reached.
- Hook that offers an audit after a `SKILL.md` is created or changed, configurable with `on_skill_write` (`suggest`, `run`, `off`).

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/skill-diagnostics--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.0
