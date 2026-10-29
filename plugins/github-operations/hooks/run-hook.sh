#!/usr/bin/env bash
# Launcher for github-operations' hooks: runs github_hooks.py <handler> with python3 3.12 or
# later. Without a usable python3 the guards deny only the calls they guard, and the
# compaction hook says why the state was not restored.
# No -e: the fallback must still print its decision when a check fails.
set -uo pipefail

handler=${1:-}
root=${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}

if command -v python3 > /dev/null 2>&1 \
  && python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 12))' > /dev/null 2>&1; then
  exec python3 "${root}/hooks/github_hooks.py" "${handler}"
fi

payload=$(cat)
reason='github-operations: python3 3.12 or later is needed to check this call and is not installed; install python3 3.12+, then run /reload-plugins.'

deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "${reason}"
}

# Only what the call sends is searched: the cwd and other fields could name a folder "git".
call=${payload#*\"tool_input\"}
case ${handler} in
  shell)
    if printf '%s' "${call}" | grep -Eq '(^|[^A-Za-z0-9_.-])(git|gh|curl)([^A-Za-z0-9_-]|$)'; then
      deny
    fi
    ;;
  mcp)
    if printf '%s' "${payload}" | grep -Eq 'merge_pull_request|"agent_type" *: *"github-operations:'; then
      deny
    fi
    ;;
  files)
    if printf '%s' "${payload}" | grep -Eq '"agent_type" *: *"github-operations:'; then
      deny
    fi
    ;;
  compact)
    printf '%s\n' '{"systemMessage":"github-operations: python3 3.12 or later is not installed; state was not restored."}'
    ;;
  *)
    deny
    ;;
esac
exit 0
