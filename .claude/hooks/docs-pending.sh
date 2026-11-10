#!/usr/bin/env bash
# Detects documentation chains that a change has set off and that have not
# run yet. Keeps no state: it derives everything from git and the files.
#
#   docs-pending.sh           Print one line per pending chain:
#                             "<chain> <plugin>". Always exits 0.
#   docs-pending.sh --hook    Hook mode, input on stdin (PostToolUse or Stop).
#
# component-change: a plugin has changed files other than its documents,
# compared with the upstream branch (or HEAD when there is none), and its
# CHANGELOG has no entry under "## [Unreleased]".
set -uo pipefail
here="$(dirname "$0")"
# shellcheck source=.claude/hooks/docs-lib.sh
. "${here}/docs-lib.sh"
docs_require

# True when the Unreleased section of a changelog holds at least one bullet.
has_unreleased_entry() {
  awk '
    /^## \[Unreleased\]/ { inside = 1; next }
    /^## \[/             { inside = 0 }
    inside && /^- /      { found = 1 }
    END                  { exit found ? 0 : 1 }
  ' "$1" 2>/dev/null
}

# Print "<chain> <plugin>" for every pending chain.
pending() {
  local base tracked untracked rel plugin found seen=" "
  base="HEAD"
  if git -C "${DOCS_ROOT}" rev-parse --verify --quiet '@{upstream}' >/dev/null 2>&1; then
    base='@{upstream}'
  fi
  tracked="$(git -C "${DOCS_ROOT}" diff --name-only "${base}" -- plugins 2>/dev/null || true)"
  untracked="$(git -C "${DOCS_ROOT}" ls-files --others --exclude-standard -- plugins 2>/dev/null || true)"

  while IFS= read -r rel; do
    [[ -n "${rel}" ]] || continue
    case "${rel}" in
      plugins/*/LICENSE | plugins/*/NOTICE.txt) continue ;;
      plugins/*/*) ;;
      *) continue ;;
    esac
    found="$(docs_lookup "${rel}")"
    [[ -z "${found}" ]] || continue
    plugin="${rel#plugins/}"
    plugin="${plugin%%/*}"
    case "${seen}" in
      *" ${plugin} "*) continue ;;
      *) seen="${seen}${plugin} " ;;
    esac
    [[ -d "${DOCS_ROOT}/plugins/${plugin}" ]] || continue
    has_unreleased_entry "${DOCS_ROOT}/plugins/${plugin}/CHANGELOG.md" \
      || printf 'component-change %s\n' "${plugin}"
  done <<<"${tracked}"$'\n'"${untracked}"
}

if [[ "${1:-}" != "--hook" ]]; then
  pending
  exit 0
fi

input="$(cat)"
event="$(docs_field "${input}" '.hook_event_name')"
# Only the main session is told: a writer agent is itself running the chain.
agent="$(docs_field "${input}" '.agent_type')"
[[ -z "${agent}" ]] || exit 0
# One reminder per turn is enough; the second pass lets the turn end.
active="$(docs_field "${input}" '.stop_hook_active')"
[[ "${active}" == "true" ]] && exit 0

list="$(pending)"
[[ -n "${list}" ]] || exit 0

case "${event}" in
  Stop | PostToolUse)
    jq -n --arg e "${event}" --arg l "${list}" \
      '{hookSpecificOutput: {hookEventName: $e, additionalContext: ("Documentation chains are pending for changes in this working tree, one per line as <chain> <plugin>:\n" + $l + "\nLoad the documentation-governance skill and run each chain. If a change has no effect a user would notice, say so and leave the documents as they are.")}}'
    ;;
  *) ;;
esac
