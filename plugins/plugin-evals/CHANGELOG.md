# Changelog

All notable changes to **Plugin Evals** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-14

### Added

- Skill `plugin-evals`: loads whenever a task involves Claude Code plugin evals, and checks every time-sensitive fact against the installed `claude` CLI, the live docs and the changelog before using it.
- A method for suites whose score means something: cases that prove a difference, an outcome and a process grader per case, triggering measured as a rate, tools that match the graders, a one-run pilot, and a cost check before every paid run. CI commands always carry pinned agent and judge models, a cost ceiling, the threshold and trust inside the command.
- References for the case format and graders, fixtures and MCP mocks, running and CI (targets, options, tool grants and the OS sandbox, trust, credentials, exit codes), reading results and troubleshooting, and other eval formats (skill-creator's `evals.json`, `/claude-api build-eval`), written against Claude Code v2.1.299.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/plugin-evals--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-evals--v0.1.0
