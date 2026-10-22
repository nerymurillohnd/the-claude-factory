#!/usr/bin/env bash
# PreToolUse hook for `git push`: denies the push while a plugin changed since origin/main has no
# version bump. Standalone: it needs only bash, git, sed and grep. Any other command goes ahead.
# The `if` filter in settings.json is best-effort, so this script checks for a real push itself.
set -euo pipefail

base="origin/main"
input="$(cat)"

# The Bash command of the hook input, still JSON-escaped.
command_text=""
command_pattern='"command"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)"'
if [[ ${input} =~ ${command_pattern} ]]; then
  command_text="${BASH_REMATCH[1]}"
fi

push_found=0
greater=0

# Sets push_found=1 when one command of $1 is `git [options] push`.
detect_git_push() {
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
    if [[ ${words[i]:-} == push ]]; then
      push_found=1
    fi
  done
}

# Sets greater=1 when version $1 is above version $2 (major.minor.patch).
compare_versions() {
  local i x y
  local -a a b
  greater=0
  IFS=. read -r -a a <<< "${1%%[-+]*}"
  IFS=. read -r -a b <<< "${2%%[-+]*}"
  for i in 0 1 2; do
    x=$((10#${a[i]:-0}))
    y=$((10#${b[i]:-0}))
    if ((x != y)); then
      if ((x > y)); then
        greater=1
      fi
      return 0
    fi
  done
}

# The first "version" value of a plugin.json read from stdin.
manifest_version() {
  sed -n '/"version"/{s/^[^:]*:[[:space:]]*"\([^"]*\)".*/\1/p;q;}'
}

detect_git_push "${command_text}"
[[ ${push_found} == 1 ]] || exit 0

project_dir="${CLAUDE_PROJECT_DIR:-}"
if [[ -z ${project_dir} ]]; then
  project_dir="$(git rev-parse --show-toplevel)"
fi
cd "${project_dir}"
git rev-parse -q --verify "${base}" > /dev/null 2>&1 || exit 0

changed="$(git diff --name-only "${base}...HEAD" -- plugins/)"
seen=" "
errors=""
while IFS= read -r path; do
  name="${path#plugins/}"
  name="${name%%/*}"
  [[ -n ${name} && ${seen} != *" ${name} "* && -f plugins/${name}/.claude-plugin/plugin.json ]] || continue
  seen+="${name} "
  files="$(git diff --name-only "${base}...HEAD" -- "plugins/${name}/")"
  # Edits limited to the plugin README do not reach users through `claude plugin update`.
  other=0
  while IFS= read -r file; do
    [[ ${file} == "plugins/${name}/README.md" ]] || other=1
  done <<< "${files}"
  [[ ${other} == 1 ]] || continue
  base_manifest="$(git show "${base}:plugins/${name}/.claude-plugin/plugin.json" 2> /dev/null)" || continue
  base_version="$(manifest_version <<< "${base_manifest}")"
  version="$(manifest_version < "plugins/${name}/.claude-plugin/plugin.json")"
  compare_versions "${version}" "${base_version}"
  if [[ ${greater} == 0 ]]; then
    list="${files//plugins\/${name}\//}"
    list="${list//$'\n'/, }"
    errors+="- plugins/${name}: files changed (${list}) but version is still ${base_version}. Run bump-version.mjs ${name} <level>."$'\n'
  elif ! grep -q -F "## [${version}]" "plugins/${name}/CHANGELOG.md" 2> /dev/null; then
    errors+="- plugins/${name}: CHANGELOG.md has no entry for ${version}."$'\n'
  fi
done <<< "${changed}"

[[ -n ${errors} ]] || exit 0

reason="Push blocked: plugin changes since ${base} are missing a version bump."$'\n'
reason+="${errors}"
reason+='For each plugin, read what changed and pick the SemVer level:'$'\n'
reason+='- major: breaking. A removed or renamed skill, agent or command, changed config keys, a new required dependency, or a change in behavior users rely on.'$'\n'
reason+='- minor: a new component, option or capability, backwards compatible.'$'\n'
reason+='- patch: a bug fix, a wording fix, performance, or an internal refactor with the same behavior.'$'\n'
reason+='Summarize the change under [Unreleased] in the plugin CHANGELOG.md, run: node scripts/bump-version.mjs <plugin> <level>. Commit the result, then push again.'$'\n'
reason+='If the plugin README.md no longer matches the change, update it first. Changes limited to README.md need no bump.'

# A JSON string escapes a backslash, a double quote and a newline.
backslash=$'\\'
quote='"'
newline=$'\n'
reason="${reason//"${backslash}"/"${backslash}${backslash}"}"
reason="${reason//"${quote}"/"${backslash}${quote}"}"
reason="${reason//"${newline}"/"${backslash}n"}"
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "${reason}"
