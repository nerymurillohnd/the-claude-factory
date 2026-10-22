#!/usr/bin/env bash
# Post-edit hook of the TypeScript LSP intelligence plugins. Reads one PostToolUse or
# PostToolUseFailure event on stdin and type-checks every TypeScript or JavaScript file the
# tool call changed, with the project's environment and the plugin's strictness:
#
# - Environment (module resolution, paths, jsx, lib, types, include) comes from the
#   project: the nearest tsconfig.json or jsconfig.json above the file, followed through
#   its references to the program that lists the file, then the tsconfig.<name>.json and
#   jsconfig.<name>.json beside it (a tsconfig.tests.json that adds the excluded tests).
# - Strictness comes from STRICT_POLICY below: each option is passed on the command line, so
#   it overrides the project's value, explicit false too, and only to a tsc that knows it.
#   Its checkJs brings the JavaScript files of a program into the check, as allowJs would.
# - A file outside every program is checked alone on top of the nearest config, or with the
#   compiler's own defaults and the strict options without one.
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
# block with onFailure. Every message that reaches Claude ends with one line naming the plugin's
# ts-lifecycle skill, so a hook that checks is never taken for the whole workflow; the
# user-only systemMessage does not carry it. Bash 3.2 or later; no jq, no Python. This file is
# byte-identical in typescript6-lsp-intelligence and typescript7-lsp-intelligence.

set -euo pipefail

readonly MAX_REPORT_CHARS=9000
readonly BASH_SLACK_S=2
readonly FALLBACK_WINDOW_S=30
readonly MAX_WALK_FILES=20000
readonly TS_FILE_PATTERN='\.(ts|tsx|mts|cts|js|jsx|mjs|cjs)$'
readonly NL=$'\n'

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly HOOK_DIR
PLUGIN_ROOT="$(cd "${HOOK_DIR}/.." && pwd -P)"
readonly PLUGIN_ROOT
# The first "name" key is the plugin's own: plugin.json lists it before author.name.
PLUGIN="$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "${PLUGIN_ROOT}/.claude-plugin/plugin.json" \
  | head -n 1 | sed 's/.*:[[:space:]]*"\([^"]*\)"$/\1/')"
readonly PLUGIN
readonly SKILL_HINT="Use the ${PLUGIN}:ts-lifecycle skill and apply all its knowledge when working on TypeScript and JavaScript files."
# A mise shim whose tool is missing would install it; this hook installs nothing.
export MISE_AUTO_INSTALL=false
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

# Sets UTF8 to code point $1 encoded as UTF-8.
UTF8=""
utf8_of() {
  local c="$1" octal
  if ((c < 0x80)); then
    octal="$(printf '\\0%03o' "${c}")"
  elif ((c < 0x800)); then
    octal="$(printf '\\0%03o\\0%03o' $((0xC0 | c >> 6)) $((0x80 | (c & 0x3F))))"
  elif ((c < 0x10000)); then
    octal="$(printf '\\0%03o\\0%03o\\0%03o' $((0xE0 | c >> 12)) $((0x80 | (c >> 6 & 0x3F))) $((0x80 | (c & 0x3F))))"
  else
    octal="$(printf '\\0%03o\\0%03o\\0%03o\\0%03o' $((0xF0 | c >> 18)) $((0x80 | (c >> 12 & 0x3F))) \
      $((0x80 | (c >> 6 & 0x3F))) $((0x80 | (c & 0x3F))))"
  fi
  # The x keeps a trailing newline from being stripped by the command substitution.
  UTF8="$(printf '%bx' "${octal}")"
  UTF8="${UTF8%x}"
}

# Sets UNESCAPED to JSON string body $1 with every escape decoded, \uXXXX and surrogate
# pairs included.
UNESCAPED=""
json_unescape() {
  local s="$1" out="" rest c hex low code
  while [[ ${s} == *\\* ]]; do
    out="${out}${s%%\\*}"
    rest="${s#*\\}"
    c="${rest:0:1}"
    s="${rest:1}"
    case "${c}" in
      n) out="${out}${NL}" ;;
      t) out="${out}"$'\t' ;;
      r) out="${out}"$'\r' ;;
      b) out="${out}"$'\b' ;;
      f) out="${out}"$'\f' ;;
      u)
        hex="${s:0:4}"
        s="${s:4}"
        [[ ${hex} =~ ^[0-9A-Fa-f]{4}$ ]] || hex=FFFD
        code=$((16#${hex}))
        if ((code >= 0xD800 && code < 0xDC00)) && [[ ${s:0:2} == '\u' && ${s:2:4} =~ ^[0-9A-Fa-f]{4}$ ]]; then
          low=$((16#${s:2:4}))
          if ((low >= 0xDC00 && low < 0xE000)); then
            code=$((0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)))
            s="${s:6}"
          fi
        fi
        utf8_of "${code}"
        out="${out}${UTF8}"
        ;;
      *) out="${out}${c}" ;;
    esac
  done
  UNESCAPED="${out}${s}"
}

# A JSON string token.
readonly JSON_STR='"([^"\\]|\\.)*"'

# Sets VALUE to the first string value of key $1 anywhere in the event, empty when absent.
VALUE=""
json_string() {
  local raw
  raw="$(printf '%s' "${EVENT}" | sed -E -n \
    "s/^[^\"]*(\"([^\"\\\\]|\\\\.)*\"[^\"]*)*\"$1\"[[:space:]]*:[[:space:]]*\"(([^\"\\\\]|\\\\.)*)\".*/\\3/p")"
  json_unescape "${raw}"
  VALUE="${UNESCAPED}"
}

# Sets VALUE to string key $2 of the flat top-level object $1 (tool_input), empty when absent.
json_member() {
  local raw
  raw="$(printf '%s' "${EVENT}" | sed -E -n \
    "s/.*\"$1\"[[:space:]]*:[[:space:]]*\\{([^\"{}]|${JSON_STR})*\"$2\"[[:space:]]*:[[:space:]]*\"(([^\"\\\\]|\\\\.)*)\".*/\\3/p")"
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
  s="$(printf '%s' "$1" | LC_ALL=C tr -d '\000-\010\013-\037')"
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

# Sets MIXED to $1 as a Windows compiler reads it (C:/x/y) under Git Bash; other paths stay.
MIXED=""
mixed_path() {
  MIXED="$1"
  if [[ $1 == /* ]] && command -v cygpath > /dev/null 2>&1; then
    MIXED="$(cygpath -m "$1")"
  fi
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

# Sets TSC, TSC_ID and TSC_VERSION from compiler identity $1 ("native|<path>|<version>" or
# "node|<path>|<version>"); TSC is empty for an empty identity.
TSC=()
TSC_ID=""
TSC_VERSION=""
set_tsc() {
  local kind path rest
  TSC=()
  TSC_ID="$1"
  TSC_VERSION=""
  [[ -n ${TSC_ID} ]] || return 0
  kind="${TSC_ID%%|*}"
  rest="${TSC_ID#*|}"
  path="${rest%%|*}"
  TSC_VERSION="${rest#*|}"
  strict_flags_for "${TSC_VERSION}"
  if [[ ${kind} == native ]]; then
    TSC=("${path}")
  else
    TSC=(env "PATH=${NODE_DIR}:${PATH}" "${path}")
  fi
}

# Sets FOUND_ID to the identity of tsc candidate $1, empty when it cannot run. Each candidate
# is probed once per run.
FOUND_ID=""
PROBED="${NL}"
use_tsc() {
  local tsc="$1" package="" version line
  FOUND_ID=""
  if [[ ${PROBED} == *"${NL}${tsc}"$'\t'* ]]; then
    line="${PROBED#*"${NL}${tsc}"$'\t'}"
    FOUND_ID="${line%%"${NL}"*}"
    return 0
  fi
  SEARCHED="${SEARCHED}${tsc}${NL}"
  resolve_link "${tsc}"
  case "${CANONICAL}" in
    */typescript/bin/tsc) package="${CANONICAL%/bin/tsc}" ;;
    *) ;;
  esac
  if [[ ${NATIVE} == yes && -n ${package} ]]; then
    native_compiler "${package}"
    if [[ -n ${NATIVE_TSC} ]]; then
      version="$("${NATIVE_TSC}" --version 2> /dev/null || true)"
      [[ ${version} == Version* ]] && FOUND_ID="native|${NATIVE_TSC}|${version#Version }"
    fi
  fi
  if [[ -z ${FOUND_ID} && -z ${NODE_DIR} ]]; then
    SKIPPED="${SKIPPED}${tsc} (no Node.js ${NODE_MIN} or later to run it)${NL}"
  elif [[ -z ${FOUND_ID} ]]; then
    version="$(PATH="${NODE_DIR}:${PATH}" "${tsc}" --version 2> /dev/null || true)"
    if [[ ${version} == Version* ]]; then
      FOUND_ID="node|${tsc}|${version#Version }"
    else
      SKIPPED="${SKIPPED}${tsc} (did not run with ${NODE_DIR}/node)${NL}"
    fi
  fi
  PROBED="${PROBED}${tsc}"$'\t'"${FOUND_ID}${NL}"
}

# Sets TSC for file $1: the project's node_modules above it first, then a global tsc. Each
# file gets its own, so files of different packages run their own compilers.
find_tsc() {
  local dir candidate
  set_tsc ""
  dir="$(dirname "$1")"
  while :; do
    for candidate in "${dir}/node_modules/.bin/tsc" "${dir}/node_modules/typescript/bin/tsc"; do
      [[ -f ${candidate} ]] || continue
      use_tsc "${candidate}"
      if [[ -n ${FOUND_ID} ]]; then
        set_tsc "${FOUND_ID}"
        return 0
      fi
    done
    [[ ${dir} == / || ${dir} == . ]] && break
    dir="$(dirname "${dir}")"
  done
  for dir in "${DIRS[@]+"${DIRS[@]}"}"; do
    candidate="${dir}/tsc"
    [[ -f ${candidate} ]] || continue
    use_tsc "${candidate}"
    if [[ -n ${FOUND_ID} ]]; then
      set_tsc "${FOUND_ID}"
      return 0
    fi
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
# JavaScript counts as checkJs admits it: the nearest config, then its references, then the
# sibling tsconfig.<name>.json and jsconfig.<name>.json files beside it, sorted by name. Sets
# it to "uncovered <nearest>" when no program does, or to "none" without a config. A nearest
# config tsc cannot read is used as is; a sibling tsc cannot read is skipped.
PROGRAM=""
program_of() {
  local file="$1" nearest queue config listed sibling seen="${NL}"
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
  # A sibling is a program of its own that the nearest config does not reference.
  for sibling in "$(dirname "${nearest}")"/tsconfig.*.json "$(dirname "${nearest}")"/jsconfig.*.json; do
    [[ -f ${sibling} ]] || continue
    canonical "${sibling}"
    config="${CANONICAL}"
    [[ ${seen} == *"${NL}${config}${NL}"* ]] && continue
    seen="${seen}${config}${NL}"
    listed="$(cd "$(dirname "${config}")" && "${TSC[@]}" --listFilesOnly -p "${config}" "${STRICT_FLAGS[@]+"${STRICT_FLAGS[@]}"}" 2>&1 || true)"
    [[ ${listed} == *"error TS"* ]] && continue
    if [[ "${NL}${listed}${NL}" == *"${NL}${file}${NL}"* ]]; then
      PROGRAM="${config}"
      return 0
    fi
  done
  PROGRAM="uncovered ${nearest}"
}

# The strictest policy: one option per line, with the value the edited files are held to and
# the TypeScript version that introduced it (0 for options older than TypeScript 4.0, which no
# compiler this hook runs lacks). Only options that hold in any project: nothing of the
# environment (target, module, moduleResolution, lib, types, paths), which stays the project's.
# skills/ts-lifecycle/scripts/run-fixtures.sh holds the same block; a test keeps them equal.
readonly STRICT_POLICY="strict true 0
noImplicitAny true 0
strictNullChecks true 0
strictFunctionTypes true 0
strictBindCallApply true 0
strictPropertyInitialization true 0
strictBuiltinIteratorReturn true 5.6.0
noImplicitThis true 0
useUnknownInCatchVariables true 4.4.0
alwaysStrict true 0
exactOptionalPropertyTypes true 4.4.0
noUncheckedIndexedAccess true 4.1.0
noPropertyAccessFromIndexSignature true 4.2.0
noImplicitReturns true 0
noImplicitOverride true 4.3.0
noFallthroughCasesInSwitch true 0
noUnusedLocals true 0
noUnusedParameters true 0
allowUnusedLabels false 0
allowUnreachableCode false 0
allowJs true 0
checkJs true 0
skipLibCheck true 0"
# The hook's own guards, in the same form: never emit, and never let a project's noCheck
# switch the check off. A tsc without noCheck (before 5.6) has nothing to switch off.
readonly GUARD_POLICY="noEmit true 0
noCheck false 5.6.0"

# Sets STRICT_FLAGS to the policy and guard options that tsc version $1 knows, as
# command-line flags. Each strict option left out goes into NOT_APPLIED, once per version.
STRICT_FLAGS=()
NOT_APPLIED=""
strict_flags_for() {
  local version="$1" name value since left=""
  STRICT_FLAGS=()
  while IFS=' ' read -r name value since; do
    [[ -n ${name} ]] || continue
    if [[ ${since} != 0 ]]; then
      version_at_least "${version}" "${since}"
      if [[ ${AT_LEAST} == no ]]; then
        left="${left:+${left}, }${name} (TypeScript ${since} or later)"
        continue
      fi
    fi
    STRICT_FLAGS+=("--${name}" "${value}")
  done <<< "${STRICT_POLICY}"
  while IFS=' ' read -r name value since; do
    [[ -n ${name} ]] || continue
    if [[ ${since} != 0 ]]; then
      version_at_least "${version}" "${since}"
      [[ ${AT_LEAST} == no ]] && continue
    fi
    STRICT_FLAGS+=("--${name}" "${value}")
  done <<< "${GUARD_POLICY}"
  if [[ -n ${left} && ${NOT_APPLIED} != *"tsc ${version}: "* ]]; then
    NOT_APPLIED="${NOT_APPLIED}tsc ${version}: ${left}${NL}"
  fi
}

# Writes config $1 that checks file $3 alone on top of base config $2.
write_alone_config() {
  local out="$1" base="$2" file="$3" options="" roots="" dir types shown base_json file_json root
  # A config in a temporary folder would not find the project's @types: give it the
  # folders tsc searches by default, unless the base sets typeRoots itself.
  if [[ -n ${base} ]]; then
    shown="$(cd "$(dirname "${base}")" && "${TSC[@]}" --showConfig -p "${base}" 2> /dev/null || true)"
    if [[ ${shown} != *'"typeRoots"'* ]]; then
      dir="$(dirname "${base}")"
      while :; do
        types="${dir}/node_modules/@types"
        if [[ -d ${types} ]]; then
          mixed_path "${types}"
          json_escape "${MIXED}"
          roots="${roots:+${roots}, }\"${ESCAPED}\""
        fi
        [[ ${dir} == / || ${dir} == . ]] && break
        dir="$(dirname "${dir}")"
      done
      [[ -n ${roots} ]] && options="${options:+${options}, }\"typeRoots\": [${roots}]"
    fi
  fi
  # The config lives in a temporary folder, which TypeScript 6 takes as the default rootDir,
  # and composite requires every imported file in the files list: neither fits one file.
  mixed_path "${file}"
  case "${MIXED}" in
    [A-Za-z]:/*) root="${MIXED:0:3}" ;;
    *) root=/ ;;
  esac
  options="${options:+${options}, }\"composite\": false, \"rootDir\": \"${root}\""
  base_json=""
  if [[ -n ${base} ]]; then
    mixed_path "${base}"
    json_escape "${MIXED}"
    base_json="\"extends\": \"${ESCAPED}\", "
  fi
  mixed_path "${file}"
  json_escape "${MIXED}"
  file_json="${ESCAPED}"
  printf '{ %s"files": ["%s"], "include": [], "compilerOptions": { %s } }\n' \
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
      to_posix "${where}"
      where="${POSIX}"
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
IGNORED=0

# Sets ERRORS to the number of error lines in tsc output $1.
ERRORS=0
count_errors() {
  local line
  ERRORS=0
  while IFS= read -r line; do
    [[ ${line} == *"error TS"* ]] && ERRORS=$((ERRORS + 1))
  done <<< "$1"
  return 0
}

# Sets FIRST_LINES to the first 20 lines of $1, or "(no output)".
FIRST_LINES=""
first_lines() {
  FIRST_LINES="$(printf '%s\n' "$1" | head -n 20)"
  [[ -n ${FIRST_LINES} ]] || FIRST_LINES="(no output)"
}

# Checks one program, or one file alone, and appends what it finds to REPORT. $1 is what
# program_of found, $2 the edited files with a newline on each side. A run that exits
# non-zero without a TypeScript error (a crash, a killed process, an unknown output format)
# is reported as not checked, never as a pass.
check_group() {
  local found="$1" files="$2" config base note="" run_dir strict project file status=0
  local config_errors edited_errors other_errors project_other="" parts="" strict_count
  case "${found}" in
    none | uncovered\ *)
      file="${files#"${NL}"}"
      file="${file%"${NL}"}"
      if [[ ${found} == none ]]; then
        base=""
        note="No tsconfig.json or jsconfig.json covers ${file}; it was checked alone with the compiler's defaults and the strictest options."
      else
        base="${found#uncovered }"
        note="${file} is not part of the program of ${base}, its references or the tsconfig.<name>.json and jsconfig.<name>.json beside it; it was checked alone on top of that config. Add it to include or files to check it with the rest of the program."
      fi
      config="${WORK}/alone-${RANDOM}-${RANDOM}.json"
      write_alone_config "${config}" "${base}" "${file}"
      ;;
    *) config="${found}" ;;
  esac
  run_dir="$(dirname "${config}")"
  # Both passes write nothing into the project: the policy's noEmit, and the tsbuildinfo of an
  # incremental or composite config goes to WORK (--incremental false fails on composite).
  strict="$(cd "${run_dir}" && "${TSC[@]}" -p "${config}" --pretty false --tsBuildInfoFile "${WORK}/strict-${RANDOM}${RANDOM}.tsbuildinfo" "${STRICT_FLAGS[@]+"${STRICT_FLAGS[@]}"}" 2>&1)" || status=$?
  parse_output "${strict}" "${run_dir}" "${files}"
  config_errors="${GROUP_CONFIG}"
  edited_errors="${GROUP_EDITED}"
  other_errors="${GROUP_OTHER}"
  if [[ ${status} -ne 0 && -z ${config_errors}${edited_errors}${other_errors} ]]; then
    first_lines "${strict}"
    parts="tsc ${TSC_VERSION} exited with status ${status} without reporting a TypeScript error, so these files were not checked:${files}Its output:${NL}${FIRST_LINES}${NL}${NL}"
  fi
  if [[ -n ${other_errors} && ${config} == "${found}" ]]; then
    status=0
    project="$(cd "${run_dir}" && "${TSC[@]}" -p "${config}" --pretty false --noEmit true --tsBuildInfoFile "${WORK}/project-${RANDOM}${RANDOM}.tsbuildinfo" 2>&1)" || status=$?
    parse_output "${project}" "${run_dir}" "${files}"
    project_other="${GROUP_OTHER}"
    if [[ ${status} -ne 0 && -z ${GROUP_CONFIG}${GROUP_EDITED}${GROUP_OTHER} ]]; then
      first_lines "${project}"
      parts="${parts}The strictest run found errors in other files, but the check under the project's own config exited with status ${status} without a TypeScript error, so whether they are the project's own is unknown:${NL}${other_errors}Its output:${NL}${FIRST_LINES}${NL}${NL}"
    else
      count_errors "${other_errors}"
      strict_count="${ERRORS}"
      count_errors "${project_other}"
      ((strict_count > ERRORS)) && IGNORED=$((IGNORED + strict_count - ERRORS))
    fi
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
  local project="$1" window="$2" ref="${WORK}/since" now when stamp home_real rel
  now="$(date +%s)"
  when=$((now - window))
  stamp="$(date -u -r "${when}" +%Y%m%d%H%M.%S 2> /dev/null || date -u -d "@${when}" +%Y%m%d%H%M.%S)"
  TZ=UTC touch -t "${stamp}" "${ref}"
  if git -C "${project}" rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    # NUL-separated: without -z git quotes names with non-ASCII bytes ("caf\303\251.ts"),
    # and the quoted form is no file. Staged files count too: a command that runs git add
    # leaves nothing --modified.
    {
      git -C "${project}" ls-files -z --modified --others --exclude-standard || true
      git -C "${project}" diff -z --cached --name-only --relative 2> /dev/null || true
    } > "${WORK}/listed"
    while IFS= read -r -d '' rel; do
      [[ -n ${rel} && -f "${project}/${rel}" && "${project}/${rel}" -nt ${ref} ]] && printf '%s\n' "${project}/${rel}"
    done < "${WORK}/listed"
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
      json_member tool_input file_path
      to_posix "${VALUE}"
      [[ -n ${POSIX} ]] && printf '%s\n' "${POSIX}"
      return 0
      ;;
    Bash | PowerShell) ;;
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
    # An incomplete or skipped list is a floor, not the answer: add the recent changes.
    [[ ${EVENT} =~ \"(unavailable|skipped)\"[[:space:]]*:[[:space:]]*true ]] || return 0
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

# Sets BOUNDED to $1, cut under the hook output cap less $2 characters kept in reserve.
BOUNDED=""
bounded() {
  local limit=$((MAX_REPORT_CHARS - ${2:-0}))
  BOUNDED="$1"
  if [[ ${#BOUNDED} -gt ${limit} ]]; then
    BOUNDED="${BOUNDED:0:limit}${NL}… output cut at ${MAX_REPORT_CHARS} characters"
  fi
}

# Sets BOUNDED to $1, cut under the cap and followed by the skill hint on its own line.
hinted() {
  bounded "$1" $((${#NL} + ${#SKILL_HINT}))
  BOUNDED="${BOUNDED}${NL}${SKILL_HINT}"
}

# Sets NAMES to the files in $1 (one per line), comma-separated and relative to the project.
NAMES=""
names_of() {
  local project="${CLAUDE_PROJECT_DIR:-}" line
  NAMES=""
  if [[ -n ${project} && -d ${project} ]]; then
    project="$(cd "${project}" && pwd -P)"
  fi
  while IFS= read -r line; do
    [[ -n ${line} ]] || continue
    [[ -n ${project} ]] && line="${line#"${project}/"}"
    NAMES="${NAMES:+${NAMES}, }${line}"
  done <<< "$1"
  return 0
}

# Sets NOTICE to the once-per-session message about a missing compiler, empty after the first.
NOTICE=""
compiler_notice() {
  local session marker_dir marker
  NOTICE=""
  json_string session_id
  session="${VALUE:-unknown}"
  marker_dir="${CLAUDE_PLUGIN_DATA:-${TMPDIR:-/tmp}/${PLUGIN}}/notices"
  marker="${marker_dir}/${session//[!A-Za-z0-9_-]/_}"
  [[ -f ${marker} ]] && return 0
  NOTICE="${PLUGIN}: no usable TypeScript compiler was found, so edited files are not type-checked.${NL}Searched:${NL}${SEARCHED:-(no node or tsc in any known folder)${NL}}"
  [[ -n ${SKIPPED} ]] && NOTICE="${NOTICE}Skipped:${NL}${SKIPPED}"
  NOTICE="${NOTICE}Requirements: ${README_URL}"
  mkdir -p "${marker_dir}"
  : > "${marker}"
}

# Prints the one JSON object of this run. $1 is the passed files, $2 the files without a
# compiler, $3 the edited files left out (with the reason on each line), $4 the compilers used.
# Findings block on PostToolUse; PostToolUseFailure takes only additionalContext, so there
# they go to Claude that way.
emit() {
  local passed="$1" unchecked="$2" left_out="$3" used="$4" event context="" message="" fields=""
  json_string hook_event_name
  event="${VALUE:-PostToolUse}"
  if [[ -n ${unchecked} ]]; then
    names_of "${unchecked}"
    context="${PLUGIN}: ${NAMES} not type-checked: no usable TypeScript compiler was found. Do not treat these files as checked.${NL}"
    compiler_notice
    message="${NOTICE}"
  fi
  if [[ -n ${left_out} ]]; then
    context="${context}${PLUGIN}: these edited files were not type-checked:${NL}${left_out}"
  fi
  if [[ -n ${NOT_APPLIED} ]]; then
    context="${context}${PLUGIN}: these strictest options were not applied, because the project's tsc is too old to know them:${NL}${NOT_APPLIED}"
  fi
  if [[ -n ${REPORT} ]]; then
    hinted "TypeScript errors detected after file edit. Fix them before continuing; do not suppress them.${NL}${NL}${REPORT}${context:+${NL}${context}}"
    json_escape "${BOUNDED}"
    if [[ ${event} == PostToolUseFailure ]]; then
      fields="\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUseFailure\",\"additionalContext\":\"${ESCAPED}\"}"
    else
      fields="\"decision\":\"block\",\"reason\":\"${ESCAPED}\""
    fi
  else
    if [[ -n ${passed} ]]; then
      names_of "${passed}"
      message="${message:+${message}${NL}}${PLUGIN}: tsc ${used} · the edited files pass the strictest policy"
      ((IGNORED > 0)) && message="${message}; strictest-only errors in other files not counted, since the project's own config accepts them: ${IGNORED}"
      message="${message} · ${NAMES}"
      [[ -n ${SKIPPED} ]] && message="${message}${NL}Compilers skipped first:${NL}${SKIPPED%"${NL}"}"
    fi
    if [[ -n ${context} ]]; then
      json_escape "${event}"
      fields="\"hookSpecificOutput\":{\"hookEventName\":\"${ESCAPED}\""
      hinted "${context}"
      json_escape "${BOUNDED}"
      fields="${fields},\"additionalContext\":\"${ESCAPED}\"}"
    fi
  fi
  if [[ -n ${message} ]]; then
    bounded "${message}"
    json_escape "${BOUNDED}"
    fields="\"systemMessage\":\"${ESCAPED}\"${fields:+,${fields}}"
  fi
  [[ -n ${fields} ]] && printf '{%s}' "${fields}"
  return 0
}

# ── Main ────────────────────────────────────────────────────────────────────────────────

main() {
  local raw path files="" file keys="" listed key group passed="" unchecked="" left_out="" used=""
  json_string tool_name
  if [[ -z ${VALUE} ]]; then
    echo "${PLUGIN}: the hook event has no tool_name; it is not the JSON Claude Code sends" >&2
    echo "${SKILL_HINT}" >&2
    return 1
  fi
  raw="$(candidates)"
  while IFS= read -r path; do
    [[ -n ${path} && ${path} =~ ${TS_FILE_PATTERN} ]] || continue
    case "${path}" in
      */node_modules/* | */.venv/* | */venv/* | */site-packages/*)
        left_out="${left_out}${path} (dependency folder; the hook checks project code only)${NL}"
        continue
        ;;
      *) ;;
    esac
    if [[ ! -f ${path} ]]; then
      # A Bash command can delete a file; an edit tool cannot leave one missing.
      json_string tool_name
      [[ ${VALUE} == Edit || ${VALUE} == Write ]] && left_out="${left_out}${path} (not found on disk)${NL}"
      continue
    fi
    canonical "${path}"
    file="${CANONICAL}"
    [[ ${files} == *"${NL}${file}${NL}"* ]] && continue
    files="${files:-${NL}}${file}${NL}"
  done <<< "${raw}"
  if [[ -z ${files} ]]; then
    emit "" "" "${left_out}" ""
    return 0
  fi

  collect_dirs
  find_node

  # One run per program and compiler; a file outside every program is checked on its own.
  while IFS= read -r file; do
    [[ -n ${file} ]] || continue
    find_tsc "${file}"
    if [[ ${#TSC[@]} -eq 0 ]]; then
      unchecked="${unchecked}${file}${NL}"
      continue
    fi
    [[ ${NL}${used} == *"${NL}${TSC_VERSION}${NL}"* ]] || used="${used}${TSC_VERSION}${NL}"
    passed="${passed}${file}${NL}"
    program_of "${file}"
    case "${PROGRAM}" in
      none | uncovered\ *) check_group "${PROGRAM}" "${NL}${file}${NL}" ;;
      *) keys="${keys}${TSC_ID}"$'\t'"${PROGRAM}"$'\t'"${file}${NL}" ;;
    esac
  done <<< "${files}"
  listed="$(printf '%s' "${keys}" | cut -f1,2 | sort -u)"
  while IFS= read -r key; do
    [[ -n ${key} ]] || continue
    group="$(printf '%s' "${keys}" | awk -F '\t' -v k="${key}" '$1 "\t" $2 == k { print $3 }')"
    set_tsc "${key%%$'\t'*}"
    check_group "${key#*$'\t'}" "${NL}${group}${NL}"
  done <<< "${listed}"

  used="${used%"${NL}"}"
  emit "${passed}" "${unchecked}" "${left_out}" "${used//${NL}/, }"
}

main
