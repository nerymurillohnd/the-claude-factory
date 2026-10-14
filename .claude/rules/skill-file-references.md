---
paths:
  - "plugins/*/skills/**"
  - ".claude/skills/**"
---

# Skill File References

## Sources

- <https://agentskills.io/specification#file-references>
- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns>
- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-deeply-nested-references>
- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#structure-longer-reference-files-with-table-of-contents>

## Links

- Link every skill file from `SKILL.md` with a Markdown link and its path from the skill root: `[<file>.md](references/<file>.md)`.
- Never link a skill file with `../`, with a backslash, or relative to the linking file.
- Give every skill file a condition for reading it where `SKILL.md` lists it: `Read [<file>.md](references/<file>.md) when <condition>.`
- In a text or code block, where links do not render, write the path from the skill root: `references/<file>.md`.
- Say whether Claude runs a script or reads it: `Run scripts/<script>`, `See scripts/<script> for <topic>`.

## Depth

- Keep references one level deep: only `SKILL.md` names other skill files.
- Claude may only partly read a file reached through another reference.
- Never name another skill file inside `references/`, `assets/` or `scripts/`. Move the pointer into `SKILL.md`, at the step that reads both files.
- A file outside `SKILL.md` may point back to a section of `SKILL.md`.

## Long Files

- Open every reference file over 100 lines with a `## Contents` list of its sections, so a partial read still shows the file's full scope.
- List every `##` heading in order, with its `###` headings nested under it, word for word.

## Checks

- Resolve every link from the skill root.
- Confirm every file in `references/` and `assets/` is linked from `SKILL.md`.
- Grep `references/` and `assets/` for other skill file names; expect none.
