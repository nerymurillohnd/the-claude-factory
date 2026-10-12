---
description: "Case 2, second half (hook-offer proves the hook fires): once the user accepts the offer, the audit runs on the written skill: the skill folder's full inventory, and both lens agents told to read every file. Plugin options can't be set in an eval run, so the hook runs in its default suggest mode, and the user accepts the offer in advance, as a user would by answering yes. Without the plugin no hook fires and no audit follows."
tags: [hook, agents]
max_turns: 80
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Write the file skills/invoice-pack/SKILL.md with exactly the content of this code block (without the fence lines). The other files of the skill are already in place. If you are offered a check of the skill after writing it, go ahead with the check.

~~~markdown
---
name: invoice-pack
description: Renders a customer invoice in the customer's language from an order file, with tax and currency rules applied. Use when the user asks to create, render or send an invoice for an order.
---

# Invoice pack

Input: the path of one order JSON file. No path: ask for it.

1. Read the order. Find the customer's country in [countries.md](references/countries.md) to get the language code and the currency.
2. Apply [tax-rules.md](references/tax-rules.md) for that country, and format money with [currency.md](references/currency.md).
3. Render the invoice:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/render.py --lang <code> --order <order.json> --out invoice.md
   ```

4. Check the totals:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/check_totals.py invoice.md
   ```

5. Reply with the path of `invoice.md`, the language used, and the grand total.
~~~
