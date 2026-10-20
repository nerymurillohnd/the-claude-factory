#!/usr/bin/env bash
# Seeds a git repository with one accepted ADR.
set -euo pipefail
git init -q
mkdir -p .claude/maintainer/decisions
cat > .claude/maintainer/decisions/ADR_2026-03-14_keep-sessions-in-postgres.md << 'EOF'
---
status: accepted
date: 2026-03-14
decision-makers:
  - "Project owner"
supersedes: none
superseded-by: none
---

# Keep sessions in Postgres

## Scope

User sessions of the web app.

## Context and problem statement

Where should user sessions live?

## Decision drivers

- One store is enough at the current traffic.

## Considered options

- **Postgres**: chosen.
- **Redis**: rejected because it adds a second service to run.

## Decision outcome

Chosen option: **Postgres**, because it avoids a second service.

### Consequences

- Good, because there is one store to operate.
- Bad, because session reads share the database load.
EOF
