# Changelog

All notable changes to **Skill Diagnostics** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-11-09

### Added

- The `skills-best-practices` skill writes and edits skills by the official best practices, starting from a template, with a validation loop against one checklist.
- A full audit: three validation scripts, four independent reviewers (description, instructions, scripts and runtime, security), a cold executor that follows every workflow without guessing, and an adversarial verifier that checks every finding against the official sources. It returns one report with file-and-line evidence and one verdict.
- Each audit report has an Accounting table that gives every finding of every agent one outcome (kept, merged or withdrawn), and the audit saves each agent's report unchanged, with the final report, in a temporary folder the report names, so you can check that no finding was dropped.
- The skill checks that a skill writes every command that uses `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_PLUGIN_DATA}` in `SKILL.md`, since Claude Code doesn't substitute them in the files a skill links to.
- A gate: after Claude writes or edits a skill, it audits the skill before it finishes the turn. A Stop hook also finds skills changed by shell commands.
- The `/skill-diagnostics:evals` workflow measures whether a skill triggers on the right requests and improves the output, with and without the skill. It runs only on request and changes no file of the skill.

### Changed

- **Breaking:** `/skill-diagnostics:audit` is replaced by `/skill-diagnostics:skills-best-practices`, which also writes skills.
- **Breaking:** `on_skill_write` now takes only `gate`, `suggest` or `off`, and the default is `gate` (it was `suggest`). Any other value is no longer accepted, so an unknown value can't silently fall back to another mode.
- **Breaking:** the hooks now need Bash and `jq`. If `jq` is missing, the hooks report an error and don't gate. Python 3.12 or later as `python3` is still needed, now for the skill's scripts.
- **Breaking:** an audit covers one skill folder per run; auditing a skill from a URL or every skill of a plugin folder in one run is no longer offered.

### Removed

- **Breaking:** the `conformance-auditor` and `executability-auditor` agents and the Python hook, replaced by the six new agents and the Bash hooks.

## [0.2.2] - 2026-11-06

### Changed

- The plugin's description now names the tools and terms people type when they search for a plugin like this one in `/plugin`, which matches only the plugin's name, display name and description. Nothing changes in how the plugin works.

## [0.2.1] - 2026-11-05

### Added

- A listing icon and links to this README, the issue forms and the marketplace's privacy policy, which Anthropic's plugin directory shows on the plugin's page. Claude Code ignores these fields when it loads the plugin, so nothing changes in how it works.

## [0.2.0] - 2026-10-27

### Changed

- **Breaking:** the hook now requires Python 3.12 or later as `python3`, up from 3.9. Check yours with `python3 --version`; older versions are no longer supported.

### Fixed

- The hook runs as `python3` through Bash instead of relying on the script's executable bit, and on Windows it always runs through Git Bash, never PowerShell.

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

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/skill-diagnostics--v0.3.0...HEAD
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.3.0
[0.2.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.2.2
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.2.0
[0.1.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.3
[0.1.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.2
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.0
