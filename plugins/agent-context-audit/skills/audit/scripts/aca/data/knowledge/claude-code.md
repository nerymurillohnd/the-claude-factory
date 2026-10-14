# Claude Code: what loads, in what order, and what good looks like

Knowledge for the auditors. Checked against the Claude Code docs on 2026-10-14 for Claude Code 2.1.300. When `drift.md` shows that a section changed since then, the live text there wins.

## Contents

- Instruction files and load order
- Imports
- Rules in .claude/rules/
- AGENTS.md as read by Claude Code
- Auto memory
- Writing good instruction files
- Subagents, output styles, loop.md
- Settings files and precedence
- Permission rules
- Hooks and MCP servers
- Outside the audit's scope

## Instruction files and load order

Source: <https://code.claude.com/docs/en/memory>

- Locations, broadest first: managed policy (`/Library/Application Support/ClaudeCode/CLAUDE.md` on macOS, `/etc/claude-code/CLAUDE.md` on Linux and WSL), the user file `~/.claude/CLAUDE.md`, the project file `./CLAUDE.md` or `./.claude/CLAUDE.md`, and the personal project file `./CLAUDE.local.md`.
- At launch Claude Code loads `CLAUDE.md` and `CLAUDE.local.md` from the working directory and every directory above it. The files are concatenated, never overridden: content runs from the filesystem root down to the working directory, and within one directory `CLAUDE.local.md` comes after `CLAUDE.md`. When two instructions contradict each other, Claude may follow either one.
- Files in subdirectories load on demand, once Claude reads, writes or edits a file in that subdirectory.
- Block-level HTML comments (`<!-- ... -->`) are stripped before the content reaches Claude; comments inside code blocks are kept. Text inside such a comment is never an instruction to Claude.
- A CLAUDE.md file larger than 4 MiB is skipped entirely.
- `claudeMdExcludes` (any settings layer; arrays merge) skips matching files by absolute path or glob. Managed policy files cannot be excluded.
- `CLAUDE.local.md` is meant for personal, uncommitted preferences and should be gitignored. In a project that relies on AGENTS.md, adding a `CLAUDE.local.md` makes Claude Code stop reading AGENTS.md (see below).

## Imports

Source: <https://code.claude.com/docs/en/memory#import-additional-files>

- `@path` imports another file at launch, next to the file that references it. Relative paths resolve from the importing file, not the working directory; `~/` and absolute paths work.
- Imports can nest at most four hops deep.
- A path with spaces needs a backslash before each space. A path in quotes is never imported, with or without backslashes.
- Imports inside inline code spans and fenced code blocks are ignored; wrapping a path in backticks keeps it literal.
- An import in a project file that resolves outside the working directory is external: it loads only after the user approves external imports for that project. Imports in user-scope files load without that approval.
- Imports organize a long file but do not reduce its context cost: imported files also load at launch.

## Rules in .claude/rules/

Source: <https://code.claude.com/docs/en/memory#organize-rules-with-claude/rules/>

- Every `.md` file under `.claude/rules/` (recursively) and under `~/.claude/rules/` is a rule. User rules load before project rules; neither overrides the other.
- A rule without `paths` frontmatter loads at launch, with the same priority as `.claude/CLAUDE.md`.
- `paths` is the only frontmatter key Claude Code reads from a rule; any other key is ignored without an error. It takes a YAML list or a comma-separated string of globs (`**`, `*`, `{a,b}` brace expansion with a budget of 1,000 expanded patterns).
- A path-scoped rule loads when Claude reads, writes or edits a matching file (also through a Bash read such as `cat`). Patterns are relative to the project.
- If the frontmatter does not parse as YAML, Claude Code ignores it and loads the rule as if it had no `paths`, so a path-scoped rule silently becomes always-loaded.
- Rules in a nested `.claude/rules/` directory load on demand, like a nested CLAUDE.md.
- A symlinked rule that points outside the working directory needs the external-imports approval.

## AGENTS.md as read by Claude Code

Source: <https://code.claude.com/docs/en/memory#agents-md> (Claude Code 2.1.277 or later)

- By default (`claude-md-or-agents-md`) Claude Code reads `AGENTS.md` and `.claude/AGENTS.md` from the working directory and above only when there is no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` there. The user and managed CLAUDE.md files and `.claude/rules/` do not count for that check.
- With a CLAUDE.md present, AGENTS.md is not read unless a CLAUDE.md imports it (`@AGENTS.md`) or the Project instructions setting is `claude-md-and-agents-md`.
- The setting lives in `pluginConfigs["cc-plugin-agents-md@builtin"].options.instructionFiles` (older key `agents-md@builtin`), read from user settings, `--settings` or managed settings only. Values: `claude-md-or-agents-md`, `claude-md-and-agents-md`, `claude-md`, `managed-only`.
- Never read by Claude Code: `AGENTS.local.md`, `AGENTS.override.md`, anything under `.agents/`.
- A subdirectory's AGENTS.md loads on demand when that subdirectory has none of the three CLAUDE.md files.

## Auto memory

Source: <https://code.claude.com/docs/en/memory#auto-memory>

- Per repository at `~/.claude/projects/<project>/memory/` (all worktrees share it), or `autoMemoryDirectory`. Turned off by `autoMemoryEnabled: false` or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
- `MEMORY.md` is the index: only its first 200 lines or first 25 KB, whichever comes first, load at session start. The rest never reaches Claude.
- Topic files load on demand when Claude reads them.
- Claude saves corrections and preferences there on its own; it skips what it can derive from the code and what CLAUDE.md already says.
- The main conversation's auto memory does not reach subagents.

## Writing good instruction files

Sources: <https://code.claude.com/docs/en/memory#write-effective-instructions> and <https://code.claude.com/docs/en/best-practices>

- Target under 200 lines per CLAUDE.md. Longer files cost context and reduce adherence.
- The test for every line: would removing it cause Claude to make mistakes? If not, cut it.
- Include: commands Claude cannot guess, style rules that differ from the defaults, test instructions and preferred runners, repository etiquette, project-specific architecture decisions, environment quirks, non-obvious gotchas.
- Exclude: anything Claude can figure out by reading the code, standard language conventions, detailed API documentation, information that changes often, long tutorials, file-by-file descriptions, self-evident advice such as "write clean code".
- Write instructions concrete enough to verify ("Use 2-space indentation", "Run `npm test` before committing", "API handlers live in `src/api/handlers/`").
- Group related instructions under headings; keep files consistent with each other; review them for contradictions.
- Multi-step procedures and knowledge needed only sometimes belong in skills; guidance for one part of the codebase belongs in a path-scoped rule.
- CLAUDE.md is context, not enforcement: a rule that must hold every time belongs in a hook or a permission rule.
- Emphasis ("IMPORTANT") works only on a few lines; emphasizing many makes none stand out.

## Subagents, output styles, loop.md

Sources: <https://code.claude.com/docs/en/sub-agents,> <https://code.claude.com/docs/en/output-styles,> <https://code.claude.com/docs/en/scheduled-tasks>

- Subagent files live in `.claude/agents/` (project) and `~/.claude/agents/` (user). With the same name, the project agent wins over the user agent (managed and `--agents` rank higher, plugin agents lower).
- Required frontmatter: `name`, `description`. Optional: `tools` (allowlist), `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `autoCompactWindow`, `skills`, `mcpServers`, `hooks`, `memory` (`user`, `project`, `local`), `background`, `omitClaudeMd`, `effort`, `isolation`, `color`, `initialPrompt`, `experimental`. Claude Code ignores an unknown field without an error.
- A subagent starts with its own prompt plus the CLAUDE.md hierarchy (unless `omitClaudeMd: true`), never the conversation history or the main auto memory.
- Subagent memory: `~/.claude/agent-memory/<agent>/`, `.claude/agent-memory/<agent>/`, `.claude/agent-memory-local/<agent>/`; its MEMORY.md loads into that subagent.
- Output styles live in `.claude/output-styles/` and `~/.claude/output-styles/`; only the style named by `outputStyle` applies. Frontmatter: `name`, `description`, `keep-coding-instructions`.
- `loop.md` (`.claude/loop.md`, else `~/.claude/loop.md`) replaces the default prompt of a bare `/loop`; content beyond 25,000 bytes is truncated.

## Settings files and precedence

Sources: <https://code.claude.com/docs/en/settings> and <https://code.claude.com/docs/en/settings-reference>

- Highest precedence first: managed settings, `--settings`, `.claude/settings.local.json`, `.claude/settings.json`, `~/.claude/settings.json`. A key at a higher level overrides the same key lower down; list keys such as `permissions.allow` merge across files.
- The Settings index of the settings reference lists every documented key and the files that may hold it (`Any file`, `Managed`, `User or managed`, `User, local, or managed`, `User`, `Global config` meaning `~/.claude.json`). A key in a file that does not read it has no effect. The script checks keys mechanically; auditors judge whether a documented key's value makes sense.
- In non-interactive mode a settings file that fails validation is ignored silently.
- `includeGitInstructions` (default on) gives Claude built-in commit and pull request instructions; `attribution` customizes the commit and PR attribution Claude Code adds.

## Permission rules

Source: <https://code.claude.com/docs/en/permissions>

- Evaluation: deny, then ask, then allow; the first match wins, so a deny rule beats an allow rule for the same call.
- Read and Edit path rules use gitignore syntax: `//path` is absolute, `~/path` is from home, `/path` is relative to the settings file's location, a bare relative path is relative to the working directory.
- Path rules on Write, NotebookEdit, Glob or MultiEdit are accepted but never consulted (use Edit or Read). A rule on a tool's primary content field, such as `Bash(command:...)`, is ignored.
- File reads inside the working directories need no approval; built-in read-only Bash commands (`ls`, `cat`, `grep`, `find`, read-only `git`...) run without a prompt. File edits and other commands prompt by default.

## Hooks and MCP servers

Sources: <https://code.claude.com/docs/en/hooks> and <https://code.claude.com/docs/en/mcp>

- Hooks in settings files run shell commands on lifecycle events; a hook script path that does not exist fails every time the event fires.
- MCP servers: project scope in `.mcp.json` (needs the user's approval), user and local scope in `~/.claude.json` (local scope under that project's entry). A `"type": "sdk"` entry is skipped by Claude Code.

## Outside the audit's scope

These load but are never reported: skills (custom commands are skills since Claude Code merged them), saved workflows, everything an installed plugin provides (this plugin included), and managed policy files. They may be cited as evidence when a user-owned instruction duplicates or contradicts them. The `enabledPlugins` entry of `agent-context-audit@...` is legitimate configuration.
