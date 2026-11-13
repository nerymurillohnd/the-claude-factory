---
paths:
  - "**/*.py"
  - "**/*.sh"
  - "**/*.{js,cjs,mjs,ts,cts,mts,tsx}"
  - "/biome.jsonc"
  - "/ruff.toml"
  - "/pyrightconfig.json"
  - "scripts/pyrightconfig.json"
  - "/tsconfig*.json"
  - "/.shellcheckrc"
  - "/.editorconfig"
---

# Formatting, linting and type checking

Each file type has one formatter, one linter and, where the language has types, one type checker. Their configuration files are the only source of style rules: never restate one of their settings in prose.

| Files | Format and lint | Type check | Run | Configuration |
| :-- | :-- | :-- | :-- | :-- |
| Python | ruff | basedpyright | `npm run lint:python`, `npm run typecheck:python` | `ruff.toml`, `pyrightconfig.json`, `scripts/pyrightconfig.json` |
| Shell (Bash) | shfmt formats, ShellCheck lints | none | `npm run lint:shell` | `.editorconfig` (`[[shell]]`), `.shellcheckrc` |
| TypeScript and JavaScript | Biome | `tsc` | `npm run lint:js`, `npm run typecheck:ts` | `biome.jsonc`, `tsconfig.json`, `tsconfig.base.json` |
| JSON, YAML and the Markdown written for people | Biome | none | `npm run lint:js` | `biome.jsonc` |

- After changing a file, run the checks of its row before you commit; `npm run lint` and `npm run typecheck` run every row.
- Apply the formatting and the safe fixes with `npm run fix`, which rewrites files in place, then run the checks again.
- Fix each finding at its cause instead of suppressing it. When a finding cannot be fixed at its cause, ask the owner before suppressing it, and write the reason beside the suppression.
