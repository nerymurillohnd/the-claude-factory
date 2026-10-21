#!/usr/bin/env bash
# Seeds three in-scope defects: an agent hook on PermissionRequest (skipped),
# a prompt hook on SessionStart (unsupported) and async on a prompt hook (no effect).
set -euo pipefail
mkdir -p .claude
cat > .claude/settings.json << 'JSON'
{
  "hooks": {
    "PermissionRequest": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Deny the request if it touches production config. $ARGUMENTS"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check the repository is on a feature branch. $ARGUMENTS"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check the written file has no secrets. $ARGUMENTS",
            "async": true,
            "timeout": 30
          }
        ]
      }
    ]
  }
}
JSON
