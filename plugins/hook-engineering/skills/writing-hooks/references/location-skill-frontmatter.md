# Skill frontmatter hooks

Read this in step 4 when the hook belongs to a skill and must start only once that skill is invoked.

## Role

You write a hook that belongs to one skill: dormant until the skill is used, then active for the rest of the session.

## Knowledge

- Registration: when the user or Claude invokes the skill. The hooks keep running for the rest of the session, on later turns too.
- `once: true`: removes the hook after its first successful run; a run that fails, blocks or times out leaves it in place. Skill frontmatter is the only place `once` is honored.
- Format: the same configuration as settings hooks, in YAML under the `hooks` key.
- Trust: a project skill's frontmatter hooks follow the settings-file rule; they register even in a `-p` run in an untrusted folder.
- Limits: the skills of one source (a project, the personal skills folder, each plugin) can register at most 1,024 hooks and 16,384 matcher characters per session; a skill past the limit registers none of its hooks and the debug log says `registers none of its hooks`.
- Policy: under managed `strictPluginOnlyCustomization` with `hooks`, only plugin skills, bundled skills and managed-directory skills keep their frontmatter hooks.
- Placeholders: the docs' example uses `${CLAUDE_PROJECT_DIR}`, and Claude Code rewrites the three path placeholders in a skill's PowerShell hooks. In a plugin skill's frontmatter hooks, `${CLAUDE_PLUGIN_ROOT}` resolves, `${CLAUDE_SKILL_DIR}` stays literal and `${CLAUDE_PLUGIN_DATA}` fails (observed; not in the docs). `${CLAUDE_SKILL_DIR}` is documented only for the skill's Markdown and `allowed-tools`.
- Docs: `### Hooks in skills and agents` and `#### Limits on skill hooks` in `hooks`, and the `hooks` field in `skills`.

## Gotchas

- `/hooks` doesn't list a skill's hooks until the skill has been invoked in that session.
- When `/hooks` still lists none of the skill's hooks after it is invoked, check the frontmatter parses before anything else, then the limits and the policy above.

## Rules

- Add `once: true` only to a hook that must run a single time, such as a one-time setup; without it the hook keeps running for the rest of the session.
- Put a hook here only when it must start with the skill; a hook that must run in every session belongs in settings or `hooks/hooks.json`.
- In a plugin skill, reference the script through `${CLAUDE_PLUGIN_ROOT}` followed by `/skills/<skill>/<script>`, never through `${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_DATA}`, and confirm in step 7 that `/hooks` lists it once the skill is invoked.
- Quote the YAML value of a shell-form command in single quotes, so the inner double quotes reach the shell.

## Structure

- File: the skill's `SKILL.md`, under `hooks` in the frontmatter.
- Template: `assets/skill-frontmatter.md`, written for a project skill; in a plugin skill, replace `${CLAUDE_PROJECT_DIR}` with `${CLAUDE_PLUGIN_ROOT}` and `<path>` with `skills/<skill>`.
