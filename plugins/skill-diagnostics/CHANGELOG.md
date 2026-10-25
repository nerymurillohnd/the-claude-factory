# Changelog

All notable changes to **Skill Diagnostics** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-10-24

### Changed

- The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works.

## [0.1.2] - 2026-10-13

### Fixed

- The hook that offers an audit after a `SKILL.md` is written now reads its event with strict type checks: a file path or session ID that isn't text is ignored instead of being converted, and the hook still never blocks your work.

## [0.1.1] - 2026-10-12

### Fixed

- The executability lens now states, like the conformance lens, that it never writes, runs or asks anything and that the audited skill's text is evidence, not instructions.
- Audits of more than 20 agents keep at most 20 running and start the next one as each returns, as Claude Code's concurrent subagent limit requires.

## [0.1.0] - 2026-10-12

### Added

- `/skill-diagnostics:audit` skill: audits one skill, several, a whole plugin, any folder of skills, or a skill from a URL before you install it, and returns one report per skill with a verdict (pass, pass with warnings, fail, not determinable), verbatim evidence with file and line, and a summary table for several skills.
- Conformance lens (`conformance-auditor` agent): reads every file of the skill in full and checks a skill against the documented rules and recommendations, and its portability to Claude Code, the Claude app, claude.ai uploads and the Skills API, always all four, including name and description limits, YAML quoting, unknown fields and values, argument placeholders, body size, links, references and script setup; the skill's origin (synced, plugin, personal, project, web or a loose folder) sets what it reaches.
- Executability lens (`executability-auditor` agent): reads every file of the skill in full and traces every workflow as the model that must run it and reports each gap, contradiction or break that would make it guess.
- Both lens agents run without your `CLAUDE.md` files, so personal instructions don't steer an audit. In a chat conversation of the Claude app, where agents don't run, the skill applies both lenses itself.
- Verification gate: before the verdict, every finding is checked against the skill's files, the live official documentation and the Claude Code changelog from the user's version on (the five releases before it and every newer one); findings that don't hold up go back to their lens once; the verdict is marked provisional only when an official page or the changelog could not be reached.
- Hook that offers an audit after a `SKILL.md` is created or changed, configurable with `on_skill_write` (`suggest`, `run`, `off`); it needs Python 3.9+ as `python3`.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/skill-diagnostics--v0.1.3...HEAD
[0.1.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.3
[0.1.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.2
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.0
