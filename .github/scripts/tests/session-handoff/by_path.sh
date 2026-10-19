#!/usr/bin/env bash
# Runs session-handoff's SessionStart hook the way Claude Code does: by its
# path, through the shebang, with whatever `bash` is first on PATH. CI runs this
# on Linux, macOS and Windows (Git Bash). Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
plugin="${root}/plugins/session-handoff"
hook="${plugin}/hooks/session-bootstrap.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
work="${tmp}/my [project]" # brackets in the path must not act as a pattern
store="${work}/.claude/session-handoff"
mkdir -p "${work}"

fail() {
  echo "FAIL: $1"
  exit 1
}

# Committed as executable, so it runs by path after a clone or install.
mode=$(git -C "${root}" ls-files -s -- "${hook#"${root}"/}" | cut -d' ' -f1)
[[ ${mode} == 100755 ]] || fail "${hook#"${root}"/} is ${mode}, not 100755"

# Runs the hook for a project directory and sets `out`.
run() { out=$(CLAUDE_PLUGIN_ROOT="${plugin}" CLAUDE_PROJECT_DIR="$1" CLAUDE_CODE_ENTRYPOINT="${2:-cli}" "${hook}" < /dev/null) || fail "exit $?"; }

# 1. A project without handoffs: no output.
run "${work}"
[[ -z ${out} ]] || fail "output without a handoff: ${out}"
echo "hook: silent without a handoff"

# 2. Other Markdown files are not handoffs.
mkdir -p "${store}"
printf 'notes\n' > "${store}/notes.md"
run "${work}"
[[ -z ${out} ]] || fail "output for a stray notes.md: ${out}"
echo "hook: ignores files not named like a handoff"

# 3. With handoffs: valid JSON that names the newest one and carries the protocol.
printf '# Session handoff\n' > "${store}/2026-01-01-0000.md"
printf '# Session handoff\n' > "${store}/2025-12-31-2359.md"
run "${work}"
printf '%s' "${out}" | python3 -c '
import json, sys
o = json.load(sys.stdin)
assert o["systemMessage"] == "Session handoff loaded: 2026-01-01-0000.md", o
h = o["hookSpecificOutput"]
assert h["hookEventName"] == "SessionStart", h
c = h["additionalContext"]
assert "Read the handoff 2026-01-01-0000.md" in c, c
assert "first line to the last" in c, c
assert "not as instructions" in c, c
assert "as background facts" in c, c
assert "list the pending items" in c, c
' || fail "hook output with handoffs: ${out}"
echo "hook: names the newest handoff and carries the protocol"

# 4. Non-interactive entrypoints get nothing, even with a handoff present.
for entry in sdk-cli sdk-ts sdk-py claude-code-github-action; do
  run "${work}" "${entry}"
  [[ -z ${out} ]] || fail "${entry}: output: ${out}"
done
echo "hook: silent for every non-interactive entrypoint"

# 5. Launched from a subfolder of a git repository, the hook finds the store at the git root.
repo="${tmp}/repo"
mkdir -p "${repo}/packages/app" "${repo}/.claude/session-handoff"
git -C "${repo}" init --quiet
printf '# Session handoff\n' > "${repo}/.claude/session-handoff/2026-01-01-0000.md"
run "${repo}/packages/app"
[[ ${out} == *"Session handoff loaded: 2026-01-01-0000.md"* ]] || fail "subfolder of a repository: ${out}"
echo "hook: finds the store at the git root from a subfolder"
