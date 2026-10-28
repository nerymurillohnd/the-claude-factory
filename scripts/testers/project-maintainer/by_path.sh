#!/usr/bin/env bash
# Runs project-maintainer's SessionStart hook the way Claude Code does: by its
# path, through the shebang, with whatever `bash` is first on PATH. CI does not run
# it; the pre-push gate runs it locally. Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
plugin="${root}/plugins/project-maintainer"
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

# Runs the hook for a project directory and sets `out`. Claude Code starts a hook in the session's
# current directory: run [project] [entrypoint] [current directory, the project by default].
run() { out=$(cd "${3:-$1}" && CLAUDE_PLUGIN_ROOT="${plugin}" CLAUDE_PROJECT_DIR="$1" CLAUDE_CODE_ENTRYPOINT="${2:-cli}" "${hook}" < /dev/null) || fail "exit $?"; }

# Asserts on the hook's JSON output: check_json <python assertions on o, h, c>.
# `o` is the whole output, `h` hookSpecificOutput and `c` additionalContext.
check_json() {
  printf '%s' "${out}" | python3 -c '
import json, sys
o = json.load(sys.stdin)
h = o["hookSpecificOutput"]
c = h["additionalContext"]
'"$1" || fail "$2: ${out}"
}

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
assert "DEBT-NNN" in c, c
assert ".claude/maintainer/technical-debt/pending-debt.md" in c, c
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

# 6. In a worktree, the handoff of the checkout the session works in wins; the checkout the session
# started in is searched when the worktree has none.
wt_repo="${tmp}/wt-repo"
mkdir -p "${wt_repo}/.claude/session-handoff"
git -C "${wt_repo}" init --quiet
git -C "${wt_repo}" -c commit.gpgsign=false -c user.name=test -c user.email=test@example.com commit --quiet --allow-empty -m init
git -C "${wt_repo}" worktree add --quiet "${tmp}/wt" -b wt-branch
printf '# Session handoff\n' > "${wt_repo}/.claude/session-handoff/2026-01-01-0000.md"
run "${wt_repo}" cli "${tmp}/wt"
[[ ${out} == *"Session handoff loaded: 2026-01-01-0000.md"* ]] || fail "worktree without its own handoff: ${out}"
echo "hook: falls back to the checkout the session started in"
mkdir -p "${tmp}/wt/.claude/session-handoff"
printf '# Session handoff\n' > "${tmp}/wt/.claude/session-handoff/2025-06-06-0606.md"
run "${wt_repo}" cli "${tmp}/wt"
[[ ${out} == *"Session handoff loaded: 2025-06-06-0606.md"* ]] || fail "worktree with its own handoff: ${out}"
echo "hook: prefers the handoff of the worktree the session works in"

# 7. Records that changed after the handoff are named, by ID and by the date in the file name.
drift="${tmp}/drift"
records="${drift}/.claude/maintainer"
mkdir -p "${drift}/.claude/session-handoff" "${records}/technical-debt" "${records}/decisions"
cat > "${drift}/.claude/session-handoff/2026-03-01-1200.md" << 'HANDOFF'
# Session handoff

## Open items
1. [2026-02-20] DEBT-001 Export fails: Pending; closes with the new API. First action: ask the vendor
2. [2026-02-21] DEBT-002 Slow nightly job: Blocked; closes when the cache ships. First action: wait

## Decisions
- ADR_2026-02-01_old-choice: keep one store; fewer moving parts
HANDOFF
printf '# Pending Debt\n\n### DEBT-001 — Export fails\n\n### DEBT-003 — New finding\n' > "${records}/technical-debt/pending-debt.md"
printf '# Closed Debt\n\n### DEBT-002 — Slow nightly job\n' > "${records}/technical-debt/closed-debt.md"
printf '# old\n' > "${records}/decisions/ADR_2026-02-01_old-choice.md"
printf '# newer\n' > "${records}/decisions/ADR_2026-03-02_newer-choice.md"
printf '# not an ADR name\n' > "${records}/decisions/notes.md"
printf '# bad slug\n' > "${records}/decisions/ADR_2026-03-03_Bad Slug.md"
run "${drift}"
check_json '
assert o["systemMessage"] == "Session handoff loaded: 2026-03-01-1200.md (records changed since: 3)", o
assert "9. The project records changed after this handoff was written:" in c, c
assert "DEBT-003 is pending and missing from the handoff" in c, c
assert "DEBT-002 is closed but the handoff lists it as open" in c, c
assert "ADR_2026-03-02_newer-choice is newer than the handoff and not cited in it" in c, c
assert "DEBT-001 is" not in c, c
assert "ADR_2026-02-01_old-choice is" not in c, c
assert "notes" not in c and "Bad Slug" not in c, c
' "drift"
echo "hook: names pending, stale and newer records, and ignores the rest"

# 8. Nothing changed: no drift note, and the output is the plain protocol.
clean="${tmp}/clean"
mkdir -p "${clean}/.claude/session-handoff" "${clean}/.claude/maintainer/technical-debt" "${clean}/.claude/maintainer/decisions"
cat > "${clean}/.claude/session-handoff/2026-03-01-1200.md" << 'HANDOFF'
# Session handoff

## Open items
1. [2026-02-20] DEBT-001 Export fails: Pending; closes with the new API. First action: ask the vendor

## Decisions
- ADR_2026-02-01_old-choice: keep one store

## Done this session
- DEBT-002 closed as resolved on 2026-02-28
HANDOFF
printf '# Pending Debt\n\n### DEBT-001 — Export fails\n' > "${clean}/.claude/maintainer/technical-debt/pending-debt.md"
printf '# Closed Debt\n\n### DEBT-002 — Slow job\n' > "${clean}/.claude/maintainer/technical-debt/closed-debt.md"
printf '# old\n' > "${clean}/.claude/maintainer/decisions/ADR_2026-02-01_old-choice.md"
run "${clean}"
check_json '
assert o["systemMessage"] == "Session handoff loaded: 2026-03-01-1200.md", o
assert "9." not in c and "records changed" not in c, c
' "clean records"
echo "hook: adds nothing when the records match the handoff"

# 9. At most 10 changes reach the context.
many="${tmp}/many"
mkdir -p "${many}/.claude/session-handoff" "${many}/.claude/maintainer/technical-debt"
printf '# Session handoff\n\n## Open items\nNone known.\n' > "${many}/.claude/session-handoff/2026-03-01-1200.md"
: > "${many}/.claude/maintainer/technical-debt/pending-debt.md"
for n in 001 002 003 004 005 006 007 008 009 010 011 012; do
  printf '### DEBT-%s — Item\n' "${n}" >> "${many}/.claude/maintainer/technical-debt/pending-debt.md"
done
run "${many}"
check_json '
assert o["systemMessage"].endswith("(records changed since: 12)"), o
assert "DEBT-010 is pending" in c and "DEBT-011 is pending" not in c, c
assert "and 2 more" in c, c
' "many changes"
echo "hook: caps the list at 10 changes"
