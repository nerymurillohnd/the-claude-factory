---
name: {{skillName}}
description: {{skillDescription}}
---

<!--
  Procedure: .claude/references/skill.md
  Becomes skills/{{skillName}}/SKILL.md. The opening --- must stay the file's first line, or Claude Code reads no frontmatter.
  name: kebab-case, identical to the skill's directory name.
  description: what the skill does and when to use it, key use case first. With an optional when_to_use field,
  the two together are cut at 1,536 characters in the skill listing.
  Optional fields (when_to_use, argument-hint, allowed-tools and the rest) are listed in the procedure; add only the ones the skill needs.
  Keep this file under 500 lines and move detailed material to files beside it. Delete this comment.
-->

# {{skillTitle}}

{{skillInstructions}}
