#!/usr/bin/env bash
# Runs this skill's type-check fixtures through the strict check and prints, for each one,
# the expected and observed TypeScript error codes.
#   run-fixtures.sh <owning tsconfig.json> [tsc]   implementation mode: inside the project
#   run-fixtures.sh --outside [tsc]                research mode: a temporary folder outside it
# Without [tsc], the project's node_modules/.bin/tsc is used (walking up from the tsconfig),
# then a tsc on PATH. Always exits 0: read the verdict from the output.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
readonly ASSETS="${SCRIPT_DIR}/../assets"
readonly FIXTURES="clean_control type_mismatch implicit_any possibly_undefined missing_member"
readonly STRICT=(--pretty false --noEmit true --skipLibCheck true --allowJs true --checkJs true
  --strict true --noImplicitAny true --strictNullChecks true --strictFunctionTypes true
  --strictBindCallApply true --strictPropertyInitialization true --strictBuiltinIteratorReturn true
  --noImplicitThis true --useUnknownInCatchVariables true --alwaysStrict true
  --exactOptionalPropertyTypes true --noUncheckedIndexedAccess true
  --noPropertyAccessFromIndexSignature true --noImplicitReturns true --noImplicitOverride true
  --noFallthroughCasesInSwitch true --noUnusedLocals true --noUnusedParameters true
  --allowUnusedLabels false --allowUnreachableCode false)

# The folder in use right now, removed on exit even if a run stops midway.
CURRENT=""
trap 'rm -rf "${CURRENT}" "${BUILDINFO_DIR:-}"' EXIT

# Sets TSC to the compiler for folder $1, or leaves it empty.
TSC=""
find_tsc() {
  local dir="$1"
  while [[ -n ${dir} ]]; do
    if [[ -x ${dir}/node_modules/.bin/tsc ]]; then
      TSC="${dir}/node_modules/.bin/tsc"
      return 0
    fi
    [[ ${dir} == / ]] && break
    dir="$(dirname "${dir}")"
  done
  TSC="$(command -v tsc || true)"
  return 0
}

# Sets EXPECTED to the error code fixture $1 must produce, or "none".
EXPECTED=""
expected_for() {
  case "$1" in
    type_mismatch) EXPECTED=TS2322 ;;
    implicit_any) EXPECTED=TS7006 ;;
    possibly_undefined) EXPECTED=TS18048 ;;
    missing_member) EXPECTED=TS2551 ;;
    *) EXPECTED=none ;;
  esac
  return 0
}

# Sets ROOT_DIR to the folder the fixture folders go in: the owner's rootDir, or its folder.
ROOT_DIR=""
root_dir_for() {
  local owner="$1" owner_dir shown value
  owner_dir="$(cd "$(dirname "${owner}")" && pwd -P)"
  shown="$(cd "${owner_dir}" && "${TSC}" --showConfig -p "${owner}" 2> /dev/null || true)"
  value="$(printf '%s\n' "${shown}" | sed -n 's/^ *"rootDir": *"\(.*\)",\{0,1\}$/\1/p' | head -n 1)"
  if [[ -z ${value} ]]; then
    ROOT_DIR="${owner_dir}"
  elif [[ ${value} == /* ]]; then
    ROOT_DIR="${value}"
  else
    ROOT_DIR="$(cd "${owner_dir}/${value}" 2> /dev/null && pwd -P || printf '%s' "${owner_dir}")"
  fi
  return 0
}

OUTSIDE=no
OWNER=""
if [[ ${1:-} == --outside ]]; then
  OUTSIDE=yes
  TSC="${2:-}"
  [[ -n ${TSC} ]] || find_tsc "${PWD}"
elif [[ -n ${1:-} && -f ${1} ]]; then
  owner_dir="$(dirname "$1")"
  owner_dir="$(cd "${owner_dir}" && pwd -P)" || exit 0
  OWNER="${owner_dir}/${1##*/}"
  TSC="${2:-}"
  [[ -n ${TSC} ]] || find_tsc "$(dirname "${OWNER}")"
else
  printf 'Fixtures not run: give the owning tsconfig.json, or --outside in research mode.\n'
  exit 0
fi
if [[ -z ${TSC} ]]; then
  printf 'Fixtures not run: no tsc found in node_modules/.bin or on PATH. The checks are not proven.\n'
  exit 0
fi

VERSION="$("${TSC}" --version 2>&1 || true)"
BUILDINFO_DIR="$(mktemp -d)"
if [[ ${OUTSIDE} == yes ]]; then
  printf 'Compiler: %s (%s)\nProgram: tsconfig.json.fixture in a temporary folder outside the project; this proves the compiler, not the project config.\n\n' "${TSC}" "${VERSION}"
else
  root_dir_for "${OWNER}"
  printf 'Compiler: %s (%s)\nProgram: extends %s\nFolders: %s/lsp-fixture-*\n\n' "${TSC}" "${VERSION}" "${OWNER}" "${ROOT_DIR}"
fi

PASSED=0
TOTAL=0
for name in ${FIXTURES}; do
  TOTAL=$((TOTAL + 1))
  if [[ ${OUTSIDE} == yes ]]; then
    work="$(mktemp -d)"
  else
    work="$(mktemp -d "${ROOT_DIR}/lsp-fixture-XXXXXX")"
  fi
  CURRENT="${work}"
  cp "${ASSETS}/${name}.ts.fixture" "${work}/${name}.ts"
  if [[ ${OUTSIDE} == yes ]]; then
    cp "${ASSETS}/tsconfig.json.fixture" "${work}/tsconfig.json"
  else
    printf '{ "extends": "%s", "files": [], "include": ["*.ts"] }\n' "${OWNER}" > "${work}/tsconfig.json"
  fi
  output="$(cd "${work}" && "${TSC}" -p "${work}/tsconfig.json" "${STRICT[@]}" \
    --tsBuildInfoFile "${BUILDINFO_DIR}/${name}.tsbuildinfo" 2>&1 || true)"
  codes="$(printf '%s\n' "${output}" | grep -o 'error TS[0-9]*' | sed 's/error //' | sort -u | tr '\n' ' ')"
  codes="${codes% }"
  expected_for "${name}"
  if [[ ${EXPECTED} == none && -z ${codes} ]]; then
    verdict=ok
  elif [[ ${EXPECTED} != none && " ${codes} " == *" ${EXPECTED} "* ]]; then
    verdict=ok
  else
    verdict=MISMATCH
  fi
  [[ ${verdict} == ok ]] && PASSED=$((PASSED + 1))
  printf '%-20s expected %-8s observed %-24s %s\n' "${name}" "${EXPECTED}" "${codes:-none}" "${verdict}"
  if [[ ${verdict} != ok && -n ${output} ]]; then
    printf '%s\n' "${output}" | head -n 5 | sed 's/^/    /'
  fi
  rm -rf "${work}"
  CURRENT=""
done

printf '\n%s of %s fixtures as expected.' "${PASSED}" "${TOTAL}"
if [[ ${PASSED} -eq ${TOTAL} ]]; then
  printf ' The type-check layer sees broken code here.\n'
else
  printf ' The check is blind or misfires here; see fixtures.md "Reading the outcome".\n'
fi
exit 0
