---
name: invoice-totals
description: Checks that every invoice in a CSV export adds up and lists the ones that don't. Use when the user asks to check, reconcile or validate invoice totals.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/check_totals.py *)
---

Requires Python 3.9+ as `python3`; standard library only.

## Scripts

- `scripts/check_totals.py`: run it, don't read it. Prints a JSON report and exits 0 whenever it printed one, with the failing invoices inside; exits 2 on unreadable input.

## Steps

1. Run `${CLAUDE_SKILL_DIR}/scripts/check_totals.py <csv-file>`.
2. Exit 2: read the error, correct the path or the file, and run it again.
3. Report each invoice under `failing`, with its expected and actual total.
