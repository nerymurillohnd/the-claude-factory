#!/usr/bin/env bash
# bash-lsp quality gate for sh/bash files, one chain per file:
#   shfmt -w <file> && shellcheck <file>
# No flags and no cd: both run where the hook is invoked, exactly as typed in the session,
# and read their own config. shfmt takes its style from the nearest .editorconfig, else its
# defaults; shellcheck takes its rules from the nearest .shellcheckrc above the script, then
# ~/.shellcheckrc, then ~/.config/shellcheckrc, else its defaults.
# Where the files come from:
#   PostToolUse       Edit/Write           -> tool_input.file_path
#                     Bash                 -> tool_response.bashEditDiff.changedFiles
#                                             (needs "bashEditDiffEnabled": true in user settings)
#   Stop/SubagentStop every file Claude changed in the session (or subagent), read
#                     from the transcript, plus every project file modified since the
#                     session's SessionStart stamp (catches Bash-made changes that
#                     bashEditDiff misses). Every stop re-checks: Claude Code ends the turn
#                     itself after 8 consecutive blocks, so there is no loop to guard.
#   arguments         the files given (manual run: bash shfmt-shellcheck.sh <file>...)
# A file counts as sh/bash when it ends in .sh/.bash or its shebang runs sh or bash
# (directly or via env). zsh is excluded: shellcheck does not support it.
# Findings -> exit 2 with the last 20 lines per file: PostToolUse feeds them to
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

is_shell() {
  local shebang
  case "$1" in
    *.sh | *.bash) return 0 ;;
    *.zsh) return 1 ;;
    *)
      IFS= read -r shebang < "$1" || true
      [[ ${shebang:-} =~ ^#!.*/(env[[:space:]]+(-S[[:space:]]+)?)?(bash|sh)([[:space:]]|$) ]]
      ;;
  esac
}

event=""
if (($# > 0)); then
  collected=$(printf '%s\n' "$@")
else
  input=$(cat)
  if ! command -v jq > /dev/null 2>&1; then
    printf 'bash-lsp gate: jq is not installed, so no files were checked. Install it (brew install jq).\n' >&2
    exit 2
  fi
  if ! event=$(jq -r '.hook_event_name // empty' <<< "${input}") \
    || ! collected=$(collect_files "${event}" "${input}"); then
    printf 'bash-lsp gate: could not read the hook input or transcript, so no files were checked.\n' >&2
    exit 2
  fi
fi
collected=$(sort -u <<< "${collected}")

files=()
while IFS= read -r f; do
  [[ -n ${f} && -f ${f} ]] || continue
  is_shell "${f}" && files+=("${f}")
done <<< "${collected}"
((${#files[@]})) || exit 0

for tool in shfmt shellcheck; do
  if ! command -v "${tool}" > /dev/null 2>&1; then
    printf 'bash-lsp gate: %s is not installed; cannot check %s\n' "${tool}" "${files[*]}" >&2
    exit 2
  fi
done

report=""
reformatted=()
for file in "${files[@]}"; do
  before=$(shasum -a 256 "${file}")
  if ! out=$(shfmt -w "${file}" 2>&1); then
    report+="shfmt failed on ${file}:"$'\n'"$(tail -n 20 <<< "${out}")"$'\n'
    continue
  fi
  after=$(shasum -a 256 "${file}")
  [[ ${after} != "${before}" ]] && reformatted+=("${file}")
  if ! out=$(shellcheck "${file}" 2>&1); then
    report+="shellcheck found issues in ${file}:"$'\n'"$(tail -n 20 <<< "${out}")"$'\n'
  fi
done

if [[ -n ${report} ]]; then
  report+="How to fix these without weakening the gate: fix each finding above in the script, at its file and line, by its SC code. Never suppress it (# shellcheck disable=...) or loosen the shellcheck or shfmt config; every edit is checked again until the file is clean."$'\n'
  ((${#reformatted[@]})) && report+="shfmt reformatted ${reformatted[*]}; re-read before editing."$'\n'
  printf '%s' "${report}" >&2
  exit 2
fi
if ((${#reformatted[@]})) && [[ ${event} == PostToolUse ]]; then
  jq -n --arg f "${reformatted[*]}" '{hookSpecificOutput: {hookEventName: "PostToolUse",
    additionalContext: ("shfmt reformatted " + $f + "; re-read before further edits. shellcheck passed.")}}'
fi
exit 0
