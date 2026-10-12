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
mkdir -p "${work}"

# 1. Committed as executable, so it runs by path after a clone or install.
mode=$(git -C "${root}" ls-files -s -- "${hook#"${root}"/}" | cut -d' ' -f1)
[[ ${mode} == 100755 ]] || {
  echo "FAIL: ${hook#"${root}"/} is ${mode}, not 100755"
  exit 1
}

run() { CLAUDE_PLUGIN_ROOT="${plugin}" CLAUDE_PROJECT_DIR="${work}" "${hook}" < /dev/null; }

# 2. A project without handoffs: no output, exit 0.
out=$(run)
[[ -z ${out} ]] || {
  echo "FAIL: output without a handoff: ${out}"
  exit 1
}
echo "hook: silent without a handoff"

# 3. Other Markdown files are not handoffs.
mkdir -p "${work}/.claude/session-handoff"
printf 'notes\n' > "${work}/.claude/session-handoff/notes.md"
out=$(run)
[[ -z ${out} ]] || {
  echo "FAIL: output for a stray notes.md: ${out}"
  exit 1
}
echo "hook: ignores files not named like a handoff"

# 4. A project with a handoff: valid JSON that adds the start-of-session protocol.
printf '# Session handoff\n' > "${work}/.claude/session-handoff/2026-01-01-0000.md"
out=$(run)
printf '%s' "${out}" | python3 -c '
import json, sys
o = json.load(sys.stdin)["hookSpecificOutput"]
assert o["hookEventName"] == "SessionStart", o
assert "SESSION START PROTOCOL" in o["additionalContext"], o
' || {
  echo "FAIL: hook output with a handoff: ${out}"
  exit 1
}
echo "hook: asks Claude to read the newest handoff"
