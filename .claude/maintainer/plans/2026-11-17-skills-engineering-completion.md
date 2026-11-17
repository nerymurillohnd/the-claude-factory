# skills-engineering: completion plan

Moved from the earlier, long version of `.claude/rules/plugins/skills-engineering.md` on 2026-11-17, unchanged. Some of these files already exist on the branch (`plugin.json`, `LICENSE`, `CHANGELOG.md`, `README.md`); check each step against them before acting.

## Components

- Built: `skills/auditing-skills/SKILL.md`; the reviewers `content-patterns`, `runtime-contract`, `size-limits-and-budgets`, `knowledge-delta`, `task-mechanisms`, `frontmatter-description`, `comprehension`, `feature-fit` and `scripts`, each with its agent, its reference in `references/` and the shared `assets/audit-report.md`; and `references/skill-types-and-frontmatter.md`, the lookup of fields, names, arguments, body features and layouts by type of skill, which `SKILL.md` passes to `runtime-contract` and `frontmatter-description`.
- Not built: the scripts of the mechanical checks, `.claude-plugin/plugin.json`, `LICENSE`, `CHANGELOG.md`, `README.md`, the plugin's row in the root `README.md` catalog, and its entry in `PRIVACY.md`.
- Content moved out of a reviewer's scope, the verified-facts ledgers and the runtime-contract traceability map are in `.claude/maintainer/skills-engineering/`. Build the future security reviewer from the parked content there.

## Completing the plugin

Follow the docs-maintenance skill's New plugin event, in its order:

1. Write `.claude-plugin/plugin.json`: `name` `skills-engineering`; `displayName` "Skills Engineering"; a `description` the owner approves; `version` from the plugin-versioning skill; `license` `MIT`; `metadata.surfaces` Claude Code and Claude; `metadata.category`, which the owner chooses from the root catalog; `engines["claude-code"]` from v2.1.304. Then run `claude plugin validate plugins/skills-engineering --strict` and fix what it reports.
2. Write `LICENSE` and `CHANGELOG.md` with docs-maintenance. Record in the CHANGELOG entry that sets the minimum why it is v2.1.304: from that release a subagent that Claude messages right after it finishes keeps its latest work, which `SKILL.md` relies on when it resumes a reviewer with `SendMessage`. The other features the plugin uses came earlier: `omitClaudeMd` (v2.1.271), `claude plugin validate --json` (v2.1.259), `effort` in subagent frontmatter (v2.1.80).
3. Launch the `plugin-readme-writer` subagent for the README, briefed as docs-maintenance's governance says, with these owner values: emoji 🔬; surfaces Claude Code and Claude; minimum Claude Code version v2.1.304. Give it these facts too:
   - Prerequisites: Claude Code; the Claude Code docs MCP server, recommended, added with `claude mcp add --transport http --scope user claude-code-docs https://code.claude.com/docs/mcp` and checked with `claude mcp list`, which shows `claude-code-docs` connected; it needs no sign-in.
   - What's inside: the skill `auditing-skills` and its reviewer agents.
   - Usage: `/skills-engineering:auditing-skills` with a skill path, name or URL; reviewer names (`content-patterns`, `runtime-contract`, `size-limits-and-budgets`, `knowledge-delta`, `task-mechanisms`, `frontmatter-description`, `comprehension`, `feature-fit`, `scripts`) run only those reviewers, and none runs all; it also runs after a skill is created or edited.
   - What this plugin runs and sends: no hooks and no MCP server of its own; the reviewers read the official docs through the user's docs MCP server, and through WebSearch and WebFetch to code.claude.com, platform.claude.com, claude.com and support.claude.com; files written: none.
   - Compatibility note: the reviewers are agents, so in Claude the audit runs only where Claude can run tasks, and elsewhere the skill reports that its reviewers aren't available.
   - Limitations: until a mechanical check has a script, the reviewers report it as not run and their reports come back incomplete.
4. Run `claude plugin validate plugins/skills-engineering --strict --profile directory`, add the plugin's row to the root `README.md` catalog, and add it to `PRIVACY.md`.

## Open decisions

- `SKILL.md` uses `argument-hint`, a Claude Code-only field. Confirm with a test upload to Claude that a plugin skill keeps it.
- With the docs MCP server added under another name, or as a Claude connector (`mcp__claude_ai_<connector>__*`), the reviewers' `tools` list doesn't reach it, and they fall back to WebSearch and WebFetch.
