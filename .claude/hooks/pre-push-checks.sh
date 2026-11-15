#!/usr/bin/env bash
# PreToolUse gate for `git push`: the push goes out only when `npm run check:pr` passes, so a
# branch that would fail Validate's Checks job never reaches GitHub.
#
# It runs scripts/validators/pr-checks.sh, the source the Checks job shares, and blocks (exit 2)
# with the failed steps and their output on stderr. It is a gate: anything it can't run blocks too,
# and its handler sets onFailure "block" for a crash or a timeout.
set -euo pipefail

block() {
  printf '%s\n' "$1" >&2
  exit 2
}

# The `if` filter is best effort: it also runs the hook for any command holding $VAR, $() or
# backticks, so the command itself decides whether this is a push.
command -v jq > /dev/null || block "pre-push checks: jq is not installed, so the hook can't read the command; the push is blocked."
input="$(cat)"
cmd="$(jq -r '.tool_input.command // empty' <<< "${input}" 2> /dev/null)" \
  || block "pre-push checks: the hook input is not JSON; the push is blocked."
# A push is `git`, any global options (each with an optional value, such as -C <dir>), then `push`
# as the subcommand, so `git stash push` is not one.
push_re='(^|[^[:alnum:]_.-])git([[:space:]]+-[^;&|[:space:]]+([[:space:]]+[^-;&|[:space:]][^;&|[:space:]]*)?)*[[:space:]]+push([[:space:]]|$)'
if ! grep -Eq "${push_re}" <<< "${cmd}"; then
  exit 0
fi

root="${CLAUDE_PROJECT_DIR:-}"
[[ -n ${root} && -d ${root} ]] || block "pre-push checks: CLAUDE_PROJECT_DIR is not set, so the checks can't run; the push is blocked."
cd "${root}"
[[ -f scripts/validators/pr-checks.sh ]] || block "pre-push checks: scripts/validators/pr-checks.sh is missing, so the checks can't run; the push is blocked."

log="$(mktemp)"
trap 'rm -f "${log}"' EXIT

if bash scripts/validators/pr-checks.sh > "${log}" 2>&1; then
  exit 0
fi

failed_line="$(grep -E '^pr-checks: failed: ' "${log}" | tail -n 1)" || failed_line=""
failed="${failed_line#pr-checks: failed: }"
{
  echo "The push is blocked: npm run check:pr failed, so Validate's Checks job would fail too."
  if [[ -n ${failed} ]]; then
    echo "Failed steps: ${failed}"
    # The output of each failed step, from its "== pr-checks: <step>" header to the next one.
    awk -v failed=" ${failed} " '
      /^== pr-checks: / { step = $3; show = index(failed, " " step " ") > 0; if (show) print; next }
      show' "${log}" | tail -n 60
  else
    echo "pr-checks stopped before it could list the failed steps. Last lines of its output:"
    tail -n 40 "${log}"
  fi
  echo "Fix each failed step, commit, run npm run check:pr until it passes, then push again."
  echo "It checks committed changes against origin/main, plus the working tree for lint and tests."
} >&2
exit 2
