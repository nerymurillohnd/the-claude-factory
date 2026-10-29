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
  [[ -z ${2:-} ]] || sed 's/^/  output: /' "$2"
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

# ── Skill scripts: branch-states.sh and verify-backup.sh on a fixture repository ──
scripts="${plugin}/skills/github/scripts"
git_path=$(command -v git) || fail "git is not on PATH"
tools_path="${git_path%/*}:/usr/bin:/bin"
fx="${tmp}/fixture"
mkdir -p "${fx}"
g() { GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git -C "${fx}" -c user.name=t -c user.email=t@example.com -c commit.gpgsign=false "$@"; }
g init -q -b main
echo a > "${fx}/f.txt"
g add f.txt
g commit -qm base
g branch merged
g switch -qc squash
echo s > "${fx}/s.txt"
g add s.txt
g commit -qm s
g switch -q main
echo s > "${fx}/s.txt"
g add s.txt
g commit -qm "squash of s"
g switch -qc differs
echo d > "${fx}/d.txt"
g add d.txt
g commit -qm d
g switch -q main
g switch -qc conflicts
echo c > "${fx}/f.txt"
g commit -qam c
g switch -q main
echo m > "${fx}/f.txt"
g commit -qam m
g switch -q --orphan orphan
echo o > "${fx}/o.txt"
g add o.txt
g commit -qm o
g switch -q main

states="${tmp}/branch-states.tsv"
env -i HOME= PATH="${tools_path}" "${scripts}/branch-states.sh" "${fx}" main "${states}" 2> "${tmp}/err" \
  || fail "branch-states.sh exited non-zero"
for expected in merged:merged in-base:squash differs:differs conflicts:conflicts unrelated:orphan; do
  state=${expected%%:*}
  branch=${expected#*:}
  grep -q "^${state}	refs/heads/${branch}	" "${states}" || fail "${branch} is not ${state}" "${states}"
  count=$((count + 1))
done
status=0
env -i HOME= PATH="${tools_path}" "${scripts}/branch-states.sh" "${fx}" no-such-ref "${tmp}/x.tsv" 2> "${tmp}/err" || status=$?
[[ ${status} -eq 1 ]] || fail "branch-states.sh on a missing base exited ${status}, not 1"
count=$((count + 1))

backup="${tmp}/backup"
mkdir -p "${backup}"
g bundle create -q "${backup}/all.bundle" --all
echo changed > "${fx}/f.txt"
g diff > "${backup}/uncommitted-main.patch"
g checkout -q -- f.txt
echo kept > "${tmp}/untracked.txt"
tar -cf "${backup}/untracked-main.tar" -C "${tmp}" untracked.txt
env -i HOME= PATH="${tools_path}" "${scripts}/verify-backup.sh" "${fx}" "${backup}" > "${tmp}/out" 2> "${tmp}/err" \
  || fail "verify-backup.sh failed a good backup" "${tmp}/out"
for line in 'PASS bundle verify' 'PASS refs match' 'PASS apply --check uncommitted-main.patch' \
  'PASS tar -tf untracked-main.tar'; do
  grep -qx "${line}" "${tmp}/out" || fail "no '${line}' line" "${tmp}/out"
  count=$((count + 1))
done
[[ -d "${backup}/restore-test.git" ]] || fail "verify-backup.sh left no restore-test.git"
status=0
env -i HOME= PATH="${tools_path}" "${scripts}/verify-backup.sh" "${fx}" "${backup}" > "${tmp}/out" 2> "${tmp}/err" || status=$?
if [[ ${status} -ne 1 ]] || ! grep -q '^FAIL restore clone' "${tmp}/out"; then
  fail "a second run over an existing restore-test.git did not fail at the restore clone" "${tmp}/out"
fi
count=$((count + 1))
cp "${backup}/all.bundle" "${tmp}/good.bundle"

# damaged <bytes> <check>: a bundle cut to its first bytes fails at that check, and nowhere else.
damaged() {
  rm -rf "${backup}/restore-test.git"
  dd if="${tmp}/good.bundle" of="${backup}/all.bundle" bs=1 count="$1" 2> /dev/null
  status=0
  env -i HOME= PATH="${tools_path}" "${scripts}/verify-backup.sh" "${fx}" "${backup}" > "${tmp}/out" 2> "${tmp}/err" || status=$?
  if [[ ${status} -ne 1 ]] || ! grep -qx "FAIL $2" "${tmp}/out"; then
    fail "a bundle cut to $1 bytes did not fail at $2 (exit ${status})" "${tmp}/out"
  fi
  count=$((count + 1))
}
# bundle verify reads only the header, so each cut is caught by a different check.
damaged 0 "bundle verify"   # empty: not a bundle at all
damaged 20 "head count"     # the signature only: a bundle that lists no refs
damaged 200 "restore clone" # the refs are whole, the pack is cut: only a restore shows it

echo "by_path: ${count} checks passed"
