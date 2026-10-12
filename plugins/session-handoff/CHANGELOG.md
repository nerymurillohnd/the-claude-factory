# Changelog

All notable changes to **Session Handoff** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-12

### Added

- `/session-handoff:write-handoff` skill, also started when you ask Claude for a handoff as you wrap up: at the end of a session, reads the project's git state (branch, uncommitted work, stashes, unpushed commits, commits since the last handoff, pull requests), offers to commit, push or open a pull request first, reconciles every open item of the previous handoff, drafts the new handoff with you and saves it as `.claude/session-handoff/YYYY-MM-DD-HHMM.md` in the project, never overwriting an earlier one.
- Every handoff records what was done, decided, corrected and learned, what is still open with where it stands and what finishing needs, the next steps in order, and what could not be verified; open items older than 30 days are marked for you to confirm or drop.
- `SessionStart` hook: when a session starts or is cleared in a project that has handoffs, Claude reads the newest one in full, summarizes it, lists its pending items, keeps your first request as the current one and asks how you want to proceed before starting work; in a run where nobody can answer, such as `claude -p`, it goes on with the request. In projects without handoffs the plugin adds nothing to the conversation.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/session-handoff--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/session-handoff--v0.1.0
