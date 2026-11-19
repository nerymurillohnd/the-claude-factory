#!/usr/bin/env bash
# The merge gate's checks, the single source for Validate's Checks job and `npm run check:pr`, so a
# branch that passes here passes in CI.
#
# Usage: pr-checks.sh [step...]
#   With no step, runs every step of the Checks job, keeps going after a failure, and exits 1 if any
#   failed. With steps, runs only those, in order.
#
# Steps: lint biome-changed typecheck test-scripts test-plugins validate mods consistency
#        release-notes install debt-validate (debt-validate belongs to the Debt job, never to "all")
#
# CHECKS_BASE is the commit the branch is compared with for biome-changed and install; it defaults
# to origin/main. Both read committed changes only, as CI sees them.
set -Eeuo pipefail
trap 'exit 1' ERR

# The plugins that fail plain `claude plugin validate --strict` today (DEBT-003): the Debt job
# validates them strictly, and the Checks job installs them with `check:install --no-strict`.
DEBT_003_PLUGINS="file-tree-pane model-trace project-maintainer tool-ledger turn-meter"
ALL_STEPS="lint biome-changed typecheck test-scripts test-plugins validate mods consistency release-notes install"

root="$(git rev-parse --show-toplevel)"
cd "${root}"
base="${CHECKS_BASE:-origin/main}"

is_debt_003() {
  [[ " ${DEBT_003_PLUGINS} " == *" $1 "* ]]
}

step_lint() {
  # lint:js is held back by DEBT-006; biome-changed gates the files a branch changes instead.
  npm run lint:python
  npm run lint:shell
  npm run lint:workflows
  npm run lint:github
}

step_biome_changed() {
  # New Biome findings only: the files changed since the base, so DEBT-006 can't hide them.
  npx biome check --changed --since="${base}" --error-on-warnings --max-diagnostics=none \
    --no-errors-on-unmatched
}

step_validate() {
  local dir name status=0
  for dir in plugins/*/; do
    name="$(basename "${dir}")"
    if [[ " ${DEBT_003_PLUGINS} " == *" ${name} "* ]]; then continue; fi
    claude plugin validate --strict "${dir}" || status=1
  done
  claude plugin validate --strict . || status=1
  npm run validate:claude || status=1
  return "${status}"
}

step_release_notes() {
  # release.yml stops at the first plugin whose notes are missing, so every plugin is checked.
  local names name status=0
  names="$(node -e 'console.log(require("./.claude-plugin/marketplace.json").plugins.map((p) => p.name).join(" "))')"
  for name in ${names}; do
    npm run --silent release:notes -- "${name}" > /dev/null || status=1
  done
  return "${status}"
}

step_install() {
  # A DEBT-003 plugin is still installed, loaded and tested; only its strict validation waits.
  local changed name
  local -a strict=() debt=()
  changed="$(git diff --name-only "${base}...HEAD" -- plugins/ | cut -d/ -f2 | sort -u)"
  for name in ${changed}; do
    if [[ ! -f plugins/${name}/.claude-plugin/plugin.json ]]; then continue; fi
    if [[ " ${DEBT_003_PLUGINS} " == *" ${name} "* ]]; then debt+=("${name}"); else strict+=("${name}"); fi
  done
  if ((${#strict[@]} + ${#debt[@]} == 0)); then
    echo "No plugin changed."
    return 0
  fi
  if ((${#strict[@]} > 0)); then npm run check:install -- --from local "${strict[@]}"; fi
  if ((${#debt[@]} > 0)); then npm run check:install -- --from local --no-strict "${debt[@]}"; fi
}

step_debt_validate() {
  local name status=0
  for name in ${DEBT_003_PLUGINS}; do
    claude plugin validate --strict "plugins/${name}/" || status=1
  done
  return "${status}"
}

run_step() {
  case "$1" in
    lint) step_lint ;;
    biome-changed) step_biome_changed ;;
    typecheck) npm run typecheck ;;
    test-scripts) npm run test:scripts ;;
    test-plugins) npm run test:plugins ;;
    validate) step_validate ;;
    mods) npm run validate:mods ;;
    # A branch is checked as main will be after the merge (PC-05, --main).
    consistency) npm run check:consistency -- --main ;;
    release-notes) step_release_notes ;;
    install) step_install ;;
    debt-validate) step_debt_validate ;;
    *)
      echo "pr-checks: unknown step '$1'; steps: ${ALL_STEPS} debt-validate" >&2
      return 2
      ;;
  esac
}

main() {
  if (($# > 0)); then
    local step
    for step in "$@"; do run_step "${step}"; done
    return 0
  fi
  local step failed=()
  for step in ${ALL_STEPS}; do
    echo "== pr-checks: ${step}"
    # Each step runs in its own process, so set -e holds inside it and one failure doesn't stop
    # the other steps.
    if ! bash "${BASH_SOURCE[0]}" "${step}"; then failed+=("${step}"); fi
  done
  if ((${#failed[@]} > 0)); then
    echo "pr-checks: failed: ${failed[*]}" >&2
    return 1
  fi
  echo "pr-checks: every step passed"
}

main "$@"
