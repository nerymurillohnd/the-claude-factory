# Changelog

All notable changes to **Skills Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- `authoring-skills` now loads `plugin-engineering:test-and-evals` for the evals of a skill in a plugin, which replaces `plugin-testing-and-debugging`.

## [0.4.1] - 2026-11-23

### Fixed

- `authoring-skills` now tells Claude to convert backslashes to forward slashes in every path a skill's script reads from Claude Code, such as a hook's file path, before comparing it: on Windows that path arrives with backslashes even under Git Bash. Its scripts guidance now matches what `auditing-skills` already checks.

## [0.4.0] - 2026-11-23

### Added

- A new check, `frontmatter.keys`, reports a frontmatter key Claude Code doesn't recognize and ignores without a word, with the field you most likely meant, such as `allowed-tools` for `tools`. It also reports keys outside the six fields of the Agent Skills specification, and a byte-order mark or CRLF line ends, which skill uploads reject.
- A `SessionEnd` hook removes the skill checks' results of a session when it ends, unless it ends to resume, as `/resume` and `/branch` end it, and any left older than 24 hours. It starts nothing when no results exist, prints nothing, and never stops a session from ending; an unexpected error goes to one line of `session-end.log` in the plugin's data folder.
- `authoring-skills` now runs the same checks on the skill it writes, in its self-review, and fixes what they find before it calls the skill done. It fixes only the findings that matter where the skill runs: a plugin skill keeps a valid Claude Code field such as `argument-hint`.

### Changed

- **Breaking:** `auditing-skills` no longer pastes every reviewer's full report into the conversation. Each reviewer writes its report to `.claude/skill-audits/<skill name>/<date and time>/<reviewer name>.md` in your project, and the audit shows you every critical, high and medium finding with its evidence and fix, where to start, and the path of each report for the low findings and improvements. Claude Code asks you to approve writes to `.claude/`; where it can't, the reports appear in the conversation as before. Reviewers may use Write only for their own report and never change the skill they audit.
- Both skills now share one checks script, `scripts/skill-checks.py`, at the plugin's root. `--help` lists every check and the exit codes, `check --help` works, and an unknown check name lists the valid ones.
- The skill checks write their results to the plugin's data folder, one folder per session, instead of your temporary folder, and never to your project. The reviewers that receive them read them there, instead of a copy in their prompt.
- `auditing-skills` runs the frontmatter checks as soon as you ask for an audit, before it asks you to confirm the reviewers, so they run without a permission prompt.
- The frontmatter checks need only Python 3.12 or later; they no longer need the `claude` command.

### Fixed

- A `description` that is 1,024 characters long plus the final newline of a `|` block is no longer reported as too long for uploads, which strip that newline first.
- `<` and `>` in `when_to_use` are now reported, since Claude Code shows them escaped there too, even when `description` is missing.
- A `name`, `description` or `compatibility` such as `n` or `1e3` is no longer reported as a non-string, since uploads read it as text, and a value uploads do type, such as `5`, is reported for uploads only.
- A specification field whose value reads as a boolean or null, such as `description: yes`, is now reported for uploads only, since the open specification's validator reads it as text, and a value uploads also keep as text, such as `yEs`, is no longer reported.
- A key such as `Tools` or `Version` now gets the same suggestion as `tools` or `version`, whatever its case.
- A name with a character that the open specification's validator turns into a capital, such as `ℌ`, is now reported for the open specification too.
- A SKILL.md path that isn't a regular file, or a SKILL.md that can't be read while the checks run, now stops the checks with one line naming the file, instead of hanging or failing with a traceback.
- `metadata` values such as `y`, `n` and `1e3` are no longer reported as non-strings: the upload validator reads them as text. A value it does type, such as `1.0` or `yes`, is now reported for uploads only.
- A lowercase name written in another alphabet is now reported for uploads only, since the open specification accepts it.
- Findings on Claude Code fields such as `argument-hint` no longer claim to break uploads or the open specification.
- A value that starts with `-` is now reported as a convention, not as an error, since YAML parsers read it as text.

## [0.3.1] - 2026-11-21

### Changed

- `authoring-skills` no longer tells the skills it writes to install nothing globally. Where a script's dependencies go is left to the skill's own design and its users' permissions.
- `auditing-skills` no longer flags a script that installs packages globally on the user's machine.

## [0.3.0] - 2026-11-19

### Changed

- **Breaking:** when you ask for a review without naming reviewers, `auditing-skills` now picks the reviewers your request is about, such as only `frontmatter-description` for a question about a skill's description or why Claude never uses it, instead of launching all nine. It tells you which reviewers it chose and why, and waits for your confirmation before it launches them. A general audit still runs every reviewer. Name the reviewers, or ask for a full audit, to choose them yourself.
- `auditing-skills` can now audit several skills in one request, running its workflow once per skill with the reviewers you confirmed for each.
- The `auditing-skills` description now leads with the words of a review request and the symptoms of a skill that misbehaves, such as a skill Claude never uses, so Claude loads it for those requests.

## [0.2.0] - 2026-11-19

### Added

- `authoring-skills` now researches the domain of the skill you ask for before it designs it: it reviews the code, data or documents the skill will act on, and reads the official sources of every technology, standard or platform the skill uses, at the version you run.
- `authoring-skills` now presents its design as a document you approve, from a template, and updates it and shows it again in full after each of your corrections, so the plan starts from what you approved and not from memory of the conversation.
- In Claude Code, `authoring-skills` now writes its plan in plan mode, so the plan only goes ahead once you approve it.

### Changed

- `authoring-skills` is rebuilt in seven phases, each with a clear end: your intent, the design, the plan, the build, a self-review, a report with a question, and an audit or evals. Each topic it teaches sits in its own reference file, which it reads at the step that needs it.
- The skills `authoring-skills` writes now follow current Agent Skills best practices: steps with a working example instead of exhaustive coverage, one default instead of a menu, checklists, validation loops with a stop, plan-validate-execute for batch or risky work, and gotchas written as the trap and its fix.
- After it builds a skill, `authoring-skills` reviews it from Claude's seat, then asks how to go on, with no option preselected: keep it, run `auditing-skills`, build evals, or anything else. It checks each audit finding with you before applying it, and asks again until you keep the skill.
- `authoring-skills` never writes a credential's value into a skill: it names each credential by its environment variable, and pushes back when you ask it to include a value.
- In Claude Code, the commands in the skills `authoring-skills` writes reach their scripts with the skill's folder variable, so they work wherever the session's working folder is; links between the skill's files stay relative.

- The reviewers no longer forbid themselves to run or measure anything; they take the mechanical results from the audit and keep strictly to auditing, treating any change to your files as a serious defect of the audit.
- The nine reviewers now keep only their model, effort level and denied tools in their settings: they load your `CLAUDE.md` files like any subagent and have no turn limit or color of their own.
- The nine `auditing-skills` reviewers no longer list their tools: each inherits every tool your session has, MCP tools included, except `Agent`, `Edit` and `Write`, so it reaches your Claude Code docs server whatever its name. Before, they listed one docs server name, and a session whose server had another name gave them none of its tools.
- `authoring-skills` now warns that a subagent running in the background keeps the Skill and ToolSearch tools and every MCP tool but only part of the built-in tools, so a skill a subagent loads names each tool it relies on and what to do without it.
- `auditing-skills` now weighs how a description states when to use the skill: an imperative "Use…" clause whose form fits how the skill is invoked ("Use when…", "Use only when…", "Use every time…"), and whether it comes first, as the Claude Code docs ask for the key use case. It sets any severity by the consequence on Claude's choice, not by the form alone, and leaves out skills that only you can invoke.
- `auditing-skills` now also checks the description of every subagent that preloads the skill or reads its files, weighing "use proactively" against how the subagent is launched. It no longer flags a base skill that is meant to load alongside its specialized siblings.
- Where official sources disagree, `auditing-skills` now follows Anthropic's own documentation first, and names the disagreement.
- `authoring-skills` writes descriptions by the same points: a "Use…" clause fitted to the skill, opening the description when the trigger is what tells the skill apart.
- The `comprehension` reviewer now checks how a skill that works in phases organizes its files: it flags a reference that holds rules for more than one phase, so one phase's rules arrive late or never, and a phase that reads several files without saying in which order, and suggests putting the phase in each phase-specific file's name. Each finding comes with the split or the ordered list to apply.

## [0.1.0] - 2026-11-18

### Added

- Initial release. Requires Claude Code 2.1.304 or later: from that release, a subagent that Claude messages right after it finishes keeps its latest work, which the audit relies on when it sends a reviewer back to complete its report.
- Added the `auditing-skills` skill. It audits a skill with specialized reviewer agents, each on its own domain. Before they start, it checks the skill's frontmatter for problems `claude plugin validate` doesn't report. These checks need Python 3.12 or later; without it, the reviewers are told the checks didn't run. When it loads right after you create or edit a skill without asking for an audit, it asks you first, and runs only the reviewers you agree to.
- Added the `authoring-skills` skill. It writes new skills and changes existing ones, wherever a skill lives: personal, project, plugin, claude.ai, the Skills API and subagents. It first learns your environment, your goal and the skills you already have, asks you only for context, and shows you a plan to approve. Then it builds the skill from the current official docs, reviews it the way Claude will read it, and reports what it checked and what it could not. At the end it offers to keep the skill as it is, take your observations, build evals, or run `auditing-skills` on it when that skill is installed.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/skills-engineering--v0.4.1...HEAD
[0.4.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.4.1
[0.4.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.4.0
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.3.0
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.1.0
