---
description: "Trigger rate, authoring: a plain-words request to write or improve a skill, with no slash command and no skill name. Authoring is in the skill's scope since 0.3.0, so skills-best-practices must be invoked."
tags: [trigger, authoring]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Every release I do the same steps by hand: bump the version in package.json, move the Unreleased notes in CHANGELOG.md under the new version, tag it and push the tag. Turn that into a skill under skills/release-steps so you can do it for me next time.
