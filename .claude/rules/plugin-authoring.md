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
- Workflow scripts (`workflows/*.js`) use the top-level `return` the workflow runtime provides, which no JavaScript parser accepts, so Biome skips `plugins/*/workflows`. Keep them small, keep their schemas equal to the JSON schemas the plugin's own validator uses (a unit test checks the embedded copies), and test them with a real run.

## Naming

- kebab-case; no `claude-`, `anthropic-`, `cc-plugin-` prefix; avoid `claude` as a whole word anywhere.
- Name = folder = marketplace entry = `plugin.json` `name`. Permanent once published.

## Manifest (`plugin.json`)

- Required by our policy: `name`, `displayName`, `version` (semver), `description`, `author`, `homepage` (plugin README on main), `repository`, `license: MIT`, `keywords`, `metadata.surfaces`.
- Secrets and per-user values go in `userConfig` (`sensitive: true` for secrets) — never hardcoded.

## Cross-surface behavior

- Follow `.claude/rules/cross-surface-compatibility.md` (component matrix, design rules, README obligations). Default target: Claude Code **and** the Claude app.

## Skills inside plugins

- Description: what it does + when to use it, third person, ≤ ~500 characters, specific trigger phrases.
- Body: headers, numbered steps, bullets; under 500 lines and ~5,000 tokens. Follow [agentskills.io best practices](https://agentskills.io/skill-creation/best-practices):
  - Moderate detail: each line must be something the model would get wrong without it. The main path stays in `SKILL.md`; situational paths go to `references/` with a "read when …" trigger, one level deep. Leave layout and rare cases to the model.
  - Prescriptive only where the task is fragile (exact commands, sequences, formats); elsewhere state the goal and why.
  - Defaults, not menus: one default with a short escape hatch.
  - A short input/output example; a template for output that must keep its shape.
  - Read arguments with `$ARGUMENTS` (or `$N`) rather than relying on the appended `ARGUMENTS:` line.
- Audit our own skills with `/skill-diagnostics:audit`. The audit reports every verified finding; fix first those that change a verdict, findings or produced files. Re-audit after any rewrite: slimming can drop a load-bearing rule.
- `context: fork` only for a self-contained task that needs no conversation history (the forked subagent doesn't see it).
- Frontmatter must parse: Claude Code loads a skill with malformed YAML with empty metadata, so its description never matches. Validate every skills directory with `claude plugin validate` (v2.1.233+); `.github/scripts/validate-claude.sh` runs it on `.claude/` and on every plugin.
- Measure triggering as a rate, never one prompt at a time: several realistic prompts, each an eval case with a `tool_used: Skill` grader, re-run after every description change (`.claude/rules/evals.md`, Trigger rate).
- Keep the skill followed for the whole session (docs: skills, Claude stops following a skill):
  - A rule that must hold every time goes in a hook, in the skill's `hooks` frontmatter or the plugin's `hooks/hooks.json`; instructions alone get skipped.
  - Guidance that needs judgment is worded for the whole task ("after every edit", not "once").
  - The most important instructions sit near the top of `SKILL.md`: after compaction Claude Code may keep only its start. After a compaction, invoke the skill again.
- Generic for any user: no personal, company or language-specific assumptions.

## Hooks and scripts

- Fail safe: a hook error must never block the user without a clear message.
- Scripts start with `#!/usr/bin/env <interpreter>` (no version), are committed as `100755`, and are called by path (`${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}`). The user's first interpreter on `PATH` runs them.
- No per-OS fallbacks: every runtime a script needs (interpreter, minimum version, POSIX shell or Git for Windows) is declared in the README **Requirements** section.
- Standard library only, no install step, unless declared in Requirements.
- A script Claude runs through Bash exits 0 whenever it printed its result, and reports problems inside the output. Claude Code treats exit 1 as a failed command and cuts its output to about 10,000 characters (docs: tools-reference, Output limits).
- Never exfiltrate data; network calls only when the plugin's purpose requires them and the README discloses them.

## Done means

- README: every required section filled, no TODO/TEMPLATE comments, real usage examples.
- `claude plugin validate --strict plugins/<name>` passes.
- Tested with `/test-installed-plugin <name>` (copied install, load check, eval suite) and exercised in the Claude app, in a Cowork session and a chat conversation (unless declared Claude Code-only).
