# Configuration, directory, file and worktree events

ConfigChange · CwdChanged · DirectoryAdded · FileChanged · WorktreeCreate · WorktreeRemove

Sources: https://code.claude.com/docs/en/hooks and the Claude Code CHANGELOG.md; changelog-only facts are tagged *(changelog vX.Y.Z)*. Fields listed are in addition to the common input fields. All six support `command`, `http`, `mcp_tool` handlers only.

---

## Contents

- ConfigChange
- CwdChanged
- DirectoryAdded
- FileChanged
- WorktreeCreate
- WorktreeRemove

## ConfigChange

Docs: [event](https://code.claude.com/docs/en/hooks#configchange) · [input](https://code.claude.com/docs/en/hooks#configchange-input) · [decision control](https://code.claude.com/docs/en/hooks#configchange-decision-control)

**Fires:** during a session, when a settings file, a managed policy file (`managed-settings.json` or a file in `managed-settings.d/`), or a skill file changes. Not for server-managed settings, macOS managed preferences, Windows registry policy, or WSL `wslInheritsWindowsSettings` policy polls.

**Matcher → `source`:** `user_settings` (`~/.claude/settings.json`), `project_settings` (`.claude/settings.json`), `local_settings` (`.claude/settings.local.json`), `policy_settings`, `skills` (`.claude/skills/`).

**Input:** `source`, `file_path?`.

**Output:** top-level `decision: "block"` or exit 2 keeps the new settings out of the running session. `reason` is accepted but never shown; a block surfaces nothing to the user or Claude, only a debug-log line. `systemMessage` and `continue` discarded. `policy_settings` can't be blocked (hooks still fire, useful for logging). Use for auditing settings edits or enforcing change policy.

---

## CwdChanged

Docs: [event](https://code.claude.com/docs/en/hooks#cwdchanged) · [input](https://code.claude.com/docs/en/hooks#cwdchanged-input) · [output](https://code.claude.com/docs/en/hooks#cwdchanged-output)

**Fires:** a shell command in the main conversation changes the working directory (e.g. Claude runs `cd`).

**Matcher:** none.

**Input:** `old_cwd`, `new_cwd`.

**Output:** `watchPaths` (absolute paths) replaces the dynamic FileChanged watch list; matcher-configured paths stay watched; `[]` clears the dynamic list, typical on entering a new directory. `systemMessage` shows as a brief terminal notification in interactive sessions (not in the SDK stream); `continue` discarded. Can't block.

**`CLAUDE_ENV_FILE`:** available; variables written persist into later Bash commands until the next CwdChanged, which clears them. Pair with FileChanged for direnv-style setups.

---

## DirectoryAdded

Docs: [event](https://code.claude.com/docs/en/hooks#directoryadded) · [input](https://code.claude.com/docs/en/hooks#directoryadded-input)

**Fires:** after a working directory is added mid-session with `/add-dir` or the SDK `register_repo_root` control request. Not for `--add-dir` at startup (SessionStart covers those), the `/permissions` Workspace tab, or a directory already inside a working directory. Sandbox and permission state are refreshed first; the hook itself runs unsandboxed, in the background, 600 s default timeout; the add completes immediately.

**Matcher → `source`:** `slash_command`, `register_repo_root`.

**Input:** `directory` (absolute), `source`.

**Output:** can't block (already done); `continue` discarded. `slash_command`: `systemMessage` goes to Claude as context on the next turn (not shown to the user); a failed-hook count appears in the transcript; failure details go to the debug log. `register_repo_root`: `systemMessage` and failures go to the debug log only. Exit 2 stderr → debug log.

Use for preparing the added repo, e.g. installing its dependencies.

---

## FileChanged

Docs: [event](https://code.claude.com/docs/en/hooks#filechanged) · [input](https://code.claude.com/docs/en/hooks#filechanged-input) · [output](https://code.claude.com/docs/en/hooks#filechanged-output)

**Fires:** a watched file changes on disk, detected by a filesystem watcher, so it fires whatever changed the file: Edit/Write, a Bash script, or an external process. Fires after the change; can't block it.

**Matcher has two roles:**
1. **Watch list:** split on `|`, each segment registered as a literal filename in the working directory. `.envrc|.env` watches those two files. Regex is useless here: `^\.env` watches a file literally named `^\.env`; `*` registers a file literally named `*`.
2. **Filter:** when a watched file changes, the same value filters hook groups against the changed file's basename with normal matcher rules (exact set for this event: letters, digits, `_`, `|`; a hyphen, space or comma → regex).

**Dynamic watching:** return `watchPaths` from a FileChanged, SessionStart or CwdChanged hook. The watcher starts only once something names a file, so seed it with a FileChanged group that names at least one file, or a SessionStart/CwdChanged hook returning `watchPaths`. Give the group handling dynamic paths an omitted matcher (matches every watched file, adds nothing to the list).

**Input:** `file_path` (absolute), `event` (`change`, `add`, `unlink`).

**Output:** `watchPaths` replaces the dynamic watch list (matcher paths stay). `systemMessage` → brief terminal notification in interactive sessions; `continue` discarded. Exit 2 shows stderr to the user.

**`CLAUDE_ENV_FILE`:** available; persists until the next CwdChanged.

**Loop trap:** a hook that rewrites the watched file fires itself again. Guard on exactly the condition the rewrite removes (e.g. `grep -q $'\r$'` before `perl -pi -e 's/\r$//'`), since tools like `perl -i` rewrite even when nothing changes.

---

## WorktreeCreate

Docs: [event](https://code.claude.com/docs/en/hooks#worktreecreate) · [input](https://code.claude.com/docs/en/hooks#worktreecreate-input) · [output](https://code.claude.com/docs/en/hooks#worktreecreate-output)

**Fires:** Claude Code creates a worktree: `claude --worktree`, the `EnterWorktree` tool, a subagent with `isolation: "worktree"`, a workflow agent in its own worktree, background-session isolation, `claude remote-control` in worktree mode. Not when Claude runs `git worktree add` via Bash (use PreToolUse on `Bash`).

**Matcher:** none.

Plugin WorktreeCreate and WorktreeRemove hooks didn't run when Claude Code started with `--worktree` before v2.1.300, and still don't with `--tmux` *(changelog v2.1.300)*.

Configuring this hook **replaces** the default `git worktree` behavior entirely (use for SVN, Perforce, Mercurial). `.worktreeinclude` is no longer processed; copy `.env` and similar inside the hook.

**Input:** `name` (slug, user-given or generated like `bold-oak-a3f2`).

**Output:** the created directory path. Command hook: last non-empty stdout line (ANSI codes stripped, so shell banners before it are fine; send everything else to stderr). HTTP hook: `hookSpecificOutput.worktreePath`. Failure or no path → creation fails. Relative paths resolve against the hook's directory with `.`/`..` collapsed; an absolute path with `.`/`..` segments, or any path through a symlink below the repo root, is refused (since v2.1.216). A path that isn't an enterable directory → error, exit code 1. `systemMessage`/`continue` discarded. Any non-zero exit fails creation.

---

## WorktreeRemove

Docs: [event](https://code.claude.com/docs/en/hooks#worktreeremove) · [input](https://code.claude.com/docs/en/hooks#worktreeremove-input)

**Fires:** cleanup of a worktree a WorktreeCreate hook made: user exits a worktree session and chooses removal; exits an unnamed one with no changed/untracked files (auto-removed); deletes a background session; `ExitWorktree` tool; `remote-control` session ends cleanly or is stopped with no changes, untracked files or new commits.

Not fired when a subagent or workflow agent finishes: their hook-created worktrees are kept; remove them yourself.

Before v2.1.301, quitting could remove a hook-created worktree without asking even when it might hold unpushed commits *(changelog)*.

No user prompt precedes `ExitWorktree` or `remote-control` cleanup. `ExitWorktree` refuses a hook-created worktree unless `discard_changes: true`, so the hook is the last check. "No changes" is detected via git, so a non-git worktree always looks clean: check for uncommitted work in the hook before deleting.

**Matcher:** none.

**Without a WorktreeRemove hook:** exit/`ExitWorktree` → removed like `git worktree remove --force` (a non-git worktree stays on disk); `remote-control` cleanup → kept (`worktree removal failed, kept: <path>`).

**Input:** `worktree_path` (absolute).

**Outcome by exit code:** 0 → counts as removed (Claude Code reads nothing else, so actually delete the directory). Non-zero → fails only if the directory still exists afterward; no git fallback; command and stderr to debug log; agent view reports how the hook ended; `remote-control` shows `worktree removal failed, kept: <path>`. Branches are never deleted by Claude Code for hook worktrees: delete any branch your WorktreeCreate made here. JSON output fields discarded.

Background-session delete verifies the stored path first and refuses symlinks below the repo root (v2.1.216+); for a worktree with files, the hook runs only after confirmation in agent view, and `claude rm` keeps the session instead.
