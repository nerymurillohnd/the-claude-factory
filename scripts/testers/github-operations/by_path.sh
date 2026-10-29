#!/usr/bin/env bash
# Runs github-operations' hooks and scripts the way Claude Code and the skill do: by their path, in
# a stripped environment. CI does not run it; the pre-push gate runs it locally. Exits non-zero on
# the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
plugin="${root}/plugins/github-operations"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
count=0

fail() {
  echo "FAIL: $1"
  [[ ! -s "${tmp}/err" ]] || sed 's/^/  stderr: /' "${tmp}/err"
  exit 1
}

# Every hook and skill script is committed executable, so it runs by path after an install.
git -C "${root}" ls-files -s -- \
  'plugins/github-operations/hooks/*.sh' 'plugins/github-operations/hooks/*.py' \
  'plugins/github-operations/skills/github/scripts/*' > "${tmp}/modes"
while IFS= read -r line; do
  mode=${line%% *}
  file=${line##*$'\t'}
  [[ ${mode} == 100755 ]] || fail "${file} is ${mode}, not 100755"
  count=$((count + 1))
done < "${tmp}/modes"
[[ ${count} -gt 0 ]] || fail "no hook or skill script is tracked"

# A bin folder with the tools the launcher needs and no python3, and one with a python3 that
# fails the version check.
bare="${tmp}/bare"
old="${tmp}/old"
mkdir -p "${bare}" "${old}"
for tool in bash cat grep sed dirname env; do
  path=$(command -v "${tool}") || fail "${tool} is not on PATH"
  ln -s "${path}" "${bare}/${tool}"
  ln -s "${path}" "${old}/${tool}"
done
printf '#!/bin/sh\nexit 1\n' > "${old}/python3"
chmod +x "${old}/python3"

# run <bin dir> <script> <payload> [args...]: sets `out`; stderr goes to ${tmp}/err.
run() {
  local bin=$1 script=$2 payload=$3
  shift 3
  out=$(printf '%s' "${payload}" | env -i HOME= PATH="${bin}" CLAUDE_PLUGIN_ROOT="${plugin}" \
    CLAUDE_PLUGIN_DATA="${tmp}/data" "${script}" "$@" 2> "${tmp}/err") || fail "${script##*/} $* exited non-zero"
}

expect_deny() {
  [[ ${out} == *'"permissionDecision":"deny"'* && ${out} == *'github-operations: '* ]] \
    || fail "not denied: $1 -> ${out}"
  count=$((count + 1))
}

expect_silent() {
  [[ -z ${out} ]] || fail "not silent: $1 -> ${out}"
  count=$((count + 1))
}

bash_call='{"session_id":"s","tool_name":"Bash","tool_input":{"command":"git push --force"},"cwd":"/home/u/github/x"}'
ls_call='{"session_id":"s","tool_name":"Bash","tool_input":{"command":"ls -la"},"cwd":"/home/u/github/x"}'
merge_call='{"session_id":"s","tool_name":"mcp__github__merge_pull_request","tool_input":{"owner":"o"}}'
read_call='{"session_id":"s","tool_name":"mcp__github__get_me","tool_input":{}}'
agent_write='{"session_id":"s","agent_type":"github-operations:pr-tracker","tool_name":"Write","tool_input":{"file_path":"/x"}}'
main_write='{"session_id":"s","tool_name":"Write","tool_input":{"file_path":"/x"}}'
compact='{"session_id":"s","hook_event_name":"SessionStart","source":"compact"}'

run "${bare}" "${plugin}/hooks/deny-mcp-file-writes.sh" "${read_call}"
expect_deny "deny-mcp-file-writes.sh"

for bin in "${bare}" "${old}"; do
  launcher="${plugin}/hooks/run-hook.sh"
  run "${bin}" "${launcher}" "${bash_call}" shell
  expect_deny "shell without python3 (${bin##*/})"
  [[ ${out} == *'python3 3.12'* ]] || fail "the deny does not name python3 3.12: ${out}"
  run "${bin}" "${launcher}" "${ls_call}" shell
  expect_silent "ls without python3 (${bin##*/})"
  run "${bin}" "${launcher}" "${merge_call}" mcp
  expect_deny "merge without python3 (${bin##*/})"
  run "${bin}" "${launcher}" "${read_call}" mcp
  expect_silent "MCP read without python3 (${bin##*/})"
  run "${bin}" "${launcher}" "${agent_write}" files
  expect_deny "agent write without python3 (${bin##*/})"
  run "${bin}" "${launcher}" "${main_write}" files
  expect_silent "main write without python3 (${bin##*/})"
  run "${bin}" "${launcher}" "${compact}" compact
  [[ ${out} == *'"systemMessage"'*'python3 3.12'* ]] || fail "compact without python3: ${out}"
  count=$((count + 1))
done

echo "by_path: ${count} checks passed"
