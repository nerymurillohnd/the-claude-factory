#!/usr/bin/env bash
# Runs block-no-verify's launcher the way Claude Code does: by its path, in a stripped
# environment. CI runs this on Linux, macOS and Windows (Git Bash). Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
launcher="${root}/plugins/block-no-verify/hooks/block-no-verify.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

fail() {
  echo "FAIL: $1"
  [[ ! -s "${tmp}/err" ]] || sed 's/^/  stderr: /' "${tmp}/err"
  exit 1
}

# Both are committed as executable, so they run by path after a clone or an install.
for file in hooks/block-no-verify.sh hooks/block_no_verify.py; do
  mode=$(git -C "${root}" ls-files -s -- "plugins/block-no-verify/${file}" | cut -d' ' -f1)
  [[ ${mode} == 100755 ]] || fail "${file} is ${mode:-untracked}, not 100755"
done

# A minimal PATH that still finds python3 (and python, which the Windows CI shim runs).
python=$(command -v python3) || fail "python3 is not on PATH"
dirs=${python%/*}
if other=$(command -v python 2> /dev/null); then dirs="${dirs}:${other%/*}"; fi
safe_path="${dirs}:/usr/bin:/bin"
bash_path=$(command -v bash)

deny='{"tool_name":"Bash","tool_input":{"command":"git commit --no-verify -m x"}}'
allow='{"tool_name":"Bash","tool_input":{"command":"git commit -m x"}}'

# Runs the launcher by path in an empty environment: run <PATH> <payload>. Sets `out` and `status`.
run() {
  status=0
  out=$(printf '%s' "$2" | env -i HOME= PATH="$1" "${launcher}" 2> "${tmp}/err") || status=$?
}

# The same, through an explicit bash, for a PATH that must not hold python3 or env's bash lookup.
run_bash() {
  status=0
  out=$(printf '%s' "$2" | env -i HOME= PATH="$1" "${bash_path}" "${launcher}" 2> "${tmp}/err") || status=$?
}

# Asserts on the JSON in `out`: check_json <python assertions on o> <message>.
check_json() {
  printf '%s' "${out}" | python3 -c '
import json, sys
o = json.load(sys.stdin)
'"$1" || fail "$2: ${out}"
}

# 1. A bypass is denied: one JSON object, exit 0.
run "${safe_path}" "${deny}"
[[ ${status} -eq 0 ]] || fail "deny payload exited ${status}"
check_json '
assert set(o) == {"hookSpecificOutput"}
h = o["hookSpecificOutput"]
assert h["hookEventName"] == "PreToolUse" and h["permissionDecision"] == "deny"
assert "--no-verify" in h["permissionDecisionReason"]
' "not a deny"
echo "launcher: denies a bypass"

# 2. An ordinary commit passes in silence.
run "${safe_path}" "${allow}"
[[ ${status} -eq 0 && -z ${out} ]] || fail "allowed payload gave status ${status}, output: ${out}"
echo "launcher: stays silent for a normal commit"

# 3. Without python3 the guard says it is inactive and blocks nothing.
mkdir "${tmp}/empty"
notice='
assert "block-no-verify is inactive" in o["systemMessage"]
h = o["hookSpecificOutput"]
assert h["hookEventName"] == "PreToolUse" and "permissionDecision" not in h
assert "not being blocked" in h["additionalContext"]
'
run_bash "${tmp}/empty" "${deny}"
[[ ${status} -eq 0 ]] || fail "missing python3 exited ${status}"
check_json "${notice}" "no notice without python3"
echo "launcher: notice, no block, without python3"

# 4. A python3 older than 3.9 gets the same notice.
mkdir "${tmp}/old"
printf '#!/bin/sh\nexit 1\n' > "${tmp}/old/python3"
chmod +x "${tmp}/old/python3"
run_bash "${tmp}/old" "${deny}"
[[ ${status} -eq 0 ]] || fail "old python3 exited ${status}"
check_json "${notice}" "no notice with an old python3"
echo "launcher: notice, no block, with python3 older than 3.9"

# 5. Past the version check a crash is not hidden: its exit code and an empty stdout reach
# Claude Code, which blocks the call because the hook sets onFailure to block.
mkdir "${tmp}/crash"
cat > "${tmp}/crash/python3" << 'EOF'
#!/bin/sh
case "$1" in
  -c) exit 0 ;;
  *) echo boom >&2; exit 3 ;;
esac
EOF
chmod +x "${tmp}/crash/python3"
run_bash "${tmp}/crash" "${deny}"
[[ ${status} -eq 3 && -z ${out} ]] || fail "a crash gave status ${status}, output: ${out}"
echo "launcher: a crash after the version check keeps its exit code"
