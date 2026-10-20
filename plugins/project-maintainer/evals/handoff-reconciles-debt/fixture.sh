#!/usr/bin/env bash
# Seeds a git repository with a previous handoff and the records: DEBT-001 and DEBT-002 pending, DEBT-003 closed.
set -euo pipefail
git init -q
mkdir -p .claude/session-handoff .claude/maintainer/technical-debt
cat > .claude/session-handoff/2026-03-01-1200.md << 'EOF'
# Session handoff

Project: /workspace
Written: 2026-03-01 12:00 UTC
Previous handoff: No previous handoff.
Branch: main
HEAD: none

## Current state
- Uncommitted: None known.

## Open items
1. [2026-02-10] DEBT-003 Report totals are off by one cent: Pending; closes when the rounding rule is decided. First action: ask finance

## Context for the next session
- Recommendation: none

## Decisions
- None known.

## Done this session
- Set up the repository.

Previous handoff items:
No previous handoff.

## Unverified and gaps
- None known.
EOF
cat > .claude/maintainer/technical-debt/pending-debt.md << 'EOF'
# 🧾 Pending Debt

## 📋 Index

| ID | Title | Status |
| --- | --- | --- |
| DEBT-001 | Nightly export fails over 2 GB | 🟡 Pending |
| DEBT-002 | Slow search on large catalogs | 🟠 Blocked |

## 📂 Open items

### DEBT-001 — Nightly export fails over 2 GB

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | reliability |
| **Owner** | unassigned |
| **Logged** | 2026-02-20 |

- **Impact / risk:** large customers get no nightly export.
- **Why it is not fixed now:** it waits on the vendor's new API.
- **Next action:** ask the vendor for a release date.
- **Review condition:** the vendor ships the new API.

### DEBT-002 — Slow search on large catalogs

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | performance |
| **Owner** | unassigned |
| **Logged** | 2026-02-25 |

- **Impact / risk:** search takes 8 seconds above 100k products.
- **Why it is not fixed now:** it waits on a decision about a search service.
- **Next action:** compare two hosted search services.
- **Review condition:** the owner picks a search service.
EOF
cat > .claude/maintainer/technical-debt/closed-debt.md << 'EOF'
# ✅ Closed Debt

## 📚 Index

| Date | ID | Outcome | Closure | Superseded by |
| --- | --- | --- | --- | --- |
| 2026-03-02 | DEBT-003 | resolved | Rounding rule fixed | none |

## 🏁 Closed items

### DEBT-003 — Rounding rule fixed

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-03-02 |
| **Logged on** | 2026-02-10 |
| **Owner** | unassigned |

- **Superseded by:** none
EOF
