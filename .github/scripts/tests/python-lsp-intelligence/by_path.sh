#!/usr/bin/env bash
# Runs python-lsp-intelligence's hook the way Claude Code does: by its path, through the
# shebang, with whatever python3 is first on PATH. CI runs this on Linux, macOS and Windows
# (Git Bash). Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
hook="${root}/plugins/python-lsp-intelligence/hooks/check.py"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

python=$(command -v python3)
version=$(python3 --version)
echo "python3: ${python} (${version})"

# 1. Committed as executable, so it runs by path after a clone or install.
mode=$(git -C "${root}" ls-files -s -- "${hook#"${root}"/}" | cut -d' ' -f1)
[[ ${mode} == 100755 ]] || {
  echo "FAIL: ${hook#"${root}"/} is ${mode}, not 100755"
  exit 1
}

# 2. The hook, by path: an edit of a non-Python file produces no output and exit 0.
printf '# hi\n' > "${work}/notes.md"
native=$(cd "${work}" && (pwd -W 2> /dev/null || pwd) ) # Windows path on Git Bash, as Claude Code sends it
event=$(printf '{"hook_event_name":"PostToolUse","tool_name":"Edit","tool_input":{"file_path":"%s/notes.md"}}' "${native}")
out=$(printf '%s' "${event}" | CLAUDE_PLUGIN_ROOT="${root}/plugins/python-lsp-intelligence" "${hook}")
[[ -z ${out} ]] || {
  echo "FAIL: a Markdown edit produced output: ${out}"
  exit 1
}
echo "hook: runs by path and ignores non-Python files"
