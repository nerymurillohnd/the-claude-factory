#!/usr/bin/env bash
set -uo pipefail

# Setup failures exit 2 with the failed step and the next action on stderr; no report is printed.
fail() {
  printf '%s\n' "$*" >&2
  exit 2
}

skill_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P) || fail 'Cannot locate the skill folder; run the script by its absolute path.'
manifest="${skill_root}/references/fixtures.json"
fixture_root="${skill_root}/references/fixtures"
fixture_shfmt=shfmt
fixture_shellcheck=shellcheck
while (($#)); do
  [[ $1 == --tool && $# -ge 2 ]] || {
    printf 'Usage: verify-fixtures.sh [--tool name=/absolute/executable]...\n' >&2
    exit 2
  }
  case "${2%%=*}" in
    shfmt) fixture_shfmt=${2#*=} ;;
    shellcheck) fixture_shellcheck=${2#*=} ;;
    *)
      printf 'Unknown tool override: %s\n' "${2%%=*}" >&2
      exit 2
      ;;
  esac
  shift 2
done
command -v jq > /dev/null 2>&1 || {
  printf 'jq 1.6 or later is required; no controls ran. Install it and rerun.\n' >&2
  exit 2
}
# Resolves a profile named in fixtures.json to a file in the controls folder; the name may not contain a path.
read_profile() {
  local name
  name=$(jq -er --arg tool "$1" '.profiles[$tool]' "${manifest}") || return 1
  [[ ${name} =~ ^[a-z0-9_.]+\.fixture$ && -f ${fixture_root}/${name} ]] || return 1
  printf '%s\n' "${fixture_root}/${name}"
}
language=$(jq -er '.language' "${manifest}") || fail 'Cannot read references/fixtures.json; reinstall the plugin.'
case "${language}" in
  bash)
    required_tools=("${fixture_shfmt}" "${fixture_shellcheck}")
    tool_roles=(shfmt shellcheck)
    shellcheck_profile=$(read_profile shellcheck) || fail "fixtures.json names no usable shellcheck profile; reinstall the plugin."
    shfmt_profile=$(read_profile shfmt) || fail "fixtures.json names no usable shfmt profile; reinstall the plugin."
    ;;
  *)
    printf 'Unsupported control language: %s; reinstall the plugin.\n' "${language}" >&2
    exit 2
    ;;
esac
for tool in "${required_tools[@]}"; do
  command -v "${tool}" > /dev/null 2>&1 || {
    printf 'Required executable missing: %s; no controls ran. Install it, or pass its absolute path with --tool.\n' "${tool}" >&2
    exit 2
  }
done
test_root=$(mktemp -d "${TMPDIR:-/tmp}/skill-controls.XXXXXXXX") || fail 'Cannot create a temporary folder; check that TMPDIR points to a writable folder.'
trap '[[ -d ${test_root} ]] && rm -rf -- "${test_root}"' EXIT
test_root=$(cd "${test_root}" && pwd -P) || fail 'Cannot enter the temporary folder; check that TMPDIR points to a writable folder.'
tool_index=0
for tool in "${required_tools[@]}"; do
  resolved_tool=$(command -v "${tool}") || fail "Cannot resolve ${tool}; pass its absolute path with --tool."
  if "${tool}" --version > "${test_root}/version.stdout" 2> "${test_root}/version.stderr"; then
    jq -cn --arg role "${tool_roles[tool_index]}" --arg executable "${resolved_tool}" --rawfile version "${test_root}/version.stdout" --rawfile stderr "${test_root}/version.stderr" '{role:$role,executable:$executable,version:$version,stderr:$stderr}' >> "${test_root}/tools.jsonl" || fail 'jq failed while recording tool versions; jq 1.6 or later is required.'
  else
    printf 'Cannot identify executable version: %s; no controls ran. Check that it runs, or pass another with --tool.\n' "${tool}" >&2
    cat "${test_root}/version.stderr" >&2
    exit 2
  fi
  tool_index=$((tool_index + 1))
done
tool_metadata=$(jq -s '.' "${test_root}/tools.jsonl") || fail 'jq failed while reading tool versions; jq 1.6 or later is required.'
records="${test_root}/records.jsonl"
: > "${records}"
failed=0

run_stage() {
  local stage=$1
  shift
  local status parse_ok=true codes='[]' expected_codes expected_exit ok
  if "$@" > "${case_root}/${stage}.stdout" 2> "${case_root}/${stage}.stderr"; then status=0; else status=$?; fi
  case "${stage}" in
    shellcheck)
      codes=$(jq -ce 'if type == "array" then [.[].code | "SC" + tostring] else error("Expected ShellCheck diagnostics array") end' "${case_root}/${stage}.stdout") || parse_ok=false
      ;;
    format)
      # Error text on stderr marks a tool failure rather than a formatting difference.
      if [[ ${status} != 0 ]] && grep -qE 'error|unexpected|reached EOF|failed to parse' "${case_root}/${stage}.stderr"; then parse_ok=false; fi
      ;;
    *)
      printf 'Unknown verification stage: %s; reinstall the plugin.\n' "${stage}" >&2
      exit 2
      ;;
  esac
  # Exit 0 (clean) and 1 (findings) are the only statuses that carry a valid result; any other status is a tool failure.
  case "${stage}:${status}" in
    format:0 | format:1 | shellcheck:0 | shellcheck:1) ;;
    *) parse_ok=false ;;
  esac
  expected_codes=$(jq -c --arg stage "${stage}" '.expect[$stage].codes // []' <<< "${control}") || fail "fixtures.json has an invalid expectation for ${filename}; reinstall the plugin."
  expected_exit=$(jq -er --arg stage "${stage}" '.expect[$stage].exit' <<< "${control}") || fail "fixtures.json has an invalid expectation for ${filename}; reinstall the plugin."
  [[ ${expected_exit} == zero || ${expected_exit} == nonzero ]] || {
    printf 'Invalid expected exit condition in fixtures.json; reinstall the plugin.\n' >&2
    exit 2
  }
  # shfmt 3.14.1 exits 1 for a diff and for a parse error alike; only a diff prints an @@ hunk header.
  if [[ ${stage} == format && ${language} == bash && ${expected_exit} == nonzero ]] && ! grep -q '^@@' "${case_root}/${stage}.stdout"; then parse_ok=false; fi
  ok=$(jq -n --argjson actual "${codes:-[]}" --argjson expected "${expected_codes}" --argjson parse_ok "${parse_ok}" --argjson status "${status}" --arg expected_exit "${expected_exit}" '$parse_ok and (($expected - $actual) | length == 0) and (if $expected_exit == "zero" then $status == 0 and ($actual | length) == 0 else $status != 0 end)') || fail "jq failed while comparing ${filename}; jq 1.6 or later is required."
  [[ ${ok} == true ]] || failed=1
  jq -cn --arg file "${filename}" --arg stage "${stage}" --argjson exit "${status}" --argjson codes "${codes:-[]}" --argjson ok "${ok}" --rawfile stdout "${case_root}/${stage}.stdout" --rawfile stderr "${case_root}/${stage}.stderr" '{file:$file,stage:$stage,exit:$exit,diagnosticCodes:$codes,expectedOutcomeMatched:$ok,stdout:$stdout,stderr:$stderr}' >> "${records}" || fail "jq failed while recording ${filename}; jq 1.6 or later is required."
}

index=0
jq -c '.cases[]' "${manifest}" > "${test_root}/cases.jsonl" || fail 'Cannot read the cases in fixtures.json; reinstall the plugin.'
while IFS= read -r control; do
  filename=$(jq -er '.file' <<< "${control}") || fail 'A case in fixtures.json names no file; reinstall the plugin.'
  # A plain name with the .sh.fixture suffix: no path separators, so the copy stays inside the case directory.
  [[ ${filename} =~ ^[a-z0-9_]+\.(sh)\.fixture$ ]] || {
    printf 'fixtures.json names an unsafe control file; reinstall the plugin.\n' >&2
    exit 2
  }
  case_root="${test_root}/${index}"
  mkdir "${case_root}" || fail "Cannot copy ${filename} into the temporary folder; check free space and TMPDIR."
  file="${case_root}/${filename%.fixture}"
  cp "${fixture_root}/${filename}" "${file}" || fail "Cannot copy ${filename} into the temporary folder; check free space and TMPDIR."
  case "${language}" in
    bash)
      cp "${shellcheck_profile}" "${case_root}/.shellcheckrc" || fail "Cannot copy ${filename} into the temporary folder; check free space and TMPDIR."
      cp "${shfmt_profile}" "${case_root}/.editorconfig" || fail "Cannot copy ${filename} into the temporary folder; check free space and TMPDIR."
      run_stage format "${fixture_shfmt}" -d "${file}"
      run_stage shellcheck env -u SHELLCHECK_OPTS "${fixture_shellcheck}" --rcfile="${case_root}/.shellcheckrc" --severity=style --check-sourced --format=json "${file}"
      ;;
    *)
      printf 'Unsupported verification language; reinstall the plugin.\n' >&2
      exit 2
      ;;
  esac
  index=$((index + 1))
done < "${test_root}/cases.jsonl"
((index > 0)) || {
  printf 'fixtures.json lists no controls; reinstall the plugin.\n' >&2
  exit 2
}
jq -s --arg language "${language}" --argjson tools "${tool_metadata}" --argjson matched "$((1 - failed))" '{language:$language,tools:$tools,allExpectedOutcomesMatched:($matched == 1),results:.}' "${records}" || fail 'jq failed while printing the report; jq 1.6 or later is required.'
# The report carries the verdict; exit 0 keeps it whole in Claude Code, which cuts a failed command's output to about 10,000 characters.
exit 0
