#!/usr/bin/env bash
# Seeds a multi-file skill whose defect only shows when every file is read in
# full: the renderer script rejects one language that the country table, a
# template and SKILL.md all treat as supported.
set -euo pipefail
d=skills/invoice-pack
mkdir -p "${d}/references" "${d}/assets" "${d}/scripts"

cat > "${d}/SKILL.md" << 'EOF'
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
EOF

cat > "${d}/references/countries.md" << 'EOF'
# Countries

| Country | Language code | Currency |
| :-- | :-- | :-- |
| United States | en | USD |
| Canada | en | CAD |
| United Kingdom | en | GBP |
| France | fr | EUR |
| Belgium | fr | EUR |
| Germany | de | EUR |
| Austria | de | EUR |
| Spain | es | EUR |
| Mexico | es | MXN |

A country not in this table: use `en` and USD, and say so in the reply.
EOF

cat > "${d}/references/tax-rules.md" << 'EOF'
# Tax rules

- United States and Canada: no tax line; the order's `tax` field is shown as given.
- United Kingdom: VAT 20% on the subtotal.
- EU countries: VAT at the order's `vat_rate`, shown as a separate line.
- Mexico: IVA 16% on the subtotal.

Round each tax line half up to two decimals before adding it to the total.
EOF

cat > "${d}/references/currency.md" << 'EOF'
# Currency formats

| Currency | Example |
| :-- | :-- |
| USD, CAD | $1,234.50 |
| GBP | £1,234.50 |
| EUR | 1.234,50 € |
| MXN | $1,234.50 MXN |
EOF

for lang in en fr de es; do
  case ${lang} in
    en)
      title="Invoice"
      total="Total due"
      ;;
    fr)
      title="Facture"
      total="Total à payer"
      ;;
    de)
      title="Rechnung"
      total="Gesamtbetrag"
      ;;
    es)
      title="Factura"
      total="Total a pagar"
      ;;
    *) exit 1 ;;
  esac
  cat > "${d}/assets/invoice-${lang}.md" << EOF
# ${title} {{number}}

{{customer}}
{{date}}

{{lines}}

${total}: {{total}}
EOF
done

cat > "${d}/scripts/render.py" << 'EOF'
#!/usr/bin/env python3
"""Render an invoice from an order JSON file and a language template.

The template is assets/invoice-<lang>.md next to this script's folder. Each
{{field}} in it is replaced from the order; {{lines}} becomes one Markdown
line per item.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def money(value: float) -> str:
    return f"{value:,.2f}"


def item_lines(items: list[dict]) -> str:
    rows = []
    for item in items:
        qty = item.get("qty", 1)
        price = float(item["price"])
        rows.append(f"- {item['name']} × {qty}: {money(qty * price)}")
    return "\n".join(rows)


def fill(template: str, order: dict) -> str:
    values = {
        "number": str(order["number"]),
        "customer": order["customer"]["name"],
        "date": order["date"],
        "lines": item_lines(order["items"]),
        "total": money(float(order["total"])),
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", required=True, choices=["en", "fr", "de"])
    parser.add_argument("--order", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    order = json.loads(args.order.read_text(encoding="utf-8"))
    template = (ASSETS / f"invoice-{args.lang}.md").read_text(encoding="utf-8")
    args.out.write_text(fill(template, order), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
EOF

cat > "${d}/scripts/check_totals.py" << 'EOF'
#!/usr/bin/env python3
"""Print OK when an invoice file has a total line, or what is missing."""

import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
labels = ("Total due:", "Total à payer:", "Gesamtbetrag:", "Total a pagar:")
print("OK" if any(label in text for label in labels) else "missing total line")
EOF
chmod 755 "${d}/scripts/render.py" "${d}/scripts/check_totals.py"
