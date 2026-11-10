---
name: documentation-standards-sources
description: "External standards behind the plugin CHANGELOG and README contracts, with the date each was read"
metadata:
  node_type: memory
  type: reference
  originSessionId: 2a662f9e-80ae-553c-8ae9-6f9759fae7f1
  modified: 2026-11-10T10:15:37.932Z
---

Sources the `changelog-writer` and `plugin-readme-writer` contracts rest on. All read 2026-11-10; re-read before changing a rule that cites one.

Plugin changelog:

- Keep a Changelog 2.0.0, `https://keepachangelog.com/en/2.0.0/`: `Unreleased` at the top; one `## [X.Y.Z] - YYYY-MM-DD` section per release, newest first; six change types; `**Breaking:**`; `[YANKED]`; link references at the bottom. It sets no time zone; the project dates releases in UTC.
- Semantic Versioning 2.0.0.
- Claude Code docs `plugins/cli-reference` → `claude plugin tag`: release tags are `<name>--v<version>`.

Plugin README:

- GitHub Docs, "About the repository README file" and "Basic writing and formatting syntax" (`github/docs` at `f309096`): relative links resolve inside the repository; alerts are for content "crucial for user success", "one or two per article", never consecutive or nested; content past 500 KiB is truncated.
- Claude Code docs `plugins/manifest-reference` and `plugins/install`.
- claude.com `/docs/plugins/pre-submission-checklist` (checked 2026-10-25): the directory blocks a README under 40 words, code blocks excluded.
- claude.com `/docs/plugins/platform-support`: the component by surface matrix now embedded in the README contract's Compatibility table.

**How to apply:** when a contract in `.claude/agents/docs/` changes a rule marked as coming from one of these, read the source again and update this note's date. Related: [[claude-surfaces-merge]].
