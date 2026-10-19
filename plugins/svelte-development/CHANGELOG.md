# Changelog

All notable changes to **Svelte Development** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-19

### Added

- `svelte-best-practices` skill: writes, reviews and explains Svelte 5 and SvelteKit 3 code by current practice (runes, snippets, events, routes, load, forms and remote functions, hooks, env, config, adapters and security) and migrates Svelte 4 and SvelteKit 2 projects, with references for the Svelte CLI (`sv`), Astro, Tailwind CSS, the changelogs and known errors in the official docs.
- `svelte-docs-and-autofixer` skill: looks up the official Svelte, SvelteKit and Svelte CLI docs and checks Svelte code with the Svelte autofixer through the plugin's Svelte MCP tools, including code pasted in the chat, and creates Svelte playground links.
- `svelte-lsp-navigation` skill: answers where a component, prop, function or type is defined, used or called, and what a change would break, through the Svelte language server, and proves a change with the project's own check (`npm run check` or `svelte-check`).
- `svelte-component-editor` agent: writes and edits Svelte components and modules and SvelteKit route files, checking each change against the docs, the autofixer, the language server and the project check before handing it back.
- `svelte-code-auditor` agent: audits Svelte and SvelteKit code without changing it (legacy syntax, runes misuse, SvelteKit 2 leftovers, server and client boundary leaks, CSRF and origin settings, unsafe HTML, accessibility, Astro island props, Tailwind CSS 4 setup) and reports findings with file, line, severity and fix.
- Svelte MCP server: the Svelte team's remote server at `https://mcp.svelte.dev/mcp`, with no download or install.
- Svelte language server: `svelteserver` for `.svelte` files, with diagnostics after each edit, when `svelte-language-server` 0.18.5 or later is installed on your `PATH`.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/svelte-development--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/svelte-development--v0.1.0
