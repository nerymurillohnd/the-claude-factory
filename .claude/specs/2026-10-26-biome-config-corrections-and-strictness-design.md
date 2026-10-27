# Biome configuration: corrections, cleanup and stricter rules

Status: approved by Nery on 2026-10-27, with every decision of section 14 settled; implementation follows section 15. Nothing below is implemented except item 2, committed in `db0dfab`: the change to `biome.json` and DEBT-033's closure in the debt ledgers.

## 1. Goal

Biome's configuration (`biome.json`, or `biome.jsonc` if D4 is (a)):
- follows the Biome 2.6.3 configuration reference to the letter;
- says each thing once, with no key that repeats a default, the preset or `.editorconfig`;
- states why each non-default setting exists;
- turns on the stricter analysis the repository can carry;
- in VS Code, does on save what the CLI and the gates do (section 12).

Every step of section 15 keeps `biome ci .` green and goes in its own commit.

## 2. Sources and evidence

- Biome 2.6.3, the version pinned in `package.json` (`npx biome --version`), released 2026-10-24 (`gh release view @biomejs/biome@2.6.3 -R biomejs/biome`).
- Configuration reference, sections `$schema`, `extends`, `root`, `plugins`, `files`, `vcs`, `linter`, `assist`, `formatter`, `overrides`, `javascript`, `json`, `graphql`, `grit`, `markdown`, `yaml`, and the glob syntax reference; the linter guide (biomejs.dev/linter), including its editor-integration, migration, groups and plugins sections (target languages, plugin API, JavaScript plugins); Biome's FAQ on the Scanner's speed and memory; for the editor, see section 12.1 (biomejs.dev/reference/configuration, as Nery shared it on 2026-10-26, and Context7 `/biomejs/website`).
- `biome ci --help` and `biome explain <rule>` for every configured rule, run on 2.6.3.
- `packages/@biomejs/biome/CHANGELOG.md` on `main` of `biomejs/biome`.
- Measurements on 2026-10-26 in a scratch copy of `HEAD` (`git archive`, the repository's `node_modules`, the mods' generated `.claude-plugin/types/` copied in). Every count below comes from those runs.

## 3. Scopes

| Files | Scope | Path to `main` |
| :-- | :-- | :-- |
| `biome.json`, `package.json`, `.husky/**`, `tsconfig.base.json`, `scripts/**`, `.claude/skills/**`, `.vscode/**` | Maintainer | Direct signed commit |
| VS Code user settings, `~/.claude/ENVIRONMENT.md` | Nery's machine and global instructions | Outside the repository, only with Nery's approval |
| `plugins/<plugin>/**` | Plugin | Pull request, version bump and `CHANGELOG.md` entry (`check-version-bump.mjs` exempts only `README.md`) |

## 4. Corrections

### 4.1 Item 1: tsconfig files are force-ignored (DEBT-034)

- **Now:** `files.includes` has `!!**/tsconfig.json` and `!!**/tsconfig.base.json`, added in `b3ada31` with no reason.
- **Why it is wrong:** the reference reserves `!!` for build output and nested projects, and asks for a regular exclusion for files that give types or other project information. A tsconfig is such a file.
- **Measured:** without the exclusions, all seven tracked tsconfig files lint and parse clean. Biome treats `tsconfig.*.json` as `tsconfig.json`, so it parses them as JSONC (changelog). The only changes are `json.formatter.expand: "always"` putting one array item per line:
  - Maintainer: `scripts/tsconfig.json`. `tsconfig.base.json` and `scripts/tsconfig.plugins.json` already pass.
  - Plugins: `file-tree-pane`, `project-maintainer`, `tool-ledger`, `turn-meter`.
- **Lint effect today:** none. With `!!`, with no exclusion, or with `!` on the plugin files, `noUnresolvedImports` gives the same 28 diagnostics, and no enabled rule belongs to the `project` or `types` domain.
- **Change:** delete both `!!` patterns and format `scripts/tsconfig.json` once. Its `include` line passes 100 columns, so it changes under every option of D1. What happens to the plugin files depends on decision D1 (section 14). The override measured in section 9 checks every tsconfig and changes no plugin file.

### 4.2 Item 2: commit DEBT-033

- **Done, committed in `db0dfab`:** `formatter.indentStyle`, `indentWidth`, `lineEnding` and `markdown.formatter` were removed. `.editorconfig` is now the only source, and DEBT-033 is closed as resolved in `closed-debt.md`.
- **Evidence:** `biome ci .` checked 163 files with no fixes. In the scratch copy, changing only `.editorconfig` broke `biome ci .`: `indent_size = 4` gave 151 errors, `indent_style = tab` 139, `end_of_line = crlf` 163, and a `[*.md]` section with `indent_size = 4` 2.
- **Change:** none left. It was committed on its own, ahead of item 1.

## 5. Cleanup: keys that repeat a default or the preset

| # | Key | Why it goes |
| --: | :-- | :-- |
| 3 | `files.includes`: `!!**/node_modules` | The reference: Biome ignores `node_modules/` for processing even when a pattern matches it. The "Investigate slowness" guide adds that `!!**/node_modules` makes "type information from dependencies … [not] available anymore". So the pattern is not only redundant: it works against item 8's type-aware rules. With the Scanner on, the time, the memory and the findings were the same with and without it (section 6.4). |
| 4 | `files.maxSize: 1048576` | The default (reference, `--files-max-size`) |
| 5 | `formatter.enabled: true`, `linter.enabled: true` | The defaults |
| 6 | `linter.rules.a11y: { "preset": "recommended" }` | The global `rules.preset` already applies it to the group |
| 7 | 42 rule entries | Recommended rules set to their default severity, so the preset already enables them that way |

Item 7, by group (from `biome explain` on 2.6.3):

- `correctness` (17): `noConstAssign`, `noConstantCondition`, `noEmptyCharacterClassInRegex`, `noEmptyPattern`, `noGlobalObjectCalls`, `noInvalidConstructorSuper`, `noNonoctalDecimalEscape`, `noPrecisionLoss`, `noSelfAssign`, `noSetterReturn`, `noSwitchDeclarations`, `noUnreachable`, `noUnreachableSuper`, `noUnusedFunctionParameters`, `useIsNan`, `useValidForDirection`, `useYield`.
- `suspicious` (23): `noAssignInExpressions`, `noAsyncPromiseExecutor`, `noClassAssign`, `noCommentText`, `noCompareNegZero`, `noControlCharactersInRegex`, `noDebugger`, `noDoubleEquals`, `noDuplicateCase`, `noDuplicateClassMembers`, `noDuplicateObjectKeys`, `noDuplicateParameters`, `noExplicitAny`, `noFallthroughSwitchClause`, `noFunctionAssign`, `noGlobalAssign`, `noImportAssign`, `noMisleadingCharacterClass`, `noRedeclare`, `noShadowRestrictedNames`, `noUnsafeDeclarationMerging`, `noUnsafeNegation`, `useGetterReturn`.
- `security` (1): `noGlobalEval`.
- `performance` (1): `noAccumulatingSpread`.

**Entries that stay.** The other 33 non-nursery entries do something the preset does not:

- raise a severity, for example `noUnusedImports` (`warn` to `error`) and `useConst` (`warn` to `error`);
- enable a rule that is not recommended, for example `useBlockStatements` and `noUndeclaredVariables`;
- turn a rule off: `noUndeclaredDependencies`, `noNegationElse`.

The four `nursery` entries also stay, because the preset never enables nursery rules.

**Kept on purpose:** the `!!` on `.superpowers` and `.claude/settings.local.json`, which git also ignores. They hold if Biome runs with `--vcs-use-ignore-file=false`.

**Check for items 3 to 7, and for 15, 20, 22 and 26 (sections 7, 9, 10 and 11.5):** `biome ci .` gives the same file count and the same diagnostics before and after (today: 163 files, no fixes, 4 infos).

## 6. Stricter analysis

| # | Change | Default severity | Findings (maintainer / plugins / files) |
| --: | :-- | :-- | :-- |
| 8 | `linter.domains.test: "recommended"`, plus seven scanner rules at `"error"` (section 6.4) | n/a | 0 new diagnostics |
| 9 | `security.noSecrets` | info | 9 / 7 / 7 |
| 10 | `suspicious.noShadow` | warn | 2 / 8 / 4 |
| 11 | `performance.noAwaitInLoops` | info | 0 / 31 / 5 |
| 12 | `style.noNestedTernary` | info | 0 / 27 / 8 |
| 13 | `complexity.noExcessiveCognitiveComplexity` (default `maxAllowedComplexity` 15) | info | 7 / 28 / 16 |
| 14 | `performance.useTopLevelRegex` | warn | 174 / 120 / 27 |

- **Item 8:** see section 6.4. Setting `project` and `types` to `"recommended"`, as first drafted, starts the Scanner but catches nothing: a planted import cycle passed under both. Item 8 now names the scanner rules that work, one by one.
- **Items 9 to 14:** each rule is turned on at `"error"`, since the gates already fail on warnings. Its findings are fixed, or suppressed with Nery's approval and a written reason. Then it is committed.
  - Findings under `plugins/` go through one pull request per plugin, with its bump.
  - `noSecrets` findings are reviewed one by one. A false positive is handled with `entropyThreshold` or a justified suppression, never by turning the rule off.
  - Item 13's threshold is Nery's decision (D2).
  - Item 14 is last. Its own documentation warns that top-level regexes can slow startup, which matters for hooks that start on every event.

### 6.1 Severity: `info` never fails a gate

Source: the linter guide (biomejs.dev/linter), as Nery shared it on 2026-10-26.
- `"error"` always fails the CLI.
- `"warn"` fails it only with `--error-on-warnings`. The gates pass that flag (`scripts/gates.mjs:422` and `:488`).
- `"info"` never fails it, "even when `--error-on-warnings` is passed".

**Gap:** 218 non-nursery rules are recommended in 2.6.3: 132 default to `error`, 58 to `warn` and 28 to `info`. The configuration raises four of the 28 (`noExtraBooleanCast`, `noUselessCatch`, `useExponentiationOperator`, `useTemplate`). The other 24 run, print their findings, and block nothing:

`complexity`: `noFlatMapIdentity`, `noUselessConstructor`, `noUselessContinue`, `noUselessEmptyExport`, `noUselessEscapeInRegex`, `noUselessFragments`, `noUselessLabel`, `noUselessLoneBlockStatements`, `noUselessRename`, `noUselessStringRaw`, `noUselessSwitchCase`, `noUselessTernary`, `noUselessThisAlias`, `noUselessTypeConstraint`, `noUselessUndefinedInitialization`, `useFlatMap`, `useIndexOf`, `useLiteralKeys`. `correctness`: `useParseIntRadix`. `style`: `useArrayLiterals`, `useNodejsImportProtocol`, `useShorthandFunctionType`. `suspicious`: `noDuplicateFields`, `noQuickfixBiome`.

| # | Change | Findings |
| --: | :-- | :-- |
| 30 | Set those 24 rules to `"error"`, with `useLiteralKeys` under D8 | Only the 4 `useLiteralKeys` infos `biome ci .` prints today, all in maintainer files; 0 for the other 23 |

`useLiteralKeys` is DEBT-032: it conflicts with tsc's `noPropertyAccessFromIndexSignature` in `tsconfig.base.json`. Raising it to `"error"` would make the gates contradict the type-check. D8 settles it before item 30 lands.

The same rule shapes the levels this spec sets. Every rule it adds or raises goes to `"error"`: items 9 to 14, 24, 25, 30 and 31. Several of those rules default to `info`, and at `info` they would never block anything.

### 6.1.1 Diagnostics: severities and tags

Source: Biome's diagnostics reference (biomejs.dev/reference/diagnostics), as Nery shared it on 2026-10-26 and marked as important.
- The severities are fatal, error, warning and information.
- The tags are `verbose`, `internal`, `fixable` and `deprecated`.
- A `verbose` diagnostic is hidden unless `--verbose` is passed.

Probed on the repository and in the scratch copy:

| Question | Evidence | Verdict |
| :-- | :-- | :-- |
| Does `biome ci` hide anything from the gates, which never pass `--verbose`? | `biome ci .` against `biome ci . --verbose`: both exit 0. The verbose run adds only two `VERBOSE` blocks, "Files processed" (the list of checked files) and "Files fixed" ("The list is empty") | Nothing is hidden today |
| Do fatal and internal diagnostics fail the gates? | The Biome gates judge only the exit code: neither `biome-maintainer` nor `biome-plugins` has an `after` check (`scripts/gates.mjs`; the only `after` checks belong to the test and signature gates). A fatal or internal error exits non-zero | Yes, through the exit code |
| Does an unknown configuration key fail? | `linter.rules.style.noSuchRule`: "× Found an unknown key", "Biome exited because the configuration resulted in errors", exit 1 | Yes |
| **Does a deprecated configuration key fail?** | `linter.rules.recommended: true` instead of `preset` gave a `deserialize DEPRECATED` diagnostic at **information** severity ("The use of the recommended field has been deprecated, and will removed in the next major version"). Exit 0, **even with `--error-on-warnings`**. Next to `preset`, a second warning ("cannot be used together") made that run fail, but the deprecation alone passed. `files.experimentalScannerIgnores` gave a warning, which `--error-on-warnings` does fail | **No: a deprecation reported as info passes every gate** |
| Does `biome migrate` signal a pending migration? | With the deprecated key, the preview printed "Configuration file can be updated" and the diff to `preset`, then exited 0, as it does when up to date ("no migration needed") | No signal in the exit code |

**Gap, item 37:** a deprecated key can reach `main` and stay there until the next major release removes it. A Dependabot bump or a hand edit can bring one in, and no gate says so.

Add a gate, `biome-migrate`, in the `lint` group. It runs `biome migrate` (preview only, never `--write`) and fails unless its stdout and stderr together contain "no migration needed". Today a gate's `after` check receives only stdout (`scripts/gates.mjs`), so this gate needs both streams.
- The gate passes only on the exact up-to-date message. If a later Biome rewords it, the gate fails until it is updated: a false failure, never a silent pass.
- It is the first Biome gate that reads Biome's output. The phrase is checked on 2.6.3. The gates' tests get a case with a deprecated key planted.
- It also covers section 11.4's nursery renames, which `biome migrate` rewrites.

**Verification aid:** `biome ci . --verbose` lists every file Biome processes. Items 1, 23 and 26 change what Biome sees. Comparing that list before and after each one shows exactly which files entered or left. Items 1 and 23 should add `.claude/settings.json` and the seven tsconfig files; item 26 should change nothing.

### 6.2 Domains

Source: the linter guide's "Domains". A domain's recommended rules turn on by themselves only when Biome finds a known dependency in the nearest `package.json`. This repository runs its tests on `node:test` and lists no `mocha`, `jest`, `vitest`, `react` or `playwright`, so no domain ever turns on by itself. 2.6.3 has 16 domains: `astro`, `drizzle`, `next`, `playwright`, `project`, `qwik`, `react`, `reactNative`, `solid`, `svelte`, `tailwind`, `tanstackQuery`, `test`, `turborepo`, `types` and `vue`. `noFocusedTests`, `noSkippedTests` (`test`) and `noChildrenProp` (`react`) run today only because they are listed one by one.

Measured one domain at a time in the scratch copy:

| Domain | `"recommended"` | `"all"`, beyond the 4 `useLiteralKeys` infos |
| :-- | :-- | :-- |
| `test` | 0 new; a planted duplicate test title fails (`noIdenticalTestTitle`), and `it`/`describe` stop counting as undeclared | `noConditionalExpect` 7 (1 maintainer, 6 plugins); `useConsistentTestIt` 273 (rejected in section 13) |
| `project` | 0 new, and catches nothing: a planted import cycle passed (section 6.4) | `noUnresolvedImports` 28 (rejected in section 13); `useImportExtensions` 6 |
| `types` | 0 new, and catches nothing (section 6.4) | `useArraySortCompare` 4 |
| `react` | `noArrayIndexKey` 2 (plugins) | plus `noJsxPropsBind` 7 and `noLeakedRender` 4 |

| # | Change | Findings |
| --: | :-- | :-- |
| 31 | `suspicious.noConditionalExpect` at `"error"` | 7: `scripts/tests/typescript6-lsp-intelligence/tsc-check.test.mjs:185`; `plugins/file-tree-pane/tests/pane.test.tsx:627` to `:636` (six) |

**Rejected:**
- `useImportExtensions`. Its 6 findings are the mods' `import … from '../types'` and the SvelteKit fixture's `$lib` imports. Both resolve under `moduleResolution: "bundler"` (the mods' generated tsconfig) or SvelteKit, where no extension is needed.
- `useArraySortCompare`. Its 4 findings (`scripts/check-repo.mjs:90`, `scripts/gates.mjs:226`, `scripts/lib.mjs:128` and `:133`) sort arrays of path strings. There, the default code-unit order is the intended, stable order.
- The `react` domain. The mods render with the engine's `h`, not React, and the domain's rules assume React's model. Unverified: whether the engine reconciles list children by `key`, which is what `noArrayIndexKey` protects.

### 6.3 Code fixes

Source: the linter guide's "Safe fixes", "Unsafe fixes" and "Configure the code fix".
- **Already right:**
  - The editor applies only safe fixes on save (`source.fixAll.biome`, section 12).
  - `npm run fix` runs `biome check --write` without `--unsafe`, so unsafe fixes are always reviewed by hand.
  - No rule changes its fix classification.
- **Not needed:** a `fix` override. No safe fix in this repository has changed semantics, and no unsafe fix is routinely accepted.

### 6.4 The Scanner: cost and the rules that need it

Source: Biome's FAQ entries "Why is Biome linter so slow compared to v1?" and "Why is Biome using so much memory?", as Nery shared them on 2026-10-26. The Scanner builds the module graph and the inferred types. It starts only when a rule of the `project` domain (or of `types`) is on, and it reads `.d.ts` files in `node_modules`, transitive ones included. The FAQ's numbers: about 2,000 files go from about 800 ms to about 2 s, and about 5,000 files from about 1 s to about 8 s.

Measured in the scratch copy, with `biome ci .` timed by `/usr/bin/time -l` (163 files; 245 `.d.ts` files in a 100 MB `node_modules`):

| Configuration | Wall time | Peak memory | Catches the planted case |
| :-- | :-- | :-- | :-- |
| Today, no Scanner | 0.09 s | 69 MB | n/a |
| `project: "recommended"` | 0.11 s | 97 MB | Import cycle: no |
| `types: "recommended"` | 0.11 s | 103 MB | Floating promise: no |
| `project: "all"` | 0.12 s | 97 MB | Import cycle: yes (`noImportCycles`) |
| `suspicious.noImportCycles` alone | 0.11 s | 97 MB | Import cycle: yes |
| `nursery.noFloatingPromises` alone | 0.12 s | 103 MB | Floating promise from a local `async` function: yes |

So a domain's `"recommended"` set runs the Scanner here but no rule that catches either planted case. `biome explain` marks no `project` or `types` rule as recommended, and the domains' recommended sets are not listed anywhere this spec could read. Naming the rules one by one is what works. The cost at this size is about 30 ms and 30 MB, well under the FAQ's numbers.

Item 8's rules, each with 0 findings in the repository (measured one at a time):
- `project`: `suspicious.noImportCycles`, `correctness.noPrivateImports`, `suspicious.noDeprecatedImports`, `nursery.noSelfImport`.
- `types`: `nursery.noFloatingPromises`, `nursery.noMisusedPromises`, `nursery.useAwaitThenable`.

The three `types` rules sit in the nursery, with the risk section 11.4 describes. `noFloatingPromises` matters most for the mods' and plugins' async hooks, where a dropped promise fails without a trace.

**Limit, measured:** an unawaited `writeFile(…)` from `node:fs/promises` was not caught. That held with `!!**/node_modules` and without it, at the same time and memory, so item 3's removal changes nothing for the Scanner. `noFloatingPromises` covers promises whose type Biome infers inside the repository, not those typed by `@types/node`. tsc's checks are not a substitute: TypeScript has no floating-promise check.

**Editor:** the FAQ's memory note applies to the VS Code extension too. With item 8, the Biome process holds about 100 MB instead of about 70 MB. Item 39 brings that back down to about 80 MB.

**Scanner targeting** (Biome's architecture page, shared by Nery on 2026-10-27). The Scanner has three jobs:
- it finds nested `biome.json` files;
- with `vcs.useIgnoreFile`, it finds nested `.gitignore` files, such as the one with `*` inside each mod's `.claude-plugin/types/`;
- with a `project` rule on, it indexes `package.json` and the source files.

Without `project` rules, it scans only the folders the run targets. With them, "these optimisations don't apply", so item 8 makes even a one-file run scan the whole project. That covers the pre-commit hook's `--staged`, which with item 8 also runs the Scanner across the repository, and every file the editor opens.

Measured, `biome check scripts/lib.mjs` alone: 0.04 s and 53 MB today, 0.06 s and 63 MB with item 8's rules and item 39. That is the cost item 8 adds to each commit and each editor session, and it stays well under a second.

The same page explains why parse errors never pass silently here. The parser recovers and marks broken code with "bogus" nodes, but a parse error is still an error diagnostic. The configuration leaves `formatWithErrors` at `false` (section 8), and no command passes `--skip-parse-errors` (section 6.4.1).

**Profiling** (the "Investigate slowness in Biome" guide, shared by Nery on 2026-10-26), with item 8's scanner rules on:
- **`biome lint --profile-type-inference`** (since 2.6). The costliest file is `plugins/file-tree-pane/tests/pane.test.tsx`, at 10.0 ms of type inference. The other files cost less. Removing `!!**/node_modules` (item 3) changed that to 8.3 ms, which is noise.
- **Tracing**: `biome lint --log-level=tracing --log-kind=json --log-file=<scratch>`, filtered with `jq` by span name. The guide's `pull_diagnostics` span does not appear in a `lint` run on 2.6.3, while `open_file_internal` and `update_module_graph_internal` do. The four costliest files in both spans are the engine-generated `plugins/<mod>/.claude-plugin/types/claude-code/index.d.ts`: 16,981 lines each, 17 to 34 ms each to open and to add to the module graph. The Scanner indexes them although git ignores them, as the reference allows when it "may still … index excluded source files needed for analysis".

| # | Change | Measured with item 8's rules on (best of five runs) |
| --: | :-- | :-- |
| 39 | Add `!!plugins/*/.claude-plugin/types` to `files.includes` | `biome ci .`: 0.13 s → 0.11 s, 106 MB → 79 MB. Findings are the same, with `noUnresolvedImports` turned on to test it: 28 before, 28 after. |

The reference prefers a regular exclusion for "generated source files that provide types". This one is force-ignored for two reasons:
- Biome cannot use these types. The mods reach them through `typeRoots` and an ambient `declare module 'claude-code'`, which Biome does not resolve (section 13, `noUnresolvedImports`). tsc keeps using them through `tsc -p plugins/<mod>/tsconfig.json`, which Biome's exclusions do not touch.
- They are the largest files Biome would ever index here, in every editor session.

If a later Biome resolves ambient modules, `noUnresolvedImports`' 28 false findings disappear. That is the signal to drop the `!!`, and the reason beside the pattern (item 19) says so.

### 6.4.1 Total cost and how each step is verified

Source: the CLI reference for `version`, `upgrade`, `rage`, `start`, `stop` and `check`, as Nery shared it on 2026-10-26.

**All the proposals together**, measured in the scratch copy: items 8, 9 to 14, 24, 25, 30 without `useLiteralKeys`, 31 and 33, plus the `test` domain.
- `biome rage --linter` lists 297 enabled rules, against 242 today.
- `biome ci .` takes 0.44 s and peaks at 114 MB, against 0.09 s and 69 MB today. That run includes printing the findings of items 9 to 14.
- `biome lint --profile-rules`, which excludes the semantic model and Scanner preparation, puts the three slowest rules in the nursery, at under 40 ms each over the whole repository: `noFloatingPromises` 39.7 ms, `noUselessAssignment` 33.0 ms, `noMisusedPromises` 30.0 ms. Then come `noSecrets` 18.4 ms and `noRedeclare` 11.4 ms.

**Verification for each step of section 15:**
- `biome rage --linter` before and after the commit. The count of enabled rules changes by exactly the rules the step adds or removes, and items 3 to 7 and 15 change it by 0. This replaces the per-rule `biome explain` loops used to draft this spec.
- `biome rage --formatter` does the same for items 2, 21 and 22, where the formatter settings must stay identical.
- `biome lint --only=<rule> --reporter=summary` lists, before a rule is turned on, the files and counts its commit or pull request has to fix.
- If a nursery rule makes a later Dependabot upgrade slow, `--profile-rules` shows which one.

**Other CLI facts, checked against the repository:**
- `biome upgrade` updates only a standalone or Homebrew binary, never `@biomejs/biome` from npm.
  - That matches `~/.claude/LESSONS.md`, which upgrades the standalone `~/.local/bin/biome` with `biome upgrade`.
  - The repository's copy moves only through Dependabot's pull request (section 11.4).
  - Today both are 2.6.3 (`biome version`, `~/.local/bin/biome --version`). They can drift apart; the editor uses `node_modules` first (section 12.2), and the hooks and the gates use the pinned copy through `npm run`.
- `--staged` is "intended for local use", which is how the pre-commit hook uses it.
- `--changed` and `--since` are meant for CI. They are not needed here: a full `biome ci .` takes well under a second.
- `--enforce-assist` defaults to `true` (section 7).
- `--watch`, `start` and `stop` are not used; the VS Code extension manages its own server.
- `biome lint` (CLI reference, shared by Nery on 2026-10-26):
  - Its `--only` and `--skip` take a group, rule, domain or plugin, but no assist action, unlike `check`. That matches section 7's probe, where `biome lint` never reported `organizeImports`. No repository command runs `biome lint`.
  - This spec counted findings with `biome lint --only=<rule>`. The reference says `--only` sets a rule that is `off` to `error` if it is recommended, or `warn` otherwise. So every count in sections 6, 11.4 and 11.6 covers each rule's full findings, whether or not `biome.json` enables it.
  - `--suppress` and `--reason` stay unused (section 6.5).
- `biome format` and `biome ci` (CLI reference, shared by Nery on 2026-10-26):
  - **Gap, item 34:** `npm run format` runs `biome format --write .`, and `format` applies no assist action. Probe: after `biome format --write` on a file with unsorted imports, `biome ci` still failed with `assist/source/organizeImports`. After `biome check --write --linter-enabled=false` on the same file, `biome ci` passed. Item 34 changes the script's Biome part to `biome check --write --linter-enabled=false .`. `npm run format` then leaves every file passing the formatter and assist parts of `biome ci`, and lint fixes stay with `npm run fix`. Like `format` today, it also writes in `plugins/`, and a plugin file it changes goes through a pull request (`.claude/CLAUDE.md`).
  - **CI annotations:**
    - Probe: with `GITHUB_ACTIONS=true`, `biome ci` printed `::error title=assist/source/organizeImports,file=…,line=1,…` without any `--reporter` flag.
    - In CI, `npm run gates:ci -- --group lint` runs `biome-maintainer` through `scripts/gates.mjs`. That script passes its environment on to `biome` and prints the gate's output when the gate fails (`scripts/gates.mjs`, around lines 577 to 607). So a failing `biome-maintainer` should show as annotations on the pull request.
    - Unverified, because no failing CI run was read: whether GitHub attaches them, given that the probe printed an absolute `file=` path. To check: read the log of the next failing `lint` job.
  - **Reporters** (the CLI reference's "Reporter flags", shared by Nery on 2026-10-26; probed in the scratch copy):
    - The default is `default`. Under `GITHUB_ACTIONS=true`, plain `biome ci` printed the full diagnostic and the `::error` command for the same finding. That is the output of `--reporter=default --reporter=github`, which gave the same two lines without the variable. So the gates need no `--reporter` flag. They inherit `GITHUB_ACTIONS` from the runner, and the log keeps the readable diagnostics.
    - `--reporter=github` writes the same absolute `file=` path, so the open question above stays open.
    - `--reporter=summary` groups findings by rule and lists each file with its count. It replaces the shell pipelines this spec used to count findings per file. For items 9 to 14, `biome lint --only=<rule> --reporter=summary` gives the list for each plugin's pull request directly.
    - **Not used:**
      - `json` and `json-pretty`, which the reference marks experimental and liable to change in patch releases, so no script parses them;
      - `sarif`, for GitHub code scanning, which would need an upload step and the `security-events` permission, while the gates already block the merge;
      - `gitlab`, `junit`, `checkstyle`, `rdjson`, which no tool here reads.
  - `--threads` / `BIOME_THREADS`: not needed. The whole repository takes under half a second.
  - `--formatter-enabled`, `--linter-enabled`, `--assist-enabled` stay at their defaults in the gates, so `biome ci` enforces all three.
- `init`, `migrate`, `search`, `explain`, `clean`, `lsp-proxy` and the global flags (CLI reference, shared by Nery on 2026-10-26):
  - **`biome migrate`** (preview, no `--write`): "Your configuration file is up to date … no migration needed" on 2.6.3. Every Dependabot pull request that bumps `@biomejs/biome` runs it, and `--write` applies what it proposes. That matches `~/.claude/LESSONS.md`, and also catches renamed nursery rules (section 11.4).
  - **`biome migrate prettier|eslint|stylelint`:** not applicable. The repository tracks no Prettier, ESLint, Stylelint or markdownlint configuration or ignore file. The `.prettierignore` that `84afdae` added is gone.
  - **`biome init --jsonc`** creates a new `biome.jsonc`. D4 (a) renames the existing file instead, so the init is not used.
  - **`biome search`** (experimental, read-only): it confirmed item 32's pattern independently. Searching `scripts` for an `===` that involves `process.argv[1]` found 1 match in 21 files: `scripts/lib.mjs:286`, inside `isMain()` itself, which the plugin's `includes` leaves out. So the plugin starts with 0 findings.
  - **`--max-diagnostics` defaults to 20.** The gates call `biome ci --error-on-warnings` without it (`scripts/gates.mjs:422`, `:488`). A failing run therefore prints, and annotates, at most 20 findings, while the exit code still fails. **Item 35:** add `--max-diagnostics=none` to both Biome gates. A failure then shows every finding in the log and in the pull request's annotations, and the full list matters while items 9 to 14 land.
  - **`--no-errors-on-unmatched`** is used where it belongs: the pre-commit hook, where a commit may stage no file Biome handles. **`--skip-parse-errors`** is never used: it would let a file that does not parse pass silently.
  - **`--config-path` and `BIOME_CONFIG_PATH`:** unset (`biome rage`), since the config sits at the root.
  - **`--diagnostic-level`** stays at its default, `info`, so the gates' output also shows the infos that item 30 turns into errors.
  - **Not used:** `--use-server`, `lsp-proxy` (the editor extension's job), `clean`, and `explain daemon-logs`.
- **Shared flags** (CLI reference, shared by Nery on 2026-10-26). These are the CLI forms of the configuration's settings, and a flag overrides `biome.json`. An override anywhere would make one run differ from the others.
  - **Already right:**
    - No command in `package.json`, `scripts/gates.mjs`, `.github/workflows/` or `.claude/settings.json` passes a configuration, formatter, JSON-parser, VCS or watcher flag.
    - No `BIOME_*` variable is set in this environment (`env`, names only), so `BIOME_CONFIG_PATH`, `BIOME_WATCHER_KIND` and the rest leave the defaults.
    - The editor, the hooks, the gates and CI all read `biome.json` and `.editorconfig`, and nothing else.
  - **The one override:** the pre-commit hook passes `--files-ignore-unknown=true` (since `ac37c2e`), while `biome.json` sets `files.ignoreUnknown: false`. Probe in the scratch copy: with a staged `.sh` file, `biome check --staged --no-errors-on-unmatched` reported no diagnostic, with the flag or without it. The first `files.includes` pattern never selects an unknown extension, so the flag changes nothing today.
    - **Item 36:** drop the flag from `.husky/pre-commit`. The hook then runs under exactly the configuration the gates use.
    - Biome's git-hooks guide (shared by Nery on 2026-10-27) puts `--files-ignore-unknown=true` in its lint-staged and git-format-staged examples. Those tools pass every staged path (`'*'`), which needs the flag. This hook uses Biome's own `--staged`, which selects files through `files.includes`, so it does not.
    - The guide's `prepare: "husky"` is already in `package.json`.
    - Its stdin-based git-format-staged check fails on 2.6.3 even for a clean file. That keeps DEBT-036 a risk accepted; the evidence is now in its entry.
    - If `files.includes` ever widened to `**`, the hook would report an unknown staged file instead of skipping it. That is the strict choice `ignoreUnknown: false` already makes.
  - **JSON-parser flags** (`--json-parse-allow-comments`, `--json-parse-allow-trailing-commas`): never used, which keeps the manifests strict (section 11).
  - **`--watcher-kind`, `--watcher-polling-interval`:** the daemon's file watcher, left at `recommended`. They are the CLI form of the editor's `biome.lsp.watcher.*`, which section 12.4 leaves unset.
- **Environment variables** (Biome's environment-variables reference, shared by Nery on 2026-10-26). No `BIOME_*` variable is set in this environment, and none is set or read anywhere in `.github/workflows/`, `scripts/`, `.husky/` or `.claude/settings.json` (`git grep`). Two of them can silently replace what the gates are meant to run:
  - **`BIOME_BINARY`** "overrides the Biome binary used by the `@biomejs/biome` npm package". Probe: with it pointing at a fake binary that prints `Version: 9.9.9-fake`, both `node_modules/.bin/biome --version` and `npm exec -- biome --version` printed the fake version. That is the path `npm run` and the gates use. So the exact pin in `package.json` and `package-lock.json` holds only while the variable is unset.
  - **`BIOME_CONFIG_PATH`** points Biome at another configuration. Probe: with it pointing at a scratch config with `lineWidth: 20`, `biome ci scripts/lib.mjs` reported an error that the repository's configuration does not.
  - Today's partial guard: `.claude/hooks/repo-setup.sh` prints the repository's and the global `biome --version` at session start, so an overridden binary shows a different version there. It only reports, and only for the session's own environment.
  
  **Item 38:**
  - `scripts/gates.mjs` refuses to run its Biome gates while `BIOME_BINARY` or `BIOME_CONFIG_PATH` is set. It fails loudly with the variable's name, never its value, and says to unset it.
  - `.husky/pre-commit` gets the same check before its `biome check --staged`.
  
  This follows `~/.claude/CLAUDE.md` (fail loudly when an input is not what the check needs). The other option, dropping the two variables from the gates' environment the way `GIT_HOOK_VARIABLES` drops git's, would hide the override from whoever set it. The gates' tests get a case for each variable.
  - **Harmless, left alone:**
    - `BIOME_THREADS` (speed only);
    - `BIOME_WATCHER_KIND` and `BIOME_WATCHER_POLLING_INTERVAL` (the daemon's watcher);
    - `BIOME_LOG_*` (logging only, below);
    - `BIOME_DISTRIBUTION`, which only steers `biome upgrade` for the global standalone binary. Detection already works for `~/.local/bin/biome`, as `~/.claude/LESSONS.md` uses it.
  - **For a Biome panic** (a `FATAL` diagnostic, section 6.1.1): rerun with `RUST_BACKTRACE=1` and attach the backtrace to the upstream report.
- **Logging flags** (CLI reference, shared by Nery on 2026-10-26): `--log-file`, `--log-level` (default `none`), `--log-kind`, `--log-path`, `--log-prefix-name`, and their `BIOME_LOG_*` variables.
  - **Already right:** none is passed anywhere, and no `BIOME_LOG_*` variable is set, so every run logs nothing.
  - The daemon's rotated logs sit in `~/Library/Caches/dev.biomejs.biome/biome-logs`, the path `biome explain daemon-logs` prints: 5 files, 20 KB, as of 2026-10-27. No cleanup is needed, and `biome clean` exists if they grow.
  - **For troubleshooting only, never in a committed file:** `--log-level=debug --log-file=<scratch path>` on one CLI run. For the editor, `biome rage --daemon-logs` together with the extension's `biome.lsp.trace.server: "verbose"` (section 12) is the route the extension's reference gives. Checking 28e may need it.

### 6.5 Suppressions

Source: the linter guide's "Integration with editors" and "Migrate from other linters". `~/.claude/CLAUDE.md` requires Nery's approval and a written reason for every targeted suppression.

**Already right**, probed in the scratch copy:
- A suppression with an empty reason fails: `// biome-ignore lint/suspicious/noDebugger:` gave "Reason is missing and can't be empty" (`suppressions/parse`, an error).
- A suppression that suppresses nothing fails too: "Suppression comment has no effect" is a warning, and the gates' `--error-on-warnings` turns it into a failure.
- A top-level `biome-ignore-all` at the top of a file applies to the whole file.
- The repository holds no lint suppression today. `git grep biome-ignore` finds only the `biome-ignore format` marker that `scripts/generators/catalog.mjs` writes into the generated Markdown tables.
- **Formatter suppressions** (the formatter's "Ignore Code" page, shared by Nery on 2026-10-27): `biome-ignore format: <reason>` before a node, or `biome-ignore-all format: <reason>` at the top of a file. They follow the same approval rule as lint suppressions.
  - The one in the repository has both a reason and an owner: `<!-- biome-ignore format: generated by scripts/generators/catalog.mjs -->`. It keeps each generated catalog table byte-identical to the generator's output, so `--check` can compare them.
  - Generated JSON needs no suppression. `.claude-plugin/marketplace.json` is written with `JSON.stringify(…, 2)`, which `json.formatter.expand: "always"` already matches (section 8).

**Gap, closed by item 27:** the editor offers a one-click inline suppression and a one-click top-level suppression on every diagnostic. The guide's switches, `source.suppressRule.inline.biome` and `source.suppressRule.topLevel.biome`, both set to `"never"`, go into item 27's `.vscode/settings.json`. A suppression then exists only when someone writes it on purpose, with its reason.

**Never used here:**
- `biome lint --suppress --reason …`. It suppresses every current finding at once, which skips the per-suppression approval.
- `biome migrate eslint`. The repository has no ESLint configuration (`git ls-files` finds none, and `package.json` has no ESLint dependency).

### 6.6 Linter plugins

Source: the linter guide's "Plugins" section, as Nery shared it on 2026-10-26.
- **GritQL:**
  - a short DSL;
  - runs on every file unless restricted with `includes`;
  - no semantic model;
  - memory controlled by Biome.
- **JavaScript:**
  - more verbose;
  - has the semantic model and CST;
  - can slow every run;
  - its memory is outside Biome's control.

**Today:** no `plugins` key. The repository's conventions are checked by the Python validators in `scripts/validators/`, which cover manifests, names, versions, the catalog and skill references, not JS code, or by review.

**Candidate rule, from a past failure:** `scripts/lib.mjs` exports `isMain(metaUrl)`, which compares `import.meta.url` with `realpathSync(process.argv[1])`. Without the `realpathSync`, `check-repo.mjs` once ran nothing and exited 0 in the script tests on macOS only, because temp folders sit under the `/var` → `/private/var` link (recorded in `809cf90`'s memory notes). Every entry point now calls `isMain(import.meta.url)`, but nothing stops a new script from writing the comparison inline again.

| # | Change | Measured |
| --: | :-- | :-- |
| 32 | A GritQL plugin, `scripts/biome-plugins/main-module.grit`, registered with `includes: ["scripts/**", "!scripts/lib.mjs"]`. It reports any `===` comparison that involves `process.argv[1]` outside `isMain()`. `grit` joins the first `files.includes` pattern, as section 11.1 requires. | On 2.6.3 it caught a planted `import.meta.url === \`file://${process.argv[1]}\`` with its message, and reported nothing else in the repository. `biome ci .` went from 0.09 s and 69 MB to 0.13 s and 71 MB. |

- The plugin covers `scripts/**` only. The plugins under `plugins/` are self-contained and never import `scripts/lib.mjs`.
- A finding is suppressed only with `// biome-ignore lint/plugin: <reason>`, under the rule of section 6.5.
- A rewrite (`=>`) is left out on purpose: replacing an inline comparison with an import of `isMain` is a change to review, not an automatic fix. Without `fix_kind`, Biome would treat a rewrite as unsafe anyway.

**Plugin API facts the rule relies on** (the guide's "Target Languages" and "Plugin API"):
- A `.grit` file with no `language` line targets JavaScript and its super languages (TypeScript, JSX), which is what item 32 needs.
- `register_diagnostic` defaults to severity `error`, so the finding fails the gates with no `severity` argument. A `warn` would fail them too, through `--error-on-warnings`. A `hint` or `info` never would (section 6.1), so item 32 never sets either.
- Biome's GritQL also targets CSS and JSON. JSON rules are not needed here: the JSON-schema validators in `scripts/validators/` already check every manifest.

**Rejected:** JavaScript plugins. GritQL covers the one candidate. The guide marks JS plugins as a Developer Preview, where "breaking changes can happen in patch releases". That clashes with an exact-pinned Biome that Dependabot bumps weekly (section 11.4). The guide also warns that JS plugins can slow every downstream run, and that their memory is outside Biome's control.
 Assist actions

Source: the reference's `assist` section, the configuration schema of 2.6.3, and `biome explain <action>`. `biome ci` enforces assist actions by default (`--enforce-assist`, default `true`), so an enabled action that is not applied fails the gate.

**Already right:**
- `assist.includes` is unset, so assist covers what `files.includes` selects. No deprecated `actions.recommended` is used.
- The assist overview (biomejs.dev/assist, shared by Nery on 2026-10-26) counts 13 actions, and the 2.6.3 schema has exactly 13 under `source`. This section places each one:
  - `organizeImports` is on;
  - items 16, 17 and 18 are proposed;
  - D5 covers two;
  - five are rejected: `useSortedKeys`, `useSortedProperties` and the three GraphQL sorters (`useGraphqlSortedArguments`, `useGraphqlSortedDefinitions`, `useGraphqlSortedVariables`);
  - the last two also need GraphQL and sit under the same rejection: `useSortedSelectionSet`, `useSortedTypeFields`.
- The overview says assist is enforced through the CLI. Probe with an unsorted import:
  - `biome check` reported `organizeImports`, and `biome lint` did not.
  - The gates and the pre-commit hook run `biome ci` and `biome check --staged`, so assist is enforced.
  - `npm run fix` (`biome check --write`) applies its fixes.
  - `npm run format` (`biome format --write`) formats only and leaves imports unsorted, which `biome ci` then reports.

**Cleanup:**

| # | Key | Why it goes |
| --: | :-- | :-- |
| 15 | `assist.enabled: true` and `assist.actions.source.organizeImports: "on"` | `enabled` defaults to `true`. `organizeImports` is recommended, and `actions.preset` defaults to `"recommended"`. In the scratch copy, with the whole `assist` block deleted, `biome ci .` gave the same result, and a planted unsorted import still failed with `assist/source/organizeImports`. |

**Stricter:** measured one action at a time in the scratch copy.

| # | Action | Since | Files it would change (maintainer / plugins) |
| --: | :-- | :-- | :-- |
| 16 | `useSortedPackageJson` | 2.5.0 | 1 / 0: the root `package.json`, 18 lines moved |
| 17 | `noDuplicateClasses` | 2.4.0 | 0 / 0; it guards the mods' JSX `className` |
| 18 | `useSortedAttributes` | 2.0.0 | 0 / 3: `file-tree-pane/hooks/body.client.tsx`, `file-tree-pane/hooks/register.tsx`, `tool-ledger/hooks/register.tsx` (pull request) |

**For Nery (D5):** `useSortedInterfaceMembers` (2.4.0) and `useSortedEnumMembers` (2.5.0) report nothing today. Turning them on would force alphabetical order on every future interface and enum, even where members are grouped by meaning, for example a mod's types that follow the engine's payload.

**Rejected:**
- `useSortedKeys`: it would reorder object keys in 115 files (60 maintainer, 55 plugins), among them `plugin.json` manifests, `.lsp.json`, `hooks.json`, the JSON schemas and the generated `.claude-plugin/marketplace.json`, which the repository's scripts rewrite in their own order.
- `useSortedProperties`, `useSortedSelectionSet`, `useSortedTypeFields` and the GraphQL sorters: the repository has no CSS or GraphQL.

## 8. Formatter settings

Source: the reference's `formatter` section.

**Already right; keep:**
- `lineWidth: 100`. `.editorconfig` cannot carry it: Biome removed `max_line_length` (changelog), and the reference lists only `indent_style`, `indent_size`, `end_of_line` and `insert_final_newline` as read. 100 is also the root `ruff.toml` line length, Nery's standard since `809cf90`.
- `json.formatter.expand: "always"`. Commit `809cf90` gives the reason: the scripts write JSON with `JSON.stringify(…, 2)`, which always expands, so Biome's output matches what they write. Measured alternatives: `"auto"` would reformat 62 files (36 maintainer, 26 plugins) and `"never"` 70 (43 / 27).
- `useEditorconfig: true`, now the only source of indentation and line endings (item 2).
- `trailingNewline`, `formatWithErrors`, `bracketSpacing`, `delimiterSpacing`, `attributePosition` and `bracketSameLine` stay at their defaults and unset. `insert_final_newline = true` in `.editorconfig` agrees with `trailingNewline`.
- Markdown hard breaks survive. `.editorconfig`'s `trim_trailing_whitespace = false` for `*.md` is not a key Biome reads. Probe: a two-space hard break in a formatted Markdown file was kept, and a trailing tab was removed.

**Gap:**

| # | Change | Why |
| --: | :-- | :-- |
| 19 | Record the reason for each non-default setting | The reasons for `lineWidth`, `expand`, `quoteStyle`, `semicolons`, `jsxEverywhere`, `frontmatter`, the remaining `!!` patterns, each override (section 9) and each raised or added rule live only in commit bodies, or nowhere. DEBT-034 existed because of exactly this. Two ways (D4): rename `biome.json` to `biome.jsonc`, which the reference says always allows comments, and put a one-line reason beside each setting; or one ADR listing them. No script reads `biome.json` by name (`git grep` finds only Markdown); `.claude/CLAUDE.md` names it twice, and settled ADRs keep the old name as history. |

## 9. Overrides

Source: the reference's `overrides` section. When several overrides set the same single-value setting, the last match wins.

**Now:** two overrides.
- The tests override covers `**/*.test.{js,mjs,ts}`, `**/*.spec.{js,mjs,ts}`, `**/__tests__/**`, `**/test/**` and `**/tests/**`, and turns off `noConsole`, `noImplicitBoolean` and `useNamingConvention`.
- The `scripts/**` override turns off `noConsole`.

**Already right:**
- The scripts override keeps `noConsole` off where console output is the interface.
- The tests override keeps the stricter style rules out of test code.
- The order is safe: neither override sets a value the other one changes.

**Findings:**

| # | Change | Evidence |
| --: | :-- | :-- |
| 20 | Reduce the tests override's `includes` to `**/tests/**` | All 20 tracked JS and TS test files sit under a `tests/` folder (`git ls-files`). No tracked file matches `*.test.*`, `*.spec.*`, `__tests__/` or `test/` outside `tests/`, so those four patterns do nothing. Two of them list only `js`, `mjs` and `ts`, unlike the eight extensions in `files.includes`. The repository puts tests in `scripts/tests/<plugin>/` and `plugins/<plugin>/tests/` (`.claude/CLAUDE.md`, Maintainer Tooling). |
| 21 | Add an override for tsconfig files: `includes: ["**/tsconfig.json", "**/tsconfig.*.json"]`, `json.formatter.expand: "auto"` | Measured with the `!!` patterns removed: of the seven tsconfig files, only `scripts/tsconfig.json` changes, because its `include` line passes 100 columns. The four plugin tsconfig files pass unchanged, and `biome ci .` checks 169 files. The reason for `expand: "always"` (scripts write JSON with `JSON.stringify(…, 2)`, section 8) does not reach tsconfig files: no repository script writes one. Only the tests write throwaway ones, in temporary workspaces. |

**Considered, already settled:** an override that turns the formatter off but keeps linting on for the plugins' and skills' Markdown. `ADR_2026-10-26_biome-never-formats-plugin-and-skill-markdown` rejected lint-only, and this spec does not reopen it.

**Not needed today:**
- `overrides.<ITEM>.javascript.globals`: `b3ada31` left `javascript.globals` unset on purpose, because declaring Bun hid a real error.
- JSON `parser.allowComments` overrides: there is no `.vscode/`, and well-known files already allow comments.
- Per-path `files.maxSize` and per-path `plugins`.

## 10. JavaScript options

Source: the reference's "Language-specific options" and `javascript` sections. A language setting wins over its global one. With item 2 done, no language section sets indentation or line endings, so `.editorconfig` governs every language.

**Now:**
- `javascript.formatter`: `quoteStyle: "single"`, `jsxQuoteStyle: "double"`, `semicolons: "asNeeded"`, `trailingCommas: "all"`.
- `javascript.parser`: `jsxEverywhere: false`.

**Already right; keep:**
- `quoteStyle: "single"` and `semicolons: "asNeeded"`. Both differ from the defaults (`"double"`, `"always"`) and are Nery's standard config (`809cf90`). Their reason goes beside them with item 19.
- `jsxEverywhere: false`. Reason from `b3ada31`: Node runs the `.js`, `.mjs` and `.cjs` files, never as JSX. JSX lives only in the mods' seven `.tsx` files, and `biome ci .` passes with JSX refused elsewhere.
- `jsxRuntime` unset, so `"transparent"`. The mods never import a JSX factory: the engine declares `h` as a global (`.claude-plugin/types/claude-code/index.d.ts`), and the generated tsconfig sets `"jsx": "react"` with `jsxFactory: "h"`. `"reactClassic"` only treats a factory import as used. Measured: it changes nothing (163 files, the same 4 infos).
- `globals` unset (section 9).
- Unused, with nothing in the repository that needs them:
  - `unsafeParameterDecoratorsEnabled`: no decorators;
  - `experimentalEmbeddedSnippetsEnabled`: experimental, and there are no `css`, `styled`, `gql` or `graphql` templates;
  - `resolver.experimentalPnpmCatalogs`: the repository uses npm.

**TypeScript version** (language-support page, shared by Nery on 2026-10-27): Biome "supports TypeScript version 5.9", while the repository pins TypeScript 6.0.3 (`package.json`), and `typescript7-lsp-intelligence` serves TypeScript 7 users.
- Biome parses syntax. tsc stays the authority on types (`npm run typecheck`).
- Every tracked `.ts`, `.mts` and `.tsx` parses under Biome today, since `biome ci .` passes.
- If a file ever uses syntax newer than 5.9, Biome reports a parse error. A parse error is an error diagnostic, so the gate fails loudly rather than passing a file it cannot read (sections 6.1.1 and 6.4).
- Nothing to change. A Biome release that raises its supported version is a Dependabot pull request like any other.
- **JavaScript version**, from the same page: Biome supports ES2024, and adds syntax once a proposal reaches Stage 3, while `scripts/tsconfig.json` targets `es2025` with `ESNext.Collection` and `ESNext.Temporal`. Those are mostly APIs, which Biome does not need to know. A `git grep` found no ES2025-or-later syntax in the tracked code: no import attributes (`with { type: … }`), no `using` declarations, no RegExp modifiers (`(?i:…)`). The same parse-error safeguard applies.
- **Not applicable:** Google Apps Script (`.gs`), since no such file exists. Embedded CSS and GraphQL snippets, covered in this section.

**Cleanup:**

| # | Key | Why it goes |
| --: | :-- | :-- |
| 22 | `javascript.formatter.jsxQuoteStyle: "double"` and `trailingCommas: "all"` | Both are the defaults. Measured without them: 163 files, no fixes, the same 4 infos. |

Biome's "Formatter Option Philosophy" page (shared by Nery on 2026-10-27) backs this. Biome follows Prettier's option philosophy. It keeps options such as `arrowParentheses` and `bracketSameLine` only "for compatibility", calls them a cause of "bike-shedding", and adds no new ones. The four non-default formatter settings the repository keeps are `lineWidth`, `json.formatter.expand`, `quoteStyle` and `semicolons`. They are Nery's standard (`809cf90`), and item 19 writes their reasons beside them. Nothing here adds another.

**Not proposed:** the style options with no quality effect.
- `operatorLinebreak: "before"` would reformat 16 files.
- `arrowParentheses: "asNeeded"` would reformat 34 files.
- `quoteProperties: "preserve"` would reformat none, and keeping the default `"asNeeded"` is just as good.

## 11. JSON options

Source: the reference's `json` section.

**Now:** `json.formatter.expand: "always"` (section 8). Everything else is unset.

**Already right; keep:**
- `json.parser.allowComments` and `allowTrailingCommas` unset. Reason from `b3ada31`: a comment in a manifest must fail, as it does under `JSON.parse`. Probe: a comment in `turn-meter/.claude-plugin/plugin.json` failed `biome ci` ("Expected a property but instead found '// probe'"), and so did a trailing comma.
  - Unset, Biome follows each file's default. The well-known `tsconfig.json` and `tsconfig.*.json` still accept comments and trailing commas once item 1 lets Biome see them.
  - `biome.jsonc` always accepts both, so D4 (a) changes nothing for the manifests.
  - The language-support page (shared by Nery on 2026-10-27) adds the defaults for any `.jsonc` file: comments and trailing commas allowed, and the formatter's `trailingCommas` at `none`. No `.jsonc` file is tracked today. `biome.jsonc` (D4) and `.vscode/settings.json` (item 27) would be the first files Biome reads with comments allowed.
  - Every other tracked JSON is parsed strictly: 17 `plugin.json`, 10 `hooks.json`, 5 `.lsp.json`, 2 `.mcp.json`, the JSON schemas, the 3 `pyrightconfig.json`. This is stricter than pyright itself, which accepts JSONC, and no file needs more.
- `trailingCommas` unset (`"none"`), as the reference requires for strict JSON.
- `lineWidth` unset, so it inherits the global 100.
- `bracketSpacing`, `delimiterSpacing`, `trailingNewline` and `enabled` stay at their defaults.
- `!!**/package-lock.json`: npm writes it. Reason from `d86e3b1`, which keeps the plugins' npm lockfiles out of Biome. It goes beside the pattern with item 19.

**Finding:**

| # | Change | Evidence |
| --: | :-- | :-- |
| 23 | Let Biome check `.claude/settings.json`: delete `!!.claude/settings.json` | Commit `84afdae` added the exclusion with no reason. The file is tracked and passes today: in the scratch copy without the pattern, `biome ci .claude/settings.json` checked 1 file with no fixes. Once checked, a malformed or badly formatted settings file fails at commit instead of reaching every session. `.claude/settings.local.json` stays excluded: it is personal, and git ignores it. |

### 11.1 GraphQL and GritQL options

Source: the reference's `graphql` and `grit` sections.

- **Now:** both are unset. No tracked file is GraphQL or GritQL (`git ls-files '*.graphql' '*.gql' '*.graphqls' '*.grit'` finds 0), and the first `files.includes` pattern lists neither extension, so Biome never opens one. Nothing to change.
- **Condition, now met by item 32 (section 6.6):** a GritQL lint plugin adds `.grit` files. That commit adds `grit` to the first `files.includes` pattern. Without it, Biome would load the plugin but never format or lint the plugin's own source. Indentation and line endings would then come from `.editorconfig`, like every other language. GritQL assist is on by default (`grit.assist.enabled: true`). GraphQL assist is off by default (`graphql.assist.enabled: false`), so the GraphQL sorters of section 7 could not run even if GraphQL files appeared.

### 11.2 Markdown options

Source: the reference's `markdown` section. Biome checks 13 Markdown files: `README.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, the six `docs/*.md`, and the test fixture `scripts/tests/svelte-development/kit3-app/README.md`. Every other Markdown file is excluded under `ADR_2026-10-26_biome-never-formats-plugin-and-skill-markdown`.

**Now:** `markdown.parser.frontmatter: true`. Since item 2, nothing else is set.

**Already right; keep:**
- `frontmatter: true`, added in `e1d58b2`. None of the 13 files has frontmatter today, but the setting protects any that gets one. Probe with a `docs/` file starting with `---`:
  - With it on, Biome formatted the block as YAML (`title:   Probe` became `title: Probe`, `[a,b]` became `[a, b]`).
  - With it off, Biome inserted a blank line after the opening `---`, which breaks the frontmatter, and left the YAML unformatted.
- `gfm` unset (`true`): the README and `docs/` use tables.
- `cjkFriendlyEmphasis` unset (`false`): the documentation is in English and contains no CJK text.
- `formatEmbeds` unset (`true`). It formats the three `json` fences. The `bash`, `sh` and `text` fences (14) stay as written, since Biome has no formatter for them. `biome ci .` passes as it is.
- `proseWrap` unset (`"preserve"`): line breaks stay as written, so a one-word edit keeps a one-line diff. `lineWidth` (100) wraps paragraphs only under `"always"`.

**Stricter:**

| # | Change | Since | Findings |
| --: | :-- | :-- | :-- |
| 24 | `nursery.useTopLevelHeading` and `nursery.useConsistentUnicodeBom` set to `"error"` | 2.5.8 and 2.6.3 | 0 in the 163 files |

- Together with the three rules already on (`useConsistentHeadingLevel`, `useFencedCodeLanguage`, `useSingleTopLevelHeading`), these are every nursery Markdown rule in 2.6.3. The one non-nursery Markdown rule, `suspicious.noEmptySource`, is item 33 (section 11.6). The list comes from `biome explain` on the 154 nursery rules in the configuration schema.
- With `preset: "all"` and the whole nursery group on, the 13 files gave no diagnostic.
- `useConsistentUnicodeBom` disallows a byte order mark by default. The reference calls nursery rules unstable, so a Biome upgrade can rename or move them. The upgrade's `biome migrate` handles that.

**Rejected:** `analyzeEmbeds: true`. It gave 50 parse errors: 10 in `README.md`, 18 in `docs/faq.md`, 22 in `docs/troubleshooting.md`. Every one is the GitHub pattern that opens `<div align="center">` or `<details><summary>` in one HTML block, puts Markdown inside, and closes the tag in a later block. Biome parses each HTML block alone, so it reports "Expected a closing tag" and "This closing tag has no matching opening tag" for valid Markdown. Reconsider when Biome parses split HTML blocks together.

### 11.3 YAML options

Source: the reference's `yaml` section.

- **Scope:** Biome checks 12 YAML files: `.claude/skills/testing-plugins/assets/evals-ci.yml` and the eleven `plugins/*/evals/**/case.yaml`. `.github/` is force-ignored, as `.claude/CLAUDE.md` (Maintainer Tooling) requires; actionlint covers the workflows. In the scratch copy without that exclusion, Biome would reformat `.github/workflows/claude.yml` and `claude-code-review.yml`. Not proposed, because the project rule decides it.
- **Now:** nothing set under `yaml`, and all 12 files pass.
- **Already right:**
  - `indentWidth` comes from `.editorconfig` (2). YAML has no `indentStyle` option, since YAML indents only with spaces, which matches `indent_style = space`.
  - `lineWidth` inherits 100.
  - `quoteStyle` stays at its default, `"double"`, unlike JavaScript's `"single"`. All 12 files already pass with it under `biome ci .`.
  - Markdown frontmatter (section 11.2) is formatted with these same settings.
- **Gap:** `yaml.linter.enabled` is `true`, yet no YAML rule runs. The only YAML rule in 2.6.3 is `nursery.noDuplicateMapKeys` (since 2.6.0), and the preset never enables nursery rules. Probe: a file with `a: 1`, `b: 2`, `a: 3` passes today. With the rule on, it fails with "The key a was already declared". Item 25 covers it.

### 11.4 Recommended nursery rules

The reference calls nursery rules unstable and says they need an explicit opt-in. `biome explain` marks 37 of the 154 nursery rules in 2.6.3 as recommended, but the preset turns on none of them. The repository enables three (`useConsistentHeadingLevel`, `useFencedCodeLanguage`, `useSingleTopLevelHeading`). The reference allows a group `preset` only for non-nursery groups, so each rule has to be listed by name.

| # | Change | Findings |
| --: | :-- | :-- |
| 25 | Enable the other 34 recommended nursery rules at `"error"` | 6: `scripts/gates.mjs:591` (`noUselessAssignment`); in `file-tree-pane`, `hooks/register.tsx:1789` (`noUselessAssignment`), `hooks/body.client.tsx:38`, `tests/pane.test.tsx:594` and `:795` (`useCapitalizedConstructors`), `tests/units.test.ts:297` (`noEagerArrayMethodsInLoops`) |

The 34 rules: `noAccidentalBitwiseOperators`, `noArgumentsCallerOrCallee`, `noArraySortForMinMax`, `noBooleanSortComparator`, `noDoubleComparison`, `noDuplicateMapKeys`, `noEagerArrayMethodsInLoops`, `noImpliedEval`, `noInvalidPropertyInitValue`, `noJsonUnsafeValues`, `noMisplacedListElements`, `noObsoleteAttributes`, `noOctal`, `noPathConcat`, `noReturnInFinally`, `noUnsafeIframeSandbox`, `noUselessAssignment`, `noUselessCall`, `noUselessDateGetTime`, `noUselessSplice`, `noXorAsExponentiation`, `noZeroLengthUnit`, `useBigintLiterals`, `useBlockStatementOverIife`, `useCapitalizedConstructors`, `useConsistentObjectKeys`, `useFlatMathMinMax`, `useMathAbs`, `useMathTrunc`, `useModernMathApis`, `usePackageJsonValidCpu`, `usePackageJsonValidEngines`, `useSimplifiedBooleanReturn`, `useUnaryMinus`.

- Each finding is fixed, or suppressed with Nery's approval and a written reason.
- **The 2.6.3 changelog** (shared by Nery on 2026-10-27) shows how new these rules are. 2.6.3 itself added eleven of the 34: `noArraySortForMinMax`, `noBooleanSortComparator`, `noEagerArrayMethodsInLoops`, `noObsoleteAttributes`, `noPathConcat`, `noUselessSplice`, `noZeroLengthUnit`, `useBlockStatementOverIife`, `useMathAbs`, `useMathTrunc`, `usePackageJsonValidCpu` and `usePackageJsonValidEngines`. It also added item 24's `useConsistentUnicodeBom`. That is why the semver warning below matters.
- **New in 2.6.3 but not recommended,** measured one at a time with `--only`:

  | Rule | Default | Findings (maintainer / plugins) | Verdict |
  | :-- | :-- | :-- | :-- |
  | `noUnsafeReturn` (`types`) | info | 5 / 1 | **Item 40**, at `"error"`: returning an `any`, such as `JSON.parse(…)`, from a function hides an unchecked shape. The scripts read many JSON manifests, and `~/.claude/CLAUDE.md` asks that critical data be validated where it is received. |
  | `noNewRequire` | warn | 0 / 0 | **Item 40**, at `"error"`: free, and `new require(…)` is always a mistake |
  | `noUnreadableForOfExpression` | info | 9 / 6 | Rejected: a readability preference with no correctness effect |
  | `useIteratorZip` | info | 0 / 1 | Rejected: `Iterator.zip()` needs a recent runtime, and plugins run on users' unknown Node versions (`.claude/CLAUDE.md`, Plugin Tooling) |
  | `noDanglingUnderscore` | info | 0 / 0 | Rejected: it forbids the leading `_` that marks a deliberately unused binding, which Biome's own unused-variable rules accept |

- **Other 2.6.3 fixes that touch this spec:**
  - Since #12593, the default reporter writes its command summary to stderr. `biome migrate` prints "no migration needed" on both streams on 2.6.3, but item 37's gate checks stdout and stderr together, so a later move cannot hide it.
  - #12526 and #12509 fixed Markdown formatter defects, two of them with `proseWrap` `"always"` or `"never"`, which this repository does not use (section 11.2). The repository is already on 2.6.3.
- A Biome upgrade can add, rename or promote nursery rules. The upgrade runs `biome migrate` and rechecks the recommended list with `biome explain`.
- The linter guide warns that nursery rules "are not subject to semantic version", and may still have bugs or performance problems even when recommended. A patch release can therefore change what items 24 and 25 report. Two things contain the risk:
  - `@biomejs/biome` is pinned to an exact version in `package.json`.
  - Dependabot proposes each new version weekly, as its own pull request (`.github/dependabot.yml`, the `npm` entry).
  
  If a nursery change breaks that pull request's CI, the change is fixed or the rule is adjusted in that pull request, never on `main`.

### 11.5 Glob patterns

Source: the reference's "Glob syntax reference". Every pattern in `files.includes` and in the overrides was checked against it, together with the patterns this spec adds.

**Already right:**
- No pattern uses unsupported syntax: no `?`, no `[…]` classes, no nested `{…}`, no partial or consecutive `**`. That covers all 23 `files.includes` entries, both overrides, item 21's `**/tsconfig.json` and `**/tsconfig.*.json`, and D1 (a)'s `!plugins/*/tsconfig.json`.
- The list starts with a positive pattern (`**/*.{js,cjs,mjs,jsx,ts,cts,mts,tsx,json,jsonc,md,yml,yaml}`). After it, each entry only excludes, so "the last matching pattern wins" never puts back a file an earlier entry removed.
- In `files.includes`, directories are excluded in the directory form (`!.claude/memory`, `!!.github`, `!!**/dist`). The overrides, which filter files, use the `/**` form (`scripts/**`, `**/tests/**`), as the reference requires.
- `!!` appears only in `files.includes`, the only place where it means force-ignore.
- `!.claude/skills/building-plugins/assets/plugin-template.json` uses `!`, not `!!`. The template's `{{…}}` placeholders are not JSON (`809cf90`). The item 8 run, with the `project` and `types` scanner on, still gave the same 163 files and diagnostics, so scanning near it causes no error.
- **CLI globs:** no command hands Biome a glob for the shell to expand.
  - `package.json` runs `biome … .`.
  - The pre-commit hook runs `biome check --staged`.
  - `scripts/gates.mjs` builds real paths from `git ls-files` (top-level names for the maintainer run, `plugins` for the plugin run).

**Cleanup:**

| # | Pattern | Why it goes |
| --: | :-- | :-- |
| 26 | `!**/SKILL.md` | Added in `e1d58b2`, before the broader exclusions existed. Every tracked `SKILL.md` sits under `plugins/` or `.claude/skills/`, already excluded by `!plugins/**/*.md` and `!.claude/skills/**/*.md` (`git ls-files` finds none elsewhere). Measured without it: 163 files, no fixes, the same 4 infos. `!**/CLAUDE.md` stays: `.claude/CLAUDE.md` matches no other exclusion, and Nery's list in `ADR_2026-10-26_biome-never-formats-plugin-and-skill-markdown` covers every `CLAUDE.md`. |

### 11.6 JSON and Markdown rules

Source: the rule lists for JSON and Markdown (biomejs.dev/linter), as Nery shared them on 2026-10-26, checked with `biome explain` on 2.6.3.

**JSON, already active through the preset:**
- `noBiomeFirstException` (error) and `noDuplicateObjectKeys` (error). Item 7 removes only the explicit JS entry; the preset keeps the rule for both languages.
- `useBiomeIgnoreFolder` (warn), which `biome.json` passes today. The scratch runs of items 1, 3, 21, 23 and 26 found no `useBiomeIgnoreFolder` diagnostic either.
- `noQuickfixBiome`, which is `info`, so item 30 raises it.

**JSON and Markdown nursery rules already covered:**
- Item 25: `noJsonUnsafeValues`, `useConsistentObjectKeys`, `usePackageJsonValidCpu`, `usePackageJsonValidEngines`.
- Item 24: `useConsistentUnicodeBom`, `useTopLevelHeading`.
- The three Markdown rules already on: `useConsistentHeadingLevel`, `useFencedCodeLanguage`, `useSingleTopLevelHeading`.
- The page lists no recommended Markdown rule, while `biome explain` marks those three as recommended. The linter guide explains why: a nursery rule marked "recommended" is one Biome plans to recommend once it is stable, and stable versions never turn it on by themselves.

**Not used yet:** each one was measured at `"error"` in the scratch copy, and each gives 0 findings today. The table gives what it catches, as a planted case or from the rule's documentation.

| # | Rule | Since | What it catches |
| --: | :-- | :-- | :-- |
| 33 | `suspicious.noDuplicateDependencies` | 2.2.4 | A package listed twice across `package.json` sections. Planted `husky` in `dependencies` and `devDependencies`: caught. |
| 33 | `nursery.noRestrictedDependencies` | 2.5.0 | An import with a better native or modern replacement, from e18e's data. Planted `import fs from 'fs-extra'`: caught. |
| 33 | `suspicious.noEmptySource` (default `warn`) | 2.6.0 | An empty file, or an empty YAML document between `---` lines. Planted an empty `docs/*.md` and an empty `scripts/*.mjs`: both caught. |
| 33 | `suspicious.noEmptyObjectKeys` | 2.4.7 | A `""` key in JSON. |
| 33 | `style.noTopLevelLiterals` | 2.4.7 | A JSON file whose top level is not an object or an array. |
| 33 | `suspicious.useRequiredScripts`, with `requiredScripts`: `test`, `typecheck`, `lint`, `format`, `fix`, `validate`, `gates`, `setup`, `generate` | 2.3.9 | A missing maintenance script in `package.json`. `.claude/CLAUDE.md` requires every maintenance command to be an `npm run` script. The rule takes exact names, so the `check:*` family stays outside it. |

`noRestrictedDependencies` also checks `plugins/`. A finding there is fixed in that plugin's pull request, like the other plugin findings.

**Not proposed:** `suspicious.noUntrustedLicenses` (2.4.9, `project` domain). With `deny: ["MIT"]` set to force a finding, linting `package.json` reported nothing, so it is unverified which files the rule checks. The four dev dependencies are `MIT OR Apache-2.0` (Biome), `Apache-2.0` (TypeScript), `MIT` (Husky) and `MIT` (`@types/node`). They do not ship to users.

### 11.7 One configuration, and the v2 breaking changes

Sources: the guides "Use Biome in big projects" and "Upgrade to Biome v2: breaking changes", as Nery shared them on 2026-10-27.

**One root configuration, and no nested one:**
- `biome.json` is the only tracked Biome configuration, and the only one on disk outside `node_modules`.
- The SvelteKit fixture `scripts/tests/svelte-development/kit3-app` ships only `.example` files.
- No worktree exists today. A worktree under `.claude/worktrees/` is a full checkout with its own root `biome.json`, which is the guide's "vendored folder" case. `!!.claude/worktrees` already keeps it out, as the guide advises.

**Nested configurations in `plugins/<plugin>/`, rejected:** `extends: "//"` would let a plugin carry its own settings, but a file inside `plugins/<plugin>/` ships to users with the plugin. A maintainer `biome.json` there would put the maintainer's tooling into what users install, which `.claude/CLAUDE.md` forbids (Maintainer and Plugin Scopes). Per-plugin needs go through the root configuration's `overrides`, as item 21 does for the tsconfig files.

**A shared configuration across Nery's repositories** (`extends` with a path, or a published npm package): not adopted. `809cf90` records `biome.json` as "Nery's standard config (from claude-essentials)". That standard could become one extended file, but a public repository cannot extend a local path, and publishing a package adds a release process for one consumer. Revisit when a second repository needs to stay in step with this one. The "Publish packages" guide (shared by Nery on 2026-10-27) gives the shape for that day. Since 2.6 it is a package whose `exports.biome` points at a `biome-manifest.json` (`"version": 1`, a `configs` list and optionally `plugins.rules` and `plugins.presets`), listed under the `biome-plugin` keyword. Consumers write `extends: ["<package>/configs/<name>"]`. The guide warns that a path beginning with `.` or ending in `.json` is read as relative and never resolved from `node_modules`. Item 32's local `.grit` file needs none of this: a plain relative path in `plugins` is enough for one repository.

**v2 breaking changes, checked against the tracked files** (`git grep`):
- **No Rome leftovers:** no `rome.json`, no `rome-ignore`, no `ROME_BINARY`. No old suppression form, `biome-ignore lint(group/rule)`.
- **No `ignore` or `include` keys:** the configuration uses `includes`, and `biome migrate` reports nothing to migrate (section 6.4.1).
- **Globs are relative to the configuration, and `*` no longer crosses `/`:** every pattern in this spec is written for that, including item 21's `**/tsconfig.json` and `**/tsconfig.*.json`, and item 32's `scripts/**` (section 11.5).
- **No `import … assert { … }`:** the old syntax that v2 dropped for `with`.
- **`style` rules no longer error by default:** the configuration sets each style rule it wants at its own level, and the gates fail on warnings.
- **The import organizer no longer puts bare Node built-ins first.** No tracked file imports a bare built-in such as `'fs'` or `'path'`: all use the `node:` protocol. Item 30 turns `useNodejsImportProtocol` into an error, which keeps it that way.
- **`linter.rules.all` was removed in v2,** and `rules.preset: "all"` is its current form. Section 13 rejects it on measured findings, not on the old option.

## 12. Editor setup (VS Code)

The goal: on save, VS Code does exactly what `npm run format`, the pre-commit hook and the gates do, and never touches a file Biome excludes. VS Code matters here even though Nery does not edit in it: its diagnostics reach Claude Code sessions through the IDE integration (`~/.claude/LESSONS.md`).

### 12.1 Sources and installed versions

- The extension's settings reference, as Nery shared it on 2026-10-26 (biomejs.dev/reference/vscode). Also read on biomejs.dev: "Use Biome in your editor" and the first-party extensions guide. From Context7 `/biomejs/website`: `configuration/editors.mdx` and the `noQuickfixBiome` rule page.
- `biomejs/biome-vscode`: `CHANGELOG.md`, `src/locator.ts`, `src/utils.ts`, and the release list (latest tag `v3.8.0`, 2026-10-21; the changelog's top entry is 3.8.1).
- `biomejs/biome`: `crates/biome_lsp/src/extension_settings.rs` and `session.rs`, the server side of the extension's settings.
- Installed: VS Code 1.143.1; `biomejs.biome` 3.8.1, which needs VS Code ^1.91.0 (its manifest). Version 3.8.0 added Markdown and YAML support, which the formatter setup below needs. Also installed: `davidanson.vscode-markdownlint` 0.62.1, `esbenp.prettier-vscode` 12.4.0, `redhat.vscode-yaml` 2.0.0, `editorconfig.editorconfig` 0.18.2.

### 12.2 What already works

- **Which binary runs.** `src/locator.ts` looks for Biome in this order: `biome.lsp.bin`, the project's `node_modules`, Yarn PnP, then `PATH`. After `npm ci`, the editor runs the same pinned 2.6.3 as the CLI, the hooks and the gates. So `biome.lsp.bin` stays unset: it would only pin a platform-specific path. Without `node_modules`, the editor falls back to `~/.local/bin/biome`, which is also 2.6.3 today.
- **Nery's user settings** already set:
  - `biome.requireConfiguration: true`, so Biome runs only where a configuration file is loaded. The server returns "Missing" when no configuration path was found (`session.rs`). That path comes from the same loader as the CLI, which also loads `biome.jsonc`: probed by renaming the scratch copy's config to `biome.jsonc` with a comment, after which `biome rage` reports `Path: biome.jsonc` and `biome ci .` passes. D4 (a) therefore keeps the editor working; this last step is inferred from the shared loader, not tested in VS Code.
  - `biome.suggestInstallingGlobally: false`.
  - Biome as the formatter of JavaScript, TypeScript, JSX, TSX, JSON and JSONC.
  - `source.fixAll.biome` and `source.organizeImports.biome` set to `"explicit"`, and no `quickfix.biome`, which the recommended rule `suspicious/noQuickfixBiome` forbids.
- **Excluded files stay untouched.** Probe in the editor's stdin mode: `biome format --stdin-file-path=plugins/turn-meter/README.md` returned the file unchanged, with "The content was not formatted because the path … is ignored". The same command on a path under `docs/` formatted the content. So with Biome as the Markdown formatter, saving a never-format file in VS Code changes nothing.
  - **Limit, from the CLI reference and a probe:** `--stdin-file-path` with a virtual path, one not on disk, "bypass[es] `files.includes` and VCS ignore checks".
    - `plugins/turn-meter/NEW-NOT-ON-DISK.md` and `.claude/skills/x/NEW.md`, neither of which exists, both came back formatted.
    - The existing `plugins/turn-meter/README.md` came back unchanged.
    
    A file VS Code saves exists on disk, so the protection holds for it. That last step is inferred: the editor talks to Biome through the LSP, not through stdin. No script or hook in the repository uses `--stdin-file-path` (`git grep`).
- **Shared basics:** `.editorconfig` is read by the EditorConfig extension. The user settings set `editor.rulers: [100]` (the `lineWidth`), and keep trailing whitespace in Markdown (`files.trimTrailingWhitespace: false`), which matches `.editorconfig`.

### 12.3 Conflicts in Nery's user settings

These come from `~/Library/Application Support/Code/User/settings.json`, which is outside the repository.

| # | Setting now | Effect in this repository |
| --: | :-- | :-- |
| 28a | `[markdown]` formatter `DavidAnson.vscode-markdownlint`, with `editor.formatOnSave: true` | Saving any Markdown file applies markdownlint's fixes, including the files Biome must never format (`plugins/`, `.claude/skills/`, every `CLAUDE.md`, and the rest). The 13 files Biome formats get a different formatter on save than under `npm run format`. |
| 28b | `[yaml]` formatter `esbenp.prettier-vscode`, with `prettier.requireConfig: true` | The repository has no Prettier config, so YAML is not formatted on save, while `npm run format` formats it with Biome. The difference shows up only at commit. |
| 28c | markdownlint lints `allFiles` on type (`markdownlint.appliesTo`, `markdownlint.run` defaults), and there is no markdownlint config in the repository | Its default rules produce diagnostics on every Markdown file, the never-format ones included. Through the IDE integration they reach Claude sessions, beside Biome's own Markdown rules. |
| 28d | `js/ts.preferences.quoteStyle: "double"` | Auto-imports insert double quotes. Biome rewrites them to single on save: harmless churn. |
| 28e | Top-level `codeActionsOnSave` turns on `source.action.noDuplicateClasses.biome` and `source.action.useSortedAttributes.biome` | Unverified: whether Biome offers an assist action that `biome.json` does not enable. If it does, saving a mod's `.tsx` would sort JSX attributes that the gates do not require yet (item 18). To check: save `plugins/file-tree-pane/hooks/register.tsx` in VS Code on a scratch branch. |

Nery said on 2026-10-26 that Biome is the global default and that `~/.claude/ENVIRONMENT.md` says so. The file does not: it names `biome` only in the `PATH` order (entry 1), and `~/.claude/LESSONS.md` covers only its installation. The user settings' own comment chose Biome as "never a global default". The reason: with `requireConfiguration: true`, a project without a Biome configuration would have no formatter at all for those languages.

### 12.4 Changes

| # | Change | Scope |
| --: | :-- | :-- |
| 27 | Commit `.vscode/extensions.json` and `.vscode/settings.json` (D6) | Maintainer, direct commit |
| 28 | Fix 28a to 28d in the user settings (D7) | Nery's machine, outside the repository |
| 29 | State in `~/.claude/ENVIRONMENT.md` that Biome is the default formatter for the languages it supports, and that a project without a Biome configuration keeps VS Code's own formatter | Global instructions |

Item 27's content:

- `.vscode/extensions.json`:
  - `recommendations`: `biomejs.biome` and `editorconfig.editorconfig`;
  - `unwantedRecommendations`: `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode` and `davidanson.vscode-markdownlint`.
  
  The migration guide's "After migrating" step says to replace the other tools' editor extensions with Biome's. The repository has no ESLint, Prettier or Stylelint dependency or configuration, so `biome migrate eslint|prettier|stylelint` has nothing to import (section 6.4.1). Nery keeps those extensions installed for other projects, so this repository turns them off for itself instead of removing them.
- `.vscode/settings.json`:
  - `[markdown]` and `[yaml]`: `editor.defaultFormatter: "biomejs.biome"` and `editor.codeActionsOnSave` with `source.fixAll.biome: "explicit"`. This holds in any clone or worktree, whatever the user settings say.
  - `js/ts.preferences.quoteStyle: "single"`.
  - `eslint.enable: false` and `prettier.enable: false`, both `resource`-scoped settings in the installed extensions' manifests. With them, neither extension lints or formats here, whatever the user settings say.
  - `markdownlint.appliesTo: "noFiles"`. The enum is `allFiles`, `projectFiles`, `workspaceFiles`, `noFiles` (the extension's manifest), and Biome lints the Markdown it covers.
  - `source.action.useSortedAttributes.biome: "never"` and `source.action.noDuplicateClasses.biome: "never"`, until items 17 and 18 enable those actions in the configuration, if 28e proves the risk.
  - `source.suppressRule.inline.biome: "never"` and `source.suppressRule.topLevel.biome: "never"` (section 6.5).
  - **Assist on save follows the configuration.** The assist overview's IDE section ("Use assist actions in your IDE") says `source.fixAll.biome` applies the lint fixes. Each assist action runs on save only through its own code action, `source.action.<action>.biome`. `organizeImports` is the exception, with `source.organizeImports.biome`. So `.vscode/settings.json` lists `source.organizeImports.biome: "explicit"`, plus each assist action that `biome.json` enables:
    - item 16 adds `source.action.useSortedPackageJson.biome`;
    - item 17 adds `source.action.noDuplicateClasses.biome`;
    - item 18 adds `source.action.useSortedAttributes.biome`;
    - D5, if on, adds `source.action.useSortedInterfaceMembers.biome` and `source.action.useSortedEnumMembers.biome`.
    
    Each one goes in with `"explicit"`, in the commit that enables it in the configuration, and replaces any `"never"` above. On save, the editor then applies exactly the actions `biome ci` enforces, no more and no fewer.
- **Not needed:** an assist-only gate (`biome check --formatter-enabled=false --linter-enabled=false`, from the same page). The gates' `biome ci` already enforces assist together with the formatter and the linter (section 7).
- Biome checks both files: they match `**/*.json`, and nothing excludes them. They are well-known files that allow comments, and `noQuickfixBiome` guards them.

**Not used:**
- `biome.inlineConfig`: it makes the editor differ from the CLI and the gates.
- `biome.gotoDefinition`: tsserver already does that.
- `biome.configurationPath`: the config sits at the root.
- `biome.lsp.watcher.*`: no watcher problem has been seen.
- The 3.8.1 manifest does not contribute `biome.inlineConfig` or `biome.gotoDefinition`, although the server reads both (`extension_settings.rs`). Unverified whether the extension passes them on.

## 13. Rejected

The assist actions rejected are listed in section 7.

- **`rules.preset: "all"`:** hundreds of findings from rules that do not fit this repository, such as `useQwikValidLexicalScope` (162), `noNodejsModules` (60), `noTernary` (340) and `useConsistentTestIt` (273).
- **`correctness.noUnresolvedImports`:** 28 false findings on the mods' `claude-code` and `claude-code/testing` imports. Those resolve through `typeRoots` and ambient `declare module` in the engine-generated `.claude-plugin/types/tsconfig.json`, which Biome does not read for resolution.
- **JavaScript plugins and per-rule `fix` overrides:** see sections 6.6 and 6.3. GritQL plugins are adopted for one rule (item 32), with section 11.1's `files.includes` change.

## 14. Decisions for Nery

**Approved by Nery on 2026-10-27, each with its recommendation:** D1 (c), D2 15, D3 the proposed order, D4 (a) `biome.jsonc`, D5 off, D6 (a) commit, D7 (a), D8 (a), D9 (a). Each decision that shapes the configuration gets its ADR in the commit that implements it.

- **D1, the plugin tsconfig files (item 1):**
  - (a) Keep them out with a regular `!plugins/*/tsconfig.json`, recorded in an ADR, as with the plugins' Markdown. No releases.
  - (b) Include them under the JSON-wide `expand: "always"`, with one pull request covering the four mods, each with a patch bump and changelog entry.
  - (c) Include them with item 21's override. All seven are checked, no plugin file changes, and nothing is left out.
  - Recommended: (c). It is the only option that checks every tsconfig without touching a plugin.
- **D2, item 13's threshold:** the default 15, or another value.
  - Recommended: 15. It is Biome's default, and at 15 the rule reports 35 functions (7 maintainer, 28 plugins), so it already demands real refactoring. No measurement here supports a different number. Lowering it adds findings without evidence that those functions are harder to maintain, and raising it hides some of the 35.
- **D3, the order of items 9 to 14:** the proposal is 9, 10, 11, 12, 13, 14.
  - Recommended: that order.
    - `noSecrets` comes first, because a leaked secret is the only one of these findings that can harm users or Nery's accounts.
    - Then by rising cost of the fix: `noShadow` (10 findings), `noAwaitInLoops` and `noNestedTernary` (mechanical rewrites), then `noExcessiveCognitiveComplexity` (refactoring).
    - `useTopLevelRegex` comes last: it has the most findings (294), and its own documentation warns it can slow startup, which needs measuring in the hooks first.
- **D4, where the reasons live (item 19):**
  - (a) `biome.jsonc`, with a comment beside each setting.
  - (b) One ADR.
  - Recommended: (a). The reason then sits where the setting is changed, and it moves with any edit.
- **D5, interface and enum sorting (section 7):** on or off.
  - Recommended: off. Both report nothing today, so turning them on fixes nothing. They would only force alphabetical order on future interfaces and enums, where members are often grouped by meaning, such as a mod's types that follow the engine's payload. The assist overview says its actions are "not meant to … impose a particular coding style".
- **D9, how item 38 handles `BIOME_BINARY` and `BIOME_CONFIG_PATH`:**
  - (a) Refuse to run, naming the variable.
  - (b) Drop the two variables from the gates' environment, the way `GIT_HOOK_VARIABLES` drops git's.
  - Recommended: (a). `~/.claude/CLAUDE.md` asks the receiving side to fail loudly, and (b) would silently overrule whoever set the variable.
- **D8, `useLiteralKeys` (item 30, DEBT-032):**
  - (a) Turn it off for JS and TS, with the reason beside it: tsc's `noPropertyAccessFromIndexSignature` already decides how index-signature keys are written, and its bracket form is the stricter of the two.
  - (b) Drop `noPropertyAccessFromIndexSignature` from `tsconfig.base.json`, and raise `useLiteralKeys` with the other 23.
  - Recommended: (a). It keeps the stricter type-check, and closes DEBT-032 as resolved.
- **D6, the `.vscode/` files (item 27):**
  - (a) Commit them. Every clone and worktree under `.claude/worktrees/` gets them. They hold no secret, and a reader of the public repository sees only editor preferences.
  - (b) Keep them local and add `.vscode/` to `.gitignore`.
  - Recommended: (a).
- **D7, Markdown and YAML in the user settings (item 28):**
  - (a) Make Biome their global default formatter, like JS and JSON. A project without a Biome configuration then has no Markdown or YAML formatter on save, as JS already has none there today.
  - (b) Keep markdownlint and Prettier global, and rely on item 27's workspace override in this repository.
  - Recommended: (a), as Nery stated, recorded by item 29. Item 27 stays either way, so the repository does not depend on one machine's settings.

## 15. Order and commits

1. **Done.** Items 1, 21 and 23 are in one commit, with ADR_2026-10-27_biome-checks-every-tsconfig-with-auto-expand, and DEBT-034 closed as resolved. Item 2 is in `db0dfab`.
2. Items 3 to 7, 15, 20, 22 and 26: one commit. Item 34 (`package.json`'s `format` script): its own commit. Item 36 (`.husky/pre-commit`): its own commit, checked by committing a change that stages a `.sh` file next to a `.mjs` file. Item 37 (`scripts/gates.mjs`, `scripts/tests/gates.test.mjs`): its own commit, before any Biome upgrade. Item 38 (`scripts/gates.mjs`, `.husky/pre-commit`, `scripts/tests/gates.test.mjs`): its own commit, checked by running `npm run lint:js` with each variable set, to see the refusal, and unset, to see the pass. Item 35 (`scripts/gates.mjs`): its own commit, before step 8, so the gates show every finding of items 9 to 14. `scripts/tests/gates.test.mjs` does not pin Biome's arguments, so the check is a run of `npm run lint:js` with a planted file that has more than 20 findings, to confirm every one is printed.
3. Item 19: one commit, if D4 is (a). Done before the rules change, so every later commit adds its reason beside its setting.
4. Item 8: one commit, with item 39 in the same commit, since item 8 is what starts the Scanner.
5. Items 16, 17 and 24: one commit, plus `useSortedInterfaceMembers` and `useSortedEnumMembers` if D5 is on. Each assist action enabled here also gets its `source.action.<action>.biome` line in `.vscode/settings.json` (section 12.4). If item 27 is not in yet, that line goes in when item 27 lands.
6. Item 30: one commit, after D8, with `useLiteralKeys` settled the same way. Item 31: one commit with its maintainer fix; the `file-tree-pane` findings go in that plugin's pull request.
7. Item 33: one commit, with no fix needed today. Item 40: one commit with its maintainer fixes; the plugin finding goes in that plugin's pull request. Item 25: one commit with the rules and the `scripts/gates.mjs` fix. The `file-tree-pane` findings go in that plugin's pull request.
8. Item 32: one commit with the `.grit` file, its `plugins` entry and `grit` in `files.includes`.
9. Items 9 to 14: one commit per rule for maintainer files; one pull request per affected plugin. Item 18 goes in the `file-tree-pane` and `tool-ledger` pull requests.
10. Item 27: one commit, after step 1, so Biome checks `.vscode/settings.json` under the final configuration. Items 28 and 29 are not repository commits: they change Nery's user settings and `~/.claude/ENVIRONMENT.md`, with his approval.

Each step runs `npm run lint:js` (the `biome-` gates) before its commit, and records `biome rage --linter`'s enabled-rule count before and after it (section 6.4.1). The pre-push gates run on push.
