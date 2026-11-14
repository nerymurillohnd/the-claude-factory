# Changelog

All notable changes to **Skill Diagnostics** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2026-11-14

### Fixed

- The gate no longer asks Claude to audit skills nobody changed. After you cloned a repository, checked out a branch or pulled during a session, every skill in it had new file times and the gate asked for an audit of each one. Inside a Git repository, a skill now counts as changed only when Git lists a file in it as modified, untracked or staged, or when a commit made in the session touches it. Outside Git, file times decide as before.
- A pending skill that Git shows unchanged, such as one whose edit you reverted, is dropped instead of being asked for again.
- When a command inside the gate failed with status 2, the gate could exit with 2 and keep Claude from stopping. Every failure now exits 1, as the README states.

## [0.4.0] - 2026-11-14

### Removed

- **Breaking:** the `/skill-diagnostics:evals` workflow is gone. If you ran `/skill-diagnostics:evals <skill folder>` to measure a skill's trigger rates and output quality with and without the skill, that command no longer exists after you update. The plugin no longer ships its own eval runner. To run evals, use Claude Code's `claude plugin eval` or a skill-writing skill such as `skill-creator`. The audit still checks a skill's evals, and the plugin's README says where to run them.

## [0.3.0] - 2026-11-09

### Added

- A full audit: five validation scripts, four independent reviewers (description, instructions, scripts and runtime, security), a cold executor that follows every workflow without guessing, and an adversarial verifier that checks every finding against the official sources. It returns one report with file-and-line evidence and one verdict.
- Each audit report has an Accounting table that gives every finding of every agent one outcome (kept, merged or withdrawn). A `SubagentStop` hook, and a `PostToolUse` hook on `SubagentHandback` in auto mode, save each agent's report unchanged in the session's audit folder in the plugin's data directory, which the report names, so you can check that no finding was dropped. Claude makes no tool call to save them. Audit folders are deleted after 7 days.
- A `PermissionRequest` hook approves the skill's own six scripts, run exactly as the skill writes them, in an audit's later turns, where the skill's pre-approval has ended and Claude Code would otherwise ask you. It approves nothing else, never denies and never adds a permission rule.
- The skill checks that a skill writes every command that uses `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_PLUGIN_DATA}` in `SKILL.md`, since Claude Code doesn't substitute them in the files a skill links to.
- The skill checks that a skill's frontmatter hooks don't name `${CLAUDE_PLUGIN_DATA}`, which Claude Code refuses in a skill hook, and its references say what each placeholder and a relative path resolve to in a skill hook.
- The skill checks how a skill that runs other agents runs them (subagents, workflows, agent teams) against the official comparison, and that no pre-approved command depends on running after a subagent's result, since the skill's pre-approval covers only the turn that invokes it.
- The skill checks the size of `SKILL.md`: at most 500 lines, and a body of at most 5,000 tokens (Claude Code's figure from `claude plugin details` when the skill is in a plugin and `claude` is installed, otherwise estimated from its characters), the part Claude Code re-attaches after compaction; it flags a body above 4,500 tokens.
- The skill audits a skill's evals, when it has them, against the official eval best practices: its `evals/evals.json` (format, ids, input files, assertions) and the `claude plugin eval` cases that invoke it (graders, regex flags, must-not-invoke cases) by script, and the realism, coverage, trigger queries and direct invocations of its cases by the reviewers. Running the evals stays outside the audit.
- The skill checks a skill's name against the other skills and built-in commands it can shadow, a skill named `verify` or `simplify` (which Claude Code runs before each commit), and a skill folder that holds its own `.claude-plugin/plugin.json` and so loads its own agents, hooks and MCP servers.
- Each audit agent sets its own model and effort: the four reviewers on Sonnet and the cold executor and adversarial verifier on Opus; `xhigh` effort for the scripts-and-runtime and security reviewers and the verifier, `high` for the others.
- A gate: after Claude writes or edits a skill, it audits the skill before it finishes the turn.
- After an audit, when the skill has no evals, Claude asks whether you want some; writing them is a separate step you choose. A Stop hook also finds skills changed by shell commands.
- The `/skill-diagnostics:evals` workflow measures whether a skill triggers on the right requests and improves the output, with and without the skill. It runs only on request and changes no file of the skill.

### Changed

- **Breaking:** `/skill-diagnostics:audit` is replaced by `/skill-diagnostics:skills-best-practices`. It still only audits; to write a skill, Claude uses a skill-writing skill such as `skill-creator`.
- The plugin's and the skill's descriptions say what the audit is and when it runs: after any skill, in a plugin, user, project or local folder, is created or edited, and whenever you ask to audit, review or improve one.
- **Breaking:** `on_skill_write` now takes only `gate`, `suggest` or `off`, and the default is `gate` (it was `suggest`); set it to `suggest` to keep the old behavior. `run` is gone, and any other value is no longer accepted, so an unknown value can't silently fall back to another mode.
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

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/skill-diagnostics--v0.4.1...HEAD
[0.4.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.4.1
[0.4.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.4.0
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.3.0
[0.2.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.2.2
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.2.0
[0.1.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.3
[0.1.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.2
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skill-diagnostics--v0.1.0
