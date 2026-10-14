#!/usr/bin/env bash
# Runs agent-context-audit the way Claude Code and a terminal do: the entry script by its path,
# through the shebang, with whatever `python3` is first on PATH, and the SessionStart hook with the
# exact command hooks.json declares. CI runs this on Linux, macOS and Windows (Git Bash), where the
# audit must refuse to run and say why. Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
plugin="${root}/plugins/agent-context-audit"
entry="${plugin}/skills/audit/scripts/agent_context_audit.py"
fake="${root}/.github/scripts/tests/agent-context-audit/fake_claude.py"
work=$(mktemp -d)
trap 'rm -rf "${work}"' EXIT

fail() {
  echo "FAIL: $*"
  exit 1
}

python=$(command -v python3)
version=$(python3 --version)
echo "python3: ${python} (${version})"

# 1. Committed as executable, so they run by path after a clone or install.
for script in "${entry}" "${fake}"; do
  mode=$(git -C "${root}" ls-files -s -- "${script#"${root}"/}" | cut -d' ' -f1)
  [[ ${mode} == 100755 ]] || fail "${script#"${root}"/} is '${mode}', not 100755"
done
echo "modes: 100755"

out=$("${entry}" --version)
[[ ${out} == "agent-context-audit "* ]] || fail "--version printed: ${out}"
echo "entry: ${out}"

# 2. Native Windows: the audit refuses, says to use WSL, and exits 4.
case "$(uname -s)" in
  MINGW* | MSYS* | CYGWIN*)
    set +e
    out=$("${entry}" run --repo "${work}" 2>&1)
    code=$?
    set -e
    [[ ${code} == 4 ]] || fail "exit ${code} on native Windows: ${out}"
    [[ ${out} == *"native Windows is not supported"* ]] || fail "no refusal message: ${out}"
    echo "windows: refused with exit 4 and a WSL hint"
    exit 0
    ;;
  *) ;;
esac

# 3. A whole audit by path, with the fake claude CLI and a throwaway HOME.
repo="${work}/repo"
mkdir -p "${repo}" "${work}/home"
printf '# Project\n\nSee @docs/missing.md for the rules.\n' > "${repo}/CLAUDE.md"
git -C "${repo}" init -q -b main
git -C "${repo}" add -A
git -C "${repo}" -c user.name=ci -c user.email=ci@example.com -c commit.gpgsign=false \
  commit -q -m init
set +e
out=$(HOME="${work}/home" AGENT_CONTEXT_AUDIT_CLAUDE="${fake}" \
  "${entry}" run --repo "${repo}" --offline 2>&1)
code=$?
set -e
[[ ${code} == 1 ]] || fail "audit exit ${code}: ${out}"
[[ ${out} == *"status: complete-with-findings"* ]] || fail "audit output: ${out}"
found=0
for report in "${repo}/.claude/agent-context-audit"/*/report.md; do
  [[ -f ${report} ]] && found=1
done
[[ ${found} == 1 ]] || fail "no report.md"
echo "audit: complete-with-findings, report written"

# 4. The SessionStart hook, as hooks.json declares it: announce once, then stay quiet.
command=$(python3 -c 'import json, sys
hook = json.load(open(sys.argv[1]))["hooks"]["SessionStart"][0]["hooks"][0]
print(hook["command"])' "${plugin}/hooks/hooks.json")
event='{"hook_event_name":"SessionStart","source":"startup"}'
hook() {
  printf '%s' "${event}" | HOME="${work}/home" CLAUDE_PLUGIN_ROOT="${plugin}" \
    CLAUDE_PROJECT_DIR="${repo}" sh -c "${command}"
}
out=$(hook)
[[ ${out} == *'"systemMessage"'* ]] || fail "hook printed no notice: ${out}"
out=$(hook)
[[ -z ${out} ]] || fail "hook repeated the notice: ${out}"
echo "hook: announces a new report once"
