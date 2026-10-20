#!/usr/bin/env bash
# PreToolUse (Bash): runs the Python guard on the hook event, which Claude Code writes to stdin.
# Without Python 3.9 or later it says so and blocks nothing: with "onFailure": "block" a missing
# interpreter would otherwise block every Bash call, not only the git commands the guard watches.
# Past that check a crash is not hidden: its exit code reaches Claude Code, which then blocks.
set -u

notice() {
  printf '%s\n' '{"systemMessage":"block-no-verify is inactive: Python 3.9 or later was not found on PATH. Install it (see the plugin README), then run /reload-plugins.","hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"The block-no-verify guard did not run because Python 3.9 or later is missing, so Git bypass flags such as --no-verify are not being blocked."}}'
  exit 0
}

# Fails when python3 is missing, too old, or a stub that cannot run.
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' > /dev/null 2>&1 || notice

here=${0%/*}
[[ ${here} != "${0}" ]] || here=.
exec python3 "${here}/block_no_verify.py"
