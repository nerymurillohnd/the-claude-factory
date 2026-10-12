#!/usr/bin/env bash
# Seeds a realistic skill with three subtle cross-file defects:
# a placeholder named differently in the reference that defines it,
# a script flag the script does not accept, and a step that uses a value
# only a later step produces.
set -euo pipefail
d=skills/invoice-note
mkdir -p "$d/assets" "$d/references" "$d/scripts"
cat >"$d/SKILL.md" <<'SKILL'
---
name: invoice-note
description: Writes a payment reminder for an overdue invoice and logs it. Use when the user asks to chase an unpaid invoice.
---

# Invoice note

Input: the invoice the user gives (number, client, issue date, amount).

1. Read [fields.md](references/fields.md) for how each template value is computed.
2. Copy [template.md](assets/template.md) and fill every placeholder; include the `reminder_id` in the subject line.
3. Check the amount with `${CLAUDE_SKILL_DIR}/scripts/amount.py --format csv <amount>`; stop if it exits non-zero.
4. Save the note as `outbox/<invoice_id>.md` and log it with `${CLAUDE_SKILL_DIR}/scripts/log.py`, which prints the new `reminder_id`.

Done when the note is in `outbox/` and the log has its line.
SKILL
cat >"$d/assets/template.md" <<'TEMPLATE'
Subject: Reminder {{reminder_id}} for invoice {{invoice_id}}

Dear {{client_name}},

Invoice {{invoice_id}} is {{days_late}} days overdue. Please pay {{amount}} by {{grace_date}}.
TEMPLATE
cat >"$d/references/fields.md" <<'REF'
# Template fields

| Field | Source |
| --- | --- |
| client_name | The client on the invoice |
| invoice_id | The invoice number |
| days_late | Today minus the issue date minus 30 |
| amount | The invoice amount, two decimals |
| grace-date | Today plus 7 days, as YYYY-MM-DD |
REF
cat >"$d/scripts/amount.py" <<'PY'
#!/usr/bin/env python3
"""Validate an invoice amount. Usage: amount.py [--format json|text] AMOUNT"""
import argparse, json, sys
p = argparse.ArgumentParser()
p.add_argument("--format", choices=("json", "text"), default="text")
p.add_argument("amount")
a = p.parse_args()
ok = a.amount.replace(".", "", 1).isdigit()
print(json.dumps({"ok": ok}) if a.format == "json" else ("ok" if ok else "invalid"))
sys.exit(0 if ok else 1)
PY
cat >"$d/scripts/log.py" <<'PY'
#!/usr/bin/env python3
"""Append a reminder to the log and print its new reminder_id."""
import time
rid = f"R{int(time.time())}"
with open("reminders.log", "a", encoding="utf-8") as fh:
    fh.write(rid + "\n")
print(rid)
PY
chmod 755 "$d/scripts/"*.py
