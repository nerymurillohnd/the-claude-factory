#!/usr/bin/env bash
# Runs block-no-verify's handler the way Claude Code does: by its path, a payload on stdin, in a
# stripped environment. CI does not run it; the pre-push gate runs it locally. Needs jq on PATH, as
# the plugin does. Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
hook="${root}/plugins/block-no-verify/hooks/block-no-verify.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
count=0

fail() {
  echo "FAIL: $1"
  [[ ! -s "${tmp}/err" ]] || sed 's/^/  stderr: /' "${tmp}/err"
  exit 1
}

# Committed as executable, so it runs by path after a clone or an install.
mode=$(git -C "${root}" ls-files -s -- plugins/block-no-verify/hooks/block-no-verify.sh | cut -d' ' -f1)
[[ ${mode} == 100755 ]] || fail "block-no-verify.sh is ${mode:-untracked}, not 100755"

jq_path=$(command -v jq) || fail "jq is not on PATH: the plugin needs it"
safe_path="${jq_path%/*}:/usr/bin:/bin"
bash_path=$(command -v bash)

# Runs the handler by path on a raw payload. Sets `status` and `out`; stderr goes to ${tmp}/err.
run_raw() {
  status=0
  out=$(printf '%s' "$1" | env -i HOME= PATH="${safe_path}" "${hook}" 2> "${tmp}/err") || status=$?
}

# run <tool> <command>: the payload Claude Code sends for one tool call.
run() {
  local payload
  payload=$(jq -n --arg tool "$1" --arg cmd "$2" '{tool_name: $tool, tool_input: {command: $cmd}}')
  run_raw "${payload}"
}

# A deny: exit 2, one JSON deny object on stdout, a reason that starts with the plugin name on stderr.
expect_deny() {
  run "${2:-Bash}" "$1"
  [[ ${status} -eq 2 ]] || fail "not denied (exit ${status}): $1"
  printf '%s' "${out}" | jq -e '.hookSpecificOutput | .hookEventName == "PreToolUse" and .permissionDecision == "deny"' > /dev/null \
    || fail "no deny object on stdout: $1"
  [[ $(< "${tmp}/err") == block-no-verify:* ]] || fail "no reason on stderr: $1"
  count=$((count + 1))
}

# A pass: exit 0 and nothing on stdout.
expect_pass() {
  run "${2:-Bash}" "$1"
  [[ ${status} -eq 0 && -z ${out} ]] || fail "wrongly stopped (exit ${status}): $1"
  count=$((count + 1))
}

denied=(
  # the flags, in full, abbreviated and short
  'git commit --no-verify -m x'
  'git commit -n -m x'
  'git commit -nm x'
  'git commit --no-veri -m x'
  'git commit --no-gpg-sign -m x'
  'git push --no-verify'
  'git merge --no-verify b'
  'git am -n p.patch'
  # signing and hooks switched off through configuration
  'git -c commit.gpgsign=false commit -m x'
  'git -c commit.gpgsign= commit -m x'
  'git -c commit.gpgsign=00 commit -m x'
  'git -c tag.gpgsign=off tag v1'
  'git config commit.gpgsign false'
  'git -c core.hooksPath=/dev/null commit -m x'
  'git config core.hooksPath /dev/null'
  'HUSKY=0 git commit -m x'
  'GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false git commit -m x'
  'git -c alias.ci="commit --no-verify" ci -m x'
  # wrappers, grouping and control flow around the git call
  'sudo -n git commit --no-verify -m x'
  'env git commit --no-verify -m x'
  'time git commit --no-verify -m x'
  'exec git commit --no-verify -m x'
  '(git commit --no-verify)'
  '{ git commit --no-verify -m x; }'
  '! git commit --no-verify -m x'
  'if true; then git commit --no-verify -m x; fi'
  'for f in a; do git commit -n -m x; done'
  'sleep 1 & git commit --no-verify -m x'
  '2>/dev/null git commit --no-verify -m x'
  # command substitutions, quoting and line joins
  $'echo "$(git commit --no-verify -m x)"'
  $'out=$(git commit --no-verify -m x)'
  $'echo `git commit -n -m x`'
  "git commit \$'--no-verify' -m x"
  'g"i"t commit --no-verify -m x'
  $'git commit \\\n--no-verify -m x'
  # a shell, eval or a heredoc that runs
  'bash -c "git commit --no-verify -m x"'
  'sh -lc "git commit -n"'
  'eval "git commit --no-verify -m x"'
  "bash -c \"bash -c 'git commit --no-verify'\""
  $'bash <<\'EOF\'\ngit commit --no-verify\nEOF'
  $'cat <<\'EOF\' | bash\ngit commit -n\nEOF'
)
for command in "${denied[@]}"; do expect_deny "${command}"; done
echo "handler: denies ${count} bypasses, with exit 2, a deny object and a reason"

passed=(
  'git status'
  'git commit -m x'
  'git commit -m "docs: mention --no-verify"'
  'git commit --no-edit --amend'
  'git push -n'
  'git merge -n b'
  'git pull -n'
  'git cherry-pick -n abc'
  'git config --get commit.gpgsign'
  'git log --grep=no-verify'
  'echo "(git commit --no-verify)"'
  "echo 'never run git commit --no-verify'"
  'grep -rn -- --no-verify .'
  'ls -la'
  # heredocs that only write text: a quote, or a line that mentions the flag, is not a command
  $'cat > f <<\'EOF\'\nit\'s "odd\nEOF'
  $'cat > README.md <<\'EOF\'\ngit commit --no-verify\nEOF'
  $'python3 - <<\'EOF\'\n# don\'t break\nprint(1)\nEOF'
  $'gh pr create --body "$(cat <<\'EOF\'\nfix: a 5" pipe\nEOF\n)"'
  # Claude's own commit form
  $'git commit -m "$(cat <<\'EOF\'\nfeat: x\n\nDo not use --no-verify.\nEOF\n)"'
  $'git commit -am "$(cat <<\'EOF\'\nfix: a 5" pipe\nEOF\n)"'
  $'git add -A && git commit -m "$(cat <<\'EOF\'\nx " y\nEOF\n)"'
)
before=${count}
for command in "${passed[@]}"; do expect_pass "${command}"; done
echo "handler: lets $((count - before)) harmless commands through, in silence"

# The PowerShell tool is guarded too; other tools are not its business.
expect_deny 'git commit --no-verify -m x' PowerShell
expect_pass 'git status' PowerShell
expect_pass 'git commit --no-verify -m x' Read
run_raw '{"tool_name":"Bash","tool_input":{"command":5}}'
[[ ${status} -eq 0 && -z ${out} ]] || fail "a command that is not a string must pass"
run_raw '{"tool_name":"Bash"}'
[[ ${status} -eq 0 && -z ${out} ]] || fail "a call without tool_input must pass"
echo "handler: guards the PowerShell tool and ignores calls without a Bash command"

# A native jq.exe on Windows prints CRLF for every LF it writes. jq 1.6 has no --binary to stop it, so
# the tool name arrives as "Bash\r" unless the handler undoes it. This stub does the same on any system.
mkdir "${tmp}/winjq"
cat > "${tmp}/winjq/jq" << STUB
#!/usr/bin/env bash
set -o pipefail
"${jq_path}" "\$@" | sed \$'s/\$/\\r/'
STUB
chmod +x "${tmp}/winjq/jq"
unix_path=${safe_path}
safe_path="${tmp}/winjq:${unix_path}"
expect_deny 'git commit --no-verify -m x'
expect_deny $'git commit \\\n--no-verify -m x'
expect_pass 'git status'
expect_pass $'git commit -m "$(cat <<\'EOF\'\nfeat: x\n\nDo not use --no-verify.\nEOF\n)"'
safe_path=${unix_path}
echo "handler: reads the payload the same when jq prints CRLF, as a native Windows jq does"

# What it cannot read it refuses: an unreadable payload or a command with an open quote.
for payload in 'not json' '[]' '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"x"}}'; do
  run_raw "${payload}"
  [[ ${status} -eq 2 ]] || fail "unreadable input must be denied (exit ${status}): ${payload}"
done
echo "handler: fails closed on a payload or a command it cannot read"

# Without jq it cannot read the payload: a command that could involve git is denied with the
# reason, anything else passes. Bash alone, on an empty PATH.
mkdir "${tmp}/empty"
no_jq() {
  local payload
  payload=$(jq -n --arg cmd "$1" '{tool_name: "Bash", tool_input: {command: $cmd}}')
  status=0
  out=$(printf '%s' "${payload}" | env -i HOME= PATH="${tmp}/empty" "${bash_path}" "${hook}" 2> "${tmp}/err") || status=$?
}
no_jq 'git status'
[[ ${status} -eq 2 ]] || fail "without jq a git command must be denied (exit ${status})"
grep -q 'jq is not installed' "${tmp}/err" || fail "without jq the reason must say so"
no_jq 'ls -la'
[[ ${status} -eq 0 && -z ${out} ]] || fail "without jq a command with no git must pass"
echo "handler: without jq it denies git commands, says why, and lets the rest through"

# A very long command must not outlast the hook: the handler meters its own work. A watchdog turns
# a hang into a failure, and each size is timed so a slowdown shows where it starts.
long_command() { # $1: length of the commit message
  local payload pid dog started=${SECONDS}
  printf -v long "%${1}s" ''
  long=${long// /a}
  payload=$(jq -n --arg cmd "git commit -m \"${long}\"" '{tool_name: "Bash", tool_input: {command: $cmd}}')
  printf '%s' "${payload}" | env -i HOME= PATH="${safe_path}" "${hook}" > "${tmp}/out" 2> "${tmp}/err" &
  pid=$!
  (sleep 20 && kill "${pid}") > /dev/null 2>&1 &
  dog=$!
  status=0
  wait "${pid}" || status=$?
  kill "${dog}" > /dev/null 2>&1 || true
  [[ ${status} -eq 0 && ! -s "${tmp}/out" ]] || fail "a ${1}-character command was stopped or took over 20 s (exit ${status})"
  echo "handler: reads a ${1}-character command in $((SECONDS - started)) s"
}
for size in 2000 5000 10000 20000; do long_command "${size}"; done
