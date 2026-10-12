#!/usr/bin/env bash
# Runs skill-diagnostics' hook the way Claude Code does: by its path,
# through the shebang, with whatever `python3` is first on PATH. CI runs this on
# Linux, macOS and Windows (Git Bash). Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
plugin="${root}/plugins/skill-diagnostics"
hook="${plugin}/hooks/skill_written.py"
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

# 2. The hook, by path: a SKILL.md write gets the audit offer.
mkdir -p "${work}/skills/demo"
printf -- '---\nname: demo\ndescription: Demo. Use when asked.\n---\n\nDo it.\n' > "${work}/skills/demo/SKILL.md"
native=$(cd "${work}" && (pwd -W 2> /dev/null || pwd) ) # Windows path on Git Bash, as Claude Code sends it
event=$(printf '{"session_id":"ci","hook_event_name":"PostToolUse","tool_name":"Write","tool_input":{"file_path":"%s/skills/demo/SKILL.md"}}' "${native}")
out=$(printf '%s' "${event}" | env -u CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE \
  CLAUDE_PLUGIN_ROOT="${plugin}" CLAUDE_PLUGIN_DATA="${work}/data" CLAUDE_CONFIG_DIR="${work}/cfg" "${hook}")
case "${out}" in
  *"/skill-diagnostics:audit"*) echo "hook: offers the audit" ;;
  *)
    echo "FAIL: hook output: ${out}"
    exit 1
    ;;
esac
