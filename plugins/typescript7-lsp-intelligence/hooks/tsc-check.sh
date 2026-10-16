#!/usr/bin/env bash
# Post-edit hook of the TypeScript LSP intelligence plugins. Reads one PostToolUse or
# PostToolUseFailure event on stdin and type-checks every TypeScript or JavaScript file the
# tool call changed, with the project's environment and the plugin's strictness:
#
# - Environment (module resolution, paths, jsx, lib, types, include) comes from the
#   project: the nearest tsconfig.json or jsconfig.json above the file, followed through
#   its references to the program that lists the file.
# - Strictness comes from tsconfig.strictest.json next to this script: each boolean option
#   is passed on the command line, so it overrides the project's value, explicit false too.
#   Its checkJs brings the JavaScript files of a program into the check, as allowJs would.
# - A file outside every program is checked alone on top of the nearest config, or on top
#   of tsconfig.strictest.json without one.
# - Strictest errors count for the edited files only; errors in other files count only when
#   the project's own config finds them too; errors in the project's config always count.
#
# The compiler is the user's own: the project's node_modules first, then a global install
# found on PATH or in the folders of the common Node version managers, since hooks do not
# load the user's shell profile. Nothing is installed. typescript7-lsp-intelligence runs the
# native compiler directly; typescript6-lsp-intelligence runs tsc on Node.
#
# Findings reach Claude as {"decision":"block"} JSON. Without a usable compiler the hook does
# not block: the user is told once per session where it searched, and Claude is told the
# files were not checked. Any other failure exits non-zero, which hooks.json turns into a
# block with onFailure. Bash 3.2 or later; no jq, no Python. This file is byte-identical in
# typescript6-lsp-intelligence and typescript7-lsp-intelligence.

set -euo pipefail

readonly MAX_REPORT_CHARS=9000
readonly BASH_SLACK_S=2
readonly FALLBACK_WINDOW_S=30
readonly MAX_WALK_FILES=20000
readonly TS_FILE_PATTERN='\.(ts|tsx|mts|cts|js|jsx|mjs|cjs)$'
readonly NL=$'\n'

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly HOOK_DIR
readonly STRICTEST="${HOOK_DIR}/tsconfig.strictest.json"
PLUGIN_ROOT="$(cd "${HOOK_DIR}/.." && pwd -P)"
readonly PLUGIN_ROOT
PLUGIN="$(sed -n 's/^[[:space:]]*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
  "${PLUGIN_ROOT}/.claude-plugin/plugin.json")"
PLUGIN="${PLUGIN%%"${NL}"*}"
readonly PLUGIN
case "${PLUGIN}" in
  typescript7-*)
    readonly NATIVE=yes
    readonly NODE_MIN=16.20.0
    ;;
  *)
    readonly NATIVE=no
    readonly NODE_MIN=14.17.0
    ;;
esac
readonly README_URL="https://github.com/nerymurillohnd/the-claude-factory/tree/main/plugins/${PLUGIN}#-requirements"

# Canonical, so the paths tsc prints relative to it resolve back to the same files.
WORK="$(mktemp -d)"
WORK="$(cd "${WORK}" && pwd -P)"
readonly WORK
trap 'rm -rf "${WORK}"' EXIT

EVENT="$(tr '\n\r' '  ')"
readonly EVENT

# ── JSON ────────────────────────────────────────────────────────────────────────────────

# Sets UNESCAPED to $1 without the JSON escapes a path or an identifier can carry.
UNESCAPED=""
json_unescape() {
  local s="$1" bs=$'\001'
  s="${s//\\\\/${bs}}"
  s="${s//\\\"/\"}"
  s="${s//\\\//\/}"
  s="${s//\\t/$'\t'}"
  UNESCAPED="${s//${bs}/\\}"
}

# Sets VALUE to the first string value of key $1 anywhere in the event, empty when absent.
VALUE=""
json_string() {
  local raw
  raw="$(printf '%s' "${EVENT}" | sed -E -n \
    "s/^[^\"]*(\"([^\"\\\\]|\\\\.)*\"[^\"]*)*\"$1\"[[:space:]]*:[[:space:]]*\"(([^\"\\\\]|\\\\.)*)\".*/\\3/p")"
  json_unescape "${raw}"
  VALUE="${UNESCAPED}"
}

# Sets VALUE to the first number value of key $1 anywhere in the event, empty when absent.
json_number() {
  VALUE="$(printf '%s' "${EVENT}" | sed -E -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*([0-9]+).*/\\1/p")"
}

# Sets ESCAPED to $1 escaped for a JSON string; control characters other than tab and
# newline are dropped.
ESCAPED=""
json_escape() {
  local s
  s="$(printf '%s' "$1" | LC_ALL=C tr -d '\000-\010\013\014\016-\037')"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\t'/\\t}"
  ESCAPED="${s//${NL}/\\n}"
}

# ── Paths ───────────────────────────────────────────────────────────────────────────────

# Sets POSIX to $1 as Git Bash sees a Windows path; other paths stay as they are.
POSIX=""
to_posix() {
  POSIX="$1"
  case "$1" in
    [A-Za-z]:[\\/]*)
      if command -v cygpath > /dev/null 2>&1; then
        POSIX="$(cygpath -u "$1")"
      fi
      ;;
    *) ;;
  esac
}

# Sets CANONICAL to the path of $1 with its folder's symlinks resolved, as tsc lists files;
# $1 itself when its folder does not exist.
CANONICAL=""
canonical() {
  local dir
  CANONICAL="$1"
  dir="$(dirname "$1")"
  [[ -d ${dir} ]] || return 0
  dir="$(cd "${dir}" && pwd -P)"
  CANONICAL="${dir}/$(basename "$1")"
}

# Sets CANONICAL to the real file behind a chain of symlinks.
resolve_link() {
  local path="$1" target count=0
  while [[ -L ${path} && ${count} -lt 40 ]]; do
    target="$(readlink "${path}")"
    case "${target}" in
      /*) path="${target}" ;;
      *) path="$(dirname "${path}")/${target}" ;;
    esac
    count=$((count + 1))
  done
  canonical "${path}"
}

# ── Tool discovery ──────────────────────────────────────────────────────────────────────

SEARCHED=""
SKIPPED=""
DIRS=()

add_dir() {
  local dir="$1" known
  [[ -n ${dir} && -d ${dir} ]] || return 0
  for known in "${DIRS[@]+"${DIRS[@]}"}"; do
    [[ ${known} == "${dir}" ]] && return 0
  done
  DIRS+=("${dir}")
}

add_posix_dir() {
  to_posix "$1"
  add_dir "${POSIX}$2"
}

add_nvm_dirs() {
  local nvm_dir="${NVM_DIR:-}" versions wanted names sorted version
  if [[ -z ${nvm_dir} ]]; then
    if [[ -n ${XDG_CONFIG_HOME:-} ]]; then
      nvm_dir="${XDG_CONFIG_HOME}/nvm"
    else
      nvm_dir="${HOME}/.nvm"
    fi
  fi
  versions="${nvm_dir}/versions/node"
  [[ -d ${versions} ]] || return 0
  if [[ -f "${nvm_dir}/alias/default" ]]; then
    wanted="$(head -n 1 "${nvm_dir}/alias/default")"
    add_dir "${versions}/v${wanted#v}/bin"
  fi
  names="$(find "${versions}" -mindepth 1 -maxdepth 1 -name 'v*' -exec basename {} \;)"
  sorted="$(printf '%s\n' "${names}" | sed 's/^v//' | sort -t . -k1,1nr -k2,2nr -k3,3nr)"
  while IFS= read -r version; do
    [[ -n ${version} ]] && add_dir "${versions}/v${version}/bin"
  done <<< "${sorted}"
  return 0
}

# Candidate bin folders: the inherited PATH first, then every Node manager's global folder.
collect_dirs() {
  local entry data_home="${XDG_DATA_HOME:-${HOME}/.local/share}" os fnm_dir prefix pnpm_home
  local -a entries
  IFS=: read -r -a entries <<< "${PATH}"
  for entry in "${entries[@]+"${entries[@]}"}"; do
    add_dir "${entry}"
  done
  add_nvm_dirs
  for fnm_dir in "${FNM_DIR:-}" "${data_home}/fnm" "${HOME}/.fnm" \
    "${HOME}/Library/Application Support/fnm"; do
    [[ -n ${fnm_dir} ]] && add_posix_dir "${fnm_dir}" /aliases/default/bin
  done
  add_posix_dir "${VOLTA_HOME:-${HOME}/.volta}" /bin
  add_posix_dir "${ASDF_DATA_DIR:-${HOME}/.asdf}" /shims
  add_posix_dir "${MISE_DATA_DIR:-${data_home}/mise}" /shims
  add_posix_dir "${N_PREFIX:-/usr/local}" /bin
  [[ -n ${NPM_CONFIG_PREFIX:-} ]] && add_posix_dir "${NPM_CONFIG_PREFIX}" /bin
  if [[ -f "${HOME}/.npmrc" ]]; then
    prefix="$(sed -n 's/^[[:space:]]*prefix[[:space:]]*=[[:space:]]*//p' "${HOME}/.npmrc")"
    prefix="${prefix%%"${NL}"*}"
    prefix="${prefix/#\~/${HOME}}"
    [[ -n ${prefix} ]] && add_posix_dir "${prefix}" /bin
  fi
  add_dir "${HOME}/.local/bin"
  os="$(uname -s)"
  pnpm_home="${PNPM_HOME:-}"
  if [[ -z ${pnpm_home} ]]; then
    if [[ ${os} == Darwin ]]; then
      pnpm_home="${HOME}/Library/pnpm"
    else
      pnpm_home="${data_home}/pnpm"
    fi
  fi
  add_posix_dir "${pnpm_home}" /bin
  add_posix_dir "${pnpm_home}" ""
  add_posix_dir "${BUN_INSTALL:-${HOME}/.bun}" /bin
  add_dir /opt/homebrew/bin
  add_dir /usr/local/bin
  add_dir /home/linuxbrew/.linuxbrew/bin
  [[ -n ${APPDATA:-} ]] && add_posix_dir "${APPDATA}" /npm
  return 0
}

# Sets AT_LEAST to yes when version $1 (x.y.z) is at least $2, else no.
AT_LEAST=no
version_at_least() {
  local a1 a2 a3 b1 b2 b3
  IFS=. read -r a1 a2 a3 <<< "$1"
  IFS=. read -r b1 b2 b3 <<< "$2"
  a1="${a1//[!0-9]/}" a2="${a2//[!0-9]/}" a3="${a3//[!0-9]/}"
  a1="${a1:-0}" a2="${a2:-0}" a3="${a3:-0}"
  AT_LEAST=no
  if ((a1 != b1)); then
    ((a1 > b1)) && AT_LEAST=yes
  elif ((a2 != b2)); then
    ((a2 > b2)) && AT_LEAST=yes
  elif ((a3 >= b3)); then
    AT_LEAST=yes
  fi
  return 0
}

# Sets NODE_DIR to the first folder whose node is at least NODE_MIN; empty without one.
NODE_DIR=""
find_node() {
  local dir version
  for dir in "${DIRS[@]+"${DIRS[@]}"}"; do
    [[ -x "${dir}/node" || -x "${dir}/node.exe" ]] || continue
    SEARCHED="${SEARCHED}${dir}/node${NL}"
    version="$(PATH="${dir}:${PATH}" node --version 2> /dev/null || true)"
    version="${version#v}"
    if [[ -n ${version} ]]; then
      version_at_least "${version}" "${NODE_MIN}"
      if [[ ${AT_LEAST} == yes ]]; then
        NODE_DIR="${dir}"
        return 0
      fi
    fi
    SKIPPED="${SKIPPED}${dir}/node (${version:-did not run}; needs ${NODE_MIN} or later)${NL}"
  done
  return 0
}

# Sets NATIVE_TSC to the native compiler of TypeScript 7 package $1, found the way Node
# resolves its platform package: in node_modules folders from the package upward.
NATIVE_TSC=""
native_compiler() {
  local dir os arch platform exe=tsc
  NATIVE_TSC=""
  os="$(uname -s)"
  case "${os}" in
    Darwin) os=darwin ;;
    Linux) os=linux ;;
    MINGW* | MSYS* | CYGWIN*)
      os=win32
      exe=tsc.exe
      ;;
    *) return 0 ;;
  esac
  arch="$(uname -m)"
  case "${arch}" in
    arm64 | aarch64) arch=arm64 ;;
    x86_64 | amd64) arch=x64 ;;
    *) return 0 ;;
  esac
  platform="@typescript/typescript-${os}-${arch}/lib/${exe}"
  dir="$1"
  while :; do
    if [[ -x "${dir}/node_modules/${platform}" ]]; then
      NATIVE_TSC="${dir}/node_modules/${platform}"
      return 0
    fi
    if [[ ${dir##*/} == node_modules && -x "${dir}/${platform}" ]]; then
      NATIVE_TSC="${dir}/${platform}"
      return 0
    fi
    [[ ${dir} == / || ${dir} == . || -z ${dir} ]] && return 0
    dir="$(dirname "${dir}")"
  done
}

# Sets TSC to the command that runs tsc candidate $1; leaves it empty when it cannot run.
TSC=()
use_tsc() {
  local tsc="$1" package="" version
  TSC=()
  resolve_link "${tsc}"
  case "${CANONICAL}" in
    */typescript/bin/tsc) package="${CANONICAL%/bin/tsc}" ;;
    *) ;;
  esac
  if [[ ${NATIVE} == yes && -n ${package} ]]; then
    native_compiler "${package}"
    if [[ -n ${NATIVE_TSC} ]]; then
      version="$("${NATIVE_TSC}" --version 2> /dev/null || true)"
      if [[ ${version} == Version* ]]; then
        TSC=("${NATIVE_TSC}")
        return 0
      fi
    fi
  fi
  if [[ -z ${NODE_DIR} ]]; then
    SKIPPED="${SKIPPED}${tsc} (no Node.js ${NODE_MIN} or later to run it)${NL}"
    return 0
  fi
  version="$(PATH="${NODE_DIR}:${PATH}" "${tsc}" --version 2> /dev/null || true)"
  if [[ ${version} != Version* ]]; then
    SKIPPED="${SKIPPED}${tsc} (did not run with ${NODE_DIR}/node)${NL}"
    return 0
  fi
  TSC=(env "PATH=${NODE_DIR}:${PATH}" "${tsc}")
}

# Sets TSC for file $1: the project's node_modules above it first, then a global tsc.
find_tsc() {
  local dir candidate
  TSC=()
  dir="$(dirname "$1")"
  while :; do
    for candidate in "${dir}/node_modules/.bin/tsc" "${dir}/node_modules/typescript/bin/tsc"; do
      [[ -f ${candidate} ]] || continue
      SEARCHED="${SEARCHED}${candidate}${NL}"
      use_tsc "${candidate}"
      [[ ${#TSC[@]} -gt 0 ]] && return 0
    done
    [[ ${dir} == / || ${dir} == . ]] && break
    dir="$(dirname "${dir}")"
  done
  for dir in "${DIRS[@]+"${DIRS[@]}"}"; do
    candidate="${dir}/tsc"
    [[ -f ${candidate} ]] || continue
    SEARCHED="${SEARCHED}${candidate}${NL}"
    use_tsc "${candidate}"
    [[ ${#TSC[@]} -gt 0 ]] && return 0
  done
  return 0
}

# ── Programs ────────────────────────────────────────────────────────────────────────────

# Sets NEAREST to the nearest tsconfig.json or jsconfig.json above file $1, or empty.
NEAREST=""
nearest_config() {
  local dir name
  NEAREST=""
  dir="$(dirname "$1")"
  while :; do
    for name in tsconfig.json jsconfig.json; do
      if [[ -f "${dir}/${name}" ]]; then
        NEAREST="${dir}/${name}"
        return 0
      fi
    done
    [[ ${dir} == / || ${dir} == . ]] && return 0
    dir="$(dirname "${dir}")"
  done
}

# Sets REFERENCED to the configs config $1 references, one per line, resolved through tsc
# so extends and comments are handled; a folder reference means its tsconfig.json.
REFERENCED=""
referenced_configs() {
  local config="$1" base shown paths line target
  REFERENCED=""
  base="$(dirname "${config}")"
  shown="$(cd "${base}" && "${TSC[@]}" --showConfig -p "${config}" 2> /dev/null || true)"
  paths="$(printf '%s\n' "${shown}" | sed -n '/"references"/,$p' \
    | sed -n 's/^[[:space:]]*"path"[[:space:]]*:[[:space:]]*"\(.*\)",\{0,1\}[[:space:]]*$/\1/p')"
  while IFS= read -r line; do
    [[ -n ${line} ]] || continue
    json_unescape "${line}"
    case "${UNESCAPED}" in
      /*) target="${UNESCAPED}" ;;
      *) target="${base}/${UNESCAPED}" ;;
    esac
    [[ -d ${target} ]] && target="${target}/tsconfig.json"
    [[ -f ${target} ]] || continue
    canonical "${target}"
    REFERENCED="${REFERENCED}${CANONICAL}${NL}"
  done <<< "${paths}"
  return 0
}

# Sets PROGRAM to the config whose program lists file $1 under the strictest flags, so
# JavaScript counts as checkJs admits it; to "uncovered <nearest>" when no program does,
# or to "none" without a config. A config tsc cannot read is used as is.
PROGRAM=""
program_of() {
  local file="$1" nearest queue config listed seen="${NL}"
  nearest_config "${file}"
  if [[ -z ${NEAREST} ]]; then
    PROGRAM=none
    return 0
  fi
  canonical "${NEAREST}"
  nearest="${CANONICAL}"
  queue="${nearest}${NL}"
  while [[ -n ${queue} ]]; do
    config="${queue%%"${NL}"*}"
    queue="${queue#*"${NL}"}"
    [[ -n ${config} ]] || continue
    [[ ${seen} == *"${NL}${config}${NL}"* ]] && continue
    seen="${seen}${config}${NL}"
    listed="$(cd "$(dirname "${config}")" && "${TSC[@]}" --listFilesOnly -p "${config}" "${STRICT_FLAGS[@]+"${STRICT_FLAGS[@]}"}" 2>&1 || true)"
    if [[ ${listed} == *"error TS"* && ${config} == "${nearest}" ]]; then
      PROGRAM="${config}"
      return 0
    fi
    if [[ "${NL}${listed}${NL}" == *"${NL}${file}${NL}"* ]]; then
      PROGRAM="${config}"
      return 0
    fi
    referenced_configs "${config}"
    queue="${queue}${REFERENCED}"
  done
  PROGRAM="uncovered ${nearest}"
}

# The boolean options of tsconfig.strictest.json as command-line flags.
STRICT_FLAGS=()
load_strict_flags() {
  local options name value
  options="$(sed -n -E 's/^[[:space:]]*"([A-Za-z]+)"[[:space:]]*:[[:space:]]*(true|false),?[[:space:]]*$/\1 \2/p' "${STRICTEST}")"
  while IFS=' ' read -r name value; do
    [[ -n ${name} ]] && STRICT_FLAGS+=("--${name}" "${value}")
  done <<< "${options}"
  return 0
}

# Writes config $1 that checks file $3 alone on top of base config $2.
write_alone_config() {
  local out="$1" base="$2" file="$3" options="" roots="" dir types shown base_json file_json
  # A config in a temporary folder would not find the project's @types: give it the
  # folders tsc searches by default, unless the base sets typeRoots itself.
  if [[ ${base} != "${STRICTEST}" ]]; then
    shown="$(cd "$(dirname "${base}")" && "${TSC[@]}" --showConfig -p "${base}" 2> /dev/null || true)"
    if [[ ${shown} != *'"typeRoots"'* ]]; then
      dir="$(dirname "${base}")"
      while :; do
        types="${dir}/node_modules/@types"
        if [[ -d ${types} ]]; then
          json_escape "${types}"
          roots="${roots:+${roots}, }\"${ESCAPED}\""
        fi
        [[ ${dir} == / || ${dir} == . ]] && break
        dir="$(dirname "${dir}")"
      done
      [[ -n ${roots} ]] && options="${options:+${options}, }\"typeRoots\": [${roots}]"
    fi
  fi
  json_escape "${base}"
  base_json="${ESCAPED}"
  json_escape "${file}"
  file_json="${ESCAPED}"
  printf '{ "extends": "%s", "files": ["%s"], "include": [], "compilerOptions": { %s } }\n' \
    "${base_json}" "${file_json}" "${options}" > "${out}"
}

# ── Output parsing ──────────────────────────────────────────────────────────────────────

GROUP_CONFIG=""
GROUP_EDITED=""
GROUP_OTHER=""

# Sorts tsc output $1 into config, edited-file and other-file errors, keeping each error's
# indented explanation lines with it. $2 is tsc's working folder, $3 the edited files with a
# newline on each side.
parse_output() {
  local text="$1" cwd="$2" edited="$3" line where current=""
  local re='^(.*)\([0-9]+,[0-9]+\): error TS[0-9]+: ' bare='^error TS[0-9]+: ' more='^[[:space:]]+[^[:space:]]'
  GROUP_CONFIG=""
  GROUP_EDITED=""
  GROUP_OTHER=""
  while IFS= read -r line; do
    if [[ ${line} =~ ${re} ]]; then
      where="${BASH_REMATCH[1]}"
      [[ ${where} == /* ]] || where="${cwd}/${where}"
      canonical "${where}"
      where="${CANONICAL}"
      if [[ ${where} == *.json ]]; then
        current=config
      elif [[ ${edited} == *"${NL}${where}${NL}"* ]]; then
        current=edited
      else
        current=other
      fi
    elif [[ ${line} =~ ${bare} ]]; then
      current=config
    elif [[ -z ${current} || ! ${line} =~ ${more} ]]; then
      current=""
      continue
    fi
    case "${current}" in
      config) GROUP_CONFIG="${GROUP_CONFIG}${line}${NL}" ;;
      edited) GROUP_EDITED="${GROUP_EDITED}${line}${NL}" ;;
      other) GROUP_OTHER="${GROUP_OTHER}${line}${NL}" ;;
      *) ;;
    esac
  done <<< "${text}"
  return 0
}

REPORT=""

# Checks one program, or one file alone, and appends what it finds to REPORT. $1 is what
# program_of found, $2 the edited files with a newline on each side.
check_group() {
  local found="$1" files="$2" config base note="" run_dir strict project file
  local config_errors edited_errors other_errors project_other="" parts=""
  case "${found}" in
    none | uncovered\ *)
      file="${files#"${NL}"}"
      file="${file%"${NL}"}"
      if [[ ${found} == none ]]; then
        base="${STRICTEST}"
        note="No tsconfig.json or jsconfig.json covers ${file}; it was checked alone with the plugin's strictest config."
      else
        base="${found#uncovered }"
        note="${file} is not part of the program of ${base} or its references; it was checked alone on top of that config. Add it to include or files to check it with the rest of the program."
      fi
      config="${WORK}/alone-${RANDOM}-${RANDOM}.json"
      write_alone_config "${config}" "${base}" "${file}"
      ;;
    *) config="${found}" ;;
  esac
  run_dir="$(dirname "${config}")"
  # Both passes write nothing into the project: no emitted files, and the tsbuildinfo of an
  # incremental or composite config goes to WORK (--incremental false fails on composite).
  strict="$(cd "${run_dir}" && "${TSC[@]}" -p "${config}" --pretty false --tsBuildInfoFile "${WORK}/strict-${RANDOM}${RANDOM}.tsbuildinfo" "${STRICT_FLAGS[@]+"${STRICT_FLAGS[@]}"}" 2>&1 || true)"
  parse_output "${strict}" "${run_dir}" "${files}"
  config_errors="${GROUP_CONFIG}"
  edited_errors="${GROUP_EDITED}"
  other_errors="${GROUP_OTHER}"
  if [[ -n ${other_errors} && ${config} == "${found}" ]]; then
    project="$(cd "${run_dir}" && "${TSC[@]}" -p "${config}" --pretty false --noEmit true --tsBuildInfoFile "${WORK}/project-${RANDOM}${RANDOM}.tsbuildinfo" 2>&1 || true)"
    parse_output "${project}" "${run_dir}" "${files}"
    project_other="${GROUP_OTHER}"
  fi
  if [[ -n ${config_errors} ]]; then
    parts="${parts}The TypeScript config (${found#uncovered }) has errors, so tsc could not check the code as configured:${NL}${config_errors}${NL}"
  fi
  if [[ -n ${edited_errors} ]]; then
    parts="${parts}Errors in the edited files under the strictest policy, with the project environment:${NL}${edited_errors}${NL}"
  fi
  if [[ -n ${project_other} ]]; then
    parts="${parts}Errors in other files of the program under the project's own config; this edit may have caused them:${NL}${project_other}${NL}"
  fi
  [[ -z ${parts} ]] && return 0
  [[ -n ${note} ]] && parts="${note}${NL}${NL}${parts}"
  REPORT="${REPORT}${parts}"
}

# ── Changed files ───────────────────────────────────────────────────────────────────────

# Prints the files a Bash command changed inside project $1 in the last $2 seconds.
changed_since() {
  local project="$1" window="$2" ref="${WORK}/since" now when stamp home_real listed rel
  now="$(date +%s)"
  when=$((now - window))
  stamp="$(date -u -r "${when}" +%Y%m%d%H%M.%S 2> /dev/null || date -u -d "@${when}" +%Y%m%d%H%M.%S)"
  TZ=UTC touch -t "${stamp}" "${ref}"
  if git -C "${project}" rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    listed="$(git -C "${project}" ls-files --modified --others --exclude-standard)"
    while IFS= read -r rel; do
      [[ -n ${rel} && -f "${project}/${rel}" && "${project}/${rel}" -nt ${ref} ]] && printf '%s\n' "${project}/${rel}"
    done <<< "${listed}"
    return 0
  fi
  home_real="$(cd "${HOME}" 2> /dev/null && pwd -P || printf '%s' "${HOME}")"
  # A walk of the whole home folder or disk is never worth a hook's budget.
  [[ ${project} == "${home_real}" || ${project} == / ]] && return 0
  find "${project}" \( -name node_modules -o -name .git -o -name dist -o -name build -o -name .cache \
    -o -name .next -o -name .venv -o -name venv -o -name coverage \) -prune -o \
    -type f -newer "${ref}" -print 2> /dev/null | head -n "${MAX_WALK_FILES}"
  return 0
}

# Prints the files the tool call changed, one per line.
candidates() {
  local tool project duration window inner rest item re='^[^"]*"(([^"\\]|\\.)*)"(.*)$'
  json_string tool_name
  tool="${VALUE}"
  case "${tool}" in
    Edit | Write)
      json_string file_path
      to_posix "${VALUE}"
      [[ -n ${POSIX} ]] && printf '%s\n' "${POSIX}"
      return 0
      ;;
    Bash) ;;
    *) return 0 ;;
  esac
  if [[ ${EVENT} =~ \"changedFiles\"[[:space:]]*:[[:space:]]*\[ ]]; then
    inner="$(printf '%s' "${EVENT}" | sed -E -n \
      's/.*"changedFiles"[[:space:]]*:[[:space:]]*\[(([^]"]|"([^"\\]|\\.)*")*)\].*/\1/p')"
    rest="${inner}"
    while [[ ${rest} =~ ${re} ]]; do
      item="${BASH_REMATCH[1]}"
      rest="${BASH_REMATCH[3]}"
      json_unescape "${item}"
      to_posix "${UNESCAPED}"
      printf '%s\n' "${POSIX}"
    done
    return 0
  fi
  project="${CLAUDE_PROJECT_DIR:-}"
  if [[ -z ${project} || ! -d ${project} ]]; then
    json_string cwd
    project="${VALUE}"
  fi
  to_posix "${project}"
  project="${POSIX}"
  [[ -n ${project} && -d ${project} ]] || project="${PWD}"
  project="$(cd "${project}" && pwd -P)"
  json_number duration_ms
  duration="${VALUE}"
  if [[ -n ${duration} ]]; then
    window=$((duration / 1000 + BASH_SLACK_S))
  else
    window="${FALLBACK_WINDOW_S}"
  fi
  changed_since "${project}" "${window}"
}

# ── Output ──────────────────────────────────────────────────────────────────────────────

# Sets BOUNDED to $1, cut under the hook output cap.
BOUNDED=""
bounded() {
  BOUNDED="$1"
  if [[ ${#BOUNDED} -gt ${MAX_REPORT_CHARS} ]]; then
    BOUNDED="${BOUNDED:0:MAX_REPORT_CHARS}${NL}… output cut at ${MAX_REPORT_CHARS} characters"
  fi
}

# Tells the user once per session, and Claude every time, that files $1 went unchecked.
report_unchecked() {
  local files="$1" event session marker_dir marker message="" context names line
  json_string hook_event_name
  event="${VALUE:-PostToolUse}"
  json_string session_id
  session="${VALUE:-unknown}"
  names=""
  while IFS= read -r line; do
    [[ -n ${line} ]] && names="${names:+${names}, }${line}"
  done <<< "${files}"
  context="${PLUGIN}: ${names} not type-checked: no usable TypeScript compiler was found. Do not treat these files as checked."
  marker_dir="${CLAUDE_PLUGIN_DATA:-${TMPDIR:-/tmp}/${PLUGIN}}/notices"
  marker="${marker_dir}/${session//[!A-Za-z0-9_-]/_}"
  if [[ ! -f ${marker} ]]; then
    message="${PLUGIN}: no usable TypeScript compiler was found, so edited files are not type-checked.${NL}Searched:${NL}${SEARCHED:-(no node or tsc in any known folder)${NL}}"
    [[ -n ${SKIPPED} ]] && message="${message}Skipped:${NL}${SKIPPED}"
    message="${message}Requirements: ${README_URL}"
    mkdir -p "${marker_dir}"
    : > "${marker}"
  fi
  json_escape "${event}"
  event="${ESCAPED}"
  json_escape "${context}"
  context="${ESCAPED}"
  if [[ -n ${message} ]]; then
    bounded "${message}"
    json_escape "${BOUNDED}"
    printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}' \
      "${ESCAPED}" "${event}" "${context}"
  else
    printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}' "${event}" "${context}"
  fi
}

# Confirms to the user in one line that files $1 passed.
report_passed() {
  local files="$1" project names="" line
  project="${CLAUDE_PROJECT_DIR:-}"
  if [[ -n ${project} && -d ${project} ]]; then
    project="$(cd "${project}" && pwd -P)"
  fi
  while IFS= read -r line; do
    [[ -n ${line} ]] || continue
    [[ -n ${project} ]] && line="${line#"${project}/"}"
    names="${names:+${names}, }${line}"
  done <<< "${files}"
  json_escape "${PLUGIN}: tsc passed (strictest) · ${names}"
  printf '{"systemMessage":"%s"}' "${ESCAPED}"
}

# ── Main ────────────────────────────────────────────────────────────────────────────────

main() {
  local raw path files="" file keys="" listed key group first
  raw="$(candidates)"
  while IFS= read -r path; do
    [[ -n ${path} && -f ${path} && ${path} =~ ${TS_FILE_PATTERN} ]] || continue
    case "${path}" in
      */node_modules/* | */.venv/* | */venv/* | */site-packages/*) continue ;;
      *) ;;
    esac
    canonical "${path}"
    file="${CANONICAL}"
    [[ ${files} == *"${NL}${file}${NL}"* ]] && continue
    files="${files:-${NL}}${file}${NL}"
  done <<< "${raw}"
  [[ -z ${files} ]] && return 0

  if [[ ! -f ${STRICTEST} ]]; then
    echo "${PLUGIN}: ${STRICTEST} is missing; reinstall the plugin" >&2
    return 1
  fi
  collect_dirs
  find_node
  load_strict_flags
  first="${files#"${NL}"}"
  first="${first%%"${NL}"*}"
  find_tsc "${first}"
  if [[ ${#TSC[@]} -eq 0 ]]; then
    report_unchecked "${files}"
    return 0
  fi

  # One run per program; a file outside every program is checked on its own.
  while IFS= read -r file; do
    [[ -n ${file} ]] || continue
    program_of "${file}"
    case "${PROGRAM}" in
      none | uncovered\ *) check_group "${PROGRAM}" "${NL}${file}${NL}" ;;
      *) keys="${keys}${PROGRAM}"$'\t'"${file}${NL}" ;;
    esac
  done <<< "${files}"
  listed="$(printf '%s' "${keys}" | cut -f1 | sort -u)"
  while IFS= read -r key; do
    [[ -n ${key} ]] || continue
    group="$(printf '%s' "${keys}" | awk -F '\t' -v k="${key}" '$1 == k { print $2 }')"
    check_group "${key}" "${NL}${group}${NL}"
  done <<< "${listed}"

  if [[ -z ${REPORT} ]]; then
    report_passed "${files}"
    return 0
  fi
  bounded "${REPORT}"
  json_escape "TypeScript errors detected after file edit. Fix them before continuing; do not suppress them.${NL}${NL}${BOUNDED}"
  printf '{"decision":"block","reason":"%s"}' "${ESCAPED}"
}

main
