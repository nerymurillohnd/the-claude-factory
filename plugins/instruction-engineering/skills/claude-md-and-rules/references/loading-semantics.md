# How Claude Code loads instruction files

Checked on 2026-10-28 against https://code.claude.com/docs/en/memory (raw page), /best-practices, /large-codebases, /hooks and the Claude Code changelog through v2.1.312. When the installed client is newer, search the changelog for `CLAUDE.md`, `rules`, `paths` and `AGENTS.md` after v2.1.312 before relying on a detail below; the changelog wins over the docs when they disagree.

## Contents

1. Context, not configuration
2. Locations and load order
3. When each file loads
4. Path-scoped rules
5. Imports
6. Size limits
7. AGENTS.md interplay
8. Exclusions, additional directories, symlinks
9. Compaction
10. How to observe what loaded
11. Common myths and the current fact

## 1. Context, not configuration

- CLAUDE.md and rules are delivered as a user message after the system prompt, not as part of it. Claude reads them and usually follows them; there is no guarantee.
- All discovered files are concatenated. Nothing overrides anything. Later position (closer directory, CLAUDE.local.md, project after user) is not precedence: when two instructions conflict, Claude may pick either one.
- Deterministic enforcement lives elsewhere: hooks (`command` or `http` type; `prompt`/`agent` hooks are model judgments), permission `deny` rules, the sandbox, managed settings. A `command` hook blocks by exiting with code 2 (exit 1 is a non-blocking error); an `http` hook blocks by returning a 2xx response whose JSON carries the decision fields. `onFailure: "block"` (v2.1.295+) also blocks when the hook itself fails.
- Block-level HTML comments (`<!-- ... -->` on their own lines) in CLAUDE.md are stripped before injection, so they are free maintainer notes. Comments inside code blocks are kept.

## 2. Locations and load order

Listed broadest to most specific; each later file appears later in context.

| Scope | Location | Shared with |
| :-- | :-- | :-- |
| Managed policy | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux/WSL `/etc/claude-code/CLAUDE.md`; Windows `C:\Program Files\ClaudeCode\CLAUDE.md`; or `claudeMd` in managed settings | Everyone on the machine; cannot be excluded |
| User | `~/.claude/CLAUDE.md` (or `$CLAUDE_CONFIG_DIR/CLAUDE.md`), user rules in `~/.claude/rules/**/*.md` | Only the user, every project |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md`; project rules in `./.claude/rules/**/*.md` | Team, via git |
| Local | `./CLAUDE.local.md` (add to `.gitignore`) | Only the user, this checkout |

- User rules load before project rules; neither overrides the other.
- Unscoped project rules load at launch "with the same priority as `.claude/CLAUDE.md`".
- Within one directory, CLAUDE.local.md is appended after CLAUDE.md.
- A gitignored CLAUDE.local.md exists only in the worktree where it was created; to share personal notes across worktrees, import a file from the home directory (`@~/.claude/my-project-instructions.md`).
- Rules are skipped when `project` is excluded from `--setting-sources` (on-demand rules too since v2.1.211).

## 3. When each file loads

| Loads | What |
| :-- | :-- |
| At launch | Managed, user CLAUDE.md, unscoped user rules, CLAUDE.md/CLAUDE.local.md/.claude/CLAUDE.md in the working directory and every ancestor, unscoped project rules from the `.claude/rules/` of the working directory and of every ancestor (Agent SDK "CLAUDE.md load locations"; an ancestor rule's globs are relative to that ancestor), everything those files import |
| On demand, once | CLAUDE.md and CLAUDE.local.md in a subdirectory when Claude reads, writes or edits a file in that subdirectory; rules under a subdirectory's own `.claude/rules/` load on demand too (the docs don't state their trigger; the same one is inferred) |
| On demand | A rule with `paths:` when Claude uses Read, Write or Edit on a matching file, or views one with a single-file Bash read (`cat`, `head`, `tail`, `sed -n`, `grep`); it loads again after compaction when a matching file is touched |
| Not at all by default | CLAUDE.md in an `--add-dir` directory (needs `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`), files excluded by `claudeMdExcludes`, files blocked by a Read deny rule or `blockReadsOutsideWorkingDirectories` (an "Instruction file not loaded" notice names the reason) |

Version notes: Write and Edit trigger path-scoped rules and nested CLAUDE.md since v2.1.288 (before, only Read did, which is why old guides recommend a "touch then read" PreToolUse hook; that workaround is obsolete). Single-file Bash reads trigger them since v2.1.293.

A subdirectory CLAUDE.md does not appear under **Memory files** in `/context` because it is not loaded at launch; a `Loaded <path>` line appears in the terminal when it loads.

## 4. Path-scoped rules

- `paths` is the only frontmatter field Claude Code reads from a rule. Any other key (`globs`, `alwaysApply`, `description`, `priority`, `include`, `applyTo`, `name`, `tools`) is ignored silently. A rule whose only scoping key is foreign therefore loads unconditionally.
- `paths` accepts a YAML list or a comma-separated string. Quote each glob: an unquoted value beginning with `*` is a YAML alias, `{` or `[` a flow collection, `!` a tag, `&` an anchor.
- If the frontmatter YAML does not parse, Claude Code ignores the frontmatter and loads the rule as if it had no `paths` (every session). `claude --debug` shows the parse error.
- Frontmatter is read only when the opening `---` is the first line.
- Directory names inside `.claude/rules/` are for humans: `.claude/rules/frontend/a11y.md` without `paths` loads in every session. Every `.md` under a rules directory is discovered recursively, including backups such as `old-api.md` or `backup/`.
- Base directory for patterns:
  - Project rule: the directory that contains the rule's `.claude` folder (for a nested `pkg/.claude/rules/x.md`, that is `pkg/`).
  - User rule: the session's primary working directory, not the home directory.
  - To match files in a sibling git worktree, start Claude in that worktree or move the session there with `/cd`.
- Glob behavior: `**/*.ts` recursive; `src/**/*` everything under `src/`; `*.md` root only; `src/components/*.tsx` direct children only. Brace expansion works (`src/**/*.{ts,tsx}`); a rule's whole `paths` list has a budget of 1,000 expanded patterns and 4 MiB, and an over-budget pattern is used unexpanded (its literal braces match nothing). A `[` that is not a valid bracket expression makes that one pattern invalid (it matches nothing; the others keep working); escape a literal `[` as `\[`.
- `.claude/rules/` supports symlinks to share rules across projects (circular links are handled). A link whose target is outside the working directory needs the one-time external-import approval, and after approval only the linked rules without `paths` load. Network-path targets (UNC shares, `/net`, `/Network`) are never followed. Edit and Write refuse to write through a symlink or into a symlinked directory and point at the target. To load shared rules without approval, keep them in `~/.claude/rules/`. In Cowork desktop sessions a symlinked `~/.claude/rules/` directory or rule pointing outside the working directory is skipped.

## 5. Imports

- `@path/to/file` in CLAUDE.md (and in AGENTS.md read directly) expands the file into context next to the importing file. Imports organize; they never reduce context cost.
- Relative paths resolve from the importing file. Absolute and `~/` paths work. Maximum recursive depth: four hops.
- Spaces need a backslash per space (`@Design\ Docs/api.md`); a quoted path is not imported. Code spans and fenced code blocks are skipped, so `` `@README` `` stays literal.
- An import in a project-level file that resolves outside the working directory triggers a one-time approval dialog per project; declining disables them. User-scope files import without the dialog, except in Cowork desktop sessions, which skip user-scope imports that resolve outside the session's working directory, and skip a `~/.claude/CLAUDE.md` that is itself a symlink or hard link (dotfile setups lose the whole user file there).
- A sentence such as "read docs/x.md" is not an import: Claude opens the file only if it decides to.

## 6. Size limits

| Limit | Applies to | Effect |
| :-- | :-- | :-- |
| Under 200 lines per CLAUDE.md | Guidance | Longer files cost context and reduce adherence. Not truncation. A startup and `/status` warning appears when a file is over the recommended length, and when many files together pass a combined limit (each CLAUDE.md, rule file and import counts separately; the combined number is not published) |
| 4 MiB | CLAUDE.md files that load at launch (documented); other instruction files are not covered by the docs | The file is skipped entirely |
| 40,000 characters (200K window); 150,000 (1M window, models after Opus 4.6 / Sonnet 4.6); 200,000 (1M, Opus 4.6 / Sonnet 4.6) | On-demand files: subdirectory CLAUDE.md/CLAUDE.local.md and their imports, rules in a subdirectory's `.claude/rules/`, path-scoped rules in the project or user rules | Claude receives only the start plus a note to read the rest; since v2.1.309. Measure with `wc -m` |
| 200 lines or 25 KB | Auto memory `MEMORY.md` only | The rest is not loaded at session start |

## 7. AGENTS.md interplay (v2.1.277+)

- Default (`claude-md-or-agents-md`): Claude reads AGENTS.md only when no CLAUDE.md, `.claude/CLAUDE.md` or CLAUDE.local.md exists in the working directory or above. `~/.claude/CLAUDE.md`, managed CLAUDE.md and `.claude/rules/` do not count for that check and keep loading.
- Adding a personal CLAUDE.local.md to a repository that relies on AGENTS.md stops AGENTS.md from loading for that user, unless Project instructions is `claude-md-and-agents-md`.
- `@AGENTS.md` inside a CLAUDE.md always works and never loads it twice. A CLAUDE.md that only says "read AGENTS.md" in words does not import it.
- Not read: `AGENTS.local.md`, `AGENTS.override.md`, `.agents/`.
- The setting lives in `/config` (Project instructions) or `pluginConfigs["cc-plugin-agents-md@builtin"].options.instructionFiles` in user, `--settings` or managed settings; project and local settings files are ignored for it. Before v2.1.285 the plugin ID was `agents-md@builtin` and the `cc-plugin-` key was ignored; v2.1.285+ reads either.

## 8. Exclusions, additional directories, symlinks

- `claudeMdExcludes` (any settings layer, arrays merge) skips CLAUDE.md and rules by absolute-path glob; it cannot exclude the managed file. Put personal exclusions in `.claude/settings.local.json`.
- `--add-dir` grants file access only; set `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` to load that directory's CLAUDE.md, `.claude/CLAUDE.md`, `.claude/rules/*.md` and CLAUDE.local.md. The `additionalDirectories` setting also grants access without loading instructions.
- Edit and Write refuse to write through a symlinked CLAUDE.md and point at the target.
- Writes into the project's `.claude/` folder (rules included) and into `~/.claude/` are protected-path writes: prompted in default and `acceptEdits` modes (the prompt offers a session-wide allowance for that folder), routed to the classifier in auto mode, allowed in `bypassPermissions` (and in plan mode in interactive terminal sessions where bypass permissions is available), and denied in `dontAsk`. `Edit(.claude/**)` allow rules do not pre-approve them. `.claude/CLAUDE.md` and `~/.claude/CLAUDE.md` are inside protected folders; a root `CLAUDE.md` or `CLAUDE.local.md` is not. A few paths inside `.claude` are exempt (Claude's worktrees, Markdown files in agent-memory directories); rules are not among them. Source: permission-modes, "Protected paths", checked 2026-10-28.

## 9. Compaction

Project-root CLAUDE.md is re-read from disk after `/compact` or auto-compaction. Nested CLAUDE.md files and path-scoped rules reload only when a matching file is touched again. An instruction given only in conversation does not survive compaction; put durable ones in a file.

## 10. How to observe what loaded

- `/context` lists the memory files loaded at launch under **Memory files**.
- `/memory` lists and opens CLAUDE.md, CLAUDE.local.md, auto memory and AGENTS.md read directly (v2.1.280+).
- `claude --debug` shows frontmatter parse errors.
- An `InstructionsLoaded` hook (observability only; cannot block) receives `file_path`, `memory_type`, `load_reason` (`session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`), `globs`, `trigger_file_path`, `parent_file_path`. It is the cleanest positive and negative test for a scoped rule.
- `/doctor prompt-audit` (alias `/checkup prompt-audit`, v2.1.283+, needs the bundled `/claude-api` skill enabled) proposes fixes for stale paths and commands, contradictions and old-model prompting; it changes nothing until asked. `/doctor` proposes trims for a checked-in CLAUDE.md.
- Asking Claude "which rules do you see?" is weak evidence, and asking it to read a rule file to test loading contaminates the test.

## 11. Common myths and the current fact

| Myth (seen in guides and generators) | Current fact |
| :-- | :-- |
| CLAUDE.local.md or a nested file "overrides" broader files; attention recency gives precedence | Files are concatenated; conflicts are resolved arbitrarily. Remove the conflict |
| Managed CLAUDE.md "cannot be overridden", so it enforces policy | It cannot be excluded, but it is still guidance; enforce with managed `permissions.deny`, sandbox, hooks |
| Instructions are followed "90-98%" of the time | No such figure is published |
| `globs:`, `alwaysApply:`, `description:` or `priority:` work in Claude rules | Only `paths` is read |
| Path-scoped rules miss newly written files, so add a PreToolUse touch-and-read hook | Fixed in v2.1.288: Write and Edit load matching rules |
| Splitting CLAUDE.md into `@imports` saves context | Imports load with the importer |
| A rules subfolder name scopes the rule | Only `paths` scopes |
| `/claude-api prompt-audit` is the way to audit instruction files | `/claude-api prompt-audit` (v2.1.221+) audits prompts, skills and tool descriptions; for CLAUDE.md, rules and the rest of `.claude/`, use `/doctor prompt-audit` (v2.1.283+), which runs through the bundled `/claude-api` skill |
| A PreToolUse hook that `sys.exit(1)`s blocks the edit | Exit 2 blocks; exit 1 is a non-blocking error |
| `IMPORTANT`/`CRITICAL`/caps make a line stick | Current models over-apply emphasized lines; shorten the file or move the rule to a hook |
| "think step by step" / "be thorough" deepen reasoning | Effort is the control; `ultrathink` works per turn |
| Describe the architecture and directory tree in CLAUDE.md | Claude reads the repo; keep only what it can't find or would rediscover each session |
| Every CLAUDE.md over 200 lines is truncated | 200 is guidance; truncation applies to on-demand files over the per-file character limit and to MEMORY.md |
