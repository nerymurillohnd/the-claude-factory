#!/usr/bin/env bash
# Runs in the empty workspace before each run, only with --scaffold, with a minimal environment and a 120-second limit.
# Write files and git state only: project configuration written here is not loaded.
set -euo pipefail
mkdir -p src
printf '%s\n' 'example content' > src/example.txt
