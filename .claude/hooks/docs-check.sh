#!/usr/bin/env bash
# Checks governed documents against the rules a script can verify.
#
#   docs-check.sh <file>...   Check the given files. Prints one line per
#                             problem and exits 1 when any file fails.
#   docs-check.sh --hook      Hook mode, input on stdin. As PostToolUse it
#                             checks the file just written; as SubagentStop it
#                             checks every changed document the agent owns.
set -uo pipefail
here="$(dirname "$0")"
# shellcheck source=.claude/hooks/docs-lib.sh
. "${here}/docs-lib.sh"

problems=""

# Append one problem line.
report() {
  problems="${problems}$1"$'\n'
}

# Append a problem for each line of a file that matches a pattern.
report_matches() {
  local path="$1" rel="$2" pattern="$3" label="$4" hits line
  hits="$(grep -n -e "${pattern}" "${path}" 2>/dev/null || true)"
  [[ -n "${hits}" ]] || return 0
  hits="$(printf '%s\n' "${hits}" | head -n 5)"
  while IFS= read -r line; do
    report "${rel}:${line} <- ${label}"
  done <<<"${hits}"
}

# Append a problem for each heading of a level that is not an allowed one.
report_headings() {
  local path="$1" rel="$2" level="$3" allowed="$4" label="$5" hits line
  hits="$(grep -n -e "^${level} " "${path}" 2>/dev/null || true)"
  [[ -n "${hits}" ]] || return 0
  hits="$(printf '%s\n' "${hits}" | grep -v -E -e "${allowed}" || true)"
  [[ -n "${hits}" ]] || return 0
  while IFS= read -r line; do
    report "${rel}:${line} <- ${label}"
  done <<<"${hits}"
}

check_file() {
  local rel="$1" kind="$2" path heading badges
  path="${DOCS_ROOT}/${rel}"
  if [[ ! -f "${path}" ]]; then
    report "${rel}: file does not exist"
    return 0
  fi

  report_matches "${path}" "${rel}" '{{' 'unresolved {{value}}'
  report_matches "${path}" "${rel}" '<!--' 'leftover comment or marker'

  case "${kind}" in
    plugin-changelog)
      grep -q -e '^## \[Unreleased\]$' "${path}" || report "${rel}: missing the '## [Unreleased]' heading"
      report_headings "${path}" "${rel}" '##' \
        '^[0-9]+:## \[(Unreleased\]|[0-9]+\.[0-9]+\.[0-9]+\] - [0-9]{4}-[0-9]{2}-[0-9]{2}( \[YANKED\])?)$' \
        "version heading is not '## [X.Y.Z] - YYYY-MM-DD'"
      report_headings "${path}" "${rel}" '###' \
        '^[0-9]+:### (Added|Changed|Deprecated|Removed|Fixed|Security)$' \
        'not one of the six change types'
      ;;
    plugin-readme)
      for heading in '## 📋 Prerequisites' '## 📥 Installation' '## 🔍 What this plugin runs and sends' \
        '## 🔄 Updating' '## 🗑️ Uninstalling' '## 🧭 Compatibility' '## 📝 Changelog' '## 📄 License'; do
        grep -q -F -x -e "${heading}" "${path}" || report "${rel}: missing the '${heading}' section"
      done
      grep -q -F -e '**Platforms:**' "${path}" || report "${rel}: missing the Platforms line under Compatibility"
      badges="$(grep -c -e 'label=version' "${path}" || true)"
      [[ "${badges}" == "1" ]] || report "${rel}: expected exactly one Version badge, found ${badges}"
      ;;
    *) ;;
  esac
}

# Check a repository-relative path when it is governed and, if a second
# argument is given, owned by that agent.
check_rel() {
  local found
  found="$(docs_lookup "$1")"
  [[ -n "${found}" ]] || return 0
  if [[ -n "${2:-}" && "${found%% *}" != "$2" ]]; then
    return 0
  fi
  check_file "$1" "${found##* }"
}

docs_require

if [[ "${1:-}" != "--hook" ]]; then
  for arg in "$@"; do
    rel="$(docs_relpath "${arg}")"
    check_rel "${rel}"
  done
  [[ -z "${problems}" ]] && exit 0
  printf '%s' "${problems}"
  exit 1
fi

input="$(cat)"
event="$(docs_field "${input}" '.hook_event_name')"

case "${event}" in
  PostToolUse)
    file="$(docs_field "${input}" '.tool_input.file_path')"
    if [[ -n "${file}" ]]; then
      rel="$(docs_relpath "${file}")"
      check_rel "${rel}"
    fi
    ;;
  SubagentStop)
    # Let the agent stop on the second pass, so a check it cannot satisfy
    # never loops; the independent review still sees the result.
    active="$(docs_field "${input}" '.stop_hook_active')"
    [[ "${active}" == "true" ]] && exit 0
    agent="$(docs_field "${input}" '.agent_type')"
    [[ -n "${agent}" ]] || exit 0
    changed="$(git -C "${DOCS_ROOT}" status --porcelain --untracked-files=all 2>/dev/null || true)"
    while IFS= read -r line; do
      [[ -n "${line}" ]] && check_rel "${line:3}" "${agent}"
    done <<<"${changed}"
    ;;
  *) exit 0 ;;
esac

[[ -z "${problems}" ]] && exit 0
jq -n --arg p "${problems}" \
  '{decision: "block", reason: ("Documentation checks failed. Fix each line, then run .claude/hooks/docs-check.sh on the file again:\n" + $p)}'
