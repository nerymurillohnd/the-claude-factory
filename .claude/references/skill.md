# Skill

How to create a plugin skill's `SKILL.md` from `.claude/templates/skill-template.md`.

## Produces

`plugins/<plugin>/skills/<skill>/SKILL.md`, plus any supporting files beside it (`references/`, `scripts/`, `assets/`).

## When

- When a plugin gains a skill, and when a skill's purpose or triggers change.

## Sources

Read 2026-11-10, Claude Code docs `skills`:

- Frontmatter is read only when the opening `---` is the file's first line; YAML that doesn't parse loads the skill with no fields set.
- `name` is optional and defaults to the directory name; `description` is recommended: "Put the key use case first: the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing."
- Optional fields: `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility`.
- Outside Claude Code (claude.ai uploads, the Skills API) only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools` are allowed; any other field fails the upload with a hard error.
- "Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files."

## Placeholders

| Value | Meaning | True value from |
| :-- | :-- | :-- |
| `{{skillName}}` | Kebab-case name, identical to the directory | The skill's directory |
| `{{skillDescription}}` | What the skill does and when to use it, key use case first | The skill's own files |
| `{{skillTitle}}` | The H1 heading | The skill's purpose |
| `{{skillInstructions}}` | The body Claude follows | The skill's procedure |

## Procedure

1. Create `plugins/<plugin>/skills/<skill>/` and copy the template to `SKILL.md`; the `---` stays on line 1.
2. Fill `name` and `description`; delete the instruction comment.
3. Add only the optional fields the skill needs. For a plugin that reaches Claude, keep to the portable subset, or the skill fails to upload there.
4. Write the body; move long material to files beside it and link them.
5. Run the checks.

## Rules

Official:

- Frontmatter on line 1, valid YAML.
- `description` plus `when_to_use` within 1,536 characters, key use case first.
- `SKILL.md` under 500 lines.

This repository:

- The description is written from the skill's own files, imperative, with no quoted trigger phrases.
- A colon goes only after a field name. No value holds a colon or is wrapped in quotes: reword the sentence instead, so every value stays plain text that strict YAML parsers read.
- `name` equals the directory name.
- Never take another plugin's skill as a model.

## Checks

- `claude plugin validate --strict plugins/<plugin>`.
- `claude plugin details plugins/<plugin>`: the skill is listed, with its size.
- `python3 scripts/validators/skill-names-consistency.py` and `python3 scripts/validators/skill-size.py`.

## Never

- Never add a frontmatter field the skill does not use.
- Never put a secret or a machine path in a skill.
