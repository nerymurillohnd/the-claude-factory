#!/usr/bin/env bash
# skill-diagnostics PermissionRequest hook for Bash. The skill's allowed-tools approve its scripts
# only during the turn that invokes it; agent results arrive in later turns, where the same
# commands would ask the user. This hook answers that prompt with allow, and only when the command
# is exactly one of the skill's own scripts run the way SKILL.md writes it:
#   python3 <plugin root>/skills/skills-best-practices/scripts/<script>.py <arguments>
# with <script> one of check-metadata, check-structure, check-runtime, check-size, check-evals
# and record-verdict, and no shell operator, substitution or redirect in the arguments.
# Anything else prints nothing, so the user is asked as usual. It never denies, never adds a
# permission rule (it ignores permission_suggestions, which would write to the user's settings),
# and the user's deny and ask rules still apply before it.
# Needs bash 3.2+ and jq; without jq it prints nothing and the prompt appears. Exits 0.
set -uo pipefail
export LC_ALL=C
unset CDPATH

root=${CLAUDE_PLUGIN_ROOT:-}
if [[ -z ${root} ]] || ! command -v jq > /dev/null 2>&1; then
  exit 0
fi
input=$(cat)
command=$(printf '%s' "${input}" | jq -r 'if .tool_name == "Bash" then .tool_input.command // empty | strings else empty end' 2> /dev/null) || exit 0
[[ -n ${command} ]] || exit 0

prefix="python3 ${root%/}/skills/skills-best-practices/scripts/"
[[ ${command} == "${prefix}"* ]] || exit 0
rest=${command#"${prefix}"}
script=${rest%%[[:space:]]*}
case "${script}" in
  check-metadata.py | check-structure.py | check-runtime.py | check-size.py | check-evals.py | record-verdict.py) ;;
  *) exit 0 ;;
esac
arguments=${rest#"${script}"}
case "${arguments}" in
  '' | [[:space:]]*) ;;
  *) exit 0 ;;
esac
# No operator, substitution, redirect, escape or line break: the command runs only that script.
case "${arguments}" in
  *[\;\&\|\`\$\<\>\(\)\\]* | *$'\n'* | *$'\r'*) exit 0 ;;
  *) ;;
esac

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'
exit 0
