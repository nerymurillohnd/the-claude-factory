#!/usr/bin/env bash
# Lists hook-related Claude Code changelog entries released after a given version.
#
# Usage: bash hook-changes.sh <since-version> [installed-version]
#   since-version      the skill's "Changelog baseline" version, or the installed version to list
#                      what that version lacks; entries at or below it are skipped
#   installed-version  optional, e.g. from `claude --version`; entries above it are tagged [newer than installed]
#
# Source: the CHANGELOG.md in github.com/anthropics/claude-code, which is published
# before the docs site catches up. Requires curl and awk on PATH. Exits 3 when the
# changelog can't be downloaded or read, so a network failure never reads as "no changes".

set -euo pipefail

usage="usage: hook-changes.sh <since-version> [installed-version] (bare numbers like 2.1.305, no leading v)"
since="${1:?${usage}}"
installed="${2:-}"
for version in "${since}" "${installed}"; do
  if [[ -n ${version} && ! ${version} =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "hook-changes.sh: '${version}' is not a bare version number. ${usage}" >&2
    exit 2
  fi
done
url="https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

events='SessionStart|Setup|InstructionsLoaded|UserPromptSubmit|UserPromptExpansion|MessageDisplay|PreToolUse|PermissionRequest|PostToolUse|PostToolUseFailure|PostToolBatch|PermissionDenied|Notification|SubagentStart|SubagentStop|TaskCreated|TaskCompleted|StopFailure|TeammateIdle|ConfigChange|CwdChanged|DirectoryAdded|FileChanged|WorktreeCreate|WorktreeRemove|PreCompact|PostCompact|PreModelSwitch|PostModelSwitch|SessionEnd|Elicitation|ElicitationResult'
terms="[Hh]ook|${events}|CLAUDE_ENV_FILE|hookSpecificOutput|additionalContext|permissionDecision|updatedInput|updatedToolOutput|watchPaths|initialUserMessage|reloadSkills|stop_hook_active|matcher|asyncRewake|ARGUMENTS|continueOnBlock|[Tt]rust"

if ! changelog=$(curl -fsSL "${url}"); then
  echo "hook-changes.sh: could not download ${url}; the changelog was not checked, so treat version-sensitive conclusions as unverified." >&2
  exit 3
fi

printf '%s\n' "${changelog}" | awk -v since="${since}" -v installed="${installed}" -v terms="${terms}" -v url="${url}" '
  function cmp(a, b,   x, y, i, n) {
    n = split(a, x, "."); split(b, y, ".")
    for (i = 1; i <= 3; i++) { if ((x[i] + 0) != (y[i] + 0)) return (x[i] + 0) < (y[i] + 0) ? -1 : 1 }
    return 0
  }
  done { next }
  /^## [0-9]+\.[0-9]+\.[0-9]+/ {
    ver = $2
    headings++
    if (cmp(ver, since) <= 0) { done = 1; next }
    tag = (installed != "" && cmp(ver, installed) > 0) ? " [newer than installed]" : ""
    printed = 0
    next
  }
  ver != "" && /^[[:space:]]*[-*] / && $0 ~ terms {
    if (!printed) { print "## " ver tag; printed = 1; found++ }
    sub(/^[[:space:]]*[-*] /, "- ")
    print
  }
  END {
    if (!headings) {
      print "hook-changes.sh: " url " has no version headings; the changelog was not checked, so treat version-sensitive conclusions as unverified." > "/dev/stderr"
      exit 3
    }
    if (!found) print "No hook-related changelog entries after " since "."
  }
'
