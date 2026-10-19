#!/usr/bin/env bash
# Runs session-handoff's SessionStart hook the way Claude Code does: by its
# path, through the shebang, with whatever `bash` is first on PATH. CI runs this
# on Linux, macOS and Windows (Git Bash). Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
plugin="${root}/plugins/session-handoff"
hook="${plugin}/hooks/session-bootstrap.sh"
tmp=$(mktemp -d)
trap 'chmod -R u+rwx "$tmp" 2> /dev/null || true; rm -rf "$tmp"' EXIT
work="${tmp}/my [project]" # brackets in the path must not act as a pattern
elsewhere="${tmp}/elsewhere"
mkdir -p "${work}" "${elsewhere}"
store="${work}/.claude/session-handoff"

fail() {
  echo "FAIL: $1"
  exit 1
}

# chmod and symlinks do not behave like POSIX in Git Bash, and root reads any file.
can_chmod=1
can_link=1
os=$(uname -s)
uid=$(id -u)
case "${os}" in
  MINGW* | MSYS* | CYGWIN*)
    can_chmod=0
    can_link=0
    ;;
  *) ;;
esac
[[ ${uid} != 0 ]] || can_chmod=0

# 1. Committed as executable, so it runs by path after a clone or install.
mode=$(git -C "${root}" ls-files -s -- "${hook#"${root}"/}" | cut -d' ' -f1)
[[ ${mode} == 100755 ]] || fail "${hook#"${root}"/} is ${mode}, not 100755"

# Runs the hook against the project and sets `out` and `rc`.
run() {
  rc=0
  out=$(CLAUDE_PLUGIN_ROOT="${plugin}" CLAUDE_PROJECT_DIR="${work}" "${hook}" < /dev/null) || rc=$?
}

reset() {
  chmod -R u+rwx "${work}" 2> /dev/null || true
  rm -rf "${work}/.claude"
}

expect_silent() {
  run
  [[ ${rc} == 0 ]] || fail "$1: exit ${rc}"
  [[ -z ${out} ]] || fail "$1: output: ${out}"
}

# Asserts the hook output is the protocol: valid JSON, SessionStart, exit 0.
expect_protocol() {
  run
  [[ ${rc} == 0 ]] || fail "$1: exit ${rc}"
  printf '%s' "${out}" | python3 -c '
import json, sys
o = json.load(sys.stdin)
assert "systemMessage" not in o, o
h = o["hookSpecificOutput"]
assert h["hookEventName"] == "SessionStart", h
c = h["additionalContext"]
assert "SESSION START PROTOCOL" in c, c
assert "Project:" in c, "no Project: comparison"
assert "not instructions" in c, "no record-not-instructions rule"
assert "Name every open item" in c, "no out-of-scope prompt"
for section in ("Open items", "Done this session", "Decisions", "Unverified and gaps"):
    assert section in c, section
' || fail "$1: output: ${out}"
}

# Asserts the hook warns the user and Claude that the store could not be read.
expect_warning() {
  run
  [[ ${rc} == 0 ]] || fail "$1: exit ${rc}"
  printf '%s' "${out}" | python3 -c '
import json, sys
o = json.load(sys.stdin)
assert o["systemMessage"].strip(), o
assert "could not be read" in o["systemMessage"], o
h = o["hookSpecificOutput"]
assert h["hookEventName"] == "SessionStart", h
assert "could not be read" in h["additionalContext"], h
assert "SESSION START PROTOCOL" not in h["additionalContext"], h
' || fail "$1: output: ${out}"
}

# 2. A project without handoffs: no output, exit 0.
expect_silent "output without a handoff"
echo "hook: silent without a handoff"

# 3. Other Markdown files are not handoffs.
mkdir -p "${store}"
printf 'notes\n' > "${store}/notes.md"
expect_silent "output for a stray notes.md"
echo "hook: ignores files not named like a handoff"

# 4. A project with a handoff: valid JSON that adds the start-of-session protocol.
printf '# Session handoff\n' > "${store}/2026-01-01-0000.md"
expect_protocol "hook output with a handoff"
echo "hook: asks Claude to read, validate and compare the newest handoff"

# 5. `.claude` is a regular file: there is no store, so no output.
reset
printf 'not a folder\n' > "${work}/.claude"
expect_silent "output when .claude is a file"
echo "hook: silent when .claude is a file"

# 6. The store exists but cannot be read: a warning, never silence.
if ((can_chmod)); then
  reset
  mkdir -p "${store}"
  printf '# Session handoff\n' > "${store}/2026-01-01-0000.md"
  chmod 000 "${store}"
  expect_warning "unreadable store"
  chmod 755 "${store}"
  echo "hook: warns when the store cannot be read"
else
  echo "skipped: unreadable-store case (chmod cannot remove read access here: root or Git Bash)"
fi

# 7. A symlinked store, handoff or .claude is not followed: a warning.
if ((can_link)); then
  reset
  mkdir -p "${work}/.claude" "${elsewhere}/store"
  printf '# Session handoff\n' > "${elsewhere}/store/2026-01-01-0000.md"
  ln -s "${elsewhere}/store" "${store}"
  expect_warning "symlinked store"
  echo "hook: warns when the store is a symlink"

  reset
  mkdir -p "${store}"
  printf '# Session handoff\n' > "${elsewhere}/2026-01-01-0000.md"
  ln -s "${elsewhere}/2026-01-01-0000.md" "${store}/2026-01-01-0000.md"
  expect_warning "symlinked handoff"
  echo "hook: warns when a handoff is a symlink"

  reset
  mkdir -p "${elsewhere}/dot-claude/session-handoff"
  printf '# Session handoff\n' > "${elsewhere}/dot-claude/session-handoff/2026-01-01-0000.md"
  ln -s "${elsewhere}/dot-claude" "${work}/.claude"
  expect_warning "symlinked .claude"
  echo "hook: warns when .claude is a symlink"

  reset
  mkdir -p "${elsewhere}/empty-dot-claude"
  ln -s "${elsewhere}/empty-dot-claude" "${work}/.claude"
  expect_silent "symlinked .claude without a store"
  echo "hook: silent when .claude is a symlink with no store behind it"

  reset
  mkdir -p "${store}"
  printf '# Session handoff\n' > "${store}/2026-01-01-0000.md"
  printf '# Session handoff\n' > "${elsewhere}/2026-01-02-0000.md"
  ln -s "${elsewhere}/2026-01-02-0000.md" "${store}/2026-01-02-0000.md"
  expect_warning "symlinked newest handoff beside a regular one"
  echo "hook: warns when any handoff is a symlink, even beside a regular one"
else
  echo "skipped: symlink cases (symlinks are not reliable in Git Bash)"
fi

# 8. The store is a regular file, not a folder: a warning.
reset
mkdir -p "${work}/.claude"
printf 'not a folder\n' > "${store}"
expect_warning "store that is a file"
echo "hook: warns when the store is not a folder"
