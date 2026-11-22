#!/usr/bin/env bash
# Runs one step on every plugin under plugins/, so package.json holds one command per script.
#
# Usage: plugins.sh install | validate | portable | mods | tests
#   install   npm ci in each plugin that has a package-lock.json: tsc follows the repository's
#             imports into plugin code, which needs its runtime packages
#   validate  claude plugin validate --strict on each plugin
#   portable  the same with --profile directory: what the Anthropic directory checks
#   mods      claude plugin test on each plugin with tests/*.test.ts or *.test.tsx
#   tests     each plugin's standard-library tests: python3 -m unittest for tests/test_*.py, and
#             node --test for tests/*.test.mjs
#
# Every plugin is checked even after one fails, and the script exits 1 if any failed, so one run
# reports them all. Written for bash 3.2, the bash macOS ships.
set -Eeuo pipefail
trap 'exit 1' ERR

check="${1:-}"
case "${check}" in
  install | validate | portable | mods | tests) ;;
  *)
    echo "usage: plugins.sh install | validate | portable | mods | tests" >&2
    exit 2
    ;;
esac

root="$(git rev-parse --show-toplevel)"
cd "${root}"

failed=()
for dir in plugins/*/; do
  case "${check}" in
    install)
      if [[ -f ${dir}package-lock.json ]]; then
        npm ci --prefix "${dir%/}" --no-audit --no-fund || failed+=("${dir}")
      fi
      ;;
    validate)
      claude plugin validate --strict "${dir}" || failed+=("${dir}")
      ;;
    portable)
      claude plugin validate --profile directory --strict "${dir}" || failed+=("${dir}")
      ;;
    mods)
      if compgen -G "${dir}tests/*.test.ts*" > /dev/null; then
        claude plugin test "${dir}" || failed+=("${dir}")
      fi
      ;;
    tests)
      if compgen -G "${dir}tests/test_*.py" > /dev/null; then
        python3 -m unittest discover -s "${dir}tests" -p 'test_*.py' || failed+=("${dir}")
      fi
      if compgen -G "${dir}tests/*.test.mjs" > /dev/null; then
        node --test "${dir}"tests/*.test.mjs || failed+=("${dir}")
      fi
      ;;
    *) ;;
  esac
done

if ((${#failed[@]} > 0)); then
  echo "plugins.sh ${check}: failed: ${failed[*]}" >&2
  exit 1
fi
