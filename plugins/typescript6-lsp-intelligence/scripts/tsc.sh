#!/usr/bin/env bash
# ts-lsp quality gate for TypeScript/JavaScript files, one run per program:
#   tsc --noEmit -p <tsconfig> --listFiles
# The project is the nearest directory above the file that holds any tsconfig*.json, and
# every program that directory declares is checked, not only tsconfig.json: a file often
# belongs to a sibling program (tsconfig.scripts.json, tsconfig.tests.json), and checking
# the config whose name is nearest reported green on a file it had never read. tsc checks
# a whole program, so breakage in files that import the edited one surfaces too, in every
# program that reaches it. Each program runs with the project's own node_modules/.bin/tsc
# when present, else the global tsc, and its tsconfig decides everything (--noEmit only
# keeps the check from writing output). There is no cd: tsc runs where the hook is invoked,
# and -p names the tsconfig by its full path, whose own paths resolve from its directory.
# A tsconfig*.json with no include anywhere in its extends chain and no files of its own
# defines no program: it exists to be extended, and checking it would compile every file
# under the directory with another program's options. tsc --showConfig decides, so an
# include inherited through extends counts. Plain tsconfig.json is always a program, since
# `{}` is a valid one.
# --listFiles names every file each program read, which is what tells the gate whether the
# changed files were checked at all. A file in no program is reported rather than passed
# over in silence, unless it sits in generated output (dist, build, out, coverage, .astro,
# .next, .svelte-kit, .wrangler, .output). Files with no tsconfig*.json above them belong
# to no TypeScript project and are skipped.
# hooks.json registers this script on Stop/SubagentStop only: a whole-project tsc after
# every edit was too slow, and ts-lsp already pushes TypeScript diagnostics after each
# edit. PostToolUse input is still understood, for manual or future use.
# Where the files come from:
#   PostToolUse       Edit/Write           -> tool_input.file_path
#                     Bash                 -> tool_response.bashEditDiff.changedFiles
#                                             (needs "bashEditDiffEnabled": true in user settings)
#   Stop/SubagentStop every file Claude changed in the session (or subagent), read
#                     from the transcript, plus every project file modified since the
#                     session's SessionStart stamp (catches Bash-made changes that
#                     bashEditDiff misses). Every stop re-checks: Claude Code ends the turn
#                     itself after 8 consecutive blocks, so there is no loop to guard.
#   arguments         the files given (manual run: bash tsc.sh <file>...)
# Errors -> exit 2 with the last 20 lines per project: PostToolUse feeds them to
# Claude, Stop/SubagentStop blocks the stop until they are fixed. The gate fails
# closed: a missing jq or an unreadable hook input or transcript also exits 2
# (a transcript that was never written is covered by the stamp scan when a stamp exists).
set -uo pipefail

# Print project files modified since this session's stamp (written by session-stamp.sh),
# one per line. Git work trees: modified and untracked files git doesn't ignore. Elsewhere:
# a find that skips VCS, dependency and cache directories. Never scans $HOME or /.
changed_since_stamp() {
  local input=$1 session_id project stamp rel
  session_id=$(jq -r '.session_id // empty' <<< "${input}") || return 1
  project=${CLAUDE_PROJECT_DIR:-$(jq -r '.cwd // empty' <<< "${input}")} || return 1
  stamp="${CLAUDE_PLUGIN_DATA:-}/sessions/${session_id}.stamp"
  [[ -n ${session_id} && -n ${CLAUDE_PLUGIN_DATA:-} && -f ${stamp} && -d ${project} ]] || return 0
  [[ ${project} == "${HOME}" || ${project} == / ]] && return 0
  if git -C "${project}" rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    git -C "${project}" ls-files -z --modified --others --exclude-standard \
      | while IFS= read -r -d '' rel; do
        [[ "${project}/${rel}" -nt ${stamp} ]] && printf '%s\n' "${project}/${rel}"
      done
  else
    find "${project}" \( -name .git -o -name node_modules -o -name .venv -o -name venv \
      -o -name __pycache__ -o -name .ruff_cache -o -name .cache \) -prune \
      -o -type f -newer "${stamp}" -print 2> /dev/null | head -n 2000
  fi
  return 0
}

# Succeed when changed_since_stamp can see this session: a stamp exists and the project is
# a scannable directory. Lets a stop whose transcript was never written (claude -p
# --no-session-persistence) rely on the stamp scan alone instead of failing.
stamp_covers_session() {
  local input=$1 session_id project
  session_id=$(jq -r '.session_id // empty' <<< "${input}") || return 1
  project=${CLAUDE_PROJECT_DIR:-$(jq -r '.cwd // empty' <<< "${input}")} || return 1
  [[ -n ${session_id} && -n ${CLAUDE_PLUGIN_DATA:-} && -d ${project} ]] || return 1
  [[ ${project} != "${HOME}" && ${project} != / ]] || return 1
  [[ -f "${CLAUDE_PLUGIN_DATA}/sessions/${session_id}.stamp" ]]
}

# Print the candidate files for hook event $1 from hook input $2, one per line.
collect_files() {
  local event=$1 input=$2 transcript
  case "${event}" in
    Stop | SubagentStop)
      transcript=$(jq -r '.agent_transcript_path // .transcript_path // empty' <<< "${input}") || return 1
      if [[ -n ${transcript} && ! -e ${transcript} ]]; then
        # Never written (session not persisted): the stamp scan below must cover the session.
        stamp_covers_session "${input}" || return 1
      elif [[ -n ${transcript} ]]; then
        [[ -f ${transcript} && -r ${transcript} ]] || return 1
        # fromjson? skips a line still being written instead of aborting the read.
        jq -rR 'fromjson? |
          (select(.type == "assistant") | .message.content[]?
            | select(.type == "tool_use" and (.name | IN("Edit", "Write")))
            | .input.file_path // empty),
          (.toolUseResult | objects | .bashEditDiff.changedFiles // [] | .[])
          ' "${transcript}" || return 1
      fi
      changed_since_stamp "${input}" || return 1
      ;;
    *)
      jq -r '
        if .tool_name == "Bash" then
          (.tool_response.bashEditDiff.changedFiles // [])[]
        else
          (.tool_input.file_path // .tool_response.filePath // empty)
        end' <<< "${input}"
      ;;
  esac
}

# Print the first directory from $1 upward that contains one of the markers.
find_up() {
  local dir=$1 marker
  shift
  dir=$(cd "${dir}" 2> /dev/null && pwd -P) || return 1
  while :; do
    for marker in "$@"; do
      if [[ -e "${dir}/${marker}" ]]; then
        printf '%s' "${dir}"
        return 0
      fi
    done
    [[ ${dir} == / ]] && return 1
    dir=$(dirname "${dir}")
  done
}

# Print the first directory from $1 upward that holds any tsconfig*.json.
find_up_tsconfig() {
  local dir=$1 cfg
  dir=$(cd "${dir}" 2> /dev/null && pwd -P) || return 1
  while :; do
    for cfg in "${dir}"/tsconfig*.json; do
      if [[ -f ${cfg} ]]; then
        printf '%s' "${dir}"
        return 0
      fi
    done
    [[ ${dir} == / ]] && return 1
    dir=$(dirname "${dir}")
  done
}

# Print the base name of every tsconfig*.json in directory $1 that declares a program of its
# own, using the tsc at $2, one per line. A config is a program when it is the conventional
# tsconfig.json (`{}` is a valid program), when it declares files itself, or when tsc resolves
# an include for it. The include is read from tsc --showConfig rather than from the file, so a
# config that inherits its include through extends counts: reading the text alone skipped it
# and then called its files unchecked. A config with no include anywhere in its extends chain
# is a catch-all meant to be extended, and checking it would compile every file beside it with
# another program's options; one tsc cannot resolve at all is checked, so tsc reports why.
# The files pattern accepts the key at the start of a line or after { or , so that a
# commented-out or prose mention inside a JSONC comment is not read as a declaration.
program_configs() {
  local dir=$1 tsc=$2 cfg resolved
  for cfg in "${dir}"/tsconfig*.json; do
    [[ -f ${cfg} ]] || continue
    if [[ ${cfg##*/} == tsconfig.json ]] \
      || grep -qE '(^|[{,])[[:space:]]*"files"[[:space:]]*:' "${cfg}"; then
      printf '%s\n' "${cfg##*/}"
      continue
    fi
    if ! resolved=$("${tsc}" --showConfig -p "${cfg}" 2>&1) \
      || grep -qE '^[[:space:]]*"include"[[:space:]]*:' <<< "${resolved}"; then
      printf '%s\n' "${cfg##*/}"
    fi
  done
}

# Print $1 with its directory resolved, so it compares equal to the paths tsc --listFiles
# prints (/tmp and /private/tmp are the same directory on macOS, spelled two ways).
canonical_path() {
  local dir
  dir=$(cd "$(dirname "$1")" 2> /dev/null && pwd -P) || return 1
  printf '%s/%s' "${dir}" "${1##*/}"
}

if (($# > 0)); then
  collected=$(printf '%s\n' "$@")
else
  input=$(cat)
  if ! command -v jq > /dev/null 2>&1; then
    printf 'ts-lsp gate: jq is not installed, so no files were checked. Install it (brew install jq).\n' >&2
    exit 2
  fi
  if ! event=$(jq -r '.hook_event_name // empty' <<< "${input}") \
    || ! collected=$(collect_files "${event}" "${input}"); then
    printf 'ts-lsp gate: could not read the hook input or transcript, so no files were checked.\n' >&2
    exit 2
  fi
fi
collected=$(sort -u <<< "${collected}")

projects=()
candidates=()
while IFS= read -r f; do
  [[ -n ${f} && -f ${f} ]] || continue
  case "${f}" in
    *.ts | *.tsx | *.mts | *.cts | *.js | *.jsx | *.mjs | *.cjs) ;;
    *) continue ;;
  esac
  [[ ${f} == */node_modules/* ]] && continue
  dir=$(dirname "${f}")
  dir=$(find_up_tsconfig "${dir}") || continue
  canonical=$(canonical_path "${f}") || continue
  candidates+=("${canonical}")
  seen=0
  for known in ${projects[@]+"${projects[@]}"}; do
    [[ ${known} == "${dir}" ]] && seen=1 && break
  done
  ((seen)) || projects+=("${dir}")
done <<< "${collected}"
((${#projects[@]})) || exit 0

report=""
read_files=""
for dir in "${projects[@]}"; do
  if bin_dir=$(find_up "${dir}" node_modules/.bin/tsc); then
    tsc="${bin_dir}/node_modules/.bin/tsc"
  elif ! tsc=$(command -v tsc); then
    printf 'ts-lsp gate: tsc is not installed; cannot check %s\n' "${dir}" >&2
    exit 2
  fi
  configs=$(program_configs "${dir}" "${tsc}") || configs=""
  while IFS= read -r cfg; do
    [[ -n ${cfg} ]] || continue
    out=$("${tsc}" --noEmit -p "${dir}/${cfg}" --listFiles 2>&1)
    # tsc prints the file list and the diagnostics to the same stream, and prints the list
    # even when the program has errors. A config error (TS18003, an include matching
    # nothing) has no file:line prefix, so the pattern must not require one.
    errors=$(grep -E 'error TS[0-9]+' <<< "${out}")
    read_files+=$(grep '^/' <<< "${out}")$'\n'
    if [[ -n ${errors} ]]; then
      report+="tsc found errors in ${dir} (${cfg}):"$'\n'"$(tail -n 20 <<< "${errors}")"$'\n'
    fi
  done <<< "${configs}"
done

uncovered=""
for f in ${candidates[@]+"${candidates[@]}"}; do
  # Generated output belongs to no program by design, so it is not a finding.
  case "${f}" in
    */dist/* | */build/* | */out/* | */coverage/* | */.astro/* | */.next/* | \
      */.svelte-kit/* | */.wrangler/* | */.output/*) continue ;;
    *) ;;
  esac
  grep -Fxq "${f}" <<< "${read_files}" && continue
  uncovered+="  ${f}"$'\n'
done
if [[ -n ${uncovered} ]]; then
  report+="these files are in no TypeScript program, so tsc never checked them:"$'\n'
  report+="${uncovered}"
  report+="Add each one to the include or files of a tsconfig in its project."$'\n'
fi

if [[ -n ${report} ]]; then
  report+="How to fix these without weakening the gate: fix each error above in the code, at its file and line, by its TS code. Never suppress it (@ts-ignore, @ts-expect-error, any, or a cast only to silence it) or loosen the tsconfig; every stop is checked again until the projects are clean."$'\n'
  printf '%s' "${report}" >&2
  exit 2
fi
exit 0
