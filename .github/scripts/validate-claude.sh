#!/usr/bin/env bash
# Runs the official Claude Code validator on the marketplace, every plugin
# (manifest and components, skills included), then the mod tests of every plugin that
# ships them.
# --strict everywhere, except the marketplace while it lists zero plugins
# (an empty catalog is a validator warning, not a defect).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${root}"

command -v claude > /dev/null || {
  echo "✖ claude CLI not found (npm i -g @anthropic-ai/claude-code)"
  exit 1
}
version="$(claude --version)"
echo "Claude Code ${version}"

count="$(node -e 'console.log(require("./.claude-plugin/marketplace.json").plugins.length)')"
status=0

if [[ ${count} -gt 0 ]]; then
  claude plugin validate --strict . || status=1
else
  echo "ℹ Marketplace lists no plugins yet — validating without --strict"
  claude plugin validate . || status=1
fi

for dir in plugins/*/; do
  [[ -d ${dir} ]] || continue
  echo
  claude plugin validate --strict "${dir}" || status=1
  # A plugin that ships a mod ships its tests: they run in the engine's own test environment.
  tests=$(find "${dir}" \( -name '*.test.ts' -o -name '*.test.tsx' \) -print -quit)
  if [[ -n ${tests} ]]; then
    echo
    claude plugin test "${dir}" || status=1
  fi
done

exit "${status}"
