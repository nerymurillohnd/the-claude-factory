#!/usr/bin/env bash
# Seeds a git repository whose pending-debt.md holds DEBT-001 and has no closed ledger yet.
set -euo pipefail
git init -q
mkdir -p .claude/maintainer/technical-debt
cat > .claude/maintainer/technical-debt/pending-debt.md << 'EOF'
# 🧾 Pending Debt

## 📋 Index

| ID | Title | Status |
| --- | --- | --- |
| DEBT-001 | Nightly export fails over 2 GB | 🟡 Pending |

## 📂 Open items

### DEBT-001 — Nightly export fails over 2 GB

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | reliability |
| **Owner** | unassigned |
| **Logged** | 2026-02-20 |

#### 🔎 Evidence

- **Confirmed facts:** jobs/export.sh exits with an out-of-memory error on files over 2 GB.
- **Inferences:** none
- **Open questions:** none

#### 📈 Impact and next step

- **Impact / risk:** large customers get no nightly export.
- **Why it is not fixed now:** it waits on the vendor's new API.
- **Next action:** ask the vendor for a release date.
- **Review condition:** the vendor ships the new API.
- **Related records:** none
EOF
