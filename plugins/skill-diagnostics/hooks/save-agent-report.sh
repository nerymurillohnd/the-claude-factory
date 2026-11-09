#!/usr/bin/env bash
# skill-diagnostics hook that saves each audit agent's report unchanged, so the main session can
# be checked against what every agent found. It runs on two events (hooks/hooks.json):
#   SubagentStop, matched on this plugin's six agents: the report is last_assistant_message.
#   PostToolUse on SubagentHandback (auto mode): the report is tool_input.message, and the agent
#     is agent_type; tool calls of other agents are ignored.
# Writes ${CLAUDE_PLUGIN_DATA}/audits/<session_id>/agents/<agent>-<agent_id>.md. A report that
# SubagentHandback already saved is not overwritten by the closing text SubagentStop carries.
# session-start.sh deletes audit folders older than 7 days. Prints nothing; it never blocks.
# Needs bash 3.2+ and jq. When a command fails it writes the error to stderr and exits 1.
set -euo pipefail
export LC_ALL=C
unset CDPATH

# Any failure exits 1, never 2: exit 2 would keep the subagent running.
trap '[[ $? -eq 0 ]] || { echo "skill-diagnostics: save-agent-report.sh failed" >&2; exit 1; }' EXIT

die() {
  printf 'skill-diagnostics: %s\n' "$1" >&2
  exit 1
}

data=${CLAUDE_PLUGIN_DATA:-}
if [[ -z ${data} ]]; then
  die 'CLAUDE_PLUGIN_DATA is not set'
fi

input=$(cat)
if ! printf '%s' "${input}" | jq -e 'type == "object"' > /dev/null; then
  die 'cannot read the hook input: jq is missing or the input is not a JSON object'
fi
field() {
  printf '%s' "${input}" | jq -r "$1 // empty | strings"
}
event=$(field .hook_event_name)
session_id=$(field .session_id)
agent_id=$(field .agent_id)
agent=$(field .agent_type)
agent=${agent#skill-diagnostics:}
case "${agent}" in
  description-reviewer | instructions-reviewer | scripts-runtime-reviewer | security-reviewer | \
    cold-executor | adversarial-verifier) ;;
  *) exit 0 ;;
esac
for value in "${session_id}" "${agent_id}"; do
  case "${value}" in
    '' | . | .. | *[!A-Za-z0-9._-]*) die 'the hook input has no usable session_id or agent_id' ;;
    *) ;;
  esac
done

case "${event}" in
  SubagentStop) report=$(field .last_assistant_message) ;;
  PostToolUse) report=$(field .tool_input.message) ;;
  *) exit 0 ;;
esac
if [[ -z ${report//[[:space:]]/} ]]; then
  exit 0
fi

folder="${data}/audits/${session_id}/agents"
target="${folder}/${agent}-${agent_id}.md"
if [[ ${event} == SubagentStop ]] && [[ -f ${target} ]]; then
  exit 0
fi
mkdir -p "${folder}"
temporary="${target}.$$.tmp"
printf '%s\n' "${report}" > "${temporary}"
mv -f "${temporary}" "${target}"
exit 0
