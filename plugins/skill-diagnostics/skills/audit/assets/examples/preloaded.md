---
name: changelog-style
description: Keep a Changelog rules for writing and checking release notes. Use when writing or reviewing a CHANGELOG entry.
---

This skill is preloaded into the `release-notes` agent through its `skills` field.

## Input

The delegation message gives the version, the release date and the list of changes. Missing any: return one line saying which, and stop; never ask.

## Steps

1. Sort each change into Added, Changed, Deprecated, Removed, Fixed or Security.
2. Write one line per change, in the past tense, naming what a user notices.
3. Leave out sections with no entries.

## Return

Your final message is the only output the caller sees: the entry, from its `## [<version>] - <date>` heading to its last line.
