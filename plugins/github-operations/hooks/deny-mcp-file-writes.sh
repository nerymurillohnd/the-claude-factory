#!/usr/bin/env bash
# PreToolUse guard for the GitHub MCP tools that write repository files (push_files,
# create_or_update_file, delete_file). The matcher alone decides, so the input is not read:
# every call is denied, because those commits skip the user's local hooks and signing.
set -euo pipefail
printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"github-operations: do not write repository files through the GitHub MCP server; those commits skip local hooks and signing. Edit the files in the clone, commit with git and push."}}'
