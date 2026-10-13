#!/usr/bin/env bash
# basedpyright-lsp quality gate for Python files, one chain per file:
#   ruff check --fix <file>; ruff format <file>; basedpyright --warnings <file>
# No rule or style flags and no cd: ruff and basedpyright run from the directory the hook runs
# in, exactly as typed in the session, and resolve their own config and environment
# (nearest config up the tree, then global, then defaults; basedpyright uses the project's .venv).
# Where the files come from:
#   PostToolUse       Edit/Write           -> tool_input.file_path
#                     NotebookEdit         -> tool_input.notebook_path
#                     Bash                 -> tool_response.bashEditDiff.changedFiles
#                                             (needs "bashEditDiffEnabled": true in user settings)
#   Stop/SubagentStop every file Claude changed in the session (or subagent), read
#                     from the transcript, plus every project file modified since the
#                     session's SessionStart stamp (catches Bash-made changes that
#                     bashEditDiff misses). Every stop re-checks: Claude Code ends the turn
#                     itself after 8 consecutive blocks, so there is no loop to guard.
#   arguments         the files given (manual run: bash ruff-basedpyright.sh <file>...)
# A file counts as Python when it ends in .py/.pyi/.pyw/.ipynb or its shebang runs
# python or `uv run`. A PEP 723 script (`# /// script` block) is checked against its
# uv-managed env (uv sync --script), which basedpyright cannot find on its own; uv is
# needed only for those scripts.
# Findings -> exit 2 with the last 20 lines per tool: PostToolUse feeds them to
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
            | select(.type == "tool_use" and (.name | IN("Edit", "Write", "NotebookEdit")))
            | .input.file_path // .input.notebook_path // empty),
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
          (.tool_input.file_path // .tool_input.notebook_path // .tool_response.filePath // empty)
        end' <<< "${input}"
      ;;
  esac
}

is_python() {
  local shebang
  case "$1" in
    *.py | *.pyi | *.pyw | *.ipynb) return 0 ;;
    *)
      IFS= read -r shebang < "$1" || true
      [[ ${shebang:-} =~ ^#!.*(python[0-9.]*|uv[[:space:]]+run)([[:space:]]|$) ]]
      ;;
  esac
}

event=""
if (($# > 0)); then
  collected=$(printf '%s\n' "$@")
else
  input=$(cat)
  if ! command -v jq > /dev/null 2>&1; then
    printf 'basedpyright-lsp gate: jq is not installed, so no files were checked. Install it (brew install jq).\n' >&2
    exit 2
  fi
  if ! event=$(jq -r '.hook_event_name // empty' <<< "${input}") \
    || ! collected=$(collect_files "${event}" "${input}"); then
    printf 'basedpyright-lsp gate: could not read the hook input or transcript, so no files were checked.\n' >&2
    exit 2
  fi
fi
collected=$(sort -u <<< "${collected}")

files=()
while IFS= read -r f; do
  [[ -n ${f} && -f ${f} ]] || continue
  # Third-party code: virtualenvs and installed packages are never Claude's to fix.
  case "/${f}" in
    */.venv/* | */venv/* | */site-packages/*) continue ;;
    *) ;;
  esac
  is_python "${f}" || continue
  # Absolute path, so every report names the file the same way whatever the caller's cwd.
  dir=$(dirname "${f}")
  dir=$(cd "${dir}" && pwd -P) || continue
  files+=("${dir}/${f##*/}")
done <<< "${collected}"
((${#files[@]})) || exit 0

for tool in ruff basedpyright; do
  if ! command -v "${tool}" > /dev/null 2>&1; then
    printf 'basedpyright-lsp gate: %s is not installed; cannot check %s\n' "${tool}" "${files[*]}" >&2
    exit 2
  fi
done

report=""
rewritten=()
for file in "${files[@]}"; do
  python_path=""
  if grep -q '^# /// script$' "${file}"; then
    if ! command -v uv > /dev/null 2>&1; then
      report+="uv is not installed; cannot build the environment of the PEP 723 script ${file}"$'\n'
      continue
    fi
    if ! out=$(uv sync --script "${file}" --quiet 2>&1); then
      report+="uv sync --script failed for ${file} (fix the PEP 723 block):"$'\n'"$(tail -n 20 <<< "${out}")"$'\n'
      continue
    fi
    python_path=$(uv python find --script "${file}" 2> /dev/null) || python_path=""
  fi

  before=$(shasum -a 256 "${file}")
  if ! out=$(ruff check --fix "${file}" 2>&1); then
    report+="ruff check found issues in ${file}:"$'\n'"$(tail -n 20 <<< "${out}")"$'\n'
  fi
  if ! out=$(ruff format "${file}" 2>&1); then
    report+="ruff format failed on ${file}:"$'\n'"$(tail -n 20 <<< "${out}")"$'\n'
  fi
  after=$(shasum -a 256 "${file}")
  [[ ${after} != "${before}" ]] && rewritten+=("${file}")

  bp_args=(--warnings)
  [[ -n ${python_path} ]] && bp_args+=(--pythonpath "${python_path}")
  if ! out=$(basedpyright "${bp_args[@]}" "${file}" 2>&1); then
    report+="basedpyright found issues in ${file}:"$'\n'"$(tail -n 20 <<< "${out}")"$'\n'
  fi
done

if [[ -n ${report} ]]; then
  report+="How to fix these without weakening the gate: fix each finding above in the code, at its file and line, by its rule. Never suppress it (# noqa, # type: ignore, # pyright: ignore) or loosen the ruff or basedpyright config; every edit is checked again until the file is clean."$'\n'
  ((${#rewritten[@]})) && report+="ruff rewrote ${rewritten[*]}; re-read before editing."$'\n'
  printf '%s' "${report}" >&2
  exit 2
fi
if ((${#rewritten[@]})) && [[ ${event} == PostToolUse ]]; then
  jq -n --arg f "${rewritten[*]}" '{hookSpecificOutput: {hookEventName: "PostToolUse",
    additionalContext: ("ruff rewrote " + $f + "; re-read before further edits. ruff and basedpyright passed.")}}'
fi
exit 0
