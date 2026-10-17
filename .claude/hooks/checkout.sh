#!/usr/bin/env bash
# SessionStart hook for The Claude Factory checkout: reports the checkout and toolchain state
# to Claude as plain-text context. It never fails the session: every probe falls back and it exits 0.

root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "${root}" 2> /dev/null || exit 0

count_lines() {
  local n=0
  if [[ -n $1 ]]; then
    while IFS= read -r _; do
      n=$((n + 1))
    done <<< "$1"
  fi
  echo "${n}"
}

report_session_state() {
  local branch upstream status_out stash_out worktree_out claude_out
  branch="$(git branch --show-current 2> /dev/null || true)"
  upstream="$(git rev-list --left-right --count origin/main...HEAD 2> /dev/null || true)"
  status_out="$(git status --porcelain 2> /dev/null)" || status_out=""
  stash_out="$(git stash list 2> /dev/null)" || stash_out=""
  worktree_out="$(git worktree list 2> /dev/null)" || worktree_out=""
  claude_out="$(claude --version 2> /dev/null)" || claude_out=""

  local behind="${upstream%%[[:space:]]*}" ahead="${upstream##*[[:space:]]}"
  local node_have node_want claude_want
  node_have="$(node --version 2> /dev/null || echo unknown)"
  node_want="v$(cat .nvmrc 2> /dev/null || echo unknown)"
  claude_want="$(sed -n 's/^ *CLAUDE_CODE_VERSION: "\(.*\)"/\1/p' .github/workflows/validate.yml 2> /dev/null)"

  echo "Session start check (The Claude Factory):"
  echo "- Branch: ${branch:-detached}; vs origin/main: ${ahead:-?} ahead, ${behind:-?} behind (last fetch)."
  local dirty stashes worktrees
  dirty="$(count_lines "${status_out}")"
  stashes="$(count_lines "${stash_out}")"
  worktrees="$(count_lines "${worktree_out}")"
  echo "- Uncommitted entries: ${dirty}; stashes: ${stashes}; worktrees: ${worktrees}."
  echo "- Node: ${node_have} (.nvmrc ${node_want}); claude: ${claude_out%% *} (CI pin ${claude_want:-unknown})."
}

report_session_state
exit 0
