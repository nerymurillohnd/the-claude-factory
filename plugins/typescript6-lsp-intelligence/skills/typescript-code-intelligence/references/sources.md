# TypeScript source map

External links are citations and optional lookups requiring network access. Offline, use the installed tool definition/help and local configuration; do not make web access a prerequisite for ordinary work.

Check the selected executable, its package metadata and matching documentation when compiler generation or option behavior matters. Consult release notes for API compatibility changes and regressions. This map does not freeze a release or label a patch as permanently current.

| Question | Primary source |
|---|---|
| What does the loaded semantic tool accept? | [Claude LSP behavior](https://code.claude.com/docs/en/tools-reference#lsp-tool-behavior), plus its runtime tool definition |
| Which files/options define the program? | [TSConfig reference](https://www.typescriptlang.org/tsconfig/), [compiler CLI](https://www.typescriptlang.org/docs/handbook/compiler-options.html) |
| What does checked JavaScript mean? | [checkJs](https://www.typescriptlang.org/tsconfig/checkJs.html), [allowJs](https://www.typescriptlang.org/tsconfig/allowJs.html) |
| What interface does the native generation provide? | [TypeScript native implementation](https://github.com/microsoft/typescript-go), [TypeScript blog](https://devblogs.microsoft.com/typescript/) |
| What does the legacy wrapper require? | [typescript-language-server](https://github.com/typescript-language-server/typescript-language-server), [releases](https://github.com/typescript-language-server/typescript-language-server/releases) |
| Which options are in a strictest preset? | [tsconfig strictest source](https://github.com/tsconfig/bases/blob/main/bases/strictest.json) |
| How do narrowing and JSON repair work? | [Type narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html), [TypeScript 4.9 property narrowing](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html#unlisted-property-narrowing-with-the-in-operator) |
| What do lint/format commands change? | [Biome CLI](https://biomejs.dev/reference/cli/), [changelog](https://biomejs.dev/internals/changelog/) |
