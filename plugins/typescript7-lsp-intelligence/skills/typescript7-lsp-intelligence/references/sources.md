# Primary sources and version assumptions

Tested on 2026-10-12 with TypeScript 7.0.2 (native generation: compiler and `tsc --lsp --stdio`), TypeScript 6.0.3 with typescript-language-server 6.0.2 (legacy `tsserver` generation), and Biome 2.5.15. These versions record what was tested; they are not a request to upgrade or install tools.

The links below are citations. Open them only when an installed tool behaves differently from this skill and network access is available; otherwise report the difference and the version you observed.

| Topic | Primary source | Verify |
|---|---|---|
| Claude semantic client | [LSP behavior](https://code.claude.com/docs/en/tools-reference#lsp-tool-behavior) | Model-visible operations and request schema |
| Program options | [TSConfig reference](https://www.typescriptlang.org/tsconfig/) | Resolved options, JS checking, program membership, module/runtime choices |
| CLI modes | [Compiler options](https://www.typescriptlang.org/docs/handbook/compiler-options.html) | Config inspection versus actual compilation |
| Native generation | [TypeScript 7](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/) | Native compiler, LSP, and compatibility boundaries |
| Native implementation | [typescript-go](https://github.com/microsoft/typescript-go) | Actual native interfaces and capabilities |
| Legacy wrapper | [typescript-language-server 6.0.2](https://github.com/typescript-language-server/typescript-language-server/tree/v6.0.2) | tsserver integration, initialization, configuration |
| Strictest preset | [tsconfig bases](https://github.com/tsconfig/bases/blob/main/bases/strictest.json) | Actual preset options; no invented CLI flag |
| Lint and format | [Biome CLI](https://biomejs.dev/reference/cli/) | Command scope, write/fix modes, statuses, and available output |
| Language semantics | [Type narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html) | Unknown values, runtime checks, and inferred types |

The control tests were run with both compiler generations. The native protocol probe did not establish a clean shutdown lifecycle, so do not infer complete client-integration reliability from semantic responses. Configuration and declaration dependencies can change diagnostics without a source edit.
