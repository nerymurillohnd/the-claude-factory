#!/usr/bin/env bash
# PreToolUse hook for Bash: denies every pip command. This repository installs and runs Python
# tools, interpreters and packages with uv only (uv tool install, uvx, uv python install,
# uv run --script); pip is never used, in any form.
#
# Denied, in command position (after the start, ;, &&, ||, |, (, $( or a newline, past any
# VAR=value assignments and the wrappers sudo, env, command, exec, nohup, time, xargs):
#   pip, pip3, pip3.12 and the like, by bare name or by path (/usr/bin/pip3);
#   python, python3 or python3.x followed by `-m pip` or `-m ensurepip`;
#   uv pip ...;
#   ensurepip.
# A mention of the word in an argument, such as a commit message, is not a command and passes.
set -euo pipefail

input="$(cat)"

# The Bash command of the hook input, still JSON-escaped.
command_text=""
command_pattern='"command"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)"'
if [[ ${input} =~ ${command_pattern} ]]; then
  command_text="${BASH_REMATCH[1]}"
else
  # No command to judge: let the call go on to the normal permission flow.
  exit 0
fi

found=""

# pip, pip3, pip3.12 or ensurepip; python, python3 or python3.12.
pip_word='^(pip[0-9]*(\.[0-9]+)?|ensurepip)$'
python_word='^python[0-9]*(\.[0-9]+)?$'

# Sets found to the offending command when one command of $1 runs pip.
detect_pip() {
  local text="$1" part i word next module
  local -a parts words
  local bs=$'\\'
  text="${text//"${bs}n"/;}"
  text="${text//\$(/;}"
  text="${text//(/;}"
  text="${text//&&/;}"
  text="${text//||/;}"
  text="${text//|/;}"
  text="${text//&/;}"
  IFS=';' read -r -a parts <<< "${text}"
  for part in "${parts[@]}"; do
    read -r -a words <<< "${part}"
    i=0
    while [[ ${words[i]:-} =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; do
      i=$((i + 1))
    done
    while [[ ${words[i]:-} =~ ^(sudo|env|command|exec|nohup|time|xargs)$ ]]; do
      i=$((i + 1))
      while [[ ${words[i]:-} == -* || ${words[i]:-} =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; do
        i=$((i + 1))
      done
    done
    # The last path segment of the command word: /usr/bin/pip3 -> pip3.
    word="${words[i]:-}"
    word="${word##*/}"
    next="${words[i + 1]:-}"
    module="${words[i + 2]:-}"
    if [[ ${word} =~ ${pip_word} ]]; then
      found="${part}"
    elif [[ ${word} =~ ${python_word} && ${next} == -m && ${module} =~ ${pip_word} ]]; then
      found="${part}"
    elif [[ ${word} =~ ${python_word} && ${next} =~ ^-m(pip|ensurepip)$ ]]; then
      found="${part}"
    elif [[ ${word} == uv && ${next} == pip ]]; then
      found="${part}"
    fi
    [[ -z ${found} ]] || return 0
  done
}

detect_pip "${command_text}"
[[ -n ${found} ]] || exit 0

# Trim the offending command for the message and escape it for JSON.
found="${found#"${found%%[![:space:]]*}"}"
found="${found:0:200}"
backslash=$'\\'
quote='"'
found="${found//"${backslash}"/"${backslash}${backslash}"}"
found="${found//"${quote}"/"${backslash}${quote}"}"
reason="pip is never used in this repository. Blocked: ${found}. Use uv instead: uv tool install <tool>==<version> for a CLI tool, uvx <tool> to run one once, uv python install <version> for an interpreter, and PEP 723 metadata with uv run --script for a script's dependencies. If uv itself cannot do it, stop and ask Nery."
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "${reason}"
