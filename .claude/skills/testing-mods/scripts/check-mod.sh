#!/usr/bin/env bash
# Run `claude plugin validate --strict` then `claude plugin test` on a mod directory and
# print both outputs. Exits 0 only if both succeed and the test output ends with
# its summary line.
#
# Usage: check-mod.sh <mod-dir>
#
# `claude plugin test` writes to a file here, not a pipe: on a pipe it can lose
# the tail of its output, summary included, and still exit 0
# (anthropics/claude-code#103055). A missing summary therefore fails the check.
#
# NOTE: `claude plugin test` executes the mod's JavaScript and its *.test.ts
# files. Run it on this marketplace's own mods, or on a third-party clone you
# have read first.
set -uo pipefail

dir="${1:?usage: check-mod.sh <mod-dir>}"
log="$(mktemp "${TMPDIR:-/tmp}/check-mod.XXXXXX")"
trap 'rm -f "${log}"' EXIT

printf '== claude plugin validate --strict %s\n' "${dir}"
claude plugin validate --strict "${dir}" < /dev/null
validate_status=$?

printf '\n== claude plugin test %s\n' "${dir}"
claude plugin test "${dir}" < /dev/null > "${log}" 2>&1
test_status=$?
cat "${log}"

summary=missing
if grep -Eq '^Ran [0-9]+ tests? across [0-9]+ files?' "${log}"; then
  summary=present
fi

printf '\n== validate exit=%s, test exit=%s, test summary=%s\n' "${validate_status}" "${test_status}" "${summary}"
[[ ${validate_status} -eq 0 ]] && [[ ${test_status} -eq 0 ]] && [[ ${summary} == present ]]
