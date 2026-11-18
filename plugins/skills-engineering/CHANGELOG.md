# Changelog

All notable changes to **Skills Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-18

### Changed

- The nine `auditing-skills` reviewers no longer list their tools: each inherits every tool your session has, MCP tools included, except `Agent`, `Edit` and `Write`, so it reaches your Claude Code docs server whatever its name. Before, they listed one docs server name, and a session whose server had another name gave them none of its tools.
- `authoring-skills` now warns that a subagent running in the background keeps the Skill and ToolSearch tools and every MCP tool but only part of the built-in tools, so a skill a subagent loads names each tool it relies on and what to do without it.
- `auditing-skills` now weighs how a description states when to use the skill: an imperative "Use…" clause whose form fits how the skill is invoked ("Use when…", "Use only when…", "Use every time…"), and whether it comes first, as the Claude Code docs ask for the key use case. It sets any severity by the consequence on Claude's choice, not by the form alone, and leaves out skills that only you can invoke.
- `auditing-skills` now also checks the description of every subagent that preloads the skill or reads its files, weighing "use proactively" against how the subagent is launched. It no longer flags a base skill that is meant to load alongside its specialized siblings.
- Where official sources disagree, `auditing-skills` now follows Anthropic's own documentation first, and names the disagreement.
- `authoring-skills` writes descriptions by the same points: a "Use…" clause fitted to the skill, opening the description when the trigger is what tells the skill apart.

## [0.1.0] - 2026-11-18

### Added

- Initial release. Requires Claude Code 2.1.304 or later: from that release, a subagent that Claude messages right after it finishes keeps its latest work, which the audit relies on when it sends a reviewer back to complete its report.
- Added the `auditing-skills` skill. It audits a skill with specialized reviewer agents, each on its own domain. Before they start, it checks the skill's frontmatter for problems `claude plugin validate` doesn't report. These checks need Python 3.12 or later; without it, the reviewers are told the checks didn't run. When it loads right after you create or edit a skill without asking for an audit, it asks you first, and runs only the reviewers you agree to.
- Added the `authoring-skills` skill. It writes new skills and changes existing ones, wherever a skill lives: personal, project, plugin, claude.ai, the Skills API and subagents. It first learns your environment, your goal and the skills you already have, asks you only for context, and shows you a plan to approve. Then it builds the skill from the current official docs, reviews it the way Claude will read it, and reports what it checked and what it could not. At the end it offers to keep the skill as it is, take your observations, build evals, or run `auditing-skills` on it when that skill is installed.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/skills-engineering--v0.2.0...HEAD
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.1.0
