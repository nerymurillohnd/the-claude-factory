# Plugin Design Rules

Apply only when Nery explicitly asks to create, build or start a plugin.

## Design brief
Write the brief and agree it with Nery, in Spanish, before building anything. It covers:
- Market check: what already exists for this domain, what users must combine today, and what this plugin covers in one install that they cannot find elsewhere.
- Problem and outcome: the recurring friction it removes, and who it is for.
- Overlap: when an existing plugin of this marketplace covers part of the domain, weigh extending it against a new plugin, and propose the choice (recall memory `no-other-plugins-as-precedent`).
- Name: kebab-case, permanent, no `claude-` or `anthropic-` prefix, named for what it does; a display name and an emoji.
- Category: an `id` from `scripts/categories.json`.
- Components: skills, agents, hooks, MCP, LSP, output styles, monitors, scripts, each justified by a user task.
- Surfaces: Claude Code and the Claude app by default. Check every component against `docs/compatibility.md`; if a part forces Claude Code-only, say why and get Nery's OK.
- Requirements: CLIs, accounts, API keys (`userConfig`), dependencies, minimum Claude Code version.
- Evals: only when Nery explicitly requests them.
- Sources: the current official docs for every component type used, with their version-gated features.

## While building
- Pass `--claude-code-only` to `new-plugin.mjs` only when the brief approved it.
- Exercise each component while you build with `claude --plugin-dir plugins/<name>`.
- While Nery is still shaping the plugin, run only the cheap checks each edit needs; do not run or announce live tests, the full gate sequence or the plugin review (recall memory `no-unrequested-verification-while-designing`). Run the closing checks only once he says it is ready.

## Closing checks
- The release gate in `.claude/CLAUDE.md` → Purpose and release gate, with the plugin review run from `.claude/templates/plugin-review-brief.md`.
- Nery runs no per-plugin Claude app check: state what was not observed live as unverified, and never log it as debt, an open item or a release blocker.
- After the first push, run `sync-labels.mjs` to create the `plugin: <name>` label.
- Hand off what was built, the raw gate output, the surfaces tested live and those taken from the docs, and the release step (`release-and-versioning`).
