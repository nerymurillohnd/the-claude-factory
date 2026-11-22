#!/usr/bin/env bash
# Post-edit hook of bash-lsp-intelligence: shfmt -w, then shellcheck, on the shell scripts a
# tool call changed. Reads one PostToolUse or PostToolUseFailure event on stdin. The tools run
# the way they run from a terminal and read the user's .editorconfig, .shellcheckrc and
# SHELLCHECK_OPTS; the plugin's defaults (shfmt -i 2 -ci -bn, shellcheck -o all -S style -x -a
# -P SCRIPTDIR) apply only when none of those exists.
#
# The user always gets one systemMessage line saying which tools ran on which files, whether
# shfmt reformatted any and whether they found errors, or why they did not run. Claude gets a
# message only when the tools found errors or failed on a file: the findings on stderr with
# exit 2, and the instruction to audit and fix them with the plugin's skill before continuing.
# Files of other languages are ignored in silence.
#
# The hook judges only what the tool call changed and never blocks because it cannot check:
# - A tool that is not installed is reported to the user on every call, with the install
#   command for this system's package manager, and exit 0.
# - Files that a Bash command left under a nested Git work tree count only when Git lists them
#   as modified, untracked or staged there, so a clone, a checkout or a pull is never checked.
# - More than MAX_FILES files found by modification time alone, outside Git, are an arrival
#   (an extracted archive, a generated tree), not an edit: none is checked, and the user is told.
#
# Needs Bash 3.2 or later and POSIX awk, env, find, head, date, touch, mktemp, rm and cksum;
# uses git when it is installed. The event is read with read-event.awk and the user's line is encoded
# with json-string.awk, both next to this script. Every helper reports through a variable and
# returns 0, so set -e stays in force inside it; any unexpected failure exits 1 with a message.

set -Eeuo pipefail

readonly PLUGIN='bash-lsp-intelligence'
TMP=''
# set -E hands this trap to every command substitution too, and Bash 3.2 runs it there for a
# failure its caller handles, such as `x=$(command -v shfmt) || missing=shfmt`. Inside a
# subshell it only exits 1 and leaves the caller to decide; only the hook itself reports.
trap '((BASH_SUBSHELL == 0)) || exit 1; printf "%s: the post-edit hook failed at line %s, so the changed shell scripts were not checked.\n" "${PLUGIN}" "${LINENO}" >&2; exit 1' ERR
trap '[[ -z ${TMP} ]] || rm -rf -- "${TMP}"' EXIT

HERE=${BASH_SOURCE[0]%/*}
if [[ ${HERE} == "${BASH_SOURCE[0]}" ]]; then
  HERE=.
fi
readonly HERE
readonly CLAUDE_INSTRUCTION="Use the Skill tool to load \"${PLUGIN}:${PLUGIN}\", audit these errors with it and fix them before continuing with anything else."
# A Bash command that rewrites more files than this gets the rest reported, not checked.
readonly MAX_FILES=20
# The modification-time walk gives up after this many files, so a huge tree stays cheap.
readonly MAX_WALK_FILES=20000
# Claude Code saves hook output over 10,000 characters to a file and passes Claude only its
# path and a 2,000-character preview, so the findings must fit under the cap.
readonly MAX_REPORT_CHARS=9000
# Clock slack added to duration_ms when looking for files a Bash command changed.
readonly BASH_SLACK_MS=2000
# Window used when the event carries no duration_ms.
readonly FALLBACK_WINDOW_MS=30000
readonly NL=$'\n'

# Sets PHYSICAL to the canonical path of the existing file or folder $1, symlinks resolved, or
# to '' when it does not exist or can't be resolved.
physical() {
  local path=$1 link dir hops=0
  PHYSICAL=''
  while [[ -L ${path} ]]; do
    hops=$((hops + 1))
    if ((hops > 40)) || ! link=$(readlink -- "${path}"); then
      return 0
    fi
    if [[ ${link} == /* || ${path} != */* ]]; then
      path=${link}
    else
      path=${path%/*}/${link}
    fi
  done
  if [[ -d ${path} ]]; then
    if dir=$(cd -P -- "${path}" && pwd -P); then
      PHYSICAL=${dir}
    fi
    return 0
  fi
  if [[ ! -e ${path} ]]; then
    return 0
  fi
  dir=.
  if [[ ${path} == */* ]]; then
    dir=${path%/*}
    dir=${dir:-/}
  fi
  if ! dir=$(cd -P -- "${dir}" && pwd -P); then
    return 0
  fi
  PHYSICAL=${dir%/}/${path##*/}
}

# Sets LISTED to 1 when the newline-separated list $1 holds the line $2, else to 0.
listed() {
  case "${NL}$1" in
    *"${NL}$2${NL}"*) LISTED=1 ;;
    *) LISTED=0 ;;
  esac
}

# Sets NAMES to the paths given as a comma-separated list, each relative to BASE when it lies
# under it.
names_of() {
  local path name
  NAMES=''
  for path in "$@"; do
    name=${path}
    if [[ -n ${BASE} && ${path} == "${BASE}"/* ]]; then
      name=${path#"${BASE}"/}
    fi
    NAMES+="${NAMES:+, }${name}"
  done
}

# Sets DIALECT to sh, bash or zsh by suffix or shebang, or to '' for a file of another language.
dialect() {
  local path=$1 name=${1##*/} suffix='' line='' shell=''
  local shebang='^#!([^[:space:]]*/)?(env[[:space:]]+(-S[[:space:]]+)?)?(sh|bash|zsh)([[:space:]]|$)'
  if [[ ${name} == ?*.* ]]; then
    suffix=.${name##*.}
  fi
  DIALECT=''
  if [[ ${suffix} == .zsh ]]; then
    DIALECT=zsh
    return 0
  fi
  if [[ -r ${path} ]]; then
    IFS= read -r -n 256 line < "${path}" || :
  fi
  if [[ ${line} =~ ${shebang} ]]; then
    shell=${BASH_REMATCH[4]}
  fi
  case ${suffix} in
    .sh | .bash)
      DIALECT=bash
      if [[ ${shell} == zsh ]]; then
        DIALECT=zsh
      fi
      ;;
    '') DIALECT=${shell} ;;
    *) ;;
  esac
}

# Sets GIT_OK to 1 and GIT_LIST to the files Git lists as modified, untracked or staged in work
# tree $1, one per line; GIT_OK is 0 outside a work tree or without git. Staged files count too:
# a command that runs `git add` leaves nothing `--modified`.
git_changed() {
  local tree=$1 rel
  GIT_OK=0
  GIT_LIST=''
  if [[ -z ${GIT} ]] || ! "${GIT}" -C "${tree}" rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    return 0
  fi
  GIT_OK=1
  "${GIT}" -C "${tree}" ls-files -z --modified --others --exclude-standard > "${TMP}/git" 2> /dev/null || :
  "${GIT}" -C "${tree}" diff -z --cached --name-only --relative >> "${TMP}/git" 2> /dev/null || :
  while IFS= read -r -d '' rel; do
    if [[ -n ${rel} && ${rel} != *"${NL}"* ]]; then
      GIT_LIST+="${tree}/${rel}${NL}"
    fi
  done < "${TMP}/git"
}

# Drops from FILES the files Git ignores: what a command writes into an ignored place, such as
# the hook scripts a package manager generates on install or a build folder, is output, not
# source the project maintains. A file outside every work tree is kept.
drop_ignored() {
  local path folder folders='' ignored='' name kept=()
  if [[ -z ${GIT} ]] || ((${#FILES[@]} == 0)); then
    return 0
  fi
  for path in "${FILES[@]}"; do
    listed "${folders}" "${path%/*}"
    if ((LISTED == 0)); then
      folders+="${path%/*}${NL}"
    fi
  done
  while IFS= read -r folder; do
    if [[ -z ${folder} ]]; then
      continue
    fi
    : > "${TMP}/names"
    for path in "${FILES[@]}"; do
      if [[ ${path%/*} == "${folder}" ]]; then
        printf '%s\0' "${path}" >> "${TMP}/names"
      fi
    done
    # Exit 0 lists the ignored paths, 1 means none is, 128 that the folder is in no work tree.
    if "${GIT}" -C "${folder}" check-ignore --stdin -z < "${TMP}/names" > "${TMP}/ignored" 2> /dev/null; then
      while IFS= read -r -d '' name; do
        ignored+="${name}${NL}"
      done < "${TMP}/ignored"
    fi
  done <<< "${folders}"
  for path in "${FILES[@]}"; do
    listed "${ignored}" "${path}"
    if ((LISTED == 0)); then
      kept+=("${path}")
    fi
  done
  FILES=(${kept[@]+"${kept[@]}"})
}

# Creates ${TMP}/since, a file whose modification time is $1 seconds ago (UTC, whole seconds).
mark_since() {
  local now stamp
  now=$(date +%s)
  stamp=$(env LC_ALL=C awk -v t="$((now - $1))" 'BEGIN {
    days = int(t / 86400); secs = t - days * 86400
    z = days + 719468; era = int(z / 146097); doe = z - era * 146097
    yoe = int((doe - int(doe / 1460) + int(doe / 36524) - int(doe / 146096)) / 365)
    doy = doe - (365 * yoe + int(yoe / 4) - int(yoe / 100)); mp = int((5 * doy + 2) / 153)
    d = doy - int((153 * mp + 2) / 5) + 1; m = mp < 10 ? mp + 3 : mp - 9; y = yoe + era * 400 + (m <= 2)
    printf "%04d%02d%02d%02d%02d.%02d", y, m, d, int(secs / 3600), int(secs % 3600 / 60), secs % 60
  }')
  env TZ=UTC0 touch -t "${stamp}" "${TMP}/since"
}

# Sets FILES to the files under $1 modified since ${TMP}/since: Git's view in a work tree, else
# a pruned walk of at most MAX_WALK_FILES files, after which WALKED is set to $1.
changed_since() {
  local project=$1 path
  FILES=()
  git_changed "${project}"
  if ((GIT_OK)); then
    while IFS= read -r path; do
      if [[ -n ${path} && -f ${path} && ${path} -nt ${TMP}/since ]]; then
        FILES+=("${path}")
      fi
    done <<< "${GIT_LIST}"
    return 0
  fi
  physical "${HOME:-/}"
  # A walk of the whole home directory or disk is never worth a hook's budget.
  if [[ ${project} == / || ${project} == "${PHYSICAL:-/}" ]]; then
    return 0
  fi
  {
    find "${project}" -type d \( -name .git -o -name node_modules -o -name .venv -o -name venv \
      -o -name site-packages -o -name dist -o -name build -o -name __pycache__ -o -name .cache \) \
      -prune -o -type f -print 2> /dev/null || :
  } | head -n "${MAX_WALK_FILES}" > "${TMP}/walk" || :
  while IFS= read -r path; do
    if [[ ${path} -nt ${TMP}/since ]]; then
      FILES+=("${path}")
    fi
  done < "${TMP}/walk"
  WALKED=${project}
}

# Sets TREE to the nearest folder between file $1 and WALKED that holds a .git entry, a nested
# work tree, or to '' when there is none.
nested_tree() {
  local dir=${1%/*}
  TREE=''
  while [[ ${dir} != "${WALKED}" && ${dir} == "${WALKED}"/* ]]; do
    if [[ -e ${dir}/.git ]]; then
      TREE=${dir}
      return 0
    fi
    dir=${dir%/*}
  done
}

# Splits FILES, found by modification time under WALKED, into VERIFIED and LOOSE. A clone, a
# checkout or a pull writes files with a new modification time that nobody edited: inside a
# nested Git work tree only the files Git lists as modified, untracked or staged are a change
# (verified), and the rest are dropped. Files outside every work tree are loose: nothing tells
# an edit from an arrival there.
own_changes() {
  local path i found trees=() lists=() oks=()
  VERIFIED=()
  LOOSE=()
  for path in ${FILES[@]+"${FILES[@]}"}; do
    nested_tree "${path}"
    if [[ -z ${TREE} ]]; then
      LOOSE+=("${path}")
      continue
    fi
    found=-1
    for ((i = 0; i < ${#trees[@]}; i++)); do
      if [[ ${trees[i]} == "${TREE}" ]]; then
        found=${i}
      fi
    done
    if ((found < 0)); then
      found=${#trees[@]}
      git_changed "${TREE}"
      trees+=("${TREE}")
      lists+=("${GIT_LIST}")
      oks+=("${GIT_OK}")
    fi
    listed "${lists[found]}" "${path}"
    if ((oks[found] == 0)); then
      LOOSE+=("${path}") # a .git entry Git does not accept as a work tree, or no git
    elif ((LISTED)); then
      VERIFIED+=("${path}")
    fi
  done
}

# Sets FOUND to the first of the names $2... in folder $1 or above it, or to '' when none is.
find_up() {
  local dir=$1 name
  shift
  FOUND=''
  for (( ; ; )); do
    for name in "$@"; do
      if [[ -e ${dir}/${name} ]]; then
        FOUND=${dir}/${name}
        return 0
      fi
    done
    if [[ -z ${dir} || ${dir} == / ]]; then
      return 0
    fi
    dir=${dir%/*}
  done
}

# Sets USER_CONFIG to 1 when ShellCheck finds a configuration of the user's for script $1.
shellcheck_config() {
  USER_CONFIG=1
  if [[ -n ${SHELLCHECK_OPTS:-} && ! ${SHELLCHECK_OPTS} =~ ^[[:space:]]*$ ]]; then
    return 0
  fi
  find_up "${1%/*}" .shellcheckrc shellcheckrc
  if [[ -n ${FOUND} || -e ${HOME:-}/.shellcheckrc || -e ${XDG_CONFIG_HOME:-${HOME:-}/.config}/shellcheckrc ]]; then
    return 0
  fi
  USER_CONFIG=0
}

# Runs shfmt and shellcheck on script $1, appends what they report to FINDINGS and sets REWROTE
# to 1 when shfmt changed the file, else to 0.
check_file() {
  local path=$1 before after code output
  local shfmt_args=(-i 2 -ci -bn -w) shellcheck_args=(-o all -S style -x -a -P SCRIPTDIR)
  before=$(cksum < "${path}")
  find_up "${path%/*}" .editorconfig
  if [[ -n ${FOUND} ]]; then
    shfmt_args=(-w)
  fi
  code=0
  "${SHFMT}" "${shfmt_args[@]}" "${path}" > "${TMP}/out" 2>&1 || code=$?
  output=$(< "${TMP}/out")
  if ((code != 0)); then
    FINDINGS+="shfmt (${path}):${NL}${output}${NL}"
  fi
  after=$(cksum < "${path}")
  REWROTE=0
  if [[ ${before} != "${after}" ]]; then
    REWROTE=1
  fi
  shellcheck_config "${path}"
  if ((USER_CONFIG)); then
    shellcheck_args=()
  fi
  code=0
  "${SHELLCHECK}" ${shellcheck_args[@]+"${shellcheck_args[@]}"} "${path}" > "${TMP}/out" 2>&1 || code=$?
  output=$(< "${TMP}/out")
  if ((code == 1)); then
    FINDINGS+="shellcheck (${path}):${NL}${output}${NL}"
  elif ((code != 0)); then
    FINDINGS+="shellcheck failed, so ${path} was not checked:${NL}${output}${NL}"
  fi
}

# Sets HINT to the command that installs tool $1 (shfmt or shellcheck) on this system, from the
# package manager found here, as each tool's own install instructions give it.
install_hint() {
  local tool=$1 system=''
  system=$(uname -s)
  if [[ ${system} == Darwin ]]; then
    HINT="brew install ${tool}"
    if ! command -v brew > /dev/null && command -v port > /dev/null; then
      HINT="sudo port install ${tool}"
    fi
    return 0
  fi
  if command -v apt-get > /dev/null; then
    HINT="sudo apt install ${tool}"
  elif command -v dnf > /dev/null; then
    HINT="sudo dnf install ${tool}"
    if [[ ${tool} == shellcheck ]]; then
      HINT='sudo dnf install ShellCheck'
    fi
  elif command -v pacman > /dev/null; then
    HINT="sudo pacman -S ${tool}"
  elif command -v zypper > /dev/null; then
    HINT="sudo zypper install ${tool}"
    if [[ ${tool} == shellcheck ]]; then
      HINT='sudo zypper install ShellCheck'
    fi
  elif command -v apk > /dev/null && [[ ${tool} == shfmt ]]; then
    HINT='sudo apk add shfmt'
  elif command -v brew > /dev/null; then
    HINT="brew install ${tool}"
  elif [[ ${tool} == shfmt ]]; then
    HINT='go install mvdan.cc/sh/v3/cmd/shfmt@latest, or a binary from https://github.com/mvdan/sh/releases'
  else
    HINT='a binary from https://github.com/koalaman/shellcheck/releases'
  fi
}

# Prints the JSON object with the one line the user sees: the plugin's name, then the parts
# given, joined with " · ".
user_message() {
  local part line="${PLUGIN}:" separator=' ' quoted
  for part in "$@"; do
    line+="${separator}${part}"
    separator=' · '
  done
  quoted=$(printf '%s' "${line}" | env LC_ALL=C awk -f "${HERE}/json-string.awk")
  printf '{"systemMessage":%s}\n' "${quoted}"
}

# Sets REPORT to text $1 cut on a line boundary so that it and $2 more characters fit under
# MAX_REPORT_CHARS, saying how many lines were dropped.
bounded() {
  local text=$1 limit=$((MAX_REPORT_CHARS - $2)) line size=0 dropped=0
  REPORT=${text}
  if ((${#text} <= limit)); then
    return 0
  fi
  REPORT=''
  while IFS= read -r line; do
    if ((dropped > 0 || size + ${#line} + 1 > limit)); then
      dropped=$((dropped + 1))
      continue
    fi
    REPORT+="${line}${NL}"
    size=$((size + ${#line} + 1))
  done <<< "${text%"${NL}"}"
  REPORT+="… ${dropped} more lines${NL}"
}

# Sets FILES to the files the tool call in event $1 changed, by tool name: the Edit or Write
# path, the list Claude Code passes for a Bash call, or else the files under the project
# modified while it ran. Exits 0 for any other tool or for input that is not an event.
changed_files() {
  local fields key value tool='' cwd='' duration='' file_path='' bash_list=0 changed=() window
  if ! fields=$(printf '%s' "$1" | env LC_ALL=C awk -f "${HERE}/read-event.awk"); then
    exit 0
  fi
  while IFS=$'\t' read -r key value; do
    case ${key} in
      tool_name) tool=${value} ;;
      cwd) cwd=${value} ;;
      duration_ms) duration=${value} ;;
      tool_input.file_path) file_path=${value} ;;
      tool_response.bashEditDiff.changedFiles) bash_list=1 ;;
      'tool_response.bashEditDiff.changedFiles[]') changed+=("${value}") ;;
      *) ;;
    esac
  done <<< "${fields}"
  case ${tool} in
    Edit | Write)
      changed=("${file_path}")
      bash_list=0
      ;;
    Bash) ;;
    *) exit 0 ;;
  esac
  TMP=$(mktemp -d "${TMPDIR:-/tmp}/${PLUGIN}.XXXXXX")
  GIT=$(command -v git) || GIT=''
  BASE=''
  for value in "${CLAUDE_PROJECT_DIR:-}" "${cwd}" "${PWD}"; do
    if [[ -n ${value} && -d ${value} ]]; then
      physical "${value}"
      BASE=${PHYSICAL}
      if [[ -n ${BASE} ]]; then
        break
      fi
    fi
  done
  FILES=()
  WALKED=''
  BASH_LIST=${bash_list}
  if [[ ${tool} != Bash || ${bash_list} == 1 ]]; then
    for value in ${changed[@]+"${changed[@]}"}; do
      physical "${value}"
      if [[ -n ${value} && -f ${PHYSICAL} ]]; then
        FILES+=("${PHYSICAL}")
      fi
    done
  elif [[ -n ${BASE} ]]; then
    window=${FALLBACK_WINDOW_MS}
    if [[ -n ${duration} ]]; then
      window=$((duration + BASH_SLACK_MS))
    fi
    mark_since $(((window + 999) / 1000))
    changed_since "${BASE}"
  fi
}

main() {
  local input='' path seen='' shell_files=() scripts=() zsh=() notes=()
  IFS= read -r -d '' input || :
  changed_files "${input}"

  # The shell scripts among them, once each, outside third-party folders.
  for path in ${FILES[@]+"${FILES[@]}"}; do
    listed "${seen}" "${path}"
    case "/${path}/" in
      */node_modules/* | */.venv/* | */venv/* | */site-packages/*) continue ;;
      *) ;;
    esac
    if ((LISTED)); then
      continue
    fi
    seen+="${path}${NL}"
    dialect "${path}"
    if [[ -n ${DIALECT} ]]; then
      shell_files+=("${path}")
    fi
  done
  FILES=(${shell_files[@]+"${shell_files[@]}"})
  if [[ -n ${WALKED} ]]; then
    own_changes
    if ((${#LOOSE[@]} > MAX_FILES)); then
      notes+=("not run on ${#LOOSE[@]} shell files this command left outside a Git work tree (more than the ${MAX_FILES} checked per tool call)")
      FILES=(${VERIFIED[@]+"${VERIFIED[@]}"})
    else
      FILES=(${VERIFIED[@]+"${VERIFIED[@]}"} ${LOOSE[@]+"${LOOSE[@]}"})
    fi
  elif ((BASH_LIST)); then
    drop_ignored
  fi
  for path in ${FILES[@]+"${FILES[@]}"}; do
    dialect "${path}"
    if [[ ${DIALECT} == zsh ]]; then
      zsh+=("${path}")
    else
      scripts+=("${path}")
    fi
  done
  if ((${#zsh[@]} > 0)); then
    names_of "${zsh[@]}"
    notes=("not run on ${NAMES}: ShellCheck does not support zsh" ${notes[@]+"${notes[@]}"})
  fi
  if ((${#scripts[@]} == 0)); then
    if ((${#notes[@]} > 0)); then
      user_message "${notes[@]}"
    fi
    exit 0
  fi

  local missing=''
  SHFMT=$(command -v shfmt) || missing=shfmt
  SHELLCHECK=$(command -v shellcheck) || missing=${missing:-shellcheck}
  if [[ -n ${missing} ]]; then
    install_hint "${missing}"
    names_of "${scripts[@]}"
    user_message "not run on ${NAMES}: ${missing} is not installed (install it with ${HINT})" ${notes[@]+"${notes[@]}"}
    exit 0
  fi

  local checked=("${scripts[@]:0:MAX_FILES}") unchecked=() rewritten=() with_errors=() findings='' parts=() head
  if ((${#scripts[@]} > MAX_FILES)); then
    unchecked=("${scripts[@]:MAX_FILES}")
  fi
  for path in "${checked[@]}"; do
    FINDINGS=''
    check_file "${path}"
    if ((REWROTE)); then
      rewritten+=("${path}")
    fi
    if [[ -n ${FINDINGS} ]]; then
      with_errors+=("${path}")
      findings+=${FINDINGS}
    fi
  done
  names_of "${checked[@]}"
  parts=("ran shfmt, shellcheck on ${NAMES}")
  head="${PLUGIN}'s post-edit hook ran shfmt, shellcheck on ${NAMES} and found errors:${NL}"
  parts+=('no formatting changes')
  if ((${#rewritten[@]} > 0)); then
    names_of "${rewritten[@]}"
    parts[1]="reformatted ${NAMES}"
  fi
  parts+=('no errors')
  if ((${#with_errors[@]} > 0)); then
    names_of "${with_errors[@]}"
    parts[2]="errors in ${NAMES}, sent to Claude to fix"
  fi
  if ((${#unchecked[@]} > 0)); then
    names_of "${unchecked[@]}"
    parts+=("not run on ${NAMES} (more than the ${MAX_FILES} checked per tool call)")
  fi
  user_message "${parts[@]}" ${notes[@]+"${notes[@]}"}
  if [[ -n ${findings} ]]; then
    bounded "${head}${findings}" $((${#CLAUDE_INSTRUCTION} + 1))
    printf '%s%s\n' "${REPORT}" "${CLAUDE_INSTRUCTION}" >&2
    exit 2
  fi
  exit 0
}

main
