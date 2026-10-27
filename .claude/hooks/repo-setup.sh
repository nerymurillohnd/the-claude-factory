#!/usr/bin/env bash
set -euo pipefail
# Repository setup, run by checkout.sh at every session start: installs the dependencies, runs the
# validators, lists outdated packages, and prints the repository's tool versions beside the global
# ones. A failing step stops the script with its own error.

root="${CLAUDE_PROJECT_DIR:-${PWD}}"
cd "${root}"

echo "== npm install"
npm install --no-audit --no-fund

echo "== validators"
npm run --silent validate

echo "== npm outdated"
# npm outdated exits 1 when a package is outdated: that is the report, not a failure.
npm outdated || true

echo "== repo vs global"
npm ls --depth=0
repo_biome="$(npx --no-install biome --version)"
global_biome="$(biome --version)"
repo_tsc="$(npx --no-install tsc --version)"
global_tsc="$(tsc --version)"
global_node="$(node --version)"
echo "biome: repo ${repo_biome} | global ${global_biome}"
echo "tsc:   repo ${repo_tsc} | global ${global_tsc}"
echo "node:  global ${global_node}"
