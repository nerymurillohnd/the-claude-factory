---
name: frontmatter-values-without-colons-or-quotes
description: The owner's rule for every frontmatter value in skills, agents and commands, no colon and no quotes
metadata:
  type: feedback
---

In the frontmatter of skills, agents and commands, a colon goes only after a field name (`name:`, `description:`). No value ever holds a colon, and no value is wrapped in quotes. Reword the sentence instead: "in its local clone, then validates", never "in its local clone: validates" or a quoted description.

**Why:** the owner stated it on 2026-11-14 after three github-operations agents shipped a `description` with ": " that strict YAML parsers reject; Claude Code tolerated it, so `claude plugin validate --strict` passed. Quoting would also make the YAML valid, but the owner rejects quotes.

**How to apply:** when writing or reviewing any frontmatter value, remove colons by rewording, never by quoting. Values YAML cannot hold unquoted, such as an `argument-hint` that starts with `[`, and qualified identifiers such as `plugin:skill` in an agent's `skills` list, go to the owner before they change. See [[research-claude-code-with-the-project-skills]].
