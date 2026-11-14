---
paths:
  - "**/*.{js,cjs,mjs,ts,cts,mts,tsx}"
  - "**/*.{json,jsonc,yml,yaml}"
  - "/tsconfig*.json"
  - "/biome.jsonc"
---

# TypeScript, JavaScript, JSON and YAML

- Fix every finding at its cause, never its symptom. Never lower, relax, bypass or route around a gate, test, check or script to make it pass, and never add a suppression: no `biome-ignore`, `@ts-ignore`, `@ts-expect-error`, `@ts-nocheck`, `any` or `as` cast to silence a type, `eslint-disable`, or loosened `biome.jsonc` or `tsconfig*.json`.
- Fix every finding the `typescript6-lsp-intelligence` plugin's post-edit hook reports after an edit before the next edit; the hook type-checks each changed TypeScript or JavaScript file with `tsc`.
- Run `npx biome check --write <file>` after each edit to format it, lint it and sort its imports, because no hook runs Biome; then read the file again.
