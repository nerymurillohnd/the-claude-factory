#!/usr/bin/env bash
# Runs the full eval suite (both arms, 3 runs per case) of every plugin that
# ships an evals/ folder, with the tool grants and cost ceiling set for it in
# .github/scripts/evals-config.json. ONLY=<plugin> limits the run to one plugin.
# Exits non-zero when any suite fails or a plugin with evals has no config.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
config=.github/scripts/evals-config.json
mkdir -p eval-results
status=0
ran=0
for dir in plugins/*/; do
  name=$(basename "$dir")
  [ -d "$dir/evals" ] || continue
  [ "${ONLY:-all}" = all ] || [ "$ONLY" = "$name" ] || continue
  if ! node -e 'process.exit(require(process.argv[1])[process.argv[2]] ? 0 : 1)' "./$config" "$name"; then
    echo "::error::$name ships evals but has no entry in $config"
    status=1
    continue
  fi
  mapfile -t tools < <(node -e 'for (const t of require(process.argv[1])[process.argv[2]].allow_tools) console.log(t)' "./$config" "$name")
  cap=$(node -e 'console.log(require(process.argv[1])[process.argv[2]].max_cost_usd)' "./$config" "$name")
  echo "::group::$name (cap \$$cap)"
  ran=1
  # Granted Bash runs in a sandbox that can't read the home directory, and a CI
  # checkout lives under it (/home/runner/work): evaluate a copy outside it.
  copy="$(mktemp -d /tmp/plugin-eval.XXXXXX)/$name"
  cp -R "$dir" "$copy"
  claude plugin eval "$copy" \
    --trust-plugin --scaffold --no-publish \
    --model "${EVAL_MODEL:?}" --judge-model "${EVAL_JUDGE_MODEL:?}" \
    --max-cost-usd "$cap" \
    --json "$root/eval-results/$name.json" \
    --output-dir "$root/eval-results/$name" \
    --allow-tools "${tools[@]}" || status=1
  echo "::endgroup::"
done
[ "$ran" = 1 ] || echo "No plugin with an eval suite matched ONLY=${ONLY:-all}."
exit "$status"
