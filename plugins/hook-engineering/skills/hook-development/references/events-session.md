# Session lifecycle events

SessionStart · Setup · InstructionsLoaded · SessionEnd

Sources: https://code.claude.com/docs/en/hooks and the Claude Code CHANGELOG.md; changelog-only facts are tagged *(changelog vX.Y.Z)*. Fields listed are in addition to the common input fields.

---

## Contents

- SessionStart
- Setup
- InstructionsLoaded
- SessionEnd

## SessionStart

Docs: [event](https://code.claude.com/docs/en/hooks#sessionstart) · [input](https://code.claude.com/docs/en/hooks#sessionstart-input) · [decision control](https://code.claude.com/docs/en/hooks#sessionstart-decision-control)

**Fires:** a new or resumed session starts. Runs on every session, so keep it fast. For static context, CLAUDE.md is the better tool.

**Handlers:** `command` and `mcp_tool` only.

**Matcher → `source`:**

| Value | When |
|---|---|
| `startup` | new session |
| `resume` | `--resume`, `--continue`, `/resume` |
| `clear` | `/clear` |
| `compact` | auto or manual compaction |
| `fork` | `--fork-session` with `--resume`/`--continue`, `/fork` background copy, `/branch`, or a conversation moved to the background |

**Timing:** at launch, `--continue`/`--resume` at launch, and `/clear`, hooks run in the background: the user can type immediately, but Claude's first response waits for them. `/resume` inside a session waits for the hooks before switching. If the user runs `/clear` or switches while background hooks still run, their output is discarded. Esc pulls a waiting prompt back into the input; hooks keep running.

**Input:**

| Field | Notes |
|---|---|
| `source` | as matcher table |
| `model` | optional; can be missing (after `/clear`, conversation recovery). Check before reading. Only SessionStart ever gets `model` |
| `agent_type` | present with `claude --agent <name>` |
| `session_title` | custom title only (`--name`, `/rename`, a hook's `sessionTitle`, SDK `renameSession()`); generated titles don't appear |

When `source` is `resume` or `fork` and the transcript has at least one Claude response (v2.1.251+): `seconds_since_last_response`, `context_tokens`, `prompt_cache_likely_expired`, `estimated_cache_write_usd`. Use them to warn about the cost of resuming a stale conversation (e.g. via `systemMessage`).

**Output (`hookSpecificOutput`, `hookEventName: "SessionStart"`):**

| Field | Effect |
|---|---|
| `additionalContext` | added to Claude's context before the first prompt. Plain-text stdout does the same without JSON |
| `initialUserMessage` | first user message, only in `-p` mode; becomes the first turn even with no prompt passed |
| `sessionTitle` | like `/rename`; applies for `startup`, `resume`, `fork` |
| `watchPaths` | absolute paths to watch for `FileChanged` |
| `reloadSkills` | `true` → re-scan skill/command directories after SessionStart hooks finish |

A plugin's `initialUserMessage`/`sessionTitle` is ignored if the plugin finished installing after SessionStart hooks ran.

**Reload skills:** skill discovery runs before SessionStart hooks finish, so a hook that writes into `~/.claude/skills/` or `.claude/skills/` must return `reloadSkills: true` for those skills to exist on the first prompt.

**`CLAUDE_ENV_FILE`:** append (`>>`) `export` lines to persist env vars into later Bash commands. Each Bash command sources the file first, so `$PATH` references work. To capture everything a setup command changed, diff `export -p | sort` before and after and append the new lines.

**`CLAUDE_ENV_FILE` available on:** `SessionStart`, `Setup`, `CwdChanged`, `FileChanged` only, and never for hooks running in PowerShell.

PowerShell commands (v2.1.296+) get these variables only if every line in the file is blank, a `#` comment, or one plain assignment (`export NAME=value`, `declare -x NAME=value`, `NAME=value`) whose value Bash would use literally: unquoted `[A-Za-z0-9_@%+=:,./-]`, single-quoted text, or double-quoted text with `$`, backtick and `"` escaped. One non-conforming line (unescaped `$PATH`, `source`, direnv's `$'...'`) and PowerShell gets none of them; debug log says `Session environment is not all plain assignments`. On Windows, values containing `/` or `\` never reach PowerShell. Sandboxed PowerShell gets none. A hook that itself runs in PowerShell has no `CLAUDE_ENV_FILE`.

**Exit 2:** can't block; stderr shown to the user as a `<hook name> hook error` notice; Claude doesn't see it.

**VS Code:** time a SessionStart command hook spends running no longer counts toward the 60 s session-start limit, up to 10 minutes in total *(changelog v2.1.304)*; v2.1.305 shows a "Running start-up hooks" status while SessionStart or Setup hooks run.

---

## Setup

Docs: [event](https://code.claude.com/docs/en/hooks#setup) · [input](https://code.claude.com/docs/en/hooks#setup-input) · [decision control](https://code.claude.com/docs/en/hooks#setup-decision-control)

**Fires:** only with `claude --init-only`, or `-p` with `--init` or `--maintenance`. Never on a normal start. Use for one-time installs or scheduled cleanup driven from CI or scripts. `--init-only` runs Setup, then SessionStart `startup` hooks, then exits without a conversation and prints nothing on success; confirm with `claude --debug-file <path> --init-only`. With `-p`, a prompt is still required (argument or stdin) unless a SessionStart hook supplies `initialUserMessage` or a deferred tool call is being resumed.

**Handlers:** `command` only in practice (`mcp_tool` on Setup is always skipped).

**Matcher → `trigger`:** `init` (`--init-only`, `-p --init`), `maintenance` (`-p --maintenance`).

**Input:** `trigger`.

**Output:** none. Can't block on any exit code; all JSON output fields are discarded. With `-p`, stdout/stderr/exit code appear only as `hook_response` events under `--output-format stream-json --verbose`. `CLAUDE_ENV_FILE` is available.

Docs and engine can disagree on `additionalContext`. The docs say Setup discards every JSON output field, while the mod declarations the installed build writes (`.claude-plugin/types/claude-code/index.d.ts`, `ClassicResultFields`) can list it as a field Setup reads. Check the installed build before you rely on either:

1. Run `claude --settings <file> --init-only --debug-file <path>` with a Setup hook that prints `additionalContext`.
2. Look in the log for `Hook Setup (...) provided additionalContext`: it shows the engine reads the field.
3. Treat whether that text reaches Claude under `-p --init` as unverified: `--init-only` opens no conversation.

Don't design a hook that depends on it, and report the disagreement.

**Plugin pattern:** don't rely on Setup to install a plugin dependency, since it rarely runs. Check on first use and install on miss (e.g. test `${CLAUDE_PLUGIN_DATA}/node_modules`). Marketplace plugins may get eligible Node.js dependencies installed automatically when cached.

---

## InstructionsLoaded

Docs: [event](https://code.claude.com/docs/en/hooks#instructionsloaded) · [input](https://code.claude.com/docs/en/hooks#instructionsloaded-input) · [decision control](https://code.claude.com/docs/en/hooks#instructionsloaded-decision-control)

**Fires:** a CLAUDE.md or `.claude/rules/*.md` loads into context: eagerly at session start, and lazily later (nested CLAUDE.md in a subdirectory Claude touches, conditional rules whose `paths:` match). Runs asynchronously, for observability.

Doesn't fire when Claude reads AGENTS.md directly via the Project instructions setting. Does fire when a CLAUDE.md imports AGENTS.md (`load_reason: include`) or CLAUDE.md is a symlink to it.

**Matcher → `load_reason`:** `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` (re-load after compaction). E.g. `path_glob_match|nested_traversal` for lazy loads only.

**Input:**

| Field | Notes |
|---|---|
| `file_path` | absolute path of the loaded file |
| `memory_type` | `User`, `Project`, `Local`, `Managed` |
| `load_reason` | as above |
| `globs` | `paths:` patterns; only for `path_glob_match` |
| `trigger_file_path` | file whose access caused a lazy load |
| `parent_file_path` | including file, for `include` |

**Output:** no decision control; can't block or modify loading; JSON fields such as `systemMessage` and `continue` are discarded; exit code ignored. Use for audit and compliance logging.

---

## SessionEnd

Docs: [event](https://code.claude.com/docs/en/hooks#sessionend) · [input](https://code.claude.com/docs/en/hooks#sessionend-input)

**Fires:** session ends.

**Matcher → `reason`:** `clear` (`/clear`), `resume` (interactive `/resume` switch), `logout`, `prompt_input_exit` (exited with the prompt input visible), `other`. `bypass_permissions_disabled` was removed in v2.1.234 and is never sent; drop it from matchers.

**Input:** `reason`.

**Output:** can't block; JSON fields (incl. `systemMessage`) discarded; exit 2 shows stderr to the user only.

Before v2.1.300, SessionEnd hooks sometimes didn't run when the user exited while a background command was still running *(changelog)*.

**Timeout (the usual failure):** default 1.5 s budget on exit, `/clear`, interactive `/resume`. Raise it by:
- a per-hook `timeout` in settings files: the overall budget rises to the highest such timeout, up to 60 s; hooks without their own `timeout` still keep 1.5 s. Plugin-provided hook timeouts don't raise the budget.
- `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`: sets the budget explicitly and, since v2.1.268, also the per-hook timeout for hooks without their own.
