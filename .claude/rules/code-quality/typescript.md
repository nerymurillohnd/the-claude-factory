---
paths:
  - "**/*.{js,cjs,mjs,ts,cts,mts,tsx}"
  - "**/*.{json,jsonc,yml,yaml}"
  - "/tsconfig*.json"
  - "/biome.jsonc"
---

# TypeScript, JavaScript, JSON and YAML

- Load the `typescript6-lsp-intelligence:ts-lifecycle` skill whenever you write, edit or review TypeScript or JavaScript.
- Fix every issue a check reports before the next step or task; never leave it as debt.

## Gotchas

- `biome check --write` formats, lints and sorts imports in one pass; never use Prettier or ESLint.
- `tsc` checks the whole project: there is no per-file type check with the project's configuration.
- Add a `biome-ignore` comment only for a proven false positive, with its reason and the owner's approval.

## After writing or editing one of these files, in this order

1. Run `npx biome check --write <file>` to format, lint and sort imports; fix the rest by hand and run it again.
2. Run `npx tsc --noEmit -p tsconfig.json`, after a `.ts` or `.tsx` change, to type-check the final code.
3. Read the file again before the next edit, because step 1 rewrites it.

## Before a commit

1. Run `npm run lint:js` to check every file Biome reads.
2. Run `npm run typecheck:ts` to type-check the TypeScript project.
