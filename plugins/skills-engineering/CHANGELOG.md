# Changelog

All notable changes to **Skills Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/skills-engineering--v0.2.0...HEAD
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.1.0
