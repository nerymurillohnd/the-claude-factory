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

- Required by our policy: `name`, `displayName`, `version` (semver), `description`, `author`, `homepage` (plugin README on main), `repository`, `license: MIT`, `keywords`, `metadata.surfaces`.
- Secrets and per-user values go in `userConfig` (`sensitive: true` for secrets) — never hardcoded.

## Cross-surface behavior

- Follow `.claude/rules/cross-surface-compatibility.md` (component matrix, design rules, README obligations). Default target: Claude Code **and** Cowork.

## Skills inside plugins

- Description: what it does + when to use it, third person, ≤ ~500 characters, specific trigger phrases.
- Body: headers, numbered steps, bullets; under 500 lines and ~5,000 tokens. Follow [agentskills.io best practices](https://agentskills.io/skill-creation/best-practices):
  - Moderate detail: each line must be something the model would get wrong without it. The main path stays in `SKILL.md`; situational paths go to `references/` with a "read when …" trigger, one level deep. Leave layout and rare cases to the model.
  - Prescriptive only where the task is fragile (exact commands, sequences, formats); elsewhere state the goal and why.
  - Defaults, not menus: one default with a short escape hatch.
  - A short input/output example; a template for output that must keep its shape.
  - Read arguments with `$ARGUMENTS` (or `$N`) rather than relying on the appended `ARGUMENTS:` line.
- Audit our own skills with `/skill-diagnostics:audit`; fix only findings that change a verdict, findings or produced files. Re-audit after any rewrite: slimming can drop a load-bearing rule.
- `context: fork` only for a self-contained task that needs no conversation history (the forked subagent doesn't see it).
- Generic for any user: no personal, company or language-specific assumptions.

## Hooks and scripts

- Fail safe: a hook error must never block the user without a clear message.
- Scripts start with `#!/usr/bin/env <interpreter>` (no version), are committed as `100755`, and are called by path (`${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}`). The user's first interpreter on `PATH` runs them.
- No per-OS fallbacks: every runtime a script needs (interpreter, minimum version, POSIX shell or Git for Windows) is declared in the README **Requirements** section.
- Standard library only, no install step, unless declared in Requirements.
- Never exfiltrate data; network calls only when the plugin's purpose requires them and the README discloses them.

## Done means

- README: every required section filled, no TODO/TEMPLATE comments, real usage examples.
- `claude plugin validate --strict plugins/<name>` passes.
- Installed from a local marketplace (`claude plugin marketplace add ./`) and exercised in Claude Code **and** Cowork (unless declared Claude Code-only).
