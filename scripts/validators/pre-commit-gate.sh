#!/usr/bin/env bash
# The Git pre-commit gate: checks only the files staged for this commit, with the project's own
# tools and configuration, and blocks the commit when any of them fails. .githooks/pre-commit runs
# it; `git commit --no-verify` (-n) skips it, as Git documents for every pre-commit hook.
#
# What it checks, by staged file type:
#   .ts .tsx .mjs .md .json   Biome (biome.jsonc), formatting and lint
#   .ts .tsx .mjs             tsc --noEmit with the root tsconfig.json, or a mod's generated one
#   .py .pyi             ruff check, ruff format --check --diff, basedpyright (pyproject.toml)
#   shell scripts        shfmt -d (.editorconfig), shellcheck (.shellcheckrc, SHELLCHECK_OPTS):
#                        .sh files, and any file shfmt -f finds by its shebang, such as a Git hook
# Other types, and deleted files, are not checked here; Validate's Checks job still checks them.
#
# It runs every check, reports each failure, and exits 1 if any failed. A tool it needs and can't
# find blocks the commit: a skipped check never passes in silence. Written for bash 3.2, the bash
# macOS ships: no mapfile, no associative arrays, and no "${empty[@]}" under set -u.
set -Eeuo pipefail
trap 'exit 1' ERR

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
# A shell script is found as npm run lint:shell finds it, with shfmt -f, which reads the extension
# and the shebang; ShellCheck's own pre-commit hook selects files the same way (types: [shell]).
# Without shfmt, a shell shebang on the first line marks one; shfmt's absence then blocks below.
shfmt_detect=""
if [[ -x node_modules/.bin/shfmt ]]; then
  shfmt_detect="node_modules/.bin/shfmt"
elif command -v shfmt > /dev/null 2>&1; then
  shfmt_detect="$(command -v shfmt)"
fi
is_sh=0
detect_shell() {
  # detect_shell <file>: sets is_sh to 1 when the file is a shell script, else to 0.
  local found="" first=""
  is_sh=0
  if [[ -n ${shfmt_detect} ]]; then
    found="$("${shfmt_detect}" -f "$1" 2> /dev/null)" || found=""
    [[ -z ${found} ]] || is_sh=1
  else
    IFS= read -r first < "$1" || first="${first:-}"
    [[ ${first} != '#!'*sh* ]] || is_sh=1
  fi
}

biome_files=()
ts_files=()
py_files=()
sh_files=()
partial=()
while IFS= read -r -d '' file; do
  case "${file}" in
    *.ts | *.tsx | *.mjs) biome_files+=("${file}") ts_files+=("${file}") ;;
    *.md | *.json) biome_files+=("${file}") ;;
    *.py | *.pyi) py_files+=("${file}") ;;
    *.sh) sh_files+=("${file}") ;;
    *)
      detect_shell "${file}"
      ((is_sh == 1)) || continue
      sh_files+=("${file}")
      ;;
  esac
  # The tools read the file in the work tree. If it differs from what is staged, they would check
  # text the commit doesn't hold, so the commit waits until the file is staged whole.
  git diff --quiet -- "${file}" || partial+=("${file}")
done < "${scratch}/staged"

if ((${#partial[@]} > 0)); then
  {
    echo "pre-commit: these staged files have unstaged changes, so the checks can't read what the"
    echo "commit holds. Stage them whole (git add) or stash the rest (git stash --keep-index):"
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

if ((${#biome_files[@]} > 0)); then
  find_tool biome biome
  if [[ -n ${biome} ]]; then
    # The recipe Biome documents for a pre-commit hook, given the staged list instead of --staged
    # so only the covered types are checked; warnings fail as they do in CI.
    run_tool biome "${biome}" check --files-ignore-unknown=true --no-errors-on-unmatched \
      --error-on-warnings --max-diagnostics=none "${biome_files[@]}"
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
      run_tool tsc "${tsc}" -p "${scratch}/root.json" --noEmit
    fi
    for plugin in ${plugins}; do
      group=()
      for file in "${ts_files[@]}"; do
        [[ ${file} == "plugins/${plugin}/"* ]] && group+=("${root}/${file}")
      done
      write_config "${scratch}/${plugin}.json" "${root}/plugins/${plugin}/tsconfig.json" "${group[@]}"
      run_tool tsc "${tsc}" -p "${scratch}/${plugin}.json" --noEmit
    done
    if ((${#unchecked[@]} > 0)); then
      # A mod's types and tsconfig.json are generated by Claude Code when it loads the mod from
      # --plugin-dir in an interactive session, and are git-ignored; without them tsc can't
      # resolve the mod's claude-code imports. A .ts file that can't be type-checked blocks the
      # commit, like a missing tool.
      {
        echo "pre-commit: not type-checked: no tsconfig.json covers these files. For a mod, load it"
        echo "once with claude --plugin-dir plugins/<name> to generate its tsconfig.json:"
        printf '  %s\n' "${unchecked[@]}"
      } >&2
      fail tsc
    fi
  fi
fi

if ((${#py_files[@]} > 0)); then
  find_tool ruff ruff
  if [[ -n ${ruff} ]]; then
    # ruff-pre-commit's own hooks: ruff-check runs `ruff check --force-exclude` before ruff-format
    # runs `ruff format --force-exclude`, on python and pyi files (Markdown stays Biome's, and
    # pyproject.toml excludes it). Both only check: a fix written during the commit would leave the file
    # with unstaged changes; run `ruff check --fix` and `ruff format` before staging instead.
    run_tool "ruff check" "${ruff}" check --force-exclude "${py_files[@]}"
    run_tool "ruff format" "${ruff}" format --check --diff --force-exclude "${py_files[@]}"
  fi
  find_tool basedpyright basedpyright
  if [[ -n ${basedpyright} ]]; then
    # Files given on the command line replace the config's include list; everything else in
    # pyproject.toml's [tool.basedpyright] still applies, executionEnvironments included, so one run
    # checks plugins/ at Python 3.12 and scripts/ at 3.15, as npm run typecheck:python does.
    run_tool basedpyright "${basedpyright}" "${py_files[@]}"
  fi
fi

if ((${#sh_files[@]} > 0)); then
  find_tool shfmt shfmt
  if [[ -n ${shfmt} ]]; then
    run_tool shfmt "${shfmt}" -d "${sh_files[@]}"
  fi
  find_tool shellcheck shellcheck
  if [[ -n ${shellcheck} ]]; then
    # ShellCheck reads .shellcheckrc and adds SHELLCHECK_OPTS from the environment to the start of
    # its command line itself; -S style and -a have no .shellcheckrc key, so they are passed as npm
    # run lint:shell does.
    run_tool shellcheck "${shellcheck}" -S style -a "${sh_files[@]}"
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
