#!/usr/bin/env bash
# PostToolUse hook of plugin-engineering: after Claude edits or writes a file inside a plugin,
# runs `claude plugin validate --strict` on that plugin, and hands every error and warning to
# Claude. A file under a marketplace's own .claude-plugin/ folder validates the marketplace. When
# the edited file is code (.ts, .tsx, .js, .mjs, .cjs) or hooks/hooks.json in a plugin that has
# mod tests (*.test.ts or *.test.tsx), it also runs `claude plugin test` on the plugin.
#
# Reads one PostToolUse event (Edit or Write) on stdin. Two outcomes, never mixed:
# - Findings: a check ran and reported problems (exit 1 from the validator or the tests). The
#   reports go to stderr with exit 2, which Claude sees next to the tool result.
# - Hook failure: a check could not run (no claude binary, mods turned off in this shell, any
#   other exit code). The reason goes to stderr with exit 1; hooks.json sets onFailure "block",
#   so Claude sees it too.
# Silent, exit 0, when the file is in no plugin or every check passes. Every report goes to Claude
# whole, never cut: the docs set no cap on a hook's stderr on exit 2.
#
# A plugin is the nearest folder above the file that holds .claude-plugin/plugin.json; a plugin
# without a manifest isn't detected. The checks run with the session's own binary
# (CLAUDE_CODE_EXECPATH, set by Claude Code but not documented), else the first claude on PATH.
#
# Needs Bash 3.2 or later, POSIX awk, env and find. Reads only the edited file's path and the
# plugin's file names; writes nothing and makes no network call. The event is read with
# read-event.awk, next to this script.

set -Eeuo pipefail

readonly PLUGIN='plugin-engineering'
# set -E hands this trap to every command substitution too, and Bash 3.2 runs it there for a
# failure its caller handles, such as `x=$(command -v claude) || x=''`. Inside a subshell it
# only exits 1 and leaves the caller to decide; only the hook itself reports.
trap '((BASH_SUBSHELL == 0)) || exit 1; printf "%s: the validation hook failed at line %s, so the plugin was not checked.\n" "${PLUGIN}" "${LINENO}" >&2; exit 1' ERR

HERE=${BASH_SOURCE[0]%/*}
if [[ ${HERE} == "${BASH_SOURCE[0]}" ]]; then
  HERE=.
fi

FINDINGS=''
FAILURES=''

# Sets FILE to the Edit or Write path of event $1, with backslashes turned into slashes.
# Exits 0 for any other tool, an event with no path, or input that is not an event.
edited_file() {
  local fields key value tool='' path=''
  if ! fields=$(printf '%s' "$1" | env LC_ALL=C awk -f "${HERE}/read-event.awk"); then
    exit 0
  fi
  while IFS=$'\t' read -r key value; do
    case ${key} in
      tool_name) tool=${value} ;;
      tool_input.file_path) path=${value} ;;
      *) ;;
    esac
  done <<< "${fields}"
  case ${tool} in
    Edit | Write) ;;
    *) exit 0 ;;
  esac
  if [[ -z ${path} ]]; then
    exit 0
  fi
  FILE=${path//\\//}
}

# Sets TARGET to the folder to check for FILE, and KIND to plugin or marketplace: the nearest
# folder above it with .claude-plugin/plugin.json, or a marketplace root when FILE is in its
# .claude-plugin/ folder. Exits 0 when there is none.
target_folder() {
  local dir=${FILE%/*} parent
  while [[ -n ${dir} ]]; do
    if [[ -f ${dir}/.claude-plugin/plugin.json ]]; then
      TARGET=${dir}
      KIND=plugin
      return 0
    fi
    if [[ -f ${dir}/.claude-plugin/marketplace.json ]]; then
      if [[ ${FILE} == "${dir}/.claude-plugin/"* ]]; then
        TARGET=${dir}
        KIND=marketplace
        return 0
      fi
      exit 0
    fi
    parent=${dir%/*}
    if [[ ${parent} == "${dir}" ]]; then
      break
    fi
    dir=${parent}
  done
  exit 0
}

# Sets CLAUDE to the claude binary to check with. Exits 1 with the reason when there is none.
claude_binary() {
  if [[ -n ${CLAUDE_CODE_EXECPATH:-} && -x ${CLAUDE_CODE_EXECPATH} ]]; then
    CLAUDE=${CLAUDE_CODE_EXECPATH}
    return 0
  fi
  if CLAUDE=$(command -v claude); then
    return 0
  fi
  printf '%s: found no claude binary, neither CLAUDE_CODE_EXECPATH nor claude on PATH, so %s was not checked after this edit. Run claude plugin validate --strict %s yourself.\n' \
    "${PLUGIN}" "${TARGET}" "${TARGET}" >&2
  exit 1
}

# Runs check $1 (a label, the command line shown) as the command $2...: exit 0 passes, exit 1 is a
# finding, any other exit, or the mods-off message, is a hook failure.
check() {
  local label=$1 output status=0
  shift
  output=$("$@" 2>&1) || status=$?
  if [[ ${output} == *'hooks modules are turned off'* ]]; then
    FAILURES+="${label} could not run: mods can't load in this shell."$'\n'"${output}"$'\n\n'
    return 0
  fi
  case ${status} in
    0) ;;
    1) FINDINGS+="${label} fails:"$'\n'"${output}"$'\n\n' ;;
    *) FAILURES+="${label} exited ${status} instead of 0 or 1:"$'\n'"${output}"$'\n\n' ;;
  esac
}

# Sets MOD_TESTS to yes when FILE is code or hooks/hooks.json of a plugin that has mod tests.
mod_tests() {
  local found
  MOD_TESTS=no
  case ${FILE} in
    *.ts | *.tsx | *.js | *.mjs | *.cjs | "${TARGET}/hooks/hooks.json") ;;
    *) return 0 ;;
  esac
  found=$(find "${TARGET}" -name node_modules -prune -o \( -name '*.test.ts' -o -name '*.test.tsx' \) -print 2> /dev/null) || found=''
  if [[ -n ${found} ]]; then
    MOD_TESTS=yes
  fi
}

main() {
  local event
  event=$(cat)
  edited_file "${event}"
  target_folder
  claude_binary
  check "claude plugin validate --strict ${TARGET}" "${CLAUDE}" plugin validate --strict "${TARGET}"
  mod_tests
  if [[ ${KIND} == plugin && ${MOD_TESTS} == yes ]]; then
    check "claude plugin test ${TARGET}" "${CLAUDE}" plugin test "${TARGET}"
  fi
  if [[ -n ${FAILURES} ]]; then
    printf '%s: these checks could not run after the edit of %s, so it is not fully checked:\n\n%s' "${PLUGIN}" "${FILE}" "${FAILURES}" >&2
    if [[ -n ${FINDINGS} ]]; then
      printf 'The checks that did run also found problems:\n\n%s' "${FINDINGS}" >&2
    fi
    exit 1
  fi
  if [[ -n ${FINDINGS} ]]; then
    printf '%s: checks found problems after the edit of %s. Fix every error and warning they report; the next edit in this folder checks it again.\n\n%s' "${PLUGIN}" "${FILE}" "${FINDINGS}" >&2
    exit 2
  fi
  exit 0
}

main "$@"
