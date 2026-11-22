#!/usr/bin/env bash
# Runs one step on every plugin under plugins/, so package.json holds one command per script.
#
# Usage: plugins.sh install | portable | hooks-catch | mods | tests
#   install      npm ci in each plugin that has a package-lock.json: tsc follows the repository's
#                imports into plugin code, which needs its runtime packages
#   portable     claude plugin validate --profile directory --strict: every --strict check, plus
#                what the Anthropic directory would refuse
#   hooks-catch  every gating hook of a mod has its own .catch (validate --json reports it)
#   mods         claude plugin test on each plugin with tests/*.test.ts or *.test.tsx
#   tests        each plugin's standard-library tests: python3 -m unittest for tests/test_*.py, and
#                node --test for tests/*.test.mjs
#
# Every plugin is checked even after one fails, and the script exits 1 if any failed, so one run
# reports them all. Written for bash 3.2, the bash macOS ships.
set -Eeuo pipefail
trap 'exit 1' ERR

check="${1:-}"
root="$(git rev-parse --show-toplevel)"
cd "${root}"

failed=()
for dir in plugins/*/; do
  ok=1
  case "${check}" in
    install)
      if [[ -f ${dir}package-lock.json ]]; then
        npm ci --prefix "${dir%/}" --no-audit --no-fund || ok=0
      fi
      ;;
    portable)
      claude plugin validate --profile directory --strict "${dir}" || ok=0
      ;;
    hooks-catch)
      # validate exits 1 on unrelated warnings under its own rules; the JSON report is still whole.
      report="$(claude plugin validate --json "${dir}" || true)"
      found="$(jq -r --arg dir "${dir%/}" '.contents[]?.gatingHooks[]? | select(.hasCatch == false)
        | "\($dir): \(.hook) in \(.module) has no .catch"' <<< "${report}")"
      if [[ -n ${found} ]]; then
        printf '%s\n' "${found}"
        ok=0
      fi
      ;;
    mods)
      if compgen -G "${dir}tests/*.test.ts*" > /dev/null; then
        claude plugin test "${dir}" || ok=0
      fi
      ;;
    tests)
      if compgen -G "${dir}tests/test_*.py" > /dev/null; then
        python3 -m unittest discover -s "${dir}tests" -p 'test_*.py' || ok=0
      fi
      if compgen -G "${dir}tests/*.test.mjs" > /dev/null; then
        node --test "${dir}"tests/*.test.mjs || ok=0
      fi
      ;;
    *)
      echo "usage: plugins.sh install | portable | hooks-catch | mods | tests" >&2
      exit 2
      ;;
  esac
  if ((ok == 0)); then
    failed+=("${dir}")
  fi
done

if ((${#failed[@]} > 0)); then
  echo "plugins.sh ${check}: failed: ${failed[*]}" >&2
  exit 1
fi
