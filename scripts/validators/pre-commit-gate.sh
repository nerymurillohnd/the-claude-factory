#!/usr/bin/env bash
# The Git pre-commit gate: runs only on the files staged for this commit, with the project's own
# tools and configuration. .githooks/pre-commit runs it; `git commit --no-verify` (-n) skips it,
# as Git documents for every pre-commit hook.
#
# By staged file type, in this order:
#   .ts .mjs .md .json   Biome: lint and format fixes (biome check --write), then biome check
#   .py .pyi             Ruff: lint fixes and format (ruff check --fix, ruff format), then
#                        ruff check and ruff format --check; then basedpyright
#   .sh                  shfmt -w, then shellcheck
#   .ts .mjs             tsc --noEmit; a mod's .ts file without its generated tsconfig.json is
#                        named as not type-checked, without blocking
#   agent .md            agent-headings (no Markdown heading in a subagent's body), for the .md
#                        files under plugins/*/agents/ and .claude/agents/
# The configuration is pyproject.toml (Ruff, basedpyright), biome.jsonc, tsconfig.json,
# .editorconfig (shfmt), .shellcheckrc and SHELLCHECK_OPTS.
#
# Fixes are written to the files and staged again, so the commit holds them. A staged file with
# unstaged changes on top is refused first: staging the fix would stage those changes too.
# Every check runs, each failure is reported, and the gate exits 1 if any failed. A tool it needs
# and can't find blocks the commit. Written for bash 3.2, the bash macOS ships: no mapfile, no
# associative arrays, and no "${empty[@]}" under set -u.
set -Eeuo pipefail
trap 'exit 1' ERR

# The gate's own tree, found with builtins only: the tool check below must be able to report a
# missing tool, so nothing runs before it that needs one.
gate_dir="${BASH_SOURCE[0]%/*}"
if [[ ${gate_dir} == "${BASH_SOURCE[0]}" ]]; then
  gate_dir="."
fi
gate_root="$(cd "${gate_dir}/../.." && pwd)"
root="$(git rev-parse --show-toplevel)"
cd "${root}"

failed=""
fail() {
  printf 'pre-commit: %s failed\n' "$1" >&2
  failed="${failed} $1;"
}

scratch="$(git rev-parse --absolute-git-dir)/pre-commit-gate"
rm -rf "${scratch}"
mkdir -p "${scratch}"
trap 'rm -rf "${scratch}"' EXIT

# The staged files, as Git records them: Added, Copied, Modified or Renamed, NUL-separated so any
# file name survives (git-diff --cached --name-only --diff-filter=ACMR -z).
git diff --cached --name-only --diff-filter=ACMR -z > "${scratch}/staged"
biome_files=()
ts_files=()
py_files=()
sh_files=()
agent_files=()
partial=()
while IFS= read -r -d '' file; do
  case "${file}" in
    *.ts | *.mjs) biome_files+=("${file}") ts_files+=("${file}") ;;
    *.md | *.json) biome_files+=("${file}") ;;
    *.py | *.pyi) py_files+=("${file}") ;;
    *.sh) sh_files+=("${file}") ;;
    *) continue ;;
  esac
  # A subagent: an .md file under a plugin's agents/ or .claude/agents/, nested folders included,
  # as agent-headings discovers them. A case pattern's * also matches /, so a regex instead.
  if [[ ${file} =~ ^(plugins/[^/]+|\.claude)/agents/.+\.md$ ]]; then agent_files+=("${file}"); fi
  git diff --quiet -- "${file}" || partial+=("${file}")
done < "${scratch}/staged"

if ((${#partial[@]} > 0)); then
  {
    echo "pre-commit: these staged files have unstaged changes. The gate stages its fixes, which"
    echo "would stage those changes too. Stage them whole (git add) or stash the rest"
    echo "(git stash --keep-index):"
    printf '  %s\n' "${partial[@]}"
  } >&2
  exit 1
fi

# A tool is the repository's own copy (node_modules/.bin) or one on PATH (npm run setup installs
# them all). find_tool sets the variable named by $1 to its path, or to nothing and reports it
# missing: a missing tool blocks the commit.
find_tool() {
  local var="$1" tool="$2" found=""
  if [[ -x "node_modules/.bin/${tool}" ]]; then
    found="node_modules/.bin/${tool}"
  elif command -v "${tool}" > /dev/null 2>&1; then
    found="$(command -v "${tool}")"
  else
    printf 'pre-commit: %s is not installed, so its check can not run; run npm run setup.\n' \
      "${tool}" >&2
    fail "${tool}"
  fi
  printf -v "${var}" '%s' "${found}"
}

run_tool() {
  # run_tool <label> <command...>: run one check and record its failure under its label.
  local label="$1"
  shift
  printf '== pre-commit: %s\n' "${label}"
  "$@" || fail "${label}"
}

fix() {
  # fix <label> <command...>: apply one tool's fixes. What a fix can't repair is reported by the
  # check that follows it, so the fix's own exit status is not a verdict.
  local label="$1"
  shift
  printf '== pre-commit: %s\n' "${label}"
  if ! "$@"; then
    printf 'pre-commit: %s left findings it could not fix; the check below reports them.\n' \
      "${label}"
  fi
}

restage() {
  # restage <file...>: stage again each file a fix changed, so the commit holds the fix.
  local file
  for file in "$@"; do
    if ! git diff --quiet -- "${file}"; then
      git add -- "${file}"
      printf 'pre-commit: staged the fixes in %s\n' "${file}"
    fi
  done
}

if ((${#biome_files[@]} > 0)); then
  find_tool biome biome
  if [[ -n ${biome} ]]; then
    biome_args=(--files-ignore-unknown=true --no-errors-on-unmatched --error-on-warnings
      --max-diagnostics=none)
    fix "biome lint and format" "${biome}" check --write "${biome_args[@]}" "${biome_files[@]}"
    restage "${biome_files[@]}"
    run_tool "biome check" "${biome}" check "${biome_args[@]}" "${biome_files[@]}"
  fi
fi

if ((${#py_files[@]} > 0)); then
  find_tool ruff ruff
  if [[ -n ${ruff} ]]; then
    fix "ruff lint fixes" "${ruff}" check --fix --force-exclude "${py_files[@]}"
    fix "ruff format" "${ruff}" format --force-exclude "${py_files[@]}"
    restage "${py_files[@]}"
    run_tool "ruff check" "${ruff}" check --force-exclude "${py_files[@]}"
    run_tool "ruff format --check" "${ruff}" format --check --force-exclude "${py_files[@]}"
  fi
  find_tool basedpyright basedpyright
  if [[ -n ${basedpyright} ]]; then
    # Files given on the command line replace pyproject.toml's include list; the rest of
    # [tool.basedpyright] still applies, executionEnvironments included.
    run_tool basedpyright "${basedpyright}" "${py_files[@]}"
  fi
fi

if ((${#sh_files[@]} > 0)); then
  find_tool shfmt shfmt
  if [[ -n ${shfmt} ]]; then
    run_tool "shfmt -w" "${shfmt}" -w "${sh_files[@]}"
    restage "${sh_files[@]}"
  fi
  find_tool shellcheck shellcheck
  if [[ -n ${shellcheck} ]]; then
    # ShellCheck reads .shellcheckrc and adds SHELLCHECK_OPTS from the environment itself; -S style
    # and -a have no .shellcheckrc key, so they are passed as npm run lint:shell does.
    run_tool shellcheck "${shellcheck}" -S style -a "${sh_files[@]}"
  fi
fi

if ((${#agent_files[@]} > 0)); then
  find_tool uv uv
  if [[ -n ${uv} ]]; then
    # The validator from the gate's own tree, so the gate and its validator always match: -P keeps
    # the committed tree's folder off the import path, and PYTHONPATH puts the gate's tree on it.
    run_tool agent-headings env "PYTHONPATH=${gate_root}" "${uv}" run --quiet python -P \
      -m scripts.checks.agent_headings.cli "${agent_files[@]}"
  fi
fi

if ((${#ts_files[@]} > 0)); then
  find_tool tsc tsc
  find_tool node node
  if [[ -n ${tsc} && -n ${node} ]]; then
    # tsc ignores tsconfig.json when it is given files, and TypeScript 6 makes that an error
    # (TS5112). So each group of staged files gets a temporary config that extends its project's
    # tsconfig and lists only those files: the project's options apply, and only they are checked.
    # It lives in the Git directory, inside the work tree, so node_modules/@types stays visible.
    project_files="$("${tsc}" -p tsconfig.json --listFilesOnly)"
    root_group=()
    unchecked=()
    plugins=""
    for file in "${ts_files[@]}"; do
      if grep -Fxq "${root}/${file}" <<< "${project_files}"; then
        root_group+=("${root}/${file}")
        continue
      fi
      plugin="${file#plugins/}"
      plugin="${plugin%%/*}"
      if [[ ${file} == plugins/*/* && -f "plugins/${plugin}/tsconfig.json" ]]; then
        [[ " ${plugins} " == *" ${plugin} "* ]] || plugins="${plugins} ${plugin}"
      else
        unchecked+=("${file}")
      fi
    done
    write_config() {
      # write_config <config> <extends> <file...>: JSON written by node, so any path is escaped.
      "${node}" -e 'const [out, base, ...files] = process.argv.slice(1);
        require("node:fs").writeFileSync(out, JSON.stringify({ extends: base, include: [], files }));' \
        "$@"
    }
    if ((${#root_group[@]} > 0)); then
      write_config "${scratch}/root.json" "${root}/tsconfig.json" "${root_group[@]}"
      run_tool "tsc --noEmit" "${tsc}" -p "${scratch}/root.json" --noEmit
    fi
    for plugin in ${plugins}; do
      group=()
      for file in "${ts_files[@]}"; do
        [[ ${file} == "plugins/${plugin}/"* ]] && group+=("${root}/${file}")
      done
      write_config "${scratch}/${plugin}.json" "${root}/plugins/${plugin}/tsconfig.json" "${group[@]}"
      run_tool "tsc --noEmit" "${tsc}" -p "${scratch}/${plugin}.json" --noEmit
    done
    if ((${#unchecked[@]} > 0)); then
      # A mod's types and tsconfig.json are generated by Claude Code when it loads the mod from
      # --plugin-dir in an interactive session, and are git-ignored; without them tsc can't
      # resolve the mod's claude-code imports. These files are named, and the commit goes on.
      {
        echo "pre-commit: not type-checked: no tsconfig.json covers these files. For a mod, load it"
        echo "once with claude --plugin-dir plugins/<name> to generate its tsconfig.json:"
        printf '  %s\n' "${unchecked[@]}"
      } >&2
    fi
  fi
fi

if [[ -n ${failed} ]]; then
  {
    echo
    echo "pre-commit: the commit is blocked. Failed:${failed}"
    echo "Fix each finding, stage the fixes, and commit again."
  } >&2
  exit 1
fi
