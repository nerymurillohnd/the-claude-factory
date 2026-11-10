#!/usr/bin/env bash
# PreToolUse hook for Write and Edit: a governed document is written only by
# the agent that owns it. Reads the hook input on stdin.
set -uo pipefail
here="$(dirname "$0")"
# shellcheck source=.claude/hooks/docs-lib.sh
. "${here}/docs-lib.sh"
docs_require

input="$(cat)"
file="$(docs_field "${input}" '.tool_input.file_path')"
[[ -n "${file}" ]] || exit 0

rel="$(docs_relpath "${file}")"
found="$(docs_lookup "${rel}")"
[[ -n "${found}" ]] || exit 0

owner="${found%% *}"
agent="$(docs_field "${input}" '.agent_type')"
[[ "${agent}" == "${owner}" ]] && exit 0

reason="${rel} is a governed document owned by the ${owner} agent. Load the documentation-governance skill and run the chain for this change instead of writing the file directly."
jq -n --arg r "${reason}" \
  '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
