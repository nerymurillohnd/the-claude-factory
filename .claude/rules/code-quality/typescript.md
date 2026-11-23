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
- Write plugin JavaScript that runs on the user's `node` (MCP servers, hook scripts, tests) to run unchanged on Node.js 24 through 26, with no API newer than Node 24; `tsc` checks it against `@types/node` 24. Mods are exempt: they run inside Claude Code.
- Normalize `\` to `/` in every path a hook, mod or script reads from Claude Code, such as `tool_input.file_path`, before comparing it (`path.replaceAll("\\", "/")`), then match a segment such as `/src/`, not the start of the path: on Windows the path arrives with backslashes even under Git Bash, so an unnormalized pattern never matches and a guard lets the call through.
- Keep the root `@types/node` on the major of the plugins' Node.js floor (24), not on `.nvmrc`'s Node 26: maintainer JavaScript is checked against it too, and Dependabot holds its majors back.
