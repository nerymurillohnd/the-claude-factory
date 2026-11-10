#!/usr/bin/env bash
# Lists documentation chains that a change has set off and that have not run
# yet, one per line as "<chain> <plugin>". Keeps no state: it derives
# everything from git and the files. Always exits 0.
#
# component-change: a plugin has changed files other than its documents,
# compared with the upstream branch (or HEAD when there is none), and its
# CHANGELOG has no entry under "## [Unreleased]".
set -uo pipefail
here="$(dirname "$0")"
# shellcheck source=.claude/skills/documentation-governance/scripts/lib.sh
. "${here}/lib.sh"
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

base="HEAD"
if git -C "${DOCS_ROOT}" rev-parse --verify --quiet '@{upstream}' >/dev/null 2>&1; then
  base='@{upstream}'
fi
tracked="$(git -C "${DOCS_ROOT}" diff --name-only "${base}" -- plugins 2>/dev/null || true)"
untracked="$(git -C "${DOCS_ROOT}" ls-files --others --exclude-standard -- plugins 2>/dev/null || true)"
seen=" "

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
exit 0
