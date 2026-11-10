#!/usr/bin/env bash
# PostToolUse and Stop hook: tells the main session which documentation chains
# its changes have set off. Reads the hook input on stdin.
set -uo pipefail
here="$(dirname "$0")"
scripts="${here}/../skills/documentation-governance/scripts"
# shellcheck source=.claude/skills/documentation-governance/scripts/lib.sh
. "${scripts}/lib.sh"
docs_require

input="$(cat)"
event="$(docs_field "${input}" '.hook_event_name')"
case "${event}" in
  Stop | PostToolUse) ;;
  *) exit 0 ;;
esac

# Only the main session is told: a writer agent is itself running the chain.
agent="$(docs_field "${input}" '.agent_type')"
[[ -z "${agent}" ]] || exit 0
# One reminder per turn is enough; the second pass lets the turn end.
active="$(docs_field "${input}" '.stop_hook_active')"
[[ "${active}" == "true" ]] && exit 0
# A chain that is running has not written its documents yet.
running="$(docs_field "${input}" '[.background_tasks[]? | select(.type == "workflow" and .name == "documentation-chain")] | length')"
[[ "${running:-0}" == "0" ]] || exit 0

list="$("${scripts}/pending-chains.sh" || true)"
[[ -n "${list}" ]] || exit 0

jq -n --arg e "${event}" --arg l "${list}" \
  '{hookSpecificOutput: {hookEventName: $e, additionalContext: ("Documentation chains are pending for changes in this working tree, one per line as <chain> <plugin>:\n" + $l + "\nLoad the documentation-governance skill and run each chain. If a change has no effect a user would notice, say so and leave the documents as they are.")}}'
