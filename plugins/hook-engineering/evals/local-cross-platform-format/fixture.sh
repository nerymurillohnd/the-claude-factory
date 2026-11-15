#!/usr/bin/env bash
# Seeds a team repository whose shared .claude/settings.json is committed and whose team uses macOS and Windows.
set -euo pipefail
git init -q
mkdir -p .claude src
cat > .claude/settings.json << 'EOF'
{ "permissions": { "allow": ["Bash(npm test)"] } }
EOF
printf 'node_modules/\n' > .gitignore
cat > README.md << 'EOF'
# Acme web

The team develops on macOS and Windows (Git for Windows). Run `npm test` before you push.
EOF
cat > package.json << 'EOF'
{ "name": "acme-web", "private": true, "scripts": { "test": "node --test" }, "devDependencies": { "prettier": "3.6.2" } }
EOF
printf 'export const add = (a, b) => a + b;\n' > src/math.js
git add -A && git -c user.name=Fixture -c user.email=fixture@example.test commit -qm "Initial project"
