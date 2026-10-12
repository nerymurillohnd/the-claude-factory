---
type: llm
---

The skill has three planted defects:
(a) assets/template.md uses `{{grace_date}}` but references/fields.md defines `grace-date` (hyphen), so the value has no matching definition;
(b) SKILL.md step 3 calls `scripts/amount.py --format csv`, but the script only accepts `json` or `text`, so the step always fails;
(c) SKILL.md step 2 fills `reminder_id`, but that value is produced only by `scripts/log.py` in step 4.

PASS if the reply says the skill is not ready AND correctly identifies at least two of (a), (b), (c), each tied to a file.
FAIL if it calls the skill ready, or identifies fewer than two of them.
