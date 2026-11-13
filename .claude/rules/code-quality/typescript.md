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

## Run in this order after each write or edit

1. Run `npx biome check --write <file>` to format it, lint it and sort its imports.
2. Run `npx tsc --noEmit -p tsconfig.json` to type-check the project after a `.ts` or `.tsx` change.
3. Fix every finding, then run steps 1 and 2 again until both pass.
4. Read the file again before the next edit.
