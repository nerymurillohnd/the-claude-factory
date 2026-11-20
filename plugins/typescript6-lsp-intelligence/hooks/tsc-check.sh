#!/usr/bin/env bash
# Post-edit hook of typescript6-lsp-intelligence, for macOS and Linux. PostToolUse runs it after
# Edit, Write and Bash calls with the event JSON on stdin; UserPromptSubmit runs it with
# --new-turn to start a new turn's list of edited files. It checks that Node.js is on PATH and
# hands the event to hooks/tsc-report.mjs, which runs the project's own
# `tsc --noEmit --pretty false --strict` and reports the result.
#
# Exit codes: 0 when the result is reported (or nothing TypeScript changed), 2 when an edited file
# has errors (Claude fixes them first), 1 when the hook could not verify or report, so no result
# passes in silence. Without Node.js, it prints one notice and exits 0: tsc needs Node.js too.
# Bash 3.2 or later.

set -Eeuo pipefail
trap 'printf "typescript6-lsp-intelligence: the hook failed unexpectedly at line %s, so the edited files were not verified.\n" "${LINENO}" >&2; exit 1' ERR

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly HOOK_DIR
readonly MODE="${1:-}"

if ! command -v node > /dev/null 2>&1; then
  # A new turn needs no notice; a check without Node.js can't run tsc either.
  [[ ${MODE} == --new-turn ]] && exit 0
  printf '%s\n' '{"systemMessage":"typescript6-lsp-intelligence: tsc check did not run: Node.js was not found on PATH."}'
  exit 0
fi

status=0
node "${HOOK_DIR}/tsc-report.mjs" "${MODE}" || status=$?
case "${status}" in
  0 | 1 | 2) exit "${status}" ;;
  *)
    printf 'typescript6-lsp-intelligence: the check stopped with exit %s, so the edited files were not verified.\n' "${status}" >&2
    exit 1
    ;;
esac
