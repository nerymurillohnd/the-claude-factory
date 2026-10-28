# Changelog

All notable changes to **Tailwind CSS Development** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2026-10-28

### Changed

- The MCP server script `mcp/server.mjs` is now executable, as its `#!/usr/bin/env node` line declares, so it can also be run directly. Claude Code keeps starting it with `node`, so nothing changes in how the plugin runs.

## [0.3.0] - 2026-10-28

### Added

- Four agents Claude can hand Tailwind work to: `tailwind-docs` answers with the exact syntax and the doc sections behind it, and `tailwind-auditor` reviews code against the docs and returns prioritized fixes, both without changing files; `tailwind-refactorer` cleans up existing markup into token-based classes without changing how it looks; `tailwind-migrator` moves a v3 project to v4 in a separate git worktree and reports every breaking change with its verdict.
- Guidance in the docs skill for custom variants, JavaScript-replaced markup, responsive strategy, stylesheet structure, refactoring and a review checklist, taken from Lombiq's Tailwind Agent Skills under the BSD 3-Clause License (see `NOTICE.txt`).
- Before Claude first hands a Tailwind task to one of the plugin's agents in a session, it checks that every link in the docs skill still answers. Broken links come back with their file and line, so you know up front and the agent reaches those sections from the site's navigation instead of failing on a dead page. The check needs Python 3.12 or later as `python3` and asks your permission to run.

### Changed

- The docs skill is now the first source for any Tailwind question or task. It sends Claude to a short reference for each part of the docs (installation, editor setup, compatibility, the upgrade guide, core concepts and every utility family) and from there to the exact section of the live page.

### Fixed

- The requirements now list git: moving a project from Tailwind CSS v3 to v4 needs git and the project in a git repository, because the migration runs in a separate git worktree.

## [0.2.2] - 2026-10-27

### Fixed

- Moving a project from Tailwind CSS v3 to v4 now covers the whole official upgrade guide, not just its tables of removed and renamed utilities. Claude runs the official upgrade tool first, in a new branch, then checks every breaking change against your project (default border and ring colors, Preflight, gradients, `container`, the prefix, custom utilities, variant order, `theme()`, the JavaScript config and the rest) and reports each one as changed, not present, kept on purpose or needing your decision.

## [0.2.1] - 2026-10-27

### Changed

- The checks ask the Tailwind CSS language server for the quick fixes of every diagnostic, and for the CSS of every class, at once instead of one after another, and look for a Tailwind CSS install in every parent folder at once. The answers are the same, in the same order.
- Internal code cleanup from stricter lint rules; nothing else changes in what the checks and tools return.
- Validated with Claude Code v2.1.312.

## [0.2.0] - 2026-10-27

### Added

- Tailwind CSS language-server checks in Claude Code: after every file Claude edits or writes, the official Tailwind CSS language server reviews it and Claude gets each class conflict, non-canonical class and invalid `theme()` path or directive with the exact replacement to apply. It claims no file type, so your TypeScript, Svelte or other language servers keep working.
- `tailwindcss` MCP server with four read-only tools Claude can call: `check_file` (a file's diagnostics with their fixes), `class_css` (the CSS and resolved color a class generates in your theme), `project_classes` (the classes your theme defines for a prefix, variants included) and `sort_classes` (Tailwind's official class order).
- Options: one switch per file type for the automatic check (CSS and preprocessors, HTML, JavaScript and TypeScript, Vue, Svelte, Astro, Markdown and MDX, server templates; all on by default), the class functions and class attributes the checks read, and the Tailwind CSS entry point for monorepos, several entry points or `@reference` in CSS modules and `<style>` blocks.
- Requires Node.js 24 or later and npm for the checks. Claude Code downloads the plugin's pinned packages from the npm registry when it installs or updates the plugin.

## [0.1.0] - 2026-10-27

### Added

- `tailwind-ui-design` skill: designs, builds, refactors and reviews interfaces in Tailwind CSS v4 with a product designer's craft. It reads your tokens, brand and components first, checks that the type, spacing, colour, elevation and radius systems exist as `@theme` tokens, composes hierarchy before colour, depth and finish, covers every state, verifies the rendered result in each appearance mode and width with measured WCAG 2.2 AA contrast (in your project's own build, or in a Play CDN preview page where there is none), and critiques it against generic-UI tells. Syntax questions go to `tailwind-official-docs`.
- `tailwind-official-docs` skill: gets Tailwind CSS syntax and behaviour right by reading the exact official page for each utility, variant and configuration a task touches, for the Tailwind version your project resolves, and verifies the result with your project's own checks. It carries an index of every page of the Tailwind docs, the 19 framework installation guides included, and the section anchors of the long concept pages. It installs Tailwind from zero by following the guide for your framework (or the Vite, PostCSS or CLI path when there is none) and checks that a first class renders, routes editor setup and Prettier class sorting, checks whether a project can adopt v4, and answers which version added a feature from the release posts and changelog, never using a feature newer than your installed version. It reads Context7 first when you have it, and reports only the documentation a decision depended on.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/tailwind-development--v0.3.1...HEAD
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/tailwind-development--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/tailwind-development--v0.3.0
[0.2.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/tailwind-development--v0.2.2
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/tailwind-development--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/tailwind-development--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/tailwind-development--v0.1.0
