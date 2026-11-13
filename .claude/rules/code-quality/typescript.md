---
paths:
  - "**/*.{js,cjs,mjs,ts,cts,mts,tsx}"
  - "**/*.{json,jsonc,yml,yaml}"
  - "/tsconfig*.json"
  - "/biome.jsonc"
---

# TypeScript, JavaScript and data file quality

Use Biome to format and lint TypeScript, JavaScript, JSON, YAML and the Markdown written for people, and `tsc` to type-check, never Prettier or ESLint.

## After editing one of these files

- Format and lint it, applying the safe fixes: `npx biome check --write <file>`.
- Type-check the TypeScript project after a `.ts` or `.tsx` edit: `npx tsc --noEmit -p tsconfig.json`.
- Read the file again before the next edit: `biome check --write` rewrites it.

## Before a commit

- Check every file Biome reads: `npm run lint:js`.
- Type-check the TypeScript project: `npm run typecheck:ts`.

## Findings

- Fix each finding at its cause.
- When a finding is a false positive, show the evidence and ask the owner before adding a `biome-ignore` comment with its reason.

## LSP

- Load the `typescript6-lsp-intelligence:ts-lifecycle` skill before writing, editing or reviewing TypeScript or JavaScript.
