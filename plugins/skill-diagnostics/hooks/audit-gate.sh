#!/usr/bin/env bash
# skill-diagnostics Stop hook, in gate mode only ("suggest" and "off" do nothing).
# 1. Adds to ${CLAUDE_PLUGIN_DATA}/pending/<session_id> every skill folder under the project and
#    under ~/.claude/skills that changed after the session marker, which catches skills written
#    by Bash or an outside process; heavy folders (.git, node_modules, ...) are not searched.
# 2. Drops pending skills that are gone, or whose verdict file is newer than every file in them.
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
all="${pending}.$$.all"
keep="${pending}.$$.keep"
mkdir -p "${data}/pending"
trap 'rm -f "${all}" "${keep}"; [[ $? -eq 0 ]] || { echo "skill-diagnostics: audit-gate.sh failed" >&2; exit 1; }' EXIT
: > "${all}"
: > "${keep}"
if [[ -f ${pending} ]]; then
  cat "${pending}" > "${all}"
fi

# scan ROOT: adds every skill folder under ROOT changed after the marker, unless a verdict or a
# guard file is already newer than its last change.
scan() {
  local root=$1 rel skill key list
  [[ -d ${root} ]] || return 0
  list="${pending}.$$.scan"
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
