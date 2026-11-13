# Changelog

All notable changes to **Model Trace** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- The plugin is now listed under the **Monitoring** category instead of **Mods**, with the marketplace's other observability tools. Nothing changes in how the plugin works.

## [0.1.4] - 2026-11-06

### Changed

- The plugin's description now names the tools and terms people type when they search for a plugin like this one in `/plugin`, which matches only the plugin's name, display name and description. Nothing changes in how the plugin works.

## [0.1.3] - 2026-11-05

### Added

- A listing icon and links to this README, the issue forms and the marketplace's privacy policy, which Anthropic's plugin directory shows on the plugin's page. Claude Code ignores these fields when it loads the plugin, so nothing changes in how it works.

## [0.1.2] - 2026-10-30

### Removed

- The `tsconfig.json` at the plugin's root, a development file that shipped by mistake: it pointed at type files your copy never has, and the mod never used it. Nothing changes in how the plugin works.

## [0.1.1] - 2026-10-28

### Fixed

- A row in a narrow pane, such as the desktop app's side panel, shows the capability's whole name instead of cutting it to a few letters; when the origin doesn't fit beside it, it shows in the row's details.
- A section's title now counts the same uses as the header, and names the hook output it leaves out separately, as in `2 · 2 uses · 9 output`, in the pane and in the reports.
- Tested with Claude Code v2.1.312.

## [0.1.0] - 2026-10-28

### Added

- The Model Trace pane, opened with `/model-trace`: each skill, agent, MCP server, plugin, hook and web tool Claude uses in the session appears the first time it is used, with its count and the time of every use.
- Reports: **Save .md**, **Save .html** and **Copy Markdown** in the pane, and `/model-trace md` or `/model-trace html`, saved to the `exportDir` option's folder (`~/Downloads` by default).
- An optional status line entry with the session's count (`statusLine`, off by default).
- Requires Claude Code v2.1.299 or later. Tested with Claude Code v2.1.312.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/model-trace--v0.1.4...HEAD
[0.1.4]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/model-trace--v0.1.4
[0.1.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/model-trace--v0.1.3
[0.1.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/model-trace--v0.1.2
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/model-trace--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/model-trace--v0.1.0
