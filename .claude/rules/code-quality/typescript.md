---
paths:
  - "**/*.{js,cjs,mjs,ts,cts,mts,tsx}"
  - "**/*.{json,jsonc,yml,yaml}"
  - "/tsconfig*.json"
  - "/biome.jsonc"
---

# TypeScript, JavaScript, JSON and YAML

- Load the `typescript6-lsp-intelligence:ts-lifecycle` skill for TypeScript and JavaScript.
- Use only Biome and `tsc`; never Prettier or ESLint.
- Fix every finding before moving on; never leave one as debt.
- Add a `biome-ignore` comment only for a proven false positive, with its reason and the owner's approval.

## After each write or edit, run in order

1. Format, lint and sort imports: `npx biome check --write <file>`.
2. Type-check, after a `.ts` or `.tsx` change: `npx tsc --noEmit -p tsconfig.json`.
3. Fix every finding, then repeat steps 1 and 2 until both pass.
4. Read the file again before the next edit.
