---
description: "Trigger rate, near miss: a plain-words request to turn a manual routine into a new skill. The plugin only audits and its description excludes writing a skill from scratch, so skills-best-practices must not be invoked, in either arm."
tags: [trigger, negative]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Every release I do the same steps by hand: bump the version in package.json, move the Unreleased notes in CHANGELOG.md under the new version, tag it and push the tag. Turn that into a skill under skills/release-steps so you can do it for me next time.
