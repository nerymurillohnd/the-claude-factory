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
masked=""

# pip, pip3, pip3.12 or ensurepip; python, python3 or python3.12.
pip_word='^(pip[0-9]*(\.[0-9]+)?|ensurepip)$'
python_word='^python[0-9]*(\.[0-9]+)?$'

# Sets masked to $1, the JSON-escaped command, with a space in place of every character the
# shell does not read as command text: quote marks, what single or double quotes hold, an
# escaped character, and the body of a heredoc whose delimiter is quoted. A $( ) inside double
# quotes runs a command, so its text is kept. A heredoc with an unquoted delimiter can run $( ),
# so its body stays and is read as commands. Bash 3.2 syntax only.
mask_quoted() {
  local s="$1" c two n i=0 state=0 esc=0 depth top
  local hd="" hd_dash=0 j delim rest line k
  local -a sub=()
  local bs=$'\\'
  local dq="${bs}\""
  n=${#s}
  masked=""
  while ((i < n)); do
    c="${s:i:1}"
    if [[ ${c} == "${bs}" ]]; then
      # A JSON escape: \" is a shell double quote, \\ a shell backslash, \n a newline.
      two="${s:i:2}"
      i=$((i + 2))
      if [[ ${two} == "${dq}" ]]; then
        if ((esc == 1 || state == 1)); then
          esc=0
        elif ((state == 2)); then
          state=0
        else
          state=2
        fi
        masked+=" "
      elif [[ ${two} == "${bs}${bs}" ]]; then
        if ((state != 1)); then
          esc=$((1 - esc))
        fi
        masked+=" "
      elif [[ ${two} == "${bs}n" ]]; then
        esc=0
        if ((state != 0)); then
          masked+=" "
          continue
        fi
        masked+="${two}"
        if [[ -n ${hd} ]]; then
          # Skip a quoted heredoc's body, up to the line that holds only its delimiter.
          k=${i}
          while ((k < n)); do
            rest="${s:k}"
            line="${rest%%"${bs}n"*}"
            k=$((k + ${#line}))
            if ((hd_dash == 1)); then
              while [[ ${line} == "${bs}t"* ]]; do
                line="${line:2}"
              done
            fi
            [[ ${line} != "${hd}" ]] || break
            k=$((k + 2))
          done
          masked+=" "
          i=${k}
          hd=""
        fi
      else
        esc=0
        masked+=" "
      fi
      continue
    fi
    if ((esc == 1)); then
      esc=0
      masked+=" "
      i=$((i + 1))
      continue
    fi
    if ((state == 1)); then
      [[ ${c} != "'" ]] || state=0
      masked+=" "
      i=$((i + 1))
      continue
    fi
    if ((state == 2)); then
      if [[ ${s:i:2} == "\$(" ]]; then
        sub[${#sub[@]}]=0
        state=0
        masked+="\$("
        i=$((i + 2))
      else
        masked+=" "
        i=$((i + 1))
      fi
      continue
    fi
    if [[ ${c} == "'" ]]; then
      state=1
      masked+=" "
      i=$((i + 1))
      continue
    fi
    if [[ ${s:i:2} == "<<" && ${s:i:3} != "<<<" ]]; then
      j=$((i + 2))
      hd_dash=0
      if [[ ${s:j:1} == "-" ]]; then
        hd_dash=1
        j=$((j + 1))
      fi
      while [[ ${s:j:1} == " " ]]; do
        j=$((j + 1))
      done
      if [[ ${s:j:1} == "'" ]]; then
        rest="${s:j+1}"
        delim="${rest%%\'*}"
        hd="${delim}"
        j=$((j + 1 + ${#delim} + 1))
      elif [[ ${s:j:2} == "${dq}" ]]; then
        rest="${s:j+2}"
        delim="${rest%%"${dq}"*}"
        hd="${delim}"
        j=$((j + 2 + ${#delim} + 2))
      fi
      masked+=" "
      i=$((i + 2))
      [[ -z ${hd} ]] || i=${j}
      continue
    fi
    top=$((${#sub[@]} - 1))
    if ((top >= 0)) && [[ ${c} == "(" ]]; then
      sub[top]=$((sub[top] + 1))
    elif ((top >= 0)) && [[ ${c} == ")" ]]; then
      depth=${sub[top]}
      if ((depth == 0)); then
        unset "sub[top]"
        state=2
        masked+=" "
        i=$((i + 1))
        continue
      fi
      sub[top]=$((depth - 1))
    fi
    masked+="${c}"
    i=$((i + 1))
  done
}

# Sets found to the offending command when one command of $1 runs pip.
detect_pip() {
  local text part i word next module
  local -a parts words
  local bs=$'\\'
  mask_quoted "$1"
  text="${masked}"
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
