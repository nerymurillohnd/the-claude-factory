# Codex CLI: what loads, in what order, and what good looks like

Knowledge for the auditors. Checked against the Codex docs on 2026-10-14 for Codex CLI 0.162.1. When `drift.md` shows that a section changed since then, the live text there wins.

## Contents

- Instruction discovery
- Size limit
- Config layers, trust and keys
- Custom agents, rules and hooks
- Writing good AGENTS.md files
- Outside the audit's scope

## Instruction discovery

Source: <https://developers.openai.com/codex/guides/agents-md>

- Global scope: in the Codex home (`~/.codex`, or `CODEX_HOME`), Codex reads `AGENTS.override.md` when it exists and is not empty, otherwise `AGENTS.md`. Only the first non-empty file at that level counts.
- Project scope: starting at the project root (normally the git root) and walking down to the working directory, each directory contributes at most one file, checked in this order: `AGENTS.override.md`, `AGENTS.md`, then each name in `project_doc_fallback_filenames`. Without a project root, only the working directory is checked.
- Files are concatenated from the root down, joined by blank lines; guidance closer to the working directory comes later in the prompt.
- Empty files are skipped. A directory's `AGENTS.override.md` hides that directory's `AGENTS.md` while it exists.
- Codex stops at the working directory: an AGENTS.md in a deeper folder loads only when Codex starts in that folder or below it.
- Codex rebuilds the chain on every run; there is no cache.

## Size limit

Sources: <https://developers.openai.com/codex/guides/agents-md> and <https://learn.chatgpt.com/docs/config-file/config-advanced>

- Codex stops adding files once the combined size reaches `project_doc_max_bytes`, 32 KiB by default. Content beyond the limit never reaches the model. Raise the limit or split guidance into nested directories.

## Config layers, trust and keys

Source: <https://developers.openai.com/codex/config-reference>

- User config: `~/.codex/config.toml`. Project config: `.codex/config.toml`, loaded only when the project is trusted (`projects."<path>".trust_level = "trusted"` in the user config). Untrusted projects skip project `.codex/` layers: config, hooks and rules.
- `project_doc_fallback_filenames`: extra names to try when AGENTS.md is missing in a directory. `project_doc_max_bytes`: the size limit above.
- `model_instructions_file` replaces the built-in instructions; `developer_instructions` adds developer instructions; `instructions` is reserved for future use.
- Deprecated or unsupported values are listed in `codex-config.json` in this folder (for example `experimental_instructions_file` renamed to `model_instructions_file`, `approval_policy = "on-failure"` deprecated, `approval_policy = "untrusted"` unsupported).

## Custom agents, rules and hooks

Sources: <https://learn.chatgpt.com/docs/agent-configuration/subagents,> <https://learn.chatgpt.com/docs/agent-configuration/rules,> <https://learn.chatgpt.com/docs/hooks>

- Custom agents are TOML files in `~/.codex/agents/` (personal) or `.codex/agents/` (project). Each must define `name`, `description` and `developer_instructions`; `model` and `model_reasoning_effort` are optional. They inherit the parent's permissions, provider and MCP servers.
- Command rules are Starlark `.rules` files in a `rules/` folder next to an active config layer (`~/.codex/rules/`, `.codex/rules/` when trusted).
- Hooks come from `hooks.json` or an inline `[hooks]` table in a config layer, enabled by `features.hooks` (`features.codex_hooks` is a deprecated alias).

## Writing good AGENTS.md files

Sources: <https://developers.openai.com/codex/guides/agents-md> and <https://agents.md>

- Put repository-wide expectations at the root and specialized rules in the nearest nested file, so each directory gets only what applies to it.
- Keep files concise and within the size limit; split long guidance across directories instead of letting it be cut.
- Use `AGENTS.override.md` for temporary overrides and remove it when done; while it exists, the AGENTS.md beside it is ignored.
- Code review rules for Codex review go in a `## Code Review Rules` section of the AGENTS.md closest to the code they govern.
- A file read by both Codex and Claude Code should hold only guidance valid for both tools; tool-specific directives belong in that tool's own file.

## Outside the audit's scope

Codex skills (`.agents/skills`, `~/.agents/skills`) and custom prompts (deprecated in favor of skills) load but are never reported.
