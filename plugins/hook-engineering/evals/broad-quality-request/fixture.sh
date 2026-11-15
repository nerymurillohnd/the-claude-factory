#!/usr/bin/env bash
# Seeds a small project with no hooks, no linter and no CI.
set -euo pipefail
git init -q
mkdir -p src
printf '{ "name": "acme-api", "private": true, "type": "module", "scripts": { "test": "node --test" } }\n' > package.json
printf 'export function handler(req) {\n  return { status: 200, body: req.body }\n}\n' > src/handler.js
git add -A && git -c user.name=Fixture -c user.email=fixture@example.test commit -qm "Initial project"
