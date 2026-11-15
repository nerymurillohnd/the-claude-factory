#!/usr/bin/env bash
# Seeds a team project whose README pins Claude Code at 2.1.290, before onFailure (2.1.295).
set -euo pipefail
git init -q
mkdir -p .claude src
printf '{ "permissions": { "allow": ["Bash(npm test)"] } }\n' > .claude/settings.json
cat > README.md << 'MD'
# Acme billing

IT pins Claude Code at 2.1.290 on every developer machine and in CI; nobody can update it.
The team works on macOS and Linux.
MD
printf 'export const total = (items) => items.reduce((sum, i) => sum + i.price, 0);\n' > src/total.js
git add -A && git -c user.name=Fixture -c user.email=fixture@example.test commit -qm "Initial project"
