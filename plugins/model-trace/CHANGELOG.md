# Changelog

All notable changes to **Model Trace** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-28

### Added

- The Model Trace pane, opened with `/model-trace`: each skill, agent, MCP server, plugin, hook and web tool Claude uses in the session appears the first time it is used, with its count and the time of every use.
- Reports: **Save .md**, **Save .html** and **Copy Markdown** in the pane, and `/model-trace md` or `/model-trace html`, saved to the `exportDir` option's folder (`~/Downloads` by default).
- An optional status line entry with the session's count (`statusLine`, off by default).
- Requires Claude Code v2.1.299 or later. Tested with Claude Code v2.1.312.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/model-trace--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/model-trace--v0.1.0
