---
paths:
  - "**/*.{js,cjs,mjs,ts,cts,mts,tsx}"
  - "**/*.{json,jsonc,yml,yaml}"
  - "/tsconfig*.json"
  - "/biome.jsonc"
---

# TypeScript, JavaScript and data file quality

## Formatting and linting

- Format and lint TypeScript, JavaScript, JSON, YAML and the Markdown written for people with Biome, never Prettier or ESLint.
- After editing one of these files, run `npx biome check --write <file>`, then read the file again before the next edit.
- Before a commit, run `npm run lint:js`.

## Type checking

- Type-check with `tsc` through `npm run typecheck:ts`.

## Findings

- Fix each finding at its cause.
- When a finding is a false positive, show the evidence and ask the owner before adding a `biome-ignore` comment with its reason.

## LSP

- Load the `typescript6-lsp-intelligence:ts-lifecycle` skill before writing, editing or reviewing TypeScript or JavaScript.
