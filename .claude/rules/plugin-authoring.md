---
paths:
  - "plugins/**"
  - ".claude/templates/plugin/**"
---

# Plugin authoring rules

## Structure

- Scaffold only with `node .github/scripts/new-plugin.mjs` — never copy another plugin by hand.
- Components live at the plugin root, never inside `.claude-plugin/`: `skills/<name>/SKILL.md`, `agents/*.md`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `output-styles/`, `monitors/monitors.json`, `bin/`, `settings.json`.
- Prefer `skills/` over `commands/` for new work.
- Reference plugin files from hooks and MCP/LSP configs as `${CLAUDE_PLUGIN_ROOT}/...`; persistent data goes in `${CLAUDE_PLUGIN_DATA}`.
- Component paths in `plugin.json` start with `./` and stay inside the plugin.

## Naming

- kebab-case; no `claude-`, `anthropic-`, `cc-plugin-` prefix; avoid `claude` as a whole word anywhere.
- Name = folder = marketplace entry = `plugin.json` `name`. Permanent once published.

## Manifest (`plugin.json`)

- Required by our policy: `name`, `displayName`, `version` (semver), `description`, `author`, `homepage` (plugin README on main), `repository`, `license: MIT`, `keywords`.
- Secrets and per-user values go in `userConfig` (`sensitive: true` for secrets) — never hardcoded.

## Cross-surface behavior

- Follow `.claude/rules/cross-surface-compatibility.md` (component matrix, design rules, README obligations). Default target: Claude Code **and** Cowork.

## Skills inside plugins

- Description: what it does + when to use it, third person, ≤ ~500 characters, specific trigger phrases.
- Body: headers, numbered steps, bullets; under 500 lines; move detail to `references/`.
- Knowledge-first: teach options and label recommendations; don't force one way.
- Generic for any user: no personal, company or language-specific assumptions.

## Hooks and scripts

- Fail safe: a hook error must never block the user without a clear message.
- Scripts are POSIX-compatible or Node/Python with no install step unless declared in Requirements.
- Never exfiltrate data; network calls only when the plugin's purpose requires them and the README discloses them.

## Done means

- README: every required section filled, no TODO/TEMPLATE comments, real usage examples.
- `claude plugin validate --strict plugins/<name>` passes.
- Installed from a local marketplace (`claude plugin marketplace add ./`) and exercised in Claude Code **and** Cowork (unless declared Claude Code-only).
