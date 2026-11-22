#!/usr/bin/env bash
# The merge gate's checks, the single source for Validate's Checks job and `npm run check:pr`, so a
# branch that passes here passes in CI.
#
# Usage: pr-checks.sh [step...]
#   With no step, runs every step of the Checks job, keeps going after a failure, and exits 1 if any
#   failed. With steps, runs only those, in order.
#
# Steps: lint biome-changed typecheck test-scripts test-plugins validate mods consistency
#        release-notes install links
#
# CHECKS_BASE is the commit the branch is compared with for biome-changed, install and links; it
# defaults to origin/main. They read committed changes only, as CI sees them.
set -Eeuo pipefail
trap 'exit 1' ERR

ALL_STEPS="lint biome-changed typecheck test-scripts test-plugins validate mods consistency release-notes install links"

root="$(git rev-parse --show-toplevel)"
cd "${root}"
base="${CHECKS_BASE:-origin/main}"

step_lint() {
  # Every part of `npm run lint` except lint:js, held back by DEBT-006; biome-changed gates the
  # files a branch changes instead.
  npm run lint:agents
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
  # Every script of `npm run validate` except validate:mods, which is the mods step.
  local status=0
  npm run validate:plugins || status=1
  npm run validate:marketplace || status=1
  npm run validate:claude || status=1
  # What the Anthropic directory checks, and a .catch on every gating hook of a mod.
  npm run validate:portable || status=1
  npm run validate:hooks-catch || status=1
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
  local changed name
  local -a names=()
  changed="$(git diff --name-only "${base}...HEAD" -- plugins/ | cut -d/ -f2 | sort -u)"
  for name in ${changed}; do
    if [[ ! -f plugins/${name}/.claude-plugin/plugin.json ]]; then continue; fi
    names+=("${name}")
  done
  if ((${#names[@]} == 0)); then
    echo "No plugin changed."
    return 0
  fi
  npm run check:install -- --from local "${names[@]}"
}

step_links() {
  # The live URLs of the files the branch adds or changes; the weekly Links workflow checks all.
  local file names
  local -a changed=()
  names="$(git diff --name-only --diff-filter=ACMR "${base}...HEAD")"
  while IFS= read -r file; do
    if [[ -n ${file} ]]; then changed+=("${file}"); fi
  done <<< "${names}"
  if ((${#changed[@]} == 0)); then
    echo "No file changed."
    return 0
  fi
  npm run check:links -- "${changed[@]}"
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
    links) step_links ;;
    *)
      echo "pr-checks: unknown step '$1'; steps: ${ALL_STEPS}" >&2
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
