#!/usr/bin/env bash
# SessionStart hook for The Claude Factory checkout: reports the checkout and toolchain state
# to Claude as plain-text context. It never fails the session: every probe falls back and it exits 0.
# A cloud session clones only its working branch, shallowly, so origin/main can be missing or share
# no history with HEAD; ensure_main_ref fetches what the ahead/behind count needs. A full clone with
# origin/main already present makes no network request.
# No `set -euo pipefail`: a failing probe, an unset variable or a broken pipe must fall back to its
# default, never end the hook before it reports.

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

# Runs git with a time limit where timeout(1) exists (Linux; not stock macOS), and never prompts.
git_bounded() {
  if command -v timeout > /dev/null 2>&1; then
    GIT_TERMINAL_PROMPT=0 timeout 60 git "$@"
  else
    GIT_TERMINAL_PROMPT=0 git "$@"
  fi
}

ensure_main_ref() {
  git remote get-url origin > /dev/null 2>&1 || return 0
  if ! git rev-parse --verify --quiet refs/remotes/origin/main > /dev/null; then
    git_bounded fetch --quiet --no-tags origin +refs/heads/main:refs/remotes/origin/main 2> /dev/null || return 0
  fi
  git merge-base HEAD refs/remotes/origin/main > /dev/null 2>&1 && return 0
  local shallow
  shallow="$(git rev-parse --is-shallow-repository 2> /dev/null)" || shallow=""
  if [[ ${shallow} == true ]]; then
    git_bounded fetch --quiet --no-tags --unshallow origin 2> /dev/null || true
  fi
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
  local node_have node_want
  node_have="$(node --version 2> /dev/null || echo unknown)"
  node_want="v$(cat .nvmrc 2> /dev/null || echo unknown)"

  echo "Session start check (The Claude Factory):"
  echo "- Branch: ${branch:-detached}; vs origin/main: ${ahead:-?} ahead, ${behind:-?} behind (last fetch)."
  local dirty stashes worktrees
  dirty="$(count_lines "${status_out}")"
  stashes="$(count_lines "${stash_out}")"
  worktrees="$(count_lines "${worktree_out}")"
  echo "- Uncommitted entries: ${dirty}; stashes: ${stashes}; worktrees: ${worktrees}."
  echo "- Node: ${node_have} (.nvmrc ${node_want}); claude: ${claude_out%% *}."
  if ! node_in_caret_range "${node_have}" "${node_want}"; then
    # npm bundled with an older Node rewrites package-lock.json (npm 10 drops the libc fields);
    # devEngines in package.json (^ plus the .nvmrc version) makes npm refuse to install here.
    echo "- Warning: Node is outside ^${node_want#v} (devEngines). Do not run npm install or the" \
      "gates here; select ${node_want} first, or package-lock.json may be rewritten."
  fi
}

# Succeeds when $1 (vX.Y.Z) satisfies ^$2 (vX.Y.Z): same major, and not older. A prerelease such
# as v26.13.0-rc.1 fails, as npm's ^ range excludes it. Succeeds too when either version cannot
# be read, so a missing node or .nvmrc prints no warning.
node_in_caret_range() {
  local pattern='^v([0-9]+)\.([0-9]+)\.([0-9]+)$'
  local h1 h2 h3
  [[ $2 =~ ${pattern} ]] || return 0
  local w1="${BASH_REMATCH[1]}" w2="${BASH_REMATCH[2]}" w3="${BASH_REMATCH[3]}"
  if [[ $1 =~ ^v[0-9]+\.[0-9]+\.[0-9]+-[0-9A-Za-z.-]+$ ]]; then
    return 1
  fi
  [[ $1 =~ ${pattern} ]] || return 0
  h1="${BASH_REMATCH[1]}" h2="${BASH_REMATCH[2]}" h3="${BASH_REMATCH[3]}"
  ((10#${h1} == 10#${w1})) || return 1
  ((10#${h2} > 10#${w2})) && return 0
  ((10#${h2} == 10#${w2} && 10#${h3} >= 10#${w3}))
}

ensure_main_ref
report_session_state
exit 0
