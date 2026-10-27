---
status: accepted
date: 2026-10-27
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# tsc decides how index-signature keys are written, not Biome

## Scope

- `biome.jsonc`: `linter.rules.complexity.useLiteralKeys`.
- `tsconfig.base.json`: `noPropertyAccessFromIndexSignature`.
- Every JavaScript and TypeScript file Biome and tsc check.

## Context and problem statement

Biome's `useLiteralKeys`, recommended at `info`, rewrites `obj['key']` as `obj.key`. tsc's `noPropertyAccessFromIndexSignature`, set in `tsconfig.base.json`, requires the bracket form when the key comes from an index signature, such as `process.env['GIT_INDEX_FILE']`. `biome ci` reported 4 such infos in `scripts/tests/gates.test.mjs` (DEBT-032). Raising the preset's info-level rules to `"error"` (item 30 of the Biome spec) would have made the gates contradict the type-check. Which tool decides?

## Decision drivers

- The gates must never require code that another gate rejects.
- Keep the stricter check.

## Considered options

- **Turn `useLiteralKeys` off, with the reason beside it**: chosen.
- **Drop `noPropertyAccessFromIndexSignature` from `tsconfig.base.json` and raise `useLiteralKeys` with the other rules**: rejected, because the bracket form marks a key that may be absent, which is the stricter rule.

## Decision outcome

Chosen option: **`useLiteralKeys` off**. tsc alone decides how an index-signature key is written. The other 23 info-level rules of the preset go to `"error"` in the same commit.

### Consequences

- Good, because the gates and the type-check agree, and Biome's output has no finding the code must ignore.
- Bad, because Biome no longer suggests dot access for a literal key on a type without an index signature; tsc does not report that case either.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Biome reports no `useLiteralKeys` finding and tsc passes | `biome ci . --error-on-warnings` and `npm run typecheck:ts` | 171 files, no diagnostic; tsc passes | After a Biome upgrade |

## More information

- Decided by Nery on 2026-10-27, as D8 (a) of `.claude/specs/2026-10-26-biome-config-corrections-and-strictness-design.md`, item 30.
- Closes DEBT-032 as resolved.
