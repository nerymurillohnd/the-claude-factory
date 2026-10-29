#!/usr/bin/env bash
# Verify the cleanup backup (action A-01) before any other action runs.
#
# Usage: verify-backup.sh REPO BACKUP_DIR
#
# Runs, in order: bundle verify, a non-zero head count, the checksum written to
# all.bundle.sha256, a restore clone into BACKUP_DIR/restore-test.git, fsck --connectivity-only
# on it, the restored refs against the live refs, apply --check for each uncommitted-*.patch and
# tar -tf for each untracked-*.tar. Prints PASS <check> or FAIL <check> with the raw output, and
# stops at the first failure.
# Exit 0 = every check passed, 1 = a check failed, 2 = usage error.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: verify-backup.sh REPO BACKUP_DIR" >&2
  exit 2
fi
repo=$1
dir=$2
bundle="${dir}/all.bundle"
restore="${dir}/restore-test.git"
out=$(mktemp)
trap 'rm -f "${out}"' EXIT

# check <name> <command...>: runs the command, prints PASS or FAIL with its output.
check() {
  local name=$1
  shift
  if "$@" > "${out}" 2>&1; then
    echo "PASS ${name}"
  else
    echo "FAIL ${name}"
    sed 's/^/  /' "${out}"
    exit 1
  fi
}

has_heads() {
  local heads
  heads=$(git -C "${repo}" bundle list-heads "${bundle}")
  [[ -n ${heads} ]] || {
    echo "the bundle lists no heads"
    return 1
  }
}

write_checksum() {
  if command -v shasum > /dev/null 2>&1; then
    shasum -a 256 "${bundle}" > "${bundle}.sha256"
  else
    sha256sum "${bundle}" > "${bundle}.sha256"
  fi
  [[ -s "${bundle}.sha256" ]]
}

restore_clone() {
  if [[ -e ${restore} ]]; then
    echo "${restore} already exists; remove it before verifying again"
    return 1
  fi
  git clone --quiet --mirror "${bundle}" "${restore}"
}

ref_list() {
  git -C "$1" for-each-ref --format='%(refname) %(objectname)' \
    refs/heads refs/tags refs/remotes refs/repo-cleanup-backup | grep -v '/HEAD ' | sort || true
}

same_refs() {
  ref_list "${repo}" > "${dir}/live-refs.txt"
  ref_list "${restore}" > "${dir}/restored-refs.txt"
  diff "${dir}/live-refs.txt" "${dir}/restored-refs.txt"
}

check "bundle verify" git -C "${repo}" bundle verify "${bundle}"
check "head count" has_heads
check "checksum written" write_checksum
check "restore clone" restore_clone
check "fsck --connectivity-only" git -C "${restore}" fsck --connectivity-only
check "refs match" same_refs
for patch in "${dir}"/uncommitted-*.patch; do
  [[ -e ${patch} ]] || continue
  check "apply --check ${patch##*/}" git -C "${repo}" apply --check "${patch}"
done
for archive in "${dir}"/untracked-*.tar; do
  [[ -e ${archive} ]] || continue
  check "tar -tf ${archive##*/}" tar -tf "${archive}"
done
