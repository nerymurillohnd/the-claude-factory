---
paths:
  - "**/*.{js,cjs,mjs,ts,cts,mts,tsx}"
  - "**/*.{json,jsonc,yml,yaml}"
  - "/tsconfig*.json"
  - "/biome.jsonc"
---

# TypeScript, JavaScript, JSON and YAML quality

Use Biome to format and lint TypeScript, JavaScript, JSON and YAML, and `tsc` to type-check, never Prettier or ESLint.

## Order of work on one of these files

1. Before changing a symbol's name, signature or existence, find every use with the LSP tool, as `lsp.md` sets.
2. Edit the file, then fix the LSP diagnostics Claude Code reports for it.
3. Format, lint and sort imports in one pass, applying the safe fixes: `npx biome check --write <file>`. Biome orders those steps itself.
4. Fix by hand any finding step 3 could not fix, then repeat step 3.
5. After a `.ts` or `.tsx` edit, type-check last, on the final code: `npx tsc --noEmit -p tsconfig.json`.
6. Read the file again before the next edit: step 3 rewrites it.

## Before a commit

- Check every file Biome reads: `npm run lint:js`.
- Type-check the TypeScript project: `npm run typecheck:ts`.

## Findings

- Fix each finding at its cause.
- When a finding is a false positive, show the evidence and ask the owner before adding a `biome-ignore` comment with its reason.

## LSP

- Load the `typescript6-lsp-intelligence:ts-lifecycle` skill before writing, editing or reviewing TypeScript or JavaScript.
