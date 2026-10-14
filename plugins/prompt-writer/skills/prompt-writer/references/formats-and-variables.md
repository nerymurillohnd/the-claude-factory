# Formats and variables

Read when the prompt is the text of something Claude loads, has Claude build one, or takes variable inputs.

## Formats change

System prompt, skill, slash command, agent, `CLAUDE.md`, hook and plugin formats change between releases. Before you write one, or a prompt that has Claude build one, check its current official page and follow it over memory:

- System prompts for the API: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>
- Skills and slash commands (slash commands are skills; `.claude/commands/` files are the older form): <https://code.claude.com/docs/en/skills>
- Subagents: <https://code.claude.com/docs/en/sub-agents>
- `CLAUDE.md` and memory: <https://code.claude.com/docs/en/memory>
- Hooks: <https://code.claude.com/docs/en/hooks>
- Plugins: <https://code.claude.com/docs/en/plugins/overview>

## Variables by what fills them

- **Claude Code, from the text typed after a skill's or slash command's name:** `$ARGUMENTS` for all of it, `$ARGUMENTS[N]` or `$N` by position from 0, `$name` for names declared in the `arguments` frontmatter. Escape a literal `$` before a digit or one of those names with a backslash (`\$1.00`). A skill or slash command with no placeholder gets the typed text appended at its end, where it reads as a fresh instruction; when the input could read as an order, place the placeholder where the input belongs and frame it as data, for example inside a tag.
- **An application that fills a template before an API call:** the application's own syntax; `{{VARIABLE_NAME}}` when it has none.
- **A person who pastes the prompt:** `{{VARIABLE_NAME}}`, each named in the reply.
