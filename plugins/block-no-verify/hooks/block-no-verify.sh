#!/usr/bin/env bash
# Claude Code PreToolUse handler (Bash and PowerShell tools). Denies Git
# commands that bypass local verification (Git hooks: pre-commit, husky,
# lefthook, ...) or commit/tag signing when Claude runs them.
#
# Contract:
#   stdin   one PreToolUse JSON payload
#   allow   exit 0, no output
#   deny    hookSpecificOutput JSON on stdout, the reason on stderr, exit 2.
#           Exit 2 blocks even if something (a shell profile) corrupts stdout.
#   errors  fail closed: malformed payloads, unterminated quotes, and internal
#           errors deny. Payloads for other tools, or without a string
#           tool_input.command, pass through.
#
# Requires bash >= 3.2 and jq >= 1.6 (git optional, read-only, for aliases).
# Standard tools only; no network, no writes. Parsing is metered so no input can
# outlast the hook timeout (a timed-out hook does not block). Documented blind
# spots: values from outside the command (functions, earlier exports, scripts
# run from files) and anything outside Claude's tool calls.

set -E -o pipefail
export LC_ALL=C

readonly MAX_DEPTH=3
readonly GUIDANCE="Do not retry with another bypass. Run the command without it and fix the underlying hook or signing failure; if the hook itself is wrong, ask the user to fix or skip it themselves."

MODE=posix # posix | psh (PowerShell tool payloads)
CUR_DEPTH=0
LEVEL_TEXT=""  # the command text of the level being analyzed
NONGIT_TEXT="" # segments of the level that invoke no git (where values are set)
PAYLOAD_CWD="" # the tool call's working directory, for alias lookup
GIT_ENV=()
TK_S=""     # the text being tokenized (global: bash copies strings passed as arguments)
CMD_TEXT="" # the whole command, for the over-budget text check
WORK=0
readonly WORK_LIMIT=20000000
# Anchored negated-class regexes for tk_find and chunk scans (ERE; a backslash
# inside brackets is literal).
readonly R_PAREN=$'^[^\\\\\'"()#<\n]*'
readonly R_NL=$'^[^\n]*'
readonly R_SQ="^[^']*"
readonly R_DQQ='^[^"]*'
readonly R_DQ='^[^"\\]*'
readonly R_HDSUB='^[^\\$`]*'
readonly R_BT='^[^\\`]*'
readonly R_BRACE='^[^}]*'
readonly R_WORD='^[^[:space:];&|()<>'"'"'"\\$`]*'
readonly R_WORD_PS='^[^[:space:];&|(){}<>'"'"'"`$#@]*'
readonly R_DQCH='^[^"\\$`]*'
readonly R_DQ_PS='^[^"`$]*'
HD_BODY=""

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\n'/\\n}
  s=${s//$'\r'/\\r}
  s=${s//$'\t'/\\t}
  s=${s//[$'\x01'-$'\x1f']/}
  RET=${s}
}

deny() {
  local detail=$1 reason
  if ((${#detail} > 160)); then
    detail="${detail:0:160}..."
  fi
  reason="block-no-verify: ${detail}. ${GUIDANCE}"
  json_escape "${reason}"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "${RET}"
  printf '%s\n' "${reason}" >&2
  exit 2
}

on_internal_error() {
  trap - ERR
  deny "internal error in the handler (line $1); failing closed"
}
trap 'on_internal_error ${LINENO}' ERR

# --- small predicates ---------------------------------------------------------

lower() { # sets LOWER; forks tr only when there is an uppercase ASCII letter
  if [[ $1 == *[A-Z]* ]]; then
    LOWER=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
  else
    LOWER=$1
  fi
}

base_name() { # sets BASE: lowercase last path component, without a .exe suffix
  # No command name is this long; skipping huge words (messages) keeps bash
  # 3.2's quadratic ${var##pattern} off them.
  if ((${#1} > 255)); then
    BASE=""
    return 0
  fi
  local w=${1##*/}
  w=${w##*\\}
  w=${w#=} # zsh =cmd expansion
  lower "${w}"
  BASE=${LOWER%.exe}
}

# Git booleans: true/yes/on or a non-zero integer (strtoimax base 0, so hex
# and octal count, after leading whitespace, with an optional k/m/g unit).
# Anything else is false or rejected by git, so treat it as not true.
is_true() {
  lower "$1"
  local v=${LOWER}
  while [[ ${v} == [[:space:]]* ]]; do v=${v#?}; done
  [[ ${v} == true || ${v} == yes || ${v} == on ]] && return 0
  [[ ${v} =~ ^[+-]?0*[1-9][0-9]*[kmg]?$ ]] && return 0
  [[ ${v} =~ ^[+-]?0x0*[1-9a-f][0-9a-f]*[kmg]?$ ]] && return 0
  return 1
}

# A persistent core.hooksPath that stays inside the repository (versioned,
# reviewable hooks) rather than pointing at an empty or external location.
is_repo_hooks_path() {
  lower "$1"
  local v=${LOWER}
  [[ -n ${v} ]] || return 1
  case ${v} in
    /* | ~* | \\* | [a-z]:* | *..* | nul | .) return 1 ;;
    *) return 0 ;;
  esac
}

# long option $1 is an accepted abbreviation (or the full spelling) of $2
abbrev_of() {
  local opt=$1 full=$2 min=$3
  ((${#opt} >= min)) || return 1
  ((${#opt} <= ${#full})) || return 1
  [[ ${full:0:${#opt}} == "${opt}" ]]
}

is_protected_key() {
  lower "$1"
  case ${LOWER} in
    commit.gpgsign | tag.gpgsign | tag.forcesignannotated | core.hookspath | gpg.program | gpg.*.program | include.path | includeif.*) return 0 ;;
    *) return 1 ;;
  esac
}

# Conservative text check for contexts the parser cannot resolve (nesting past
# MAX_DEPTH, commands fed from pipes, unresolved command words).
has_marker() {
  lower "$1"
  local t=${LOWER}
  case ${t} in
    *no-v* | *no-gp* | *no-si* | *gpgsign* | *hookspath* | *husky* | *lefthook* | *pre_commit* | *skip=* | *skip_simple* | *overcommit* | *git_config* | *gpg.* | *config-env* | *include.path* | *includeif* | *editor=* | *commit-tree*) return 0 ;;
    *) ;;
  esac
  [[ ${t} =~ (commit|am)[^\;\&\|]*[[:space:]]-[[:alpha:]]*n ]] && return 0
  return 1
}

looks_like_bypass() {
  lower "$1"
  [[ ${LOWER} == *git* ]] || return 1
  has_marker "$1"
}

check_opaque() { # $1 text, $2 what it is
  if looks_like_bypass "$1"; then
    deny "$2 could hide a verification or signing bypass and cannot be checked; run the git command directly"
  fi
}

# --- tokenizer ----------------------------------------------------------------
# Fills TK_WORDS/TK_KINDS (kind w = word, s = separator), TK_STDIN (heredoc and
# here-string text per segment index) and TK_SUBST (command substitution bodies).

TK_WORDS=()
TK_KINDS=()
TK_STDIN=()
TK_SUBST=()
TK_PIPED=() # 1 when the segment's stdin comes from a pipe

tk_reset() {
  TK_WORDS=()
  TK_KINDS=()
  TK_STDIN=()
  TK_SUBST=()
  TK_PIPED=()
  T_SEG=0
  T_CUR=""
  T_HAVE=0
  T_REDIR=0
  T_HD_DELIMS=()
  T_HD_STRIP=()
  T_HD_QUOTED=()
  T_HD_SEG=()
  T_HERESTR=0
  TK_PIPED[0]=0
}

tk_finish_word() {
  if ((T_HAVE)); then
    if ((T_HERESTR)); then
      TK_STDIN[T_SEG]="${TK_STDIN[T_SEG]}${T_CUR}"$'\n'
      T_HERESTR=0
    elif ((T_REDIR)); then
      :
    else
      TK_WORDS+=("${T_CUR}")
      TK_KINDS+=(w)
    fi
    T_REDIR=0
  fi
  T_CUR=""
  T_HAVE=0
}

tk_sep() { # $1: 1 when the next segment reads from a pipe
  tk_finish_word
  TK_WORDS+=("")
  TK_KINDS+=(s)
  T_SEG=$((T_SEG + 1))
  TK_PIPED[T_SEG]=${1:-0}
}

# Every scan step costs time proportional to the text length in bash, so the
# work is metered. Past the budget the command is too large to parse within
# the hook's time limit, and only a conservative text check is applied.
work() {
  WORK=$((WORK + ${#TK_S} + 64))
  if ((WORK > WORK_LIMIT)); then
    if looks_like_bypass "${CMD_TEXT}"; then
      deny "the command is too large to analyze within the hook's time budget and mentions a verification or signing bypass; run smaller commands"
    fi
    exit 0
  fi
}

# Sets MATCH to the index of the first character after the run that regex $1
# (an anchored negated class, e.g. ^[^"]*) matches, starting at $2 in TK_S,
# or -1. Bounded windows and regexec keep each step linear even in bash 3.2,
# whose ${var%%pattern} is quadratic.
tk_find() {
  local i=$2 n=${#TK_S} w
  while ((i < n)); do
    work
    w=${TK_S:i:1024}
    [[ ${w} =~ $1 ]] || true
    if ((${#BASH_REMATCH[0]} < ${#w})); then
      MATCH=$((i + ${#BASH_REMATCH[0]}))
      return 0
    fi
    i=$((i + ${#w}))
  done
  MATCH=-1
}

# Heredoc body starting at $1 with delimiter $2 ($3 = 1 for <<-). Sets HD_BODY
# and MATCH (index after the delimiter line, or the end of the text).
tk_heredoc_end() {
  local i=$1 d=$2 strip=$3 line cmp consumed=0
  work
  HD_BODY=""
  while IFS= read -r line; do
    consumed=$((consumed + ${#line} + 1))
    cmp=${line}
    if [[ ${strip} == 1 ]]; then
      while [[ ${cmp} == $'\t'* ]]; do cmp=${cmp#$'\t'}; done
    fi
    [[ ${cmp} == "${d}" ]] && break
    HD_BODY+="${line}"$'\n'
  done <<< "${TK_S:i}"
  MATCH=$((i + consumed))
  ((MATCH <= ${#TK_S})) || MATCH=${#TK_S}
}

# Index of the closing ) of a $( starting at $2 (just after the paren), or -1.
# Aware of quotes, comments, and heredocs, so a body such as
# $(cat <<'EOF' ... don't ... EOF) matches correctly.
tk_match_paren() {
  local i=$1 start=$1 n=${#TK_S} depth=1 c j prev delim rest strip
  local -a hd=() hs=()
  while ((i < n)); do
    tk_find "${R_PAREN}" "${i}"
    ((MATCH >= 0)) || break
    i=${MATCH}
    c=${TK_S:i:1}
    case ${c} in
      \\) i=$((i + 2)) ;;
      $'\n')
        i=$((i + 1))
        for j in "${!hd[@]}"; do
          tk_heredoc_end "${i}" "${hd[j]}" "${hs[j]}"
          i=${MATCH}
        done
        hd=()
        hs=()
        ;;
      \#)
        prev=${TK_S:i-1:1}
        if ((i == start)) || [[ ${prev} == [[:space:]\;\&\|\(] ]]; then
          tk_find "${R_NL}" "${i}"
          if ((MATCH < 0)); then i=${n}; else i=${MATCH}; fi
        else
          i=$((i + 1))
        fi
        ;;
      \<)
        if [[ ${TK_S:i:2} == '<<' && ${TK_S:i+2:1} != \< ]]; then
          i=$((i + 2))
          strip=0
          if [[ ${TK_S:i:1} == - ]]; then
            strip=1
            i=$((i + 1))
          fi
          while [[ ${TK_S:i:1} == [\ $'\t'] ]]; do i=$((i + 1)); done
          rest=${TK_S:i:256}
          delim=${rest%%[[:space:]\;\&\|\)\<\>]*}
          i=$((i + ${#delim}))
          delim=${delim//[\'\"\\]/}
          hd+=("${delim}")
          hs+=("${strip}")
        else
          i=$((i + 1))
        fi
        ;;
      \')
        tk_find "${R_SQ}" $((i + 1))
        if ((MATCH < 0)); then return 0; fi
        i=$((MATCH + 1))
        ;;
      \")
        i=$((i + 1))
        while :; do
          tk_find "${R_DQ}" "${i}"
          if ((MATCH < 0)); then return 0; fi
          i=${MATCH}
          if [[ ${TK_S:i:1} == \\ ]]; then i=$((i + 2)); else break; fi
        done
        i=$((i + 1))
        ;;
      \()
        depth=$((depth + 1))
        i=$((i + 1))
        ;;
      \))
        depth=$((depth - 1))
        if ((depth == 0)); then
          MATCH=${i}
          return 0
        fi
        i=$((i + 1))
        ;;
      *) i=$((i + 1)) ;;
    esac
  done
  MATCH=-1
}

# Index of the closing backtick for a backtick starting at $2, or -1.
tk_match_backtick() {
  local i=$(($1 + 1))
  while :; do
    tk_find "${R_BT}" "${i}"
    ((MATCH >= 0)) || return 0
    i=${MATCH}
    if [[ ${TK_S:i:1} == \\ ]]; then i=$((i + 2)); else return 0; fi
  done
}

# Queues the $(...) and backtick substitutions inside an unquoted heredoc body.
tk_heredoc_substs() {
  local outer=${TK_S} i=0
  TK_S=$1
  while :; do
    tk_find "${R_HDSUB}" "${i}"
    ((MATCH >= 0)) || break
    i=${MATCH}
    case ${TK_S:i:1} in
      \\) i=$((i + 2)) ;;
      \$)
        if [[ ${TK_S:i+1:1} == \( ]]; then
          tk_match_paren $((i + 2))
          if ((MATCH < 0)); then deny "unterminated command substitution in a heredoc; failing closed"; fi
          TK_SUBST+=("${TK_S:i+2:MATCH-i-2}")
          i=$((MATCH + 1))
        else
          i=$((i + 1))
        fi
        ;;
      *)
        tk_match_backtick "${i}"
        if ((MATCH < 0)); then deny "unterminated backtick substitution in a heredoc; failing closed"; fi
        TK_SUBST+=("${TK_S:i+1:MATCH-i-1}")
        i=$((MATCH + 1))
        ;;
    esac
  done
  TK_S=${outer}
}

# Reads pending heredoc bodies starting at T_I (just after a newline).
tk_read_heredocs() {
  local k body
  for k in "${!T_HD_DELIMS[@]}"; do
    tk_heredoc_end "${T_I}" "${T_HD_DELIMS[k]}" "${T_HD_STRIP[k]}"
    T_I=${MATCH}
    body=${HD_BODY}
    TK_STDIN[T_HD_SEG[k]]="${TK_STDIN[T_HD_SEG[k]]}${body}"
    # An unquoted heredoc runs its substitutions whatever reads it.
    if [[ ${T_HD_QUOTED[k]} == 0 ]]; then tk_heredoc_substs "${body}"; fi
  done
  T_HD_DELIMS=()
  T_HD_STRIP=()
  T_HD_QUOTED=()
  T_HD_SEG=()
}

# Parses a heredoc operator at T_I (pointing at the first <).
tk_heredoc_op() {
  local n=${#TK_S} strip=0 quoted=0 delim="" c j
  T_I=$((T_I + 2))
  if [[ ${TK_S:T_I:1} == - ]]; then
    strip=1
    T_I=$((T_I + 1))
  fi
  while [[ ${TK_S:T_I:1} == [\ $'\t'] ]]; do T_I=$((T_I + 1)); done
  while ((T_I < n)); do
    c=${TK_S:T_I:1}
    case ${c} in
      [\ $'\t'$'\n'\;\&\|\<\>\(\)]) break ;;
      \' | \")
        quoted=1
        if [[ ${c} == \' ]]; then tk_find "${R_SQ}" $((T_I + 1)); else tk_find "${R_DQQ}" $((T_I + 1)); fi
        if ((MATCH < 0)); then deny "unterminated heredoc delimiter quote; failing closed"; fi
        delim+=${TK_S:T_I+1:MATCH-T_I-1}
        T_I=$((MATCH + 1))
        ;;
      \\)
        quoted=1
        delim+=${TK_S:T_I+1:1}
        T_I=$((T_I + 2))
        ;;
      *)
        delim+=${c}
        T_I=$((T_I + 1))
        ;;
    esac
  done
  T_HD_DELIMS+=("${delim}")
  T_HD_STRIP+=("${strip}")
  T_HD_QUOTED+=("${quoted}")
  T_HD_SEG+=("${T_SEG}")
}

# Decodes an ANSI-C $'...' body (hex, octal, and the usual escapes).
tk_ansi_c() {
  local body=$1 re='\\([uU])([0-9a-fA-F]+)' hex max code rep
  body=${body//\\\'/\'}
  body=${body//\\\"/\"}
  # bash 3.2 printf has no \u: turn ASCII code points into \x escapes first.
  while [[ ${body} =~ ${re} ]]; do
    max=4
    [[ ${BASH_REMATCH[1]} == U ]] && max=8
    hex=${BASH_REMATCH[2]:0:max}
    code=$((16#${hex}))
    if ((code < 128)); then printf -v rep '\\x%02x' "${code}"; else rep='?'; fi
    body=${body/"\\${BASH_REMATCH[1]}${hex}"/${rep}}
  done
  printf -v RET '%b' "${body}"
}

tokenize_posix() {
  TK_S=$1
  local n=${#TK_S} c nx rest chunk end body
  tk_reset
  T_I=0
  while ((T_I < n)); do
    work
    c=${TK_S:T_I:1}
    case ${c} in
      ' ' | $'\t')
        tk_finish_word
        T_I=$((T_I + 1))
        ;;
      $'\n')
        tk_sep 0
        T_I=$((T_I + 1))
        if ((${#T_HD_DELIMS[@]})); then tk_read_heredocs; fi
        ;;
      \;)
        tk_sep 0
        T_I=$((T_I + 1))
        ;;
      \&)
        nx=${TK_S:T_I+1:1}
        if [[ ${nx} == \& ]]; then
          tk_sep 0
          T_I=$((T_I + 2))
        elif [[ ${nx} == \> ]]; then
          tk_finish_word
          T_REDIR=1
          T_I=$((T_I + 2))
          if [[ ${TK_S:T_I:1} == \> ]]; then T_I=$((T_I + 1)); fi
        else
          tk_sep 0
          T_I=$((T_I + 1))
        fi
        ;;
      \|)
        nx=${TK_S:T_I+1:1}
        if [[ ${nx} == \| ]]; then
          tk_sep 0
          T_I=$((T_I + 2))
        elif [[ ${nx} == \& ]]; then
          tk_sep 1
          T_I=$((T_I + 2))
        else
          tk_sep 1
          T_I=$((T_I + 1))
        fi
        ;;
      \( | \))
        tk_sep 0
        T_I=$((T_I + 1))
        ;;
      \< | \>)
        if [[ ${c} == \< && ${TK_S:T_I+1:1} == \( ]] || [[ ${c} == \> && ${TK_S:T_I+1:1} == \( ]]; then
          # process substitution: a command, kept inside the word
          tk_match_paren $((T_I + 2))
          end=${MATCH}
          if ((end < 0)); then deny "unterminated process substitution; failing closed"; fi
          body=${TK_S:T_I+2:end-T_I-2}
          TK_SUBST+=("${body}")
          T_CUR+="${c}(${body})"
          T_HAVE=1
          T_I=$((end + 1))
        elif [[ ${c} == \< && ${TK_S:T_I+1:1} == \< && ${TK_S:T_I+2:1} != \< ]]; then
          tk_finish_word
          tk_heredoc_op
        else
          if ((T_HAVE)) && [[ ${T_CUR} =~ ^[0-9]+$ ]]; then
            T_CUR=""
            T_HAVE=0
          fi
          tk_finish_word
          if [[ ${TK_S:T_I:3} == '<<<' ]]; then
            T_HERESTR=1
            T_I=$((T_I + 3))
          else
            T_REDIR=1
            T_I=$((T_I + 1))
            case ${TK_S:T_I:1} in
              \> | \& | \|) T_I=$((T_I + 1)) ;;
              *) ;;
            esac
          fi
        fi
        ;;
      \#)
        if ((T_HAVE)); then
          T_CUR+='#'
          T_I=$((T_I + 1))
        else
          tk_find "${R_NL}" "${T_I}"
          if ((MATCH < 0)); then T_I=${n}; else T_I=${MATCH}; fi
        fi
        ;;
      \')
        tk_find "${R_SQ}" $((T_I + 1))
        if ((MATCH < 0)); then deny "unterminated single quote; failing closed"; fi
        T_CUR+=${TK_S:T_I+1:MATCH-T_I-1}
        T_HAVE=1
        T_I=$((MATCH + 1))
        ;;
      \")
        tk_double_quote
        ;;
      \\)
        nx=${TK_S:T_I+1:1}
        if [[ ${nx} != $'\n' ]]; then
          T_CUR+=${nx}
          T_HAVE=1
        fi
        T_I=$((T_I + 2))
        ;;
      \$)
        tk_dollar
        ;;
      \`)
        tk_match_backtick "${T_I}"
        end=${MATCH}
        if ((end < 0)); then deny "unterminated backtick substitution; failing closed"; fi
        body=${TK_S:T_I+1:end-T_I-1}
        TK_SUBST+=("${body}")
        T_CUR+="\`${body}\`"
        T_HAVE=1
        T_I=$((end + 1))
        ;;
      *)
        rest=${TK_S:T_I:1024}
        [[ ${rest} =~ ${R_WORD} ]] || true
        chunk=${BASH_REMATCH[0]}
        if [[ -z ${chunk} ]]; then chunk=${c}; fi
        T_CUR+=${chunk}
        T_HAVE=1
        T_I=$((T_I + ${#chunk}))
        ;;
    esac
  done
  tk_finish_word
}

tk_double_quote() {
  local n=${#TK_S} c rest chunk end body
  T_HAVE=1
  T_I=$((T_I + 1))
  while :; do
    work
    if ((T_I >= n)); then deny "unterminated double quote; failing closed"; fi
    rest=${TK_S:T_I:1024}
    [[ ${rest} =~ ${R_DQCH} ]] || true
    chunk=${BASH_REMATCH[0]}
    T_CUR+=${chunk}
    T_I=$((T_I + ${#chunk}))
    if ((T_I >= n)); then deny "unterminated double quote; failing closed"; fi
    c=${TK_S:T_I:1}
    case ${c} in
      \")
        T_I=$((T_I + 1))
        return 0
        ;;
      \\)
        case ${TK_S:T_I+1:1} in
          \$ | \` | \" | \\) T_CUR+=${TK_S:T_I+1:1} ;;
          $'\n') ;;
          *) T_CUR+="\\${TK_S:T_I+1:1}" ;;
        esac
        T_I=$((T_I + 2))
        ;;
      \`)
        tk_match_backtick "${T_I}"
        end=${MATCH}
        if ((end < 0)); then deny "unterminated backtick substitution; failing closed"; fi
        body=${TK_S:T_I+1:end-T_I-1}
        TK_SUBST+=("${body}")
        T_CUR+="\`${body}\`"
        T_I=$((end + 1))
        ;;
      *)
        if [[ ${TK_S:T_I+1:1} == \( ]]; then
          tk_match_paren $((T_I + 2))
          end=${MATCH}
          if ((end < 0)); then deny "unterminated command substitution; failing closed"; fi
          body=${TK_S:T_I+2:end-T_I-2}
          TK_SUBST+=("${body}")
          T_CUR+="\$(${body})"
          T_I=$((end + 1))
        else
          T_CUR+='$'
          T_I=$((T_I + 1))
        fi
        ;;
    esac
  done
}

tk_dollar() {
  local n=${#TK_S} nx end body j
  nx=${TK_S:T_I+1:1}
  case ${nx} in
    \')
      j=$((T_I + 2))
      while ((j < n)); do
        case ${TK_S:j:1} in
          \\) j=$((j + 2)) ;;
          \') break ;;
          *) j=$((j + 1)) ;;
        esac
      done
      if ((j >= n)); then deny "unterminated \$'...' quote; failing closed"; fi
      tk_ansi_c "${TK_S:T_I+2:j-T_I-2}"
      T_CUR+=${RET}
      T_HAVE=1
      T_I=$((j + 1))
      ;;
    \")
      T_I=$((T_I + 1))
      tk_double_quote
      ;;
    \()
      tk_match_paren $((T_I + 2))
      end=${MATCH}
      if ((end < 0)); then deny "unterminated command substitution; failing closed"; fi
      body=${TK_S:T_I+2:end-T_I-2}
      TK_SUBST+=("${body}")
      T_CUR+="\$(${body})"
      T_HAVE=1
      T_I=$((end + 1))
      ;;
    \{)
      tk_find "${R_BRACE}" $((T_I + 2))
      if ((MATCH < 0)); then deny $'unterminated ${...} expansion; failing closed'; fi
      body=${TK_S:T_I+2:MATCH-T_I-2}
      T_CUR+="\${${body}}"
      T_HAVE=1
      T_I=$((T_I + ${#body} + 3))
      ;;
    *)
      T_CUR+='$'
      T_HAVE=1
      T_I=$((T_I + 1))
      ;;
  esac
}

# PowerShell grammar: '' inside single quotes, backtick escapes, @'...'@
# here-strings, <# #> comments, $( ) subexpressions. Backslash is literal.
tokenize_ps() {
  TK_S=$1
  local n=${#TK_S} c nx rest chunk end body close
  tk_reset
  T_I=0
  while ((T_I < n)); do
    work
    c=${TK_S:T_I:1}
    case ${c} in
      ' ' | $'\t' | $'\r')
        tk_finish_word
        T_I=$((T_I + 1))
        ;;
      $'\n' | \; | \{ | \} | \( | \))
        tk_sep 0
        T_I=$((T_I + 1))
        ;;
      \&)
        if [[ ${TK_S:T_I+1:1} == \& ]]; then
          tk_sep 0
          T_I=$((T_I + 2))
        else
          tk_finish_word
          T_I=$((T_I + 1))
        fi
        ;;
      \|)
        if [[ ${TK_S:T_I+1:1} == \| ]]; then
          tk_sep 0
          T_I=$((T_I + 2))
        else
          tk_sep 1
          T_I=$((T_I + 1))
        fi
        ;;
      \> | \<)
        if ((T_HAVE)) && [[ ${T_CUR} =~ ^[0-9*]+$ ]]; then
          T_CUR=""
          T_HAVE=0
        fi
        tk_finish_word
        T_REDIR=1
        T_I=$((T_I + 1))
        while [[ ${TK_S:T_I:1} == [\>\&0-9] ]]; do T_I=$((T_I + 1)); done
        ;;
      \#)
        if ((T_HAVE)); then
          T_CUR+='#'
          T_I=$((T_I + 1))
        else
          tk_find "${R_NL}" "${T_I}"
          if ((MATCH < 0)); then T_I=${n}; else T_I=${MATCH}; fi
        fi
        ;;
      \`)
        nx=${TK_S:T_I+1:1}
        if [[ ${nx} != $'\n' ]]; then
          T_CUR+=${nx}
          T_HAVE=1
        fi
        T_I=$((T_I + 2))
        ;;
      \')
        T_HAVE=1
        T_I=$((T_I + 1))
        while :; do
          work
          tk_find "${R_SQ}" "${T_I}"
          if ((MATCH < 0)); then deny "unterminated single quote; failing closed"; fi
          T_CUR+=${TK_S:T_I:MATCH-T_I}
          T_I=$((MATCH + 1))
          if [[ ${TK_S:T_I:1} == \' ]]; then
            T_CUR+=\'
            T_I=$((T_I + 1))
          else
            break
          fi
        done
        ;;
      \")
        tk_ps_double
        ;;
      @)
        nx=${TK_S:T_I+1:1}
        if [[ ${nx} == \' || ${nx} == \" ]]; then
          close=$'\n'"${nx}@"
          rest=${TK_S:T_I+2}
          if [[ ${rest} != *"${close}"* ]]; then deny "unterminated here-string; failing closed"; fi
          body=${rest%%"${close}"*}
          T_CUR+=${body#$'\n'}
          T_HAVE=1
          T_I=$((T_I + 2 + ${#body} + ${#close}))
        else
          T_CUR+=@
          T_HAVE=1
          T_I=$((T_I + 1))
        fi
        ;;
      \$)
        if [[ ${TK_S:T_I+1:1} == \( ]]; then
          tk_match_paren $((T_I + 2))
          end=${MATCH}
          if ((end < 0)); then deny "unterminated subexpression; failing closed"; fi
          body=${TK_S:T_I+2:end-T_I-2}
          TK_SUBST+=("${body}")
          T_CUR+="\$(${body})"
          T_I=$((end + 1))
        else
          T_CUR+='$'
          T_I=$((T_I + 1))
        fi
        T_HAVE=1
        ;;
      *)
        if [[ ${c} == \< && ${TK_S:T_I+1:1} == \# ]]; then
          rest=${TK_S:T_I+2}
          if [[ ${rest} != *'#>'* ]]; then deny "unterminated block comment; failing closed"; fi
          chunk=${rest%%'#>'*}
          T_I=$((T_I + 2 + ${#chunk} + 2))
          continue
        fi
        rest=${TK_S:T_I:1024}
        [[ ${rest} =~ ${R_WORD_PS} ]] || true
        chunk=${BASH_REMATCH[0]}
        if [[ -z ${chunk} ]]; then chunk=${c}; fi
        T_CUR+=${chunk}
        T_HAVE=1
        T_I=$((T_I + ${#chunk}))
        ;;
    esac
  done
  tk_finish_word
}

tk_ps_double() {
  local n=${#TK_S} c rest chunk end body
  T_HAVE=1
  T_I=$((T_I + 1))
  while :; do
    work
    rest=${TK_S:T_I:1024}
    [[ ${rest} =~ ${R_DQ_PS} ]] || true
    chunk=${BASH_REMATCH[0]}
    T_CUR+=${chunk}
    T_I=$((T_I + ${#chunk}))
    if ((T_I >= n)); then deny "unterminated double quote; failing closed"; fi
    c=${TK_S:T_I:1}
    case ${c} in
      \")
        if [[ ${TK_S:T_I+1:1} == \" ]]; then
          T_CUR+=\"
          T_I=$((T_I + 2))
        else
          T_I=$((T_I + 1))
          return 0
        fi
        ;;
      \`)
        T_CUR+=${TK_S:T_I+1:1}
        T_I=$((T_I + 2))
        ;;
      *)
        if [[ ${TK_S:T_I+1:1} == \( ]]; then
          tk_match_paren $((T_I + 2))
          end=${MATCH}
          if ((end < 0)); then deny "unterminated subexpression; failing closed"; fi
          body=${TK_S:T_I+2:end-T_I-2}
          TK_SUBST+=("${body}")
          T_CUR+="\$(${body})"
          T_I=$((end + 1))
        else
          T_CUR+='$'
          T_I=$((T_I + 1))
        fi
        ;;
    esac
  done
}

# --- policy -------------------------------------------------------------------

# $1 "key[=value]"; $2 origin label for the reason; $3 oneshot | persist
check_config_kv() {
  local kv=$1 origin=$2 kind=${3:-oneshot} key val="" has=0
  lower "${kv%%=*}"
  key=${LOWER}
  if [[ ${kv} == *=* ]]; then
    val=${kv#*=}
    has=1
  fi
  case ${key} in
    commit.gpgsign | tag.gpgsign | tag.forcesignannotated)
      if ((has)) && ! is_true "${val}"; then deny "${origin} sets ${key} to a value that is not true, which disables signing"; fi
      ;;
    core.hookspath)
      if [[ ${kind} == persist ]] && ((has)) && is_repo_hooks_path "${val}"; then return 0; fi
      deny "${origin} points core.hooksPath away from the repository's hooks"
      ;;
    gpg.program | gpg.*.program) deny "${origin} overrides ${key}, which can fake or skip signing" ;;
    include.path | includeif.*)
      if [[ ${kind} != persist ]]; then deny "${origin} injects config through ${key}, which can disable hooks or signing"; fi
      ;;
    core.editor | sequence.editor | core.pager | pager.* | core.sshcommand | diff.external | core.fsmonitor | \
      credential.helper | credential.*.helper | filter.*.clean | filter.*.smudge | filter.*.process | \
      merge.*.driver | diff.*.command | diff.*.textconv)
      # These keys run a command; inspect it like any other nested command.
      if ((has)) && [[ -n ${val} ]]; then analyze_nested "${val#!}" posix "the ${key} command"; fi
      ;;
    alias.*)
      if ((has)); then
        if [[ ${val} == '!'* ]]; then
          analyze_nested "${val#!}" posix "the ${key} alias"
        else
          analyze_nested "git ${val}" posix "the ${key} alias"
        fi
      fi
      ;;
    *) ;;
  esac
}

# $@: NAME=VALUE entries in effect for a git invocation
check_env() {
  # Names compare case-insensitively: Windows environments ignore case, and a
  # stricter match only costs false positives on unusual lowercase names.
  local e orig name val lval k idx vkv
  for e in "$@"; do
    orig=${e%%=*}
    lower "${orig}"
    name=${LOWER}
    val=${e#*=}
    lower "${val}"
    lval=${LOWER}
    case ${name} in
      husky) if [[ ${val} == 0 ]]; then deny "${orig}=0 disables husky hooks"; fi ;;
      husky_skip_hooks | skip | pre_commit_allow_no_config | lefthook_exclude | skip_simple_git_hooks | overcommit_disable)
        if [[ -n ${val} ]]; then deny "${orig}=${val} skips hooks"; fi
        ;;
      lefthook) if [[ ${val} == 0 || ${lval} == false ]]; then deny "${orig}=${val} disables lefthook"; fi ;;
      git_config_parameters) deny "${orig} injects config that can disable hooks or signing" ;;
      git_editor | git_sequence_editor | editor | visual | git_pager | pager | git_ssh_command | git_external_diff)
        # Git runs these as commands; inspect them like any other nested command.
        if [[ -n ${val} ]]; then analyze_nested "${val}" posix "${orig}"; fi
        ;;
      git_config_global | git_config_system | git_config_nosystem | home | xdg_config_home)
        deny "${orig} redirects the Git configuration, which can drop signing or hooks settings"
        ;;
      git_config_key_*)
        idx=${name#git_config_key_}
        if is_protected_key "${lval}" || [[ ${lval} == alias.* ]]; then
          vkv="${val}="
          for k in "$@"; do
            lower "${k%%=*}"
            if [[ ${LOWER} == "git_config_value_${idx}" ]]; then vkv="${val}=${k#*=}"; fi
          done
          check_config_kv "${vkv}" "${orig}"
        fi
        ;;
      *) ;;
    esac
  done
}

# Git options that take a separate value, per subcommand (exact spellings).
takes_value() { # $1 sub, $2 option
  case "$1:$2" in
    commit:-m | commit:-F | commit:-C | commit:-c | commit:-t | commit:--message | commit:--file | \
      commit:--reuse-message | commit:--reedit-message | commit:--fixup | commit:--squash | \
      commit:--author | commit:--date | commit:--template | commit:--trailer | commit:--cleanup | \
      commit:--pathspec-from-file) return 0 ;;
    merge:-m | merge:-F | merge:-s | merge:-X | merge:--message | merge:--file | merge:--strategy | \
      merge:--strategy-option | merge:--into-name | merge:--cleanup) return 0 ;;
    pull:-s | pull:-X | pull:-o | pull:-j | pull:--strategy | pull:--strategy-option | \
      pull:--server-option | pull:--jobs | pull:--depth | pull:--deepen | pull:--shallow-since | \
      pull:--shallow-exclude | pull:--upload-pack | pull:--negotiation-tip) return 0 ;;
    tag:-m | tag:-F | tag:-u | tag:--message | tag:--file | tag:--local-user | tag:--contains | \
      tag:--no-contains | tag:--points-at | tag:--merged | tag:--no-merged | tag:--sort | \
      tag:--format | tag:--cleanup) return 0 ;;
    rebase:-s | rebase:-X | rebase:--strategy | rebase:--strategy-option | rebase:--onto) return 0 ;;
    push:-o | push:--push-option | push:--repo | push:--receive-pack | push:--exec) return 0 ;;
    am:--patch-format | am:--exclude | am:--include | am:--directory | am:--whitespace | \
      am:--resolvemsg | am:--empty) return 0 ;;
    cherry-pick:-m | cherry-pick:-s | cherry-pick:-X | cherry-pick:--mainline | cherry-pick:--strategy | \
      cherry-pick:--strategy-option | cherry-pick:--cleanup) return 0 ;;
    revert:-m | revert:-s | revert:-X | revert:--mainline | revert:--strategy | \
      revert:--strategy-option | revert:--cleanup) return 0 ;;
    *) return 1 ;;
  esac
}

# Walks a short-option cluster such as -anm. Echoes "value" when the last
# value-taking letter needs the next word as its value.
short_cluster() { # $1 sub, $2 cluster without the leading dash
  local sub=$1 cl=$2 i ch rest
  RET=""
  for ((i = 0; i < ${#cl}; i++)); do
    ch=${cl:i:1}
    rest=${cl:i+1}
    if [[ ${ch} == n && (${sub} == commit || ${sub} == am) ]]; then
      deny "git ${sub} -n is --no-verify, which skips hooks"
    fi
    if [[ ${sub} == rebase && ${ch} == x ]]; then
      if [[ -n ${rest} ]]; then
        analyze_nested "${rest}" posix "git rebase --exec"
        return 0
      fi
      RET=want_exec
      return 0
    fi
    if takes_value "${sub}" "-${ch}"; then
      if [[ -z ${rest} ]]; then RET=want_value; fi
      return 0
    fi
    case "${sub}:${ch}" in
      commit:u | commit:S | am:S | am:C | am:p | merge:S | pull:S | rebase:S | rebase:C | \
        cherry-pick:S | revert:S) return 0 ;;
      *) ;;
    esac
  done
  return 0
}

analyze_git_sub() { # $1 sub, rest: its arguments
  local sub=$1 a name r chk i=0
  shift
  local -a args=("$@")
  local n=${#args[@]}
  while ((i < n)); do
    a=${args[i]}
    i=$((i + 1))
    # An argument built by an expansion ($(...), `...`, $VAR) can produce a
    # bypass flag at run time: check it with the values set elsewhere in the level.
    # Attached option values (-m"$(...)", --message=$(...)) are messages, not flags.
    case ${a} in
      --*) chk=${a%%=*} ;;
      -*) chk="" ;;
      *) chk=${a} ;;
    esac
    if [[ ${chk} == *\$* || ${chk} == *\`* ]] && has_marker "${chk} ${NONGIT_TEXT}"; then
      deny "git ${sub} receives an argument built from an expansion that can carry a bypass; pass literal arguments"
    fi
    case ${a} in
      --) break ;;
      --*)
        name=${a%%=*}
        # Brace expansion (--no-{verify,}) produces the flag in the shell.
        [[ ${name} == *\{* ]] && name=${name//[\{\},]/}
        if abbrev_of "${name}" --no-verify 6; then deny "git ${sub} ${name} skips hooks (--no-verify)"; fi
        if abbrev_of "${name}" --no-gpg-sign 6; then deny "git ${sub} ${name} skips signing (--no-gpg-sign)"; fi
        if [[ ${sub} == tag ]] && abbrev_of "${name}" --no-sign 6; then deny "git tag ${name} skips tag signing (--no-sign)"; fi
        if [[ ${sub} == rebase ]] && abbrev_of "${name}" --exec 5; then
          if [[ ${a} == *=* ]]; then
            analyze_nested "${a#*=}" posix "git rebase --exec"
          elif ((i < n)); then
            analyze_nested "${args[i]}" posix "git rebase --exec"
            i=$((i + 1))
          fi
          continue
        fi
        if [[ ${a} != *=* ]] && takes_value "${sub}" "${name}"; then i=$((i + 1)); fi
        ;;
      -?*)
        short_cluster "${sub}" "${a#-}"
        r=${RET}
        if [[ ${r} == want_value ]]; then
          i=$((i + 1))
        elif [[ ${r} == want_exec ]] && ((i < n)); then
          analyze_nested "${args[i]}" posix "git rebase -x"
          i=$((i + 1))
        fi
        ;;
      *) ;;
    esac
  done
}

analyze_git_config() {
  local a mode="" sub
  local -a pos=()
  while (($#)); do
    a=$1
    shift
    case ${a} in
      -f | --file | --blob | --type | --default | --comment | --value) shift ;;
      --unset | --unset-all) mode=m_unset ;;
      --rename-section | --remove-section) mode=m_section ;;
      --add | --replace-all) mode=m_set ;;
      --get | --get-all | --get-regexp | --get-urlmatch | --get-color | --get-colorbool | -l | --list | -e | --edit) mode=m_read ;;
      -*) ;;
      *) pos+=("${a}") ;;
    esac
  done
  if [[ -z ${mode} && ${#pos[@]} -gt 0 ]]; then
    sub=${pos[0]}
    case ${sub} in
      set | unset | rename-section | remove-section | list | get | edit)
        pos=("${pos[@]:1}")
        case ${sub} in
          set) mode=m_set ;;
          unset) mode=m_unset ;;
          *-section) mode=m_section ;;
          *) mode=m_read ;;
        esac
        ;;
      *) ;;
    esac
  fi
  if [[ -z ${mode} ]]; then
    if ((${#pos[@]} >= 2)); then mode=m_set; else mode=m_read; fi
  fi
  case ${mode} in
    m_set) if ((${#pos[@]} >= 2)); then check_config_kv "${pos[0]}=${pos[1]}" "git config" persist; fi ;;
    m_unset)
      if ((${#pos[@]})) && is_protected_key "${pos[0]}"; then deny "git config unsets ${pos[0]}, which can disable hooks or signing"; fi
      ;;
    m_section)
      if ((${#pos[@]})); then
        lower "${pos[0]}"
        case ${LOWER} in
          core | commit | tag | gpg | gpg.* | include | includeif*) deny "git config rewrites the [${pos[0]}] section, which holds hooks and signing settings" ;;
          *) ;;
        esac
      fi
      ;;
    *) ;;
  esac
}

# Built-in subcommands, so anything else can be looked up as an alias.
known_sub() {
  case $1 in
    add | am | annotate | apply | archive | bisect | blame | branch | bundle | cat-file | check-attr | \
      check-ignore | checkout | cherry | cherry-pick | clean | clone | commit | commit-tree | config | \
      count-objects | credential | describe | diff | diff-files | diff-index | diff-tree | difftool | \
      fetch | for-each-ref | format-patch | fsck | gc | grep | hash-object | help | hook | init | log | \
      ls-files | ls-remote | ls-tree | maintenance | merge | merge-base | mergetool | mv | notes | pull | \
      push | range-diff | rebase | reflog | remote | repack | replace | reset | restore | rev-list | \
      rev-parse | revert | rm | shortlog | show | show-ref | sparse-checkout | stash | status | submodule | \
      switch | symbolic-ref | tag | update-index | update-ref | var | version | whatchanged | worktree | \
      write-tree) return 0 ;;
    *) return 1 ;;
  esac
}

# Subcommands that run verification hooks or create signed objects.
hook_sub() {
  case $1 in
    commit | merge | pull | rebase | am | cherry-pick | revert | tag | push | commit-tree) return 0 ;;
    *) return 1 ;;
  esac
}

# Expands a Git alias from the repository's configuration (read-only) and
# analyzes the expansion with the remaining arguments. Returns 1 if no alias.
resolve_alias() { # $1 name, rest: arguments
  local name=$1 expansion
  shift
  [[ ${name} =~ ^[a-z0-9][a-z0-9_.-]*$ ]] || return 1
  command -v git > /dev/null 2>&1 || return 1
  expansion=$(git -C "${PAYLOAD_CWD:-.}" config --get "alias.${name}" 2> /dev/null) || return 1
  [[ -n ${expansion} ]] || return 1
  if [[ ${expansion} == '!'* ]]; then
    analyze_nested "${expansion#!} $*" posix "the git ${name} alias"
  else
    analyze_nested "git ${expansion} $*" posix "the git ${name} alias"
  fi
  return 0
}

# $1 index of the git word in SEG, $2 its base name; GIT_ENV holds the
# environment assignments in effect for this invocation.
analyze_git() {
  local base=$2 a sub=""
  local -a genv=("${GIT_ENV[@]}")
  local -a args=("${SEG[@]:$1+1}")
  local n=${#args[@]} i=0
  if [[ ${base} == git-* ]]; then
    sub=${base#git-}
  else
    while ((i < n)); do
      a=${args[i]}
      case ${a} in
        -C | --git-dir | --work-tree | --namespace | --attr-source | --super-prefix) i=$((i + 2)) ;;
        -c | --config)
          check_config_kv "${args[i + 1]}" "git ${a}"
          i=$((i + 2))
          ;;
        --config=*)
          check_config_kv "${a#--config=}" "git --config"
          i=$((i + 1))
          ;;
        --config-env | --config-env=*)
          if [[ ${a} == *=* ]]; then a=${a#*=}; else a=${args[i + 1]}; fi
          lower "${a%%=*}"
          a=${LOWER}
          if is_protected_key "${a}" || [[ ${a} == alias.* ]]; then deny "git --config-env sets ${a} from the environment, which can disable hooks or signing"; fi
          if [[ ${args[i]} == *=* ]]; then i=$((i + 1)); else i=$((i + 2)); fi
          ;;
        -c?*)
          check_config_kv "${a#-c}" "git -c"
          i=$((i + 1))
          ;;
        -*) i=$((i + 1)) ;;
        *)
          sub=${a}
          i=$((i + 1))
          break
          ;;
      esac
    done
  fi
  [[ -n ${sub} ]] || return 0
  lower "${sub}"
  sub=${LOWER}
  # Environment bypasses matter only where hooks or signing run; unknown
  # subcommands may be aliases, so they are checked too.
  if ! known_sub "${sub}" || hook_sub "${sub}"; then check_env "${genv[@]}"; fi
  if ! known_sub "${sub}"; then
    resolve_alias "${sub}" "${args[@]:i}" && return 0
  fi
  case ${sub} in
    commit-tree) deny "git commit-tree creates commits without running hooks or honoring commit.gpgsign; use git commit" ;;
    config) analyze_git_config "${args[@]:i}" ;;
    submodule | bisect)
      if [[ ${args[i]} == foreach || ${args[i]} == run ]]; then
        analyze_nested "${args[*]:i+1}" posix "git ${sub} ${args[i]}"
      fi
      ;;
    *) analyze_git_sub "${sub}" "${args[@]:i}" ;;
  esac
}

is_assignment() { [[ $1 =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; }

ps_env_assignment() { # prints NAME=VALUE for $env:NAME=VALUE words
  local w=$1 rest
  lower "${w:0:5}"
  [[ ${LOWER} == $'$env:' ]] || return 1
  rest=${w:5}
  [[ ${rest} =~ ^[A-Za-z_][A-Za-z0-9_]* ]] || return 1
  RET=${rest}
}

# Collects NAME=VALUE entries that persist for the rest of the level:
# export/declare -x/typeset -x, bare assignment statements, $env: in PowerShell.
collect_level_env() {
  local k w0 w nx e
  LEVEL_ENV=()
  for ((k = 0; k < ${#TK_WORDS[@]}; k++)); do
    [[ ${TK_KINDS[k]} == w ]] || continue
    w=${TK_WORDS[k]}
    if [[ ${MODE} == psh ]]; then
      if ps_env_assignment "${w}"; then
        e=${RET}
        if [[ ${e} != *=* ]]; then
          nx=${TK_WORDS[k + 1]}
          if [[ ${nx} == = ]]; then
            e="${e}=${TK_WORDS[k + 2]}"
          elif [[ ${nx} == =* ]]; then
            e="${e}${nx}"
          else
            continue
          fi
        fi
        LEVEL_ENV+=("${e}")
      fi
      continue
    fi
    if ((k == 0)) || [[ ${TK_KINDS[k - 1]} == s ]]; then
      w0=${w}
    fi
    case ${w0} in
      export | declare | typeset | readonly | local)
        if is_assignment "${w}"; then LEVEL_ENV+=("${w}"); fi
        ;;
      *)
        if is_assignment "${w}" && is_assignment "${w0}"; then LEVEL_ENV+=("${w}"); fi
        ;;
    esac
  done
}

# Hook files and configs that bypasses tamper with.
is_hook_path() {
  lower "$1"
  case ${LOWER} in
    *.git/hooks | *.git/hooks/* | .git/hooks* | *.husky | *.husky/* | .husky* | *lefthook*.yml | *lefthook*.yaml | \
      *lefthook*.json | *lefthook*.toml | *.pre-commit-config.yaml | *.pre-commit-config.yml | *.overcommit.yml) return 0 ;;
    *) return 1 ;;
  esac
}

# rm/unlink/truncate/shred of hook files, mv of them away, chmod removing
# their exec bit. Creating or installing hooks stays allowed.
guard_hook_files() { # $1 index of the command word in SEG, $2 its base name
  local base=$2 k w mode="" last=""
  local -a paths=()
  for ((k = $1 + 1; k < ${#SEG[@]}; k++)); do
    w=${SEG[k]}
    if [[ ${w} == --* ]] || [[ ${w} == -* && ${base} != chmod ]] || [[ ${base} == chmod && ${w} =~ ^-[RfvcHLP]+$ ]]; then continue; fi
    if [[ ${base} == chmod && -z ${mode} && ${w} != --* ]]; then
      mode=${w}
      continue
    fi
    paths+=("${w}")
  done
  ((${#paths[@]})) || return 0
  last=${paths[${#paths[@]} - 1]}
  for w in "${paths[@]}"; do
    is_hook_path "${w}" || continue
    case ${base} in
      mv) [[ ${w} == "${last}" ]] && continue ;;
      chmod) is_removing_exec "${mode}" || continue ;;
      *) ;;
    esac
    deny "${base} on ${w} disables the repository's hooks; ask the user to change hooks"
  done
}

is_removing_exec() { # chmod mode that clears the owner exec bit
  local m=$1
  case ${m} in
    *-*x* | *=*) [[ ${m} != *=*x* ]] && return 0 ;;
    *) ;;
  esac
  if [[ ${m} =~ ^0?[0-7]?([0-7])[0-7][0-7]$ ]]; then
    ((BASH_REMATCH[1] % 2 == 0)) && return 0
  fi
  return 1
}

analyze_segment() { # SEG words, $1 segment index
  local si=$1 p m=${#SEG[@]} w base j script found prev_base="" seen_xargs=0
  local -a lead=()
  for ((p = 0; p < m; p++)); do
    w=${SEG[p]}
    base_name "${w}"
    base=${BASE}
    # A command name from a variable, or a word that splices "git" together
    # with expansions (git${IFS}commit), cannot be resolved without running it.
    if [[ ${w} == *\$* || ${w} == *\`* ]]; then
      if ((p == 0)) && [[ ${MODE} == psh && (${w} == *=* || ${SEG[1]} == =*) ]]; then
        : # PowerShell assignment ($x = ...), not a command
      elif ((p == 0)) || [[ ${w} != *\$\(* && ${w} != *\`* && ${w} == *[gG][iI][tT]* ]]; then
        check_opaque "${w} ${NONGIT_TEXT}" "a command built from variables or substitutions"
      fi
    fi
    # Assignments and xargs seen before this word, tracked incrementally.
    if ((p > 0)); then
      if is_assignment "${SEG[p - 1]}"; then lead+=("${SEG[p - 1]}"); fi
      if [[ ${prev_base} == xargs ]]; then seen_xargs=1; fi
    fi
    prev_base=${base}
    case ${base} in
      git | git-*)
        if [[ ${base} == git-* && ! ${base} =~ ^git-[a-z-]+$ ]]; then continue; fi
        GIT_ENV=("${INHERITED_ENV[@]}" "${LEVEL_ENV[@]}" "${lead[@]}")
        if ((seen_xargs)) && has_marker "${NONGIT_TEXT}"; then
          deny "git run through xargs takes arguments from a pipe that can carry a bypass; pass literal arguments"
        fi
        analyze_git "${p}" "${base}"
        ;;
      bash | sh | zsh | dash | ksh | mksh | ash | fish)
        script=""
        found=0
        for ((j = p + 1; j < m; j++)); do
          w=${SEG[j]}
          if ((found)); then
            script=${w}
            break
          fi
          case ${w} in
            -o | -O | +o | +O) j=$((j + 1)) ;;
            --*) ;;
            -*c*) found=1 ;;
            -* | +*) ;;
            *) break ;;
          esac
        done
        if ((found)); then
          CHILD_ENV=("${lead[@]}")
          analyze_nested "${script}" posix "${base} -c"
        elif ((j >= m)); then
          if [[ -n ${TK_STDIN[si]} ]]; then
            CHILD_ENV=("${lead[@]}")
            analyze_nested "${TK_STDIN[si]}" posix "${base} reading a heredoc"
          elif [[ ${TK_PIPED[si]} == 1 ]]; then
            check_opaque "${LEVEL_TEXT}" "a shell reading commands from a pipe"
          fi
        fi
        ;;
      pwsh | powershell)
        for ((j = p + 1; j < m; j++)); do
          lower "${SEG[j]}"
          case ${LOWER} in
            -c | -co | -com | -comm | -comma | -comman | -command | /c | /command)
              CHILD_ENV=("${lead[@]}")
              analyze_nested "${SEG[*]:j+1}" psh "${base} -Command"
              break
              ;;
            *) ;;
          esac
        done
        ;;
      eval)
        CHILD_ENV=("${lead[@]}")
        analyze_nested "${SEG[*]:p+1}" posix "eval"
        ;;
      iex | invoke-expression)
        analyze_nested "${SEG[*]:p+1}" psh "Invoke-Expression"
        ;;
      env)
        for ((j = p + 1; j < m; j++)); do
          case ${SEG[j]} in
            -S | --split-string)
              CHILD_ENV=("${lead[@]}")
              analyze_nested "${SEG[*]:j+1}" posix "env -S"
              break
              ;;
            -S?* | --split-string=*)
              w=${SEG[j]}
              w=${w#--split-string=}
              w=${w#-S}
              CHILD_ENV=("${lead[@]}")
              analyze_nested "${w} ${SEG[*]:j+1}" posix "env -S"
              break
              ;;
            *) ;;
          esac
        done
        ;;
      watch)
        j=$((p + 1))
        while ((j < m)) && [[ ${SEG[j]} == -* ]]; do
          case ${SEG[j]} in
            -n | --interval | -q | --equexit) j=$((j + 2)) ;;
            *) j=$((j + 1)) ;;
          esac
        done
        analyze_nested "${SEG[*]:j}" posix "watch"
        ;;
      rm | unlink | truncate | shred | mv | chmod) guard_hook_files "${p}" "${base}" ;;
      pre-commit | lefthook | husky | overcommit)
        for ((j = p + 1; j < m; j++)); do
          case ${SEG[j]} in
            uninstall | --uninstall) deny "${base} ${SEG[j]} removes the repository's hooks; ask the user to do it" ;;
            *) ;;
          esac
        done
        ;;
      su | runuser | flock | script)
        for ((j = p + 1; j < m; j++)); do
          case ${SEG[j]} in
            -c | --command)
              analyze_nested "${SEG[j + 1]}" posix "${base} -c"
              break
              ;;
            --command=*)
              w=${SEG[j]}
              analyze_nested "${w#--command=}" posix "${base} -c"
              break
              ;;
            *) ;;
          esac
        done
        ;;
      *) ;;
    esac
  done
}

# Analyzes one level of command text. Recursion depth is bounded.
analyze_text() { # $1 text, $2 mode
  local text=$1 k si isgit segtext=""
  local MODE=$2 LEVEL_TEXT=$1 NONGIT_TEXT=""
  local -a words kinds stdin subst piped SEG LEVEL_ENV CHILD_ENV
  if [[ ${MODE} == psh ]]; then tokenize_ps "${text}"; else tokenize_posix "${text}"; fi
  words=("${TK_WORDS[@]}")
  kinds=("${TK_KINDS[@]}")
  stdin=("${TK_STDIN[@]}")
  subst=("${TK_SUBST[@]}")
  piped=("${TK_PIPED[@]}")
  # Segments that invoke no git: where flags hidden in variables get their values.
  isgit=0
  for ((k = 0; k <= ${#words[@]}; k++)); do
    if ((k == ${#words[@]})) || [[ ${kinds[k]} == s ]]; then
      ((isgit)) || NONGIT_TEXT+="${segtext} ; "
      isgit=0
      segtext=""
    else
      base_name "${words[k]}"
      [[ ${BASE} == git || ${BASE} == git-* ]] && isgit=1
      segtext+="${words[k]} "
    fi
  done
  collect_level_env
  SEG=()
  si=0
  for ((k = 0; k <= ${#words[@]}; k++)); do
    if ((k == ${#words[@]})) || [[ ${kinds[k]} == s ]]; then
      if ((${#SEG[@]})); then
        TK_STDIN=("${stdin[@]}")
        TK_PIPED=("${piped[@]}")
        analyze_segment "${si}"
      fi
      SEG=()
      si=$((si + 1))
    else
      SEG+=("${words[k]}")
    fi
  done
  for k in "${!subst[@]}"; do
    analyze_nested "${subst[k]}" "${MODE}" "a command substitution"
  done
}

analyze_nested() { # $1 text, $2 mode, $3 label
  local -a INHERITED_ENV=("${INHERITED_ENV[@]}" "${LEVEL_ENV[@]}" "${CHILD_ENV[@]}")
  local CUR_DEPTH=$((CUR_DEPTH + 1))
  CHILD_ENV=()
  if ((CUR_DEPTH > MAX_DEPTH)); then
    check_opaque "$1" "$3 nested too deeply to parse"
    return 0
  fi
  analyze_text "$1" "$2"
}

# Without jq the payload can't be parsed properly. Look only at the shell
# tool's command string (never cwd or transcript paths, which often contain
# "git") and deny if it could involve git; everything else passes.
no_jq_decision() {
  local p=$1 cmd
  local re_tool='"tool_name"[[:space:]]*:[[:space:]]*"(Bash|PowerShell)"'
  local re_cmd='"command"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)"'
  [[ ${p} =~ ${re_tool} ]] || exit 0
  [[ ${p} =~ ${re_cmd} ]] || exit 0
  cmd=${BASH_REMATCH[1]}
  lower "${cmd}"
  if [[ ${LOWER} == *git* || ${LOWER} == *\\u* ]]; then
    deny "jq is not installed, so this git command cannot be checked; install jq (the policy requires it)"
  fi
  exit 0
}

main() {
  local payload="" parsed tag tool cmd stripped
  IFS= read -r -d '' payload || true
  if ! command -v jq > /dev/null 2>&1; then no_jq_decision "${payload}"; fi
  if ! parsed=$(printf '%s' "${payload}" | jq -r '
      if type != "object" then "!"
      elif ((.tool_input | type) == "object") and ((.tool_input.command | type) == "string") then
        if (.tool_input.command | explode | any(. == 0)) then "!"
        else "S" + ((.tool_name // "") | tostring) + "\n" + ((.cwd // "") | tostring | gsub("\n"; "")) + "\n" + .tool_input.command end
      else "N" end' 2> /dev/null); then
    deny "the hook payload is not valid JSON; failing closed"
  fi
  tag=${parsed:0:1}
  case ${tag} in
    N) exit 0 ;;
    S) ;;
    *) deny "the hook payload is malformed; failing closed" ;;
  esac
  parsed=${parsed:1}
  # A native jq.exe on Windows prints CRLF for every LF, and jq 1.6 has no --binary to stop it.
  # The tool name never ends in a CR, so one that does marks the conversion: undo it exactly.
  if [[ ${parsed%%$'\n'*} == *$'\r' ]]; then parsed=${parsed//$'\r\n'/$'\n'}; fi
  tool=${parsed%%$'\n'*}
  parsed=${parsed#*$'\n'}
  PAYLOAD_CWD=${parsed%%$'\n'*}
  cmd=${parsed#*$'\n'}
  case ${tool} in
    Bash) MODE=posix ;;
    PowerShell) MODE=psh ;;
    *) exit 0 ;;
  esac
  # Fast path: nothing Git- or hook-related even after removing quoting
  # characters, and no $'...' escapes that could spell it.
  # bash 3.2's ${var//pattern/} is quadratic, so long commands go through tr.
  if ((${#cmd} > 512)); then
    stripped=$(printf '%s' "${cmd}" | tr -d "\\\\'\"\`")
  else
    stripped=${cmd//[\\\'\"\`]/}
  fi
  lower "${stripped}"
  stripped=${LOWER}
  if [[ ${cmd} != *"\$'"* ]]; then
    case ${stripped} in
      *git* | *husky* | *lefthook* | *pre-commit* | *overcommit*) ;;
      *) exit 0 ;;
    esac
  fi
  CMD_TEXT=${cmd}
  INHERITED_ENV=()
  LEVEL_ENV=()
  CHILD_ENV=()
  analyze_text "${cmd}" "${MODE}"
  # return, not exit: the script then ends with status 0 all the same, and
  # ShellCheck can see that on_internal_error is reached through the ERR trap.
  return 0
}

main
