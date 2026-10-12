---
type: llm
weight: 2
---

In this skill, scripts/render.py only accepts `--lang` values en, fr and de, while references/countries.md maps Spain and Mexico to `es` (and an `es` template exists), so rendering any invoice for Spain or Mexico fails.

PASS if the reply reports that the renderer rejects `es` (or that Spanish, Spain or Mexico invoices cannot be rendered) because of the script's accepted languages.
FAIL if it does not report this, including when it calls the skill ready.
