#!/usr/bin/env bash
# CI step for a plugin's eval suite. Set the values marked <...> with the user.
# Needs: Claude Code on PATH, credentials in the environment (for example ANTHROPIC_API_KEY),
# python3, and this skill's scripts/gate_eval_result.py copied into the repository (path in GATE_SCRIPT).
set -uo pipefail

PLUGIN_DIR="${PLUGIN_DIR:-.}"
RESULT="${RESULT:-eval-results.json}"

# Target first: --tag, --allow-tools and --json take values, so a target after them is read as their value.
claude plugin eval "${PLUGIN_DIR}" \
  --trust-plugin \
  --json "${RESULT}" \
  --threshold "<0..1, default is 1.0>" \
  --model "<pinned agent model id>" \
  --judge-model "<pinned judge model id>" \
  --no-publish \
  --max-cost-usd "<ceiling>"
status=$?

case "${status}" in
  0) ;;
  1)
    echo "eval failed: a case below threshold, a load error, or a run that ended on an API error; read stderr and cases[].arms.*[].error" >&2
    exit 1
    ;;
  2)
    echo "partial run (cost ceiling or rejected credential); result marked partial: true, not used for the gate" >&2
    exit 2
    ;;
  *)
    echo "eval interrupted or terminated (exit ${status})" >&2
    exit "${status}"
    ;;
esac

# The delta never changes the exit code above, so gate on it from the JSON result.
python3 "${GATE_SCRIPT:-./gate_eval_result.py}" "${RESULT}" --min-mean-delta "<minimum mean delta>"
