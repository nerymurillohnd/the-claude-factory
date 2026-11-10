#!/usr/bin/env bash
# PostToolUse and SubagentStop hook: runs the document checks on what was just
# written and blocks when they fail. Reads the hook input on stdin.
#
# PostToolUse checks the file the tool wrote. SubagentStop checks every
# changed document the stopping agent owns.
set -uo pipefail
here="$(dirname "$0")"
scripts="${here}/../skills/documentation-governance/scripts"
# shellcheck source=.claude/skills/documentation-governance/scripts/lib.sh
. "${scripts}/lib.sh"
docs_require

input="$(cat)"
event="$(docs_field "${input}" '.hook_event_name')"
problems=""

case "${event}" in
  PostToolUse)
    file="$(docs_field "${input}" '.tool_input.file_path')"
    [[ -n "${file}" ]] || exit 0
    problems="$("${scripts}/check-document.sh" "${file}" || true)"
    ;;
  SubagentStop)
    # Let the agent stop on the second pass, so a check it cannot satisfy
    # never loops; the independent review still sees the result.
    active="$(docs_field "${input}" '.stop_hook_active')"
    [[ "${active}" == "true" ]] && exit 0
    agent="$(docs_field "${input}" '.agent_type')"
    [[ -n "${agent}" ]] || exit 0
    changed="$(git -C "${DOCS_ROOT}" status --porcelain --untracked-files=all 2>/dev/null || true)"
    files=()
    while IFS= read -r line; do
      [[ -n "${line}" ]] && files+=("${line:3}")
    done <<<"${changed}"
    [[ "${#files[@]}" -gt 0 ]] || exit 0
    problems="$("${scripts}/check-document.sh" --owner "${agent}" "${files[@]}" || true)"
    ;;
  *) exit 0 ;;
esac

[[ -n "${problems}" ]] || exit 0
jq -n --arg p "${problems}" \
  '{decision: "block", reason: ("Documentation checks failed. Fix each line:\n" + $p)}'
