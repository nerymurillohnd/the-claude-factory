#!/usr/bin/env bash
# Where every local and remote-tracking branch stands against a base ref.
#
# Usage: branch-states.sh REPO BASE_REF OUT_FILE
#
# Writes one sorted line per branch to OUT_FILE: state, ref, +ahead, -behind, SHA, separated by
# tabs. States: merged (the tip is reachable from the base), in-base (merging it changes
# nothing), differs, conflicts, unrelated (no shared history), error(n) (git failed).
# merge-tree writes tree objects, so it writes them to a temporary object store that is removed
# on exit; the repository gets nothing new.
# Exit 0 = written, 1 = BASE_REF does not resolve, 2 = usage error.
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: branch-states.sh REPO BASE_REF OUT_FILE" >&2
  exit 2
fi
repo=$1
base=$2
out_file=$3

if ! base_sha=$(git -C "${repo}" rev-parse --verify --quiet "${base}^{commit}"); then
  echo "branch-states: base ${base} does not resolve to a commit in ${repo}" >&2
  exit 1
fi
base_tree=$(git -C "${repo}" rev-parse "${base}^{tree}")
shared=$(git -C "${repo}" rev-parse --path-format=absolute --git-path objects)
store=$(mktemp -d)
trap 'rm -rf "${store}"' EXIT

state_of() {
  local sha=$1 ahead=$2 merged code
  if [[ ${ahead} == 0 ]]; then
    echo merged
    return
  fi
  if ! git -C "${repo}" merge-base "${base_sha}" "${sha}" > /dev/null 2>&1; then
    echo unrelated
    return
  fi
  code=0
  merged=$(GIT_OBJECT_DIRECTORY="${store}" GIT_ALTERNATE_OBJECT_DIRECTORIES="${shared}" \
    git -C "${repo}" merge-tree --write-tree --no-messages "${base_sha}" "${sha}" 2> /dev/null) || code=$?
  if [[ ${code} == 1 ]]; then
    echo conflicts
  elif [[ ${code} != 0 ]]; then
    echo "error(${code})"
  elif [[ ${merged%%$'\n'*} == "${base_tree}" ]]; then
    echo in-base
  else
    echo differs
  fi
}

refs="${store}/refs"
git -C "${repo}" for-each-ref --format='%(refname)' refs/heads refs/remotes > "${refs}"
lines="${store}/lines"
: > "${lines}"
while IFS= read -r ref; do
  if [[ ${ref} == refs/remotes/*/HEAD ]]; then
    continue
  fi
  sha=$(git -C "${repo}" rev-parse "${ref}^{commit}")
  counts=$(git -C "${repo}" rev-list --left-right --count "${base_sha}...${sha}")
  behind=${counts%%[[:space:]]*}
  ahead=${counts##*[[:space:]]}
  state=$(state_of "${sha}" "${ahead}")
  printf '%s\t%s\t+%s\t-%s\t%s\n' "${state}" "${ref}" "${ahead}" "${behind}" "${sha}" >> "${lines}"
done < "${refs}"
sort "${lines}" > "${out_file}"
