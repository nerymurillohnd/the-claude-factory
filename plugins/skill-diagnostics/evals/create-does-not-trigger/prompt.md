---
description: "Trigger conflict: a request to create a skill must not run the audit skill, in either arm."
tags: [negative]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Create a skill in skills/release-notes that drafts release notes from the git tags of the current repository. Keep it short.
