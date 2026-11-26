# Changelog

All notable changes to **Instruction Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.3] - 2026-11-26

### Fixed

- The loading reference was checked again against the current Claude Code docs and changelog, and it now names that version in one place: the skill, the reviewer agent and the checker point to it instead of repeating older versions.
- The loading reference now says that `--add-dir` with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` loads no rule that sets `paths`, and that Markdown files in agent-memory folders are exempt from the protected-path prompt only in a session started without `--restricted`.

## [0.2.2] - 2026-11-19

### Changed

- The `reviewer` agent's instructions now open with its role, its expertise and a goal that sums up its existing rules, and mark each section with a plain label instead of a Markdown heading. Its checks and its report are unchanged.

## [0.2.1] - 2026-11-18

### Fixed

- The `reviewer` agent can now check loader facts in the current Claude Code docs through your session's docs server: it no longer lists its tools, so it inherits your MCP tools, and it still can't edit files, start other agents, publish artifacts or enter worktrees.

## [0.2.0] - 2026-11-18

### Changed

- **Breaking:** the `claude-md-and-rules` skill is now `cc-md-and-rules`, because claude.ai and the Claude API reject a skill name that contains `claude`. Anyone who runs `/instruction-engineering:claude-md-and-rules` must run `/instruction-engineering:cc-md-and-rules` instead. What the skill does is unchanged, and the reviewer agent reads its files from the new folder.

## [0.1.5] - 2026-11-15

### Fixed

- `claude-md-and-rules` now explains where the checker script lives in plain words; the sentence that named the skill's folder placeholder read as a bare folder path once Claude Code filled it in.

## [0.1.4] - 2026-11-15

### Fixed

- The checker now matches a rule's `paths` the way Claude Code documents them. A leading `/` anchors a pattern to the folder that holds `.claude/`: `/package.json` matches only the root file. Before, the checker reported such a pattern as matching no file and said the rule never loads through it. A pattern with no `/`, such as `*.md`, matches at any depth: before, the checker treated it as matching only the root. The skill's references teach the same rules, and the plugin now ships tests for them.

## [0.1.3] - 2026-11-06

### Changed

- The plugin's description now names the tools and terms people type when they search for a plugin like this one in `/plugin`, which matches only the plugin's name, display name and description. Nothing changes in how the plugin works.

## [0.1.2] - 2026-11-05

### Added

- A listing icon and links to this README, the issue forms and the marketplace's privacy policy, which Anthropic's plugin directory shows on the plugin's page. Claude Code ignores these fields when it loads the plugin, so nothing changes in how it works.

## [0.1.1] - 2026-11-02

### Changed

- The plugin's keywords now name what it works on: `claude-md`, `rules`, `instructions`, `memory` and `audit`.
- The README states why Claude Code 2.1.271 is the minimum.

### Fixed

- The changelog describes what 0.1.0 shipped.

## [0.1.0] - 2026-10-28

### Added

- `instruction-engineering:claude-md-and-rules` skill: writes, edits, reviews, audits, debugs and refactors `CLAUDE.md`, `CLAUDE.local.md` and `.claude/rules` files at user and project scope against Claude Code's current loading rules. It checks every change against the whole instruction set, finds contradictions, duplicates, ambiguous and misplaced lines, and says when a line belongs in a path-scoped rule, a skill or a hook instead.
- A read-only checker, `check_instructions.py`, that the skill runs with `python3` 3.12 or later: it inventories the instruction files at project and user scope and reports frontmatter problems, path globs that match nothing, imports that do not resolve, duplicate lines and size limits. It never edits, runs or uploads anything.
- `instruction-engineering:reviewer` agent: an independent, read-only reviewer that audits a large instruction set, a refactor or proposed changes in its own context, without loading your `CLAUDE.md` files.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/instruction-engineering--v0.2.3...HEAD
[0.2.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.2.3
[0.2.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.2.2
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.2.0
[0.1.5]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.1.5
[0.1.4]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.1.4
[0.1.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.1.3
[0.1.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.1.2
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.1.0
