#!/usr/bin/env bash
# Checks governed documents against the rules a script can verify.
#
#   check-document.sh [--owner <agent>] <file>...
#
# Prints one line per problem and exits 1 when any file fails. A file that is
# not governed, or not owned by the agent given with --owner, is skipped.
set -uo pipefail
here="$(dirname "$0")"
# shellcheck source=.claude/skills/documentation-governance/scripts/lib.sh
. "${here}/lib.sh"

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

docs_require

owner=""
if [[ "${1:-}" == "--owner" ]]; then
  owner="${2:-}"
  shift 2 || exit 0
fi

for arg in "$@"; do
  rel="$(docs_relpath "${arg}")"
  found="$(docs_lookup "${rel}")"
  [[ -n "${found}" ]] || continue
  if [[ -n "${owner}" && "${found%% *}" != "${owner}" ]]; then
    continue
  fi
  check_file "${rel}" "${found##* }"
done

[[ -z "${problems}" ]] && exit 0
printf '%s' "${problems}"
exit 1
