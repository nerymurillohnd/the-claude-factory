#!/usr/bin/env bash
# Post-edit type check of typescript6-lsp-intelligence, for macOS and Linux (Bash 3.2 or later).
#
# It runs the project's own `tsc --noEmit --pretty false --strict` over every TypeScript or
# JavaScript file Claude changed this turn, whenever the event names a changed one. hooks.json runs
# it on three events, each checking on its own, so a file one of them misses in a parallel edit
# is still checked:
#   PostToolUse on Edit|Write  the call's tool_input.file_path.
#   PostToolUse on Bash        the command's tool_response.bashEditDiff.changedFiles, which only
#                              PostToolUse receives.
#   PostToolBatch              every Edit and Write path in tool_calls, once the batch resolves.
# With --new-turn, on UserPromptSubmit, it starts a new turn's list.
#
# Errors in the changed files reach Claude: on PostToolUse as stderr with exit 2, on PostToolBatch
# as additionalContext before the next model call, since exit 2 there would stop the agentic
# loop. Every result reaches the user as a systemMessage. Whether tsc type-checked at all comes from tsc
# itself: --extendedDiagnostics prints "Check time" only when the type checker ran, and
# --listFiles lists the files in the program; hooks/tsc-classify.awk sorts the output. Any
# unexpected failure exits 1, which hooks.json
# turns into a block with onFailure "block". Needs Node.js, which tsc runs on; the hook uses it
# only to read and write JSON.

set -Eeuo pipefail
trap 'printf "typescript6-lsp-intelligence: the hook failed at line %s, so the changed files were not verified.\n" "${LINENO}" >&2; exit 1' ERR

PLUGIN='typescript6-lsp-intelligence'
SKILL="${PLUGIN}:ts-6-writing-and-navigation"
COMMAND='tsc --noEmit --pretty false --strict'
MODE="${1:-}"
TURNS="${CLAUDE_PLUGIN_DATA:+${CLAUDE_PLUGIN_DATA}/turns}"
MAX_LINES=100

if ! command -v node > /dev/null 2>&1; then
  [[ ${MODE} != --new-turn ]] || exit 0
  printf '%s\n' '{"systemMessage":"typescript6-lsp-intelligence: tsc check did not run: Node.js was not found on PATH."}'
  exit 0
fi

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

# Writes the event name, the session key, the cwd and the changed files the event names, one per
# line, to $1: an Edit or Write call's file_path and a Bash call's bashEditDiff.changedFiles on
# PostToolUse, the Edit and Write paths of tool_calls on PostToolBatch.
read_event() {
  node -e '
const e = JSON.parse(require("fs").readFileSync(0, "utf8"))
const id = (v, d) => (typeof v === "string" && v !== "" ? v : d).replace(/[^A-Za-z0-9_-]/g, "_")
const edits = (c) => c && ["Edit", "Write"].includes(c.tool_name) && c.tool_input ? [c.tool_input.file_path] : []
const calls = Array.isArray(e.tool_calls) ? e.tool_calls : [e]
const diff = e.tool_response && typeof e.tool_response === "object" ? e.tool_response.bashEditDiff : undefined
const files = calls
  .flatMap(edits)
  .concat(diff && Array.isArray(diff.changedFiles) ? diff.changedFiles : [])
  .filter((f) => typeof f === "string" && f !== "" && !f.includes("\n"))
const head = [
  typeof e.hook_event_name === "string" ? e.hook_event_name : "",
  id(e.session_id, "unknown") + "-" + id(e.agent_id, "main"),
  typeof e.cwd === "string" ? e.cwd : "",
]
process.stdout.write(head.concat(files).join("\n") + "\n")' > "$1"
}

# Prints the hook's JSON output for event $1: $2 for the user, $3 (optional) for Claude.
emit() {
  node -e '
const event = process.argv[1]
const user = process.argv[2]
const claude = process.argv[3]
const out = { systemMessage: "typescript6-lsp-intelligence: " + user }
if (claude) out.hookSpecificOutput = { hookEventName: event, additionalContext: claude }
process.stdout.write(JSON.stringify(out))' "$1" "$2" "${3:-}"
}

# Prints the physical path of $1 when it is an existing TypeScript or JavaScript file inside the
# project, outside node_modules and .git.
source_file() {
  local file="$1" dir
  case "${file}" in
    /*) ;;
    *) file="${CWD}/${file}" ;;
  esac
  case "${file}" in
    *.ts | *.tsx | *.mts | *.cts | *.js | *.jsx | *.mjs | *.cjs) ;;
    *) return 0 ;;
  esac
  [[ -f ${file} ]] || return 0
  dir="$(cd "$(dirname "${file}")" && pwd -P)" || return 0
  file="${dir}/$(basename "${file}")"
  case "${file}" in
    */node_modules/* | */.git/*) return 0 ;;
    "${BASE}"/*) printf '%s\n' "${file}" ;;
    *) return 0 ;;
  esac
}

# Prints the nearest folder at or above $1 that holds $2, or nothing.
find_up() {
  local dir="$1"
  while :; do
    if [[ -e "${dir}/$2" ]]; then
      printf '%s\n' "${dir}"
      return 0
    fi
    [[ ${dir} != / ]] || return 0
    dir="$(dirname "${dir}")"
  done
}

# Prints the project's node_modules/.bin/tsc nearest to $1, else the tsc on PATH, or nothing.
find_tsc() {
  local dir
  dir="$(find_up "$1" node_modules/.bin/tsc)"
  if [[ -n ${dir} && -x "${dir}/node_modules/.bin/tsc" ]]; then
    printf '%s\n' "${dir}/node_modules/.bin/tsc"
  else
    command -v tsc || return 0
  fi
}

read_event "${TMP}/event"
EVENT="$(sed -n 1p "${TMP}/event")"
KEY="$(sed -n 2p "${TMP}/event")"
CWD="$(sed -n 3p "${TMP}/event")"
BASE="$(cd "${CLAUDE_PROJECT_DIR:-${CWD:-.}}" && pwd -P)"
sed 1,3d "${TMP}/event" > "${TMP}/named"
CHANGED=()
while IFS= read -r line; do
  file="$(source_file "${line}")"
  [[ -z ${file} ]] || CHANGED+=("${file}")
done < "${TMP}/named"

case "${MODE}:${EVENT}" in
  --new-turn:*)
    [[ -z ${TURNS} ]] || rm -f "${TURNS}/${KEY}.list"
    exit 0
    ;;
  :PostToolUse | :PostToolBatch) ;;
  *)
    printf '%s: unexpected arguments "%s" for event "%s".\n' "${PLUGIN}" "${MODE}" "${EVENT}" >&2
    exit 1
    ;;
esac
[[ ${#CHANGED[@]} -gt 0 ]] || exit 0

# The turn's changed files: this call's added to the turn list, then the whole list.
USER_NOTES=()
if [[ -n ${TURNS} ]]; then
  mkdir -p "${TURNS}"
  find "${TURNS}" -type f -mtime +7 -exec rm -f {} +
  printf '%s\n' "${CHANGED[@]}" >> "${TURNS}/${KEY}.list"
  sort -u "${TURNS}/${KEY}.list" > "${TMP}/turn"
else
  printf '%s\n' "${CHANGED[@]}" | sort -u > "${TMP}/turn"
  USER_NOTES+=("turn tracking unavailable (no CLAUDE_PLUGIN_DATA): only this call's files were checked.")
fi

# One group per nearest tsconfig.json folder; files without one are grouped by their own folder.
: > "${TMP}/groups"
while IFS= read -r file; do
  [[ -f ${file} ]] || continue
  folder="$(dirname "${file}")"
  project="$(find_up "${folder}" tsconfig.json)"
  if [[ -n ${project} ]]; then
    printf 'project\t%s\t%s\n' "${project}" "${file}" >> "${TMP}/groups"
  else
    printf 'loose\t%s\t%s\n' "${folder}" "${file}" >> "${TMP}/groups"
  fi
done < "${TMP}/turn"

CLASSIFY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/tsc-classify.awk"

MINE=()
BLIND=()
NOT_CHECKED=()
SKIPPED=()
RAN=()
OTHERS=0
HIDDEN=0
ASK=0

# Runs tsc for one group ($1 kind, $2 folder) and records its findings.
check_group() {
  local kind="$1" folder="$2" tsc version status=0 tag line flag=0 k f file
  local files=() args=() mine=() other=() missing=() unknown=() blind=0
  while IFS=$'\t' read -r k f file; do
    [[ ${k} == "${kind}" && ${f} == "${folder}" ]] || continue
    case "${kind}:${file}" in
      loose:*.js | loose:*.jsx | loose:*.mjs | loose:*.cjs)
        NOT_CHECKED+=("${file#"${BASE}"/} (no tsconfig.json: tsc does not type-check JavaScript by default)")
        ;;
      *) files+=("${file}") ;;
    esac
  done < "${TMP}/groups"
  [[ ${#files[@]} -gt 0 ]] || return 0
  tsc="$(find_tsc "${folder}")"
  if [[ -z ${tsc} ]]; then
    SKIPPED+=("no tsc in the project's node_modules/.bin or on PATH (install TypeScript 6: npm install -g typescript@6)")
    return 0
  fi
  version="$("${tsc}" --version 2>&1)" || version=''
  if [[ ${version} != "Version 6."* ]]; then
    SKIPPED+=("${tsc} reports '${version:-no version}', and this plugin checks TypeScript 6 only")
    ASK=1
    return 0
  fi
  if [[ ${kind} == project ]]; then
    flag=1
    args=(--listFiles --extendedDiagnostics --tsBuildInfoFile "${TMP}/tsc.tsbuildinfo")
  else
    args=(--listFiles --extendedDiagnostics "${files[@]}")
  fi
  (cd "${folder}" && "${tsc}" --noEmit --pretty false --strict "${args[@]}") > "${TMP}/out" 2>&1 || status=$?
  case "${status}" in
    0 | 1 | 2) ;;
    *)
      SKIPPED+=("tsc stopped with status ${status} in ${folder}")
      return 0
      ;;
  esac
  RAN+=("tsc ${version#Version } (${tsc}) in ${folder}")
  printf '%s\n' "${files[@]}" > "${TMP}/edited"
  awk -v folder="${folder}" -v base="${BASE}" -v project="${flag}" \
    -f "${CLASSIFY}" "${TMP}/edited" "${TMP}/out" > "${TMP}/parsed"
  while IFS=$'\t' read -r tag line; do
    case "${tag}" in
      M) mine+=("${line}") ;;
      O) other+=("${line}") ;;
      N) missing+=("${line}") ;;
      B) blind=1 ;;
      *) unknown+=("${line}") ;;
    esac
  done < "${TMP}/parsed"
  if [[ ${#unknown[@]} -gt 0 ]]; then
    printf '%s: tsc printed output the hook could not classify, so the changed files were not verified:\n' "${PLUGIN}" >&2
    printf '%s\n' "${unknown[@]}" | head -20 >&2
    exit 1
  fi
  if [[ ${status} -ne 0 && ${#mine[@]} -eq 0 && ${#other[@]} -eq 0 ]]; then
    printf '%s: tsc exited %s without a diagnostic in %s, so the changed files were not verified.\n' \
      "${PLUGIN}" "${status}" "${folder}" >&2
    exit 1
  fi
  MINE+=(${mine[@]+"${mine[@]}"})
  for line in ${missing[@]+"${missing[@]}"}; do
    NOT_CHECKED+=("${line} (not part of the program of ${folder#"${BASE}"/}/tsconfig.json)")
  done
  if [[ ${blind} -eq 1 && ${#mine[@]} -gt 0 ]]; then
    HIDDEN=1
  elif [[ ${blind} -eq 1 ]]; then
    BLIND+=("${folder#"${BASE}"/}: tsc ran but did not type-check (no Check time in --extendedDiagnostics)${other[0]:+; it reported:}")
    BLIND+=(${other[@]+"${other[@]}"})
  else
    OTHERS=$((OTHERS + ${#other[@]}))
  fi
}

cut -f1,2 "${TMP}/groups" | sort -u > "${TMP}/keys"
while IFS=$'\t' read -r kind folder; do
  check_group "${kind}" "${folder}"
done < "${TMP}/keys"

# Joins the lines of file $1 with ", ".
join_lines() {
  paste -sd ',' "$1" | sed 's/,/, /g'
}

sed "s|^${BASE}/||" "${TMP}/turn" > "${TMP}/shown"
TURN_FILES="$(join_lines "${TMP}/shown")"
RAN_TEXT="$(printf '%s; ' ${RAN[@]+"${RAN[@]}"})"
RAN_TEXT="${RAN_TEXT%; }"
CLAUDE=()

if [[ ${#MINE[@]} -gt 0 ]]; then
  printf '%s\n' "${MINE[@]}" | cut -d: -f1 | sort -u > "${TMP}/mine-files"
  FILES="$(join_lines "${TMP}/mine-files")"
  printf '%s\n' "${MINE[@]}" | head -n "${MAX_LINES}" > "${TMP}/mine-lines"
  LIST="$(cat "${TMP}/mine-lines")"
  [[ ${#MINE[@]} -le ${MAX_LINES} ]] || LIST="${LIST}"$'\n'"… $((${#MINE[@]} - MAX_LINES)) more (run ${COMMAND} to see them all)"
  TEXT="Unresolved type errors in files changed this turn (${FILES}), from ${COMMAND}:"$'\n'"${LIST}"
  [[ ${HIDDEN} -eq 0 ]] || TEXT="${TEXT}"$'\n'"tsc stopped before type-checking, so more errors can appear once these are fixed."
  CLAUDE+=("${TEXT}"$'\n'"The skill \"${SKILL}\" (loaded with the Skill tool when it is not in context) covers navigating with the LSP tool and Grep to fix them.")
  NOUN=issues
  [[ ${#MINE[@]} -ne 1 ]] || NOUN=issue
  USER_NOTES+=("${COMMAND} found ${#MINE[@]} ${NOUN} in ${FILES} (${RAN_TEXT}); Claude received them to fix.")
fi
if [[ ${#BLIND[@]} -gt 0 ]]; then
  printf '%s\n' "${BLIND[@]}" | head -n "${MAX_LINES}" > "${TMP}/blind"
  TEXT="$(cat "${TMP}/blind")"
  USER_NOTES+=("the changed files were not type-checked: ${TEXT}")
  CLAUDE+=("The post-edit type check did not cover the changed files: ${TEXT}")
fi
if [[ ${#NOT_CHECKED[@]} -gt 0 ]]; then
  TEXT="$(printf '%s; ' "${NOT_CHECKED[@]}")"
  USER_NOTES+=("not type-checked: ${TEXT%; }.")
  CLAUDE+=("The post-edit type check did not cover: ${TEXT%; }.")
fi
if [[ ${#SKIPPED[@]} -gt 0 ]]; then
  TEXT="$(printf '%s; ' "${SKIPPED[@]}")"
  USER_NOTES+=("tsc check skipped: ${TEXT%; }.")
  if [[ ${ASK} -eq 1 ]]; then
    CLAUDE+=("The TypeScript 6 check did not run: ${TEXT%; }. How to proceed with type checking is the user's decision.")
  else
    CLAUDE+=("The post-edit type check did not run: ${TEXT%; }.")
  fi
fi
if [[ ${OTHERS} -gt 0 ]]; then
  NOUN=issues
  [[ ${OTHERS} -ne 1 ]] || NOUN=issue
  USER_NOTES+=("${OTHERS} ${NOUN} in other files (their pre-existence was not verified).")
fi
if [[ ${#MINE[@]} -eq 0 && ${#BLIND[@]} -eq 0 && ${#NOT_CHECKED[@]} -eq 0 && ${#SKIPPED[@]} -eq 0 && ${OTHERS} -eq 0 ]]; then
  USER_NOTES+=("${COMMAND}: the compiler completed without diagnostics under the project's configuration (${TURN_FILES}; ${RAN_TEXT}).")
fi

USER_TEXT="$(printf '%s ' ${USER_NOTES[@]+"${USER_NOTES[@]}"})"
CLAUDE_TEXT="$(printf '%s\n' ${CLAUDE[@]+"${CLAUDE[@]}"})"
if [[ ${EVENT} == PostToolUse && ${#MINE[@]} -gt 0 ]]; then
  # PostToolUse: exit 2 shows stderr to Claude, and Claude Code still reads the JSON on stdout.
  printf '%s\n' "${CLAUDE_TEXT}" >&2
  emit "${EVENT}" "${USER_TEXT% }"
  exit 2
fi
emit "${EVENT}" "${USER_TEXT% }" "${CLAUDE_TEXT}"
