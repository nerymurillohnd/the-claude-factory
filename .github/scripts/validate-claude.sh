#!/usr/bin/env bash
# Runs the official Claude Code validator on the marketplace, every plugin
# (manifest and components, skills included) and the repo's own .claude/.
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

# The maintainers' own skills, agents and commands: frontmatter that does not
# parse leaves a skill without metadata, so Claude can't match its description.
echo
claude plugin validate --strict .claude || status=1

for dir in plugins/*/; do
  [[ -d ${dir} ]] || continue
  echo
  claude plugin validate --strict "${dir}" || status=1
done

exit "${status}"
