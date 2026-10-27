# Changelog

All notable changes to **Tailwind CSS Development** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Tailwind CSS language-server checks in Claude Code: after every file Claude edits or writes, the official Tailwind CSS language server reviews it and Claude gets each class conflict, non-canonical class and invalid `theme()` path or directive with the exact replacement to apply. It claims no file type, so your TypeScript, Svelte or other language servers keep working.
- `tailwindcss` MCP server with four read-only tools Claude can call: `check_file` (a file's diagnostics with their fixes), `class_css` (the CSS and resolved color a class generates in your theme), `project_classes` (the classes your theme defines for a prefix, variants included) and `sort_classes` (Tailwind's official class order).
- Options: one switch per file type for the automatic check (CSS and preprocessors, HTML, JavaScript and TypeScript, Vue, Svelte, Astro, Markdown and MDX, server templates; all on by default), the class functions and class attributes the checks read, and the Tailwind CSS entry point for monorepos, several entry points or `@reference` in CSS modules and `<style>` blocks.
- Requires Node.js 20 or later and npm for the checks. Claude Code downloads the plugin's pinned packages from the npm registry when it installs or updates the plugin.

## [0.1.0] - 2026-10-27

### Added

- `tailwind-ui-design` skill: designs, builds, refactors and reviews interfaces in Tailwind CSS v4 with a product designer's craft. It reads your tokens, brand and components first, checks that the type, spacing, colour, elevation and radius systems exist as `@theme` tokens, composes hierarchy before colour, depth and finish, covers every state, verifies the rendered result in each appearance mode and width with measured WCAG 2.2 AA contrast (in your project's own build, or in a Play CDN preview page where there is none), and critiques it against generic-UI tells. Syntax questions go to `tailwind-official-docs`.
- `tailwind-official-docs` skill: gets Tailwind CSS syntax and behaviour right by reading the exact official page for each utility, variant and configuration a task touches, for the Tailwind version your project resolves, and verifies the result with your project's own checks. It carries an index of every page of the Tailwind docs, the 19 framework installation guides included, and the section anchors of the long concept pages. It installs Tailwind from zero by following the guide for your framework (or the Vite, PostCSS or CLI path when there is none) and checks that a first class renders, routes editor setup and Prettier class sorting, checks whether a project can adopt v4, and answers which version added a feature from the release posts and changelog, never using a feature newer than your installed version. It reads Context7 first when you have it, and reports only the documentation a decision depended on.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/tailwind-development--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/tailwind-development--v0.1.0
