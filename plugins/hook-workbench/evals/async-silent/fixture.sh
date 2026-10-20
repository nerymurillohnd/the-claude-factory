#!/usr/bin/env bash
# Seeds a project whose async PostToolUse hook prints a progress line before its
# pretty-printed JSON, so Claude Code reads the output as plain text and drops it.
set -euo pipefail
mkdir -p .claude/hooks
cat > .claude/settings.json << 'JSON'
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/run-tests-async.sh",
            "args": [],
            "async": true
          }
        ]
      }
    ]
  }
}
JSON
cat > .claude/hooks/run-tests-async.sh << 'SH'
#!/usr/bin/env bash
input=$(cat)
file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')
echo "Running tests for $file_path..."
if result=$(npm test 2>&1); then
  msg="Tests passed after editing $file_path"
else
  msg="Tests failed after editing $file_path: $result"
fi
jq -n --arg msg "$msg" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $msg}}'
SH
chmod +x .claude/hooks/run-tests-async.sh
