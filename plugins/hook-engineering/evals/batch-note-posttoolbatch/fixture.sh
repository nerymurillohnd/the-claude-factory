#!/usr/bin/env bash
# Seeds a project with a few files Claude may read in one batch, and no hooks.
set -euo pipefail
git init -q
mkdir -p ledger
for f in accounts transactions reports; do printf '# %s module\n' "${f}" > "ledger/${f}.py"; done
git add -A && git -c user.name=Fixture -c user.email=fixture@example.test commit -qm "Initial project"
