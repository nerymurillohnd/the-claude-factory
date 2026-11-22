#!/usr/bin/env bash
set -euo pipefail

# List every mod gating hook that has no .catch, from `claude plugin validate --json`
# (contents[].gatingHooks[].hasCatch). Run it through `npm run validate:hooks-catch`.
# Exit 1 when any plugin has one, 0 when none does.

status=0
for dir in plugins/*/; do
  # validate exits 1 on unrelated warnings under its own rules; the JSON report is still whole.
  report="$(claude plugin validate --json "${dir}" || true)"
  found="$(jq -r --arg dir "${dir%/}" \
    '.contents[]?.gatingHooks[]? | select(.hasCatch == false)
		| "\($dir): \(.hook) in \(.module) has no .catch"' <<< "${report}")"
  if [[ -n ${found} ]]; then
    printf '%s\n' "${found}"
    status=1
  fi
done
exit "${status}"
