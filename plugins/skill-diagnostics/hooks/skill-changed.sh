#!/usr/bin/env bash
# skill-diagnostics PostToolUse hook for Write and Edit, in the main agent and in subagents.
# Finds the skill folder of the written file (the nearest folder, upwards, that holds SKILL.md)
# and adds it to ${CLAUDE_PLUGIN_DATA}/pending/<session_id>, one absolute folder per line.
#   gate:    the first time a skill is added, tells Claude to audit it before the turn ends.
#   suggest: once per skill and session, asks Claude to offer the user an audit.
#   off:     does nothing.
# Skips the folders Claude Code overwrites (plugins/ and skills/synced/ under the config folder)
# and this plugin's own folder. Prints one JSON object or nothing.
# Needs bash 3.2+ and jq. When a command fails it writes the error to stderr and exits 1.
set -euo pipefail
export LC_ALL=C
unset CDPATH

# Any failure exits 1, never 2: exit 2 would show stderr to Claude as if the hook had blocked.
trap '[[ $? -eq 0 ]] || { echo "skill-diagnostics: skill-changed.sh failed" >&2; exit 1; }' EXIT

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

mode=${CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE:-gate}
if [[ ${mode} == off ]]; then
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
file_path=$(printf '%s' "${input}" | jq -r '.tool_input.file_path // empty | strings')
case "${session_id}" in
  '' | . | .. | *[!A-Za-z0-9._-]*) die 'the hook input has no usable session_id' ;;
  *) ;;
esac
if [[ -z ${file_path} ]]; then
  exit 0
fi
newline='
'
case "${file_path}" in
  *"${newline}"*) exit 0 ;; # a pending list holds one folder per line
  *) ;;
esac

# The skill folder: the file's own folder or the nearest one above it that holds SKILL.md.
file_path=$(normalize "${file_path}")
dir=${file_path%/*}
case "${dir}" in
  '') dir=/ ;;
  [A-Za-z]:) dir="${dir}/" ;;
  *) ;;
esac
skill=''
while :; do
  if [[ -f "${dir%/}/SKILL.md" ]]; then
    skill=${dir}
    break
  fi
  case "${dir}" in
    / | [A-Za-z]:/) break ;;
    *) ;;
  esac
  dir=${dir%/*}
  case "${dir}" in
    '') dir=/ ;;
    [A-Za-z]:) dir="${dir}/" ;;
    *) ;;
  esac
done
if [[ -z ${skill} ]]; then
  exit 0
fi

config=$(normalize "${CLAUDE_CONFIG_DIR:-${HOME}/.claude}")
own=''
if [[ -n ${CLAUDE_PLUGIN_ROOT:-} ]]; then
  own=$(normalize "${CLAUDE_PLUGIN_ROOT}")
fi
hit=0
under "${skill}" "${config}/plugins"
under "${skill}" "${config}/skills/synced"
under "${skill}" "${own}"
if [[ ${hit} == 1 ]]; then
  exit 0
fi

# The pending list is also the list of skills already announced in this session.
pending="${data}/pending/${session_id}"
hit=0
listed "${pending}" "${skill}"
if [[ ${hit} == 1 ]]; then
  exit 0
fi
mkdir -p "${data}/pending"
printf '%s\n' "${skill}" >> "${pending}"

if [[ ${mode} == suggest ]]; then
  context="Skill ${skill} changed. Once the user has finished working on this skill, offer them an audit with /skill-diagnostics:skills-best-practices ${skill}. Do not run the audit unless the user asks for it."
else
  context="Skill ${skill} changed. Before you finish this turn, audit it with /skill-diagnostics:skills-best-practices ${skill} (audit branch); a Stop hook will remind you until a verdict newer than the change is recorded."
fi
jq -cn --arg context "${context}" \
  '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $context}}'
