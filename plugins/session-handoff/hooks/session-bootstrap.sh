#!/usr/bin/env bash
# SessionStart (startup, clear): when the project holds a session handoff, tell Claude to read the
# newest one and ask the user how to proceed. A project without handoffs gets no output, so the
# plugin stays silent there. The instructions are fixed text; Claude finds and reads the file.
set -euo pipefail

store="${CLAUDE_PROJECT_DIR:-.}/.claude/session-handoff"
# The path stays literal (a project path may hold [, ], * or \); only the file name is a pattern.
LC_ALL=C # digit ranges match only 0-9
found=0
for handoff in "${store}"/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9].md; do
  [[ -f ${handoff} ]] && found=1 && break
done
[[ ${found} == 1 ]] || exit 0

cat << 'JSON'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "SESSION START PROTOCOL — Complete this before addressing the user's initial request:\n1. From the project root, find the newest previous-session handoff in .claude/session-handoff/: its files are named YYYY-MM-DD-HHMM.md, so the last such name is the newest. Do not confuse the project root with the plugin directory.\n2. Read the selected handoff completely, not just an excerpt or summary. If it cannot be read completely, state that clearly; never claim to have read it.\n3. Return to the user's initial input and preserve it as the current request. Do not replace it with the handoff's pending tasks or execute either set of tasks yet.\n4. In your first response, use the user's language, confirm which handoff you read, provide a concise summary that demonstrates actual understanding, and explicitly highlight its pending tasks. Distinguish the handoff's recorded state from independently verified current state.\n5. Ask the user to choose how to proceed: (a) address the initial request now and defer the handoff's pending tasks; (b) resume the pending tasks and defer the initial request; or (c) specify another approach. Wait for the user's decision before starting substantive work. In a non-interactive run, such as claude -p, where no one can answer, skip the question and proceed with the initial request. If no readable handoff exists, report that limitation and proceed with the initial request unless another clarification is necessary."
  }
}
JSON
