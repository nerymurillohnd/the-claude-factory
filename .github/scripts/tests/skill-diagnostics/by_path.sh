#!/usr/bin/env bash
# Runs skill-diagnostics' scripts the way Claude Code does: by their path,
# through the shebang, with whatever `python3` is first on PATH. CI runs this on
# Linux, macOS and Windows (Git Bash). Exits non-zero on the first failure.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
plugin="$root/plugins/skill-diagnostics"
checker="$plugin/skills/audit/scripts/check_skill.py"
hook="$plugin/hooks/skill_written.py"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

echo "python3: $(command -v python3) ($(python3 --version))"

# 1. Committed as executable, so it runs by path after a clone or install.
for script in "$checker" "$hook"; do
  mode=$(git -C "$root" ls-files -s -- "${script#"$root"/}" | cut -d' ' -f1)
  [ "$mode" = 100755 ] || { echo "FAIL: ${script#"$root"/} is $mode, not 100755"; exit 1; }
done

# 2. The checker, by path: inventory and check of a real skill, valid JSON, exit 0.
"$checker" --list "$plugin/skills/audit" >"$work/list.json"
"$checker" --target code "$plugin/skills/audit" >"$work/check.json"
python3 - "$work/list.json" "$work/check.json" <<'PY'
import json, sys
inventory = json.load(open(sys.argv[1], encoding="utf-8"))
report = json.load(open(sys.argv[2], encoding="utf-8"))
assert inventory["count"] >= 9 and not inventory["not_listed"], inventory
assert report["summary"]["error"] == 0, report["summary"]
print(f"checker: {inventory['count']} files listed, {report['summary']} on its own skill")
PY

# 3. The hook, by path: a SKILL.md write gets the audit offer.
mkdir -p "$work/skills/demo"
printf -- '---\nname: demo\ndescription: Demo. Use when asked.\n---\n\nDo it.\n' >"$work/skills/demo/SKILL.md"
native=$(cd "$work" && (pwd -W 2>/dev/null || pwd))  # Windows path on Git Bash, as Claude Code sends it
event=$(printf '{"session_id":"ci","hook_event_name":"PostToolUse","tool_name":"Write","tool_input":{"file_path":"%s/skills/demo/SKILL.md"}}' "$native")
out=$(printf '%s' "$event" | env -u CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE \
  CLAUDE_PLUGIN_ROOT="$plugin" CLAUDE_PLUGIN_DATA="$work/data" CLAUDE_CONFIG_DIR="$work/cfg" "$hook")
case "$out" in
  *"/skill-diagnostics:audit"*) echo "hook: offers the audit" ;;
  *) echo "FAIL: hook output: $out"; exit 1 ;;
esac
