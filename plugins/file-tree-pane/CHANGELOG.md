# Changelog

All notable changes to **File Tree Pane** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-23

### Added

- The file tree pane and the `/file-tree [path]` command: a tree that follows the working directory or a pinned folder, draws only the rows on screen, and scrolls to its last row with the wheel, the scrollbar and the keys.
- Git status per file and folder in color, `+N -N` line counts, `?:N M:N D:N` folder counts, and the branch, upstream and ahead/behind in the header.
- Claude's reads and searches, writes and commits highlighted in the tree, Follow Claude, and `git` and `gh` operations in the footer.
- The selected file or folder passed to Claude with each prompt while the pane is on screen, and `@path` mentions revealed in the tree.
- Search over folders never opened, previews, diffs in the pane, sizes with folder disk usage, Quick Look on macOS, and opening files in their default app (never one that app would run), an editor in tmux or herdr, or your own commands.
- Theme colors, a light palette at WCAG AAA contrast, theme keys only under the `auto` theme, your own Palette, and Nerd Font icons only where a Nerd Font is installed.
- Settings in `/config`: Claude activity, Follow Claude, Open at start, Right column, Hints, Search spacing, Shortcut row, Open with, Edit with, Diff with, Ignore, Palette and Glyphs.
- Validated and tested on Claude Code v2.1.310.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/file-tree-pane--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/file-tree-pane--v0.1.0
