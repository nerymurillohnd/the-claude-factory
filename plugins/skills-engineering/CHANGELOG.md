# Changelog

All notable changes to **Skills Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release. Requires Claude Code 2.1.304 or later: from that release, a subagent that Claude messages right after it finishes keeps its latest work, which the audit relies on when it sends a reviewer back to complete its report.
- Added the `auditing-skills` skill. It audits a skill with nine reviewer agents, each on its own domain. Before they start, it checks the skill's frontmatter for problems `claude plugin validate` doesn't report. These checks need Python 3.12 or later; without it, the reviewers are told the checks didn't run.
- Added the `authoring-skills` skill. It writes new skills and changes existing ones, for every kind of skill and every place a skill lives. It starts from the domain's own material and the current platform docs, then hands the finished skill to `auditing-skills` for review.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/commits/main/plugins/skills-engineering
