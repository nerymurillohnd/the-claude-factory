#!/usr/bin/env bash
# Runs agent-files-diagnostics' entry script the way Claude Code does: by its path, through the
# shebang, with whatever `python3` is first on PATH. CI runs this on Linux, macOS and Windows
# (Git Bash), where the audit must refuse to run and say why. Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
plugin="${root}/plugins/agent-files-diagnostics"
entry="${plugin}/skills/agent-context-audit/scripts/agent_context_audit.py"
work=$(mktemp -d)
trap 'rm -rf "${work}"' EXIT

fail() {
  echo "FAIL: $*"
  exit 1
}

python=$(command -v python3)
version=$(python3 --version)
echo "python3: ${python} (${version})"

# 1. Committed as executable, so it runs by path after a clone or install.
mode=$(git -C "${root}" ls-files -s -- "${entry#"${root}"/}" | cut -d' ' -f1)
[[ ${mode} == 100755 ]] || fail "${entry#"${root}"/} is '${mode}', not 100755"
echo "mode: 100755"

out=$("${entry}" --version)
[[ ${out} == "agent-context-audit "* ]] || fail "--version printed: ${out}"
echo "entry: ${out}"

# 2. A fake claude on PATH, so prepare passes preflight without the real CLI.
mkdir -p "${work}/bin"
printf '#!/bin/sh\necho "2.1.300 (Claude Code)"\n' > "${work}/bin/claude"
chmod +x "${work}/bin/claude"
export PATH="${work}/bin:${PATH}"

# 3. Native Windows: prepare refuses, says to use WSL, and still prints JSON.
case "$(uname -s)" in
  MINGW* | MSYS* | CYGWIN*)
    out=$("${entry}" prepare --repo "${work}" --offline 2>&1)
    [[ ${out} == *'"cannot-run"'* ]] || fail "no refusal on native Windows: ${out}"
    [[ ${out} == *"WSL"* ]] || fail "no WSL hint: ${out}"
    echo "windows: refused with a WSL hint"
    exit 0
    ;;
  *) ;;
esac

# 4. prepare by path on a tiny repository with a throwaway HOME: a run folder with task files.
repo="${work}/repo"
mkdir -p "${repo}" "${work}/home"
printf '# Project\n\nSee @docs/missing.md for the rules.\n' > "${repo}/CLAUDE.md"
git -C "${repo}" init -q -b main
git -C "${repo}" add -A
git -C "${repo}" -c user.name=ci -c user.email=ci@example.com -c commit.gpgsign=false \
  commit -q -m init
out=$(HOME="${work}/home" "${entry}" prepare --repo "${repo}" --offline 2>&1)
[[ ${out} == *'"run_dir"'* ]] || fail "prepare output: ${out}"
[[ ${out} == *'"deterministic_findings": 1'* ]] || fail "the missing import was not found: ${out}"
run_dir=$(python3 -c 'import json, sys; print(json.loads(sys.stdin.read())["run_dir"])' <<< "${out}")
[[ -f "${run_dir}/state.json" ]] || fail "no state.json in ${run_dir}"
[[ -d "${run_dir}/work/tasks" ]] || fail "no task files in ${run_dir}"
echo "prepare: run folder written with one deterministic finding"

# 5. latest with no finished run says so.
out=$(HOME="${work}/home" "${entry}" latest --repo "${repo}")
[[ ${out} == *'"no-report"'* ]] || fail "latest output: ${out}"
echo "latest: no report yet"
