# Changelog

All notable changes to **Agent Context Audit** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-14

### Added

- `agent-context-audit:audit` skill, started only with `/agent-context-audit:audit`: runs the audit in the background and presents the status, the findings by severity and each high-severity finding; `latest` presents the newest report without a new run, and external claims can be checked in the session with your own permissions.
- A read-only audit of everything Claude Code and Codex load as context: the CLAUDE.md chain and its imports, CLAUDE.local.md, rules and their `paths`, nested CLAUDE.md files, auto memory, subagents, output styles, `loop.md`, settings at every scope, hooks, permissions, `.mcp.json` and the MCP part of `~/.claude.json`, AGENTS.md files and overrides, and Codex `config.toml`, hooks, rules and custom agents. Each source is listed with how it loads (always, for some paths, on demand, truncated, shadowed, dead or not loaded); skills, commands, workflows and plugin components are listed as out of scope.
- Deterministic checks that need no model: missing import targets, rules whose paths match no file, files cut by a size limit or never loaded, exact duplicates (in one context, or kept in two files that load separately), invalid settings JSON, undocumented, deprecated or misplaced settings keys, permission rules that never apply or contradict each other, hook scripts that don't exist or depend on the current directory, and deprecated Codex config keys.
- Isolated auditor sessions, one per group of files per domain, that read redacted copies line by line with read-only tools, in `claude -p` sessions that load no settings, hooks, MCP servers, plugins or memory; every line they receive is checked, so a skipped line makes the run partial.
- Validation of every finding before it is reported: exact lines and excerpt, and a conflict that resolves to another file and line, a path in the repository, an official docs URL or a documented default; judgment-only redundancy is never proposed for removal.
- A reviewer that reconciles the auditors' findings and compares similar instructions across files, with up to two challenge rounds on disputed findings; findings no one can settle stay open with both positions.
- External claims about third-party tools kept apart from findings, with opt-in `--verify-online` checks limited to GitHub, package registries and the official Claude Code, Anthropic and OpenAI docs.
- `report.md`, `report.json` and `status.json` per run in a self-ignored `.claude/agent-context-audit/` folder (or `--out`), with coverage per file, an executive summary, a remediation plan, limitations, run cost, and the change since the last run by stable finding IDs.
- Proof that nothing changed: hashes of every audited file and the git working tree and `HEAD` before and after the run.
- Exit codes for terminals and schedulers (0 complete, 1 findings, 2 partial, 3 failure, 4 cannot run), `--json`, `--exit-zero`, and a live check of the bundled docs knowledge (skip it with `--offline`).
- A `SessionStart` hook that says once when a new report exists, turned off with the `session_notice` option.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/agent-context-audit--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/agent-context-audit--v0.1.0
