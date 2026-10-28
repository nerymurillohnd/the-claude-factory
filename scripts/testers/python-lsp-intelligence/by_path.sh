#!/usr/bin/env bash
# Runs python-lsp-intelligence's hook the way Claude Code does: the command declared in
# hooks/hooks.json, through bash, with whatever python3 is first on PATH. CI does not run it;
# the pre-push gate runs it locally. Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
plugin="${root}/plugins/python-lsp-intelligence"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

python=$(command -v python3)
version=$(python3 --version)
echo "python3: ${python} (${version})"

# 1. Every handler runs in shell form through bash and declares the same command.
command=$(
  python3 - "${plugin}/hooks/hooks.json" << 'EOF'
import json, sys
handlers = [h for groups in json.load(open(sys.argv[1]))["hooks"].values() for g in groups for h in g["hooks"]]
bad = [h["command"] for h in handlers if h.get("shell") != "bash" or "args" in h]
commands = {h["command"] for h in handlers}
if bad or len(commands) != 1:
    sys.exit(f"FAIL: handlers not in shell form through bash, or commands differ: {bad or sorted(commands)}")
print(commands.pop())
EOF
)
echo "command: ${command}"

# 2. The declared command: an edit of a non-Python file produces no output and exit 0.
printf '# hi\n' > "${work}/notes.md"
native=$(cd "${work}" && (pwd -W 2> /dev/null || pwd) ) # Windows path on Git Bash, as Claude Code sends it
event=$(printf '{"hook_event_name":"PostToolUse","tool_name":"Edit","tool_input":{"file_path":"%s/notes.md"}}' "${native}")
out=$(printf '%s' "${event}" | CLAUDE_PLUGIN_ROOT="${plugin}" bash -c "${command}")
[[ -z ${out} ]] || {
  echo "FAIL: a Markdown edit produced output: ${out}"
  exit 1
}
echo "hook: the declared command runs and ignores non-Python files"
