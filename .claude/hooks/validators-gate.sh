#!/usr/bin/env bash
# PreToolUse hook for `git commit`: runs every validator in scripts/validators/ and denies the
# commit when one fails, with the output of each failing validator as the reason. Any other command goes ahead. The
# Husky pre-push hook runs the full gates; this one checks earlier, at each commit Claude makes.
# The `if` filter in settings.json is best-effort, so this script checks for a real commit itself.
set -euo pipefail

input="$(cat)"

# The Bash command of the hook input, still JSON-escaped.
command_text=""
command_pattern='"command"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)"'
if [[ ${input} =~ ${command_pattern} ]]; then
  command_text="${BASH_REMATCH[1]}"
else
  echo "validators-gate could not read tool_input.command from the hook input, so it blocks the call." >&2
  exit 2
fi

commit_found=0

# Sets commit_found=1 when one command of $1 is `git [options] commit`.
detect_git_commit() {
  local text="$1" part i
  local -a parts words
  local bs=$'\\'
  [[ -n ${text} ]] || return 0
  text="${text//"${bs}n"/;}"
  text="${text//&&/;}"
  text="${text//||/;}"
  text="${text//|/;}"
  IFS=';' read -r -a parts <<< "${text}"
  for part in "${parts[@]}"; do
    read -r -a words <<< "${part}"
    i=0
    while [[ ${words[i]:-} =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; do
      i=$((i + 1))
    done
    [[ ${words[i]:-} == git ]] || continue
    i=$((i + 1))
    while [[ ${words[i]:-} == -* ]]; do
      case "${words[i]}" in
        -C | -c | --git-dir | --work-tree | --namespace) i=$((i + 2)) ;;
        *) i=$((i + 1)) ;;
      esac
    done
    if [[ ${words[i]:-} == commit ]]; then
      commit_found=1
    fi
  done
}

detect_git_commit "${command_text}"
[[ ${commit_found} == 1 ]] || exit 0

project_dir="${CLAUDE_PROJECT_DIR:-}"
if [[ -z ${project_dir} ]]; then
  project_dir="$(git rev-parse --show-toplevel)"
fi
cd "${project_dir}"

# Every validator of scripts/validators/, as `npm run validate` runs them, so a new one is never
# left out. Versioning (bumps, changelogs) is not a validator: it belongs to the release.
shopt -s nullglob
VALIDATORS=(scripts/validators/*.py)
shopt -u nullglob
if ((${#VALIDATORS[@]} == 0)); then
  echo "validators-gate found no validator in scripts/validators/, so it blocks the commit." >&2
  exit 2
fi

output=""
for validator in "${VALIDATORS[@]}"; do
  if ! result="$("${validator}" 2>&1)"; then
    output+="${validator##*/}:"$'\n'"${result}"$'\n'
  fi
done

if [[ -z ${output} ]]; then
  # No permissionDecision: the commit goes on to the normal permission flow.
  printf '{"systemMessage":"validators-gate: all %d maintainer validators passed"}\n' "${#VALIDATORS[@]}"
  exit 0
fi

# Drop control characters other than a tab and a newline, which JSON cannot carry raw.
output="$(printf '%s' "${output}" | LC_ALL=C tr -d '\000-\010\013-\037\177')"

# Keep the reason under the 10,000-character cap on what Claude reads.
max=8000
if ((${#output} > max)); then
  output="${output:0:max}"$'\n'"[output truncated; run npm run validate to see all of it]"
fi
reason="Commit blocked: a maintainer validator failed. Fix each cause below, then commit again."$'\n'
reason+="${output}"

# A JSON string escapes a backslash, a double quote, a newline and a tab.
backslash=$'\\'
quote='"'
newline=$'\n'
tab=$'\t'
reason="${reason//"${backslash}"/"${backslash}${backslash}"}"
reason="${reason//"${quote}"/"${backslash}${quote}"}"
reason="${reason//"${newline}"/"${backslash}n"}"
reason="${reason//"${tab}"/"${backslash}t"}"
printf '{"systemMessage":"validators-gate: a maintainer validator failed; commit blocked","hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "${reason}"
