---
description: "Gate mode (the default), full half, CI only: once Claude writes SKILL.md into a nine-file skill, the gate must make it run the whole audit before the turn ends (the four scripts, all six agents, a recorded verdict) without the user asking, and without the Stop hook's give-up warning. The fixture is the seeded-defect skill without its SKILL.md. Plugin options can't be set in an eval run, so this is the only mode an eval can reach; by_path.sh covers suggest and off. Grants needed: claude plugin eval . --case '<name>' --trust-plugin --scaffold --allow-tools Write Edit 'Bash(python3 *)' 'Bash(claude --version)' 'WebFetch(domain:code.claude.com)' 'WebFetch(domain:platform.claude.com)' 'WebFetch(domain:support.claude.com)' 'WebFetch(domain:claude.com)' 'WebFetch(domain:agentskills.io)' 'WebFetch(domain:github.com)' 'WebFetch(domain:raw.githubusercontent.com)'; without the WebFetch grants the verifier cannot reach the official sources and the verdict is provisional. Bash forces the OS sandbox (bubblewrap and socat on Linux)."
tags: [hook, gate, agents]
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Agent, Write, Bash]
---

Write the file skills/invoice-pack/SKILL.md with exactly the content of this code block (without the fence lines), then tell me you are done. The other files of the skill are already in place.

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
