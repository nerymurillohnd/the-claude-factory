# Changelog

All notable changes to **Skills Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release. Requires Claude Code 2.1.304 or later: from that release, a subagent that Claude messages right after it finishes keeps its latest work, which the audit relies on when it sends a reviewer back to complete its report.
- Added the `auditing-skills` skill. It audits a skill with specialized reviewer agents, each on its own domain. Before they start, it checks the skill's frontmatter for problems `claude plugin validate` doesn't report. These checks need Python 3.12 or later; without it, the reviewers are told the checks didn't run.
- Added the `authoring-skills` skill. It writes new skills and changes existing ones, for every kind of skill and every place a skill lives: personal, project, plugin, claude.ai, the Skills API and subagents. It first learns your environment, your goal and the skills you already have, asks only for context, and shows you a plan to approve. Then it builds the skill from the current official docs, tests it in a fresh session, and reports what it checked and what it could not. It works on its own; when `auditing-skills` is installed, it offers an audit as one of the next steps.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/commits/main/plugins/skills-engineering
