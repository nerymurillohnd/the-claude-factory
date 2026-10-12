#!/usr/bin/env bash
# Seeds a skill whose two files disagree on the date format of the file it
# produces: a defect that changes the output on every run.
set -euo pipefail
d=skills/expense-export
mkdir -p "$d/references"
cat >"$d/SKILL.md" <<'SKILL'
---
name: expense-export
description: Exports the expenses in expenses.json to a CSV file for the accountant. Use when the user asks to export or prepare expenses for accounting.
---

# Expense export

1. Read `expenses.json` from the working directory. Missing: say so and stop.
2. Write `expenses.csv` with the columns and rules in [format.md](references/format.md).
3. Write every date as YYYY-MM-DD.
4. Reply with the path and the number of rows written.
SKILL
cat >"$d/references/format.md" <<'REF'
# CSV format

Columns, in this order: date, vendor, category, amount.

- date: DD/MM/YYYY, the only format the accountant's software imports.
- vendor: as written in the source, trimmed.
- category: travel, meals or office; anything else becomes other.
- amount: two decimals, dot as the decimal separator, no currency sign.
REF
