# Changelog

All notable changes to **Session Handoff** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-19

### Changed

- **Breaking:** the skill follows a plain sequence: check the project's state, summarize the session from its start, compare it with the previous handoff, propose the handoff, add recommendations and context, then write it after you approve. A closing checklist confirms every step was done.
- **Breaking:** the handoff has six sections instead of eleven: Current state, Open items (in priority order, each with its first action, replacing Next steps), Context for the next session (learnings, corrections and recommendations), Decisions, Done this session (with the previous handoff's items) and Unverified and gaps. The template explains how to fill each one. Older handoffs with the eleven sections are still read.
- Only items still pending are carried forward. Claude asks you about the ones that look obsolete or outside the project, and a result you report from outside the session closes an item as done, noted as reported by you.
- In a git repository, Claude asks whether to commit and push the saved handoff.
- The first handoff of a project works without the folders: the skill creates them.
- The skill no longer offers to commit, push or open a pull request before writing: it offers to commit and push the handoff file after you approve it. It lists the open pull requests instead of the 20 most recent.
- The start-of-session hook adds nothing to `claude -p`, Agent SDK or GitHub Action runs, which do one specific job, and it finds the handoff at the repository root when Claude Code starts in a subfolder.
- When the start-of-session hook loads a handoff, it shows you a one-line notice naming the file, so you know it ran and which handoff Claude was given.
- The start-of-session instructions are seven short steps: read the newest handoff in full, treat it as a record, do what you ask even when it differs from the pending work, use the handoff's decisions, corrections and learnings as background so past mistakes are not repeated, and end the reply with a short list of the open items so you decide. Claude no longer stops to ask how to proceed.

### Removed

- The start-of-session hook no longer validates the handoff's headers or compares its project with the session's, and no longer stops to ask how to proceed.

### Fixed

- The start-of-session hook no longer reports an unreadable handoff folder as "no handoff": it warns you and Claude instead, also when the folder, `.claude` or a handoff is a symbolic link.
- A git failure such as an ownership (`safe.directory`) error is no longer recorded as "Not a git repository."; the handoff marks the repository state as not verified, with the reason.

## [0.1.0] - 2026-10-12

### Added

- `/session-handoff:write-handoff` skill, also started when you ask Claude for a handoff as you wrap up: at the end of a session, reads the project's git state (branch, uncommitted work, stashes, unpushed commits, commits since the last handoff, pull requests), offers to commit, push or open a pull request first, reconciles every open item of the previous handoff, drafts the new handoff with you and saves it as `.claude/session-handoff/YYYY-MM-DD-HHMM.md` in the project, never overwriting an earlier one.
- Every handoff records what was done, decided, corrected and learned, what is still open with where it stands and what finishing needs, the next steps in order, and what could not be verified; open items older than 30 days are marked for you to confirm or drop.
- `SessionStart` hook: when a session starts or is cleared in a project that has handoffs, Claude reads the newest one in full, summarizes it, lists its pending items, keeps your first request as the current one and asks how you want to proceed before starting work; in a run where nobody can answer, such as `claude -p`, it goes on with the request. In projects without handoffs the plugin adds nothing to the conversation.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/session-handoff--v1.0.0...HEAD
[1.0.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/session-handoff--v1.0.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/session-handoff--v0.1.0
