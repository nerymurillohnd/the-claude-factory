---
paths:
  - "**/*.{js,cjs,mjs,ts,cts,mts,tsx}"
  - "**/*.{json,jsonc,yml,yaml}"
  - "/tsconfig*.json"
  - "/biome.jsonc"
---

# TypeScript, JavaScript, JSON and YAML

- Load the `typescript6-lsp-intelligence:ts-lifecycle` skill for TypeScript and JavaScript.
- Fix every finding the plugin's hook reports after an edit before the next edit; the hook type-checks each changed TypeScript or JavaScript file with `tsc`.
- Run `npx biome check --write <file>` after each edit to format it, lint it and sort its imports, because no hook runs Biome; then read the file again.
- Add a `biome-ignore` comment only with the owner's approval, and write the reason in it.
