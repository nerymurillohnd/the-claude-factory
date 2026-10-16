#!/usr/bin/env bash
# Runs the git-cleanup scripts the way Claude Code does: by their path, through the shebang,
# with whatever `python3` is first on PATH. CI runs this on Linux and macOS. Exits non-zero
# on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
plugin="${root}/plugins/github-operations"
guard="${plugin}/hooks/git_cleanup_guard.py"
inventory="${plugin}/skills/git-cleanup/scripts/inventory.py"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

python=$(command -v python3)
version=$(python3 --version)
echo "python3: ${python} (${version})"

# 1. Committed as executable, so they run by path after a clone or install.
for script in "${guard}" "${inventory}"; do
  mode=$(git -C "${root}" ls-files -s -- "${script#"${root}"/}" | cut -d' ' -f1)
  [[ ${mode} == 100755 ]] || {
    echo "FAIL: ${script#"${root}"/} is ${mode}, not 100755"
    exit 1
  }
done

# 2. The guard, by path: a force-push is denied, a status passes.
event='{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git push --force origin x"}}'
out=$(printf '%s' "${event}" | "${guard}")
case "${out}" in
  *'"permissionDecision": "deny"'*) echo "guard: denies a force-push" ;;
  *)
    echo "FAIL: guard output: ${out}"
    exit 1
    ;;
esac
event='{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git status"}}'
out=$(printf '%s' "${event}" | "${guard}")
[[ -z ${out} ]] || {
  echo "FAIL: guard objected to git status: ${out}"
  exit 1
}
echo "guard: lets git status through"

# 3. The inventory, by path, on a throwaway repository.
git init -q -b main "${work}/repo"
git -C "${work}/repo" -c user.name=ci -c user.email=ci@example.com commit -q --allow-empty -m init
out=$("${inventory}" --repo "${work}/repo" --section context)
case "${out}" in
  *'"main_exists": true'*) echo "inventory: reads a repository" ;;
  *)
    echo "FAIL: inventory output: ${out}"
    exit 1
    ;;
esac
