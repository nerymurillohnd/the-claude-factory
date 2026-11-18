# Changelog

All notable changes to **Skills Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-18

### Changed

- `auditing-skills` now reports a skill description that doesn't open with a "Use…" clause saying when to use the skill as a Medium defect. Any such clause counts, such as "Use when…", "Use for…" or "Use every time…". Skills that only you can invoke are exempt, because Claude never reads their description. It also flags a description whose key use case comes late, where Claude Code's listing can cut it.
- `auditing-skills` now applies the same rule to the description of every subagent that preloads the skill or reads its files, and no longer flags a base skill that is meant to load alongside its specialized siblings.
- `authoring-skills` writes descriptions by the same rule: any opening "Use…" clause, not only "Use when".

## [0.1.0] - 2026-11-18

### Added

- Initial release. Requires Claude Code 2.1.304 or later: from that release, a subagent that Claude messages right after it finishes keeps its latest work, which the audit relies on when it sends a reviewer back to complete its report.
- Added the `auditing-skills` skill. It audits a skill with specialized reviewer agents, each on its own domain. Before they start, it checks the skill's frontmatter for problems `claude plugin validate` doesn't report. These checks need Python 3.12 or later; without it, the reviewers are told the checks didn't run. When it loads right after you create or edit a skill without asking for an audit, it asks you first, and runs only the reviewers you agree to.
- Added the `authoring-skills` skill. It writes new skills and changes existing ones, wherever a skill lives: personal, project, plugin, claude.ai, the Skills API and subagents. It first learns your environment, your goal and the skills you already have, asks you only for context, and shows you a plan to approve. Then it builds the skill from the current official docs, reviews it the way Claude will read it, and reports what it checked and what it could not. At the end it offers to keep the skill as it is, take your observations, build evals, or run `auditing-skills` on it when that skill is installed.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/skills-engineering--v0.2.0...HEAD
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/skills-engineering--v0.1.0
