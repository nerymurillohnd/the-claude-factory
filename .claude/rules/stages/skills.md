---
paths:
  - "plugins/*/skills/**"
  - ".claude/skills/**"
---

# Skills

## Sources

- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-time-sensitive-information>
- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#use-consistent-terminology>

## Time-Sensitive Information

- Never make an instruction depend on today's date: `before <month> <year>, use X`.
- Never date a fact about a product or model with words that expire: `now`, `currently`, `the latest`, `new`, `current models`.
- Anchor a change to a version or a fixed event: `since Claude Code 2.1.217`, `accounts created on or after 2026-08-31`.
- Label superseded behavior as old, after the current method, with the version or date it ended: an "Old patterns" section, or `the older form` inline.
- Keep the snapshot date of copied facts in one place in the skill.

## Terminology

- Pick one term per concept and use it in every file of the skill.
- Define a term the docs do not define where it first appears in `SKILL.md`.

## File reference sources

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
