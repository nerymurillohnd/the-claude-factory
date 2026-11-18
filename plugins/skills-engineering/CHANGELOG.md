# Changelog

All notable changes to **Skills Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release. Requires Claude Code 2.1.304 or later: from that release, a subagent that Claude messages right after it finishes keeps its latest work, which the audit relies on when it sends a reviewer back to complete its report.
- Added the `auditing-skills` skill. It audits a skill with specialized reviewer agents, each on its own domain. Before they start, it checks the skill's frontmatter for problems `claude plugin validate` doesn't report. These checks need Python 3.12 or later; without it, the reviewers are told the checks didn't run. When it loads right after you create or edit a skill without asking for an audit, it asks you first, and runs only the reviewers you agree to.
- Added the `authoring-skills` skill. It writes new skills and changes existing ones, wherever a skill lives: personal, project, plugin, claude.ai, the Skills API and subagents. It first learns your environment, your goal and the skills you already have, asks you only for context, and shows you a plan to approve. Then it builds the skill from the current official docs, reviews it the way Claude will read it, and reports what it checked and what it could not. At the end it offers to keep the skill as it is, take your observations, build evals, or run `auditing-skills` on it when that skill is installed.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/commits/main/plugins/skills-engineering
