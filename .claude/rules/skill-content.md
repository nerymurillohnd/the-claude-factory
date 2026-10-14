---
paths:
  - "plugins/*/skills/**"
  - ".claude/skills/**"
---

# Skill Content

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
- Grep the skill for each term's synonyms before finishing.
