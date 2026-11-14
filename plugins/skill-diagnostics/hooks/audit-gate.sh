#!/usr/bin/env bash
# skill-diagnostics Stop hook, in gate mode only ("suggest" and "off" do nothing).
# 1. Adds to ${CLAUDE_PLUGIN_DATA}/pending/<session_id> every skill folder under the project and
#    under ~/.claude/skills that changed after the session marker, which catches skills written
#    by Bash or an outside process; heavy folders (.git, node_modules, ...) are not searched.
#    Inside a Git work tree a new file time is not enough, since a clone, a checkout or a pull
#    writes files nobody edited: the skill must also be changed for Git (see session_change).
# 2. Drops pending skills that are gone, that Git shows the session did not change, or whose
#    verdict file is newer than every file in them.
# 3. For the rest, asks Claude to audit them (additionalContext) up to 2 times per skill without
#    a new change; the third time it lets Claude stop and warns the user (systemMessage).
# Prints one JSON object or nothing.
# Needs bash 3.2+ and jq. When a command fails it writes the error to stderr and exits 1.
set -euo pipefail
export LC_ALL=C
unset CDPATH

# Any failure exits 1, never 2: exit 2 would keep Claude from stopping.
trap '[[ $? -eq 0 ]] || { echo "skill-diagnostics: audit-gate.sh failed" >&2; exit 1; }' EXIT

die() {
  printf 'skill-diagnostics: %s\n' "$1" >&2
  exit 1
}

# normalize PATH: backslashes as slashes, made absolute against $PWD, "." and ".." resolved by
# name, no trailing slash. On Git Bash, /c/... becomes C:/..., the form Claude Code sends.
normalize() {
  local path rest part out='' prefix drive
  path=$(printf '%s' "$1" | tr '\134' /)
  case "${OSTYPE:-}" in
    msys* | cygwin*)
      case "${path}" in
        /[A-Za-z] | /[A-Za-z]/*)
          drive=$(printf '%s' "${path:1:1}" | tr '[:lower:]' '[:upper:]')
          path="${drive}:/${path:3}"
          ;;
        *) ;;
      esac
      ;;
    *) ;;
  esac
  case "${path}" in
    /*) prefix='' ;;
    [A-Za-z]:/*)
      prefix=${path%%/*}
      path=${path#*/}
      ;;
    *)
      path="${PWD}/${path}"
      normalize "${path}"
      return
      ;;
  esac
  rest=${path#/}
  while [[ -n ${rest} ]]; do
    part=${rest%%/*}
    case "${rest}" in
      */*) rest=${rest#*/} ;;
      *) rest='' ;;
    esac
    case "${part}" in
      '' | .) ;;
      ..) out=${out%/*} ;;
      *) out="${out}/${part}" ;;
    esac
  done
  printf '%s\n' "${prefix}${out:-/}"
}

# skill_key FOLDER: the verdict and guard file name; record-verdict.py builds the same.
skill_key() {
  printf '%s' "$1" | sed -e 's/%/%25/g' -e 's|/|%2F|g' -e 's/:/%3A/g'
}

# under PATH PREFIX: sets hit=1 when PATH is PREFIX or inside it.
under() {
  if [[ -n $2 ]]; then
    case "$1" in
      "$2" | "$2"/*) hit=1 ;;
      *) ;;
    esac
  fi
}

# listed FILE LINE: sets hit=1 when FILE has exactly this line.
listed() {
  local line
  if [[ -f $1 ]]; then
    while IFS= read -r line || [[ -n ${line} ]]; do
      if [[ ${line} == "$2" ]]; then
        hit=1
      fi
    done < "$1"
  fi
}

# skipped FOLDER: sets hit=1 for the folders Claude Code overwrites and for this plugin.
skipped() {
  hit=0
  under "$1" "${config}/plugins"
  under "$1" "${config}/skills/synced"
  under "$1" "${own}"
}

# session_change SKILL: sets verdict to "yes" when the session changed SKILL for Git, to "no"
# when it did not, and to "unknown" when Git cannot tell (no git, SKILL outside a work tree or
# ignored by it, or a marker without a start time), in which case the file times alone decide.
# The session changed a skill when
#   - Git lists a file in it as modified, untracked or staged, or
#   - a commit made in this session touches it: a HEAD reflog entry at or after the session
#     start whose action is a commit. A clone, checkout, pull, merge, reset or rebase is not.
# The list of such files is built once per work tree, in ${work}.git.<n>.
session_change() {
  local skill=$1 top prefix index state line when rest sha
  verdict=unknown
  [[ -n ${start} ]] || return 0
  command -v git > /dev/null 2>&1 || return 0
  top=$(git -C "${skill}" rev-parse --show-toplevel 2> /dev/null) || return 0
  [[ -n ${top} ]] || return 0
  if git -C "${skill}" check-ignore -q SKILL.md 2> /dev/null; then
    return 0
  fi
  prefix=$(git -C "${skill}" rev-parse --show-prefix 2> /dev/null) || return 0
  index=0
  while [[ ${index} -lt ${#tops[@]} ]] && [[ ${tops[index]} != "${top}" ]]; do
    index=$((index + 1))
  done
  state="${work}.git.${index}"
  if [[ ${index} -eq ${#tops[@]} ]]; then
    tops[index]=${top}
    {
      git -C "${top}" ls-files -z --modified --others --exclude-standard \
        && git -C "${top}" diff -z --cached --name-only
    } > "${state}.raw" 2> /dev/null || return 0
    while IFS= read -r line; do
      when=${line#*\{}
      when=${when%%\}*}
      case "${when}" in
        '' | *[!0-9]*) continue ;;
        *) ;;
      esac
      # The reflog is newest first: nothing older than the session start can follow.
      [[ ${when} -ge ${start} ]] || break
      rest=${line#* }
      sha=${rest%% *}
      case "${rest#* }" in
        commit:* | 'commit ('*)
          git -C "${top}" diff-tree -z --no-commit-id --name-only -r --root "${sha}" \
            >> "${state}.raw" 2> /dev/null || true
          ;;
        *) ;;
      esac
    done < <(git -C "${top}" reflog show --format='%gd %H %gs' --date=unix HEAD 2> /dev/null || true)
    # One path per line, relative to the work tree; generated folders do not count.
    tr '\0' '\n' < "${state}.raw" \
      | { grep -v -E '(^|/)(\.git|node_modules|\.venv|venv|__pycache__)/' || true; } > "${state}"
  fi
  # A work tree whose state could not be read stays unknown.
  [[ -f ${state} ]] || return 0
  verdict=no
  if [[ -z ${prefix} ]]; then
    if [[ -s ${state} ]]; then
      verdict=yes
    fi
  elif PREFIX="${prefix}" awk 'index($0, ENVIRON["PREFIX"]) == 1 { hit = 1; exit } END { exit !hit }' "${state}"; then
    verdict=yes
  fi
}

# newer FOLDER FILE: sets changed=1 when FOLDER or a file in it is newer than FILE. Generated
# folders (.git, node_modules, .venv, venv, __pycache__) do not count.
newer() {
  local found
  found=$(
    cd -- "$1" \
      && find . \( -type d \( -name .git -o -name node_modules -o -name .venv -o -name venv \
        -o -name __pycache__ \) \) -prune -o -newer "$2" -print
  ) || die "cannot compare the files in $1 with $2"
  changed=0
  if [[ -n ${found} ]]; then
    changed=1
  fi
}

mode=${CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE:-gate}
if [[ ${mode} != gate ]]; then
  exit 0
fi

data=${CLAUDE_PLUGIN_DATA:-}
if [[ -z ${data} ]]; then
  die 'CLAUDE_PLUGIN_DATA is not set'
fi

input=$(cat)
if ! printf '%s' "${input}" | jq -e 'type == "object"' > /dev/null; then
  die 'cannot read the hook input: jq is missing or the input is not a JSON object'
fi
session_id=$(printf '%s' "${input}" | jq -r '.session_id // empty | strings')
case "${session_id}" in
  '' | . | .. | *[!A-Za-z0-9._-]*) die 'the hook input has no usable session_id' ;;
  *) ;;
esac
# stop_hook_active is not read: the guard files below decide when Claude may stop.

data=$(normalize "${data}")
config=$(normalize "${CLAUDE_CONFIG_DIR:-${HOME}/.claude}")
own=''
if [[ -n ${CLAUDE_PLUGIN_ROOT:-} ]]; then
  own=$(normalize "${CLAUDE_PLUGIN_ROOT}")
fi
marker="${data}/sessions/${session_id}"
pending="${data}/pending/${session_id}"
guards="${data}/guard/${session_id}"
work="${pending}.$$"
all="${work}.all"
keep="${work}.keep"
mkdir -p "${data}/pending"
# finish: removes the work files, then turns any failure into exit 1. The status is read before
# the cleanup, whose own status would replace it.
finish() {
  local status=$?
  rm -f "${work}".*
  if [[ ${status} -ne 0 ]]; then
    echo "skill-diagnostics: audit-gate.sh failed" >&2
    exit 1
  fi
}
trap finish EXIT
: > "${all}"
: > "${keep}"
# The session start in seconds since the epoch, which session-start.sh writes in the marker; a
# marker from a version before 0.4.1 is empty, and the file times alone decide.
start=''
if [[ -f ${marker} ]]; then
  IFS= read -r start < "${marker}" || true
  case "${start}" in
    '' | *[!0-9]*) start='' ;;
    *) ;;
  esac
fi
# The Git work trees session_change has listed, by position.
tops=()
if [[ -f ${pending} ]]; then
  cat "${pending}" > "${all}"
fi

# scan ROOT: adds every skill folder under ROOT changed after the marker, unless a verdict or a
# guard file is already newer than its last change.
scan() {
  local root=$1 rel skill key list
  [[ -d ${root} ]] || return 0
  list="${work}.scan"
  (cd -- "${root}" && find . \( -type d \( -name .git -o -name node_modules -o -name .venv \
    -o -name venv -o -name __pycache__ -o -name dist -o -name build -o -name target \) \) \
    -prune -o -type f -name SKILL.md -print0) > "${list}" || die "cannot search ${root} for skills"
  while IFS= read -r -d '' rel; do
    rel=${rel%/SKILL.md}
    rel=${rel#.}
    skill="${root%/}${rel}"
    if [[ -z ${rel} ]]; then
      skill=${root}
    fi
    skipped "${skill}"
    [[ ${hit} == 0 ]] || continue
    newer "${skill}" "${marker}"
    [[ ${changed} == 1 ]] || continue
    session_change "${skill}"
    [[ ${verdict} != no ]] || continue
    key=$(skill_key "${skill}")
    if [[ -f "${data}/verdicts/${key}" ]]; then
      newer "${skill}" "${data}/verdicts/${key}"
      [[ ${changed} == 1 ]] || continue
    fi
    if [[ -f "${guards}/${key}" ]]; then
      newer "${skill}" "${guards}/${key}"
      [[ ${changed} == 1 ]] || continue
    fi
    printf '%s\n' "${skill}" >> "${all}"
  done < "${list}"
  rm -f "${list}"
}

# The scan needs the session marker. A project folder that is the home folder or the root is not
# scanned: it cannot be searched within the hook's timeout.
if [[ -f ${marker} ]]; then
  if [[ -n ${CLAUDE_PROJECT_DIR:-} ]]; then
    project=$(normalize "${CLAUDE_PROJECT_DIR}")
    home=$(normalize "${HOME:-/}")
    case "${project}" in
      / | [A-Za-z]:/ | "${home}") ;;
      *) scan "${project}" ;;
    esac
  fi
  scan "${config}/skills"
fi

# Pending skills that still need an audit, each once.
while IFS= read -r skill || [[ -n ${skill} ]]; do
  [[ -n ${skill} ]] || continue
  hit=0
  listed "${keep}" "${skill}"
  [[ ${hit} == 0 ]] || continue
  [[ -d ${skill} ]] && [[ -f "${skill}/SKILL.md" ]] || continue
  session_change "${skill}"
  [[ ${verdict} != no ]] || continue
  key=$(skill_key "${skill}")
  if [[ -f "${data}/verdicts/${key}" ]]; then
    newer "${skill}" "${data}/verdicts/${key}"
    [[ ${changed} == 1 ]] || continue
  fi
  printf '%s\n' "${skill}" >> "${keep}"
done < "${all}"

if [[ ! -s ${keep} ]]; then
  rm -f "${pending}"
  exit 0
fi

# Loop guard: count the Stop continuations asked for each skill since its last change.
mkdir -p "${guards}"
newline='
'
context=''
paths=''
active=0
while IFS= read -r skill || [[ -n ${skill} ]]; do
  key=$(skill_key "${skill}")
  guard="${guards}/${key}"
  count=0
  if [[ -f ${guard} ]]; then
    newer "${skill}" "${guard}"
    if [[ ${changed} == 0 ]]; then
      count=$(cat "${guard}")
    fi
  fi
  case "${count}" in
    '' | *[!0-9]*) count=0 ;;
    *) ;;
  esac
  count=$((count + 1))
  printf '%s\n' "${count}" > "${guard}"
  if [[ ${count} -le 2 ]]; then
    active=1
  fi
  line="Skill ${skill} changed and has no audit after the change. Run /skill-diagnostics:skills-best-practices on ${skill} before finishing."
  context="${context}${context:+${newline}}${line}"
  paths="${paths}${paths:+, }${skill}"
done < "${keep}"

if [[ ${active} == 1 ]]; then
  mv -f "${keep}" "${pending}"
  jq -cn --arg context "${context}" \
    '{hookSpecificOutput: {hookEventName: "Stop", additionalContext: $context}}'
else
  rm -f "${pending}"
  jq -cn --arg message "skill-diagnostics: ${paths} changed and wasn't audited after the change." \
    '{systemMessage: $message}'
fi
